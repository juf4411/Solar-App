from solar_app.calculations.calculations import (
    calculate_average_power,
    calculate_dashboard_kpis,
    calculate_pv_ratio,
)


def test_calculate_average_power():
    assert (
        calculate_average_power(
            [
                {"production_power_w": 100.0},
                {"production_power_w": 300.0},
            ]
        )
        == 200.0
    )


def test_calculate_pv_ratio():
    assert calculate_pv_ratio(50.0, 100.0) == 50.0
    assert calculate_pv_ratio(150.0, 100.0) == 100.0
    assert calculate_pv_ratio(50.0, 0.0) == 0.0


def test_calculate_dashboard_kpis():
    kpis = calculate_dashboard_kpis(
        [
            {
                "production_power_w": 100.0,
                "consumption_power_w": 200.0,
                "daily_production_wh": 2500.0,
                "daily_consumption_wh": 5000.0,
            },
            {
                "production_power_w": 300.0,
                "consumption_power_w": 400.0,
                "daily_production_wh": 4000.0,
                "daily_consumption_wh": 8000.0,
            },
        ]
    )

    assert kpis["record_count"] == 2
    assert kpis["average_power_w"] == 200.0
    assert kpis["current_production_w"] == 300.0
    assert kpis["current_consumption_w"] == 400.0
    assert kpis["daily_production_wh"] == 4000.0
    assert kpis["daily_consumption_wh"] == 8000.0
    assert kpis["daily_pv_ratio_percent"] == 50.0
