# hauhau_client.ts

Migriert: 2026-07-06

TS-Pendant zu `hauhau_client.py` (`/root/flextrawurst/scripts/hauhau_client.ts`),
fuer die Node-basierten Frontends (dolphin). Nutzt Node's rohes `http`-Modul
statt fetch, weil `chatStream()` denselben `http.ClientRequest` zurueckgeben muss,
den der Aufrufer schon kennt und zum Abbrechen (`req.destroy()`) braucht — das
war der zentrale Grund warum eine simple fetch/Promise-Abstraktion nicht gereicht
haette.

**Funktionen**: `chat()`, `chatStream()` (mit `onToken`/`onDone`/`onError`-Callbacks
statt Generator, passend zum bestehenden Callback-Stil des Projekts), `chatRaw()`.

**Bug gefunden + gefixt beim ersten echten Einsatz**: Weder `chat()` noch
`chatStream()` prüften den HTTP-Statuscode der Antwort. Bei einem Fehler (z.B.
"Kontext zu voll") schickt llama-server eine JSON-Fehlermeldung statt eines
SSE-Streams zurück — ohne Statusprüfung wurde das still als leere, erfolgreiche
Antwort behandelt (kein Fehler, aber auch kein Text). Jetzt wird bei Status ≥400
sauber `onError`/eine Promise-Rejection ausgelöst.

**Zusatzfeature**: `stream_options: {include_usage: true}` wird immer mitgeschickt
— llama-server liefert dann im letzten SSE-Chunk `usage.completion_tokens`/
`prompt_tokens`, was die bisherige Ollama-Token-Zähler-Anzeige (`eval_count`/
`prompt_eval_count`) im Frontend unverändert weiterleben lässt.
