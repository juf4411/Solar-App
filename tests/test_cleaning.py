import pytest

from solar_app.data_cleaning.cleaning import clean_pv_record


def test_clean_pv_record_normalizes_legacy_values():
    record = clean_pv_record(
        {
            "timestamp": "2026-06-07T12:00:00Z",
            "plant_id": " pv-1 ",
            "power_w": "1000",
            "daily_production_wh": "7500",
            "daily_consumption_wh": "9000",
        }
    )

    assert record["plant_id"] == "pv-1"
    assert record["production_power_w"] == 1000.0
    assert record["consumption_power_w"] == 0.0
    assert record["daily_production_wh"] == 7500.0
    assert record["daily_consumption_wh"] == 9000.0


def test_clean_pv_record_normalizes_thi_payload():
    record = clean_pv_record(
        {
            "collected_at": "2026-06-07T12:00:00Z",
            "data": [
                {"type": "generation", "value": "1200"},
                {"type": "consumption", "value": "1800"},
            ],
        }
    )

    assert record["plant_id"] == "pv-system"
    assert record["production_power_w"] == 1200.0
    assert record["consumption_power_w"] == 1800.0


def test_clean_pv_record_rejects_invalid_numeric_value():
    with pytest.raises(ValueError):
        clean_pv_record(
            {
                "timestamp": "2026-06-07T12:00:00Z",
                "production_power_w": "keine-zahl",
            }
        )
