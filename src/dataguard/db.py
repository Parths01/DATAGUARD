from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Iterable

import psycopg2
from psycopg2.extras import RealDictCursor


class DataGuardDB:
    def __init__(self, database_url: str | None = None, sqlite_path: str | None = None) -> None:
        self.database_url = database_url or os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
        self.sqlite_path = sqlite_path or os.getenv("SQLITE_PATH", str(Path(__file__).resolve().parents[2] / "data" / "dataguard.db"))
        self.use_sqlite = not self.database_url

    def connect(self):
        if self.use_sqlite:
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row
            return conn
        return psycopg2.connect(self.database_url)

    def init_db(self) -> None:
        with closing(self.connect()) as conn:
            if self.use_sqlite:
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS dim_dataset (dataset_id TEXT PRIMARY KEY, dataset_name TEXT, source_location TEXT, destination_table TEXT, primary_key TEXT, expected_update_frequency TEXT, owner TEXT, downstream_tables TEXT)")
                cursor.execute("CREATE TABLE IF NOT EXISTS schema_snapshot (snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT, dataset_name TEXT, schema_json TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
                cursor.execute("CREATE TABLE IF NOT EXISTS pipeline_run (run_id INTEGER PRIMARY KEY AUTOINCREMENT, batch_id TEXT, dataset_name TEXT, started_at TEXT, finished_at TEXT, row_count INTEGER, health_score REAL)")
                cursor.execute("CREATE TABLE IF NOT EXISTS fact_check_run (check_id INTEGER PRIMARY KEY AUTOINCREMENT, batch_id TEXT, dataset_name TEXT, check_name TEXT, check_type TEXT, severity TEXT, status TEXT, measured_value TEXT, threshold TEXT, message TEXT, sample_rows TEXT, executed_at TEXT DEFAULT CURRENT_TIMESTAMP)")
                cursor.execute("CREATE TABLE IF NOT EXISTS fact_incident (incident_id INTEGER PRIMARY KEY AUTOINCREMENT, dataset_name TEXT, check_name TEXT, severity TEXT, status TEXT, opened_at TEXT, resolved_at TEXT, message TEXT, batch_id TEXT)")
                cursor.execute("CREATE TABLE IF NOT EXISTS metric_history (metric_id INTEGER PRIMARY KEY AUTOINCREMENT, dataset_name TEXT, metric_type TEXT, metric_value REAL, observed_at TEXT)")
                cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_incident_active ON fact_incident(dataset_name, check_name, status) WHERE status = 'open'")
                conn.commit()
                return
            cursor = conn.cursor()
            cursor.execute("CREATE SCHEMA IF NOT EXISTS raw")
            cursor.execute("CREATE SCHEMA IF NOT EXISTS meta")
            cursor.execute("CREATE TABLE IF NOT EXISTS meta.dim_dataset (dataset_id TEXT PRIMARY KEY, dataset_name TEXT, source_location TEXT, destination_table TEXT, primary_key TEXT, expected_update_frequency TEXT, owner TEXT, downstream_tables TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS meta.schema_snapshot (snapshot_id SERIAL PRIMARY KEY, dataset_name TEXT, schema_json TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
            cursor.execute("CREATE TABLE IF NOT EXISTS meta.pipeline_run (run_id SERIAL PRIMARY KEY, batch_id TEXT, dataset_name TEXT, started_at TIMESTAMP, finished_at TIMESTAMP, row_count INTEGER, health_score REAL)")
            cursor.execute("CREATE TABLE IF NOT EXISTS meta.fact_check_run (check_id SERIAL PRIMARY KEY, batch_id TEXT, dataset_name TEXT, check_name TEXT, check_type TEXT, severity TEXT, status TEXT, measured_value TEXT, threshold TEXT, message TEXT, sample_rows TEXT, executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
            cursor.execute("CREATE TABLE IF NOT EXISTS meta.fact_incident (incident_id SERIAL PRIMARY KEY, dataset_name TEXT, check_name TEXT, severity TEXT, status TEXT, opened_at TIMESTAMP, resolved_at TIMESTAMP, message TEXT, batch_id TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS meta.metric_history (metric_id SERIAL PRIMARY KEY, dataset_name TEXT, metric_type TEXT, metric_value REAL, observed_at TIMESTAMP)")
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_incident_active ON meta.fact_incident(dataset_name, check_name, status) WHERE status = 'open'")
            conn.commit()

    def register_dataset(self, dataset: dict[str, Any]) -> None:
        with closing(self.connect()) as conn:
            if self.use_sqlite:
                conn.execute(
                    "INSERT OR REPLACE INTO dim_dataset(dataset_id, dataset_name, source_location, destination_table, primary_key, expected_update_frequency, owner, downstream_tables) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        dataset.get("dataset_id"),
                        dataset.get("dataset_name"),
                        dataset.get("source_location"),
                        dataset.get("destination_table"),
                        dataset.get("primary_key"),
                        dataset.get("expected_update_frequency"),
                        dataset.get("owner"),
                        ";".join(dataset.get("downstream_tables", [])),
                    ),
                )
            else:
                conn.cursor().execute(
                    "INSERT INTO meta.dim_dataset(dataset_id, dataset_name, source_location, destination_table, primary_key, expected_update_frequency, owner, downstream_tables) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (dataset_id) DO UPDATE SET dataset_name = EXCLUDED.dataset_name, source_location = EXCLUDED.source_location, destination_table = EXCLUDED.destination_table, primary_key = EXCLUDED.primary_key, expected_update_frequency = EXCLUDED.expected_update_frequency, owner = EXCLUDED.owner, downstream_tables = EXCLUDED.downstream_tables",
                    (
                        dataset.get("dataset_id"),
                        dataset.get("dataset_name"),
                        dataset.get("source_location"),
                        dataset.get("destination_table"),
                        dataset.get("primary_key"),
                        dataset.get("expected_update_frequency"),
                        dataset.get("owner"),
                        ";".join(dataset.get("downstream_tables", [])),
                    ),
                )
            conn.commit()

    def record_batch_run(self, batch_id: str, dataset_name: str, started_at: str, finished_at: str, row_count: int, health_score: float) -> None:
        with closing(self.connect()) as conn:
            if self.use_sqlite:
                conn.execute(
                    "INSERT INTO pipeline_run(batch_id, dataset_name, started_at, finished_at, row_count, health_score) VALUES (?, ?, ?, ?, ?, ?)",
                    (batch_id, dataset_name, started_at, finished_at, row_count, health_score),
                )
            else:
                conn.cursor().execute(
                    "INSERT INTO meta.pipeline_run(batch_id, dataset_name, started_at, finished_at, row_count, health_score) VALUES (%s, %s, %s, %s, %s, %s)",
                    (batch_id, dataset_name, started_at, finished_at, row_count, health_score),
                )
            conn.commit()

    def record_check_run(self, batch_id: str, dataset_name: str, check_name: str, check_type: str, severity: str, status: str, measured_value: Any, threshold: Any, message: str, sample_rows: Any) -> None:
        with closing(self.connect()) as conn:
            if self.use_sqlite:
                conn.execute(
                    "INSERT INTO fact_check_run(batch_id, dataset_name, check_name, check_type, severity, status, measured_value, threshold, message, sample_rows, executed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))",
                    (
                        batch_id,
                        dataset_name,
                        check_name,
                        check_type,
                        severity,
                        status,
                        str(measured_value),
                        str(threshold),
                        message,
                        str(sample_rows) if sample_rows is not None else None,
                    ),
                )
            else:
                conn.cursor().execute(
                    "INSERT INTO meta.fact_check_run(batch_id, dataset_name, check_name, check_type, severity, status, measured_value, threshold, message, sample_rows, executed_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)",
                    (
                        batch_id,
                        dataset_name,
                        check_name,
                        check_type,
                        severity,
                        status,
                        str(measured_value),
                        str(threshold),
                        message,
                        str(sample_rows) if sample_rows is not None else None,
                    ),
                )
            conn.commit()

    def get_recent_metrics(self, dataset_name: str, metric_type: str, limit: int = 30) -> list[float]:
        with closing(self.connect()) as conn:
            if self.use_sqlite:
                rows = conn.execute(
                    "SELECT metric_value FROM metric_history WHERE dataset_name = ? AND metric_type = ? ORDER BY metric_id DESC LIMIT ?",
                    (dataset_name, metric_type, limit),
                ).fetchall()
            else:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT metric_value FROM meta.metric_history WHERE dataset_name = %s AND metric_type = %s ORDER BY metric_id DESC LIMIT %s",
                        (dataset_name, metric_type, limit),
                    )
                    rows = cursor.fetchall()
            return [float(row[0]) for row in rows]

    def store_metric(self, dataset_name: str, metric_type: str, metric_value: float, observed_at: str | None = None) -> None:
        with closing(self.connect()) as conn:
            if self.use_sqlite:
                conn.execute(
                    "INSERT INTO metric_history(dataset_name, metric_type, metric_value, observed_at) VALUES (?, ?, ?, ?)",
                    (dataset_name, metric_type, float(metric_value), observed_at or "NOW"),
                )
            else:
                conn.cursor().execute(
                    "INSERT INTO meta.metric_history(dataset_name, metric_type, metric_value, observed_at) VALUES (%s, %s, %s, %s)",
                    (dataset_name, metric_type, float(metric_value), observed_at or "CURRENT_TIMESTAMP"),
                )
            conn.commit()

    def fetch_incidents(self, dataset_name: str | None = None, severity: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        with closing(self.connect()) as conn:
            if self.use_sqlite:
                query = "SELECT * FROM fact_incident WHERE 1=1"
                params: list[Any] = []
                if dataset_name:
                    query += " AND dataset_name = ?"
                    params.append(dataset_name)
                if severity:
                    query += " AND severity = ?"
                    params.append(severity)
                if status:
                    query += " AND status = ?"
                    params.append(status)
                query += " ORDER BY opened_at DESC"
                rows = conn.execute(query, params).fetchall()
            else:
                query = "SELECT * FROM meta.fact_incident WHERE 1=1"
                params: list[Any] = []
                if dataset_name:
                    query += " AND dataset_name = %s"
                    params.append(dataset_name)
                if severity:
                    query += " AND severity = %s"
                    params.append(severity)
                if status:
                    query += " AND status = %s"
                    params.append(status)
                query += " ORDER BY opened_at DESC"
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
            return [dict(row) for row in rows]


def get_db() -> DataGuardDB:
    return DataGuardDB()
