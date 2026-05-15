from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from dataguard.db import DataGuardDB
from dataguard.health import calculate_health_score, status_for_score
from dataguard.ingestion import ingest_dataset_batch
from dataguard.rules import execute_rule


SEVERITY_WEIGHTS = {"critical": 5, "warning": 2, "informational": 1}


def run_batch_pipeline(
    db: DataGuardDB,
    dataset: dict[str, Any],
    source_path: str,
    rules: list[dict[str, Any]],
) -> dict[str, Any]:
    started_at = datetime.now(timezone.utc)
    batch = ingest_dataset_batch(db, dataset, source_path)
    dataframe = batch.pop("dataframe")
    checks = [execute_rule(rule, dataframe) for rule in rules]
    failures = {
        severity: sum(
            result["status"] == "failed" and result.get("severity") == severity
            for result in checks
        )
        for severity in SEVERITY_WEIGHTS
    }
    health_score = calculate_health_score(SEVERITY_WEIGHTS, failures)
    finished_at = datetime.now(timezone.utc)

    for result in checks:
        db.record_check_run(
            batch["batch_id"],
            dataset.get("dataset_name", dataset.get("dataset_id", "")),
            result.get("rule_id", "unknown"),
            result.get("rule_type", "unknown"),
            result.get("severity", "informational"),
            result["status"],
            result.get("measured_value"),
            result.get("threshold"),
            result.get("message", ""),
            result.get("sample_rows"),
        )
    db.record_batch_run(
        batch["batch_id"],
        dataset.get("dataset_name", dataset.get("dataset_id", "")),
        started_at.isoformat(),
        finished_at.isoformat(),
        batch["row_count"],
        health_score,
    )
    return {
        **batch,
        "checks": checks,
        "health_score": health_score,
        "status": status_for_score(health_score),
    }
