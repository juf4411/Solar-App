# Dashboard-Spezifikation

Das Dashboard soll im Endausbau PV-Daten einer Anlage anzeigen.

## Geplante KPIs

| KPI | Einheit | Beschreibung |
| --- | --- | --- |
| Aktuelle Leistung | W | Momentane PV-Leistung |
| Tagesenergie | kWh | Bisher erzeugte Energie des Tages |
| Mittelwert Leistung | W | Durchschnitt der gespeicherten Leistungswerte |
| Temperatur | C | Temperaturwert aus der PV-Datenquelle |
| Datenstatus | Text | Mock-up-Daten oder Echtdaten |

## Geplante Grafiken

| Grafik | Beschreibung |
| --- | --- |
| Leistungsverlauf | Liniendiagramm der Leistung ueber Zeit |
| Tagesertrag | Balken- oder Liniendiagramm fuer Energie |
| KPI-Karten | kompakte Werte fuer aktuelle Leistung, Mittelwert und Tagesenergie |

## Datenquelle

Die echte PV-Datenquelle wird spaeter ueber `PV_DATA_URL` konfiguriert. Bis dahin verwendet das Projekt Mock-up-Daten.
