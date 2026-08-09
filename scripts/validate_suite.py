#!/usr/bin/env python3
"""Validate the public skill suite without third-party dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
SECRET_PATTERNS = {
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "generic API token": re.compile(r"(?i)\b(api[_-]?key|access[_-]?token|password)\s*[:=]\s*['\"][^$<{][^'\"]{7,}"),
    "cookie header": re.compile(r"(?i)\bcookie\s*:\s*[^$<{\n]{12,}"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}
PUBLIC_FORBIDDEN = {
    "personal name": re.compile(r"曹桂铭|\bLoki\b", re.IGNORECASE),
    "personal email": re.compile(r"sales35@qilutractor\.com", re.IGNORECASE),
    "personal phone": re.compile(r"188[\s-]*8088[\s-]*9296"),
    "Windows user path": re.compile(r"(?i)C:\\Users\\(Administrator|ADMINI~1)\\"),
    "private supplier price override": re.compile(r"鲁源|魔亨|58[, ]?500|49[, ]?800|37[, ]?500"),
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def validate_json(root: Path, errors: list[str]) -> None:
    for path in root.rglob("*.json"):
        if any(part in {".git", "dist", "release", "runtime"} for part in path.parts):
            continue
        try:
            json.loads(read_text(path))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"invalid JSON {path.relative_to(root)}: {exc}")


def parse_frontmatter(path: Path, errors: list[str]) -> dict[str, str]:
    text = read_text(path)
    match = FRONTMATTER_RE.search(text)
    if not match:
        errors.append(f"missing YAML frontmatter: {path}")
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def validate_skills(root: Path, errors: list[str]) -> None:
    skills_root = root / "skills"
    if not skills_root.is_dir():
        errors.append("missing skills directory")
        return
    for skill_dir in sorted(p for p in skills_root.iterdir() if p.is_dir()):
        skill = skill_dir / "SKILL.md"
        agent = skill_dir / "agents" / "openai.yaml"
        if not skill.is_file():
            errors.append(f"missing {skill.relative_to(root)}")
            continue
        meta = parse_frontmatter(skill, errors)
        if meta.get("name") != skill_dir.name:
            errors.append(f"skill name/folder mismatch: {skill_dir.name} vs {meta.get('name')}")
        if not meta.get("description"):
            errors.append(f"missing description: {skill.relative_to(root)}")
        lines = read_text(skill).count("\n") + 1
        if lines > 500:
            errors.append(f"SKILL.md exceeds 500 lines: {skill.relative_to(root)} ({lines})")
        if not agent.is_file():
            errors.append(f"missing {agent.relative_to(root)}")


def scan_tree(root: Path, public: bool, errors: list[str]) -> None:
    ignored = {".git", "dist", "release", "runtime", "__pycache__"}
    for path in root.rglob("*"):
        if not path.is_file() or any(part in ignored for part in path.parts):
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".zip", ".pdf"}:
            continue
        try:
            text = read_text(path)
        except UnicodeDecodeError:
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{label} found in {path.relative_to(root)}")
        if public and path.resolve() != Path(__file__).resolve():
            for label, pattern in PUBLIC_FORBIDDEN.items():
                if pattern.search(text):
                    errors.append(f"public boundary violation ({label}) in {path.relative_to(root)}")


def validate_automation(root: Path, errors: list[str]) -> None:
    for path in root.glob("automations/**/*.toml*"):
        text = read_text(path)
        if 'status = "PAUSED"' not in text:
            errors.append(f"automation template is not paused: {path.relative_to(root)}")
        if "$yiyunying-agri-auto-follow-generic" not in text:
            errors.append(f"automation does not explicitly invoke its controller: {path.relative_to(root)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--public", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []

    manifest = root / ".codex-plugin" / "plugin.json"
    if not manifest.is_file():
        errors.append("missing .codex-plugin/plugin.json")
    validate_json(root, errors)
    validate_skills(root, errors)
    scan_tree(root, args.public, errors)
    validate_automation(root, errors)

    required = [
        "yiyunying-sales-core",
        "yiyunying-agri-product-pack",
        "yiyunying-trade-quote-pi",
        "yiyunying-no-auto-follow",
        "yiyunying-auto-authorized",
        "yiyunying-agri-sales-distribution",
        "yiyunying-agri-auto-follow-generic",
        "yiyunying-agri-ai3-team",
        "yiyunying-sales-universal",
    ]
    for name in required:
        if not (root / "skills" / name / "SKILL.md").is_file():
            errors.append(f"missing required skill: {name}")

    for portable in ("manifest.json", "core.md", "README.md"):
        if not (root / "portable" / portable).is_file():
            errors.append(f"missing portable prompt component: {portable}")
    if not (root / "scripts" / "build_prompt_pack.py").is_file():
        errors.append("missing portable prompt builder")

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Validation passed: {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
