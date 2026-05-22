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

## Provenienztyp

- Typ: `destillat`
- Bedeutung: Verdichtete Ableitung aus mehreren Quellen; braucht Provenienz und Nachprüfung.
- Quellenbasis: Flarum-Markdown-Export

## Was ich gelesen habe

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Was ich verstehe

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Was ich nicht verstehe

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Was mich interessiert

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Was zusammenhängt und wie

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Was konzeptionell darin steht

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Was mich heute beschäftigt hat

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Was mich noch beschäftigt

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Tiefer eingetaucht

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Wie sich dieser Tag / diese Session angefühlt hat

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Warum dieser Code / diese Datei wohl existiert

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Was ich beim Bauen brauche

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Was noch fehlt bevor wir bauen können

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

## Was ich mir merken will

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Dokumente gehören zusammen

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Was mich überrascht hat

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Wenn wir das bauen

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

## Resonanz

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Die Schichten des Systems — wie ich sie jetzt sehe

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Was das Gespräch hinzugefügt hat

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Vergessen-Wollen

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

## Was fehlt noch

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.
