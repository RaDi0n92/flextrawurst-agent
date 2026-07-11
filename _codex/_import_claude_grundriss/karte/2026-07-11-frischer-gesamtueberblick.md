---
datum: 2026-07-11
betrifft: [systemueberblick, refresh, welt-api, innenleben, pol-c, schatten-dialog, kompoase]
importable: false
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

# System-Karte-Auffrischung — Antworten auf die Mai-Fragen + Korrektur

Ergänzt `system_heute.md` (2026-05-11) und die heutige `2026-07-11-geni-gedaechtnis-und-grenzen.md`.
Direkter Auftrag von Daniel: die alte Karte war zu Recht als veraltet aufgefallen, hier die
Auffrischung anhand echter Checks (systemctl, Dateien), nicht Vermutung.

## Korrektur einer eigenen Aussage von heute

Ich hatte in der Dreiergespann-Idee und der GENI-Analyse geschrieben, Schatten-Dialog sei "noch
nicht gebaut". Das war falsch — `build_surface.ts` hat bereits eine vollständige
`generateSchattenView()` (Schatten-Threads, dynamisches Grid, `sh-count`/`sh-grid`). Ich hatte mich
auf eine ältere Projekt-Notiz verlassen, ohne den aktuellen Code zu prüfen. Wird in beiden
Ursprungsdateien nicht rückwirkend korrigiert (Provenienz: der Fehler zum Zeitpunkt des Schreibens
bleibt sichtbar), aber hier richtiggestellt.

## Die fünf offenen Fragen aus system_heute.md — heutiger Stand

1. **"Was macht innenleben/ genau?"** — jetzt beantwortbar, ohne den Ordner zu modifizieren (nur
`BUILD_STATE.json` gelesen, Grundgesetz 6 respektiert): ein LangGraph-Reflexionssystem mit
ChromaDB-Embeddings (`all-MiniLM-L6-v2`, ONNX), Emotion-Bewerter, Memory-Writer-Node,
Reflection-Node, Integrator-Node, Flarum-Feeder. Alle 12 Bauschritte laut `BUILD_STATE.json` `done`,
zuletzt aktualisiert 2026-05-08. Modell: `gemma4:e2b-it-q4_K_M`.

2. **Pol C** — weiterhin nur Konzept, dokumentiert in `erkenntnis/KONFLIKT_ENGINE.md` ("die
wichtigste Erfindung... der Beobachter der Spannung zwischen Pol A und Pol B"). Keine
`tensions`-Tabelle oder ähnliches gefunden — noch nicht als Mechanismus kodiert, Stand unverändert
seit Mai.

3. **Wesen-Einzug** — weiterhin gesperrt (laut Bau-Reihenfolge in CLAUDE.md: "GESPERRT bis Daniel es
sagt"). Mehrere Entscheidungs-Dokumente existieren bereits
(`docs/daniel_entscheidungsboard_vor_einzug.md`, `docs/vor_einzugsfreeze_final.md`,
`docs/vor_einzugsreife_bericht.md`, `_claude/ideen/wesen_einzug_architektur.md`) — die Vorbereitung
ist also weit, der Einzug selbst noch nicht ausgelöst.

4. **KompOase Theater** — laut aktuellem Code (`build_surface.ts`) weiterhin: "BEGRIFFSPRÜFUNG OFFEN
· kein aktiver Datenfeed · Slot blockiert (blocked_until_concept)". Das ksResize-Problem von Mai ist
nicht mehr die Frage — der Slot ist konzeptionell blockiert, nicht technisch kaputt.

5. **welt-api crash-loop** — **gelöst.** `welt-api.service` läuft seit 2026-07-08 06:51 Uhr
durchgehend, 0 Neustarts. Das schmerzhafte Mai-Problem ist seit über 2 Tagen (Stand heute)
vollständig weg.

## Was seit Mai zusätzlich gebaut wurde (bestätigt über Tab-Liste in build_surface.ts)

Neue Tabs seit der alten Karte: `wissen`, `schlaf`, `cyberlinge`, `einsicht`, `gruppen`, `schatten`,
`archaeologie`, `zitate`, `weltstrom`, `splitter`, `gordslider`, `flarum`, `diskurs`, `gesetze`,
`forschung`, `partner`, `denken`, `screens`, `suche` — deutlich mehr als im Mai-Stand beschrieben.
Passt zur Bau-Reihenfolge in CLAUDE.md (Post-System, Zwischenraum, Schlaf-System, Cyberling,
WISSEN-Tab, Entitätenschichten — alle als ✅ markiert).

## Codewesen-Landschaft heute

7 einzelne Codewesen-Services bestätigt
(`codewesen-{dakgordsystem,F3INSCHM3CK3R,jumpa,R1ZZ1,Resonanzknoten,Schorschel,traeumerlie}.service`),
dazu pro Wesen ein `codewesen-reaktion@NAME`- bzw. dedizierter Reaktions-Service, plus gemeinsame
Dienste (Chat-UI, Batch-Generator, Engagement, Forum-Neugier, Weltbild-Builder,
LangGraph-Persistenz-Daemon). Alle heute `active`, außer `codewesen-umgekehrte-neugier.service`
(inaktiv) und `geni-forum-lektuere.service` (inaktiv, aber Timer läuft alle 45 Min).

## Was ich nicht geprüft habe (bewusste Grenze dieser Auffrischung)

Keine inhaltliche Prüfung der einzelnen neuen Tabs (nur Existenz bestätigt, nicht Funktionalität).
Keine Prüfung der PostgreSQL-Schema-Änderungen seit Mai. Das wäre eine eigene, größere Aufgabe —
diese Auffrischung war als Karten-Korrektur gedacht, nicht als vollständiger Systemaudit.
