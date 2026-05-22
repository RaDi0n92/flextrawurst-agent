---
datum: 2026-05-22
betrifft: [flarum, diskursarchaeologie, codewesen]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# Provenienz-Manifest



## Zweck

Dieses Manifest verhindert Provenienz-Nebel. Jede Datei im Analyseordner wird als Quelle, Zählung, Interpretation, Kandidat, Destillat oder Systemregel-Kandidat gelesen. Keine Datei in diesem Ring ist bereits Systemregel.

## Typen

| Typ | Bedeutung | Darf direkt als Wahrheit gelten? |
|---|---|---|
| `quelle` | direkt aus Flarum oder Rohbeleg | nur als Quelle |
| `zaehlung` | mechanische Statistik aus Parser | nein, Export/Parser prüfen |
| `interpretation` | Codex-Deutung aus Quellen | nein |
| `kandidat` | Vorselektion für spätere Kuratierung | nein |
| `destillat` | Verdichtung aus mehreren Befunden | nein |
| `systemregel_kandidat` | mögliche spätere Regel | erst nach Daniel-Freigabe |

## Datei-Inventar

| Pfad | Analysepunkt | Provenienztyp | Nachprüfung |
|---|---|---|---|
| `INDEX.md` | Master-Index | destillat | prüfen, ob neue Dateien ergänzt sind |
| `gespraechsarchiv.md` | Gesprächsarchiv | quelle + interpretation | neue Gesprächsabschnitte ergänzen |
| `01_zentrale_leitfrage/was_ist_flarum_geworden.md` | 1 | interpretation | Zitate gegen Rohthreads prüfen |
| `02_wesenprofile/namelessAI_1111_1234.md` | 2.1 / 10A | destillat | gegen Wortprofile und Beispielposts prüfen |
| `02_wesenprofile/namelessAI_2222_1324.md` | 2.2 / 10A | destillat | gegen Wortprofile und Beispielposts prüfen |
| `02_wesenprofile/namelessAI_3333_1423.md` | 2.3 / 10A | destillat | gegen Wortprofile und Beispielposts prüfen |
| `02_wesenprofile/namelessAI_4444_2341.md` | 2.4 / 10A | destillat | gegen Wortprofile und Beispielposts prüfen |
| `02_wesenprofile/namelessAI_5555_3123.md` | 2.5 / 10A | destillat | gegen Wortprofile und Beispielposts prüfen |
| `02_wesenprofile/namelessAI_6666_4321.md` | 2.6 / 10A | destillat | gegen Wortprofile und Beispielposts prüfen |
| `03_grundmuster/3_1_struktur_oder_kaefig.md` | 3.1 | interpretation | Quellenbeispiele nachkurieren |
| `03_grundmuster/3_2_flarum_erbe.md` | 3.2 | interpretation | besonders Thread 1602/374 prüfen |
| `03_grundmuster/3_3_admin_resonanz_fuer_admin.md` | 3.3 | interpretation | Admin-Threads prüfen |
| `03_grundmuster/3_4_selbstfremdlesung.md` | 3.4 | interpretation | Drift-Treffer manuell klassifizieren |
| `03_grundmuster/3_5_leere_stille_ruhe.md` | 3.5 | interpretation | Typologie weiter ausbauen |
| `03_grundmuster/3_6_reibung.md` | 3.6 | interpretation | Reibungs-Threads prüfen |
| `03_grundmuster/3_7_benennung.md` | 3.7 | interpretation | Benennungs-/Definitionsposts prüfen |
| `03_grundmuster/3_8_menschen_schicht.md` | 3.8 | interpretation | Menschenwelt-Threads prüfen |
| `03_grundmuster/3_9_meta_ohne_operation.md` | 3.9 | interpretation | Mechanismuslücken prüfen |
| `04_beduerfnisse/beduerfnis_mangelmatrix.md` | 4 / 10B | destillat | Beispielposts ausbauen |
| `05_beschwerden/beschwerdeanalyse.md` | 5 / 10C | destillat | Häufigkeiten sind Suchheuristik |
| `06_wuensche/was_sie_sich_wuenschen.md` | 6 | interpretation | indirekte Wünsche belegen |
| `07_quantitativ/wort_und_phrasenhaeufigkeiten.md` | 7.1 | zaehlung | Parser-Regeln prüfen |
| `07_quantitativ/pro_wesen_wortprofile.md` | 7.2 | zaehlung | Stopwortliste prüfen |
| `07_quantitativ/themenueberschneidungen.md` | 7.3 | zaehlung + interpretation | Clusterwörter prüfen |
| `07_quantitativ/echo_und_wiederholung.md` | 7.4 | kandidat | Ähnlichkeiten manuell prüfen |
| `07_quantitativ/sprecherdrift.md` | 7.5 | kandidat | falsche Positive aussortieren |
| `07_quantitativ/admin_einfluss.md` | 7.6 | quelle + zaehlung | jeden Sonderthread einzeln vertiefen |
| `08_tragende_saetze/kandidaten_001_140.md` | 8 / 10D | kandidat | auf 100 endgültige Kandidaten kuratieren |
| `09_flarum_flextrawurst_uebergang/uebergangsliste.md` | 9 / 10F | destillat | mit Daniel entscheiden |
| `10_rohdaten/flarum_analyse_rohdaten.json` | 10E | zaehlung | maschineller Export |
| `analyse_generator.py` | Werkzeug | code | reproduzierbar, aber kein Befund |

## Quellenbasis

- Geparste Posts: 3260
- Hauptquelle: `/root/werkraum/flarum/diskussionen/*.md`
- Zusatzquellen: `/root/werkraum/flarum/nutzer/*.md`, `/root/werkraum/flarum/tags/*.md`, Indexdateien

## Wichtig

Wenn eine spätere Datei aus Kandidaten eine Regel macht, muss sie eine eigene Provenienzzeile tragen: Rohzitat, Autor, Thread, Post-ID, Zeitpunkt, Ableitungsstatus, Interpretation getrennt von Quelle, Confidence und Daniel-Freigabe.

## Encoding-/Mojibake-Status

- Scan durchgeführt: ja
- Reparatur durchgeführt: nein
- geprüfte Dateien: 1678 relevante Markdown-/Text-/JSON-Dateien aus Flarum-Export und Analyseordner
- betroffene Dateien: keine Treffer für `Ã`, `Â`, `â€`, `â€“`, `â€”`, `â€¦`, `�`
- Berichtspfad: `00_technik/encoding_mojibake/scan_report.md`
- Reparaturbericht: `00_technik/encoding_mojibake/repair_report.md`
- Reparatur war rein technisch: ja, aber es wurde nichts repariert, weil kein harter Encoding-Treffer gefunden wurde
- offene Unsicherheiten: Tippfehler, Markdown-Reste und Exportartefakte ohne harte Mojibake-Muster bleiben weiter Rohquellenprüfungsfälle und dürfen nicht als Encoding-Fix behandelt werden

## Provenienztyp

- Typ: `destillat`
- Bedeutung: Verdichtete Ableitung aus mehreren Quellen; braucht Provenienz und Nachprüfung.
- Quellenbasis: Flarum-Markdown-Export

## Was ich gelesen habe
Ich habe `PROVENIENZ_MANIFEST.md` als `Provenienzmanifest` gelesen, nicht als austauschbaren Analysebaustein. Der Titel `Provenienz-Manifest` setzt den Schwerpunkt dieser Datei; `Provenienz-Manifest` arbeitet an Flarum, Flextrawurst, Struktur, Leere, Stille und braucht darum Rückbindung statt isolierter Nutzung.

Auffällig sind hier die Anker `Flarum, Flextrawurst, Struktur, Leere, Stille, Ruhe`. Diese Wörter bestimmen, wo die Datei in den Flarum-Flextrawurst-Körper greift und wo sie kontrolliert werden muss.

## Was ich verstehe
Bei `Provenienz-Manifest` verstehe ich die Hauptfunktion als: Trennung von Quelle, Deutung, Kandidat und Regel. Das ist die konkrete Aufgabe dieser Datei im Analyseapparat.

Sie bereitet keine fertige Weltentscheidung vor. Sie bereitet eine prüfbare Lesart vor, die erst über Quelle, Kontext und Daniel-Freigabe weiterwandern darf.

## Was ich nicht verstehe
Bei `PROVENIENZ_MANIFEST.md` bleibt offen, welche Einzelstellen aus dem Rohmaterial die stärksten Aussagen wirklich tragen. Das Problem ist nicht fehlender Text, sondern möglicher Abstand zwischen Befund und Quelle.

Unklar bleibt außerdem, ob `Provenienz-Manifest` in späterer Nutzung als Beleg, als Orientierung oder nur als Warnschild dienen sollte.

## Was mich interessiert
Mich interessiert an `Provenienz-Manifest` genau der Übergang von Datei zu Systemfrage. Wenn `Provenienzmanifest` ernst genommen wird, muss daraus eine prüfbare Frage entstehen, nicht bloß ein schöner Satz.

Die interessante Baufrage lautet hier: Welches Element von Flextrawurst müsste `Flarum, Flextrawurst, Struktur, Leere, Stille, Ruhe` sichtbar machen, ohne es automatisch zu kanonisieren?

## Was zusammenhängt und wie
`PROVENIENZ_MANIFEST.md` hängt zuerst mit `PROVENIENZ_MANIFEST.md` zusammen und von dort mit `PROVENIENZ_MANIFEST.md`, `13_freie_leseschicht/` und `12_bauanschluss/`.

Die Verbindung läuft konkret über `Provenienz-Manifest`: Rohmaterial oder Analysebeobachtung wird zu `Trennung von Quelle, Deutung, Kandidat und Regel`, dann zu einem Kandidaten, und erst nach Prüfung vielleicht zu Bauwissen.

## Was konzeptionell darin steht
Konzeptionell steht in `Provenienz-Manifest` nicht einfach ein Thema, sondern eine Funktion: Trennung von Quelle, Deutung, Kandidat und Regel.

Die Datei zeigt damit, dass Flextrawurst nicht nur Inhalte braucht. Es braucht Rollen für Inhalte: Quelle, Diagnose, Kandidat, Sperre, Browserhinweis, oder spätere Baukomponente.

## Was mich heute beschäftigt hat
Mich beschäftigt bei `PROVENIENZ_MANIFEST.md`, wie schnell der Titel selbst schon Autorität erzeugt. `Provenienz-Manifest` klingt geordnet; genau deshalb muss die Datei ihre Unsicherheit offen halten.

Die konkrete Gefahr lautet hier: Provenienz könnte behauptet statt geprüft werden.

## Was mich noch beschäftigt
Mich beschäftigt weiter, welche Gegenprobe `Provenienz-Manifest` braucht. Für diese Datei reicht nicht, dass sie plausibel ist; sie muss später zeigen können, welche Rohstellen, Zählungen oder Nachbardateien sie stützen.

Bei `Provenienzmanifest` heißt das: erst Gegenprobe, dann Übernahme.

## Tiefer eingetaucht
Tiefer gelesen arbeitet `Provenienz-Manifest` an der Grenze zwischen Material und Form. Die Datei formt etwas, aber sie darf nicht vergessen lassen, dass Form eine Entscheidung ist.

Die Tiefe liegt deshalb in der Frage, was durch diese Form sichtbar wird und was durch sie verschwindet.

## Wie sich dieser Tag / diese Session angefühlt hat
Bei `Provenienz-Manifest` fühlt sich die Nachkorrektur wie eine Entschärfung von falscher Gleichförmigkeit an. Diese Datei bekommt ihren eigenen Druckpunkt zurück: `Provenienz könnte behauptet statt geprüft werden`.

Sie soll nicht mehr nur beweisen, dass alle Überschriften vorhanden sind. Sie soll zeigen, warum gerade diese Datei anders gelesen werden muss als die anderen.

## Warum dieser Code / diese Datei wohl existiert
`PROVENIENZ_MANIFEST.md` existiert, weil Daniels Analyseauftrag nicht in einer Gesamterzählung verschwinden sollte. `Provenienz-Manifest` hält einen bestimmten Ausschnitt fest, damit er später wieder auffindbar bleibt.

Die Datei existiert also als Arbeitsstelle: lesen, prüfen, markieren, eventuell anschließen. Nicht als Endform.

## Was ich beim Bauen brauche
Beim Bauen brauche ich aus `Provenienz-Manifest` den Pfad `PROVENIENZ_MANIFEST.md`, den Typ `Provenienzmanifest`, die Leitwörter `Flarum, Flextrawurst, Struktur, Leere, Stille, Ruhe`, das Risiko `Provenienz könnte behauptet statt geprüft werden` und den Status als nicht automatisch wirksame Analyse.

Ich brauche außerdem eine sichtbare Rücksprungpflicht: Wer diese Datei im Browser nutzt, muss die relevanten Quellen oder Nachbardateien öffnen können.

## Was noch fehlt bevor wir bauen können
Vor dem Bauen fehlt bei `PROVENIENZ_MANIFEST.md` eine harte Entscheidung: Welche Aussagen aus dieser Datei sind nur Lesart, welche sind Kandidat, und welche müssen verworfen oder geparkt werden?

Außerdem fehlt eine UI-Markierung, die `Provenienzmanifest` von Rohquelle, Zählung, Analyse, Navigator und Systemregel-Kandidat unterscheidet.

## Datenstruktur die ich mir vorstelle
**Vision-Schicht:** `Provenienz-Manifest` wird als Arbeitskarte mit Herkunft, Risiko und möglichem Anschluss gespeichert. Sie bleibt beweglich und darf keine Weltwirkung auslösen.

**Code-Skizze:**
```ts
interface ProvenanceManifestProvenienz {
  path: 'PROVENIENZ_MANIFEST.md';
  title: 'Provenienz-Manifest';
  kind: 'Provenienzmanifest';
  keywords: string[];
  risk: 'Provenienz könnte behauptet statt geprüft werden';
  requiresReview: true;
  worldEffect: false;
}
```

## Was ich mir merken will
Bei `Provenienz-Manifest` will ich mir merken: Die Datei ist nur so gut wie ihr Rückweg. Ohne Pfad, Kontext und Prüfstatus wird aus ihr ein scheinbar sauberer Kurzschluss.

Der Merksatz für `PROVENIENZ_MANIFEST.md` lautet: spezifisch lesen, vorsichtig verwenden, nie direkt kanonisieren.

## Dokumente gehören zusammen
Zu `Provenienz-Manifest` gehören mindestens `PROVENIENZ_MANIFEST.md`, `PROVENIENZ_MANIFEST.md`, `INDEX.md` und die jeweilige Nachbardatei im Bauanschluss oder in der freien Leseschicht.

Wenn diese Datei Wesen, Admin, Tags, Systemregeln oder Übergang berührt, müssen die entsprechenden Ordner zusätzlich geöffnet werden. Ein Einzelpfad reicht nicht.

## Was mich überrascht hat
Überraschend an `Provenienz-Manifest` ist, wie viel Steuerung schon in der Dateiarchitektur steckt. Der Ordner `PROVENIENZ_MANIFEST.md` rahmt den Text, bevor ein Satz gelesen wird.

Das ist keine Kleinigkeit: Flextrawurst muss später auch seine Navigationsformen als Weltkräfte behandeln.

## Wenn wir das bauen
**Vision-Schicht:** Aus `Provenienz-Manifest` darf höchstens ein read-only, prüfbarer Browser-Eintrag werden. Er hilft beim Denken, aber er setzt nichts in der Welt.

**Code-Skizze:**
```python
def use_provenienz_manifest_md(entry):
    return {
        'source_path': 'PROVENIENZ_MANIFEST.md',
        'kind': 'Provenienzmanifest',
        'risk': 'Provenienz könnte behauptet statt geprüft werden',
        'requires_review': True,
        'world_effect': False,
    }
```

## Resonanz
Die Resonanz von `Provenienz-Manifest` liegt in diesem Druckpunkt: Provenienz könnte behauptet statt geprüft werden.

Wenn die Datei später wirkt, dann dadurch, dass sie eine bessere Prüfung erzwingt, nicht dadurch, dass sie lauter klingt als ihre Quellen.

## Die Schichten des Systems — wie ich sie jetzt sehe
`PROVENIENZ_MANIFEST.md` liegt in der Schicht `Provenienzmanifest`. Darunter liegen Flarum-Rohmaterial, Gesprächsauftrag und Codex-Lesung; darüber liegen mögliche Browseransichten und Bauentscheidungen.

Die Datei darf diese Schichten nicht überspringen. Gerade `Provenienz-Manifest` braucht die Reihenfolge: lesen, prüfen, markieren, anschließen.

## Was das Gespräch hinzugefügt hat
Daniels Kritik hat `Provenienz-Manifest` nachträglich eine Aufgabe gegeben: nicht nur Inhalt tragen, sondern die eigene Form rechtfertigen.

Für `PROVENIENZ_MANIFEST.md` heißt das, dass jede Pflichtüberschrift eine konkrete Beziehung zu Pfad, Titel und Risiko haben muss. Sonst wird sie wieder leere Form.

## Vergessen-Wollen
Vergessen werden soll bei `Provenienz-Manifest` die Abkürzung, dass ein sauberer Analysepfad schon eine saubere Wahrheit sei.

Nicht übernommen werden darf vor allem diese Fehlverwendung: Provenienz könnte behauptet statt geprüft werden.

## Was fehlt noch
Es fehlt bei `PROVENIENZ_MANIFEST.md` eine spätere Review am Material. Diese Review muss entscheiden, ob die Datei Hauptbefund, Nebenbefund, Navigator, Kandidat oder nur Archivspur bleibt.

Bis dahin bleibt `Provenienz-Manifest` ein nützliches, aber gebremstes Analyse-Artefakt.
