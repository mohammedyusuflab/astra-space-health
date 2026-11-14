# ASTRA — Launch and Submission Checklist

## Current release state

The repository contains the analysis engine, interactive browser workspace, source data, automated tests, documentation, and GitHub Pages deployment workflow. GitHub Pages has been enabled and the landing page was previously confirmed to open. The latest interactive-dashboard release still requires a fresh deployment and browser acceptance check before it can be described as verified.

## 1. Build verification

The CI workflow must pass all unit tests and the static-site build. The build creates:

- index.html: public project landing page.
- dashboard/index.html and dashboard/app.js: interactive ASTRA browser workspace (manual entry, CSV import, browser-side analysis, review queue, filtering and exports).
- output/demo-report.json: generated synthetic telemetry report (60 observations, six personal baselines, two demonstration review alerts).
- data/nasa/osd569-cbc.json: normalized NASA OSDR OSD-569 research data (553 measurements, 28 samples, four de-identified subjects, 20 analytes, one suspect sample).

The dashboard loads these JSON files and its application script using relative paths. The synthetic/operational telemetry workflow and historical NASA research remain separate. The build validates required interactive controls, checks JavaScript syntax when Node.js is available, checks the expected dataset summary, and fails rather than silently publishing an incomplete bundle.

To build locally from the repository root:

    python scripts/build_site.py

The generated website is written to build/site/. No third-party Python packages are required.

## 2. GitHub Pages configuration

GitHub Pages has been configured with **Source = GitHub Actions**. The workflow deploys automatically after a push to `main`, and can also be started manually from the Actions tab. Do not create a personal access token or add repository secrets for the supplied workflow.

## 3. Publish the public demo

After the final commit, open the repository's **Actions** tab and verify the latest **Deploy ASTRA website** run completed successfully. Then open the deployment URL shown by the github-pages environment. A successful code commit alone is not proof that the latest website version has deployed.

Expected project-site URL:

https://mohammedyusuflab.github.io/astra-space-health/

The expected dashboard URL is:

https://mohammedyusuflab.github.io/astra-space-health/dashboard/

These are target URLs until a successful Pages deployment is recorded. Do not paste them into the competition form as live demo links before checking them.

## 4. Anonymous browser acceptance test

Open the deployed site in an incognito/private browser window (logged out of GitHub) and verify:

- The root page loads and the **Open ASTRA dashboard** link works.
- The dashboard header shows **DEMONSTRATION MODE** and the operational workspace is visible.
- Bundled demo data load as 60 observations across six indicators, with six personal baselines and two repeated-deviation demonstration alerts.
- Change the baseline dates/threshold/repeat count and press **Run analysis**; the metrics, chart, review queue and log update.
- Add one valid manual observation; it appears in the log and the analysis reruns.
- Import the downloaded CSV template after filling at least three valid calibration readings and subsequent readings; verify baseline and result states.
- Import a malformed CSV and verify row/field issues are reported rather than silently accepted.
- Export JSON and CSV and confirm both files contain the current result set.
- Clear the operational workspace and confirm the NASA historical panel remains available and separate.
- The observation log filters by search text and result state.
- Mark a repeated alert as reviewed, confirm the acknowledgement is shown, then reopen it; the analysis result must remain unchanged.
- The NASA research panel loads all five summary counts and both selectors.
- C001 / White blood cell count shows the historical sample timeline.
- C003 / Absolute neutrophils visibly marks the suspect L-92 sample and explains the data-quality flag.
- NASA measurements do not enter the synthetic alert engine.
- No browser console/network error indicates missing JSON/JavaScript, runtime failure, or a broken path.
- The page is readable on a narrow mobile viewport as well as desktop.

If any item fails, do not submit the website as a working demo link. Fix and redeploy first.

## 5. Competition submission

Use the team's Project tab on the official NASA Space Apps site. Confirm the team, selected challenge, required participant details, and exact form fields before finalizing.

Submission content is drafted in:

- docs/SUBMISSION_DRAFT.md
- docs/CHALLENGE_BRIEF.md
- docs/DATA_SOURCES.md
- docs/AI_DISCLOSURE.md

Keep the challenge resource **Ongoing HRP Research in Space** and the dataset **NASA OSDR OSD-569** as distinct references. Verify the exact Resources entry shown on the team's challenge page. Do not claim that the challenge resource directly links to the OSD-569 file unless the live page proves that relationship.

Add the verified public website URL, public repository URL, and demo video/slides URL to the form. Disclose ChatGPT as an AI-assisted development tool as described in docs/AI_DISCLOSURE.md. Recheck all external links while logged out.

The prepared walkthrough is in docs/DEMO_SCRIPT.md. The submission guide and the team's live Project form are authoritative for media limits, required fields, and declarations; follow their current instructions rather than relying on an older template.

The official 2026 event page states that project submission opened on November 14, 2026 at 9:00 a.m. local time and closes on November 15, 2026 at 11:59 p.m. local time. Confirm the applicable local time shown for the team's registered event/team lead. Save the project and explicitly complete the final **Submit** action before the deadline.

## 6. Final release decision

ASTRA is ready to be treated as a working public demo only after the latest Pages workflow succeeds and every anonymous-browser acceptance check above passes. It is not a clinically validated medical device or certified flight-health system. It is not considered competition-submission complete until the team has submitted the project through the official Space Apps Project tab.
