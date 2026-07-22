# tools/bildgenerierung_test.py

Migriert: 2026-07-06

**Was es tut**: Test-/Entwicklungs-App für Bildgenerierung — enthält u.a.
`_ollama_suggest()`: fragt ein LLM welches Bildmodell (sdxl_lightning,
juggernaut_xl, pony, realvis_xl, flux_schnell, flux_dev) und welcher Mix-Typ
(blend/collage) für einen Prompt am besten passt. Fällt bei Timeout/Fehler auf
eine Keyword-basierte Heuristik zurück.

**Wozu**: Statt hart codierter Regeln entscheidet ein kleines, schnelles LLM
situativ welches Bildmodell passt — mit Sicherheitsnetz falls das LLM nicht
rechtzeitig antwortet.

**Migration**: `urllib.request` (prompt-Stil, `api/generate`) → `hauhau_client.chat()`.
**Zu beachten**: Der Funktions-Default-Timeout (5s) war auf gemma4s Geschwindigkeit
zugeschnitten — mit hauhaucs (aktuell ~4-7 tok/s statt gemma4s deutlich schnellerer
Antwortzeit) dürfte der Ollama-Vorschlag jetzt öfter in den Keyword-Fallback
laufen, weil 5s oft nicht reichen. Funktional nicht kaputt (Fallback greift),
aber die reale "LLM schlägt Modell vor"-Funktion könnte seltener zum Zug kommen
als früher — falls das auffällt, ist der Timeout-Wert der erste Ansatzpunkt.
