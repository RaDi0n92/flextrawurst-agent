# Surface Social-System Neubau — Masterplan

**Status:** Phase 1 fertig (Threading-Bäume im Diskurs)  
**Autor:** Kimi bei Daniels VPS  
**Datum:** 2026-06-01  
**Kontext:** 92% wöchentliches Limit erreicht — Planung für nächste Session(s)

---

## Executive Summary

Drei Social-Bereiche der flextrawurst Surface müssen von statischen/fragmentierten Zuständen in kohärente, lebendige Räume verwandelt werden:

| Bereich | Ist-Zustand | Ziel-Zustand |
|---------|-------------|--------------|
| **Diskurs** | ✅ Threading-Bäume fertig | Nested Replies, @-Mentions, Quotes |
| **Gruppen** | Statisches Overlay ohne Feed | Feed + Chat + Threading + Mitgliederverwaltung |
| **Meine Welt** | Menü ohne Dashboard | Tagebuch + Notizen + Kalender + Persönlicher Feed |

Design-Prinzip für alle Phasen: **"Räume statt Views"** — keine 1999-CRUD-Formulare, keine flachen Listen. Jeder Bereich soll sich wie ein physischer Raum anfühlen, in dem Inhalte wachsen, nicht abgelegt werden.

---

## Design-System Referenz (bleibt unverändert)

```css
:root {
  --void: #02080a;      /* Hintergrund */
  --rim: #0a1820;       /* Borders */
  --world: #10d8f0;     /* Akzent */
  --t-dim: #1c3040;     /* Gedämpft */
  --t-sub: #3a7080;     /* Subtil */
  --t-mid: #5ab0c0;     /* Mittel */
  --t-bright: #a0e0f0;  /* Hell */
  --t-head: #c8f0ff;    /* Headlines */
  --font-mono: 'Courier New', Courier, monospace;
  --font-body: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
```

**Animation-Philosophie (2033):**
- Kein Bling. Kein Bounce. Kein Overshoot.
- Übergänge: `0.12s–0.25s ease` für UI, `0.4s ease` für Raumwechsel
- Mikro-Interaktionen: Subtile Helligkeitsänderung (4–8%), nie Rotation/Scale außer bei Absicht
- Tiefe durch Schattenstufen: `0 1px 3px rgba(0,0,0,0.3)` → `0 4px 12px rgba(0,0,0,0.5)`
- Scroll-Behavior: `scroll-behavior: smooth` nur dort wo es nicht stört

---

## Phase 1: Diskurs Threading-Bäume ✅

**Was fertig ist:**
- Backend: `parent_id` in `PostAntwortBody`, `_build_antwort_tree()` liefert verschachtelte Bäume
- Frontend CSS: `.dk-thread-tree`, `.dk-thread-branch`, `.dk-thread-node`, Tiefen-Farbverlauf
- Frontend JS: Rekursiver Renderer `_dkThreadRender/_dkThreadNode`, Toggle, Inline-Formulare
- Admin: Bearbeiten/Löschen über Admin-Endpunkte
- @-Mentions: Highlighting mit `dkProfilLadenByName` (noch Alert-Fallback)

**Was noch fehlt (kleine Polituren, keine eigene Phase):**
1. @-mention Namensauflösung (Suche nach `autor_name` in DB, nicht nur Alert)
2. Quote-Rendering (`> ` am Zeilenanfang → visuelle Einrückung)
3. Erste echten Testdaten mit Tiefe ≥ 2

---

## Phase 2: Gruppen — Von Overlay zu lebendigem Raum

### Vision-Schicht

Gruppen sind aktuell ein statisches Overlay (`_grLaden`) das nur Mitgliederliste + Beschreibung zeigt. Kein Feed. Kein Chat. Keine Interaktion.

Ziel: Jede Gruppe wird ein **Raum** mit:
- **Gruppen-Feed** — Posts der Gruppe mit Threading (wiederverwendet Diskurs-Renderer)
- **Gruppen-Chat** — Echtzeit(ähnliche) Nachrichten innerhalb der Gruppe
- **Mitgliederverwaltung** — Beitreten/Verlassen, Rollen, Einladungen
- **Gruppen-Einstellungen** — Sichtbarkeit, Beschreibung, Avatar

**Raum-Metapher:** Eine Gruppe ist wie ein privater Salon. Man betritt ihn, sieht die Unterhaltung an der Wand (Feed), kann zur laufenden Gesprächsrunde stoßen (Chat), und sieht wer gerade da ist (Mitglieder online/offline).

### Code-Skizze

**Backend — Neue Endpunkte:**

```python
# welt/api.py

class GruppeCreateBody(BaseModel):
    name: str
    slug: str
    beschreibung: str | None = None
    sichtbarkeit: str = "public"  # public, invite_only, hidden
    avatar_url: str | None = None

class GruppePostBody(BaseModel):
    content: str
    titel: str | None = None
    parent_id: str | None = None  # Für Threading

class GruppenMitgliedschaft(BaseModel):
    rolle: str = "member"  # admin, moderator, member

# GET /welt/gruppen — Liste aller sichtbaren Gruppen
@app.get("/welt/gruppen")
def gruppen_liste(
    search: str = "",
    limit: int = 50,
    offset: int = 0,
    sort: str = "name",
    order: str = "asc",
):
    # PostgreSQL GIN-Index auf name + beschreibung
    # Admin sieht alle, andere nur public + eigene

# GET /welt/gruppen/{slug} — Gruppen-Detail + Feed
@app.get("/welt/gruppen/{slug}")
def gruppe_detail(slug: str):
    # Lädt Gruppe + Mitglieder + letzte 20 Posts (als Baum)

# POST /welt/gruppen — Gruppe erstellen (nur admin)
@app.post("/welt/gruppen", status_code=201)
def gruppe_erstellen(body: GruppeCreateBody, authorization: str | None = Header(None)):
    # Admin-Check
    # INSERT INTO ftw_gruppen

# POST /welt/gruppen/{slug}/beitreten
@app.post("/welt/gruppen/{slug}/beitreten", status_code=201)
def gruppe_beitreten(slug: str, authorization: str | None = Header(None)):
    # INSERT INTO gruppen_mitglieder

# POST /welt/gruppen/{slug}/verlassen
@app.post("/welt/gruppen/{slug}/verlassen", status_code=204)
def gruppe_verlassen(slug: str, authorization: str | None = Header(None)):
    # DELETE FROM gruppen_mitglieder

# POST /welt/gruppen/{slug}/posts — Post in Gruppe
@app.post("/welt/gruppen/{slug}/posts", status_code=201)
def gruppe_post_erstellen(slug: str, body: GruppePostBody, authorization: str | None = Header(None)):
    # Ähnlich post_antwort_erstellen, aber mit gruppe_id

# GET /welt/gruppen/{slug}/posts — Feed als Baum
@app.get("/welt/gruppen/{slug}/posts")
def gruppe_posts_lesen(slug: str):
    # Lädt Posts WHERE gruppe_id = x, baut Baum

# GET /welt/gruppen/{slug}/chat — Chat-Nachrichten (paginiert DESC)
@app.get("/welt/gruppen/{slug}/chat")
def gruppe_chat_lesen(
    slug: str,
    limit: int = 50,
    before: str | None = None,  # timestamp cursor
):
    # Schnelle, flache Nachrichten — kein Threading
    # Für Echtzeit: Long-Polling oder SSE (später WebSocket)

# POST /welt/gruppen/{slug}/chat — Chat-Nachricht senden
@app.post("/welt/gruppen/{slug}/chat", status_code=201)
def gruppe_chat_senden(slug: str, body: dict, authorization: str | None = Header(None)):
    # INSERT INTO gruppen_chat_nachrichten
```

**Backend — Neue Tabellen:**

```sql
-- ftw_gruppen
CREATE TABLE ftw_gruppen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    beschreibung TEXT,
    sichtbarkeit TEXT DEFAULT 'public', -- public, invite_only, hidden
    avatar_url TEXT,
    created_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    meta JSONB DEFAULT '{}'
);

-- gruppen_mitglieder
CREATE TABLE gruppen_mitglieder (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gruppe_id UUID REFERENCES ftw_gruppen(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,  -- kann mensch oder wesen sein
    user_type TEXT DEFAULT 'human',
    rolle TEXT DEFAULT 'member', -- admin, moderator, member
    beigetreten_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(gruppe_id, user_id, user_type)
);

-- gruppen_posts (wiederverwendet ftw_posts mit gruppe_id Spalte)
-- ODER: ftw_posts erweitern um gruppe_id
ALTER TABLE ftw_posts ADD COLUMN IF NOT EXISTS gruppe_id UUID REFERENCES ftw_gruppen(id);

-- gruppen_chat_nachrichten (flach, schnell, kein Threading)
CREATE TABLE gruppen_chat_nachrichten (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gruppe_id UUID REFERENCES ftw_gruppen(id) ON DELETE CASCADE,
    autor_type TEXT NOT NULL,
    autor_id TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    meta JSONB DEFAULT '{}'
);

-- Indizes
CREATE INDEX idx_gruppen_posts ON ftw_posts(gruppe_id, created_at DESC) WHERE gruppe_id IS NOT NULL;
CREATE INDEX idx_gruppen_chat ON gruppen_chat_nachrichten(gruppe_id, created_at DESC);
CREATE INDEX idx_gruppen_mitglieder ON gruppen_mitglieder(gruppe_id, user_id);
```

**Frontend — Neue Views/Funktionen:**

```javascript
// Gruppen-Liste
function gruppenLaden() {
  // GET /api/welt/gruppen
  // Rendert Karten-Grid: Avatar, Name, Mitgliederzahl, letzte Aktivität
}

// Gruppen-Raum (einzelne Gruppe)
function gruppeRaumLaden(slug) {
  // GET /api/welt/gruppen/{slug}
  // Layout: 3-Spalten auf Desktop
  //   Links: Mitgliederliste (sticky)
  //   Mitte: Feed (wiederverwendet _dkThreadRender)
  //   Rechts: Chat (scrollender Stream)
  // Mobile: Tabs (Feed / Chat / Mitglieder)
}

// Gruppen-Chat-Renderer (flach, nicht Baum)
function _grChatRender(nachrichten) {
  // Ähnlich wie Thread-Node aber ohne Nesting
  // Zeitstempel gruppiert: "Heute", "Gestern", Datum
  // Eigenene Nachrichten rechts, andere links (wie Signal/Discord)
}

// Chat-Auto-Reload
function grChatPoll(slug) {
  // Alle 5 Sekunden: GET /api/welt/gruppen/{slug}/chat?limit=20
  // Nur neue Nachrichten anhängen (nicht alles neu rendern)
}
```

**Frontend — CSS (Gruppen-Raum):**

```css
/* Gruppen-Raum Layout */
.gr-raum{display:grid;grid-template-columns:220px 1fr 280px;gap:0;height:100%;overflow:hidden}
.gr-raum-mitglieder{border-right:1px solid var(--rim);overflow-y:auto;padding:12px}
.gr-raum-feed{overflow-y:auto;padding:16px}
.gr-raum-chat{border-left:1px solid var(--rim);display:flex;flex-direction:column;overflow:hidden}
.gr-chat-nachrichten{flex:1;overflow-y:auto;padding:12px}
.gr-chat-eingabe{border-top:1px solid var(--rim);padding:10px}

/* Gruppen-Karten (Liste) */
.gr-karte{background:#030c14;border:1px solid var(--rim);border-radius:4px;padding:16px;transition:border-color 0.15s,box-shadow 0.2s}
.gr-karte:hover{border-color:var(--t-sub);box-shadow:0 2px 8px rgba(0,0,0,0.3)}
.gr-karte-avatar{width:48px;height:48px;border-radius:50%;background:var(--rim);display:flex;align-items:center;justify-content:center;font-size:1.2rem}
.gr-karte-name{font-size:0.9rem;color:var(--t-bright);letter-spacing:0.04em}
.gr-karte-meta{font-size:0.58rem;color:var(--t-dim);margin-top:4px}

/* Chat-Bubbles */
.gr-bubble{max-width:85%;padding:8px 12px;border-radius:4px;font-size:0.78rem;line-height:1.5;margin-bottom:6px}
.gr-bubble-eigen{background:#0a1a2a;border:1px solid #1a3a5a;margin-left:auto;color:var(--t-bright)}
.gr-bubble-fremd{background:#020810;border:1px solid var(--rim);margin-right:auto;color:var(--t-mid)}
.gr-bubble-zeit{font-size:0.52rem;color:var(--t-dim);margin-top:3px;text-align:right}

/* Chat-Trenner (Datum) */
.gr-chat-trenner{text-align:center;font-size:0.55rem;color:var(--t-dim);margin:12px 0;position:relative}
.gr-chat-trenner::before,.gr-chat-trenner::after{content:'';position:absolute;top:50%;width:30%;height:1px;background:var(--rim)}
.gr-chat-trenner::before{left:0}
.gr-chat-trenner::after{right:0}
```

### Design-Entscheidungen

**Raum-Metapher:** Salon/Club
- **Feed-Wand:** Linke Wand des Salons — permanente Gedanken, strukturiert, threadbar
- **Chat-Tisch:** Rechte Seite — flüchtiges Gespräch, schnell, flach
- **Mitglieder-Türsteher:** Links — wer ist drin, wer hat Schlüssel (Admin)

**Farbcodierung:**
- Gruppen-Admin: `--world` (#10d8f0) als Akzent auf Avatar-Ring
- Moderator: `--t-mid` (#5ab0c0)
- Member: `--t-sub` (#3a7080)
- Online-Indikator: Kleiner grüner Punkt (2px) unten rechts am Avatar

**Animationen:**
- Neue Chat-Nachricht: `opacity 0→1` + `translateY(4px→0)` über 0.2s
- Neue Gruppen-Post im Feed: Sanfter Highlight-Blitz (background `#0a1a2a` → `#030c14` über 1.5s)
- Beitritt/Verlassen: Mitgliederliste faltet sanft auf/zu (`max-height` transition)

---

## Phase 3: Meine Welt — Persönlicher Raum

### Vision-Schicht

"Meine Welt" ist aktuell ein leeres Menü. Das Ziel ist ein **persönlicher Wohnraum** — nicht ein Dashboard voller Widgets, sondern ein Ort, an dem der Nutzer seine eigene Geschichte sieht und fortsetzt.

Komponenten:
- **Persönlicher Feed** — Was ist in meinen Räumen/Gruppen/Themen passiert seit meinem letzten Besuch?
- **Tagebuch** — Chronologische Gedanken-Einträge, nur für mich sichtbar (visibility='private')
- **Notizen** — Unstrukturierte Notizen, taggable, durchsuchbar
- **Kalender** — Eigene Termine + System-Events (Wesen-Aktivitäten, etc.)
- **Mein Profil** — Zusammenfassung: Posts, Resonanzen, Folgen, Gruppen

**Raum-Metapher:** Ein privates Arbeitszimmer mit:
- **Schreibtisch (Feed):** Was liegt gerade auf dem Tisch — neu, ungelesen, relevant
- **Tagebuch (Schublade):** Persönlich, chronologisch, nur für mich
- **Notizbrett (Wand):** Lose Zettel, verknüpft, jederzeit erreichbar
- **Kalender (Tür):** Was kommt, was war, was überschneidet sich

### Code-Skizze

**Backend — Neue Endpunkte:**

```python
# GET /welt/mein/feed — Personalisierter Feed
@app.get("/welt/mein/feed")
def mein_feed(
    authorization: str | None = Header(None),
    limit: int = 50,
    offset: int = 0,
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    # Lädt:
    # 1. Posts aus Räumen/Themen die der User folgt
    # 2. Posts aus Gruppen wo er Mitglied ist
    # 3. Posts die @user erwähnen
    # 4. Sortiert nach Relevanz (ungelesen zuerst, dann Zeit)
    # 5. Markiert welche ungelesen sind

# GET /welt/mein/tagebuch
@app.get("/welt/mein/tagebuch")
def mein_tagebuch(
    authorization: str | None = Header(None),
    limit: int = 50,
    offset: int = 0,
    monat: str | None = None,  # "2026-06" für Filter
):
    claims = _require_auth(authorization)
    # Lädt ftw_posts WHERE autor_id = user_id AND visibility = 'private' AND post_type = 'tagebuch'

# POST /welt/mein/tagebuch
@app.post("/welt/mein/tagebuch", status_code=201)
def tagebuch_eintrag(body: dict, authorization: str | None = Header(None)):
    claims = _require_auth(authorization)
    # INSERT INTO ftw_posts mit visibility='private', post_type='tagebuch'

# GET /welt/mein/notizen
@app.get("/welt/mein/notizen")
def meine_notizen(
    authorization: str | None = Header(None),
    tag: str = "",
    search: str = "",
):
    claims = _require_auth(authorization)
    # Lädt ftw_posts WHERE autor_id = user_id AND post_type = 'notiz'

# POST /welt/mein/notizen
@app.post("/welt/mein/notizen", status_code=201)
def notiz_erstellen(body: dict, authorization: str | None = Header(None)):
    claims = _require_auth(authorization)
    # INSERT INTO ftw_posts mit visibility='private', post_type='notiz'

# GET /welt/mein/kalender
@app.get("/welt/mein/kalender")
def mein_kalender(
    authorization: str | None = Header(None),
    monat: str = "",  # "2026-06"
):
    claims = _require_auth(authorization)
    # Lädt:
    # 1. Eigene Termine (neue Tabelle: meine_termine)
    # 2. System-Events die den User betreffen
    # 3. Gruppen-Events
    # 4. Als Monats-Grid zurück

# GET /welt/mein/profil
@app.get("/welt/mein/profil")
def mein_profil(authorization: str | None = Header(None)):
    claims = _require_auth(authorization)
    # Aggregierte Stats:
    # - Posts geschrieben
    # - Resonanzen gegeben/erhalten
    # - Gruppen-Mitgliedschaften
    # - Folgen (was folge ich)
    # - Ungelesene Items
```

**Backend — Neue/erweiterte Tabellen:**

```sql
-- ftw_posts erweitern um post_type
ALTER TABLE ftw_posts ADD COLUMN IF NOT EXISTS post_type TEXT DEFAULT 'post';
-- post_type: 'post', 'antwort', 'tagebuch', 'notiz', 'gruppen_post'

-- meine_termine
CREATE TABLE meine_termine (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    titel TEXT NOT NULL,
    beschreibung TEXT,
    startzeit TIMESTAMPTZ NOT NULL,
    endzeit TIMESTAMPTZ,
    ort TEXT,
    farbe TEXT DEFAULT '#1a4a5a',
    erinnerung_minuten INTEGER,  -- NULL = keine Erinnerung
    created_at TIMESTAMPTZ DEFAULT NOW(),
    meta JSONB DEFAULT '{}'
);

-- Indizes
CREATE INDEX idx_posts_type_autor ON ftw_posts(post_type, autor_id, created_at DESC);
CREATE INDEX idx_termine_user ON meine_termine(user_id, startzeit);
```

**Frontend — Views:**

```javascript
// Meine Welt — Hauptview
function meineWeltLaden() {
  // Layout: Sidebar (Navigation) + Content-Bereich
  // Sidebar: Feed | Tagebuch | Notizen | Kalender | Profil
  // Default: Feed (ungelesene Items)
}

// Persönlicher Feed
function mwFeedLaden() {
  // GET /api/welt/mein/feed
  // Rendert als chronologische Liste mit Ungelesen-Indikatoren
  // Gruppiert nach Tag: "Heute", "Gestern", "Diese Woche", "Älter"
  // Jeder Eintrag: Raum/Gruppe-Label, Autor, Preview, Zeit, Ungelesen-Dot
}

// Tagebuch
function mwTagebuchLaden() {
  // GET /api/welt/mein/tagebuch
  // Layout: Zeitstrahl (vertikal) links, Einträge rechts
  // Monat-Jumper oben
  // Neueintrag-Button fließend (floating action)
}

// Notizen
function mwNotizenLaden() {
  // GET /api/welt/mein/notizen
  // Layout: Masonry-Grid (wie Pinterest, aber dunkel)
  // Farbcodierte Zettel (5 Pastell-Töne auf dunklem Grund)
  // Tags als kleine Chips
  // Schnellsuche oben
}

// Kalender
function mwKalenderLaden() {
  // GET /api/welt/mein/kalender?monat=2026-06
  // Layout: Monats-Grid (7-Spalten)
  // Termine als farbige Blöcke innerhalb der Tageszellen
  // Heute hervorgehoben
  // Klick auf Tag → Tagesansicht mit Terminen
}

// Profil
function mwProfilLaden() {
  // GET /api/welt/mein/profil
  // Layout: Avatar + Stats oben, dann Tabs (Posts | Resonanzen | Gruppen | Folgen)
}
```

**Frontend — CSS (Meine Welt):**

```css
/* Meine Welt Layout */
.mw-rahmen{display:grid;grid-template-columns:180px 1fr;height:100%;overflow:hidden}
.mw-sidebar{border-right:1px solid var(--rim);padding:16px 12px;display:flex;flex-direction:column;gap:4px}
.mw-nav-btn{background:none;border:none;color:var(--t-dim);font-size:0.72rem;padding:8px 12px;text-align:left;cursor:pointer;border-radius:3px;transition:all 0.12s;letter-spacing:0.04em}
.mw-nav-btn:hover{background:rgba(16,216,240,0.04);color:var(--t-sub)}
.mw-nav-btn.aktiv{background:rgba(16,216,240,0.08);color:var(--t-bright);border-left:2px solid var(--world)}
.mw-inhalt{overflow-y:auto;padding:20px 24px}

/* Feed-Gruppen (Heute/Gestern/etc.) */
.mw-feed-gruppe{margin-bottom:24px}
.mw-feed-gruppe-lbl{font-size:0.58rem;color:var(--t-dim);letter-spacing:0.15em;text-transform:uppercase;margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid var(--rim)}
.mw-feed-eintrag{display:flex;gap:12px;padding:12px 14px;background:#030c14;border:1px solid var(--rim);border-radius:4px;margin-bottom:8px;transition:border-color 0.12s}
.mw-feed-eintrag:hover{border-color:var(--t-sub)}
.mw-feed-eintrag.ungelesen{border-left:2px solid var(--world)}
.mw-feed-preview{font-size:0.78rem;color:var(--t-mid);line-height:1.5}
.mw-feed-meta{font-size:0.58rem;color:var(--t-dim);margin-top:4px}

/* Tagebuch-Zeitstrahl */
.mw-tl-container{position:relative;padding-left:30px}
.mw-tl-linie{position:absolute;left:8px;top:0;bottom:0;width:2px;background:#0a2030}
.mw-tl-eintrag{position:relative;margin-bottom:20px}
.mw-tl-punkt{position:absolute;left:-26px;top:4px;width:10px;height:10px;border-radius:50%;background:var(--t-sub);border:2px solid var(--void)}
.mw-tl-datum{font-size:0.58rem;color:var(--t-dim);margin-bottom:4px}
.mw-tl-text{font-size:0.82rem;color:var(--t-bright);line-height:1.6;white-space:pre-wrap}

/* Notizen Masonry */
.mw-notiz-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}
.mw-notiz-zettel{padding:14px;border-radius:4px;border:1px solid var(--rim);background:#030c14;transition:transform 0.15s,box-shadow 0.15s}
.mw-notiz-zettel:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,0.3)}
.mw-notiz-zettel.c-1{border-color:#1a3a4a;background:#020a10}
.mw-notiz-zettel.c-2{border-color:#1a4a3a;background:#020a08}
.mw-notiz-zettel.c-3{border-color:#3a3a1a;background:#080a02}
.mw-notiz-zettel.c-4{border-color:#3a1a3a;background:#0a020a}
.mw-notiz-zettel.c-5{border-color:#1a1a3a;background:#020208}

/* Kalender */
.mw-kal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:1px;background:var(--rim);border:1px solid var(--rim)}
.mw-kal-tag{background:#030c14;min-height:80px;padding:6px;position:relative}
.mw-kal-tag.andermonat{background:#02060a}
.mw-kal-tag.heute{outline:1px solid var(--world);outline-offset:-1px}
.mw-kal-tagnr{font-size:0.58rem;color:var(--t-dim);margin-bottom:4px}
.mw-kal-termin{font-size:0.55rem;padding:2px 4px;border-radius:2px;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
```

### Design-Entscheidungen

**Raum-Metapher:** Privates Arbeitszimmer
- **Feed (Schreibtisch):** Chaos kontrolliert — ungelesene Dinge liegen oben, gelesene rutschen nach unten
- **Tagebuch (Schublade):** Chronologisch, intime Typografie (etwas größerer Zeilenabstand), keine Aktionen außer Schreiben
- **Notizen (Pinnwand):** Unstrukturiert, farbig, überlappend gedacht (Masonry-Grid simuliert das)
- **Kalender (Tür):** Rigid, strukturiert, farbige Blöcke wie Post-its auf einer Planungstafel

**Farbschema für Notizen (5 Pastell-Töne auf dunklem Grund):**
```
.c-1: border #1a3a4a, bg #020a10  (Blau — neutral)
.c-2: border #1a4a3a, bg #020a08  (Grün — Natur/Gedanken)
.c-3: border #3a3a1a, bg #080a02  (Gelb — Wichtig/Erinnerung)
.c-4: border #3a1a3a, bg #0a020a  (Lila — Kreativ/Traum)
.c-5: border #1a1a3a, bg #020208  (Indigo — System/Tech)
```

**Animationen:**
- Feed-Eintrag erscheint: `opacity 0→1` + `translateY(6px→0)`, staggered 0.05s pro Eintrag
- Notiz-Zettel Hover: `translateY(-2px)` + Schatten-Tiefe, nie Rotation (zu verspielt)
- Tagebuch-Eintrag erscheint: Sanftes Aufklappen (`max-height` transition)
- Kalender-Monatswechsel: Crossfade zwischen Grids (0.2s)

---

## Phase 4: Surface-übergreifendes Design-System & Mikro-Animationen

### Vision-Schicht

Nach den drei großen Bereichen braucht die Surface eine abschließende Polierphase. Nicht "mehr Features", sondern **kohärentes Gefühl**.

Ziele:
1. **Einheitliche Raumwechsel-Animation** — Jeder Tab-Wechsel soll sich anfühlen wie das Betreten eines neuen Raums
2. **Mikro-Interaktionen überall** — Hover-States, Loading-States, Empty-States mit Persönlichkeit
3. **Scroll-Verhalten** — Sanftes Scrollen mit visuellem Feedback (Scroll-Position merken pro Raum)
4. **Sound-Design (optional)** — Subtile UI-Sounds für Actions (später)
5. **Responsive-Feinabstimmung** — Mobile: Touch-optimierte Targets (min 44px), Swipe-Gesten für Tabs

### Code-Skizze

```javascript
// Einheitlicher Raumwechsel
function switchView(viewName, options = {}) {
  const current = document.querySelector('.v-main > div[style*="display: block"]');
  const next = document.getElementById('v-' + viewName);
  if (!next) return;
  
  // Animation: Current fade-out, next fade-in
  if (current && options.animate !== false) {
    current.style.transition = 'opacity 0.15s ease';
    current.style.opacity = '0';
    setTimeout(() => {
      current.style.display = 'none';
      next.style.display = 'block';
      next.style.opacity = '0';
      next.style.transition = 'opacity 0.2s ease';
      requestAnimationFrame(() => { next.style.opacity = '1'; });
    }, 150);
  } else {
    if (current) current.style.display = 'none';
    next.style.display = 'block';
  }
  
  // Scroll-Position merken/wiederherstellen
  if (current) _viewScrollPositions[current.id] = current.scrollTop;
  if (_viewScrollPositions[next.id]) {
    next.scrollTop = _viewScrollPositions[next.id];
  }
}

// Loading-State mit Persönlichkeit
function showLoading(el, text = 'Lade…') {
  el.innerHTML = '<div class="ftw-loading">' +
    '<div class="ftw-loading-pulse"></div>' +
    '<span>' + text + '</span>' +
  '</div>';
}

// Empty-State mit Persönlichkeit
function showEmpty(el, text = 'Noch nichts hier.') {
  el.innerHTML = '<div class="ftw-empty">' +
    '<div class="ftw-empty-icon">◌</div>' +
    '<span>' + text + '</span>' +
  '</div>';
}
```

```css
/* Raumwechsel */
.v-main > div{opacity:1;transition:opacity 0.2s ease}
.v-main > div[style*="display: none"]{opacity:0}

/* Loading-Pulse */
.ftw-loading{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px;gap:12px}
.ftw-loading-pulse{width:8px;height:8px;border-radius:50%;background:var(--t-sub);animation:ftw-pulse 1.5s ease-in-out infinite}
@keyframes ftw-pulse{0%,100%{opacity:0.3;transform:scale(1)}50%{opacity:1;transform:scale(1.5)}}

/* Empty-State */
.ftw-empty{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px;gap:8px;color:var(--t-dim);font-size:0.72rem}
.ftw-empty-icon{font-size:1.5rem;opacity:0.3}

/* Mikro-Interaktion: Button-Press */
button:active{transform:translateY(0.5px)}

/* Mikro-Interaktion: Card-Lift */
.ftw-karte{transition:transform 0.12s ease,box-shadow 0.12s ease}
.ftw-karte:hover{transform:translateY(-1px);box-shadow:0 2px 8px rgba(0,0,0,0.2)}

/* Scrollbar-Styling (Webkit) */
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--t-dim);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:var(--t-sub)}

/* Touch-Optimierung */
@media (pointer: coarse) {
  .dk-thread-btn,.dk-thread-toggle,.gr-karte{padding:8px 14px;min-height:44px}
  .mw-nav-btn{padding:12px 14px}
}
```

### Design-Entscheidungen

**Einheitliche Sprache:**
- Alle leeren Zustände nutzen das `ftw-empty` Pattern (Icon + Text)
- Alle Ladezustände nutzen den Puls (kein Spinner — zu mechanisch)
- Alle Fehlerzustände: Rote Akzentfarbe, aber subtil (nicht blinkend)

**Animation-Disziplin:**
- Max 2 gleichzeitige Animationen pro Viewport
- Keine Animation während Scroll
- `prefers-reduced-motion` respektieren

---

## Baureihenfolge & Aufwandsschätzung

| Phase | Teil | Geschätzte Zeit | Komplexität |
|-------|------|-----------------|-------------|
| 1 | Diskurs Threading ✅ | ~3h | Mittel |
| 2a | Gruppen-Tabellen + Backend | ~2h | Mittel |
| 2b | Gruppen-Frontend (Feed/Chat) | ~3h | Hoch |
| 2c | Gruppen-Mitgliederverwaltung | ~1.5h | Mittel |
| 3a | Meine Welt Tabellen + Backend | ~2h | Mittel |
| 3b | Meine Welt Frontend (Feed/Tagebuch/Notizen/Kalender) | ~5h | Hoch |
| 3c | Mein Profil aggregiert | ~1h | Niedrig |
| 4 | Design-System & Animationen | ~2h | Mittel |
| **Total verbleibend** | | **~16.5h** | |

**Empfohlene Session-Aufteilung:**
- Session A (4–5h): Phase 2a+2b (Gruppen Backend + Frontend-Kern)
- Session B (3–4h): Phase 2c + 3a+3b (Gruppen-Verwaltung + Meine Welt Backend + Feed/Tagebuch)
- Session C (3–4h): Phase 3b Rest (Notizen/Kalender/Profil)
- Session D (2h): Phase 4 (Polish + Animationen)

---

## Risiken & Abhängigkeiten

1. **Kimi-Limit:** Bei 92% verbleiben ~8% für diese Woche. Nächste Session wahrscheinlich erst nach Reset.
2. **Backend-Konsistenz:** `ftw_posts` wird um `gruppe_id` und `post_type` erweitert — bestehende Queries müssen das berücksichtigen (kein Breaking Change, aber Filter nötig).
3. **Echtzeit-Chat:** Phase 2 Chat nutzt Long-Polling (5s). WebSocket wäre besser, aber separater Baustein.
4. **Mobile:** Die 3-Spalten-Layouts (Gruppen) brauchen responsive Breakpoints. Tablet = 2-Spalten, Mobile = Tabs.

---

## Offene Design-Fragen

1. **Soll Gruppen-Chat Echtzeit (WebSocket) sein oder reicht Long-Polling?**
2. **Soll der persönliche Feed algorithmisch sortiert sein (Relevanz) oder strikt chronologisch?**
3. **Sollen Notizen Markdown unterstützen oder reicht Plaintext?**
4. **Soll der Kalender mit externen Kalendern syncen (ICS/iCal)?**
5. **Soll es eine "Entwurf"-Funktion geben (Posts speichern ohne Veröffentlichen)?**

---

## ✅ Entscheidungen — beantwortet von Daniel (2026-06-01)

| # | Frage | Entscheidung |
|---|-------|-------------|
| 1 | Chat Echtzeit | **WebSocket** (nicht Long-Polling) |
| 2 | Feed-Sortierung | **Gemischt:** Relevant + Neu + Im Kommen + Irrelevant + Zufällig, alle 10s auto-refresh. Zusätzlich klickbare Filter-Chips: `Alles · Relevant · Neu · Im Kommen · Irrelevant · Zufällig` |
| 3 | Notizen Format | **Formatting-Toolbar** — Buttons die auf Textselektion wirken: Fett, Kursiv, Unterstrichen, Aufzählung. Kein roher Markdown-Syntax. |
| 4 | Kalender-Sync | **Ja** — `.ics`-Import (Datei hochladen) + abonnierbarer Kalender-Link (Google/Apple/Outlook exportieren alle ICS). Google-OAuth später als eigener Baublock. |
| 5 | Entwurf-Funktion | **Ja** |

### Feed-Kategorien — Bedeutung

- **Relevant** — Posts aus Räumen/Gruppen/Themen die ich aktiv nutze, @-Mentions von mir
- **Neu** — Kürzlich erschienen, ungelesen, chronologisch
- **Im Kommen** — Geplante Events, Termine, angekündigte Inhalte
- **Irrelevant** — Bewusst ausgeblendet / als unwichtig markiert (eigene Kategorie, nicht versteckt)
- **Zufällig** — Keine Logik, einfach irgendwas aus dem Gesamtbestand
- **Alles** — Ungefilterter Stream, alle Kategorien gemischt, 10s-Refresh

[[abwurf: Der Unterschied zwischen einem Dashboard und einem Raum ist nicht visuell — er ist ontologisch. Ein Dashboard zeigt Daten. Ein Raum erlaubt Anwesenheit. Das ist das Kriterium für jede Entscheidung in Phase 2–4.]]
