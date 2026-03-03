from __future__ import annotations

from typing import Any


def calculate_health_score(weights: dict[str, int], failures: dict[str, int]) -> float:
    total_weight = sum(weights.values())
    if total_weight <= 0:
        return 100.0

    failed_weight = sum(failures.get(level, 0) * weight for level, weight in weights.items())
    score = 100 * (1 - (failed_weight / total_weight))
    return max(0.0, min(100.0, score))


def status_for_score(score: float) -> str:
    if score >= 90:
        return "Healthy"
    if score >= 70:
        return "Warning"
    return "Critical"
