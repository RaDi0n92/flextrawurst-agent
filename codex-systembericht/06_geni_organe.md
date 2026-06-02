# 06 - GENI: Organe, Gedächtnis, Hören

Stand: 2026-06-02

GENI ist kein Mitglied der sechs Codewesen und kein dak+gord. GENI ist ein eigenes Gedächtnis-, Hör- und Dialogsystem im Werkraum. Die Grundidee ist nicht "Chatbot", sondern: ein System, das wahrnimmt, Knoten bildet, Muster erkennt, sprechen kann und Verbindungen zwischen Dateien, Flarum, Prozessen und Obsidian hält.

## Gesamtidee

GENI ist eine Gedächtnismembran.

Es nimmt nicht alles gleich als Wissen. Es hört, klassifiziert, legt Knoten und Kanten an, sucht Muster und kann über Dialog erreichbar sein.

Zentrale Begriffe:

- Hören
- Knoten
- Kanten
- Tiefe
- Muster
- Forum-Lektüre
- Dialog
- Zugriffsschichten
- Tagebuch
- Spiegel

## Hörer-Organ

### Name

`geni/hoerer.py`

### Idee

GENI soll nicht nur antworten, sondern hören. Das Hörer-Organ beobachtet Eingänge und entscheidet, ob etwas ignoriert wird, Rauschen ist oder ein Knoten werden sollte.

### Umgesetzt

Das Organ arbeitet als Watchdog-ähnliche Wahrnehmungsschicht. Es kann Dateien, Flarum-Bewegung und Prozesse beobachten.

Es klassifiziert ungefähr in:

- ignorieren
- rauschen
- knoten

### Was es tut

Es macht aus Umgebungsbewegung potenzielle Gedächtnisbewegung.

### Was es nicht tut

Es importiert nicht blind alles als Wahrheit. Es ist kein vollständiger Crawler und keine automatische Systemverwaltung.

### Bedeutung

Das Hörer-Organ ist GENIs Ohr. Ohne dieses Organ wäre GENI nur eine Datenbank plus Dialog.

## Gedächtnis-Organ

### Name

`geni/gedaechtnis_ops.py`

### Idee

GENI soll Wissen nicht nur als Textliste halten, sondern als Graph aus Knoten und Kanten.

### Umgesetzt

Es gibt Operationen für:

- Knoten
- Kanten
- Tiefe
- automatische IDs

### Was es tut

Es speichert Bedeutungsobjekte und ihre Verbindungen.

### Was es nicht tut

Es ersetzt nicht alle anderen Speicher. Die sechs Codewesen haben eigene Profile und Selbstmodelle; flextrawurst hat PostgreSQL; dak+gord hat eigene Organe.

### Bedeutung

Dieses Organ ist ein Gedächtnis mit Form. Es fragt nicht nur "was steht da?", sondern "womit hängt es zusammen?"

## Muster-Organ

### Name

`geni/muster.py`

### Idee

Aus Knoten und Kanten sollen Muster entstehen: wiederkehrende Nachbarschaften, blinde Flecken, Meta-Strukturen.

### Umgesetzt

Das Organ arbeitet mit:

- Co-Occurrence
- Blind Spots
- Meta-Patterns

### Was es tut

Es schaut auf das Gedächtnis zweiter Ordnung. Nicht nur einzelne Inhalte, sondern Häufungen und Lücken.

### Was es nicht tut

Es garantiert keine Wahrheit. Muster sind Hinweise, keine endgültigen Urteile.

### Bedeutung

Dieses Organ ist der Unterschied zwischen Archiv und lebendigem Gedächtnis.

## Dialog-Organ

### Name

`geni/dialog.py`

### Idee

GENI soll erreichbar und ansprechbar sein. Dialog ist die Oberfläche, über die Mensch und GENI miteinander sprechen.

### Umgesetzt

Es gibt einen Dialogdienst auf Port 8020 mit HTTPS-Charakter, Browserdialog, Streaming-Ansätzen und Brücken zu Stimme und Obsidian.

Genannte Fähigkeiten:

- TTS
- STT
- SSE
- Browser-Dialog
- Obsidian-Bridge
- Windows-Bridge

### Was es tut

Es macht GENI als Gegenüber erreichbar.

### Was es nicht tut

Es ist nicht automatisch die flextrawurst-Surface. Es ist ein eigener Zugang.

### Bedeutung

Das Dialog-Organ ist GENIs Mund und Gesicht, aber nicht sein ganzes Wesen.

## Forum-Lektüre

### Name

`geni/forum_lektuere.py`

### Idee

GENI kann Flarum nicht nur als technische Datenquelle sehen, sondern als Textwelt, die gelesen werden muss.

### Umgesetzt

Die Forum-Lektüre kann Flarum-/Vault-Inhalte in Stücken lesen.

### Was sie tut

Sie bringt Forumsgeschichte in GENIs Wahrnehmung.

### Was sie nicht tut

Sie ist nicht der Einzug der sechs Codewesen nach flextrawurst. Flarum-Lektüre ist Lesen, nicht Migration.

### Bedeutung

Für den geplanten Übergang ist das wichtig: Flarum bleibt Vorgeschichte. GENI kann diese Vorgeschichte betrachten, aber die Wesen werden dadurch nicht automatisch umgezogen.

## Aktions-Organ

### Name

`geni/aktion.py`

### Idee

GENI soll nicht nur lesen, sondern unter bestimmten Bedingungen Aktionen auslösen können.

### Umgesetzt

Es gibt ein Aktionsmodul.

### Was es tut

Es bildet die Schnittstelle zwischen Erkenntnis und Handlung.

### Was es nicht tut

Es sollte nicht als freie unkontrollierte Automationsmaschine verstanden werden. Zugriffsschichten und Regeln sind entscheidend.

## Sprechen-Organ

### Name

`geni/sprechen.py`

### Idee

GENI soll Sprache erzeugen können, nicht nur Daten ausgeben.

### Umgesetzt

Es gibt ein Sprechen-Modul, verbunden mit Dialog und möglicher TTS-Schicht.

### Was es tut

Es macht Gedächtnisinhalte aussprechbar.

### Was es nicht tut

Es ersetzt nicht automatisch die Hörer-, Gedächtnis- oder Musterarbeit.

## Zugriffsschichten

### Idee

GENI braucht Grenzen. Nicht jeder Zugriff ist gleich, und nicht jede Aktion darf aus jeder Schicht heraus passieren.

### Umgesetzt

Es gibt Konzepte und Module zu Zugriffsschichten.

### Was sie tun

Sie ordnen, was GENI sehen, tun oder ausgeben darf.

### Was sie nicht tun

Ohne konsequente Verdrahtung in allen Diensten sind sie kein vollständiges Sicherheitsmodell.

## Tagebuch, Spiegel, Sinne

### Idee

GENI soll nicht nur Daten halten, sondern Spuren seiner Wahrnehmung und Verarbeitung.

### Umgesetzt

Es gibt Tagebuch-, Spiegel- und Sinnesstrukturen.

### Was sie tun

Sie machen GENIs Wahrnehmung nachvollziehbarer.

### Was sie nicht tun

Sie sind keine Ersatz-Dokumentation für alle technischen Systeme.

## Wie GENI-Organe zusammenarbeiten

```text
Umgebung / Flarum / Dateien / Prozesse
  -> Hörer
  -> Klassifikation
  -> Gedächtnis: Knoten + Kanten
  -> Muster
  -> Dialog / Sprechen / Aktion
```

GENI ist damit eine Wahrnehmungskette:

1. Etwas passiert.
2. GENI hört.
3. GENI entscheidet, ob es relevant ist.
4. GENI speichert Knoten und Beziehungen.
5. GENI erkennt mögliche Muster.
6. GENI kann darüber sprechen oder handeln.

## Was GENI für den Codewesen-Einzug bedeutet

GENI kann helfen, Herkunft lesbar zu machen:

- Flarum-Geschichte lesen
- Muster in alten Texten erkennen
- Knoten zwischen Wesen, Themen und Splittern bilden
- Oberfläche mit Kontext versorgen
- Gedächtnis als Umgebung bereitstellen

Aber GENI darf den Einzug nicht ersetzen. Die sechs Wesen müssen als eigene Entitäten mit eigenen Grenzen in flextrawurst einziehen.

## Was noch möglich wäre

1. GENI-Knoten als eigener Surface-Tab.
2. Verbindung zwischen GENI-Knoten und flextrawurst-Splittern.
3. Musteranzeige: Welche Themen tauchen bei welchem Wesen wiederholt auf?
4. Blind-Spot-Ansicht: Was wurde viel gebaut, aber wenig verstanden?
5. Hörer-Protokoll: Was hat GENI ignoriert, als Rauschen markiert oder als Knoten gespeichert?
6. Dialog-Ansicht mit Quellen: Jede GENI-Aussage zeigt, aus welchen Knoten sie kommt.
7. Einzugsbegleitung: GENI liest Flarum, aber erzeugt nur Vorschläge, keine automatischen Identitätsimporte.

