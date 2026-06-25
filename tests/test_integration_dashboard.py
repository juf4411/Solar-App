from solar_app.frontend.dashboard import create_app


def fake_pv_record(source_url, api_key, verify_ssl=True):
    return {
        "timestamp": "2026-06-07T12:00:00Z",
        "production_power_w": 1000,
        "consumption_power_w": 1500,
        "daily_production_wh": 7000,
        "daily_consumption_wh": 9000,
    }


def test_dashboard_page_loads(monkeypatch, tmp_path):
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path / "pv_values.json"))
    monkeypatch.setenv("PV_DATA_URL", "https://example.test/data")
    monkeypatch.setenv("PV_API_KEY", "test-key")
    monkeypatch.setenv("ENABLE_BACKGROUND_FETCH", "false")
    monkeypatch.setenv("PV_VERIFY_SSL", "false")
    monkeypatch.setattr(
        "solar_app.frontend.dashboard.fetch_current_pv_values",
        fake_pv_record,
    )

    app = create_app()
    response = app.test_client().get("/")

    assert response.status_code == 200
    assert "THI Energy Management Dashboard" in response.text
    assert "Direkt auslesbare Metriken" in response.text
    assert "Kumulierte Metriken" in response.text
    assert 'data-view="direct"' in response.text
    assert 'data-view="cumulative"' in response.text
    assert "Tagesverlauf Erzeugung und Verbrauch" in response.text
    assert "Monatserzeugung" in response.text
    assert "Jahresverbrauch" in response.text


def test_kpi_api_returns_json(monkeypatch, tmp_path):
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path / "pv_values.json"))
    monkeypatch.setenv("PV_DATA_URL", "https://example.test/data")
    monkeypatch.setenv("PV_API_KEY", "test-key")
    monkeypatch.setenv("ENABLE_BACKGROUND_FETCH", "false")
    monkeypatch.setenv("PV_VERIFY_SSL", "false")
    monkeypatch.setattr(
        "solar_app.frontend.dashboard.fetch_current_pv_values",
        fake_pv_record,
    )

    app = create_app()
    response = app.test_client().get("/api/kpis")

    assert response.status_code == 200
    assert response.is_json
    assert response.json["monthly_pv_ratio_percent"] > 0
