# Architecture

The project separates four concerns that must not overwrite one another:

1. **Sales core** owns customer evidence, queue, state, outbound and CRM rules.
2. **Product pack** owns product facts, packing, certificates and material lookup.
3. **Profile/overlay** belongs to the deploying organization or private user and owns identity, brands, private prices and source locations.
4. **Permission mode** only decides whether the workflow may inspect, send or write automatically.

The distribution orchestrator composes these concerns. The automation controller
does not contain product facts or customer data and cannot grant itself
permission.

## Deployment entry points

- `yiyunying-agri-sales-distribution`: identity-free agricultural group distribution.
- `yiyunying-agri-ai3-team`: non-personal AI3 stage/report defaults over the same agricultural core.
- `yiyunying-sales-universal`: all-company cross-industry entry point; requires a deployment product adapter.
- Private personal deployments add their own profile, source/price overlays and automation controller without copying the public references.

## Source precedence

For customer intent: direct current inbound message, verified CRM record, prior
quote/order evidence, then historical notes. For product data: effective-dated
user override, live exact product detail by stable ID, approved snapshot, then
historical documents. For shipping: a final factory packing sheet overrides a
catalog snapshot; a freight quote never changes product facts.

Every value used for a customer decision carries a source, observed time,
effective time when applicable, customer/product binding and confidence. A
conflict is reported and blocks the affected action instead of being silently
resolved.

## Generated and runtime data

Generated releases, action ledgers, browser state, customer records and
credentials are excluded from Git. Runtime state must be stored outside the
skill source and keyed by stable customer and action IDs.
