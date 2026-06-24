"""Berechnet Kennzahlen für das PV-Dashboard."""

from typing import Any


def calculate_average_power(records: list[dict[str, Any]]) -> float:
    """Berechnet die durchschnittliche PV-Leistung."""

    if not records:
        return 0.0
    return round(sum(float(record["production_power_w"]) for record in records) / len(records), 2)


def calculate_pv_ratio(production_wh: float, consumption_wh: float) -> float:
    """Berechnet den PV-Anteil am Gesamtverbrauch in Prozent."""

    if consumption_wh <= 0:
        return 0.0
    return round(min(production_wh / consumption_wh, 1.0) * 100, 2)


def calculate_dashboard_kpis(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Erstellt alle Kennzahlen für das Dashboard."""

    latest = records[-1] if records else None
    latest_or_empty = latest or {}

    daily_production_wh = float(latest_or_empty.get("daily_production_wh", 0))
    daily_consumption_wh = float(latest_or_empty.get("daily_consumption_wh", 0))

    return {
        "record_count": len(records),
        "latest": latest,
        "average_power_w": calculate_average_power(records),
        "current_production_w": float(latest_or_empty.get("production_power_w", 0)),
        "current_consumption_w": float(latest_or_empty.get("consumption_power_w", 0)),
        "daily_production_wh": daily_production_wh,
        "daily_consumption_wh": daily_consumption_wh,
        "daily_pv_ratio_percent": calculate_pv_ratio(
            daily_production_wh,
            daily_consumption_wh,
        ),
    }
