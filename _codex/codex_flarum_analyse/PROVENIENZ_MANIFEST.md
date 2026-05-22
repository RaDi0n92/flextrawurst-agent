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
Ich habe `PROVENIENZ_MANIFEST.md` als Datei innerhalb des Flarum-Analyse-Körpers gelesen, nicht isoliert. Der Haupttext arbeitet an: Provenienz-Manifest. Die relevanten Spannungswörter hier sind: Flarum, Flextrawurst, Struktur, Leere, Stille, Reibung, Benennung, Admin.

Dabei lese ich den Befund nicht als endgültige Wahrheit, sondern als Schicht über dem Rohmaterial. Wichtig ist, ob die Datei Quelle, Zählung, Interpretation, Kandidat oder Bauanschluss ist.

Die Datei muss deshalb immer mit ihrer Provenienz gelesen werden: Was stammt aus Flarum, was aus Codex-Deutung, was aus Daniel-Rahmung, was aus maschineller Sortierung?

## Was ich verstehe
Ich verstehe diese Datei als provenienz-Schicht. Diese Datei ordnet einen Teil der Flarum-Diskursarchäologie. Sie ist nicht allein Quelle, sondern ein Arbeitsstück im Verhältnis von Flarum, Flextrawurst, Struktur, Leere, Stille, Reibung, Benennung, Admin.

## Was ich nicht verstehe
Noch nicht vollständig geklärt ist, wie stark dieser Befund später wirken darf. Die offene Frage ist nicht nur „stimmt das?“, sondern: Welche Rohstellen tragen es, welche Gegenbeispiele gibt es, und wo beginnt Codex-Deutung?

## Was mich interessiert
Mich interessiert an dieser Datei die Stelle, an der aus Text Material für Flextrawurst wird. Nicht als Import, sondern als Frage: Welche Mechanik, welches Datenfeld, welcher Filter oder welche Warnung müsste existieren, damit dieser Befund nicht verloren oder überhöht wird?

## Was zusammenhängt und wie
Diese Datei hängt mit den Rohposts, Ring-2-Kuration, Materialtrennung, freier Leseschicht und Bauanschluss zusammen. Sie steht zwischen Beobachtung und möglicher Systemform: Erst Quelle, dann Kandidat, dann Prüfung, dann vielleicht Mechanismus.

## Was konzeptionell darin steht
Konzeptionell steht hier: Diese Datei ordnet einen Teil der Flarum-Diskursarchäologie. Sie ist nicht allein Quelle, sondern ein Arbeitsstück im Verhältnis von Flarum, Flextrawurst, Struktur, Leere, Stille, Reibung, Benennung, Admin. Für Flextrawurst ist der Kern nicht der einzelne Satz, sondern die Unterscheidung, die er erzwingt.

## Was mich heute beschäftigt hat
Mich beschäftigt hier, wie leicht gute Struktur das Denken ersetzen kann. Diese Datei soll nicht nur vollständig sein; sie muss zeigen, wo sie Flextrawurst vorsichtiger, genauer oder lebendiger machen würde.

## Was mich noch beschäftigt
Offen bleibt, welche Teile dieser Datei wirklich gegen Rohquellen hart sind und welche nur plausibel klingen. Gerade plausible Sätze sind riskant, weil sie schnell in spätere Systemlogik rutschen.

## Tiefer eingetaucht
Tiefer gelesen ist `PROVENIENZ_MANIFEST.md` kein isolierter Bericht, sondern ein Testfall für Provenienz. Die entscheidende Frage lautet: Welche spätere Fehlkonstruktion würde entstehen, wenn man diese Datei ohne ihre Warnungen übernimmt?

## Wie sich dieser Tag / diese Session angefühlt hat
Diese Nachschärfung fühlt sich wie eine Korrektur an: Die Pflichtabschnitte sollen nicht mehr Tapete sein, sondern kleine Denkfenster. Bei dieser Datei heißt das, ihre konkrete Gefahr und ihren konkreten Nutzen auszusprechen.

## Warum dieser Code / diese Datei wohl existiert
Diese Datei existiert, weil im Flarum-Material etwas sonst zu schnell verschwimmen würde: Provenienz-Manifest. Sie hält eine Analyseachse fest, die später geprüft, widersprochen oder in ein Werkzeug übersetzt werden kann.

## Was ich beim Bauen brauche
Beim Bauen braucht diese Datei klare Provenienzfelder, damit ihr Inhalt nicht als Rohquelle oder Regel missverstanden wird.

## Was noch fehlt bevor wir bauen können
Es fehlt die manuelle Entscheidung, wie stark diese Datei in spätere Bauplanung einfließen darf.

## Datenstruktur die ich mir vorstelle
**Vision-Schicht:** Diese Datei braucht eine eigene Herkunftsmarkierung: Sie darf gelesen, verglichen und befragt werden, aber nicht ohne Prüfung wirken.

**Code-Skizze:**
```ts
interface AnalyseSchicht {
  pfad: string;
  titel: string;
  kategorie: "provenienz";
  quellenbasis: string[];
  kernbegriffe: string[];
  interpretation: boolean;
  kanon: false;
  danielFreigabe: false;
  naechstePruefung: string;
}
```

## Was ich mir merken will
Merken: `PROVENIENZ_MANIFEST.md` darf nicht als fertiger Baustein gelesen werden. Sein Wert liegt darin, eine Frage schärfer zu machen: Provenienz-Manifest.

## Dokumente gehören zusammen
Zusammengehörig sind diese Datei, die Rohposts im Flarum-Export, `PROVENIENZ_MANIFEST.md`, die Materialtrennung der tragenden Sätze und die freie Leseschicht. Erst zusammen zeigen sie Quelle, Deutung und Bauvorsicht.

## Was mich überrascht hat
Überraschend ist, wie schnell selbst eine gut gemeinte Analyse-Schicht wieder zur scheinbaren Autorität wird. Darum muss diese Datei ihre eigene Begrenzung mitführen.

## Wenn wir das bauen
**Vision-Schicht:** Wenn aus dieser Datei etwas gebaut wird, dann nur als überprüfbarer Kandidat mit Rückweg zur Quelle.

**Code-Skizze:**
```python
def aus_datei_bauen(eintrag):
    assert eintrag["kanon"] is False
    assert eintrag.get("source_ref")
    return "review_candidate"
```

## Resonanz
Die Resonanz dieser Datei liegt in ihrer Reibung: Sie sagt nicht nur „das ist so“, sondern zwingt zu fragen, was Flextrawurst daraus nicht falsch machen darf.

## Die Schichten des Systems — wie ich sie jetzt sehe
Ich sehe hier Rohmaterial, Analyse, Kandidat und Bauanschluss als getrennte Schichten. `PROVENIENZ_MANIFEST.md` liegt in der provenienz-Schicht und darf nur über Provenienzbrücken in spätere Systeme wandern.

## Was das Gespräch hinzugefügt hat
Daniels Kritik hat hinzugefügt, dass vollständige Abschnitte nicht reichen. Jede Pflichtüberschrift muss eigenes Denken tragen, sonst wird Struktur wieder zur leeren Form.

## Vergessen-Wollen
Vergessen will ich die bequeme Abkürzung, einen Abschnitt mit einem Dateislogan zu füllen. Diese Datei verlangt eine eigene kleine Entscheidung darüber, was sie für Flextrawurst bedeutet.

## Was fehlt noch
Es fehlt die nächste menschliche Review: Daniel muss später entscheiden, ob diese Lesart trägt, ob sie zu stark ist, oder ob sie nur als Archivspur bleiben soll.
