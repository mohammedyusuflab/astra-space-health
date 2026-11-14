"""CSV input and JSON-friendly report serialization."""

from __future__ import annotations

import csv
from dataclasses import asdict
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from .models import AnalysisReport
from .validation import validate_records


def load_csv(path: str | Path):
    """Load and validate a CSV file. Returns a ValidationReport."""
    csv_path = Path(path)
    with csv_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV file has no header row")
        return validate_records(reader)


def report_to_dict(report: AnalysisReport) -> dict[str, Any]:
    def convert(value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        if hasattr(value, "value") and isinstance(value.value, str):
            return value.value
        if isinstance(value, tuple):
            return [convert(item) for item in value]
        if isinstance(value, list):
            return [convert(item) for item in value]
        if isinstance(value, dict):
            return {key: convert(item) for key, item in value.items()}
        if hasattr(value, "__dataclass_fields__"):
            return {key: convert(item) for key, item in asdict(value).items()}
        return value
    return convert(report)


def write_json_report(report: AnalysisReport, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report_to_dict(report), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
