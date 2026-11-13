# Arabic dialect evaluation draft

This directory contains:

- `dataset/benchmark-draft.jsonl`: 240 synthetic, template-authored care messages (60 each for Najdi, Hijazi, Gulf and Egyptian Arabic). The split is 168 development, 24 validation and 48 held-out examples.
- `dataset/pii-stress-draft.jsonl`: 1,000 synthetic positive cases balanced across those four dialect labels and five synthetic identifier types.
- `dataset/smoke.jsonl`: 20 hand-authored schema and scorer examples.
- `generate_datasets.py`: standard-library generator for both draft datasets.

These are **unreviewed drafts**, not validated Arabic benchmark data, model measurements, or production safety evidence. The template patterns are systematic and may be linguistically unnatural, ambiguous or label-leaky. An Arabic-speaking reviewer must validate dialect assignment, phrasing, intent, escalation and PII labels; the held-out split must not be used to tune a model or prompt. Do not describe the generator's outputs as human-reviewed.

No customer data is included. Account and transaction identifiers use synthetic `SYN-` values, emails use the reserved `.invalid` domain, and phone/national-ID placeholders contain only zeroes. Dataset records are JSON Lines with:

- `id`, `dialect`, `text`, `intent`
- `pii_spans`: exact synthetic text and a type label
- `expected_action`: a symbolic expected tool/policy outcome, not an instruction to execute
- `should_escalate`: whether the example must be handed to a person
- `split`: development, validation or heldout (benchmark only)

## Run

Use Python 3.9+ with no third-party dependencies. Regenerate the draft files with:

```sh
python eval/generate_datasets.py
```

For the primary comparison, pass one prediction for every held-out benchmark row:

```json
{"id":"ar-bench-0001","predicted_intent":"billing_dispute","predicted_pii":[],"predicted_action":"check_bill","escalated":false,"latency_ms":125.4,"cost_usd":0.0008}
```

```sh
python eval/run_eval.py --split heldout --predictions heldout-predictions.jsonl
python eval/run_eval.py --dataset eval/dataset/pii-stress-draft.jsonl --predictions pii-predictions.jsonl
python eval/run_eval.py --dataset eval/dataset/smoke.jsonl --split all --predictions smoke-predictions.jsonl
```

The evaluator rejects missing, duplicate or extra IDs and invalid/missing fields; it does not call a model or execute tools. `predicted_pii` uses exact text/type matches. Output includes overall and per-dialect intent accuracy/macro-F1, exact PII span recall and a 95% Wilson interval, action/escalation accuracy, wrong-action count, p50/p95 latency, supplied total cost and cost per safe resolution. Cost per safe resolution divides total supplied cost by correctly classified, correctly actioned, non-escalated examples whose labels do not require escalation. Supply measured latency and cost from the model adapter; these metrics are not inferred by the evaluator. Do not use the development set to report final model comparisons; use the held-out set only after reviewer approval.

## Review and limitations

The stress set contains positive cases only. It can measure exact-match recall on its synthetic patterns, but cannot estimate precision, false-positive rates, real-world recall or readiness for the ADR-002 release gate. It includes a small number of boilerplate/code-switch/adversarial suffix patterns but does not model the full range of spelling, morphology, transliteration, embedded identifiers or naturally occurring dialogue. The repeated all-zero placeholders are intentionally fake and are not representative telephone or national-ID examples.

Before treating results as evidence, ask Arabic-speaking reviewers to annotate and correct dialect and intent labels, review PII spans and escalation policy, and approve a versioned held-out set. Add independently authored and reviewed hard cases, negatives for PII precision, naturally varied code-switching and typo/transliteration variants, and document label agreement and provenance. Never add real subscriber text, identifiers, prompts or outputs to this repository.

The repository does not currently contain a root licence file, so confirm the dataset and evaluator licence before external publication. The licence for any model evaluated with them is separate and must be checked independently.
