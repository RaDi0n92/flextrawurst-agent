# Dolphin Mischpult — Konzept & Stand

> Letztes Update: 2026-06-22  
> Pfad: `/root/flextrawurst/out/process_camera/dolphin_mischpult.html`  
> Erreichbar: `http://localhost:8787/dolphin`  
> Server-Daten: `/root/werkraum/dolphin_mischpult/`

---

## Was ist das

Das Dolphin Mischpult ist ein live steuerbares Chat-Interface für `dolphin3-daniel` (lokal via Ollama). Kein statisches System-Prompt-Feld — stattdessen ein Mischpult: mehrere Felder die sich zu einem Gesamtpromt zusammensetzen, jederzeit anpassbar während ein Gespräch läuft.

Es ist der **Blueprint** — dieselbe Architektur soll später auf gemma2b, gemma4b und zensi übertragen werden.

---

## Architektur

```
Browser (dolphin_mischpult.html)
  → POST /dolphin/chat
    → buildSystemPrompt() kompiliert: base + overlay-tags + pendingFeedbackModel
    → Ollama dolphin3-daniel (Port 11434, streaming, think:false)
    → SSE-Stream zurück zum Browser

Server-Daten (append-only):
  sessions/YYYY-MM-DD_HH-MM-SS.jsonl   ← ein File pro Session
  changes.jsonl                          ← jede Mischpult-Änderung
  feedback.jsonl                         ← Daumen + Text-Feedback
  sessions-index.json                    ← Name + archived-Flag pro Session
  best_prompt.md                         ← kanonischer Default-Prompt (geplant)
  trash/                                 ← gelöschte Sessions (geplant)
```

**Session-JSONL Format** (pro Zeile ein JSON-Objekt):
```json
{"role":"user","content":"...","ts":"...","sessionId":"..."}
{"role":"assistant","content":"...","ts":"...","systemBase":"...","overlays":{...},"feedbackModel":"..."}
{"evtype":"field","content":"[ton] aktiviert: ...","ts":"..."}
```

Jede Modell-Antwort trägt den `systemBase` + `overlays` die damals galten. Das ist die Wahrheit — nicht localStorage.

---

## Systempromt-Logik

`buildSystemPrompt()` kompiliert zur Sendezeit:

```
[base-text]          ← nur wenn baseActivated=true
---
[ton]
[wert des ton-tags]
---
[fokus]
[wert des fokus-tags]
---
[feedback vom nutzer für diesen output]
[pendingFeedbackModel]
```

Der kompilierte Prompt ist in der Vorschau sichtbar ("vorschau" Button im Mischpult).

---

## Mischpult-Felder

### Systempromt Basis
- Langes Freitextfeld, standardmäßig eingeklappt
- Muss explizit per "aktivieren →" aktiviert werden (erzeugt Protokoll-Event)
- Vorschau zeigt was dolphin wirklich bekommt

### Overlay-Felder (5 vordefiniert + custom)
| Feld | Zweck | Beispiel |
|------|-------|---------|
| ton | Wie klingen die Antworten | "schärfer bitte" |
| fokus | Womit soll sich dolphin beschäftigen | "nur technische Details" |
| tempo | Schnell/kurz vs. ausführlich | "maximal 3 Sätze" |
| haltung | Grundhaltung gegenüber dem Input | "kritisch hinterfragen" |
| kontext | Rahmen des Gesprächs | "du redest mit jemandem der..." |

Jedes Feld: Textarea → "aktivieren →" erzeugt einen Tag. Tags können einzeln entfernt werden (= deaktiviert, Protokoll-Event). Mehrere Tags pro Feld möglich (werden zusammengeführt).

Custom-Felder: via Formular mit Name + "Wofür gedacht?" + Beispiel.

---

## Chat als Protokoll

Der Chatverlauf ist nicht nur Gespräch — er dokumentiert alles:

```
[chat-message] user
[chat-message] dolphin
[proto-event]  [ton] aktiviert: "schärfer bitte"   ← type: field
[proto-event]  — Kontext zurückgesetzt —              ← type: reset  
[proto-event]  📝 Feedback: "zu lang gewesen"        ← type: feedback
[chat-message] user
[chat-message] dolphin
```

Protokoll-Events haben eigene Farben im Chat:
- `field` → lila
- `reset` → orange  
- `feedback` → grün

---

## Pro-Nachricht Aktionen (Modell-Antworten)

Jede Dolphin-Antwort hat Buttons (Desktop: bei Hover, Mobile: immer sichtbar):

| Button | Funktion |
|--------|----------|
| 🔊 | TTS dieser einzelnen Nachricht (forciert, unabhängig vom globalen TTS-Status) |
| 👍 | Thumb-Up → speichert in `feedback.jsonl` |
| 👎 | Thumb-Down → speichert in `feedback.jsonl` |
| 📝 | Feedback-Popup → Text wird als `pendingFeedbackModel` in NÄCHSTEN System-Prompt eingebaut |
| ↩ | Rollback → entfernt alles nach diesem Punkt aus Chat + msgs-Array |

---

## TTS

- Global: Button oben rechts (`🔊`/`🔇`) — alle neuen Antworten werden vorgelesen
- Pro-Nachricht: 🔊 Button unter jeder Dolphin-Antwort — liest diese eine vor
- Voice: `de-DE-KatjaNeural`, Chunks à 400 Zeichen, POST `/tts/speak`
- Markdown-Bereinigung vor dem Vorlesen (kein Code, kein \*\*, keine #)

---

## Sessions

### Sidebar (links, 160px)
- Zeigt alle nicht-archivierten Sessions
- Klick → lädt Chat-Verlauf (und bald: Systempromt)
- Aktive Session hervorgehoben

### Pro Session
- Optionaler Name (Doppelklick oder Rename-Button) — debounced, auto-save
- Archivieren → verschwindet aus Sidebar (bleibt in Index als `archived:true`)
- MD-Export → Download als Markdown mit allen Nachrichten

### Storage
- Pro Session: `/root/werkraum/dolphin_mischpult/sessions/YYYY-MM-DD_HH-MM-SS.jsonl`
- Index: `/root/werkraum/dolphin_mischpult/sessions-index.json`
- Append-only — kein Löschen, kein Überschreiben

---

## Persistenz-Status

| Was | Wo | Geräteübergreifend |
|-----|----|--------------------|
| Chat-Verlauf | Session-JSONL auf Server | ✅ |
| Systempromt-Text | localStorage (Cache) + JSONL (Wahrheit) | ⚠️ nur JSONL |
| baseActivated-Flag | localStorage | ❌ |
| Overlay-Tags (aktive) | localStorage | ❌ |
| Mischpult-Änderungen | changes.jsonl | ✅ |
| Feedback (Daumen+Text) | feedback.jsonl | ✅ |

→ Ziel: alles was zählt liegt auf dem Server. localStorage nur als schneller Cache.

---

## Offene Features (Tasks #15–#24)

### Systempromt-System (Tasks 15–19)
- **#15** Systempromt cross-device: beim Session-Wechsel aus JSONL lesen
- **#16** Session-Wechsel → letzten Systempromt aus JSONL laden + aktivieren
- **#17** Neue Session = leerer Prompt + "← beste Version" Button
- **#18** `best_prompt.md` anlegen + `GET /dolphin/best-prompt` Route
- **#19** Systempromt als `.md` ↓ runterladen / ↑ hochladen (manueller Transfer)

#### best_prompt.md Konzept
Eine Datei auf dem Server: `/root/werkraum/dolphin_mischpult/best_prompt.md`  
Editierbar per WinSCP — das ist der "kanonische" Prompt der bei neuen Sessions per Knopfdruck geladen werden kann. Neue Sessions starten **leer** (sauberer Anfang), aber "beste Version →" holt diese Datei.

### Sessions erweitern (Tasks 20–23)
- **#20** Session-Upload: fremde JSONL hochladen → wird neue Session (inkl. Prompt-Restore)
- **#21** Soft-Delete: `trash/` Ordner — Sessions verschwinden aus Sidebar, Datei bleibt
- **#22** Herkunft-Marker beim Laden: kein neues erstes Event, sondern Marker IM Verlauf an der Ladestelle
- **#23** Herkunft-Eintrag am Anfang jeder neuen Session: timestamp, sessionId, modell, user-agent

### Preset-System (Task 24)
- **#24** Presets als ZIP: kompletter Mischpult-Snapshot (base + alle Overlay-Felder) als benannte Datei. Download als ZIP (jedes Feld = eigene .md). Upload: ZIP gesamt oder einzelne .md. Kein Auto-Load beim Start.

---

## Server-Routen (aktuell)

| Methode | Pfad | Funktion |
|---------|------|----------|
| GET | `/dolphin` | HTML ausliefern |
| POST | `/dolphin/chat` | Streaming-Chat mit dolphin3-daniel |
| POST | `/dolphin/log-change` | Mischpult-Änderung in changes.jsonl |
| GET | `/dolphin/sessions` | Alle Session-IDs |
| GET | `/dolphin/sessions-index` | Index mit Namen + archived |
| GET | `/dolphin/session/:id` | Session-JSONL lesen |
| GET | `/dolphin/session/:id/md` | Session als Markdown |
| POST | `/dolphin/session/:id/rename` | Session umbenennen |
| POST | `/dolphin/session/:id/archive` | Session archivieren |
| POST | `/dolphin/session/:id/event` | Event in Session-JSONL appenden |
| POST | `/dolphin/feedback` | Daumen/Text-Feedback speichern |

**Geplante Routen:**
- `GET /dolphin/best-prompt` — best_prompt.md lesen
- `POST /dolphin/session/:id/delete` — in trash/ verschieben
- `POST /dolphin/session/upload` — fremde JSONL hochladen

---

## Modell-Info

```
Name:     dolphin3-daniel
Basis:    dolphin3:8b (Ollama)
Custom:   FROM dolphin3:8b + repeat_penalty 1.3 + Daniels System-Prompt
think:    false (kein Chain-of-Thought)
Port:     11434
```

---

## Als Blueprint: Übertragung auf andere Modelle

Das Mischpult-System ist für dolphin3-daniel entwickelt, aber die Idee gilt für alle:
- `gemma2b` (gemma4:e2b-it-q4_K_M) → Port 8787/gemma2b
- `gemma4b` (gemma4:e4b-it-q4_K_M) → Port 8787/gemma4b  
- `zensi` → eigenes Interface

Wenn das System ausgereift ist: dieselbe Mischpult-Logik auf alle übertragen. Sessions wären dann modellspezifisch — ein Session-Upload von gemma4b → dolphin würde den Prompt aus der gemma4b-Session laden und dolphin damit initialisieren.
