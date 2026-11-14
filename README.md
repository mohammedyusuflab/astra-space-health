# ASTRA — Astronaut Health Monitoring Prototype

ASTRA is an educational astronaut-health monitoring prototype for the 2026 NASA Space Apps Challenge. It ingests health-indicator observations, compares them with an individual's personal baseline, explains changes, and prompts a review. The included crew and readings are fictional synthetic demonstration data.

> ASTRA is not a medical device, does not diagnose or recommend treatment, does not determine mission readiness, and is not a NASA product or endorsement.

## Current implementation

- CSV ingestion and validation
- valid/missing/invalid/outlier quality handling
- synthetic/real provenance with required references for real data
- provenance-separated personal baselines
- explainable deviation analysis and repeated-deviation alerts
- CLI and JSON report generation
- Browser dashboard for trends, baselines, alerts, provenance, and observation history
- Automated tests; Python standard library only

**Data status:** the demo CSV is synthetic. No astronaut medical records, spacecraft sensors, live telemetry, or qualifying challenge-resource dataset is currently connected. Do not describe the demo readings as NASA data.

## Run the analysis

Python 3.10+; no third-party dependencies.

```bash
PYTHONPATH=src python -m astra \
  --input data/synthetic/demo_telemetry.csv \
  --baseline-start 2026-11-01T00:00:00Z \
  --baseline-end 2026-11-07T23:59:00Z \
  --json output/demo-report.json
```

## Open the dashboard

After generating the report, start a local static server from the repository root:

```bash
python -m http.server 8000
```

Open http://localhost:8000/dashboard/ . The dashboard reads `output/demo-report.json`; it does not upload data to a server.

## Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## NASA context and data integrity

NASA Standard Measures describes human-spaceflight measurement domains including activity/light exposure, sleep, and cognition: https://www.nasa.gov/reference/standard-measures/

The challenge's official guidance states that Global Awards eligibility requires at least one NASA data source included in the selected challenge's Resources. The challenge page is https://www.spaceappschallenge.org/2026/challenges/health-monitoring-software/ . The challenge resources currently identified for ASTRA are references and research context; we have not yet verified a downloadable structured dataset from them. Accordingly, ASTRA does not claim to have met the qualifying-data requirement yet.

## Limitations

The default 2-standard-deviation band and two-consecutive-observation rule are demonstration settings only. They are not NASA requirements or medical thresholds.

## Documentation

- docs/CHALLENGE_BRIEF.md
- docs/DATA_SOURCES.md
- docs/SCOPE.md
- docs/ARCHITECTURE.md
- docs/ALGORITHM.md
- docs/IMPLEMENTATION_STATUS.md

## License

MIT.
