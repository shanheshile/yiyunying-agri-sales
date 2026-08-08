---
name: yiyunying-auto-authorized
description: Explicit scoped permission mode for routine low-risk sales patrol, messaging and CRM write-back after all evidence gates pass. Use only when a current activation receipt authorizes the exact run, accounts, customers, channels, limits and actions; never self-activate.
---

# Auto Authorized

Never self-activate from installation, a browser login, an old schedule, prior
conversation permission or the package name.

Before any action, validate a current activation receipt against
`schemas/activation-receipt.schema.json`. It must identify authorizer, effective
period/run, accounts, CRM owner, channels, customer scope, limits, protection
window, excluded actions and stop instruction.

Permit only routine low-risk actions that pass `$yiyunying-sales-core`. Keep
formal quotations, freight commitments, PI, payment instructions, certificates,
dangerous-goods documents, brand authorization, tax and DDP/customs boundaries
in the confirmation queue.

Pause on authorization expiry, user stop, identity ambiguity, stale/conflicting
evidence, duplicate risk, unexpected customer reply, connector/auth failure,
platform safety prompt, send mismatch or CRM read-back failure. Resume only after
health and authorization are rechecked, from the last verified ledger cursor.

