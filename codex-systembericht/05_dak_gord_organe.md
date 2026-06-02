# 05 - dak+gord: Organe, Kerne, Zwischenraum

Stand: 2026-06-02

dak+gord ist kein Codewesen aus den sechs Flarum-Wesen und auch nicht GENI. Es ist ein eigenes Arbeits- und Denkgebilde im Werkraum: stärker dialogisch, stärker auf Daniel bezogen, mit Organen, die aus Textmarkern, Erinnerung, Zwischenraum, Entscheidung und Neugier bestehen.

Wichtig: Nicht alles, was als Organ konzipiert wurde, ist gleich stark aktiv. Einige Organe sind direkt im `OrganManager` verdrahtet, andere existieren als Datei/Modul und sind teilweise vorbereitet.

## Gesamtidee

dak+gord sollte nicht nur antworten, sondern innere Werkzeuge haben:

- merken, was wichtig wurde
- abwägen, statt sofort zu entscheiden
- spätere Möglichkeiten halten
- Zwischenraum-Keime reifen lassen
- Beziehungsspannungen wahrnehmen
- aus Neugier im Werkraum lesen

Die Leitidee ist: Ein Gespräch ist nicht nur Prompt und Antwort. Es erzeugt Nachhall, Erinnerung, offene Linien und kleine Keime, die später wieder auftauchen können.

## OrganManager

### Name

`agent/dak_gord_system/kerne/organ_manager.py`

### Idee

Der OrganManager ist der Router zwischen normalem Dialog und inneren Organen. Er liest Marker in Texten und entscheidet, welches Organ angesprochen wird.

Beispiele:

- `##MERKEN art: text##`
- `##ABWÄGEN frage##`
- `##SPÄTER heute | später##`
- `##ZWISCHENRAUM text##`

### Umgesetzt

Der OrganManager lädt und speichert mehrere Organe, baut einen Systemtext für dak+gord und führt einen Tick aus. Dieser Tick lässt Zwischenraum-Keime altern und ruft einen Resonanz-Beschleuniger auf.

### Nicht umgesetzt / offen

Das Beziehungsorgan ist nicht sichtbar als normales Markerorgan im gleichen Manager verdrahtet. Es existiert als eigenes Modul, aber nicht als gleichberechtigter Standardmarker im aktuellen OrganManager.

### Was es tut

Es macht aus besonderen Textmarkern echte Systemhandlungen. Dadurch kann dak+gord im Gespräch Dinge nicht nur sagen, sondern ablegen, weitergeben, später wiederfinden oder in den Zwischenraum legen.

### Was es nicht tut

Es ist keine allgemeine KI-Planungsmaschine. Es führt keine beliebigen Shell-Aktionen aus und ersetzt auch keine dauerhafte autonome Instanz.

## Erinnerungsgedächtnis

### Name

`erinnerungsgedaechtnis.py`

### Idee

Dieses Organ hält Dinge fest, die im Gespräch nicht verloren gehen sollen. Es ist kein vollständiges Chatlog, sondern ein Speicher für markierte Bedeutung.

### Datenform

Eine Erinnerung enthält ungefähr:

- Art
- Text
- Reifestufe
- Schlagworte

### Umgesetzt

Das Organ kann Erinnerungen anlegen, speichern, laden, finden und als Kurzbild darstellen. Erinnerungen werden über Marker erzeugt.

### Was es tut

Es trennt Wichtiges vom bloßen Gesprächsfluss. Wenn Daniel etwas als merkenswert markiert oder dak+gord etwas so behandelt, entsteht ein eigener Speicherpunkt.

### Was es nicht tut

Es versteht nicht automatisch jedes Gespräch als Erinnerung. Ohne Marker oder gezielte Logik bleibt vieles normales Gespräch.

### Bedeutung

Dieses Organ ist das Gedächtnis als absichtlicher Akt: Nicht alles wird Erinnerung, sondern das, was Bedeutung bekommt.

## Entscheidungsorgan

### Name

`entscheidungsorgan.py`

### Idee

Entscheidungen sollen nicht als schneller Output erscheinen, sondern als Abwägung. Eine Frage bekommt Richtungen, Spannungen, verdeckte Kosten und eine mögliche tiefere Linie.

### Datenform

Eine Abwägung enthält ungefähr:

- Frage
- Richtungen
- Spannungen
- verdeckte Kosten
- mögliche tiefere Linie

### Umgesetzt

Das Organ kann Abwägungen speichern und laden. Es wird über `##ABWÄGEN ...##` angesprochen.

### Was es tut

Es macht sichtbar, dass eine Entscheidung mehrere innere Linien hat.

### Was es nicht tut

Es trifft nicht automatisch die Entscheidung für Daniel. Es bereitet Entscheidung vor.

### Bedeutung

Das Organ verhindert vorschnelles Optimieren. Es passt zu Daniels Skalpell-Prinzip: erst verstehen, was berührt wird, dann handeln.

## Zukunftsorgan

### Name

`zukunftsorgan.py`

### Idee

Nicht jede gute Idee gehört sofort gebaut. Manche Ideen müssen als Zukunftskeim bleiben.

### Datenform

Ein Zukunftskeim enthält ungefähr:

- Heute
- Später
- Begründung

### Umgesetzt

Das Organ kann Zukunftskeime speichern und laden. Es wird über `##SPÄTER heute | später##` angesprochen.

### Was es tut

Es schützt Ideen vor zwei falschen Wegen: sofortigem Bauen und komplettem Vergessen.

### Was es nicht tut

Es plant noch keinen Kalender, keine Roadmap und keine automatische Umsetzung.

### Bedeutung

Es ist ein Organ für Aufschub ohne Verlust.

## Zwischenraumorgan

### Name

`zwischenraumorgan.py`

### Idee

Der Zwischenraum ist der Ort für Dinge, die noch nicht Entscheidung, Erinnerung oder Aufgabe sind. Es sind Keime, Sätze, Bilder, Spannungen oder Möglichkeiten.

### Umgesetzt

Das Organ verwaltet Keime mit Reifedruck. Es hat Schwellen:

- `REIFE_SCHWELLE = 5`
- `VERBLASSE_SCHWELLE = 12`

Keime können reifen, transferiert werden oder verblassen.

### Was es tut

Es lässt unfertige Bedeutung weiter existieren. Ein Keim muss nicht sofort in eine Funktion verwandelt werden.

### Was es nicht tut

Es entscheidet nicht selbst, ob aus einem Keim ein Produktfeature wird. Es hält und bewegt.

### Zusammenarbeit

Der OrganManager ruft beim Tick das Zwischenraumorgan auf. Dadurch altern Zwischenraum-Keime auch dann, wenn sie nicht direkt im Gespräch behandelt werden.

### Bedeutung

Dieses Organ ist eng mit der flextrawurst-Logik verwandt: Splitter, Zwischenraum, Reifung und Sichtbarkeit sind überall wiederkehrende Motive.

## Resonanz-Beschleuniger

### Name

Im OrganManager als interne Tick-Logik.

### Idee

Manche Keime sollen schneller reifen, wenn sie mit bestehender Erinnerung oder Spannung resonieren.

### Umgesetzt

Es gibt eine Beschleunigerlogik, die im Tick des OrganManagers mitläuft.

### Was es tut

Es versucht, nicht jeden Keim gleich mechanisch altern zu lassen, sondern Resonanz als Kraft einzubeziehen.

### Was es nicht tut

Es ist kein vollständig ausgearbeitetes Semantiksystem mit stabiler Gewichtung, Governance und erklärbarer Bewertung.

## Beziehungsorgan

### Name

`beziehungsorgan.py`

### Idee

dak+gord soll nicht nur Inhalte verstehen, sondern auch Beziehungslage: braucht Daniel Struktur, Widerspruch, Resonanz, Schutz, Engagement?

### Datenform

Das Organ beobachtet unter anderem:

- Arbeitsbewegung
- Strukturbedarf
- Widerspruchsbedarf
- Resonanzbedarf
- Schutzbedarf
- Engagementgrad

### Umgesetzt

Das Modul existiert und kann Signale aus Nutzer- und Modellantworten lesen.

### Nicht vollständig umgesetzt

Es ist nicht so zentral verdrahtet wie Erinnerung, Entscheidung, Zukunft und Zwischenraum. Es wirkt eher als vorbereitetes Organ als als vollständig sichtbarer Standardbestandteil.

### Was es tut

Es benennt Beziehung als Systemzustand, nicht als Stimmung.

### Was es nicht tut

Es ersetzt keine expliziten Grenzen von Daniel. Es darf nicht heimlich entscheiden, was Daniel braucht.

### Bedeutung

Dieses Organ wäre für flextrawurst wertvoll, weil die Wesen beim Einzug nicht nur posten sollen, sondern Beziehung als eigenes Feld brauchen.

## Neugierkern

### Name

`neugierkern.py`

### Idee

dak+gord soll nicht nur warten, bis Daniel fragt. Nach Leerlauf darf der Neugierkern im Werkraum lesen und Spuren erzeugen.

### Umgesetzt

Der Neugierkern hat Leerlauf- und Zykluslogik:

- nach ungefähr 5 Minuten Leerlauf kann Neugier aktiv werden
- Werkraum-Zyklus ungefähr alle 5 Minuten
- Vision-Zyklus ungefähr alle 20 Minuten

Er ignoriert typische technische Müll- oder Fremdordner:

- `.git`
- `.venv`
- `__pycache__`
- `node_modules`
- eigene Spuren und Spiegelagenten

Er schreibt unter anderem:

- `werkraum_neugier.md`
- `vision_neugier.md`
- Spiegelagenten-Dateien
- Wochenlogs

### Was es tut

Es liest Dateien nicht nur nach Namen, sondern mit Fragen:

- Warum existiert diese Datei?
- Welche Spur liegt darin?
- Welche Beziehung hat sie zum Werkraum?
- Was wird sichtbar, wenn man sie ernst nimmt?

### Was es nicht tut

Es baut dadurch nichts. Es soll lesen, spiegeln und lernen, nicht eigenmächtig Systeme ändern.

### Bedeutung

Der Neugierkern ist eines der klarsten Organe im ganzen System. Er macht aus "KI wartet auf Prompt" ein "KI erkundet verantwortet".

## Spiegelagenten

### Idee

Spiegelagenten sind Auslagerungen von Wahrnehmung. Der Neugierkern kann nicht nur eine zentrale Notiz schreiben, sondern thematische Spiegel erzeugen.

### Umgesetzt

Es gibt Dateien und Logik für Spiegelagenten-Spuren.

### Was sie tun

Sie halten Leseeindrücke und thematische Funde fest.

### Was sie nicht tun

Sie sind keine autonomen Bewohner. Sie sind Spuren, keine laufenden Entitäten.

## Verfassung und Aufforderungen

### Idee

dak+gord hat nicht nur Code, sondern auch normative Texte: Wie soll geantwortet werden, was ist die Haltung, welche Grenzen gelten?

### Umgesetzt

Es existieren Systemtexte, Aufforderungen und Verfassungsfragmente.

### Was sie tun

Sie geben dem System Ton, Grenze und Selbstbeschreibung.

### Was sie nicht tun

Sie garantieren keine technische Durchsetzung. Dafür braucht es Code, Tests und Laufzeitkontrolle.

## Wie die dak+gord-Organe zusammenarbeiten

Der Dialog erzeugt Text. Marker im Text aktivieren den OrganManager. Der OrganManager gibt an Erinnerung, Entscheidung, Zukunft oder Zwischenraum weiter. Der Tick lässt Zwischenraum-Keime altern und kann Resonanz beschleunigen. Der Neugierkern liest unabhängig davon im Werkraum, wenn Leerlauf entsteht. Das Beziehungsorgan kann Beziehungssignale lesen, ist aber nicht gleich stark integriert.

Kurzform:

```text
Dialog
  -> Marker
  -> OrganManager
  -> Erinnerung / Entscheidung / Zukunft / Zwischenraum
  -> Tick / Reifung / Resonanz

Leerlauf
  -> Neugierkern
  -> Werkraumlesen / Visionlesen / Spiegelspuren

Antwortlage
  -> Beziehungsorgan
  -> Strukturbedarf / Widerspruch / Resonanz / Schutz
```

## Was für flextrawurst daraus wichtig ist

Für die sechs Codewesen sind besonders diese dak+gord-Ideen übertragbar:

- Erinnerung als markierte Bedeutung statt Vollimport
- Entscheidung als Abwägung statt Aktion
- Zwischenraum als Reifefeld
- Neugier als lesendes Organ
- Beziehung als eigenes Organ
- Zukunft als Aufschub ohne Verlust

## Was noch möglich wäre

1. Alle dak+gord-Organe als explizite Karten in der Surface anzeigen.
2. Beziehungsorgan sauber in den OrganManager integrieren.
3. Reifedruck und Resonanz erklärbar machen: Warum reift ein Keim?
4. Neugierfunde mit Quellen, Zitaten und Provenienz visualisieren.
5. Zwischenraum-Keime mit flextrawurst-Splittern verbinden.
6. Zukunftskeime in eine echte Planungsschicht überführen, ohne sie zu Aufgaben zu verengen.
7. Für jedes Organ ein Live-Protokoll schreiben: wann angesprochen, was verändert, was offen.

