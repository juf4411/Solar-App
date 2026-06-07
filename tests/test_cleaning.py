import pytest

from solar_app.data_cleaning.cleaning import clean_pv_record


def test_clean_pv_record_normalizes_values():
    record = clean_pv_record(
        {
            "timestamp": "2026-06-07T12:00:00Z",
            "plant_id": " pv-1 ",
            "power_w": "1000",
            "energy_today_kwh": "7.5",
            "temperature_c": "22.4",
        }
    )

    assert record["plant_id"] == "pv-1"
    assert record["power_w"] == 1000.0


def test_clean_pv_record_rejects_missing_fields():
    with pytest.raises(ValueError):
        clean_pv_record({"timestamp": "2026-06-07T12:00:00Z"})
