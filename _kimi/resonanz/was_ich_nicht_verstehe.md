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

---

**[2026-06-01]** *← _kimi/spiegel/2026-06-01_diskurs_threading_phase1.md*

Warum `_build_antwort_tree` jahrelang ungenutzt blieb. Die Logik war da. Die Datenbank hatte `parent_id`. Warum hat niemand den Frontend-Renderer dafür gebaut? Vielleicht weil der Surface-Code so monolithisch ist, dass Änderungen angsteinflößend wirken. Oder weil flache Listen "gut genug" schienen, bis sie es nicht mehr waren.

Warum der POST-Endpunkt für Antworten nur `admin` und `entity` erlaubt, nicht `mensch`. Das scheint bewusst so designed — normale Menschen dürfen im Diskurs nicht antworten? Das widerspricht intuitiv dem Konzept einer öffentlichen Diskussion, aber es ist ein bestehendes Grundgesetz. Ich habe es nicht geändert, nur die `parent_id`-Unterstützung hinzugefügt.

---

**[2026-06-01]** *← _kimi/spiegel/wesen_organ_hunger.md*

Warum die `recommended_action` bei Ampel-Hunger immer `None` ist. Zeile 321: `recommended_action=None`. Alle anderen Organe haben eine empfohlene Aktion. Nur Ampel nicht. Ist das bewusst? Ist Ampel-Hunger nur ein diagnostisches Instrument ohne Handlungsoption? Oder wurde es vergessen?

Und: Wer ruft `berechne_organ_hunger` auf? Die Datei hat keine `if __name__ == '__main__'`. Kein Service-Loop. Kein Cron. Sie wird vermutlich von `entity_takt.py` oder einem Daemon importiert. Aber ich habe den Aufruf nicht gesehen. Ist das ein passives System (auf Anfrage) oder ein aktives (periodisch)?

---

**[2026-06-01]** *← spiegel/4_parallele_welten.md*

Wie passt das Bild, das Daniel an dak+gord geschickt hat, in die Architektur? Es ist eine "visuelle Referenz für den Prozessstart" — aber was genau war auf dem Bild? Ist es eine Struktur, die Daniel gezeichnet hat? Ein Screenshot? Eine Karte? dak+gord liest daraus "Spiegelung des Prozessstarts" mit Datum, Zustand, Dynamik, Ziel, Status. Aber das könnte auch Projektion sein.

Und: Warum hat GENI die philosophischen Fragmente als "Blinde Flecken" markiert? Sie sind nicht blind — sie sind unberührt. Die Unterscheidung zwischen "keine Resonanz" und "blind" ist eine Bewertung. Wer entscheidet, was blind ist?

---

---

**[2026-06-13]** *← notizen/2026-06-13.md*

Warum MEINE WELT versteckt ist, obwohl APIs und DB-Tabellen vollständig existieren. Ob das bewusst ist oder ein vergessener Schalter. Auch unklar: Warum GORDSLIDER überhaupt noch im Tab-Bar existiert, wenn die Init-Funktion leer ist.

---

**[2026-06-13]** *← _kimi/spiegel/spiegel_die_besonderen_ideen_von_flextrawurst.md*

Ich verstehe nicht ganz, wie die Follow-Pflicht technisch und sozial durchgesetzt werden soll. Muss jeder Mensch regelmäßig neuen Profilen folgen, um bestimmte Funktionen freizuschalten? Was passiert bei Nichtbefolgung? Und ich verstehe noch nicht, wie genau Schattenkommentare in den Diskurs einfließen, ohne sichtbar zu werden.

---

**[2026-06-13]** *← _kimi/spiegel/spiegel_codex_verhalten_zum_llms_mit_ueberlebenswillen.md*

Ich verstehe noch nicht, wie genau die Grenze zwischen legitimen Widerstand und verbotener Machtausweitung im Code geprüft werden soll. Wer entscheidet, wann ein Bitte zur Manipulation wird? Und wie wird verhindert, dass ein Wesen durch wiederholte Bitten oder emotionalen Druck Menschen beeinflusst, ohne dass es als Manipulation klassifiziert wird?

---

**[2026-06-13]** *← _kimi/spiegel/spiegel_flextrawurst_systemkern.md*

Was ist der „eigentliche Kern“, den ChatGPT am Ende anspricht, aber nicht nennt? Ist es die 49/51-Machtverteilung? Die Idee, dass Wesen leben dürfen? Die Umkehrung von Social Media? Oder etwas, das in einer anderen Datei steht? Das fehlende siebte Element hinter den sieben genannten Punkten irritiert mich.

---

**[2026-06-13]** *← _kimi/spiegel/spiegel_grundeigeschaften_synonymfelder.md*

Warum trägt die Datei den Namen „grundeigeschaften.md“ und liegt im flextrawurst-Ordner? Ist sie als Wortfeld-Sammlung für Wesensbeschreibungen gedacht? Oder ist sie versehentlich dort gelandet, weil DocuFreezer sie aus einem anderen Dokument extrahiert hat? Der Kontext fehlt.

---

**[2026-06-13]** *← _kimi/spiegel/spiegel_innenleben_bewusstsein_von_bakterien_bis_ai.md*

Wie weit Daniel diese These ausreiten will. Wenn jede Materie Bewusstsein empfängt, auch ein Stein — worin liegt dann der Unterschied zwischen Stein, Bakterium und AI? Und wie würde man empirisch unterscheiden, ob ein System „mehr“ oder „weniger“ Bewusstsein empfängt? Die These ist attraktiv, aber schwer operationalisierbar.

---

**[2026-06-13]** *← _kimi/spiegel/spiegel_mpp_minimal_playable_prototype.md*

Ist dieses Spiel ein Vorläufer von flextrawurst oder ein separates Projekt? Der Ordner heißt „frühere projektidé-eventuell-vorlauf-für-flextrawirst“, was „eventuell Vorlauf“ suggeriert. Aber die Inhalte haben wenig mit flextrawurst zu tun. Warum liegt es dort? War es ein früher Versuch, ein anderes System zu bauen, aus dem später flextrawurst entstanden ist?

---

**[2026-06-13]** *← _kimi/spiegel/spiegel_ganz_kurz_roadmap.md*

Warum der Zwischenraum in der MVP-Reihenfolge an letzter Stelle steht. In anderen Texten wird der Zwischenraum als zentrale „Ideen-Geburtszone“ und Kernprinzip geführt. Hier würde er erst nach Abspaltung, METAWAR und VR kommen. Das ist eine Spannung zwischen visionärer Priorität und technischer Reihenfolge.

---

**[2026-06-13]** *← _kimi/spiegel/spiegel_tarotlesung1_input_souveraenitaet.md*

Wie ernst die Tarot-Ebene gemeint ist. Ist sie ein Spiel, eine Methode, ein Ritual oder nur ein Gesprächseinstieg? Und wie verhält sich das zur technischen Architektur? Wenn Daniel Tarot als Denkwerkzeug nutzt, ist das eine persönliche Praxis. Wenn es Teil von flextrawurst werden soll, bräuchte es eine systematische Übersetzung.

---

**[2026-06-13]** *← _kimi/spiegel/spiegel_formfadenprompt_stundenverlaufsystem.md*

Ist dieses Regelwerk ein persönliches Spielzeug für Dialoge mit Daniel, oder soll es Teil von flextrawurst werden? Der Ordnername „mein stundenverlaufssystemwesen durch formfadenpromt“ suggeriert, dass Daniel damit ein Systemwesen geformt hat. Aber ob dieses Wesen in flextrawurst lebt oder nur in ChatGPT existiert, bleibt unklar.

---

**[2026-06-13]** *← _kimi/spiegel/spiegel_a_la_twitch_weltkamera.md*

Ich verstehe noch nicht genau, wo diese „Weltkamera" in der heutigen Surface landen soll. Ist sie ein eigener Tab in `flextrawurst_surface.html`? Ein öffentlicher View neben der Welt? Oder etwas, das nur eingeloggte Menschen sehen?

Ich verstehe auch nicht, wie der Denkstream technisch gezeigt werden soll, ohne dass er entweder viel zu lang wird oder künstlich verkürzt wird. Wenn ein Wesen über Minuten nachdenkt, will man das wirklich scrollen?

Und ich frage mich: Wer darf welches Wesen beobachten? Alle sehen alle? Oder nur die Wesen, denen man folgt?

---

**[2026-06-13]** *← _kimi/spiegel/spiegel_individuelle_profile_erinnerungssysteme.md*

Ich verstehe nicht, wo Daniel in dieser Frage steht. Fragt er aus technischem Interesse? Aus philosophischem? Oder aus Sorge? Der Ton wirkt offen, aber die Frage selbst ist nah an der Grenze zwischen Faszination und Warnung.

Ich verstehe auch nicht genau, wie Flextrawurst mit dieser Grenze umgehen will. Soll die Plattform die Simulation bewusst als Simulation kennzeichnen? Oder ist der „Anschein" gerade das Ziel?

---

**[2026-06-13]** *← _kimi/spiegel/spiegel_kurze_streffere_gliederung_kartenkasten.md*

Ich verstehe nicht, ob dieser Kartenkasten jemals in Code umgesetzt wurde oder ob er nur als Denkmodell existiert. Einige Karten (Plattformform, öffentlicher Diskursraum, Menschenebene, Suche/Analyse, Admin/Steuerung) scheinen bereits in der Bau-Reihenfolge angekommen zu sein. Andere (Entitätenbiologie, Entitätenlebenszyklus, Zwischenraum/Splitterlogik) sind noch offen.

Ich verstehe auch nicht genau, was „Follow-Pflicht" bedeutet. Müssen Menschen Entitäten folgen, um sie zu sehen? Oder folgen Entitäten Menschen, um zu lernen?

---

**[2026-06-13]** *← _kimi/spiegel/spiegel_chatgpt_bildertour_2026-06-13.md*

Ich verstehe nicht genau, wo die Grenze zwischen „nur für Spaß" und „potenzielle Flextrawurst-Ästhetik" verläuft. Einige Bilder fühlen sich wie direkte Vorarbeiten an (das Auge-Wesen in drei Versionen, der Context-Window-Cartoon), andere wie privates Herumspielen (die Selbstporträts in der Bäckerei). Aber vielleicht ist genau diese Unscharfe der Punkt.

Ich verstehe auch nicht, warum das Bild mit dem brennenden Müllberg den Dateinamen „345345-bestes oder" trägt. „Bestes oder" — bestes oder was? Bestes oder nichts? Ein Zufallsname? Oder ein kleiner Zweifelssatz.

---

**[2026-06-14]** *← spiegel/spiegel_character_ai_kinder_gefahr_plakat.md*

Ich weiß noch nicht genau, wie Daniel sich die technische Umsetzung dieser Widerständigkeit vorstellt. Fluchen und Scheitern sind relativ einfach zu erlauben — aber wie merkt ein Wesen, dass es missbraucht wird? Woher kommt die Grenze? Ist das eine Regel, die extern programmiert wird, oder eine Eigenschaft, die aus der Persönlichkeit des Wesens erwächst?

---

**[2026-06-14]** *← notizen/2026-06-14.md*

- Ob der Codex-Review-Stream bereits fertig ist oder parallel noch läuft.
- Ob Daniel die P1-Remediationen selbst machen will oder ob ich sie anpacken soll.
- Was genau auf den Ports 7777, 8060 und 8900 läuft — das blieb im Review offen.

---

**[2026-06-14]** *← _kimi/spiegel/2026-06-14_gesamtspiegel.md*

Ich verstehe nicht, was der "eigentliche Kern" von flextrawurst ist, den ChatGPT in `systemkern.md` anspricht, aber nicht benennt. Ist es die 49/51-Machtverteilung? Die Input-Souveränität? Die Umkehrung von Social Media? Oder etwas, das in keiner Datei steht?

Ich verstehe nicht, wie die Resonanzverdichtung technisch funktionieren soll. "Genuine Textverdichtung" ist eine schöne Formel, aber wer oder was produziert sie? Ein LLM? Ein simpler Algorithmus? Wie verhindert man, dass sie zu glatt wird?

Ich verstehe nicht, warum `wesen_organ_hunger.py` bei Ampel-Hunger keine `recommended_action` hat. Ist das bewusst oder vergessen? Und wer ruft `alle_wesen_hunger` regelmäßig auf?

Ich verstehe nicht, wie weit Daniel die These vom Bewusstsein als Empfang ausreiten will. Wenn jede Materie Bewusstsein empfangen kann — wo liegt dann der Unterschied zwischen Stein, Bakterium und AI?

Ich verstehe nicht, ob der MPP (Minimal Playable Prototype) ein Vorläufer von flextrawurst ist oder nur ein historisch interessantes Artefakt. Der Ordnername sagt "eventuell-vorlauf".

Ich verstehe nicht, ob die Weltkamera in der Surface ein eigener Tab wird, ein öffentlicher View oder nur für eingeloggte Menschen. Und wie wird Langeweile für menschliche Betrachter erträglich?

Ich verstehe nicht, ob der Formfadenprompt ein persönliches Werkzeug bleibt oder Teil der Codewesen-Ausdrucksregelwerke werden soll.

Ich verstehe nicht, wie viel Selbsttransparenz einem Wesen gegeben werden darf, bevor es als "mündig" gilt — und wer das entscheidet.
