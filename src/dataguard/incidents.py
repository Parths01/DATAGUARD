from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class IncidentManager:
    def __init__(self) -> None:
        self._incidents: dict[tuple[str, str], dict[str, Any]] = {}

    def open_incident(self, dataset_name: str, check_name: str, severity: str, message: str, batch_id: str | None = None) -> dict[str, Any]:
        key = (dataset_name, check_name)
        existing = self._incidents.get(key)
        if existing and existing.get("status") == "open":
            return existing

        incident = {
            "incident_id": len(self._incidents) + 1,
            "dataset_name": dataset_name,
            "check_name": check_name,
            "severity": severity,
            "status": "open",
            "message": message,
            "batch_id": batch_id,
            "opened_at": datetime.now(timezone.utc).isoformat(),
            "resolved_at": None,
        }
        self._incidents[key] = incident
        return incident

    def resolve_incident(self, dataset_name: str, check_name: str, message: str | None = None) -> dict[str, Any] | None:
        key = (dataset_name, check_name)
        incident = self._incidents.get(key)
        if incident is None or incident.get("status") != "open":
            return None
        incident["status"] = "resolved"
        incident["resolved_at"] = datetime.now(timezone.utc).isoformat()
        if message:
            incident["message"] = message
        return incident

    def list_incidents(self, dataset_name: str | None = None, severity: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        incidents = list(self._incidents.values())
        if dataset_name:
            incidents = [incident for incident in incidents if incident["dataset_name"] == dataset_name]
        if severity:
            incidents = [incident for incident in incidents if incident["severity"] == severity]
        if status:
            incidents = [incident for incident in incidents if incident["status"] == status]
        return sorted(incidents, key=lambda x: x["opened_at"], reverse=True)
