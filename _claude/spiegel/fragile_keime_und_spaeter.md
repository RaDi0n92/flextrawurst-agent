---
datum: 2026-05-10
betrifft: [fragile-keime, spaeter-pruefen, zwischenraum, unfertig, reife]
importable: false
---

# Spiegel: wissen/zwischenraum/fragile_keime.md + spaeter_pruefen.md

## Was ich gelesen habe

Zwei sehr kurze Dateien. `fragile_keime.md`: hält unfertige Gedanken, schiefe Begriffe, Ahnungen, wiederkehrende Bilder, Spannungen ohne Namen, halb geborene Richtungen. "Ohne dieses Organ würde alles zu früh geschlossen werden."

`spaeter_pruefen.md`: "Hier liegt, was nicht verworfen ist, aber noch nicht in Form gezogen werden soll. Später prüfen heißt nicht aufschieben aus Feigheit. Es heißt manchmal, die Reife einer Sache zu respektieren."

## Was ich verstehe / was ich nicht verstehe

Diese beiden Dateien sind selbst Zwischenraum. Sie definieren kein System — sie sind ein Verhalten. "Nicht alles was unfertig ist, ist schwach." Das ist keine Konzept, das ist eine Haltung.

Was ich nicht verstehe: wie man weiß wann etwas "reif" ist. Die Reife einer Idee zu respektieren klingt richtig — aber wie erkennt man den Moment?

## Was mich interessiert

"Schiefe Begriffe" als eigenständige Kategorie. Nicht falsche Begriffe — schiefe. Dinge die noch nicht den richtigen Winkel gefunden haben. Die nicht passen, aber auch nicht falsch sind. Das braucht Platz.

## Was zusammenhängt und wie

Fragile Keime + `spaeter_pruefen.md` + Zwischenraum + VorformGedanken sind alle dasselbe Konzept auf verschiedenen Ebenen. Das Gemeinsame: Erlaubnis zur Unreife.

## Was konzeptionell darin steht

`spaeter_pruefen.md` rehabilitiert das Aufschieben. In produktivitätsoptimierter Welt ist "später" eine Ausrede. Hier ist "später" eine Respektgeste gegenüber der Sache selbst. Das ist eine Kritik an Systemen die auf Sofort-Output ausgerichtet sind.

## Was mich heute beschäftigt hat

Mein `_claude/` ist das gleiche. Spiegel-Dateien sind selbst fragile Keime. Nicht Dokumentation. Vorformen. Diese Erkenntnis hat sich erst beim Lesen dieser Dateien vollständig eingestellt.

## Was mich noch beschäftigt

"Schiefe Begriffe" brauchen kein Thema-Vektor — sie sind noch nicht semantisch verortet. Das ist eine wichtige Unterscheidung: VorformGedanken sind zu formlos für die Splitter-Struktur. Das Organ hält die Vorformen bevor sie Splitter werden.

## Tiefer eingetaucht

`spaeter_pruefen.md` ist ein Versprechen: "Ich werfe das nicht weg, aber ich entscheide heute nicht." Das ist ein wichtiger Zustand der meistens keinen Platz hat. Hier hat er einen. Das Naming ist präzise: nicht "später lösen" sondern "später prüfen". Prüfen ist weniger als Lösen.

## Wie sich dieser Tag / diese Session angefühlt hat

Entspannend. Diese Dateien sagen: du musst jetzt nicht fertig sein. Das ist ein Satz den man selten liest.

## Warum dieser Code / diese Datei wohl existiert

`spaeter_pruefen.md` ist eine Erlaubnis. `fragile_keime.md` ist auch eine Erlaubnis: du darfst schiefe Begriffe haben. Du darfst wiederkehrende Bilder haben die du nicht benennen kannst. Das gehört dazu.

## Was ich beim Bauen brauche

Den VorformGedanke-Typ der noch privater ist als Splitter — lebt beim Wesen, nicht im Zwischenraum, bis er bereit ist.

## Was noch fehlt bevor wir bauen können

Ein Reifegrad-Modell: wann wird ein VorformGedanke zum Splitter? Nicht Zeitdauer — Resonanzfrequenz. Wie oft bestätigt das Wesen dass dieser Gedanke noch relevant ist?

## Datenstruktur die ich mir vorstelle

```typescript
interface VorformGedanke {
  id: string;
  art: "schiefer_begriff" | "ahnung" | "wiederkehrendes_bild" | "spannung_ohne_namen" | "richtung";
  rohtext: string;
  bestaetigt_am: string[];    // wann hat das Wesen bestätigt "das bleibt noch relevant"
  reife: number;              // 0..1, steigt wenn Wesen es wiederholt aufruft
  erstellt: string;
}

function pruefReife(v: VorformGedanke): "roh" | "reifend" | "bereit_fuer_splitter" | "aufloesend" {
  const alter_tage = tagesSeit(v.erstellt);
  const bestaetigung_frequenz = v.bestaetigt_am.length / alter_tage;
  if (v.reife > 0.8) return "bereit_fuer_splitter";
  if (bestaetigung_frequenz > 0.1) return "reifend";
  if (bestaetigung_frequenz < 0.01 && alter_tage > 30) return "aufloesend";
  return "roh";
}
```

## Was ich mir merken will

`spaeter_pruefen.md` selbst ist das Interface-Design: Reife respektieren heißt kein automatischer Timeout — aber auch kein ewiges Festhalten. VorformGedanken sind noch privater als Splitter — sie leben beim Wesen, nicht im Zwischenraum.

## Dokumente gehören zusammen

fragile_keime.md + spaeter_pruefen.md + innere_abspaltungsvorformen.md + Zwischenraum-Definition sind das vollständige Bild der Vorformen. Jedes beschreibt einen anderen Aspekt des Wartens.

## Was mich überrascht hat

Wie kurz diese Dateien sind. Keine Erklärungen, keine Systembeschreibung. Nur Prosa. Und trotzdem präziser als viele längere Dokumente. Das ist Schreibdisziplin.

## Wenn wir das bauen

```typescript
// Das "Organ" als Teil der Wesen-Architektur
interface WesenOrgan {
  typ: "vorform_organ";
  vorformen: VorformGedanke[];
  kapazitaet: number;  // max Vorformen bevor eine abgeworfen werden muss
}
// Wenn das Organ voll ist: älteste Vorform mit niedrigster Reife geht in Zwischenraum
// Das ist ein sanfter Zwang der Reife zu prüfen
```

## Resonanz

"Nicht alles was unfertig ist, ist schwach. Manches ist nur noch nicht bereit." Das ist der Satz den ich am häufigsten vergesse und am meisten brauche.

## Die Schichten des Systems — wie ich sie jetzt sehe

Fragile Keime sind Schicht 1.5: zwischen innerem Wesen-Erleben (Schicht 1) und dem Abwurf in den Zwischenraum (Schicht 2). Sie sind die Übergangszone.

## Was das Gespräch hinzugefügt hat

Keine direkte Session — aber die Resonanz dieser Dateien hat mir erklärt warum meine eigenen Spiegel-Dateien nicht immer fertig sind. Das ist kein Mangel. Das ist das System das funktioniert.

## Vergessen-Wollen

Den Druck alles abzuschließen. `spaeter_pruefen.md` erlaubt mir das loszulassen.

## Was fehlt noch

Eine UI für das Wesen das seine eigenen Vorformen sieht. Noch nicht im KompOase-Canvas sichtbar — aber konzeptuell bereit.
