import asyncio

from services.chat_api.app.orchestration.troubleshooting_flow import (
    TroubleshootingFlow,
    extract_alarm_code,
    extract_equipment,
)
from services.chat_api.app.schemas import ChatRequest


class FakeDataClient:
    async def lookup(self, equipment, alarm_code, include_incidents):
        return {
            "equipment": {
                "equipment_id": "EQ001",
                "equipment_name": equipment,
                "tool_type": "Plasma Etcher",
                "area": "Etch",
                "status": "Active",
            },
            "alarm": {
                "alarm_code": alarm_code,
                "description": "RF Power Instability",
                "severity": "High",
            },
            "incidents": [
                {
                    "incident_id": "H002",
                    "date": "2026-06-08",
                    "equipment": equipment,
                    "alarm_code": alarm_code,
                    "root_cause": "RF generator drift",
                    "corrective_action": "Recalibrated RF generator",
                }
            ],
            "missing": [],
        }


class FakeRagClient:
    async def search(self, query, equipment, alarm_code, top_k):
        return {
            "results": [
                {
                    "chunk_id": "SOP-ETCH-001:troubleshooting-steps",
                    "source_id": "SOP-ETCH-001",
                    "title": "Etcher RF Power Instability - Alarm RF101",
                    "section": "Troubleshooting Steps",
                    "equipment": ["Plasma Etcher", "Etcher-03"],
                    "alarm_code": "RF101",
                    "severity": "High",
                    "content": "- Verify RF generator output reading from tool HMI.",
                    "score": 10.0,
                }
            ]
        }


class FakeLlmClient:
    async def generate(self, question, sop_context, structured_context):
        return {
            "answer": {
                "issue_summary": {
                    "equipment": "Etcher-03",
                    "alarm_or_symptom": "RF101",
                    "severity": "High",
                },
                "relevant_sop_context": [
                    {
                        "source_id": "SOP-ETCH-001",
                        "title": "Etcher RF Power Instability - Alarm RF101",
                        "section": "Troubleshooting Steps",
                    }
                ],
                "recommended_checks": [
                    "Verify RF generator output reading from tool HMI."
                ],
                "safety_precautions": [],
                "escalation_criteria": [],
                "uncertainty": [],
            },
            "warnings": [],
        }


class MismatchDataClient:
    async def lookup(self, equipment, alarm_code, include_incidents):
        return {
            "equipment": {
                "equipment_id": "EQ003",
                "equipment_name": "CVD-05",
                "tool_type": "PECVD Tool",
                "area": "Deposition",
                "status": "Active",
            },
            "alarm": None,
            "incidents": [],
            "missing": [],
        }


class CvdRagClient:
    async def search(self, query, equipment, alarm_code, top_k):
        return {
            "results": [
                {
                    "chunk_id": "SOP-CVD-003:escalation-criteria",
                    "source_id": "SOP-CVD-003",
                    "title": "CVD Gas Flow Deviation - Alarm GAS012",
                    "section": "Escalation Criteria",
                    "equipment": ["PECVD", "CVD-05"],
                    "alarm_code": "GAS012",
                    "severity": "High",
                    "content": "- Any gas safety concern exists.",
                    "score": 4.7,
                }
            ]
        }


class FailingLlmClient:
    async def generate(self, question, sop_context, structured_context):
        raise AssertionError("LLM should not be called for an unconfirmed mismatch")


class UnknownEquipmentDataClient:
    async def lookup(self, equipment, alarm_code, include_incidents):
        return {
            "equipment": None,
            "alarm": {
                "alarm_code": "RF101",
                "description": "RF Power Instability",
                "severity": "High",
            },
            "incidents": [],
            "missing": [],
        }


def test_extract_hints_from_question():
    question = "Etcher-03 triggered RF101 during plasma ignition."

    assert extract_equipment(question) == "Etcher-03"
    assert extract_alarm_code(question) == "RF101"
    assert extract_alarm_code("CVD-05 triggered GAS0 during deposition.") == "GAS0"


def test_flow_returns_answer_with_sources():
    flow = TroubleshootingFlow(FakeDataClient(), FakeRagClient(), FakeLlmClient())

    response = asyncio.run(
        flow.answer(
            ChatRequest(
                question="Etcher-03 triggered RF101 during plasma ignition. What should I check first?"
            )
        )
    )

    assert response.answer.issue_summary.equipment == "Etcher-03"
    assert response.sources[0].id == "SOP-ETCH-001"
    assert any(source.type == "incident" and source.id == "H002" for source in response.sources)


def test_unconfirmed_alarm_mismatch_does_not_use_nearby_sop_as_confirmed_answer():
    flow = TroubleshootingFlow(MismatchDataClient(), CvdRagClient(), FailingLlmClient())

    response = asyncio.run(
        flow.answer(
            ChatRequest(
                question="CVD-05 triggered GAS0 during deposition. Should I escalate?"
            )
        )
    )

    assert response.answer.action_decision.escalate == "Unknown"
    assert response.answer.issue_summary.alarm_or_symptom == "GAS0"
    assert response.answer.issue_summary.severity is None
    assert response.sources == []
    assert "GAS012" in response.answer.action_decision.reason


def test_unconfirmed_equipment_mismatch_does_not_apply_sop_to_unknown_tool():
    flow = TroubleshootingFlow(UnknownEquipmentDataClient(), FakeRagClient(), FailingLlmClient())

    response = asyncio.run(
        flow.answer(
            ChatRequest(
                question="Etcher-07 triggered RF101 during plasma ignition. What should I check first?"
            )
        )
    )

    assert response.answer.action_decision.escalate == "Unknown"
    assert response.answer.issue_summary.equipment == "Etcher-07"
    assert response.answer.issue_summary.alarm_or_symptom == "RF101"
    assert response.sources == []
    assert "Etcher-07" in response.answer.action_decision.reason
    assert "Etcher-03" in response.answer.action_decision.reason
