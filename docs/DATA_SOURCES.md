# Data-Source Register

## Provenance rules

- Every reading identifies synthetic or real provenance.
- Synthetic values are never labeled as NASA data.
- Real readings require a traceable source reference.
- Baselines are separated by source type, source, and source reference.
- A scientific reference is not automatically a usable dataset.

## Current implementation

`data/synthetic/demo_telemetry.csv` contains 40 synthetic observations for fictional astronaut ASTRA-01. The dashboard and CLI use this data for the demonstration. No real NASA or partner-agency dataset is ingested by the current code.

## Challenge resources identified

| Resource | Origin | Treatment in ASTRA |
| --- | --- | --- |
| 5 Hazards of Human Spaceflight | NASA | Background context |
| Risks of Human Spaceflight | NASA HRP | Research context |
| Ongoing HRP Research in Space | NASA HRP | Research context; inspect for structured data |
| Monitoring Radiation for Astronaut Health | Canadian Space Agency | Partner research context |
| Why Do We Conduct Science Experiments in Space? | NASA | Educational context |

These titles must be checked against the live challenge Resources tab and linked source pages before claiming any one of them is a qualifying data source. The organizer guidance says Global Awards eligibility requires at least one NASA data source included in the selected challenge Resources. Do not substitute an unrelated NASA dataset without confirming eligibility.

## NASA measurement reference

NASA Standard Measures: https://www.nasa.gov/reference/standard-measures/

This describes measurement domains including activity/light exposure, sleep, and cognition. It informs candidate metrics but is not treated as live telemetry or as the qualifying challenge dataset.

## Integration decision

No dataset adapter is claimed as implemented. Before integration, confirm:
1. The resource is included in this challenge's official Resources tab.
2. The resource exposes actual structured observations, not only descriptive research text.
3. Units, timestamps, subject identifiers, access conditions, and license/terms are understood.
4. Any privacy restrictions are respected.

Until then, the dashboard explicitly labels the included data synthetic.
