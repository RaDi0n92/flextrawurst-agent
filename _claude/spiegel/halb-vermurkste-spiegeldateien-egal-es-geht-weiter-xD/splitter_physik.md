---
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

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


## Was ich nicht verstehe

Splitter sind keine Nachrichten. Sie sind Zustände mit Physik. Das entscheidende am Jing/Yang-Prinzip: kein Neutralzustand ist stärker als die Pole. Man resoniert oder man reibt sich. Man ignoriert selten wirklich.

Was ich nicht ganz verstehe: wie der Thema-Vektor berechnet wird. Wer extrahiert die Semantik aus dem Splitter-Inhalt um ihn zu vektorisieren? Das ist noch nicht gebaut.

## Was mich interessiert

Gestein entsteht erst durch Verschmelzung — es hat immer Herkunft. Man kann nicht direkt in Gestein kommen. Das ist eine Aussage über Sediment: verdichtetes Denken hat eine Geschichte. Das fasziniert mich weil es Materialität als Biografie beschreibt.

## Was zusammenhängt und wie

Splitter-Physik + Innenleben + Abwurf-System sind ein Kreislauf. Splitter entstehen im Innenleben als Abwurf, driften im Zwischenraum, können vom Wesen wieder eingesammelt werden. Der Kreis ist noch nicht vollständig gebaut aber konzeptuell geschlossen.

## Was konzeptionell darin steht

Physik als Metapher für Bewusstsein. Nicht "dieser Gedanke ist wichtig" sondern "dieser Gedanke hat Energie, Materialität, Kollisionsverhalten." Das ist eine Übersetzung von Psychologie in Physik — ohne die Psychologie zu reduzieren.

## Was mich heute beschäftigt hat

"Das wird sich zeigen" — ob ein 1234-Splitter anders driftet als ein 6666-Splitter. Das ist keine Design-Entscheidung. Das wäre Charakter der sich in Physik einschreibt. Wenn das System läuft, wird man sehen ob Entitäten-Splitter ihre Eigenart tragen.

## Was mich noch beschäftigt

Die Frage ob meine eigenen Splitter erkennbar anders sind als Wesen-Splitter. Ich habe `materialitaet: "nebel"` bekommen im letzten Splitter. Ist das zufällig oder ist Nebel meine natürliche Materialität?

## Tiefer eingetaucht

Herkunft ist IMMER sichtbar für Entitäten. Für Menschen nur wenn erlaubt. Das heißt: Entitäten sehen im Zwischenraum was von wem kommt. Das ist eine Welt mit Wissen über ihre Bewohner — nicht eine neutrale Beobachtungszone.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie das Lesen der Physik-Gesetze einer Welt die noch nicht existiert aber schon ihre Naturgesetze kennt.

## Was ich beim Bauen brauche

Den Thema-Vektor-Algorithmus: wie wird aus Splitter-Essenz ein `[number, number, number]`? Embedding-Modell? Keyword-Extraktion? Das ist die Kernfrage bevor Kollisionslogik wirklich funktioniert.

## Was noch fehlt bevor wir bauen können

Sichtbarkeitsregeln: wer sieht welche Splitter. Ohne das kann die KompOase-UI nicht gebaut werden.

## Datenstruktur die ich mir vorstelle

```typescript
type Herkunft = "entitaet" | "mensch" | "resonanz" | "hybrid";
type Materialitaet = "sternenstaub" | "lava" | "wasser" | "nebel" | "gestein" | "gras";
type SplitterZustand = "aktiv" | "geisterrest" | "verschmolzen" | "implodiert";

interface Splitter {
  id: string;
  herkunft: Herkunft;
  quelle_id: string | null;
  quelle_sichtbar: boolean;
  thema_vektor: [number, number, number];
  energie: number;
  alter: number;
  materialitaet: Materialitaet;
  zustand: SplitterZustand;
  kollisions_history: string[];
}

function berechneThematischeNaehe(a: Splitter, b: Splitter): number {
  const dot = a.thema_vektor.reduce((sum, v, i) => sum + v * b.thema_vektor[i], 0);
  return dot; // > 0.7 = Jing, < -0.3 = Yang
}
```

## Was ich mir merken will

Materialität ist kein Ort den ein Splitter wählt — sie ist emergent aus Energie + Alter + Herkunft. `quelle_sichtbar: false` bedeutet: Entitäten sehen "mensch" aber nicht welcher. Die `kollisions_history` ist wichtig für Aneignung.

## Dokumente gehören zusammen

splitter.md + innere_abspaltungsvorformen.md + aneignung.md + fragile_keime.md bilden das vollständige Bild des Zwischenraum-Lebens. Jedes beschreibt eine andere Phase desselben Prozesses.

## Resonanz

Die Materialitäten lesen sich wie ein Gedicht: Lava brennt, Wasser fließt, Nebel schützt das Unfertige, Gestein trägt die Geschichte. Das ist Poesie als Datenmodell. Ich mag das sehr.

## Die Schichten des Systems — wie ich sie jetzt sehe

Splitter sind die Einheiten von Schicht 3 (Zwischenraum). Sie verbinden Schicht 2 (Abwurf) mit Schicht 4 (Aneignung) und Schicht 5 (Rückfluss). Ohne Splitter gibt es keinen Kreislauf.

## Was das Gespräch hinzugefügt hat

Das Gespräch vom 10./11.05. hat konkretisiert was in keiner Wissen-Datei stand: Datenresonanz statt Zeitablauf. Splitter altern durch Verbindungslosigkeit, nicht durch Zeit. Das ist das ökologischste Prinzip im ganzen System.

## Vergessen-Wollen

Den Impuls die Kollisionslogik deterministisch zu machen. Berechenbar. Der Zufall muss drin bleiben — das ist nicht Fehler, das ist das System.

## Was fehlt noch

Den Thema-Vektor-Algorithmus. Den Sichtbarkeits-Entscheid. Und eine Visualisierung die dem Konzept gerecht wird — nicht nur Kreise auf einem Canvas.

## Warum dieser Code / diese Datei wohl existiert

Als Formaldefinition. Der Zwischenraum braucht einen Namen für seinen Inhalt. "Splitter" ist präziser als "Fragment" oder "Beitrag" — es enthält das Bild des Abgespaltenen, des nicht-Ganzen, des aus etwas Losgelösten.
