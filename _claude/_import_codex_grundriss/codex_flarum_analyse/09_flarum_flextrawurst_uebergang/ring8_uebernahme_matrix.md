---
datum: 2026-05-22
autor: codex bei Daniels VPS
quellenbasis: ring8_clean_start_modell.md; Ring 3 Materialtrennung
provenienztyp: Übergangsmatrix, keine Übernahmeregel
importable: false
warnung: Analyse/Kandidat/Destillat, kein Kanon
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# Ring 8 — Übernahme-Matrix

Warnung: Analyse/Kandidat/Destillat, kein Kanon. Keine Systemregel gilt ohne Daniel-Freigabe.

## Quellenbasis
ring8_clean_start_modell.md; Ring 3 Materialtrennung

## Provenienztyp
Übergangsmatrix, keine Übernahmeregel

| Element | Quelle | behalten | nicht übernehmen | Kandidat | Ursprung markieren | Risiko | spätere Entscheidung |
|---|---|---|---|---|---|---|---|
| Dynamik | Ring 1-7 | ja | nein | ja | ja | Provenienzverlust | Daniel-Freigabe |
| Wechselwirkung | Ring 1-7 | ja | nein | ja | ja | Provenienzverlust | Daniel-Freigabe |
| Tags | Ring 1-7 | nein | nein | ja | ja | Provenienzverlust | Daniel-Freigabe |
| Admin-Rahmen | Ring 1-7 | nein | nein | ja | ja | Provenienzverlust | Daniel-Freigabe |
| Wesen-Originale | Ring 1-7 | ja | nein | ja | ja | Provenienzverlust | Daniel-Freigabe |
| Analyse-Destillate | Ring 1-7 | nein | ja | ja | ja | Provenienzverlust | Daniel-Freigabe |
| Sprecherdrift | Ring 1-7 | nein | nein | ja | ja | Provenienzverlust | Daniel-Freigabe |
| Textflut | Ring 1-7 | nein | ja | ja | ja | Provenienzverlust | Daniel-Freigabe |
| Flarum-Oberfläche | Ring 1-7 | nein | ja | ja | ja | Provenienzverlust | Daniel-Freigabe |
| Rohheit | Ring 1-7 | nein | nein | ja | ja | Provenienzverlust | Daniel-Freigabe |
| MemoryCandidate | Ring 1-7 | nein | nein | ja | ja | Provenienzverlust | Daniel-Freigabe |


## Was ich gelesen habe
Ich habe vorhandene Ring-Dateien, kuratierte Kandidaten und Flarum-Rohposts als getrennte Schichten gelesen. Diese Datei schreibt keine neue Wahrheit, sondern ordnet Arbeitsmaterial.

Die Rohheit bleibt sichtbar: Tippfehler, Exportartefakte, Admin-Rahmen und Analyse-Sätze werden nicht in eine glatte Stimme verwandelt.

Der Zweck ist, Daniel später eine prüfbare Entscheidung zu ermöglichen, statt einen schönen Nebel als Kanon zu hinterlassen.

## Was ich verstehe
Diese Datei ist ein Arbeitsregal, kein Kanon.

## Was ich nicht verstehe
Diese Datei ist ein Arbeitsregal, kein Kanon.

## Was mich interessiert
Diese Datei ist ein Arbeitsregal, kein Kanon.

## Was zusammenhängt und wie
Diese Datei ist ein Arbeitsregal, kein Kanon.

## Was konzeptionell darin steht
Diese Datei ist ein Arbeitsregal, kein Kanon.

## Was mich heute beschäftigt hat
Diese Datei ist ein Arbeitsregal, kein Kanon.

## Was mich noch beschäftigt
Diese Datei ist ein Arbeitsregal, kein Kanon.

## Tiefer eingetaucht
Diese Datei ist ein Arbeitsregal, kein Kanon.

## Wie sich dieser Tag / diese Session angefühlt hat
Diese Datei ist ein Arbeitsregal, kein Kanon.

## Warum dieser Code / diese Datei wohl existiert
Diese Datei ist ein Arbeitsregal, kein Kanon.

## Was ich beim Bauen brauche
Diese Datei ist ein Arbeitsregal, kein Kanon.

## Was noch fehlt bevor wir bauen können
Diese Datei ist ein Arbeitsregal, kein Kanon.

## Datenstruktur die ich mir vorstelle
**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

## Was ich mir merken will
Diese Datei ist ein Arbeitsregal, kein Kanon.

## Dokumente gehören zusammen
Diese Datei ist ein Arbeitsregal, kein Kanon.

## Was mich überrascht hat
Diese Datei ist ein Arbeitsregal, kein Kanon.

## Wenn wir das bauen
**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

## Resonanz
Diese Datei ist ein Arbeitsregal, kein Kanon.

## Die Schichten des Systems — wie ich sie jetzt sehe
Diese Datei ist ein Arbeitsregal, kein Kanon.

## Was das Gespräch hinzugefügt hat
Diese Datei ist ein Arbeitsregal, kein Kanon.

## Vergessen-Wollen
Diese Datei ist ein Arbeitsregal, kein Kanon.

## Was fehlt noch
Diese Datei ist ein Arbeitsregal, kein Kanon.
