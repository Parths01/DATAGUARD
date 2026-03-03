from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def freshness_status(latest_success_ts: str | None, expected_hours: float, grace_factor: float = 1.5) -> dict[str, Any]:
    if latest_success_ts is None:
        return {"status": "missing", "hours_since_last_success": None, "threshold_hours": expected_hours * grace_factor, "violates": True}

    try:
        latest = datetime.fromisoformat(latest_success_ts.replace("Z", "+00:00"))
    except ValueError:
        return {"status": "error", "hours_since_last_success": None, "threshold_hours": expected_hours * grace_factor, "violates": True}

    now = datetime.now(timezone.utc)
    if latest.tzinfo is None:
        latest = latest.replace(tzinfo=timezone.utc)
    elapsed_hours = (now - latest).total_seconds() / 3600.0
    threshold = max(expected_hours * grace_factor, 0.0)
    violated = elapsed_hours > threshold
    return {
        "status": "fresh" if not violated else "stale",
        "hours_since_last_success": elapsed_hours,
        "threshold_hours": threshold,
        "violates": violated,
        "expected_hours": expected_hours,
        "grace_factor": grace_factor,
    }
