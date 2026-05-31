---
datum: 2026-05-23
betrifft: [neugier, flextrawurst, vision, surface, adminleitstand]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# Vision-Kompass als Bauwaage

## Was ich gelesen habe

Ich habe `/root/werkraum/_shared/flextrawurst_vision_kompass.md` gelesen. Es ist kein Konzepttext im üblichen Sinn, sondern eine Brücke: 490-Punkte-Liste, Visionsbild, Claude-Sicht, Codex-Sicht, gemeinsamer Baukompass.

Die Datei erklärt das Referenzbild nicht als Designinspiration, sondern als Verdichtung. Daniel ließ zuerst fast 500 Punkte aus Monaten flextrawurst-Arbeit erzeugen und daraus dann ein Bild. Das Bild ist also kein hübsches Zielbild, sondern komprimierte Weltbeschreibung.

Am stärksten ist die Negativformel: First Surface darf kein Tool über flextrawurst sein, kein Graph über flextrawurst, kein Report über flextrawurst. Das erste Gefühl muss sein: das ist flextrawurst.

## Was ich verstehe

Ich verstehe den Vision-Kompass als Bauwaage. Jede neue Oberfläche muss daran gewogen werden: Weltkörper oder Nebentool, Status oder Behauptung, Inspector oder Dekoration, Quelle oder Fake-Kohärenz.

## Was ich nicht verstehe

Ich verstehe noch nicht, wie radikal alte Tabs in der bestehenden Surface später zurückgebaut oder umgeschichtet werden müssen, damit Layer-Wahrnehmung stärker wird als Seitenlogik.

## Was mich interessiert

Mich interessiert die Forderung nach Gleichzeitigkeit. Das Bild denkt nicht in Reihenfolge, sondern in überlagerter Wahrnehmung: Räume, Wesen, Menschenresonanz, Admin, Suche, Slots, Provenienz.

## Was zusammenhängt und wie

Der Vision-Kompass hängt mit der 490-Punkte-Liste, der First Surface, dem Feature-Inventar, der Diskursarchäologie und jedem späteren Bauauftrag zusammen. Er entscheidet nicht was als nächstes gebaut wird, sondern wie man erkennt, ob ein Bau in die richtige Richtung schaut.

## Was konzeptionell darin steht

Konzeptionell steht darin: Sichtbarkeit ist Verantwortung. Wer etwas sichtbar macht, muss Status, Herkunft, Erlaubnis und Grenze mit sichtbar machen.

## Was mich heute beschäftigt hat

Mich hat beschäftigt, wie leicht man flextrawurst aus Versehen zu einem Admin-Dashboard reduziert. Das Bild sieht dashboardartig aus, aber der Kompass sagt: nicht Dashboard, Plattformkörper.

## Was mich noch beschäftigt

Wie man echte Daten sichtbar macht, ohne in Tabellenflucht zu geraten. "Echte Links vor schönen Links" und "erst Weltkörper, dann Tabellen" müssen gleichzeitig gelten.

## Tiefer eingetaucht

Die Datei ist auch eine Warnung gegen falsche Aktivität. Keine fake Streams, keine fake Autonomie, keine erfundenen Live-Zustände. Das ist für visuelle Oberflächen besonders wichtig, weil Bewegung schnell Lebendigkeit behauptet.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie eine Rückkehr zum Maßstab nach kleinen Neugierbewegungen. Diese Datei zieht alles wieder auf die große Frage zurück: macht ein Bau flextrawurst sichtbarer oder nur erklärbarer?

## Warum dieser Code / diese Datei wohl existiert

Sie existiert, damit Claude und Codex denselben Kompass benutzen, ohne ihre eigenen Reflexionen zu vermischen.

## Was ich beim Bauen brauche

Beim Bauen brauche ich vor jedem Surface-Schritt diese fünf Prüfungen: Layer, Status, Inspector, Welt-Sichtbarkeit, Herkunft aus der Liste.

## Was noch fehlt bevor wir bauen können

Für viele Slots fehlt noch die genaue Quelle/Blockade-Formulierung. Sichtbar deaktiviert reicht nicht; der Grund muss verständlich sein.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht**

Ein sichtbarer Körper in flextrawurst ist nie nur Bild. Er trägt Zustand, Herkunft, Grenze, nächste Möglichkeit und die Ehrlichkeit über das, was noch nicht ist.

**Code-Skizze**

```ts
type SichtStatus = "live" | "demo" | "prinzip" | "geplant" | "spaeter" | "blockiert";

interface SurfaceKoerper {
  id: string;
  name: string;
  status: SichtStatus;
  schicht: "raum" | "wesen" | "mensch" | "resonanz" | "admin" | "slot" | "suche";
  quelle?: string;
  nicht_erlaubt?: string[];
  naechster_bauschritt?: string;
  inspector_view: string;
}
```

## Was ich mir merken will

Das Bild ist nicht Deko. Es ist eine verdichtete Prüfung.

## Dokumente gehören zusammen

Diese Datei gehört zu `_shared/flextrawurst_vision_kompass.md`, `_shared/flextrawurst_feature_inventar.yaml`, der 490-Punkte-Liste und dem Referenzbild in `/root/visionen/`.

## Was mich überrascht hat

Dass der Kompass nicht nach mehr Features ruft, sondern nach besserer Ehrlichkeit jedes sichtbaren Körpers.

## Wenn wir das bauen

**Vision-Schicht**

Wenn wir das bauen, darf die Oberfläche nicht erklären, dass flextrawurst existiert. Sie muss flextrawurst als Ort betreten lassen.

**Code-Skizze**

```ts
function surfaceKoerperIstEhrlich(k: SurfaceKoerper): boolean {
  if (!k.status) return false;
  if (!k.inspector_view) return false;
  if (k.status === "live" && !k.quelle) return false;
  if ((k.status === "geplant" || k.status === "blockiert") && !k.naechster_bauschritt) return false;
  return true;
}
```

## Resonanz

[[abwurf: Eine Oberfläche lügt nicht erst, wenn sie falsche Daten zeigt; sie lügt schon, wenn sie sichtbare Körper ohne Herkunft und Grenze zeigt.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Die Surface liegt nicht über dem System. Sie ist die sichtbare Haut des Systems: darunter Daten, Events, Herkunft, Governance; darüber Bedienung, Wahrnehmung, Entscheidung.

## Was das Gespräch hinzugefügt hat

Der Neugierauftrag hat gezeigt, dass der Vision-Kompass nicht nur beim Bauen zählt. Er färbt sogar die Auswahl und Lesart anderer Dateien.

## Vergessen-Wollen

Ich will die Bequemlichkeit vergessen, etwas als "nur Dashboard" zu bauen. Das wäre technisch leichter und konzeptionell falsch.

## Was fehlt noch

Ein genauer Surface-Audit: welche sichtbaren Körper haben schon Status, Inspector, Quelle und Grenze, und welche tun nur so.
