"""NASA OSDR OSD-569 Inspiration4 CBC research-data adapter.

Historical lab samples are deliberately kept outside ASTRA's synthetic
telemetry baseline and alert pipeline. OSD-569 has pre-flight and post-return
samples only; it is not an in-flight telemetry feed.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

DATASET_ID = "OSD-569"
DATASET_TITLE = "Whole Blood Measurements from the SpaceX Inspiration4 Mission (CBC and other assays)"
DATASET_URL = "https://osdr.nasa.gov/bio/repo/data/studies/OSD-569"
DOWNLOAD_URL = (
    "https://osdr.nasa.gov/geode-py/ws/studies/OSD-569/download"
    "?source=datamanager&file=LSDS-7_Complete_Blood_Count_CBC.upload_SUBMITTED.csv"
)
DATASET_DOI = "10.26030/e0rx-sh52"
DEFAULT_CSV = (
    Path(__file__).resolve().parents[2]
    / "data" / "nasa" / "osd569"
    / "LSDS-7_Complete_Blood_Count_CBC.upload_SUBMITTED.csv"
)
DEFAULT_OUTPUT = (
    Path(__file__).resolve().parents[2]
    / "data" / "nasa" / "osd569-cbc.json"
)

_REQUIRED = {
    "ANALYTE", "VALUE", "RANGE_MIN", "RANGE_MAX", "UNITS",
    "TEST_TYPE", "SUBJECT_ID", "SEX", "TEST_DATE",
}
_TIMEPOINT = re.compile(r"^([LR])([+-])(\d+)$")
_ANALYTE_SUFFIX = re.compile(r"\s*\(FEMALE\)$", re.IGNORECASE)
_COUNT_PAIRS = (
    ("NEUTROPHILS", "ABSOLUTE NEUTROPHILS"),
    ("LYMPHOCYTES", "ABSOLUTE LYMPHOCYTES"),
    ("MONOCYTES", "ABSOLUTE MONOCYTES"),
    ("EOSINOPHILS", "ABSOLUTE EOSINOPHILS"),
    ("BASOPHILS", "ABSOLUTE BASOPHILS"),
)
# Data-integrity check only; not a clinical threshold.
_COUNT_RECONCILIATION_TOLERANCE_THOUSAND_PER_UL = 0.05
_TIMEPOINT_ORDER = {
    "L-92": 0, "L-44": 1, "L-3": 2,
    "R+1": 3, "R+45": 4, "R+82": 5, "R+194": 6,
}
_DISPLAY = {
    "WHITE BLOOD CELL COUNT": "White blood cell count",
    "RED BLOOD CELL COUNT": "Red blood cell count",
    "PLATELET COUNT": "Platelet count",
    "ABSOLUTE NEUTROPHILS": "Absolute neutrophils",
    "ABSOLUTE LYMPHOCYTES": "Absolute lymphocytes",
    "ABSOLUTE MONOCYTES": "Absolute monocytes",
    "ABSOLUTE EOSINOPHILS": "Absolute eosinophils",
    "ABSOLUTE BASOPHILS": "Absolute basophils",
}


class OSDRDataError(ValueError):
    """Raised when the downloaded OSDR CBC file is malformed or inconsistent."""


def _number(raw: str, field: str, row_number: int) -> float:
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise OSDRDataError(f"row {row_number}: {field} is not numeric: {raw!r}") from exc
    if not math.isfinite(value):
        raise OSDRDataError(f"row {row_number}: {field} must be finite")
    return value


def _timepoint(raw: str) -> dict[str, Any]:
    match = _TIMEPOINT.fullmatch(raw.strip())
    if not match:
        raise OSDRDataError(f"unsupported OSD-569 sample timepoint: {raw!r}")
    prefix, sign, days_text = match.groups()
    if (prefix, sign) not in {("L", "-"), ("R", "+")}:
        raise OSDRDataError(f"unsupported OSD-569 sample timepoint: {raw!r}")
    days = int(days_text)
    if days <= 0:
        raise OSDRDataError(f"unsupported OSD-569 sample timepoint: {raw!r}")
    before = prefix == "L"
    return {
        "id": raw,
        "phase": "pre-flight" if before else "post-flight",
        "relative_day": -days if before else days,
        "relative_to": "launch" if before else "return",
        "label": f"{days} day{'s' if days != 1 else ''} {'before launch' if before else 'after return'}",
    }


def _analyte_id(name: str) -> str:
    cleaned = _ANALYTE_SUFFIX.sub("", name.strip())
    return re.sub(r"[^a-z0-9]+", "_", cleaned.lower()).strip("_")


def _flag_inconsistent_samples(
    samples: dict[tuple[str, str], dict[str, Any]]
) -> dict[tuple[str, str], str]:
    """Flag samples where absolute differential counts conflict with percentages."""
    flagged: dict[tuple[str, str], str] = {}
    for key, sample in samples.items():
        by_name = sample["by_analyte"]
        wbc = by_name.get("WHITE BLOOD CELL COUNT")
        if wbc is None:
            continue
        mismatches = []
        for percentage_name, absolute_name in _COUNT_PAIRS:
            percentage = by_name.get(percentage_name)
            absolute = by_name.get(absolute_name)
            if percentage is None or absolute is None:
                continue
            expected = wbc["value"] * 1000.0 * percentage["value"] / 100.0
            difference = abs(absolute["value"] - expected) / 1000.0
            if difference > _COUNT_RECONCILIATION_TOLERANCE_THOUSAND_PER_UL:
                mismatches.append(absolute_name)
        if mismatches:
            flagged[key] = (
                "Sample-level data-integrity warning: absolute differential values "
                "do not reconcile with the reported differential percentages and "
                "white blood cell count (" + ", ".join(mismatches) + "). "
                "Original NASA values are preserved and marked suspect."
            )
    return flagged


def build_osd569_dataset(csv_path: str | Path = DEFAULT_CSV) -> dict[str, Any]:
    """Parse the NASA OSD-569 CSV; keep sample dates as relative mission labels."""
    path = Path(csv_path)
    if not path.is_file():
        raise OSDRDataError(f"NASA OSD-569 CSV not found: {path}")

    samples: dict[tuple[str, str], dict[str, Any]] = {}
    subjects: dict[str, str] = {}
    records: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = sorted(_REQUIRED - set(reader.fieldnames or ()))
        if missing:
            raise OSDRDataError("CSV is missing required columns: " + ", ".join(missing))

        for row_number, row in enumerate(reader, start=2):
            subject = (row.get("SUBJECT_ID") or "").strip()
            sex = (row.get("SEX") or "").strip()
            analyte = _ANALYTE_SUFFIX.sub("", (row.get("ANALYTE") or "").strip())
            unit = (row.get("UNITS") or "").strip()
            timepoint_id = (row.get("TEST_DATE") or "").strip()
            if not subject or not sex or not analyte or not unit:
                raise OSDRDataError(
                    f"row {row_number}: subject, sex, analyte, and units are required"
                )
            if sex not in {"M", "F"}:
                raise OSDRDataError(f"row {row_number}: unsupported sex code {sex!r}")
            if subject in subjects and subjects[subject] != sex:
                raise OSDRDataError(f"subject {subject} has inconsistent sex metadata")

            subjects[subject] = sex
            timepoint = _timepoint(timepoint_id)
            value = _number(row.get("VALUE", ""), "VALUE", row_number)
            range_min = _number(row.get("RANGE_MIN", ""), "RANGE_MIN", row_number)
            range_max = _number(row.get("RANGE_MAX", ""), "RANGE_MAX", row_number)
            if range_min > range_max:
                raise OSDRDataError(f"row {row_number}: RANGE_MIN is greater than RANGE_MAX")

            sample_key = (subject, timepoint_id)
            sample = samples.setdefault(sample_key, {
                "subject_id": subject,
                "sex": sex,
                "timepoint": timepoint,
                "by_analyte": {},
            })
            if analyte in sample["by_analyte"]:
                raise OSDRDataError(
                    f"duplicate {analyte} value for {subject} at {timepoint_id}"
                )
            sample["by_analyte"][analyte] = {
                "value": value,
                "unit": unit,
                "range_min": range_min,
                "range_max": range_max,
            }
            records.append({
                "subject_id": subject,
                "sex": sex,
                "timepoint": timepoint_id,
                "phase": timepoint["phase"],
                "relative_day": timepoint["relative_day"],
                "relative_to": timepoint["relative_to"],
                "analyte_id": _analyte_id(analyte),
                "analyte_name": _DISPLAY.get(analyte, analyte.title()),
                "value": value,
                "unit": unit,
                "reference_range_min": range_min,
                "reference_range_max": range_max,
                "quality": "valid",
                "quality_note": "",
            })

    if not records:
        raise OSDRDataError("NASA OSD-569 CSV contains no measurements")

    flagged = _flag_inconsistent_samples(samples)
    for record in records:
        key = (record["subject_id"], record["timepoint"])
        if key in flagged:
            record["quality"] = "suspect"
            record["quality_note"] = flagged[key]

    timepoints = [
        _timepoint(timepoint_id)
        for timepoint_id in sorted(
            {sample["timepoint"]["id"] for sample in samples.values()},
            key=lambda item: _TIMEPOINT_ORDER.get(item, 999),
        )
    ]
    records.sort(key=lambda item: (
        item["subject_id"],
        _TIMEPOINT_ORDER.get(item["timepoint"], 999),
        item["analyte_id"],
    ))
    return {
        "schema_version": 1,
        "dataset": {
            "id": DATASET_ID,
            "title": DATASET_TITLE,
            "provider": "NASA Open Science Data Repository (OSDR)",
            "url": DATASET_URL,
            "download_url": DOWNLOAD_URL,
            "doi": DATASET_DOI,
            "citation": (
                "NASA Open Science Data Repository (OSDR), OSD-569, "
                "SpaceX Inspiration4 Whole Blood / Complete Blood Count data, "
                f"doi:{DATASET_DOI}. {DATASET_URL}"
            ),
            "source_file": path.name,
            "data_type": "historical laboratory research data",
            "access_note": (
                "Publicly downloadable OSDR content. Follow current OSDR terms "
                "and acknowledgement requirements. This adapter does not assert "
                "a study-specific Creative Commons license."
            ),
        },
        "summary": {
            "record_count": len(records),
            "sample_count": len(samples),
            "subject_count": len(subjects),
            "analyte_count": len({record["analyte_id"] for record in records}),
            "suspect_sample_count": len(flagged),
            "suspect_record_count": sum(
                record["quality"] == "suspect" for record in records
            ),
            "subjects": sorted(subjects),
            "timepoints": timepoints,
        },
        "limitations": [
            "Samples were taken before launch and after return; there are no in-flight samples.",
            "These are retrospective laboratory measurements from four de-identified Inspiration4 crew members, not current telemetry or the user's medical data.",
            "Laboratory reference intervals are displayed as source context only; they are not personalized baselines, mission limits, alerts, or diagnostic criteria.",
            "Missing analytes are not imputed. Original source values are preserved.",
            "A sample-level data-integrity check flags C003 at L-92. Its original values are preserved but should not be used for inference.",
            "The research dataset is kept separate from ASTRA's synthetic telemetry analysis and alert engine.",
        ],
        "quality_flags": [
            {
                "subject_id": subject,
                "timepoint": timepoint,
                "reason": reason,
            }
            for (subject, timepoint), reason in sorted(flagged.items())
        ],
        "records": records,
    }


def write_osd569_json(
    csv_path: str | Path = DEFAULT_CSV,
    output_path: str | Path = DEFAULT_OUTPUT,
) -> dict[str, Any]:
    """Build normalized JSON for the historical research dashboard."""
    document = build_osd569_dataset(csv_path)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return document


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the ASTRA NASA OSD-569 CBC research-data view."
    )
    parser.add_argument("--input", default=str(DEFAULT_CSV))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    document = write_osd569_json(args.input, args.output)
    summary = document["summary"]
    print(
        f"OSD-569: {summary['record_count']} research measurements, "
        f"{summary['sample_count']} samples, {summary['subject_count']} subjects, "
        f"{summary['suspect_sample_count']} suspect sample(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
