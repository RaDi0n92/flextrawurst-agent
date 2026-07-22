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

## Nachtrag 2026-07-21 (spätabends): systemischer Zuverlässigkeits-Bug in ALLEN vier LISTEN/NOTIFY-SSE-Endpunkten gefunden und behoben

Auftrag von Daniel: Browser-Agenten "weiterfeilen ... dass alles live schnell richtig verfolgbar ist". Beim Bau des neuen Live-Spiegels im SCREENS-Grid (siehe [[29_browser_agent_aktivierung]]) fiel auf, dass `dom_events_api.py`s SSE-Stream über Stunden hinweg in wiederholten, sorgfältig kontrollierten Tests (Playwright, curl direkt gegen Port 8030, Ground-Truth-Vergleich per unabhängigem LISTEN-Skript) **konsequent nichts auslieferte** — trotz nachweislich aktiver NOTIFYs auf dem Kanal.

**Zwei unabhängige, sich überlagernde Bugs gefunden, beide seit dem Bau dieser vier Dateien am 2026-07-21 vormittags vorhanden:**

**Bug 1 — `bool(select.select(...))` ist immer `True`.** `select.select()` gibt immer ein 3-Tupel zurück (auch bei Timeout, dann mit drei leeren Listen drin) — ein nicht-leeres Tupel ist in Python immer wahr, unabhängig vom Inhalt. `_poll_once()` in allen vier Dateien gab damit immer `True` zurück, der `else`-Zweig (Heartbeat-Zählung) war toter Code. Folge: kein Heartbeat-Kommentar wurde je gesendet, verwaiste Verbindungen hatten kein Lebenszeichen. Fix: `readable, _, _ = sel.select(...); return bool(readable)`.

**Bug 2 (der eigentliche Stille-Killer) — Verbindungsaufbau und Notify-Verarbeitung liefen auf verschiedenen Threads.** Alle vier Routen (`denkstream_sse`, `dom_events_sse`, `fokus_events_sse`, `events_sse`) waren als **synchrone** `def`-Funktionen deklariert. FastAPI führt synchrone Routen über `anyio.to_thread.run_sync()` in einem Worker-Thread aus — `psycopg2.connect()` + `cur.execute("LISTEN ...")` liefen also dort. Die zurückgegebene `StreamingResponse` iteriert den `async def gen()`-Generator danach aber auf dem **Event-Loop-Thread** — `conn.poll()` und der Zugriff auf `conn.notifies` liefen folglich auf einem anderen Thread als der, auf dem die Verbindung geboren wurde. Ein isoliertes Standalone-Skript mit identischer LISTEN/poll-Logik auf **einem** durchgehenden Thread empfing Notifies zuverlässig; ein Selbsttest (`pg_notify` unmittelbar aus derselben Codestelle heraus gefeuert) kam ebenfalls an — aber echte NOTIFYs von externen, separaten Prozessen (browser_agent.py, echte Ankündigungs-INSERTs) kamen nie zuverlässig durch. Mit einem parallel laufenden, unabhängigen Ground-Truth-LISTEN-Skript bestätigt: NOTIFYs kamen auf dem Kanal an, die SSE-Verbindung lieferte trotzdem nichts.

Fix: `psycopg2.connect()` + `LISTEN` ziehen in `async def gen()` selbst hinein (läuft dann konsequent auf dem Event-Loop-Thread), die vier Routen-Funktionen von `def` auf `async def` umgestellt (damit FastAPI sie direkt auf dem Event-Loop ausführt, kein Worker-Thread-Sprung mehr für den Verbindungsaufbau).

**Betroffen waren alle vier:** `denkstream_api.py` (`_pg_listen_sse`, beide Routen `/{entity_id}` und `/all/stream`), `dom_events_api.py`, `fokus_events_api.py`, `events_stream_api.py` — also potenziell der komplette Grundgesetz-8-Unterbau, nicht nur der neue Live-Spiegel. Die frühere "Voller Live-Test"-Verifikation weiter oben in diesem Dokument (Ankündigungen, `events_stream_api.py`) hat den Bug vermutlich nicht bemerkt, weil ihr Test-Insert zeitlich eng genug an den Poll-Zyklus grenzte, um trotzdem durchzukommen — genau das Muster, das auch bei den eigenen Selbsttests heute gelegentlich "zufällig" funktionierte.

**Verifiziert nach dem Fix:** Pre-etablierte curl-SSE-Verbindung + parallel laufendes, unabhängiges Ground-Truth-LISTEN-Skript über 130s, alle 7 Wesen gleichzeitig beobachtet — reale `entity_dom_events`-NOTIFYs von drei verschiedenen Wesen (Schorschel, träumerlie, F3INSCHM3CK3R) kamen jeweils binnen ~0,1–1s bei der SSE-Verbindung an, exakt zeitgleich mit dem Ground-Truth-Treffer. Zusätzlich per echtem Playwright-Browsertest (nicht nur curl) bestätigt: SCREENS-Grid-Kachel wechselt von "WARTET AUF AKTIVITÄT" auf sichtbaren Live-Inhalt, sobald ein Event eintrifft.

**Separat gefunden, aber NICHT verändert (nginx-Proxy im Frontend hatte einen dritten, unabhängigen Bug):** siehe [[29_browser_agent_aktivierung]] für den gepufferten `/api/*`-Proxy in `serve_process_camera_preview.ts`, der zusätzlich jeden SSE-Stream über Port 8787 blockierte.

## Nachtrag 2026-07-22: vierter Bug, nur bei `dom_events_sse` — kein Backlog für neu verbundene Clients

Daniel live beim Testen: Schorschels SCREENS-Kachel zeigt "wach" im Status, das Bild bleibt aber dauerhaft bei "WARTET AUF AKTIVITÄT", obwohl der Stream nachweislich läuft (mit curl direkt gegen Port 8030 UND über den Port-8787-Proxy verifiziert — beide liefern in Echtzeit echte `entity_dom_events`, kein Reste des Bugs von oben).

**Ursache:** `_pg_listen_dom_events_sse()` lauscht ausschließlich auf NEUE NOTIFYs ab dem Moment des Connects — komplett korrekt für normale Mutations-Events, aber rrweb.Replayer braucht zwingend zuerst ein `Meta`(type 4)+`FullSnapshot`(type 2)-Paar, um überhaupt eine Basis-DOM zu haben, auf die spätere inkrementelle Events (type 3) angewendet werden können. Dieses Paar wird nur EINMAL gesendet, beim `page.goto()`/`'load'`-Event des Wesens (siehe `starte_rrweb_aufnahme()` in `browser_agent.py`) — bei Schorschel lag das zum Zeitpunkt von Daniels Test schon ~9 Minuten zurück (mehrere Neustarts heute für die mechanische-Bewegung- und Check-in-Arbeit). Jeder Browser, der SEIT diesem Full-Snapshot verbindet oder reconnected (z.B. nach Seiten-Reload), sieht dadurch nur noch zukünftige Inkremente ohne Basis — der Replayer hat nichts zum Draufsetzen und bleibt für immer bei "wartet", unabhängig davon wie aktiv das Wesen tatsächlich ist. Verifiziert per direkter Abfrage: `WHERE event_json->>'type' = '2'` zeigte den letzten FullSnapshot für Schorschel bei `06:47:55` UTC, während der Test um `06:56+` lief — 4882 Events lagen dazwischen, alle für einen frisch verbundenen Client unsichtbar.

**Fix:** `_pg_listen_dom_events_sse()` fragt jetzt vor dem Eintritt in die LISTEN-Schleife per `_hole_backlog()` den zuletzt aktiven Meta+FullSnapshot-Block (und alle Inkremente seither, per `created_at`-Fenster) ab und sendet ihn als Backlog-Burst, bevor die normale Live-Weiterleitung beginnt. Kein Fix in `denkstream_api.py`/`fokus_events_api.py`/`events_stream_api.py` nötig — die haben kein "Basis-Snapshot"-Konzept, reine Text-/Notify-Streams brauchen keinen Bootstrap.

**Verifiziert:** frische curl-Verbindung gegen Port 8030 UND gegen den Port-8787-Proxy liefert sofort 288 Backlog-Zeilen (Meta zuerst, dann FullSnapshot, dann alle Inkremente), bevor der Live-Teil weiterläuft. `welt-api.service` danach `active`.
