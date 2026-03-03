# Testing Strategy

## Goals
- Verify core functionality before claiming feature completion.
- Maintain unit coverage for validation rules and anomaly logic.
- Validate database initialization and ingestion behavior in isolated test data.
- Ensure dashboard pages render and functional filters work.
- Run CI checks in GitHub Actions for core validation.

## Testing layers
1. Unit tests for YAML validation, rules, anomaly calculations, health scoring, incident deduplication.
2. Integration tests for PostgreSQL schema and ingestion workflow.
3. Airflow DAG import and dependency checks.
4. Dashboard tests for rendering and filters.
5. Full end-to-end workflow with synthetic fault injection.

## Required validation areas
- Rule engine behavior for all required rule types.
- Schema drift detection and baseline updates.
- Statistical detection edge cases.
- Freshness thresholds and grace factors.
- Incident lifecycle and duplicate prevention.
- Alert delivery safety.
- Docker and CI execution.

## Acceptance standard
A task is only considered verified when the relevant tests pass and the behavior matches the documented acceptance criteria.
