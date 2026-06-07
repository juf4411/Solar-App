from solar_app.frontend.dashboard import create_app


def test_dashboard_page_loads(monkeypatch, tmp_path):
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path / "pv_values.json"))
    app = create_app()

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b"Solar-App Dashboard" in response.data
