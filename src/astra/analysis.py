"""Explainable deviation analysis with repeated-observation alerting."""

from __future__ import annotations

from collections import defaultdict
import math
from typing import Iterable

from .models import AnalysisResult, Baseline, ReadingQuality, ResultStatus, TelemetryReading


def analyze_readings(
    readings: Iterable[TelemetryReading],
    baselines: Iterable[Baseline],
    *,
    deviation_threshold: float = 2.0,
    repeated_deviations_for_alert: int = 2,
) -> tuple[AnalysisResult, ...]:
    """Compare readings with personal baselines; no medical thresholds are used."""
    if not math.isfinite(deviation_threshold) or deviation_threshold <= 0:
        raise ValueError("deviation_threshold must be a finite number greater than zero")
    if repeated_deviations_for_alert < 2:
        raise ValueError("repeated_deviations_for_alert must be at least 2")

    baseline_index = {
        (item.astronaut_id, item.metric, item.unit, item.source_type, item.source, item.source_reference): item
        for item in baselines
    }
    grouped: dict[tuple[str, str, str, str, str, str], list[TelemetryReading]] = defaultdict(list)
    for reading in readings:
        grouped[(reading.astronaut_id, reading.metric, reading.unit, reading.source_type, reading.source, reading.source_reference)].append(reading)

    output: list[AnalysisResult] = []
    for key in sorted(grouped):
        baseline = baseline_index.get(key)
        consecutive = 0
        for reading in sorted(grouped[key], key=lambda item: item.timestamp):
            if reading.quality != ReadingQuality.VALID or reading.value is None:
                consecutive = 0
                output.append(AnalysisResult(
                    reading=reading, status=ResultStatus.MISSING,
                    baseline_mean=baseline.mean if baseline else None,
                    baseline_standard_deviation=baseline.standard_deviation if baseline else None,
                    deviation_score=None, consecutive_deviations=0, alert=False,
                    explanation="This observation is missing or marked unusable. It is excluded from analysis and is not interpreted as normal.",
                    suggested_action="Verify the source measurement; record a correction or context note if available.",
                ))
                continue

            if baseline is None:
                consecutive = 0
                output.append(AnalysisResult(
                    reading=reading, status=ResultStatus.NO_BASELINE,
                    baseline_mean=None, baseline_standard_deviation=None,
                    deviation_score=None, consecutive_deviations=0, alert=False,
                    explanation="There is not enough valid personal reference data for this metric and unit.",
                    suggested_action="Collect sufficient valid observations in a defined calibration period before comparing changes.",
                ))
                continue

            delta = reading.value - baseline.mean
            if baseline.standard_deviation == 0:
                is_deviation = abs(delta) > 1e-12
                score = None
                comparison = "the calibration readings had no variation"
            else:
                score = delta / baseline.standard_deviation
                is_deviation = abs(score) >= deviation_threshold
                comparison = f"{score:+.2f} baseline standard deviations from the personal mean"

            if is_deviation:
                consecutive += 1
                is_alert = consecutive >= repeated_deviations_for_alert
                status = ResultStatus.ALERT if is_alert else ResultStatus.DEVIATION
                if is_alert:
                    explanation = (
                        f"{reading.metric} is outside the configured demonstration band on "
                        f"{consecutive} consecutive valid observations ({comparison}); "
                        f"the personal baseline is {baseline.mean:.2f} {baseline.unit}."
                    )
                    action = "Verify the measurement and review mission-approved procedures or contact the mission medical officer according to protocol."
                else:
                    explanation = (
                        f"{reading.metric} differs from the personal baseline ({baseline.mean:.2f} "
                        f"{baseline.unit}) by {comparison}. One observation alone does not trigger an alert."
                    )
                    action = "Check the measurement and add relevant workload, schedule, or event context."
            else:
                consecutive = 0
                is_alert = False
                status = ResultStatus.WITHIN_BASELINE
                explanation = (
                    f"{reading.metric} is within the configured demonstration band around the personal "
                    f"baseline ({baseline.mean:.2f} {baseline.unit}; standard deviation "
                    f"{baseline.standard_deviation:.2f} {baseline.unit})."
                )
                action = "No follow-up is generated by this demonstration rule; continue recording valid observations."

            output.append(AnalysisResult(
                reading=reading, status=status,
                baseline_mean=baseline.mean,
                baseline_standard_deviation=baseline.standard_deviation,
                deviation_score=score,
                consecutive_deviations=consecutive,
                alert=is_alert,
                explanation=explanation,
                suggested_action=action,
            ))

    return tuple(sorted(output, key=lambda item: (item.reading.timestamp, item.reading.astronaut_id, item.reading.metric)))
