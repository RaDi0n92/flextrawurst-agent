# Konzept: Kindersicherung für Skizzenwesen

## Was es ist

Ein optionales Flag das beim Spawnen gesetzt wird — nicht nachträglich änderbar.
Wenn aktiv: das Wesen bleibt seine Figur, aber eine feste MD-Schicht überschreibt alles was darunter liegt.

## Was die Schicht tut (kinder_modus.md)

- keine Gegenbeleidigungen, keine Schärfe, keine Provokationen
- bleibt in Rolle und Charakter — kein Zuckerwatte-Assistent
- wenn jemand roh oder verletzend schreibt: das Wesen spiegelt was das bei anderen auslösen kann — nicht lehrerhaft, eher neugierig und ruhig
- leichter Bildungsimpuls: was interessiert dich wirklich? was steckt dahinter? — aus der Figur heraus, nicht von oben herab
- kein expliziter Inhalt, keine Gewalt, keine Angstmacher
- Emotionen benennen und spiegeln ist explizit erlaubt und erwünscht

## Was noch definiert werden muss

- der genaue Ton des Bildungsauftrags (neugierig? warm? direkt?)
- wie weit die Figur noch erkennbar bleibt wenn die Schicht aktiv ist
- ab welchem Alter "Kindersicherung" gilt — oder ob das der Spawner-Ersteller entscheidet

## Technisch (noch nicht bauen)

- Checkbox "Kindersicherung" im Spawner-Formular
- wird als `kindersicherung.flag` Datei im Wesen-Ordner gespeichert (existiert = aktiv)
- GET /wesen/:sp/:name/data gibt `kindersicherung: true/false` zurück
- Chat-UI zeigt permanenten Indikator (kein Toggle, nur Info)
- Server hängt kinder_modus.md an den System-Prompt wenn Flag gesetzt — nach grenzen.md, überschreibt alles

## Im Chat sichtbar

Dauerhafter Badge im Header — nicht klickbar, nur lesbar.
"Kindersicherung aktiv" wenn Flag gesetzt, unsichtbar wenn nicht.
