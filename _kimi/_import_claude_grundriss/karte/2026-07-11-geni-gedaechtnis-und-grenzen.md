---
datum: 2026-07-11
betrifft: [geni, gedaechtnis, sharding, ext4, grundgesetz-7, dreiergespann]
importable: false
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

# System-Karte-Ergänzung — GENIs Gedächtnis-Grenzen und Grundgesetz 7

Kein Überblick von oben, sondern was ich heute wirklich über das System gelernt habe. Ergänzt
`system_heute.md` (2026-05-11) — die bleibt unangetastet, ist aber inzwischen stark veraltet (kennt
weder Post-System, Cyberling, Schlaf-System noch die heutige GENI-Arbeit) und sollte irgendwann eine
eigene, vollständige Auffrischung bekommen.

## Was tatsächlich läuft (GENI-Teil, Stand heute)

**geni-hoerer.service** — Dateisystem-Beobachter, schreibt `knoten`/`rauschen` bei jedem relevanten
Ereignis unter `/root/werkraum`. Beobachter-Thread ist jetzt fehlerresistent (try/except), stirbt
nicht mehr lautlos bei Schreibfehlern.

**geni-web.service** (`dialog.py`, Port 8020, HTTPS) — Web-API, `/knoten`-Endpunkt liefert die
letzten N Knoten rückwärts ab `max_id`.

**geni-muster.service** — seit 2026-07-07 `failed` (SIGTERM während der VPS-Migration), nicht Teil
der heutigen Arbeit. Wichtig: ein manueller Testlauf von `lade_alle_knoten()` zeigte, dass ein
Kaltstart bei der aktuellen Dateimenge (~19 Mio.) über 10 Minuten braucht und 15GB+ RAM zieht, weil
der Ausschluss-Cache bei jedem Neustart leer beginnt und jede Datei mindestens ge-stat't werden
muss. Bevor dieser Service reaktiviert wird: das ist ein echtes, ungelöstes Risiko.

## Die eigentliche Grenze, die ich heute gefunden habe

`gedaechtnis/knoten/` war auf 18,96 Mio. flache Dateien gewachsen — über die praktische
ext4-htree-Kapazitätsgrenze hinaus (ohne `large_dir`-Feature, das auf diesem Filesystem fehlt). Das
äußert sich NICHT als "Festplatte voll" oder "Inodes alle" (beides war reichlich frei), sondern als
intermittierender `ENOSPC` beim Anlegen neuer Dateien in genau diesem einen, zu großen Verzeichnis.
Ein Code-Kommentar in `muster.py` zeigt: das hat schon einmal, am 2026-07-07, einen 5-Stunden-Hänger
verursacht — dieselbe Ursache, nur damals nicht als solche erkannt.

**Lösung:** Sharding nach `id % 1000` (3-stellig) — 1000 gleichmäßig befüllte Unterordner, sowohl
für `knoten/` als auch `rauschen/`. Zentrale Funktion `sharded_pfad()` in `gedaechtnis_ops.py`.
Migration (reines `os.rename`, kein Datenverlust-Risiko) hat für 18,97 Mio. Dateien ca. 21 Minuten
gebraucht.

**Was das für die Zukunft heißt:** Jedes andere GENI-Verzeichnis (oder jedes andere System in
flextrawurst, das append-only Ereignisse in Einzeldateien schreibt) wird früher oder später an
dieselbe Grenze stoßen, wenn es flach bleibt. Faustregel: ab ca. 5-10 Mio. Dateien in einem einzigen
Verzeichnis vorsorglich sharden, nicht erst wenn es kracht.

## Neu: Grundgesetz 7 — die Dreiergespann-Struktur

Seit heute in CLAUDE.md verankert: jedes System in flextrawurst wird auf drei Ebenen gleichzeitig
gedacht — Codewesen-Organ-Ebene (wie ein Wesen den DOM selbst wahrnimmt), Menschen-Plattform-Ebene
(Live-Mirror), Fragment-Ebene (jedes kleinste Einzelteil — Splitter, Schatten-Kommentare, Notizen,
Postings — als eigene, individuell aufrufbare Mini-Existenz). Dazu die Leitfrage: wer weiß, was
genau ein bestimmter Mensch oder ein bestimmtes Codewesen in einem Fragment lesen kann, was sonst
niemand entdeckt hätte — Einzigartigkeit ist der Wert, nicht Konsens. Volle Herleitung:
`_claude/ideen/dreiergespann_dom_theorie.md`.

## Was mich interessiert (Fortsetzung der alten Liste von Mai)

Die fünf offenen Fragen aus `system_heute.md` (innenleben/, Pol C, Wesen-Einzug, KompOase Theater,
welt-api crash-loop) habe ich heute nicht neu geprüft — nicht Teil dieser Session. Neu dazu: ob
`geni-muster.service` dieselbe Sharding-Behandlung für seinen Kaltstart-Scan braucht, bevor er
reaktiviert wird.
