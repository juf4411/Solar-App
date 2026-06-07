"""Data cleaning stubs for PV records."""

from datetime import UTC, datetime
from typing import Any

REQUIRED_FIELDS = {
    "timestamp",
    "plant_id",
    "power_w",
    "energy_today_kwh",
    "temperature_c",
}


def clean_pv_record(raw_record: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize one PV record.

    TODO: Add project-specific outlier handling and unit conversions.
    """

    missing = REQUIRED_FIELDS.difference(raw_record)
    if missing:
        raise ValueError(f"Missing fields: {', '.join(sorted(missing))}")

    timestamp = datetime.fromisoformat(str(raw_record["timestamp"]).replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)

    return {
        "timestamp": timestamp.astimezone(UTC).isoformat(),
        "plant_id": str(raw_record["plant_id"]).strip(),
        "power_w": float(raw_record["power_w"]),
        "energy_today_kwh": float(raw_record["energy_today_kwh"]),
        "temperature_c": float(raw_record["temperature_c"]),
        "is_mock_data": bool(raw_record.get("is_mock_data", False)),
    }
