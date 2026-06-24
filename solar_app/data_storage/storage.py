"""Speichert bereinigte PV-Messwerte als JSON."""

import json
from pathlib import Path
from typing import Any


def save_record(record: dict[str, Any], storage_path: str) -> None:
    """Hängt einen bereinigten Datensatz an eine JSON-Datei an."""

    path = Path(storage_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    records = load_records(storage_path)
    records.append(record)
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")


def load_records(storage_path: str) -> list[dict[str, Any]]:
    """Lädt alle gespeicherten PV-Messwerte aus der JSON-Datei."""

    path = Path(storage_path)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))
