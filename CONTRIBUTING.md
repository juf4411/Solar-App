# Mitarbeit am Projekt

Änderungen am Projekt werden über Pull Requests eingebracht.

## Ablauf

1. Eigenen Branch für die Aufgabe erstellen.
2. Änderung lokal umsetzen.
3. Tests und Formatierung prüfen.
4. Branch auf GitHub hochladen.
5. Pull Request gegen `main` erstellen.
6. Merge erfolgt erst nach Prüfung durch die Projektverantwortlichen.

## Prüfbefehle

```powershell
py -m pytest
py -m ruff check .
py -m ruff format --check .
```

## Hinweise

- Zugangsdaten bleiben lokal in `.env`.
- Keine direkten Änderungen auf `main`.
- Keine Force Pushes auf geteilte Branches.
- Das zurückgehaltene Feature wird in einem eigenen Branch entwickelt.
