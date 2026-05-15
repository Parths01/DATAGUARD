from __future__ import annotations

import pandas as pd

from dataguard.db import DataGuardDB
from dataguard.ingestion import ingest_dataset_batch
from dataguard.pipeline import run_batch_pipeline


def test_ingest_dataset_batch_writes_metadata(tmp_path):
    source = tmp_path / "orders.csv"
    pd.DataFrame(
        {
            "order_id": ["a", "b"],
            "order_status": ["created", "shipped"],
        }
    ).to_csv(source, index=False)
    db = DataGuardDB(sqlite_path=str(tmp_path / "dataguard.db"))
    db.init_db()

    batch = ingest_dataset_batch(
        db,
        dataset={"dataset_id": "orders", "dataset_name": "Orders"},
        source_path=str(source),
    )

    assert batch["dataset_id"] == "orders"
    assert batch["row_count"] == 2
    assert batch["batch_id"]


def test_run_batch_pipeline_persists_checks_and_health(tmp_path):
    source = tmp_path / "orders.csv"
    pd.DataFrame(
        {
            "order_id": ["a", None],
            "order_status": ["created", "unknown"],
        }
    ).to_csv(source, index=False)
    db = DataGuardDB(sqlite_path=str(tmp_path / "dataguard.db"))
    db.init_db()

    summary = run_batch_pipeline(
        db,
        dataset={"dataset_id": "orders", "dataset_name": "Orders"},
        source_path=str(source),
        rules=[
            {
                "rule_id": "orders-id-required",
                "rule_type": "not_null",
                "dataset": "orders",
                "column": "order_id",
                "severity": "critical",
            },
            {
                "rule_id": "orders-status-allowed",
                "rule_type": "accepted_values",
                "dataset": "orders",
                "column": "order_status",
                "severity": "warning",
                "parameters": {"allowed_values": ["created", "shipped"]},
            },
        ],
    )

    assert summary["row_count"] == 2
    assert summary["status"] == "Critical"
    assert {result["status"] for result in summary["checks"]} == {"failed"}
