"""Fetch current PV values from a URL or return mock data."""

from typing import Any

import requests

MOCK_PV_RECORD = {
    "timestamp": "2026-06-07T12:00:00Z",
    "plant_id": "pv-campus-demo",
    "power_w": 2450.0,
    "energy_today_kwh": 18.4,
    "temperature_c": 26.1,
    "is_mock_data": True,
}


def fetch_current_pv_values(source_url: str | None = None) -> dict[str, Any]:
    """Fetch current PV values.

    TODO: Replace the mock fallback with the real university PV endpoint once available.
    """

    if not source_url:
        return MOCK_PV_RECORD.copy()

    response = requests.get(source_url, timeout=10)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("PV endpoint must return one JSON object")
    return payload
