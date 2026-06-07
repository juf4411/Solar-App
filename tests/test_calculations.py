from solar_app.calculations.calculations import calculate_average_power, calculate_dashboard_kpis


def test_calculate_average_power():
    assert calculate_average_power([{"power_w": 100.0}, {"power_w": 300.0}]) == 200.0


def test_calculate_dashboard_kpis():
    kpis = calculate_dashboard_kpis(
        [{"power_w": 100.0, "energy_today_kwh": 2.5}, {"power_w": 300.0, "energy_today_kwh": 4.0}]
    )

    assert kpis["record_count"] == 2
    assert kpis["average_power_w"] == 200.0
    assert kpis["energy_today_kwh"] == 4.0
