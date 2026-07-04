from pathlib import Path
import re

from ..schemas import SopContextChunk


SOP_HEADING_RE = re.compile(r"^## (SOP-[A-Z]+-\d+): (.+)$")
SECTION_RE = re.compile(r"^### (.+)$")
ALARM_RE = re.compile(r"Alarm ([A-Z]+\d+)")


def load_sop_chunks(path: Path) -> list[SopContextChunk]:
    text = path.read_text(encoding="utf-8")
    records = _split_sops(text)
    chunks: list[SopContextChunk] = []
    for record in records:
        chunks.extend(_record_to_chunks(record))
    return chunks


def _split_sops(text: str) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    current_section: str | None = None
    section_lines: list[str] = []

    def flush_section() -> None:
        nonlocal section_lines, current_section
        if current is not None and current_section:
            sections = current.setdefault("sections", {})
            assert isinstance(sections, dict)
            sections[current_section] = "\n".join(section_lines).strip()
        section_lines = []

    for line in text.splitlines():
        sop_match = SOP_HEADING_RE.match(line)
        if sop_match:
            flush_section()
            if current is not None:
                records.append(current)
            source_id, title = sop_match.groups()
            alarm_match = ALARM_RE.search(title)
            current = {
                "source_id": source_id,
                "title": title,
                "alarm_code": alarm_match.group(1) if alarm_match else None,
                "equipment": [],
                "severity": None,
                "sections": {},
            }
            current_section = None
            continue

        if current is None:
            continue

        if line.startswith("Applicable Equipment:"):
            raw = line.split(":", 1)[1].strip()
            current["equipment"] = [part.strip() for part in raw.split("/") if part.strip()]
            continue

        if line.startswith("Severity:"):
            current["severity"] = line.split(":", 1)[1].strip()
            continue

        section_match = SECTION_RE.match(line)
        if section_match:
            flush_section()
            current_section = section_match.group(1)
            continue

        if current_section:
            section_lines.append(line)

    flush_section()
    if current is not None:
        records.append(current)
    return records


def _record_to_chunks(record: dict[str, object]) -> list[SopContextChunk]:
    source_id = str(record["source_id"])
    title = str(record["title"])
    equipment = list(record.get("equipment") or [])
    alarm_code = record.get("alarm_code")
    severity = record.get("severity")
    sections = dict(record.get("sections") or {})

    summary = "\n".join(
        item
        for item in [
            f"Applicable Equipment: {', '.join(equipment)}" if equipment else "",
            f"Severity: {severity}" if severity else "",
        ]
        if item
    )
    chunks = [
        SopContextChunk(
            chunk_id=f"{source_id}:summary",
            source_id=source_id,
            title=title,
            section="Summary",
            equipment=equipment,
            alarm_code=str(alarm_code) if alarm_code else None,
            severity=severity if severity in {"Low", "Medium", "High"} else None,
            content=summary,
        )
    ]

    for section, content in sections.items():
        if not content:
            continue
        slug = section.lower().replace(" ", "-")
        chunks.append(
            SopContextChunk(
                chunk_id=f"{source_id}:{slug}",
                source_id=source_id,
                title=title,
                section=section,
                equipment=equipment,
                alarm_code=str(alarm_code) if alarm_code else None,
                severity=severity if severity in {"Low", "Medium", "High"} else None,
                content=content,
            )
        )
    return chunks
