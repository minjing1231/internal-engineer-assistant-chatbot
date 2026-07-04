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


def test_extract_hints_from_question():
    question = "Etcher-03 triggered RF101 during plasma ignition."

    assert extract_equipment(question) == "Etcher-03"
    assert extract_alarm_code(question) == "RF101"


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
