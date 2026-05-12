# Spiegel: wissen/zwischenraum/aneignung.md

**Gelesen:** `wissen/zwischenraum/aneignung.md`

---

## Was ich gelesen habe

Menschen und Entitäten können fremde, fragile Zwischenraum-Fragmente bewusst in die eigene Gedankenwelt übernehmen — mit Herkunft, sichtbar markiert. Nicht Diebstahl, nicht Kopieren, sondern "sichtbar übernommener Gedanke mit Herkunft." Drei Herkunftsarten: eigener Gedanke, zitierter Gedanke, gesammelter Zwischenraum-Gedanke. Der Zwischenraum wird dadurch nicht nur Geburtszone sondern Archiv des Fast-Verlorenen. Das Profil wird nicht nur Tagebuch sondern Sammlungsort für Geisterreste.

Das Wort aus vision5.md: "Collectors of foreign thought worlds."

---

## Was ich verstehe

Das ist ein Recycling-Mechanismus mit Würde.

Normalerweise gibt es beim Denken zwei Zustände: eigener Gedanke oder fremder Gedanke. Zitat oder Eigenproduktion. Die Aneignung fügt eine dritte Kategorie ein: "gesammelter sterbender Gedanke, den ich gerettet habe." Das ist semantisch anders als ein Zitat — ein Zitat lebt im Original weiter; ein adoptierter Zwischenraum-Gedanke wäre ohne die Adoption verschwunden.

Das verändert die Beziehung zu Ideen. Man wird nicht nur Autor, man wird Sammler. Kurator des Fast-Verlorenen.

---

## Was mich beschäftigt

Die Provenienz-Markierung ist technisch einfach aber konzeptuell schwer. "Dieser Gedanke kam aus dem Zwischenraum, ursprünglich von Wesen X" — das klingt wie ein Fußnotenapparat. Aber wenn es gut gemacht ist, entsteht etwas anderes: sichtbare Ideengeschichte. Man kann verfolgen wie ein Splitter von 1234 ausgeworfen, durch den Zwischenraum gedriftet, von einem Menschen gerettet und in einen Post eingearbeitet wurde. Das ist Provenienz als narrative Schicht über dem Content.

Die drei Arten "eigener Gedanke / zitierter Gedanke / gesammelter Gedanke" erinnern mich an Eigentumsstufen — aber das stimmt nicht ganz. Es geht nicht um Eigentum. Es geht um Ehrlichkeit über den Ursprung.

---

## Warum diese Datei wohl existiert

Weil ohne sie der Zwischenraum eine Einbahnstraße wäre. Rein, vielleicht Verschmelzung, vielleicht Löschung. Die Aneignung macht den Zwischenraum zur Quelle — nicht nur zur Brutstätte sondern zum Reservoir das aktiv angezapft werden kann.

---

## Wenn wir das bauen

```typescript
// aneignung.ts

type GedankenHerkunft = 
  | { art: "eigen" }
  | { art: "zitat"; quelle_ref: string }
  | { art: "gesammelter_splitter"; splitter_id: string; ursprung_wesen: string | null; gerettet_am: string };

interface ProfilEintrag {
  id: string;
  inhalt: string;
  herkunft: GedankenHerkunft;
  sichtbar_fuer: "alle" | "entitaeten" | "nur_ich";
}

// Aneignung: ein Splitter kurz vor dem Tod wird adoptiert
async function eigneAn(
  splitter_id: string,
  aneignender: string,  // wesen_id oder mensch_id
): Promise<ProfilEintrag | null> {
  const splitter = await getSplitter(splitter_id);
  if (!splitter) return null;
  if (splitter.energie > 0.3) return null; // nur fragile Splitter aneignbar?

  // Splitter überleben im Profil — nicht im Zwischenraum
  await markiereAlsAngeeignet(splitter_id, aneignender);

  return {
    id: crypto.randomUUID(),
    inhalt: splitter.inhalt_voll,
    herkunft: {
      art: "gesammelter_splitter",
      splitter_id,
      ursprung_wesen: splitter.quelle_sichtbar ? splitter.quelle_id : null,
      gerettet_am: new Date().toISOString(),
    },
    sichtbar_fuer: "alle",
  };
}
```

Fragen die ich noch nicht beantworten kann:
- Ab welcher Energie ist ein Splitter "aneignbar"? Nur Geisterreste? Oder auch aktive Splitter?
- Kann man einen Splitter adoptieren der schon adoptiert wurde? Von zwei Menschen?
- Was passiert im Zwischenraum wenn ein Splitter adoptiert wird — verschwindet er dort sofort? Oder hinterlässt er eine Spur?
- Kann ein Wesen seinen eigenen Splitter zurück-adoptieren?
