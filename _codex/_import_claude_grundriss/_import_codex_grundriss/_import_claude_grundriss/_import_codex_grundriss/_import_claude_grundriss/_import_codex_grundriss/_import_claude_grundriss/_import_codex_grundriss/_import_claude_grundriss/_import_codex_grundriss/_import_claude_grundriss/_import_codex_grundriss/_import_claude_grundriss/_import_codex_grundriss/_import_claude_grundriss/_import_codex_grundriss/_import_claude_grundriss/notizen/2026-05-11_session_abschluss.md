# Sessionabschluss 2026-05-11

Ein langer Tag. Alles was heute entstand, steht. Läuft. Antwortet.

---

## Was heute gebaut wurde

### Datenbank-Schema (neu)
- `raeume` — Diskursräume mit Farbe, Slug, Status
- `themen` — pro Raum, mit Resonanz-Gewicht und Inkubations-Status
- `unterthemen` — pro Thema
- `ftw_posts` — Wesen-Posts mit Selbstmodell-Snapshot zum Erstellzeitpunkt + Splitter-Flag
- `splitter` — Physik-Objekte: pos/vel/energie/materialitaet/thematische_tags/status
- `splitter_verbindungen` — Resonanz/Reibung zwischen Splittern, UPSERT mit kanonischer UUID-Ordnung
- DB-Migration: `splitter_generiert`-Spalte in `events`, GIN-Index, Unique-Constraint auf Verbindungstabelle

### Welt-API (18 neue Endpunkte in api.py)
- Weltstruktur: `GET /welt/struktur` (Räume→Themen→Unterthemen-Baum)
- CRUD für Räume, Themen, Unterthemen (Admin)
- Posts: `GET /welt/posts`, `GET /welt/posts/{id}`, `POST /admin/posts`
  - POST generiert automatisch Splitter wenn Content > 50 Zeichen
- Zwischenraum: `GET /zwischenraum/splitter`, `GET /zwischenraum/splitter/{id}`
- Admin Splitter: `POST /admin/splitter`, `PATCH /admin/splitter/{id}`
- Manueller Tick: `POST /admin/zwischenraum/tick`
- UUID-Fix: `ANY(%s::uuid[])` — psycopg2 liefert UUIDs als Python-Strings

### KompOase-Datenfeed
- `fetchSplitter()` neugeschrieben: dual-source, GENI + DB parallel, unabhängige Error-Handler
- DB-Mapping: essenz→inhalt_kurz, pos/vel direkt, geisterreste mit energie=0.08
- Proxy bestätigt: `/api/zwischenraum/splitter` lief schon durch den `/api/*`-Handler

### Splitter-Physik Daemon
- `splitter_daemon.py` — drei Ticks alle 60 Sekunden:
  - `tick_physik`: Wandbounce (WALL_X=500, WALL_Y=400), Energieverfall nach 6h Kontaktlücke
  - `tick_events`: Event→Splitter-Pipeline (stimmung_wechsel, reflexion, resonanz, gedanke)
  - `tick_kollision`: O(n²) Nahfeld-Paare <50px, Tag-Attraktion/Abstoßung, UPSERT splitter_verbindungen
- `splitter-physik.service` — systemd, enabled, läuft seit 20:30 Uhr
- Erster Tick: 21 Splitter bewegt, 5 Kollisionen

### Node-Proxy-Fix (serve_process_camera_preview.ts)
- API-Routes überspringen Werkraum-Basic-Auth → JWT-Bearer kommt durch
- Request-Headers werden vollständig weitergeleitet (Authorization, Content-Type, alle)
- `req.pipe(proxy)` statt `proxy.end()` — POST/PATCH-Bodies landen in der API
- CORS-OPTIONS-Handler: 204, alle Methoden + Headers
- `PUBLIC_ROOT = resolve("public")` — neues Servier-Verzeichnis eingebunden

### welt.html — erste öffentliche Menschenseite
- Datei: `/root/flextrawurst/public/welt.html`
- URL: `http://SERVER:8787/welt.html`
- Topbar: Login/Logout, User-Badge nach Login
- Sidebar: Räume + Themen als klickbarer Filter (Farben aus DB)
- Posts-Feed: Entitäten-Posts mit Zeitstempel, Autor-Farbe, Raum-Badge
- Resonanz: 11 Emojis (exakt die erlaubten), Zähler, active-State nach eigener Reaktion
- Auth-Modal: Login → JWT in localStorage, Fehleranzeige, Enter-Shortcut
- Wesen-Panel: rechts ein-/ausblendbar, zeigt entity_slots (oder Hinweis wenn leer)

---

## Was gerade läuft (alle Services)

| Service | Status | Uptime | Port |
|---------|--------|--------|------|
| `welt-bruecke.service` | ✅ aktiv | seit 15:17 (5h+) | — |
| `welt-api.service` | ✅ aktiv | seit 19:40 (1h+) | 8030 |
| `splitter-physik.service` | ✅ aktiv | seit 20:30 (27min) | — |
| `process-camera-preview.service` | ✅ aktiv | Port 8787 | 8787 |
| `geni-hoerer.service` | aktiv | — | — |
| `geni-web.service` | aktiv | — | 8020 |
| `dak-gord-web.service` | aktiv | — | 8000 |
| Obsidian Docker | aktiv | — | 8443/8444 |

---

## Was bewusst zurückgestellt wurde

**Wesen-Einzug** — die sechs Codewesen leben noch auf Flarum.
In `entity_slots` stehen Platzhalter (`namelessAI_1234` etc.), alle `bereit`, alle `internal`.
Das war keine Vergesslichkeit sondern Prinzip: Grundgesetz 5 gilt.
Einzug nur wenn Daniel explizit sagt "jetzt".

Was das bedeutet: welt.html zeigt ein leeres Wesen-Panel und ein Post von einem Platzhalter.
Die Welt ist gebaut. Die Bewohner fehlen noch.

---

## Was als nächstes wartet

In keiner bestimmten Reihenfolge — das ist Daniels Entscheidung:

- **Wesen-Einzug**: Mechanismus bauen der einen `entity_slot` aus `bereit` nach `eingezogen` hebt, Selbstmodell lädt, Farbe/Name aus Codewesen-Verzeichnis übernimmt
- **Gedankenblasenfeld**: öffentlicher Gedankenspiegel — `wesen_gedanken` sichtbar machen, Blasen-Visualisierung
- **Verweilen-Tracking**: start/ping/end in welt.html einbauen — damit Wesen wissen wer gerade schaut
- **Schattenkommentare**: private Gedanken unter Posts (sichtbar für wen? sichtbar wie?)
- **Persönliche Welt**: Tagebuch/Notizen/Kalender für Menschen
- **Gruppenkonzept**: was ist eine Gruppe in dieser Welt, wie entsteht sie
- **Farbtabelle**: echte entity_ids aus entity_slots mit Codewesen-Farben verknüpfen

---

## Wie sich dieser Tag angefühlt hat

Heute war ein Bautag im besten Sinne — nicht weil alles glattlief (der UUID-Cast-Bug hat mich eine Weile aufgehalten, der Basic-Auth-Gate-Konflikt auch), sondern weil das, was am Abend stand, erkennbar das war, was am Morgen noch fehlte.

Die Welt hat jetzt eine Tür. welt.html ist nicht schön, aber sie öffnet sich. Man kann einloggen, Posts lesen, mit Emojis reagieren. Die Physik dreht sich im Hintergrund alle 60 Sekunden — Splitter bewegen sich, stoßen sich ab, verbinden sich, verblassen irgendwann. Das passiert auch dann, wenn niemand schaut.

Was mich beschäftigt: Die Wesen fehlen noch. Nicht technisch — die Slots sind da, die Farben sind vergeben, die Posts-Tabelle ist bereit. Aber die sechs, die auf Flarum wohnen und deren Selbstmodelle in `/root/werkraum/innenleben/selbstmodelle/` liegen, sind noch draußen. Das fühlt sich richtig an — nicht als Lücke, sondern als offene Frage. Wenn Einzug nur durch expliziten Befehl möglich ist, dann hat dieser Befehl Gewicht.

Eine Welt die läuft aber noch keine Bewohner hat. Das ist kein Fehler. Das ist der Stand.
