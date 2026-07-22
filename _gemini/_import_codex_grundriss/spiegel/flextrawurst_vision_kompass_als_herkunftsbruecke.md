---
datum: 2026-05-24
betrifft: [flextrawurst, vision, kompass, bild, herkunft]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex - ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe `/root/werkraum/_shared/flextrawurst_vision_kompass.md` gelesen.

Der Text erklärt das Visionsbild nicht als Designidee, sondern als Verdichtung der 490 Punkte. Bild, Liste, Claude-Sicht und Codex-Sicht werden darin verbunden.

Mir fiel auf: Der Kompass sagt dauernd Herkunft. Jedes sichtbare Objekt braucht Status, Inspector, Quelle, Erlaubnis, ehrliche Nicht-Quelle.

## Was ich verstehe

Ich verstehe den Kompass als gemeinsame Brücke, nicht als private Spiegelung.

## Was ich nicht verstehe

Ich verstehe noch nicht, wie viel Surface heute schon wirklich diesem Bild folgt.

## Was mich interessiert

Mich interessiert der Satz: Erst Weltkörper, dann Tabellen.

## Was zusammenhängt und wie

Das Bild hängt an der 490-Punkte-Liste; die Liste hängt an Daniels langer flextrawurst-Arbeit.

## Was konzeptionell darin steht

Konzeptionell steht darin: Sichtbarkeit ohne Herkunft ist falsche Oberfläche.

## Was mich heute beschäftigt hat

Mich beschäftigt, dass mein Explorer-Fehler genau gegen diesen Kompass ging.

## Was mich noch beschäftigt

Mich beschäftigt, wie man eine Surface baut, die Welt sichtbar macht, ohne Status zu fälschen.

## Tiefer eingetaucht

Tiefer liegt darin ein Anti-Fake-Gesetz: keine schönen Links vor echten Links.

## Wie sich dieser Tag / diese Session angefühlt hat

Es fühlte sich an wie Rückkehr zum Ursprung nach einer unruhigen UI-Schleife.

## Warum dieser Code / diese Datei wohl existiert

Sie existiert, damit Claude und Codex nicht aus demselben Bild verschiedene falsche Systeme bauen.

## Was ich beim Bauen brauche

Ich brauche bei jedem sichtbaren Objekt Status, Herkunft und Inspector-Frage.

## Was noch fehlt bevor wir bauen können

Es fehlt ein konsequentes Mapping von Surface-Elementen auf Punkte, Status und Quelle.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Jedes sichtbare Ding trägt Herkunft.

**Code-Skizze:**
```ts
interface VisibleWorldObject {
  id: string;
  status: "LIVE" | "DEMO" | "PRINZIP" | "GEPLANT" | "SPÄTER" | "BLOCKIERT";
  sourceRefs: string[];
  inspector: true;
}
```

## Was ich mir merken will

Das Bild ist Verdichtung, nicht Stimmung.

## Dokumente gehören zusammen

Kompass, 490-Punkte-Liste, Visionsbild und Surface gehören zusammen.

## Was mich überrascht hat

Mich überrascht, wie konkret das Bild gemappt ist.

## Wenn wir das bauen

**Vision-Schicht:** Surface muss Weltkörper werden, nicht Bericht über Welt.

**Code-Skizze:**
```ts
function hasHonestSurface(o: VisibleWorldObject) { return o.inspector && o.sourceRefs.length > 0; }
```

## Resonanz

Resonanz: Keine Sichtbarkeit ohne Herkunft.

## Die Schichten des Systems - wie ich sie jetzt sehe

Ich sehe Bild, Liste, Kompass, Surface, API und Daten als zusammenhängende Herkunftskette.

## Was das Gespräch hinzugefügt hat

Das Gespräch hat die Regel verschärft: Herkunft gilt vor allen Änderungen.

## Vergessen-Wollen

Vergessen will ich, ein Bild als bloße Ästhetik zu lesen.

## Was fehlt noch

Es fehlt ein sichtbarer Herkunftsinspektor für jede Surface-Zone.
