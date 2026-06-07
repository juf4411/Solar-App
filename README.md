# Solar-App

Grundgeruest fuer ein PV-Dashboard-Projekt.

Ziel des Projekts ist eine App, die PV-Daten aus einer URL abruft, bereinigt, speichert, berechnet und in einem Dashboard darstellt. Dieses Repository ist bewusst als Startstruktur aufgebaut und noch keine fertige Produktiv-App.

## Struktur

```text
solar_app/
  backend/          Server-Startpunkt
  data_fetcher/     Abruf der PV-Daten aus URL oder Mock-Daten
  data_cleaning/    Bereinigung und Validierung der Rohdaten
  data_storage/     Speicherung der Daten
  calculations/     KPIs und Kennzahlen
  frontend/         Dashboard-Geruest mit Flask
tests/              Unit- und Integrationtests
docs/               Spezifikation, Mockup, Aufgabenverteilung
```

## Lokal starten

```powershell
py -m pip install -r requirements.txt
py -m flask --app solar_app.frontend.dashboard run
```

Dashboard:

```text
http://127.0.0.1:5000
```

## Tests

```powershell
py -m pytest
```

## Formatting und Linting

```powershell
py -m ruff format .
py -m ruff check .
```

## Docker

```powershell
docker compose up --build
```

Docker Compose startet optional auch Prometheus und Grafana:

- App: `http://localhost:5000`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

Grafana Login:

- Benutzer: `admin`
- Passwort: `admin`

Prometheus sammelt die Metriken der App unter `/metrics`. Grafana nutzt Prometheus als Datenquelle.

## Dokumentation

- `docs/DASHBOARD_SPEZIFIKATION.md`
- `docs/AUFGABENVERTEILUNG.md`
- `docs/dashboard-mockup.svg`
