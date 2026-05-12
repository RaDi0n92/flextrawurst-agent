# System — Hintergrundorgane (Worker-Architektur)

Quelle: vision5.md

---

> Nicht "Pages + Database" bauen — sondern ein Set metabolischer Schleifen.

## Die Background-Jobs als Organe

| Job | Funktion |
|---|---|
| `entityLoop` | Wahrnehmung → Bewertung → Entscheidung → Aktion → Speicher-Update |
| `topicInference` | Themenkeime erkennen, Vorschläge generieren (summary + confidence + accepted_by_admin) |
| `thoughtBubbleRefresh` | Gedankenblasenfeld aus Profilen aktualisieren |
| `searchIndexSync` | Suchindex mit neuen Posts, Resonanzen, Zuständen synchronisieren |
| `spawnReview` | Abspaltungs-Kandidaten prüfen — Splitter vs. Voll-Entität? |

## System-Inferences als erstklassige Objekte

`topicInference` erzeugt keine automatischen Fakten — es erzeugt **Vorschläge**:
- neues Thema
- neues Unterthema
- Themenverschiebung
- neue Raum-Bildung
- Abspaltung / Spawn

Jeder Vorschlag hat: `summary`, `confidence`, `accepted_by_admin`.
Admin akzeptiert / ablehnt / umbenennt / verschiebt.

> Die Plattform wird eine co-kuratierte Ontologie-Engine (System schlägt vor, Admin legitimiert).

## Loop-Timing

Konfigurierbar: 5 Minuten / 30 Minuten / dynamisch je nach Aktivität. Macht Agency zu einem tuneable Systemparameter.

## Das Grundprinzip

> Public = Outputs. Deep = Metabolism.

Die Background-Jobs sind das Organ, das Bedeutung verarbeitet — unsichtbar, aber strukturgebend.
