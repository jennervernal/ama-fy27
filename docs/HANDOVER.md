# Handover: status and next steps

_Last updated: Thu 12 Nov 2026. Written to let work continue in GitHub Copilot._

## Where we are
- Case, rubric and MasterClass material analysed.
- ADR-001 (deployment region and residency fallback) accepted and committed.
- A personal playbook exists in OneDrive (Word, sections 1-12); this repo is the source of truth for decisions and code.
- Not built yet: model choice, evaluation set, demo, infrastructure templates, rubric tracker.

## Next steps, in priority order
1. **ADR-002: model choice and evidence** (drives A5, A6 and the demo)
   - Compare: small dialect-tuned model(s) vs a larger general model vs a router that sends each request to one or the other.
   - Define "good enough" for Saudi-dialect intent understanding and PII detection (target accuracy / recall).
   - Define cost per resolved conversation and latency budget.
   - Note in-Kingdom availability and provenance of each candidate (open weights, licence, origin).
   - Output: `docs/adr/ADR-002-model-choice.md`.
2. **Saudi-dialect evaluation set = TLA seed** (due 27 Nov)
   - Synthetic customer messages in Saudi dialect (Najdi / Hijazi / Gulf), labelled with intent and PII spans.
   - Decide size (start ~200-300 items), labelling scheme, licence, how it is generated without real data, and an evaluation script that outputs accuracy, PII recall, latency and cost.
   - Suggested layout: `eval/dataset/`, `eval/run_eval.py`, `eval/README.md`.
   - Publish as a Tech Community post + public repo for D3.
3. **Demo script (< 2 minutes, B3)**
   - One Saudi-dialect message handled autonomously by the Care agent, guardrail visible, cost and latency on screen, residency check green.
   - Write `docs/demo-script.md` first, then build only what the script needs.
4. **Deployment kit (A1-A4)**
   - `infra/main.bicep` with `location` parameter; Kingdom zone and shared zone.
   - `infra/policy/` allowed-locations + deny Global / Data Zone model deployments.
   - `scripts/residency-check` that lists every resource and model deployment with its region and fails on anything outside the allow list.
   - Rehearse the region switch (redeploy to a second region from the same templates).
5. **Rubric-to-evidence tracker and dated plan to 11 Dec**
   - `docs/rubric-tracker.md`: one row per criterion, the evidence, status, owner, gap.

## Smaller loose ends
- `docs/industry-context.md`: telecom market, HUMAIN / ALLaM, regulators (CST, NCA, SDAIA), PDPL summary.
- Mine the 12 Nov MasterClass session for useful material.

## Suggested first prompts for GitHub Copilot
- "Read .github/copilot-instructions.md and docs/HANDOVER.md, then draft docs/adr/ADR-002-model-choice.md following the ADR-001 format, with candidate models and evaluation criteria. Mark anything unverified."
- "Propose a schema and 20 sample synthetic Saudi-dialect telecom care messages with intent and PII labels for eval/dataset/."
- "Create infra/main.bicep with location as a parameter and infra/policy for allowed locations."

## Open questions to settle with the panel narrative
- Is intent-only processing ever acceptable to the sponsor and DPO, given "all inference in-Kingdom"?
- Which candidate models are truly deployable in-Kingdom on day one?
- How to show cost per business outcome credibly with synthetic traffic.
