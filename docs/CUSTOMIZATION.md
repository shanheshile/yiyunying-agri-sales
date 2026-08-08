# Customization

## Stable extension points

- Change operational defaults in `config/defaults.json`.
- Register CRM, product, material, quote and freight adapters in a local source registry validated by `schemas/source-registry.schema.json`.
- Add organization identity and brand routing in a private profile; do not edit reusable core rules for one salesperson.
- Add product changes as effective-dated, exact-ID field overlays. Do not rewrite the original snapshot without a new manifest and checksum.
- Add new product families to the product qualification reference and data schema before using them in customer work.
- Add report fields in the deployment reporting reference while retaining verified/unknown distinctions.

## Rule precedence

Safety and evidence boundaries cannot be weakened by a template or UI default.
A current direct user instruction may narrow or explicitly authorize one run. A
one-run limit, exception or wording does not become a permanent rule unless it is
added to the deployment configuration with an effective date.

## Change process

1. Record the reason and effective date.
2. Update the smallest owning layer.
3. Add or update a deterministic test or coverage check.
4. Run public validation and all tests.
5. Bump semantic version and changelog for released behavior.
6. Refresh private vendored core and its upstream lock after the public release.

Do not append new facts to a historical monolithic rule file. Replace or version
the owning structured record so the current source remains unambiguous.

