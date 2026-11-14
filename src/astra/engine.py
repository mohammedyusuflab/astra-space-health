"""High-level orchestration for the ASTRA analysis engine."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .analysis import analyze_readings
from .baseline import build_baselines
from .io import load_csv
from .models import AnalysisReport


def run_analysis(
    csv_path: str | Path,
    *,
    baseline_start: datetime,
    baseline_end: datetime,
    minimum_baseline_samples: int = 3,
    deviation_threshold: float = 2.0,
    repeated_deviations_for_alert: int = 2,
) -> AnalysisReport:
    validation = load_csv(csv_path)
    baselines = build_baselines(
        validation.readings,
        period_start=baseline_start,
        period_end=baseline_end,
        minimum_samples=minimum_baseline_samples,
    )
    results = analyze_readings(
        validation.readings,
        baselines,
        deviation_threshold=deviation_threshold,
        repeated_deviations_for_alert=repeated_deviations_for_alert,
    )
    return AnalysisReport(baselines, results, validation.issues)
