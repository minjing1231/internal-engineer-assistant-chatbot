from services.llm_reasoning.app.prompts.troubleshooting_prompt import build_messages
from services.llm_reasoning.app.response_parser import fallback_answer, parse_answer
from services.llm_reasoning.app.schemas import (
    Alarm,
    Equipment,
    GenerateRequest,
    SopContextChunk,
    StructuredContext,
)


def _request() -> GenerateRequest:
    return GenerateRequest(
        question="Etcher-03 triggered RF101. What should I check first?",
        sop_context=[
            SopContextChunk(
                source_id="SOP-ETCH-001",
                title="Etcher RF Power Instability - Alarm RF101",
                section="Troubleshooting Steps",
                content="- Verify RF generator output reading from tool HMI.\n- Check recent RF power trend.",
            ),
            SopContextChunk(
                source_id="SOP-ETCH-001",
                title="Etcher RF Power Instability - Alarm RF101",
                section="Safety Precautions",
                content="- Do not touch RF cables while RF power is enabled.",
            ),
        ],
        structured_context=StructuredContext(
            equipment=Equipment(
                equipment_id="EQ001",
                equipment_name="Etcher-03",
                tool_type="Plasma Etcher",
                area="Etch",
                status="Active",
            ),
            alarm=Alarm(
                alarm_code="RF101",
                description="RF Power Instability",
                severity="High",
            ),
        ),
    )


def test_prompt_contains_grounding_rules_and_context():
    messages = build_messages(_request())

    assert messages[0]["role"] == "system"
    assert "Use only the provided SOP context" in messages[0]["content"]
    assert "SOP-ETCH-001" in messages[1]["content"]
    assert "Etcher-03" in messages[1]["content"]


def test_fallback_answer_uses_retrieved_sop_context():
    answer = fallback_answer(_request(), uncertainty="Provider unavailable.")

    assert answer.issue_summary.equipment == "Etcher-03"
    assert answer.issue_summary.alarm_or_symptom == "RF101"
    assert answer.recommended_checks[0].startswith("Verify RF generator")
    assert answer.safety_precautions == [
        "Do not touch RF cables while RF power is enabled."
    ]
    assert "Provider unavailable." in answer.uncertainty


def test_parse_answer_normalizes_string_fields_from_model():
    content = """
{
  "issue_summary": "Etcher-03 triggered RF101 during plasma ignition.",
  "relevant_sop_context": "SOP-ETCH-001 - Plasma Etcher RF instability.",
  "recommended_checks": "Verify RF generator output. Check recent RF power trend.",
  "safety_precautions": "Ensure tool is in safe state; Do not touch RF cables while RF power is enabled.",
  "escalation_criteria": "Downtime exceeds 30 minutes; RF101 repeats more than twice within 7 days.",
  "uncertainty": "No definitive root cause can be confirmed from the provided context."
}
"""

    answer = parse_answer(content, _request())

    assert answer.issue_summary.equipment == "Etcher-03"
    assert answer.issue_summary.alarm_or_symptom == "RF101"
    assert answer.relevant_sop_context[0].source_id == "SOP-ETCH-001"
    assert answer.recommended_checks == [
        "Verify RF generator output.",
        "Check recent RF power trend.",
    ]
    assert answer.safety_precautions == [
        "Ensure tool is in safe state",
        "Do not touch RF cables while RF power is enabled.",
    ]
