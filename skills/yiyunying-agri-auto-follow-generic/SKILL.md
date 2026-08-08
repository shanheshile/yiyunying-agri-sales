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
4. Process real inbound questions before proactive queues; deduplicate by stable customer and action key.
5. Apply customer protection, channel limits, content quality, confirmation and public-pool rules.
6. Keep quote, freight commitment, PI, payment, certificate, tax/customs and dangerous-goods work in the confirmation queue.
7. Verify every allowed send/write, update the ledger cursor and report exact counts and failures.

The template under `automations/generic/` is not active installation. Never enable,
resume or widen it merely because this skill is installed.

