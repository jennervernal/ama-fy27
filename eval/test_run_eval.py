import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from generate_datasets import DIALECTS, PII_TYPES, benchmark_rows, pii_stress_rows
from run_eval import evaluate, load_dataset, load_predictions


DATASET = Path(__file__).parent / "dataset"


class GeneratedDatasetTests(unittest.TestCase):
    def test_benchmark_is_balanced_and_has_heldout_split(self):
        rows = benchmark_rows()
        self.assertEqual(len(rows), 240)
        self.assertEqual(Counter(row["dialect"] for row in rows), {dialect: 60 for dialect in DIALECTS})
        self.assertEqual(
            Counter(row["split"] for row in rows),
            {"development": 168, "validation": 24, "heldout": 48},
        )
        self.assertEqual(len({row["id"] for row in rows}), len(rows))

    def test_pii_stress_set_is_balanced_and_synthetic(self):
        rows = pii_stress_rows()
        self.assertEqual(len(rows), 1000)
        self.assertEqual(Counter(row["dialect"] for row in rows), {dialect: 250 for dialect in DIALECTS})
        self.assertEqual(Counter(row["case_group"] for row in rows), {kind: 200 for kind in PII_TYPES})
        for row in rows:
            self.assertEqual(len(row["pii_spans"]), 1)
            span = row["pii_spans"][0]
            self.assertIn(span["text"], row["text"])
            self.assertTrue(
                span["text"].startswith("SYN-")
                or span["text"].endswith("@example.invalid")
                or set(span["text"]) <= {"0", "٠", "-", " "},
                span["text"],
            )

    def test_heldout_scorer_reports_per_dialect_and_recall_interval(self):
        rows = load_dataset(DATASET / "benchmark-draft.jsonl", "heldout")
        self.assertEqual(len(rows), 48)
        predictions = {
            row["id"]: {
                "predicted_intent": row["intent"],
                "predicted_pii": row["pii_spans"],
                "predicted_action": row["expected_action"],
                "escalated": row["should_escalate"],
                "latency_ms": 100,
                "cost_usd": 0.001,
            }
            for row in rows
        }
        metrics = evaluate(rows, predictions)
        self.assertEqual(metrics["examples"], 48)
        self.assertEqual(metrics["intent_accuracy"], 1)
        self.assertEqual(metrics["pii_span_recall"], 1)
        self.assertEqual(set(metrics["by_dialect"]), set(DIALECTS))
        self.assertTrue(all(result["examples"] == 12 for result in metrics["by_dialect"].values()))
        low, high = metrics["pii_span_recall_wilson_95"]
        self.assertLess(low, 1)
        self.assertEqual(high, 1)

    def test_prediction_loader_rejects_missing_rows(self):
        rows = load_dataset(DATASET / "smoke.jsonl")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "predictions.jsonl"
            path.write_text(
                json.dumps({
                    "id": rows[0]["id"],
                    "predicted_intent": rows[0]["intent"],
                    "predicted_pii": rows[0]["pii_spans"],
                    "predicted_action": rows[0]["expected_action"],
                    "escalated": rows[0]["should_escalate"],
                    "latency_ms": 1,
                    "cost_usd": 0,
                }) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "missing predictions"):
                load_predictions(path, {row["id"] for row in rows})


if __name__ == "__main__":
    unittest.main()
