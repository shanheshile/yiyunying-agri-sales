#!/usr/bin/env python3
"""Build a compact, platform-neutral prompt from selected modules."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").strip()


def select(mapping: dict[str, str], key: str, kind: str, root: Path) -> Path:
    try:
        relative = mapping[key]
    except KeyError as exc:
        choices = ", ".join(sorted(mapping))
        raise ValueError(f"unknown {kind} {key!r}; choose one of: {choices}") from exc
    path = (root / relative).resolve()
    if not path.is_file():
        raise ValueError(f"missing {kind} module: {path}")
    return path


def compose(root: Path, variant: str, tasks: list[str], platform: str, extras: list[Path]) -> str:
    manifest = json.loads(read(root / "manifest.json"))
    selected = [
        (root / manifest["core"]).resolve(),
        select(manifest["platforms"], platform, "platform", root),
        select(manifest["variants"], variant, "variant", root),
    ]
    selected.extend(select(manifest["tasks"], task, "task", root) for task in tasks)
    selected.extend(path.resolve() for path in extras)
    missing = [str(path) for path in selected if not path.is_file()]
    if missing:
        raise ValueError(f"missing prompt module(s): {', '.join(missing)}")
    return "\n\n".join(read(path) for path in selected) + "\n"


def estimate_tokens(text: str) -> int:
    ascii_chars = sum(ord(char) < 128 for char in text)
    non_ascii_chars = len(text) - ascii_chars
    return math.ceil(ascii_chars / 4 + non_ascii_chars * 1.2)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1] / "portable")
    parser.add_argument("--variant", default="agri")
    parser.add_argument("--task", action="append", required=True)
    parser.add_argument("--platform", default="generic")
    parser.add_argument("--extra", action="append", type=Path, default=[])
    parser.add_argument("--budget-tokens", type=int)
    parser.add_argument("--allow-over-budget", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    manifest = json.loads(read(root / "manifest.json"))
    tasks = list(dict.fromkeys(args.task))
    try:
        result = compose(root, args.variant, tasks, args.platform, args.extra)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"cannot build prompt pack: {exc}", file=sys.stderr)
        return 2
    estimate = estimate_tokens(result)
    budget = args.budget_tokens or int(manifest["defaultTokenBudget"])
    if estimate > budget and not args.allow_over_budget:
        print(f"prompt estimate {estimate} exceeds token budget {budget}", file=sys.stderr)
        return 2
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(result)
    print(f"estimated_tokens={estimate}; budget={budget}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
