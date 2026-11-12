# ADR-001: Deployment region and residency fallback

- **Status:** Accepted
- **Date:** 2026-11-12
- **Owner:** Jenner Vernal
- **Review trigger:** Azure Saudi Arabia East opens, or the sponsors request live operation before it does

## Context

The case requires all inference over Saudi subscriber data to run in the Kingdom and assumes Azure Saudi Arabia East goes live in Q4 2026. In reality the region could not be confirmed as open, and the build environment has neither a Saudi region nor Azure Local hardware. The capstone must still show a platform that works end to end (rubric A4) and enforces residency by design (rubric A3).

## Decision

Build and test the whole platform in a neighbouring staging region (UAE North) with **synthetic data only**. The region is a single parameter in the deployment templates. When Saudi Arabia East opens, redeploy the same templates there; from then on all inference runs in the Kingdom. **No live Saudi subscriber data ever touches the staging region.**

- Residency is enforced by policy: allowed regions only; Global and Data Zone model deployment types are denied, even in staging.
- Only services and models expected in Saudi Arabia East at launch are used. Each dependency is tracked as *expected*, *unverified* or *fallback needed*.
- The switch to a second region is rehearsed once, so the redeployment is evidence rather than a claim. Most Azure resources cannot change region in place: this is a redeployment, not a move.
- An automated residency check lists every resource and data store with its region and fails if anything is out of place.

## Fallback: intent-only processing

If live operation is needed before the Saudi region opens, or a required service or model is missing there, the agent is split. A thin in-Kingdom layer keeps the customer's identity, data and tool calls. The model in the neighbouring region only receives the **intent and a generic, de-identified question**. The link between that question and the customer exists only in the Kingdom.

| Step | Where | What happens |
|---|---|---|
| 1 | In-Kingdom | Receive the customer's message |
| 2 | In-Kingdom | Detect and remove personal data (Saudi dialect detector, fail closed when unsure) |
| 3 | In-Kingdom | Identify the intent, e.g. billing dispute, bill well above plan |
| 4 | In-Kingdom | Write a generic question that cannot single out the customer |
| 5 | Neighbouring region | A larger model reasons on the generic question and returns a generic answer |
| 6 | In-Kingdom | Hold identity and session; nothing about the customer leaves |
| 7 | In-Kingdom | Call customer-data tools (bill, plan, line status) and take any account action |
| 8 | In-Kingdom | Apply the generic answer to this customer and reply |

Strictly, this is **data minimisation, not anonymisation**. The outbound question is non-personal only if it cannot single anyone out; the session link that makes the answer usable stays in the Kingdom. Under the Saudi PDPL, irreversibly anonymised data falls outside the law, whereas pseudonymised data (codes plus a lookup table) remains personal data.

### Trigger and exit conditions

- **Trigger:** written approval from the sponsors (CDO and CCO) and the customer's data protection officer, as a time-limited exception to the in-Kingdom inference requirement.
- **Prerequisite:** an in-Kingdom footprint for the thin layer (customer data centre, Azure Local on customer hardware, or an in-Kingdom partner such as HUMAIN). The fallback reduces in-Kingdom capacity needs but cannot remove them.
- **Gate:** personal-data detection recall on the Gulf and Egyptian dialect test set is measured and enforced in the release pipeline.
- **Exit:** the fallback ends when the required models and services are generally available in the Kingdom.

## Alternatives considered

| Alternative | Verdict | Why |
|---|---|---|
| Run with live Saudi data in a neighbouring region | Rejected | Breaches the in-Kingdom inference requirement and expectations on a likely critical-infrastructure operator |
| Pseudonymise, process abroad, restore on return | Rejected as default | Still personal data under the PDPL and a cross-border transfer; left for the customer's legal team to assess |
| Anonymise everything sent abroad | Accepted for offline use only | Works for analytics, training and test datasets; cannot answer a specific customer |
| Wait for the region before building | Rejected | No working build for the panel and no learning before go-live |
| In-Kingdom partner or customer hardware for everything now | Kept as interim production option | Valid, but depends on the customer; not available in the build environment |

## Consequences by agent

| Agent (autonomy) | Main path | Under the fallback |
|---|---|---|
| Customer Care (L3) | Fully in-Kingdom; small dialect-tuned models carry most intents | Common intents only; lower resolution than the 45% deflection target, slower answers |
| B2B Sales (L2) | Fully in-Kingdom | Best fit: generic solution drafting without the client name; a human approves anyway |
| Network Ops (L3, human approval) | Fully in-Kingdom | Generic runbook knowledge only; topology and telemetry never leave |
| Guardrail & Evaluation (L4) | Fully in-Kingdom | Not eligible: must inspect raw content in place; anonymised sets used offline |
| Tenant Governance (L4) | Shared zone, configuration only | Not affected: holds no customer content |

## Risks and open items

- A personal detail leaking into the generic question: mitigated by measured detection, fail-closed handling and outbound tests in the pipeline.
- Saudi Arabia East opening date and day-one service and model list: unverified; confirm with the Azure product team.
- Final wording of the PDPL rules on transfers outside the Kingdom, and telecom and cybersecurity regulator data-location rules: not yet checked.
- Identity (Entra ID) is a global service and cannot be made Saudi-only; needs explicit customer acceptance.

## References

- SDAIA, PDPL Implementing Regulation: definitions of pseudonymisation and anonymisation (Article 1).
- SDAIA, Personal Data Destruction, Anonymization and Pseudonymisation Guideline.
- Microsoft Learn, Foundry Local on Azure Local: bring your own models.
- Microsoft Learn, Bring your own model to Foundry Agent Service.
