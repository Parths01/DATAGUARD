from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any


RULE_REGISTRY: dict[str, Callable[..., dict[str, Any]]] = {}


def register_rule(rule_type: str):
    def decorator(func: Callable[..., dict[str, Any]]):
        RULE_REGISTRY[rule_type] = func
        return func

    return decorator


def _result(rule: dict[str, Any], status: str, measured_value: Any, threshold: Any, message: str, sample_rows: Any = None) -> dict[str, Any]:
    return {
        "rule_id": rule.get("rule_id"),
        "dataset": rule.get("dataset"),
        "column": rule.get("column"),
        "rule_type": rule.get("rule_type"),
        "severity": rule.get("severity"),
        "status": status,
        "measured_value": measured_value,
        "threshold": threshold,
        "message": message,
        "sample_rows": sample_rows,
    }


@register_rule("not_null")
def not_null_rule(df, rule: dict[str, Any]) -> dict[str, Any]:
    column = rule.get("column")
    if column not in df.columns:
        return _result(rule, "error", None, None, f"Column {column} not found.", None)
    null_count = int(df[column].isna().sum())
    if null_count > 0:
        return _result(rule, "failed", null_count, "0", f"Column {column} has {null_count} null values.", df[df[column].isna()].head(5).to_dict(orient="records"))
    return _result(rule, "passed", 0, "0", f"Column {column} has no null values.", None)


@register_rule("unique")
def unique_rule(df, rule: dict[str, Any]) -> dict[str, Any]:
    column = rule.get("column")
    if column not in df.columns:
        return _result(rule, "error", None, None, f"Column {column} not found.", None)
    duplicates = df[column].duplicated().sum()
    threshold = rule.get("parameters", {}).get("max_duplicates", 0)
    if duplicates > threshold:
        return _result(rule, "failed", duplicates, threshold, f"Duplicate values detected in {column}: {duplicates} duplicates.", df[df[column].duplicated()].head(5).to_dict(orient="records"))
    return _result(rule, "passed", duplicates, threshold, f"No duplicate violations found in {column}.", None)


@register_rule("accepted_values")
def accepted_values_rule(df, rule: dict[str, Any]) -> dict[str, Any]:
    column = rule.get("column")
    allowed = set(rule.get("parameters", {}).get("allowed_values", []))
    if column not in df.columns:
        return _result(rule, "error", None, None, f"Column {column} not found.", None)
    bad = df[~df[column].fillna("__missing").astype(str).isin([str(x) for x in allowed])]
    if not bad.empty:
        return _result(rule, "failed", len(bad), f"Allowed values: {sorted(allowed)}", f"Unexpected values found in {column}.", bad.head(5).to_dict(orient="records"))
    return _result(rule, "passed", 0, f"Allowed values: {sorted(allowed)}", f"Values in {column} match accepted values.", None)


@register_rule("range")
def range_rule(df, rule: dict[str, Any]) -> dict[str, Any]:
    column = rule.get("column")
    params = rule.get("parameters", {})
    min_value = params.get("min")
    max_value = params.get("max")
    if column not in df.columns:
        return _result(rule, "error", None, None, f"Column {column} not found.", None)
    if min_value is None and max_value is None:
        return _result(rule, "error", None, None, "Range rule requires min or max parameter.", None)
    numeric = pd.to_numeric(df[column], errors="coerce")
    bad = df[(numeric < min_value) | (numeric > max_value)] if min_value is not None and max_value is not None else df[(numeric < min_value) if min_value is not None else (numeric > max_value)]
    if not bad.empty:
        return _result(rule, "failed", len(bad), f"[{min_value}, {max_value}]", f"Values outside the permitted range in {column}.", bad.head(5).to_dict(orient="records"))
    return _result(rule, "passed", 0, f"[{min_value}, {max_value}]", f"All values in {column} are within the permitted range.", None)


@register_rule("regex")
def regex_rule(df, rule: dict[str, Any]) -> dict[str, Any]:
    column = rule.get("column")
    pattern = rule.get("parameters", {}).get("pattern")
    if column not in df.columns:
        return _result(rule, "error", None, None, f"Column {column} not found.", None)
    if not pattern:
        return _result(rule, "error", None, None, "Regex rule requires a pattern parameter.", None)
    matcher = re.compile(pattern)
    bad = df[~df[column].fillna("").astype(str).map(lambda x: bool(matcher.fullmatch(x)))]
    if not bad.empty:
        return _result(rule, "failed", len(bad), pattern, f"Values in {column} do not match the expected pattern.", bad.head(5).to_dict(orient="records"))
    return _result(rule, "passed", 0, pattern, f"Values in {column} match the expected pattern.", None)


@register_rule("row_count_between")
def row_count_between_rule(df, rule: dict[str, Any]) -> dict[str, Any]:
    params = rule.get("parameters", {})
    min_rows = params.get("min_rows")
    max_rows = params.get("max_rows")
    row_count = len(df)
    if min_rows is None and max_rows is None:
        return _result(rule, "error", row_count, None, "row_count_between requires min_rows or max_rows.", None)
    if row_count < min_rows if min_rows is not None else False or row_count > max_rows if max_rows is not None else False:
        return _result(rule, "failed", row_count, f"[{min_rows}, {max_rows}]", f"Row count {row_count} is outside the expected range.", None)
    return _result(rule, "passed", row_count, f"[{min_rows}, {max_rows}]", f"Row count is within expected range ({row_count}).", None)


@register_rule("foreign_key")
def foreign_key_rule(df, rule: dict[str, Any]) -> dict[str, Any]:
    params = rule.get("parameters", {})
    column = rule.get("column")
    reference_dataset = params.get("reference_dataset")
    reference_column = params.get("reference_column")
    if not reference_dataset or not reference_column:
        return _result(rule, "error", None, None, "foreign_key rules require reference_dataset and reference_column parameters.", None)
    if column not in df.columns:
        return _result(rule, "error", None, None, f"Column {column} not found.", None)
    reference_values = params.get("reference_values", [])
    if reference_values:
        invalid = df[~df[column].fillna("").astype(str).isin([str(x) for x in reference_values])]
        if not invalid.empty:
            return _result(rule, "failed", len(invalid), reference_values, f"Foreign key column {column} contains invalid values.", invalid.head(5).to_dict(orient="records"))
        return _result(rule, "passed", 0, reference_values, f"Foreign key values in {column} are valid.", None)
    return _result(rule, "passed", 0, {"reference_dataset": reference_dataset, "reference_column": reference_column}, "Foreign key check configured without live reference data.", None)


def execute_rule(rule: dict[str, Any], dataframe) -> dict[str, Any]:
    rule_type = rule.get("rule_type")
    if rule_type not in RULE_REGISTRY:
        return _result(rule, "error", None, None, f"Unknown rule type: {rule_type}", None)
    try:
        return RULE_REGISTRY[rule_type](dataframe, rule)
    except Exception as exc:  # pragma: no cover - guard real error capture
        return _result(rule, "error", None, None, f"Rule execution error: {exc}", None)


import pandas as pd
