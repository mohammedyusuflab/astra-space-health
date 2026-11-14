from __future__ import annotations

import csv
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from astra.analysis import analyze_readings
from astra.baseline import build_baselines
from astra.engine import run_analysis
from astra.io import write_json_report
from astra.models import ReadingQuality, ResultStatus
from astra.validation import validate_records


BASELINE_START = datetime(2026, 11, 1, tzinfo=timezone.utc)
BASELINE_END = datetime(2026, 11, 7, 23, 59, tzinfo=timezone.utc)


class ValidationTests(unittest.TestCase):
    def test_missing_value_is_not_normal(self):
        report = validate_records([{
            "timestamp": "2026-11-08T08:00:00Z",
            "astronaut_id": "ASTRA-01",
            "metric": "sleep_duration",
            "value": "",
            "unit": "hours",
            "source_type": "synthetic",
            "source": "test",
        }])
        self.assertEqual(report.readings[0].quality, ReadingQuality.MISSING)
        self.assertIsNone(report.readings[0].value)

    def test_naive_timestamp_is_rejected(self):
        report = validate_records([{
            "timestamp": "2026-11-08T08:00:00",
            "astronaut_id": "ASTRA-01",
            "metric": "m",
            "value": "1",
            "unit": "u",
            "source_type": "synthetic",
            "source": "test",
        }])
        self.assertFalse(report.readings)
        self.assertEqual(report.issues[0].code, "invalid_timestamp")

    def test_real_data_requires_traceable_reference(self):
        report = validate_records([{
            "timestamp": "2026-11-08T08:00:00Z",
            "astronaut_id": "ASTRA-01",
            "metric": "m",
            "value": "1",
            "unit": "u",
            "source_type": "real",
            "source": "test",
        }])
        self.assertFalse(report.readings)
        self.assertEqual(report.issues[0].code, "missing_source_reference")

    def test_non_finite_value_is_rejected(self):
        report = validate_records([{
            "timestamp": "2026-11-08T08:00:00Z",
            "astronaut_id": "ASTRA-01",
            "metric": "m",
            "value": "nan",
            "unit": "u",
            "source_type": "synthetic",
            "source": "test",
        }])
        self.assertFalse(report.readings)
        self.assertEqual(report.issues[0].code, "invalid_value")


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.demo = Path(__file__).parents[1] / "data" / "synthetic" / "demo_telemetry.csv"

    def test_demo_creates_six_baselines_and_sleep_alerts(self):
        report = run_analysis(self.demo, baseline_start=BASELINE_START, baseline_end=BASELINE_END)
        self.assertEqual(len(report.baselines), 6)
        self.assertEqual(len(report.validation_issues), 0)
        self.assertEqual(len(report.alerts), 2)
        self.assertTrue(all(a.reading.metric == "sleep_duration" for a in report.alerts))

    def test_one_deviation_does_not_alert(self):
        records = [
            {"timestamp": f"2026-11-0{d}T08:00:00Z", "astronaut_id": "A", "metric": "m",
             "value": value, "unit": "u", "source_type": "synthetic", "source": "test"}
            for d, value in ((1, "10"), (2, "10"), (3, "10"), (4, "15"))
        ]
        validation = validate_records(records)
        baseline = build_baselines(
            validation.readings,
            period_start=BASELINE_START,
            period_end=datetime(2026, 11, 3, 23, 59, tzinfo=timezone.utc),
        )
        result = analyze_readings(validation.readings, baseline)[-1]
        self.assertEqual(result.status, ResultStatus.DEVIATION)
        self.assertFalse(result.alert)

    def test_missing_observation_resets_consecutive_counter(self):
        records = [
            {"timestamp": f"2026-11-0{d}T08:00:00Z", "astronaut_id": "A", "metric": "m",
             "value": value, "unit": "u", "source_type": "synthetic", "source": "test"}
            for d, value in ((1, "10"), (2, "10"), (3, "10"), (4, ""), (5, "20"))
        ]
        validation = validate_records(records)
        baseline = build_baselines(
            validation.readings,
            period_start=BASELINE_START,
            period_end=datetime(2026, 11, 3, 23, 59, tzinfo=timezone.utc),
        )
        result = analyze_readings(validation.readings, baseline)[-1]
        self.assertEqual(result.consecutive_deviations, 1)
        self.assertFalse(result.alert)

    def test_sources_are_not_mixed(self):
        records = [
            {"timestamp": f"2026-11-0{d}T08:00:00Z", "astronaut_id": "A", "metric": "m",
             "value": str(value), "unit": "u", "source_type": "synthetic", "source": "A"}
            for d, value in ((1, 10), (2, 11), (3, 9))
        ] + [{
            "timestamp": "2026-11-04T08:00:00Z", "astronaut_id": "A", "metric": "m",
            "value": "25", "unit": "u", "source_type": "real", "source": "B",
            "source_reference": "https://example.org/dataset"
        }]
        validation = validate_records(records)
        baselines = build_baselines(
            validation.readings,
            period_start=BASELINE_START,
            period_end=datetime(2026, 11, 3, 23, 59, tzinfo=timezone.utc),
        )
        results = analyze_readings(validation.readings, baselines)
        real = next(r for r in results if r.reading.source_type == "real")
        self.assertEqual(real.status, ResultStatus.NO_BASELINE)

    def test_non_finite_threshold_is_rejected(self):
        with self.assertRaises(ValueError):
            analyze_readings([], [], deviation_threshold=float("nan"))
        with self.assertRaises(ValueError):
            analyze_readings([], [], deviation_threshold=float("inf"))

    def test_json_report_creates_parent_directory(self):
        report = run_analysis(self.demo, baseline_start=BASELINE_START, baseline_end=BASELINE_END)
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "nested" / "report.json"
            write_json_report(report, target)
            self.assertTrue(target.is_file())
            self.assertIn('"baselines"', target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
