import re

from ..schemas import (
    ActionDecision,
    ChatRequest,
    ChatResponse,
    IssueSummary,
    ServiceError,
    SopReference,
    SourceReference,
    TroubleshootingAnswer,
)


ALARM_RE = re.compile(r"\b[A-Z]{2,}\d+\b")
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
        if self._has_unconfirmed_alarm_mismatch(alarm_hint, structured_context, sop_context):
            warnings.append(
                f"Requested alarm {alarm_hint} was not confirmed in structured data; retrieved SOP context uses a different alarm."
            )
            return self._alarm_mismatch_response(
                equipment_hint,
                alarm_hint,
                structured_context,
                sop_context,
                warnings,
            )
        if self._has_unconfirmed_equipment_mismatch(equipment_hint, structured_context, sop_context):
            warnings.append(
                f"Requested equipment {equipment_hint} was not confirmed in structured data; retrieved SOP context uses different equipment."
            )
            return self._equipment_mismatch_response(
                equipment_hint,
                alarm_hint,
                structured_context,
                sop_context,
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

    def _has_unconfirmed_alarm_mismatch(
        self,
        alarm_hint: str | None,
        structured_context: dict,
        sop_context: list[dict],
    ) -> bool:
        if not alarm_hint:
            return False
        structured_alarm = structured_context.get("alarm") or {}
        if structured_alarm.get("alarm_code") == alarm_hint:
            return False
        sop_alarm_codes = {
            item.get("alarm_code")
            for item in sop_context
            if item.get("alarm_code")
        }
        return bool(sop_alarm_codes and alarm_hint not in sop_alarm_codes)

    def _has_unconfirmed_equipment_mismatch(
        self,
        equipment_hint: str | None,
        structured_context: dict,
        sop_context: list[dict],
    ) -> bool:
        if not equipment_hint:
            return False
        structured_equipment = structured_context.get("equipment") or {}
        if structured_equipment.get("equipment_name") == equipment_hint:
            return False
        sop_equipment = {
            equipment
            for item in sop_context
            for equipment in item.get("equipment", [])
        }
        return bool(sop_equipment and equipment_hint not in sop_equipment)

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
                action_decision=ActionDecision(
                    primary_action="Verify the equipment and alarm code, then search for matching SOP guidance.",
                    escalate="Unknown",
                    reason="No relevant SOP context was found, so the assistant cannot make a grounded escalation decision.",
                ),
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

    def _alarm_mismatch_response(
        self,
        equipment_hint: str | None,
        alarm_hint: str | None,
        structured_context: dict,
        sop_context: list[dict],
        warnings: list[str],
    ) -> ChatResponse:
        equipment = structured_context.get("equipment") or {}
        retrieved_alarms = sorted(
            {
                item.get("alarm_code")
                for item in sop_context
                if item.get("alarm_code")
            }
        )
        alarm_label = alarm_hint or "Unknown alarm"
        suggested_alarm = retrieved_alarms[0] if retrieved_alarms else None
        direct_response = (
            f"Cannot find alarm type {alarm_label}. Do you mean {suggested_alarm}?"
            if suggested_alarm
            else f"Cannot find alarm type {alarm_label}."
        )
        return ChatResponse(
            answer=TroubleshootingAnswer(
                direct_response=direct_response,
                action_decision=ActionDecision(
                    primary_action="Verify the exact alarm code on the tool HMI before applying a specific SOP.",
                    escalate="Unknown",
                    reason=(
                        f"The requested alarm {alarm_label} is not confirmed in structured data and does not match "
                        f"the retrieved SOP alarm code(s): {', '.join(retrieved_alarms) or 'none'}."
                    ),
                ),
                issue_summary=IssueSummary(
                    equipment=equipment.get("equipment_name") or equipment_hint,
                    alarm_or_symptom=alarm_hint,
                    severity=None,
                ),
                recovery_next_steps=[
                    "Re-check the alarm code and equipment ID from the tool HMI.",
                    "Search again with the confirmed alarm code.",
                    "If there is any gas safety concern, stop recovery work and follow site escalation procedure.",
                ],
                uncertainty=[
                    f"Alarm {alarm_label} was not found in the mock alarm reference data.",
                    (
                        "Retrieved SOP context was for a different alarm code "
                        f"({', '.join(retrieved_alarms)}), so it was not used as confirmed evidence."
                    ),
                ],
            ),
            sources=[],
            warnings=warnings,
        )

    def _equipment_mismatch_response(
        self,
        equipment_hint: str | None,
        alarm_hint: str | None,
        structured_context: dict,
        sop_context: list[dict],
        warnings: list[str],
    ) -> ChatResponse:
        alarm = structured_context.get("alarm") or {}
        retrieved_equipment = sorted(
            {
                equipment
                for item in sop_context
                for equipment in item.get("equipment", [])
            }
        )
        equipment_label = equipment_hint or "Unknown equipment"
        suggested_equipment = self._suggest_equipment_id(retrieved_equipment)
        direct_response = (
            f"Cannot find equipment ID {equipment_label}. Do you mean {suggested_equipment}?"
            if suggested_equipment
            else f"Cannot find equipment ID {equipment_label}."
        )
        return ChatResponse(
            answer=TroubleshootingAnswer(
                direct_response=direct_response,
                action_decision=ActionDecision(
                    primary_action="Verify the equipment ID on the tool HMI before applying a specific SOP.",
                    escalate="Unknown",
                    reason=(
                        f"The requested equipment {equipment_label} is not confirmed in structured data and does not match "
                        f"the retrieved SOP equipment: {', '.join(retrieved_equipment) or 'none'}."
                    ),
                ),
                issue_summary=IssueSummary(
                    equipment=equipment_hint,
                    alarm_or_symptom=alarm_hint,
                    severity=alarm.get("severity"),
                ),
                recovery_next_steps=[
                    "Re-check the equipment ID and alarm code from the tool HMI.",
                    "Search again with the confirmed equipment ID.",
                    "If the alarm is safety-critical or the tool cannot be confirmed, escalate to the equipment owner.",
                ],
                uncertainty=[
                    f"Equipment {equipment_label} was not found in the mock equipment master data.",
                    (
                        "Retrieved SOP context was for different equipment "
                        f"({', '.join(retrieved_equipment)}), so it was not used as confirmed evidence."
                    ),
                ],
            ),
            sources=[],
            warnings=warnings,
        )

    def _suggest_equipment_id(self, equipment_values: list[str]) -> str | None:
        for value in equipment_values:
            if EQUIPMENT_RE.fullmatch(value):
                return value
        return equipment_values[0] if equipment_values else None

    def _fallback_answer(self, sop_context: list[dict], structured_context: dict) -> TroubleshootingAnswer:
        equipment = structured_context.get("equipment") or {}
        alarm = structured_context.get("alarm") or {}
        recommended_checks = self._extract_lines(sop_context, "Troubleshooting Steps")
        escalation_criteria = self._extract_lines(sop_context, "Escalation Criteria")
        return TroubleshootingAnswer(
            action_decision=ActionDecision(
                primary_action=(
                    recommended_checks[0]
                    if recommended_checks
                    else "Review retrieved SOP context before taking recovery action."
                ),
                escalate="Conditional" if escalation_criteria else "Unknown",
                reason="LLM fallback used; escalation depends on the retrieved SOP criteria.",
            ),
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
            recommended_checks=recommended_checks,
            likely_causes=self._incident_causes(structured_context),
            recovery_next_steps=self._recovery_steps(recommended_checks, escalation_criteria),
            safety_precautions=self._extract_lines(sop_context, "Safety Precautions"),
            escalation_criteria=escalation_criteria,
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

    def _incident_causes(self, structured_context: dict) -> list[str]:
        causes: list[str] = []
        for incident in structured_context.get("incidents", []):
            cause = incident.get("root_cause")
            if cause and cause not in causes:
                causes.append(cause)
        return causes

    def _recovery_steps(self, recommended_checks: list[str], escalation_criteria: list[str]) -> list[str]:
        steps = recommended_checks[:3]
        if escalation_criteria:
            steps.append("Escalate if any listed escalation criterion is met.")
        return steps

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
