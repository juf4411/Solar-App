from solar_app.frontend.dashboard import create_app


def test_dashboard_page_loads(monkeypatch, tmp_path):
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path / "pv_values.json"))

    app = create_app()
    response = app.test_client().get("/")

    assert response.status_code == 200
    assert "THI Energy Management Dashboard" in response.text
    assert "Leistungsverlauf" in response.text


def test_kpi_api_returns_json(monkeypatch, tmp_path):
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path / "pv_values.json"))

    app = create_app()
    response = app.test_client().get("/api/kpis")

    assert response.status_code == 200
    assert response.is_json
