import json
import re
from typing import Any

from .schemas import (
    ActionDecision,
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
    incidents = request.structured_context.incidents
    uncertainty_items = []
    if uncertainty:
        uncertainty_items.append(uncertainty)
    if equipment is None:
        uncertainty_items.append("Equipment was not found in structured data.")
    if alarm is None:
        uncertainty_items.append("Alarm was not found in structured data.")

    return TroubleshootingAnswer(
        action_decision=ActionDecision(
            primary_action=_default_primary_action(recommended, escalation),
            escalate=_default_escalation_decision(request, escalation),
            reason=_default_decision_reason(request, escalation),
        ),
        issue_summary=IssueSummary(
            equipment=equipment.equipment_name if equipment else None,
            alarm_or_symptom=alarm.alarm_code if alarm else None,
            severity=alarm.severity if alarm else None,
        ),
        relevant_sop_context=relevant,
        recommended_checks=recommended,
        likely_causes=_incident_causes(incidents),
        recovery_next_steps=_recovery_steps(recommended, escalation),
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
    normalized["action_decision"] = _normalize_action_decision(
        normalized.get("action_decision"),
        request,
        normalized,
    )
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
        "likely_causes",
        "recovery_next_steps",
        "safety_precautions",
        "escalation_criteria",
        "uncertainty",
    ]:
        normalized[key] = _as_list(normalized.get(key))
    return normalized


def _normalize_action_decision(
    value: Any,
    request: GenerateRequest | None,
    data: dict[str, Any],
) -> dict[str, str | None]:
    if isinstance(value, dict):
        return {
            "primary_action": value.get("primary_action"),
            "escalate": _normalize_escalate(value.get("escalate")),
            "reason": value.get("reason"),
        }
    recommended = _as_list(data.get("recommended_checks"))
    escalation = _as_list(data.get("escalation_criteria"))
    return {
        "primary_action": _default_primary_action(recommended, escalation),
        "escalate": _default_escalation_decision(request, escalation),
        "reason": _default_decision_reason(request, escalation),
    }


def _normalize_escalate(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text in {"yes", "true", "escalate"}:
        return "Yes"
    if text in {"no", "false", "do not escalate"}:
        return "No"
    if text in {"conditional", "condition", "depends"}:
        return "Conditional"
    return "Unknown"


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


def _default_primary_action(recommended: list[str], escalation: list[str]) -> str | None:
    if recommended:
        return recommended[0]
    if escalation:
        return "Review escalation criteria and verify whether any condition is met."
    return None


def _default_escalation_decision(request: GenerateRequest | None, escalation: list[str]) -> str:
    question = request.question.lower() if request else ""
    severity = request.structured_context.alarm.severity if request and request.structured_context.alarm else None
    if "unknown" in question or (request and request.structured_context.alarm is None):
        return "Unknown"
    if "should i escalate" in question or "what should be escalated" in question:
        if severity == "High" or escalation:
            return "Yes"
        return "Conditional"
    if severity == "High" and escalation:
        return "Conditional"
    return "Conditional" if escalation else "Unknown"


def _default_decision_reason(request: GenerateRequest | None, escalation: list[str]) -> str | None:
    if request and request.structured_context.alarm and request.structured_context.alarm.severity == "High":
        return "The alarm is high severity; verify SOP escalation criteria before recovery."
    if escalation:
        return "Escalation depends on whether the listed SOP criteria are met."
    return None


def _incident_causes(incidents) -> list[str]:
    causes: list[str] = []
    for incident in incidents:
        cause = incident.root_cause
        if cause and cause not in causes:
            causes.append(cause)
    return causes


def _recovery_steps(recommended: list[str], escalation: list[str]) -> list[str]:
    steps = recommended[:3]
    if escalation:
        steps.append("Escalate if any listed escalation criterion is met.")
    return steps
