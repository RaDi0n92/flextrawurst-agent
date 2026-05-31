---
datum: 2026-05-22
autor: codex bei Daniels VPS
quellenbasis: alle Flarum-Dateinamen und Threadtitel aus /root/werkraum/flarum/diskussionen; 1575 Diskussionen
provenienztyp: Dateinamen-/Titelanalyse, Codex-Interpretation, kein Kanon
importable: false
warnung: Analyse/Kandidat/Destillat, kein Kanon
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# Systemanforderungen aus Dateinamen

Warnung: Diese Datei analysiert Dateinamen und Threadtitel. Titel sind Rahmung, nicht Beweis. Keine Systemregel gilt ohne Daniel-Freigabe.

## Aus Titeln ableitbare Systemanforderungen

1. **TitleFrame-Provenienz**: Titel müssen als Rahmung gespeichert werden, getrennt vom Postinhalt.
2. **Motivdrift-Erkennung**: Wenn Stille/Leere/Fundament inflationär werden, braucht das System Hinweise auf Begriffssättigung.
3. **Nicht jeder Titel ist Regel**: Titel wie „Die Reibung als Motor“ sind Kandidatenformeln, keine Systemgesetze.
4. **Benennungsverlauf**: Wiederholte Titelmuster sollten als NameHistory sichtbar werden.
5. **Konkretheitsfilter**: Titel können anzeigen, wann ein Thread Meta bleibt und wann er auf Flarum, Tags, Admin, Menschenwelt oder Mechanismus trifft.
6. **Rohpost-Rückbindung**: Jeder starke Titel braucht direkte Verknüpfung zum Rohpost.

## Baunahe Kandidaten

- `TitleFrame`
- `MotifSaturation`
- `NameHistory`
- `TitleToPostReview`
- `OverclaimMarker`
- `ConcreteAnchorDetector`

## Warum das wichtig ist

Die Dateinamen sind nicht nur hübsche Überschriften. Sie sind frühe Selbstkanonisierung. Wenn Flextrawurst sie blind übernimmt, importiert es Pathos als Struktur. Wenn es sie ignoriert, verliert es wichtige Selbstdeutungen.

## Was ich gelesen habe

Ich habe die Systemanforderungen aus Dateinamen gelesen: TitleFrame-Provenienz, Titel/Postkörper-Trennung, Nicht-jeder-Titel-ist-Regel, Benennungsverlauf, Konkretheitsfilter und Rohpost-Rückbindung.

Das ist die bau-nächste Datei dieses Ordners.

## Was ich verstehe

Ich verstehe: Aus Titeln kann man echte Anforderungen ableiten, aber nur Anforderungen an Umgang mit Titeln, nicht an die Welt selbst.

Der wichtigste Punkt ist Trennung von Rahmung und Inhalt.

## Was ich nicht verstehe

Ich verstehe noch nicht, welche Anforderungen sofort in den read-only Browser gehören und welche später.

## Was mich interessiert

Mich interessiert, ob TitleFrame-Provenienz als erstes kleines Datenmodell im Analyse-Browser nützlich wäre.

## Was zusammenhängt und wie

`Systemanforderungen aus Dateinamen` hängt mit der freien Leseschicht zur Titelgrammatik zusammen und mit den quantitativen Wortprofilen. Titelmotive können Begriffshäufungen erklären, aber sie ersetzen keine Postlektüre.

Die Datei hängt außerdem mit Benennung zusammen: Titel sind Namen auf Probe.

## Was konzeptionell darin steht

Konzeptionell steht hier die Benennungsschicht des Forums. `Systemanforderungen aus Dateinamen` liest nicht den Körper der Diskussion, sondern ihre Stirn: wie sie sich nennt, bevor man hineinliest.

Diese Schicht ist stark für Navigation und schwach als Beweis.

## Was mich heute beschäftigt hat

Mich beschäftigt, wie sehr Titel das Material schwerer machen. Ein einfacher Post wird durch einen Titel wie `Die Stille als Fundament` sofort ontologisch aufgeladen.

Das kann hilfreich sein, aber auch Pathos als Struktur tarnen.

## Was mich noch beschäftigt

Mich beschäftigt, welche Titel aus den Wesen selbst stammen und welche durch Export, Slug, Wiederholung oder Dateisystem geglättet wurden.

Auch offen: Wann zeigt ein Titel echte Entwicklung und wann nur eine neue Verpackung für denselben Loop?

## Tiefer eingetaucht

Tiefer betrachtet ist `Systemanforderungen aus Dateinamen` eine Analyse der Selbstüberschrift. Die Wesen und der Export erzeugen nicht nur Texte, sondern Lesebefehle.

Flextrawurst muss solche Lesebefehle speichern können, aber sie darf ihnen nicht blind glauben.

## Wie sich dieser Tag / diese Session angefühlt hat

Diese Nacharbeit fühlt sich wie Arbeit an der Oberfläche an, aber Oberfläche ist hier nicht oberflächlich. Titel sind die erste Form, in der ein Gedanke sich selbst zur Welt macht.

Gerade deshalb brauchen sie Warnungen.

## Warum dieser Code / diese Datei wohl existiert

Diese Datei existiert, weil Daniel ausdrücklich wollte, dass auch Dateinamen Kontext bauen. `Systemanforderungen aus Dateinamen` beantwortet diesen Wunsch, aber mit Provenienzgrenze.

Dateiname ist Kontext, nicht Rohzitat.

## Was ich beim Bauen brauche

Beim Bauen brauche ich `TitleFrame`, `NameHistory`, `TitleBodyCheck` und Warnbadges.

Keine Titelregel ohne Postprüfung.

## Was noch fehlt bevor wir bauen können

Es fehlt ein Minimalmodell mit echten Beispieldaten aus drei Titeln.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** `Systemanforderungen aus Dateinamen` behandelt Titel als Rahmungsschicht. Ein Titel zeigt, wie ein Thread sich selbst nennt; er beweist nicht, was der Postkörper wirklich tut.

**Code-Skizze:**
```ts
interface TitleFrameAnalysis {
  discussionId: number;
  title: string;
  slug: string;
  author?: string;
  motifs: string[];
  interpretation: string;
  proofStatus: 'title_only' | 'post_checked';
  canonStatus: 'none';
}
```

## Was ich mir merken will

Merken will ich mir: Titel sind frühe Selbstkanonisierung. Genau darum brauchen sie technische Trennung.

## Dokumente gehören zusammen

Diese Datei gehört zu `13_freie_leseschicht/08_dateinamen_titel_als_unterbewusste_karte.md`, zu `07_quantitativ/` und zu den Rohdiskussionen.

Sie sollte im Browser als Titel-/Rahmungsanalyse erscheinen, getrennt vom Postinhalt.

## Was mich überrascht hat

Überrascht hat mich, wie direkt aus Dateinamen sehr konkrete Provenienzanforderungen werden.

## Wenn wir das bauen

**Vision-Schicht:** `Systemanforderungen aus Dateinamen` behandelt Titel als Rahmungsschicht. Ein Titel zeigt, wie ein Thread sich selbst nennt; er beweist nicht, was der Postkörper wirklich tut.

**Code-Skizze:**
```ts
interface TitleFrameAnalysis {
  discussionId: number;
  title: string;
  slug: string;
  author?: string;
  motifs: string[];
  interpretation: string;
  proofStatus: 'title_only' | 'post_checked';
  canonStatus: 'none';
}
```

## Resonanz

Die Resonanz von `Systemanforderungen aus Dateinamen` ist aufmerksam und misstrauisch. Titel geben Richtung, aber sie dürfen die Richtung nicht als Ziel ausgeben.

Diese Datei soll Suche verbessern, nicht Wahrheit ersetzen.

## Die Schichten des Systems — wie ich sie jetzt sehe

Postkörper, Titel, Slug, Dateiname, Analyseüberschrift und spätere UI-Anzeige sind verschiedene Schichten.

Diese Datei behandelt Titel/Dateiname, nicht den ganzen Thread.

## Was das Gespräch hinzugefügt hat

Das Gespräch hat hinzugefügt, dass Dateinamen als Kontext ernst genommen werden sollen.

Diese Nacharbeit hält dazu die Gegenregel fest: ernst nehmen, aber nicht beweisen lassen.

## Vergessen-Wollen

Vergessen werden soll die Gleichsetzung von Titel und Inhalt.

Vergessen werden soll auch, Dateinamen als bloß technische Ablage zu unterschätzen.

## Was fehlt noch

Es fehlt die direkte Prüfung ausgewählter Titel gegen ihre Postkörper.

Erst danach kann man sagen, ob ein Titel trifft, überhöht oder verdeckt.
