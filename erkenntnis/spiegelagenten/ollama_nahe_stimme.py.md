---
## Archiv-Eintrag — Datei gelöscht 2026-04-18

Originaldatei: `/root/werkraum/agent/dak_gord_system/stimmen/ollama_nahe_stimme.py`
Status: **ENTFERNT** — gesamtes `stimmen/`-Verzeichnis gelöscht, da nie importiert.

## Was ich darin erkannte (vor Löschung)

Ein Kommunikations-Adapter zwischen Ollama-API und Sprach-Output. Der Name "OllamaNaheStimme" verknüpfte Ziel (Sprach-Output) mit Quelle (API), steuerte aber nur Textfluss, keine Akustik. Die Abhängigkeit von Umgebungsvariablen erhöhte Flexibilität auf Kosten von Fragilität.

## Was die Löschung bedeutet

Die Stimme als Konzept (wie spricht das System?) ist weiterhin relevant — sie liegt jetzt direkt in `ollama_chat.py` und dem Systemtext von `gespraechsgraf.py`. Die separate Datei war eine Abstraktionsschicht ohne tatsächliche Funktion.

## Offene Frage

Die Idee einer eigenen "Stimme" für das System — eine konsistente Tonalität jenseits des Systemtexts — ist noch nicht realisiert. Das wäre kein Kommunikations-Adapter, sondern ein Stil-Protokoll.
