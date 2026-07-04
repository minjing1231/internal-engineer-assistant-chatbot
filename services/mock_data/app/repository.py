import csv
from pathlib import Path

from .schemas import Alarm, Equipment, Incident, LookupResponse


class MockDataRepository:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.equipment = [
            Equipment(**row) for row in self._read_csv("equipment_master.csv")
        ]
        self.alarms = [Alarm(**row) for row in self._read_csv("alarm_reference.csv")]
        self.incidents = [
            Incident(**row) for row in self._read_csv("historical_incidents.csv")
        ]

    def _read_csv(self, filename: str) -> list[dict[str, str]]:
        path = self.data_dir / filename
        with path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def get_equipment(self, equipment_name: str) -> Equipment | None:
        wanted = equipment_name.casefold()
        return next(
            (item for item in self.equipment if item.equipment_name.casefold() == wanted),
            None,
        )

    def get_alarm(self, alarm_code: str) -> Alarm | None:
        wanted = alarm_code.casefold()
        return next(
            (item for item in self.alarms if item.alarm_code.casefold() == wanted),
            None,
        )

    def search_incidents(
        self,
        equipment: str | None = None,
        alarm_code: str | None = None,
        limit: int = 5,
    ) -> list[Incident]:
        results = self.incidents
        if equipment:
            wanted_equipment = equipment.casefold()
            results = [
                item for item in results if item.equipment.casefold() == wanted_equipment
            ]
        if alarm_code:
            wanted_alarm = alarm_code.casefold()
            results = [
                item for item in results if item.alarm_code.casefold() == wanted_alarm
            ]
        return sorted(results, key=lambda item: item.date, reverse=True)[:limit]

    def lookup(
        self,
        equipment: str | None,
        alarm_code: str | None,
        include_incidents: bool = True,
        incident_limit: int = 5,
    ) -> LookupResponse:
        equipment_record = self.get_equipment(equipment) if equipment else None
        alarm_record = self.get_alarm(alarm_code) if alarm_code else None
        incidents = (
            self.search_incidents(equipment, alarm_code, incident_limit)
            if include_incidents
            else []
        )

        missing = []
        if equipment and equipment_record is None:
            missing.append("equipment")
        if alarm_code and alarm_record is None:
            missing.append("alarm")
        if include_incidents and not incidents:
            missing.append("incidents")

        return LookupResponse(
            equipment=equipment_record,
            alarm=alarm_record,
            incidents=incidents,
            missing=missing,
        )
