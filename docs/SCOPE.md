# Scope

ASTRA explores how astronaut health-indicator observations could be compared with an individual's own baseline and communicated with an understandable explanation.

## Implemented

- synthetic telemetry for a fictional astronaut;
- CSV validation;
- valid/missing/invalid/outlier quality handling;
- personal baseline calculation;
- explainable deviation comparison;
- repeated-deviation alerts; and
- CLI/JSON reporting.

The demo contains sleep duration, activity, light exposure, and cognitive performance. These are configurable metric names, not a closed list.

## Boundaries

ASTRA does not provide medical diagnosis, treatment recommendations, mission/flight readiness, validated clinical thresholds, direct NASA-system connections, or claims that synthetic readings are NASA data.

Synthetic and real records are explicitly labeled and never combined into one baseline. Real records require a traceable source reference.

## Deferred

Dashboard, API, persistent storage, live data integration, qualifying NASA-resource integration, deployment, and final submission assets.
