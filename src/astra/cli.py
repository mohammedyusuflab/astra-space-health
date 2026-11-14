"""Command-line entry point for ASTRA."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .engine import run_analysis
from .io import write_json_report


def _timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise argparse.ArgumentTypeError("timestamp must include a timezone, e.g. 2026-11-01T00:00:00Z")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze astronaut health-indicator observations.")
    parser.add_argument("--input", required=True, help="Input telemetry CSV")
    parser.add_argument("--baseline-start", required=True, type=_timestamp)
    parser.add_argument("--baseline-end", required=True, type=_timestamp)
    parser.add_argument("--json", dest="json_path", help="Optional JSON report output path")
    parser.add_argument("--threshold", type=float, default=2.0, help="Demonstration deviation threshold in standard deviations")
    parser.add_argument("--repeat", type=int, default=2, help="Consecutive deviations required for an alert")
    args = parser.parse_args()

    if args.baseline_start > args.baseline_end:
        parser.error("--baseline-start must not be after --baseline-end")
    if args.repeat < 1:
        parser.error("--repeat must be at least 1")

    report = run_analysis(
        args.input,
        baseline_start=args.baseline_start,
        baseline_end=args.baseline_end,
        deviation_threshold=args.threshold,
        repeated_deviations_for_alert=args.repeat,
    )
    if args.json_path:
        write_json_report(report, args.json_path)

    print(f"Readings analyzed: {len(report.results)}")
    print(f"Baselines created: {len(report.baselines)}")
    print(f"Validation issues: {len(report.validation_issues)}")
    print(f"Alerts: {len(report.alerts)}")
    if args.json_path:
        print(f"JSON report: {Path(args.json_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
