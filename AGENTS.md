# AI Agent Entry

Use the native `skills/` entry points when the agent supports Codex Skills.
For other agents, build a compact prompt with `scripts/build_prompt_pack.py`.
Load only one deployment variant and the modules needed for the current task.
Default to `no-auto-follow`; never infer credentials, identity, prices or sends.
