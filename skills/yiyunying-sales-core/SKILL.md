---
name: yiyunying-sales-core
description: Evidence-first sales control for customer identity, intent review, queue eligibility, stage transitions, multilingual outbound quality, send verification, CRM write-back, public-pool handling, deduplication, and resumable action ledgers. Use whenever a task reads or changes customer, WhatsApp, email, CRM, stage, follow-up, refusal, public-pool, or daily sales state.
---

# Yiyunying Sales Core

Use this skill before any customer-facing or CRM-changing action. Product facts,
prices and freight belong to their dedicated skills. Permission belongs to the
selected permission-mode skill.

## Load references

- Read `references/evidence-and-identity.md` before interpreting a customer.
- Read `references/state-queue-and-protection.md` before selecting or changing a stage, queue or public-pool state.
- Read `references/outbound-and-channel-verification.md` before drafting or sending WhatsApp or email.
- Read `references/crm-and-audit-ledger.md` before writing CRM or reporting counts.

## Required workflow

1. Bind the exact customer by stable CRM ID. Without one, require exact normalized phone or email plus a corroborating field.
2. Check whether a valid background-research result already exists. Run it at most once and record it before normal follow-up.
3. Read complete inquiry, contact, CRM dynamics, WhatsApp, email, quote, PI, order, payment and shipping evidence that is relevant to the action.
4. Resolve message direction, sender, language, country, latest intent, confirmed product facts, current blocker and time protection.
5. Classify the action as `eligible`, `protected`, `blocked`, `confirmation-required`, or `ready-for-public-pool`.
6. Draft one meaningful next action in the customer's language. Do not contact a group or a customer who gave a future-contact time before that time.
7. Run channel preflight and deduplication. A missing or conflicting fact remains missing; never guess it.
8. Perform only actions allowed by the active permission mode. Treat a click as pending until read-back proves the result.
9. Write concise customer business facts to CRM, adjust the stage from verified evidence, then independently read both back.
10. Append the verified action result to the runtime ledger and report failures separately from completed work.

## Fail closed

Stop the affected action on identity ambiguity, message-direction ambiguity,
missing readable content, stale or conflicting evidence, protected timing,
duplicate risk, high-risk claims, failed channel verification, failed CRM
read-back, or a stage change unsupported by customer evidence.

