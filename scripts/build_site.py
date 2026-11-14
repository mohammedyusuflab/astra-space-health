"""Build a self-contained static ASTRA website for GitHub Pages."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DEMO_CSV = ROOT / "data" / "synthetic" / "demo_telemetry.csv"
NASA_CSV = (
    ROOT / "data" / "nasa" / "osd569"
    / "LSDS-7_Complete_Blood_Count_CBC.upload_SUBMITTED.csv"
)
DEFAULT_OUTPUT = ROOT / "build" / "site"


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _landing_page() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="ASTRA is an explainable astronaut health-monitoring prototype with separate synthetic telemetry and NASA historical research views.">
  <meta name="theme-color" content="#08111f">
  <title>ASTRA | Astronaut Health Monitoring Prototype</title>
  <style>
    :root{color-scheme:dark;--bg:#08111f;--panel:#101d30;--line:#24364e;--muted:#a2b3c8;--text:#edf4fc;--cyan:#65d4d0;--amber:#f1bd68}
    *{box-sizing:border-box}
    body{margin:0;background:radial-gradient(ellipse at 15% 0%,#152c43 0,transparent 42%),var(--bg);color:var(--text);font:16px/1.6 Inter,system-ui,sans-serif}
    main{max-width:1000px;margin:auto;padding:56px 24px 44px}
    .brand{letter-spacing:.22em;font-size:12px;color:var(--cyan);font-weight:700}
    h1{font-size:clamp(40px,7vw,68px);line-height:1.05;letter-spacing:-.04em;margin:18px 0}
    .lead{max-width:760px;color:var(--muted);font-size:19px}
    .actions{display:flex;gap:14px;flex-wrap:wrap;margin:30px 0 42px}
    a.primary,a.secondary{display:inline-block;padding:12px 18px;border-radius:5px;text-decoration:none;font-weight:650}
    a.primary{background:var(--cyan);color:#06131c}
    a.secondary{border:1px solid var(--line);color:var(--text)}
    .grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
    .panel{background:linear-gradient(145deg,#13243a,#0e1a2b);border:1px solid var(--line);border-radius:9px;padding:22px}
    .eyebrow{color:var(--cyan);font-size:11px;font-weight:700;letter-spacing:.15em}
    h2{font-size:19px;margin:8px 0}
    p{color:var(--muted);margin:8px 0}
    .notice{margin-top:18px;border-left:3px solid var(--amber);padding:12px 15px;background:#211f1a;color:#e7d8bd;font-size:13px}
    footer{border-top:1px solid var(--line);margin-top:36px;padding-top:18px;color:var(--muted);font-size:12px}
    @media(max-width:680px){main{padding:36px 17px}.grid{grid-template-columns:1fr}.lead{font-size:17px}}
  </style>
</head>
<body>
  <main>
    <div class="brand">ASTRA / FLIGHT HEALTH SYSTEMS</div>
    <h1>Context before alarms.</h1>
    <p class="lead">An explainable astronaut health-monitoring prototype that demonstrates personal baselines, sustained-deviation review prompts, and a separately cited view of historical NASA astronaut research data.</p>
    <div class="actions">
      <a class="primary" href="./dashboard/">Open ASTRA dashboard</a>
      <a class="secondary" href="https://github.com/mohammedyusuflab/astra-space-health" target="_blank" rel="noopener">Source code on GitHub</a>
    </div>
    <section class="grid" aria-label="Data paths">
      <article class="panel">
        <div class="eyebrow">OPERATIONAL DEMONSTRATION</div>
        <h2>Personal health trends</h2>
        <p>Fictional daily telemetry is validated and compared with a personal baseline. Repeated deviations are surfaced with explanations for human review.</p>
      </article>
      <article class="panel">
        <div class="eyebrow">NASA OSDR · OSD-569</div>
        <h2>Historical astronaut research</h2>
        <p>Inspiration4 blood-count measurements are presented as retrospective research, with relative sample dates and visible data-quality context. They are not in-flight telemetry.</p>
      </article>
    </section>
    <div class="notice">ASTRA is an educational prototype, not a medical device or NASA product. It does not diagnose, prescribe treatment, determine mission readiness, or connect to live spacecraft sensors.</div>
    <footer>NASA OSDR acknowledgement: “Data are courtesy of the NASA Open Science Data Repository.” Dataset: OSD-569 · DOI 10.26030/e0rx-sh52.</footer>
  </main>
</body>
</html>
"""


def build_site(destination: Path) -> Path:
    """Generate the synthetic report and stage every file the browser needs."""
    target = destination.expanduser().resolve()
    if target == ROOT or _is_relative_to(ROOT, target):
        raise ValueError("The output directory must not overwrite the repository.")
    if _is_relative_to(target, ROOT) and not _is_relative_to(target, ROOT / "build"):
        raise ValueError("Repository-local site output must stay inside build/.")

    if target.exists():
        shutil.rmtree(target)

    dashboard_dir = target / "dashboard"
    output_dir = target / "output"
    nasa_dir = target / "data" / "nasa"
    dashboard_dir.mkdir(parents=True)
    output_dir.mkdir(parents=True)
    nasa_dir.mkdir(parents=True)

    dashboard_source = ROOT / "dashboard" / "index.html"
    dashboard_app_source = ROOT / "dashboard" / "app.js"
    dashboard_sw_source = ROOT / "dashboard" / "sw.js"
    if not dashboard_source.is_file():
        raise FileNotFoundError(f"Dashboard file not found: {dashboard_source}")
    if not dashboard_app_source.is_file():
        raise FileNotFoundError(f"Dashboard application script not found: {dashboard_app_source}")
    if not dashboard_sw_source.is_file():
        raise FileNotFoundError(f"Dashboard service worker not found: {dashboard_sw_source}")
    if not DEMO_CSV.is_file() or not NASA_CSV.is_file():
        raise FileNotFoundError("A required demo or NASA OSDR source CSV is missing.")

    dashboard_html = dashboard_source.read_text(encoding="utf-8")
    required_controls = (
        'id="load-demo"',
        'id="csv-file"',
        'id="manual-form"',
        'id="run-analysis"',
        'id="download-json"',
        'id="download-csv"',
        'id="nasa-research"',
        'src="./app.js"',
        "register('./sw.js')",
    )
    missing_controls = [item for item in required_controls if item not in dashboard_html]
    if missing_controls:
        raise RuntimeError(f"Dashboard is missing required interactive elements: {missing_controls}")
    if dashboard_html.count('id="rows"') != 1:
        raise RuntimeError("Dashboard must contain exactly one operational observation table.")

    if shutil.which("node"):
        subprocess.run(
            ["node", "--check", str(dashboard_app_source)],
            cwd=ROOT,
            check=True,
        )
        subprocess.run(
            ["node", "--check", str(dashboard_sw_source)],
            cwd=ROOT,
            check=True,
        )

    shutil.copy2(dashboard_source, dashboard_dir / "index.html")
    shutil.copy2(dashboard_app_source, dashboard_dir / "app.js")
    shutil.copy2(dashboard_sw_source, dashboard_dir / "sw.js")

    report_path = output_dir / "demo-report.json"
    nasa_json_path = nasa_dir / "osd569-cbc.json"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")

    command = [
        sys.executable, "-m", "astra",
        "--input", str(DEMO_CSV),
        "--baseline-start", "2026-11-01T00:00:00Z",
        "--baseline-end", "2026-11-07T23:59:00Z",
        "--json", str(report_path),
        "--nasa-cbc", str(NASA_CSV),
        "--nasa-cbc-json", str(nasa_json_path),
    ]
    subprocess.run(command, cwd=ROOT, env=env, check=True)

    report = json.loads(report_path.read_text(encoding="utf-8"))
    nasa = json.loads(nasa_json_path.read_text(encoding="utf-8"))

    if len(report.get("results", [])) != 60:
        raise RuntimeError("Expected 60 synthetic observations in the deployment report.")
    if len(report.get("baselines", [])) != 6:
        raise RuntimeError("Expected six provenance-separated synthetic baselines.")
    alert_count = sum(1 for item in report["results"] if item.get("alert"))
    if alert_count != 2:
        raise RuntimeError("Expected two repeated-deviation demonstration alerts.")
    summary = nasa.get("summary", {})
    expected = {
        "record_count": 553,
        "sample_count": 28,
        "subject_count": 4,
        "analyte_count": 20,
        "suspect_sample_count": 1,
    }
    mismatches = {
        key: (summary.get(key), value)
        for key, value in expected.items()
        if summary.get(key) != value
    }
    if mismatches:
        raise RuntimeError(f"NASA OSD-569 dataset summary mismatch: {mismatches}")

    (target / "index.html").write_text(_landing_page(), encoding="utf-8")
    (target / ".nojekyll").touch()

    print(f"Static ASTRA site built: {target}")
    print(f"Synthetic observations: {len(report['results'])}")
    print(f"Synthetic baselines: {len(report['baselines'])}")
    print(f"Synthetic review alerts: {alert_count}")
    print(
        "NASA OSDR OSD-569: "
        f"{summary['record_count']} measurements / "
        f"{summary['sample_count']} samples / "
        f"{summary['subject_count']} subjects / "
        f"{summary['analyte_count']} analytes / "
        f"{summary['suspect_sample_count']} suspect sample"
    )
    print("Browser assets verified: dashboard/index.html + dashboard/app.js + dashboard/sw.js")
    print("Browser data paths verified: dashboard -> ../output and ../data/nasa")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a self-contained static ASTRA website."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output directory (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()
    build_site(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
