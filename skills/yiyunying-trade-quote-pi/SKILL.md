---
name: yiyunying-trade-quote-pi
description: Deterministic agricultural machinery quotation, freight and PI control for EXW, FCA, FOB, CFR, CNF, CIF, DAP, DDU and DDP. Use when a customer asks for price, delivery, freight, customs, landed cost, a formal quotation, PI, payment terms, or when comparing forwarder replies and validating product/currency/profit/packing data.
---

# Yiyunying Trade Quote And PI

Load the exact customer evidence with `$yiyunying-sales-core` and exact product
evidence with `$yiyunying-agri-product-pack` before using this skill.

## Load references

- Read `references/quote-control.md` for price, currency, profit and quote-builder rules.
- Read `references/freight-control.md` for inquiry, forwarder capability and comparison.
- Read `references/pi-control.md` before creating, checking or sending a PI or payment detail.

## Required result

Return confirmed inputs, missing inputs, source/freshness, formula, per-currency
calculation, inclusions, exclusions, risk, recommended option and confirmation
status. Keep every external formal amount, PI and payment instruction in
`confirmation-required` until the user approves that exact customer version.

Never expose internal cost, profit, forwarder price or supplier identity to the
customer. Never invent a tax, duty, certificate, DDP boundary or delivery promise.

