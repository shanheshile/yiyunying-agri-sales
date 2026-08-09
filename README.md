# Yiyunying Agricultural Sales Skill Suite

This public Codex plugin provides an evidence-first workflow for agricultural
machinery export sales. It is deliberately free of personal identities,
customer records, credentials, internal cost prices, private freight contacts,
and browser session data.

## Included skills

| Skill | Responsibility |
| --- | --- |
| `yiyunying-sales-core` | Customer identity, evidence audit, queue, stage, outbound verification, CRM write-back |
| `yiyunying-agri-product-pack` | Product, parameter, packaging, certification, warranty, image and video source resolution |
| `yiyunying-trade-quote-pi` | EXW/FOB/CIF/CFR/DAP/DDU/DDP checks, freight comparison, currency, quotation and PI validation |
| `yiyunying-no-auto-follow` | Draft-only permission mode |
| `yiyunying-auto-authorized` | Explicit, scoped, revocable automation permission mode |
| `yiyunying-agri-sales-distribution` | Generic end-to-end agricultural sales orchestrator |
| `yiyunying-agri-auto-follow-generic` | Generic scheduled-run controller; paused and dry-run by default |
| `yiyunying-agri-ai3-team` | Non-personal AI3 team defaults over the agricultural distribution core |
| `yiyunying-sales-universal` | All-company, cross-industry orchestrator with deployment-supplied product adapters |

## Safety defaults

- External sending, CRM writes, public-pool moves and scheduled patrols are off by default.
- Product facts, cost, packing, freight and certificates require source evidence and freshness.
- Formal prices, PI, payment details, tax statements, certificates and freight commitments require human confirmation.
- A click is not a successful send or write. Every action needs channel or CRM read-back evidence.
- Explicit refusal is different from silence, hesitation, price concern or a future-contact date.

## Configure

1. Copy `config/sources.example.json` to `config/sources.local.json`.
2. Register the current product catalog, material library, quote builder, CRM and channel adapters.
3. Keep credentials in the platform credential store or environment variables. Never place tokens, cookies or passwords in this repository.
4. Run the validator before use:

```powershell
python scripts/validate_suite.py --root . --public
```

The suite accepts product and sales evidence through the JSON schemas under
`schemas/`. `config/defaults.json` contains editable policy defaults. A one-run
instruction may narrow those defaults but must not silently weaken a safety or
evidence boundary.

## Build and install

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build-release.ps1
powershell -ExecutionPolicy Bypass -File scripts/install-skills.ps1
```

The installer backs up colliding skills before copying them into
`$CODEX_HOME/skills`. The generated ZIP and checksum manifest are placed under
`release/` and are not committed.

## Automation

`automations/generic/agri-sales-daily.automation.toml.example` is a template,
not an active schedule. Test the same prompt manually in dry-run mode, verify
data access and read-back, then create or enable a schedule through Codex's
automation controls. See `docs/AUTOMATION.md`.

## Other AI platforms and token use

The native Codex Skills remain the detailed source. For ChatGPT projects/custom
instructions, Claude projects, Gemini Gems/CLI and generic assistants, build a
compact prompt containing only one deployment variant and the current task:

```powershell
python scripts/build_prompt_pack.py --variant ai3-team --task followup --platform chatgpt
```

See `portable/README.md`. Credentials are referenced through environment,
browser/session or OS credential stores and are never embedded in a prompt pack.

## Public/private boundary

Use this repository for reusable workflow and schemas. Keep personal identity,
live customer data, internal prices, supplier names, private freight contacts,
account-specific URLs and runtime memories in a separate private repository.
See `docs/DATA-GOVERNANCE.md`.
