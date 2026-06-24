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
    <title>THI Solar Dashboard</title>
    <style>
      body {
        margin: 0;
        background: #071b1d;
        color: #f4fffd;
        font-family: Arial, sans-serif;
      }

      main {
        max-width: 1180px;
        margin: auto;
        padding: 40px;
      }

      h1 {
        margin: 0;
        font-size: 36px;
      }

      p {
        color: #91bbb5;
      }

      .grid {
        display: grid;
        grid-template-columns: repeat(12, 1fr);
        gap: 16px;
        margin-top: 28px;
      }

      .panel {
        background: #0d292b;
        border: 1px solid #20484a;
        border-radius: 8px;
        padding: 24px;
      }

      .hero {
        grid-column: span 6;
        min-height: 260px;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        background: linear-gradient(135deg, #0d292b, #17453f);
      }

      .cards {
        grid-column: span 6;
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
      }

      .card {
        background: #123336;
        border: 1px solid #20484a;
        border-radius: 8px;
        padding: 20px;
      }

      .card span {
        color: #91bbb5;
      }

      .card strong {
        display: block;
        margin-top: 10px;
        font-size: 30px;
      }

      .cyan {
        color: #3fe0d0;
      }

      .yellow {
        color: #ffca41;
      }

      .chart {
        grid-column: 1 / -1;
      }

      .chart-box {
        min-height: 210px;
        display: grid;
        place-items: center;
        background: #092426;
        border: 1px solid #20484a;
        border-radius: 8px;
        color: #91bbb5;
      }

      @media (max-width: 900px) {
        .hero,
        .cards,
        .chart {
          grid-column: 1 / -1;
        }
      }
    </style>
  </head>
  <body>
    <main>
      <h1>THI Energy Management Dashboard</h1>
      <p>PV-Erzeugung und Energiekennzahlen im Ueberblick.</p>

      <section class="grid">
        <article class="panel hero">
          <h2>Technische Hochschule Ingolstadt</h2>
          <p>Campus-PV-Monitoring</p>
        </article>

        <section class="cards">
          <article class="card">
            <span>Aktuelle Leistung</span>
            <strong class="cyan">{{ "%.1f"|format(power) }} W</strong>
          </article>
          <article class="card">
            <span>Mittelwert</span>
            <strong>{{ "%.1f"|format(average) }} W</strong>
          </article>
          <article class="card">
            <span>Energie heute</span>
            <strong class="yellow">{{ "%.1f"|format(energy) }} kWh</strong>
          </article>
          <article class="card">
            <span>Datensaetze</span>
            <strong>{{ record_count }}</strong>
          </article>
        </section>

        <section class="panel chart">
          <h2>Leistungsverlauf</h2>
          <div class="chart-box">
            PV-Erzeugung und Verbrauch werden hier im Verlauf dargestellt.
          </div>
        </section>
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

    source_url = os.getenv("PV_DATA_URL") or None
    storage_path = get_storage_path()

    raw_record = fetch_current_pv_values(source_url)
    cleaned_record = clean_pv_record(raw_record)
    save_record(cleaned_record, storage_path)

    return calculate_dashboard_kpis(load_records(storage_path))


def create_app() -> Flask:
    """Erstellt die Flask-Anwendung fuer das Dashboard."""

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
            record_count=kpis["record_count"],
        )

    @app.get("/api/kpis")
    def api_kpis():
        return jsonify(collect_pipeline())

    return app
