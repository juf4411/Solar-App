from solar_app.frontend.dashboard import create_app


def test_dashboard_page_loads(monkeypatch, tmp_path):
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path / "pv_values.json"))
    monkeypatch.setenv("PV_DATA_URL", "https://example.test/data")
    monkeypatch.setenv("PV_API_KEY", "test-key")
    monkeypatch.setattr(
        "solar_app.frontend.dashboard.fetch_current_pv_values",
        lambda source_url, api_key: {
            "timestamp": "2026-06-07T12:00:00Z",
            "production_power_w": 1000,
            "consumption_power_w": 1500,
            "daily_production_wh": 7000,
            "daily_consumption_wh": 9000,
        },
    )
    app = create_app()

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b"Solar-App Dashboard" in response.data
