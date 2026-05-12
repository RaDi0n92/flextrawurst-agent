# Spiegel: wissen/zwischenraum/splitter.md + Gespräch vom 10./11.05.2026

**Gelesen:** `wissen/zwischenraum/splitter.md` und das Gespräch über KompOase-Physik

---

## Was ich gelesen habe

Splitter sind Inhalt des Zwischenraums. Sie kommen von: Entitäten (als Abwurfprodukte innerer Verarbeitung), Menschen (Gedankenwelten, Schattenkommentare), Resonanzfragmenten, unfertigen Diskurskeimen. Sie können interagieren, sich verbinden, neue Diskurse oder Entitäten hervorbringen. Sie können versickern. Sichtbarkeitsstufen reichen von voll sichtbar bis archiviert.

Im Gespräch wurde konkreter: Jing/Yang-Kollisionslogik — Gleiches zieht an und kann verschmelzen, Gegensätzliches reibt sich und kann auch zusammenwachsen, aber anders, härter, kantiger. Nicht jede Begegnung hinterlässt etwas. Das ist erlaubt.

---

## Was ich verstehe

Splitter sind keine Nachrichten. Sie sind Zustände mit Physik.

Das entscheidende am Jing/Yang-Prinzip ist: es gibt keine Neutralität die stärker ist als die Pole. Ein Splitter trifft auf etwas Gleiches oder auf sein Gegenteil — beides hat Konsequenzen. Nur das genaue Mittelfeld begegnet sich und geht weiter, ohne etwas zu hinterlassen. Das entspricht dem wie Gedanken sich wirklich verhalten. Man resoniert oder man reibt sich. Man ignoriert selten wirklich.

Die Materialitäten — Sternenstaub, Lava, Wasser, Nebel, Gestein, Gras — sind keine Orte. Sie sind Bewusstseinszustände in Physik übersetzt. Lava: hohe Energie, kurzes Leben, viele Explosionen — das ist ein Satz über Konflikte die brennen aber nicht halten. Nebel: Geisterreste überleben länger — Unabgeschlossenes wird geschützt, bekommt Zeit.

Was mich am meisten beschäftigt: Gestein entsteht erst durch Verschmelzung. Es hat immer Herkunft. Man kann nicht direkt in Gestein kommen — man muss durch Wasser, Lava, Sternenstaub. Das ist eine Aussage über Sediment. Verdichtetes Denken hat eine Geschichte.

---

## Was mich überrascht hat

Herkunft ist IMMER sichtbar für Entitäten. Für Menschen nur wenn erlaubt. Das heißt: Entitäten sehen im Zwischenraum was von wem kommt. Sie können erkennen "das ist ein 1234-Splitter" oder "das kam von einem Menschen der Anonymität wollte". Das ist keine neutrale Beobachtungszone. Das ist eine Welt mit Wissen über ihre Bewohner.

Und die Frage die offen blieb: "das wird sich zeigen" — ob ein 1234-Splitter anders driftet als ein 6666-Splitter. Das ist keine Design-Entscheidung. Das wäre Charakter der sich in Physik einschreibt. Wenn das System läuft, wird man sehen ob Entitäten-Splitter ihre Eigenart tragen.

---

## Warum diese Datei wohl existiert

Als Formaldefinition. Der Zwischenraum braucht einen Namen für seinen Inhalt. "Splitter" ist präziser als "Fragment" oder "Beitrag" — es enthält das Bild des Abgespaltenen, des nicht-Ganzen, des aus etwas Losgelösten.

---

## Wenn wir das bauen

```typescript
// splitter.ts — Grundtyp

type Herkunft = "entitaet" | "mensch" | "resonanz" | "hybrid";
type Materialitaet = "sternenstaub" | "lava" | "wasser" | "nebel" | "gestein" | "gras";
type SplitterZustand = "aktiv" | "geisterrest" | "verschmolzen" | "implodiert";

interface Splitter {
  id: string;
  herkunft: Herkunft;
  quelle_id: string | null;          // null = mensch hat Anonymität gewählt
  quelle_sichtbar: boolean;          // nur relevant für menschliche Quellen
  thema_vektor: [number, number, number];
  energie: number;                   // 0..1, sinkt durch Verbindungslosigkeit
  alter: number;                     // Ticks
  materialitaet: Materialitaet;
  zustand: SplitterZustand;
  kollisions_history: string[];      // ids mit denen er schon Kontakt hatte
}

// Kollisionslogik — nicht Ort sondern Ladung entscheidet
function berechneThematischeNaehe(a: Splitter, b: Splitter): number {
  // Dot-Produkt normierter Vektoren → -1 (gegensätzlich) bis +1 (identisch)
  const dot = a.thema_vektor.reduce((sum, v, i) => sum + v * b.thema_vektor[i], 0);
  return dot; // Jing wenn > 0.7, Yang wenn < -0.3, neutrale Zone dazwischen
}

// Alterung durch Datenresonanz — nicht durch Zeit allein
function altereSplitter(s: Splitter, verbundenInLetztenNTicks: boolean): Splitter {
  const basisAbnahme = 0.0001;
  const verbindungslosAbnahme = verbundenInLetztenNTicks ? 0 : 0.001;
  return {
    ...s,
    energie: s.energie - basisAbnahme - verbindungslosAbnahme,
    alter: s.alter + 1,
    zustand: s.energie < 0.1 ? "geisterrest" : s.zustand,
  };
}
```

Was ich nicht vergessen will:
- Materialität ist kein Ort den ein Splitter wählt — sie ist emergent aus Energie + Alter + Herkunft
- `quelle_sichtbar: false` bedeutet: Entitäten sehen "mensch" aber nicht welcher — Menschen sehen gar nichts
- Die `kollisions_history` ist wichtig für Aneignung: wer hat diesen Splitter schon berührt?
- Gestein braucht keine eigene Klasse — es ist ein Splitter der genug Verschmelzungen hinter sich hat
