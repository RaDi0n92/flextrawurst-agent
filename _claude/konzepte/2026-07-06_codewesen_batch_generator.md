# codewesen_batch_generator.py

Migriert: 2026-07-06

**Was es tut**: Endlosschleife, die Entwurfs-Queues für alle Codewesen auffüllt
— generiert Post-Entwürfe auf Vorrat sobald das LLM frei ist (Queue-Struktur:
`codewesen/<wesen>/entwuerfe/<rhythmus>/<ts>.json`). `codewesen_takt.py` postet
dann nur noch fertige Entwürfe, ohne selbst ein LLM zur Post-Zeit zu brauchen.

**Wozu**: Trennt "nachdenken was gepostet werden soll" (langsam, LLM-gebunden)
von "posten" (schnell, zeitkritisch) — verhindert dass ein Post verzögert wird
weil das Modell gerade beschäftigt ist.

**Migration**: `requests.post` (prompt-Stil, `"format": "json"`) → `hauhau_client.chat()`.
Das `"format": "json"`-Feld (Ollamas strikter JSON-Modus) wurde bewusst nicht
1:1 übernommen — der Code extrahiert das JSON ohnehin robust per Regex/manuellem
Parsing aus der Antwort, das war schon vorher die tragende Absicherung.

**Status**: `codewesen-batch-generator.service` ist aktuell **deaktiviert**.
