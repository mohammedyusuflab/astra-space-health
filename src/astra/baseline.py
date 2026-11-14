"""Personal baseline calculation over an explicitly selected calibration window."""

from __future__ import annotations

from datetime import datetime
from statistics import fmean, pstdev
from typing import Iterable

from .models import Baseline, ReadingQuality, TelemetryReading


def build_baselines(
    readings: Iterable[TelemetryReading],
    *,
    period_start: datetime,
    period_end: datetime,
    minimum_samples: int = 3,
) -> tuple[Baseline, ...]:
    """Create per-astronaut, per-metric, per-unit baselines within [start, end]."""
    if period_start.tzinfo is None or period_end.tzinfo is None:
        raise ValueError("baseline period boundaries must be timezone-aware")
    if period_end < period_start:
        raise ValueError("period_end must be on or after period_start")
    if minimum_samples < 2:
        raise ValueError("minimum_samples must be at least 2")

    groups: dict[tuple[str, str, str, str, str, str], list[TelemetryReading]] = {}
    for reading in readings:
        if not (period_start <= reading.timestamp <= period_end):
            continue
        if reading.quality != ReadingQuality.VALID or reading.value is None:
            continue
        key = (
            reading.astronaut_id, reading.metric, reading.unit,
            reading.source_type, reading.source, reading.source_reference,
        )
        groups.setdefault(key, []).append(reading)

    baselines: list[Baseline] = []
    for (astronaut_id, metric, unit, source_type, source, source_reference), group in sorted(groups.items()):
        if len(group) < minimum_samples:
            continue
        values = [item.value for item in group if item.value is not None]
        baselines.append(Baseline(
            astronaut_id=astronaut_id, metric=metric, unit=unit,
            source_type=source_type, source=source, source_reference=source_reference,
            mean=fmean(values), standard_deviation=pstdev(values),
            sample_count=len(values),
            period_start=min(item.timestamp for item in group),
            period_end=max(item.timestamp for item in group),
        ))
    return tuple(baselines)
