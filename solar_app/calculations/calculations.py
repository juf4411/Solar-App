"""Calculation stubs for PV dashboard KPIs."""

from typing import Any


def calculate_average_power(records: list[dict[str, Any]]) -> float:
    """Calculate average power in watts."""

    if not records:
        return 0.0
    return round(sum(float(record["power_w"]) for record in records) / len(records), 2)


def calculate_dashboard_kpis(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the KPI dictionary used by the dashboard."""

    latest = records[-1] if records else None
    return {
        "record_count": len(records),
        "latest": latest,
        "average_power_w": calculate_average_power(records),
        "energy_today_kwh": float(latest["energy_today_kwh"]) if latest else 0.0,
    }
