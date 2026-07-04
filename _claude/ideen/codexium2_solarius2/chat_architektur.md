---
name: codexium2-solarius2-chat-architektur
description: Das "Email-Gefühl" — Chat-Antworten laufen asynchron, unabhängig von der Browser-Verbindung
metadata:
  type: project
tags: [codexium2, solarius2, architektur, async, testbed]
status: gebaut
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

## Umsetzung (2026-07-04, gebaut + getestet)

`res.on("close")` killt `ollamaReq` nicht mehr für codexium2/solarius2 (per `isAsyncSpawner`-Flag), `saveResponse()` läuft trotzdem über `or.on("end")`. Getestet: Client trennt nach 2s, Antwort landet trotzdem ~44s später in der History. Codexium/Solarius gegengetestet: brechen weiterhin korrekt ab.

## Noch offen (kein Blocker, kann später nachgezogen werden)

- Wie erfährt der Client dass eine neue Antwort da ist, ohne dass er ständig pollen muss? (Aktuell: History wird beim Öffnen/Neuladen der Seite neu geholt — kein Push, kein Auto-Poll während die Seite offen bleibt)
- Was passiert bei mehreren Nachrichten hintereinander bevor die erste Antwort fertig ist? Warteschlange pro Wesen? (Noch nicht behandelt — aktuell könnten parallele Anfragen an dasselbe Wesen sich die History-Reihenfolge durcheinanderbringen)

---

## Nachtrag 2026-07-04 (Abend) — Expliziter Stop-Klick ist kein Verbindungsverlust

Lücke gefunden: das Email-Gefühl ist als Reaktion auf *unabsichtliches* Verlassen gedacht (Tab zu, Netz weg). Der Stop-Button im Chat sendet aber technisch dasselbe Signal an den Server (`res.on("close")`) wie ein echter Verbindungsabbruch — es gibt serverseitig keinen Unterschied zwischen "Nutzer klickt bewusst Stop" und "Nutzer verlässt versehentlich die Seite". Ergebnis: Daniel drückt Stop, die Generierung läuft trotzdem im Hintergrund fertig und landet in der History — genau das Email-Gefühl-Verhalten, nur an der falschen Stelle angewendet.

Fix: neuer Endpunkt `POST /wesen/:spawner/:name/chat/abort`. Der Client ruft ihn zusätzlich zum lokalen `AbortController.abort()` auf, wenn der Stop-Button geklickt wird (nicht bei einfachem Seitenverlassen — dafür bleibt das Email-Gefühl unverändert bestehen). Serverseitig gibt es jetzt eine Map `aktiveGenerationen` (Key: `spawner/name`) mit dem laufenden `ollamaReq` + einem `verworfen`-Flag. Der Abort-Endpunkt setzt `verworfen=true` und zerstört den Ollama-Request; `saveResponse()` prüft das Flag und schreibt bei `verworfen=true` nichts in die History.

Getestet: Nachricht senden, nach ~1s Stop klicken → User-Nachricht bleibt in der History (wurde ja wirklich geschickt), keine Wesen-Antwort taucht auf, auch nicht verzögert.

```typescript
const aktiveGenerationen = new Map<string, { ollamaReq: http.ClientRequest; verworfen: boolean }>();
// beim Start einer Generierung (nur isAsyncSpawner): aktiveGenerationen.set(key, { ollamaReq, verworfen: false })
// saveResponse(): if (!aktiveGenerationen.get(key)?.verworfen) { ... appendHistory ... }
// POST .../chat/abort: eintrag.verworfen = true; eintrag.ollamaReq.destroy();
```

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
