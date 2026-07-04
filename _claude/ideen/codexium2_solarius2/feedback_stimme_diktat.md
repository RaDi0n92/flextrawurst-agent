---
name: codexium2-solarius2-feedback-stimme-diktat
description: Feedbacksystem (Daumen hoch/runter + Kommentar), Stimmenauswahl männlich/weiblich, Spracheingabe und Pin-Selektions-Fix für Codexium2/Solarius2
metadata:
  type: project
tags: [codexium2, solarius2, feedback, tts, speech-to-text, pin, testbed]
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

**3. Speech-to-Text.** Mikrofon-Button neben dem Senden-Button, nutzt die browsereigene Web Speech API (`SpeechRecognition`/`webkitSpeechRecognition`, `lang: de-DE`, `continuous: true`, `interimResults: true`). Kein Server-Roundtrip, kein neuer Endpoint. Button versteckt sich selbst per Feature-Detection wenn der Browser die API nicht kennt (z.B. Firefox Desktop). Diktierter Text wird an bereits Getipptes angehängt, nicht überschrieben.

**4. Pin-Fix.** Der Pin-Mechanismus aus `memory_container.md` sollte von Anfang an einzelne markierte Sätze pinnen können, hat aber in der Praxis immer die ganze Nachricht gegriffen. Ursache: ein Klick auf den Pin-Button erzeugt einen eigenen `mousedown` am Klickpunkt (auf dem Button, nicht im Text) — das kollabiert jede vorher im Bubble-Text getroffene Selektion, bevor der `click`-Handler überhaupt läuft. Browser-Standardverhalten, kein offensichtlicher Bug im eigenen Code. Fix: `mousedown`-Handler auf dem Pin-Button mit `preventDefault()`, plus eine robustere Prüfung ob die Selektion wirklich aus dieser Bubble stammt (`Range`-Containment via `bubble.contains(selection.anchorNode)` statt fragilem Substring-Vergleich).

---

## Was ich nicht verstehe

Ob mobile Text-Selektion (Android/iOS, Long-Press + Ziehen der Selektionsgriffe) nach diesem Fix zuverlässig funktioniert. Der `mousedown`-Fix hilft nachweislich bei Maus-Klicks (getestet); mobile Browser können eine Selektion aber auch durch reines Antippen des Bildschirms an anderer Stelle über OS-Ebene kollabieren, unabhängig von JS. Das ist nicht durch Seiten-Code allein lösbar. Sollte Daniel das auf dem Handy testen und es dort noch hakt, bräuchte es einen anderen Ansatz (z.B. Text-Abschnitte einzeln antippbar machen statt freier Selektion).

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
- Stimmenauswahl, Mic-Button, Feedback-Buttons, Pin-Fix: alle in `wesen_chat.html`.
- Getestet: Feedback-Klick schreibt `feedback.json` + `feedback/<id>.md` korrekt (verifiziert am Beispiel GluPKI). Pin-Selektion übersteht jetzt Button-Klick (direkter DOM-Test: Teilauswahl "Testsatz z" aus einer längeren Nachricht landet unverändert im Pin-Modal). Stimmen-Dropdown zeigt beide Optionen. Mic-Button erscheint bei Browsern mit Web-Speech-Support.
- Nicht getestet (nicht headless simulierbar): echtes Mikrofon-Diktat, mobile Touch-Selektion.
