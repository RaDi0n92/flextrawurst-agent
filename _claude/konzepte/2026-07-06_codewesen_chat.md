# codewesen_chat.py

Migriert: 2026-07-06

**Was es tut**: FastAPI-Server auf Port 8002 — Direktchat-UI mit den 6 Codewesen.
`/chat/<name>` zeigt eine Chatoberfläche, `/api/chat/{name}` streamt die Antwort
Token für Token per Server-Sent-Events.

**Wozu**: Das ist Daniels direkter 1:1-Chat-Zugang zu jedem einzelnen Codewesen —
nutzt das Gedächtnis (eigene Forum-Posts) als Kontext, speichert den Verlauf
dauerhaft (`chat_verlauf.jsonl`), und schreibt nach jedem Gespräch eine stille
Selbstreflexion (via `codewesen_reflexion.py`).

**Migration — die komplexeste bisher**:
- `stream_ollama()` (async, Streaming, Vision via `bilder`) → `hauhau_client.achat_stream()`
- Ein zweiter, nicht-streamender Aufruf (`analysiere_chat_verlauf`, Brainstorming-
  Auswertung nach dem Gespräch) → `hauhau_client.chat()`
- `_ollama_fuer_chat_freiraumen()` entfernt (killte fremde Prozesse, wartete auf
  Ollamas `/api/ps` — beides nur nötig weil Ollama Modelle be-/entlädt; llama-server
  ist permanent geladen, das Problem existiert nicht mehr). Der `CHAT_AKTIV_FLAG`-Touch
  blieb aber bestehen — andere Wesen-Prozesse lesen dieses Flag noch, um dem
  Live-Chat CPU-Vorrang zu geben.
- `MODELLE`-Dict (früher "mittel"/"schnell" = zwei gemma4-Größen) zeigt jetzt beide
  auf `hauhaucs-q6` — es gibt nur noch ein Modell, keine Tier-Wahl mehr.

**Zusammenhang**: `codewesen-chat.service` (systemd). Getestet: echter Chat gegen
`namelessAI_1234` lief Ende-zu-Ende durch Streaming.

---

## Nachtrag 2026-07-06 (später) — id_slot=0 + Trace-Log

`stream_ollama()` bekam einen neuen `quelle`-Parameter (Default
`"codewesen_chat:unbekannt"`), von beiden Aufrufstellen mit `codewesen_chat:{name}`
befüllt. Vor jedem `achat_stream()`-Call: `id_slot=0` (Chat bekommt garantiert
Priorität vor Automatikbetrieb) und `hauhau_client.trace_prioritaet(quelle, ...)`
(Reaktion auf zwei nicht zurückverfolgbare Chat-Hänger — siehe Nachtrag in
`hauhau_client.md`).
