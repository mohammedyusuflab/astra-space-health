# ASTRA — NASA Space Apps 2026 Submission Draft

## Project title
ASTRA — Astronaut Health Monitoring and Decision Support

## Challenge
Create Health Monitoring Software for Astronauts on Space Missions

## Short description
ASTRA is an astronaut-facing health-monitoring prototype that makes changes in health indicators easier to inspect and explain. It combines an operational demonstration using clearly labelled synthetic daily telemetry with a separate historical research view built from NASA's Inspiration4 OSDR OSD-569 blood-count dataset. The two data paths remain separate: synthetic readings demonstrate personal baselines and sustained-deviation review prompts, while NASA research samples are displayed with their original relative collection times, source reference intervals, and data-quality flags. ASTRA does not treat historical lab samples as live spacecraft telemetry, and it does not diagnose, prescribe treatment, or determine mission readiness.

## Problem and motivation
On long-duration missions, crew members need to recognize meaningful changes in their own health indicators and understand what evidence supports a concern. A raw list of readings is difficult to interpret without personal context, clear provenance, and an explanation of why a change is being highlighted. Public astronaut-health data are fragmented and do not necessarily provide a single continuous stream of vital signs.

## What ASTRA does
1. Loads timestamped synthetic daily health-indicator observations from CSV.
2. Validates timestamps, values, quality, source type, and provenance.
3. Builds per-astronaut personal baselines for an explicitly selected calibration period.
4. Compares later observations with the matching baseline and explains deviations.
5. Requires repeated consecutive deviations before raising a demonstration alert.
6. Presents the result in a browser dashboard with trends, baseline context, an alert-review queue, and an observation log.
7. Separately loads NASA OSDR OSD-569 Inspiration4 CBC research data and presents the historical sample timeline, pre-flight comparison, source lab ranges, and data-quality warnings.

## NASA data used
**NASA Open Science Data Repository (OSDR), OSD-569 — Whole Blood Measurements from the SpaceX Inspiration4 Mission**

- Study page: https://osdr.nasa.gov/bio/repo/data/studies/OSD-569
- OSDR Inspiration4 mission collection: https://osdr.nasa.gov/bio/repo/data/missions/SpaceX%20Inspiration4
- DOI: 10.26030/e0rx-sh52
- Included source file: data/nasa/osd569/LSDS-7_Complete_Blood_Count_CBC.upload_SUBMITTED.csv
- Data view: data/nasa/osd569-cbc.json

The bundled CBC file contains 553 measurements from 28 blood-draw samples, 20 analytes, and four de-identified crew identifiers. Collection labels are L-92, L-44, and L-3 before launch and R+1, R+45, R+82, and R+194 after return. There are no in-flight CBC samples in this file.

ASTRA flags sample C003 at L-92 because its absolute white-cell differential counts do not reconcile with the reported percentages and white blood cell count. Original values are preserved and marked suspect. Missing analytes are not imputed. Source lab reference intervals are presented as research context only, not mission limits or medical thresholds.

## Challenge resource reference
The NASA challenge resource **Ongoing HRP Research in Space** provides the relevant NASA Human Research Program research context. Its Omics Archive context describes astronaut biospecimen research, and NASA's OSDR SpaceX Inspiration4 mission collection lists OSD-569. The challenge Navigator also recommends OSDR as a useful source for astronaut-health research.

List these separately in the submission:
- Challenge resource: NASA, Ongoing HRP Research in Space — https://www.nasa.gov/hrp/ongoing-hrp-research/
- Data source: NASA OSDR, OSD-569 — https://osdr.nasa.gov/bio/repo/data/studies/OSD-569

Before final submission, confirm the precise Resource entry shown in the team's live submission page and cite it exactly as displayed.

## Technical implementation
- Python 3.10+; standard library only; no third-party Python packages.
- CSV ingestion and validation.
- Provenance-aware baselines and explainable rule-based analysis for the synthetic demo.
- NASA OSDR source adapter with schema checks, checksum protection, relative sample-time handling, and sample-quality flagging.
- Static browser dashboard with two separately labelled data paths.
- GitHub Actions workflow for unit tests and normalized OSDR data build.

## Safety and limitations
ASTRA is an educational prototype, not a medical device. It does not diagnose, prescribe, or determine flight readiness. The synthetic deviation band and repeated-observation rule are demonstration parameters, not clinical or NASA flight-medicine thresholds. OSD-569 is retrospective research from the three-day Inspiration4 mission, has no in-flight CBC samples, and does not validate long-duration mission monitoring. The demo does not connect to spacecraft sensors or current astronaut medical records.

## Repository and run instructions
- Source repository: https://github.com/mohammedyusuflab/astra-space-health
- Run from the repository root: PYTHONPATH=src python -m astra --input data/synthetic/demo_telemetry.csv --baseline-start 2026-11-01T00:00:00Z --baseline-end 2026-11-07T23:59:00Z --json output/demo-report.json
- Start local server: python -m http.server 8000
- Open http://localhost:8000/dashboard/
- Build the complete static website bundle with `python scripts/build_site.py`; output is written to `build/site/`.
- After GitHub Pages is enabled and the manual deployment workflow succeeds, the expected public project URL is https://mohammedyusuflab.github.io/astra-space-health/ and the dashboard URL is https://mohammedyusuflab.github.io/astra-space-health/dashboard/. These target URLs must be tested anonymously before they are entered into the final competition form.

## AI tools and external resources
See AI_DISCLOSURE.md and DATA_SOURCES.md. The AI assistant helped draft code and documentation; no generative AI model runs inside the ASTRA prototype.
