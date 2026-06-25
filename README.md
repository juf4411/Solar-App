# Solar-App

PV-Dashboard-Projekt für Solardaten der Hochschule.

Ziel des Projekts ist eine App, die PV-Daten aus einer URL abruft, bereinigt, speichert, berechnet und in einem Dashboard darstellt. Der Server kann die Daten regelmäßig abrufen, solange die Anwendung läuft.

## Struktur

```text
solar_app/
  backend/          Server-Startpunkt
  data_fetcher/     Abruf der PV-Daten aus der Hochschul-URL
  data_cleaning/    Bereinigung und Validierung der Rohdaten
  data_storage/     Speicherung der Daten
  calculations/     KPIs und Kennzahlen
  frontend/         Dashboard mit Flask
tests/              Unit- und Integrationtests
docs/               Spezifikation, Mockup, Aufgabenverteilung
```

## Konfiguration

Die Datei `.env` muss lokal vorhanden sein und die Datenquelle enthalten:

```text
PV_DATA_URL=https://jupyterhub-wi.rz.fh-ingolstadt.de:8443/data
PV_API_KEY=hier_lokal_eintragen
FETCH_INTERVAL_SECONDS=10
```

Der API-Key bleibt nur lokal in `.env` und wird nicht ins Repository geschrieben.

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
docker compose --env-file .env up --build
```

Dashboard:

```text
http://localhost:5000
```

## Dokumentation

- `docs/DASHBOARD_SPEZIFIKATION.md`
- `docs/AUFGABENVERTEILUNG.md`
- `docs/dashboard-mockup.svg`

## Mitarbeit

Änderungen werden über Pull Requests eingebracht. Die wichtigsten Regeln stehen in `CONTRIBUTING.md`.
