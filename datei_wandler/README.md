# Datei-Wandler

Kleiner Werkraum-Webservice fuer gemischte Datei-Exporte.

## Funktionen

- VPS-Pfade eintragen, eine Datei pro Zeile.
- Mehrere Dateien gleichzeitig hochladen.
- Ausgabe als Offline-HTML, Markdown oder beides als ZIP.
- HTML-Dateien wahlweise als Quelltext, als extrahierter Markdown oder beides behandeln.
- Inhalte werden escaped und nicht ausgefuehrt.
- Offline-HTML bekommt eine Suche, Verschiebe-Buttons und einen Download der aktuellen Reihenfolge.
- Markdown-Export baut ein Verzeichnis und erkennt einfache Verweise zu anderen ausgewählten Dateien.

## Start

```bash
cd /root/werkraum
/root/werkraum/venv/bin/python3 -m uvicorn datei_wandler.app:app --host 0.0.0.0 --port 8877
```

Dann im Browser:

```text
http://SERVER:8877/
```

Produktiver Werkraum-Zugang:

```text
https://217.154.14.29:8449/
```

Dieser Zugang laeuft ueber nginx mit Werkraum-Basic-Auth. Der App-Prozess selbst soll lokal auf `127.0.0.1:8878` laufen.

## Grenzen

Erlaubte Pfad-Wurzeln:

- `/root/werkraum`
- `/root/visionen`

Blockiert:

- `.env`
- private Keys und Zertifikate
- lokale Datenbanken wie `.sqlite` / `.db`
- Binaerdateien
- Dateien ueber 2 MB
