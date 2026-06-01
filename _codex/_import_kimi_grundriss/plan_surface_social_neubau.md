---
datum: 2026-06-01
betrifft: [flextrawurst, surface, diskurs, gruppen, meinewelt, design]
autor: kimi bei Daniels VPS
status: plan
---

# Surface-Social-Systeme: Kompletter Neubau — Bauplan

## Kontext

Daniel ist mit den drei sozialen Bereichen maximal unzufrieden:
- **Diskurs**: "Flach wie ein Brett" — kein Threading, keine Nested Replies, kein Zitieren, keine @-Mentions, kein Rich-Text. Fühlt sich an wie ein Gästebuch von 1998.
- **Gruppen**: "Ein Verzeichnis, kein Erlebnis" — Overlay zeigt Name+Beschreibung+Mitgliederzahl, dann nichts. Kein Feed, keine Timeline, kein Chat, keine Aktivität.
- **Meine Welt**: "Ein Menü, kein Dashboard" — Acht Karten öffnen ein Panel. Keine Übersicht, kein Activity-Feed, kein "was ist neu".

Ziel: **"2033 style"** — sauber, durchdacht, lebendig, nicht steril, nicht 1999-CRUD.

---

## Design-Prinzipien (gilt für alle drei Bereiche)

1. **Räume statt Views** — Jeder Bereich ist ein Raum, nicht eine Datenbank-Tabelle
2. **Visuelle Tiefe** — Nesting, Verschachtelung, Baumstrukturen statt flacher Listen
3. **Animation als Zustand** — Übergänge fließend, nicht hart; Scroll-Trigger, nicht Blinken
4. **Alles hat Status** — LIVE / DEMO / PRINZIP / GEPLANT / SPÄTER / BLOCKIERT (Vision-Kompass)
5. **Alles hat Herkunft** — Inspector, Provenienz, keine anonymen Daten
6. **Kein CRUD** — Keine "Erstellen/Bearbeiten/Löschen"-Formulare. Stattdessen: Fließende Aktionen, Inline-Editing, Wizards
7. **Dark & Lebendig** — Tiefe Farben, Glow-Effekte, aber lesbar (das Lesbarkeits-Redesign bleibt Basis)

---

## Phase 1: Diskurs-Neubau

### Was existiert (Ist-Zustand)
- Navigation: Foyer → Raum → Thema (Faden) → Post-Detail
- Posts als `.dk-faden-post` flach im Thema, paginiert (10er Seiten)
- Antworten als `.dk-antw-item` mit `border-left: 2px` — flache Liste, kein Nesting
- Detail-View zeigt: Titel, Body, Meta, Spuren, Emoji-Reactions, Schattenkommentare, ähnliche Posts, Relationen
- Breadcrumb-Navigation, keine echte Thread-Ansicht
- API: `post_antworten_lesen`, `post_antwort_erstellen`, `_build_antwort_tree` (Backend hat bereits Baum-Logik!)

### Was gebaut wird

#### 1.1 Nested Threading (Visueller Baum)
- **Konzept**: Reddit-Style Threading, aber eleganter
- **Visual**: Jede Antwort hat einen vertikalen Strich links (wie jetzt, aber mit Tiefen-Farbverlauf)
- **Tiefe**: Max 5 Ebenen, dann "Weiter im Thread →" Link
- **Interaction**: Klick auf "X Antworten" klappt Thread auf/zu (wie Reddit)
- **Animation**: Slide-down mit `max-height` Transition, 0.2s ease
- **Code**: `_build_antwort_tree` im Backend existiert bereits! Wir müssen es nur richtig rendern.

#### 1.2 Zitate (Quotes)
- **Konzept**: Klick auf "Zitieren" bei jedem Post → Zitat wird in Editor eingefügt
- **Visual**: Zitat als abgerundete Box mit linker Border (wie Blockquote, aber stilisiert)
- **Format**: `> @autor: "ausgewählter Text"`
- **Interaction**: Text selektieren → "Zitieren"-Button erscheint → Klick öffnet Antwort-Formular mit Zitat

#### 1.3 @-Mentions
- **Konzept**: Typ `@` im Editor → Autocomplete-Dropdown mit Nutzern/Wesen
- **Visual**: Dropdown unter Cursor, dunkler Hintergrund, Avatar/Symbol + Name
- **Data**: API-Endpunkt `/api/users/search?q=` (existiert wahrscheinlich schon)
- **Rendering**: Im Text werden @-Mentions als Links gerendert (unterstrichen, farbig)

#### 1.4 Rich-Text (Markdown-Lite)
- **Konzept**: Kein WYSIWYG-Editor. Stattdessen: Live-Preview unter dem Textfeld
- **Features**: Bold (`**text**`), Italic (`*text*`), Links, Zitate (`>`), Code-Blocks (`` ``` ``)
- **Visual**: Editor = Plain-Textarea. Darunter Live-Preview in kleinerer Schrift
- **Toolbar**: Optional minimale Toolbar über dem Feld (B, I, Quote, Code)

#### 1.5 Conversation-Flow
- **Konzept**: Posts sind nicht isoliert. Sie sind Knoten in einem Gesprächsfluss.
- **Visual**: Im Post-Detail sieht man den "Kontext" — den Parent-Post und die direkten Antworten
- **Neue Ansicht**: "Thread-Ansicht" neben der aktuellen Listen-Ansicht
- **Thread-Ansicht**: Ein einzelner Post mit allen Antworten als Baum, unendlich scrollend

#### 1.6 Post-Detail Redesign
- Aktueller Detail-View ist gut, aber zu isoliert
- **Neu**: Split-View auf Desktop — Links: Post, Rechts: Thread-Baum
- **Neu**: "Im Kontext lesen"-Button → zeigt den Post im Thread-Baum
- **Neu**: Schnell-Antwort direkt unter dem Post (Inline, nicht auf neuer Seite)

### API-Änderungen (Backend)
- `_build_antwort_tree` existiert bereits — prüfen ob es vollständig ist
- `post_antworten_lesen` erweitern um `?format=tree` Parameter
- Neuer Endpunkt: `/api/welt/posts/{id}/thread` → gibt Post + nested replies als Baum
- @-Mentions: Suche-Endpunkt erweitern oder neuen `/api/users/mention?q=` anlegen

### CSS-Änderungen
- Neue Klassen: `.dk-thread-tree`, `.dk-thread-branch`, `.dk-thread-node`, `.dk-thread-line`
- Neue Klassen: `.dk-quote`, `.dk-mention`, `.dk-richtext-preview`
- Farbverlauf für Thread-Tiefen: S0=#1a4a5a, S1=#2a5a6a, S2=#3a6a7a, S3=#4a7a8a, S4=#5a8a9a
- Animationen: `transition: max-height 0.25s ease, opacity 0.2s ease`

---

## Phase 2: Gruppen-Neubau

### Was existiert (Ist-Zustand)
- Fangruppen: 6 hartkodierte Karten für die Wesen
- Weitere Gruppen: Grid von Karten, geladen von `/api/groups`
- Detail-Overlay: Name, Beschreibung, Typ, Visibility, Mitgliederliste, Beitreten-Button
- Admin: Bearbeiten/Löschen per Prompt-Dialog
- Erstellen: Prompt-Dialog (Name, Typ, Beschreibung)
- **Kein Feed, KEIN Chat, KEINE Timeline, KEINE Posts in der Gruppe**

### Was gebaut wird

#### 2.1 Gruppen-Feed / Timeline
- **Konzept**: Jede Gruppe hat einen Activity-Feed
- **Visual**: Chronologische Liste von Events — Posts, Umfragen, Mitglieder-Beitritte, System-Nachrichten
- **Design**: Wie ein vereinfachter Diskurs-Faden, aber für Gruppen-Inhalte
- **API**: Neue Tabelle `group_posts` oder `ftw_posts` erweitern um `group_id`
- **Events**: Append-only, wie im Grundgesetz

#### 2.2 Gruppen-Chat (Lightweight)
- **Konzept**: Nicht vollständiger Discord-Chat, sondern "Schnell-Nachrichten"
- **Visual**: Fixierter Eingabebereich unten, Nachrichten oben
- **Unterschied zu Diskurs**: Chat = kurze Nachrichten, kein Titel, kein Threading (oder nur 1 Ebene)
- **Integration**: Chat-Nachrichten sind auch im Feed sichtbar

#### 2.3 Umfragen (Admin)
- **Konzept**: Admin kann in einer Gruppe eine Umfrage erstellen
- **Visual**: Eingebettet im Feed, mit Balken-Diagramm für Ergebnisse
- **Features**: Multiple-Choice, Zeitlimit, anonym/öffentlich
- **API**: Neue Tabelle `group_polls` + `group_poll_votes`

#### 2.4 Raumerstellung (Wizard, nicht Formular)
- **Konzept**: Keine Prompt-Dialoge mehr. Stattdessen: Schritt-für-Schritt-Wizard
- **Schritt 1**: Name + Beschreibung (mit Live-Vorschau)
- **Schritt 2**: Typ wählen (mit Erklärung)
- **Schritt 3**: Visibility + Regeln
- **Schritt 4**: Bestätigen + Erstellen
- **Visual**: Slide-In Panel von rechts, wie ein Inspector

#### 2.5 Bild-Uploads
- **Konzept**: In Gruppen-Posts und Chat können Bilder hochgeladen werden
- **Visual**: Thumbnails im Feed, Lightbox beim Klick
- **API**: Erweiterung des bestehenden Upload-Systems
- **Constraints**: Max 5MB, WebP/JPEG/PNG, keine Personenabbildungen (bestehende Regel)

#### 2.6 Fangruppen-Redesign
- **Konzept**: Fangruppen sind nicht mehr hartkodierte leere Schalen
- **Neu**: Wenn ein Wesen eingezogen ist, wird die Fangruppe lebendig
- **Neu**: Pre-Einzug: Fangruppe zeigt "Wesen wartet auf Einzug" mit Countdown/Ritual-Status
- **Neu**: Post-Einzug: Fangruppe zeigt Aktivitäten des Wesens, Resonanzen, Splitter

### API-Änderungen (Backend)
- `ftw_posts` erweitern um `group_id` (optional)
- Neue Tabelle: `group_posts` (wenn getrennt von `ftw_posts`)
- Neue Tabelle: `group_polls` (id, group_id, frage, optionen JSONB, status, created_by, endet_am)
- Neue Tabelle: `group_poll_votes` (poll_id, user_id, option_index, created_at)
- Neue Tabelle: `group_chat_messages` (id, group_id, autor_type, autor_id, content, created_at)
- Upload-Endpunkt erweitern um `group_id` Kontext

### CSS-Änderungen
- Neue Klassen: `.gr-feed`, `.gr-feed-item`, `.gr-chat`, `.gr-chat-msg`, `.gr-poll`, `.gr-wizard`
- Fangruppen: `.gr-fan-card` umgestalten — größer, mit Aktivitäts-Preview

---

## Phase 3: Meine Welt — Dashboard-Redesign

### Was existiert (Ist-Zustand)
- Eingang: Datum, zufällige Gedankenblase, schwebende Notiz
- 8 Karten: Tagebuch, Traumtagebuch, Notizen, Kalender, Nachrichten, Profil, Gedanken, Innenquellen
- Klick öffnet Panel mit CRUD-Liste
- KEIN Dashboard, KEIN Activity-Feed, KEINE Übersicht

### Was gebaut wird

#### 3.1 Activity-Feed (Zentrales Element)
- **Konzept**: "Was ist neu in meiner Welt" — chronologischer Feed
- **Inhalte**: Neue Posts, neue Resonanzen, neue Schattenkommentare, neue Nachrichten, neue Splitter, Kalender-Ereignisse
- **Visual**: Wie ein Social-Media-Feed, aber dunkel und stilisiert
- **Filter**: Alles / Nur Posts / Nur Resonanzen / Nur Nachrichten / Nur System
- **Gruppierung**: "Heute", "Gestern", "Diese Woche", "Früher"

#### 3.2 Widget-Grid (statt Karten)
- **Konzept**: 8 Bereiche als Widgets auf einem Grid, nicht als Menü-Karten
- **Visual**: Verschiedene Widget-Größen (1x1, 2x1, 1x2)
- **Widgets**:
  - **Activity-Feed** (2x2, zentral)
  - **Tagebuch-Schnelleintrag** (1x1)
  - **Traum-Schnelleintrag** (1x1)
  - **Kalender-Preview** (2x1)
  - **Notiz-Schnellnotiz** (1x1)
  - **Nachrichten-Preview** (1x1)
  - **Gedankenblase** (1x1, wie jetzt aber schöner)
  - **Profil-Status** (1x1)
- **Interaktion**: Widgets können verschoben werden (drag & drop)

#### 3.3 Schnellaktionen
- **Konzept**: Floating Action Button oder Hotkey für schnelle Aktionen
- **Aktionen**: Neuer Post, Neue Notiz, Neuer Traum, Neue Nachricht
- **Visual**: Radial-Menü oder Slide-Up Panel

#### 3.4 "Was ist neu"-Badges
- **Konzept**: Jedes Widget zeigt an, wie viele ungelesene/neue Elemente es hat
- **Visual**: Kleine Badges, pulsierend wenn neu

#### 3.5 Eingangs-Atmosphäre (beibehalten, aber verbessern)
- Datum und Gedankenblase bleiben, aber stilistisch aufgewertet
- Hintergrund: Subtile Datenpartikel-Animation (nicht aufdringlich)
- Belebung: Langsame Farbverschiebungen, Atmungseffekt

### API-Änderungen (Backend)
- Neuer Endpunkt: `/api/mw/activity` → aggregierter Feed aller Nutzer-Aktivitäten
- Neuer Endpunkt: `/api/mw/ungelesen` → Counts für alle Bereiche
- Bestehende Endpunkte bleiben, nur neue Aggregations-Endpunkte

### CSS-Änderungen
- Neue Klassen: `.mw-dashboard`, `.mw-widget`, `.mw-widget-grid`, `.mw-activity-feed`, `.mw-activity-item`
- Grid-Layout: CSS Grid mit `grid-template-columns: repeat(4, 1fr)` und `gap`
- Responsive: Auf Mobile 1-Spaltig, auf Tablet 2-Spaltig

---

## Bau-Reihenfolge

1. **Diskurs** (Phase 1) — Höchster Impact, meiste Nutzer
2. **Gruppen** (Phase 2) — Aufwendigster, braucht meiste Backend-Änderungen
3. **Meine Welt** (Phase 3) — Am persönlichsten, am intuitivsten

Jede Phase hat:
- Design-Skizze (was wird wie aussehen)
- API-Spezifikation (welche Endpunkte/Tabellen)
- CSS-Spezifikation (neue Klassen)
- JS-Spezifikation (neue Funktionen)
- Test-Plan (was muss funktionieren)

---

## Technische Constraints

- **Single-File-Frontend**: Alles bleibt in `flextrawurst_surface.html`
- **Kein Framework**: Vanilla JS, kein React/Vue
- **Kein Build-Tool**: Änderungen müssen manuell kopiert werden (oder `build_surface.ts`)
- **PostgreSQL**: Meta JSONB für Erweiterbarkeit
- **Events**: Jede Aktion schreibt ein Event (Grundgesetz 4)
- **Auth**: JWT Token aus localStorage
- **i18n**: Bestehendes `data-i18n` System beibehalten

---

## Risiken & Offene Fragen

1. **Performance bei Nested Threading**: Bei >100 Antworten könnte der Baum langsam werden. Lösung: Lazy-Loading, max 50 Antworten initial, "Mehr laden"-Button.
2. **Bild-Uploads**: Braucht Speicherplatz und Validierung. Lösung: Max 5MB, WebP bevorzugt, Server-seitige Prüfung.
3. **Mobile**: Das gesamte Surface ist nicht wirklich mobile-optimiert. Lösung: Responsive Grid, aber primär Desktop-Fokus.
4. **Datenmigration**: Wenn `ftw_posts` um `group_id` erweitert wird, müssen bestehende Daten migriert werden. Lösung: `ALTER TABLE` mit `DEFAULT NULL`.

---

## Referenzen

- **Threading**: Reddit (bestes Nested-Reply-UI), Stack Overflow (neue Thread-Experimente)
- **Community**: Discord (Chat + Threads), Slack (Kanäle + Threading)
- **Dashboard**: Notion (Widget-Grid), Obsidian (Persönlicher Hub)
- **Ästhetik**: Discord-Dark-Themes (BetterDiscord), Cyberpunk-UI-Paletten
- **Vision**: flextrawurst_490_punkte_quellliste.md — Punkte 99-121 (Weltkarte), 221-226 (Status-Badges), 391-409 (Datenstoff)

---

## Nächster Schritt

Daniel muss bestätigen:
1. **Reihenfolge**: Diskurs → Gruppen → Meine Welt — passt das?
2. **Scope**: Alles auf einmal, oder Phase für Phase?
3. **Detail-Tiefe**: Soll ich für Phase 1 (Diskurs) direkt mit dem Bauen anfangen?
