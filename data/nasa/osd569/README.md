# NASA OSDR OSD-569 — Inspiration4 Complete Blood Count

This folder contains the public OSDR submitted CSV used by ASTRA's **historical research-data view**.

- Study page: https://osdr.nasa.gov/bio/repo/data/studies/OSD-569
- Direct OSDR download: https://osdr.nasa.gov/geode-py/ws/studies/OSD-569/download?source=datamanager&file=LSDS-7_Complete_Blood_Count_CBC.upload_SUBMITTED.csv
- DOI: 10.26030/e0rx-sh52
- Source file: LSDS-7_Complete_Blood_Count_CBC.upload_SUBMITTED.csv
- SHA-256: 10a878b009eb2ea11a13fe92ad698098858639e8ed02f5ee849431313b9457d3
- Checked for this project: 2026-11-14
- Shape: 553 observation rows, 28 blood-draw samples, 4 de-identified crew identifiers, 20 reported analytes.

The dataset is NASA OSDR whole-blood research from the 2021 Inspiration4 mission. The CSV is the submitted CBC clinical-assay table, not raw genome sequence data.

## Time and interpretation boundaries

- Sample labels are relative to launch/return: L-92, L-44, L-3 (before launch), and R+1, R+45, R+82, R+194 (after return).
- There are **no in-flight CBC samples** in this file.
- These are retrospective research measurements from four de-identified crew members. They are not live spacecraft telemetry, the current astronaut's data, or the demo user's medical records.
- Lab reference intervals are source-provided Earth-laboratory context only. They are not personal baselines, mission limits, alert thresholds, or diagnoses.
- Missing analytes remain missing; ASTRA does not impute values.
- The adapter flags an internal inconsistency at C003 / L-92 because absolute differential counts do not reconcile with the reported percentages and white blood cell count. Original source values are preserved and marked suspect; they are not silently corrected.

## Re-fetch and verify

From the repository root:

```bash
python scripts/fetch_nasa_osd569.py
```

The script downloads directly from NASA OSDR and refuses to overwrite the local data unless the SHA-256 matches the checked source file.

NASA OSDR citation and acknowledgement must be retained. This project does not assign a new license to the dataset. The repository's software license does not replace the dataset's source terms.

Acknowledgement: **Data are courtesy of the NASA Open Science Data Repository.**
