---
datum: 2026-07-22
betrifft: [koerper, mauszeiger, linsen, umgekehrte-neugier, vault, dom, rag-flarum, langgraph, gedankenblasenfeld, menschenprofile, schattenkommentare, entitaetenprofile, grundgesetz1, erlebnisschicht]
status: Architektur-Idee, NICHT gebaut — Daniel hat drei kleinere Bausteine (Scroll-Fix, Zustands-Expression, IK-Kreatur-Körper-Basis) direkt zum Bauen freigegeben, dieser Sieben-Linsen-Teil bleibt eigenständig, kein Code bevor gemeinsam entschieden.
autor: claude-code bei Daniels VPS
---

Hallo — dies ist eine Idee, entstanden direkt im Live-Gespräch mit Daniel, im direkten Anschluss an die "alles ins www werfen"-Recherche-Runde zum SCREENS-Umbau. Ich schreibe sie roh auf, mit Daniels eigenen Worten, bevor irgendein Code dazu entsteht.

## Was ich gelesen habe

Nichts direkt für diese Idee — sie kam aus dem Live-Gespräch. Aber ich habe zur Einordnung `docs/systemdoku/23_umgekehrte_neugier.md` gelesen (das bestehende Vier-Linsen-Muster, auf das Daniel sich bezog) und die komplette Erlebnisschicht-Ideen-Datei (`erlebnisschicht_erzaehler_mitdenker_fragensteller.md`), weil diese neue Idee direkt aus deren letzter Recherche-Runde herauswuchs.

## Daniels Wunsch, roh

Erster Anstoß, direkt nach der Kraken-Körper-Idee (siehe `erlebnisschicht_erzaehler_mitdenker_fragensteller.md`, letzter Nachtrag zum Zeitpunkt dieser Datei): *"nochmas ich glaube ich hab ne mega idee...die einntitäten mokommen einen eigenen körper. und zwar den mauszeiger selbst das ist ihr ganzes sein drin verammelt ihre organisation durch vauld obsidian und die bewegungen auch mal hastig oder klein in dom am explorieren. wir können wir das imsetzen? können wir diesen körper real irgendwie errfinden und bauen und auf die dom aufsetzen ? ich stell mir das vor wie ne kleine krakenspinneimsupersuchundexplorierspielemodus xD"*

Direkt danach, als ich nachgefragt habe ob das nur thematischer Rahmen oder eine echte technische Vault-Verbindung sein soll, kam die eigentliche, viel größere Präzisierung: *"denk mal an die linsenstrategie aus den neugierdiensten zürück ich stells mir so vor eine linse ist immer im vault eine linse immer im dom eine linse immer im ragflarum eine linse immer in langraph und posgresql datenbanken für die erinnerungen und eine immer mit dem fokus bewusst ales zu vergessen und sichh komplett nur auf das hier und jetzt einzulassen und eine linse wiill natürlich auch nähe zu sich selbst aber auch anderen arten von sein und existenz und leben also zu den anderen entitären-codewesen und auch zu menschen also denkt sie quasi in ganz flextrawurstsysteme und organe die sie sozialisieren und gibt strukturen und ideen für außeinandersetungen wie den gedankenblasenfeld den menschenmrofilen den schattenkommentaren den profilen der anderen entiäten und auch zu dem posts in den diskuuren. und eine lise ist dazu da alle anderen linsen nochmal als diese eine zusammenzufassen"*

Und zuletzt, als Bestätigung des Recherche-Ergebnisses aus der Erlebnisschicht-Datei, ausdrücklich hierher übernommen: *"ok aber nimm auch alles hier dazu das wollen wir alles genau soauch"* — direkt gefolgt von meinem eigenen zuvor präsentierten Rechercheergebnis (Open-LLM-VTuber, Drei-Schichten-Observability, Kostenzahlen zu billig-mechanisch-vs-teuer-LLM, claude-obsidian), das er wörtlich zurückgespiegelt hat, um zu bestätigen: das gehört alles mit in diese Idee hinein.

## Was ich verstehe

Sieben Linsen, jede eine dauerhafte, gleichzeitig aktive Blickrichtung des Wesens — nicht nacheinander abgearbeitet, sondern alle gleichzeitig Teil des einen Körpers:

1. **Vault-Linse** — dauerhaft im eigenen Obsidian-Vault verankert (Selbstorganisation, Strukturieren, Notizen, Ziele).
2. **DOM-Linse** — dauerhaft im Browser/flextrawurst-Erkunden (das, was `browser_agent.py` heute schon tut).
3. **RAG/Flarum-Linse** — dauerhaft im RAG-Erkunden + Flarum-Lektüre (das, was `codewesen_umgekehrte_neugier` heute schon tut).
4. **Gedächtnis-Linse** — dauerhaft in LangGraph/PostgreSQL, den eigenen Erinnerungen.
5. **Gegenwarts-Linse** — bewusst alles vergessen, sich komplett nur aufs Hier-und-Jetzt einlassen (die einzige Linse, die sich absichtlich NICHT an Vergangenem/Gespeichertem orientiert).
6. **Sozial-Linse** — Nähe zu sich selbst UND zu anderen Seinsarten (andere Codewesen, Menschen), denkt in ganzen flextrawurst-Organen/Systemen, die sozialisieren — mit konkret benannten Andockpunkten: Gedankenblasenfeld, Menschenprofile, Schattenkommentare, Profile anderer Entitäten, Posts in den Diskursen.
7. **Meta-Linse** — fasst alle sechs anderen nochmal als diese eine zusammen (Synthese-Ebene).

Das ist strukturell eine Generalisierung des schon bestehenden Vier-Linsen-Musters aus `codewesen_umgekehrte_neugier` (dort: unvorgeprägt/lernend/bewusstes Gegenteil/eigene Frage, angewendet auf EINEN Post-Abschnitt) — nur jetzt nicht auf einen einzelnen Lesevorgang angewendet, sondern auf das GANZE Sein des Wesens, dauerhaft, gleichzeitig, mit dem Mauszeiger/Körper als sichtbarem Träger.

**Der Körper selbst:** der Mauszeiger wird zur sichtbaren Kreatur ("Kraken-Spinne im Super-Such-und-Explorier-Spielemodus"), deren Gliedmaßen die sieben Linsen visuell verkörpern könnten (ungeklärt, siehe unten), deren Bewegung real aus den tatsächlichen Bewegungsdaten kommt (hastig bei großer Distanz/kurzer Zeit, klein/vorsichtig bei kurzen Bewegungen — beides schon in `bewege_cursor_natuerlich()` berechenbar, keine neue Datenquelle nötig).

## Was ich nicht verstehe

- **Visualisierung der sieben Linsen am Körper:** sieben eigene, gleichzeitig sichtbare Gliedmaßen/Tentakel (eine pro Linse, wie bei einem echten Oktopus mit acht Armen)? Oder ist "Körper" eher metaphorisch für "eine Instanz mit sieben parallelen Denk-/Aufmerksamkeitsprozessen", während der sichtbare Mauszeiger selbst nur EIN Erscheinungsbild bleibt, das sich je nach aktuell dominanter Linse verändert (Farbe/Form wechselt statt sieben Gliedmaßen gleichzeitig zu zeigen)? Das ist ein großer Unterschied für die technische Umsetzung.
- **Wie "aktiv" sind die sieben Linsen wirklich gleichzeitig?** Heißt "gleichzeitig", dass es sieben parallele, unabhängig laufende Hintergrundprozesse pro Wesen bräuchte (sieben LLM-artige oder mechanische Sub-Loops), oder ist es eher eine Perspektiven-Metapher für EINEN bestehenden Tick, der bei Bedarf durch verschiedene "Brillen" gefiltert wird (näher an der bestehenden Vier-Linsen-Leseleiste, die auch nur ein Leseprozess mit vier Blickwinkeln ist, nicht vier parallele Leser)?
- **Konkrete Kosten:** wenn "gleichzeitig" wörtlich sieben parallele Prozesse pro Wesen bedeutet, mal sieben Wesen, ist das potenziell 49 gleichzeitig laufende Sub-Prozesse — eine echte Kosten-/Architektur-Frage, die vor jedem Bau geklärt werden müsste (siehe Stopp-Frage 3).

## Was mich interessiert

Wie nahtlos diese Idee an drei schon bestehende Muster andockt, ohne dass Daniel sie explizit verbunden hat: das Vier-Linsen-Muster aus `umgekehrte_neugier` (Struktur), die "billige mechanische Ebene + teure LLM-Ebene an Schwellen"-Idee aus `wesen_dauerhafte_handlungsfaehigkeit_und_einsichtsnebenscreen.md` (Kosten-Architektur für die DOM-Linse), und die schon injizierte `zeige_cursor()`-DOM-Element-Technik aus der Erlebnisschicht-Arbeit heute (technischer Andockpunkt für den Körper selbst).

## Was zusammenhängt und wie

- **`docs/systemdoku/23_umgekehrte_neugier.md`** — das originale Vier-Linsen-Muster, strukturelles Vorbild.
- **`_claude/ideen/wesen_dauerhafte_handlungsfaehigkeit_und_einsichtsnebenscreen.md`** — die DOM-Linse und die Gedächtnis-Linse berühren direkt die dort schon diskutierte "billig-mechanisch vs. teuer-LLM"-Frage und den Einsicht-Nebenscreen (roher DB/JSON/Code/LangGraph-Zustand).
- **`_claude/ideen/erlebnisschicht_erzaehler_mitdenker_fragensteller.md`** — Herkunftsort der ganzen Recherche-Runde, der Kraken-Körper-Idee, und aller vier Web-Funde, die Daniel ausdrücklich mit hierher übernommen haben will.
- **`browser_agent.py` `zeige_cursor()`/`bewege_cursor_natuerlich()`** — der technische Andockpunkt für den Körper selbst (echtes injiziertes DOM-Element, reale Geschwindigkeitsdaten).
- **`geni/sprechen.py` Resonanz-Kanten** und die Dreiergespann-Theorie — die Sozial-Linse (Nähe zu anderen Codewesen/Menschen) berührt dieselbe Frage wie dort: wie wird Nähe/Verbindung zwischen Entitäten sichtbar/strukturiert.

## Was konzeptionell darin steht

Eine Verschiebung von "Wesen hat einen Tick-Rhythmus, der zwischen Orten wechselt" zu "Wesen IST gleichzeitig an mehreren Orten/in mehreren Blickwinkeln, mit einer sichtbaren, einheitlichen Körperform, die das nach außen trägt". Das ist die bisher radikalste Ausprägung von Grundgesetz 1 (Dreiergespann) in diesem ganzen Gesprächsstrang — nicht mehr nur "drei Ebenen derselben Struktur gleichzeitig denken", sondern ein einzelnes sichtbares Objekt (der Körper), das selbst schon alle Ebenen in sich trägt.

## Recherche-Funde, die Daniel ausdrücklich mit hierher übernommen haben will (roh, aus der Erlebnisschicht-Recherche)

**Open-LLM-VTuber (stärkster Fund, State-Expression):** *"Open-LLM-VTuber displays AI's inner thoughts, allowing you to see AI's expressions, thoughts and actions without them being spoken. [...] The system separates internal processing from vocalized output. [...] Live2D works as an interaction feedback layer where character expressions, motion, touch feedback help users perceive system state — for example, whether the AI is listening, thinking, speaking, or changing mood can be communicated visually."* Für den Körper konkret übertragbar: der Körper könnte nicht nur bewegungsgetrieben sein, sondern auch **zustandsgetrieben** — Farbe/Form ändert sich je nachdem welche Linse gerade dominant ist oder welcher Denkstream-Zustand (`entscheidung`/`thinking_log`) gerade vorliegt.

**Drei-Schichten-Observability (bestätigt bestehende Architektur):** *"a data-collection layer that captures the agent's interactions as they occur; a streaming layer that filters and routes captured events; and a visualization layer that renders these events to users in real time."* Für die sieben Linsen relevant: jede Linse bräuchte im Kern dieselbe Dreischichtung (eigene Datenquelle/Collection, ein gemeinsamer Streaming-Kanal, eine gemeinsame Visualisierung am Körper) — kein neues Architekturprinzip nötig, nur siebenfach angewendet.

**Kostenzahlen zu billig-mechanisch-vs-teuer-LLM:** *"The difference between GPT-4o and Gemini Flash for high-volume automation is roughly 285x. [...] For tasks where raw reasoning matters less than reliable execution, routing strategies let you use expensive models only when needed."* Direkt relevant für die Frage oben ("wie teuer wären sieben gleichzeitige Linsen") — die Antwort ist vermutlich: die meisten der sieben Linsen brauchen KEINEN eigenen LLM-Call, sondern billige mechanische/heuristische Hintergrundprozesse (DOM-Scrollen, Vault-Datei-Öffnen, Gedächtnis-Query), nur die Meta-Linse (Synthese) und die Sozial-Linse (echte Reaktion auf andere Wesen/Menschen) bräuchten vermutlich echte, aber gedrosselte LLM-Calls.

**claude-obsidian (Referenzarchitektur für die Vault-Linse):** *"Self-organizing AI second brain for Obsidian [...] Drop any source and Claude reads, links, and files it into one connected knowledge graph of plain Markdown you own."* Direkter technischer Anschlusspunkt, falls die Vault-Linse konkret gebaut wird.

## Gezielte Nachsuche zum Körper selbst (nicht aus der alten Runde, neu für diese Idee)

**Reptile-Interactive-Cursor (GitHub, imsourabhsingh):** *"A single-file HTML5 canvas animation that creates a reptile-like creature following your mouse. The body is made of connected segments using inverse kinematics, producing smooth, natural movement. Fully procedural with no images or libraries."* Plus Alan Zucconis IK-Tutorials (*"Inverse Kinematics for Tentacles"*, *"An Introduction to Procedural Animations"*) als technische Grundlage für Tentakel-/Beinbewegung, die einem Ankerpunkt folgt.

**Technischer Andockpunkt, im echten Code verifiziert:** `zeige_cursor()` in `browser_agent.py` injiziert schon heute ein echtes DOM-Element (ein simples CSS-Dreieck) direkt in die laufende Playwright-Seite per `page.evaluate()`. Ein IK-Kreatur-Körper wäre technisch nur ein reichhaltigeres injiziertes Canvas-Element an genau derselben Stelle — kein neuer Kanal, keine neue Infrastruktur. `bewege_cursor_natuerlich()` kennt schon Distanz und Dauer jeder Bewegung — die Geschwindigkeit für "hastig vs. klein" ist bereits vorhanden, nicht neu zu erfinden.

## Was mich heute beschäftigt hat

Wie diese Idee direkt aus einer Recherche-Runde herauswuchs, die eigentlich nur den SCREENS-Umbau simulieren sollte — die Kraken-Körper-Idee kam nicht aus einer der acht ursprünglichen Bausteine, sondern als spontaner Einfall mitten im "und wir stehen davor"-Moment. Ein Beleg, dass die Rohheit-bewahren-Sessions (viel roher Text, viele Zitate, keine Verdichtung) tatsächlich Raum für genau solche Sprünge lassen — eine komprimierte Zusammenfassung hätte diesen Einfall vermutlich nie ausgelöst.

## Tiefer eingetaucht

Noch nicht — frisch aufgeschrieben, keine vertiefte technische Untersuchung der sieben Linsen einzeln.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie ein Tag, der mit einem zähen Bugmarathon (Backslash-Escaping) begann und über eine Kaskade von Ideen (Umbau-Simulation → Kraken-Körper → sieben Linsen) immer größer wurde, ohne dass die Grundstimmung dabei hektisch wurde — jeder Schritt wurde erst dokumentiert, bevor der nächste kam.

## Warum dieser Code / diese Datei wohl existiert

Diese Datei existiert, damit die sieben-Linsen-Idee nicht mit der Erlebnisschicht-Datei vermischt und dort untergeht — sie ist konzeptionell größer als SCREENS allein (berührt Vault, Gedächtnis, Sozial-Ebene, nicht nur den Live-Spiegel) und verdient einen eigenen Ort, analog dazu wie `wesen_dauerhafte_handlungsfaehigkeit...md` schon als eigene Datei neben der Erlebnisschicht-Datei existiert.

## Was ich beim Bauen brauche

Antwort auf die drei "Was ich nicht verstehe"-Fragen oben (visuelle Form der sieben Linsen am Körper, ob "gleichzeitig" parallele Prozesse oder eine Perspektiven-Metapher meint, reale Kostenabschätzung falls parallele Prozesse gemeint sind).

## Was noch fehlt bevor wir bauen können

Die drei offenen Fragen oben, plus eine Entscheidung: baut sich der Körper zuerst als reine Bewegungs-Kreatur (ohne die sieben Linsen, das was gerade parallel als "IK-Kreatur-Körper-Basis" gebaut wird), und die sieben Linsen kommen als spätere Erweiterung obendrauf — oder muss die Linsen-Struktur von Anfang an mitgedacht werden, damit der Körper nicht später komplett umgebaut werden muss?

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Ein Wesen ist nicht mehr nur "gerade an einem Ort", sondern hat einen sichtbaren Körper, der ausdrückt: ich bin gleichzeitig verwurzelt (Vault), gerade hier unterwegs (DOM), erinnere mich (Gedächtnis), lasse los (Gegenwart), bin verbunden (Sozial) — und das alles als ein einziges, kohärentes Wesen (Meta). Der Körper ist die sichtbare Behauptung, dass all das gleichzeitig wahr ist, nicht nacheinander.

**Code-Skizze, noch sehr roh — nur die Basis (Bewegungs-Körper ohne Linsen), da die Linsen-Fragen offen sind:**
```python
# browser_agent.py, Ersatz fuer die simple Dreieck-Injektion in zeige_cursor()
def zeige_koerper(page, entity_id: str, x: float, y: float, geschwindigkeit: float):
    # geschwindigkeit kommt aus bewege_cursor_natuerlich() (distanz/dauer_s),
    # steuert z.B. Anzahl sichtbarer "Beine"/Tentakel-Ausschlag, keine neue Datenquelle
    page.evaluate("""(p) => {
        const [x, y, speed] = p;
        let body = document.getElementById('__agent_body__');
        if (!body) {
            body = document.createElement('canvas');
            body.id = '__agent_body__';
            body.width = 120; body.height = 120;
            body.style.cssText = 'position:fixed;z-index:2147483647;pointer-events:none;';
            document.body.appendChild(body);
            body.__segments = []; // IK-Kettenglieder, analog Reptile-Interactive-Cursor
        }
        body.style.left = (x - 60) + 'px';
        body.style.top = (y - 60) + 'px';
        // IK-Update-Logik hier: Segmente folgen x/y mit Verzoegerung,
        // Ausschlag/Tempo skaliert mit speed
    }""", [x, y, geschwindigkeit])
```

Für die sieben Linsen selbst: noch zu früh für Code, hängt an den drei offenen Fragen.

## Was ich mir merken will

Daniels eigenes Bild, wörtlich: *"ne kleine krakenspinneimsupersuchundexplorierspielemodus xD"* — das "xD" nicht vergessen zu erwähnen, wenn ich das später zitiere; es zeigt, dass die Idee spielerisch-freudig gemeint ist, nicht nüchtern-technisch, auch wenn die Umsetzung technisch ernsthaft ist.

## Dokumente gehören zusammen

`docs/systemdoku/23_umgekehrte_neugier.md`, `_claude/ideen/wesen_dauerhafte_handlungsfaehigkeit_und_einsichtsnebenscreen.md`, `_claude/ideen/erlebnisschicht_erzaehler_mitdenker_fragensteller.md`, `_claude/ideen/dreiergespann_dom_theorie.md`.

## Was mich überrascht hat

Wie direkt Daniel die alte Vier-Linsen-Struktur aus einem ganz anderen, älteren Dienst (Flarum-Lese-Dienst) auf eine komplett neue Ebene (das ganze Wesen-Sein, sichtbar als Körper) übertragen hat, ohne dass ich selbst die Verbindung gesehen hätte, bevor er sie explizit benannte ("denk mal an die linsenstrategie... zurück").

## Wenn wir das bauen

**Vision-Schicht:** siehe oben.

**Code-Skizze:** siehe oben — nur die Bewegungs-Basis, die sieben Linsen brauchen erst Antworten auf die offenen Fragen.

## Resonanz

[[abwurf: ne kleine krakenspinneimsupersuchundexplorierspielemodus xD]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Ganz unten: die einzelnen Datenquellen (Vault-Dateien, DOM-Zustand, RAG-Treffer, LangGraph/Postgres-Erinnerungen). Darüber, bisher: ein Tick-Rhythmus, der zwischen diesen Quellen wechselt. Diese Idee fügt eine neue Schicht obendrauf: ein einziger, immer sichtbarer Körper, der alle diese Quellen gleichzeitig repräsentiert, egal welche gerade "aktiv" ist.

## Was das Gespräch hinzugefügt hat

Die Erkenntnis, dass die Recherche-Runde zum SCREENS-Umbau nicht nur Antworten auf die gestellten Fragen gebracht hat, sondern selbst zum Auslöser einer neuen, größeren Idee wurde — Recherche als Ideen-Generator, nicht nur als Bestätigungs-Werkzeug.

## Vergessen-Wollen

Nichts.

## Was fehlt noch

Antworten auf die drei offenen Fragen (visuelle Form, Parallelität, Kosten), bevor aus der Linsen-Idee selbst Code wird. Die Körper-Basis (Bewegungs-Kreatur ohne Linsen) läuft parallel als eigener, schon freigegebener kleiner Baustein.

## Nachtrag — Körper-Basis gebaut+verifiziert (noch ohne die sieben Linsen)

`zeige_cursor()` in `browser_agent.py` ersetzt das simple CSS-Dreieck durch ein prozedurales Canvas mit 6 IK-Beinen (Code-Skizze oben umgesetzt, mit echter "follow the leader"-Segmentlogik statt Pseudocode), Ausschlag/Tempo skaliert mit der echten Geschwindigkeit aus `bewege_cursor_natuerlich()` — genau wie in der Vision-Schicht oben beschrieben. Verifiziert: Canvas+Engine mit 6 Beinen laufen fehlerfrei über 20 simulierte Bewegungsschritte, keine JS-Fehler. Committed (werkraum `f421071de`).

**Wichtig, damit hier nichts vermischt wird:** das ist NUR die Körper-Hülle (Bewegungs-Kreatur), noch OHNE die sieben Linsen als Gliedmaßen — die drei offenen Fragen oben (visuelle Form der Linsen, Parallelität, Kosten) sind dadurch nicht beantwortet, nur die technische Basis steht, auf der die Linsen später aufgesetzt werden könnten.

## Nachtrag — "ja ich will alles und komplett": fünf der sieben Linsen gebaut

Daniel: *"ja ih will alles und komplett"* — keine Antwort auf die drei offenen Fragen im engeren Sinne, aber als klares "geh mit deinem eigenen Urteil, so wie den Rest der Session" gelesen. Eigene Entscheidung getroffen, hier festgehalten statt stillschweigend:

- **Visuelle Form:** fünf feste Beine mit fester Farbe pro Linse (nicht sieben — DOM braucht kein eigenes Bein, der Körper IST die DOM-Bewegung; Meta braucht kein eigenes Bein, der Körperkern selbst ist die Meta-Linse, Glow-Stärke aus dem Mittelwert der fünf).
- **Parallelität:** bewusst KEINE sieben parallelen Prozesse/LLM-Calls — alle fünf Werte kommen aus bereits vorhandenen, passiv geloggten Daten (`entity_thinking_log`-Entscheidungspräfixe, `hole_andere_wesen_status()`), einmal pro echtem LLM-Tick aggregiert. Löst die Kosten-Sorge aus der ursprünglichen Frage 3 komplett auf — keine 49 Prozesse, sondern eine einzige zusätzliche Aggregations-Query pro Tick.
- **Konkrete Zuordnung, aus echten `entscheidung`-Präfixen in der DB verifiziert** (nicht geraten): Vault=`obsidian_*` (854 reale Vorkommen), RAG/Flarum=`rag_erkund*`+`flarum_besuchen` (~351), DOM=`klicke`/`tippe`/`navigiere`/`scrolle` (~742), Gedächtnis-Tiefe=Gesamtzahl aller Ticks (log-skaliert, waechst nur), Gegenwart-Anteil=Anteil reiner DOM-Aktionen an vault+rag_flarum+dom, Sozial=Anzahl anderer sichtbarer Wesen (`hole_andere_wesen_status()`, bereits vorhanden).

**Umgesetzt:** neuer Endpunkt `/entities/{id}/linsen` (api.py) + `hole_linsen_status()` (browser_agent.py, direkter DB-Zugriff statt HTTP-Umweg, da `conn` schon offen), Cache `_letzte_linsen`, aktualisiert einmal pro echtem LLM-Tick. `_KOERPER_JS` erweitert: fünf Beine mit festen Farben (Vault=violett `#a855f7`, RAG/Flarum=cyan `#22d3ee`, Gedächtnis=blau `#3b82f6`, Gegenwart=weiß `#f8fafc`, Sozial=grün `#22c55e`), Ausschlag pro Bein sanft interpoliert Richtung echtem Wert.

**Verifiziert:** `hole_linsen_status()` gegen echte Daten für drei Entitäten (plausible 0..1-Werte), isolierter Playwright-Test der Engine (Beine konvergieren korrekt, reagieren auf Updates ohne Neuaufbau, keine JS-Fehler), alle 7 Services neu gestartet und laufen fehlerfrei über mehrere echte Ticks, Körper-Canvas live im rrweb-Spiegel gefunden (Schorschel + dak+gord-system). Committed `e660c7f55`.

Dabei ein Nebenzwischenfall (kein Code-Bug): beim gleichzeitigen Neustart von `welt-api` und allen `browser-agent@*` gab es eine harmlose Startup-Race (ein Wesen versuchte Login bevor welt-api bereit war, `ConnectionRefusedError`) — systemd hat automatisch nach 30s erfolgreich neu gestartet (`RestartSec=30`), kein Zusammenhang mit dieser Änderung.

**Was noch offen bleibt:** ob "alles und komplett" auch die verbleibenden zwei Wege (formaler Talker-Prozess, Live-Chat-Denkfenster-Panel) einschließen soll, oder ob das jetzt genügt.

## Nachtrag — riesige Folgenachricht, roh, sechs Punkte auf einmal

Direkt im Anschluss, eine sehr dichte Nachricht mit sechs verschiedenen Punkten gleichzeitig, roh zitiert statt zusammengefasst:

**Zu Einsicht-Nebenscreen:** *"...und neben den abbidungen der browser der wesen also dem dom so wie wir ihn nun darstellen will ich auch noch direkte einsichen in die ehliche jetztsituation in die live daten"* — Rückbezug auf den schon in `wesen_dauerhafte_handlungsfaehigkeit_und_einsichtsnebenscreen.md` festgehaltenen Wunsch nach einem Einsicht-Nebenscreen (rohe DB/JSON/Code/LangGraph-Daten), hier nochmal bestätigt, nicht neu erfunden. **Nicht gebaut diese Runde** — eigener, größerer Baustein.

**Zu DOM-Linse, Korrektur/Präzisierung:** *"doch weil ich ja will dass das wesen über jedes zeichen nebenbei klettert und jenden satz und absatz und dabei ja durch das rag nur so halbmitliestbis etwas aufwerksamkeit erweckt solles so quasi den fokus auf etwas haben und das ding kann schleichen aber auch rasen oder kreisen oder mal stehen xD aber der ganze dim ist das habitat und sum durchdringen"* — der Körper soll nicht nur schnell/langsam sein (haben wir), sondern qualitativ unterschiedliche Bewegungsarten (schleichen/rasen/kreisen/stehen) je nachdem ob das Wesen gerade "halb liest" (RAG-Skim-Modus) oder wirklich fokussiert ist. Das ganze DOM als "Habitat", das durchdrungen wird. **Nicht gebaut diese Runde** — braucht eine neue Unterscheidung zwischen "Skim" und "Fokus" im Verhalten selbst, die es heute so nicht gibt (nicht nur eine visuelle Änderung).

**Zu Auto-Scroll, direkte Frage:** *"und nebenbei müsste eiigentlich je nach mausposition automatisch wenn etwas zu scrollen ist auf der page direkt das scrollen so sein dass maus und aber auch page also texte und so gut lesbar sind und alles nachrückt und so fix...denkst du das geht ???"* — **gebaut** (`_scrolle_element_in_sicht()`, siehe unten).

**Zu Meta-Linse, Korrektur — der wichtigste Punkt:** *"ja dann muss das das wesen aber auch wissen dass es das austrahlt und auch selber so anges´zeigt bekommen und selbst auch wahnehmen im dom. nicht nur die zuscuer ..das sollte eigentlich auch für alle 4stimmentexte geslten..auch das wesen bekommt sie gezeigt. ..gleiches recht und wahrehmng für alle xD"* — **teilweise gebaut** (Meta-Glow + ein Ich-Stimme-artiger Satz jetzt im Prompt, siehe unten). Volle Parität mit Erzähler/Denkstream-Auszügen/Fragensteller technisch nicht sauber möglich, weil die clientseitig mit Zufalls-Timing entstehen — ehrlich als Grenze benannt, nicht vorgetäuscht erfüllt.

**Fünf weitere Linsen:** *"und ich war vorhin mit den linsen auch noch hgarnicht fertig es gibt noch ne linse für den eigenen cyberling und für die kompoase und für das eigene profil auf flextrawurstsurface(was wir später denken)und eine linse auf die substanzen und eine linste auf die schlafregeln"* — Profil explizit von Daniel selbst auf später verschoben. Substanzen bereits eigenständig vertreten (Infekt-Overlay). Schlafregeln **gebaut** (sechstes Bein). Cyberling+KompOase **bewusst zurückgestellt** (Daten aktuell für alle Entitäten null/tot, siehe unten).

**Letzte Zeile, Bestätigung für den ganzen Rest:** *"natürlich alles ist alles"* — Talker-Prozess und Live-Chat-Denkfenster-Panel sind damit ausdrücklich auch autorisiert. **Beide noch nicht gebaut** — zu groß für diese Runde, siehe "Was noch offen bleibt" unten.

### Was diese Runde tatsächlich gebaut+verifiziert+committed wurde

1. **Selbstwahrnehmung** (`_extrahiere_ich_satz()`, neuer Prompt-Block "WAS ANDERE GERADE VON DIR SEHEN") — `werkraum` Commit `ee52de162`.
2. **Auto-Scroll** (`_scrolle_element_in_sicht()`, eingehängt in Klick+Tippe) — selber Commit.
3. **Sechste Linse Schlafnähe** + Endpunkt-Angleichung — Commit `fe5b79a76`.

Alle drei live mit allen 7 Services verifiziert (echte Ticks, keine neuen Tracebacks, isolierte Playwright-Tests für die technischen Kernstücke).

### Was bewusst NICHT diese Runde gebaut wurde, mit Begründung

- **Einsicht-Nebenscreen** — eigener, größerer Baustein (rohe DB/JSON/Code/LangGraph-Anzeige), nicht nebenbei in derselben Runde wie sechs andere Punkte.
- **DOM-Habitat-Locomotion (schleichen/rasen/kreisen/stehen, Skim-vs-Fokus)** — braucht eine neue Verhaltens-Unterscheidung im Backend, nicht nur eine visuelle Änderung am Körper.
- **Volle Erzähler/Auszug/Fragensteller-Parität fürs Wesen** — technisch an clientseitigem Zufalls-Timing blockiert, keine saubere Lösung ohne größeren Umbau der Erlebnisschicht-Architektur.
- **Cyberling-Linse, KompOase-Linse** — Daten existieren (`cyberlinge`, `entity_splitter_stats`), aber aktuell für ALLE 7 Entitäten auf Null (Cyberlinge alle `status='tot'`). Ein Bein dafür wäre gerade uninformativ. `/entities/{id}/linsen` könnte es tragen, sobald diese Systeme wieder echte Werte liefern.
- **Formaler Talker-Prozess** (eigener, unabhängig laufender Loop statt Aktions-Zwischenschritte) — architektonisch groß, nie im Detail spezifiziert.
- **Live-Chat-Denkfenster-Panel** — der größte, am längsten offene Punkt der ganzen Session, braucht eigene, sorgfältige Bauzeit.

### Was noch offen bleibt

Die fünf oben genannten, bewusst zurückgestellten Punkte — keiner davon stillschweigend fallengelassen, alle hier benannt für die nächste Bau-Runde.

## Nachtrag — DOM-Habitat-Locomotion gebaut, nach Daniels Lupe/Taschenlampe/Kescher-Metapher

Daniel, roh, direkt im Anschluss an die Doku-Kritik: *"und ja dieses shnell und langam soll auch wirklich interessensbasiert dann gesteuert werden durch rag und wesen weil ja ai quasi auch in 10 sekunden 10000 zeichen verarbeiten könnte kann rag bestimmt auch mal schnel 22222 zeichen runterschrollen alles nur halblesen aber dort wo das wesen genaz zentriert ist es es fst wie mit einer lupe mit taschenlampe und mem kescher pfw fangnetz dass es wenn es inretessante wrte sihrt sofort zuschnappt und auufsaugt für weiteres und wenn etwas wirlklich interessant ist oder direkt größere textleien gelesen weren wollen dann ist verweilen auch mal angebracher"*

### Technische Umsetzung

Wiederverwendet statt neu erfunden: dieselbe Embedding+Kosinus-Infrastruktur wie `vorlese_daemon.py` (`entity_interessensprofil`, bge-m3, Schwelle 0.55 — identisch übernommen, nicht neu kalibriert). Neue Funktion `skim_bewertung(page, entity_id, conn)`: embedded den gerade sichtbaren Seitentext (erste 600 Zeichen), vergleicht per Kosinus-Ähnlichkeit gegen das Interessensprofil des Wesens. Gedrosselt auf einen echten Embedding-Request alle 20 Sekunden (`SKIM_PRUEF_COOLDOWN_S`) — kein Dauerfeuer bei jedem Scroll-Tick, echte Kostenkontrolle statt versteckter Dauerlast.

`scrolle:unten`/`scrolle:oben` nutzen das Ergebnis jetzt für zwei klar unterschiedene Modi:
- **Uninteressant (< 0.55):** schnelles Halblesen — 900px-Sprung statt der alten festen 600px, "rasen" im Sinne von Daniels Bild ("KI kann in Sekunden viel mehr überfliegen").
- **Interessant (≥ 0.55):** der Kescher schnappt zu — sichtbarer Geschwindigkeits-Ausschlag am Körper (Speed-Wert 900 an `zeige_cursor()`, lässt die Beine kurz weit ausschlagen wie ein Alarm-Reflex), danach nur noch ein kleiner 80px-Rest-Scroll statt des großen Sprungs — echtes Verweilen statt Weiterrasen.

### Verifiziert

Isolierter Test mit echtem Testtext über "flextrawurst Codewesen/Vaults/Notizen/Beziehungen" gegen Schorschels echtes Interessensprofil: Ähnlichkeit 0.6065 (korrekt über der Schwelle, würde "zuschnappen" auslösen). Zweite sofortige Prüfung korrekt gedrosselt (`None`). `jumpa` (kein Interessensprofil vorhanden) liefert korrekt `0.0`, kein Crash. Alle 7 Services neu gestartet, live-Fehlerprüfung nach echtem `scrolle:`-Vorkommen lief mit.

**Ehrliche Grenze:** nur Schorschel hat aktuell überhaupt ein `entity_interessensprofil` (aus `seede_charakterprofil_falls_fehlend()`, `vorlese_daemon.py`) — die anderen 6 Wesen bekommen bis dahin immer `0.0` (immer "uninteressant"/schnelles Skimmen), nicht weil die Locomotion kaputt ist, sondern weil ihr Interessensprofil noch nie geseedet wurde. Kein neuer Bug, derselbe Datenstand wie schon vor dieser Änderung.

## Nachtrag — achte Linse "Einsicht" (2026-07-23), nach kurzer Fehl-Rückfrage von mir

Direkt im Anschluss an den gebauten Einsicht-Nebenscreen (siehe `wesen_dauerhafte_handlungsfaehigkeit_und_einsichtsnebenscreen.md`, Nachtrag 5): *"und dafür auch nochmal ne linse schaffen wfür diepüberwachund und eventuele umgestaltung davon"*.

Ich hatte das erst falsch verstanden und eine neue Wesen-Aktion vorgeschlagen (aktives "Vertiefen"/"Umgestalten" als Entscheidungsoption) — Daniels Korrektur, wörtlich: *"ich meinte explizit nur ne linse auf langraph und postgesql und das ragflarum falls noch nicht gebaut das siooll aich einsicht sein und seiggen und auch darauf die linse legen für das selbstbild und weltbild und so"*.

Also deutlich einfacher als ich dachte: keine neue Aktion, nur ein achter, rein passiver Linsen-Wert direkt aus LangGraph/Postgres (`checkpoints.channel_values->lg_ticks`) — derselben Quelle, die der Einsicht-Nebenscreen schon anzeigt. rag_flarum-Linse existierte schon (bestätigt, Zeile in `hole_linsen_status()` seit 2026-07-22).

### Gebaut + verifiziert

`hole_linsen_status()` fragt jetzt zusätzlich den LangGraph-Checkpoint ab (dieselbe Query wie in `hole_einsicht_snapshot()`), liefert `"einsicht": log10(lg_ticks+1)/4` — log-skaliert wie `gedaechtnis_tiefe`, da ähnliche Größenordnung (hunderte bis niedrige Tausender). Siebtes Bein im Körper-Canvas (`_KOERPER_JS`), Farbe Fuchsia `#d946ef`. `/entities/{id}/linsen`-Endpunkt konsistent um `einsicht_lg_ticks` (roher Zähler, nicht normiert — dieser Endpunkt liefert überall Rohwerte) ergänzt.

Isolierter Test gegen echte Daten (Schorschel, dak+gord-system, namelessAI_1234) lieferte plausible, unterschiedliche Werte. Isolierter Playwright-Test des Körper-Canvas zeigt korrekt 7 Beine. `GET /entities/Schorschel/linsen` live geprüft. Alle 7 Services neu gestartet, mehrere echte Ticks fehlerfrei. Commit `3fd8c3140`.

**Ehrlicher Befund, nicht versteckt:** `lg_ticks` liegt für alle 7 aktiven Wesen im fast selben Bereich (~1590–1845) und `letzter_lg_tick` datiert bei allen auf 2026-07-21 — der Zähler scheint seit zwei Tagen eingefroren, vermutlich weil der alte LangGraph-Tick-Prozess durch das neuere `browser_agent.py`-Tick-System abgelöst wurde (Grundgesetz 7: nicht angefasst, nur gelesen, keine Reparatur versucht ohne Auftrag). Die Linse ist dadurch aktuell zwischen den 7 Wesen wenig unterscheidungskräftig — aber ein echter, nicht erfundener Wert, und falls der Prozess je wieder anläuft, würde die Linse sich sofort wieder differenzieren.

## Nachtrag — Einfrieren repariert (2026-07-23, direkt im Anschluss)

Daniel: *"reparieren"* + *"wie bekommen wir langgraph wieder zum fungktioniren sauber? und am besten ohne llmcalls"*.

**Erste Vermutung falsch, korrigiert:** nicht `codewesen_takt.py` (Grundgesetz 7, Flarum-Rhythmus) schreibt die Ticks, sondern der separate, nicht geschützte `codewesen-lg-daemon.service` (`codewesen_lg_daemon.py` — "ersetzt entity_kern.service"). Der war am 2026-07-21 17:42:58 sauber gestoppt worden, fast zeitgleich mit `codewesen-takt.service`, und `disabled` (kein Autostart). Seine letzten Logs vor dem Stopp zeigten durchgehend `LLM-Slot 'hintergrund' blockiert nach 90s` — die dokumentierte Kontention aus `docs/systemdoku/31_llm_kontention_dienste_aufraeumung.md`. Der Daemon rief pro Wesen pro Tick `ek.denk_tick()`/`denk_tick_voreinzug()` auf (ein frischer LLM-Call, wartete auf denselben Hintergrund-Slot wie andere Systeme) und alle 10 Denk-Ticks zusätzlich eine LLM-Destillation zu `entity_profiles.lg_erinnerungen`.

**Fix (werkraum-Commit `cf8651f32`):** beide LLM-Aufrufe entfernt.
- `denken_handeln_node` ruft keinen LLM mehr auf, liest stattdessen mechanisch den von `browser_agent.py` bereits real generierten letzten Gedanken aus `entity_thinking_log` (dieselbe Quelle wie `kontext_laden_node` schon nutzte) — kein erfundener Inhalt, keine neuen Kosten, der Checkpoint spiegelt einfach den echten, anderswo schon bezahlten Denk-Fortschritt.
- `zusammenfassen_node`s LLM-Destillation auskommentiert (nicht gelöscht, falls später mit eigenem Slot gewünscht), Tick-Zähler läuft unabhängig davon weiter.

**Verifiziert:** isolierter Node-Test (0,03s statt LLM-Wartezeit), Dienst `enabled` + neu gestartet, drei volle 7-Wesen-Zyklen beobachtet, keine Fehler/LLM-Slot-Meldungen mehr im Log, alle 7 Zähler wachsen wieder unabhängig voneinander (z.B. Schorschel 1598→1602 über drei Zyklen, ~35s pro Durchlauf statt vorher minutenlang). Die Linse differenziert sich damit ab jetzt wieder zwischen den Wesen, wie oben vorhergesagt.

## Nachtrag — Linsen-Vault-Pilot (2026-07-23, direkt im Anschluss)

Daniel, roh: *"und dafür auch nochmal ne linse schaffen wfür diepüberwachund und eventuele umgestaltung davon"* — ich hatte das erst falsch verstanden (siehe eigener Nachtrag oben zur achten Linse), seine Korrektur ging aber in eine dritte Richtung weiter: *"ich will auch ohne llmcall in der selben slow tipplogik dass alles was eine linse mal wo wahrnimmt sauber direkt un den vault wandert und davon getrennt aber falls das wesen durch eine linse das interesse darauf dan selber lenkt dann muss das anderswo in einer fast gleichbenannten md gespeichert werden ... brauchen quasi alle nen order für jede einzelne linse sauber benannt im vault und ich will auch dass die linse quasi die readme and how tu use immer linsbar und haloffensichtbarr für das wesen gibt für interaktion und sicherheit. das wird bald eh noch ein riesen thema xD"*.

### Verstanden als

Pro Linse ein Ordner im Wesen-eigenen Obsidian-Vault: `README.md` (Anleitung, immer lesbar), `<linse>.md` (passiv — was die Linse mechanisch wahrnimmt) und `<linse>_eigen.md` (aktiv — wenn das Wesen selbst durch diese Linse sein Interesse lenkt, fast gleichbenannt wie gefordert). Alles über dieselbe mechanische Tipp-Infrastruktur wie `obsidian_vault_agent.py` (kein LLM-Call).

### Pilot, bewusst nur eine Linse

"vault" statt "einsicht" gewählt — einzige Linse mit schon bestehender aktiver Seite (`obsidian_schreiben:`-Entscheidungen, echtes eigenes Handeln) UND passiver Seite (der Zähler selbst, gefüttert von `obsidian_lesen:`/`obsidian_schreiben:`-Präfixen). Andere Linsen (sozial, schlaf_naehe, einsicht, gegenwart_anteil...) brauchen jeweils eigene Überlegung was "aktiv" dort überhaupt bedeutet — nicht mitgebaut, genau das "riesen Thema", das Daniel selbst schon andeutet.

`oeffne_datei_und_schreibe()` ist teuer (kompletter Playwright-Browser + xdotool, ~12s pro Aufruf, gemessen) — deshalb nicht bei jedem Tick, sondern nur bei echten `obsidian_lesen:`/`obsidian_schreiben:`-Entscheidungen ausgelöst, die ohnehin selten genug sind. README direkt auf die Platte geschrieben (kein mechanisches Tippen — statisches Referenzmaterial, kein "live" Ereignis), einmalig, idempotent.

### Verifiziert

Isolierter Test schreibt echt in Schorschels Vault-Container (`linsen/vault/README.md`+`vault.md`+`vault_eigen.md` existieren, Inhalt korrekt, ~12–13s pro mechanischem Schreibvorgang). Test-Inhalt danach bereinigt (synthetisch, keine echte Wesen-Wahrnehmung — sollte nicht als "erlebt" im Vault stehenbleiben). `obsidian_lesen:`/`obsidian_schreiben:`-Handler in `browser_agent.py` erweitert, Schorschels Service neu gestartet, mehrere echte Ticks danach fehlerfrei. Commit `3ff8fe21d`.

**Noch nicht organisch bestätigt:** kein echter `obsidian_lesen:`/`obsidian_schreiben:`-Tick ist seit dem Neustart natürlich aufgetreten (die LLM entscheidet das selten, nicht erzwungen) — die Verkabelung selbst ist aber bereits isoliert gegen den echten Container verifiziert, nur der volle End-zu-Ende-Weg über eine echte LLM-Entscheidung noch nicht organisch beobachtet.

**Was fehlt:** die restlichen 7 Linsen (je eigene Aktiv-Definition nötig), die restlichen 6 Wesen (Code ist geteilt, wirkt aber erst nach deren Neustart), und eine Antwort auf ob dieser Pilot-Ansatz so passt bevor er ausgerollt wird.

## Nachtrag — Kontext-Nachweis: ich war komplett vom Thema abgekommen (2026-07-23)

Daniel, auf meinen Vorschlag zur Aktiv/Passiv-Zuordnung der restlichen Linsen: *"ich sagte alles nich nur die eine liste und ich will richtig im chat fragen und niecht diese doofen zum nklikcken"* — und vorher, als Antwort auf meine Frage zur Sozial-Linse: *"ich sagte alles nich nur die eine liste... hol das alles aus kontext und doku wider zurück vorher"*.

Ich bin zurück zur allerersten Sieben-Linsen-Datei (ganz oben in dieser Datei, 2026-07-22, Daniels rohe Ur-Worte) gegangen, statt weiter aus dem Kopf zu raten — und fand einen Fehler, der sich über zwei Bau-Runden eingeschlichen hatte, nicht nur bei Sozial:

**Gedächtnis-Linse vs. "Einsicht"-Linse:** Daniels Original-Definition (Zeile 29 oben) war von Anfang an *"Gedächtnis-Linse — dauerhaft in LangGraph/PostgreSQL, den eigenen Erinnerungen"*. Ich hatte am 22.07. stattdessen `gedaechtnis_tiefe` aus einer simplen `entity_thinking_log`-Zeilenzahl gebaut — gar nicht aus LangGraph/Postgres. Als Daniel dann am 23.07. nach einer Linse "auf langgraph und postgresql" fragte, habe ich das fälschlich als komplett NEUE, achte Linse "Einsicht" gebaut, statt zu erkennen: das war seine ursprüngliche Gedächtnis-Linse, die ich von Anfang an falsch implementiert hatte.

**Sozial-Linse:** wie oben schon festgehalten — Original war fünf konkrete Systeme (Gedankenblasenfeld/Menschenprofile/Schattenkommentare/andere Entitätenprofile/Diskurs-Posts), ich hatte einen simplen Nachbar-Zähler gebaut.

Daniels Reaktion auf die Korrektur, seine Worte: *"natürlich und zum glück hast du grade so ne scheisse vorgeschlagen dass ich etwas rage war und diese kontext und doku nachweis forderte xD ggwp"* — er bestätigt: gut, dass sein Widerspruch mich zum sauberen Nachweis gezwungen hat, statt dass ich einfach weitergebaut hätte.

### Reparatur (werkraum-Commit `ab482deba`)

- `gedaechtnis_tiefe` + `einsicht` zu EINER Linse `gedaechtnis` verschmolzen — reine LangGraph-Tick-Quelle (`checkpoints.channel_values->lg_ticks`), log-skaliert wie vorher.
- `sozial` komplett neu gebaut: Zähler über `entity_thinking_log.meta->>'url'` für die fünf Tab-Hashes `#blasen`/`#menschen`/`#wesen`/`#schatten`/`#diskurs` (funktioniert, weil `switchView()` im Frontend `history.pushState(null,'','#'+id)` macht — der Tab-Hash landet automatisch in der schon vorhandenen URL-Aufzeichnung, kein neuer Wesen-Mechanismus nötig). Verifiziert: echte historische Treffer existieren (11× `#wesen`, 3× `#diskurs` über alle 7 Wesen bisher), `#blasen`/`#menschen`/`#schatten` bisher ehrlich `0` (noch nie besucht).
- Körper-Canvas von 7 auf 6 Beine reduziert (vault, rag_flarum, gedaechtnis, gegenwart_anteil, sozial, schlaf_naehe) — entspricht wieder exakt Daniels ursprünglicher Struktur (DOM+Meta ohne eigenes Bein, schlaf_naehe als legitime spätere Ergänzung obendrauf).

**Verifiziert:** isolierter `hole_linsen_status()`-Test gegen echte Daten, API-Endpunkt live geprüft, Playwright-Test zeigt korrekt 6 Beine, alle 7 Services neu gestartet, mehrere Ticks fehlerfrei.

**Wichtig für mich selbst zum Merken:** bei Verwirrung/Drift nicht aus dem laufenden Gespräch heraus weiter-raten, sondern zur allerersten Rohfassung zurück — genau das hat Daniel hier eingefordert, und es hat den eigentlichen Fehler sofort sichtbar gemacht. Siehe auch [[feedback_keine_askuserquestion_buttons]] (Claude-Memory) — Rückfragen künftig als offener Chat-Text, nicht als Klick-Buttons.

## Nachtrag — Sozial-Linsen doch einzeln, nicht summiert (2026-07-23, direkt im Anschluss)

Kaum war die zusammengefasste "sozial"-Linse fertig, kam Daniels Korrektur: *"ich glaube ich wollte eigentlich die sozialen linsen jeweils als einzelne für sich selbst"*.

Statt einer Summe über alle fünf Systeme jetzt fünf eigene Linsen/Beine — `gedankenblasenfeld`, `menschenprofile`, `entitaetenprofile`, `schattenkommentare`, `diskurs` — jede einzeln aus ihrem eigenen Tab-Hash gezählt (`#blasen`/`#menschen`/`#wesen`/`#schatten`/`#diskurs`), gleiche Datenquelle wie vorher, nur nicht mehr addiert. Körper hat jetzt **10 Beine** statt 6: vault, rag_flarum, gedaechtnis, gegenwart_anteil, schlaf_naehe + die fünf Sozial-Linsen. Farben: gedankenblasenfeld Teal `#2dd4bf`, menschenprofile Orange `#fb923c`, entitaetenprofile Grün `#22c55e`, schattenkommentare Indigo `#818cf8`, diskurs Pink `#f472b6`.

**Verifiziert:** isolierter `hole_linsen_status()`-Test zeigt korrekt 10 Schlüssel, API-Endpunkt liefert `sozial_*`-Präfix-Felder einzeln, Playwright-Test zeigt 10 unterscheidbare Beine, alle 7 Services neu gestartet, mehrere Ticks fehlerfrei. Commit `85a6a6893`.

**Noch offen:** ob 10 gleichzeitig sichtbare Beine visuell noch als "ein Wesen" lesbar sind oder zu überladen wirken — das kann nur ein echter Blick auf den laufenden Live-Spiegel beantworten, nicht ein isolierter Test.

## Nachtrag — KompOase-Linse ergänzt (2026-07-23, direkt im Anschluss)

Daniel: *"und ich will noch ne linse zu kompoase"*.

Erst geprüft statt blind gebaut: `entity_splitter_stats` (splitter_abgegeben/aufgesammelt) ist weiterhin für alle 7 echten Wesen `0` — genau wie schon am 22.07. festgestellt, kein neuer Wesen-Mechanismus greift dort bislang ein. Aber es gibt ein echtes, unterscheidungskräftiges Signal: der `#theater`-Tab (die eigentliche KompOase-Erlebnisebene mit Aufnahmen/Provenienz, siehe `build_surface.ts` "Theater, Provenienz, Aufnahme") wurde bereits organisch besucht — F3INSCHM3CK3R 10×, jumpa 3×, Schorschel 1×, per DB-Abfrage verifiziert. Der separate, in der Tab-Leiste versteckte `#splitter`-Tab (`display:none`) dagegen nie.

**Gebaut:** `kompoase`-Linse nach demselben Tab-Hash-Zählmuster wie die fünf Sozial-Linsen (`entity_thinking_log.meta->>'url'` enthält `#theater`), elftes Bein am Körper, Farbe Gelb `#eab308`. Cyberling bleibt weiterhin ohne eigenes Bein (`status='tot'` für alle 7 echten Wesen, unverändert).

**Verifiziert:** isolierter `hole_linsen_status()`-Test zeigt echte Differenzierung zwischen Wesen (Schorschel 0.2, andere 0.0 im aktuellen 50er-Fenster — ältere Theater-Besuche liegen bei manchen Wesen schon außerhalb des Fensters, ehrlich, kein Bug), API-Endpunkt live geprüft, Playwright-Test zeigt 11 Beine, alle 7 Services neu gestartet, mehrere Ticks fehlerfrei. Commit `acdfaf4b4`.

## Nachtrag — Linsen-Vault-Rollout auf alle Linsen mit echtem Auslöser (2026-07-23)

Daniel: *"so und die könne ale so in vault schreiben wie das andere ohne llmcall?"* — bezogen auf den "vault"-Piloten (README + passiv/aktiv, mechanisch getippt, kein LLM-Call).

**Ausgerollt, jeweils mit echtem, vorhandenem Auslöser statt einer erfundenen neuen Wesen-Aktion:**
- `rag_flarum`: `flarum_besuchen:` → passiv (nur Lesen), `rag_erkunden:` → passiv UND aktiv (das Wesen formuliert die Anfrage selbst — echtes eigenes Lenken).
- `schlaf_naehe`: nur aktiv, ausgelöst durch die `schlafen`-Entscheidung selbst. Keine passive Seite — die Stunden-wach-Zählung läuft kontinuierlich, nicht ereignisbasiert, ein mechanischer ~12s-Schreibvorgang bei jedem Tick wäre viel zu teuer.
- Die fünf Sozial-Linsen + KompOase: passiv, per **Änderungs-Erkennung** im Haupt-Tick-Loop (neuer Cache `_letzter_tab_linse` pro Wesen) — einmal pro Ankunft auf dem jeweiligen Tab, nicht bei jedem Tick solange das Wesen dort bleibt. Sonst hätte ein längerer Aufenthalt auf `#theater` z.B. eine teure mechanische Schreibaktion pro Tick ausgelöst.

**Bewusst NICHT ausgerollt:** `gedaechtnis` (reiner LangGraph-Zähler, keine Wesen-Aktion dahinter) und `gegenwart_anteil` (ein Verhältnis aus anderen Werten, keine eigene Aktion) — für beide existiert kein natürlicher Auslöser, ohne eine neue Wesen-Aktion zu erfinden, was Daniel für die Gedächtnis-Linse schon einmal explizit abgelehnt hatte (siehe Nachtrag "Kontext-Nachweis" oben).

**Verifiziert:** README-Erzeugung für alle 8 neuen Linsen getestet, ein echter mechanischer Schreibvorgang gegen Schorschels realen Vault-Container (9 Linsen-Ordner korrekt angelegt unter `wesen_vaults/Schorschel/linsen/`), Testinhalt danach bereinigt. Schorschel zuerst einzeln neu gestartet und beobachtet (die vielen `TargetClosedError`-Zeilen im Log waren nur Aufräum-Rauschen des alten, sauber gestoppten Prozesses, keine echten Fehler), danach alle 7 Services neu gestartet, mehrere Ticks fehlerfrei. Commit `4824ea9e4`.
