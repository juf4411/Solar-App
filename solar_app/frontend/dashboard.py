"""Flask-Dashboard fuer die Anzeige der PV-Daten."""

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
    <title>Solar-App Dashboard</title>
    <style>
      body {
        margin: 0;
        background: #071b1d;
        color: #f4fffd;
        font-family: Arial, sans-serif;
      }
      main {
        padding: 40px;
      }
      .grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
      }
      .card {
        background: #0d292b;
        border: 1px solid #20484a;
        border-radius: 8px;
        padding: 20px;
      }
      strong {
        display: block;
        font-size: 28px;
        margin-top: 8px;
      }
    </style>
  </head>
  <body>
    <main>
      <h1>THI Energy Management Dashboard</h1>
      <p>PV-Erzeugung, Verbrauch und Eigenversorgung im Live-Monitoring</p>

      <section class="grid">
        <article class="card">
          <span>Momentanerzeugung</span>
          <strong>{{ "%.1f"|format(kpis.current_production_w) }} W</strong>
        </article>
        <article class="card">
          <span>Momentanverbrauch</span>
          <strong>{{ "%.1f"|format(kpis.current_consumption_w) }} W</strong>
        </article>
        <article class="card">
          <span>Tageserzeugung</span>
          <strong>{{ "%.1f"|format(kpis.daily_production_wh) }} Wh</strong>
        </article>
        <article class="card">
          <span>PV-Anteil heute</span>
          <strong>{{ "%.1f"|format(kpis.daily_pv_ratio_percent) }} %</strong>
        </article>
      </section>
    </main>
  </body>
</html>
"""


def get_storage_path() -> str:
    """Gibt den konfigurierten Speicherpfad zurueck."""

    return os.getenv("STORAGE_PATH", "data/pv_values.json")


def collect_pipeline() -> dict:
    """Fuehrt Abruf, Bereinigung, Speicherung und Berechnung einmal aus."""

    source_url = os.getenv("PV_DATA_URL", "")
    api_key = os.getenv("PV_API_KEY", "")
    verify_ssl = os.getenv("PV_VERIFY_SSL", "true").lower() != "false"

    raw_record = fetch_current_pv_values(source_url, api_key, verify_ssl=verify_ssl)
    cleaned_record = clean_pv_record(raw_record)
    save_record(cleaned_record, get_storage_path())
    return calculate_dashboard_kpis(load_records(get_storage_path()))


def create_app() -> Flask:
    """Erstellt die Flask-Anwendung fuer das Dashboard."""

    app = Flask(__name__)

    @app.get("/")
    def dashboard():
        kpis = collect_pipeline()
        return render_template_string(DASHBOARD_TEMPLATE, kpis=kpis)

    @app.get("/api/kpis")
    def api_kpis():
        return jsonify(collect_pipeline())

    return app
