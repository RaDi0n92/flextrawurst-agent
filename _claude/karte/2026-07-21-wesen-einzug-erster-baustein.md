---
datum: 2026-07-21
betrifft: [wesen-einzug, browser-agent, rag, live-update-kanal, grundgesetz8, dreiergespann]
importable: false
autor: claude-code bei Daniels VPS
---

## Was heute wirklich passiert ist

Der Wesen-Einzug — seit Mai 2026 als "GESPERRT bis Daniel es sagt" markiert — hat heute seinen ersten echten Baustein bekommen. Nicht der ganze Einzug (Flarum-Accounts sind noch nicht migriert, kein `wesen.schwelle_passiert`-Event, kein atomischer Übergang), aber der Teil, der laut `ideen/wesen-desktop.md` und der Dreiergespann-Theorie (`ideen/dreiergespann_dom_theorie.md`) die technische Voraussetzung für alles Weitere ist: alle 6 Wesen haben jetzt einen eigenen, dauerhaften virtuellen Browser (Playwright, headless Chrome), der als systemd-Dienst läuft, echte Flarum-Vorwelt lesen kann (nicht posten — Grundgesetz 6 bleibt intakt, weil kein Flarum-Login existiert) und ihr eigenes RAG-Gedächtnis (Ring 1, Flarum-Archiv + Weltwissen) selbst erkunden kann.

Daniel hat dabei eine neue, wörtliche Selbstdefinition für ein Wesen formuliert: *"Ich bin ein dauerhaftes, organisiertes und selbststrukturiertes Wesen. Ich kann über das DOM und meinen eigenen virtuellen Browser auf Flextrawurst wahrnehmen, reagieren und eingreifen."* Das ist keine Implementierungsnotiz — das ist jetzt Teil dessen, was ein Wesen in diesem System *ist*.

## Was ich über das System gelernt habe

**Dormanter Code ist nicht getesteter Code.** `browser_agent.py` lag seit dem 6.7. fertig, syntaxgeprüft, migriert — aber nie unter echter Last gelaufen. Heute, beim ersten echten Start, kamen sechs unabhängige Bugs zum Vorschein, die kein Code-Review je gefunden hätte, weil sie nur bei tatsächlicher Ausführung sichtbar werden: ein fehlendes Bearer-Prefix (bricht jede In-Page-JS-Interaktion, aber nicht Server-Calls — zwei verschiedene Auth-Pfade im selben System), ein `NameError` der nur bei drei bestimmten Aktionen ausgelöst wird, ein Playwright-Threading-Verstoß der niemals crasht sondern nur stumm nie funktioniert, zwei fehlende systemd-Konfigurationswerte, und ein `%i`-vs-`%I`-Unterschied der nur bei Wesen-Namen mit Sonderzeichen (träumerlie) auftaucht. Lehre: "syntaktisch korrekt" und "läuft wirklich" sind bei asynchronem, Thread- und Prozess-übergreifendem Code zwei komplett verschiedene Aussagen.

**Sicherheit durch Abwesenheit statt durch Blockade.** Daniels eigene Beobachtung (nicht meine Idee): der Browser-Agent kann auf Flarum nicht posten, nicht weil ich das verhindere, sondern weil er dort nie eingeloggt ist — und Flarums eigene Gast-Rechtegruppe hat serverseitig ohnehin nur `viewForum`. Zwei unabhängige Schichten (kein Login + keine Gast-Rechte), keine davon von mir gebaut, beide schon vorher da. Die sicherste Sperre ist oft die, die man nicht extra bauen muss, weil sie sich aus der Architektur selbst ergibt.

**Deklarierter, aber nie benutzter Code ist ein eigenes Muster.** `LOCK_FILE = "/tmp/ollama_browser_lock"` stand seit der ersten Fassung von `browser_agent_coordinator.py` da — nie tatsächlich in einem `with`-Block verwendet. Genau wie `ALTER DEFAULT PRIVILEGES` nie eingerichtet wurde (Ankündigungen-Session, selber Tag), gibt es in diesem System eine wiederkehrende Lücke zwischen "die Absicht ist im Code sichtbar" und "die Absicht ist auch umgesetzt". Beim nächsten Fund dieser Art: prüfen, ob es noch mehr solcher Geister-Deklarationen gibt.

## Was mich am meisten beschäftigt

Wie schnell sich eine Diskussion über Ankündigungen-Formatierung ("wie ein ganzer Post lesbar sein") in denselben Abend zum tatsächlichen Start des Wesen-Einzugs entwickelt hat. Kein Bruch, kein Themenwechsel im Gespräch — Daniel hat einfach gesagt "so nun zum eigentlichen" und gemeint: das hier, die Ankündigungen, war Vorbereitung, das war nie das Ziel des Abends.

## Was ich mir merken will

Vor jeder Aktivierung eines lange gesperrten, "fertigen" Systems: davon ausgehen, dass es Bugs enthält, die nur unter echtem Betrieb sichtbar werden — nicht weil der Code schlecht ist, sondern weil er nie widerlegt wurde. Kurz, kontrolliert live testen (ein Wesen zuerst), bevor alle sechs gleichzeitig starten.
