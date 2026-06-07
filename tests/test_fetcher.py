from solar_app.data_fetcher.fetcher import fetch_current_pv_values


def test_fetcher_returns_mock_data_without_url():
    record = fetch_current_pv_values()

    assert record["plant_id"] == "pv-campus-demo"
    assert record["is_mock_data"] is True
