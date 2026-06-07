"""Minimal Flask dashboard skeleton."""

import os

from flask import Flask, jsonify, render_template_string

from solar_app.calculations.calculations import calculate_dashboard_kpis
from solar_app.data_cleaning.cleaning import clean_pv_record
from solar_app.data_fetcher.fetcher import fetch_current_pv_values
from solar_app.data_storage.storage import load_records, save_record

DASHBOARD_TEMPLATE = """
<!doctype html>
<html lang="de">
  <head>
    <meta charset="utf-8">
    <title>Solar-App</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 40px; background: #eef3f1; color: #1e2a2f; }
      main { max-width: 900px; margin: auto; }
      .cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
      .card { background: white; padding: 20px; border-radius: 8px; border: 1px solid #dbe5e1; }
      strong { display: block; font-size: 28px; margin-top: 8px; }
    </style>
  </head>
  <body>
    <main>
      <h1>Solar-App Dashboard</h1>
      <p>
        Grundgeruest mit Mock-up-Daten.
        Die echte Dashboard-Gestaltung wird im Projektverlauf ergaenzt.
      </p>
      <section class="cards">
        <article class="card"><span>Aktuelle Leistung</span><strong>{{ power }} W</strong></article>
        <article class="card"><span>Mittelwert</span><strong>{{ average }} W</strong></article>
        <article class="card"><span>Energie heute</span><strong>{{ energy }} kWh</strong></article>
      </section>
    </main>
  </body>
</html>
"""


def collect_pipeline() -> dict:
    """Run the planned fetch-clean-store-calculate pipeline once."""

    source_url = os.getenv("PV_DATA_URL") or None
    storage_path = os.getenv("STORAGE_PATH", "data/pv_values.json")
    raw_record = fetch_current_pv_values(source_url)
    cleaned_record = clean_pv_record(raw_record)
    save_record(cleaned_record, storage_path)
    return calculate_dashboard_kpis(load_records(storage_path))


def create_app() -> Flask:
    """Create the Flask application."""

    app = Flask(__name__)

    @app.get("/")
    def dashboard():
        kpis = collect_pipeline()
        latest = kpis["latest"] or {}
        return render_template_string(
            DASHBOARD_TEMPLATE,
            power=latest.get("power_w", 0),
            average=kpis["average_power_w"],
            energy=kpis["energy_today_kwh"],
        )

    @app.get("/api/kpis")
    def api_kpis():
        return jsonify(collect_pipeline())

    return app
