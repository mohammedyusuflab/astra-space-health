# ASTRA Analysis Engine — Algorithm Notes

## Processing sequence

1. Read rows from CSV.
2. Validate required fields, timezone-aware ISO 8601 timestamps, finite numeric values, source type, source reference, and quality.
3. Preserve missing observations as missing; exclude missing, invalid, and outlier observations from baseline calculation.
4. Calculate a separate personal baseline for each astronaut, metric, unit, and provenance over the selected calibration interval.
5. Require at least three valid calibration observations by default.
6. Compare later valid observations with the baseline mean and population standard deviation.
7. Mark a demonstration deviation when absolute z-score is at least 2.0. If standard deviation is zero, a changed value is treated as a deviation without inventing an infinite score.
8. Generate an alert only after at least two consecutive valid deviations. Missing/unusable observations reset the counter.
9. Return observed value, baseline, score where defined, consecutive count, explanation, and a non-treatment review prompt.

## Why this rule

A transparent statistical rule is easier to inspect and explain during a short prototype than an opaque machine-learning model. The defaults are demonstration settings, not health thresholds.

## Provenance

Every input row identifies synthetic or real provenance. Real inputs require a traceable source reference. Baselines are separated by provenance, so unrelated sources are never blended.
