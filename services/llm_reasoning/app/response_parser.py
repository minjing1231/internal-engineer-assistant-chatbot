import json
import re
from typing import Any

from .schemas import (
    GenerateRequest,
    IssueSummary,
    SopReference,
    TroubleshootingAnswer,
)


def parse_answer(content: str, request: GenerateRequest | None = None) -> TroubleshootingAnswer:
    data = json.loads(content)
    data = _normalize_answer_payload(data, request)
    return TroubleshootingAnswer(**data)


def fallback_answer(request: GenerateRequest, uncertainty: str | None = None) -> TroubleshootingAnswer:
    equipment = request.structured_context.equipment
    alarm = request.structured_context.alarm

    relevant = [
        SopReference(
            source_id=chunk.source_id,
            title=chunk.title,
            section=chunk.section,
        )
        for chunk in request.sop_context
    ]

    recommended = _lines_for_sections(request, {"Troubleshooting Steps"})
    safety = _lines_for_sections(request, {"Safety Precautions"})
    escalation = _lines_for_sections(request, {"Escalation Criteria"})
    uncertainty_items = []
    if uncertainty:
        uncertainty_items.append(uncertainty)
    if equipment is None:
        uncertainty_items.append("Equipment was not found in structured data.")
    if alarm is None:
        uncertainty_items.append("Alarm was not found in structured data.")

    return TroubleshootingAnswer(
        issue_summary=IssueSummary(
            equipment=equipment.equipment_name if equipment else None,
            alarm_or_symptom=alarm.alarm_code if alarm else None,
            severity=alarm.severity if alarm else None,
        ),
        relevant_sop_context=relevant,
        recommended_checks=recommended,
        safety_precautions=safety,
        escalation_criteria=escalation,
        uncertainty=uncertainty_items,
    )


def _lines_for_sections(request: GenerateRequest, sections: set[str]) -> list[str]:
    lines: list[str] = []
    for chunk in request.sop_context:
        if chunk.section not in sections:
            continue
        for raw_line in chunk.content.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            line = line.removeprefix("- ").strip()
            if line and line not in lines:
                lines.append(line)
    return lines


def _normalize_answer_payload(data: dict[str, Any], request: GenerateRequest | None) -> dict[str, Any]:
    normalized = dict(data)
    normalized["issue_summary"] = _normalize_issue_summary(
        normalized.get("issue_summary"),
        request,
    )
    normalized["relevant_sop_context"] = _normalize_sop_context(
        normalized.get("relevant_sop_context"),
        request,
    )
    for key in [
        "recommended_checks",
        "safety_precautions",
        "escalation_criteria",
        "uncertainty",
    ]:
        normalized[key] = _as_list(normalized.get(key))
    return normalized


def _normalize_issue_summary(value: Any, request: GenerateRequest | None) -> dict[str, str | None]:
    if isinstance(value, dict):
        return value
    equipment = request.structured_context.equipment if request else None
    alarm = request.structured_context.alarm if request else None
    return {
        "equipment": equipment.equipment_name if equipment else None,
        "alarm_or_symptom": alarm.alarm_code if alarm else None,
        "severity": alarm.severity if alarm else None,
    }


def _normalize_sop_context(value: Any, request: GenerateRequest | None) -> list[dict[str, str | None]]:
    if isinstance(value, list):
        return value
    if request:
        return [
            {
                "source_id": chunk.source_id,
                "title": chunk.title,
                "section": chunk.section,
            }
            for chunk in request.sop_context
        ]
    if isinstance(value, str):
        return [{"source_id": "unknown", "title": value, "section": None}]
    return []


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        parts = [
            part.strip(" -\n\t")
            for part in re.split(r"\n+|;|(?<=\.)\s+(?=[A-Z])", value)
        ]
        return [part for part in parts if part]
    return [str(value)]
