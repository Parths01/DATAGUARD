import pandas as pd

from dataguard.config_loader import load_dataset_configs, load_rule_configs, validate_dataset_config
from dataguard.health import calculate_health_score
from dataguard.incidents import IncidentManager
from dataguard.rules import execute_rule
from dataguard.schema import detect_schema_drift
from dataguard.anomaly import detect_anomaly


def test_dataset_config_loads():
    datasets = load_dataset_configs("config")
    assert datasets[0]["dataset_id"] == "olist_orders"
    validate_dataset_config(datasets[0])


def test_rule_configs_load():
    rules = load_rule_configs("config")
    assert rules[0]["rule_type"] == "not_null"


def test_not_null_rule_failure():
    df = pd.DataFrame({"order_id": ["a", None, "c"]})
    result = execute_rule({"rule_id": "r1", "rule_type": "not_null", "dataset": "olist_orders", "column": "order_id", "severity": "critical"}, df)
    assert result["status"] == "failed"
    assert result["measured_value"] == 1


def test_schema_drift_detection():
    current = pd.DataFrame({"order_id": ["a"], "status": ["shipped"], "new_col": [1]})
    baseline = {"columns": {"order_id": "object", "status": "object"}}
    drift = detect_schema_drift(current, baseline)
    assert drift["added"] == ["new_col"]
    assert drift["dropped"] == []
    assert len(drift["changed"]) == 0


def test_health_score_calculation():
    score = calculate_health_score({"critical": 5, "warning": 2, "informational": 1}, {"critical": 0, "warning": 1, "informational": 0})
    assert 70 <= score <= 100
    assert score == 75.0


def test_anomaly_detection():
    series = [10, 11, 10, 12, 11, 12, 10, 11, 1000]
    result = detect_anomaly(series)
    assert result["status"] == "anomaly"


def test_incident_manager_deduplication():
    manager = IncidentManager()
    first = manager.open_incident("orders", "missing_column", "critical", "check failed")
    second = manager.open_incident("orders", "missing_column", "critical", "check failed")
    assert first["incident_id"] == second["incident_id"]
    assert len(manager.list_incidents()) == 1
