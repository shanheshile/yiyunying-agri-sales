#!/usr/bin/env python3
"""Append one privacy-minimized AI effectiveness run to a JSONL ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import string
import sys
from datetime import datetime, timezone
from pathlib import Path

from effectiveness_report import validate_run


def boolean(value: str) -> bool:
    normalized = value.casefold()
    if normalized in {"true", "yes", "1"}:
        return True
    if normalized in {"false", "no", "0"}:
        return False
    raise argparse.ArgumentTypeError("use true or false")


def generated_run_id() -> str:
    return "run-" + "".join(secrets.choice(string.ascii_lowercase) for _ in range(20))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--task-type", required=True)
    parser.add_argument("--actor-id", required=True, help="Pseudonymous internal actor ID only")
    parser.add_argument("--artifact-version", required=True)
    parser.add_argument("--baseline", type=float, required=True)
    parser.add_argument("--ai-execution", type=float, required=True)
    parser.add_argument("--input-preparation", type=float, required=True)
    parser.add_argument("--human-review", type=float, required=True)
    parser.add_argument("--rework", type=float, required=True)
    parser.add_argument("--maintenance-allocated", type=float, required=True)
    parser.add_argument("--quality-pass", type=boolean, required=True)
    parser.add_argument("--risk-incident", type=boolean, required=True)
    parser.add_argument("--data-security-incident", type=boolean, required=True)
    parser.add_argument("--verification-status", choices=("verified", "pending", "rejected"), required=True)
    parser.add_argument("--real-business", type=boolean, required=True)
    parser.add_argument("--occurred-at")
    parser.add_argument("--run-id")
    receipt = parser.add_mutually_exclusive_group()
    receipt.add_argument("--evidence-receipt", type=Path)
    receipt.add_argument("--evidence-receipt-hash")
    args = parser.parse_args()

    evidence_hash = args.evidence_receipt_hash
    if args.evidence_receipt:
        if not args.evidence_receipt.is_file():
            parser.error("--evidence-receipt must be an existing file")
        evidence_hash = file_sha256(args.evidence_receipt)
    if args.verification_status == "verified" and not evidence_hash:
        parser.error("verified runs require --evidence-receipt or --evidence-receipt-hash")

    occurred_at = args.occurred_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    row = {
        "schemaVersion": "1.0",
        "runId": args.run_id or generated_run_id(),
        "occurredAt": occurred_at,
        "taskType": args.task_type,
        "pseudonymousActorId": args.actor_id,
        "realBusiness": args.real_business,
        "verificationStatus": args.verification_status,
        "timingMinutes": {
            "baselineTotal": args.baseline,
            "aiExecution": args.ai_execution,
            "inputPreparation": args.input_preparation,
            "humanReview": args.human_review,
            "rework": args.rework,
            "maintenanceAllocated": args.maintenance_allocated,
        },
        "qualityPass": args.quality_pass,
        "riskIncident": args.risk_incident,
        "dataSecurityIncident": args.data_security_incident,
        "artifactVersion": args.artifact_version,
        "evidenceReceiptHash": evidence_hash,
    }
    errors = validate_run(row, 1)
    if errors:
        parser.error("; ".join(errors))

    args.ledger.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    descriptor = os.open(args.ledger, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
    try:
        os.write(descriptor, payload)
    finally:
        os.close(descriptor)
    sys.stdout.write(json.dumps(row, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
