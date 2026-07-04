from fastapi import FastAPI, HTTPException, Query

from .config import DATA_DIR
from .logging_utils import install_file_logging
from .repository import MockDataRepository
from .schemas import (
    Alarm,
    Equipment,
    HealthResponse,
    IncidentList,
    LookupRequest,
    LookupResponse,
)

app = FastAPI(
    title="Mock Data Service",
    version="0.1.0",
    description="Structured mock equipment, alarm, and historical incident data API.",
)
install_file_logging(app, "mock-data")
repository = MockDataRepository(DATA_DIR)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    return HealthResponse(
        service="mock-data",
        status="ok",
        dependencies={
            "equipment_records": len(repository.equipment),
            "alarm_records": len(repository.alarms),
            "incident_records": len(repository.incidents),
        },
    )


@app.get("/equipment/{equipment_name}", response_model=Equipment, tags=["equipment"])
async def get_equipment(equipment_name: str) -> Equipment:
    equipment = repository.get_equipment(equipment_name)
    if equipment is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


@app.get("/alarms/{alarm_code}", response_model=Alarm, tags=["alarms"])
async def get_alarm(alarm_code: str) -> Alarm:
    alarm = repository.get_alarm(alarm_code)
    if alarm is None:
        raise HTTPException(status_code=404, detail="Alarm not found")
    return alarm


@app.get("/incidents", response_model=IncidentList, tags=["incidents"])
async def get_incidents(
    equipment: str | None = None,
    alarm_code: str | None = None,
    limit: int = Query(default=5, ge=1, le=20),
) -> IncidentList:
    return IncidentList(
        incidents=repository.search_incidents(equipment, alarm_code, limit)
    )


@app.post("/lookup", response_model=LookupResponse, tags=["lookup"])
async def lookup(request: LookupRequest) -> LookupResponse:
    if not request.equipment and not request.alarm_code:
        raise HTTPException(
            status_code=400,
            detail="Provide equipment, alarm_code, or both.",
        )
    return repository.lookup(
        equipment=request.equipment,
        alarm_code=request.alarm_code,
        include_incidents=request.include_incidents,
        incident_limit=request.incident_limit,
    )
