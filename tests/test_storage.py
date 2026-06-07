from solar_app.data_storage.storage import load_records, save_record


def test_save_and_load_records(tmp_path):
    storage_path = tmp_path / "records.json"
    record = {"power_w": 1000.0}

    save_record(record, str(storage_path))

    assert load_records(str(storage_path)) == [record]
