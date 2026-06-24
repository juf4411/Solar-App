# Dashboard-Spezifikation

Das Dashboard zeigt PV-Daten der Hochschul-Anlage in einer Flask-Webanwendung. Die Daten werden über die konfigurierte URL abgerufen, bereinigt, gespeichert und anschließend für die Anzeige vorbereitet.

## Kennzahlen

- Momentanerzeugung und Momentanverbrauch
- Tageserzeugung und Tagesverbrauch
- Monatserzeugung und Monatsverbrauch
- Jahreserzeugung und Jahresverbrauch
- Verhältnis Verbrauch aus PV zu Gesamtverbrauch für Tag, Monat und Jahr
- Durchschnittliche PV-Leistung
- Anzahl gespeicherter Datensätze

## Grafiken

- Zeitverlauf der Tageserzeugung und des Tagesverbrauchs in einem Diagramm
- Donutdiagramme für den PV-Anteil am Gesamtverbrauch für Tag, Monat und Jahr
- Darstellung der wichtigsten Kennzahlen in KPI-Karten

## Datenquelle

Die Datenquelle wird über Umgebungsvariablen gesetzt.

```text
PV_DATA_URL=https://jupyterhub-wi.rz.fh-ingolstadt.de:8443/data
PV_API_KEY=hier_lokal_eintragen
FETCH_INTERVAL_SECONDS=10
```

Der API-Key wird nur lokal in der Datei `.env` eingetragen und nicht ins Repository geschrieben.
