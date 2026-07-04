from pathlib import Path

from services.mock_data.app.repository import MockDataRepository


DATA_DIR = Path(__file__).resolve().parents[3] / "data"


def test_lookup_known_equipment_alarm_and_incidents():
    repo = MockDataRepository(DATA_DIR)

    result = repo.lookup("Etcher-03", "RF101")

    assert result.equipment is not None
    assert result.equipment.equipment_id == "EQ001"
    assert result.alarm is not None
    assert result.alarm.severity == "High"
    assert [item.incident_id for item in result.incidents] == ["H002", "H001"]
    assert result.missing == []


def test_lookup_unknown_alarm_reports_missing():
    repo = MockDataRepository(DATA_DIR)

    result = repo.lookup("Unknown-99", "ABC999")

    assert result.equipment is None
    assert result.alarm is None
    assert "equipment" in result.missing
    assert "alarm" in result.missing
