"""Flask-Dashboard für die Anzeige der PV-Daten."""

import logging
import os
import threading
import time
from typing import Any

from flask import Flask, jsonify, render_template_string

from solar_app.calculations.calculations import calculate_dashboard_kpis
from solar_app.data_cleaning.cleaning import clean_pv_record
from solar_app.data_fetcher.fetcher import fetch_current_pv_values
from solar_app.data_storage.storage import load_records, save_record

LOGGER = logging.getLogger(__name__)
COLLECTOR_STARTED = False
COLLECTOR_LOCK = threading.Lock()
LAST_COLLECTION_ERROR: str | None = None

DASHBOARD_TEMPLATE = """
<!doctype html>
<html lang="de">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="{{ refresh_interval }}">
    <title>THI Solar Dashboard</title>
    <style>
      :root {
        --bg: #061f20;
        --panel: #0b3434;
        --panel-soft: #0f403f;
        --line: #24605d;
        --text: #f4fffd;
        --muted: #9cc7c1;
        --cyan: #35ded1;
        --yellow: #ffc533;
        --green: #42df8f;
        --red: #ff5f63;
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        min-height: 100vh;
        background:
          radial-gradient(circle at top right, rgba(53, 222, 209, 0.16), transparent 28rem),
          linear-gradient(135deg, #061f20 0%, #092928 55%, #071b1d 100%);
        color: var(--text);
        font-family: Arial, sans-serif;
      }

      main {
        width: min(1520px, calc(100vw - 48px));
        margin: auto;
        padding: 32px 0 42px;
      }

      .topbar {
        display: flex;
        justify-content: space-between;
        gap: 24px;
        align-items: end;
        margin-bottom: 22px;
      }

      h1,
      h2,
      h3,
      p {
        margin: 0;
      }

      h1 {
        font-size: 38px;
      }

      .subtitle,
      .muted {
        color: var(--muted);
      }

      .status {
        color: var(--muted);
        text-align: right;
      }

      .status-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        margin-right: 8px;
        border-radius: 999px;
        background: {{ "var(--red)" if last_error else "var(--green)" }};
        box-shadow: 0 0 14px currentColor;
      }

      .grid {
        display: grid;
        grid-template-columns: repeat(12, 1fr);
        gap: 16px;
      }

      .panel,
      .card {
        background: rgba(11, 52, 52, 0.92);
        border: 1px dashed rgba(80, 177, 169, 0.58);
        border-radius: 8px;
      }

      .panel {
        padding: 22px;
      }

      .hero {
        grid-column: span 4;
        min-height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        overflow: hidden;
        background:
          linear-gradient(rgba(6, 31, 32, 0.22), rgba(6, 31, 32, 0.82)),
          linear-gradient(135deg, #164644, #0a2b2c);
      }

      .hero h2 {
        font-size: 28px;
      }

      .flow {
        grid-column: span 4;
      }

      .flow-layout {
        display: grid;
        grid-template-columns: 150px 1fr;
        gap: 22px;
        align-items: center;
        margin-top: 24px;
      }

      .donut {
        width: 150px;
        aspect-ratio: 1;
        display: grid;
        place-items: center;
        border-radius: 50%;
        background:
          radial-gradient(circle, var(--panel) 0 48%, transparent 49%),
          conic-gradient(var(--cyan) calc(var(--value) * 1%), var(--yellow) 0);
      }

      .donut strong {
        font-size: 28px;
      }

      .legend {
        display: grid;
        gap: 14px;
      }

      .legend-row {
        display: grid;
        grid-template-columns: 12px 1fr auto;
        gap: 10px;
        align-items: center;
      }

      .bullet {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: var(--cyan);
      }

      .bullet.yellow {
        background: var(--yellow);
      }

      .bullet.green {
        background: var(--green);
      }

      .periods {
        grid-column: span 4;
      }

      .period-row {
        display: grid;
        grid-template-columns: 70px 1fr 1fr 80px;
        gap: 16px;
        align-items: center;
        padding: 16px 0;
        border-bottom: 1px solid rgba(80, 177, 169, 0.25);
      }

      .period-row:last-child {
        border-bottom: 0;
      }

      .bar {
        height: 6px;
        margin-top: 8px;
        border-radius: 999px;
        background: rgba(156, 199, 193, 0.14);
        overflow: hidden;
      }

      .bar span {
        display: block;
        width: min(calc(var(--value) * 1%), 100%);
        height: 100%;
        background: var(--cyan);
      }

      .bar.yellow span {
        background: var(--yellow);
      }

      .cards {
        grid-column: 1 / -1;
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 16px;
      }

      .card {
        padding: 18px;
      }

      .card span {
        color: var(--muted);
      }

      .card strong {
        display: block;
        margin-top: 10px;
        font-size: 28px;
      }

      .chart {
        grid-column: span 8;
      }

      .ratio-panel {
        grid-column: span 4;
      }

      .ratio-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-top: 24px;
      }

      .mini-donut {
        display: grid;
        gap: 10px;
        justify-items: center;
        text-align: center;
      }

      .mini-donut .circle {
        width: 104px;
        aspect-ratio: 1;
        display: grid;
        place-items: center;
        border-radius: 50%;
        background:
          radial-gradient(circle, var(--panel) 0 52%, transparent 53%),
          conic-gradient(var(--cyan) calc(var(--value) * 1%), rgba(156, 199, 193, 0.18) 0);
      }

      svg {
        width: 100%;
        min-height: 300px;
        margin-top: 18px;
        background: rgba(5, 27, 28, 0.45);
        border-radius: 8px;
      }

      .axis {
        stroke: rgba(156, 199, 193, 0.28);
      }

      .line-production {
        fill: none;
        stroke: var(--cyan);
        stroke-width: 4;
      }

      .line-consumption {
        fill: none;
        stroke: var(--yellow);
        stroke-width: 4;
      }

      .chart-legend {
        display: flex;
        gap: 18px;
        color: var(--muted);
      }

      .empty {
        min-height: 300px;
        display: grid;
        place-items: center;
        color: var(--muted);
        background: rgba(5, 27, 28, 0.45);
        border-radius: 8px;
      }

      .error {
        grid-column: 1 / -1;
        color: #ffd6d7;
        background: rgba(255, 95, 99, 0.12);
        border: 1px solid rgba(255, 95, 99, 0.35);
        border-radius: 8px;
        padding: 14px 18px;
      }

      @media (max-width: 1050px) {
        main {
          width: min(100vw - 28px, 760px);
          padding-top: 24px;
        }

        .topbar {
          display: grid;
          align-items: start;
        }

        .status {
          text-align: left;
        }

        .hero,
        .flow,
        .periods,
        .chart,
        .ratio-panel {
          grid-column: 1 / -1;
        }

        .cards {
          grid-template-columns: repeat(2, minmax(0, 1fr));
        }
      }

      @media (max-width: 640px) {
        h1 {
          font-size: 30px;
        }

        .cards,
        .ratio-grid {
          grid-template-columns: 1fr;
        }

        .period-row {
          grid-template-columns: 1fr;
        }

        .flow-layout {
          grid-template-columns: 1fr;
          justify-items: center;
        }
      }
    </style>
  </head>
  <body>
    <main>
      <header class="topbar">
        <div>
          <h1>THI Energy Management Dashboard</h1>
          <p class="subtitle">PV-Erzeugung und Energiekennzahlen im Überblick</p>
        </div>
        <p class="status">
          <span class="status-dot"></span>
          {{ "Live-Verbindung unterbrochen" if last_error else "Live-Verbindung aktiv" }}
          · {{ record_count }} Datensätze · Aktualisierung alle {{ refresh_interval }} Sekunden
        </p>
      </header>

      <section class="grid">
        {% if last_error %}
          <div class="error">
            Aktuelle Serverdaten konnten nicht geladen werden. Gespeicherte Werte bleiben sichtbar.
          </div>
        {% endif %}

        <article class="panel hero">
          <p class="muted">Campus-PV-Monitoring</p>
          <h2>Technische Hochschule Ingolstadt</h2>
        </article>

        <section class="panel flow">
          <h2>Aktueller Energiefluss</h2>
          <div class="flow-layout">
            <div class="donut" style="--value: {{ daily_ratio }}">
              <strong>{{ "%.1f"|format(daily_ratio) }}%</strong>
            </div>
            <div class="legend">
              <div class="legend-row">
                <span class="bullet"></span>
                <span>PV-Erzeugung</span>
                <strong>{{ "%.1f"|format(current_production_w / 1000) }} kW</strong>
              </div>
              <div class="legend-row">
                <span class="bullet yellow"></span>
                <span>Verbrauch</span>
                <strong>{{ "%.1f"|format(current_consumption_w / 1000) }} kW</strong>
              </div>
              <div class="legend-row">
                <span class="bullet green"></span>
                <span>Mittelwert</span>
                <strong>{{ "%.1f"|format(average_power_w / 1000) }} kW</strong>
              </div>
            </div>
          </div>
        </section>

        <section class="panel periods">
          <h2>Erzeugung und Verbrauch</h2>
          {% for row in period_rows %}
            <div class="period-row">
              <strong>{{ row.label }}</strong>
              <div>
                <span class="muted">Erzeugung</span>
                <strong>{{ "%.1f"|format(row.production_kwh) }} kWh</strong>
                <div class="bar" style="--value: {{ row.production_percent }}"><span></span></div>
              </div>
              <div>
                <span class="muted">Verbrauch</span>
                <strong>{{ "%.1f"|format(row.consumption_kwh) }} kWh</strong>
                <div class="bar yellow" style="--value: {{ row.consumption_percent }}">
                  <span></span>
                </div>
              </div>
              <strong class="cyan">{{ "%.1f"|format(row.ratio) }}%</strong>
            </div>
          {% endfor %}
        </section>

        <section class="cards">
          <article class="card">
            <span>Momentanerzeugung</span>
            <strong class="cyan">{{ "%.1f"|format(current_production_w) }} W</strong>
          </article>
          <article class="card">
            <span>Momentanverbrauch</span>
            <strong class="yellow">{{ "%.1f"|format(current_consumption_w) }} W</strong>
          </article>
          <article class="card">
            <span>Tageserzeugung</span>
            <strong>{{ "%.1f"|format(daily_production_wh / 1000) }} kWh</strong>
          </article>
          <article class="card">
            <span>Tagesverbrauch</span>
            <strong>{{ "%.1f"|format(daily_consumption_wh / 1000) }} kWh</strong>
          </article>
          <article class="card">
            <span>Monatserzeugung</span>
            <strong>{{ "%.1f"|format(monthly_production_wh / 1000) }} kWh</strong>
          </article>
          <article class="card">
            <span>Monatsverbrauch</span>
            <strong>{{ "%.1f"|format(monthly_consumption_wh / 1000) }} kWh</strong>
          </article>
          <article class="card">
            <span>Jahreserzeugung</span>
            <strong>{{ "%.1f"|format(yearly_production_wh / 1000) }} kWh</strong>
          </article>
          <article class="card">
            <span>Jahresverbrauch</span>
            <strong>{{ "%.1f"|format(yearly_consumption_wh / 1000) }} kWh</strong>
          </article>
        </section>

        <section class="panel chart">
          <h2>Tagesverlauf Erzeugung und Verbrauch</h2>
          <div class="chart-legend">
            <span>● Tageserzeugung Wh</span>
            <span>● Tagesverbrauch Wh</span>
          </div>
          {% if production_line and consumption_line %}
            <svg viewBox="0 0 760 300" role="img" aria-label="Zeitverlauf der Tageswerte">
              <line class="axis" x1="44" y1="252" x2="724" y2="252"></line>
              <line class="axis" x1="44" y1="36" x2="44" y2="252"></line>
              <polyline class="line-production" points="{{ production_line }}"></polyline>
              <polyline class="line-consumption" points="{{ consumption_line }}"></polyline>
              <text x="44" y="282" fill="#9cc7c1" font-size="14">{{ first_label }}</text>
              <text x="680" y="282" fill="#9cc7c1" font-size="14">{{ last_label }}</text>
            </svg>
          {% else %}
            <div class="empty">Noch zu wenige Messwerte für den Zeitverlauf vorhanden.</div>
          {% endif %}
        </section>

        <section class="panel ratio-panel">
          <h2>PV-Anteil am Gesamtverbrauch</h2>
          <div class="ratio-grid">
            {% for row in ratio_rows %}
              <div class="mini-donut">
                <div class="circle" style="--value: {{ row.value }}">
                  <strong>{{ "%.1f"|format(row.value) }}%</strong>
                </div>
                <span>{{ row.label }}</span>
              </div>
            {% endfor %}
          </div>
        </section>
      </section>
    </main>
  </body>
</html>
"""


def get_storage_path() -> str:
    """Gibt den konfigurierten Speicherpfad zurück."""

    return os.getenv("STORAGE_PATH", "data/pv_values.json")


def get_fetch_interval_seconds() -> int:
    """Liest das Abrufintervall aus der Umgebung."""

    return max(int(os.getenv("FETCH_INTERVAL_SECONDS", "10")), 1)


def ssl_verification_enabled() -> bool:
    """Liest, ob HTTPS-Zertifikate geprüft werden sollen."""

    return os.getenv("PV_VERIFY_SSL", "false").lower() in {"1", "true", "yes"}


def collect_current_record(storage_path: str) -> None:
    """Holt einen Messwert vom Server und speichert ihn lokal."""

    source_url = os.getenv("PV_DATA_URL") or ""
    api_key = os.getenv("PV_API_KEY", "")

    raw_record = fetch_current_pv_values(
        source_url,
        api_key,
        verify_ssl=ssl_verification_enabled(),
    )
    cleaned_record = clean_pv_record(raw_record)
    save_record(cleaned_record, storage_path)


def background_fetch_enabled() -> bool:
    """Prüft, ob der regelmäßige Hintergrundabruf aktiv sein soll."""

    return os.getenv("ENABLE_BACKGROUND_FETCH", "true").lower() in {"1", "true", "yes"}


def collect_pipeline() -> dict[str, Any]:
    """Erstellt die aktuellen Dashboard-Daten."""

    storage_path = get_storage_path()
    global LAST_COLLECTION_ERROR

    if not background_fetch_enabled():
        try:
            collect_current_record(storage_path)
            LAST_COLLECTION_ERROR = None
        except Exception as exc:
            LOGGER.warning("PV data collection failed: %s", exc)
            LAST_COLLECTION_ERROR = str(exc)

    kpis = calculate_dashboard_kpis(load_records(storage_path))
    kpis["last_error"] = LAST_COLLECTION_ERROR
    return kpis


def build_line(points: list[dict[str, Any]], key: str, maximum: float) -> str:
    """Erstellt eine SVG-Polyline aus Dashboard-Punkten."""

    if len(points) < 2:
        return ""

    width = 760
    height = 300
    padding = 44
    usable_width = width - padding * 2
    usable_height = height - padding * 2
    denominator = max(len(points) - 1, 1)

    coordinates = []
    for index, point in enumerate(points):
        x = padding + (usable_width / denominator) * index
        value = float(point.get(key, 0))
        y = height - padding - (value / maximum) * usable_height
        coordinates.append(f"{x:.1f},{y:.1f}")

    return " ".join(coordinates)


def build_period_rows(kpis: dict[str, Any]) -> list[dict[str, Any]]:
    """Bereitet Tages-, Monats- und Jahreswerte für die Oberfläche vor."""

    rows = [
        (
            "Tag",
            kpis["daily_production_wh"],
            kpis["daily_consumption_wh"],
            kpis["daily_pv_ratio_percent"],
        ),
        (
            "Monat",
            kpis["monthly_production_wh"],
            kpis["monthly_consumption_wh"],
            kpis["monthly_pv_ratio_percent"],
        ),
        (
            "Jahr",
            kpis["yearly_production_wh"],
            kpis["yearly_consumption_wh"],
            kpis["yearly_pv_ratio_percent"],
        ),
    ]
    maximum = max(
        (max(production, consumption) for _, production, consumption, _ in rows),
        default=1,
    )
    maximum = maximum or 1

    return [
        {
            "label": label,
            "production_kwh": production / 1000,
            "consumption_kwh": consumption / 1000,
            "production_percent": round(production / maximum * 100, 2),
            "consumption_percent": round(consumption / maximum * 100, 2),
            "ratio": ratio,
        }
        for label, production, consumption, ratio in rows
    ]


def build_view_model(kpis: dict[str, Any]) -> dict[str, Any]:
    """Ergänzt berechnete Werte für die HTML-Darstellung."""

    points = kpis.get("chart_points", [])
    maximum = max(
        (
            max(
                float(point.get("daily_production_wh", 0)),
                float(point.get("daily_consumption_wh", 0)),
            )
            for point in points
        ),
        default=0,
    )
    maximum = maximum or 1

    return {
        **kpis,
        "refresh_interval": get_fetch_interval_seconds(),
        "daily_ratio": kpis["daily_pv_ratio_percent"],
        "production_line": build_line(points, "daily_production_wh", maximum),
        "consumption_line": build_line(points, "daily_consumption_wh", maximum),
        "first_label": points[0]["label"] if points else "",
        "last_label": points[-1]["label"] if points else "",
        "period_rows": build_period_rows(kpis),
        "ratio_rows": [
            {"label": "Tag", "value": kpis["daily_pv_ratio_percent"]},
            {"label": "Monat", "value": kpis["monthly_pv_ratio_percent"]},
            {"label": "Jahr", "value": kpis["yearly_pv_ratio_percent"]},
        ],
    }


def background_collector() -> None:
    """Holt im Hintergrund regelmäßig neue PV-Daten."""

    storage_path = get_storage_path()
    interval = get_fetch_interval_seconds()
    global LAST_COLLECTION_ERROR

    while True:
        try:
            collect_current_record(storage_path)
            LAST_COLLECTION_ERROR = None
        except Exception as exc:
            LOGGER.warning("PV background collection failed: %s", exc)
            LAST_COLLECTION_ERROR = str(exc)
        time.sleep(interval)


def start_background_collector() -> None:
    """Startet den regelmäßigen Datenabruf einmal pro Prozess."""

    global COLLECTOR_STARTED

    if not background_fetch_enabled():
        return

    with COLLECTOR_LOCK:
        if COLLECTOR_STARTED:
            return
        thread = threading.Thread(target=background_collector, daemon=True)
        thread.start()
        COLLECTOR_STARTED = True


def create_app() -> Flask:
    """Erstellt die Flask-Anwendung für das Dashboard."""

    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)
    start_background_collector()

    @app.get("/")
    def dashboard():
        view_model = build_view_model(collect_pipeline())
        return render_template_string(DASHBOARD_TEMPLATE, **view_model)

    @app.get("/api/kpis")
    def api_kpis():
        return jsonify(collect_pipeline())

    return app
