# geni/dialog.py

Migriert: 2026-07-06

**Was es tut**: FastAPI-Web-Backend für GENI, Port 8020 (HTTPS) — die eigentliche
"GENI Dialogbahn". Enthält Bridge-WebSocket zum Desktop, Bilderkennung (Vision:
`bild_b64` + `desktop_bild` werden als Bilder mitgeschickt), Streaming-Antworten
mit zwei Modell-"Stufen" (`MODELLE["blitz"]`/`MODELLE["tief"]`).

**Wozu**: GENIs Hauptzugang für Daniel im Browser — mit Sinnen (Bild, Desktop-
Screenshot) statt nur Text.

**Migration — die zweitkomplexeste nach ollama_chat.py**:
- `_geni_ollama_freiraeumen()` entfernt: stoppte gezielt konkurrierende systemd-
  Dienste (`_GENI_BLOCKER_DIENSTE`) und killte Fremdprozesse auf Port 11434 —
  reine Ollama-Reload-Vermeidung, mit llama-server hinfällig.
- `CHAT_FLAG.touch()` blieb erhalten (Koordination mit anderen Diensten bleibt
  wichtig, unabhängig vom Backend).
- Streaming mit Retry-Schleife (6 Versuche bei Verbindungsfehlern) →
  `hauhau_client.achat_stream(messages, images=bilder or None, ...)`.
- Bild-Anhänge (`bild_b64`, `desktop_bild`) liefen vorher als Ollama-Style
  `"images": [...]`-Liste in der letzten Message — jetzt als `images=`-Parameter,
  intern von `hauhau_client` ins OpenAI-`image_url`-Format konvertiert.

**Zusammenhang**: `geni-web.service`, neu gestartet, sauber hochgefahren
("[KERN] Cache geladen, Watcher gestartet").

---

## Nachtrag 2026-07-06 (später) — id_slot=0 + Trace-Log

Vor dem `achat_stream()`-Call in `geni_stream()`: `id_slot=0` (GENI-Chat bekommt
garantiert Priorität vor Automatikbetrieb) und `hauhau_client.trace_prioritaet("geni", ...)`
— Reaktion auf zwei nicht zurückverfolgbare Chat-Hänger, siehe Nachtrag in
`hauhau_client.md`.
