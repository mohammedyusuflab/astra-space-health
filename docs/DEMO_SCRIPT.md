# ASTRA — 30-Second Demo Script

**Format:** one continuous screen recording with brief cuts; record the browser at 16:9. Narration should be in English for the project submission, with captions if needed.

| Time | Screen action | Narration |
|---|---|---|
| 0–4 s | Show ASTRA dashboard header and synthetic-data status. | “ASTRA helps astronauts inspect health-indicator changes with clear personal context and explanations.” |
| 4–10 s | Show synthetic indicators, sleep trend, personal baseline, and the repeated-deviation review queue. | “The operational demo validates daily readings, compares them with a personal baseline, and flags repeated deviations — not isolated changes.” |
| 10–17 s | Scroll to the NASA OSDR section. Select crew C001 and White blood cell count. | “A separate research view uses NASA’s real Inspiration4 OSDR blood-count data, with the original pre-flight and post-return sample timeline.” |
| 17–23 s | Select crew C003; choose Absolute neutrophils; show the L-92 amber suspect marker and data-quality explanation. | “ASTRA preserves source values and exposes a data-quality inconsistency instead of silently correcting it.” |
| 23–30 s | Hold on the disclosure/citation at the bottom of the NASA research panel. | “Historical research is never presented as live telemetry. ASTRA supports review; it does not diagnose or prescribe.” |

## Recording checklist
- Generate output/demo-report.json with the CLI before opening the dashboard.
- Serve the repository root with python -m http.server 8000 and open /dashboard/.
- Confirm both panels load before recording.
- Keep the DEMONSTRATION MODE badge and REAL NASA RESEARCH DATA label visible in the relevant shots.
- Include the OSDR citation and acknowledgement in the final frame.
- Do not describe the CBC data as in-flight measurements.
- Do not imply a clinical diagnosis, NASA endorsement, or validated flight-medicine alert threshold.
- Keep the recording within the challenge's current submission limit.
