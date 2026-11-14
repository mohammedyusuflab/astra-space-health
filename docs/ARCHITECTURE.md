# ASTRA Architecture

## Implemented flow

1. CSV input loads observations and provenance.
2. Validation checks identifiers, timezone-aware timestamps, finite values, source type/reference, and quality.
3. Baseline calculation groups by astronaut, metric, unit, and provenance and calculates mean and population standard deviation over an explicit calibration window.
4. Deviation analysis compares later valid observations with the matching baseline.
5. Alert evaluation requires repeated consecutive deviations.
6. Explanation output contains baseline context, deviation score where defined, reason, and non-treatment review prompt.
7. CLI/JSON output presents results without coupling the engine to a web interface.

## Repository structure

```
.
├── src/astra/
├── data/synthetic/demo_telemetry.csv
├── docs/
└── tests/test_engine.py
```

## Boundaries

The implementation does not include a database, API, graphical dashboard, authentication, live sensor integration, NASA data ingestion, real-time streaming, or deployment.

Synthetic and real data are explicitly separated. Real data requires traceable provenance.
