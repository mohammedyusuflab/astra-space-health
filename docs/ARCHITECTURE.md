# ASTRA Architecture

## Operational synthetic telemetry flow

1. CSV input loads the fictional astronaut's synthetic observations.
2. Validation checks identifiers, timezone-aware timestamps, finite values, source type/reference, and quality.
3. Baseline calculation groups by astronaut, metric, unit, and provenance for an explicitly selected calibration window.
4. Deviation analysis compares later valid observations with the matching personal baseline.
5. Alert evaluation requires repeated consecutive deviations.
6. Explanation output contains baseline context, deviation score, reason, and a non-treatment review prompt.
7. CLI/JSON output presents the results independently of the web interface.

## NASA historical research flow

1. NASA OSDR OSD-569 CBC source CSV is stored under \`data/nasa/osd569/\`.
2. \`src/astra/osdr.py\` validates its schema, numeric values, reference ranges, sample-time labels, and duplicate analytes.
3. A source-integrity check compares absolute white-cell differential values with the corresponding reported percentage and WBC. Suspect samples are flagged and source values are retained.
4. The adapter writes normalized research data to \`data/nasa/osd569-cbc.json\`.
5. The browser dashboard reads that JSON into a separate historical-research panel.

This path intentionally does not call \`TelemetryReading\`, the personal-baseline builder, or the repeated-deviation alert engine. Relative sample labels such as L-92 and R+1 remain relative labels; the application does not invent calendar timestamps.

## Repository structure

\`\`\`
.
├── src/astra/
│   ├── analysis.py
│   ├── baseline.py
│   ├── cli.py
│   ├── engine.py
│   ├── osdr.py
│   └── ...
├── data/
│   ├── synthetic/demo_telemetry.csv
│   └── nasa/osd569/
├── dashboard/index.html
├── scripts/fetch_nasa_osd569.py
├── docs/
└── tests/
\`\`\`

## Boundaries

No live spacecraft sensor feed, current astronaut medical records, or real-time NASA system is connected. OSD-569 is retrospective human research data. ASTRA is not a medical device.
