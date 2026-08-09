import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
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
effectiveness = load_module("effectiveness_report", ROOT / "scripts" / "effectiveness_report.py")


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

    def test_every_credential_reference_uses_a_provider_prefix(self):
        config = json.loads((ROOT / "config" / "credential-bindings.example.json").read_text(encoding="utf-8"))
        for service in config["services"].values():
            for key, value in service.items():
                if key.endswith("Ref") and value is not None:
                    self.assertRegex(value, r"^(env|credential-manager|platform):[^\s]+$")

    def test_measurement_is_loaded_only_when_selected(self):
        followup = prompt_pack.compose(ROOT / "portable", "agri", ["followup"], "generic", [])
        measurement = prompt_pack.compose(ROOT / "portable", "agri", ["measurement"], "generic", [])
        self.assertNotIn("Effectiveness Measurement Task", followup)
        self.assertIn("Effectiveness Measurement Task", measurement)


def effectiveness_project():
    return {
        "schemaVersion": "1.0",
        "project": {
            "id": "project-alpha",
            "name": "Verified AI workflow",
            "productionStartDate": "2026-01-01",
            "asOfDate": "2026-02-11",
            "annualTaskVolume": 500,
            "standardHourlyCostCny": 100,
            "ownerRole": "workflow owner",
            "artifacts": [{"type": "skill", "version": "1.3.0", "reusable": True}],
        },
        "scope": {"teamAdopted": False, "crossRoleOrDepartment": False},
        "metrics": {
            "coreQuality": {
                "name": "verified completion rate",
                "direction": "higher-is-better",
                "baselineValue": 98,
                "aiValue": 99,
                "allowedDegradation": 0,
            },
            "risk": {"name": "critical error rate", "aiValue": 0, "maximumAllowed": 0},
        },
        "economics": {
            "annualDirectCostSavingsCny": 0,
            "annualAddedGrossProfitCny": 0,
            "annualAiToolApiProcurementMaintenanceCostCny": 0,
            "annualBusinessErrorLossCny": 0,
        },
        "awardPolicy": {
            "tiers": [
                {"key": "practice", "label": "Practice", "minRealRunDays": 14, "minVerifiedTasks": 10, "minNetEfficiencyPct": 15, "minUniqueUsers": None, "adoptionRule": "none", "minAnnualNetValueCny": None},
                {"key": "third", "label": "Level 3", "minRealRunDays": 28, "minVerifiedTasks": 30, "minNetEfficiencyPct": 20, "minUniqueUsers": None, "adoptionRule": "none", "minAnnualNetValueCny": None},
                {"key": "second", "label": "Level 2", "minRealRunDays": 42, "minVerifiedTasks": 50, "minNetEfficiencyPct": 30, "minUniqueUsers": 3, "adoptionRule": "users", "minAnnualNetValueCny": None},
                {"key": "first", "label": "Level 1", "minRealRunDays": 56, "minVerifiedTasks": 100, "minNetEfficiencyPct": 40, "minUniqueUsers": 10, "adoptionRule": "team-or-users", "minAnnualNetValueCny": None}
            ],
            "secondTranche": {"eligibleTierKeys": ["second", "first"], "minStableRunDays": 90, "minActiveUserRetentionPct": 50}
        },
        "userValidations": [
            {"pseudonymousUserId": "actor-a", "verifiedAt": "2026-02-11", "confirmedRealUse": True, "confirmedUseful": True}
        ],
        "sustainabilityReview": {
            "stableRunDays": 42,
            "activeUserRetentionPct": 100,
            "qualityIncidentCount": 0,
            "businessErrorCount": 0,
            "customerComplaintCount": 0,
            "evidenceConsistencyConfirmed": True,
            "maintainerAssigned": True,
            "dataSecurityCompliant": True,
        },
    }


def effectiveness_run(index: int):
    occurred = date(2026, 1, 1) + timedelta(days=index % 42)
    return {
        "schemaVersion": "1.0",
        "runId": f"run-alpha-{index:03d}",
        "occurredAt": f"{occurred.isoformat()}T08:00:00Z",
        "taskType": "followup",
        "pseudonymousActorId": ("actor-a", "actor-b", "actor-c")[index % 3],
        "realBusiness": True,
        "verificationStatus": "verified",
        "timingMinutes": {
            "baselineTotal": 60,
            "aiExecution": 10,
            "inputPreparation": 5,
            "humanReview": 8,
            "rework": 2,
            "maintenanceAllocated": 1,
        },
        "qualityPass": True,
        "riskIncident": False,
        "dataSecurityIncident": False,
        "artifactVersion": "1.3.0",
        "evidenceReceiptHash": "a" * 64,
    }


class EffectivenessTests(unittest.TestCase):
    def test_net_formula_and_second_award_gate(self):
        report = effectiveness.evaluate(effectiveness_project(), [effectiveness_run(index) for index in range(50)])
        self.assertEqual(report["time"]["averageNetSavedMinutes"], 34)
        self.assertAlmostEqual(report["time"]["netEfficiencyPct"], 56.6667)
        self.assertEqual(report["evidence"]["durationDays"], 42)
        self.assertEqual(report["recommendedAward"], "Level 2")

    def test_missing_quality_evidence_blocks_award(self):
        project = effectiveness_project()
        project["metrics"]["coreQuality"]["aiValue"] = None
        report = effectiveness.evaluate(project, [effectiveness_run(index) for index in range(50)])
        self.assertIsNone(report["recommendedAward"])
        self.assertTrue(any("核心质量指标缺少" in reason for reason in report["awardReadiness"][0]["reasons"]))

    def test_personal_identifier_and_missing_receipt_are_rejected(self):
        row = effectiveness_run(1)
        row["pseudonymousActorId"] = "person@example.com"
        row["evidenceReceiptHash"] = None
        with self.assertRaisesRegex(ValueError, "pseudonymousActorId"):
            effectiveness.evaluate(effectiveness_project(), [row])

    def test_recorder_appends_a_verified_privacy_minimized_row(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            receipt = directory / "receipt.txt"
            receipt.write_text("sanitized internal evidence receipt", encoding="utf-8")
            ledger = directory / "runs.jsonl"
            command = [
                sys.executable,
                str(ROOT / "scripts" / "effectiveness_record.py"),
                "--ledger", str(ledger),
                "--task-type", "followup",
                "--actor-id", "actor-a",
                "--artifact-version", "1.3.0",
                "--baseline", "60",
                "--ai-execution", "10",
                "--input-preparation", "5",
                "--human-review", "8",
                "--rework", "2",
                "--maintenance-allocated", "1",
                "--quality-pass", "true",
                "--risk-incident", "false",
                "--data-security-incident", "false",
                "--verification-status", "verified",
                "--real-business", "true",
                "--evidence-receipt", str(receipt),
            ]
            result = subprocess.run(command, check=False, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            row = json.loads(ledger.read_text(encoding="utf-8"))
            self.assertEqual(row["pseudonymousActorId"], "actor-a")
            self.assertEqual(len(row["evidenceReceiptHash"]), 64)


if __name__ == "__main__":
    unittest.main()
