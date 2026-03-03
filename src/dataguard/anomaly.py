from __future__ import annotations

import math
from statistics import mean, pstdev
from typing import Any


def detect_anomaly(values: list[float], historical_window: int | None = None) -> dict[str, Any]:
    if not values:
        return {"status": "insufficient_history", "method": "none", "details": "No values provided."}
    if len(values) < 7:
        return {"status": "insufficient_history", "method": "none", "details": "At least 7 historical observations are required."}

    current = float(values[-1])
    hist = [float(v) for v in values[:-1]]
    if not hist or all(v == hist[0] for v in hist):
        return {"status": "insufficient_history", "method": "none", "details": "Insufficient variability for anomaly detection."}

    avg = mean(hist)
    std = pstdev(hist)
    if math.isclose(std, 0.0, abs_tol=1e-9):
        return {"status": "insufficient_history", "method": "none", "details": "Zero variance detected; anomaly detection skipped."}

    z = abs((current - avg) / std)
    if z > 3:
        return {"status": "anomaly", "method": "zscore", "z_score": z, "threshold": 3, "current": current, "baseline_mean": avg, "baseline_std": std}

    q1 = sorted(hist)[max(0, len(hist) // 4)]
    q3 = sorted(hist)[min(len(hist) - 1, int(len(hist) * 0.75))]
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    if current < lower or current > upper:
        return {"status": "anomaly", "method": "iqr", "current": current, "lower_bound": lower, "upper_bound": upper}
    return {"status": "normal", "method": "zscore_or_iqr", "current": current, "baseline_mean": avg, "baseline_std": std}
