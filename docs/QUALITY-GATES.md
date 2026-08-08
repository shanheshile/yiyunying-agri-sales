# Quality Gates

Every release must pass:

1. Plugin and Skill metadata validation.
2. JSON parsing and required-file checks.
3. Public privacy/credential/path scan.
4. Product source and overlay binding tests.
5. Profit-semantics and upward-rounding tests.
6. Freight completeness/no-splicing checks.
7. PI required-field and line-total checks.
8. Automation paused/explicit-controller checks.
9. Release checksum generation.

Operational runs add customer-specific gates: exact identity, complete evidence,
protection/dedup, customer-language content, send read-back, CRM read-back and
stage read-back. A release passing static tests does not authorize an external
action.

