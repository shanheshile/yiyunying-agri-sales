#!/usr/bin/env python3
"""Create a public product catalog using an explicit allowlist."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def products_of(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    for key in ("products", "data", "items", "records"):
        if isinstance(payload.get(key), list):
            return payload[key]
    return []


def pick(item: dict[str, Any], *paths: str) -> Any:
    for path in paths:
        value: Any = item
        for part in path.split("."):
            if not isinstance(value, dict) or part not in value:
                value = None
                break
            value = value[part]
        if value not in (None, "", []):
            return value
    return None


def sanitize(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(pick(item, "id", "raw.id") or ""),
        "model": pick(item, "model", "raw.productModel"),
        "code": pick(item, "code", "raw.productCode"),
        "nameEn": pick(item, "nameEn", "raw.productNameEn", "raw.productName"),
        "nameLocal": pick(item, "nameCn", "raw.productNameCn"),
        "category": pick(item, "category", "raw.categoryName"),
        "specs": pick(item, "specs", "raw.productParams") or {},
        "compatibility": pick(item, "compatibility") or {},
        "publicDescription": pick(item, "raw.productDescriptionEn", "raw.aiDescriptionStandard"),
        "publicMaterials": {
            "images": pick(item, "raw.productImages") or [],
            "mainImage": pick(item, "raw.mainImageUrl"),
            "videos": pick(item, "raw.productVideos", "raw.videoUrls") or [],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8-sig"))
    rows = [sanitize(x) for x in products_of(payload)]
    rows = [x for x in rows if x["id"] and x["model"]]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"schemaVersion": "1.0", "productCount": len(rows), "products": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} redacted products to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

