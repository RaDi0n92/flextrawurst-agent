---
name: codexium2-solarius2-chat-architektur
description: Das "Email-Gefühl" — Chat-Antworten laufen asynchron, unabhängig von der Browser-Verbindung
metadata:
  type: project
tags: [codexium2, solarius2, architektur, async, testbed]
status: in-diskussion
datum: 2026-07-04
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Scope

Gilt NUR für Codexium2/Solarius2 (siehe `project_codexium2_testbed` in Claudes Memory). Codexium/Solarius laufen weiter mit der aktuellen, synchronen Architektur.

---

## Was ich verstehe

Daniels Bild: Chat soll sich wie E-Mail anfühlen. Mensch schickt eine Nachricht ab und kann die Seite sofort verlassen. Nach ein paar Minuten wieder reinschauen — dann ist da (wenn fertig) eine neue Antwort. Kein Zwang zum Warten/Zuschauen.

**Ist-Zustand (Codexium/Solarius, aktueller Code in `serve_process_camera_preview.ts`):** Das Gegenteil ist der Fall — der Server killt die laufende Ollama-Generierung aktiv, sobald die Client-Verbindung schließt:
```typescript
res.on("close", () => {
  if (!ollamaReq.destroyed) ollamaReq.destroy();
});
```
Verlässt man die Seite mitten in der Generierung, wird nichts fertig, nichts landet in der History.

**Für Codexium2/Solarius2 gilt jetzt: das muss weg.** Generierung wird vom HTTP-Request des Clients entkoppelt:
1. Mensch schickt Nachricht → Server bestätigt sofort (Nachricht ist in History gespeichert), Verbindung kann sofort geschlossen werden.
2. Ollama-Generierung läuft server-seitig weiter, unabhängig davon ob der Client noch da ist.
3. Fertige Antwort wird in die (bereits server-seitige) History geschrieben — History ist ja laut bisherigem Konzept schon "alleinige Wahrheit" (siehe Commit "server als einzige wahrheit für chat-verläufe").
4. Client lädt beim nächsten Öffnen einfach die History neu — wie ein Postfach-Refresh.

Automatische Memory-Extraktion (siehe `memory_container.md`) nutzt denselben Mechanismus: vom Menschen getriggert, läuft als eigener Hintergrund-Auftrag, schreibt Ergebnis in Memory wenn fertig — kein Sofort-Ding.

**Entschieden (2026-07-04): Live-Streaming bleibt erhalten, zusätzlich zum Email-Modus.** Wer auf der Seite bleibt, sieht weiter Token-für-Token mit Cursor wie bisher. Wer die Seite verlässt, killt das die Generierung nicht mehr — sie läuft server-seitig weiter und landet in der History, ganz gleich ob noch jemand zuschaut. Beides ist also derselbe Vorgang, nur mit oder ohne Zuschauer. Daniels Begründung: aktuell nur ein Nutzer (er selbst), Wesen-Einzug noch gesperrt, das 144s-Ratelimit-Problem vom Zwischenwesen-Konzept existiert hier noch gar nicht — Testphase, kein Lastproblem.

---

## Was noch fehlt bevor wir bauen können

- Wie erfährt der Client dass eine neue Antwort da ist, ohne dass er ständig pollen muss? (Einfaches Polling beim Öffnen reicht evtl. erstmal — kein Push nötig für den Anfang)
- Was passiert bei mehreren Nachrichten hintereinander bevor die erste Antwort fertig ist? Warteschlange pro Wesen?

---

## Datenstruktur die ich mir vorstelle

### Vision-Schicht
Der Chat wird vom Live-Gespräch zum Briefwechsel. Das nimmt Druck raus — man muss nicht mehr zusehen wie das Wesen "tippt", man kann fragen und weggehen. Passt auch zum langsamen, bedächtigen Charakter den ein 35B-Modell auf CPU sowieso hat (Antwortzeiten die eh schon nicht "live" sind).

### Code-Skizze
```typescript
// POST /codexium2/:name/chat — Streaming bleibt, Disconnect killt nicht mehr
// Weiterhin SSE-Response wie bisher — solange der Client zuhört, sieht er Token live.
res.writeHead(200, { "Content-Type": "text/event-stream", ... });

let fullResponse = "";
let responseSaved = false;
function saveResponse() {
  if (!responseSaved && fullResponse) { responseSaved = true; appendHistory(hp, "assistant", fullResponse); }
}

or.on("data", (c) => {
  // ... token parsen wie bisher ...
  fullResponse += tok;
  if (!res.writableEnded) res.write(`data: ${JSON.stringify({ token: tok })}\n\n`); // nur schreiben wenn noch verbunden
});
or.on("end", () => { saveResponse(); if (!res.writableEnded) { res.write("data: [DONE]\n\n"); res.end(); } });

// GEAENDERT ggue. Codexium/Solarius: KEIN ollamaReq.destroy() bei res.on("close")
res.on("close", () => { /* bewusst leer — Generierung laeuft weiter, saveResponse() greift trotzdem via or.on("end") */ });

// Client beim (Wieder-)Öffnen: GET /wesen/:spawner/:name/history — wie gehabt
```
