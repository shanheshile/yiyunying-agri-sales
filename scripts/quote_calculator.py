#!/usr/bin/env python3
"""Deterministic internal quotation calculator with explicit profit semantics."""

from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_CEILING, getcontext
from pathlib import Path
from typing import Any

getcontext().prec = 28


def dec(value: Any) -> Decimal:
    return Decimal(str(value))


def rate_map(rows: list[dict[str, Any]]) -> dict[tuple[str, str], Decimal]:
    rates: dict[tuple[str, str], Decimal] = {}
    for row in rows:
        source, target = row["from"].upper(), row["to"].upper()
        rate = dec(row["rate"])
        rates[(source, target)] = rate
        rates[(target, source)] = Decimal(1) / rate
    return rates


def convert(amount: Decimal, source: str, target: str, rates: dict[tuple[str, str], Decimal]) -> Decimal:
    source, target = source.upper(), target.upper()
    if source == target:
        return amount
    if (source, target) in rates:
        return amount * rates[(source, target)]
    for bridge in {x[1] for x in rates if x[0] == source}:
        if (bridge, target) in rates:
            return amount * rates[(source, bridge)] * rates[(bridge, target)]
    raise ValueError(f"missing exchange rate {source}->{target}")


def calculate(payload: dict[str, Any]) -> dict[str, Any]:
    currency = payload["currency"].upper()
    rates = rate_map(payload.get("exchangeRates", []))
    item_rows = []
    product_cost = Decimal(0)
    for item in payload["items"]:
        if item.get("imageVerified") is not True:
            raise ValueError(f"product image not verified: {item.get('model')}")
        native = dec(item["unitCost"]) * dec(item["quantity"])
        converted = convert(native, item["costCurrency"], currency, rates)
        product_cost += converted
        item_rows.append({
            "model": item["model"],
            "quantity": item["quantity"],
            "nativeCost": str(native),
            "nativeCurrency": item["costCurrency"],
            "convertedCost": str(converted),
            "currency": currency,
        })

    term_rows = []
    term_cost = Decimal(0)
    for cost in payload.get("termCosts", []):
        converted = convert(dec(cost["amount"]), cost["currency"], currency, rates)
        term_cost += converted
        term_rows.append({"name": cost["name"], "convertedCost": str(converted), "currency": currency, "sourceId": cost["sourceId"]})

    basis = product_cost + term_cost
    profit = dec(payload["profitRate"])
    mode = payload["pricingMode"]
    if mode == "markup-on-cost":
        unrounded = basis * (Decimal(1) + profit)
    elif mode == "gross-margin-on-sale":
        if profit >= 1:
            raise ValueError("gross margin must be less than 1")
        unrounded = basis / (Decimal(1) - profit)
    elif mode == "backend-calculated":
        if "backendTotal" not in payload:
            raise ValueError("backend-calculated mode requires backendTotal")
        unrounded = dec(payload["backendTotal"])
    else:
        raise ValueError(f"unsupported pricingMode: {mode}")

    rounded = unrounded.to_integral_value(rounding=ROUND_CEILING)
    return {
        "customerId": payload["customerId"],
        "currency": currency,
        "incoterm": payload["incoterm"],
        "pricingMode": mode,
        "profitRate": str(profit),
        "items": item_rows,
        "termCosts": term_rows,
        "costBasis": str(basis),
        "unroundedCustomerTotal": str(unrounded),
        "customerTotalRoundedUp": str(rounded),
        "humanConfirmationRequired": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8-sig"))
    result = calculate(payload)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

