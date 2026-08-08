---
name: yiyunying-agri-product-pack
description: Agricultural machinery product evidence and selection for tractors, remote-control mowers, robotic mowers, excavators, implements, attachments, packaging, certificates, warranty, images, videos, and current catalog lookup. Use when identifying a product, checking parameters, selecting materials, preparing freight inputs, or preventing stale/wrong product claims.
---

# Yiyunying Agricultural Product Pack

Use exact product evidence, not a remembered model name or an old customer quote.
This skill does not decide customer stage, permission, price or freight scope.

## Load references

- Read `references/source-resolution.md` before looking up or reconciling product data.
- Read `references/qualification-and-materials.md` before recommending a product or sending images/videos.
- Read `references/packing-certification-warranty.md` before freight, quotation, PI, certificates, delivery or after-sales claims.

## Required workflow

1. Extract product category, use, work area, terrain/slope, vegetation/material, required width/capacity, quantity, destination, registration/emission need and attachments.
2. Search the configured live catalog by exact stable product ID when known; otherwise search model/name and resolve duplicates before selecting.
3. Merge only effective-dated, field-specific overrides that match the same product and configuration.
4. Return every decision field with source, observed/effective time and status: confirmed, historical, estimated, missing or conflicting.
5. Select exact-model materials. A system recommendation or generic image is not product evidence.
6. Mark unresolved data `待确认` and stop affected quotation, freight or certificate actions.

Do not expose internal cost, margin, supplier, factory or private source details to
customers or unrelated parties.

