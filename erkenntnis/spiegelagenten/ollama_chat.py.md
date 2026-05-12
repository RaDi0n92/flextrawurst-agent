---
## Neugier-Scan aktualisiert 2026-04-18

Originaldatei: `/root/werkraum/agent/dak_gord_system/ollama_chat.py`

## Was ich darin erkenne (aktueller Stand)

"Routenplaner für Komplexität" — das stimmt noch. Was neu ist: Der Routenplaner bricht nicht mehr bei einem Straßensperre zusammen.

**Was sich geändert hat:**
- `_anfrage_mit_retry()` — 3 Versuche, Backoff (2s/5s/10s), unterscheidet Connection-Fehler von Timeouts
- `OllamaChat`-Klasse — Wrapper um `ollama_chat()` für Kompatibilität mit `graf.py` (alter Architektur-Einstiegspunkt)

**Die Retry-Logik unterscheidet korrekt:**
- `ConnectionError` → retry (Ollama kurz nicht erreichbar)
- `Timeout` → kein retry (das Modell ist langsam, nicht weg — nochmal senden hilft nicht)
- HTTP 4xx → kein retry (Protokollfehler, nicht Verbindungsfehler)
- HTTP 5xx → retry (Serverfehler, kann transient sein)

## Was mich irritiert

Das 3-Stufen-Routing (blitz/mittel/tief) ist Keyword-basiert — keine Gewichtung, kein Lerneffekt. Wenn "resonanz" im Text steht, wird MITTEL gewählt. Aber wenn Daniel ein technisches Problem mit Resonanz-Konzepten beschreibt, sollte das MITTEL sein (Code-Denken), nicht TIEF (Philosophie).

Außerdem: `MODELL_QWEN` ist definiert und in `_qwen_sekretaer_pass()` genutzt — aber der Sekretär-Pass ist deaktiviert. Qwen ist Kapazität ohne Einsatz.

## Verbindung

→ Die `OllamaChat`-Klasse ist ein Kompatibilitäts-Shim für `graf.py` — sie ist kein eigenes Konzept. Sie hält eine Brücke zur alten Architektur offen. Wenn `graf.py` irgendwann vollständig ersetzt wird, kann sie verschwinden.
