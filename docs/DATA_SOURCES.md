# Data-Source Register

## Provenance rules

- Every reading identifies synthetic or real provenance.
- Synthetic values are never labeled as NASA data.
- Real readings require a traceable source reference.
- Baselines are separated by source type, source, and source reference.
- A scientific reference is not automatically a usable dataset.

## Current implementation

data/synthetic/demo_telemetry.csv contains 40 synthetic observations for fictional astronaut ASTRA-01. No real NASA or partner-agency dataset is ingested by the current code.

## Challenge-resource candidates

| Resource | Origin | Treatment |
| --- | --- | --- |
| 5 Hazards of Human Spaceflight | NASA | Background context |
| Risks of Human Spaceflight | NASA HRP | Research context |
| Ongoing HRP Research in Space | NASA HRP | Research context; inspect for actual data |
| Monitoring Radiation for Astronaut Health | Canadian Space Agency | Partner resource |
| Why Do We Conduct Science Experiments in Space? | NASA | Educational context |

These titles must be rechecked against the exact live challenge Resources list before claiming that any item is a qualifying dataset.

## NASA measurement reference

NASA Standard Measures: https://www.nasa.gov/reference/standard-measures/

It informed candidate demo metrics but is not treated as live telemetry and has not been counted toward the qualifying data-source requirement.

## Next

Select a qualifying NASA data source, document URL/license/access, inspect schema/units, then add a source-specific adapter while keeping synthetic and real records separate.
