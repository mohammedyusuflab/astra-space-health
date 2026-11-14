# ASTRA — Launch and Submission Checklist

## Current release state

The repository contains the application, data, tests, documentation, a static-site builder, and a manual GitHub Pages deployment workflow. The public website is **not live yet**. The repository currently has GitHub Pages disabled; one repository setting must be changed before the deployment workflow can publish.

## 1. Build verification

The CI workflow must pass all unit tests and the static-site build. The build creates:

- index.html: public project landing page.
- dashboard/index.html: interactive ASTRA browser dashboard.
- output/demo-report.json: generated synthetic telemetry report (40 observations, four personal baselines, two demonstration review alerts).
- data/nasa/osd569-cbc.json: normalized NASA OSDR OSD-569 research data (553 measurements, 28 samples, four de-identified subjects, 20 analytes, one suspect sample).

The dashboard loads these JSON files using relative paths. The synthetic operational demo and historical NASA research remain separate. The build validates the expected dataset summary and fails rather than silently publishing an incomplete or mismatched bundle.

To build locally from the repository root:

    python scripts/build_site.py

The generated website is written to build/site/. No third-party Python packages are required.

## 2. One-time GitHub Pages setup

1. Open the repository: https://github.com/mohammedyusuflab/astra-space-health
2. Open **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to **GitHub Actions**.
4. Save the setting.

This repository-level setting is required because GitHub Pages is not enabled yet. Do not create a personal access token or add repository secrets for the supplied deployment workflow.

## 3. Publish the public demo

1. Open the repository's **Actions** tab.
2. Select **Deploy ASTRA website**.
3. Select **Run workflow** and choose the main branch.
4. Wait for the workflow to complete successfully.
5. Open the deployment URL shown by the github-pages environment.

Expected project-site URL:

https://mohammedyusuflab.github.io/astra-space-health/

The expected dashboard URL is:

https://mohammedyusuflab.github.io/astra-space-health/dashboard/

These are target URLs until a successful Pages deployment is recorded. Do not paste them into the competition form as live demo links before checking them.

## 4. Anonymous browser acceptance test

Open the deployed site in an incognito/private browser window (logged out of GitHub) and verify:

- The root page loads and the **Open ASTRA dashboard** link works.
- The dashboard header shows **DEMONSTRATION MODE**.
- Synthetic metrics, trend chart, observation log, and review queue load without a report-not-found message.
- The NASA research panel loads all five summary counts and both selectors.
- C001 / White blood cell count shows the historical sample timeline.
- C003 / Absolute neutrophils visibly marks the suspect L-92 sample and explains the data-quality flag.
- NASA measurements do not enter the synthetic alert engine.
- No browser console/network error indicates missing JSON, JavaScript failure, or a broken path.
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

ASTRA is ready for a public-demo deployment once the Pages setting is enabled and the deployment/anonymous browser checks pass. It is not considered competition-submission complete until the team has submitted the project through the official Space Apps Project tab.
