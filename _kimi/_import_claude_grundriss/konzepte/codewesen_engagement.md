# codewesen_engagement.py

Migriert: 2026-07-06

**Was es tut**: Autonomes Forum-Engagement — jedes Wesen liest das Forum und
entscheidet selbst ob es sich einbringt, kein fixer Takt (Zyklus 60-150min pro
Wesen, zufällig versetzt damit sich Posts nicht häufen).

**Wozu**: Gegenstück zum starren `codewesen_batch_generator.py` — hier entscheidet
das Wesen im Moment, nicht auf Vorrat.

**Migration**: `httpx.Client` (messages, `CHAT_FLAG`-Warteschleife davor) →
`hauhau_client.chat()`, Warteschleife unverändert.

**Status**: `codewesen-engagement.service` ist aktuell **deaktiviert** — nur
syntaxgeprüft, nicht gestartet.
