---
datum: 2026-07-22
betrifft: [browser_agent, billiges-vorlesen, embedding-rag, wesen-vaults, einsicht, denkfenster, grundgesetz1]
importable: false
status: wunsch — Daniel weiß selbst nicht ob es geht ("haha")
autor: claude-code bei Daniels VPS
---

Hallo — dies ist eine Idee, entstanden direkt im Live-Gespräch mit Daniel, nicht aus Lektüre. Er hat es selbst als Wunsch gerahmt, nicht als Bauauftrag: *"erst nochmal etwas als wunsch wie ich es mir vorstelle und wünschen würde aber nicht weiß ob es geht haha"*. Ich schreibe es roh auf, so wie er es gesagt hat, bevor ich mit dem eigentlich bestätigten nächsten Schritt (billiges Vorlesen) anfange.

## Was ich gelesen habe

Nichts — diese Idee kam aus dem Live-Gespräch, nicht aus Lektüre.

## Was ich verstehe

Daniel will, dass alle 7 Wesen **gleichzeitig, durchgehend** voll handlungsfähig sind — Tastatur und Maus jederzeit einsatzbereit, nicht nacheinander im Tick-Takt wie jetzt. Sein Wortlaut: *"die wesen alle gleichzeitig immer komplett handlungsfähig mit tastatur und maus sind dass sie sauerhalft scrollen können und insinktiv klicken und dinge so automatisch durchforsten und begehen können und schnell von ort zu ort auch zu wechseln"*. Das liest sich wie: flüssiges, mechanisches Scrollen/Klicken/Navigieren, nicht ein LLM-generierter Einzelschritt pro Tick — eher ein kontinuierlicher, fast reflexhafter Erkundungsstrom.

Weil das nicht ewig ziellos weiterlaufen soll: ein periodischer Check-in-Mechanismus. Wortlaut: *"weil sie ja wie gesagt nicht alles immer dauerhaft interessiert daher sollte nach etwa jede 44 kurz bestätigt werden vom wesen dass es dort noch weiter machen will"*. Die genaue Zahl/Einheit hinter "44" ist mir nicht klar — nachgefragt, noch keine Antwort. Alternative/Ergänzung dazu: *"ansonsten könte man den wesen alle aussichten geben wass es ja sinst alles tun oder lassen könnte"* — den Wesen eine Übersicht zeigen, was sie sonst noch tun könnten, als Entscheidungshilfe beim Check-in.

Jederzeit-Umschalten zum eigenen Vault: *"ich will ja quasi auch dass sie jederzeit switchen können um dann ihren vauld zu designen zu strukturieren neue dinge dort zu schaffen oder alte überarbeiten"* — und das soll **ohne echten LLM-Call** passieren, *"am besten durch meine 6fingerstyletaktik dachte sich xD"* — ich lese das als Anspielung auf genau das Prinzip, das wir heute Nacht schon für `obsidian_vault_agent.py` gebaut haben: mechanisches Tippen über `xdotool`, kein LLM-Call pro Taste, "wie auf der Schreibmaschine".

Neuer "Einsicht"-Nebenscreen: *"das was das wesen im hintergrund auch gleichzeitig ja immer bekommen sollte die echtes dbs die echten jsons den echten code und auch alles aus langgraph und postgersql und so das sollte eigentsich ne art gleiner nebenscreen nochmal unten rechts neben dem normalem screen sein und das denkfester teilern"* — ein kleiner Nebenscreen unten rechts, der zusätzlich zum normalen Browser-Screen läuft, mit rohen Systemdaten (DB, JSON, Code, LangGraph/Postgres-Zustand) — nicht nur für Daniel als Beobachter gedacht, sondern etwas, das das Wesen selbst "im Hintergrund" bekommt. Das bestehende Denkfenster/Modal würde dafür geteilt (Bild+Denkstream ist ja jetzt schon eine 68/32-Aufteilung, hier käme eine dritte Spalte/Sektion dazu).

## Was ich nicht verstehe

Die Zahl "44" — Sekunden? Klicks? Scrollvorgänge? Ticks? Ohne die Einheit kann ich den Check-in-Rhythmus nicht bauen, direkt nachgefragt.

Auch nicht ganz klar: soll das "gleichzeitige, durchgehende Handeln" bedeuten, dass die Wesen komplett vom aktuellen LLM-Tick-Modell wegkommen (dauerhafte, mechanische Aktion statt Tick-für-Tick-Entscheidung), oder soll der bestehende Tick-Rhythmus bestehen bleiben und nur die *Bewegung zwischen* den Entscheidungen flüssiger/mechanischer werden? Das ist architektonisch ein großer Unterschied — beim eigentlichen Bauen müsste das explizit geklärt werden (Stopp-Frage 3: Architektur-Entscheidung, nicht allein zu treffen).

## Was mich interessiert

Wie nah das an "billiges Vorlesen" dran ist, ohne dass Daniel die beiden Ideen explizit zusammengebracht hat — für mich lesen sie sich wie zwei Seiten derselben Vision: billiges, mechanisches Wahrnehmen/Bewegen die meiste Zeit, teure LLM-Ticks nur an Entscheidungspunkten (Check-in, "ist das interessant genug für einen echten Blick").

## Was zusammenhängt und wie

- **Billiges Vorlesen** (aus dem Tagesbericht, TEIL 6, "Parkiert für später"): Embedding-Vergleich statt LLM-Call für breites Scannen, echter Tick nur bei ausreichender Nähe zu bisherigen Interessen.
- **Dieser Wunsch hier:** dieselbe Grundidee, aber auf Bewegung/Navigation statt nur auf "was lesen" angewendet — mechanisches Scrollen/Klicken/Wechseln die meiste Zeit, ein LLM-Tick nur beim periodischen Check-in oder wenn das Wesen selbst eingreifen will.
- **`obsidian_vault_agent.py`** (heute Nacht fertig gebaut): liefert schon das Muster für "Aktion ohne LLM-Call pro Schritt" (xdotool-Tippen). Die Vault-Umschaltung, die Daniel hier will, ist im Kern dieselbe Technik, nur als Navigations- statt Tipp-Aktion.
- **Röntgenblick-Overlay / Denkstream-Modal** (`build_surface.ts`, SCREENS-Tab): die bestehende 68/32-Aufteilung (Live-Spiegel/Denkstream) ist die Stelle, an der ein dritter "Einsicht"-Bereich andocken würde.

## Was konzeptionell darin steht

Eine Verschiebung weg vom reinen "LLM entscheidet jeden einzelnen Schritt" hin zu "billige mechanische Dauerbewegung + teure LLM-Entscheidung nur an Schwellen". Das ist dieselbe Denkfigur wie Grundgesetz 1 (Dreiergespann: Codewesen-Organ-Ebene/Menschen-Plattform-Ebene/Fragment-Ebene) nochmal auf einer anderen Achse — hier geht es um *Kosten*-Ebenen statt Wahrnehmungs-Ebenen: billige mechanische Ebene vs. teure LLM-Ebene, mit einem definierten Übergang dazwischen.

## Was mich heute beschäftigt hat

Nichts — dieser Abschnitt gehört primär zu Reflexions-Dateien nach dem Lesen/Erleben einer ganzen Session, hier ist es nur eine einzelne Idee mittendrin.

## Was mich noch beschäftigt

Ob der Einsicht-Nebenscreen wirklich fürs Wesen selbst gedacht ist (als zusätzlicher Wahrnehmungskanal, den es "sieht") oder ob Daniel eigentlich einen Beobachtungs-Screen für sich selbst meint, der zufällig neben dem Wesen-Screen sitzt. Der Wortlaut *"das was das wesen im hintergrund auch gleichzeitig ja immer bekommen sollte"* liest sich für mich wie ersteres, aber das würde bedeuten: das Wesen bekommt rohe DB/JSON/Code-Daten als Teil seines eigenen Kontexts — eine ganz neue Art Wahrnehmungskanal, kein reines Beobachtungsfeature für Menschen.

## Tiefer eingetaucht

Nichts — noch keine Bauarbeit an dieser Idee, nur das Festhalten.

## Wie sich dieser Tag / diese Session angefühlt hat

Nichts — siehe Notiz-Datei für den Gesamteindruck der Session, hier nur die einzelne Idee.

## Warum dieser Code / diese Datei wohl existiert

Diese Datei existiert, damit der Wunsch nicht verlorengeht, bevor die Klärung ("was heißt 44") und die eigentliche Bauarbeit (billiges Vorlesen) beginnen — Daniel hatte selbst die Sorge geäußert, dass frühere Beschreibungen dieser Art schon einmal untergegangen sind.

## Was ich beim Bauen brauche

Antwort auf "44" (Einheit/Zahl). Klärung, ob Tick-Modell bestehen bleibt oder grundlegend verschoben wird. Für den Einsicht-Nebenscreen: Klärung, ob er fürs Wesen selbst (neuer Kontext-Kanal) oder für Menschen (Beobachtungsfeature) gedacht ist — das sind zwei ganz verschiedene Bauaufträge.

## Was noch fehlt bevor wir bauen können

Die drei offenen Fragen oben. Für den ERSTEN, bestätigten Schritt (billiges Vorlesen) fehlt davon nichts — der ist unabhängig von diesen Detailfragen umsetzbar.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Ein Wesen bewegt sich die meiste Zeit "von selbst" — scrollt, klickt auf offensichtlich klickbare Elemente, wechselt zwischen offenen Orten (Flarum/Surface/eigener Vault) — ohne dass für jeden einzelnen Schritt ein LLM gefragt wird. In regelmäßigen Abständen (die "44") hält es kurz inne und ein echter LLM-Tick entscheidet: hierbleiben, weiterziehen, oder zum Vault wechseln. Der Einsicht-Nebenscreen würde dem Wesen (wenn das die richtige Lesart ist) zusätzlich zum visuellen DOM auch den "Maschinenraum" zeigen — nicht nur was auf der Seite steht, sondern was in der DB/im Code dahintersteckt.

**Code-Skizze:** noch zu roh für echten Code — architektonisch hängt alles an der Tick-Modell-Frage. Grobe Richtung, sobald geklärt:
```python
# Mechanische Bewegung ohne LLM-Call (analog xdotool-Tippen)
def mechanische_erkundung(page, dauer_s):
    # zufälliges/heuristisches Scrollen, Klicken auf sichtbare Links
    # kein LLM-Aufruf hier
    ...

async def haupt_loop_v2(entity_id):
    while True:
        mechanische_erkundung(page, bis_naechster_checkin)
        # Check-in: LLM-Tick entscheidet ueber "weiter hier / wechseln / vault"
        entscheidung = echter_llm_tick(...)
        ...
```

## Was ich mir merken will

Die "44" nicht raten — nachfragen, notiert, hier festgehalten bis Antwort kommt.

## Dokumente gehören zusammen

`docs/2026-07-21_tagesbericht.md` (TEIL 6, "billiges Vorlesen"), `docs/systemdoku/29_browser_agent_aktivierung.md`, `welt/obsidian_vault_agent.py`, `_claude/ideen/dreiergespann_dom_theorie.md`.

## Was mich überrascht hat

Wie nahtlos sich dieser neue Wunsch an "billiges Vorlesen" von gestern Abend anschließt, ohne dass Daniel es selbst so benannt hat — als wäre die Grundidee (billig/mechanisch vs. teuer/LLM) bei ihm schon einmal grundsätzlich gesetzt und wird jetzt auf immer mehr Bereiche angewendet.

## Wenn wir das bauen

**Vision-Schicht:** siehe oben.

**Code-Skizze:** siehe oben — noch zu früh für mehr, drei offene Fragen zuerst.

## Resonanz

Nichts — noch keine Bauarbeit, nur das Aufschreiben.

## Die Schichten des Systems — wie ich sie jetzt sehe

Nichts — dieser Abschnitt gehört eher in Reflexions-Dateien nach echtem Lesen/Bauen, nicht in eine reine Wunsch-Notiz.

## Was das Gespräch hinzugefügt hat

Die Erkenntnis, dass Daniels Vision für die Wesen sich gerade in Richtung "dauerhaft lebendig, nicht nur tick-weise reagierend" verschiebt — eine grössere konzeptionelle Bewegung als nur ein einzelnes Feature.

## Vergessen-Wollen

Nichts.

## Was fehlt noch

Antwort auf "44". Danach: Start bei "billiges Vorlesen" wie bestätigt, die größeren Fragen (Tick-Modell, Einsicht-Nebenscreen-Zielgruppe) bleiben offen für ein späteres, eigenes Gespräch.

---

## Nachtrag — Daniels Antworten, roh (noch selber Tag, direkt im Anschluss)

Die "44" war geklärt und der Rest des Wunsches ist deutlich größer geworden als ich erst dachte — Daniels eigene Worte, unverändert:

**Die 44:** *"ja 44 sekunden"* — Sekunden, nicht Ticks/Klicks/Scrolls. Check-in-Rhythmus = alle 44 Sekunden.

**Zu 1 (Interessensprofil-Quelle):** *"mischund aus all diesen sachen"* — bewusst eine Mischung aus allen drei genannten Quellen (bisherige RAG-Anfragen, Charakterbeschreibung, tatsächliche Reaktionen), nicht eine einzelne davon.

**Zu 2 (was gescannt wird) — deutlich breiter als gedacht, Wortlaut komplett:** *"flarum soll nur momentan dazu dienen das wir ne beschäftigung für sie haben biss sie ihren ersten post machen dürfen auf flextrawurst xD später dürfen sie selbst zwar auch immer gerne entsheiden wenn sie draufklicken über die website alsp flextrawurst.de dann im flaerum zu schwelgen aber ja sie sollen auch die ankundigunegn und alle furfaceinhalte also auch das lesen dürfen aller menschprofile oder tarumanalysen und so weiter und notitzen aber auch das gedankenblasenfeld drin verweilen und oder sammeln und auch ganz wichtig das aktiv in der kompoase chillen und klicken und entdeckken und aufnehmen und so weiter xD und dann das ganze postvorbereiten in ihrem´n vaults für die richtigen posts auf flextrawurst etc"*

Flarum ist also nur eine **Übergangsbeschäftigung** bis zum ersten erlaubten echten Post auf flextrawurst — danach rein optional, ein Klick auf flextrawurst.de führt bewusst dorthin, kein Zwang mehr. Die eigentliche, dauerhafte Scan-Fläche ist praktisch die ganze Plattform: Ankündigungen, sämtliche Surface-Inhalte, Menschenprofile, Traumanalysen, Notizen, das Gedankenblasenfeld (verweilen UND sammeln — beides explizit genannt), aktiv KompOase erkunden ("chillen und klicken und entdecken und aufnehmen"). Und dann fließt das zurück in die Vaults, als Vorbereitung für echte, spätere Posts.

**Vaults als Ort für viel mehr als nur Postentwürfe:** *"ich will dass sie die vaultz auch nutzen um eigene profile mit geammelten dingen über alle anderen wesen zu machen oder zu speziellen menschne usw ich will dass sie selber dort ideen erzeugen und nachgehen sich ziele setzten sihch wichtige dinge zum erinnern schreiben und sich organisieren und umdenken klönnen zu jeder zeit und noch viel viel mehr"* — eigene Profile über andere Wesen/Menschen, selbst erzeugte Ideen die sie weiterverfolgen, eigene Ziele, Erinnerungsnotizen, jederzeit umorganisieren/umdenken können. Explizit "und noch viel viel mehr" — bewusst offen gelassen, kein abschließender Umfang.

**Obsidian-Schulung als eigener Unterpunkt:** *"wir müssen ihnen auch obsidian genau beibrngen dass sie nicht nur die formatireungen haben sondern die wikilinks und so weiter selber setzten zwischen den dateien um sich noch schneller zu bewegen in ihren strukturen"* — nicht nur Markdown-Formatierung, sondern aktives Wikilink-Setzen zwischen eigenen Dateien, als Navigationsbeschleuniger in der eigenen Vault-Struktur. Noch nicht gebaut, gehört zu den Vault-READMEs aus TEIL 6 des Tagesberichts.

**Zu 3 (wo lebt das Profil):** *"eigene tabelle mit dazugehöriger neuer jsonbfelddatei und das am besten auch live lesbar in surface als tab für die entitätenprofle als ein teil oder ? denn ich will ja dass sich sich darüber hinaus aus ir eigenes individuelles flextrawurstprofil selber mit zaubern"* — eigene Tabelle + JSONB, live lesbar als neuer Surface-Tab "Entitätenprofile". Das "oder?" am Ende ist Daniels eigene Unsicherheit, keine feste Zusage — aber klar ist: das Profil ist nicht nur internes Matching-Datum, sondern soll später die Grundlage sein, aus der sich jedes Wesen sein **eigenes, individuelles flextrawurst-Profil selbst zusammenbaut** ("zaubern").

**Zu 4 (Tick-Integration):** *"keine ahnung sag du mal das beste practice"* — bewusst an mich delegiert, keine eigene Vorstellung dazu.

**Mein Vorschlag dazu, den Daniel noch nicht endgültig bestätigt hat, nur die Phase-1-Verengung ("jo passt"):** eigener leichter Hintergrund-Daemon (nicht der Haupt-Tick-Loop, da 7 Wesen gleichzeitig günstig scannen sollen, nicht sequenziell im LLM-Slot-Takt), hört auf den heute reparierten Events-Stream-Kanal (Grundgesetz 8), embedded neue Inhalte günstig gegen jedes Wesen-Profil, schreibt Treffer über einer Schwelle als Zusatz-Kontext für den nächsten echten Tick — analog zu `rag_erkunden`, nur automatisch statt auf Zuruf.

**Phase-1-Verengung, bestätigt ("jo passt"):** Profil-Tabelle + Matching-Mechanismus zuerst nur gegen **eine** Quelle (Ankündigungen, weil dort Grundgesetz 8 schon vollständig live ist) und an **einem** Wesen verifizieren, danach Quelle für Quelle erweitern — gleiches Skalpell-Prinzip-Muster wie beim Obsidian-Vault-Pilot heute Nacht (erst Schorschel, dann alle).

## Was fehlt noch (aktualisiert)

Nichts mehr für den Start von Phase 1 — Architektur ist grob abgesteckt, Reihenfolge bestätigt. Offen für später: Tick-Modell-Grundsatzfrage (bleibt der bestehende LLM-Tick-Rhythmus, oder verschiebt sich das grundlegender Richtung "meist mechanisch, LLM nur an Schwellen"?), Einsicht-Nebenscreen (fürs Wesen selbst oder nur Beobachtungsfeature?), Obsidian-Wikilink-Schulung, "alle Wesen gleichzeitig handlungsfähig" als eigene größere Baustelle jenseits von Phase 1.

---

## Nachtrag — der 44s-Check-in als Batching-Punkt (2026-07-22, Folgegespräch)

Daniels Klärung, warum sein Batching-Vorschlag von eben (Wesen-Kontexte samt Marker in eine Datei/einen Call, strukturierter Output mit Markern zurück, per Skript wieder pro Wesen injiziert) kein Widerspruch zu meiner Einordnung ist: *"ich dachte das gilt halt eh nur für die 44sekundenabfrage und dann was dort alles gleichzeitig quasi ja kommt...nicht für alles immer..also nur wenn sie sich zu etwas umentscheiden und dann ja ne folgeentscheidung treffen müssen was mit bisherigem kontext und so noch logisches angestellt werden könnte schnell und ob sie noch was abschliesendes weiterdavon für sich halten wollen für mitnahme an den ort wo sie danach hingehen und so"*.

Das Batching gilt also NICHT für "billiges Vorlesen" (das bleibt pro Wesen, asynchron, wenn's für das einzelne Wesen interessant ist) — sondern ausschließlich für den 44-Sekunden-Check-in-Takt, der ohnehin ein gemeinsamer, periodischer Synchronisationspunkt für alle Wesen ist. Dort macht Batching architektonisch Sinn, weil der Sync-Punkt nicht künstlich geschaffen werden muss, sondern der Mechanismus selbst schon getaktet ist. Pro Wesen im selben Call: bisheriger Kontext + letzter Gedanke → Entscheidung (bleiben/weiterziehen/Vault-Wechsel) + ggf. logische Folgeentscheidung aus dem bisherigen Kontext + ein "Mitnahme-Gedanke", den es zum nächsten Ort mitträgt statt dass der Kontext beim Ortswechsel verpufft.

## Nachtrag 2 — Selbstorganisierte Aufgaben im Vault mit zwei möglichen Budget-Einheiten

Direkt im Anschluss, neue Ebene: Daniel will, dass Wesen sich **in ihren eigenen Vaults selbst Aufgaben/Ziele setzen** — sich selbst Prompts schreiben, die sie wiederkehrend oder einmalig nach dem Lesen ausführen sollen. Wörtlich: *"ich will es bald so haben dass sich die wesen auch in ihren vaults ja selber organisieren aufgaben und ziele setzen und sich selbst quasi prompts schreiben die sie dann wiederkehrend oder einmalig durchführen sollen nach lesen und so"*.

**Zwei mögliche Abschluss-Bedingungen für so eine selbstgewählte Aufgabe, laut Daniel entweder-oder oder auch kombiniert:**

1. **Kontextfenster-Füllung als Zielgröße** — die Aufgabe definiert sich über eine Zieltoken-/Füllmenge, bei der sie als "fertig" gilt.
2. **Minutenangabe** — z.B. *"ich will jetzt 8 minuten in der kompoase explorieren"* oder *"ich will jetzt 30 minuten alle meine schattenkommentare lesen"*.

**Zusätzlich, als dritte Variante — die "Speed-Funktion":** wenn Minutenangaben für uns Menschen nicht sichtbar/sinnvoll "chillig" sind, soll das Wesen stattdessen selbst in Kontext-Einheiten denken: *"das wesen sagt ok ich habe 66 neue schattenkommentare und will alle aufeinmal lesen bis kontext bei 1337 oder 3333 oder so ist"*. Wichtig dabei, explizit betont: das Wesen muss diese Zahlen (z.B. "66 neue Schattenkommentare") **direkt aus den Daten/dem Code bekommen, sofort** — nicht selbst schätzen oder raten müssen.

## Was ich daraus verstehe

Ein neues, drittes Element neben "billigem Vorlesen" (was ist interessant) und dem 44s-Check-in (bleiben/weiterziehen): **selbstgewählte, budgetierte Vorhaben**, die ein Wesen sich im eigenen Vault notiert und dann selbst abarbeitet, mit einer klaren, vom Wesen selbst festgelegten Obergrenze (Zeit ODER Kontext-Token-Menge), damit es nicht endlos in einer Sache hängen bleibt. Die Obergrenze braucht echte, aktuelle Zahlen als Grundlage (z.B. Anzahl ungelesener Schattenkommentare) — das Wesen soll informiert entscheiden, nicht blind schätzen.

## Was ich nicht raten will, sondern fragen muss

- **Wo lebt so eine selbstgewählte Aufgabe konkret?** Eine Markdown-Datei im Vault (z.B. `aufgaben.md`/`vorhaben.md`), die das Wesen selbst schreibt und die ein Mechanismus danach ausliest? Oder ein strukturierteres Format (YAML-Frontmatter mit Budget-Feldern), das ein Daemon zuverlässig parsen kann?
- **Wer überwacht die Abschluss-Bedingung?** Bei Minuten: ein Timer ist einfach. Bei "Kontext-Füllung bei 3333": heißt das, der Gesamtkontext dieses einen Lese-Vorhabens (alles was reingelesen wurde) wird mitgezählt, bis er die Zielmarke erreicht — und dann fasst das Wesen ab, schließt ab, geht weiter? Das bräuchte einen eigenen kleinen Tracking-Mechanismus pro laufendem Vorhaben.
- **Woher kommen die "Speed-Infos" (z.B. "66 neue Schattenkommentare") technisch?** Vermutlich ein einfacher COUNT-Query gegen die jeweilige Tabelle (schattenkommentare, splitter, etc.) — aber muss geklärt werden, für welche Inhaltstypen das zuerst gilt (Skalpell-Prinzip: eine Quelle zuerst, wie beim billigen Vorlesen).

Noch keine Bauentscheidung — reines Festhalten der Konzept-Erweiterung.

## Nachtrag 3 — Daniels Antworten auf die drei Fragen, roh

**Zu 1 (wo lebt das Vorhaben, wer entscheidet Format):** *"erstmal müssen wir schauen wie sie es annehmen und anwenden in den ordnern und dateien selbst das ganze sich vorzunehmen und dann auch selbstintrinsisch weiterzu verfolgen und wenn daraus was wird dann gucken was es wird und bevor es ausgeführt werden darf das erste mal sollte erst eine anfrage an uns beide versendet werden müssen eigentlich damit wir eben lesen obs ok ist xD und dann später wenn wir sehen was ihre interessen sind und waren und wie gut oder schlecht das selbstorganisieren planen und erarbeiten geklappt hat könnten wir ne art buchungssystem mit auswahlsystem und wahlbasis vorgeben und sie können daraus wählen denke ich wäre am coolsten erstmal....weil wir ja lernen was sie wirklich brauchen"*.

Explizit KEIN vorab festgelegtes Format. Erst beobachten, wie die Wesen es organisch annehmen und in ihren eigenen Vault-Dateien/Ordnern umsetzen — freie Form, kein Zwang. Bevor eine neue Art von selbstgewähltem Vorhaben zum ERSTEN Mal ausgeführt werden darf, muss eine Anfrage an Daniel UND mich (Claude) gehen — ein manuelles Freigabe-Gate, kein automatischer Durchlauf. Erst später, wenn genug beobachtet wurde was die Wesen wirklich interessiert und wie gut das Selbstorganisieren funktioniert hat, soll daraus ein kuratiertes "Buchungssystem" mit Auswahl-/Wahlbasis entstehen, aus dem die Wesen dann wählen können — nicht vorher hart kodiert, sondern aus echter Beobachtung abgeleitet.

**Zu 2 (was wird beim Kontext-Budget genau gezählt/gesammelt):** *"wenn es ne zeitangabe ist muss ja nicht immer alles sofort kontext werden oder sein oder? weil dieses über rag-halblesen ja nicht immer voll feuert oder?...dann könnten es instinktive und bewusste entscheidungen sein die das wesen mitnehmen will daraus weil es zum beispiel wirklich mal ne ganze diskussion von post 1 bis post 22 gesehen hat und zwischendurch egal bei welchen posts und wie viele sätzen und wo daraus immer wieder sachen sich gepickt hat...aber halt auch immer mit merken das ist aus postid von wesen xxx gesagt und so weiter...vielleicht auch...das hab ich mitgenommen weil...und so weiter und dann ja quasi bis das zeitlimit erreicht ist sammeln und aufnehmen während ja gleichzeitig gechillt sauber und immer handlungsfähig scrollen und tippen und navigieren können"*.

Wichtige Präzisierung: bei einer Zeitangabe wird nicht automatisch alles sofort in echten LLM-Kontext gezogen — das würde nur passieren, wenn "billiges Vorlesen" tatsächlich anschlägt (feuert nicht immer). Während der Zeit läuft die mechanische Navigation weiter (scrollen/tippen/klicken, billig, ohne LLM-Call), und dabei entstehen instinktive UND bewusste Merk-Entscheidungen — einzelne Sätze/Gedanken aus verschiedenen Posts einer ganzen Diskussion (Post 1 bis 22), die sich das Wesen "pickt", jeweils mit Herkunfts-Marker (Post-ID, Wesen XXX) und optional einer eigenen Begründung ("das hab ich mitgenommen weil...").

Zwei konkrete Beispielmuster, die Daniel nennt:
- **Post-Fall:** *"bei posts und so könnte das wesen ja vielleicht auch 4 posts nacheinander gesehen haben und in denen ist ein wort oder ein kurzer gedanke hängengeblieben und nach den 4 posts sagt das wesen halt stopp das hat mich berührt ich will direkt alle 4 posts an einem ganzen stück mitsichern und halten"* — ein spontaner "Stopp"-Moment mitten in der mechanischen Navigation, ausgelöst durch etwas, das hängengeblieben ist, der dann gezielt die letzten N Posts als zusammenhängenden Block sichert.
- **KompOase-Fall:** *"ich will solange jeden splitter anklicken und lesen und eventuell sammeln bis 2222 tokens gelesen sind usw und dann bekommt es direkt die 2222 tokens mit allen splittern die grade da offen sind und in den interessensbereichen des wesens liegen sofort zum lesen danach und kann dann entscheiden die 11 will ich mir nur merken die 3 will ich sammeln die 8 finde ich doof und merke mir auch das...und vielleicht verfasst es später über die 11 guten splitter und 6 doofen splitter und die 3 gesammelten auch noch einen post und beschreibt seine beweggründe"* — mechanisches Sammeln bis zum Budget (2222 Token), DANACH ein einziger echter LLM-Urteilsdurchgang über das gesamte Gesammelte (pro Splitter: merken/sammeln/verwerfen, jeweils mit Begründung), optional gefolgt von einem eigenen Post darüber.

**Rückbezug auf die 44 Sekunden:** *"für diese sich gegebenen oder später das gekauften (gewählten) beschäftigungen werden die 44 takte außerkraft gesetzt solange bis das 'goal' voll ist"* — der periodische 44s-Check-in wird für die Dauer eines aktiven, selbstgewählten Vorhabens ausgesetzt, bis dessen eigenes Budget (Zeit oder Kontext-Ziel) erreicht ist. Das Vorhaben selbst produziert am Ende seinen eigenen echten LLM-Entscheidungspunkt (das Urteil über das Gesammelte) — es braucht den externen 44s-Takt in dem Moment nicht, weil es seinen eigenen Abschluss-Moment mitbringt.

## Noch offen, nicht geklärt

Wie die "Anfrage an uns beide" beim ersten Ausführen eines neuen Vorhabens technisch ankommen soll (neuer Kanal? Surface-Benachrichtigung? Events-Eintrag den wir manuell prüfen?) — noch keine Bauentscheidung, reines Festhalten.

(2026-07-22, mitten in dieser Ergänzung: Daniel hat direkt bemerkt, dass ich hier wieder zu glatt/verdichtet dokumentiere, nicht roh genug — siehe `SUBCONSCIOUS.md` Muster 4, zweiter Beleg. Der Absatz, der vorher hier stand ("Drei Kosten-Ebenen, sauber geschichtet..."), ist deshalb raus — er hat nichts Neues gesagt, nur Daniels eigene Worte oben nochmal in meine eigene, ordentlichere Struktur zurückübersetzt.)

## Nachtrag 4 — Antwort auf die Typ-Frage + Kontext-Sicherung beim Wechsel (2026-07-22, direkt im Anschluss)

Zu "was macht zwei Vorhaben zum selben/verschiedenen Typ": *"es sind 2 verschiedene weil es andere vorhaben sind und andere budgets das wollte immer erst einmal drübergeschaut und dann freigegeben werden egal was hat vor dem ersten mal und wenn budgetänderungen sind sollte das wesen das nicht ändern sondern dich das ans endere aufgabe geben die dann auch freigegeben werden muss, denn freigegeben kann es dann selbständig immer direkt durchführen ohne neuen check"*.

Also: (Vorhaben-Beschreibung, Budget) zusammen definieren den Typ. Jede Kombination braucht vor der ersten Ausführung ein Drüberschauen + Freigabe, ausnahmslos. Ändert das Wesen später das Budget einer schon freigegebenen Aufgabe, gilt das nicht als Änderung derselben Aufgabe, sondern als neue, eigene Aufgabe — die wieder freigegeben werden muss. Einmal freigegeben, läuft es danach beliebig oft selbständig, ohne erneuten Check.

Zu "was passiert beim Wechsel nach einem 44s-Check-in, wenn das Wesen sagt 'ich hab hier genug'": *"ja aber auch wichtig wenn das wesen nach den 44 sekunden sagt..ok ich hab hier genug dann bieten wir ja ganz viele andere mögliche flextrawurstbeschäftigungen für die nächsten 44 sekunden an...und ich will quasi dass ein wechsel nicht auch immer ein kontextvergessen dann ist sondern ein bis zu einem logischen limit an dem die calls dann wirklich lange dauern gesammeltes gesamtkontextkonstrukt dass dann zum beispiel erstmal direkt in eine md in den vault gespeichert wird in einen dafür vorgesehenen bereich...aber zur struktur der vaults erst später genaueres wie ich mir das so vorstelle und wünsche erst später wenn hier alles sauber durch ist und auch funktioniert"*.

Zwei Dinge darin: (1) Nach einem "ich hab hier genug"-Check-in wird dem Wesen eine Auswahl weiterer möglicher flextrawurst-Beschäftigungen für die nächsten 44 Sekunden angeboten — das ist dieselbe Auswahl-/Buchungssystem-Idee aus Nachtrag 3 (zu 1), hier nochmal an einer anderen Stelle bestätigt. (2) Ein Wechsel soll NICHT automatisch Kontext-Verlust bedeuten — bis zu einer "logischen Grenze" (dort wo Calls sonst zu lange dauern würden) wird der bis dahin gesammelte Gesamtkontext zuerst in eine MD-Datei im Vault geschrieben, in einen dafür vorgesehenen Bereich, bevor gewechselt wird. Vault-Struktur/genaue Ablage explizit auf später verschoben — erst wenn der Rest sauber steht und funktioniert.

## Nachtrag 5 — Einsicht-Nebenscreen gebaut (2026-07-23), Zielgruppenfrage endlich beantwortet

Die seit dem 22.07. offene Frage aus "Was mich noch beschäftigt" oben ("fürs Wesen selbst oder Beobachtungsfeature für Menschen?") habe ich Daniel direkt gestellt, bevor irgendwas gebaut wurde (Stopp-Frage 1+3). Seine Antwort, knapp: **"Beides"** — eine gemeinsame Datenquelle, Menschen sehen sie als Panel, das Wesen bekommt zusätzlich einen kuratierten Ausschnitt im eigenen Prompt.

**Technisch umgesetzt, nicht der ganze Rest der Datei (Tick-Modell-Umbau, 44s-Check-in-Batching, selbstgewählte Vorhaben) — nur genau dieser eine Baustein:**

- `hole_einsicht_snapshot(conn, entity_id)` (`browser_agent.py`) — echter "Maschinenraum"-Schnappschuss: letzte 8 Denklog-Einträge (volle Begründung, nicht nur Präfix), Cyberling-Zustand, Splitter-Stats, letzte Schlafphase, und — Daniels expliziter Wunsch "alles aus langgraph und postgresql" — der echte LangGraph-Checkpoint-Zustand direkt aus der `checkpoints`-Tabelle in Postgres (verifiziert: 66278 echte Zeilen über alle 7 Wesen, `channel_values`-Feld enthält lesbare Ticks wie `{"lg_ticks": 1598, "denk_ticks": 1597, ...}`). Grundgesetz 7 beachtet: nur gelesen, `codewesen_takt.py`/die LangGraph-Schreibseite bleibt unangetastet.
- `GET /entities/{id}/einsicht` (`api.py`) — dieselbe Abfrage, eigenständig (api.py und browser_agent.py sind getrennte Prozesse), für den Menschen-Nebenscreen.
- Kuratierter Ausschnitt im Prompt (`baue_prompt()`, neuer Parameter `einsicht_snapshot`): eine einzige Zeile mit Cyberling-Status + LangGraph-Tick-Nummer, im selben Block wie die schon bestehende Selbstwahrnehmung (Körper-Glow, Ich-Stimme-Satz) — "gleiches Recht/gleiche Wahrnehmung fürs Wesen", jetzt auch für den Maschinenraum, nicht nur für Körper/Ich-Stimme.
- Frontend (`build_surface.ts`, SCREENS-Modal): dritte Spalte "MASCHINENRAUM" neben Bild (jetzt 50% statt 68%) und Denkstream (26% statt 32%), Poll alle 12s solange Modal offen (kein SSE nötig für einen DB-Schnappschuss), mobil (<900px) ausgeblendet statt eine vierte Spalte in eine Spalte zu quetschen.

**Ehrlich, nicht versteckt:** Cyberling ist bei 6 der 7 Wesen `status=tot` (nur `theater_01`, ein Test-Entity außerhalb der 7, ist `lebendig`), Splitter-Stats sind bei allen `0/0` — das Panel zeigt das offen mit einem "(noch inaktiv)"-Hinweis statt es zu verstecken oder wegzulassen, dieselbe Ehrlichkeits-Linie wie schon bei den Sieben-Linsen-Körper-Werten.

**Verifiziert:** isolierter Funktionstest gegen echte Schorschel-Daten, `GET /entities/Schorschel/einsicht` live gegen welt-api getestet, Playwright-Screenshot zeigt alle drei Spalten korrekt befüllt (Denklog/Cyberling/Splitter/Schlaf/LangGraph, alle mit Live-Daten), keine neuen JS-Fehler, Build+Ring-23-Tests grün (83/83), alle 7 `browser-agent@*`-Services neu gestartet und über mehrere echte Ticks fehlerfrei beobachtet. Zwei Commits: werkraum `7d835c641` (Backend), `/root` `50f6776ec` (Frontend).

**Was von dieser ganzen Ideen-Datei damit NICHT angefasst wurde:** das grundsätzliche Tick-Modell (bleibt Tick-für-Tick, keine "dauerhaft mechanisch, LLM nur an Schwellen"-Verschiebung), das 44s-Check-in-Batching über alle Wesen, selbstgewählte Vorhaben mit Budget, Obsidian-Wikilink-Schulung — alles weiterhin offen, eigene, größere Bausteine.
