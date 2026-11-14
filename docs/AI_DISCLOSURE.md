# AI and Tool Use Disclosure

## AI assistance
ChatGPT (OpenAI) was used as an AI-assisted development tool to help draft and revise Python code, tests, dashboard markup/JavaScript, technical documentation, source-data notes, and demo/submission text under the project owner's direction.

The project owner remains responsible for reviewing the implementation, the scientific interpretation, and the final submission.

## Runtime behavior
The ASTRA prototype does **not** call a generative AI model at runtime. The current analysis engine uses deterministic, explainable Python rules and standard-library statistics. It does not use machine learning to make health decisions.

## Software and services
- Python 3.10+ standard library
- GitHub repository and GitHub Actions for source control and continuous integration
- Browser-native HTML, CSS, and JavaScript for the dashboard
- NASA Open Science Data Repository (OSDR), OSD-569, as the external research-data source

## Data acknowledgement
“Data are courtesy of the NASA Open Science Data Repository.”

See DATA_SOURCES.md for dataset citations, file provenance, access notes, and interpretation limits.
