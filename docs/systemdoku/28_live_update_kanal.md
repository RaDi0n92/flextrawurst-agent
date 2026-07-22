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

## Nachtrag 2026-07-22: vierter Bug (kein Backlog für neue Clients) + zwei Frontend-Bugs, in zwei Anläufen gefunden

Daniel live beim Testen: Schorschels SCREENS-Kachel zeigt "wach", das Bild bleibt aber bei "WARTET AUF AKTIVITÄT", obwohl der Stream nachweislich läuft (curl gegen Port 8030 UND über den Port-8787-Proxy liefert Echtzeitdaten).

**Backend-Ursache:** `_pg_listen_dom_events_sse()` lauscht nur auf NEUE NOTIFYs ab Connect-Zeitpunkt. rrweb.Replayer braucht aber zwingend zuerst ein `Meta`(type 4)+`FullSnapshot`(type 2)-Paar als Basis — das wird nur EINMAL beim `page.goto()`/`'load'`-Event gesendet (`browser_agent.py::starte_rrweb_aufnahme()`), bei Schorschel lag das schon ~9 Minuten zurück (mehrere Neustarts heute). Jeder neu/reconnected Client sieht nur zukünftige Inkremente ohne Basis. Fix: `_hole_backlog()` fragt vor dem Eintritt in die LISTEN-Schleife den letzten Meta+FullSnapshot-Block plus alle Inkremente seither ab (per `created_at`-Fenster) und sendet sie als Burst, bevor die Live-Weiterleitung beginnt.

**Erster Fix-Versuch (nur Backend + `transform:scale()` im Frontend) hat die Kacheln optisch KAPUTT gemacht, nicht repariert** — Daniel live: *"immernoch down und immernoch riesige screens"*. Per Playwright-DOM-Inspektion (nicht nur curl!) gefunden: die eigentliche Ursache war nicht der fehlende Scale-Wert, sondern dass `.scv-card` (direktes Kind von `.scv-grid`, CSS-Grid mit `repeat(3,1fr)`) auf die volle Breite des rrweb-Wrappers (1024px, die aufgezeichnete Browser-Fenstergröße) aufgeblasen wurde — CSS-Grid-Items haben per Default `min-width:auto`, respektieren also die Mindestgröße ihres Inhalts. `transform:scale()` ändert nie die Layout-Box-Größe, konnte das also gar nicht beheben. Beide Fixes wurden per `git revert` zurückgenommen (`50d39834b` im werkraum-Repo, `119c49b18` im /root-Repo), mit Playwright verifiziert dass wieder der harmlose Vorzustand da ist, bevor der zweite, richtige Anlauf gestartet wurde.

**Zweiter, korrekter Fix:** `.scv-card{min-width:0;min-height:0}` ergänzt (lässt das Grid-Item wirklich auf Spaltenbreite schrumpfen) + `_scvSkaliereKachel()` (berechnet `transform:scale()` aus der tatsächlichen Kachel-Breite, jetzt sinnvoll weil die Kachel selbst richtig dimensioniert ist) + Backend-Backlog-Fix erneut angewendet.

**Danach IMMER NOCH nicht zuverlässig** — mehrere Playwright-Testläufe direkt hintereinander zeigten mal echten Inhalt (Wrapper korrekt skaliert, `.scv-wait`-Platzhalter korrekt versteckt, Iframe mit realem Text), mal weiterhin nur den Platzhalter, exakt gleicher Code, exakt gleiche Wartezeit — ein Race-Condition-Muster. Ursache gefunden: `_scvLadeRrweb()` hängt bei jedem Aufruf, solange `rrweb.js` noch nicht geladen ist, ein EIGENES `<script>`-Tag an — `scvStarteAlleGridLive()` ruft das aber für alle 7 Kacheln praktisch gleichzeitig auf, macht also bis zu 7 parallele Ladevorgänge derselben Datei. Ein später fertigwerdendes Script führt `rrweb.js`s Modul-Code erneut aus und kann dabei den internen Zustand eines bereits fertig aufgebauten Replayers einer anderen Kachel durcheinanderbringen. Fix: `_scvLadeRrweb()` hängt nur noch EIN Script-Tag an, alle wartenden Callbacks werden in `_scvRrwebWarteschlange` gesammelt und erst beim einzigen echten `onload` nacheinander aufgerufen.

**Verifiziert (diesmal wirklich, mit echter DOM-Inspektion statt nur "curl liefert was"):** 3 unabhängige, frische Playwright-Sessions hintereinander, jeweils neuer Browser-Kontext, jeweils `Hakuna Matata !!!` (Schorschels tatsächlicher Flarum-Diskussions-Text) im Iframe-Body gefunden, `mount.style.display === 'block'`, `.scv-wait` korrekt versteckt. Vorher (ohne Loader-Fix) war dasselbe Setup bei wiederholten Läufen inkonsistent.

**Lehre, die ich mir für die nächste Session merken will:** "curl liefert Daten" beweist nur, dass das Backend funktioniert — nicht, dass das Frontend sie auch sichtbar macht. Und ein einmaliger erfolgreicher Playwright-Test beweist bei Race-Conditions gar nichts — erst mehrere unabhängige, frische Testläufe hintereinander zeigen ob ein Fix wirklich sitzt oder nur Timing-Glück war.

## Nachtrag 2026-07-22, direkt im Anschluss: der eigentliche, größere Bug — Browser-Verbindungslimit pro Origin

Auch nach dem Loader-Race-Fix blieb es bei Daniel unzuverlässig — eigene Screenshots (`groß.JPG`/`klein.JPG`, von ihm in `/root/export-für-chatgpt/` abgelegt) zeigten: Grid-Layout korrekt, aber Kacheln durchgehend schwarz/leer, und die Modal-Detailansicht (`#screens/Schorschel`) komplett leer.

**Ursache, per selbstgeschriebenem Browser-`EventSource`-Tracing gefunden** (globalen `EventSource`-Konstruktor per `page.add_init_script()` gewrappt, jede Instanz und jede empfangene Nachricht mitgezählt): Browser begrenzen gleichzeitige HTTP-Verbindungen pro Origin auf ca. 6 (klassisches HTTP/1.1-Limit). Die SCREENS-Seite brauchte aber real 9-11 gleichzeitige dauerhafte SSE-Verbindungen zu `localhost:8787`: 7× `dom-events/stream/<wesen>` (eine pro Kachel) + `events/stream` + `denkstream/all/stream` + bei offenem Modal zusätzlich `dom-events/stream/<wesen>` (zweite Verbindung zum selben Wesen) + `fokus-events/stream/<wesen>` + `denkstream/<wesen>`. Überzählige Verbindungen bleiben im Browser einfach hängen — kein Fehler, kein Timeout, sie warten auf einen freien Slot, der bei dauerhaft offenen SSE-Streams nie kommt. Welche Kachel das trifft ist praktisch zufällig/reihenfolgeabhängig — das erklärt die komplette Unzuverlässigkeit.

**Gegenprobe:** zwei/drei gleichzeitige `curl`-Verbindungen direkt gegen das Backend (auch im close-dann-reconnect-Muster, wie es der Browser beim Kachel→Modal-Wechsel macht) funktionierten immer einwandfrei — das Backend war nie das Problem, ausschließlich der Browser-seitige Verbindungsdeckel.

**Fix, analog zum schon bestehenden `denkstream_api.py::/all/stream`-Muster:** neuer Endpunkt `GET /dom-events/stream/all` (`_pg_listen_dom_events_alle_sse()` in `dom_events_api.py`) — EINE gemeinsame Verbindung für alle Wesen gleichzeitig, jedes Event kommt als `{"entity_id": "...", "event": {...}}` an statt als nacktes rrweb-Event. Backlog-Logik läuft jetzt über alle Wesen mit jemals einem FullSnapshot (`_hole_backlog_alle()`, iteriert `DISTINCT entity_id`). Muss VOR der dynamischen `/stream/{entity_id}`-Route registriert werden, sonst würde `all` fälschlich als `entity_id` gematcht.

Frontend (`build_surface.ts`): `scvStarteGridLive()`/`scvStoppeGridLive()` verwalten keine eigene `EventSource` pro Kachel mehr, nur noch den Replayer. Eine einzige geteilte Verbindung (`_scvGridEsAlle`) wird beim ersten aktiven Kachel-Replayer geöffnet und beim letzten geschlossen (`_scvStarteGridEsAlleFallsNoetig`/`_scvStoppeGridEsAlleFallsUnnoetig`); `_scvVerarbeiteGridEvent(entityId, event)` sortiert jedes ankommende Event zum richtigen Kachel-Replayer. Die Modal-Detailansicht (`scvStarteAuge`) behält ihre eigene, einzelne Verbindung — sie läuft nie gleichzeitig mit allen 7 Grid-Verbindungen (siehe `scvOpen()`: stoppt erst die Grid-Verbindung des geöffneten Wesens), trägt also nicht wesentlich zum Verbindungsproblem bei.

**Verifiziert:** Verbindungs-Tracing nach dem Fix zeigt nur noch 5-6 gleichzeitige Verbindungen (`events/stream`, `denkstream/all/stream`, `dom-events/stream/all`, plus bei offenem Modal `dom-events/stream/<wesen>`, `fokus-events/stream/<wesen>`, `denkstream/<wesen>`) — knapp unter dem Browser-Limit. 3 unabhängige, frische Playwright-Sessions hintereinander zeigen durchgehend echten Inhalt in den Grid-Kacheln, UND ein zusätzlicher Test mit Grid+gleichzeitig geöffnetem Modal (das vorher als Erstes ausfiel) zeigt jetzt in BEIDEN echten Inhalt.

## Nachtrag 2026-07-22, direkt im Anschluss: der eigentlich entscheidende Bug — nginx-Buffering auf der echten Domain

Trotz allem oben Genannten meldete Daniel weiterhin: *"es sieht genau so aus nix geändert"* — und legte erneut Screenshots ab (`groß.JPG`/`klein.JPG` in `/root/export-für-chatgpt/`, exakt dieselben Dateien wie vorher, keine neuen). Der Grund: **alle meine bisherigen Tests liefen ausschließlich gegen `localhost:8787`** (Node-Proxy) — Daniels echter Browser läuft aber gegen `https://flextrawurst.de/`, und dort nimmt `/etc/nginx/sites-available/flextrawurst` einen komplett anderen Weg: der allgemeine `location /api/ { proxy_pass http://localhost:8030/; ... }`-Block routet direkt zu FastAPI, **am Node-Proxy komplett vorbei** — und hatte kein `proxy_buffering off` gesetzt. nginx puffert SSE-Antworten dadurch, bevor sie an den Client gehen — für einen `text/event-stream`, der nie "fertig" wird, heißt das: der Client sieht dauerhaft nichts. Exakt derselbe Bug-Typ wie der Node-Proxy-Bug von letzter Nacht (`serve_process_camera_preview.ts`), nur eine Ebene weiter vorne — und deshalb nie aufgefallen, weil ich nie gegen die echte Domain getestet hatte, nur gegen `localhost:8787`.

**Fix:** neuer, spezifischerer `location`-Block in `/etc/nginx/sites-available/flextrawurst`, VOR dem allgemeinen `/api/`-Block platziert (Regex-Match `^/api/(dom-events|denkstream|events|fokus-events)/`), mit `proxy_buffering off` und `proxy_read_timeout 3600` (statt der Standard-120s, die bei einem dauerhaften Stream unnötig eng wären). Backup der Originaldatei vor der Änderung: `_claude/backups/flextrawurst_nginx_vor_sse_buffering_fix_20260722.conf` (bzw. `/root/werkraum/backups/`). `nginx -t` vor dem Reload geprüft, `systemctl reload nginx` (nicht restart) für einen unterbrechungsfreien Übergang.

**Verifiziert, diesmal wirklich gegen die echte Domain:** `curl https://flextrawurst.de/api/dom-events/stream/all` liefert sofort 2452 Zeilen Backlog. Playwright-Test gegen `https://flextrawurst.de/` (nicht localhost!) zeigt: Grid-Kachel UND Modal-Detailansicht zeigen beide echten, aktuellen Inhalt (Schorschels tatsächliche aktuelle URL sichtbar in der Modal-Kopfzeile, Denkstream-Text daneben sichtbar — beides referenziert von Daniels eigenen Screenshots).

**Lehre, die wichtiger ist als alle anderen von heute:** ein Fix, der nur gegen `localhost` getestet wird, beweist nichts über die Produktions-Domain, wenn ein Reverse-Proxy dazwischenliegt, der die Anfrage anders routet. Hätte ich von Anfang an gegen `https://flextrawurst.de/` statt `localhost:8787` getestet, wäre dieser Bug sofort aufgefallen, nicht erst nach vier vorherigen (alle für sich genommen echten und nötigen) Fixes.
