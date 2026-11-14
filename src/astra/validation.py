"""Input parsing and validation using only Python's standard library."""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Iterable, Mapping

from .models import ReadingQuality, TelemetryReading, ValidationIssue, ValidationReport

_REQUIRED_FIELDS = ("timestamp", "astronaut_id", "metric", "unit", "source_type", "source")
_ALLOWED_SOURCE_TYPES = {"synthetic", "real"}
_ALLOWED_QUALITIES = {quality.value for quality in ReadingQuality}


def _parse_timestamp(raw: str) -> datetime:
    value = datetime.fromisoformat(raw.strip().replace("Z", "+00:00"))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must include a timezone, for example Z or +00:00")
    return value


def validate_records(records: Iterable[Mapping[str, Any]]) -> ValidationReport:
    """Validate CSV-like dictionaries and preserve incomplete observations as missing."""
    readings: list[TelemetryReading] = []
    issues: list[ValidationIssue] = []

    for row_number, record in enumerate(records, start=2):
        normalized = {str(key).strip(): value for key, value in record.items()}
        row_errors = False

        for field in _REQUIRED_FIELDS:
            if normalized.get(field) is None or str(normalized.get(field)).strip() == "":
                issues.append(ValidationIssue(row_number, field, "required", f"Required field '{field}' is empty."))
                row_errors = True
        if row_errors:
            continue

        try:
            timestamp = _parse_timestamp(str(normalized["timestamp"]))
        except (TypeError, ValueError) as exc:
            issues.append(ValidationIssue(row_number, "timestamp", "invalid_timestamp", str(exc)))
            continue

        source_type = str(normalized["source_type"]).strip().lower()
        source_reference = str(normalized.get("source_reference", "") or "").strip()
        if source_type not in _ALLOWED_SOURCE_TYPES:
            issues.append(ValidationIssue(row_number, "source_type", "invalid_source_type", "source_type must be 'synthetic' or 'real'."))
            continue
        if source_type == "real" and not source_reference:
            issues.append(ValidationIssue(row_number, "source_reference", "missing_source_reference", "Real data must include a traceable source URL, DOI, or repository reference."))
            continue

        raw_quality = str(normalized.get("quality", "valid") or "valid").strip().lower()
        if raw_quality not in _ALLOWED_QUALITIES:
            issues.append(ValidationIssue(row_number, "quality", "invalid_quality", f"quality must be one of: {', '.join(sorted(_ALLOWED_QUALITIES))}."))
            continue
        quality = ReadingQuality(raw_quality)

        raw_value = normalized.get("value")
        value = None
        if raw_value is None or str(raw_value).strip() == "":
            if quality == ReadingQuality.VALID:
                quality = ReadingQuality.MISSING
            issues.append(ValidationIssue(row_number, "value", "missing_value", "Value is missing; it will not be treated as a normal reading."))
        else:
            try:
                value = float(raw_value)
                if not math.isfinite(value):
                    raise ValueError("value must be a finite number")
            except (TypeError, ValueError) as exc:
                issues.append(ValidationIssue(row_number, "value", "invalid_value", str(exc)))
                continue

        if quality in {ReadingQuality.MISSING, ReadingQuality.INVALID}:
            value = None
        elif value is None:
            quality = ReadingQuality.MISSING

        mission_day = None
        raw_mission_day = normalized.get("mission_day")
        if raw_mission_day is not None and str(raw_mission_day).strip() != "":
            try:
                mission_day = int(raw_mission_day)
                if mission_day < 1:
                    raise ValueError("mission_day must be a positive integer")
            except (TypeError, ValueError) as exc:
                issues.append(ValidationIssue(row_number, "mission_day", "invalid_mission_day", str(exc)))
                continue

        readings.append(TelemetryReading(
            timestamp=timestamp,
            astronaut_id=str(normalized["astronaut_id"]).strip(),
            metric=str(normalized["metric"]).strip().lower(),
            value=value,
            unit=str(normalized["unit"]).strip(),
            source_type=source_type,
            source=str(normalized["source"]).strip(),
            source_reference=source_reference,
            quality=quality,
            mission_day=mission_day,
            context_note=str(normalized.get("context_note", "") or "").strip(),
        ))

    readings.sort(key=lambda item: (item.astronaut_id, item.metric, item.timestamp))
    return ValidationReport(tuple(readings), tuple(issues))
