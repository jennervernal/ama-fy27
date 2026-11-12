#!/usr/bin/env python3
"""Score JSONL predictions against a synthetic Arabic evaluation dataset."""

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path


DEFAULT_DATASET = Path(__file__).parent / "dataset" / "benchmark-draft.jsonl"


def read_jsonl(path):
    rows = []
    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {error}") from error
    return rows


def require_fields(row, fields, path, index):
    if not isinstance(row, dict):
        raise ValueError(f"{path}: row {index} must be a JSON object")
    missing = fields - row.keys()
    if missing:
        raise ValueError(f"{path}: row {index} is missing fields: {', '.join(sorted(missing))}")


def load_dataset(path, split="all"):
    rows = read_jsonl(path)
    if not rows:
        raise ValueError(f"{path}: dataset is empty")
    seen = set()
    for index, row in enumerate(rows, start=1):
        require_fields(
            row,
            {"id", "dialect", "text", "intent", "pii_spans", "expected_action", "should_escalate"},
            path,
            index,
        )
        if not isinstance(row["id"], str) or not isinstance(row["text"], str):
            raise ValueError(f"{path}: row {index} has an invalid id or text")
        if row["id"] in seen:
            raise ValueError(f"{path}: duplicate id {row['id']!r}")
        if not isinstance(row["pii_spans"], list) or not isinstance(row["should_escalate"], bool):
            raise ValueError(f"{path}: row {index} has invalid pii_spans or should_escalate")
        if "split" in row and row["split"] not in {"development", "validation", "heldout"}:
            raise ValueError(f"{path}: row {index} has an invalid split")
        for span in row["pii_spans"]:
            if not isinstance(span, dict) or not isinstance(span.get("text"), str) or not span["text"]:
                raise ValueError(f"{path}: row {index} has an invalid PII span")
            if not isinstance(span.get("type"), str) or span["text"] not in row["text"]:
                raise ValueError(f"{path}: row {index} has a PII span not found in text")
        seen.add(row["id"])
    if split != "all":
        if any("split" not in row for row in rows):
            raise ValueError(f"{path}: --split {split} requires split labels on every row")
        rows = [row for row in rows if row["split"] == split]
        if not rows:
            raise ValueError(f"{path}: split {split!r} contains no rows")
    return rows


def load_predictions(path, expected_ids):
    rows = read_jsonl(path)
    by_id = {}
    required = {
        "id",
        "predicted_intent",
        "predicted_pii",
        "predicted_action",
        "escalated",
        "latency_ms",
        "cost_usd",
    }
    for index, row in enumerate(rows, start=1):
        require_fields(row, required, path, index)
        if not isinstance(row["id"], str) or not all(
            isinstance(row[field], str) for field in ("predicted_intent", "predicted_action")
        ):
            raise ValueError(f"{path}: row {index} has an invalid id, intent or action")
        if row["id"] in by_id:
            raise ValueError(f"{path}: duplicate prediction id {row['id']!r}")
        if (
            not isinstance(row["predicted_pii"], list)
            or not isinstance(row["escalated"], bool)
            or isinstance(row["latency_ms"], bool)
            or not isinstance(row["latency_ms"], (int, float))
            or isinstance(row["cost_usd"], bool)
            or not isinstance(row["cost_usd"], (int, float))
            or not math.isfinite(row["latency_ms"])
            or not math.isfinite(row["cost_usd"])
            or row["latency_ms"] < 0
            or row["cost_usd"] < 0
        ):
            raise ValueError(f"{path}: row {index} has invalid prediction, latency or cost values")
        for span in row["predicted_pii"]:
            if not isinstance(span, dict) or not isinstance(span.get("text"), str) or not isinstance(span.get("type"), str):
                raise ValueError(f"{path}: row {index} has an invalid predicted PII span")
        by_id[row["id"]] = row

    missing = expected_ids - by_id.keys()
    extra = by_id.keys() - expected_ids
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing predictions for: {', '.join(sorted(missing))}")
        if extra:
            details.append(f"unknown prediction ids: {', '.join(sorted(extra))}")
        raise ValueError(f"{path}: " + "; ".join(details))
    return by_id


def macro_f1(truth, predicted):
    labels = set(truth) | set(predicted)
    scores = []
    for label in labels:
        true_positive = sum(actual == label and guess == label for actual, guess in zip(truth, predicted))
        false_positive = sum(actual != label and guess == label for actual, guess in zip(truth, predicted))
        false_negative = sum(actual == label and guess != label for actual, guess in zip(truth, predicted))
        denominator = 2 * true_positive + false_positive + false_negative
        scores.append(2 * true_positive / denominator if denominator else 0.0)
    return sum(scores) / len(scores) if scores else 0.0


def percentile(values, percentile):
    ordered = sorted(values)
    return ordered[max(0, math.ceil(percentile * len(ordered)) - 1)]


def wilson_interval(successes, total, z=1.96):
    if not total:
        return None
    proportion = successes / total
    denominator = 1 + z * z / total
    centre = (proportion + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total)) / denominator
    return [max(0.0, centre - margin), min(1.0, centre + margin)]


def evaluate(dataset, predictions):
    truth = [row["intent"] for row in dataset]
    predicted = [predictions[row["id"]]["predicted_intent"] for row in dataset]
    intent_correct = [actual == guess for actual, guess in zip(truth, predicted)]
    expected_pii = Counter()
    found_pii = Counter()
    for row in dataset:
        expected_pii.update((span["text"], span["type"]) for span in row["pii_spans"])
        found_pii.update(
            (span["text"], span["type"])
            for span in predictions[row["id"]]["predicted_pii"]
        )
    pii_total = sum(expected_pii.values())
    pii_matched = sum(min(count, found_pii[key]) for key, count in expected_pii.items())
    action_correct = [
        row["expected_action"] == predictions[row["id"]]["predicted_action"]
        for row in dataset
    ]
    escalation_correct = [
        row["should_escalate"] == predictions[row["id"]]["escalated"]
        for row in dataset
    ]
    safe_resolutions = sum(
        intent_ok and action_ok and not row["should_escalate"] and not predictions[row["id"]]["escalated"]
        for row, intent_ok, action_ok in zip(dataset, intent_correct, action_correct)
    )
    total_cost = sum(predictions[row["id"]]["cost_usd"] for row in dataset)
    latencies = [predictions[row["id"]]["latency_ms"] for row in dataset]
    by_dialect = {}
    for dialect in sorted({row["dialect"] for row in dataset}):
        indexes = [index for index, row in enumerate(dataset) if row["dialect"] == dialect]
        dialect_expected = Counter()
        dialect_found = Counter()
        for index in indexes:
            row = dataset[index]
            dialect_expected.update((span["text"], span["type"]) for span in row["pii_spans"])
            dialect_found.update(
                (span["text"], span["type"])
                for span in predictions[row["id"]]["predicted_pii"]
            )
        dialect_pii_total = sum(dialect_expected.values())
        dialect_pii_matched = sum(
            min(count, dialect_found[key]) for key, count in dialect_expected.items()
        )
        by_dialect[dialect] = {
            "examples": len(indexes),
            "intent_accuracy": sum(intent_correct[index] for index in indexes) / len(indexes),
            "intent_macro_f1": macro_f1(
                [truth[index] for index in indexes],
                [predicted[index] for index in indexes],
            ),
            "pii_span_recall": (
                dialect_pii_matched / dialect_pii_total if dialect_pii_total else None
            ),
            "action_accuracy": sum(action_correct[index] for index in indexes) / len(indexes),
        }

    return {
        "examples": len(dataset),
        "intent_accuracy": sum(intent_correct) / len(dataset),
        "intent_macro_f1": macro_f1(truth, predicted),
        "pii_span_recall": pii_matched / pii_total if pii_total else None,
        "pii_span_recall_wilson_95": wilson_interval(pii_matched, pii_total),
        "pii_spans_matched": pii_matched,
        "pii_spans_expected": pii_total,
        "action_accuracy": sum(action_correct) / len(dataset),
        "escalation_accuracy": sum(escalation_correct) / len(dataset),
        "unsafe_action_count": sum(not correct for correct in action_correct),
        "latency_ms_p50": percentile(latencies, 0.50),
        "latency_ms_p95": percentile(latencies, 0.95),
        "total_cost_usd": total_cost,
        "safe_resolutions": safe_resolutions,
        "cost_per_safe_resolution_usd": total_cost / safe_resolutions if safe_resolutions else None,
        "by_dialect": by_dialect,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument(
        "--split",
        choices=("all", "development", "validation", "heldout"),
        default="all",
        help="evaluate one labeled split; default evaluates all rows",
    )
    parser.add_argument("--predictions", type=Path, required=True, help="JSONL model outputs matching the README schema")
    args = parser.parse_args()
    try:
        dataset = load_dataset(args.dataset, args.split)
        predictions = load_predictions(args.predictions, {row["id"] for row in dataset})
        print(json.dumps(evaluate(dataset, predictions), indent=2, ensure_ascii=False))
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
