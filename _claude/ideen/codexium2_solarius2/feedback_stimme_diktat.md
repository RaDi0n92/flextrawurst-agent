---
name: codexium2-solarius2-feedback-stimme-diktat
description: Feedbacksystem, Stimmenauswahl + Lesetempo, Spracheingabe (inkl. Android-Verdopplungs-Fix) und echter Stop-Abbruch für Codexium2/Solarius2
metadata:
  type: project
tags: [codexium2, solarius2, feedback, tts, speech-to-text, pin, abort, testbed]
status: gebaut
datum: 2026-07-04
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Scope

Gilt NUR für Codexium2/Solarius2 (siehe `project_codexium2_testbed` in Claude-Memory). Codexium/Solarius bleiben unangetastet. Zwei Ausnahmen sind bewusst NICHT testbed-gated, weil sie rein additive UI/Audio-Features sind, die keine Wesen-Daten anfassen und für alle vier Spawner in derselben `wesen_chat.html` laufen: die TTS-Stimmenauswahl und die Speech-to-Text-Eingabe. Feedback-System und der Pin-Fix bleiben wie der bestehende Pin/Container/Memory-Mechanismus testbed-only.

---

## Was gebaut wurde

**1. Stimmenauswahl (männlich/weiblich).** Der TTS-Service (`tts_service.py`, Port 8035 hinter `/tts/`) konnte immer schon jede edge-tts-Stimme, das Frontend hatte `TTS_VOICE` aber hart auf `de-DE-KatjaNeural` gesetzt. Jetzt ein `<select>` im Header (Katja/weiblich, Florian/männlich — Florian ist dieselbe Stimme, die schon für Daniels eigenes Vorlesen läuft, siehe `project_ollama_setup`-Nachbardatei zu TTS), Wahl pro Charakter in `localStorage` gemerkt.

**2. Feedback-System.** Unter jeder Nachricht (Mensch UND Wesen) drei Buttons: 👍/👎 (sofortiger Toggle-Klick, erneuter Klick nimmt die Bewertung zurück) und 💬 (Modal mit Freitext-Kommentar, max. 2000 Zeichen). Braucht dafür erstmals stabile Nachrichten-IDs — `chat_history.jsonl`-Zeilen bekommen jetzt ein `id`-Feld (vom Client als UUID erzeugt, für User- UND Wesen-Nachricht, im Chat-Request mitgeschickt). Alte Nachrichten ohne ID zeigen keine Feedback-Buttons (kann technisch nicht zugeordnet werden) — kein Rückwirkungsproblem, nur für neue Nachrichten ab heute.

Persistenz bewusst doppelt, wie von Daniel gefordert:
- `feedback.json` im Charakterordner — eine Liste, Wahrheit für die UI (Upsert über die Nachrichten-ID).
- `feedback/<id>.md` im selben Ordner, eine Datei pro Nachricht, direkt lesbar ohne JSON zu parsen — wird bei jedem Update neu geschrieben (kein Anhäufen mehrerer Dateien pro Nachricht).

**3. Speech-to-Text.** Mikrofon-Button neben dem Senden-Button, nutzt die browsereigene Web Speech API (`SpeechRecognition`/`webkitSpeechRecognition`, `lang: de-DE`). Kein Server-Roundtrip, kein neuer Endpoint. Button versteckt sich selbst per Feature-Detection wenn der Browser die API nicht kennt (z.B. Firefox Desktop). Diktierter Text wird an bereits Getipptes angehängt, nicht überschrieben. **Korrigiert am Abend** — siehe Nachtrag: `continuous:true` war falsch, verdoppelte Wörter.

**4. Pin-Fix, erster Anlauf (ÜBERHOLT — siehe Nachtrag).** Erster Versuch: `mousedown`-Handler mit `preventDefault()` auf dem Pin-Button plus `Range`-Containment-Prüfung, damit eine per Maus getroffene Textauswahl den Klick auf den Button übersteht. Hat am Desktop funktioniert (getestet), aber auf dem Handy nicht — Daniel hat's getestet und es griff weiterhin immer die ganze Nachricht. Ursache: Touch-Text-Selektion kollabiert beim Antippen eines Buttons daneben auf OS-Ebene, das ist mit `mousedown.preventDefault()` (einem reinen Maus-Event) nicht zu retten. Der ganze Ansatz "Text markieren" wurde noch am selben Abend durch eine Satz-Checkbox-Liste ersetzt — siehe Nachtrag unten und `memory_container.md`.

---

## Datenstruktur die ich mir vorstelle

### Vision-Schicht
Feedback ist keine Bewertung des Wesens, sondern ein Gedächtnis für das, was zwischen Mensch und Modell wirklich getragen hat oder nicht — nützlich für spätere Prompt-Justierung, nicht für ein Ranking.

### Code-Skizze
```typescript
// chat_history.jsonl — pro Zeile jetzt optional id
interface HistoryZeile { role: string; content: string; ts: string; id?: string; }

// feedback.json (pro Wesen)
interface FeedbackEintrag {
  id: string;                    // = Nachrichten-id
  rolle: "mensch" | "wesen";
  nachricht: string;
  rating: "up" | "down" | null;
  kommentar: string | null;
  erstellt_am: string;
  aktualisiert_am: string;
}
// feedback/<id>.md — von upsertFeedback() bei jedem Update neu geschrieben, lesbarer Spiegel des JSON-Eintrags
```

---

## Umsetzung (2026-07-04, alle Punkte gebaut + getestet via Playwright)

- Message-IDs: `appendHistory`/`loadHistory`/`loadCurrentSessionHistory`/`splitSessions` in `serve_process_camera_preview.ts`, Client generiert `msgId`/`replyMsgId` in `send()`.
- Feedback-Endpunkte: `GET`/`POST /wesen/:spawner/:name/feedback` — Upsert, schreibt JSON + MD.
- Stimmenauswahl, Mic-Button, Feedback-Buttons: `wesen_chat.html`.
- Getestet: Feedback-Klick schreibt `feedback.json` + `feedback/<id>.md` korrekt (verifiziert am Beispiel GluPKI). Stimmen-Dropdown zeigt beide Optionen. Mic-Button erscheint bei Browsern mit Web-Speech-Support.
- Nicht headless testbar: echtes Mikrofon-Diktat — dafür von Daniel real auf dem Handy getestet (siehe Nachtrag).

---

## Nachtrag 2026-07-04 (Abend) — drei Korrekturen nach echtem Praxistest

Daniel hat alles auf dem Handy getestet — drei Sachen waren kaputt bzw. fehlten:

**1. Speech-to-Text verdoppelte Wörter.** Ursache recherchiert (siehe Web-Suche): bekannter Chromium-Bug auf Android (Issue #40324711) — `continuous:true` wird von Chrome durch heimliche Neustarts des nativen Recognizers simuliert, dabei wird bereits gehörter Ton nochmal mitgeschnitten. Fix laut mehreren Bug-Threads (u.a. react-speech-recognition#18): `continuous:false` setzen und im `onend` selbst sofort neu starten — ein "continuous surrogate" aus lauter Einzel-Sessions statt der kaputten nativen Continuous-Funktion. `sttFinal` bleibt über die Neustarts hinweg erhalten (akkumuliert), jede neue Einzel-Session hört nur noch Ton NACH dem Neustart, dadurch kein doppeltes Mitschneiden mehr.

**2. Stop-Klick killt die Generierung nicht wirklich.** War eine Verwechslung im eigenen Code zwischen "Nutzer klickt bewusst Stop" und "Verbindung geht verloren" — siehe ausführlich `chat_architektur.md`-Nachtrag. Kurzfassung: neuer Endpunkt `POST .../chat/abort`, den der Stop-Button zusätzlich zum lokalen Fetch-Abort aufruft; killt die Ollama-Generierung serverseitig wirklich und verwirft das Ergebnis, statt es (wie beim reinen Email-Gefühl gewollt) trotzdem fertig zu generieren und zu speichern.

**3. TTS-Tempo-Wunsch.** Slider im Header (−50% bis +100%, Schritt 10%), pro Charakter in `localStorage` gemerkt, geht direkt in den bestehenden `rate`-Parameter von `tts_service.py` (der konnte das schon immer, war im Frontend nur nie einstellbar).

Alle drei Punkte von Daniel auf dem Handy nachgetestet und bestätigt funktionierend.

**4. (separat entdeckt, gleicher Abend) Profil zeigte nur ausgefüllte Felder.** Der Spawner (`wesen_spawner.html`) schreibt beim Erstellen nur für ausgefüllte Formularfelder überhaupt eine `.md`-Datei — leere Felder existierten technisch gar nicht und tauchten im Profil (`wesen_profil.html`) deshalb nie auf, obwohl sie nachträglich befüllbar sein sollten. Fix: `wesen_profil.html` rendert jetzt eine feste Liste aller acht bekannten Feldnamen (Gesprächseinstieg, Was ich bin, Neigungen, Abneigungen, Beschreibung, Wesendefinition, Weltlore, Anleitung), leere als "— noch leer" markiert, Speichern legt die Datei bei Bedarf neu an (Backend konnte das schon immer, war nur nie sichtbar).
