# Arabic dialect evaluation smoke set

This is a small, **synthetic smoke fixture**, not the 240-example benchmark or the 1,000-case PII stress set proposed in [ADR-002](../docs/adr/ADR-002-model-choice.md). It contains 20 hand-authored examples (five each for Najdi, Hijazi, Gulf and Egyptian Arabic) to exercise the data schema and scoring code. It is not representative evidence of model quality or a production safety assessment. Ask Arabic-speaking reviewers to validate dialect wording, labels and expected actions before expanding or publishing a benchmark.

All account and transaction identifiers use visibly synthetic `SYN-` values. Any phone-like value is the all-zero placeholder `0000000000`; it is not a contact number. No customer data is included. Dataset records are JSON Lines with:

- `id`, `dialect`, `text`, `intent`
- `pii_spans`: exact synthetic text and a type label
- `expected_action`: a symbolic expected tool/policy outcome, not an instruction to execute
- `should_escalate`: whether the example must be handed to a person

## Run

Use Python 3.9+ with no third-party dependencies. Supply one prediction row per dataset row:

```sh
python eval/run_eval.py --predictions predictions.jsonl
```

Each prediction is a JSON object on one line:

```json
{"id":"ar-smoke-001","predicted_intent":"billing_dispute","predicted_pii":[{"text":"SYN-0001","type":"synthetic_account_id"}],"predicted_action":"check_bill","escalated":false,"latency_ms":125.4,"cost_usd":0.0008}
```

The evaluator rejects missing, duplicate or extra IDs and invalid/missing fields; it does not call a model or execute tools. `predicted_pii` uses exact text/type matches. Output includes intent accuracy and macro-F1, PII span recall, action and escalation accuracy, wrong-action count, p50/p95 latency, total supplied cost and cost per safe resolution. Cost per safe resolution uses total supplied cost divided by correctly classified, correctly actioned, non-escalated examples whose labels do not require escalation. Supply measured latency and cost from the model adapter; these metrics are not inferred by the evaluator.

## Before using this as benchmark evidence

Expand and version the dataset to the planned 240+ examples with a held-out split, dialect-balanced coverage, Arabic-speaking label review and documented provenance. Build a separate PII-positive stress set large enough to assess the proposed recall target, including code-switching, spelling variation and adversarial content. Report per-dialect results and uncertainty; this 20-row smoke fixture is too small to validate the gates in ADR-002. Never put real subscriber text, identifiers, prompts or outputs in this repository.

This fixture and evaluator are released under the repository's MIT licence. The licence for any model evaluated with them is separate and must be checked independently.
