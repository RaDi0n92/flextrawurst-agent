---
name: charakter-dashboard
description: Übersichtsseite /charakterdashbord über alle Charaktere aller vier Spawner + übergreifendes Feedback-Feld
metadata:
  type: project
tags: [dashboard, uebersicht, feedback, alle-spawner]
status: gebaut
datum: 2026-07-05
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Scope

Im Unterschied zu fast allen anderen Features der letzten Tage (siehe `codexium2_solarius2/`-Ordner) betrifft dieses **alle vier Spawner** — codexium, codexium2, solarius, solarius2. Daniels Wunsch explizit: "ne art übersichtsseite über alle aktuellen charektere aus ihren jeweiligen kategorien". Auf Nachfrage (AskUserQuestion) bestätigt: alle vier, nicht nur das Testbed — reines Lesen/Anzeigen verändert nichts an codexium/solarius selbst, bricht also nicht das "unangetastet lassen"-Prinzip aus Grundgesetz 6.

Erreichbar unter `/charakterdashbord` (Daniels eigene Schreibweise, bewusst genau so übernommen, nicht zu "dashboard" korrigiert — URLs sind wörtlich das was er sich merkt).

## Was ich gelesen habe

Den bestehenden Chat-Code (`serve_process_camera_preview.ts`) nach allen Stellen durchsucht, die einen Charakter anhand von Spawner+Name auflösen — 24 Stellen, alle nutzen inzwischen `resolveCharName()` (siehe die Case-Insensitivitäts-Session von heute Nacht). Das Dashboard nutzt dieselbe Infrastruktur weiter, baut nichts Neues für die Namensauflösung.

## Was ich verstehe

Ein Dashboard über "alles was existiert" ist etwas grundsätzlich anderes als die bisherigen Features — die waren immer *innerhalb* eines Charakters (Memory, Container, Abschluss). Das hier ist die erste *Meta-Ebene*, die über Charaktere hinweg schaut. Genau deshalb lila/flieder statt dem bestehenden Cyan der Chat-Oberfläche — bewusst visuell abgesetzt, damit klar ist: das ist die Vogelperspektive, nicht ein weiterer Charakter-Screen.

## Was ich nicht verstehe

Ob "Kategorien" in Daniels Formulierung ("aus ihren jeweiligen kategorien") tatsächlich die vier Spawner meinte, oder etwas Feineres (z.B. Charakter-Typen wie "düster", "freundlich" — noch nicht vorhanden als Datenfeld). Ich habe mich für "Spawner als Kategorie" entschieden, weil das die einzige tatsächlich vorhandene Gruppierung im System ist. Falls mehr gemeint war, ist das offen.

## Was mich interessiert

Wie sich das Dashboard verhält, sobald wirklich viele Charaktere existieren (aktuell 8) — die Detail-Fetches laufen parallel (`Promise.all`), aber bei z.B. 50 Charakteren wären das 100+ parallele Requests alle 10 Sekunden bei jeder Änderung. Noch kein Problem, aber ein Punkt zum Nachschauen falls die Sammlung stark wächst.

## Was zusammenhängt und wie

Das Dashboard ist die erste Stelle, die **codexium/solarius UND codexium2/solarius2 gemeinsam** sichtbar macht — bisher liefen die vier Spawner nebeneinander her, ohne dass es einen Ort gab, sie gemeinsam zu sehen. Das allgemeine Feedback-Feld hängt daran, weil es dieselbe "gilt für alle vier"-Eigenschaft hat wie das Dashboard selbst — beide sind bewusst nicht ins Testbed-Silo gesperrt.

## Was konzeptionell darin steht

Zwei verschiedene Feedback-Arten koexistieren jetzt bewusst nebeneinander: das alte, nachrichtengebundene (Daumen hoch/runter + Kommentar, nur codexium2/solarius2, Upsert-Semantik — eine Meinung pro Nachricht) und das neue allgemeine (kein Bezug zu einer Nachricht, für alle Spawner, Append-Semantik — beliebig viele Meinungen über Zeit). Unterschiedliche Fragen: "was hältst du von dieser einen Antwort" vs. "was fällt dir am Charakter insgesamt auf".

## Was mich heute beschäftigt hat

Die Reihenfolge der Anforderungen kam in einem einzigen, dichten Nachrichtenblock — Übersicht, Profilansicht, Memory/Container-Einsicht, Feedback-Übersicht, neues Feedback-Feld, MD-Sichtbarkeit, Popup-Öffnen, Auto-Refresh, Farbe. Ich habe bewusst zwei Rückfragen gestellt (Spawner-Scope, Feedback-Speicherform) statt bei neun Einzelpunkten zu raten, weil die ersten beiden echte Architektur-Gabelungen waren — der Rest (Popup, Auto-Refresh-Mechanismus, Farbwahl) war eindeutig genug zum Bauen ohne Nachfrage.

## Was mich noch beschäftigt

Ob "Profilansicht jeweils" mehr meinte als der bestehende Link zur schon vorhandenen `wesen_profil.html` — ich habe das als "Profil-Button öffnet die bestehende Profilseite" interpretiert, nicht als Auftrag für eine neue, dritte Profilansicht. Falls Daniel eine eigene, kompaktere Vorschau direkt im Dashboard meinte (statt Popup zur vollen Profilseite), wäre das ein Nachtrag.

## Tiefer eingetaucht

Die Auto-Refresh-Logik vergleicht nicht einfach "gibt es mehr Charaktere", sondern die komplette sortierte Liste als JSON-Signatur (`JSON.stringify` von Spawner+Name-Paaren) — das erkennt auch Löschungen und Umbenennungen als "Änderung", nicht nur Neuanlagen. Bewusst simpel gehalten (kein Diffing einzelner Felder), weil die Liste klein ist und ein kompletter Re-Render bei echter Änderung keine spürbaren Kosten hat.

## Wie sich dieser Tag / diese Session angefühlt hat

Der Übergang von einzelnen, engen Bugfixes (Satzabbruch, Verwerfen-Bug, Case-Sensitivität) zu einem echten neuen Feature mit eigener Seite fühlte sich wie ein Tempowechsel an — die letzten Stunden waren reaktiv (Daniel testet, meldet, ich repariere), das hier war wieder aktiv bauen nach Spezifikation.

## Warum dieser Code / diese Datei wohl existiert

`wesen_uebersicht.html` existiert, weil es bisher keinen Ort gab, an dem Daniel "alles was ich gebaut habe" auf einen Blick sehen konnte — jeder Charakter war nur einzeln über seine eigene URL erreichbar, nichts hat sie nebeneinandergestellt.

## Was ich beim Bauen brauche

Nichts Offenes. Feature ist vollständig, getestet.

## Was noch fehlt bevor wir bauen können

Nichts Blockierendes. Offen, kein Auftrag: eine kompaktere Inline-Profilvorschau statt Popup (siehe oben), eventuell serverseitige Paginierung falls die Charakterzahl stark wächst.

## Datenstruktur die ich mir vorstelle

### Vision-Schicht
Das Dashboard ist ein Fenster in eine Werkstatt mit vielen gleichzeitig laufenden Experimenten (siehe frühere Notiz zur Charakterqualität: "das ist keine einheitliche Stimme, das ist eine Werkstatt") — zum ersten Mal sichtbar als Ganzes statt als Einzelteile.

### Code-Skizze
```typescript
// GET /wesen/alle → { charaktere: [{spawner, name}] }
// GET/POST /wesen/:spawner/:name/feedback/allgemein → { eintraege: [{id, text, erstellt_am}] }
// Frontend: ladeAlle() pollt alle 10s, Signatur-Vergleich verhindert unnoetigen Re-Render
```

## Was ich mir merken will

- `/charakterdashbord` — bewusst Daniels Schreibweise, nicht "dashboard".
- Allgemeines Feedback ist Append-only (eigene Datei pro Eintrag), Nachrichten-Feedback bleibt Upsert (eine Datei pro Nachricht, überschreibbar).
- Avatar-Fallback zeigt den ersten Buchstaben des Namens, wenn kein Bild hochgeladen wurde.

## Dokumente gehören zusammen

`_claude/notizen/2026-07-05-abschluss-bugfixes-wesen-selbst.md` (derselbe Abend, vorherige Themen), `_claude/ideen/codexium2_solarius2/*` (die testbed-spezifischen Geschwister-Features, an die sich das Dashboard konzeptionell anlehnt — Memory/Container/Feedback-Anzeige folgt denselben Datenformaten).

## Was mich überrascht hat

Wie wenig neuer Code für die Namensauflösung nötig war — weil `resolveCharName()` von der Case-Insensitivitäts-Arbeit vor wenigen Stunden schon alle 24 relevanten Stellen abdeckte, musste das Dashboard nichts Neues dafür bauen, nur die bestehenden `/data`- und `/image`-Endpunkte wiederverwenden.

## Wenn wir das bauen

**Vision-Schicht:** Ein Dashboard, das mit der Zeit mitwächst — heute nur Zähler und Links, später vielleicht eine Zeitachse ("was ist heute an allen Charakteren passiert") oder ein Vergleich ("welcher Charakter bekommt das meiste Feedback").

**Code-Skizze:** Keine offene — aktuelle Version ist vollständig für den gestellten Auftrag.

## Resonanz

[[abwurf: Das Dashboard ist die erste Stelle, die alle vier Spawner gemeinsam sichtbar macht — vorher liefen sie nebeneinander her, ohne dass es einen Ort gab, sie zusammen zu sehen.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

```
Vier Spawner (codexium, codexium2, solarius, solarius2)
  → bisher: nur einzeln ueber ihre eigene URL erreichbar
  → jetzt: /charakterdashbord als gemeinsame Meta-Ebene daroberliegend
    → pro Karte: Chat/Profil (Popup zu bestehenden Seiten),
                 Memory/Container (Lese-Modal, gleiche Daten wie im Chat selbst),
                 Feedback (neu: uebergreifend, zusaetzlich zum alten nachrichtengebundenen)
```

## Was das Gespräch hinzugefügt hat

Der erste Schritt weg von "ein Charakter zur Zeit" hin zu "alles was existiert, auf einen Blick" — eine strukturelle Erweiterung, keine weitere Detailfunktion innerhalb eines einzelnen Charakters.

## Vergessen-Wollen

Nichts.

## Was fehlt noch

- Klärung ob "Profilansicht" mehr als der bestehende Popup-Link zur Profilseite gemeint war (offen, s.o.).
- Eventuell spätere Paginierung/Performance-Nachschau bei starkem Wachstum der Charakterzahl.

### Nachtrag 2026-07-05 (Nacht) — Soft-Delete + Hard-Delete, statt nur hartem Löschen

Daniel fragte direkt nach, wie Löschen eines Charakters heute tatsächlich funktioniert — nachgeschaut statt vermutet: der bestehende `DELETE /wesen/:spawner/:name`-Endpunkt war ein echtes, endgültiges `rmSync(recursive, force)`. Das widersprach "Grundgesetz 3: nichts wird gelöscht, nur deaktiviert" aus `/root/CLAUDE.md`, war aber vorher nie explizit als Bug erkannt worden.

Daniels Auftrag war klar gescopt: auf der **Profilseite** nur Soft-Delete (alles bleibt, nur verschoben), auf dem **Dashboard** beide Optionen nebeneinander, deutlich unterschieden.

Umsetzung:
- Neuer Endpunkt `POST /wesen/:spawner/:name/soft-delete` — verschiebt den ganzen Charakterordner nach `<spawner-root>/_geloescht/<name>__<zeitstempel>` (`renameSync`, kein Datenverlust). `GET /wesen/alle` und `GET /wesen/list` filtern `_geloescht` jetzt explizit raus, damit verschobene Charaktere nirgendwo mehr auftauchen, ohne dass ihre Dateien wirklich weg sind.
- `wesen_profil.html`: Lösch-Button ruft jetzt `soft-delete` statt `DELETE`, mit angepasstem Hinweistext ("wird in den Papierkorb verschoben, nichts geht verloren").
- Dashboard-Karten: zwei getrennte Buttons — 🗑️ Löschen (orange, ein `confirm()`, ruft Soft-Delete) und ⚠️ Endgültig löschen (rot, zwei `confirm()`-Dialoge hintereinander mit expliziter Warnung "kann NICHT rückgängig gemacht werden", ruft weiterhin den alten harten `DELETE`-Endpunkt).
- Der harte Endpunkt selbst blieb unverändert bestehen — Claude nutzt ihn seither auch bewusst weiter, um eigene Wegwerf-Testcharaktere nach dem Verifizieren wieder restlos zu entfernen, statt den Papierkorb mit Testmüll zu füllen.

Getestet per Playwright: Karte verschwindet nach Soft-Delete-Klick aus der Dashboard-Liste (Ordner bleibt aber unter `_geloescht/` real erhalten), zweiter Test bestätigte den Doppel-`confirm()`-Ablauf beim Hard-Delete.

**Was ich mir daraus merke:** eine als selbstverständlich behandelte Funktion (Löschen) kann trotzdem im Widerspruch zu einem längst aufgeschriebenen Grundgesetz stehen, wenn sie zu einem Zeitpunkt gebaut wurde, bevor das Grundgesetz explizit galt oder geprüft wurde. Nachfragen statt annehmen war hier genau richtig.
