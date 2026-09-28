# Scope

## Problem and learning goal

Changes in health indicators can be difficult to interpret without personal context. ASTRA Sandbox will explore, for educational purposes, how readings could be compared with a person's own baseline and how the reason for a change could be communicated clearly.

The intended demo audience is learners, reviewers, and project collaborators discussing the concept. It is not intended for clinical or operational use.

## Proposed scenario

A fictional person would have synthetic health readings. The proposed analysis would establish a personal baseline, compare later synthetic readings with that reference, and explain the changes behind each observation or alert.

This scenario is a proposal and has not been implemented.

## Task 01 scope

Task 01 includes only:

- project documentation;
- definition of boundaries; and
- a conceptual, proposed architecture.

The following work is deferred:

- generating synthetic data;
- implementing the analysis algorithm;
- building an API or user interface;
- connecting external data; and
- deployment.

Python is a preliminary direction for a future analysis engine. No framework, database, or cloud service is selected in this task.

## Claims and limitations

ASTRA Sandbox does not claim to provide:

- medical diagnosis;
- treatment recommendations;
- readiness for real-world, clinical, or mission use;
- NASA approval, ownership, or endorsement; or
- confirmed participation in Space Apps.

## Open decisions

Before implementation, the project owner must review and decide:

- the relevant official challenge and its participation requirements;
- suitable data and whether it may be used;
- which indicators and metrics belong in the demonstration;
- how a personal baseline should be calculated; and
- which rules, thresholds, and explanations should produce observations or alerts.
