# Handover: status and next steps

_Last updated: Thu 12 Nov 2026. Written to let work continue in GitHub Copilot._

## Where we are
- Case, rubric and MasterClass material analysed.
- ADR-001 (deployment region and residency fallback) accepted and committed.
- ADR-002 (proposed model routing pattern and evaluation gates) added.
- `eval/` contains a 240-example synthetic benchmark draft (including a held-out split), a 1,000-case synthetic PII-positive stress draft, a dependency-free generator and scorer. These are unreviewed scaffolds, not validated Arabic benchmark or production-safety evidence.
- A personal playbook exists in OneDrive (Word, sections 1-12); this repo is the source of truth for decisions and code.
- Not built yet: reviewed benchmark and measured model comparison, demo, infrastructure templates, rubric tracker.

## Next steps, in priority order
1. **Review and validate the Saudi-dialect evaluation set = TLA seed** (due 27 Nov)
   - Arabic-speaking reviewers must correct/approve dialect wording, intent, escalation and PII labels in the 240-row draft before it is treated as benchmark evidence; keep the held-out split untouched until then.
   - Review and expand the 1,000-case synthetic PII-positive draft; add reviewed hard cases and negative PII examples before making precision or production-safety claims.
   - Record reviewer, dataset revision, provenance and label agreement. Then run pinned model candidates through the scorer and publish measured per-dialect quality, PII recall and confidence interval, latency and cost. Current generated sets are not evidence for the ADR-002 release gates.
   - Files: `eval/dataset/`, `eval/generate_datasets.py`, `eval/run_eval.py`, `eval/README.md`.
   - Publish as a Tech Community post + public repo for D3.
2. **Demo script (< 2 minutes, B3)**
   - One Saudi-dialect message handled autonomously by the Care agent, guardrail visible, cost and latency on screen, residency check green.
   - Write `docs/demo-script.md` first, then build only what the script needs.
3. **Deployment kit (A1-A4)**
   - `infra/main.bicep` with `location` parameter; Kingdom zone and shared zone.
   - `infra/policy/` allowed-locations + deny Global / Data Zone model deployments.
   - `scripts/residency-check` that lists every resource and model deployment with its region and fails on anything outside the allow list.
   - Rehearse the region switch (redeploy to a second region from the same templates).
4. **Rubric-to-evidence tracker and dated plan to 11 Dec**
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
