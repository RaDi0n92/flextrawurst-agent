# welt/entity_kern.py

Migriert: 2026-07-06

**Was es tut**: Der "LLM-Kern" für die Wesen-Entitätenschicht (`denk_tick()`) —
jede Entität denkt alle 5 Minuten nach: baut Kontext (`build_kontext`), baut
einen Prompt, streamt die Antwort Token für Token live via PostgreSQL NOTIFY
(`entity_denkstream`-Tabelle, ~40-Zeichen-Puffer-Flushes) — das treibt das
Denkfenster/die Prozesskamera. Speichert Entscheidung + Gedanke in
`entity_thinking_log`.

**Wozu**: Kontinuierliches, beobachtbares "Innenleben" — nicht nur Ergebnis,
sondern der Denkprozess selbst wird live sichtbar.

**Migration**: Die manuelle SSE-artige Streaming-Schleife (`requests.post(..., stream=True)`
+ manuelles `json.loads` pro Zeile) wurde durch `hauhau_client.chat_stream()`
ersetzt — der liefert schon reinen Text pro Chunk, kein JSON-Parsing mehr nötig
im Aufrufer. Funktional identisch, weniger Code.

**Status**: `entity-kern.service` ist aktuell **deaktiviert** (Teil der
"Wesen-Einzug"-Bauphase, laut Bau-Reihenfolge gesperrt bis Daniel es freigibt) —
nur syntaxgeprüft, nicht gestartet, um nichts eigenständig zu aktivieren.

**Zusammenhang**: Wird auch direkt von `codewesen_lg_daemon.py` importiert
(`import entity_kern as ek`) — dessen eigene, fast identische Inline-Streaming-Logik
wurde parallel migriert und nutzt jetzt `ek.hauhau_client.chat_stream()`.
