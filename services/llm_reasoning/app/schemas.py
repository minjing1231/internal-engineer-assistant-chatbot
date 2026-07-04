from typing import Any, Literal

from pydantic import BaseModel, Field


Severity = Literal["Low", "Medium", "High"]
EscalationDecision = Literal["Yes", "No", "Conditional", "Unknown"]


class Equipment(BaseModel):
    equipment_id: str
    equipment_name: str
    tool_type: str
    area: str | None = None
    status: str | None = None


class Alarm(BaseModel):
    alarm_code: str
    description: str | None = None
    severity: Severity | None = None


class Incident(BaseModel):
    incident_id: str
    date: str
    equipment: str
    alarm_code: str
    root_cause: str
    corrective_action: str


class SopContextChunk(BaseModel):
    chunk_id: str | None = None
    source_id: str
    title: str
    section: str
    content: str
    score: float | None = None


class StructuredContext(BaseModel):
    equipment: Equipment | None = None
    alarm: Alarm | None = None
    incidents: list[Incident] = Field(default_factory=list)


class GenerateRequest(BaseModel):
    question: str = Field(min_length=1)
    sop_context: list[SopContextChunk] = Field(min_length=1)
    structured_context: StructuredContext = Field(default_factory=StructuredContext)


class IssueSummary(BaseModel):
    equipment: str | None = None
    alarm_or_symptom: str | None = None
    severity: Severity | None = None


class ActionDecision(BaseModel):
    primary_action: str | None = None
    escalate: EscalationDecision = "Unknown"
    reason: str | None = None


class SopReference(BaseModel):
    source_id: str
    title: str
    section: str | None = None


class TroubleshootingAnswer(BaseModel):
    action_decision: ActionDecision = Field(default_factory=ActionDecision)
    issue_summary: IssueSummary
    relevant_sop_context: list[SopReference] = Field(default_factory=list)
    recommended_checks: list[str] = Field(default_factory=list)
    likely_causes: list[str] = Field(default_factory=list)
    recovery_next_steps: list[str] = Field(default_factory=list)
    safety_precautions: list[str] = Field(default_factory=list)
    escalation_criteria: list[str] = Field(default_factory=list)
    uncertainty: list[str] = Field(default_factory=list)


class Usage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0


class GenerateResponse(BaseModel):
    answer: TroubleshootingAnswer
    model: str
    usage: Usage | None = None
    warnings: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    service: str
    status: Literal["ok", "degraded", "error"]
    dependencies: dict[str, Any] = Field(default_factory=dict)
