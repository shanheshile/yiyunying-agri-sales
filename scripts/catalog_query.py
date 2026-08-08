#!/usr/bin/env python3
"""Search a product catalog and apply exact, effective-dated overlays."""

from __future__ import annotations

import argparse
import copy
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


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


def set_path(item: dict[str, Any], path: str, value: Any) -> None:
    target = item
    parts = path.split(".")
    for part in parts[:-1]:
        target = target.setdefault(part, {})
    target[parts[-1]] = value


def number(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if not isinstance(value, str):
        return None
    match = re.search(r"[-+]?\d+(?:\.\d+)?", value.replace(",", ""))
    return float(match.group()) if match else None


def outer_cbm(value: Any) -> float | None:
    if not isinstance(value, str):
        return None
    dimensions = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", value)]
    if len(dimensions) < 3 or any(x <= 0 for x in dimensions[:3]):
        return None
    a, b, c = dimensions[:3]
    unit = value.casefold()
    if "mm" in unit or ("cm" not in unit and max(a, b, c) >= 100):
        divisor = 1_000_000_000
    elif "cm" in unit or ("mm" not in unit and max(a, b, c) > 10):
        divisor = 1_000_000
    else:
        divisor = 1
    return a * b * c / divisor


def quality_checks(item: dict[str, Any], packaging: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    catalog_issues = pick(item, "validation.issues") or []
    if not isinstance(catalog_issues, list):
        catalog_issues = [str(catalog_issues)]

    gross = number(packaging.get("grossWeightKg"))
    net = number(packaging.get("netWeightKg"))
    reported_cbm = number(packaging.get("cbm"))
    calculated_cbm = outer_cbm(packaging.get("size"))

    if not packaging.get("size"):
        blockers.append("PACKAGE_SIZE_MISSING")
    if gross is None or gross <= 0:
        blockers.append("GROSS_WEIGHT_MISSING")
    if reported_cbm is None or reported_cbm <= 0:
        blockers.append("CBM_MISSING")
    if gross is not None and net is not None and gross < net:
        blockers.append("REPORTED_GROSS_WEIGHT_LT_MACHINE_WEIGHT")
    if reported_cbm and calculated_cbm:
        difference = abs(reported_cbm - calculated_cbm) / calculated_cbm
        if difference > 0.10:
            warnings.append("REPORTED_CBM_DIFFERS_FROM_OUTER_DIMENSIONS")

    freight_terms = ("PACK", "PACKAGE", "GROSS", "CBM", "FREIGHT")
    for issue in catalog_issues:
        normalized_issue = str(issue).upper()
        if any(term in normalized_issue for term in freight_terms):
            blockers.append(f"CATALOG_{normalized_issue}")

    blockers = sorted(set(blockers))
    warnings = sorted(set(warnings))
    return {
        "catalogStatus": pick(item, "validation.status"),
        "catalogIssues": catalog_issues,
        "calculatedOuterCbm": round(calculated_cbm, 4) if calculated_cbm is not None else None,
        "blockers": blockers,
        "warnings": warnings,
        "freightInquiryReady": not blockers,
        "bookingReady": not blockers and not warnings,
    }


def normalized(item: dict[str, Any], include_internal: bool) -> dict[str, Any]:
    product_id = str(pick(item, "id", "raw.id") or "")
    model = str(pick(item, "model", "productModel", "raw.productModel") or "")
    packaging = {
        "size": pick(item, "dimensions.packageSize", "packagingSize", "raw.packagingSize"),
        "grossWeightKg": pick(item, "dimensions.packageWeight", "packagingWeight", "raw.packagingWeight"),
        "netWeightKg": pick(
            item,
            "dimensions.machineWeight",
            "specs.Overall machine weight",
            "specs.weight",
            "raw.attributes.weight",
        ),
        "cbm": pick(item, "dimensions.packageCbm", "packagingVolume", "raw.packagingVolume"),
    }
    result = {
        "id": product_id,
        "model": model,
        "code": pick(item, "code", "productCode", "raw.productCode"),
        "name": {
            "en": pick(item, "nameEn", "productNameEn", "raw.productNameEn", "raw.productName"),
            "local": pick(item, "nameCn", "productNameCn", "raw.productNameCn"),
        },
        "category": pick(item, "category", "categoryName", "raw.categoryName"),
        "specs": pick(item, "specs", "raw.attributes", "raw.productParams") or {},
        "compatibility": pick(item, "compatibility") or {},
        "packaging": packaging,
        "materials": {
            "images": pick(item, "materials.images", "raw.productImages") or [],
            "mainImage": pick(item, "materials.mainImage", "raw.mainImageUrl"),
            "videos": pick(item, "materials.videos", "raw.productVideos", "raw.videoUrls") or [],
        },
        "provenance": {
            "source": pick(item, "validation.sourceFile", "provenance.sourceId"),
            "updatedAt": pick(item, "raw.updateTime", "provenance.observedAt"),
            "validation": pick(item, "validation.status"),
        },
    }
    if include_internal:
        result["pricing"] = {
            "currency": pick(item, "pricing.currency") or "CNY",
            "base": pick(item, "pricing.baseCny", "raw.costPrice"),
            "source": pick(item, "pricing.costSource"),
        }
        result["internal"] = {
            "factory": pick(item, "factory", "raw.factory"),
            "tag": pick(item, "tag", "raw.tag"),
        }
    result["quality"] = quality_checks(item, packaging)
    return result


def applicable(overlay: dict[str, Any], item: dict[str, Any], as_of: date) -> bool:
    product_id = str(pick(item, "id", "raw.id") or "")
    model = str(pick(item, "model", "productModel", "raw.productModel") or "").lower()
    match = overlay.get("match", {})
    if match.get("id") and str(match["id"]) != product_id:
        return False
    if match.get("model") and str(match["model"]).lower() != model:
        return False
    if not match.get("id") and not match.get("model"):
        return False
    effective = overlay.get("effectiveFrom")
    return not effective or date.fromisoformat(effective) <= as_of


def apply_overlays(item: dict[str, Any], overlays: list[dict[str, Any]], as_of: date) -> tuple[dict[str, Any], list[str]]:
    result = copy.deepcopy(item)
    applied: list[str] = []
    candidates = [x for x in overlays if applicable(x, item, as_of)]
    candidates.sort(key=lambda x: (x.get("effectiveFrom", "0001-01-01"), x.get("priority", 0)))
    for overlay in candidates:
        for path, value in overlay.get("set", {}).items():
            set_path(result, path, value)
        applied.append(str(overlay.get("id", "unnamed-overlay")))
    return result, applied


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--overlay", action="append", default=[], type=Path)
    parser.add_argument("--query", required=True)
    parser.add_argument("--as-of", default=date.today().isoformat())
    parser.add_argument("--include-internal", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = load_json(args.catalog)
    overlays: list[dict[str, Any]] = []
    for path in args.overlay:
        data = load_json(path)
        overlays.extend(data.get("overrides", data if isinstance(data, list) else []))

    query = args.query.casefold().strip()
    matches = []
    for raw in products_of(payload):
        haystack = json.dumps(raw, ensure_ascii=False).casefold()
        if query not in haystack:
            continue
        updated, applied = apply_overlays(raw, overlays, date.fromisoformat(args.as_of))
        row = normalized(updated, args.include_internal)
        row["appliedOverlays"] = applied
        matches.append(row)

    matches.sort(key=lambda x: (0 if x["model"].casefold() == query else 1, x["model"]))
    output = {"query": args.query, "catalog": str(args.catalog), "count": len(matches), "products": matches}
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"Catalog: {args.catalog.name}; query: {args.query}; hits: {len(matches)}")
        for row in matches:
            price = row.get("pricing", {}).get("base", "[redacted]")
            print(
                f"- {row['id']} | {row['model']} | {row['category']} | price={price} "
                f"| packing={row['packaging']} | freightReady={row['quality']['freightInquiryReady']} "
                f"| bookingReady={row['quality']['bookingReady']} | blockers={row['quality']['blockers']} "
                f"| warnings={row['quality']['warnings']} | overlays={row['appliedOverlays']}"
            )
    return 0 if matches else 2


if __name__ == "__main__":
    raise SystemExit(main())
