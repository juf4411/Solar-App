"""Simple JSON storage stub for cleaned PV records."""

import json
from pathlib import Path
from typing import Any


def save_record(record: dict[str, Any], storage_path: str) -> None:
    """Append one record to a JSON file.

    TODO: Replace this with SQLite/PostgreSQL if the project needs real persistence.
    """

    path = Path(storage_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    records = load_records(storage_path)
    records.append(record)
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")


def load_records(storage_path: str) -> list[dict[str, Any]]:
    """Load all records from JSON storage."""

    path = Path(storage_path)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))
