#!/usr/bin/env python3
"""Calculate net AI efficiency, value, quality gates and award readiness."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any


RUN_KEYS = {
    "schemaVersion",
    "runId",
    "occurredAt",
    "taskType",
    "pseudonymousActorId",
    "realBusiness",
    "verificationStatus",
    "timingMinutes",
    "qualityPass",
    "riskIncident",
    "dataSecurityIncident",
    "artifactVersion",
    "evidenceReceiptHash",
}
RUN_REQUIRED_KEYS = RUN_KEYS - {"evidenceReceiptHash"}
TIMING_KEYS = {
    "baselineTotal",
    "aiExecution",
    "inputPreparation",
    "humanReview",
    "rework",
    "maintenanceAllocated",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_runs(path: Path) -> list[dict[str, Any]]:
    if path.suffix.casefold() == ".jsonl":
        rows = []
        for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSONL at line {line_number}: {exc}") from exc
        return rows
    payload = load_json(path)
    if isinstance(payload, list):
        return payload
    if isinstance(payload.get("runs"), list):
        return payload["runs"]
    raise ValueError("runs input must be a JSON array, a {runs: []} object, or JSONL")


def numeric(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
        return float(value)
    return None


def iso_date(value: Any) -> date | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def iso_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def privacy_safe_identifier(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip() or "@" in value:
        return False
    return re.search(r"\d{7,}", value) is None


def metric_status(metric: dict[str, Any]) -> tuple[bool | None, str]:
    baseline = numeric(metric.get("baselineValue"))
    current = numeric(metric.get("aiValue"))
    tolerance = numeric(metric.get("allowedDegradation"))
    if baseline is None or current is None or tolerance is None:
        return None, "核心质量指标缺少基线、AI值或容差"
    direction = metric.get("direction")
    if direction == "higher-is-better":
        passed = current + tolerance >= baseline
    elif direction == "lower-is-better":
        passed = current - tolerance <= baseline
    else:
        return None, "核心质量指标方向无效"
    return passed, "核心质量未下降" if passed else "核心质量超过允许退化范围"


def risk_status(metric: dict[str, Any]) -> tuple[bool | None, str]:
    current = numeric(metric.get("aiValue"))
    limit = numeric(metric.get("maximumAllowed"))
    if current is None or limit is None:
        return None, "风险指标缺少当前值或上限"
    passed = current <= limit
    return passed, "风险指标在上限内" if passed else "风险指标超过上限"


def validate_run(row: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    missing = RUN_REQUIRED_KEYS - set(row)
    if missing:
        errors.append(f"run {index}: missing fields: {', '.join(sorted(missing))}")
    extra = set(row) - RUN_KEYS
    if extra:
        errors.append(f"run {index}: forbidden/unknown fields: {', '.join(sorted(extra))}")
    if row.get("schemaVersion") != "1.0":
        errors.append(f"run {index}: schemaVersion must be 1.0")
    for key in ("runId", "pseudonymousActorId"):
        if not privacy_safe_identifier(row.get(key)):
            errors.append(f"run {index}: {key} must be pseudonymous and cannot look like email/phone/external ID")
    if not isinstance(row.get("runId"), str) or len(row["runId"]) < 8:
        errors.append(f"run {index}: runId must contain at least 8 characters")
    if iso_datetime(row.get("occurredAt")) is None:
        errors.append(f"run {index}: occurredAt must be ISO date-time")
    if not isinstance(row.get("taskType"), str) or not row["taskType"].strip():
        errors.append(f"run {index}: taskType must be a non-empty string")
    if not isinstance(row.get("artifactVersion"), str) or not row["artifactVersion"].strip():
        errors.append(f"run {index}: artifactVersion must be a non-empty string")
    for key in ("realBusiness", "qualityPass", "riskIncident", "dataSecurityIncident"):
        if not isinstance(row.get(key), bool):
            errors.append(f"run {index}: {key} must be boolean")
    if row.get("verificationStatus") not in {"verified", "pending", "rejected"}:
        errors.append(f"run {index}: verificationStatus is invalid")
    receipt_hash = row.get("evidenceReceiptHash")
    if receipt_hash is not None and (not isinstance(receipt_hash, str) or re.fullmatch(r"[A-Fa-f0-9]{64}", receipt_hash) is None):
        errors.append(f"run {index}: evidenceReceiptHash must be a SHA-256 hex digest or null")
    if row.get("verificationStatus") == "verified" and receipt_hash is None:
        errors.append(f"run {index}: verified runs require evidenceReceiptHash")
    timing = row.get("timingMinutes")
    if not isinstance(timing, dict):
        errors.append(f"run {index}: timingMinutes must be an object")
        return errors
    extra_timing = set(timing) - TIMING_KEYS
    if extra_timing:
        errors.append(f"run {index}: unknown timing fields: {', '.join(sorted(extra_timing))}")
    for key in TIMING_KEYS:
        value = numeric(timing.get(key))
        if value is None or value < 0:
            errors.append(f"run {index}: timingMinutes.{key} must be a non-negative number")
    if numeric(timing.get("baselineTotal")) == 0:
        errors.append(f"run {index}: baselineTotal must be greater than zero")
    return errors


def evaluate(project: dict[str, Any], runs: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    for index, row in enumerate(runs, 1):
        if not isinstance(row, dict):
            errors.append(f"run {index}: row must be an object")
        else:
            errors.extend(validate_run(row, index))
    run_ids = [row.get("runId") for row in runs if isinstance(row, dict)]
    duplicates = sorted({run_id for run_id in run_ids if run_ids.count(run_id) > 1})
    if duplicates:
        errors.append(f"duplicate runId values: {', '.join(str(item) for item in duplicates)}")
    if errors:
        raise ValueError("; ".join(errors))

    verified = [row for row in runs if row.get("realBusiness") is True and row.get("verificationStatus") == "verified"]
    receipt_hashes = [row["evidenceReceiptHash"].casefold() for row in verified]
    duplicate_receipts = sorted({item for item in receipt_hashes if receipt_hashes.count(item) > 1})
    if duplicate_receipts:
        raise ValueError("verified runs must use distinct evidenceReceiptHash values")
    excluded = len(runs) - len(verified)
    timing_rows = []
    for row in verified:
        timing = row["timingMinutes"]
        ai_total = sum(float(timing[key]) for key in TIMING_KEYS if key != "baselineTotal")
        baseline = float(timing["baselineTotal"])
        timing_rows.append({"baseline": baseline, "aiTotal": ai_total, "netSaved": baseline - ai_total})

    total_baseline = sum(row["baseline"] for row in timing_rows)
    total_net_saved = sum(row["netSaved"] for row in timing_rows)
    efficiency = total_net_saved / total_baseline * 100 if total_baseline > 0 else None
    average_net_saved = total_net_saved / len(timing_rows) if timing_rows else None

    project_info = project.get("project", {})
    start = iso_date(project_info.get("productionStartDate"))
    as_of = iso_date(project_info.get("asOfDate"))
    declared_duration_days = (as_of - start).days + 1 if start and as_of and as_of >= start else None
    occurred_dates = [iso_datetime(row["occurredAt"]).date() for row in verified]
    observed_duration_days = (max(occurred_dates) - min(occurred_dates)).days + 1 if occurred_dates else None
    duration_days = (
        min(declared_duration_days, observed_duration_days)
        if declared_duration_days is not None and observed_duration_days is not None
        else None
    )
    annual_volume = numeric(project_info.get("annualTaskVolume"))
    annual_volume_by_type = project_info.get("annualTaskVolumeByType", {})
    hourly_cost = numeric(project_info.get("standardHourlyCostCny"))
    timing_by_type: dict[str, list[float]] = {}
    for source, timing in zip(verified, timing_rows):
        timing_by_type.setdefault(source["taskType"], []).append(timing["netSaved"])
    annual_volume_source = None
    annual_saved_hours = None
    if timing_by_type and isinstance(annual_volume_by_type, dict) and all(
        numeric(annual_volume_by_type.get(task_type)) is not None for task_type in timing_by_type
    ):
        annual_saved_hours = sum(
            (sum(values) / len(values)) * float(annual_volume_by_type[task_type])
            for task_type, values in timing_by_type.items()
        ) / 60
        annual_volume = sum(float(annual_volume_by_type[task_type]) for task_type in timing_by_type)
        annual_volume_source = "task-type-weighted"
    elif len(timing_by_type) == 1 and average_net_saved is not None and annual_volume is not None:
        annual_saved_hours = average_net_saved * annual_volume / 60
        annual_volume_source = "single-task-aggregate"

    economics = project.get("economics", {})
    monetary_keys = (
        "annualDirectCostSavingsCny",
        "annualAddedGrossProfitCny",
        "annualAiToolApiProcurementMaintenanceCostCny",
        "annualBusinessErrorLossCny",
    )
    monetary = {key: numeric(economics.get(key)) for key in monetary_keys}
    annual_value = None
    if annual_saved_hours is not None and hourly_cost is not None and all(value is not None for value in monetary.values()):
        annual_value = (
            annual_saved_hours * hourly_cost
            + monetary["annualDirectCostSavingsCny"]
            + monetary["annualAddedGrossProfitCny"]
            - monetary["annualAiToolApiProcurementMaintenanceCostCny"]
            - monetary["annualBusinessErrorLossCny"]
        )

    quality_ok, quality_reason = metric_status(project.get("metrics", {}).get("coreQuality", {}))
    risk_ok, risk_reason = risk_status(project.get("metrics", {}).get("risk", {}))
    security_incidents = sum(bool(row.get("dataSecurityIncident")) for row in runs)
    quality_passes = sum(bool(row.get("qualityPass")) for row in verified)
    risk_incidents = sum(bool(row.get("riskIncident")) for row in verified)
    actors = {row["pseudonymousActorId"] for row in verified}
    validations = [
        row for row in project.get("userValidations", [])
        if row.get("confirmedRealUse") is True
        and row.get("confirmedUseful") is True
        and privacy_safe_identifier(row.get("pseudonymousUserId"))
    ]
    validated_actor_ids = {row["pseudonymousUserId"] for row in validations}
    validated_actors = actors & validated_actor_ids
    artifacts = [row for row in project_info.get("artifacts", []) if row.get("reusable") is True and row.get("version")]
    sustainability = project.get("sustainabilityReview", {})

    common_reasons = []
    if not verified:
        common_reasons.append("没有已核验的真实业务任务")
    if quality_ok is not True:
        common_reasons.append(quality_reason)
    if risk_ok is not True:
        common_reasons.append(risk_reason)
    if security_incidents:
        common_reasons.append("存在数据安全事件")
    if not validations:
        common_reasons.append("缺少实际使用者验证")
    if not artifacts:
        common_reasons.append("缺少带版本的可复制成果")
    if not project_info.get("ownerRole"):
        common_reasons.append("缺少负责维护的角色")
    if sustainability.get("evidenceConsistencyConfirmed") is not True:
        common_reasons.append("数据一致性尚未确认")
    if sustainability.get("maintainerAssigned") is not True:
        common_reasons.append("维护责任尚未确认")
    if sustainability.get("dataSecurityCompliant") is not True:
        common_reasons.append("数据安全合规尚未确认")

    award_rows = []
    scope = project.get("scope", {})
    award_policy = project.get("awardPolicy", {})
    for award in award_policy.get("tiers", []):
        reasons = list(common_reasons)
        minimum_days = numeric(award.get("minRealRunDays"))
        minimum_tasks = numeric(award.get("minVerifiedTasks"))
        minimum_efficiency = numeric(award.get("minNetEfficiencyPct"))
        minimum_users = numeric(award.get("minUniqueUsers"))
        minimum_value = numeric(award.get("minAnnualNetValueCny"))
        if minimum_days is None or duration_days is None or duration_days < minimum_days:
            reasons.append(f"真实运行需达到 {value(minimum_days, ' 天')}")
        if minimum_tasks is None or len(verified) < minimum_tasks:
            reasons.append(f"已核验真实任务需达到 {value(minimum_tasks, ' 次')}")
        if minimum_efficiency is None or efficiency is None or efficiency < minimum_efficiency:
            reasons.append(f"净提效需达到 {value(minimum_efficiency, '%')}")
        adoption_rule = award.get("adoptionRule")
        user_requirement_met = minimum_users is not None and len(validated_actors) >= minimum_users
        if adoption_rule == "users" and not user_requirement_met:
            reasons.append(f"实际使用者需达到 {value(minimum_users, ' 人')}")
        elif adoption_rule == "team-or-users" and not (scope.get("teamAdopted") is True or user_requirement_met):
            reasons.append(f"需一个小组采用或实际使用者达到 {value(minimum_users, ' 人')}")
        elif adoption_rule == "cross-role-or-users" and not (scope.get("crossRoleOrDepartment") is True or user_requirement_met):
            reasons.append(f"需跨岗位/跨部门采用或实际使用者达到 {value(minimum_users, ' 人')}")
        elif adoption_rule not in {"none", "users", "team-or-users", "cross-role-or-users"}:
            reasons.append("采用范围规则无效")
        if minimum_value is not None and (annual_value is None or annual_value < minimum_value):
            reasons.append(f"年度净价值需有完整证据且达到 {value(minimum_value, ' CNY')}")
        award_rows.append({"key": award["key"], "label": award["label"], "eligible": not reasons, "reasons": reasons})

    eligible = [row for row in award_rows if row["eligible"]]
    recommended = eligible[-1] if eligible else None
    tranche_policy = award_policy.get("secondTranche", {})
    stable_days = numeric(sustainability.get("stableRunDays"))
    retention = numeric(sustainability.get("activeUserRetentionPct"))
    minimum_stable_days = numeric(tranche_policy.get("minStableRunDays"))
    minimum_retention = numeric(tranche_policy.get("minActiveUserRetentionPct"))
    incident_keys = ("qualityIncidentCount", "businessErrorCount", "customerComplaintCount")
    incidents_known_zero = all(numeric(sustainability.get(key)) == 0 for key in incident_keys)
    second_tranche_conditions = {
        "stableRunDuration": minimum_stable_days is not None and stable_days is not None and stable_days >= minimum_stable_days,
        "activeUserRetention": minimum_retention is not None and retention is not None and retention >= minimum_retention,
        "noQualityBusinessOrComplaintIncident": incidents_known_zero,
        "evidenceConsistent": sustainability.get("evidenceConsistencyConfirmed") is True,
        "maintainerAssigned": sustainability.get("maintainerAssigned") is True,
        "dataSecurityCompliant": sustainability.get("dataSecurityCompliant") is True and security_incidents == 0,
        "qualityAndRiskStillPass": quality_ok is True and risk_ok is True,
    }

    return {
        "projectId": project_info.get("id"),
        "projectName": project_info.get("name"),
        "asOfDate": project_info.get("asOfDate"),
        "evidence": {
            "inputRuns": len(runs),
            "verifiedRealBusinessRuns": len(verified),
            "excludedRuns": excluded,
            "durationDays": duration_days,
            "declaredDurationDays": declared_duration_days,
            "observedRunSpanDays": observed_duration_days,
            "uniqueUsers": len(actors),
            "validatedUsers": len(validated_actors),
            "actualUserValidations": len(validations),
            "reusableArtifacts": len(artifacts),
        },
        "time": {
            "totalBaselineMinutes": round(total_baseline, 4),
            "totalNetSavedMinutes": round(total_net_saved, 4),
            "averageNetSavedMinutes": round(average_net_saved, 4) if average_net_saved is not None else None,
            "netEfficiencyPct": round(efficiency, 4) if efficiency is not None else None,
        },
        "value": {
            "annualTaskVolume": annual_volume,
            "annualVolumeSource": annual_volume_source,
            "annualSavedHours": round(annual_saved_hours, 4) if annual_saved_hours is not None else None,
            "standardHourlyCostCny": hourly_cost,
            **monetary,
            "annualNetValueCny": round(annual_value, 2) if annual_value is not None else None,
        },
        "qualityAndRisk": {
            "coreQualityPassed": quality_ok,
            "coreQualityReason": quality_reason,
            "riskMetricPassed": risk_ok,
            "riskMetricReason": risk_reason,
            "verifiedRunQualityPassRatePct": round(quality_passes / len(verified) * 100, 4) if verified else None,
            "verifiedRunRiskIncidentRatePct": round(risk_incidents / len(verified) * 100, 4) if verified else None,
            "dataSecurityIncidentCount": security_incidents,
        },
        "awardReadiness": award_rows,
        "recommendedAward": recommended["label"] if recommended else None,
        "secondTranche": {
            "applicable": recommended is not None and recommended["key"] in set(tranche_policy.get("eligibleTierKeys", [])),
            "ready": all(second_tranche_conditions.values()),
            "conditions": second_tranche_conditions,
        },
    }


def value(value: Any, suffix: str = "") -> str:
    if value is None:
        return "未核验"
    if isinstance(value, float):
        value = f"{value:,.2f}".rstrip("0").rstrip(".")
    return f"{value}{suffix}"


def markdown(report: dict[str, Any]) -> str:
    evidence = report["evidence"]
    timing = report["time"]
    economics = report["value"]
    quality = report["qualityAndRisk"]
    lines = [
        f"# {report.get('projectName') or 'AI提效项目'} - 提效证据报告",
        "",
        f"评估日期：{report.get('asOfDate') or '未核验'}",
        "",
        "## 核心结果",
        "",
        "| 指标 | 结果 |",
        "| --- | ---: |",
        f"| 已核验真实任务 | {value(evidence['verifiedRealBusinessRuns'], ' 次')} |",
        f"| 真实运行天数 | {value(evidence['durationDays'], ' 天')} |",
        f"| 实际使用者 | {value(evidence['uniqueUsers'], ' 人')} |",
        f"| 已完成使用确认的实际使用者 | {value(evidence['validatedUsers'], ' 人')} |",
        f"| 净节省时间 | {value(timing['totalNetSavedMinutes'], ' 分钟')} |",
        f"| 净提效比例 | {value(timing['netEfficiencyPct'], '%')} |",
        f"| 年度净价值 | {value(economics['annualNetValueCny'], ' CNY')} |",
        f"| 当前最高满足奖项 | {report.get('recommendedAward') or '暂未满足'} |",
        "",
        "## 质量与风险",
        "",
        f"- 核心质量：{quality['coreQualityReason']}。",
        f"- 风险指标：{quality['riskMetricReason']}。",
        f"- 已核验任务质量通过率：{value(quality['verifiedRunQualityPassRatePct'], '%')}。",
        f"- 已核验任务风险事件率：{value(quality['verifiedRunRiskIncidentRatePct'], '%')}。",
        f"- 数据安全事件：{quality['dataSecurityIncidentCount']} 次。",
        "",
        "## 奖项门槛",
        "",
        "| 奖项 | 是否满足 | 仍缺证据/条件 |",
        "| --- | --- | --- |",
    ]
    for row in report["awardReadiness"]:
        reasons = "-" if row["eligible"] else "；".join(row["reasons"])
        lines.append(f"| {row['label']} | {'是' if row['eligible'] else '否'} | {reasons} |")
    tranche = report["secondTranche"]
    lines.extend([
        "",
        "## 90天持续运行复核",
        "",
        f"- 是否适用：{'是' if tranche['applicable'] else '否'}。",
        f"- 当前是否满足后续兑现条件：{'是' if tranche['ready'] else '否'}。",
    ])
    for key, passed in tranche["conditions"].items():
        lines.append(f"- {key}: {'通过' if passed else '未通过/未核验'}")
    lines.extend([
        "",
        "> 本报告只汇总匿名、已核验数据。源时间研究、使用者确认和业务系统证据仍须由实际经办人、审核人复核。",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = evaluate(load_json(args.project), load_runs(args.runs))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"effectiveness evaluation failed: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else markdown(report)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
