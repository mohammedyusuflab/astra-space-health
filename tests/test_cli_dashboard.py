from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).parents[1]
DEMO = ROOT / "data" / "synthetic" / "demo_telemetry.csv"


class CliSmokeTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        return subprocess.run(
            [sys.executable, "-m", "astra", *args],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_cli_generates_json_report_from_demo(self):
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory) / "nested" / "report.json"
            nasa_path = Path(directory) / "nested" / "nasa-osd569.json"
            result = self.run_cli(
                "--input", str(DEMO),
                "--baseline-start", "2026-11-01T00:00:00Z",
                "--baseline-end", "2026-11-07T23:59:00Z",
                "--json", str(report_path),
                "--nasa-cbc-json", str(nasa_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Readings analyzed: 40", result.stdout)
            self.assertIn("Baselines created: 4", result.stdout)
            self.assertIn("Alerts: 2", result.stdout)
            self.assertTrue(report_path.is_file())
            self.assertIn('"results"', report_path.read_text(encoding="utf-8"))
            self.assertTrue(nasa_path.is_file())
            nasa = json.loads(nasa_path.read_text(encoding="utf-8"))
            self.assertEqual(nasa["dataset"]["id"], "OSD-569")
            self.assertIn("NASA OSDR OSD-569: 553 research measurements", result.stdout)

    def test_cli_rejects_timezone_naive_baseline(self):
        result = self.run_cli(
            "--input", str(DEMO),
            "--baseline-start", "2026-11-01T00:00:00",
            "--baseline-end", "2026-11-07T23:59:00Z",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("timestamp must include a timezone", result.stderr)


class DashboardSmokeTests(unittest.TestCase):
    def test_dashboard_loads_generated_report_and_discloses_synthetic_data(self):
        html = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
        self.assertIn("../output/demo-report.json", html)
        self.assertIn("DEMONSTRATION MODE", html)
        self.assertIn("not NASA telemetry", html)
        self.assertIn("Observation log", html)
        self.assertIn("validPoints", html)
        self.assertIn("Δ vs pre-flight mean", html)
        self.assertIn("no in-flight CBC samples", html)


if __name__ == "__main__":
    unittest.main()
