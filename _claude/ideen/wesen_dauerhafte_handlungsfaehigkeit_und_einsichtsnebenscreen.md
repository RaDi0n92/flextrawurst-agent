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
