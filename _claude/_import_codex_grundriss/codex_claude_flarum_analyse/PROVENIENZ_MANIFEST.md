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

Ich habe das Provenienzmanifest gelesen. Es trennt Quelle, Zählung, Interpretation, Kandidat, Destillat und Systemregel-Kandidat und hält den Mojibake-/Encoding-Status fest.

Diese Datei ist die wichtigste Schutzdatei gegen Provenienz-Nebel.

## Was ich verstehe

Ich verstehe: Ohne dieses Manifest werden schöne Sätze, Adminimpulse, ChatGPT-Destillate und Wesenoriginale wieder vermischt.

Das Manifest ist nicht optional; es ist die Bedingung, unter der die Analyse überhaupt nutzbar wird.

## Was ich nicht verstehe

Ich verstehe noch nicht, ob wirklich jede einzelne Datei korrekt im Inventar steht und ob neue Nacharbeitsdateien nachgetragen wurden.

Unklar bleibt auch, ob manche Typen noch feiner getrennt werden müssen.

## Was mich interessiert

Mich interessiert, wie das Manifest später technisch durchgesetzt werden kann. Eine Warnung im Markdown reicht nicht, wenn ein Tool trotzdem alles importiert.

## Was zusammenhängt und wie

`Provenienzmanifest` hängt mit allen Analyseordnern zusammen, aber als Eingangsschicht. Es darf Lesereihenfolge, Status und Warnung geben, aber keine Detailbefunde ersetzen.

Die Datei muss besonders klar auf `PROVENIENZ_MANIFEST.md`, `README_DANIEL_ZUERST_LESEN.md`, `13_freie_leseschicht/` und `08_tragende_saetze/` verweisen.

## Was konzeptionell darin steht

Konzeptionell steht hier Navigation statt Analyse. `Provenienzmanifest` ordnet Wege durch das Material.

Der alte Fehler wäre, Ordnung als Verständnis auszugeben. Die neue Aufgabe ist: Ordnung zeigt, wo Verständnis geprüft werden muss.

## Was mich heute beschäftigt hat

Mich beschäftigt, dass gerade die obersten Dateien Autorität ausstrahlen. Index, Manifest, README und Abschluss klingen fertig.

Darum müssen sie stärker als alle anderen sagen: Einstieg, nicht Wahrheit.

## Was mich noch beschäftigt

Mich beschäftigt, ob Daniel später eher über die freie Leseschicht oder über die Provenienzregale einsteigen will. Beide Wege sind legitim, aber sie beantworten unterschiedliche Bedürfnisse.

Der Navigator muss diese Wahl ermöglichen, nicht erzwingen.

## Tiefer eingetaucht

Tiefer betrachtet ist `Provenienzmanifest` die Schwelle zwischen Mensch und Analysekörper. Wer hier falsch abbiegt, liest entweder nur schöne Deutung oder nur Tabellen.

Eine gute obere Datei muss beides anbieten: Atem und Prüfung.

## Wie sich dieser Tag / diese Session angefühlt hat

Diese Nacharbeit fühlt sich am Ende wie Aufräumen der Eingangstüren an. Nicht neue Räume bauen, sondern Schilder richtig setzen.

Das ist weniger spektakulär als Analyse, aber für Nutzung entscheidend.

## Warum dieser Code / diese Datei wohl existiert

`Provenienzmanifest` existiert, weil die Analyse groß geworden ist. Ohne obere Navigatoren würde Daniel wieder in Ordnern statt in Gedanken landen.

Die Datei existiert also als Orientierung, nicht als Ersatz für die Arbeit darunter.

## Was ich beim Bauen brauche

Beim Bauen brauche ich Provenienztypen als Pflichtfelder im Analyse-Browser.

Kein Datensatz ohne Typ, Quelle, Prüfstatus und `importable: false`.

## Was noch fehlt bevor wir bauen können

Es fehlt eine automatische Validierung: Jede Analyse-Datei muss Frontmatter, Autor, Importstatus und Warnung tragen.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** `Provenienzmanifest` ist eine obere Navigationsschicht. Sie hilft Daniel und Codex, den Analyse-Körper zu betreten, aber sie ersetzt keine Detaildatei und keine Rohquelle.

**Code-Skizze:**
```ts
interface AnalysisNavigator {
  kind: 'Provenienzmanifest';
  primaryUse: 'entry' | 'provenance' | 'archive' | 'stop_point';
  pointsTo: string[];
  canBeSource: false;
  requiresDrilldown: true;
  liveEffect: false;
}
```

## Was ich mir merken will

Merken will ich mir: Provenienz ist nicht Dekoration. Provenienz entscheidet, ob ein Satz benutzt werden darf.

## Dokumente gehören zusammen

Diese Datei gehört zu den Top-Level-Navigatoren und zum Status der manuellen Nacharbeit.

Sie gehört nur indirekt zu Flarum-Rohquellen, weil sie auf Analysepfade zeigt.

## Was mich überrascht hat

Überraschend ist, wie viel Schaden ein schlechter Einstieg machen kann. Wenn oben nicht klar ist, was Quelle, Deutung, Kandidat und Sperre ist, nützt die ganze Detailarbeit wenig.

Der Index ist also selbst ein Provenienzwerkzeug.

## Wenn wir das bauen

**Vision-Schicht:** `Provenienzmanifest` ist eine obere Navigationsschicht. Sie hilft Daniel und Codex, den Analyse-Körper zu betreten, aber sie ersetzt keine Detaildatei und keine Rohquelle.

**Code-Skizze:**
```ts
interface AnalysisNavigator {
  kind: 'Provenienzmanifest';
  primaryUse: 'entry' | 'provenance' | 'archive' | 'stop_point';
  pointsTo: string[];
  canBeSource: false;
  requiresDrilldown: true;
  liveEffect: false;
}
```

## Resonanz

Die Resonanz ist streng. Diese Datei hält den ganzen Körper auseinander, damit er nicht wieder zur Suppe wird.

## Die Schichten des Systems — wie ich sie jetzt sehe

Ganz unten Flarum-Rohmaterial, darüber Analyse und Kuration, darüber freie Leseschicht und Übergänge, darüber diese Navigatoren.

Navigatoren dürfen nach unten führen, aber nicht selbst Fundament spielen.

## Was das Gespräch hinzugefügt hat

Das Gespräch hat hinzugefügt, dass Daniel nicht noch mehr Ringlogik will, sondern nutzbare Orientierung mit ehrlicher Provenienz.

Diese Dateien müssen deshalb knapp führen und klar warnen.

## Vergessen-Wollen

Vergessen werden soll der Reflex, eine Abschlussdatei als Abschluss der Wahrheit zu lesen.

Behalten werden soll: Abschluss heißt Stop-Punkt für Automatik, nicht Ende des Denkens.

## Was fehlt noch

Es fehlt ein finaler Statuscheck über alle Dateien und ein Commit der Top-Level-Nacharbeit.

Danach bleibt inhaltlich immer noch Prüfung durch Daniel offen, aber die manuelle Nachschärfung der heiligen Abschnitte ist als Arbeitsrunde abgeschlossen.
