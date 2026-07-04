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

---

## Was noch fehlt bevor wir bauen können

**Offene Frage an Daniel (noch nicht entschieden):** Soll das Live-Streaming (Token-für-Token-Anzeige mit "denkt nach"-Cursor) für Menschen die auf der Seite bleiben erhalten bleiben — als Extra für alle die warten wollen — oder wird die ganze Interaktion einheitlich asynchron (immer "abgeschickt, dann später fertig", nie live mitschreiben)? Das entscheidet ob der bestehende SSE-Streaming-Code als Option bleibt oder ersetzt wird.

Weitere offene Punkte:
- Wie erfährt der Client dass eine neue Antwort da ist, ohne dass er ständig pollen muss? (Einfaches Polling beim Öffnen reicht evtl. erstmal — kein Push nötig für den Anfang)
- Was passiert bei mehreren Nachrichten hintereinander bevor die erste Antwort fertig ist? Warteschlange pro Wesen?

---

## Datenstruktur die ich mir vorstelle

### Vision-Schicht
Der Chat wird vom Live-Gespräch zum Briefwechsel. Das nimmt Druck raus — man muss nicht mehr zusehen wie das Wesen "tippt", man kann fragen und weggehen. Passt auch zum langsamen, bedächtigen Charakter den ein 35B-Modell auf CPU sowieso hat (Antwortzeiten die eh schon nicht "live" sind).

### Code-Skizze
```typescript
// POST /codexium2/:name/chat — neues Verhalten
// 1. Nachricht sofort in History schreiben, Response sofort zurückgeben (kein SSE-Stream mehr nötig)
res.writeHead(202, {"Content-Type": "application/json"});
res.end(JSON.stringify({status: "angenommen"}));

// 2. Generierung läuft weiter, unabhängig vom ursprünglichen `res`/`req`
// KEIN res.on("close") das den ollamaReq killt
generateInBackground(dir, history).then(reply => {
  appendHistory(hp, "assistant", reply);
});

// 3. Client beim (Wieder-)Öffnen: GET /wesen/:spawner/:name/history — wie gehabt
```
