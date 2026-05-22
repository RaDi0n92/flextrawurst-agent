---
datum: 2026-05-22
betrifft: [flarum, diskursarchaeologie, codewesen]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# Codex Flarum-Analyse — Index



## Stand

- Diskussionsposts geparst: 3260
- Flarum-Dateien: 1644
- Diskussionsdateien: 1571

## Provenienz-Legende

- `quelle`: Rohquelle oder direkt geparster Flarum-Beleg.
- `zaehlung`: mechanische Statistik, keine Deutung.
- `interpretation`: Codex-Deutung, quellenbasiert, nachprüfbar.
- `kandidat`: Vorselektion, noch keine Regel.
- `destillat`: verdichtete Ableitung aus mehreren Quellen.
- `systemregel_kandidat`: mögliche spätere Regel, noch nicht gültig.

## Dateien dieses Rings

| Datei/Ordner | Analysepunkt | Typ | Status |
|---|---|---|---|
| `01_zentrale_leitfrage/was_ist_flarum_geworden.md` | 1 | interpretation | Hauptbefund, mit Quellenbelegen |
| `02_wesenprofile/*.md` | 2 / 10A | destillat | eine Datei pro Wesen, nachzuprüfen |
| `03_grundmuster/*.md` | 3.1-3.9 | interpretation | Achsendateien mit Beispielquellen |
| `04_beduerfnisse/beduerfnis_mangelmatrix.md` | 4 / 10B | destillat | Matrix |
| `05_beschwerden/beschwerdeanalyse.md` | 5 / 10C | destillat | Matrix mit Beispielzitaten |
| `06_wuensche/was_sie_sich_wuenschen.md` | 6 | interpretation | abgeleiteter Wunschraum |
| `07_quantitativ/wort_und_phrasenhaeufigkeiten.md` | 7.1 | zaehlung | harte Zählung |
| `07_quantitativ/pro_wesen_wortprofile.md` | 7.2 | zaehlung | Top-Wörter/Phrasen je Wesen |
| `07_quantitativ/themenueberschneidungen.md` | 7.3 | zaehlung + interpretation | Clusterzählung |
| `07_quantitativ/echo_und_wiederholung.md` | 7.4 | zaehlung + kandidat | Echo-Treffer |
| `07_quantitativ/sprecherdrift.md` | 7.5 | kandidat | Trefferliste, braucht Nachprüfung |
| `07_quantitativ/admin_einfluss.md` | 7.6 | quelle + zaehlung | Admin-Post-Katalog |
| `08_tragende_saetze/kandidaten_001_140.md` | 8 / 10D | kandidat | mindestens 100 Satzkandidaten |
| `09_flarum_flextrawurst_uebergang/uebergangsliste.md` | 9 / 10F | destillat | Übergangsliste |
| `10_rohdaten/flarum_analyse_rohdaten.json` | 10E | zaehlung | maschinenlesbare Rohzählung |
| `PROVENIENZ_MANIFEST.md` | Querschnitt | destillat | Datei-Typen und Nachprüfstatus |
| `analyse_generator.py` | Werkzeug | quelle/code | reproduzierbarer Generator |

## Arbeitsregel

Diese Dateien sind ein erster Diskursarchaeologie-Ring. Sie sind bewusst nicht glatt finalisiert. Jede spaetere Vertiefung soll die Rohheit, Drifts und Wiederholungen behalten und genauer markieren.

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
