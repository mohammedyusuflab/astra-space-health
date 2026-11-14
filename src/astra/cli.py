"""Command-line entry point for ASTRA."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .engine import run_analysis
from .io import write_json_report
from .osdr import DEFAULT_CSV as DEFAULT_NASA_CBC, DEFAULT_OUTPUT as DEFAULT_NASA_JSON, write_osd569_json


def _timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise argparse.ArgumentTypeError(
            "timestamp must include a timezone, e.g. 2026-11-01T00:00:00Z"
        )
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze synthetic astronaut telemetry and build the NASA OSD-569 research view."
    )
    parser.add_argument("--input", required=True, help="Input synthetic telemetry CSV")
    parser.add_argument("--baseline-start", required=True, type=_timestamp)
    parser.add_argument("--baseline-end", required=True, type=_timestamp)
    parser.add_argument("--json", dest="json_path", help="Optional synthetic JSON report output path")
    parser.add_argument(
        "--nasa-cbc", default=str(DEFAULT_NASA_CBC),
        help="NASA OSD-569 CBC CSV used for the separate historical research view",
    )
    parser.add_argument(
        "--nasa-cbc-json", default=str(DEFAULT_NASA_JSON),
        help="Normalized NASA OSD-569 JSON output path",
    )
    parser.add_argument(
        "--threshold", type=float, default=2.0,
        help="Demonstration deviation threshold in standard deviations",
    )
    parser.add_argument(
        "--repeat", type=int, default=2,
        help="Consecutive deviations required for a synthetic telemetry alert",
    )
    args = parser.parse_args()

    if args.baseline_start > args.baseline_end:
        parser.error("--baseline-start must not be after --baseline-end")
    if args.repeat < 2:
        parser.error("--repeat must be at least 2")

    report = run_analysis(
        args.input,
        baseline_start=args.baseline_start,
        baseline_end=args.baseline_end,
        deviation_threshold=args.threshold,
        repeated_deviations_for_alert=args.repeat,
    )
    if args.json_path:
        write_json_report(report, args.json_path)

    nasa_document = write_osd569_json(args.nasa_cbc, args.nasa_cbc_json)
    nasa_summary = nasa_document["summary"]

    print(f"Readings analyzed: {len(report.results)}")
    print(f"Baselines created: {len(report.baselines)}")
    print(f"Validation issues: {len(report.validation_issues)}")
    print(f"Alerts: {len(report.alerts)}")
    if args.json_path:
        print(f"Synthetic JSON report: {Path(args.json_path)}")
    print(
        "NASA OSDR OSD-569: "
        f"{nasa_summary['record_count']} research measurements, "
        f"{nasa_summary['sample_count']} samples, "
        f"{nasa_summary['suspect_sample_count']} suspect sample(s)"
    )
    print(f"NASA research JSON: {Path(args.nasa_cbc_json)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
