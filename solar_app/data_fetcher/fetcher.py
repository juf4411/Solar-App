"""Ruft aktuelle PV-Werte von der Hochschul-URL ab."""

from typing import Any

import requests


def fetch_current_pv_values(
    source_url: str,
    api_key: str,
    verify_ssl: bool = True,
) -> dict[str, Any]:
    """Ruft aktuelle PV-Werte von der konfigurierten Hochschul-URL ab."""

    if not source_url:
        raise ValueError("Hier PV_DATA_URL eintragen")
    if not api_key:
        raise ValueError("Hier PV_API_KEY eintragen")

    response = requests.get(
        source_url,
        headers={"X-API-Key": api_key},
        timeout=20,
        verify=verify_ssl,
    )
    response.raise_for_status()
    return select_current_record(response.json())


def select_current_record(payload: Any) -> dict[str, Any]:
    """Wählt aus der API-Antwort den aktuellsten Datensatz aus."""

    if isinstance(payload, list):
        if not payload:
            raise ValueError("PV-Endpunkt hat eine leere Liste geliefert")
        return select_current_record(payload[-1])

    if isinstance(payload, dict):
        for key in ("data", "records", "values", "items"):
            nested = payload.get(key)
            if isinstance(nested, list) and nested:
                return select_current_record(nested)
        return payload

    raise ValueError("PV-Endpunkt muss ein JSON-Objekt oder eine Liste liefern")
