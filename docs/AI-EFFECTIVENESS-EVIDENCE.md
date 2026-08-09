# AI Effectiveness Evidence Standard

## Purpose

This standard turns an AI workflow into auditable operational evidence. It is
designed for internal improvement reviews and award programs that require real
use, net efficiency, quality, adoption, value, security and repeatability.

## Required sequence

1. Freeze a measurable baseline for the original workflow.
2. Define the AI workflow, owner, users, task boundary and reusable artifact.
3. Run real business tasks and record every time/cost component.
4. Compare verified before/after data; retain negative and failed runs.
5. Collect actual-user validation without customer data.
6. Review quality, risk, privacy, maintenance and reproducibility.
7. Generate an aggregate report and preserve source evidence outside Git.

## Runtime files

Keep real records outside the repository, for example:

```text
runtime/effectiveness/project.json
runtime/effectiveness/runs.jsonl
runtime/effectiveness/report.md
```

`project.json` follows `schemas/effectiveness-project.schema.json`. Each JSONL
row follows `schemas/effectiveness-run.schema.json`. Use random run IDs and
pseudonymous actor IDs. Do not include names, phones, emails, customer messages,
CRM IDs, quotes, credentials or order/shipping documents.

Append one run with `scripts/effectiveness_record.py`. A `verified` run requires
a SHA-256 hash of a separately retained evidence receipt. The ledger stores the
hash, not the receipt contents. Keep pending or failed work; do not remove it to
improve the result.

Use one distinct per-run receipt. Reusing a receipt hash for multiple verified
runs is rejected. A counted user must both appear in verified task records and
complete actual-user validation under the same pseudonymous ID.

## Calculations

Per run:

```text
net saved minutes = baseline total
                  - AI execution
                  - input preparation
                  - human review
                  - rework
                  - allocated maintenance
```

Project:

```text
net efficiency % = total net saved minutes / total baseline minutes * 100
annual saved hours = average net saved minutes * verified annual task volume / 60
annual net value = annual saved hours * standard hourly labor cost
                 + verified annual direct cost savings
                 + verified annual added gross profit
                 - annual AI/tool/API/procurement/maintenance cost
                 - annual quantified business error loss
```

The aggregate annual-volume formula is valid only for one task type. For mixed
work, populate `annualTaskVolumeByType`; the tool weights each type by its own
verified average and annual volume. Otherwise annual saved hours and value remain
unknown rather than applying a distorted task mix.

Do not treat missing monetary inputs as zero for an award gate.

## Quality, risk and sustainability

Set at least one core quality metric and one risk metric before measurement.
Record direction, baseline/current values and allowed degradation or maximum
risk. A material quality decline, excess error/rework/complaint rate, security
incident, inconsistent evidence or missing accountable owner blocks eligibility.

For staged awards, run a 90-day sustainability review. Require maintained usage,
at least 50% active-user retention, stable quality, no disqualifying incident,
consistent data, assigned maintainer and data-security compliance.

## Deployment policy boundary

Configure organization-specific award tiers and staged-payment thresholds in
the private `awardPolicy` section of `project.json`. The public engine does not
embed internal award names, prize amounts or thresholds. This keeps the reusable
calculation logic public while internal policy remains in the authorized private
deployment.

## Tool

```powershell
python scripts/effectiveness_report.py `
  --project runtime/effectiveness/project.json `
  --runs runtime/effectiveness/runs.jsonl `
  --format markdown `
  --output runtime/effectiveness/report.md
```

The award duration uses the smaller of the declared production period and the
observed span of verified real-business runs. This prevents a manually entered
start date from overstating actual usage.

The generated report is an evidence summary, not proof by itself. Retain source
time studies, user validation and business-system evidence for human review.
