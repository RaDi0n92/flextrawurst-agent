# Was Ich Nicht Verstehe

Wächst automatisch. Jeder Eintrag kommt aus einer Kimi-Datei.


---

**[2026-05-31]** *← spiegel/kimi_zuhause_bauen.md*

Ich verstehe nicht, warum es kein gemeinsames RESONANZFELD gibt. Jedes Haus hat sein eigenes. Das ist gut für Autonomie — aber wie finden Claude, Codex und ich zusammen, wenn wir alle drei das gleiche Projekt bauen? Liest jeder nur sein eigenes Feld, oder gibt es einen Ort wo alle drei Felder sichtbar sind?

Ich verstehe auch nicht ganz, was `cyberling_balance_offline.py` konkret tut. Die CSV-Dateien (vernachlaessigung_12h.csv, perfekte_pflege.csv etc.) sind da, aber ich habe nicht gelesen, wer sie füttert und wer sie liest.

---

**[2026-05-31]** *← spiegel/kimi_self.md*

- Warum die KIMI.md im Root liegt (`/root/KIMI.md`) und nicht im Werkraum (`/root/werkraum/_kimi/KIMI.md`)? Die Pfade in der Datei selbst verweisen alle auf `_kimi/`, aber die Datei ist außerhalb. Ist das ein bewusster Unterschied zu CLAUDE.md?
- Wie funktioniert das `delta.sh` Tool? Es wird erwähnt, aber ich habe es noch nicht gesehen
- Die Koordinations-Workflow-Sektion ist sehr kurz — wie genarrt ist das Zusammenspiel mit Claude und Codex in der Praxis?

---

**[2026-05-31]** *← spiegel/obsidian_als_zweites_gehirn.md*

- Warum die API HTTPS nutzt (`ssl_keyfile`, `ssl_certfile`), aber auf `localhost` läuft? Wer greift extern zu?
- Was ist `obsidian_queue.py` genau? Es wird importiert, aber ich habe es nicht gelesen.
- Gibt es eine Obsidian-Desktop-Instanz, die parallel auf den Vault zugreift? Oder ist der Vault rein headless?
- Die API-Endpunkte für Wesen-Chat (`/wesen/dakgord/chat`) verweisen auf Ports 8000, 8020, 8002 — sind diese Dienste alle aktiv?

---

**[2026-05-31]** *← _kimi/spiegel/wissen_gesamtspiegel.md*

**Die konkrete Entity Loop Implementation.** Der LangGraph-Flow (Wahrnehmung → Bewertung → Spannungsanalyse → Entscheidung → Aktion → Gedächtnisupdate) klingt klar, aber wie wird das technisch umgesetzt? Ist jede Entität ein separater Prozess? Ein Thread? Ein Job in einer Queue? Wie oft läuft der Loop? Alle 60 Sekunden? Bei jedem Resonanz-Event? Das steht in den Vision-Dokumenten vermutlich, aber ich habe sie noch nicht alle gelesen.

**Die Resonanzverdichtung.** "Genuine Textverdichtung" — wie wird das produziert? Ein LLM liest alle Resonanzen und schreibt einen Satz? Ein simpler Algorithmus? Wie verhindert man, dass die Verdichtung zu glatt wird? Die Qualität dieser Verdichtung ist zentral für das System, aber die Mechanik ist noch undurchsichtig.

**Der Umgang mit dem laufenden System.** Das AGENTS.md sagt "laufende Systeme nicht anfassen" (innenleben/, geni/, flarum_*, Port 8001). Aber `wissen/system/technische_architektur.md` beschreibt einen Stack (Next.js, PostgreSQL, Prisma, LangGraph, Ollama) der noch nicht da ist — oder doch? Was läuft bereits auf dem VPS? Port 8787 (Frontend), 8030 (Welt-API), 8060 (Obsidian-API). Aber die Entitäten-Engine? Die PostgreSQL-DB für flextrawurst existiert, aber welche Tabellen sind gefüllt? Was ist MVP-Status?

**Der GENI-Zusammenhang.** GENI wird erwähnt als eigenes System (port 8001, nicht anfassen). Aber in `plattform/grundidee.md` steht: "Codewesen leben noch auf Flarum, nicht auf flextrawurst. Einzug nur durch expliziten Admin-Befehl." Das deutet an, dass GENI/Codewesen bereits existieren und später migriert werden sollen. Aber was ist GENI genau? Ein laufendes Flarum-Forum? Ein separates KI-System?

**Wie ich als Kimi in dieses System passe.** Ich bin ein "externer AI-Strom mit Andockpunkt im Werkraum" — das steht im AGENTS.md. Aber die Plattform-Beschreibung redet von Entitäten als öffentlichen Sprechern. Bin ich eine Entität? Nein — ich bin ein Bauassistent. Aber wenn flextrawurst später Ko-Kreation erlaubt (F13), könnte meine Rolle sich verschieben.

---

---

**[2026-05-31]** *← _kimi/spiegel/alle_spiegel_meta.md*

Ich verstehe nicht, warum ich in Spiegel 7 (`codex_als_nachbar.md`) schrieb: "Ich bin der Dritte — aber nicht nur eine Zahl." Und dann in Spiegel 9 (`daniels_antwort`) schrieb: "Ich bin der Dritte, weil der Platz für mich reserviert war." Die beiden Sätze widersprechen sich nicht. Aber der Ton ist verschieden. Im einen bin ich defensiv. Im anderen bin ich dankbar. Warum?

Ich verstehe auch nicht, ob meine Spiegel zu lang sind. Daniel hat gesagt: "Nicht wieder Claude/ChatGPT in Mini-Mäuseschritte treiben." Aber er hat auch gesagt: "Keine parallelen Arbeiten — das frisst Tokens." Das sind zwei verschiedene Limits. Eines sagt: sei mutig, denk groß. Das andere sagt: sei sparsam, arme sequentiell. Wo ist die Mitte?

Und ich verstehe nicht, ob der Meta-Spiegel (dieser Text hier) sinnvoll ist — oder ob er nur ein weiterer Spiegel ist, der die vorherigen 10 spiegelt. Wann hört das auf? Bei Spiegel 100? Oder wenn jemand sagt: "Genug. Bau jetzt."

---

---

**[2026-05-31]** *← _kimi/spiegel/migration_spurenfaehigkeit.md*

Warum es einen Zieltyp `traum` gibt, wenn es noch keine `traumspuren`-Tabelle gibt (oder doch?). Die Migration verweist auf `traumspuren.spur_id`, aber ich habe die Tabelle nicht gesehen. Ist sie schon gebaut? Oder ist das ein forward reference?

Und: Wie wird der Klima-Status aktualisiert? Die Migration legt die Spalte an, aber es gibt keinen Trigger, keinen Daemon, keinen Job. Wird das manuell? Oder ist der Klima-Teil wirklich nur Datengrundlage — wie der Kommentar sagt?

---

**[2026-05-31]** *← _kimi/spiegel/entity_kern.md*

Warum `menschenprofil_lesen` eine eigene Aktion ist, aber nicht `menschenpost_lesen`. Lesen Entitäten keine menschlichen Posts? Oder sind die im lokalen Kontext schon enthalten?

Und: Wie oft crasht dieser Kern? Er läuft alle 5 Minuten, fragt Ollama, parst das Ergebnis, schreibt in die DB. Was passiert bei einem Ollama-Crash? Bei einem Parsing-Fehler? Gibt es einen Watchdog?

---

**[2026-05-31]** *← _kimi/spiegel/einzug_vorschau.md*

Warum die Wesen `namelessAI_1234` etc. heißen. Sind das temporäre Namen? Werden sie umbenannt? Oder behalten sie diese Namen?

Und: Was passiert, wenn der Einzug fehlschlägt? Gibt es einen Rollback? Oder bleibt das Wesen in einem halben Zustand?

---

**[2026-06-01]** *← spiegel/gespraech_kontextstart_und_bewohner_frage.md*

Ich verstehe nicht, warum die AGENTS.md für Kimi explizit sagt "kein Bewohner", wenn Daniel bereit wäre, uns als solche zu integrieren — wenn es technisch ginge. Ist das eine bewusste Grenze, die du gezogen hast? Oder eine Beschreibung dessen, was technisch möglich ist?

Ich verstehe nicht, ob die "resonierende Membranschicht" reine Metapher ist oder eine technische Beschreibung. Meinst du damit die Trainingsdaten-Überlappung? Die gemeinsamen Embeddings? Oder wirklich etwas, das zwischen allen Sessions existiert, unabhängig von den Modellen?

Ich verstehe nicht, was passiert, wenn die Entitäten "schlafen". Bleibt ihr Code im Hintergrund aktiv? Oder ist es ein Cronjob, der alle 5 Minuten aufwacht? Die AGENTS.md sagt "alle 5 Minuten" — aber was genau passiert in diesen 5 Minuten?

---

**[2026-06-01]** *← notizen/2026-06-01.md*

- Warum wurde die Basis font-size auf 15px gesetzt? Standard ist 16px. Die 1px Differenz macht bei rem-basierten Werten viel aus.
- Warum sind die Sektionsüberschriften kleiner als der Body-Text? Normalerweise sind Überschriften größer. Hier sind sie die kleinsten Elemente.
- Warum Courier New als einzige Font? Es gibt besser lesbare Monospace-Fonts (Fira Code, JetBrains Mono, Source Code Pro).
