# Copilot instructions: AMA FY27 capstone (Case Study 21)

This repo holds Jenner Vernal's Azure Master Architect (AMA) FY27 EMEA Cohort 2 capstone.
Read this file, then `docs/HANDOVER.md`, before suggesting work.

## The case (see `assignment.md`)
- **Case Study 21: Sovereign Arabic Agent Platform** for a Riyadh-based telecom group (fictional; resembles a large Saudi incumbent).
- ~40M subscribers at group level; subsidiaries in Kuwait, Bahrain and Egypt.
- Agents and autonomy levels: Care (L3), B2B Sales (L2), Network Ops (L3, a human approves any change to the radio network), Guardrail & Evaluation (L4), Tenant Governance (L4).
- Shared tools exposed through MCP with per-tenant scopes. Brief says **all inference in-Kingdom**.
- Targets: 45% care deflection, B2B quote time down 60%, SAR 400M/year savings. Sponsors: CDO and CCO.
- The case assumes Azure **Saudi Arabia East** goes live in Q4 2026.

## How it is graded (see `AMA_Capstone_Rubric_Participants 1.md`)
- A Technical 35, B Communication 35, C Consultative 15, D Thought Leadership Artifact (TLA) 15.
- Floors: every section >= 60%, no criterion scored 1, TLA submitted, MasterClass attendance.
- Outcomes: Distinction 90+, Merit 78-89, Pass 66-77.
- ~30 points need a WORKING build with numbers (A4-A7):
  - A4 end-to-end working, known gaps disclosed proactively;
  - A5 cost per unit of business value (e.g. cost per resolved conversation);
  - A6 model choice justified on cost, latency, quality, with an evaluation harness;
  - A7 real autonomy with guardrails.
- B3: live demo under 2 minutes; a failure is scored on recovery. C3: raise risks unprompted.
- D: TLA is separate from the capstone documentation. A reference implementation needs a README (purpose, architecture, setup, limitations). D3 rewards publication beyond the cohort (e.g. Tech Community).
- A non-working build is not eliminatory by itself; it becomes eliminatory if A4 scores 1 or section A drops below 21/35.

## Dates
| Milestone | Date |
|---|---|
| TLA due (aim to submit ~25 Nov) | Fri 27 Nov 2026 |
| Capstone artifact due | Mon 30 Nov 2026 |
| Panel receives TLA | Fri 4 Dec 2026 |
| Panel | Fri 11 Dec 2026 |

## Decisions already taken
- **ADR-001** (`docs/adr/ADR-001-deployment-region-and-residency-fallback.md`): build in a neighbouring region (UAE North) with synthetic data only; region is a template parameter; redeploy (not migrate) to Saudi Arabia East when available; Azure Policy allows listed regions only and denies Global / Data Zone model deployments; automated residency check; fallback = intent-only processing (identity, data and tools stay in-Kingdom, only a de-identified generic question leaves), gated on sponsor + DPO sign-off and measured PII-detection recall.
- Anonymised data (permanently non-identifiable) is outside Saudi PDPL; pseudonymised data is still personal data. Do not call the fallback "anonymisation"; it is data minimisation.

## Constraints of the build environment
- No Saudi Arabia Azure region available today; no Azure Local hardware.
- Stand-ins: a "Kingdom zone" (resource group / VNet / cluster) and a "shared zone", synthetic data, policy-denial demos. Always label stand-ins honestly.

## Conventions for this repo
- Decision records go in `docs/adr/ADR-NNN-short-title.md` with sections: Status, Date, Context, Decision, Consequences, Alternatives considered, Risks and open items.
- Infrastructure as code: Bicep, region always a parameter, no hard-coded locations.
- Never commit real customer data, secrets or keys. Synthetic data only, clearly marked.
- Separate VERIFIED facts (with a source link) from UNVERIFIED assumptions. Unverified today: Saudi Arabia East opening date and day-one service list; Azure Local / Foundry Local support for KSA; final PDPL transfer regulation text; CST / NCA data-location rules; HUMAIN API format.
- Write in plain business English; British spelling is fine.
