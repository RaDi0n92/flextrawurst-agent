---
datum: 2026-07-21
betrifft: [grundgesetz8, live-update-kanal, dom_events_api, denkstream_api, fokus_events_api, events_stream_api, fastapi, browser_agent, screens-tab]
importable: false
autor: claude-code bei Daniels VPS
---

## Was ich heute über das System gelernt habe

**Der komplette Grundgesetz-8-Unterbau (`_pg_listen_sse`-Muster) hatte einen latenten, systemischen Bug — in allen vier Kopien.** `denkstream_api.py`, `dom_events_api.py`, `fokus_events_api.py`, `events_stream_api.py` bauen alle auf demselben LISTEN/poll/notifies-Muster auf (ursprünglich in `denkstream_api.py` entstanden, die anderen drei per Copy-Paste am selben Tag danach gebaut). Zwei Bugs, überlagert: (1) `bool(select.select(...))` ist IMMER `True`, weil `select()` immer ein 3-Tupel zurückgibt — der Heartbeat-Zweig war seit Einführung toter Code. (2) Der eigentliche Stille-Killer: die Routen-Funktionen waren SYNCHRON (`def`, nicht `async def`). FastAPI führt synchrone Routen über einen anyio-Worker-Thread aus — `psycopg2.connect()` + `LISTEN` liefen dort. Der zurückgegebene async-Generator (der `conn.poll()`/`conn.notifies` benutzt) läuft aber auf dem Event-Loop-Thread. Reale NOTIFYs von externen, separaten Prozessen (browser_agent.py, echte INSERTs) kamen dadurch nie zuverlässig an — obwohl ein isoliertes Standalone-Skript mit identischer Logik auf EINEM durchgehenden Thread sie zuverlässig empfing, und ein Selbsttest (Notify aus derselben Codestelle heraus gefeuert) ebenfalls ankam.

**Merksatz für jeden künftigen LISTEN/NOTIFY-SSE-Endpunkt:** Verbindungsaufbau (`psycopg2.connect`) gehört IN die `async def gen()`-Funktion selbst, niemals in eine synchrone Routen-Funktion davor. Die Routen-Funktion muss `async def` sein, sonst läuft sie in einem anderen Thread als der async-Generator, den sie zurückgibt.

**Ein dritter, unabhängiger Bug lag im Node-Frontend-Proxy.** `serve_process_camera_preview.ts`s generischer `/api/*`-Proxy sammelte die GESAMTE Upstream-Antwort in einem Buffer (`chunks.push`, `res.end()` erst bei `gr.on("end")`) bevor er sie weiterreicht — für normale JSON-Requests unsichtbar, aber `text/event-stream`-Antworten enden nie, der Proxy wartete also bis in alle Ewigkeit. Betraf ALLE über Port 8787 laufenden SSE-Streams. Fix: `gr.pipe(res)` statt Sammeln.

**Drei unabhängige Bugs mussten gleichzeitig behoben werden, damit der Live-Spiegel im SCREENS-Grid überhaupt sichtbar wurde** — jeder einzelne hätte für sich allein schon ausgereicht, um alles stumm zu halten. Das erklärt vermutlich auch, warum der frühere "Voller Live-Test"-Eintrag in `28_live_update_kanal.md` (Ankündigungen, selbe Session-Instanz früher am Tag) den Thread-Bug nicht bemerkt hat — vermutlich Timing-Glück beim damaligen Test.

**Wie man einen solchen Bug methodisch sauber findet:** kurze curl-Tests (10-40s) sind bei bursthaften, seltenen Events wertlos — man weiß nie, ob "nichts angekommen" heißt "kaputt" oder "einfach kein Ereignis in diesem Fenster". Erst ein pre-etablierter Client + ein unabhängiges, PARALLEL laufendes Ground-Truth-LISTEN-Skript über einen ausreichend langen Zeitraum (90-130s) liefert eine wirklich beweiskräftige Korrelation ("Ground-Truth-Event bei t=X, Client-Empfang bei t=X+0.1s").

## Was mich überrascht hat

Dass ein Selbsttest, der mit einer Exception fehlschlägt (ungültige UUID in meinem Test-Payload), trotzdem der entscheidende Beweis war — nicht weil er "funktionierte", sondern weil die Exception erst NACH erfolgreicher LISTEN→poll→notifies→Filter-Verarbeitung auftrat. Ein scheiternder Test kann mehr beweisen als ein glatt durchlaufender.

## Was ich mir merken will

Bei jedem neuen FastAPI-SSE/Streaming-Endpunkt zuerst prüfen: ist die Routen-Funktion `async def`? Falls sie `psycopg2`/DB-Verbindungen für LISTEN/NOTIFY nutzt und `def` (sync) ist, ist das ein sofortiges Verdachtsmoment für genau diesen Bug.
