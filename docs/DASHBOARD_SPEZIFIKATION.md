# Dashboard-Spezifikation

Das Dashboard zeigt PV-Daten der Hochschul-Anlage in einer Flask-Webanwendung.

## Kennzahlen

- Aktuelle PV-Leistung
- Durchschnittliche PV-Leistung
- Tagesenergie
- Anzahl gespeicherter Datensaetze

## Grafiken

- Bereich fuer den Leistungsverlauf von Erzeugung und Verbrauch
- Darstellung der wichtigsten Kennzahlen in KPI-Karten

## Datenquelle

Die Datenquelle wird ueber Umgebungsvariablen gesetzt.

```text
PV_DATA_URL=https://jupyterhub-wi.rz.fh-ingolstadt.de:8443/data
PV_API_KEY=hier_lokal_eintragen
Der API-Key wird nur lokal in der Datei .env eingetragen und nicht ins Repository geschrieben.

``
