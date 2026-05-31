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

*Weiter: [[06_flarum]] | [[07_codewesen_uebersicht]]*
