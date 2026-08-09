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
prompt_pack = load_module("build_prompt_pack", ROOT / "scripts" / "build_prompt_pack.py")


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

    def test_impossible_gross_weight_blocks_freight(self):
        item = {
            "id": "1",
            "model": "T1",
            "dimensions": {"packageSize": "3.2*1.6*2.45", "packageWeight": "200 kg", "packageCbm": 13},
            "raw": {"attributes": {"weight": "1950kg"}},
            "validation": {"status": "PARAM_OR_FREIGHT_TO_CONFIRM", "issues": ["MACHINE_WEIGHT_TO_CONFIRM"]},
        }
        row = catalog.normalized(item, include_internal=False)
        self.assertEqual(row["packaging"]["netWeightKg"], "1950kg")
        self.assertFalse(row["quality"]["freightInquiryReady"])
        self.assertIn("REPORTED_GROSS_WEIGHT_LT_MACHINE_WEIGHT", row["quality"]["blockers"])

    def test_cbm_mismatch_allows_inquiry_but_blocks_booking(self):
        item = {
            "id": "1",
            "model": "M1",
            "dimensions": {
                "packageSize": "1840*1520*1050",
                "packageWeight": "450 kg",
                "machineWeight": "360 kg",
                "packageCbm": 2.5,
            },
        }
        row = catalog.normalized(item, include_internal=False)
        self.assertTrue(row["quality"]["freightInquiryReady"])
        self.assertFalse(row["quality"]["bookingReady"])
        self.assertIn("REPORTED_CBM_DIFFERS_FROM_OUTER_DIMENSIONS", row["quality"]["warnings"])


class PromptPackTests(unittest.TestCase):
    def test_followup_pack_stays_compact_and_excludes_quote_module(self):
        result = prompt_pack.compose(ROOT / "portable", "agri", ["followup"], "generic", [])
        self.assertLess(prompt_pack.estimate_tokens(result), 3500)
        self.assertIn("Follow-up And CRM Task", result)
        self.assertNotIn("Quote, Freight And PI Task", result)

    def test_non_ascii_token_estimate_is_conservative(self):
        self.assertEqual(prompt_pack.estimate_tokens("背调无信息"), 6)

    def test_unknown_manifest_key_has_clear_error(self):
        with self.assertRaisesRegex(ValueError, "unknown task"):
            prompt_pack.compose(ROOT / "portable", "agri", ["missing"], "generic", [])


if __name__ == "__main__":
    unittest.main()
