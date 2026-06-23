"""Bereinigt und vereinheitlicht PV-Rohdaten."""

from datetime import UTC, datetime
from typing import Any

FIELD_ALIASES = {
    "timestamp": ("timestamp", "time", "datetime", "date", "collected_at"),
    "production_power_w": ("production_power_w", "current_production_w", "pv_power_w", "power_w"),
    "consumption_power_w": ("consumption_power_w", "current_consumption_w", "load_power_w"),
    "daily_production_wh": ("daily_production_wh", "day_production_wh", "tageserzeugung_wh"),
    "daily_consumption_wh": ("daily_consumption_wh", "day_consumption_wh", "tagesverbrauch_wh"),
}


def find_value(raw_record: dict[str, Any], aliases: tuple[str, ...], default: Any = None) -> Any:
    """Sucht den ersten vorhandenen Wert aus mehreren moeglichen Feldnamen."""

    for alias in aliases:
        if alias in raw_record and raw_record[alias] not in (None, ""):
            return raw_record[alias]
    return default


def to_float(value: Any, field_name: str) -> float:
    """Wandelt einen Wert sicher in eine Kommazahl um."""

    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} muss numerisch sein") from exc


def parse_timestamp(value: Any) -> str:
    """Normalisiert einen Zeitstempel auf UTC."""

    if value in (None, ""):
        return datetime.now(UTC).isoformat()

    timestamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)
    return timestamp.astimezone(UTC).isoformat()


def normalize_server_payload(raw_record: dict[str, Any]) -> dict[str, Any]:
    """Wandelt das Datenformat der Hochschul-API in interne Dashboard-Felder um."""

    data = raw_record.get("data")
    if not isinstance(data, list):
        return raw_record

    production_power_w = 0.0
    consumption_power_w = 0.0

    for item in data:
        if not isinstance(item, dict):
            continue
        item_type = str(item.get("type", "")).strip().lower()
        value = to_float(item.get("value", 0), "value")

        if item_type == "generation":
            production_power_w += value
        elif item_type == "consumption":
            consumption_power_w += value

    normalized = dict(raw_record)
    normalized["timestamp"] = raw_record.get("collected_at") or raw_record.get("timestamp")
    normalized["production_power_w"] = production_power_w
    normalized["consumption_power_w"] = consumption_power_w
    return normalized


def clean_pv_record(raw_record: dict[str, Any]) -> dict[str, Any]:
    """Bereinigt und vereinheitlicht einen PV-Datensatz."""

    if not isinstance(raw_record, dict):
        raise ValueError("PV-Datensatz muss ein Dictionary sein")

    raw_record = normalize_server_payload(raw_record)

    return {
        "timestamp": parse_timestamp(find_value(raw_record, FIELD_ALIASES["timestamp"])),
        "plant_id": str(raw_record.get("plant_id", "pv-system")).strip(),
        "production_power_w": to_float(
            find_value(raw_record, FIELD_ALIASES["production_power_w"], 0),
            "production_power_w",
        ),
        "consumption_power_w": to_float(
            find_value(raw_record, FIELD_ALIASES["consumption_power_w"], 0),
            "consumption_power_w",
        ),
        "daily_production_wh": to_float(
            find_value(raw_record, FIELD_ALIASES["daily_production_wh"], 0),
            "daily_production_wh",
        ),
        "daily_consumption_wh": to_float(
            find_value(raw_record, FIELD_ALIASES["daily_consumption_wh"], 0),
            "daily_consumption_wh",
        ),
    }