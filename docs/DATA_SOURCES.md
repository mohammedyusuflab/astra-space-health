# Data-Source Register

## Provenance rules

- Synthetic telemetry and historical research records are separate data products.
- Synthetic values are never labeled as NASA data.
- Real records retain a traceable source page, direct file URL, accession, and citation.
- Historical sample timepoints are never converted into invented timestamps.
- Research records are not treated as live sensor feeds or clinical thresholds.

## Integrated NASA source: OSDR OSD-569

**Dataset:** SpaceX Inspiration4 whole blood / Complete Blood Count (CBC)  
**Provider:** NASA Open Science Data Repository (OSDR)  
**Study page:** https://osdr.nasa.gov/bio/repo/data/studies/OSD-569  
**Direct file:** \`LSDS-7_Complete_Blood_Count_CBC.upload_SUBMITTED.csv\`  
**DOI:** 10.26030/e0rx-sh52  
**Bundled CSV:** \`data/nasa/osd569/LSDS-7_Complete_Blood_Count_CBC.upload_SUBMITTED.csv\`  
**Normalized JSON:** \`data/nasa/osd569-cbc.json\`  
**SHA-256:** \`10a878b009eb2ea11a13fe92ad698098858639e8ed02f5ee849431313b9457d3\`

The original CSV was checked against the source SHA-256 recorded in a NASA OSDR data mirror, then bundled unchanged. A downloader at \`scripts/fetch_nasa_osd569.py\` retrieves the file from NASA's OSDR download endpoint and verifies the same hash before writing it. Run \`PYTHONPATH=src python -m astra.osdr\` to regenerate the normalized JSON.

### Data shape

- 553 observations across 28 blood-draw samples.
- Four de-identified crew identifiers: C001–C004.
- Twenty reported analytes.
- Seven collection labels: L-92, L-44, L-3 (before launch) and R+1, R+45, R+82, R+194 (after return).
- There are no in-flight CBC samples in this file.
- Some sample/analyte combinations are absent; the adapter preserves those gaps rather than imputing values.

### ASTRA use

OSD-569 is presented as a separate historical-research panel in the dashboard. It demonstrates source-aware import, sample timeline handling, unit/reference-range preservation, and explicit data-quality reporting. It is not passed into the synthetic telemetry engine, personal-baseline builder, or repeated-deviation alert logic.

### Data-quality treatment

A data-integrity check compares absolute differential blood counts with their corresponding percentage and total white-blood-cell count. Sample C003 at L-92 fails that internal consistency check. Its original 19 values are preserved and marked \`suspect\`; the adapter does not silently correct them or use them for inference.

This is a data-quality heuristic, not a clinical rule. Source-provided lab reference ranges are displayed per measurement as Earth-laboratory context only. They are not astronaut-specific baselines, NASA mission limits, warning thresholds, or diagnostic criteria.

### Access, citation, and acknowledgement

- Study: https://osdr.nasa.gov/bio/repo/data/studies/OSD-569
- OSDR download endpoint: https://osdr.nasa.gov/geode-py/ws/studies/OSD-569/download?source=datamanager&file=LSDS-7_Complete_Blood_Count_CBC.upload_SUBMITTED.csv
- DOI: 10.26030/e0rx-sh52
- Required acknowledgement for this project: **“Data are courtesy of the NASA Open Science Data Repository.”**

NASA OSDR describes access to public data and publishes data-use terms. This repository does not assert a study-specific CC BY or CC0 license for OSD-569. Follow the current OSDR terms and preserve citation/acknowledgement; the ASTRA software license does not re-license the dataset.

## Synthetic operational demo telemetry

\`data/synthetic/demo_telemetry.csv\` contains 40 synthetic observations for fictional astronaut ASTRA-01. These records demonstrate timestamped daily telemetry, personal baselines, and repeated-deviation review prompts. They are not NASA measurements.

## Challenge-resource context

The official challenge Navigator's November 13 response to the Health Monitoring Software challenge says there is no single mandatory downloadable dataset and recommends exploring NASA OSDR and the NASA Life Sciences Portal. It explicitly warns that some astronaut-health data are biological samples or processed research results rather than real-time measurements.

The GO Team's general resources guidance separately says Global Awards eligibility requires at least one NASA data source included in the selected challenge's Resources tab. In the final project submission, list the exact Resources entry and the OSDR study separately, and confirm that the entry-to-dataset relationship is accurate. Do not represent OSD-569 as a live feed or claim it was the exact linked source unless verified.

Challenge Navigator discussion: https://github.com/nasa/spaceapps/discussions/2025  
GO Team resource requirement: https://github.com/nasa/spaceapps/discussions/1827

## Challenge-resource lineage

The Health Monitoring Software challenge Resources supplied for this project include NASA's **Ongoing HRP Research in Space** page:
https://www.nasa.gov/hrp/ongoing-hrp-research/

That NASA HRP page lists the **Omics Archive** as a past human investigation. NASA's Omics Archive reference describes collection of astronaut blood, urine, saliva, feces, and cells to study molecular changes during spaceflight:
https://www.nasa.gov/reference/omics-archive/

NASA's OSDR SpaceX Inspiration4 mission page lists OSD-569 among the mission's studies:
https://osdr.nasa.gov/bio/repo/data/missions/SpaceX%20Inspiration4

The challenge Navigator's November 13 answer to the Health Monitoring Software challenge also names NASA OSDR as a useful starting point for astronaut-health research data:
https://github.com/nasa/spaceapps/discussions/2025

This creates the documented source path used by ASTRA: the challenge's HRP research context -> NASA Omics Archive research context -> NASA OSDR's Inspiration4 mission collection -> OSD-569 CBC source file. In the submission, list the actual challenge Resources entry (“Ongoing HRP Research in Space”) and the specific OSDR dataset/file as distinct references. Do not claim the Resources page links directly to the OSD-569 file unless that direct link is visible in the live challenge submission interface.

The GO Team's general guidance says Global Awards eligibility requires at least one NASA data source included with the selected challenge's Resources:
https://github.com/nasa/spaceapps/discussions/1827

## Other references

- NASA OSDR FAQ: https://science.nasa.gov/reference/osdr-faq/
- NASA OSDR Terms and Conditions: https://science.nasa.gov/reference/osdr-help-terms-and-conditions/
- NASA HRP — Ongoing HRP Research in Space: https://www.nasa.gov/hrp/ongoing-hrp-research/
- NASA Standard Measures: https://www.nasa.gov/reference/standard-measures/
