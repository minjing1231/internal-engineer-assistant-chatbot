from typing import Any, Literal

from pydantic import BaseModel, Field


Severity = Literal["Low", "Medium", "High"]


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    equipment: str | None = None
    alarm_code: str | None = None
    top_k: int = Field(default=4, ge=1, le=10)


class SopContextChunk(BaseModel):
    chunk_id: str
    source_id: str
    title: str
    section: str
    equipment: list[str] = Field(default_factory=list)
    alarm_code: str | None = None
    severity: Severity | None = None
    content: str
    score: float = 0.0


class SearchResponse(BaseModel):
    results: list[SopContextChunk]


class ReindexResponse(BaseModel):
    status: Literal["ok"]
    sop_path: str
    chunks_indexed: int


class HealthResponse(BaseModel):
    service: str
    status: Literal["ok", "degraded", "error"]
    dependencies: dict[str, Any] = Field(default_factory=dict)
