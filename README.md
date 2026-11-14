# ASTRA — Astronaut Health Monitoring Prototype

ASTRA is an educational astronaut-health monitoring prototype for the 2026 NASA Space Apps Challenge. It demonstrates explainable analysis of synthetic daily indicators and a separate historical view of NASA astronaut research data.

> ASTRA is not a medical device, does not diagnose or recommend treatment, does not determine mission readiness, and is not a NASA product or endorsement.

## What is implemented

- Python CSV ingestion and validation for the synthetic operational demo
- Provenance-separated personal baselines and explainable repeated-deviation review prompts
- Command-line interface and JSON report output
- Browser dashboard with synthetic telemetry and a separate NASA historical-research panel
- NASA OSDR OSD-569 Inspiration4 CBC dataset, source CSV, checksum, and normalized JSON
- Sample-level data-quality flagging; published source values are preserved
- Automated tests and a GitHub Actions workflow; Python standard library only

## Run the full demo

Python 3.10+; no third-party Python dependencies.

\`\`\`bash
PYTHONPATH=src python -m astra \\
  --input data/synthetic/demo_telemetry.csv \\
  --baseline-start 2026-11-01T00:00:00Z \\
  --baseline-end 2026-11-07T23:59:00Z \\
  --json output/demo-report.json
\`\`\`

The CLI writes two separate outputs:
- \`output/demo-report.json\`: synthetic daily telemetry analysis, personal baselines, and demonstration alerts.
- \`data/nasa/osd569-cbc.json\`: normalized historical NASA OSDR CBC measurements used by the research panel.

Regenerate the NASA research view on its own:

\`\`\`bash
PYTHONPATH=src python -m astra.osdr
\`\`\`

Re-download the original file directly from NASA OSDR and verify its SHA-256 before replacing the bundled copy:

\`\`\`bash
python scripts/fetch_nasa_osd569.py
\`\`\`

## Open the dashboard

From the repository root:

\`\`\`bash
python -m http.server 8000
\`\`\`

Open http://localhost:8000/dashboard/ . The browser workspace loads the demonstration readings and supports manual observation entry, CSV import, configurable baseline windows, deviation thresholds, repeat-alert rules, searchable result logs, and JSON/CSV export. Analysis runs locally in the browser session; imported readings are not sent to a server.

CSV import requires these columns: `timestamp`, `astronaut_id`, `metric`, `value`, `unit`, `source_type`, and `source`. Timestamps must include a timezone. Use `source_type=real` only with a traceable `source_reference`. NASA OSDR historical samples remain in their separate research panel and are not loaded into the operational telemetry dataset.

## Tests

\`\`\`bash
PYTHONPATH=src python -m unittest discover -s tests -v
\`\`\`

GitHub Actions runs the Python unit suite, Node.js tests for the browser analysis engine, JavaScript syntax checks when Node.js is available, and a complete static-site build on pushes and pull requests.

## NASA dataset and interpretation

The historical panel uses NASA Open Science Data Repository study OSD-569, SpaceX Inspiration4 whole-blood / complete blood count data:

- Study page: https://osdr.nasa.gov/bio/repo/data/studies/OSD-569
- Dataset DOI: 10.26030/e0rx-sh52
- Included file: \`data/nasa/osd569/LSDS-7_Complete_Blood_Count_CBC.upload_SUBMITTED.csv\`

The source file contains 553 measurements from 28 blood-draw samples involving four de-identified crew identifiers. The sample labels are L-92, L-44, and L-3 before launch and R+1, R+45, R+82, and R+194 after return. **There are no in-flight CBC samples.** This is historical research data, not a live spacecraft sensor feed and not the ASTRA-01 synthetic data.

The adapter flags sample C003 at L-92 because the absolute differential counts do not reconcile with the corresponding percentages and white-blood-cell count. The published values remain unchanged and are marked suspect. Missing analytes remain missing. Laboratory reference ranges are shown only as source context; they are not NASA mission limits, personalized baselines, or alert thresholds.

The OSDR dataset is shown in a separate research panel. It is not mixed into the synthetic telemetry baseline or repeated-alert engine. OSDR acknowledgement:

> Data are courtesy of the NASA Open Science Data Repository.

See [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md) for source, access, provenance, and limitations. Check the current NASA OSDR study terms before reuse outside this prototype; this repository does not claim a study-specific Creative Commons license.

The challenge Navigator's November 13 response recommends OSDR as a useful source for this challenge. The separate Global Awards rule requires a NASA data source from the challenge Resources; identify the precise qualifying Resources entry in the final submission and do not claim a mapping that has not been checked.

## Limitations

The 2-standard-deviation band and two-consecutive-observation rule in the synthetic engine are demonstration settings only. They are not NASA requirements or medical thresholds. Inspiration4 was a three-day mission, so OSD-569 cannot validate health monitoring for long-duration missions.

## Submission materials

- [English project submission draft](docs/SUBMISSION_DRAFT.md)
- [Interactive demo walkthrough and recording checklist](docs/DEMO_SCRIPT.md)
- [AI and tool-use disclosure](docs/AI_DISCLOSURE.md)
- [NASA data sources and provenance](docs/DATA_SOURCES.md)

## Public browser demo and deployment

Build the complete static website bundle from the repository root:

```bash
python scripts/build_site.py
```

The builder generates the synthetic report, validates the bundled NASA OSDR OSD-569 dataset, checks the interactive dashboard controls and JavaScript syntax when Node.js is available, and stages the landing page, dashboard application script, and JSON data under `build/site/`. The bundle is self-contained and does not require a Python server at runtime.

The **Deploy ASTRA website** workflow deploys automatically after pushes to `main` (and can also be run manually). The public site is not updated until that workflow succeeds. See [docs/LAUNCH_CHECKLIST.md](docs/LAUNCH_CHECKLIST.md) for deployment, anonymous browser checks, and competition handoff.

Expected project URL after a successful deployment:
https://mohammedyusuflab.github.io/astra-space-health/

Expected dashboard URL:
https://mohammedyusuflab.github.io/astra-space-health/dashboard/

## License

The software license applies to ASTRA code. It does not supersede the source terms for NASA OSDR data.
