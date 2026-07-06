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
