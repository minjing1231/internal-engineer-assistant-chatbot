import re

from ..schemas import (
    ChatRequest,
    ChatResponse,
    IssueSummary,
    ServiceError,
    SopReference,
    SourceReference,
    TroubleshootingAnswer,
)


ALARM_RE = re.compile(r"\b[A-Z]{2,}\d{2,}\b")
EQUIPMENT_RE = re.compile(r"\b[A-Z][A-Za-z]+-\d{2}\b")


def extract_alarm_code(question: str) -> str | None:
    match = ALARM_RE.search(question)
    return match.group(0) if match else None


def extract_equipment(question: str) -> str | None:
    match = EQUIPMENT_RE.search(question)
    return match.group(0) if match else None


class TroubleshootingFlow:
    def __init__(self, data_client, rag_client, llm_client):
        self.data_client = data_client
        self.rag_client = rag_client
        self.llm_client = llm_client

    async def answer(self, request: ChatRequest) -> ChatResponse:
        equipment_hint = extract_equipment(request.question)
        alarm_hint = extract_alarm_code(request.question)
        warnings: list[str] = []

        structured_context = await self._lookup_data(
            equipment_hint,
            alarm_hint,
            request.include_incidents,
            warnings,
        )

        rag_response = await self.rag_client.search(
            query=request.question,
            equipment=equipment_hint,
            alarm_code=alarm_hint,
            top_k=request.top_k,
        )
        sop_context = rag_response.get("results", [])
        if not sop_context:
            return self._insufficient_information_response(
                equipment_hint,
                alarm_hint,
                warnings,
            )

        try:
            llm_response = await self.llm_client.generate(
                question=request.question,
                sop_context=sop_context,
                structured_context=structured_context,
            )
            answer = TroubleshootingAnswer(**llm_response["answer"])
            warnings.extend(llm_response.get("warnings", []))
        except (KeyError, ServiceError, ValueError) as exc:
            warnings.append(f"LLM service unavailable; deterministic fallback used: {exc}")
            answer = self._fallback_answer(sop_context, structured_context)

        return ChatResponse(
            answer=answer,
            sources=self._build_sources(sop_context, structured_context),
            warnings=warnings,
        )

    async def _lookup_data(
        self,
        equipment: str | None,
        alarm_code: str | None,
        include_incidents: bool,
        warnings: list[str],
    ) -> dict:
        if not equipment and not alarm_code:
            return {"equipment": None, "alarm": None, "incidents": []}
        try:
            return await self.data_client.lookup(equipment, alarm_code, include_incidents)
        except ServiceError as exc:
            warnings.append(f"Mock Data Service unavailable: {exc}")
            return {"equipment": None, "alarm": None, "incidents": []}

    def _insufficient_information_response(
        self,
        equipment: str | None,
        alarm_code: str | None,
        warnings: list[str],
    ) -> ChatResponse:
        uncertainty = [
            "No relevant SOP context was found. The assistant cannot provide a grounded troubleshooting answer."
        ]
        if equipment:
            uncertainty.append(f"Equipment hint from question: {equipment}")
        if alarm_code:
            uncertainty.append(f"Alarm hint from question: {alarm_code}")
        return ChatResponse(
            answer=TroubleshootingAnswer(
                issue_summary=IssueSummary(
                    equipment=equipment,
                    alarm_or_symptom=alarm_code,
                    severity=None,
                ),
                uncertainty=uncertainty,
            ),
            sources=[],
            warnings=warnings,
        )

    def _fallback_answer(self, sop_context: list[dict], structured_context: dict) -> TroubleshootingAnswer:
        equipment = structured_context.get("equipment") or {}
        alarm = structured_context.get("alarm") or {}
        return TroubleshootingAnswer(
            issue_summary=IssueSummary(
                equipment=equipment.get("equipment_name"),
                alarm_or_symptom=alarm.get("alarm_code"),
                severity=alarm.get("severity"),
            ),
            relevant_sop_context=[
                SopReference(
                    source_id=item["source_id"],
                    title=item["title"],
                    section=item.get("section"),
                )
                for item in sop_context
            ],
            recommended_checks=self._extract_lines(sop_context, "Troubleshooting Steps"),
            safety_precautions=self._extract_lines(sop_context, "Safety Precautions"),
            escalation_criteria=self._extract_lines(sop_context, "Escalation Criteria"),
            uncertainty=["LLM response was unavailable, so this answer was generated from retrieved SOP context only."],
        )

    def _extract_lines(self, sop_context: list[dict], section: str) -> list[str]:
        lines: list[str] = []
        for item in sop_context:
            if item.get("section") != section:
                continue
            for raw_line in item.get("content", "").splitlines():
                line = raw_line.strip().removeprefix("- ").strip()
                if line and line not in lines:
                    lines.append(line)
        return lines

    def _build_sources(self, sop_context: list[dict], structured_context: dict) -> list[SourceReference]:
        sources: list[SourceReference] = []
        for item in sop_context:
            source = SourceReference(
                type="sop",
                id=item["source_id"],
                section=item.get("section"),
            )
            if source not in sources:
                sources.append(source)

        equipment = structured_context.get("equipment")
        if equipment:
            sources.append(SourceReference(type="equipment", id=equipment["equipment_id"]))
        alarm = structured_context.get("alarm")
        if alarm:
            sources.append(SourceReference(type="alarm", id=alarm["alarm_code"]))
        for incident in structured_context.get("incidents", []):
            sources.append(SourceReference(type="incident", id=incident["incident_id"]))
        return sources
