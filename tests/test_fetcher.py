import pytest

from solar_app.data_fetcher.fetcher import fetch_current_pv_values, select_current_record


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_fetcher_uses_url_and_api_key(monkeypatch):
    calls = {}

    def fake_get(url, headers, timeout, verify):
        calls["url"] = url
        calls["headers"] = headers
        calls["timeout"] = timeout
        calls["verify"] = verify
        return FakeResponse({"production_power_w": 1200})

    monkeypatch.setattr("solar_app.data_fetcher.fetcher.requests.get", fake_get)

    record = fetch_current_pv_values("https://example.test/data", "secret")

    assert calls["url"] == "https://example.test/data"
    assert calls["headers"] == {"X-API-Key": "secret"}
    assert calls["timeout"] == 20
    assert calls["verify"] is True
    assert record["production_power_w"] == 1200


def test_fetcher_can_disable_ssl_verification(monkeypatch):
    calls = {}

    def fake_get(url, headers, timeout, verify):
        calls["verify"] = verify
        return FakeResponse({"production_power_w": 1200})

    monkeypatch.setattr("solar_app.data_fetcher.fetcher.requests.get", fake_get)

    fetch_current_pv_values("https://example.test/data", "secret", verify_ssl=False)

    assert calls["verify"] is False


def test_fetcher_requires_api_key():
    with pytest.raises(ValueError):
        fetch_current_pv_values("https://example.test/data", "")


def test_select_current_record_uses_latest_list_entry():
    record = select_current_record({"data": [{"production_power_w": 1}, {"production_power_w": 2}]})

    assert record == {"production_power_w": 2}
