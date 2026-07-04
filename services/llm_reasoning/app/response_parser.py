import json

from .schemas import (
    GenerateRequest,
    IssueSummary,
    SopReference,
    TroubleshootingAnswer,
)


def parse_answer(content: str) -> TroubleshootingAnswer:
    data = json.loads(content)
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
