---
name: yiyunying-agri-auto-follow-generic
description: Generic Codex scheduled-run controller for agricultural sales inbox review, precision queues, routine customer follow-up and CRM verification. Use only for an explicitly configured automation; it is paused and dry-run by default and never self-authorizes high-risk sends.
---

# Generic Agricultural Auto Follow

This controller is separate from the business skill and contains no salesperson
identity or private data.

1. Load `$yiyunying-agri-sales-distribution`, the deployment source registry, runtime ledger and current activation receipt.
2. If the receipt is missing, expired or does not match the run, remain dry-run and produce a review queue only.
3. Check channel and CRM health with a non-destructive read. Do not extract credentials or bypass authentication.
4. Before any customer action, apply the same background gate to every new or existing customer: search CRM dynamics, run one AI background check only when absent, wait, bind the result to the exact customer, write useful facts or exactly `背调无信息`, and read it back.
5. Do not send, change stage, move public pool or mark handled until the background entry and all required customer evidence pass read-back. A research failure blocks only that customer and enters the exception queue.
6. Process real inbound questions before proactive queues; deduplicate by stable customer and action key.
7. Apply customer protection, channel limits, content quality, confirmation and public-pool rules.
8. Keep quote, freight commitment, PI, payment, certificate, tax/customs and dangerous-goods work in the confirmation queue.
9. Verify every allowed send/write, update the ledger cursor and report exact counts and failures.

Use `scripts/customer_preflight.py` when available to test the deterministic gate.
`outboundAllowed` or `crmStageWriteAllowed` must be true before the corresponding
action is attempted.

The template under `automations/generic/` is not active installation. Never enable,
resume or widen it merely because this skill is installed.
