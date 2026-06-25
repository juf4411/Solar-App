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
        same_week = (
            timestamp.isocalendar().year == reference.isocalendar().year
            and timestamp.isocalendar().week == reference.isocalendar().week
        )
        same_month = timestamp.year == reference.year and timestamp.month == reference.month
        same_year = timestamp.year == reference.year

        if period == "week" and not same_week:
            continue
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


def timestamp_matches_period(timestamp: datetime, reference: datetime, period: str) -> bool:
    """Prüft, ob ein Zeitpunkt zum gewünschten Auswertungszeitraum gehört."""

    if period == "day":
        return timestamp.date() == reference.date()
    if period == "week":
        return (
            timestamp.isocalendar().year == reference.isocalendar().year
            and timestamp.isocalendar().week == reference.isocalendar().week
        )
    if period == "month":
        return timestamp.year == reference.year and timestamp.month == reference.month
    if period == "year":
        return timestamp.year == reference.year
    return False


def calculate_integrated_energy(
    records: list[dict[str, Any]],
    power_key: str,
    period: str,
    max_gap_seconds: int = 300,
) -> float:
    """Schätzt Energie aus Leistungswerten und Zeitabständen."""

    dated_records = sorted(
        (
            (timestamp, record)
            for record in records
            if (timestamp := parse_record_timestamp(record)) is not None
        ),
        key=lambda item: item[0],
    )
    if len(dated_records) < 2:
        return 0.0

    reference = dated_records[-1][0]
    total_wh = 0.0

    for (previous_time, previous_record), (current_time, current_record) in zip(
        dated_records,
        dated_records[1:],
        strict=False,
    ):
        if not (
            timestamp_matches_period(previous_time, reference, period)
            and timestamp_matches_period(current_time, reference, period)
        ):
            continue

        delta_seconds = (current_time - previous_time).total_seconds()
        if delta_seconds <= 0 or delta_seconds > max_gap_seconds:
            continue

        previous_power = float(previous_record.get(power_key, 0))
        current_power = float(current_record.get(power_key, 0))
        average_power = (previous_power + current_power) / 2
        total_wh += average_power * (delta_seconds / 3600)

    return round(total_wh, 2)


def calculate_period_energy(
    records: list[dict[str, Any]],
    value_key: str,
    power_key: str,
    period: str,
) -> float:
    """Nutzt Zählerwerte oder schätzt Energie aus Momentanleistung."""

    direct_total = calculate_period_total(records, value_key, period)
    if direct_total > 0:
        return direct_total
    return calculate_integrated_energy(records, power_key, period)


def build_chart_points(records: list[dict[str, Any]], limit: int = 14) -> list[dict[str, Any]]:
    """Bereitet Messwerte für den Tagesverlauf im Dashboard vor."""

    points = []
    visible_records = records[-limit:]
    production_wh = 0.0
    consumption_wh = 0.0
    previous_timestamp = None
    previous_record = None

    for record in visible_records:
        timestamp = parse_record_timestamp(record)
        if timestamp and previous_timestamp and previous_record:
            delta_seconds = (timestamp - previous_timestamp).total_seconds()
            if 0 < delta_seconds <= 300:
                production_wh += (
                    (
                        float(previous_record.get("production_power_w", 0))
                        + float(record.get("production_power_w", 0))
                    )
                    / 2
                    * (delta_seconds / 3600)
                )
                consumption_wh += (
                    (
                        float(previous_record.get("consumption_power_w", 0))
                        + float(record.get("consumption_power_w", 0))
                    )
                    / 2
                    * (delta_seconds / 3600)
                )

        label = timestamp.strftime("%H:%M") if timestamp else ""
        direct_production_wh = float(record.get("daily_production_wh", 0))
        direct_consumption_wh = float(record.get("daily_consumption_wh", 0))
        points.append(
            {
                "label": label,
                "daily_production_wh": direct_production_wh or round(production_wh, 2),
                "daily_consumption_wh": direct_consumption_wh or round(consumption_wh, 2),
                "production_power_w": float(record.get("production_power_w", 0)),
                "consumption_power_w": float(record.get("consumption_power_w", 0)),
            }
        )
        previous_timestamp = timestamp
        previous_record = record

    return points


def calculate_dashboard_kpis(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Erstellt alle Kennzahlen für das Dashboard."""

    latest = records[-1] if records else None
    latest_or_empty = latest or {}

    daily_production_wh = calculate_period_energy(
        records, "daily_production_wh", "production_power_w", "day"
    )
    daily_consumption_wh = calculate_period_energy(
        records, "daily_consumption_wh", "consumption_power_w", "day"
    )
    weekly_production_wh = calculate_period_energy(
        records, "daily_production_wh", "production_power_w", "week"
    )
    weekly_consumption_wh = calculate_period_energy(
        records, "daily_consumption_wh", "consumption_power_w", "week"
    )
    monthly_production_wh = calculate_period_energy(
        records, "daily_production_wh", "production_power_w", "month"
    )
    monthly_consumption_wh = calculate_period_energy(
        records, "daily_consumption_wh", "consumption_power_w", "month"
    )
    yearly_production_wh = calculate_period_energy(
        records, "daily_production_wh", "production_power_w", "year"
    )
    yearly_consumption_wh = calculate_period_energy(
        records, "daily_consumption_wh", "consumption_power_w", "year"
    )

    return {
        "record_count": len(records),
        "latest": latest,
        "average_power_w": calculate_average_power(records),
        "current_production_w": float(latest_or_empty.get("production_power_w", 0)),
        "current_consumption_w": float(latest_or_empty.get("consumption_power_w", 0)),
        "daily_production_wh": daily_production_wh,
        "daily_consumption_wh": daily_consumption_wh,
        "weekly_production_wh": weekly_production_wh,
        "weekly_consumption_wh": weekly_consumption_wh,
        "monthly_production_wh": monthly_production_wh,
        "monthly_consumption_wh": monthly_consumption_wh,
        "yearly_production_wh": yearly_production_wh,
        "yearly_consumption_wh": yearly_consumption_wh,
        "daily_pv_ratio_percent": calculate_pv_ratio(
            daily_production_wh,
            daily_consumption_wh,
        ),
        "weekly_pv_ratio_percent": calculate_pv_ratio(
            weekly_production_wh,
            weekly_consumption_wh,
        ),
        "weekly_grid_purchase_wh": round(
            max(weekly_consumption_wh - weekly_production_wh, 0.0),
            2,
        ),
        "weekly_feed_in_wh": round(
            max(weekly_production_wh - weekly_consumption_wh, 0.0),
            2,
        ),
        "weekly_autarky_percent": calculate_pv_ratio(
            weekly_production_wh,
            weekly_consumption_wh,
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
