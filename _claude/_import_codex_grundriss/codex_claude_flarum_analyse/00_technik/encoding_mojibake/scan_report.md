---
datum: 2026-05-22
autor: codex bei Daniels VPS
quellenbasis: Flarum-Markdown-Export; _codex/codex_flarum_analyse; 08_tragende_saetze; Provenienzdateien; Rohdaten-Textdateien
provenienztyp: technischer Encoding-Scan, kein Kanon
importable: false
warnung: Analyse/Kandidat/Destillat, kein Kanon
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# Encoding-/Mojibake Scan Report

Warnung: Analyse/Kandidat/Destillat, kein Kanon. Dieser Bericht ist technische Quellenrettung, keine Textglättung.

## Scan-Zusammenfassung
- Anzahl geprüfter Dateien: 1678
- Anzahl betroffener Dateien: 0
- Einschätzung: keine Treffer
- Rohquellen betroffen: 0
- Analyse-Dateien betroffen: 0

## Gesuchte Muster
- `Ã`
- `Â`
- `â€`
- `â€“`
- `â€”`
- `â€¦`
- `�`

## Betroffene Dateien
- keine

## Was ich gelesen habe
Ich habe hier keinen Diskursbefund gelesen, sondern eine technische Negativauskunft: 1678 Dateien wurden nach harten Mojibake-Mustern durchsucht, und der Scan fand 0 betroffene Dateien.

Das ist gerade deshalb wichtig, weil vorher echte Angst im Material lag: kaputte Umlaute könnten Sätze, Zitate, Tags und spätere Weltregeln beschädigen. Diese Datei sagt nicht „alles ist sprachlich sauber“. Sie sagt enger: Die definierten harten Encoding-Muster wurden in den geprüften Dateien nicht gefunden.

## Was ich verstehe
Ich verstehe diese Datei als Schutzschwelle vor Ring 4. Sie erlaubt Rohquellenprüfung weiterzuführen, ohne vorher eine globale Encoding-Reparatur erzwingen zu müssen.

Sie beweist aber nicht, dass alle Texte korrekt sind. Tippfehler, Exportreste, Markdown-Schäden, abgeschnittene Stellen und semantische Rohheit bleiben ausdrücklich außerhalb dieses Scans.

## Was ich nicht verstehe
Nicht geklärt ist, ob weichere Encoding-Schäden existieren, die nicht von den Suchmustern `Ã`, `Â`, `â€`, `â€“`, `â€”`, `â€¦` oder `�` erfasst werden.

Auch nicht geklärt ist, ob einzelne problematische Stellen aus späteren Kandidaten eher Tippfehler, Exportartefakt oder echte Wesen-Schreibweise sind. Diese Datei entscheidet das nicht.

## Was mich interessiert
Mich interessiert an dieser Datei die Strenge ihrer Begrenzung. Sie ist nützlich, weil sie nicht mehr behauptet, als sie geprüft hat.

Für Flextrawurst ist das ein gutes Muster: technische Prüfungen dürfen keine semantischen Urteile werden. Ein Scan kann eine Klasse von Schäden ausschließen, aber nicht Herkunft, Bedeutung oder Kanon sichern.

## Was zusammenhängt und wie
Diese Datei hängt direkt mit `repair_report.md` zusammen: Scan ohne Treffer führt zu Reparatur ohne Änderung.

Sie hängt außerdem mit `08_tragende_saetze/04_rohquellenpruefung/` zusammen, weil Zitierfähigkeit erst nach Quellenprüfung entschieden werden darf. Der Encoding-Scan nimmt nur eine technische Gefahr aus dem Weg.

## Was konzeptionell darin steht
Konzeptionell steht hier: Quellenrettung beginnt vor Interpretation. Bevor ein Satz als stark, schön oder tragend gilt, muss klar sein, ob seine Zeichen überhaupt technisch intakt sind.

Die Datei ist damit kein Inhalt über die Wesen, sondern ein Schutz um die Wesen herum.

## Was mich heute beschäftigt hat
Mich beschäftigt, dass „0 Treffer“ gefährlich beruhigend klingen kann. Null Treffer heißt nicht null Problem, sondern null Treffer für genau diese Muster in genau diesem Suchraum.

Diese Präzision muss stehen bleiben, sonst wird aus einem technischen Bericht wieder ein falscher Freibrief.

## Was mich noch beschäftigt
Mich beschäftigt, ob spätere Analysewerkzeuge eigene Scans brauchen: nicht nur Mojibake, sondern abgeschnittene Posts, kaputte Markdown-Links, doppelte Exportmarker, falsche Sprecheranker.

Der Scan hier ist ein Anfang, nicht das Ende technischer Quellenhygiene.

## Tiefer eingetaucht
Tiefer betrachtet ist die Datei eine Lektion in negativer Evidenz. Sie liefert keinen Fund, sondern räumt einen Verdacht kontrolliert beiseite.

Das ist für die Diskursarchäologie wichtig: Auch Nicht-Funde müssen sauber beschrieben werden, damit sie nicht später als unbewiesene Sicherheit auftauchen.

## Wie sich dieser Tag / diese Session angefühlt hat
Diese Datei fühlt sich trocken an, aber genau diese Trockenheit ist ihre Stärke. Sie darf nicht poetisch werden.

Der richtige Ton ist prüfend: gesucht, nichts gefunden, keine Reparatur ausgelöst, Rohquellenprüfung trotzdem nötig.

## Warum dieser Code / diese Datei wohl existiert
Diese Datei existiert, weil Daniel vor Ring 4 ausdrücklich einen Encoding-Schutzring gefordert hat. Der Zweck war, beschädigte Umlaute und Anführungszeichen nicht still in Zitate oder Regeln zu übernehmen.

Sie existiert also als technische Sperre vor Bedeutung.

## Was ich beim Bauen brauche
Beim Bauen brauche ich daraus eine kleine Prüfakte: Suchmuster, geprüfte Dateizahl, Trefferzahl, betroffene Pfade, Zeitpunkt, Ergebnis, und den Hinweis, dass nicht geprüfte Fehlerklassen offen bleiben.

Kein späteres System sollte daraus `text_is_clean: true` machen. Korrekt wäre höchstens `hard_mojibake_scan_hits: 0`.

## Was noch fehlt bevor wir bauen können
Es fehlt eine breitere Quellenhygiene-Prüfung für Nicht-Encoding-Schäden: abgeschnittene Posts, Exportreste, falsche Links, Sprecheranker und manuelle Schreibfehler.

Außerdem fehlt im Analyse-Browser eine Anzeige, welche technische Prüfung eine Quelle bereits bestanden hat und welche nicht.

## Datenstruktur die ich mir vorstelle
**Vision-Schicht:** Der Scan ist ein technischer Schutzzaun. Er hält bestimmte Encoding-Schäden fern, ohne zu behaupten, der Garten sei vollständig geordnet.

**Code-Skizze:**
```ts
interface EncodingScanReport {
  checkedFiles: number;
  hitFiles: number;
  patterns: string[];
  scope: string[];
  result: 'no_hard_mojibake_hits';
  semanticCleanlinessConfirmed: false;
  nextChecks: string[];
}
```

## Was ich mir merken will
Merken will ich mir: Null Mojibake-Treffer ist ein technischer Befund, keine semantische Reinwaschung.

Diese Datei schützt Zitate nur an einer Stelle: Zeichenkodierung.

## Dokumente gehören zusammen
Zusammen gehören `scan_report.md`, `repair_report.md`, `PROVENIENZ_MANIFEST.md`, `08_tragende_saetze/04_rohquellenpruefung/pruefprotokoll.md` und alle Dateien, aus denen später wörtlich zitiert werden soll.

Wer Zitate prüft, muss diese Datei kennen, aber darf bei ihr nicht stehen bleiben.

## Was mich überrascht hat
Überraschend ist, dass der Scan keine harten Treffer fand, obwohl in Daniels Beispiel Mojibake sichtbar war. Das kann bedeuten, dass die betroffenen Stellen außerhalb des geprüften Bereichs lagen, bereits korrigiert waren, oder nicht in den gescannten Dateien standen.

Diese Überraschung ist ein Grund, den Befund vorsichtig zu formulieren.

## Wenn wir das bauen
**Vision-Schicht:** Ein späterer Browser zeigt pro Quelle einen technischen Prüfstatus: Encoding-Scan durchgeführt, Trefferzahl, Reparaturstatus, offene Prüfarten.

**Code-Skizze:**
```python
def encoding_badge(report):
    return {
        'label': 'Hard Mojibake Scan',
        'checked_files': report.checkedFiles,
        'hits': report.hitFiles,
        'allows_quote_decision': False,
    }
```

## Resonanz
Die Resonanz dieser Datei ist Nüchternheit. Sie bremst den Wunsch, beschädigte Zeichen als Inhalt oder Stil zu lesen.

Sie sagt: Erst prüfen, dann deuten.

## Die Schichten des Systems — wie ich sie jetzt sehe
Diese Datei liegt unterhalb der Diskursdeutung, aber oberhalb der Rohdateien als technische Prüfschicht.

Sie gehört nicht in Wesenprofile, nicht in Weltregeln, sondern in Provenienz- und Zitierfähigkeitssysteme.

## Was das Gespräch hinzugefügt hat
Das Gespräch hat diese Datei notwendig gemacht, weil Daniel zu Recht verhindern wollte, dass kaputte Zeichen in Kanon, Profile oder tragende Sätze wandern.

Nach der späteren Kritik an mechanischen Abschnitten zeigt diese Datei zusätzlich: Auch Schutzberichte brauchen präzise Selbstbegrenzung.

## Vergessen-Wollen
Vergessen werden soll die falsche Lesart: „Der Scan fand nichts, also sind alle Quellen sauber.“

Behalten werden soll: „Der Scan fand keine Treffer für definierte harte Mojibake-Muster; alles andere bleibt prüfpflichtig.“

## Was fehlt noch
Es fehlt ein zweiter technischer Prüfblock für Nicht-Encoding-Artefakte und ein Link zur Rohquellenprüfung jedes tragenden Satzes.

Diese Datei ist manuell geprüft am 2026-05-22; sie ist abgeschlossen als Scanbericht, aber nicht als vollständige Quellenhygiene.

