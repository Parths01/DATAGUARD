# DataGuard

DataGuard is a Python-based data quality and observability platform for monitoring datasets, validating schema and row-level quality checks, and surfacing health trends through a Streamlit dashboard.

## Features
- Idempotent batch ingestion and traceability.
- YAML-driven dataset and rule configuration.
- Schema drift detection with baseline snapshots.
- Modular rule engine for not_null, unique, accepted_values, range, regex, row_count_between, and foreign_key checks.
- Statistical anomaly detection with z-score and IQR guardrails.
- Freshness monitoring with grace factor handling.
- Health scoring and incident lifecycle tracking.
- Alert formatting for Slack and email integrations.
- Airflow orchestration skeleton.
- Streamlit dashboard for health summaries and incident views.

## Tech stack
- Python 3.12
- Pandas, NumPy, PyYAML
- PostgreSQL
- Apache Airflow
- Streamlit and Plotly
- Docker Compose
- Pytest
- GitHub Actions

## Prerequisites
- Docker Desktop or Docker Engine
- Python 3.12
- Git

## Local setup
1. Create and activate the virtual environment.
2. Install dependencies:
   python -m pip install -r requirements.txt
3. Copy environment values:
   copy .env.example .env
4. Start PostgreSQL:
   docker compose up -d postgres

## Docker Compose
```bash
docker compose up -d
```

## Running the dashboard
```bash
streamlit run src/dataguard/dashboard.py
```

## Running tests
```bash
pytest -q
```

## Key configuration
- config/datasets.yml for dataset metadata
- config/rules.yml for validation rules
- .env for environment variables

## Troubleshooting
- If Docker is unavailable, the project defaults to SQLite-backed local execution for development and test scenarios.
- If the config file is malformed, the loader raises clear validation errors.

## Limitations
- Synthetic datasets are used for local development and test coverage rather than the Kaggle Olist dataset.
- Production alert integrations require valid credentials in environment variables.
- The project includes the required structure and functionality for the core DataGuard platform, but some optional enterprise embellishments remain as future work.
