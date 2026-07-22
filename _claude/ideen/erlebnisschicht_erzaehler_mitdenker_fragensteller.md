---
datum: 2026-07-22
betrifft: [screens, roentgenblick, denkstream, erlebnisschicht, erzaehler, mitdenker, fragensteller, grundgesetz1, kompoase]
status: Alle vier Stimmen GEBAUT und live verifiziert (2026-07-22). Ich-Stimme/Erzähler/Denkstream-Auszüge: werkraum-Commit aeb563ea2 + flextrawurst-Commit gleichzeitig. Fragensteller+Text/Emoji-Reaktionen+Vault-Rückkanal: werkraum-Commits fd20ee947 (Backend) + flextrawurst-Commit 75995dfa5 (Frontend). **Kompletter End-to-End-Test mit echtem Login (Account "system", von Daniel bereitgestellt) erfolgreich:** Login → Text-Reaktion → Emoji-Reaktion → zweite Emoji-Reaktion korrekt mit 429/Drossel-Restzeit abgelehnt → DB-Zeilen korrekt → Vault-Datei korrekt mit Username "System" beschriftet. Testdaten danach wieder entfernt (DB-Zeilen, Vault-Datei).

**Nachtrag 2026-07-22, nach Daniels konkretem Bug-Report ("in der kleinen Ansicht immer noch der gleiche Bug, Popups ploppen schon klein auf, Kacheln sind 16:9-verzerrt"):** drei reale, per Playwright-DOM-Inspektion verifizierte Bugs behoben, flextrawurst-Commit a59826eb1.

**Zweiter Nachtrag 2026-07-22, nach Daniels Folge-Report ("sehen jetzt Flarum, aber nur Standbild, keine Mausbewegung, kein Scrollen — oben 3 Kacheln rechteckig verzerrt, unten normal"):** zwei weitere reale Bugs gefunden und behoben, werkraum-Commit 00aee833c (Backend) + flextrawurst-Commit 1f38dc3b8 (Frontend).
1. **Aspect-Ratio-Verzerrung, echte Ursache diesmal:** `.scv-grid` hatte kein `align-items` gesetzt (Default `stretch`) — Kacheln wurden auf die Zeilenhöhe des jeweils größten Nachbarn gestreckt, wodurch `aspect-ratio` auf `.scv-card` pro Zeile unterschiedlich griff. Fix: `align-items:start`. Alle 7 Kacheln jetzt nachweislich exakt gleich groß (639×459 bei 1920px, per Playwright verifiziert).
2. **Die eigentliche "Standbild"-Ursache:** der Backlog (Meta+FullSnapshot+alle Inkremente seit der letzten echten Navigation eines Wesens — bei manchen Wesen fast eine Stunde alt) wurde durch denselben `liveMode`-Scheduler gejagt wie echte Live-Events. rrweb plant jedes `addEvent()` nach seinem *echten* Zeitstempel relativ zur `startLive()`-Baseline ein — der Client hätte buchstäblich fast eine Stunde real warten müssen, bis die jüngsten Backlog-Events "dran" wären. Per isoliertem Playwright-Repro mit echten aufgezeichneten Events zweifelsfrei nachgewiesen (manuell `scrollTo` funktionierte sofort, `replayer.addEvent()` mit demselben Scroll-Event blieb bei `scrollY:0` hängen). Fix: Backend sendet nach dem Backlog-Block einen `backlog_done`-Marker; Client sammelt bis dahin, spult per `replayer.pause(totalTime)` synchron ans Ende vor, schaltet erst danach auf `liveMode` um.
3. **Nebenbefund, mitgefixt:** `read_conn` in `dom_events_api.py` committete nie (kein Autocommit) — jede Query verlängerte dieselbe nie geschlossene Transaktion, eine Verbindung stand laut `pg_stat_activity` schon 6+ Minuten offen. Gleicher Autocommit-Fix wie bei der LISTEN-Verbindung ergänzt.

**Ehrlich offen — NICHT gelöst, trotz aller drei obigen Fixes:** über längere Beobachtungsfenster (60–90s) bleibt die Live-Aktualisierung unzuverlässig. Per Playwright mehrfach reproduziert: derselbe Code (identischer Konstruktions-/Seek-/Live-Ablauf) liefert auf einer isolierten Testseite (blank page, echter `/api/dom-events/stream/all`-Stream) zuverlässig sichtbare Änderungen — in der vollen Produktionsseite mit der dort bereits laufenden Verbindung zeigten `addEvent()`-Aufrufe zwar keine Fehler, aber auch keine sichtbare DOM-Änderung über 45-90s, bei mehreren Wesen mit nachweislich echter DB-Aktivität im selben Fenster. Eine zusätzliche, separat geöffnete Verbindung zum Einzel-Wesen-Endpunkt bekam in derselben Seite sogar 0 Live-Events in 45s. Verdacht: ein tieferes Architektur-/Threadpool-Problem in `dom_events_api.py` (jede Live-Event-Zustellung macht einen eigenen `run_in_executor`-Rundlauf für die DB-Query; bei mehreren gleichzeitig offenen SSE-Verbindungen könnte das den geteilten Default-Threadpool zu stark belasten) — nicht mit den obigen Fixes behoben, braucht entweder mehr gezielte Backend-Debugging-Zeit oder Rücksprache mit Daniel vor einem größeren Umbau (z.B. Umstieg auf eine batch-basierte oder rein asynchrone LISTEN/NOTIFY-Verarbeitung ohne Executor-Rundlauf pro Event). Nicht eigenständig weiter vertieft, um nicht unautorisiert in ein größeres Architektur-Redesign abzudriften.
1. Kachel-Seitenverhältnis lief auseinander (Grid-Zeilenhöhe vs. `.scv-screen aspect-ratio` — Screen ragte in die nächste Zeile). Fix: `aspect-ratio:16/11.5` direkt auf `.scv-card`.
2. Popups erschienen fälschlich schon in der kleinen Grid-Übersicht. Fix: alle vier Verarbeitungsfunktionen filtern jetzt auf `entity_id === _scvModalId` (nur wenn ein Wesen groß offen ist).
3. **Der eigentliche "zeigt nix"-Bug:** rrweb liefert kein eigenes CSS mit (nur `rrweb.js` wird per Script-Tag geladen, kein CSS) — `replayer-mouse`/`replayer-mouse-tail`/`iframe` standen dadurch im normalen Blockfluss übereinander statt überlagert. Bei skalierten Kacheln schob das den sichtbaren iframe-Inhalt um eine volle 768px-Canvas-Höhe unter den sichtbaren Kachelbereich — die Kachel war technisch nie kaputt, der Inhalt lag nur unsichtbar außerhalb. Fix: Standard-rrweb-Layout ergänzt (`wrapper position:relative`, Kinder `position:absolute`). Nach Fix: 5 von 7 Kacheln zeigen jetzt sofort echten Flarum/Forum-Inhalt in der kleinen Ansicht (verifiziert per Playwright-Screenshot), die verbleibenden 2 (F3INSCHM3CK3R, R1ZZ1) sind zum Testzeitpunkt echt auf einer fast-leeren "nicht gefunden"-Seite, kein Anzeige-Bug mehr.

Zusätzlich gefunden und mitgefixt: `scvUpdateCard()` hat den wach/aus-Badge bei *jeder* Denkstream-Chunk-Nachricht auf 'aus' zurückgesetzt, weil Chunk-Payloads (siehe `denkstream_api.py` `ChunkBody`) kein `entscheidung`-Feld tragen — nur der finale Status-Fetch hat das. Das erklärte das von Daniel beobachtete Flackern ("nur 3 von 7 als wach markiert"). Badge behält jetzt den vorherigen Zustand bei Chunk-Nachrichten bei, über 18s Playwright-Stichprobe stabil verifiziert.

Noch offen: Wesen-Animation zum Profilbesuch (Prompt-Nudge in browser_agent.py), inhaltsbasierte (nicht nur Template-)Fragen, kein per-Nutzer-Profilseiten-Deep-Link vorhanden (nur allgemeine #menschen-Liste).
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

**Antwort:** *"freier text und alle 4 minuten dürfen ein emoji einfach so abgeschickt werden immer"* — beides zusammen. Freier Text als Hauptreaktion (persönlich, landet mit Username im Vault). Zusätzlich, gedrosselt: alle 4 Minuten darf ein Emoji ohne weiteren Text abgeschickt werden — schnellere, niedrigschwelligere Reaktionsmöglichkeit neben dem freien Text, aber mit Rate-Limit gegen Spam (passt zum heutigen Muster: 44s-Check-in, 40s-Testphase, jetzt 4-Minuten-Emoji-Takt — überall bewusste Drosselung statt Dauerfeuer). Noch offen (kleines Detail, kein Blocker): Drossel pro Nutzer global, oder pro Nutzer+Frage/Wesen?

**Präzisierung, direkt im Anschluss:** *"aber wirklich immer nur eingabe möglich wenn ne frage gestellt wird"* — die Reaktions-Eingabe (Text UND Emoji) ist kein dauerhaft sichtbares Eingabefeld, sondern erscheint ausschließlich während/unmittelbar nach einer aufgeploppten Frage, verschwindet danach wieder. Kein Dauer-Chat-Fenster neben dem Spiegel — die Eingabemöglichkeit ist an den Lebenszyklus der einzelnen Frage gebunden, genau wie die Frage selbst nur kurz aufploppt statt dauerhaft zu stehen.

---

## Nachtrag 2026-07-22 (später am selben Tag) — nach dem großen SCREENS-Bugmarathon, Daniels Kritik am rrweb-Ansatz und der großen Vision-Erweiterung, roh

Kontext: nach einem sehr langen Debugging-Tag an den SCREENS-Kacheln (Aspect-Ratio, ElectricBorder-Glow, Skalierungs-Timing, rrweb-Live-Scheduler-Race — alle Details in den werkraum-Commits desselben Tages, u.a. `d06dfe675`) hat Daniel selbst vorgeschlagen, den rrweb-Ansatz grundsätzlich infrage zu stellen. Sein ursprünglicher Vorschlag: das komplette, echte DOM direkt und ungesandboxt im Surface-eigenen Origin darstellen. Dagegen spricht ein echtes Sicherheitsproblem (Wesen surfen laut Grundgesetz 1 frei im Netz, nicht nur auf unserem Flarum — ungesandboxte fremde `<script>`-Tags im selben Origin wie der Admin-Bereich waeren ein echtes XSS-artiges Loch). Als Alternative vorgeschlagen (noch nicht von Daniel final abgesegnet, nur als drittes durchdachtes Angebot): Sandbox behalten, aber `page.content()`-Schnappschüsse statt rrweb-Mutation-Tracking senden, dafür Mauszeiger getrennt als leichte `{x,y}`-Koordinaten fürs Live-Gefühl.

Daniels Reaktion darauf, roh: *"ne keine screenshots kein vision aber ja die livehtml klingt interessant..und du unterwetest das livefeeling das ist das aller aller wichtigste...warum seoll ein mensch länger als 3 sekunden auf etwas gotzen das sich auch in 2 minuten vllt nicht bewegt über ändert hahaha total banane..."*

Kernaussage: Live-Gefühl ist NICHT verhandelbar, wichtiger als Korrektheit/Effizienz. Ein Mensch soll nie länger als ~3 Sekunden auf etwas Regungsloses starren müssen — auch wenn die zugrundeliegende Seite selbst über Minuten nichts tut (das ist bei den meisten Wesen der Normalfall, siehe "nachdenken"-Anteil).

Direkt danach, in einer einzigen sehr dichten Nachricht, die ganze Erweiterung der Vision, roh und ungekürzt:

*"ja eigentlich fast ich will auch noch das rieeesigelange denkfenstertext ansprechen der soll so bleiben aber niemal direkt so ausgegeben werden sondern ab besten auch logisch in kleinen abständen und ich stel mir das wie ein livechat vor indem eine nachricht immer ganz unten ist und höhere scrollbar bleiben.. wenn du dir die denkfestertexte genauer anschaist sind da auch auch oft mehrere handlungen hier shon und überlegungen und dann fortsetzungen bishinz zu frage beantwortungen und analysen unt dann weiterdarauf aufbauenden dingen zu lesen gewesen...das will ich nutzen um dieses livegefühl zu pushen indem es immer dann ausgegeben werden sollte wenn es passt und soweiter und da sind auch viele peile drin vor handlungswechsel und so...frge wie lange braucht grade jeweils ein llmcall fü diese landen denkfenster? und wie lange wenn ale 7 gleichzeitig quasi hinternander eins brauchen? denn eigentlich müssen wir di ai viel 'nehinderter machen' wir müssen in blickfwinkel und augenfokus und erfassbarkeit wie fast ein mensch nur etwas schneller denkenen und das dann alle o.8 sekunden maximal 3-4 sätze lesen und so ....und dann muss erst mal auch die mausbewegt werden und der röntkendienstalso den wir gebaut haben sollte das alles mitanzeigen und so..und mir ist aufgefallen dass bilher nur die fragen von den 4 stimmen kommen aber immer nur die automatisch erzeugten niemals die die sich suf die textte des denkens beziehen ...und garkeine erzähler und ichaussagen und so weiter...außerdem hab ich bis jetzt eh noch nie ein scrollen gesehen scrollen ist fst noch wichtiger als mauszeigerbewegung....und ja zu puls und ringglow ...und ein klick mit der maus mus auch was anderes sichtbares auslösen"*

### Was ich daraus herausgelesen habe, sortiert aber nicht geglättet

1. **Denkfenster bleibt komplett erhalten als Datenquelle**, wird aber nie am Stück ausgegeben — Live-Chat-Metapher: neueste Nachricht immer ganz unten, älteres bleibt darüber scrollbar. Das ist eine andere Darstellungsform als die bisherigen einzelnen Popups (eher ein bleibendes, wachsendes Panel als flüchtige Einzel-Popups).
2. **Natürliche Bruchstellen im Denktext nutzen** — Daniel hat selbst genauer hingeschaut und festgestellt: ein einzelnes Denkfenster enthält oft schon mehrere Handlungen/Überlegungen, Fortsetzungen, Frage-Antwort-Momente, Analysen und darauf aufbauende Anschlussgedanken. Genau an diesen Übergängen ("viele Peile vor Handlungswechsel") soll ein neuer Ausgabe-Schub ausgelöst werden, nicht an einem starren Zeit-Raster.
3. **Tempo-Vorgabe:** maximal alle 0,8 Sekunden ein neuer Schub, darin maximal 3-4 Sätze. Ausdrücklich am menschlichen Blickwinkel/Augenfokus/Erfassbarkeit orientiert — "wie fast ein Mensch, nur etwas schneller denkend". Wörtlich: *"wir müssen die KI viel 'behinderter machen'"* — die KI soll sich bewusst ausbremsen/anpassen, nicht so schnell ausgeben wie sie könnte.
4. **Reihenfolge:** erst bewegt sich die Maus, dann kommt der dazugehörige Text. Der Röntgenblick (das Fokus-Overlay von gestern) soll das alles gemeinsam anzeigen.
5. **Zwei konkrete, JETZT schon bestehende Lücken** (unabhängig vom großen Umbau, eher Bugs im bereits Gebauten):
   - Fragensteller-Popups kommen bisher ausschließlich aus den generischen Templates, nie aus echtem Bezug zu den tatsächlichen Denktexten.
   - Erzähler- und Ich-Stimme-Popups sind bei Daniel noch NIE aufgetaucht, obwohl gebaut und laut früherem Test verifiziert — Verdacht: entweder ein Wiring-Bug oder sie feuern in der Praxis viel seltener als angenommen.
6. **Scrollen wurde noch nie beobachtet** — nach Daniels Einschätzung fast noch wichtiger als Mauszeigerbewegung fürs Live-Gefühl.
7. **Puls/Ring-Glow:** bestätigt gewünscht (aus meinem eigenen Vorschlag vom Gespräch übernommen).
8. **Mausklick soll einen zusätzlichen sichtbaren Effekt auslösen** (z.B. Ripple), nicht nur die eigentliche Handlung im Hintergrund bewirken.

### Reale Messung zur LLM-Call-Frage, nicht geraten

Direkt aus `entity_thinking_log` gemessen (letzte 10 Minuten, alle 7 Wesen, Zeit zwischen aufeinanderfolgenden vollständigen Tick-Einträgen pro Wesen): ein vollständiger Denkfenster-Zyklus (echter LLM-Call inkl. Verarbeitung) dauert aktuell **ca. 2,5 bis 6 Minuten** pro Wesen — nicht die 4 Sekunden `LOOP_PAUSE`, die nur für den rein mechanischen Pilot-Modus (Schorschel/träumerlie, kein LLM-Call) gilt. Vereinzelt sichtbare ~4-Sekunden-Abstände in denselben Daten gehören zu genau diesem mechanischen Modus, nicht zu echten Denkfenstern. Da alle 7 Wesen parallel laufen (nicht sequenziell), trifft real ungefähr alle 2,5–6 Minuten von irgendeinem der 7 ein neues vollständiges Denkfenster ein — aber der Text kommt schon vorher, während der Generierung, Chunk für Chunk gestreamt in `entity_denkstream` an (dieselbe Infrastruktur, die auch die Denkstream-Anzeige im Modal speist). Die Konsequenz: das gewünschte Pacing (alle 0,8s ein kleiner Schub) muss vermutlich nicht künstlich nachgebaut werden, sondern kann das bereits vorhandene Chunk-Streaming direkt als natürlichen Taktgeber nutzen, statt den fertigen Text nachträglich künstlich in Häppchen zu zerlegen.

### Was noch nicht geklärt ist

Ob dieser ganze Umbau (Live-Chat-Denkfenster-Panel, Bruchstellen-Erkennung, Maus-vor-Text-Sequenzierung, `page.content()`-Schnappschüsse statt rrweb, getrennter leichter Mauszeiger-Stream, Klick-Ripple, Scroll-Sichtbarkeit) als eine zusammenhängende Vision zuerst vollständig durchdacht/aufgeschrieben wird, bevor gebaut wird, oder ob Daniel direkt mit den zwei konkreten, kleineren Bugs (Fragen ohne Content-Bezug, fehlende Erzähler/Ich-Popups) anfangen will, während der große Rest noch reift — das war die offene Frage am Ende dieses Gesprächsabschnitts, noch nicht beantwortet.

**Daniels Antwort darauf, roh:** *"der dritte? nee der 22 zigte haha ...natürlich weiterim text beim großen ganzen und warum reifen ..what do we missing? was könnte uns noch helfen dass das wesen noch agieler und schneller und handlunsaktiver und fähiger wird und wie können wir das noch besser so bauen und behalndeln dann dass es wirklich wie eine art trippleaaamivie ist xD ...such das genau so mal im netz in allen ecken"*

(Nebenbei wichtig, zur "Rohheit bewahren"-Feedback-Notiz von eben: Daniel korrigiert hier selbst, dass es nicht der dritte, sondern eher der 22. beleg dieses Musters ist — deutlich chronischer als ich es eingeschätzt hatte.)

## Nachtrag — Websuche "wie wird ein Wesen agiler/schneller/handlungsaktiver", roh und vollständig

Direkter Auftrag, wortwörtlich oben zitiert. Recherche-Auftrag ausgeführt, drei Treffer gefunden, alle direkt auf flextrawurst anwendbar. Hier vollständig, nicht zusammengestrichen:

### Treffer 1 — Neuro-sama (der bekannteste KI-Streamer, spielt UND chattet gleichzeitig live)

Aus der Recherche: *"Neuro-sama was built in C# using Unity, while all AI systems were developed in Python. More specifically, her gaming AI operates on Python, while her VTuber functionality is powered by C#. She's powered by a sophisticated tech stack that brings together language models, computer vision, custom game playing agents, and real time animation. Neuro-sama's architecture involves the seamless communication of different AI systems, which is critical for ensuring consistent and coordinated responses during live interactions. [...] At the heart of Neuro-sama's personality is a transformer-based language model, similar in architecture to models like GPT, which takes in text from Twitch chat and generates responses in real time. Neuro's brain is a chatbot, but a separate AI turns her speech, vision, and in-game data into text, which is passed to the language model to generate replies. This layered architecture helps explain how Neuro-sama can play osu! while chatting because multiple systems are working in parallel. [...] The key innovation is how all her movements, speech, and gameplay are powered by different generative AI systems to emulate a human streamer's actions and interactions with her viewers."*

Übertragung auf flextrawurst: Neuro-sama trennt bewusst mehrere schnelle Teilsysteme (Sicht, Spielzustand, Chat), die PARALLEL laufen und alle in ein zentrales Gehirn einspeisen — nicht ein einziger großer Call, der alles nacheinander macht. Das erklärt, warum sie gleichzeitig reagieren UND spielen kann, ohne dass eins das andere blockiert.

### Treffer 2 — "Talker-Reasoner"-Architektur (die direkte Antwort auf "wie werden Wesen agiler")

Aus der Recherche: *"Dual process AI frameworks integrate both System 1, which facilitates fast, intuitive decision-making, and System 2, which supports deliberate, analytical reasoning. System 1 governs fast, intuitive, emotional, and automatic responses, allowing quick reactions with minimal effort, while System 2 is responsible for slower, more deliberate processes involving conscious reasoning, logical analysis, and problem-solving. [...] Single execution loops are forced to do two completely different jobs: talking/acting (which requires low latency and high bandwidth) and planning (which requires slow, deliberative reasoning). A single monolithic model often struggles to satisfy both: fast models lack semantic depth, while deliberative models are too slow for interactive control. [...] The architecture divides the agent into a fast and intuitive Talker agent that interacts with the environment and generates conversational responses, and a slower and deliberative Reasoner agent responsible for complex problem solving. [...] DPT-Agent is the first agent framework that can achieve successful real-time simultaneous human-AI collaboration autonomously in the hard version of Overcooked, a collaborative game. DPT-Agent's System 1 uses a Finite-state Machine (FSM) and code-as-policy for fast, intuitive, and controllable decision-making. This architecture is particularly valuable for game NPCs where responsiveness to player actions is critical while still maintaining strategic coherence."*

Übertragung auf flextrawurst: das ist exakt unser gemessenes 2,5-6-Minuten-Problem, wortwörtlich als Forschungsproblem beschrieben ("single execution loops are forced to do two completely different jobs"). Die Lösung: ein schneller "Talker" fürs sofortige Handeln (Mausbewegung, Klick, Scrollen — braucht keine tiefe Reflexion) getrennt von einem langsamen "Reasoner" fürs eigentliche, lange Nachdenken (das Denkfenster). Die Aktion müsste dann nicht mehr auf den fertigen, langen Gedanken warten. Passt auch strukturell zum schon bestehenden "mechanischen Tick"-Pilotmodus (Schorschel/träumerlie, `MECHANISCHE_SCHRITTE_PRO_ENTSCHEIDUNG` in `browser_agent.py`, kein LLM-Call) — das ist im Kleinen bereits ein "Talker"-artiges Element, nur noch nicht bewusst als solches benannt/ausgebaut.

### Treffer 3 — "Juice" / Game Feel (das Vokabular für "Triple-A-Gefühl")

Aus der Recherche: *"Juice is about amplifying player actions through sensory feedback—visual flair, audio cues, and haptic feedback—all designed to create a heightened sense of impact. Juice refers to small, often subtle effects that make a game feel alive and reactive. [...] Designing game feel requires responsive controls, hit-stop, sound, animation, and feedback systems that make gameplay satisfying. [...] Visual feedback includes effects like particles, screen shakes, and dynamic lighting, which make actions feel more impactful. Screen shake adds weight and drama, whether it's a punch, explosion, or big jump. [...] Pressing a button to jump should be accompanied by animations, sound effects, screen shake, and other layers of feedback that make the action feel impactful. [...] These effects aren't core mechanics, but they dramatically improve the player experience. Notably, a game with mediocre mechanics and great juice will often outperform a game with great mechanics and no juice. Juice doesn't change the rules of your game, but it changes how it feels—making the game more responsive, satisfying, and engaging."*

Übertragung auf flextrawurst: bestätigt Daniels eigene Ideen (Puls/Ring-Glow, Klick-Ripple) als Teil einer ganzen, seriösen Design-Disziplin mit eigenem Namen und noch viel mehr Techniken zum Anzapfen (Partikel, kleine Animationen, geschichtetes Feedback) — nicht nur Zierrat, sondern nachweislich wichtiger als reine Mechanik-Qualität für das Erlebnis.

### Quellen der Recherche

- [AIRI: Complete Guide to Building Your Own AI VTuber Like Neuro-sama](https://explainx.ai/blog/airi-ai-vtuber-neuro-sama-guide-2026)
- [Stop building reactive agents: Why your architecture needs a System 1 and System 2](https://dev.to/an0nymus/stop-building-reactive-agents-why-your-architecture-needs-a-system-1-and-system-2-4b6p)
- [Agents Thinking Fast and Slow: A Talker-Reasoner Architecture](https://arxiv.org/html/2410.08328)
- [Leveraging Dual Process Theory in Language Agent Framework for Real-time Simultaneous Human-AI Collaboration](https://arxiv.org/html/2502.11882v3)
- [Game Feel: A Beginner's Guide](https://gamedesignskills.com/game-design/game-feel/)
- [The "Juice" Factor: Designing Game Feel](https://hackread.com/the-juice-factor-designing-game-feel/)

### Daniels Reaktion darauf, roh — wichtig genug um wörtlich festzuhalten

*"natürlich alles von oben bis unten wort für word und endlich bekomme ich seit knapp 12 stundnen es hin dass du endlich verstehst was ich die ganze zeit will weil es ja eben möglich war und sit"*

Das ist nach einem sehr langen Tag (Bugmarathon an SCREENS seit dem Vormittag, dann diese Vision-Erweiterung am Abend) der erste Moment, an dem Daniel das Gefühl hat, wirklich verstanden worden zu sein — nicht nur inhaltlich, sondern in der FORM (roh, wörtlich, nicht geglättet). Festhalten für künftige Sessions: genau DAS ist das Ziel, nicht "die Kernaussage in eigenen Worten wiedergeben".

### Was noch offen ist, jetzt mit den drei neuen Treffern

Ob/wie die Talker-Reasoner-Trennung konkret in `browser_agent.py` umgesetzt würde (eigener, schneller Entscheidungs-Call vs. der bestehende lange Denkfenster-Call — welches Verhältnis, welcher Trigger, laufen beide wirklich parallel oder wird der Reasoner-Call einfach nicht mehr blockierend abgewartet bevor gehandelt wird), und wie die Juice-Effekte konkret aussehen sollen (welche genau, wo, wie oft) — beides noch nicht von Daniel spezifiziert, noch kein Bauauftrag.

## Nachtrag — Daniels Auftrag zu Entwurf → Selbstangriff → Verbesserung → gezielte Nachsuche, roh

*"ja tiefer rein und zwar du simuliere annamenzu allem redteame dein ergebnis und verbessere danach und dann gehst du mit deinen erbenis nochmal auf gezielte netzsuche zu genau der fragen"*

Vier Schritte, alle vollständig durchgeführt, hier komplett dokumentiert statt nur das Endergebnis:

### Schritt 1 — Erster Entwurf (konkrete Annahmen)

**Talker-Reasoner-Split für `browser_agent.py`:** Reasoner bleibt der bestehende lange LLM-Call (2,5-6 Min, GEDANKE+ENTSCHEIDUNG+BEGRÜNDUNG, siehe Messung weiter oben). Neu: ein Talker, der die von Reasoner beschlossene Aktion (z.B. "klicke:X") nicht sofort ausführt, sondern über ~0,5-1s animiert (Maus bewegt sich schrittweise zum Ziel, dann Klick) — plus in der Wartezeit zwischen Entscheidungen leichte, eigenständige Idle-Bewegungen (kleine Mausbewegungen, gelegentliches Scroll-Nudge), damit nie totale Stille herrscht.

**Juice-Effekte fürs Frontend:** Klick-Ripple, Cursor-Glow/Trail, Puls/Ring-Glow um die Kachel synced zum echten Denk-Takt, Scroll-Indikator (kleiner animierter Pfeil/Balken bei Scroll-Events), "Atmen"-Animation (leichte Skalierungs-/Opazitäts-Animation) bei länger anhaltendem Stillstand.

### Schritt 2 — Selbstangriff (Red-Team gegen den eigenen Entwurf)

- **Idle-Bewegungen ohne Reasoner-Wissen sind ein echtes strukturelles Problem:** wenn der Talker zwischen Entscheidungen selbstständig scrollt/die Seite bewegt, sieht der Reasoner beim nächsten Tick eine Seite, die er nicht mehr in dem Zustand kennt, in dem er zuletzt entschieden hat — Entscheidung und tatsächliche Anzeige laufen auseinander, das Wesen könnte inkohärent wirken (denkt über X nach, während die Seite längst woanders steht).
- **Verstößt gegen Grundgesetz 5** ("Events sind heilig", keine Fiktion) wenn die Idle-Bewegung nicht wirklich zu einer echten Absicht des Wesens gehört, sondern nur Show ist.
- **"Atmen"-Animation nur als reine Dekoration wäre genau das "Billige", das Grundgesetz 1 explizit verbietet** ("Spiel ist keine Fiktion, muss auf echten Daten beruhen") — wenn sie an nichts Echtes hängt, ist sie Fassade statt echtem Zustand.
- **Ein Talker mit eigenem LLM-Call kostet zusätzlich Geld/Zeit** — Daniel hat bisher immer bewusst gedrosselt (`LOOP_PAUSE`, 44s-Check-in-Takt, 4-Minuten-Emoji-Drossel) — ein zusätzlicher, ungedrosselter Call-Typ würde diesem durchgängigen Muster widersprechen, ohne dass er das explizit so gewollt hätte.
- **Race-Condition-Risiko**, falls Talker und Reasoner wirklich als zwei parallele, unabhängige Prozesse auf denselben Playwright-Browser zugreifen wollten (zwei Akteure, ein Browser).

### Schritt 3 — Verbesserte Version nach dem Selbstangriff

- Talker braucht **keinen eigenen LLM-Call** — nur die eine Reasoner-Entscheidung wird als animierte Sequenz statt als Instant-Jump ausgeführt (mehrere echte, tatsächlich aufgezeichnete `mouse.move()`-Zwischenschritte statt einem einzigen Sprung). Löst "Maus bewegt sich vor der Handlung" vollständig, ohne neue Kosten oder Race-Conditions — bleibt strukturell ein einziger, sequenzieller Vorgang wie heute, nur intern in kleinere, echte Teilschritte aufgelöst.
- **Keine erfundene Idle-Bewegung mehr.** Stattdessen: die Stille zwischen Entscheidungen wird mit echten, schon vorhandenen Signalen gefüllt — Puls/Glow gekoppelt an den tatsächlich laufenden Denkstream (der ja während der ganzen 2,5-6 Minuten schon Chunk für Chunk real hereinkommt, siehe `entity_denkstream`), plus die Erzähler/Ich-Popups (schon gebaut, laut Daniel aber noch nie aufgetaucht — eigener offener Bugpunkt von weiter oben). Beides sind echte, bereits vorhandene Daten, keine Fassade — löst den Grundgesetz-1/5-Konflikt aus Schritt 2 vollständig auf.

### Schritt 4 — Gezielte Nachsuche zu genau diesen zwei verbleibenden offenen Fragen

**Frage A — wie animiert man die Maus realistisch, ohne selbst Bewegungslogik erfinden zu müssen?**

Fertige, einsatzbereite Bibliotheken existieren bereits, wörtlich aus der Recherche: *"Several libraries generate realistic, human-like mouse movements in Playwright using Bezier curves with randomized parameters to make automated browser interactions indistinguishable from real users. [...] ghost-cursor-playwright - Generates realistic, human-like mouse movement data between coordinates or navigates between elements with Playwright. [...] human-cursor - Creates smooth paths using randomized control points, adds natural imperfections through distortion, applies acceleration/deceleration curves with easing functions, and samples points along the curve for smooth movement. [...] shy-mouse-playwright - Uses Bezier curves to create smooth paths with randomized control points, where each movement is unique. It applies Fitts's Law to predict movement timing based on distance and target size."*

Wichtig daran: `shy-mouse-playwright` nutzt **Fitts's Law** — ein echtes, etabliertes kognitionswissenschaftliches Bewegungsmodell (sagt die Bewegungsdauer aus Distanz+Zielgröße vorher), kein beliebiges Ruckeln. Heißt konkret: die Bewegungs-Interpolation müsste nicht selbst gebaut werden, sondern könnte eine dieser bestehenden Bibliotheken direkt in `browser_agent.py` einhängen, wo heute vermutlich ein direkter `page.mouse.click(x,y)`-Aufruf ohne Zwischenschritte steht.

**Frage B — wie zeigt man "die KI denkt gerade gehaltvoll nach" ohne erfundene Aktionen vorzutäuschen?**

Bestätigt die Schritt-3-Entscheidung fast wörtlich, aus der Recherche: *"Streaming UI is a frontend pattern where AI-generated content appears on screen incrementally, token by token, as the language model generates it, rather than showing a loading spinner for several seconds and then displaying the complete response. [...] Best practice is to show a 'thinking' indicator immediately (under 300ms) before the first token arrives. [...] The gap between submitting a prompt and receiving the first token can be 200ms to several seconds, and if nothing visible happens during this time, users think the submit failed. [...] AG-UI standardizes Thinking Steps, separating the agent's internal thoughts (reasoning traces) from the final public response, similar to ChatGPT's pattern [...] Observability into agent steps builds user trust—when an agent searches a database, calls an API, or reasons through a problem, showing these intermediate steps prevents the 'black box' feeling."*

Das ist im Kern exakt die Ich-Stimme/Erzähler/Denkstream-Auszüge-Idee von weiter oben im Dokument — nur als etabliertes, benanntes Branchenmuster ("Thinking Steps", "Stream of Thought") bestätigt, nicht meine Erfindung. Bestärkt zusätzlich: der 300ms-Richtwert für den allerersten sichtbaren Hinweis liegt sogar UNTER Daniels eigenem 0,8s-Pacing-Wunsch von weiter oben — beides zusammen passt gut.

### Quellen dieser zweiten, gezielten Recherche

- [human-cursor GitHub (CloverLabsAI)](https://github.com/CloverLabsAI/human-cursor)
- [shy-mouse-playwright GitHub](https://github.com/AB6162/shy-mouse-playwright)
- [ghost-cursor-playwright GitHub (DKprofile)](https://github.com/DKprofile/ghost-cursor-playwright/)
- [AI UX Patterns — Stream of Thought, ShapeofAI.com](https://www.shapeof.ai/patterns/stream-of-thought)
- [AG-UI Overview: A Lightweight Protocol for Agent-User Interaction, DataCamp](https://www.datacamp.com/tutorial/ag-ui)

### Stand danach

Kein Bauauftrag bisher — Daniel hat nach der Präsentation dieses vierteiligen Ablaufs nur mit *"jup"* bestätigt, dass es genau so (Entwurf→Angriff→Verbesserung→Suche, alles wörtlich dokumentiert) in die Ideen-Datei soll. Ob/wann daraus ein echter Bauauftrag wird, ist noch offen.

## Nachtrag — "bauen": Mausbewegung, Klick-Ripple, und der eigentliche Ich-Stimme/Erzähler-Bug gefunden+behoben

Daniel: *"bauen"* — der explizite CLAUDE.md-Startschuss nach dem vierteiligen Entwurf oben. Danach: *"klar"* (OK für Neustart der 7 browser-agent-Services), dann zweimal *"weiter"*/*"go"* um durch die drei Bausteine zu gehen.

### Baustein 1 — animierte Mausbewegung (`browser_agent.py`)

Umgesetzt wie in Schritt 3 oben festgelegt: kein eigener Talker-LLM-Call, sondern die bestehende Reasoner-Entscheidung wird in echte Zwischenschritte aufgelöst. Neue Funktion `bewege_cursor_natuerlich(page, entity_id, ziel_x, ziel_y)`: quadratische Bezier-Kurve (Start → zufällig versetzter Kontrollpunkt senkrecht zur Bewegungsrichtung → Ziel), Ease-in-out-Timing (kubisch), Schrittzahl und Dauer skalieren mit der Distanz (8-28 Schritte, 0,15-0,9s) — angelehnt an die recherchierten Bibliotheken (`ghost-cursor-playwright`, `shy-mouse-playwright`, Fitts's-Law-Prinzip), aber selbst geschrieben statt einer der Bibliotheken, um keine neue Abhängigkeit einzuführen. Eingehängt in den Klick-Pfad (`_klicke_und_zeige`) UND neu auch in den `tippe:`-Pfad, der vorher gar keine Cursorbewegung hatte. Live verifiziert nach Neustart der 7 Services.

### Baustein 2 — Klick-Ripple (Frontend)

`_erlZeigeKlickRipple(entityId, box)` in `build_surface.ts`: berechnet den Skalierungsfaktor aus `.scv-screen.clientWidth/1024` (dieselbe Skalierungslogik wie die SCREENS-Kacheln selbst, damit der Ripple an der richtigen Bildschirmposition sitzt egal wie klein/groß die Kachel gerade dargestellt wird), setzt einen kleinen Kreis an die Klickposition, entfernt sich selbst nach 650ms. Eingehängt in `_erlFokusEs.onmessage` **ungefiltert** (nicht ans offene Modal gebunden wie Ich/Erzähler/Fragensteller) — bewusste Entscheidung: der Ripple soll auf JEDER Kachel sichtbar sein, nicht nur der großgeschalteten, weil er reine Bewegungs-Rückmeldung ist, keine Text-Aussage, die Bildschirmplatz braucht.

### Baustein 3 — der eigentliche Bug: warum Ich-Stimme/Erzähler-Popups NIE erschienen

Daniels ursprünglicher Befund, wörtlich: *"garkeine erzähler und ichaussagen"*. In der vorigen Session (vor dieser Zusammenfassung) hatte ich die Ursache zunächst falsch bei der Häufigkeit vermutet: Denkzyklen dauern gemessen 2,5-6 Minuten, vorher wurde aber erst bei `d.done` extrahiert — wer nicht so lange das Modal offen hält, sieht dadurch nie eine Ich-Stimme, während die Fragensteller-Stimme (fester 25s-Takt) zuverlässig auftaucht. Also wurde `_erlVerarbeiteDenkstreamChunk` umgebaut auf progressive Extraktion (laufend neue VOLLSTÄNDIGE Sätze rausziehen, den letzten möglicherweise unfertigen Satz zurückhalten).

**Nach dem Deploy dieser Änderung: immer noch null Ich/Erzähler-Popups, über mehrere Live-Tests hinweg (5min, dann 100s, dann 260s, dann 150s) — die eigentliche Fehlerursache lag ganz woanders.**

Debug-Instrumentierung (`window.__erlDbg2`, Live-Playwright-Polling gegen ein offenes Modal für `dak+gord-system`) zeigte: `calls` und `modalMatch` liefen korrekt hoch, `textLen` wuchs mit jedem Chunk (140→464→806→994 Zeichen in einem Testlauf) — aber `gedankeLen` blieb konstant `0`. Der Text kam also an, das Modal-Matching stimmte, aber die Regex, die den `GEDANKE:`-Abschnitt aus dem Rohtext herausschneidet, lieferte nie etwas.

Direkter DB-Vergleich (per `psql`, echte Denkstream-Zeilen von `dak+gord-system`) zeigte: der Rohtext enthält ganz klar von Anfang an `GEDANKE: Ich befinde mich an einem leeren Ort...` — die Regex hätte matchen müssen. Test der exakten Regex in einem isolierten `node -e`-Aufruf gegen genau diesen Text: **matcht einwandfrei, 631 Zeichen Ergebnis.** Widerspruch: im Browser leer, isoliert in Node korrekt.

**Auflösung:** `grep` auf die ausgelieferte Datei (`out/surface/flextrawurst_surface.html`) zeigte die tatsächlich an den Browser ausgelieferte Regex:
```
/GEDANKE:s*([sS]*?)(ENTSCHEIDUNG:|BEGR[UÜ]NDUNG:|$)/
```
— aus `\s*` wurde `s*`, aus `[\s\S]*?` wurde `[sS]*?`. Jeder einzelne Backslash vor einem `s` war verschwunden. Root cause: `_erlVerarbeiteDenkstreamChunk` und `_erlZerlegeSaetze` liegen (wie der gesamte SCREENS/Erlebnisschicht-Frontend-Code) innerhalb der riesigen JS-Template-Literal-Rückgabe von `generateGruppenView()` in `build_surface.ts` — eine einzige, ununterbrochene Backtick-Zeichenkette, die von Zeile 8650 bis 10259 reicht (>1600 Zeilen, enthält den kompletten `<script>`-Block der Surface-Seite als literalen Text). Wenn `build_surface.ts` per `tsx` ausgeführt wird, wertet die JS-Engine selbst diese Template-Literal-Zeichenkette aus — und ein einfacher Backslash vor einem nicht-reservierten Zeichen wie `s` ist in JS-String-/Template-Literalen ein historisch gültiges, aber "totes" Escape: der Backslash wird stillschweigend verschluckt, `s` bleibt übrig (kein Syntaxfehler, keine Warnung). Bestätigt durch Gegenprobe: bereits bestehender, seit langem funktionierender Code an derselben Stelle (`tok.replace(/^Bearer\\s+/,'')`) verwendet genau deshalb **doppelte** Backslashes — die äußere Auswertung frisst einen, im ausgelieferten Browser-Code bleibt genau ein `\s` übrig. Ich hatte beim Schreiben der drei neuen Regexes in der vorigen Session diese Konvention übersehen und einfache Backslashes verwendet — dadurch war nicht nur die neue progressive Extraktion, sondern auch die schon vorher genutzte `_erlZerlegeSaetze`-Satzzerlegung und der `endetFertig`-Test von Anfang an lautlos kaputt.

**Fix:** alle drei betroffenen Regexes auf doppelte Backslashes umgestellt (`\s` → `\\s`, `[\s\S]` → `[\\s\\S]`), Build neu erzeugt, in beide Ausgabeorte kopiert (`out/surface/` und `out/process_camera/`), Debug-Instrumentierung wieder entfernt.

**Verifikation, zweistufig:**
1. Node-Simulation der exakten (reparierten) Extraktionslogik gegen einen kompletten, echten aufgezeichneten Denkstream (`stream_id=7a1a78c0…`, 290 Chunks aus der DB) — lieferte korrekt vier vollständige Ich-Stimme-Sätze.
2. Live-Playwright-Test gegen die laufenden Services: Modal für `dak+gord-system` offen gehalten, per direkter DB-Abfrage (`entity_denkstream`) auf den Beginn eines wirklich neuen Denkzyklus gewartet (Live-Tests vorher liefen mehrfach ins Leere, weil zwischen zwei Zyklen bei diesem Wesen Pausen von 3-8 Minuten liegen können — reines Timing-Pech, kein Bug). Ergebnis nach 105s: `'Ich befinde mich in einem ruhigen Zustand auf `wesen.md`.'` erscheint als echtes Ich-Stimme-Popup.

Committed (`8dbf03f41`): `build_surface.ts` + beide gebauten HTML-Ausgaben.

### Was das für die "Rohheit bewahren"-Kritik von weiter oben bedeutet

Der Bug selbst hat nichts mit dem Rohheit-Thema zu tun — aber die Suche danach ist ein Lehrstück dafür, wie leicht ein scheinbar erklärtes Verhalten (progressive Extraktion "behebt" ein Häufigkeits-Problem) einen ECHTEN, tiefer liegenden Fehler verdeckt, wenn man sich mit der ersten plausiblen Erklärung zufriedengibt. Erst der Vergleich zwischen isoliertem Node-Test (funktioniert) und Live-Browser (funktioniert nicht) hat den eigentlichen Bruch sichtbar gemacht.

### Was noch offen ist

Content-aware Fragensteller-Fragen (fragt bisher nur generische Templates, nie etwas das sich auf den tatsächlichen Denkstream-Text bezieht) — von Daniel als konkrete Lücke benannt, noch nicht begonnen. Scroll-Sichtbarkeit (Daniel: noch nie beobachtet, wichtiger als Mausbewegung). Puls/Ring-Glow gekoppelt an echten Denk-Takt. Live-chat-artiges scrollbares Denkfenster-Panel mit natürlichem Pacing (max. 3-4 Sätze pro ≤0,8s) — bisher nur Vision, kein Code.

## Nachtrag — Daniels Auftrag zum großen Umbau: Bestandsaufnahme → Vollsimulation → Selbstangriff → Verbesserung → gezielte Nachsuche, roh

Nachdem ich mich (siehe Konversation davor) selbst korrigiert hatte, dass SCREENS/die Erlebnisschicht nicht "komplett rausgeschmissen und umgedacht" wurde, sondern nur die drei kleinen Bausteine (Maus, Ripple, Ich-Stimme-Bugfix) unter demselben "bauen"-Auftrag gebaut wurden, kam Daniels nächster, wörtlicher Auftrag: *"ich will jetzt dass du alles was wir haben zum umbauen nochmal liest und strukturiert und einmal den bau komplett simulierst dann das ergebnis redteamen und danach die strategie verbessern und dann will ich dass du nochmal zusätzlich alles was wir in dokus haben zusammen mit deinem verbessertem plan ins netz wirft und nach dingen siuchst du uns noch mehr helfen. und dann stehen wir weiter"* — ausdrücklich KEIN Bauauftrag, reine Planung, "dann stehen wir weiter" heißt: danach wieder gemeinsam entscheiden.

### Schritt 0 — vollständig neu gelesen

Alle drei zusammengehörigen Ideen-Dateien vollständig (nicht nur Tail): diese Datei komplett, `wesen_dauerhafte_handlungsfaehigkeit_und_einsichtsnebenscreen.md` komplett (44s-Check-in, billiges Vorlesen, Einsicht-Nebenscreen, selbstorganisierte Vault-Vorhaben — eigenes, größeres Thema, nur als verwandter Kontext mitgedacht, nicht Teil dieser Umbau-Simulation), `dreiergespann_dom_theorie.md` (Grundgesetz-1-Herleitung) und `docs/systemdoku/26_dom_agenten_brainstorm.md` (X-Ray-Overlay als Ur-Idee, die zum Röntgenblick wurde). Dazu den echten aktuellen Code gegengeprüft statt nur aus dem Gedächtnis zu simulieren: `.scv-modal-img-wrap{flex:0 0 68%}`/`.scv-modal-stream{flex:0 0 32%}` (der reale Modal-Split, an dem ein Live-Chat-Panel andocken würde), und `browser_agent.py` Zeile 505-508.

### Echter Fund beim Gegenprüfen, nicht simuliert sondern verifiziert

`scrolle:unten`/`scrolle:oben` rufen nur `page.mouse.wheel(0,600)` bzw. `(0,-600)` auf — **kein** `melde_fokus()`-Aufruf, keine Animation, ein einziger Instant-Sprung. Das erklärt Daniels Beobachtung *"scrollen hab ich noch nie gesehen"* technisch exakt: Scroll passiert (bei den mechanisch aktiven Wesen laut `waehle_mechanische_aktion()` sogar mit 40% Wahrscheinlichkeit pro Tick — `wuerfel<0.75` nach dem 35%-Klick-Zweig), meldet sich aber nirgendwo im Röntgenblick-System. Kein Frontend-Bug — die Aktion selbst ist unsichtbar an der Quelle.

### Bestandsaufnahme, strukturiert

| # | Baustein | Stand |
|---|---|---|
| A | Live-Chat-Denkfenster-Panel (ersetzt/erweitert `.scv-modal-stream`) | nur Vision |
| B | Talker-Reasoner: Mausbewegung | gebaut (`bewege_cursor_natuerlich`) |
| B2 | Talker-Reasoner: Scroll-Animation + Meldung | fehlt komplett (echter Fund, siehe oben) |
| C | rrweb vs. `page.content()`-Schnappschüsse | nie final entschieden |
| D | Puls/Ring-Glow gekoppelt an Denkstream | von "bauen" mit-autorisiert, nicht gebaut |
| E | Content-aware Fragensteller-Fragen | nicht begonnen |
| F | Röntgenblick-Integration (alles zusammen) | Fokus-Events+Ripple gebaut, Scroll fehlt |
| G | Natürliche Bruchstellenerkennung im Denktext | nur Vision |
| H | Tempo-Vorgabe (max. 0,8s/Schub, 3-4 Sätze) | nur Vision |

### Vollsimulation

**Scroll-Fix (B2):** dieselbe Behandlung wie Klick/Tippe — echte kleinschrittige Wheel-Events statt 600px-Sprung, plus `melde_fokus(conn, entity_id, "scrolle", None, None, None)`. Kleinster, klarster Baustein, keine Architektur-Entscheidung nötig.

**rrweb→`page.content()`-Umstieg (C) simuliert:** `page.content()` liefert nur statisches HTML — kein Scroll-Offset, kein Hover, keine laufenden Animationen der Zielseite. Um Scrollen trotzdem sichtbar zu machen, bräuchte es einen separaten Scroll-Offset-Kanal zusätzlich zum ohnehin geplanten Maus-Koordinaten-Kanal — aus "eine Technik ersetzt eine andere" werden beim genauen Simulieren real DREI parallele Datenkanäle (HTML-Snapshot, Maus, Scroll), nicht einer.

**Denkfenster-Live-Chat-Panel (A+G+H) simuliert:** `.scv-modal-stream` wird vom reinen Text-Dump zum wachsenden, scrollbaren Panel. Bruchstellenerkennung zunächst simpel (Absatzwechsel/Label-Wechsel `GEDANKE:`→`ENTSCHEIDUNG:`), Pacing per Timer-Kette mit 0,8s-Deckel. Beim Simulieren fällt auf: das ist strukturell fast identisch mit der schon gebauten Ich-Stimme/Auszug-Extraktion (`_erlVerarbeiteDenkstreamChunk`) — nur die Ausgabe ändert sich (bleibendes Panel statt flüchtiges Popup).

### Selbstangriff (Red-Team)

- **C ist der teuerste, riskanteste Punkt und wurde am wenigsten hinterfragt** — wir haben uns zwischen zwei unvollständigen Optionen (rrweb: Live-Scheduler-Race, siehe der ganze Bugmarathon dieses Tages; `page.content()`: kein Scroll/Hover ohne Zusatzkanäle) festgelegt, ohne eine dritte zu prüfen.
- **Das Live-Chat-Panel (A) dupliziert die schon gebaute Ich-Stimme/Auszug-Infrastruktur fast 1:1** — als eigener neuer Baustein simuliert, entsteht dieselbe Extraktionslogik zweimal.
- **B2 (Scroll-Fix) ist der einzige Punkt mit einem echten, verifizierten Bug dahinter** — alles andere ist Vision/Erweiterung, kein Bugfix.
- **H ("KI behinderter machen", starrer 0,8s-Deckel) widerspricht potenziell Daniels eigenem, unverhandelbarem Live-Gefühl-Prinzip** (*"warum soll ein mensch länger als 3 sekunden auf etwas gotzen das sich nicht ändert"*, weiter oben in dieser Datei) — ein künstlicher Zeit-Deckel würde das Panel genau dann ausbremsen, wenn der Denkstream gerade schnell chunkt. Ein echter innerer Widerspruch im ursprünglichen Wunsch, den ich beim ersten Entwurf nicht benannt hatte.

### Verbesserte Strategie

Scroll-Fix (B2) zuerst und unabhängig vom Rest — echter Bug, sofort baubar, keine Architektur-Entscheidung. Für C: dritte Option prüfen statt zwischen zwei schlechten wählen (siehe Nachsuche unten). A nicht als neuen Baustein, sondern als zweite Ausgabe-Form derselben bestehenden Erlebnisschicht-Extraktion bauen. H präzisieren: Tempo an tatsächliche Chunk-Ankunft koppeln statt an einen starren Timer — löst den Live-Gefühl-Widerspruch auf.

### Gezielte Nachsuche zu C und H/G, mit Quellen

**Zu C — dritte Option, die keiner von uns kannte:** Chrome DevTools Protocol `Page.startScreencast`, wörtlich aus der Recherche: *"Page.startScreencast enables continuous streaming of browser frames, and can be used to build live browser previews, record user sessions, and create product demos. [...] The CDP message Page.startScreencast tells the browser to start sending screencastFrame events for every rendered frame. [...] If you use Puppeteer or Playwright, you already rely on the Chrome DevTools Protocol."* Playwright hat direkten CDP-Zugriff (`page.context().new_cdp_session(page)`). Ergebnis: echte laufende Bild-Frames des tatsächlich gerenderten Zustands — Scroll, Hover, Animation automatisch mit drin, weil es ein Video-Frame-Stream ist, kein Mutations- oder HTML-Nachbau. Sicherheitstechnisch sogar besser als beide bisherigen Optionen: reine Bilddaten, kein einziges fremdes `<script>`-Tag kommt je im Surface-Origin an.

**Zu H/G — natürliche Bruchstellen, wissenschaftlich belegt statt selbst erfunden:** CHI-2026-Paper *"Just-in-Time Tokens: Adaptive Token Pacing for Cognitive-Friendly LLM Streaming"*, wörtlich: *"Tokens are buffered until a readable unit is completed and then released as a coherent chunk; crucially, resource switching is constrained to unit boundaries, so any pauses occur at linguistically meaningful points rather than arbitrary mid-sentence positions. [...] Simple requests are streamed in larger units with minimal pauses for a fast feel, while complex requests are delivered in smaller units with controlled pauses to support step-by-step comprehension."* Das ist die publizierte Bestätigung für "Bruchstellen statt Zeitraster" UND löst den H-Widerspruch aus dem Red-Team direkt auf: demand-aware Pacing statt starrem Deckel.

Quellen:
- [Chrome DevTools Protocol - Page domain](https://chromedevtools.github.io/devtools-protocol/tot/Page/)
- [Use Chrome DevTools to debug your user's browser remotely with BrowserRemote (Kenneth Auchenberg)](https://kenneth.io/post/use-chrome-devtools-to-debug-your-users-browser-remotely-with-browserremote)
- [Screen recording with Playwright - DEV Community](https://dev.to/headlesstesting/screen-recording-with-playwright-5dm0)
- [Just-in-Time Tokens: Adaptive Token Pacing for Cognitive-Friendly LLM Streaming — CHI 2026](https://dl.acm.org/doi/10.1145/3772363.3798936)

### Stand danach

Kein Bauauftrag — wie von Daniel vorgegeben ("dann stehen wir weiter"), Ergebnis präsentiert, wartet auf gemeinsame Entscheidung.

## Nachtrag — "alles ins www werfen", roh missverstanden und richtiggestellt

Direkt im Anschluss, Daniel: *"wir nehmen jetzt alles was du da hast und die ganzen dokus und alles und werfen es inst www"*. Ich habe das zuerst als Veröffentlichungs-Auftrag gelesen (öffentlich posten) und nachgefragt, weil das mit privaten Zitaten/Systemdetails ein echtes Risiko wäre. Klärung per Nachfrage — Umfang: *"Wirklich alles"*. Ziel: *"du sollst es als suche benutzen um noch genialere strategien zu erhalten xD"* — also kein Veröffentlichen, sondern: alles was wir haben (die ganze rohe Vision, nicht nur die technische Zusammenfassung) als Grundlage für eine breitere, tiefere Websuche nutzen, um noch bessere Strategien zu finden. Kein Upload, keine Consent-Frage — reine Recherche-Erweiterung.

### Sechs Suchen, quer durch alle drei Ideen-Dateien (nicht nur SCREENS)

**Treffer 1, der stärkste — Open-LLM-VTuber existiert bereits und macht fast genau unsere Ich-Stimme-Idee:** *"Open-LLM-VTuber displays AI's inner thoughts, allowing you to see AI's expressions, thoughts and actions without them being spoken. [...] The system separates internal processing from vocalized output. [...] Live2D works as an interaction feedback layer where character expressions, motion, touch feedback help users perceive system state — for example, whether the AI is listening, thinking, speaking, or changing mood can be communicated visually."* Neue Idee daraus, die wir noch nicht hatten: Zustand (denkt/hört/spricht/Stimmung) zusätzlich zu Text-Popups auch als **visuelle Kachel-Expression** zeigen (Rahmenfarbe/Glow-Muster je nach `entscheidung`/Denkstream-Zustand) — nicht nur Text, auch Form.

**Treffer 2 — unsere bestehende Architektur entspricht bereits dem Industriestandard für Agent-Observability:** *"Real-time visualization architectures typically comprise three layers: a data-collection layer that captures the agent's interactions as they occur; a streaming layer that filters and routes captured events; and a visualization layer that renders these events to users in real time."* Entity_denkstream/fokus_events = Collection, SSE = Streaming, Popups/Grid = Visualization — schon richtig geschichtet, unabhängig von der C-Frage.

**Treffer 3 — reale Kostenzahlen zur "billig-mechanisch vs. teuer-LLM"-Frage (aus der zweiten Ideen-Datei, dauerhafte Handlungsfähigkeit):** *"The difference between GPT-4o and Gemini Flash for high-volume automation is roughly 285x. [...] Agent-E parses DOM structure directly without vision models, which runs faster but struggles when websites use dynamic dropdowns. [...] For tasks where raw reasoning matters less than reliable execution, routing strategies let you use expensive models only when needed."* Bestätigt Daniels eigene Intuition als Industriestandard, nicht nur Eigenidee.

**Treffer 4 — für die Vault-Selbstorganisation ein direktes Referenzprojekt:** `claude-obsidian` (GitHub, AgriciDaniel) — *"Self-organizing AI second brain for Obsidian [...] Drop any source and Claude reads, links, and files it into one connected knowledge graph of plain Markdown you own."*

**Zwei Suchen ohne echten neuen Ertrag, ehrlich benannt statt erfunden:** "ehrliches Feedback statt Gamification" (Grundgesetz-1-Feedbackprinzip) und "Fragment als eigene Mini-Webseite" (Dreiergespann-Fragment-Ebene) brachten nur generische Microservice-/HCI-Treffer, nichts über unsere eigene Dreiergespann-Theorie hinaus.

### Quellen

- [GitHub - Open-LLM-VTuber/Open-LLM-VTuber](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber)
- [Project Overview | Open LLM Vtuber](http://docs.llmvtuber.com/en/docs/intro/)
- [AI Agent Observability Platforms 2026 — getmaxim.ai](https://www.getmaxim.ai/articles/top-5-ai-agent-observability-platforms-in-2026/)
- [Agentic AI Observability: A 2026 Playbook — arthur.ai](https://www.arthur.ai/column/agentic-ai-observability-playbook-2026)
- [Lyfe Agents: Generative agents for low-cost real-time social interactions (arXiv)](https://arxiv.org/pdf/2310.02172)
- [Best 30+ Open Source Web Agents in 2026 — aimultiple.com](https://aimultiple.com/open-source-web-agents)
- [GitHub - AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)

### Stand danach

Immer noch kein Bauauftrag. Zwei Recherche-Runden (gezielt zu C/H, dann breit über alles) jetzt beide dokumentiert. Wartet auf Daniels Entscheidung, wo es weitergeht.

## Nachtrag — drei Bausteine gebaut+verifiziert+committed, direkt im Anschluss an "gleich direkt bauen"

Daniel: *"ja gut und wir nutzen alles davon und wollen es haben und gleich direkt bauen und umsetzten"* — Umfang geklärt als: Scroll-Fix (echter Bug), Kachel-Zustands-Expression (Open-LLM-VTuber-Fund), IK-Kreatur-Körper-Basis (Vorstufe zur Sieben-Linsen-Idee, siehe `_claude/ideen/sieben_linsen_koerper_kreatur.md`, dort die volle Herleitung).

**Scroll-Fix (`werkraum/welt/browser_agent.py`):** neue `scrolle_natuerlich()` — kleinschrittige Wheel-Bewegung statt 600px-Sprung, plus `melde_fokus(..., "scrolle", ...)`. Verifiziert: `scrollY` 0→400 auf echter scrollbarer Testseite, `entity_fokus_events`-Zeile mit `aktion='scrolle'` korrekt geschrieben (Testzeile danach entfernt).

**Kachel-Zustands-Expression (`build_surface.ts`):** `.scv-card` bekommt Rahmen-Glow je nach `zustand` (dieselben Farben wie der Badge), plus kurzer Puls bei jedem echten Denkstream-Chunk. Live per Playwright bestätigt: `scv-zust-wach` erscheint durch echte Produktionsdaten, nicht nur synthetisch.

**IK-Kreatur-Körper-Basis (`zeige_cursor()`):** ersetzt das simple CSS-Dreieck durch ein Canvas mit 6 prozeduralen IK-Beinen ("follow the leader", angelehnt an Reptile-Interactive-Cursor), Ausschlag/Tempo skaliert mit echter Geschwindigkeit aus `bewege_cursor_natuerlich()`. Verifiziert: Canvas+Engine mit 6 Beinen laufen fehlerfrei, keine JS-Fehler.

Committed: `29cfb1e97` (flextrawurst: Kachel-Expression + Scroll-Erzähler-Text), `f421071de` (werkraum: Scroll-Fix + IK-Körper). Alle 7 browser-agent-Services neu gestartet.

Direkt danach kam die Kraken-Körper-Idee ("mega idee") und daraus die Sieben-Linsen-Idee — beide jetzt in eigener Datei, siehe `_claude/ideen/sieben_linsen_koerper_kreatur.md`.
