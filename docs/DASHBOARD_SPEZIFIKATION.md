# Dashboard-Spezifikation

Das Dashboard zeigt PV-Daten der Hochschul-Anlage in einer Flask-Webanwendung.

## Kennzahlen

- Momentanerzeugung
- Momentanverbrauch
- Tageserzeugung
- Tagesverbrauch
- PV-Anteil am Tagesverbrauch
- Durchschnittliche PV-Leistung

## Grafiken

- Zeitverlauf von Erzeugung und Verbrauch
- Darstellung des PV-Anteils

## Datenquelle

Die Datenquelle wird ueber Umgebungsvariablen gesetzt.

```text
PV_DATA_URL=https://jupyterhub-wi.rz.fh-ingolstadt.de:8443/data
PV_API_KEY=d1e88a3131ade56eac79c0f4ec84969a8759f99b67c7cb5bdd28d75752c752a6
```
