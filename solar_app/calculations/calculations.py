"""Berechnet Kennzahlen für das PV-Dashboard."""

from datetime import UTC, datetime
from typing import Any


def parse_record_timestamp(record: dict[str, Any]) -> datetime | None:
    """Liest den Zeitstempel eines Messwerts als UTC-Zeit."""

    value = record.get("timestamp")
    if not value:
        return None

    try:
        timestamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)
    return timestamp.astimezone(UTC)


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


def calculate_period_total(records: list[dict[str, Any]], value_key: str, period: str) -> float:
    """Berechnet Tages-, Monats- oder Jahreswerte aus gespeicherten Messwerten."""

    dated_records = [
        (timestamp, record)
        for record in records
        if (timestamp := parse_record_timestamp(record)) is not None
    ]
    if not dated_records:
        return 0.0

    reference = dated_records[-1][0]

    if period == "day":
        matching = [
            float(record.get(value_key, 0))
            for timestamp, record in dated_records
            if timestamp.date() == reference.date()
        ]
        return round(max(matching, default=0.0), 2)

    totals_by_day: dict[str, float] = {}
    for timestamp, record in dated_records:
        same_month = timestamp.year == reference.year and timestamp.month == reference.month
        same_year = timestamp.year == reference.year

        if period == "month" and not same_month:
            continue
        if period == "year" and not same_year:
            continue

        day_key = timestamp.date().isoformat()
        totals_by_day[day_key] = max(
            totals_by_day.get(day_key, 0.0),
            float(record.get(value_key, 0)),
        )

    return round(sum(totals_by_day.values()), 2)


def build_chart_points(records: list[dict[str, Any]], limit: int = 14) -> list[dict[str, Any]]:
    """Bereitet Messwerte für den Tagesverlauf im Dashboard vor."""

    points = []
    for record in records[-limit:]:
        timestamp = parse_record_timestamp(record)
        label = timestamp.strftime("%H:%M") if timestamp else ""
        points.append(
            {
                "label": label,
                "daily_production_wh": float(record.get("daily_production_wh", 0)),
                "daily_consumption_wh": float(record.get("daily_consumption_wh", 0)),
                "production_power_w": float(record.get("production_power_w", 0)),
                "consumption_power_w": float(record.get("consumption_power_w", 0)),
            }
        )
    return points


def calculate_dashboard_kpis(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Erstellt alle Kennzahlen für das Dashboard."""

    latest = records[-1] if records else None
    latest_or_empty = latest or {}

    daily_production_wh = calculate_period_total(records, "daily_production_wh", "day")
    daily_consumption_wh = calculate_period_total(records, "daily_consumption_wh", "day")
    monthly_production_wh = calculate_period_total(records, "daily_production_wh", "month")
    monthly_consumption_wh = calculate_period_total(records, "daily_consumption_wh", "month")
    yearly_production_wh = calculate_period_total(records, "daily_production_wh", "year")
    yearly_consumption_wh = calculate_period_total(records, "daily_consumption_wh", "year")

    return {
        "record_count": len(records),
        "latest": latest,
        "average_power_w": calculate_average_power(records),
        "current_production_w": float(latest_or_empty.get("production_power_w", 0)),
        "current_consumption_w": float(latest_or_empty.get("consumption_power_w", 0)),
        "daily_production_wh": daily_production_wh,
        "daily_consumption_wh": daily_consumption_wh,
        "monthly_production_wh": monthly_production_wh,
        "monthly_consumption_wh": monthly_consumption_wh,
        "yearly_production_wh": yearly_production_wh,
        "yearly_consumption_wh": yearly_consumption_wh,
        "daily_pv_ratio_percent": calculate_pv_ratio(
            daily_production_wh,
            daily_consumption_wh,
        ),
        "monthly_pv_ratio_percent": calculate_pv_ratio(
            monthly_production_wh,
            monthly_consumption_wh,
        ),
        "yearly_pv_ratio_percent": calculate_pv_ratio(
            yearly_production_wh,
            yearly_consumption_wh,
        ),
        "chart_points": build_chart_points(records),
    }
