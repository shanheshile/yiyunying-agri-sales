# Portable Prompt Pack

This directory makes the workflow usable on AI platforms that do not load Codex
Skills. It is a compact derivative, not a second source of detailed product or
customer data.

Build only the modules required for the current task:

```powershell
python scripts/build_prompt_pack.py --variant agri --task followup --platform chatgpt
python scripts/build_prompt_pack.py --variant ai3-team --task product --task quote --platform claude
python scripts/build_prompt_pack.py --variant universal --task followup --platform gemini
python scripts/build_prompt_pack.py --variant agri --task measurement --platform generic
```

Use the output as system instructions, project instructions, a Gem/assistant
instruction, or the first message in another tool. Attach live evidence and
deployment configuration separately. Never paste passwords, cookies, tokens,
customer exports or private prices into a public prompt or shared assistant.

The builder estimates tokens with a conservative character heuristic and fails
when the selected modules exceed the configured budget unless
`--allow-over-budget` is explicitly supplied.
