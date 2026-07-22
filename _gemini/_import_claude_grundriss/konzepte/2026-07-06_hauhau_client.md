# hauhau_client.py — Zentraler LLM-Client

Migriert: 2026-07-06

Das gemeinsame Python-Modul, das ALLE gemma4/Ollama-Aufrufe im System ersetzt.
Liegt unter `/root/werkraum/hauhau_client.py`, wird von ~40 Skripten importiert.

**Was es tut**: Kapselt HTTP-Aufrufe an `llama-server` (Port 11435, OpenAI-kompatibles
Format) hinter vier einfachen Funktionen:
- `chat(prompt_oder_messages, ...)` — synchron, nicht-streamend, gibt Text zurück
- `chat_stream(...)` — synchron, Generator, liefert Text-Chunks
- `achat(...)` / `achat_stream(...)` — dieselben zwei, aber async (für FastAPI-Endpunkte)
- `chat_raw(...)` — gibt die volle Response zurück, für Tool-Calling (braucht mehr als nur `content`)

**Wozu**: Vorher hatte praktisch jede Datei ihren eigenen `OLLAMA_URL`-Boilerplate,
manche mit `httpx`, manche `requests`, manche `urllib.request` — 40 verschiedene
Kopien mit potenziell unterschiedlichen Bugs. Jetzt gibt es eine getestete Stelle.

**Warum llama-server statt Ollama**: Ollama hat einen bestätigten Bug beim Laden
von selbst-importierten GGUF+mmproj-Kombinationen für die `qwen35moe`-Architektur
(genau unser Modell) — `unknown model architecture`. llama-server läuft direkt,
ohne dieses Problem, dazu kein Reload-Overhead (Ollama entlädt nach Inaktivität).

**Wichtige Details**:
- `think=False` per Default (steuert Thinking via `chat_template_kwargs.enable_thinking`,
  funktioniert pro Request, kein Server-Neustart nötig)
- `images=[...]` Parameter für Vision — konvertiert rohe Base64-Strings intern ins
  OpenAI `image_url`-Content-Part-Format
- Alle bisherigen Locking-Mechanismen (`fcntl`-Locks auf `/tmp/ollama_locks/slot_0.lock`,
  `CHAT_AKTIV_FLAG`-Warteschleifen) blieben unverändert — die regeln weiterhin
  wer zuerst dran ist, nur der eigentliche HTTP-Call dahinter wurde ausgetauscht.

**Zusammenhang**: Läuft gegen `llama-hauhaucs.service` (systemd), das
Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive in Q6_K_P-Quantisierung dauerhaft
geladen hält, mit `--mlock` (verhindert Verdrängung aus dem RAM unter Last) und
`AllowedCPUs=0-9` (Kernisolierung gegen Konkurrenz mit Ollama/anderen Diensten).

---

## Nachtrag 2026-07-06 (später) — id_slot-Priorisierung + Trace-Log

**`_default_id_slot()`**: Hintergrund-/Daemon-Aufrufe (Wesen-Ticks, `lg_daemon`,
GENI-Hintergrundverarbeitung, Phase-2-Tools) bekommen automatisch Slot 1 oder 2
(`1 + os.getpid() % 2`), wenn kein `id_slot` explizit übergeben wird — kein Code
an diesen ~35 Aufrufstellen geändert, der sichere Default greift automatisch.
Slot 0 bleibt dadurch für Live-Chats reserviert, die es explizit anfordern
(`id_slot=0`, gesetzt in `codewesen_chat.py`, `geni/dialog.py`, `zensi/server.py`).
Grund: bei echter Gleichzeitigkeit landete Chat vorher in derselben FIFO-Warteschlange
wie Automatikbetrieb — Antwortzeiten schwankten zwischen 1,8s und 253s im Volllasttest.
`id_slot` ist ein llama.cpp-Request-Feld, live verifiziert (eine Anfrage mit
explizitem `id_slot=1` wartete nachweislich auf genau diesen Slot statt auf einen
früher freien zu wechseln).

**`trace_prioritaet(quelle, zeichen)`**: Nach zwei Chat-Hängern (2026-07-06), die
sich trotz gründlicher Recherche (alle Chat-Logs, alle Dateizeiten) keiner Quelle
zuordnen ließen, schreibt jede Slot-0-Anfrage jetzt VOR dem eigentlichen LLM-Call
einen Trace-Eintrag nach `_shared/chat_prioritaet_trace.jsonl` (Quelle wie
`codewesen_chat:namelessAI_1234`, Zeichenlänge, PID) — getrennt von den schweren
Chat-Verlaufsdateien, damit ein künftiger Hänger sich sofort zuordnen lässt.
