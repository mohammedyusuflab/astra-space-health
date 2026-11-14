# NASA Space Apps Challenge 2026 — Challenge Brief

## Official challenge

- Challenge: Create Health Monitoring Software for Astronauts on Space Missions
- Official page: https://www.spaceappschallenge.org/2026/challenges/health-monitoring-software/
- Difficulty: Intermediate
- Subjects: Human Exploration, Software, Space Exploration

The challenge asks teams to build software that gathers health indicators and enables astronauts to evaluate and act on their health status.

## ASTRA solution

ASTRA has two deliberately separate data paths:

1. **Operational demonstration:** synthetic daily telemetry for fictional astronaut ASTRA-01. It demonstrates data validation, personal baselines, explainable deviations, and a repeated-deviation review prompt.
2. **NASA historical research:** NASA OSDR OSD-569 Inspiration4 CBC measurements. They are displayed separately as retrospective research data with source citation, relative sample labels, and data-quality flags.

This separation prevents historical CBC samples from being misrepresented as current telemetry or used to calculate the fictional astronaut's daily alert baseline.

## NASA data source

- Provider: NASA Open Science Data Repository (OSDR)
- Study: OSD-569, SpaceX Inspiration4 whole blood / CBC
- Study page: https://osdr.nasa.gov/bio/repo/data/studies/OSD-569
- DOI: 10.26030/e0rx-sh52
- Local source file: \`data/nasa/osd569/LSDS-7_Complete_Blood_Count_CBC.upload_SUBMITTED.csv\`

The file provides 553 lab observations across 28 samples from four de-identified crew identifiers. Its sample labels are L-92, L-44, L-3 before launch and R+1, R+45, R+82, R+194 after return. It contains no in-flight CBC samples.

The challenge Navigator's November 13, 2026 response recommends OSDR and NASA Life Sciences Portal as research repositories, while warning that public astronaut-health data may be samples or processed research rather than live vital-sign streams. ASTRA uses the OSDR CBC file as a historical research example and uses separately labelled synthetic data for the operational time-series demonstration.

## Challenge eligibility and citation

The GO Team's general resources answer says Global Awards eligibility requires at least one NASA data source included in the selected challenge's Resources tab. The Health Monitoring Software Navigator separately says there is no single mandatory downloadable dataset and recommends OSDR. The project submission must therefore identify the exact challenge Resources entry used, cite the OSDR study/file, and list all other datasets, tools, code, text, and visual assets used. Do not claim an unverified direct link from the challenge Resources tab.

## Challenge-resource lineage and eligibility

The challenge Resources include NASA's **Ongoing HRP Research in Space**:
https://www.nasa.gov/hrp/ongoing-hrp-research/

This HRP page lists the Omics Archive as a human investigation. NASA describes the Omics Archive as research using astronaut blood, urine, saliva, feces, and cells:
https://www.nasa.gov/reference/omics-archive/

NASA's SpaceX Inspiration4 mission collection in OSDR lists OSD-569:
https://osdr.nasa.gov/bio/repo/data/missions/SpaceX%20Inspiration4

The Health Monitoring Software challenge Navigator separately recommends NASA OSDR as a useful starting point for relevant research datasets:
https://github.com/nasa/spaceapps/discussions/2025

ASTRA therefore documents its data-source path as the challenge's HRP research context -> NASA Omics Archive context -> NASA OSDR Inspiration4 mission -> OSD-569 CBC. In the project submission, list the exact challenge Resource title and the OSDR study/file separately. The GO Team's general rule for Global Awards requires a NASA source from the selected challenge's Resources:
https://github.com/nasa/spaceapps/discussions/1827
Do not claim that the challenge Resources page directly links the OSD-569 file unless that exact link is visible in the live submission interface.

## Safety and scientific limitations

- ASTRA is not a medical device; it does not diagnose, recommend treatment, or determine flight readiness.
- OSD-569 is retrospective lab data from four Inspiration4 crew members on a three-day mission. It does not validate monitoring for long-duration missions.
- Lab reference ranges are source context only, not NASA mission limits or personalized alert thresholds.
- A suspect C003 / L-92 sample is preserved and flagged, not corrected.
- Synthetic alert thresholds are demonstration placeholders, not clinical rules.

## Submission checklist

- Confirm team registration and current submission deadline in the official project form.
- Include a public demo and explain the two separate data paths.
- Cite NASA OSDR OSD-569 and include the OSDR acknowledgement.
- Identify the specific challenge Resources entry relied on for Global Awards eligibility.
- Disclose AI tools used.
- Check final form requirements and public-access permissions.
