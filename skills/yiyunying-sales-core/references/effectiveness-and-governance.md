# Effectiveness And Governance

## Evidence chain

An AI improvement is valid only when it has a measured original workflow, a
defined AI workflow, repeated real-business runs, before/after comparison,
actual-user validation and a reusable artifact. Ideas, demonstrations and one-
off generated content are not production evidence.

## Net time

For each verified task record:

`net saved minutes = baseline total - AI execution - input preparation - human review - rework - allocated maintenance`

Include every human and maintenance step. Keep negative results. Aggregate only
verified real-business runs, then calculate `net efficiency % = total net saved /
total baseline * 100`.

## Annual net value

Use a verified annual task volume and standard labor-hour cost:

`annual net value = annual saved hours * hourly cost + verified direct cost savings + verified added gross profit - AI/tool/API/procurement/maintenance cost - quantified business error loss`

Unknown inputs remain unknown; do not convert them to zero to claim eligibility.
For mixed task types, annualize each type with its own verified annual volume;
do not apply one pooled average to an unrelated production mix.

## Quality and risk gates

Define at project start at least one core quality metric and one risk metric,
including direction, baseline/current value and tolerance/limit. Efficiency is
invalid when quality materially degrades, error/rework/complaint risk exceeds the
limit, data security fails, evidence is inconsistent or responsibility is unclear.

## Privacy and low-token instrumentation

- Keep customer identity, messages, quotes and order details in the authorized business system.
- The measurement ledger stores a random run ID, pseudonymous actor ID, task type, dates, duration components, verification state and quality/risk booleans only.
- Require one distinct evidence-receipt hash per verified run. Count a user only when the same pseudonymous ID has both verified use and actual-user validation.
- Never store phone, email, customer name, message text, credentials or external-system record IDs in the measurement ledger.
- Append metrics after operational read-back. Evaluate them in a separate daily/weekly job; do not load the historical ledger into each customer prompt.
- Record tool/API cost, maintenance and exceptions even when they reduce the claimed benefit.

## Sustainability

For external review or internal rollout, preserve maintainer ownership, active-user count,
frequency, quality and incident evidence. Recheck after 90 days. A user decline
over 50%, long-term disuse, quality/business/customer incident, data mismatch,
missing maintainer or security/compliance failure blocks sustained-success claims.
Confirm that usage frequency is maintained. Repetitive roles also require
multiple cross-validations; one successful sample is insufficient.
