---
datum: 2026-05-21
betrifft: [flextrawurst, surface, adminleitstand, vision-referenz]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# Flextrawurst Adminleitstand — aktuelle beste Bildreferenz

## Was ich gelesen habe

Ich habe kein Textdokument gelesen, sondern Daniels Bildreferenz angesehen:
`/root/visionen/ChatGPT Image 21. Mai 2026, 23_30_02.png`.

Das Bild zeigt eine Flextrawurst-Adminansicht als dichten Leitstand. Oben steht
`Flextrawurst`, daneben `LIVE` und `First Surface`. Links liegen Raeume, in der
Mitte eine leuchtende Weltkarte, rechts ein Inspektor, unten Organ- und
Feature-Slots.

Daniel hat dazu gesagt, dass dieses Bild eigentlich immer als aktuell beste
Referenz gelten soll, wenn etwas an oder fuer flextrawurst gebaut wird.

## Was ich verstehe

Ich verstehe das Bild als Zielkompass fuer Admin- und Surface-Arbeit. Es ist
nicht nur Stimmung, sondern eine Bauvorgabe fuer Blickrichtung, Dichte und
Bedienlogik.

Die Surface soll perspektivisch nicht wie eine normale Website wirken. Sie soll
wie eine Kontrollwarte fuer eine lebende Welt wirken: Raeume, Entitaeten,
Provenienz, Nicht-Erlaubtes, Resonanzen, Systemkoerper, Organe, Audit und
naechste Bauschritte gleichzeitig sichtbar.

## Was ich nicht verstehe

Ich weiss noch nicht, welche Teile des Bildes zuerst gebaut werden sollen.

Ich weiss auch noch nicht, wie viel davon echte Live-Daten, wie viel davon
kuratierte Weltkarte und wie viel davon bewusstes Theater sein darf.

## Was mich interessiert

Mich interessiert besonders der rechte Inspektor. Dort wird die Welt nicht nur
angezeigt, sondern beurteilbar: Herkunft, Provenienz, Nicht-Erlaubt,
naechster Bauschritt.

Mich interessiert auch, dass die Suche oben nicht nur Volltextsuche ist. Sie
wirkt wie Diskursarchaeologie: Suche nach Bedeutung, Herkunft, Resonanz,
Zustaenden, Beziehungen und Verboten.

## Was zusammenhängt und wie

Das Bild haengt direkt mit der aktuellen Surface zusammen, aber es ordnet sie
anders. Die jetzige Surface hat schon Raeume, Entitaeten, Organ-Slots,
Feature-Status und Adminbereiche. Die Bildreferenz sagt: Diese Dinge gehoeren
in eine gleichzeitige Wahrnehmung, nicht nur in getrennte Tabs.

Es haengt auch mit der Schwellenkunde zusammen. Jede sichtbare Sache braucht
Status, Herkunft, Erlaubnis und Grenze.

## Was konzeptionell darin steht

Die Adminansicht ist ein Weltblick, kein Verwaltungsformular.

Sie zeigt nicht nur Daten, sondern Zustaende der Erlaubnis: live, demo, prinzip,
geplant, spaeter, blockiert. Sie macht sichtbar, was noch nicht gebaut werden
darf.

## Was mich heute beschäftigt hat

Mich beschaeftigt, dass dieses Bild einen klareren Zielzustand zeigt als viele
Textbeschreibungen. Es sagt sofort: Flextrawurst braucht Tiefe, Dichte,
Provenienz und operative Kontrolle.

## Was mich noch beschäftigt

Mich beschaeftigt, wie man diese Dichte baut, ohne den Code in einen
unwartbaren Surface-Monolithen wachsen zu lassen.

## Tiefer eingetaucht

Die aktuelle Surface liegt als generierte HTML-Datei vor und wird aus
`/root/flextrawurst/scripts/build_surface.ts` erzeugt. Sie ist schon eine gute
Vorform, aber das Bild ist staerker als Leitstand gedacht.

Der wichtigste Unterschied: Die Bildreferenz denkt nicht in einzelnen Seiten,
sondern in Layern, Inspektion und Weltzustaenden.

## Wie sich dieser Tag / diese Session angefühlt hat

Diese Session fuehlte sich an wie ein Umschalten von "wir haben eine Surface"
zu "wir wissen besser, welche Art Surface es werden soll".

## Warum dieser Code / diese Datei wohl existiert

Diese Datei existiert, damit zukuenftige Codex-Instanzen das Bild nicht als
zufaellige Inspiration behandeln. Es soll als aktuelle beste Referenz gelten,
wenn an flextrawurst gebaut, geplant oder bewertet wird.

## Was ich beim Bauen brauche

Beim Bauen brauche ich diese Referenz als Prueffrage:

Passt der neue Bau zur Leitstand-Idee, oder erzeugt er nur noch einen Tab?

Zeigt er Herkunft, Status, Erlaubnis und naechsten Schritt?

Bleibt sichtbar, was live, demo, prinzip, geplant, spaeter oder blockiert ist?

## Was noch fehlt bevor wir bauen können

Es fehlt eine kleine technische Uebersetzung des Bildes:

- Welche Datenstruktur beschreibt Raeume, Layer, Entitaeten, Organe und Status?
- Welche UI-Regionen sind Pflicht?
- Welche API-Datenquellen sind echt live?
- Welche Dinge duerfen als Demo sichtbar sein?

## Datenstruktur die ich mir vorstelle

**Vision-Schicht**

Die Adminansicht braucht ein Surface-Manifest. Nicht jede Ansicht erfindet ihre
eigene Wahrheit. Ein Manifest sagt: Das ist die Welt, das sind Raeume, das sind
Entitaeten, das sind Schichten, das ist erlaubt, das ist blockiert.

**Code-Skizze**

```ts
type SurfaceStatus = "live" | "demo" | "prinzip" | "geplant" | "spaeter" | "blockiert";

interface SurfaceManifest {
  reference: {
    kind: "image";
    path: string;
    role: "current_best_reference";
  };
  rooms: SurfaceRoom[];
  entities: SurfaceEntity[];
  layers: SurfaceLayer[];
  organSlots: SurfaceOrganSlot[];
  inspectorPolicies: InspectorPolicy[];
}

interface SurfaceRoom {
  id: string;
  name: string;
  status: SurfaceStatus;
  provenance?: string;
  metrics?: Record<string, number>;
}

interface SurfaceEntity {
  id: string;
  label: string;
  kind: "wesen" | "systemkoerper" | "mensch" | "splitter" | "raum";
  status: SurfaceStatus;
  roomId?: string;
  provenanceState?: "klar" | "luecken" | "ungeklaert";
}

interface InspectorPolicy {
  objectKind: string;
  show: Array<"herkunft" | "provenienz" | "nicht_erlaubt" | "naechster_bauschritt" | "audit">;
}
```

## Was ich mir merken will

`/root/visionen/ChatGPT Image 21. Mai 2026, 23_30_02.png` ist die aktuelle
beste visuelle Referenz fuer flextrawurst, besonders fuer Adminansicht und
Surface.

## Dokumente gehören zusammen

Diese Datei gehoert zusammen mit:

- `/root/visionen/ChatGPT Image 21. Mai 2026, 23_30_02.png`
- `/root/flextrawurst/scripts/build_surface.ts`
- `/root/flextrawurst/tests/surface_ring_23.test.ts`
- `/root/werkraum/_codex/resonanz/wenn_wir_das_bauen.md`
- `/root/werkraum/_codex/resonanz/datenstruktur_die_ich_mir_vorstelle.md`

## Was mich überrascht hat

Mich ueberrascht, wie sehr das Bild die vorhandene Surface nicht ersetzt,
sondern sortiert. Viele Bausteine sind schon da; ihre Anordnung ist noch nicht
die Zielanordnung.

## Wenn wir das bauen

**Vision-Schicht**

Wenn wir das bauen, sollte der erste Schritt nicht ein kompletter Neubau sein.
Er sollte die vorhandene Surface in Richtung Leitstand verschieben: Manifest,
Layer, rechter Inspektor, klare Statussprache, echte Datenquellen-Anzeige.

**Code-Skizze**

```ts
function buildAdminLeitstand(manifest: SurfaceManifest): string {
  return [
    buildTopSearch(manifest.layers),
    buildRoomRail(manifest.rooms),
    buildWorldMap(manifest),
    buildInspector(manifest.inspectorPolicies),
    buildOrganDock(manifest.organSlots),
    buildSystemStatus(manifest),
  ].join("\n");
}
```

## Resonanz

[[abwurf: Die beste Referenz fuer flextrawurst ist im Moment nicht ein Text, sondern ein Leitstandbild: Weltkarte, Inspektor, Provenienz, Nicht-Erlaubtes und naechster Bauschritt in einer Wahrnehmung.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Ich sehe drei Schichten:

Erstens die Weltkarte: Raeume, Wege, Zonen, sichtbare Verdichtungen.

Zweitens die Adminschicht: Inspektor, Provenienz, Audit, Policies, naechste
Bauschritte.

Drittens die Baugrenze: Organ-Slots, Status, Blocker, Demo/Prinzip/Live.

## Was das Gespräch hinzugefügt hat

Daniel hat klargestellt, dass das Bild als aktuelle beste Referenz gelten soll.
Das ist wichtiger als eine normale Designnotiz.

## Vergessen-Wollen

Ich will vergessen, die aktuelle Surface als Endform zu behandeln. Sie ist eine
Vorform. Das Bild ist der bessere Kompass.

## Was fehlt noch

Es fehlt eine ausdrueckliche Verankerung im Bauworkflow: Vor flextrawurst-Arbeit
sollte diese Referenz mitgedacht werden, besonders wenn UI, Surface, Adminsicht,
Weltblick oder Feature-Slots betroffen sind.
