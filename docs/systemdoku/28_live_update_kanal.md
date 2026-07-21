# Live-Update-Kanal — Grundgesetz 8 "Live statt F5"

**Datum:** 2026-07-21, Daniels expliziter Auftrag: *"ab sofort immer alles sofort am besten live aktualisiert und geupdatet ist auf ganz flextrawurst nicht immer erst bei f5."* Als Grundgesetz 8 in `/root/CLAUDE.md` festgehalten.

Generischer, systemweiter Mechanismus, damit Ansichten sich selbst aktualisieren, sobald sich Daten ändern — ohne manuellen Reload. Kein Neubau von Null: baut auf zwei bereits bestehenden Mustern auf (WebSocket für Gruppen-Chat, SSE für Denkstream — `denkstream_api.py`), generalisiert sie auf die bereits heilige `events`-Tabelle (Grundgesetz 5).

## Architektur

```
INSERT INTO events (...)          -- passiert schon überall (Grundgesetz 5)
        ↓
trg_notify_events (Trigger)       -- welt/migration_events_stream.sql
        ↓
pg_notify('events_stream', ...)   -- minimaler Payload, siehe unten
        ↓
GET /events/stream?praefix=...    -- welt/events_stream_api.py, SSE, öffentlich
        ↓
EventSource im Browser            -- ftwLiveVerbinden(), build_surface.ts
        ↓
ftwLiveRegistrieren('praefix', fn) -- jede Ansicht entscheidet selbst was sie neu lädt
```

## Backend

- `welt/migration_events_stream.sql`: `notify_events()`-Funktion + `trg_notify_events AFTER INSERT ON events`. Analog zum bestehenden `trg_notify_denkstream`-Muster (`migration_denkstream.sql`), nur generisch auf die `events`-Tabelle statt nur `entity_denkstream`.
- **Bewusst minimaler NOTIFY-Payload:** nur `event_type`, `created_at` und drei kuratierte, unsensible Routing-Hinweise (`ankuendigung_id`, `post_ref`, `post_source` — aus `payload->>'...'` extrahiert, falls vorhanden). **Kein** Kommentar-Text, keine Emoji-Reaktion, kein voller `payload`. Grund: der SSE-Endpunkt ist öffentlich und auth-frei (wie Denkstream) — er darf niemals eine zweite, ungeschützte Datenquelle sein. Das Frontend holt sich die echten Daten weiterhin über die normalen, auth-geprüften REST-Endpunkte; der Stream ist nur das Signal "hier hat sich was getan, frag nach".
- `welt/events_stream_api.py`: `GET /events/stream?praefix=xyz` — SSE, öffentlich, kein Auth. `praefix` filtert serverseitig nach `event_type`-Anfang (z.B. `praefix=ankuendigung` liefert nur `ankuendigung.*`-Events). Ohne `praefix` kommen alle Events durch. Gleiches LISTEN/Poll/Heartbeat-Muster wie `denkstream_api.py::_pg_listen_sse` (30s-Heartbeat gegen tote Verbindungen), eigenständig implementiert statt der denkstream-Funktion wiederverwendet, weil die dortige Filterlogik (`entity_id`) nicht passt.
- In `api.py` eingebunden wie `denkstream_router` (`try`/`except ImportError`, gleiches Fallback-Muster).
- Kein extra nginx-Standort nötig — läuft über den bestehenden generischen `/api/`-Block, `X-Accel-Buffering: no`-Header deaktiviert Puffering pro Response (gleicher Trick wie Denkstream).

## Frontend

- `build_surface.ts`: **eine** gemeinsame `EventSource`-Verbindung für die ganze Seite (`ftwLiveVerbinden()`, aufgerufen bei `DOMContentLoaded`), nicht eine pro Tab/Ansicht. `window._ftwLiveHandler` als Registry (bewusst `window`-Property statt `var`/`let` — Ansichten registrieren sich schon beim Skript-Laden, lange bevor die Verbindungs-Logik weiter unten in der Datei ausgeführt wird; eine `window`-Property ist beim ersten Zugriff unabhängig von der Reihenfolge im Skript da, ein normal deklarierter Array-State-Wert wäre an dieser Stelle noch `undefined` gewesen).
- `ftwLiveRegistrieren(praefix, fn)`: Ansicht registriert sich für einen `event_type`-Präfix, `fn` wird bei jedem passenden Signal aufgerufen.
- Cleanup bei `beforeunload` (`window._ftwLiveEs.close()`), im bestehenden SSE-Cleanup-Block ergänzt.

## Erster Anschluss: Ankündigungen

`akLiveUpdate(data)` registriert sich für `'ankuendigung'` und (gefiltert auf `post_source==='ankuendigung'`) für `'resonanz'`. Verhalten:
- Liste/Feed/Archiv werden nur neu geladen, wenn der Ankündigungen-Tab gerade aktiv ist (`activeView==='ankuendigungen'`) — kein sinnloses Nachladen im Hintergrund.
- Ist gerade eine Detailansicht offen (`akDetailOffenId` — neue State-Variable, gesetzt in `akDetailOeffnen()`/gelöscht in `ankDetailSchliessen()`) und betrifft das Signal genau diese Ankündigung (`ankuendigung_id`/`post_ref` stimmt überein), werden zusätzlich Kommentare und Resonanz-Zähler in der offenen Ansicht direkt aktualisiert.

**Rollout bewusst schrittweise** (Daniels Entscheidung nach Rückfrage): Ankündigungen zuerst als vollständiges, funktionierendes Muster, der Rest von flextrawurst wird nach und nach angeschlossen, wenn an den jeweiligen Bereichen ohnehin gearbeitet wird — kein einzelner Großumbau über alle ~20 Tabs auf einmal.

## Verifikation

- DB-Trigger isoliert getestet: `LISTEN events_stream` in einer psql-Session, `INSERT INTO events` in einer zweiten — Notify kommt mit korrektem, minimalem Payload an.
- SSE-Endpunkt End-to-End getestet: `curl -sN` gegen `localhost:8030` UND über die echte Domain (`https://flextrawurst.de/api/events/stream`) — beide liefern den erwarteten Payload.
- **Voller Live-Test ohne F5, per Playwright:** Seite geladen, Ankündigungen-Tab geöffnet, `window._ftwLiveEs.readyState === 1` (OPEN) bestätigt. Danach — **ohne die Seite neu zu laden** — direkt in der DB eine neue Ankündigung angelegt (exakt wie der echte POST-Endpunt: INSERT + zugehöriges Event). Anzeige sprang danach automatisch von 0 auf 1 Ankündigungen, der neue Titel erschien in der Liste. Kein JS-Fehler. Test-Eintrag danach weich gelöscht (Archiv, wiederherstellbar).
- Nebenbefund beim Testen: `wait_until='networkidle'` in Playwright greift auf dieser Seite nicht mehr sauber, weil die dauerhaft offene `EventSource`-Verbindung das Netzwerk nie "idle" werden lässt — für künftige Playwright-Tests auf dieser Seite `domcontentloaded` + explizites `wait_for_timeout` statt `networkidle` verwenden.
