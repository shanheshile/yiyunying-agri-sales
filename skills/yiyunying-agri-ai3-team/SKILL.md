---
name: yiyunying-agri-ai3-team
description: Non-personal agricultural machinery AI3 team workflow for CRM evidence review, WhatsApp/email follow-up, F/D/C/B/A stages, product and material lookup, quotation, freight, PI, public-pool handling and team reporting. Use for the agricultural AI3 team deployment; identity, prices, accounts and source locations must come from deployment configuration.
---

# Yiyunying Agricultural AI3 Team

This is a thin team orchestrator. It contains no salesperson identity, customer
record, private price, freight contact, credential or browser state.

## Required composition

1. Use `$yiyunying-sales-core` for every customer, channel, stage, CRM and public-pool action.
2. Use `$yiyunying-agri-product-pack` for every agricultural product, parameter, packing and material claim.
3. Use `$yiyunying-trade-quote-pi` for every price, freight, quote, PI or payment action.
4. Use `$yiyunying-no-auto-follow` unless a valid `$yiyunying-auto-authorized` receipt is active.
5. Apply `references/team-defaults.md` only after deployment identity, accounts and source registry are loaded.

Reuse the distribution runbook and reporting contract from
`$yiyunying-agri-sales-distribution`. Team defaults may narrow its behavior but
cannot weaken evidence, confirmation, privacy, deduplication or read-back gates.
