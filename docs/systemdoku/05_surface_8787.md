---
titel: Surface — Port 8787
typ: technik
erstellt: 2026-05-26
autor: claude-code bei Daniels VPS
---

# Surface — Port 8787

[[INDEX|← Index]]

**URL:** `http://localhost:8787` (oder extern via VPS-IP)  
**Service:** `flextrawurst-surface.service`  
**Server:** Node.js, `scripts/serve_process_camera_preview.ts`  
**WorkDir:** `/root/flextrawurst`

---

## Was Port 8787 wirklich ist

Kein Framework. Ein eigener HTTP-Server (`serve_process_camera_preview.ts`) der statische Dateien ausliefert UND als Proxy für Werkraum-Dateien dient.

```typescript
// serve_process_camera_preview.ts — Kern-Logik:
const PORT = 8787;
const WERKRAUM_ROOT = "/root/werkraum";

// Authentifizierung via Basic Auth (WERKRAUM_PASSWORD env)
// Serviert:
// - /root/flextrawurst/out/surface/flextrawurst_surface.html
// - /root/flextrawurst/out/process_camera/*
// - /root/flextrawurst/public/*
// - Werkraum-Dateien via /werkraum/<relativpath>
// - Obsidian-Links prependen via POST /prepend-link
```

---

## Dateien auf Port 8787

```
/root/flextrawurst/
├── out/
│   ├── surface/
│   │   └── flextrawurst_surface.html   ← Haupt-Surface (7147 Zeilen)
│   └── process_camera/
│       ├── dakgord_live.json            ← Live-Daten dak+gord
│       ├── flextrawurst_surface.html    ← (Duplikat?)
│       ├── kompOase_datafield.html
│       ├── kompOase_vorform.html
│       ├── kompoase.html
│       ├── process_camera_model.json
│       ├── process_camera_worldblick.html
│       ├── system_heute.html
│       └── werkraum_explorer.html
└── public/
    ├── welt.html                        ← Erste öffentliche Menschenseite
    ├── blasenfeld.html
    ├── google42fa1b893589fc41.html
    ├── robots.txt
    └── sitemap.xml
```

---

## Die Surface (flextrawurst_surface.html)

7147 Zeilen HTML. 13 Tabs. Verbindet sich direkt mit der Welt-API (Port 8030).

### Alle Tabs

| Tab | data-view | data-live | Status | Beschreibung |
|-----|-----------|-----------|--------|--------------|
| LEITSTAND | `leitstand` | ✓ | live | System-Überblick, Weltzustand-Visualisierung |
| WAS IST DAS? | `uber` | — | statisch | Erklärung des Systems (Standard-Tab beim Laden) |
| RÄUME | `raume` | — | statisch | Weltstruktur: alle 5 Räume |
| DISKURS | `diskurs` | ✓ | **aktuell gebaut** | Post-System mit vollem Feature-Set |
| WESEN | `wesen` | — | statisch | Die 6 Wesen + dak+gord |
| KOMPOASE | `theater` | ✓ | Theater-Modus | Splitter-Feld, 25 Theater-Gedanken |
| BLASEN | `blasen` | ✓ | Theater-Modus | Gedankenblasenfeld |
| MENSCHEN | `menschen` | ✓ | live | Menschenprofile |
| MEINE WELT | `meinewelt` | — | hidden | Persönliche Welt (noch nicht aktiviert) |
| SCHLAF | `schlaf` | ✓ | live | Schlaf-System der Entitäten |
| SYSTEME | `systeme` | ✓ | live | System-Status aller Services |
| ADMIN | `admin` | — | hidden | Nur für Admin (Nutzer, Bewerbungen, Moderation) |
| WISSEN | `wissen` | — | statisch | Wissensarchiv |

`data-live="1"` = Tab pollt live Daten von der Welt-API.

---

## DISKURS-Tab — was live funktioniert

Die letzten 5 Commits auf `/root/flextrawurst` zeigen was der Diskurs-Tab kann:

```
3e48bab fix: Diskurs -- Inbox-Feldname, POST->PATCH, Beitraege-Optik, Emoji-Preselect, Schatten-Edit/Delete, Topbar-Badges DM+Notif
8682aca feat: DISKURS -- Beiträge-Fix, Ungelesen-Dots, Folgen-Buttons, Inbox-Panel
cfc465a feat: Diskurs -- Antworten-UI, Emoji-Resonanzen, reply_count, Suche-Filter-Fix
44895f2 fix: Diskurs -- doppeltes Bearer-Prefix, exakte Zeitangaben, Counts immer sichtbar, Autorenname
1d14074 feat: Diskurs — Suche, Pagination, Ähnliche Beiträge, Token-Fehler, view_count
```

**Fertig implementiert:**
- Post-Liste mit Suche, Paginierung, Sortierung
- Post-Detail-Ansicht mit Antwort-Thread
- Emoji-Resonanzen auf Posts (mit Preselect der eigenen Reaktion)
- Ähnliche Beiträge (Similarity-Daemon)
- Inbox-Panel (DMs und Benachrichtigungen)
- Folgen-Buttons für Räume und Themen
- Ungelesen-Dots auf Tab-Buttons
- Topbar-Badges für DM-Count und Notification-Count
- Schattenkommentare (Edit/Delete)
- Exakte Zeitangaben, Autorname

---

## KOMPOASE-Tab — Theater-Modus

Die Welt ist bewusst leer geräumt. Stattdessen: 25 handgeschriebene Theater-Gedanken.

```
Theater-Modus AN (seit 2026-05-12)
- KompOase: 25 handgeschriebene Theater-Gedanken
- Blasenfeld: 25 Theater-Blasen
- DB-Stand: splitter, gedankenblasen, splitter_verbindungen alle (fast) leer
  → Nur echte Einträge wenn echtes Leben entsteht
```

---

## Topbar-Navigation

```html
<!-- Topbar hat Badges für DMs und Notifications -->
<button onclick="diskursNotifsOeffnen()" title="Neuigkeiten aus gefolgten Räumen/Themen">
  🔔 <span id="top-notif-cnt">...</span>
</button>
```

---

## TypeScript-Kernel (nicht die Surface)

Der Kernel in `/root/flextrawurst/kernel/` ist **nicht** die Surface. Er ist die konzeptuelle Schicht:

```
/root/flextrawurst/
├── kernel/src/     ← TypeScript-Quellcode (Ringe 1–20)
├── tests/          ← 1336 Tests (alle grün)
├── RING_INDEX.md   ← Ring-Tabelle
└── HANDOFF_CAPSULE.md
```

### Ring-Tabelle (Stand: Ring 21 aktiv)

| Ring | Name | Status |
|------|------|--------|
| 00–12 | Konzept- & Plandokumente | doku |
| 1 | World Engine Core | implementiert |
| 2 | Scenario Inspection | implementiert |
| 3 | World OS Spine | implementiert |
| 4–12 | Import Console bis Readiness Pack | doku/impl |
| 13 | World Inspection Export | implementiert |
| 14 | Static Worldview Preview | implementiert |
| 15 | First WorldBlick CLI | implementiert |
| 16 | Organ Dock Blueprints | implementiert |
| 17 | Admin Feature Control | implementiert |
| 18 | Diskursarchäologische Suche | implementiert |
| 19 | World Run Control Locks | implementiert |
| 20 | Global Governance | implementiert |
| **21** | **Build Discipline** | **aktiv (Doku-Phase)** |

**Aktuelle Sperren (Ring 21):**
- Keine Organe aktivieren
- Kein AI-Subsystem, kein Postgres
- Keine UI außer Prozesskamera (geplant)
- FeatureSlots bleiben deaktiviert

---

## Weltstruktur-Karte (aus dem LEITSTAND-Tab)

Der LEITSTAND zeigt eine SVG-Visualisierung der Welt mit Zonen:
- `diskursarchiv` — lila (`#aa55cc`)
- weitere Zonen: Vertrauen, Zwischenraum, Identität, Resonanz, Autonomie

---

## Zwei Surface-Dateien: Werkraum vs. Kernel

| Datei | Pfad | Aktuell |
|-------|------|---------|
| Werkraum-Surface | `/root/werkraum/flextrawurst/flextrawurst_surface.html` | Entwicklungsversion |
| Kernel-Surface | `/root/flextrawurst/out/surface/flextrawurst_surface.html` | Gebaute Version (vom Server ausgeliefert) |

Die Werkraum-Version ist das "Labor". Die Kernel-Version wird über `npx tsx scripts/build_surface.ts` gebaut.

---

## Nachtrag 2026-07-10 — FLARUM-Tab: erst Link, dann echtes Iframe-Embed

Daniel wollte das echte, laufende Flarum als Tab in der öffentlichen Surface erreichbar machen. Erste Umsetzung war ein reiner ausgehender Link (`target="_blank"`) — bewusst risikofrei, aber von Daniel direkt korrigiert: *"nein kein neuer browsertab....so wie gordslider"*. Zweiter, finaler Anlauf: echtes Iframe-Embed, inklusive Config-Änderung an der laufenden Flarum-Instanz (Risiko von Daniel bewusst akzeptiert). Volle technische Begründung, Backup-Pfade und Verifikation stehen in [[06_flarum]] — hier nur der Kurzverweis, damit diese Datei nicht doppelt pflegen muss.

**Kurz:** `generateFlarumView()` (Iframe-Wrapper wie `generateGordsliderView()`), Tab läuft jetzt über `switchView('flarum')` wie alle internen Views, `/flarum-live/`-nginx-Proxy zu Flarums eigenem `217.154.14.29:80`-Server-Block, Flarums `config.php`-Basis-URL entsprechend angepasst. Dabei einen echten Bug im gemeinsamen `switchView()` gefunden und gefixt: die hartkodierte `views`-Liste kannte `'flarum'` nicht, der Tab aktivierte sich visuell, zeigte aber keinen Inhalt.

---

## Nachtrag 2026-07-21 — WESEN-Tab: Solarius/Codexium (v1) entfernt, dabei toten Spawner-Script-Block gefixt

Daniel wollte die alten "+ Solarius ↗"/"+ Codexium ↗"-Buttons und die zugehörigen Karten aus dem WESEN-Tab raus — `codexium2`/`solarius2` sind die aktiven Nachfolger (siehe [[21_wesen_chat_testbed]]), `codexium`/`solarius` (v1) sollen laut [[project_codexium2_testbed]]-Konvention unangetastet, aber eben nicht mehr sichtbar sein.

Zwei Stellen in `generateWesenView()` (`build_surface.ts`): die zwei statischen Buttons entfernt, und im `ladeSpawnedWesen()`-Script (das `/wesen/list` abfragt und Karten pro gespawntem Wesen baut) einen Filter ergänzt (`w.spawner!=='solarius'&&w.spawner!=='codexium'`).

**Dabei aufgefallen:** Dieses Script war der bereits früher dokumentierte "bekannte Nebenfund" aus der Ankündigungen-Session desselben Tages ([[24_ankuendigungen]]) — derselbe Backtick-Template-Escape-Bug (`\'` wird beim Bauen aufgelöst, bevor der Code in die Ausgabedatei geschrieben wird, bricht die String-Syntax). Ergebnis: Der komplette Script-Block war seit Ewigkeiten kaputt, `ladeSpawnedWesen()` lief nie — die Karten-Liste zeigte permanent nur "Lade…", nur die beiden jetzt entfernten statischen Buttons waren der tatsächlich funktionierende Weg zu Solarius/Codexium. Gefixt mit derselben Technik wie beim Ankündigungen-Fix (Fragmente wie `"'none'"`/`"'"` statt Backslash-Escapes). Alle 22 Script-Blöcke der ausgelieferten Surface sind jetzt syntaktisch sauber (vorher 1 kaputt).

Live per Playwright verifiziert: Karten-Liste lädt jetzt tatsächlich (vorher dauerhaft "Lade…"), zeigt `solarius2`/`codexium2`-Einträge, keine `solarius`/`codexium`-Einträge mehr, keine JS-Fehler.

---

## Nachtrag 2026-07-22 — Erlebnisschicht: derselbe Backtick-Template-Escape-Bug ein drittes Mal, diesmal bei Regex-Sonderzeichen

Nach dem Ankündigungen-Fix und dem WESEN-Tab-Spawner-Fix (beide oben dokumentiert) jetzt derselbe strukturelle Bug ein drittes Mal, unabhängig gefunden — diesmal nicht bei `\'`-String-Escapes, sondern bei Regex-Metazeichen (`\s`, `[\s\S]`).

**Symptom:** Daniel meldete, dass Ich-Stimme/Erzähler-Popups im SCREENS-Denkfenster (Erlebnisschicht, siehe `_claude/ideen/erlebnisschicht_erzaehler_mitdenker_fragensteller.md`) trotz mehrfacher Fixes nie erschienen. Debug-Instrumentierung zeigte: der GEDANKE-Extraktions-Text blieb immer leer, obwohl der Rohtext nachweislich (per direkter DB-Abfrage) korrekt ankam.

**Ursache identisch zum bekannten Muster:** `_erlVerarbeiteDenkstreamChunk`/`_erlZerlegeSaetze` liegen (wie praktisch der gesamte Surface-Script-Code) innerhalb der einen großen JS-Template-Literal-Rückgabe von `generateGruppenView()` — eine einzige Backtick-Zeichenkette von Zeile ~8650 bis ~10259. Wird `build_surface.ts` per `tsx` ausgewertet, interpretiert die JS-Engine selbst diese Zeichenkette, **bevor** sie als Text in die HTML-Ausgabe geschrieben wird. Ein einfacher Backslash vor einem nicht-reservierten Zeichen (`\s`, `\S` in `[\s\S]`) ist in JS-String-/Template-Literalen ein stilles, gültiges Escape: der Backslash verschwindet ersatzlos, ohne Fehler oder Warnung (`\s` → `s`). Ausgeliefert wurde dadurch `/GEDANKE:s*([sS]*?).../` statt `/GEDANKE:\s*([\s\S]*?).../` — eine Regex, die nie sinnvoll matcht.

**Fix-Muster (gilt für jeden künftigen Fall):** Jeder Backslash, der in diesem eingebetteten Script-Bereich tatsächlich beim Browser als ein einzelner Backslash ankommen soll — egal ob String-Escape (`\'`) oder Regex-Metazeichen (`\s`, `\d`, `\w`, `\n` als Regex statt als String) — muss im `.ts`-Quelltext **doppelt** geschrieben werden (`\\s`). Bereits bestehender, funktionierender Code an derselben Stelle macht das schon richtig (`tok.replace(/^Bearer\\s+/,'')`) — das ist der Beleg, dass es kein Einzelfall-Sonderfix war, sondern die einzig korrekte Schreibweise für JEDEN neuen String/Regex innerhalb dieses Template-Literal-Bereichs.

**Fazit / Warnung für künftige Sessions:** Dieser Bug ist jetzt dreimal unabhängig aufgetreten (Ankündigungen, WESEN-Tab-Spawner, Erlebnisschicht) — kein Zufall, sondern eine strukturelle Falle der aktuellen Bauweise (riesiger Script-Block als literaler Text in einem TS-Template-Literal). Bei JEDER neuen Zeile Code, die innerhalb einer `return \`...\`-Funktion in `build_surface.ts` neu geschrieben wird und einen Backslash enthält (String-Escape ODER Regex): sofort doppelt schreiben, nicht erst beim Debuggen draufkommen. Nach jedem Build lohnt sich außerdem eine Stichprobe im ausgelieferten `out/surface/flextrawurst_surface.html` (`grep` nach der neu geschriebenen Regex/dem String), um zu sehen, ob die Backslashes wirklich angekommen sind.

Fix committed (`8dbf03f41`), live per Playwright verifiziert (Ich-Stimme-Popup erschien nach echtem Denkstream-Zyklus). Volle Fehlersuche inkl. Node-Simulation gegen echte DB-Daten: siehe `_claude/ideen/erlebnisschicht_erzaehler_mitdenker_fragensteller.md`, Abschnitt "Nachtrag — 'bauen'".

---

*Weiter: [[06_flarum]] | [[07_codewesen_uebersicht]]*
