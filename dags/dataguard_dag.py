from __future__ import annotations

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta


def discover_batches():
    return ["batch-001"]


def ingest_batches():
    return "ingested"


def validate_batches():
    return "validated"


def summarize_health():
    return "healthy"


with DAG(
    dag_id="dataguard_hourly",
    start_date=datetime(2026, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
    },
) as dag:
    discover = PythonOperator(task_id="discover_batches", python_callable=discover_batches)
    ingest = PythonOperator(task_id="ingest_batches", python_callable=ingest_batches)
    validate = PythonOperator(task_id="validate_batches", python_callable=validate_batches)
    summary = PythonOperator(task_id="summarize_health", python_callable=summarize_health)

    discover >> ingest >> validate >> summary
