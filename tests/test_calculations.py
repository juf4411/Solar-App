from solar_app.calculations.calculations import (
    calculate_average_power,
    calculate_dashboard_kpis,
    calculate_integrated_energy,
    calculate_period_total,
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
                "timestamp": "2026-06-07T08:00:00Z",
                "production_power_w": 100.0,
                "consumption_power_w": 200.0,
                "daily_production_wh": 2500.0,
                "daily_consumption_wh": 5000.0,
            },
            {
                "timestamp": "2026-06-07T12:00:00Z",
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
    assert kpis["weekly_production_wh"] == 4000.0
    assert kpis["weekly_consumption_wh"] == 8000.0
    assert kpis["monthly_production_wh"] == 4000.0
    assert kpis["monthly_consumption_wh"] == 8000.0
    assert kpis["yearly_production_wh"] == 4000.0
    assert kpis["yearly_consumption_wh"] == 8000.0
    assert kpis["daily_pv_ratio_percent"] == 50.0
    assert kpis["weekly_pv_ratio_percent"] == 50.0
    assert kpis["weekly_grid_purchase_wh"] == 4000.0
    assert kpis["weekly_feed_in_wh"] == 0.0
    assert kpis["weekly_autarky_percent"] == 50.0
    assert kpis["monthly_pv_ratio_percent"] == 50.0
    assert kpis["yearly_pv_ratio_percent"] == 50.0
    assert len(kpis["chart_points"]) == 2


def test_calculate_period_total_sums_daily_max_values():
    records = [
        {
            "timestamp": "2026-06-06T10:00:00Z",
            "daily_production_wh": 1000.0,
        },
        {
            "timestamp": "2026-06-06T15:00:00Z",
            "daily_production_wh": 2500.0,
        },
        {
            "timestamp": "2026-06-07T12:00:00Z",
            "daily_production_wh": 4000.0,
        },
    ]

    assert calculate_period_total(records, "daily_production_wh", "day") == 4000.0
    assert calculate_period_total(records, "daily_production_wh", "week") == 6500.0
    assert calculate_period_total(records, "daily_production_wh", "month") == 6500.0
    assert calculate_period_total(records, "daily_production_wh", "year") == 6500.0


def test_calculate_integrated_energy_from_power_values():
    records = [
        {
            "timestamp": "2026-06-07T12:00:00Z",
            "production_power_w": 100.0,
        },
        {
            "timestamp": "2026-06-07T12:01:00Z",
            "production_power_w": 300.0,
        },
    ]

    assert calculate_integrated_energy(records, "production_power_w", "day") == 3.33


def test_dashboard_kpis_estimate_energy_when_counters_are_missing():
    kpis = calculate_dashboard_kpis(
        [
            {
                "timestamp": "2026-06-07T12:00:00Z",
                "production_power_w": 100.0,
                "consumption_power_w": 200.0,
                "daily_production_wh": 0.0,
                "daily_consumption_wh": 0.0,
            },
            {
                "timestamp": "2026-06-07T12:01:00Z",
                "production_power_w": 300.0,
                "consumption_power_w": 400.0,
                "daily_production_wh": 0.0,
                "daily_consumption_wh": 0.0,
            },
        ]
    )

    assert kpis["daily_production_wh"] == 3.33
    assert kpis["daily_consumption_wh"] == 5.0
    assert kpis["daily_pv_ratio_percent"] == 66.6
