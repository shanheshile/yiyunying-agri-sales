#!/usr/bin/env python3
"""Deterministic customer preflight gate for follow-up and CRM actions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


BACKGROUND_DONE = {"usable", "no-information"}
REQUIRED_EVIDENCE = (
    "contact",
    "inquiry",
    "crmDynamics",
    "whatsapp",
    "recentEmail",
)


def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    customer_id = str(payload.get("customerId") or "").strip()
    if not customer_id:
        raise ValueError("customerId is required")

    background = payload.get("backgroundResearch") or {}
    if not isinstance(background, dict):
        raise ValueError("backgroundResearch must be an object")
    status = str(background.get("status") or "missing").strip()
    marker = str(background.get("marker") or "").strip()
    crm_read_back = background.get("crmReadBack") is True
    identity_match = background.get("identityMatch")

    actions: list[str] = []
    blockers: list[str] = []
    if status == "missing":
        actions.extend(("RUN_BACKGROUND_RESEARCH", "RECORD_BACKGROUND_RESULT", "READ_BACK_BACKGROUND_RESULT"))
        blockers.append("BACKGROUND_RESEARCH_MISSING")
    elif status == "running":
        actions.extend(("WAIT_FOR_BACKGROUND_RESEARCH", "RECORD_BACKGROUND_RESULT", "READ_BACK_BACKGROUND_RESULT"))
        blockers.append("BACKGROUND_RESEARCH_INCOMPLETE")
    elif status == "failed":
        actions.append("RETRY_OR_QUEUE_BACKGROUND_RESEARCH_EXCEPTION")
        blockers.append("BACKGROUND_RESEARCH_FAILED")
    elif status == "usable":
        if identity_match is not True:
            actions.append("RESOLVE_BACKGROUND_IDENTITY_CONFLICT")
            blockers.append("BACKGROUND_IDENTITY_NOT_VERIFIED")
        elif not crm_read_back:
            actions.extend(("RECORD_BACKGROUND_RESULT", "READ_BACK_BACKGROUND_RESULT"))
            blockers.append("BACKGROUND_RESULT_NOT_READ_BACK")
    elif status == "no-information":
        if marker != "背调无信息":
            actions.extend(("RECORD_EXACT_NO_INFORMATION_MARKER", "READ_BACK_BACKGROUND_RESULT"))
            blockers.append("BACKGROUND_NO_INFORMATION_MARKER_INVALID")
        elif not crm_read_back:
            actions.append("READ_BACK_BACKGROUND_RESULT")
            blockers.append("BACKGROUND_RESULT_NOT_READ_BACK")
    else:
        raise ValueError(f"unsupported backgroundResearch.status: {status}")

    background_ready = (
        status in BACKGROUND_DONE
        and crm_read_back
        and (status != "usable" or identity_match is True)
        and (status != "no-information" or marker == "背调无信息")
    )

    evidence = payload.get("evidence") or {}
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be an object")
    missing_evidence = [name for name in REQUIRED_EVIDENCE if evidence.get(name) is not True]
    if background_ready and missing_evidence:
        actions.append("READ_FULL_CUSTOMER_EVIDENCE")
        blockers.append("CUSTOMER_EVIDENCE_INCOMPLETE")

    evidence_ready = background_ready and not missing_evidence
    ready_for_intent_review = evidence_ready
    intent_reviewed = payload.get("intentReviewed") is True
    channel_verified = payload.get("channelVerified") is True
    if ready_for_intent_review and not intent_reviewed:
        actions.append("REVIEW_LATEST_CUSTOMER_INTENT")
    if ready_for_intent_review and intent_reviewed and not channel_verified:
        actions.append("VERIFY_OUTBOUND_CHANNEL")
        blockers.append("CHANNEL_NOT_VERIFIED")

    action_ready = ready_for_intent_review and intent_reviewed
    outbound_allowed = action_ready and channel_verified
    return {
        "customerId": customer_id,
        "customerKind": "new" if payload.get("isNew") is True else "existing",
        "backgroundReady": background_ready,
        "evidenceReady": evidence_ready,
        "readyForIntentReview": ready_for_intent_review,
        "outboundAllowed": outbound_allowed,
        "crmStageWriteAllowed": action_ready,
        "actions": actions,
        "blockers": blockers,
        "missingEvidence": missing_evidence,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Customer preflight JSON. Reads stdin when omitted.")
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8-sig") if args.input else sys.stdin.read())
        if not isinstance(payload, dict):
            raise ValueError("input must be a JSON object")
        print(json.dumps(evaluate(payload), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"customer preflight failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
