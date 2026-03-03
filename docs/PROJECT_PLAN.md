# DataGuard Project Plan

## Overview
This project implements a production-oriented data quality and observability platform for monitoring pipelines, schema drift, dataset freshness, health scoring, incidents, and dashboard visibility.

## Phase 1 — Repository audit and planning
- Task ID: P1.1
- Description: Inspect repository, assess existing functionality, document architecture and plan.
- Priority: Critical
- Dependencies: None
- Implementation requirements: Audit repository state, create planning docs, define scope, confirm missing components.
- Acceptance criteria: Plan and status docs created; repository baseline captured.
- Testing requirements: No test required beyond repository check.
- Current status: IMPLEMENTED

## Phase 2 — Infrastructure and database
- Task ID: P2.1
- Description: Configure Docker Compose and PostgreSQL initialization.
- Priority: Critical
- Dependencies: P1.1
- Implementation requirements: Docker Compose, PostgreSQL, schema creation, connection helpers.
- Acceptance criteria: Database starts and schema initializes reliably.
- Testing requirements: Initialization test and smoke queries.
- Current status: IN_PROGRESS

## Phase 3 — Dataset preparation and ingestion
- Task ID: P3.1
- Description: Prepare demo datasets and implement idempotent ingestion.
- Priority: Critical
- Dependencies: P2.1
- Implementation requirements: Batch discovery, raw table loading, duplicate protection, traceability.
- Acceptance criteria: Batches load correctly without duplicates and with traceability.
- Testing requirements: Ingestion unit/integration tests.
- Current status: NOT_STARTED

## Phase 4 — Configuration and validation engine
- Task ID: P4.1
- Description: Implement YAML configuration validation and data quality rules.
- Priority: Critical
- Dependencies: P3.1
- Implementation requirements: Rule registry, schema check logic, rule execution engine, persisted results.
- Acceptance criteria: All mandatory rule types execute and results are stored.
- Testing requirements: Rule and schema tests.
- Current status: NOT_STARTED

## Phase 5 — Anomaly detection and freshness
- Task ID: P5.1
- Description: Implement statistical anomaly detection and freshness monitoring.
- Priority: High
- Dependencies: P4.1
- Implementation requirements: Historical metrics, z-score and IQR detection, freshness checks.
- Acceptance criteria: Anomalies and freshness results are generated only with sufficient history and persisted.
- Testing requirements: Unit tests for edge cases.
- Current status: NOT_STARTED

## Phase 6 — Scoring, incidents, and alerts
- Task ID: P6.1
- Description: Implement health scoring, incident lifecycle, and alert integrations.
- Priority: High
- Dependencies: P5.1
- Implementation requirements: scoring model, deduped incident creation, alert sending with safe handling.
- Acceptance criteria: Incidents open and recover correctly; alerts respect deduplication rules.
- Testing requirements: Incident lifecycle tests and alert unit tests.
- Current status: NOT_STARTED

## Phase 7 — Airflow orchestration
- Task ID: P7.1
- Description: Implement Airflow DAG and orchestration workflow.
- Priority: High
- Dependencies: P3.1, P4.1, P5.1
- Implementation requirements: hourly DAG, retries, parent ordering, idempotent ingestion, health summary tasks.
- Acceptance criteria: DAG imports and task dependencies work for repeated runs.
- Testing requirements: DAG importability and dependency tests.
- Current status: NOT_STARTED

## Phase 8 — Premium dashboard
- Task ID: P8.1
- Description: Build Streamlit dashboard, design system, and views.
- Priority: High
- Dependencies: P6.1
- Implementation requirements: reusable styling, dataset health views, charts, incidents, schema history, lineage stub.
- Acceptance criteria: Dashboard renders real backend data and basic interactivity works.
- Testing requirements: Dashboard rendering and filter tests.
- Current status: NOT_STARTED

## Phase 9 — Fault injection and end-to-end testing
- Task ID: P9.1
- Description: Add fault injection workflows and verify detection.
- Priority: High
- Dependencies: P8.1
- Implementation requirements: synthetic fault generation and end-to-end evaluation.
- Acceptance criteria: Each required fault is reproducibly introduced and detected.
- Testing requirements: Through pipeline validation and detection report.
- Current status: NOT_STARTED

## Phase 10 — Final audit and delivery
- Task ID: P10.1
- Description: Full validation, documentation, Git audit, and final reporting.
- Priority: Critical
- Dependencies: All prior tasks
- Implementation requirements: Run full suite, review docs, check repo cleanliness, summarize final status.
- Acceptance criteria: Project is either verified or blockers are documented honestly.
- Testing requirements: Final end-to-end verification.
- Current status: NOT_STARTED
