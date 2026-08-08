---
name: yiyunying-agri-sales-distribution
description: Generic end-to-end agricultural machinery export sales workflow combining customer evidence, WhatsApp/email, CRM stages, product and material lookup, tractors/mowers/implements/excavators, quotation, freight, PI, payment, public-pool handling, daily action lists and reports. Use for reusable non-personal sales work; defaults to draft-only unless an explicit permission mode is active.
---

# Yiyunying Agricultural Sales Distribution

This is the public orchestrator. It contains no salesperson identity, customer
history, private cost, freight contacts or credentials.

## Required composition

1. Use `$yiyunying-sales-core` for customer evidence, queue, stage, outbound and CRM.
2. Use `$yiyunying-agri-product-pack` for product, parameters, packing and materials.
3. Use `$yiyunying-trade-quote-pi` for every price, freight, quote, PI or payment task.
4. Use `$yiyunying-no-auto-follow` unless `$yiyunying-auto-authorized` has a valid current receipt.

Read `references/runbook.md` for the end-to-end procedure and
`references/reporting.md` for per-customer action lists and daily reporting.

## Deployment configuration

Load `../../config/defaults.json`, then merge an optional local source registry
validated against `../../schemas/source-registry.schema.json`. A deployment may
narrow permissions and customize identity, brands, hours, limits, product sources,
profit semantics and report fields. It must not silently weaken evidence,
confirmation, privacy or read-back requirements.

When identity or source configuration is missing, ask only for the minimum field
needed for the current action. Use `待确认` internally; never send a placeholder
name, email, phone, website, price, certificate or delivery term to a customer.

