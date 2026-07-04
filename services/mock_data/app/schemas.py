from typing import Any, Literal

from pydantic import BaseModel, Field


Severity = Literal["Low", "Medium", "High"]


class Equipment(BaseModel):
    equipment_id: str
    equipment_name: str
    tool_type: str
    area: str
    status: str


class Alarm(BaseModel):
    alarm_code: str
    description: str
    severity: Severity


class Incident(BaseModel):
    incident_id: str
    date: str
    equipment: str
    alarm_code: str
    root_cause: str
    corrective_action: str


class IncidentList(BaseModel):
    incidents: list[Incident]


class LookupRequest(BaseModel):
    equipment: str | None = None
    alarm_code: str | None = None
    include_incidents: bool = True
    incident_limit: int = Field(default=5, ge=1, le=20)


class LookupResponse(BaseModel):
    equipment: Equipment | None = None
    alarm: Alarm | None = None
    incidents: list[Incident] = Field(default_factory=list)
    missing: list[Literal["equipment", "alarm", "incidents"]] = Field(default_factory=list)


class HealthResponse(BaseModel):
    service: str
    status: Literal["ok", "degraded", "error"]
    dependencies: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: dict[str, Any] | None = None
