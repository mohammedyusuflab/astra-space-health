"""Core data models for the ASTRA educational analysis engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ReadingQuality(str, Enum):
    VALID = "valid"
    MISSING = "missing"
    INVALID = "invalid"
    OUTLIER = "outlier"


class ResultStatus(str, Enum):
    WITHIN_BASELINE = "within_baseline"
    DEVIATION = "deviation"
    ALERT = "repeated_deviation"
    MISSING = "missing_or_unusable"
    NO_BASELINE = "no_baseline"


@dataclass(frozen=True)
class TelemetryReading:
    timestamp: datetime
    astronaut_id: str
    metric: str
    value: Optional[float]
    unit: str
    source_type: str
    source: str
    source_reference: str = ""
    quality: ReadingQuality = ReadingQuality.VALID
    mission_day: Optional[int] = None
    context_note: str = ""


@dataclass(frozen=True)
class ValidationIssue:
    row_number: int
    field: str
    code: str
    message: str


@dataclass(frozen=True)
class ValidationReport:
    readings: tuple[TelemetryReading, ...]
    issues: tuple[ValidationIssue, ...]


@dataclass(frozen=True)
class Baseline:
    astronaut_id: str
    metric: str
    unit: str
    source_type: str
    source: str
    source_reference: str
    mean: float
    standard_deviation: float
    sample_count: int
    period_start: datetime
    period_end: datetime


@dataclass(frozen=True)
class AnalysisResult:
    reading: TelemetryReading
    status: ResultStatus
    baseline_mean: Optional[float]
    baseline_standard_deviation: Optional[float]
    deviation_score: Optional[float]
    consecutive_deviations: int
    alert: bool
    explanation: str
    suggested_action: str


@dataclass(frozen=True)
class AnalysisReport:
    baselines: tuple[Baseline, ...]
    results: tuple[AnalysisResult, ...]
    validation_issues: tuple[ValidationIssue, ...]

    @property
    def alerts(self) -> tuple[AnalysisResult, ...]:
        return tuple(result for result in self.results if result.alert)
