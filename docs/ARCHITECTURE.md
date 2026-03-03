# DataGuard Architecture

## Overview
DataGuard is a Python-based data quality and observability platform with a PostgreSQL metadata store, Airflow job orchestration, and a Streamlit dashboard.

## High-level components
- Ingestion layer: discovers intake files, assigns batch IDs, persists raw data, prevents duplicate loads.
- Validation engine: executes schema and data quality checks using YAML-defined rules.
- Metrics and anomaly service: stores timeseries metrics for row counts, null percentages, and numeric drift.
- Health and incident service: computes dataset health, creates and resolves incidents, and deduplicates repeated failures.
- Alerting integration: sends Slack and email notifications for new incidents.
- Orchestration: Airflow DAG runs scheduled ingestion and validation tasks.
- Dashboard: Streamlit UI renders health, incidents, checks, and trends using live database data.

## Data flow
1. Files are placed in the working dataset directory.
2. Ingestion discovers new batches and loads them into raw schema tables.
3. Schema validation compares the loaded dataset to a baseline snapshot.
4. Rule validation executes each YAML-defined rule and stores results.
5. Metrics and freshness checks update historical observations.
6. Health scoring aggregates results into dataset health.
7. Incidents are opened and resolved; alerts are delivered for new incidents.
8. The dashboard queries the meta schema for aggregated views and drill-down data.

## Database model
- raw: raw ingested source tables with dataset-specific batch partitions.
- meta: platform metadata, check results, incidents, and historical metrics.

## Design principles
- Explicit configuration over hidden assumptions.
- Idempotent ingestion and batch-level traceability.
- Metric-driven health scoring with safe handling for missing history.
- Modular rule registry for extensibility.
- Secure configuration using environment variables.
