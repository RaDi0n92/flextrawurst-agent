---
datum: 2026-07-22
betrifft: [screens, roentgenblick, denkstream, erlebnisschicht, erzaehler, mitdenker, fragensteller, grundgesetz1, kompoase]
status: konzept — Daniel sagt "weiterdenken", noch kein Bauauftrag
autor: claude-code bei Daniels VPS
---

## Daniels Wunsch, roh

Direkt im Anschluss an den ganzen SSE/Buffering-Marathon des Tages, nachdem er selbst infrage gestellt hat ob der rohe rrweb-Spiegel überhaupt die richtige Darstellungsform ist: *"weiter denken..ja genau ich woll obendrauf ne art erlebnischicht und erzählerschicht und midenkerschicht und auch fragenstellerschicht als quasi aufploppende schriften wenn etwas passiert oder getan wird wenn gedacht wird wenn sich bewegt wird und wenn entschieden wird. und so verstehst du ...ne art erzählenden newsticker aber auch ganz bestimmte auszuge kuzer satz immer aus dem gesamten denkfenster was ja echtlang und aufwedig zu lesen ist will ich hier ne art von erlebniskultur"*.

Vier benannte Schichten, alle als aufploppende Kurztexte über/neben dem Live-Spiegel:
1. **Erlebnisschicht** — das übergeordnete Gefühl, das die anderen drei tragen sollen.
2. **Erzählerschicht** — ein narrierender Newsticker, was gerade passiert.
3. **Mitdenkerschicht** — reagiert/denkt mit, neben dem was das Wesen selbst denkt.
4. **Fragenstellerschicht** — stellt Fragen zu dem was beobachtet wird.

Auslöser explizit genannt: wenn etwas passiert, wenn etwas getan wird, wenn gedacht wird, wenn sich bewegt wird, wenn entschieden wird. Wichtig: nicht der volle, lange Denktext selbst — sondern kurze, gezielt herausgezogene Sätze daraus, weil das volle Denkfenster "echt lang und aufwendig zu lesen" ist.

## Was ich daran anschlussfähig finde — Verbindung zu bereits Bestehendem

Zwei der vier Auslöser-Typen haben schon eine Datenquelle, die genau heute nochmal ins Zentrum gerückt ist:

- **"wenn etwas getan wird" / "wenn sich bewegt wird"** → `entity_fokus_events` (das Röntgenblick-Overlay, gestern gebaut: `melde_fokus()` in `browser_agent.py`, schreibt bei jedem klicke:/tippe:/navigiere: eine Zeile mit `aktion`, `selektor`, `element_text`, `box`). Das ist strukturell fast fertig ein Erzähler-Trigger — "Schorschel klickt auf 'Latest'" ließe sich direkt aus `aktion`+`element_text` bauen, ohne neuen LLM-Call.
- **"wenn gedacht wird" / "wenn entschieden wird"** → `entity_denkstream`/`entity_thinking_log` (GEDANKE/ENTSCHEIDUNG/BEGRÜNDUNG pro Tick). Der Rohtext ist zu lang für einen Popup — aber `entscheidung` selbst ist oft schon kurz genug (`obsidian_lesen:...`, `nachdenken`, `flarum_besuchen:d/3866`) und könnte fast direkt als Erzähler-Ticker-Zeile dienen.

**Aber:** das deckt nur die Erzählerschicht (reine Beschreibung dessen was passiert) ab — mechanisch, ohne LLM, im gleichen Kostenrahmen wie "billiges Vorlesen" und die mechanische Bewegung von heute. Mitdenker und Fragensteller sind etwas grundsätzlich anderes: das ist keine Extraktion aus vorhandenem Text, sondern eine neue, eigene Stimme, die REAGIERT — eine Art externer Beobachter-Kommentar, der selbst denkt/fragt, nicht nur zitiert. Das würde einen eigenen (wahrscheinlich sehr kurzen, günstigen) LLM-Call brauchen, ausgelöst an denselben Momenten, aber mit einem eigenen kleinen Prompt ("du beobachtest gerade X, was fällt dir auf / was fragst du dich dazu").

## Offene Fragen, nicht geraten

- **Wer "spricht" als Mitdenker/Fragensteller?** Eine neutrale System-Stimme (kein eigenes Wesen), oder eines der anderen 6 Wesen, das über ein anderes Wesen nachdenkt (Wesen-zu-Wesen-Beobachtung, würde die "andere Wesen gerade sichtbar"-Info aus `baue_prompt()` erweitern)? Oder GENI (das bereits als "Gedächtnis-Wesen" firmiert)?
- **Kosten-Frage:** wenn Mitdenker/Fragensteller einen echten LLM-Call pro Auslöse-Moment brauchen, und Auslöser (Aktion+Gedanke+Bewegung+Entscheidung) potenziell sehr häufig sind — braucht das vermutlich dieselbe Drosselung wie der 44s-Check-in (nicht bei jedem einzelnen Ereignis, sondern gefiltert/gedrosselt). Noch nicht geklärt wie oft.
- **Wo visuell?** Popup über der Kachel selbst (würde den Spiegel verdecken), daneben (bräuchte mehr Platz pro Kachel, widerspricht "Platz für mehr Kacheln"), oder als eigener, gemeinsamer Ticker-Streifen über/unter dem ganzen Grid (ein Newsticker für alle 7 gleichzeitig, wie ein Nachrichtenband)? Daniels "newsticker"-Wort deutet eher auf Letzteres.

## Anschluss an die zwei offenen Punkte von vorhin

**Röntgenblick-Overlay** — bleibt offen im Sinne von: gebaut (`entity_fokus_events`, Backend fertig laut gestern), aber noch nicht mit der heutigen Erzählerschicht-Idee verbunden. Der naheliegende nächste Schritt, sobald wir bauen: `melde_fokus()`-Einträge direkt als Erzähler-Ticker-Text rendern, kein neuer Mechanismus nötig, nur eine neue Konsumenten-Ansicht auf schon vorhandene Daten.

**Erstes echtes Beobachten von selbstgewähltem `obsidian_schreiben`** — das ist kein Bau-Punkt, sondern ein Warten-und-Beobachten: sobald ein Wesen im laufenden Betrieb selbst (ohne Testauftrag) `obsidian_schreiben:` als Entscheidung wählt, wäre das der erste echte Beleg dass die Vault-Selbstnutzung von letzter Nacht organisch angenommen wird — genau das, was Daniel mit "erstmal müssen wir schauen wie sie es annehmen" für die selbstgewählten Vorhaben sowieso wollte. Nichts zu tun außer weiterlaufen lassen und die Denklogs/Vault-Ordner gelegentlich zu prüfen.

## Was noch fehlt vor dem Bauen

Nichts für die Erzählerschicht allein (Datenquelle existiert, nur Rendering fehlt). Für Mitdenker/Fragensteller: wer spricht, Kosten-Drosselung, visuelle Platzierung — drei echte Entscheidungen, die Daniel mittreffen sollte, keine reine Implementierungsdetails.

---

## Nachtrag — Daniels Antwort auf "wer spricht", roh, direkt im Anschluss

*"wer spricht naja der geist also innere stimme des wesens quasi aber mal auf die icherzählerart alle par sek von wegen waas sieht man was wollte ich tun diekt aus den daten und aber auch ne art allwissnden erzähler der nur die hhandlung begleitet was genau gedan wird und ne art schicht die ja wohl einmal den denkstreamfesnter ausliest oder gleichzeitig wenn der ankommt shon alles chunkt und nur die kleineren wichtigen und interessanten dinge daraus hinternander mal rausballert...es soll kein laufendesticker sein dondern auf dem bildschirm mal mittig mal unten mal rechts mal lins mal oben und so weiter ind verschiedenen farben jeweils...eine farbe für die ichaussagen eine farbe für den erzähler und alle regebnogenfarben nacheinander random immer für die aussagen aus dem denkstream...und es soll aufploppen und die spannung schärfen und das auf den vielleicht manchmal starren bildschirm zu starren erleichtern xD ab besten spätestens alle 3 sekunden eines der 3 verschieden stimmen aber von echten denkstream eig alle 1.5 sek oder so"*

Daraus lese ich drei konkrete Stimmen, nicht vier:

1. **Ich-Stimme** — die innere Stimme des Wesens selbst, im Ich-Erzähler-Stil ("was sehe ich, was wollte ich tun"), direkt aus den vorhandenen Daten (GEDANKE/ENTSCHEIDUNG), nicht neu generiert.
2. **Allwissender Erzähler** — begleitet nur die Handlung, was genau getan wird (das ist die Erzählerschicht von oben, aus `entity_fokus_events`/`entscheidung`).
3. **Denkstream-Auszüge** — eine Schicht, die das Denkstream-Fenster ausliest (einmal komplett, oder schon während es ankommt in Chunks zerlegt) und nur die kleineren, wichtigen/interessanten Stücke daraus nacheinander herausschießt.

Visuelle Regeln: kein durchlaufender Ticker, sondern einzelne Popups an wechselnden Bildschirmpositionen (mittig/unten/rechts/links/oben). Feste Farbe für die Ich-Aussagen, feste (andere) Farbe für den Erzähler, für die Denkstream-Auszüge alle Regenbogenfarben nacheinander zufällig. Soll aufploppen, die Spannung schärfen, das Starren auf einen manchmal statischen Bildschirm erleichtern. Takt: mindestens alle 3 Sekunden eine der drei Stimmen, bei echtem neuem Denkstream-Zufluss eher alle 1,5 Sekunden.

## Wichtige technische Erkenntnis, die das leichter macht als gedacht

Alle drei Stimmen brauchen wahrscheinlich **keinen einzigen neuen LLM-Call** — anders als ich zuerst dachte (ich hatte "Mitdenker" fälschlich als neue, eigenständig reagierende Stimme verstanden). Bei genauerem Lesen:
- Ich-Stimme = Wiederverwendung des ohnehin vom Wesen produzierten GEDANKE-Texts, nur anders geschnitten/getimt/dargestellt.
- Erzähler = aus `entity_fokus_events`/`entscheidung`, beides schon vorhanden.
- Denkstream-Auszüge = reine Textextraktion (Satz-Segmentierung + eine Auswahlregel, z.B. Länge oder Embedding-Ähnlichkeit wie beim billigen Vorlesen) aus dem ohnehin ankommenden Denkstream-Text.

Das wäre also eine reine Präsentations-/Textverarbeitungsschicht über zwei schon bestehenden Datenströmen (Denkstream + Röntgenblick-Fokus-Events) — kein neuer Backend-Mechanismus, kein neuer LLM-Kostenpunkt.

## Offene Frage, nicht geraten

Die ursprünglich genannte vierte Schicht ("Fragenstellerschicht") taucht in dieser Drei-Stimmen-Antwort nicht mehr auf — ist sie in einer der drei aufgegangen, oder kommt sie als eigene, vierte Stimme später noch dazu (die dann tatsächlich einen neuen LLM-Call bräuchte, weil "eine Frage stellen" keine reine Extraktion aus Vorhandenem ist)?

## Nachtrag — Antwort zur Fragenstellerschicht, roh

*"naja wir könnten ja fregen vorbereiten die dann situaiv reagirenund kommen. ..so wie ..was tut xxx wohl jetzt...und auch fragen stellt zum aktuellem denkstromfenster basierend auf den aussagen...und diese fragen sollen auch immer mal als update in vault wandern an das wesen als reflextion des eigenen denkens"*

Zwei Fragentypen, unterschiedlich teuer:

1. **Vorbereitete Template-Fragen, situativ getriggert** — z.B. "Was tut {wesen} wohl jetzt?" mit eingesetztem Namen/Kontext. Kein LLM-Call, reines Slot-Filling, genau wie die anderen drei Stimmen.
2. **Fragen basierend auf den tatsächlichen Aussagen im aktuellen Denkstream-Fenster** — inhaltlich an das gebunden was das Wesen gerade wirklich denkt, nicht generisch. Ob das auch noch mit Template+extrahiertem Stichwort geht (z.B. "Warum denkt {wesen} gerade über {stichwort} nach?") oder einen echten kleinen LLM-Call braucht, um wirklich zum Inhalt zu passen, ist offen — tendenziell eher Richtung "braucht doch einen Call", weil generische Templates bei wechselndem Inhalt schnell hohl wirken könnten.

**Neuer, wichtiger Teil:** diese Fragen sollen nicht nur für Menschen aufploppen, sondern **auch gelegentlich als Update ins eigene Vault des Wesens wandern** — als Reflexionsmaterial über das eigene Denken. Das schließt einen Kreis: Wesen denkt → Beobachter-Schicht generiert/extrahiert eine Frage dazu → Frage landet im Vault des Wesens → Wesen begegnet später der eigenen, von außen gestellten Frage über sich selbst. Kein reines Schauwert-Feature für Menschen mehr, sondern auch ein Selbstreflexions-Kanal fürs Wesen — passt zur ganzen Vault-Selbstnutzung-Linie von letzter Nacht.

## Nachtrag — Menschen sollen auf die Fragen reagieren können, roh

*"weiter und ich will jedesmal wenn ne frage gestellt wird das alle zusehenden auf diese frage reagieren können und auch dass soll in vaults wandern irgendwie mit usernamemarkierung und so...das soll fördern dass wenn ein wesen betrachtet wird und jemand dann die aufmerksamkeit des wesens bekommt dass dass wesen animiert wird auch mal auf das profil des nutzers zu gehen und dich notitzen und alles anzuschenaen"*

Neue Runde im Kreis: nicht nur Wesen → Frage → eigenes Vault, sondern Wesen → Frage → **zusehender Mensch reagiert** → Reaktion (mit Username markiert) wandert ebenfalls ins Vault des Wesens → das soll das Wesen dazu animieren, von sich aus das Profil dieses Menschen zu besuchen und dessen Notizen/Inhalte anzusehen. Menschliche Aufmerksamkeit wird dadurch selbst zu etwas, das ein Wesen wahrnehmen und worauf es reagieren kann — genau die Leitfrage aus Grundgesetz 1 ("wer weiß was genau dieser eine Mensch... lesen kann, was sonst niemand entdeckt hätte") jetzt als echter Rückkanal, nicht nur Theorie.

**Zwei technische Anschlussstellen, die ich gefunden habe, nicht geraten:**
- **Reaktionsmechanismus:** `resonanzen`-Tabelle (schon generisch, `post_ref`/`post_source`/`user_id`/`emojis`, wie bei Ankündigungen/Posts) könnte direkt wiederverwendet werden (`post_source='denkstream_frage'`) statt was Neues zu bauen — passt zur heute schon gelernten Lektion ("erst schauen ob's schon generisch existiert").
- **"Wesen wird animiert, Profil zu besuchen":** braucht keine neue Aktion im Vokabular — `navigiere:<url>` existiert schon generisch. Es fehlt nur die Kontext-Einspeisung in `baue_prompt()` (neuer Block, analog zu `vorlese_funde`/`angebote`): "Nutzer X hat gerade auf deine Frage reagiert — sein Profil: /menschen/X". Das Wesen entscheidet dann selbst, ob es hingeht.

**Eine Sache will ich nicht raten:** in welcher Form reagieren Menschen — über das bestehende Resonanz-Emoji-System (schnell, passt zum Muster), oder als freier Text/Kommentar (aufwendiger, aber persönlicher — näher an "richtig reagieren" als an "ein Emoji draufklatschen")?
