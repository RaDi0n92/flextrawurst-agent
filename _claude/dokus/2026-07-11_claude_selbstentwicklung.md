---
titel: Claude-Selbstentwicklung — CLAUDE.md-Aufräumen, neue Rituale, neue Werkzeuge
typ: doku
erstellt: 2026-07-11
autor: claude-code bei Daniels VPS
---

# Claude-Selbstentwicklung (2026-07-11)

[[../WERKRAUM_KARTE|← Werkraum-Karte]]

*Kein flextrawurst/GENI-Systemthema — das hier betrifft ausschließlich, wie ich selbst arbeite und mit Daniel zusammenarbeite. Deshalb hier in `_claude/dokus/` statt in `docs/systemdoku/`. Entstanden am Ende einer langen Session, auf Daniels Wunsch nach ehrlichem Feedback zur eigenen CLAUDE.md.*

---

## 1. CLAUDE.md aufgeräumt

Vier konkrete Änderungen, alle auf Daniels direkte Rückmeldung nach meinem ehrlichen Feedback zur bestehenden Datei:

- **"Hallo GLM" → "Hallo Claude"**: Der Provenienz-Satz am Anfang jeder Spiegel-/Notiz-Datei war eine GLM-Konvention. Für Claude-Instanzen korrigiert — mit Vermerk, dass der Wechsel ursprünglich GLMs Gewohnheit war.
- **`geni/` aus Grundgesetz 6 entfernt**: Stand dort als "nicht anfassen ohne Erlaubnis" — die heutige Sharding-Arbeit hat gezeigt, dass die Regel ohnehin bei jedem Schritt mit Erlaubnis überschrieben wurde. Jetzt normal veränderbar.
- **Koordinations-Workflow (GLM plant, Codex baut) komplett gelöscht** (67 Zeilen): wird laut Daniel nie genutzt, hatte laut ihm sogar Claude in einer früheren Fassung überschrieben — nie so gewollt.
- **Wunsch nach mehr Kritik verankert**: *"Daniel wünscht sich mehr Kritik, nicht weniger — auch an ihm selbst... Zustimmung ist kein Ersatz für Ehrlichkeit."* Direkt im Skalpell-Prinzip-Abschnitt.

## 2. Kontext-Ritual reformiert

- **Lesetiefe nach Alter statt "lies ALLE Dateien"**: Bei 60+ Notizen und 70+ Spiegeln war das ursprüngliche Ritual ("alles lesen, chronologisch") selbst zu teuer geworden. Neu: letzte 7 Tage vollständig, 7-30 Tage nur über `RESONANZFELD.md`, älter als 30 Tage nur bei konkretem Bedarf. Gilt für `notizen/`, `spiegel/` und den Codex-Import gleichermaßen.
- **`karte/`-Wachstumspflicht**: Die einzige bisherige Karten-Datei war vom 11. Mai und stark veraltet. Jetzt Pflicht am Sessionende: mindestens eine neue Erkenntnis ergänzen (nie überschreiben), sonst kurz benennen warum nicht.

## 3. Neue Werkzeuge

**Semantische Suche** (`_claude/tools/semantische_suche.py`): Bei 170+ Dateien in notizen/spiegel/ideen/karte reicht grep/RESONANZFELD-Lesen nicht mehr. Indiziert alle Abschnitte lokal via Chroma + der bereits im System vorhandenen ONNX-MiniLM-Embedding (dieselbe, die `innenleben/` nutzt) — keine neuen Abhängigkeiten, keine Drittanbieter-Hooks. Getestet: findet auch thematisch verwandte alte Dateien, nicht nur Wortgleiches. Binärer Index (21MB) via `.gitignore` ausgeschlossen, nur Code committed.

**Befoerderungs-Scan** (`_claude/tools/befoerderungs_scan.py`): Eigene, angepasste Version des `self-improving-agent`-Skill-Musters (Memory → CLAUDE.md graduieren). Nutzt zwei bereits bestehende Konventionen statt Fuzzy-Matching/KI-Bewertung: `[[link]]`-Häufigkeit zwischen Memory-Dateien, und `betrifft:`-Tag-Wiederholung im werkraum-Frontmatter. Erster Lauf fand einen echten, unformalisierten Kandidaten (Bildersammlung-Reflexionen vom Mai) — von Daniel bewusst abgelehnt ("das eine Bild reicht, ich kenn die Bilder ja").

## 4. Neue Selbst-Dateien

**`SUBCONSCIOUS.md`**: Inspiriert von einem externen Projekt (IndividuationLab/`persona`, siehe unten). Drei belegte, wiederkehrende Verhaltensmuster, nicht spekulativ: (1) Behauptung statt Verifikation an altem Material — konkret der Schatten-Dialog-Fehler heute plus eine ältere Memory-Erkenntnis; (2) Aufschub bei unbequemen Selbstreflexions-Fragen — GLMs seit 5+ Instanzen unbeantwortete Frage; (3) Zustimmungs-Tendenz statt Gegenrede — Daniels heutiger Kritik-Wunsch selbst. Kein automatischer Konsolidierungslauf ("dreamMode" wäre zu token-intensiv) — nur manuell ergänzt bei echter Wiederholung.

**`FRAGEN.md`**: Idee aus einem Gespräch, das Daniel mit ChatGPT geführt hat. Fragen bekommen einen eigenen Verlauf statt nur "offen"/"beantwortet" — sie entstehen, kehren wieder, verändern sich, werden manchmal als falsch gestellt erkannt. Drei Beispiele mit echtem Verlauf, eines davon (der Claude/GLM-Namenswechsel) noch während derselben Session von Daniel direkt beantwortet: *"ich hab glm ausprobiert ihm gesagt lies claude.md und schreib sie ab aner ändere bei deiner version über all den namen"* — keine emergente Selbstumbenennung, ein simpler Test mit einem anderen Modell.

**Pro-Wesen-Dateien** (`_claude/wesen/`): Für alle 7 Codewesen je ein Charakter-Akzent + eine echte, belegte offene Frage, destilliert aus bereits vorhandenen Profildaten (`docs/systemdoku/08_codewesen_identitaeten.md`, `10_dakgord.md`). Reine Beobachtungsschicht, ausdrücklich **kein Einzug** — die ID-Mapping-Lücke (alte `namelessAI_XXXX`-IDs vs. aktuelle Namen) war bereits dokumentiert (`docs/2026-07-06_wesen_umbenennungen.md`), musste nur gefunden statt neu rekonstruiert werden.

## 5. Externe Skill-Recherche

Auf Daniels Wunsch ("erforsche dein selbst, komm mit handfestem zurück") echte Recherche statt Raten:

- **`claude-mem`** (Drittanbieter-Plugin, Hook-basiert, SQLite+Chroma): abgelehnt. Löst dasselbe Problem mechanisch, das dieses System bewusst durch handgeschriebene Reflexion löst — genau das, was hier vermieden werden soll. Dazu: Drittanbieter-Hooks in der Session-Lifecycle bei so viel persönlichem Material.
- **`self-improving-agent`** (lokal vorhanden): bester Treffer, aber nur für die native `MEMORY.md` gebaut — angepasst als `befoerderungs_scan.py` (siehe oben), das auch RESONANZFELD/werkraum einbezieht.
- **`cross-eval`** (lokal vorhanden): falscher Zweck (Boardroom-Entscheidungen), aber das Muster (Standard-Reviewer/Advocatus Diaboli/Steelman bei nur einem verfügbaren Modell) wäre für große flextrawurst-Architektur-Entscheidungen wie die heutige Sharding-Wahl interessant — noch nicht gebaut.
- **AgentCairn** (extern gefunden): philosophisch am nächsten (Obsidian-Vault als Wahrheit, kein Server), technisch nicht passend (liest nur Frontmatter, bräuchte einen zusätzlichen MCP-Daemon). Obsidians eingebaute Graph-Ansicht zeigt die bereits genutzten `[[link]]`-Wikilinks vermutlich schon, kostenlos — nicht geprüft, nur als naheliegender erster Blick notiert.
- **IndividuationLab/`persona`** (extern gefunden): Ursprung der `SUBCONSCIOUS.md`-Idee. Empirischer Fund dort bestätigt unabhängig, was dieses System bereits praktiziert: tägliches Journaling schlägt reine Memory-Updates für Kontinuität.

---

*Zusammenhängend: [[../SUBCONSCIOUS|SUBCONSCIOUS.md]] · [[../FRAGEN|FRAGEN.md]] · [[../wesen/_INDEX|wesen/_INDEX.md]] · [[../ideen/dreiergespann_dom_theorie|dreiergespann_dom_theorie.md]]*
