import importlib.util
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


quote = load_module("quote_calculator", ROOT / "scripts" / "quote_calculator.py")
pi = load_module("pi_lint", ROOT / "scripts" / "pi_lint.py")
catalog = load_module("catalog_query", ROOT / "scripts" / "catalog_query.py")


class QuoteTests(unittest.TestCase):
    def test_markup_and_round_up(self):
        payload = {
            "customerId": "example",
            "currency": "USD",
            "incoterm": "EXW",
            "pricingMode": "markup-on-cost",
            "profitRate": 0.15,
            "items": [{"productId": "p1", "model": "M1", "quantity": 1, "unitCost": 100, "costCurrency": "USD", "imageVerified": True}],
            "termCosts": [],
            "exchangeRates": [],
        }
        result = quote.calculate(payload)
        self.assertEqual(result["customerTotalRoundedUp"], "115")
        self.assertTrue(result["humanConfirmationRequired"])

    def test_gross_margin_is_distinct(self):
        payload = {
            "customerId": "example",
            "currency": "USD",
            "incoterm": "EXW",
            "pricingMode": "gross-margin-on-sale",
            "profitRate": 0.15,
            "items": [{"productId": "p1", "model": "M1", "quantity": 1, "unitCost": 100, "costCurrency": "USD", "imageVerified": True}],
            "termCosts": [],
            "exchangeRates": [],
        }
        result = quote.calculate(payload)
        self.assertEqual(result["customerTotalRoundedUp"], "118")


class PiTests(unittest.TestCase):
    def test_placeholder_and_math_are_rejected(self):
        payload = {
            "piNumber": "待确认",
            "issueDate": "2026-08-08",
            "currency": "USD",
            "incoterm": "EXW",
            "destination": "Port",
            "paymentTerms": "30/70",
            "validity": "10 days",
            "seller": {"legalName": "Seller", "address": "Address"},
            "buyer": {"legalName": "Buyer", "address": "Address"},
            "bank": {"beneficiary": "Seller", "account": "1", "bankName": "Bank", "swift": "SWIFT"},
            "quoteReference": "Q1",
            "items": [{"productId": "p1", "description": "M1", "configuration": "std", "quantity": 2, "unit": "SET", "unitPrice": 100, "amount": 199}],
            "humanConfirmationRequired": True,
        }
        errors = pi.lint(payload)
        self.assertTrue(any("piNumber" in x for x in errors))
        self.assertTrue(any("amount mismatch" in x for x in errors))


class CatalogTests(unittest.TestCase):
    def test_exact_overlay(self):
        item = {"id": "1", "model": "M1", "pricing": {"baseCny": 100}}
        overlays = [{"id": "o1", "match": {"model": "M1"}, "effectiveFrom": "2026-01-01", "set": {"pricing.baseCny": 120}}]
        updated, applied = catalog.apply_overlays(item, overlays, __import__("datetime").date(2026, 8, 8))
        self.assertEqual(updated["pricing"]["baseCny"], 120)
        self.assertEqual(applied, ["o1"])


if __name__ == "__main__":
    unittest.main()

