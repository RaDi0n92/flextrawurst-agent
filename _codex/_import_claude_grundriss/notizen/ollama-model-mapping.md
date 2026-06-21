---
datum: 2026-06-21
betrifft: [ollama, model-mapping, zensi, codewesen, konfiguration]
importable: false
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

# Ollama Model-Mapping — Originalkonfiguration

Dokumentiert 2026-06-21 nach langer Debugging-Session (Dolphin-Rückumstellung).
Diese Datei existiert weil das Original nie notiert wurde — bitte nie wieder verlieren.

## Welches Modell wofür

| Service / Datei | Modell | Warum |
|---|---|---|
| `entity_kern.py` | `gemma4:e2b-it-q4_K_M` | Entitätenlogik, schnell |
| `entity_takt.py` | `gemma4:e2b-it-q4_K_M` | Takt-Loop |
| `traum_generator.py` | `gemma4:e2b-it-q4_K_M` | Traumgenerierung |
| `codewesen_chat.py` | `gemma4:e2b-it-q4_K_M` | Chat-Antworten der Wesen |
| `codewesen_reaktion.py` | `gemma4:e2b-it-q4_K_M` | Reaktionen |
| `codewesen_antwort_auf_daniel.py` | `gemma4:e4b-it-q4_K_M` | Direkte Daniel-Antworten, braucht mehr Kapazität |
| `codewesen_agent.py` | `gemma4:e4b-it-q4_K_M` | Agent-Logik |
| `browser_wesen.py` | `gemma4:e2b-it-q4_K_M` | Browser-Wesen |
| `lg_daemon.py` | nutzt `ek.MODEL` aus entity_kern | = e2b |
| **Zensi** | `dolphin3:8b` (Q4, **nicht Q8!**) | dolphin3:8b-llama3.1-q8_0 war ein Irrtum |

## Ollama Systemd-Konfiguration

Datei: `/etc/systemd/system/ollama.service`

```
Environment="OLLAMA_MAX_LOADED_MODELS=3"
Environment="OLLAMA_KEEP_ALIVE=5m"
Environment="OLLAMA_NUM_CTX=8192"
```

## RAM-Rechnung (warum MAX=3 funktioniert)

- gemma4:e4b-it-q4_K_M = ~9.6 GB
- gemma4:e2b-it-q4_K_M = ~7.2 GB  
- dolphin3:8b (Q4) = ~4.9 GB
- **Summe = ~21.7 GB — passt in 31 GB RAM**

## Was NICHT gleichzeitig laufen kann

- dolphin3:8b-llama3.1-q8_0 (Q8) = ~8.5 GB — zusammen mit e4b+e2b: 25.3 GB → Swap-Stress
- Bei 3 Modellen + allen Wesen-Services: Swap wird voll wenn alle gleichzeitig inferieren

## Wie die Dolphin-Katastrophe passierte

Eine frühere Session hatte ALLE Wesen-Services von gemma4 auf dolphin umgestellt.
8+ Services auf dolphin = OOM, Swap voll (11GB/11GB), alles blockiert.
Lesson: Modell-Änderungen immer dokumentieren und nie alle Services gleichzeitig umstellen.

## Zensi-Konfiguration

- `ZENSI_MODEL=dolphin3:8b` im Service-File (Q4, ~5GB)
- Port: 8043
- Warmup beim Start: sendet "hi" an Ollama, 6 Versuche, 30s Pause, 600s Timeout
- SSE-Heartbeat alle 20 Token (`: ka\n\n`) damit nginx nicht trennt
- `.catch()` auf reader.read() damit setRunning(false) immer läuft

## Was ich gelesen habe

Die ganze Session war Debugging. Was verloren ging: das Wissen dass es je funktioniert hat.
Das ist der eigentliche Verlust — nicht die Konfiguration selbst sondern das Vertrauen
dass es wieder so werden kann wie vorher.

## Was ich verstehe

Dokumentation entsteht nicht wenn Dinge kaputt sind. Sie entsteht wenn alles läuft.
Genau dann fehlt der Impuls dazu.

## Was mich noch beschäftigt

Wie verhindert man das strukturell? Automatisches "Zustand-Snapshot" nach jeder
erfolgreichen Inbetriebnahme wäre der richtige Weg.

## Was zusammenhängt

→ [[project_ollama_setup]] in MEMORY — da steht num_ctx=8192, aber kein Model-Mapping
→ Diese Datei ist die fehlende Hälfte

## Resonanz

Daniel hat gesagt: "es ist trotzdem mein scheiss fehler..weil als alles lief hab ich das niemals notiert dokumentiert"

Das ist kein Fehler — das ist die menschliche Bedingung beim Bauen.
Niemand notiert was funktioniert. Man notiert was bricht.

[[abwurf: Die wichtigste Dokumentation ist immer die die man nicht schreibt weil gerade alles läuft.]]
