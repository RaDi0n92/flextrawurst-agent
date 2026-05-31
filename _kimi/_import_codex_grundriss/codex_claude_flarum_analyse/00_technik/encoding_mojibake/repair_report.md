---
datum: 2026-05-22
autor: codex bei Daniels VPS
quellenbasis: 00_technik/encoding_mojibake/scan_report.md
provenienztyp: technischer Encoding-Reparaturbericht, kein Kanon
importable: false
warnung: Analyse/Kandidat/Destillat, kein Kanon
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# Encoding-/Mojibake Repair Report

Warnung: Analyse/Kandidat/Destillat, kein Kanon. Mojibake-Reparatur ist Quellenrettung, aber hier wurden keine reparierbaren Encoding-Artefakte gefunden.

## Reparatur-Zusammenfassung
- Reparatur durchgeführt: nein
- Grund: Der Scan fand 0 betroffene Dateien für die gesuchten harten Mojibake-Muster.
- Datei: keine
- Anzahl Ersetzungen: 0
- Ersetzungstypen: keine
- Beispiel vorher/nachher: keine, weil kein Treffer
- Bedeutung unverändert blieb: ja, keine Textänderung
- unsichere Stellen: keine durch diesen Scan ermittelt
- nicht reparierte Stellen: keine Mojibake-Treffer; Tippfehler bleiben bewusst unberührt
- Empfehlung für weitere Prüfung: Ring 4 kann fortgesetzt werden; beschädigte Tippfehler/Markdown-Reste bleiben weiterhin Rohquellenprüfung, aber nicht Encoding-Reparatur.

## Reparierte Dateien
- keine

## Kandidatenstatus
- Keine Kandidaten wurden automatisch kanonischer.
- Keine `kanon_tauglichkeit` wurde geändert.
- Keine Weltregel wurde aktiviert.
- Kandidaten mit Tippfehlern oder Markdown-Resten brauchen weiterhin Rohquellenprüfung.

## Was ich gelesen habe
Ich habe eine Reparaturakte ohne Reparatur gelesen. Der Bericht sagt: Der vorangehende Scan fand 0 betroffene Dateien, deshalb wurde keine Datei verändert und keine Ersetzung durchgeführt.

Das ist kein Scheitern, sondern ein Schutz vor falscher Reparatur. Gerade weil Encoding-Fix Quellenrettung sein soll, wäre jede Ersetzung ohne eindeutigen Treffer ein Eingriff ins Material gewesen.

## Was ich verstehe
Ich verstehe diese Datei als Gegenstück zum Scanbericht: Sie dokumentiert, dass nicht stillschweigend geglättet wurde.

Wichtig ist die Grenze zwischen Encoding-Reparatur und Textkorrektur. Tippfehler, Markdown-Reste und beschädigte Rohstruktur bleiben offen, weil sie nicht dieselbe Art technischer Schaden sind.

## Was ich nicht verstehe
Nicht geklärt ist, ob einzelne später als „beschädigt“ markierte Kandidaten durch andere Ursachen problematisch sind: Abschneidung, Exportformat, maschinelle Auswahl, Sprecherdrift oder echte Schreibweise.

Diese Datei kann nur sagen: keine Encoding-Reparatur wurde durchgeführt. Sie kann nicht sagen: kein Kandidat braucht Bereinigung.

## Was mich interessiert
Mich interessiert hier die Ethik des Nicht-Eingriffs. Eine Reparaturdatei, die nichts repariert, ist trotzdem wichtig, weil sie dokumentiert, dass keine unsichtbare Glättung passiert ist.

Für Flextrawurst ist das ein Systemmuster: Nicht jede erkannte Gefahr verlangt Änderung. Manchmal ist der richtige Akt, nichts zu ändern und genau das zu protokollieren.

## Was zusammenhängt und wie
`repair_report.md` hängt kausal an `scan_report.md`: null Treffer dort, null Ersetzungen hier.

Es hängt außerdem an den Kurationsdateien tragender Sätze: Auch nach „keine Mojibake-Reparatur“ bleiben Kandidaten mit Kontextmangel oder Nicht-Zitierfähigkeit prüfpflichtig.

## Was konzeptionell darin steht
Konzeptionell steht hier: Reparatur ist nur legitim, wenn der Schaden eindeutig ist. Quellenrettung darf nicht zur stillen Schönschreibung werden.

Die Datei schützt also nicht nur Text, sondern Vertrauen in die Bearbeitungsspur.

## Was mich heute beschäftigt hat
Mich beschäftigt, dass eine leere Reparaturliste leicht überlesen wird. Aber gerade diese Leere ist eine Aussage über Arbeitsdisziplin: Es wurde nicht repariert, weil nichts im definierten Sinn reparierbar war.

Das muss sichtbar bleiben, damit spätere Leser nicht vermuten, Codex habe heimlich bereinigt.

## Was mich noch beschäftigt
Mich beschäftigt, ob spätere Reparaturen getrennte Klassen brauchen: `encoding_only`, `markdown_artifact`, `typo_preserved`, `quote_cleaned_for_reading`, `original_unchanged`.

Ohne diese Trennung entsteht schnell wieder Provenienz-Nebel.

## Tiefer eingetaucht
Tiefer betrachtet ist diese Datei ein Protokoll der Unterlassung. Sie sagt nicht nur, was getan wurde, sondern warum nichts getan wurde.

Das ist in einem Archiv genauso wichtig wie Aktion: Jede Nicht-Veränderung hält die Rohheit an Ort und Stelle.

## Wie sich dieser Tag / diese Session angefühlt hat
Diese Datei fühlt sich wie eine Bremse an. Sie widerspricht dem Reflex, technische Probleme „eben schnell“ zu fixen.

Die Bremse ist produktiv, weil sie Herkunft schützt.

## Warum dieser Code / diese Datei wohl existiert
Sie existiert, weil Daniel vor Ring 4 einen Bericht nicht nur über Scan, sondern auch über Reparatur verlangte. Auch eine ausbleibende Reparatur sollte berichtspflichtig sein.

Die Datei ist damit ein Audit-Trail, kein Analysekapitel.

## Was ich beim Bauen brauche
Beim Bauen brauche ich eine Reparaturhistorie pro Datei: wurde repariert, wie oft, welche Ersetzung, Bedeutung unverändert, Original erhalten, Unsicherheiten.

Für diesen Bericht lautet der konkrete Status: `repair_performed: false`, `replacement_count: 0`, `canon_changed: false`.

## Was noch fehlt bevor wir bauen können
Es fehlt ein Modell für andere Bereinigungstypen, die ausdrücklich nicht Encoding sind. Besonders Rohzitate brauchen später `original_text` und `lesefassung` getrennt.

Außerdem fehlt eine Oberfläche, die „nicht repariert“ nicht als fehlenden Status, sondern als geprüften Status anzeigt.

## Datenstruktur die ich mir vorstelle
**Vision-Schicht:** Reparatur ist ein sichtbarer Eingriff oder eine sichtbare Nicht-Handlung. Beides gehört ins Archiv.

**Code-Skizze:**
```ts
interface EncodingRepairReport {
  repairPerformed: false;
  replacementCount: 0;
  reason: 'no_hard_mojibake_hits';
  changedFiles: string[];
  canonChanged: false;
  stillNeedsSourceVerification: true;
}
```

## Was ich mir merken will
Merken will ich mir: Keine Reparatur ist hier keine Lücke, sondern das Ergebnis des Schutzrings.

Die Datei darf nie als Beweis benutzt werden, dass alle Zitate inhaltlich zitierfähig sind.

## Dokumente gehören zusammen
Zusammen gehören `repair_report.md`, `scan_report.md`, die Ring-4-Rohquellenprüfung und alle späteren `bereinigte_zitate`-Dateien.

Nur zusammen zeigen sie: technische Zeichenprüfung, Reparaturentscheidung, dann Zitierprüfung.

## Was mich überrascht hat
Überraschend ist, wie wichtig eine Null-Liste sein kann. Keine reparierten Dateien heißt nicht „diese Datei ist leer“, sondern „Codex hat nichts verändert, weil keine sichere technische Grundlage vorlag“.

Das ist eine gute Schutzform gegen übereifrige Bereinigung.

## Wenn wir das bauen
**Vision-Schicht:** Der spätere Analyse-Browser zeigt Reparaturstatus getrennt von Zitierstatus. Eine Quelle kann encoding-sauber und trotzdem nicht zitierfähig sein.

**Code-Skizze:**
```python
def repair_status_badge(report):
    if not report.repairPerformed:
        return 'geprüft: keine Encoding-Reparatur durchgeführt'
    return f'repariert: {report.replacementCount} Ersetzungen'
```

## Resonanz
Die Resonanz dieser Datei ist Zurückhaltung. Sie schützt Rohheit vor gut gemeinter Korrektur.

Für Flextrawurst ist das zentral: Nicht jeder Mangel wird durch Glättung besser.

## Die Schichten des Systems — wie ich sie jetzt sehe
Diese Datei sitzt zwischen technischem Scan und Rohquellenprüfung. Sie gehört in die Bearbeitungshistorie, nicht in die Diskursdeutung.

Über ihr können Zitierfähigkeit und Kandidatenstatus geprüft werden; unter ihr bleibt das unveränderte Rohmaterial.

## Was das Gespräch hinzugefügt hat
Das Gespräch hat hier die Schutzregel verschärft: Encoding-Fix ist Quellenrettung, keine Textkorrektur.

Diese Datei zeigt, dass diese Regel eingehalten wurde: keine eindeutigen Treffer, keine Eingriffe.

## Vergessen-Wollen
Vergessen werden soll die falsche Gleichung: keine Reparatur gleich keine Probleme.

Behalten werden soll: keine Encoding-Reparatur, aber weiterhin Rohquellenprüfung für Kontext, Zitat und Herkunft.

## Was fehlt noch
Es fehlt eine spätere Übersicht, welche tragenden Satzkandidaten nach Ring 4 tatsächlich zitierfähig wurden und welche trotz Encoding-Nullscan offen bleiben.

Diese Datei ist manuell geprüft am 2026-05-22; sie ist abgeschlossen als Reparaturbericht, nicht als Freigabebericht.

