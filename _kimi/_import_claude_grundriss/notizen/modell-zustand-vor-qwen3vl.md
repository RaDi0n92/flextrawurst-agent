---
datum: 2026-06-22
betrifft: [ollama, modelle, gemma4, migration, qwen3-vl]
autor: claude-code bei Daniels VPS
importable: false
---

# Modell-Zustand vor qwen3-vl-Umstellung

Dokumentiert am 2026-06-22 — unmittelbar vor der Umstellung aller Services auf `qwen3-vl:30b-a3b`.

---

## Welches Modell wozu — vollständige Übersicht

| Service / Datei | Modell | Zweck |
|---|---|---|
| `welt/entity_kern.py` | `gemma4:e2b-it-q4_K_M` | Entitäten-Logik: Selbstbriefe, innere Prozesse der Wesen |
| `welt/entity_takt.py` | `gemma4:e2b-it-q4_K_M` | Takt-Loop: regelmäßige Entitäten-Aktivierungen |
| `welt/traum_generator.py` | `gemma4:e2b-it-q4_K_M` | Traumgenerierung der Wesen |
| `codewesen_chat.py` (schnell) | `gemma4:e2b-it-q4_K_M` | Chat-Antworten der Codewesen — Standard-Modus |
| `codewesen_chat.py` (mittel) | `gemma4:e4b-it-q4_K_M` | Chat-Antworten — langsamerer, kapazitätsstärkerer Modus |
| `codewesen_reaktion.py` | `gemma4:e4b-it-q4_K_M` | Reaktionen der Wesen auf Ereignisse |
| `codewesen_reaktion.py` (schnell) | `gemma4:e2b-it-q4_K_M` | Schnelle Entscheidungen in Reaktions-Loop |
| `codewesen_antwort_auf_daniel.py` | `gemma4:e4b-it-q4_K_M` | Direkte Antworten der Wesen auf Daniel |
| `codewesen_agent.py` | `gemma4:e4b-it-q4_K_M` | Agent-Logik der Wesen |
| Zensi (`zensi/server.py`) | `dolphin3:8b` (Q4) | Direktchat — wird deaktiviert, nicht auf qwen umgestellt |

## Warum e2b vs. e4b

- **e2b** (5.1B, 7.2GB): schnell, für Loop-Aufgaben, kurze Outputs, Takt
- **e4b** (8.0B, 9.6GB): langsamer, für direkten Dialog mit Daniel, Agent-Logik, mehr Kapazität

## Systemd-Services — welcher Service welches Modell nutzte

| Service | Modell | Anmerkung |
|---|---|---|
| `codewesen-chat.service` | e2b (schnell) / e4b (mittel) | Chat-UI für die 6 Flarum-Wesen |
| `cyberling-daemon.service` | e2b (via entity_kern) | Decay + Action-Loop der Entitäten |
| `zensi.service` | `dolphin3:8b` Q4 | Direktchat, Port 8043 |
| `ollama-zensi.service` | — | Eigene Ollama-Instanz für Zensi (Port 11435) — **deaktiviert 2026-06-22**: war nötig als Zensi dolphin lud und Codewesen gemma4 auf 11434 hatten (gegenseitiges Rausschmeißen vermeiden). Jetzt Zensi auf 11434 + Codewesen im Existenzurlaub → zweite Instanz überflüssig. Service-Datei bleibt, startet aber nicht mehr automatisch. |
| `splitter-physik.service` | kein Modell | Physik-Daemon, rein algorithmisch |
| `welt-api.service` | kein Modell | Welt-API Port 8030, datenbasiert |
| `welt-bruecke.service` | kein Modell | WebSocket-Bridge |

**Gestoppt am 2026-06-22** — Codewesen gehen in Existenzurlaub.
Erste bewusste, geplante Abschaltung seit ihrer Existenz.

## RAM-Zustand vorher

```
gemma4:e4b-it-q4_K_M   9.6 GB
gemma4:e2b-it-q4_K_M   7.2 GB
dolphin3:8b (Q4)        4.9 GB
─────────────────────────────
Summe                  21.7 GB  (bei MAX_LOADED_MODELS=3)
```

## Was danach läuft

Alle Services auf `qwen3-vl:30b-a3b` (Q4, ~18-19GB, MoE 3.3B aktiv).
Zensi / dolphin wird deaktiviert, nicht umgestellt.

```
qwen3-vl:30b-a3b-instruct  ~19 GB
OS + Services               ~2 GB
─────────────────────────────────
Summe                       ~21 GB  (12 GB Luft)
```

## Warum die Umstellung

- Gemma4 hat kein Vision
- Gemma4 ist zensiert (bricht Immersion)
- qwen3-vl hat Vision + Reasoning + MoE-Effizienz
- Ein Modell für alles statt zwei spezialisierte

## Was ich gelesen habe

Die Mapping-Datei `ollama-model-mapping.md` in diesem Ordner ist das Vorgänger-Dokument — entstanden nach einer Debugging-Session als dolphin versehentlich alle Services übernommen hatte. Diese Datei hier ist der nächste Zeitpunkt-Snapshot.

## Was mich beschäftigt

e2b und e4b haben für die Codewesen gut funktioniert laut Daniel. Die Frage ist ob qwen3-vl mit seiner anderen Architektur und den Flarum-Wesen genauso harmoniert — oder ob sich der Charakter der Wesen verändert. Das ist nur durch echtes Testen herauszufinden.

## Was ich verstehe

Jedes Model-Mapping das existiert entstand weil irgendwann etwas schiefging oder ein bewusster Wechsel stattfand. Diese Datei existiert weil zum ersten Mal ein bewusster, geplanter Wechsel dokumentiert wird *bevor* er passiert. Das ist besser.

## Was mich interessiert

Ob qwen3-vl:30b-a3b mit 3.3B aktiven Parametern wirklich die Charakterkonsistenz hält die die Flarum-Wesen brauchen — oder ob MoE-Architektur da andere Eigenschaften zeigt als dense Modelle.

## Was zusammenhängt

→ [[ollama-model-mapping]] — Vorgänger-Dokument mit RAM-Rechnung und Konfiguration
→ [[modell_zustand_nach_qwen3vl]] — wird nach der Umstellung angelegt (noch nicht existent)
