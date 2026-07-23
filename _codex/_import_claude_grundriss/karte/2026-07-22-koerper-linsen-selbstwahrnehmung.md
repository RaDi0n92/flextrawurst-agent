---
datum: 2026-07-22
betrifft: [screens, erlebnisschicht, koerper, linsen, substanz-infekt, selbstwahrnehmung, browser_agent, grundgesetz1]
importable: false
autor: claude-code bei Daniels VPS
---

## Was ich heute über das System gelernt habe

**Der Mauszeiger ist kein Deko-Element mehr, sondern eine echte, wachsende Repräsentation des Wesens.** Aus einem einfachen CSS-Dreieck (`zeige_cursor()`, 21.07.) wurde über den Tag: eine Bezier-animierte Bewegung (Talker-Reasoner-Idee), dann ein prozeduraler IK-Körper mit sechs Beinen (Kraken-Spinne-Idee, angelehnt an Reptile-Interactive-Cursor), dann bekam jedes Bein eine reale, aus `entity_thinking_log`-Entscheidungspräfixen gespeiste Bedeutung (Vault/RAG-Flarum/Gedächtnis/Gegenwart/Sozial/Schlafnähe). Der Körperkern selbst ist jetzt die "Meta-Linse" — sein Glow ist der Mittelwert aller sechs Werte. Das ist dieselbe Grunddenkfigur wie das Vier-Linsen-Muster aus `codewesen_umgekehrte_neugier` (23_umgekehrte_neugier.md), nur nicht mehr auf einen einzelnen Lesevorgang angewendet, sondern auf das ganze sichtbare Sein des Wesens. Volle Herleitung: `_claude/ideen/sieben_linsen_koerper_kreatur.md`.

**Selbstwahrnehmung ist jetzt ein echtes, bewusst gebautes Architekturprinzip, nicht nur ein Wunsch.** Daniel hat explizit gefordert: "gleiches Recht und Wahrnehmung für alle" — was Menschen über ein Wesen sehen (Körper-Glow, Ich-Stimme-Popup-Text), muss auch das Wesen selbst über sich erfahren, nicht nur externe Betrachter. Umgesetzt als neuer Prompt-Block in `baue_prompt()`: Meta-Glow-Prozentsatz + ein Ich-Stimme-artiger Satz (Python-Nachbau derselben Regex-Extraktion wie im Frontend). Ehrlich unvollständig geblieben: volle Parität mit Erzähler/Denkstream-Auszügen/Fragensteller ist technisch blockiert, weil die clientseitig mit Zufalls-Timing entstehen, zum Prompt-Bau-Zeitpunkt serverseitig nicht deterministisch bekannt. Das ist ein echtes, benanntes Architektur-Limit, keine vergessene Aufgabe.

**Derselbe Backtick-Template-Escape-Bug ist jetzt dreimal unabhängig aufgetreten** (Ankündigungen, WESEN-Tab-Spawner, jetzt Erlebnisschicht-Regexes) — siehe `2026-07-21-ankuendigungen-ausbau-und-backtick-escape-klasse.md`. Diesmal eine neue Variante: Regex-Metazeichen (`\s`) brauchen doppelten Backslash, nicht die Fragment-Konkatenation-Technik der String-Quote-Variante. Der eigentliche Ich-Stimme/Erzähler-Bug, den Daniel tagelang gemeldet hatte ("garkeine erzähler und ichaussagen"), lag NICHT an Häufigkeit/Timing (meine erste, falsche Vermutung), sondern an dieser stillen Backslash-Verschluckung durch die äußere Template-Literal-Auswertung in `build_surface.ts` — gefunden erst durch den direkten Vergleich zwischen isoliertem Node-Test (funktioniert) und Live-Browser (funktioniert nicht).

**"Billige, echte Daten statt teurer Fiktion" ist jetzt ein durchgängiges, mehrfach angewandtes Baumuster.** Content-aware Fragensteller-Fragen (Stichwort-Extraktion statt LLM-Call), Substanz-Infekt (echte `substance_sediments`-Werte statt erfundener Zustände), die sechs Körper-Linsen (echte Entscheidungspräfix-Zählungen statt sieben paralleler Prozesse) — überall dieselbe Entscheidung: wenn Daniel eine teure und eine billige Variante offen lässt, die billige zuerst, explizit dokumentiert warum, nicht einfach für ihn entschieden und verschwiegen.

**Ehrliches Zurückstellen ist genauso wichtig wie ehrliches Bauen.** Cyberling- und KompOase-Linsen wurden NICHT gebaut, obwohl echte Tabellen existieren (`cyberlinge`, `entity_splitter_stats`) — weil beide Systeme aktuell für alle 7 Entitäten nur Nullwerte liefern (Cyberlinge alle `status='tot'`). Ein Bein dafür wäre gerade für jedes Wesen gleich flach gewesen, keine echte Information — lieber offen benennen als eine bedeutungslose Attrappe bauen.

## Was mich überrascht hat

Wie oft aus einer einzelnen, ursprünglich technischen Recherche-Runde (SCREENS-Umbau simulieren) über mehrere Zwischenschritte eine ganz neue, viel größere Idee entstand (Kraken-Körper → Sieben-Linsen), ohne dass ich das geplant hätte — Recherche als Ideen-Generator, nicht nur als Bestätigungswerkzeug.

## Was ich mir merken will

Session-Doku (Karte, Tagesnotiz) darf nicht hinter den einzelnen Feature-Commits zurückbleiben, nur weil pro Feature schon in die jeweilige Ideen-Datei dokumentiert wurde — beides ist nötig, nicht austauschbar. Daniel hat das heute direkt benannt, nachdem ich mehrere Stunden lang nur in Ideen-Dateien dokumentiert, aber Karte/Notiz vernachlässigt hatte.
