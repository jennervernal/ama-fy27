# Case Study 21

## Sovereign Arabic Agent Platform for a Saudi Telecommunications Group

| | | | |
|---|---|---|---|
| **Industry** | Telecommunications & Digital Services | **Headquarters** | Saudi Arabia |
| **Operating Region** | Saudi Arabia, with subsidiaries in Kuwait, Bahrain, and Egypt | **Regulatory Context** | Saudi PDPL · SDAIA AI Ethics Principles · CST regulations · NCA Essential Cybersecurity Controls · Data localisation rules |

## Business Challenge

A Riyadh-based telco group wants to launch Arabic-first AI agents for consumer care, B2B sales and internal operations across 40 million subscribers, but regulators require in-Kingdom data residency, models must handle Gulf and Egyptian dialects, and each business unit is building its own bots with no shared guardrails, identity or evaluation. Existing models underperform on Arabic intent and generate culturally inappropriate content.

## Transformation Objective

Design a sovereign, multi-tenant agent platform with Arabic-optimised models, shared identity, guardrails, evaluation and observability, from which business units compose customer-care, sales and operations agents that can act on billing, provisioning and CRM systems.

## Agentic Architecture Brief

| Agent | Owns end-to-end | Autonomy level |
|---|---|---|
| **Customer Care Agent** | Resolves billing, roaming, plan changes in Arabic dialects | L3 – acts within account authority |
| **B2B Sales Agent** | Qualifies leads, configures enterprise quotes | L2 – recommend to account managers |
| **Network Ops Agent** | Triages faults, opens tickets, proposes fixes | L3 – acts in IT, human in RAN changes |
| **Guardrail & Evaluation Agent** | Runs Arabic content safety, dialect quality, cultural evals | L4 – autonomous gating |
| **Tenant Governance Agent** | Enforces platform policies per business unit | L4 – autonomous |

**Orchestration:** Platform team operates the agent runtime; each business unit registers agents via a *catalogue*; shared tools exposed through MCP with per-tenant scopes; all inference in-Kingdom.

**Governance, safety and evaluation:** PDPL residency, SDAIA ethics documentation, NCA controls; Arabic red-teaming; human review for religious or cultural sensitivity; consent and disclosure to subscribers.

## Expected Outcomes

Care contacts deflected 45% with Arabic CSAT at parity with human agents, B2B quote time down 60%, one governed platform instead of eleven bots.

## Why Now (2026–2028)

Saudi PDPL has been fully enforced by SDAIA since 14 September 2024 and 2026 is the Kingdom's declared Year of AI; the Azure Saudi Arabia East region goes live in Q4 2026, making in-Kingdom agent inference possible for the first time.

## Business Case

**Vision 2030 digital targets and a national AI push reward operators who ship Arabic-first agents first, at scale and in-Kingdom.**

Value at stake: care deflection of 45% across 40 million subscribers saves SAR 400 million a year, and Arabic-first B2B sales agents accelerate a SAR 2 billion enterprise pipeline. Cost of inaction: eleven separate bots create regulatory exposure under PDPL and SDAIA guidelines, and national digital targets reward operators that ship first. Executive sponsor: Chief Digital Officer, with the Chief Compliance Officer. Success measures: deflection rate with Arabic CSAT parity, quote cycle time, number of governed agents on the platform, and regulatory findings.
