# Universal Deployment Contract

## Required adapters

Configure external seller identity, industry and product taxonomy, stable product
IDs, current parameters, price/cost authority, material authority, lifecycle
mapping, CRM/channel adapters, delivery or freight sources, timezone, work hours,
confirmation policy, report fields and credential references.

Credentials remain in the platform credential store. Customer evidence, runtime
ledgers and automation receipts remain outside the skill source.

## Product contract

Every selected item must resolve stable ID, exact model/configuration, quantity,
public parameters, packing/delivery inputs, image/video binding, source, observed
time, effective time and validation status. Missing or conflicting fields block
only the affected action. Never infer one industry's certification, warranty,
packing, lead time or logistics rules for another industry.

## Lifecycle and communication

Map the deployment's stages to evidence-backed meanings before changing CRM.
Read all available customer channels and commercial artifacts, choose the latest
real intent, respect refusal/future-contact protection, write concise customer
facts, and verify sends and CRM writes by read-back.

## Commercial boundary

An internal calculation is not an externally authorized quote. Product price,
delivery/freight scope, tax/customs, PI, payment and regulated documents require
the deployment's exact confirmation policy. Automation cannot grant itself a
broader permission than the current receipt.
