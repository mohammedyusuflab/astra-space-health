# ASTRA — Astronaut Health Monitoring Prototype

ASTRA is an educational astronaut-health monitoring prototype for the 2026 NASA Space Apps Challenge. It demonstrates how software can ingest health-indicator observations, compare them with an individual's personal baseline, explain changes, and prompt a review. The current runnable implementation uses a fictional astronaut and clearly labeled synthetic readings.

> ASTRA is not a medical device, does not diagnose or recommend treatment, does not determine mission readiness, and is not a NASA product or endorsement.

## Current implementation

- CSV ingestion and validation
- valid/missing/invalid/outlier quality handling
- synthetic/real provenance with required references for real data
- provenance-separated personal baselines
- explainable deviation analysis
- repeated-consecutive-deviation alerts
- CLI and JSON report generation
- automated tests

No NASA dataset, NASA system, spacecraft sensor, or live telemetry feed is connected yet.

## Run

Python 3.10+; no third-party dependencies.

```bash
PYTHONPATH=src python -m astra \
  --input data/synthetic/demo_telemetry.csv \
  --baseline-start 2026-11-01T00:00:00Z \
  --baseline-end 2026-11-07T23:59:00Z \
  --json output/demo-report.json
```

Tests:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## NASA context

NASA Standard Measures describes human-spaceflight measurement domains including activity/light exposure, sleep, and cognition: https://www.nasa.gov/reference/standard-measures/

The 2026 challenge requires a qualifying NASA data source from the selected challenge Resources for Global Awards eligibility. ASTRA has not integrated that source yet. See docs/CHALLENGE_BRIEF.md and docs/DATA_SOURCES.md.

## Limitations

The default 2-standard-deviation band and two-consecutive-observation rule are demonstration settings only. They are not NASA requirements or medical thresholds.

## Documentation

- docs/CHALLENGE_BRIEF.md
- docs/DATA_SOURCES.md
- docs/SCOPE.md
- docs/ARCHITECTURE.md
- docs/ALGORITHM.md
- docs/IMPLEMENTATION_STATUS.md
- AGENTS.md

## License

MIT.
