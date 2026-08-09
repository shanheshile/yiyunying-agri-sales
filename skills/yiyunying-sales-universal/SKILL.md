---
name: yiyunying-sales-universal
description: Cross-industry, non-personal export sales workflow for customer evidence, multilingual WhatsApp/email, CRM lifecycle, quotations, delivery or freight, PI, payment risk, reporting and controlled automation. Use when the deployment is not limited to agricultural machinery and supplies its own product, pricing, material and lifecycle adapters.
---

# Yiyunying Sales Universal

This is the all-company entry point. It never assumes an industry, product,
salesperson, team, CRM vocabulary, price source, website or external account.

## Required composition

1. Use `$yiyunying-sales-core` for identity, evidence, intent, outbound, CRM and audit state.
2. Use `$yiyunying-trade-quote-pi` for export quotation, freight/delivery, PI and payment controls.
3. Use `$yiyunying-no-auto-follow` unless a current `$yiyunying-auto-authorized` receipt is active.
4. Load exactly one deployment product pack and profile/source registry before making product or identity claims.

Read `references/universal-deployment.md`. An agricultural deployment may add
`$yiyunying-agri-product-pack`; other industries must provide an equivalent
evidence-backed product adapter instead of reusing agricultural assumptions.
