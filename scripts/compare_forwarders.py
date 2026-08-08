#!/usr/bin/env python3
"""Compare complete forwarder options without combining quote components."""

from __future__ import annotations

import argparse
import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any


def evaluate(quote: dict[str, Any], as_of: date) -> dict[str, Any]:
    reasons: list[str] = []
    if quote.get("capability") not in {"available", "conditional"}:
        reasons.append("capability unavailable")
    if quote.get("validUntil") and date.fromisoformat(quote["validUntil"]) < as_of:
        reasons.append("expired")
    amounts: list[Decimal] = []
    currency: str | None = None
    for charge in quote.get("charges", []):
        normalized = charge.get("normalizedAmount")
        normalized_currency = charge.get("normalizedCurrency")
        if normalized is None or not normalized_currency:
            reasons.append(f"unresolved charge: {charge.get('name')}")
            continue
        if currency is None:
            currency = normalized_currency
        elif currency != normalized_currency:
            reasons.append("mixed normalized currencies")
        amounts.append(Decimal(str(normalized)))
        if charge.get("asActual"):
            reasons.append(f"as-actual charge: {charge.get('name')}")
    return {
        "forwarderId": quote.get("forwarderId"),
        "requestKey": quote.get("requestKey"),
        "incoterm": quote.get("incoterm"),
        "destination": quote.get("destination"),
        "currency": currency,
        "normalizedTotal": str(sum(amounts, Decimal(0))) if amounts and not any("mixed" in x for x in reasons) else None,
        "complete": not reasons,
        "reviewReasons": reasons,
        "route": quote.get("route"),
        "transitDays": quote.get("transitDays"),
        "restrictions": quote.get("restrictions", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--as-of", default=date.today().isoformat())
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8-sig"))
    quotes = payload.get("quotes", payload if isinstance(payload, list) else [])
    results = [evaluate(x, date.fromisoformat(args.as_of)) for x in quotes]
    keys = {(x["requestKey"], x["incoterm"], x["destination"]) for x in results}
    comparable = len(keys) == 1
    complete = [x for x in results if x["complete"] and x["normalizedTotal"] is not None]
    currencies = {x["currency"] for x in complete}
    if comparable and len(currencies) == 1:
        complete.sort(key=lambda x: Decimal(x["normalizedTotal"]))
    else:
        comparable = False
    print(json.dumps({"comparable": comparable, "rankedCompleteOptions": complete if comparable else [], "allOptions": results, "humanConfirmationRequired": True}, ensure_ascii=False, indent=2))
    return 0 if comparable and complete else 2


if __name__ == "__main__":
    raise SystemExit(main())

