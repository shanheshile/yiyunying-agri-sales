# Data Governance

## Public repository

Allowed: reusable rules, schemas, redacted examples, deterministic scripts and
connector configuration templates.

Forbidden: customer records, personal contact details, internal costs, supplier
or freight contact lists, account-specific tokens, cookies, passwords, mailbox
contents, automation memories, local browser profiles and absolute user paths.

## Private deployment

A private overlay may contain identity, internal prices, approved packaging
overrides and a product snapshot. Credentials still remain outside Git. Customer
records and runtime memories remain outside both repositories unless a separate,
purpose-built encrypted system has been approved.

## Evidence grades

- `confirmed-current`: direct current customer, live product detail, final packing sheet or verified order record.
- `confirmed-historical`: valid but older evidence; check freshness before reuse.
- `derived`: calculated from confirmed inputs; retain formula and units.
- `unverified`: incomplete, conflicting or inferred; never use for commitments.

## Retention and redaction

Release validation scans for credentials, private paths, phone/email patterns,
customer identifiers and internal price markers. A public build fails on a
match. Private builds fail on credentials and runtime/customer evidence even
when private pricing is allowed.

