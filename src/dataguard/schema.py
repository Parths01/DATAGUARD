from __future__ import annotations

import json
from typing import Any

import pandas as pd


def _normalize_dtype(dtype: Any) -> str:
    value = str(dtype).lower()
    if value in {"object", "string", "str", "string[python]", "string[pyarrow]"}:
        return "object"
    if value.startswith("int"):
        return "int"
    if value.startswith("float"):
        return "float"
    if value.startswith("bool"):
        return "bool"
    if value.startswith("datetime"):
        return "datetime"
    return value


def detect_schema_drift(current_df: pd.DataFrame, baseline: dict[str, Any] | None) -> dict[str, Any]:
    if baseline is None:
        return {"added": [], "dropped": [], "changed": [], "baseline_missing": True}

    baseline_columns = {col: _normalize_dtype(dtype) for col, dtype in baseline.get("columns", {}).items()}
    current_columns = {col: _normalize_dtype(dtype) for col, dtype in current_df.dtypes.items()}
    added = sorted(set(current_columns) - set(baseline_columns))
    dropped = sorted(set(baseline_columns) - set(current_columns))
    changed = []
    for column in sorted(set(current_columns) & set(baseline_columns)):
        if baseline_columns[column] != current_columns[column]:
            changed.append({"column": column, "from": baseline_columns[column], "to": current_columns[column]})
    return {"added": added, "dropped": dropped, "changed": changed, "baseline_missing": False}


def save_schema_snapshot(conn, dataset_name: str, df: pd.DataFrame) -> None:
    schema_payload = {col: str(dtype) for col, dtype in df.dtypes.items()}
    if conn.use_sqlite:
        conn.connect().execute(
            "INSERT INTO schema_snapshot(dataset_name, schema_json, created_at) VALUES (?, ?, datetime('now'))",
            (dataset_name, json.dumps(schema_payload)),
        )
        conn.connect().commit()
    else:
        with conn.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO meta.schema_snapshot(dataset_name, schema_json, created_at) VALUES (%s, %s, CURRENT_TIMESTAMP)",
                    (dataset_name, json.dumps(schema_payload)),
                )
            connection.commit()


def load_latest_schema(conn, dataset_name: str) -> dict[str, Any] | None:
    with conn.connect() as connection:
        if conn.use_sqlite:
            row = connection.execute(
                "SELECT schema_json FROM schema_snapshot WHERE dataset_name = ? ORDER BY snapshot_id DESC LIMIT 1",
                (dataset_name,),
            ).fetchone()
        else:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT schema_json FROM meta.schema_snapshot WHERE dataset_name = %s ORDER BY snapshot_id DESC LIMIT 1",
                    (dataset_name,),
                )
                row = cursor.fetchone()
        if row is None:
            return None
        value = row[0] if isinstance(row, tuple) else row["schema_json"]
        return json.loads(value)
