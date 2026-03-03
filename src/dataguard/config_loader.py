from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


def _resolve_path(path: str | None) -> Path:
    if not path:
        return Path(__file__).resolve().parents[2] / "config"
    return Path(path)


def load_yaml(path: str | Path) -> Any:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    with file_path.open("r", encoding="utf-8") as fh:
        content = yaml.safe_load(fh) or {}
    return content


def load_dataset_configs(config_path: str | None = None) -> list[dict[str, Any]]:
    config_file = _resolve_path(config_path) / "datasets.yml"
    data = load_yaml(config_file)
    if not isinstance(data, dict):
        raise ValueError("Dataset configuration root must be a dictionary.")
    datasets = data.get("datasets", [])
    if not isinstance(datasets, list):
        raise ValueError("Dataset configuration must include a 'datasets' list.")
    return datasets


def load_rule_configs(config_path: str | None = None) -> list[dict[str, Any]]:
    config_file = _resolve_path(config_path) / "rules.yml"
    data = load_yaml(config_file)
    if not isinstance(data, dict):
        raise ValueError("Rule configuration root must be a dictionary.")
    rules = data.get("rules", [])
    if not isinstance(rules, list):
        raise ValueError("Rule configuration must include a 'rules' list.")
    return rules


def validate_dataset_config(dataset: dict[str, Any]) -> None:
    required = {"dataset_id", "dataset_name", "source_location", "destination_table", "primary_key", "owner"}
    missing = sorted(required - set(dataset.keys()))
    if missing:
        raise ValueError(f"Dataset configuration missing fields: {', '.join(missing)}")


def validate_rule_config(rule: dict[str, Any]) -> None:
    required = {"rule_id", "rule_type", "dataset", "severity"}
    missing = sorted(required - set(rule.keys()))
    if missing:
        raise ValueError(f"Rule configuration missing fields: {', '.join(missing)}")

    if rule["rule_type"] not in {"not_null", "unique", "accepted_values", "range", "regex", "row_count_between", "foreign_key"}:
        raise ValueError(f"Unsupported rule type: {rule['rule_type']}")
