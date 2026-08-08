#!/usr/bin/env python3
"""Lint a PI data payload before document creation or sending."""

from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path
from typing import Any


PLACEHOLDERS = {"", "tbc", "to be confirmed", "待确认", "n/a", "--"}


def missing(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value.strip().casefold() in PLACEHOLDERS)


def lint(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for path in ("piNumber", "issueDate", "currency", "incoterm", "destination", "paymentTerms", "validity"):
        if missing(payload.get(path)):
            errors.append(f"missing {path}")
    for party_name in ("seller", "buyer"):
        party = payload.get(party_name, {})
        for field in ("legalName", "address"):
            if missing(party.get(field)):
                errors.append(f"missing {party_name}.{field}")
    bank = payload.get("bank", {})
    for field in ("beneficiary", "account", "bankName", "swift"):
        if missing(bank.get(field)):
            errors.append(f"missing bank.{field}")
    if not payload.get("quoteReference") and not payload.get("orderReference"):
        errors.append("missing quoteReference or orderReference")
    items = payload.get("items", [])
    if not items:
        errors.append("no line items")
    total = Decimal(0)
    for index, item in enumerate(items, 1):
        for field in ("productId", "description", "configuration", "quantity", "unit", "unitPrice", "amount"):
            if missing(item.get(field)):
                errors.append(f"item {index} missing {field}")
        if all(item.get(x) is not None for x in ("quantity", "unitPrice", "amount")):
            calculated = Decimal(str(item["quantity"])) * Decimal(str(item["unitPrice"]))
            amount = Decimal(str(item["amount"]))
            if calculated != amount:
                errors.append(f"item {index} amount mismatch: {calculated} != {amount}")
            total += amount
    if payload.get("total") is not None and Decimal(str(payload["total"])) != total:
        errors.append(f"PI total mismatch: {total} != {payload['total']}")
    if payload.get("humanConfirmationRequired") is not True:
        errors.append("humanConfirmationRequired must be true")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8-sig"))
    errors = lint(payload)
    print(json.dumps({"valid": not errors, "errors": errors, "humanConfirmationRequired": True}, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())

