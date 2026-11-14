# ASTRA — Interactive Demo Walkthrough

**Format:** one continuous screen recording, 60–75 seconds, 16:9. Record the deployed public dashboard after the release workflow succeeds. Narration should be in English for the project submission, with captions if needed.

| Time | Screen action | Narration |
|---|---|---|
| 0–7 s | Show ASTRA header and operational workspace. Point out the demonstration status and local processing note. | “ASTRA is an explainable astronaut health-monitoring software concept. It processes observations in the browser and keeps each data source traceable.” |
| 7–18 s | Load the bundled demonstration data. Show the observation count, tracked indicators, sleep trend, personal baseline and repeated-deviation review queue. | “The workspace validates daily observations, establishes a personal reference from a configured calibration period, and identifies sustained deviations for human review.” |
| 18–32 s | Add a new observation manually or import a prepared CSV. Press Run Analysis and show the updated log and queue. | “Operators can enter a reading or import a structured CSV, adjust the analysis window and demonstration settings, and rerun the analysis without sending the readings to a server.” |
| 32–40 s | Show a single deviation versus a repeated alert, then export JSON or CSV. | “An isolated change is not treated as a repeated alert. Each result includes its baseline context, explanation, and suggested verification step.” |
| 40–58 s | Scroll to NASA OSDR. Select C001 / White blood cell count, then C003 / Absolute neutrophils; show L-92 flagged suspect. | “A separate research panel presents historical NASA Inspiration4 CBC samples. The system preserves the suspect C003 L-92 source values and makes the data-quality warning visible.” |
| 58–70 s | Hold on the OSDR citation and the system limitations. | “Historical research is not presented as live telemetry, and the statistical demonstration is not a clinical diagnosis or a validated flight-medicine rule.” |

## Recording checklist
- Wait for the latest GitHub Pages deployment to complete successfully.
- Open the public dashboard in a private/incognito browser window and confirm that both the operational workspace and the NASA research panel load.
- Demonstrate at least one real interaction: manual entry or CSV import followed by **Run analysis**.
- Include a repeated-deviation example and show the difference between a single deviation and an alert.
- Show the export action and the separate NASA research view.
- Select C003 / Absolute neutrophils and show the suspect L-92 quality flag.
- Keep the DEMONSTRATION MODE and REAL NASA RESEARCH DATA labels visible in the relevant shots.
- Include the NASA OSDR citation and acknowledgement.
- Do not describe the CBC data as in-flight measurements.
- Do not imply a medical diagnosis, approved medical-device status, NASA endorsement, live sensor integration, or validated mission alert threshold.
- Confirm the exact video/slide limit in the live 2026 Project Submission Guide and follow it.
