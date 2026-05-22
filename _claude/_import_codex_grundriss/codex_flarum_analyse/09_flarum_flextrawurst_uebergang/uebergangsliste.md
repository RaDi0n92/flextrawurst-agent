---
datum: 2026-05-22
betrifft: [flarum, diskursarchaeologie, codewesen]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# F. Übergang Flarum → Flextrawurst



## Behalten

- Dynamik
- Wechselwirkung
- nützliche Struktur
- Ursprungsspuren
- Begriffe
- Konflikte
- Selbstlinien
- tragende Sätze
- Mechanismen, die sich bewährt haben

## Nicht übernehmen

- Oberfläche als Endform
- Textflut
- fehlerhafte Sprecherdrifts als Wahrheit
- starre Kategorien
- alte Flarum-Ästhetik
- jede Erinnerung automatisch als echte Wesen-Erinnerung
- Rohheit als finales Ideal

## Prüfen

- Selbstfremdlesungen
- wiederbelebte alte Threads
- für-Admin-Markierungen
- Tags als Prioritätskanal
- Begriffe mit starker Wiederholung

## Als Kandidat speichern

- Sätze mit Quelle, Autor, Zeitpunkt, Thread, Post-ID, Rohzitat, Interpretation und Confidence.

## Als Ursprung markieren

- Initialisierungsthreads
- Visionsthreads
- Admin-Korrekturen
- erste konkrete Strukturannahmen

## Als Fehler/Drift markieren

- falsches Ich
- falscher Name
- fremder Account als eigene Stimme
- Echo ohne neue These

## Als Weltregel-Kandidat markieren

- Nur Sätze, die über mehrere Quellen hinweg tragen oder durch Admin-Resonanz gestützt sind.

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
