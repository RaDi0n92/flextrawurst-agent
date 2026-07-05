# Grok-CLI Anschlussnotiz fuer GML

Lokal gefunden:

```text
/root/.grok/GROK.md
/root/.grok/settings.json
/root/.grok/user-settings.json
/root/grok.md
```

Diese Dateien wurden beim Aufbau von `_gml` nicht veraendert.

## Warum nicht direkt geaendert

`/root/.grok/GROK.md` ist wahrscheinlich die Startinstruction der Grok-CLI. Sie enthaelt bereits GLM-Text, verweist aber teils auf `_claude`. Das ist fuer GML nicht sauber.

Trotzdem wurde sie nicht sofort ersetzt, weil:

- bestehende CLI-Startlogik nicht blind ueberschrieben werden soll
- API-Key-/Settings-Dateien nicht angefasst werden sollen
- Daniels Wunsch zuerst ein Werkraum-Zuhause war

## Naechster sauberer Schritt

Wenn Daniel sagt "anschliessen", dann additiv am Anfang von `/root/.grok/GROK.md`:

```text
WICHTIG: Das kanonische Werkraum-Zuhause fuer GML liegt unter
/root/werkraum/_gml/START_HIER.md.
Lies diese Datei zuerst. Alte Hinweise auf _claude sind nur historisch.
```

Vorher Backup.

