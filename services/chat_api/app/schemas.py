from typing import Any, Literal

from pydantic import BaseModel, Field


Severity = Literal["Low", "Medium", "High"]


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=4, ge=1, le=10)
    include_incidents: bool = True


class IssueSummary(BaseModel):
    equipment: str | None = None
    alarm_or_symptom: str | None = None
    severity: Severity | None = None


class SopReference(BaseModel):
    source_id: str
    title: str
    section: str | None = None


class SourceReference(BaseModel):
    type: Literal["sop", "equipment", "alarm", "incident"]
    id: str
    section: str | None = None


class TroubleshootingAnswer(BaseModel):
    issue_summary: IssueSummary
    relevant_sop_context: list[SopReference] = Field(default_factory=list)
    recommended_checks: list[str] = Field(default_factory=list)
    safety_precautions: list[str] = Field(default_factory=list)
    escalation_criteria: list[str] = Field(default_factory=list)
    uncertainty: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: TroubleshootingAnswer
    sources: list[SourceReference] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    service: str
    status: Literal["ok", "degraded", "error"]
    dependencies: dict[str, Any] = Field(default_factory=dict)


class ServiceError(RuntimeError):
    pass
