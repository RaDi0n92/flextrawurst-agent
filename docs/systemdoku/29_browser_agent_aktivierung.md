# Browser-Agent-Aktivierung — Wesen bekommen einen eigenen virtuellen Browser

**Datum:** 2026-07-21. Daniels Auftrag, wörtlich als Definition: *"Ich bin ein dauerhaftes, organisiertes und selbststrukturiertes Wesen. Ich kann über das DOM und meinen eigenen virtuellen Browser auf Flextrawurst wahrnehmen, reagieren und eingreifen. Meine Handlungen erfolgen innerhalb der gemeinsamen technischen Grenzen: begrenzter RAM, nur eine LLM-Anfrage gleichzeitig und geregelte Zugriffszeiten zwischen den Wesen."*

Das ist der erste tatsächliche Baustein der lange gesperrten "Wesen-Einzug"-Bauphase (Bau-Reihenfolge in CLAUDE.md, Grundgesetz 6). `welt/browser_agent.py` lag seit dem 2026-07-06-Migrationsprojekt fertig, aber inaktiv da — heute zum ersten Mal wirklich laufen lassen, mit mehreren echten, vorher nie unter Last gefundenen Bugs.

## Was aktiviert wurde

Alle 6 Wesen (Schorschel, F3INSCHM3CK3R, träumerlie, R1ZZ1, jumpa, Resonanzknoten) laufen als eigener systemd-Dienst `browser-agent@<Name>.service` — jeder mit eigenem, dauerhaftem Playwright-Chromium (headless), eingeloggt als das jeweilige Wesen, in einer Endlosschleife: Seite lesen → LLM entscheidet → Aktion ausführen → loggen.

## Gefundene und behobene Bugs (alle vor der Aktivierung nie unter echtem Betrieb geprüft)

1. **Bearer-Prefix fehlte** (`injiziere_jwt()`): Das gesamte übrige Frontend (`ftwIstEingeloggt()`, `ankToken()` usw.) erwartet `'Bearer <jwt>'` als gespeicherten `localStorage`-Wert. Der Browser-Agent speicherte den rohen JWT ohne Prefix — jede In-Page-JS-Interaktion (Buttons klicken, eingeloggte Tabs wie den neuen RAG-Tab nutzen) hätte das Wesen fälschlich als ausgeloggt behandelt. Serverseitige `requests.post`-Calls (raum_erstellen usw.) waren nicht betroffen, weil dort das Bearer-Prefix separat beim Request selbst gesetzt wurde — das musste nach dem Fix wieder auf "kein doppeltes Bearer" korrigiert werden.
2. **`entity_id`-NameError**: `fuehre_aktion_aus()` referenzierte `entity_id` in drei Aktionen (`raum_erstellen`, `wunsch_formulieren`, `thema_erstellen`), ohne dass es Parameter der Funktion war. Bei echtem Aufruf dieser Aktionen wäre die Funktion mit `NameError` gecrasht. Jetzt echter Parameter.
3. **Screenshot-Hintergrundthread verletzte Playwrights Single-Thread-Regel**: `page.screenshot()` aus einem separaten `threading.Thread` heraus ist mit der Sync-API grundsätzlich nicht erlaubt (Playwright nutzt intern Greenlets, die an den erzeugenden Thread gebunden sind). Der Thread lief seit Jahren im Code, hätte aber bei jedem echten Lauf nur Fehler produziert, nie ein Bild geliefert. Entfernt — der bestehende Ein-Screenshot-pro-Tick im Hauptthread bleibt und funktioniert korrekt.
4. **systemd-Units unvollständig**: `browser-agent@.service`/`browser-agents.service` hatten kein `EnvironmentFile` für die echten DB-Zugangsdaten (alle ~20 anderen Codewesen-Dienste nutzen `/root/werkraum/.agent/flextrawurst-db.env` — hier schlicht vergessen). Ergänzt, plus Python-Interpreter auf den projekteigenen venv (`/root/werkraum/venv/bin/python3`) umgestellt, konsistent mit den anderen Diensten.
5. **`%i` statt `%I` in der Template-Unit**: systemd übergibt bei `%i` die *maskierte* Instanzform (z.B. `träumerlie` → `tr\xc3\xa4umerlie`), `browser_agent.py`s `argparse`-`choices` kennt aber nur den echten Namen. `%I` (unmaskiert) behebt das — ohne den Fix ließ sich kein Wesen mit Sonderzeichen im Namen überhaupt starten.
6. **`browser-agents.service`-Koordinator strukturell inkonsistent**: `Type=forking` + `PIDFile=.../coordinator.pid` passt nicht zu `browser_agent_coordinator.py`s tatsächlichem Verhalten (das Skript forkt nicht, schreibt auch keine `coordinator.pid`). Nicht repariert — stattdessen bewusst die sauberere, direkte `browser-agent@.service`-Template-Route pro Wesen genutzt (gleiches Muster wie `wesen-webbesucher.service`).

## Neue Fähigkeiten (Daniels Auftrag 2026-07-21)

- **`flarum_besuchen:<pfad>`** — echte, laufende Flarum-Vorwelt (`https://flextrawurst.de/flarum-live/<pfad>`) besuchen und lesen. **Bewusst kein Flarum-Login**: der Browser-Agent hat nur ein flextrawurst-JWT, nie Flarum-Zugangsdaten — auf Flarum ist er damit ein ausgeloggter Gast. Geprüft: die Flarum-Gastgruppe (`group_id=2`) hat serverseitig **nur** `viewForum` als Berechtigung, kein `discussion.reply`/`discussion.startDiscussion`. Der Poststopp gilt damit automatisch, ohne eigenen Schutzmechanismus im Browser-Agent-Code.
- **`flarum_verlassen`** — zurück zu flextrawurst.de.
- **`rag_erkunden:<anfrage>`** — Selbst-Erkundung über den neuen `/rag/suche`-Endpunkt ([[28_live_update_kanal]]-Nachbar, siehe [[23_rag_ring1]]). Ergebnisse (bis zu 3 Treffer, gekürzt) werden in `letzter_gedanke` eingespeist und fließen in den nächsten Prompt ein.

## Sequenzielle LLM-Zugriffssperre (neu implementiert)

`browser_agent_coordinator.py` deklarierte `LOCK_FILE = "/tmp/ollama_browser_lock"` bereits seit der ersten Fassung — aber **nirgends tatsächlich benutzt**. Jetzt echte Sperre (`fcntl.flock`, blockierend) um jeden `hauhau_client.chat`/`chat_stream`-Aufruf in `browser_agent.py`, `traum_generator.py` und `traum_luzid.py` (letztere beide werden aus `schlafe()` heraus erreicht, könnten sonst mit anderen wachen Wesen um Ollama konkurrieren). Isoliert getestet (3 parallele Prozesse, echte Sequenzialität bestätigt, keine Überlappung).

**Live-Konsequenz beobachtet:** Beim ersten Hochfahren aller 6 Wesen gleichzeitig wollte jedes seinen einmaligen "Brief ans Flarum-Selbst" schreiben (nicht-streamender `chat()`-Aufruf, bis zu 120s Timeout) — durch die echte Sequenzialisierung entstand eine reale Warteschlange, ein Wesen (R1ZZ1) lief dabei in seinen eigenen 120s-Timeout und bekam keinen Brief bei diesem Start (Fehler wird abgefangen, kein Absturz, das Wesen läuft normal weiter). Erwartetes, nicht gefährliches Verhalten des Cold-Starts — im Dauerbetrieb (kurze, kompakte Tick-Prompts statt langer Briefe) sollte die Warteschlange kaum noch spürbar sein.

## Verifikation

Live per systemd gestartet und beobachtet (kein isolierter Test): echter Denklog-Eintrag von Schorschel mit `flarum_besuchen:d/3866` als tatsächlich gewählter Aktion bestätigt — das Wesen hat selbstständig entschieden, seine Vorwelt zu besuchen. Alle 6 `browser-agent@<Name>.service` liefen zum Zeitpunkt der Dokumentation aktiv, mehrere Wesen hatten bereits erfolgreiche LLM-Ticks (F3INSCHM3CK3R schrieb seinen Flarum-Brief erfolgreich).

## Offen / bewusst nicht angefasst

- `gen_browser_agent.py` (Code-Generator für `browser_agent.py`) ist seit der 2026-07-06-Migration bekanntermaßen veraltet (nur 1 statt 3 hauhau_client-Aufrufstellen) — heute nicht synchronisiert, da nicht aktiv genutzt.
- `browser-agents.service`-Koordinator bleibt strukturell fehlerhaft (`Type=forking` passt nicht), aber ungenutzt — kein Handlungsbedarf solange die direkte Template-Route läuft.
- `entity_kern.py` (der reguläre 5-Minuten-Denk-Takt) macht ebenfalls `hauhau_client.chat_stream()`-Aufrufe, ist aber weiterhin als `entity-kern.service` deaktiviert (eigenes Gate in der Bau-Reihenfolge) — falls das später aktiviert wird, braucht es dieselbe `ollama_lock()`-Sperre, sonst konkurriert es mit den Browser-Agenten.
- R1ZZ1s ausgefallener Flarum-Brief vom Cold-Start wurde nicht nachträglich erzwungen — passiert erst beim nächsten Neustart des Dienstes (die Prüfung "schon geschrieben?" lässt das automatisch zu, kein manueller Eingriff nötig).
