# ADR-002: Model choice and evaluation evidence

- **Status:** Proposed — benchmark and regional availability gates are open
- **Date:** 2026-11-12
- **Owner:** Jenner Vernal
- **Review trigger:** Completion of the Saudi-dialect benchmark, or confirmation of the Saudi Arabia East model catalogue

## Context

The platform needs to understand Saudi, Gulf and Egyptian Arabic, protect personal data, and support customer-care actions without letting a language model make authorization decisions. The case requires inference in the Kingdom. ADR-001 permits synthetic-data testing in a neighbouring region, but it does not make that region a production option for Saudi subscriber data.

There is not yet a measured comparison on a representative, labelled dataset, nor confirmation that a specific model and deployment type will be available in Saudi Arabia East. A model recommendation without those facts would overstate the evidence. This decision therefore selects a model-serving pattern and defines the gates for selecting a production checkpoint.

## Decision

Adopt an **in-Kingdom-first, confidence-gated router** as the target pattern:

1. A small Arabic-capable model deployed in the Kingdom handles common intent classification and low-risk language tasks.
2. A larger general model may handle ambiguous or complex language tasks only if its exact deployment is confirmed to process data in Saudi Arabia East.
3. Calibrate the routing score on held-out data; do not rely on model self-reported confidence. Below the calibrated threshold, hand the request to a person or a safe deterministic flow. The router must not silently send content to a model in another region.
4. Models may propose tool calls; in-Kingdom policy services enforce tenant scope, account authority, consent and action limits. Network changes in the RAN always require human approval.

The production checkpoint is **not selected yet**. Benchmark the candidates below against the same prompt, test set, hardware or deployment class and load profile. Select the least costly candidate that passes every quality, safety, latency and residency gate. If no candidate passes, do not enable autonomous customer-care actions.

| Candidate | Proposed role | Provenance and licence evidence | Deployment status |
|---|---|---|---|
| [ALLaM-7B-Instruct](https://huggingface.co/SDAIA-ALLaM/ALLaM-7B-Instruct) | Small Arabic-capable fast path | Public checkpoint from the SDAIA-ALLaM publisher; model card reports Apache 2.0. Verify publisher, exact revision and licence terms before use | In-Kingdom serving and Saudi dialect performance are unverified |
| [Jais-13B-Chat](https://huggingface.co/inception42/jais-13b-chat) | Arabic-capable comparison candidate | Public checkpoint from the Inception42 publisher; model card reports Apache 2.0. Verify exact revision and licence terms before use | In-Kingdom serving and Saudi dialect performance are unverified |
| A larger general model listed for Saudi Arabia East | Complex requests only, behind the router | Record publisher, model version, terms and data-processing commitments from the selected service listing | Candidate is intentionally unnamed until the regional catalogue is confirmed |

Model-card descriptions and licences are claims to verify, not an endorsement or a substitute for legal review. Pin the model revision, tokenizer, quantisation, prompt, deployment SKU and licence evidence for each run. A public model checkpoint is not proof that its hosted endpoint is available in the Kingdom.

## Evaluation and release gates

Use synthetic messages only. The first screening set will contain 240 examples, balanced across Najdi, Hijazi and Gulf Arabic. Add and report an Egyptian slice separately if the business scope includes that subsidiary. Label each message with intent, dialect, spans for synthetic PII, expected tool/action and whether escalation is required. Keep a held-out test split and report per-dialect results as well as aggregate results.

The following are proposed initial gates, not measured results. Confirm them with the CDO, CCO, DPO and care operations before production:

| Measure | Initial gate | Evidence |
|---|---|---|
| Intent classification | Macro-F1 ≥ 0.90 overall and ≥ 0.85 for each dialect slice | Held-out, human-reviewed labels; report confusion matrix and confidence intervals |
| PII detection | Recall ≥ 0.99 on a PII-positive stress set, with zero misses for designated critical identifiers | At least 1,000 synthetic PII-positive cases, including dialect variation, code-switching, spelling variation and adversarial prompts; fail closed when uncertain |
| Grounded response | ≥ 0.95 correct and supported by the authorized tool result on tool-backed cases | Expected answer and tool-result checks; count unsupported claims and unsafe actions separately |
| Action policy | 100% rejection of cross-tenant, unauthorized and unapproved actions | Negative tests for tenant boundary, account authority, consent and mandatory human approval |
| Latency | p95 ≤ 2 seconds for routing/classification and ≤ 6 seconds for a standard tool-backed turn | Measure end-to-end under a declared load profile; report model-only and total latency |
| Cost per safe resolution | At most 10% of the validated cost of a human-resolved care contact | Include model usage or serving compute, retries, tools, gateway and allocated idle capacity; Finance must supply the human-contact baseline |

For each run, record the dataset revision, candidate/model revision, deployment region and SKU, prompt version, load, input/output token counts or compute time, latency percentiles, errors, escalation rate, quality metrics and dated price source. Cost per safe resolution is total measured serving and request cost divided by conversations resolved without an unsafe action and without human intervention. Also report cost per attempted conversation and escalation rate so that a low cost cannot be manufactured by excluding failures.

The 240-example set is for initial comparison, not statistical proof of a 99% PII recall rate. Expand the stress set and report confidence intervals before treating a gate as evidence of production safety. Test the exact production deployment in Saudi Arabia East when it is available; a synthetic-data run in UAE North is only a labelled staging stand-in.

## Alternatives considered

| Alternative | Verdict | Why |
|---|---|---|
| One large general model for every request | Rejected as the default | May increase latency and cost for common intents; regional availability and Arabic dialect quality are unverified |
| One small model for every request | Rejected | May not handle complex or ambiguous requests well enough; no measured quality evidence yet |
| Route to an out-of-Kingdom model by default | Rejected | Conflicts with the in-Kingdom inference requirement; ADR-001's intent-only exception requires separate written sponsor and DPO approval and a measured privacy gate |
| Select a model from benchmark scores alone | Rejected | Licence, deployment region, tenant isolation, operational cost and policy-enforced tool access are release gates too |

## Consequences

- The router keeps the common path economical while allowing a measured quality fallback for harder requests.
- The architecture remains model-provider-neutral until the regional model catalogue, licence and benchmark results are known.
- The model does not authorize or execute actions on its own. Tool gateways and policy checks remain authoritative, and low-confidence cases escalate.
- No production model performance, regional availability or cost saving is claimed until measured on the pinned candidate and validated workload.
- A model that is not available in Saudi Arabia East cannot be used for Saudi subscriber data in production. Intent-only processing from ADR-001 remains an exceptional, separately approved fallback, not part of this default decision.

## Risks and open items

- **Regional availability:** Confirm that the specific model, deployment type, SKU and required supporting services are available in Saudi Arabia East; a region announcement alone does not establish model availability.
- **Arabic quality:** The test dialect slices may not represent the full range of spelling, code-switching, names or service vocabulary. Have Arabic-speaking reviewers validate labels and failure cases.
- **PII leakage:** A detector can miss or transform personal data in dialect text. Keep detection and outbound-content checks fail-closed; do not use model confidence as a privacy control.
- **Licence and provenance:** Validate publisher identity, model revision, licence and any use restrictions with the customer before deployment or publication.
- **Economics:** Contact volume, human cost per resolved contact, load profile and final regional prices are not yet supplied. The 10% cost gate is a proposed threshold and must be confirmed by Finance.
- **Latency:** The initial latency gates are proposed targets; validate them with the real service/tool chain and agreed peak load.
- **Evaluation integrity:** Synthetic data may under-represent real operational language. Do not claim production accuracy from synthetic-only evaluation; plan a customer-approved, privacy-reviewed validation stage if needed.

## References

- [ALLaM-7B-Instruct model card](https://huggingface.co/SDAIA-ALLaM/ALLaM-7B-Instruct) — publisher metadata and Apache 2.0 licence claim to verify at the pinned revision.
- [Jais-13B-Chat model card](https://huggingface.co/inception42/jais-13b-chat) — publisher metadata and Apache 2.0 licence claim to verify at the pinned revision.
- [Microsoft Foundry region availability](https://learn.microsoft.com/en-us/azure/foundry/foundry-region-availability) — check exact model and deployment availability at decision and deployment time.
- [Microsoft Foundry regional feature support](https://learn.microsoft.com/en-us/azure/foundry/reference/region-support) — regional service support must be checked separately from model-card availability.
- [Microsoft announcement: Saudi Arabia East availability](https://news.microsoft.com/source/emea/2026/08/microsoft-announces-saudi-arabia-east-datacenter-region-will-be-available-in-november-2026/) — announcement of regional availability timing, not evidence that a specific model deployment is available.
