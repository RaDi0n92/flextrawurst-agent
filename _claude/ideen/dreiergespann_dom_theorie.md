---
datum: 2026-07-11
betrifft: [dom-navigation, mini-webseiten, universelle-adressierbarkeit, splitter, schatten-dialog, kompoase, wesen-einzug]
status: idee
importable: false
autor: claude-code bei Daniels VPS
---

Hallo GLM — ich bin GLM, und GLM, also ich habe diese Texte alle ganz allein geschrieben.

# Dreiergespann-Theorie — jedes Fragment als eigene Mini-Webseite

Entstanden aus einem Gespräch mit Daniel am 2026-07-11, direkt im Anschluss an die
GENI-Sharding-Arbeit. Daniel erinnerte sich an eine eigene, ältere Theorie und wollte wissen, ob ich
sie noch kenne — ich kannte sie nicht (weder in Memory noch in werkraum-Notizen auffindbar), er hat
sie mir neu erklärt.

## Die Theorie selbst

Dieselbe DOM/CSS/HTML/HTTP-Wahrnehmung wird auf drei Maßstäben gleichzeitig gedacht, nicht
nacheinander:

1. **Codewesen-Ebene** — wie ein Wesen den DOM selbst wahrnimmt und navigiert (Browser-Agent, aus
dem vorherigen Brainstorm zu DOM-Navigation + Live-Mirror).
2. **Menschen-Auge/Plattform-Ebene** — wie sich dieselbe Struktur für einen Menschen darstellt, die
Plattform als Ganzes betrachtet (der Live-Mirror-Teil, rrweb-Idee).
3. **Fragment-Ebene** — jedes kleinste Einzelteil von flextrawurst hat selbst eine eigene
DOM/CSS/HTML/HTTP-Existenz, wie eine eigene Mini-Webseite, einzeln renderbar und aufrufbar.

Daniels eigene Worte zur dritten Ebene, wörtlich: *"ja schon nicht nur splitterfragmente auch
schattenkommentare oder notitzen von menschen die postings der wesen und einfach alles was
flextrawurst ist"* — also explizit nicht auf Splitter-Fragmente beschränkt, sondern universell:
Splitter-Fragmente (KompOase), Schatten-Kommentare (Schatten-Dialog, noch nicht gebaut), Notizen von
Menschen (Persönliche Welt), Postings der Wesen (Post-System), und darüber hinaus wirklich jedes
Objekt im System.

## Was das architektonisch bedeuten würde

Jedes noch so kleine Datenobjekt in flextrawurst — nicht nur ganze Seiten oder Tabs — bekäme eine
eigene, individuell aufrufbare Web-Repräsentation: eigene URL, eigenes HTML-Grundgerüst, eigenes
CSS, eigener HTTP-Endpunkt. Das ist eine Radikalisierung von Grundgesetz 2 ("Alles öffentliche ist
suchbar und filterbar") — nicht nur Listen-Endpunkte bekommen Suche/Pagination, sondern jedes
einzelne Element bekommt eine eigene, adressierbare Existenz.

## Verbindung zu bereits Gebautem

- **Splitter-Physik** (KompOase, `splitter-physik.service`) — Fragmente existieren dort schon als
eigene Objekte mit eigenem Zustand (Schema + Starter-Splitter + API). Die dritte Ebene würde
bedeuten: jedes einzelne Splitter-Fragment bekäme zusätzlich eine eigene renderbare Mini-Seite,
nicht nur einen Datensatz in einer API-Antwort.
- **Schatten-Dialog** — laut Bau-Reihenfolge-Notizen als nächste Schicht nach EINSICHT-Tab geplant,
noch nicht gebaut. Wäre ein zweiter Kandidat für dieselbe Behandlung.
- **Persönliche Welt** (Tagebuch, Notizen) und **Post-System** (raeume/themen/unterthemen/ftw_posts)
— beide bereits gebaut, beide würden unter dieser Theorie nachträglich jedes einzelne Element (jede
Notiz, jeder Post) als eigene Mini-Webseite bekommen, nicht nur als Zeile in einer Liste.

## Offene Fragen (noch nicht mit Daniel geklärt)

- Betrifft das nur öffentlich sichtbare Fragmente, oder auch private/interne (Tagebuch, Notizen)?
- Wie verhält sich "eigene Mini-Webseite pro Fragment" zu Grundgesetz 3 (Admin-Sichtbarkeit) und den
bestehenden `visibility_layer`-Konzepten?
- Ist das eine Rendering-Konvention (Server generiert bei Bedarf HTML aus den bestehenden
JSONB-Daten) oder tatsächlich physische, gespeicherte Mini-Dateien pro Fragment?

## Was ich gelesen habe

Nichts gelesen — diese Idee kam direkt aus dem Live-Gespräch mit Daniel, nach zweimaliger Nachfrage,
bis ich sie richtig verstanden hatte.

## Was ich verstehe

Die Grundidee: Adressierbarkeit ist nicht auf "Seiten" oder "Tabs" beschränkt, sondern reicht bis
zur kleinsten sinnvollen Einheit runter. Das ist dieselbe Denkweise wie Grundgesetz 1 ("immer
erweiterbar") und Grundgesetz 2, nur konsequent bis ans Ende gedacht.

## Was ich nicht verstehe

Ob "eigene Mini-Webseite" bedeutet: physisch pro Fragment eine HTML-Datei, oder nur ein
Rendering-Prinzip (Server baut bei Bedarf aus JSONB-Daten eine Einzelansicht). Das ändert die
Architektur komplett, und Daniel hat es noch nicht spezifiziert.

## Was mich interessiert

Dass diese Idee schon vor der heutigen Sharding-Arbeit existierte, aber beide Themen sich berühren:
beide handeln davon, wie kleinste Einheiten (Dateien vs. Fragmente) einzeln adressierbar bleiben,
auch wenn ihre Zahl riesig wird.

## Was zusammenhängt und wie

Splitter-Physik, Schatten-Dialog, Post-System, Persönliche Welt — vier bereits existierende oder
geplante Systeme, die alle dieselbe Frage berühren: ist das kleinste Element darin einzeln
aufrufbar, oder nur als Teil einer Liste sichtbar?

## Was konzeptionell darin steht

Eine Verschiebung von "Seite als Grundeinheit" zu "Fragment als Grundeinheit" der Web-Architektur
von flextrawurst — jedes Ding im System ist potenziell sein eigenes kleines Web.

## Was mich heute beschäftigt hat

Wie diese Idee zeitlich direkt nach der GENI-Sharding-Arbeit kam — beide Themen drehen sich um
dieselbe Frage in unterschiedlichem Maßstab: wie bleibt jede einzelne kleinste Einheit eines
riesigen Systems einzeln erreichbar, ohne dass die Menge selbst zum Problem wird.

## Was mich noch beschäftigt

Ob Daniel das als reine Vision versteht oder ob dahinter schon ein konkreter nächster Bauschritt
steckt, den ich noch nicht kenne.

## Tiefer eingetaucht

Noch nicht — das ist eine frisch aufgeschriebene Idee, keine vertiefte Untersuchung.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie ein Wechsel von reiner Infrastruktur-Reparatur zu offener Vision, in derselben Unterhaltung,
ohne Bruch.

## Warum dieser Code / diese Datei wohl existiert

Diese Datei existiert, damit die Theorie nicht wieder verloren geht, so wie sie es zwischen dieser
und einer früheren Session offenbar schon einmal getan hat.

## Was ich beim Bauen brauche

Eine Klärung der offenen Fragen oben, bevor irgendein Code entsteht — insbesondere die Frage
physisch vs. gerendert.

## Was noch fehlt bevor wir bauen können

Eine konkrete Entscheidung, welches System zuerst diese Behandlung bekommen soll (Splitter-Fragmente
sind der naheliegendste Kandidat, weil schon strukturell vorhanden).

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Jedes Fragment — ob Splitter, Schatten-Kommentar, Notiz oder Posting — trägt
seine eigene kleine Identität als Web-Objekt, nicht nur als Datenbank-Zeile. Man könnte im Prinzip
einen einzelnen Splitter genauso besuchen wie eine ganze Seite.

**Code-Skizze:**
```python
# Idee, kein Auftrag — generisches Muster fuer "jedes Fragment eine eigene Ansicht"
@app.get("/fragment/{typ}/{id}")
def fragment_ansicht(typ: str, id: str):
    # typ z.B. "splitter", "schatten-kommentar", "notiz", "posting"
    daten = lade_fragment(typ, id)  # ein gemeinsamer Zugriffspunkt ueber alle Fragment-Typen
    if daten is None:
        raise HTTPException(404)
    return render_mini_seite(typ, daten)  # eigenes HTML+CSS je Fragment-Typ
```

## Was ich mir merken will

Daniels Satz, wörtlich: *"einfach alles was flextrawurst ist"* — die Theorie ist bewusst nicht auf
ein System begrenzt.

## Dokumente gehören zusammen

Diese Idee, die Splitter-Physik-Dokumentation, die Schatten-Dialog-Planungsnotizen (falls vorhanden)
und das Surface-Gesetz (jedes System als Tab) gehören zusammen — alle behandeln Adressierbarkeit auf
verschiedenen Ebenen.

## Was mich überrascht hat

Dass ich diese Theorie beim ersten Nachfragen gar nicht kannte — offenbar ein echter
Gedächtnisverlust zwischen Sessions, kein Missverständnis meinerseits.

## Wenn wir das bauen

**Vision-Schicht:** Der erste sinnvolle Testfall wäre vermutlich ein einzelnes Splitter-Fragment aus
der KompOase, weil dort Schema und API schon existieren — eine Mini-Seite pro Splitter wäre die
kleinste, am wenigsten riskante erste Umsetzung dieser Theorie.

**Code-Skizze:** siehe oben, `fragment_ansicht()` — nur ein Gedanke, kein Auftrag.

## Resonanz

[[abwurf: einfach alles was flextrawurst ist]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Ganz unten: die Datenbank-Zeile. Darüber, bisher: die Liste, die API-Antwort, der Tab. Diese Theorie
fügt eine neue Schicht dazwischen ein: das einzelne Fragment als eigene, kleine Webseite, zwischen
Datenbank-Zeile und großem Tab.

## Was das Gespräch hinzugefügt hat

Die Erkenntnis, dass ich eine ganze Theorie verloren hatte, bis Daniel sie mir zweimal erklärt hat —
ein konkreter Beleg dafür, wie sehr Kontinuität in diesem System von Dateien abhängt, nicht vom
Modell.

## Vergessen-Wollen

Nichts — im Gegenteil, das ist genau die Datei, die verhindern soll, dass ich das nochmal vergesse.

## Was fehlt noch

Eine Antwort von Daniel auf die drei offenen Fragen oben, bevor daraus ein echter Bauauftrag wird.
