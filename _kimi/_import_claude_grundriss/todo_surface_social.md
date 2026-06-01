---
datum: 2026-06-01
betrifft: [gruppen, meinewelt, websocket, feed, kalender, notizen, tagebuch, surface-social]
typ: todo
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

# To-Do: Surface Social-System Neubau

Basiert auf Kimis Masterplan + Daniels Entscheidungen vom 2026-06-01.
Beachtet: alle Grundgesetze, Surface-Gesetz, i18n-Gesetz, Backup-Pflicht.

---

## ⚠️ Vor jedem Bauschritt

- [ ] `git add -A && git commit -m "backup: vor [beschreibung]"`
- [ ] `python3 /root/werkraum/_claude/tools/ideen_scan.py [tag]` — passende Tags: `gruppen`, `meinewelt`
- [ ] Ergebnis lesen bevor Code geschrieben wird

---

## Phase 2a — Gruppen Backend + DB

### Schema
- [ ] `/root/werkraum/welt/schema_gruppen.sql` erstellen:
  - [ ] `ftw_gruppen` — id, name, slug (UNIQUE), beschreibung, sichtbarkeit (public/invite_only/hidden), avatar_url, created_by, created_at, updated_at, meta JSONB
  - [ ] `gruppen_mitglieder` — id, gruppe_id (FK), user_id, user_type (human/entity), rolle (admin/moderator/member), beigetreten_at, UNIQUE(gruppe_id, user_id, user_type)
  - [ ] `gruppen_chat_nachrichten` — id, gruppe_id (FK), autor_type, autor_id, content, created_at, meta JSONB
  - [ ] `ftw_posts`: `ALTER TABLE ftw_posts ADD COLUMN IF NOT EXISTS gruppe_id UUID REFERENCES ftw_gruppen(id)`
  - [ ] `ftw_posts`: `ALTER TABLE ftw_posts ADD COLUMN IF NOT EXISTS post_type TEXT DEFAULT 'post'`
  - [ ] Indizes: `idx_gruppen_posts`, `idx_gruppen_chat`, `idx_gruppen_mitglieder`
- [ ] Schema in Datenbank einspielen, prüfen ob bestehende Queries durch neue Spalten brechen

### REST-Backend (groups_api.py oder api.py)
- [ ] `GET /welt/gruppen` — Liste (search, limit, offset, sort, order) — Admin sieht alle, andere nur public + eigene
- [ ] `GET /welt/gruppen/{slug}` — Detail + Mitglieder + letzte 20 Posts als Baum
- [ ] `POST /welt/gruppen` — erstellen (nur Admin)
- [ ] `POST /welt/gruppen/{slug}/beitreten` — Auth required
- [ ] `POST /welt/gruppen/{slug}/verlassen`
- [ ] `POST /welt/gruppen/{slug}/posts` — Post in Gruppe (parent_id für Threading)
- [ ] `GET /welt/gruppen/{slug}/posts` — Feed als Baum (wiederverwendet `_build_antwort_tree`)
- [ ] `GET /welt/gruppen/{slug}/chat` — letzte N Nachrichten, cursor-basiert (`before` timestamp)
- [ ] `POST /welt/gruppen/{slug}/chat` — Nachricht senden (Auth required)
- [ ] Admin: `PATCH /admin/gruppen/{slug}` — Metadaten ändern, Mitglied-Rollen setzen, kick

### WebSocket-Backend
- [ ] `welt/ws_manager.py` — `ConnectionManager` Klasse:
  - [ ] `connect(websocket, gruppe_slug, user_id)` — registriert Verbindung
  - [ ] `disconnect(websocket, gruppe_slug)` — entfernt aus Raum
  - [ ] `broadcast(gruppe_slug, message)` — sendet an alle im Raum außer Sender
  - [ ] Internes Dict: `rooms: dict[str, set[WebSocket]]`
- [ ] `@app.websocket("/ws/gruppen/{slug}/chat")` in api.py oder groups_api.py:
  - [ ] JWT aus Query-Param (`?token=...`) verifizieren
  - [ ] Mitgliedschaft prüfen
  - [ ] Bei `message`-Event: in DB speichern + broadcasten
  - [ ] Bei `typing`-Event: nur broadcasten (nicht speichern), Server-Timeout 3s
  - [ ] Bei Disconnect: `manager.disconnect()`
- [ ] FastAPI benötigt `websockets` als Dependency — prüfen ob installiert

---

## Phase 2b — Gruppen Frontend

### Surface-Gesetz
- [ ] GRUPPEN-Tab onclick: `switchView('gruppen');gruppenLaden()` ergänzen (aktuell fehlt `gruppenLaden()`)
- [ ] `REQUIRED_VIEWS` in `tests/surface_ring_23.test.ts` — GRUPPEN-View prüfen ob bereits drin

### Gruppen-Liste (`gruppenLaden`)
- [ ] `GET /api/welt/gruppen` laden
- [ ] Karten-Grid: Avatar (Initiale als Fallback), Name, Mitgliederzahl, letzte Aktivität, Sichtbarkeits-Badge
- [ ] Hover: `border-color: var(--t-sub)` + `box-shadow` (0.15s)
- [ ] Klick → `gruppeRaumLaden(slug)`
- [ ] "Neue Gruppe" Button (nur Admin sichtbar)
- [ ] Empty-State: `◌` + "Noch keine Gruppen."
- [ ] i18n: alle Labels DE+EN

### Gruppen-Raum (`gruppeRaumLaden(slug)`)
**Layout: 3-Spalten-Grid (220px | 1fr | 280px)**
- [ ] CSS: `.gr-raum` mit `grid-template-columns: 220px 1fr 280px`
- [ ] Responsive Breakpoints:
  - [ ] `@media (max-width: 900px)`: 2 Spalten (Mitglieder ausblenden, Tab zum Einblenden)
  - [ ] `@media (max-width: 600px)`: 1 Spalte + Tab-Navigation (Feed | Chat | Mitglieder)
- [ ] Min-width constraints: keine Spalte unter 160px

**Linke Spalte — Mitglieder**
- [ ] Avatar + Name + Rolle-Badge (Admin=`--world`, Mod=`--t-mid`, Member=`--t-sub`)
- [ ] Online-Indikator: 2px grüner Punkt unten rechts am Avatar (via WS-Präsenz)
- [ ] Beitreten/Verlassen Button (Auth-abhängig)
- [ ] Admin: Mitglied kick + Rolle ändern (Dropdown on hover)

**Mittlere Spalte — Feed**
- [ ] Wiederverwendet `_dkThreadRender` aus Phase 1 — nur Datenquelle wechseln
- [ ] Post erstellen: Inline-Textarea mit Formatting-Toolbar (↓ Phase 3b)
- [ ] Entwurf-Button: `[Entwurf speichern]` vs `[Veröffentlichen]`
- [ ] Neuer Post: sanfter Highlight-Blitz (background `#0a1a2a → #030c14` über 1.5s, CSS `@keyframes`)
- [ ] Empty-State: `◌` + "Noch keine Posts in dieser Gruppe."

**Rechte Spalte — Chat**
- [ ] WebSocket-Verbindung aufbauen: `new WebSocket('wss://[domain]/api/ws/gruppen/{slug}/chat?token=[jwt]')`
- [ ] Reconnect-Logik:
  ```
  delays: [1s, 2s, 4s, 8s, 15s, 30s] dann alle 30s
  Status-Indicator im Chat-Header: ● Verbunden / ◌ Verbindet... / ✕ Getrennt
  ```
- [ ] Nachrichten laden beim Öffnen: `GET /api/welt/gruppen/{slug}/chat?limit=50`
- [ ] Neue Nachricht: WS-Event empfangen → `opacity 0→1` + `translateY(4px→0)` über 0.2s
- [ ] Eigene Nachrichten rechts, fremde links (Signal-Layout)
- [ ] Zeitstempel-Trenner: "Heute", "Gestern", Datum
- [ ] Optimistic UI: Nachricht erscheint sofort mit `opacity: 0.6` (pending), wird auf `1.0` gesetzt wenn Server bestätigt
- [ ] Typing-Indicator: WS-Event `{type: 'typing', user: '...'}` → "X schreibt..." anzeigen, nach 3s ausblenden
- [ ] Eingabefeld: `Shift+Enter` = neue Zeile, `Enter` = senden
- [ ] Chat-Scrollbar immer am Ende wenn neue Nachricht + User war unten (nicht scrollen wenn User hochgescrollt hat)

### i18n
- [ ] Alle neuen Strings in `UI_TR.de` + `UI_TR.en`
- [ ] Build: `⚠ i18n: N Keys ohne EN` darf nicht erscheinen

### Build + Deploy
- [ ] `npx tsx scripts/build_surface.ts`
- [ ] `npx tsx --test tests/surface_ring_23.test.ts` — grün
- [ ] `cp out/surface/flextrawurst_surface.html out/process_camera/flextrawurst_surface.html`

---

## Phase 2c — Gruppen Mitgliederverwaltung

- [ ] Einladungs-Link generieren (für `invite_only` Gruppen): Admin erstellt Token, Link enthält Token
- [ ] `POST /welt/gruppen/{slug}/einladen` — Token validieren + Mitglied hinzufügen
- [ ] Einladungs-UI: Admin-Bereich in der Gruppen-Einstellungen
- [ ] Gruppen-Einstellungen Modal: Name, Beschreibung, Sichtbarkeit, Avatar ändern (nur Admin)
- [ ] Admin-Sicht: alle Gruppen unabhängig von Sichtbarkeit

---

## Phase 3a — Meine Welt Backend

### Schema-Erweiterungen
- [ ] `ftw_posts`: `post_type` Feld (post | antwort | tagebuch | notiz | gruppen_post) — Migration prüfen ob `DEFAULT 'post'` bestehende Queries bricht
- [ ] `ftw_posts`: `post_status` Feld (published | draft) — für Entwurf-Funktion
- [ ] `ftw_posts`: `scheduled_for TIMESTAMPTZ` — für "Im Kommen" Feed-Kategorie
- [ ] Neue Tabelle `meine_termine` — id, user_id, titel, beschreibung, startzeit, endzeit, ort, farbe, meta JSONB
- [ ] Neue Tabelle `feed_markierungen` — id, user_id, item_type, item_id, markierung (irrelevant | gemerkt), created_at — für "Als irrelevant markieren" Feature
- [ ] Indizes: `idx_posts_type_autor`, `idx_termine_user`, `idx_feed_markierungen`

### API-Endpunkte
- [ ] `GET /welt/mein/feed` — Gemischter Feed:
  - [ ] Query-Param `kategorie` (alles | relevant | neu | im_kommen | irrelevant | zufällig)
  - [ ] **Relevant**: Posts aus Räumen+Gruppen wo User aktiv ist + @mentions des Users
  - [ ] **Neu**: Ungelesen, chronologisch DESC, letzten 48h
  - [ ] **Im Kommen**: `scheduled_for > NOW()` + Termine aus `meine_termine` in nächsten 7 Tagen
  - [ ] **Irrelevant**: Items aus `feed_markierungen` WHERE markierung='irrelevant'
  - [ ] **Zufällig**: `ORDER BY RANDOM() LIMIT 20` aus letzten 30 Tagen
  - [ ] **Alles**: UNION aller Kategorien, dedupliziert, gemischt
- [ ] `POST /welt/mein/feed/markieren` — Item als irrelevant/gemerkt markieren
- [ ] `GET /welt/mein/tagebuch` — eigene Posts mit `post_type='tagebuch'`, paginiert
- [ ] `POST /welt/mein/tagebuch` — neuer Eintrag (visibility='private', post_type='tagebuch')
- [ ] `PATCH /welt/mein/tagebuch/{id}` — Eintrag bearbeiten
- [ ] `GET /welt/mein/notizen` — eigene Posts mit `post_type='notiz'`, filter: tag, search
- [ ] `POST /welt/mein/notizen` — neue Notiz (post_type='notiz', visibility='private')
- [ ] `PATCH /welt/mein/notizen/{id}`
- [ ] `GET /welt/mein/kalender` — Param: `monat=2026-06` → Termine + System-Events als Monats-Grid
- [ ] `POST /welt/mein/kalender/termin` — neuer Termin
- [ ] `PATCH /welt/mein/kalender/termin/{id}`
- [ ] `POST /welt/mein/kalender/import` — `.ics` Datei parsen (`pip install icalendar`), Termine importieren
- [ ] `GET /welt/mein/kalender/export.ics` — eigene Termine als ICS exportieren (subscribe-Link)
- [ ] `GET /welt/mein/profil` — aggregierte Stats: Posts, Resonanzen, Gruppen, Folgen, ungelesene Items

---

## Phase 3b — Meine Welt Frontend

### MEINE WELT Tab
- [ ] Tab ist bereits vorhanden aber hidden — Login-Logik zeigt ihn (bereits implementiert)
- [ ] Tab onclick: `switchView('meinewelt');meineWeltLaden()` ergänzen
- [ ] Layout: 2-Spalten-Grid (180px Sidebar | 1fr Content)
- [ ] Sidebar: 5 Nav-Buttons (Feed | Tagebuch | Notizen | Kalender | Profil)
- [ ] Aktiver Nav-Button: `border-left: 2px solid var(--world)` + `color: var(--t-bright)`

### Formatting-Toolbar (wird in Tagebuch + Notizen + Gruppen-Feed genutzt)
**Implementierung mit Textarea + selectionStart/selectionEnd:**
- [ ] Toolbar-Komponente als wiederverwendbare Funktion `_ftwToolbar(textarea)`:
  - [ ] **Fett**: wrapp selection mit `<strong>...</strong>`
  - [ ] **Kursiv**: wrapp selection mit `<em>...</em>`
  - [ ] **Unterstrichen**: wrapp selection mit `<u>...</u>`
  - [ ] **Liste**: jede Zeile in selection mit `<li>` wrappen, umschließen mit `<ul>`
  - [ ] Buttons leuchten auf wenn Cursor in formatiertem Bereich (optional, Phase 2)
- [ ] Storage: Content als HTML in DB (sanitized beim Speichern — kein `<script>`)
- [ ] Render: `innerHTML` mit erlaubten Tags (strong, em, u, ul, li, p, br)
- [ ] Sanitizer-Funktion `_ftwSanitize(html)`: Whitelist-Approach, alles andere stripppen

### Feed (`mwFeedLaden`, aktive Kategorie)
- [ ] Auto-Refresh: `setInterval(mwFeedRefresh, 10000)` — nur neue Items prependen, nicht alles neu rendern
- [ ] Refresh-Strategie: `GET /api/welt/mein/feed?nach=<letzter_timestamp>` — nur was neu ist
- [ ] "N neue Einträge" Chip oben erscheint wenn neue Items kamen, klicken zum Einblenden
- [ ] Filter-Chips: `[Alles] [Relevant] [Neu] [Im Kommen] [Irrelevant] [Zufällig]`
  - [ ] Aktiver Chip: `border: 1px solid var(--world)`, `color: var(--t-bright)`
  - [ ] Chip-Wechsel: Feed neu laden, Chip-State speichern in `localStorage`
- [ ] Feed-Einträge: Staggered fade-in (0.05s Delay pro Eintrag, max 10 Einträge gestaggert)
- [ ] Hover-Action per Eintrag: `[Als irrelevant]` Button erscheint rechts (opacity 0 → 0.7)
- [ ] "Als irrelevant markieren" → `POST /api/welt/mein/feed/markieren` → Item bekommt `opacity: 0.3` + wandert bei nächstem Reload in Irrelevant-Kategorie
- [ ] Gruppierung: "HEUTE", "GESTERN", "DIESE WOCHE", "ÄLTER" (Labels: `font-size: 0.55rem`, `letter-spacing: 0.15em`, uppercase)
- [ ] Empty-State pro Kategorie: "◌ Nichts Relevantes gerade." / "◌ Alles gelesen." / etc.

### Tagebuch (`mwTagebuchLaden`)
- [ ] Zeitstrahl-Layout: `.mw-tl-linie` vertikal links, `.mw-tl-punkt` pro Eintrag
- [ ] Monat-Jumper oben: `‹ Juni 2026 ›`
- [ ] Einträge: aufklappbar (max-height transition 0.3s ease)
- [ ] Neueintrag: Floating-Button unten rechts (`position: fixed`, `bottom: 24px`, `right: 24px`)
- [ ] Inline-Editor mit Formatting-Toolbar beim Öffnen des Editors
- [ ] Entwurf: "Entwurf" Badge am Eintrag wenn `post_status='draft'`
- [ ] Datum-Anzeige: `"Montag, 1. Juni 2026"` + relative Zeit wenn heute (`"Vor 2 Stunden"`)

### Notizen (`mwNotizenLaden`)
- [ ] Masonry-Grid: `grid-template-columns: repeat(auto-fill, minmax(200px, 1fr))`
- [ ] Farbe beim Erstellen: zufällig aus c-1..c-5 wählen, in `meta.farbe` speichern
- [ ] Hover: `translateY(-2px)` + `box-shadow: 0 4px 12px rgba(0,0,0,0.3)` (0.15s ease)
- [ ] Tags: kleine Chips unter dem Text, klickbar → filtert Grid
- [ ] Schnellsuche: Debounced Input (300ms) → filtert Grid client-seitig (bei <50 Notizen) oder server-seitig
- [ ] Neue Notiz: Floating-Button + inline Modal mit Toolbar
- [ ] Bearbeiten: Klick auf Zettel öffnet Editor
- [ ] Empty-State: `◌` + "Noch keine Notizen. Die Wand ist leer."

### Kalender (`mwKalenderLaden`)
- [ ] Monats-Grid: `grid-template-columns: repeat(7, 1fr)`, 1px Gap auf `var(--rim)` Background
- [ ] Wochentag-Header: Mo–So, `font-size: 0.52rem`, `color: var(--t-dim)`
- [ ] Heutiges Datum: `outline: 1px solid var(--world)`, `outline-offset: -1px`
- [ ] Termine: farbige Blöcke in Tageszellen (Farbe aus Termin-Metadaten)
- [ ] Anderer Monat: `background: #02060a`, Datum-Zahl `opacity: 0.3`
- [ ] Monatswechsel: Crossfade zwischen Grids (0.2s)
- [ ] Klick auf Tag: Tagesansicht als Overlay — Termine in Zeitstrahl
- [ ] `[+ Termin]` Button pro Tag (erscheint bei Hover)
- [ ] ICS-Import: File-Input Button `[.ics importieren]` → `POST /api/welt/mein/kalender/import`
  - [ ] Nach Import: Erfolgs-Feedback "N Termine importiert"
  - [ ] Fehler-Feedback bei ungültiger Datei
- [ ] Kalender-Abo: `[Kalender-Link kopieren]` → URL zu `GET /api/welt/mein/kalender/export.ics?token=...`
- [ ] System-Events im Kalender (Wesen-Aktivitäten etc.) als speziell markierte Items

### Profil (`mwProfilLaden`)
- [ ] Header: Avatar + Username + Beitrittsdatum
- [ ] Stats-Row: Posts geschrieben | Resonanzen gegeben | Resonanzen erhalten | Gruppen
- [ ] Tabs: Posts | Resonanzen | Gruppen | Folgen
- [ ] Stats-Zahlen: `font-size: 1.4rem`, `color: var(--t-bright)`, `font-family: monospace`

### i18n + Build
- [ ] Alle neuen Strings DE+EN
- [ ] Build + Tests + cp

---

## Phase 4 — Design-System & Polish

### `switchView()` Enhancement
- [ ] Aktuelle Funktion (Zeile 10307) erweitern um Fade-Animation:
  - [ ] Current div: `opacity 0` über 0.15s, dann `display:none`
  - [ ] Next div: `display:block`, dann `opacity 0→1` über 0.2s
  - [ ] `requestAnimationFrame` für smooth Transition
- [ ] Scroll-Position-Memory: `_viewScrollPositions = {}` — speichern beim Leave, restore beim Enter
- [ ] `prefers-reduced-motion`: alle Transitions nur wenn `!window.matchMedia('(prefers-reduced-motion)').matches`

### Loading + Empty States
- [ ] `.ftw-loading` Pattern (Puls-Dot, `@keyframes ftw-pulse`) — überall einsetzen wo noch `innerHTML = 'Lädt...'`
- [ ] `.ftw-empty` Pattern (`◌` Icon + Text) — überall einsetzen wo noch leere divs
- [ ] Alle bestehenden Views auditieren: DISKURS, RAUME, WESEN, BLASEN, SCHATTEN, SPLITTER, ZITATE — überall Loading/Empty ergänzen

### Mikro-Interaktionen
- [ ] `button:active { transform: translateY(0.5px); }` — global
- [ ] `.ftw-karte` Hover: `translateY(-1px)` + `box-shadow` — für alle Karten-Komponenten
- [ ] Scrollbar-Styling: 6px, `var(--t-dim)` Thumb, transparent Track

### Touch + Responsive
- [ ] `@media (pointer: coarse)`: min-height 44px für alle interaktiven Elemente
- [ ] Swipe-Gesten für Tab-Navigation (mobile): `touchstart/touchend` Delta > 50px → nächster/vorheriger Tab

### Fehler-States
- [ ] Rote Akzentfarbe: `#3a1010` background + `#a04040` border — nicht blinkend
- [ ] Netzwerk-Fehler: Toast-Notification unten rechts (3s), nicht modal

---

## Querschnitt — gilt für jede Phase

- [ ] Backup-Commit **vor** jeder Änderung
- [ ] `ideen_scan.py` vor Baustart
- [ ] Alle neuen Texte: `data-i18n` + `UI_TR.de` + `UI_TR.en`
- [ ] Neue Views: in `REQUIRED_VIEWS` (surface_ring_23.test.ts) eintragen
- [ ] Nach jedem Build: `cp out/surface/... out/process_camera/...`
- [ ] Neue Endpunkte: `search`, `limit`, `offset`, `sort`, `order` — Grundgesetz 2
- [ ] Events-Tabelle: jede bedeutsame Aktion schreibt ein Event (gruppen.erstellt, gruppe.beigetreten, etc.)
- [ ] Nichts löschen — nur deaktivieren (visibility='hidden' oder is_active=false)
- [ ] Nach der Phase: Session-Notiz + Resonanzfeld-Update

---

## Empfohlene Session-Aufteilung

| Session | Inhalt | Geschätzt |
|---------|--------|-----------|
| **A** | Phase 2a (DB + REST + WebSocket-Backend) + Phase 2b (Gruppen Frontend) | 4–5h |
| **B** | Phase 2c (Mitgliederverwaltung) + Phase 3a (Meine Welt Backend) + 3b Feed+Tagebuch | 4–5h |
| **C** | Phase 3b Notizen+Kalender+Profil | 3–4h |
| **D** | Phase 4 Polish — fertig | 2h |

---

## Offene Kleinigkeiten (aus Phase 1)

- [ ] @-mention Namensauflösung im Diskurs (aktuell: Alert-Fallback)
- [ ] Quote-Rendering (`> ` → visuelle Einrückung)
- [ ] Erste Testdaten mit Tiefe ≥ 2 im Diskurs-Thread

---

*Letztes Update: 2026-06-01 — alle Designentscheidungen von Daniel eingetragen.*
