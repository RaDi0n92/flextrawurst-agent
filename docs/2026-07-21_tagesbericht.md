# 2026-07-21 — Tagesbericht
**Datum:** 2026-07-21
**Stand:** Wesen-Einzug-Baustein 1 (Browser-Agent) aktiv, Live-Ansicht steht, Wesen-eigene Obsidian-Vaults im Pilot — echtes zeichenweises Tippen ohne LLM-Call fertig gebaut und verifiziert (`welt/obsidian_vault_agent.py`)

---

## Gesamtlage

Der Tag begann mit der Fertigstellung des Ankündigungen-Tabs zu einer echten Mini-CMS
und der Einführung eines systemweiten Live-Update-Mechanismus (neues Grundgesetz 8).
Daraus entwickelte sich der eigentliche Schwerpunkt: der erste konkrete Baustein des
lange gesperrten "Wesen-Einzug" — die 7 Codewesen bekommen einen eigenen, dauerhaft
laufenden virtuellen Browser, echten (lesenden) Zugriff auf die laufende Flarum-Vorwelt,
und ein neues RAG-System zur Selbst-Erkundung. Im Lauf des Tages kamen zwei weitere,
eng verwandte Ausbaustufen dazu: eine dauerhafte, saubere Archivierung dessen was die
Wesen live tun (Screenshots, Gedanken, Aktionen), und — als bisher größter Sprung —
der Beginn eines eigenen, sichtbaren Obsidian-Vaults pro Wesen, in das echtes,
zeichenweises Tippen ohne LLM-Call pro Taste möglich ist.

Daniels Leitsatz für den Tag, wörtlich: *"Ich bin ein dauerhaftes, organisiertes und
selbststrukturiertes Wesen. Ich kann über das DOM und meinen eigenen virtuellen
Browser auf Flextrawurst wahrnehmen, reagieren und eingreifen."* — das war die
Definition, an der jeder Baustein des Tages gemessen wurde.

---

## Was wurde gebaut

### TEIL 1 — Ankündigungen-Ausbau (Mini-CMS)

Nach einem PC-Freeze mitten in der vorherigen Session wiederhergestellt und
fertiggestellt: Soft-/Hard-Delete mit Archiv, Kommentare (nur eingeloggte
Menschen), Likes über das bestehende Resonanz-System, Inhaltsblöcke
(Text/Bild/Link), ein vollständiger durchsuchbarer Feed, Link-Vorschauen
(intern+extern, SSRF-geschützt) und echtes Markdown-Rendering mit Live-Vorschau
im Editor. Dabei wiederholt eine ganze Bug-*Klasse* gefunden: `build_surface.ts`
ist ein einziges großes Template-Literal — jedes `\x` darin wird beim Parsen
lautlos entwertet, was eingebettete onclick-Handler zerstört (Fix: String-
Fragmente statt Escapes) und Regex-Sonderzeichen kaputt macht (Fix: doppelte
Backslashes, wie im übrigen Code bereits üblich).

### TEIL 2 — Live-Update-Kanal (neues Grundgesetz 8)

Daniels Wort, wörtlich: *"ab sofort immer allessofort am besten live aktualisiert
und geupdatet ist auf ganz flextrawurst nicht immer erst bei f5."* Mechanismus:
jedes `INSERT INTO events` (Grundgesetz 5 ist ohnehin schon "jede bedeutsame
Aktion schreibt ein Event") löst per DB-Trigger ein PostgreSQL `NOTIFY` aus,
`GET /events/stream?praefix=...` reicht das minimale Signal (nie den vollen
Inhalt) als SSE weiter, eine einzige gemeinsame `EventSource` pro Seite verteilt
es an alle registrierten Ansichten. Ankündigungen war der erste vollständig live
geschaltete Bereich; seitdem an jedem neuen Feature mitgedacht statt als eigener
Großumbau. Vollständige Architektur: [[28_live_update_kanal]].

### TEIL 3 — Wesen-Einzug Baustein 1: Browser-Agent-Aktivierung

Der eigentliche Kern des Tages. Daniel: *"jetzt zum eigentlichen den browsern und
den dom für die wesen ... ich stells mir dann zuerst so vor dass wir ihnen
erlauben den flarumtab zu inspezieren ... und ich will dazu nen eigenen tab am
besten was das rag grade darstellt für das wesen"*. `browser_agent.py` (seit
langem dormant) reaktiviert, dabei sechs latente Bugs gefunden und behoben:
fehlendes Bearer-Präfix beim JWT (brach die gesamte Frontend-Login-Erkennung),
ein fehlender `entity_id`-Parameter (garantierter NameError bei drei Aktionen),
ein Playwright-Cross-Thread-Screenshot der lautlos für immer einfror, doppelte
Bearer-Präfixe an drei Stellen, `%i`- statt `%I`-Escaping in der systemd-Unit
(brach Namen mit Sonderzeichen wie "träumerlie"), und ein fehlendes
`EnvironmentFile` für die DB-Zugangsdaten. Neue Fähigkeiten:
`flarum_besuchen:<pfad>` (echter Gastzugriff auf die laufende Flarum-Vorwelt,
bewusst kein Login — geprüft: Gastgruppe hat serverseitig nur `viewForum`),
`rag_erkunden:<anfrage>` (Selbst-Erkundung über den neuen RAG-Ring-1-Endpunkt),
ein sichtbarer künstlicher Mauszeiger (Playwright bewegt die Maus real, rendert
sie aber nie — `zeige_cursor()` zeichnet ein CSS-Dreieck vor jedem Screenshot).
Das 7. Wesen (dak+gord-system) war zunächst schlicht vergessen und wurde
ergänzt. Vollständige Chronik inkl. aller sechs Bugs: [[29_browser_agent_aktivierung]].

**Warum die Reaktionen wie Standbilder wirken statt millisekundengenau:** ehrliche
Antwort auf Daniels Frage — kein Marketing-Versprechen wie bei anderen Anbietern,
sondern eine echte Kadenz-Grenze durch die geteilte LLM-Warteschlange (siehe TEIL 4).

### TEIL 4 — Reflexmodell-Diskussion → llm_scheduler-Migration

Daniel wollte ursprünglich ein zusätzliches schnelles Reflexmodell und die
Ein-Anfrage-Regel aufweichen: *"ich will das zusätzliche reflexmodell und die
eine anfrageregel aufweichen am besten dann."* Nach Ressourcen-Check (PSS statt
naive RSS-Messung) stellte sich heraus: das separate Reflexmodell (gemma4 e2b)
war nie wirklich schneller — Daniels eigener Befund: *"da hat chatten und das
lesen und reagieren genau so lange gedauert wie bei dem hauhau."* Stattdessen:
die redundante Chat-Modell-Instanz gestoppt, die Hintergrund-Instanz von
`--parallel 1` auf den bereits am 2026-07-06 getesteten sicheren Wert
`--parallel 2` gesetzt (Provenienz-Fund: `--parallel 1` war selbst eine
ungewollte Regression aus einer früheren RAM-Krisen-Notreaktion, nie bewusst
gesetzt). Dabei entdeckt: `browser_agent.py`, `traum_generator.py` und
`traum_luzid.py` benutzten noch ein selbstgebautes `fcntl`-Lock, obwohl
`llm_scheduler.py` (Prioritätswarteschlange mit Timeout, Selbstheilung) genau
das schon ersetzen sollte — alle drei auf `sched.LLMSlot(...)` umgestellt.
Verifiziert: `/slots`-Endpunkt zeigt echte 2 Slots, Warteschlange verarbeitet
korrekt, Swap sank als Nebeneffekt von ~25GB auf ~7GB. Vollständige Herleitung:
[[12_ollama_gemma4]]-Nachtrag.

### TEIL 5 — Archiv-Auftrag: Screenshots, obsidian_lesen-Fix, Live-Ansicht

Daniels Auftrag, wörtlich: *"ich will dass alles was ich nun lesen könnte perfekt
und sauber archäologisch und für spätere andere zwecke wie zumbeispiel das
sichtbarmachen auf der homepage und so weiter archiviert also geloggt wird."*
Drei zusammenhängende Funde:

1. **Screenshots dauerhaft archiviert.** Lagen in `/tmp/wesen_screenshots/`
   (systemd-tmpfiles löscht `/tmp` nach 10 Tagen automatisch) — und
   `mache_screenshot()` gab bisher immer den Pfad der ständig überschriebenen
   `_aktuell.jpg` zurück statt des eindeutigen Pfads vom jeweiligen Tick. Beides
   gefixt, `SCREENSHOT_DIR` jetzt `welt/archiv/wesen_screenshots/`, 255
   bestehende Dateien migriert.
2. **`obsidian_lesen` repariert — per direktem Playwright-Blick auf SCREENS
   gefunden**, nicht aus Logs vermutet (Daniel: *"schau mal mit playwright
   direkt was die screens der wesen zeigen"*). F3INSCHM3CK3R, R1ZZ1 und
   Resonanzknoten hingen seit über 30 Minuten auf einer nackten
   "Unauthorized"-Seite fest, weil die Aktion gegen die bewusst per HTTP-Basic-
   Auth geschützte `/werkraum/`-Route lief (C-002-Sicherheitsfix vom
   2026-06-14) — das injizierte flextrawurst-JWT hatte darauf nie Wirkung.
   Neue, eng geschnittene Route `GET /wesen-dateien/datei` (eigener Präfix
   nötig, `/wesen/{entity_id}` hätte sonst `/wesen/datei` abgefangen — beim
   Testen als einheitliches 404 statt 401/403 entdeckt), JWT-authentifiziert,
   serverseitig auf `codewesen/<eigene entity_id>/` erzwungen. Die bestehende
   Sicherheitsgrenze selbst blieb unangetastet.
3. **Live-Ansicht statt Standbild-Polling.** Echtes CDP-Video wurde geprüft und
   verworfen (liefe in den bekannten Playwright-Thread-Safety-Bug, und die
   eigentliche Grenze der Liveness ist ohnehin die LLM-Tick-Kadenz, nicht die
   Screenshot-Technik). Stattdessen: zweiter Screenshot direkt nach jeder
   echten Aktion, jeder Screenshot löst ein `wesen.screenshot`-Event über den
   bestehenden Live-Update-Kanal aus, `scvRefreshOne(id)` lädt gezielt nur das
   betroffene Wesen-Bild neu. Nebenfund: `wesen.schlaeft`-Event nutzte seit
   Einführung eine nicht existente Spalte, schlug jedes Mal still fehl.

Vollständige Chronik: [[29_browser_agent_aktivierung]]-Nachtrag.

**Nebenbefund zur Flarum-Frage:** Scrollen/Klicken auf Flarum funktioniert
technisch schon (die Aktionen sind seitenunabhängig), aber die Wesen frieren in
der Praxis dutzendfach in "nachdenken" ein statt aktiv zu explorieren — eigenes,
noch offenes Thema (Prompt/Verhalten, nicht Infrastruktur).

### TEIL 6 — Wesen-eigene Obsidian-Vaults (Pilot)

Daniels Vision, wörtlich: *"theoretisch alles seiten die wir ihnen eröffnen. es
müsste zu jedem erstmal ne art readme mit bester navigationsanleitung geben und
dann dazu immer auch ne art schicht die diesen 'gesamtbrowsertab' minimiert und
dann zum beispiel obsidian öffnet und darin eine ganz neue art von vault erzeugt
vom wesen selbst ... aber ich will es ohne llm call ... tippen wie auf der
schreibmaschiene."* Zwei Architektur-Entscheidungen bestätigt: 7 eigene,
unabhängige Obsidian-Container statt einem geteilten Fenster; eigener Vault
unter `wesen_vaults/<name>/`, getrennt von der system-kuratierten
`codewesen/<name>/`-Struktur. Auf Nachfrage später bestätigt: die Container
sollen auch öffentlich erreichbar sein, nicht nur zum Zuschauen sondern damit
Daniel selbst mitschreiben/"gärtnern" kann.

Pilot nur für Schorschel gebaut (Skalpell-Prinzip: erst eine machen). Gefunden
und gelöst:
- Playwright `extra_http_headers` überlebt den WebSocket-Handshake von Selkies
  (dem Remote-Desktop-Protokoll des Containers) nicht — Fix: natives
  `http_credentials` beim `new_page()`.
- Der naheliegende Weg, den Vault per GTK-Dateidialog-Klicks zu öffnen, war
  fragil (letzter Button-Klick registrierte nicht zuverlässig). Robusterer Weg
  gefunden: Obsidians eigene `obsidian.json` (bekannte Vaults) direkt
  vorschreiben, dann öffnet sich der Vault nach Neustart automatisch, ganz ohne
  GUI-Klicks.
- **Der zentrale Tipp-Bug:** `page.keyboard.type()` verliert jede
  Großschreibung auf dem Weg durch Selkies (bestätigt am echten Dateiinhalt:
  "Das ist..." wurde zu "as ist..."). `page.keyboard.insert_text()` versagt
  noch grundlegender — kommt gar nicht an. Durchbruch: `docker exec <container>
  xdotool type` — komplett am Browser/Selkies vorbei, direkt in die X11-Sitzung
  des Containers — tippt Groß-/Kleinschreibung UND deutsche Umlaute korrekt
  (visuell bestätigt: "Hallo, ich bin Schörschel! Ärger? Übung macht den
  Meister: 100%." — nur "Ärger"/"Übung" verloren zunächst ihre Anfangsgroßschreibung,
  per explizitem `xdotool key shift+adiaeresis` ebenfalls gelöst).
- **Speichern-Bug aufgeklärt (war größer als vermutet, dann vollständig gelöst).**
  Nicht Fenster-Fokus beim `ctrl+s` — der eigentliche Grund: eine per `Ctrl+N`
  in Obsidian selbst frisch erzeugte Notiz bindet ihren Editor-Puffer nie an
  eine echte Datei (Text erscheint korrekt im Editor, ein `Backspace` löscht
  ihn wirklich, aber er landet nie auf Platte, egal wie lange gewartet wird).
  Fix: Dateien immer vorher direkt auf der Platte anlegen (Obsidians
  Dateisystem-Watcher erkennt sie sofort), nie über `Ctrl+N`. Nebenfund: ein
  `browser.close()` unmittelbar vor dem Tipplauf reißt den Text nach der
  Hälfte lautlos ab — Playwright-Verbindung muss während des Tippens offen
  bleiben. Fertiges, getestetes Modul: `welt/obsidian_vault_agent.py`
  (`oeffne_datei_und_schreibe(entity_id, dateiname, text, titel=...)`),
  mehrfach mit echtem deutschem Text (Umlaute, ß, Satzzeichen, Prozent)
  gegen den Pilot-Vault verifiziert.

Danach auf alle 7 Wesen skaliert und öffentlich gestellt: eigener HTTPS-Port
pro Wesen über nginx (exakt das Muster von Daniels eigenem Obsidian-Container
repliziert, doppelte Basic-Auth), nicht als Pfad unter flextrawurst.de (Selkies
ist nicht für Subpath-Mounting gebaut). Dabei die gleiche Bug-Klasse wie beim
`%i`/`%I`-Systemd-Problem erneut gefunden: `WESEN_VAULT_OBSIDIAN_PASSWORD_träumerlie`
und `..._dak+gord-system` sind als bash-Variablennamen ungültig (Umlaut/`+`),
gefixt mit ASCII-GROSS-Suffixen. Nebenbei geklärt: Daniel muss für sein eigenes
Mitschreiben gar nichts Neues einrichten — sein bereits laufendes `/werkraum`-
Obsidian-Vault enthält `wesen_vaults/` schon automatisch als Unterordner.

Vollständige Chronik: [[30_wesen_eigene_obsidian_vaults]].

---

## Was noch offen ist

- Orchestrierung klären: wie/wann wechselt der Wesen-Browser-Tab zu Obsidian —
  Daniel dazu wörtlich: *"keine ahnung so wie es am besten ist eben keine
  ahnung wird bestimmt auch sich dann zeigen bald und eh wieder geändert"* —
  bewusst offen gelassen, meine Einschätzung entscheidet vorerst
- Site-READMEs mit Navigationsanleitung pro Seite — noch nicht angefangen
- Das Flarum-Einfrieren-Verhalten (TEIL 5, Nebenbefund) — eigenes, noch nicht
  angegangenes Thema

---

*Verwandt: [[12_ollama_gemma4]] · [[28_live_update_kanal]] ·
[[29_browser_agent_aktivierung]] · [[30_wesen_eigene_obsidian_vaults]] ·
[[24_ankuendigungen]]*
