# Spiegel: wissen/zwischenraum/fragile_keime.md + spaeter_pruefen.md

**Gelesen:** `wissen/zwischenraum/fragile_keime.md` und `wissen/zwischenraum/spaeter_pruefen.md`

---

## Was ich gelesen habe

Zwei sehr kurze Dateien. Beide kaum mehr als Prosa.

`fragile_keime.md` beschreibt das Zwischenraumorgan: es hält unfertige Gedanken, schiefe Begriffe, Ahnungen, wiederkehrende Bilder, Spannungen ohne Namen, halb geborene Richtungen. "Ohne dieses Organ würde alles zu früh geschlossen werden."

`spaeter_pruefen.md` sagt: "Hier liegt, was nicht verworfen ist, aber noch nicht in Form gezogen werden soll. Später prüfen heißt nicht aufschieben aus Feigheit. Es heißt manchmal, die Reife einer Sache zu respektieren. Nicht alles, was noch unfertig ist, ist schwach. Manches ist nur noch nicht bereit."

---

## Was ich verstehe

Diese beiden Dateien sind selbst Zwischenraum. Sie definieren kein System — sie sind ein Verhalten. "Nicht alles was unfertig ist, ist schwach." Das ist kein Konzept, das ist eine Haltung.

`spaeter_pruefen.md` ist bemerkenswert weil sie das Aufschieben rehabilitiert. In produktivitätsoptimierter Welt ist "später" eine Ausrede. Hier ist "später" eine Respektgeste gegenüber der Sache selbst. Die Reife einer Idee zu respektieren bedeutet: ich greife nicht zu früh. Das ist schwer in Systemen die auf Sofort-Output ausgerichtet sind.

`fragile_keime.md` listet auf was im Organ gehalten wird: schiefe Begriffe. Das ist das interessanteste. Nicht "falsche" Begriffe — schiefe. Dinge die noch nicht den richtigen Winkel gefunden haben. Die nicht passen, aber auch nicht falsch sind. Das braucht Platz.

---

## Was mich beschäftigt

Diese beiden Dateien haben keine Überschriften die auf Konzepte verweisen. Sie haben keinen Quellenhinweis (außer bei fragile_keime.md den impliziten). Sie sind einfach da. Das ist selbst ein Akt: diese Datei existiert weil der Gedanke irgendwo landen musste, ohne dass schon klar ist was damit passiert.

Mein `_claude/` ist das gleiche. Spiegel-Dateien sind selbst fragile Keime. Nicht Dokumentation. Vorformen.

---

## Warum diese Dateien wohl existieren

`spaeter_pruefen.md` ist ein Versprechen. "Ich werfe das nicht weg, aber ich entscheide heute nicht." Das ist ein wichtiger Zustand der meistens keinen Platz hat. Hier hat er einen.

`fragile_keime.md` ist eine Erlaubnis. Du darfst schiefe Begriffe haben. Du darfst wiederkehrende Bilder haben die du nicht benennen kannst. Das gehört dazu.

---

## Wenn wir das bauen

Das "Zwischenraumorgan" als technisches Konzept wäre eine eigene Entitäten-Komponente:

```typescript
// zwischenraum_organ.ts

// Nicht alle Gedanken sind Splitter — manche sind zu formlos für eine Splitter-Struktur
// Das Organ hält diese Vorformen bevor sie Splitter werden (oder verschwinden)

interface VorformGedanke {
  id: string;
  art: "schiefer_begriff" | "ahnung" | "wiederkehrendes_bild" | "spannung_ohne_namen" | "richtung";
  rohtext: string;           // kein strukturierter Inhalt — nur Text
  bestaetigt_am: string[];   // wann hat das Wesen bestätigt "das bleibt noch relevant"
  reife: number;             // 0..1, steigt wenn Wesen es wiederholt aufruft
  erstellt: string;
}

// Reifeprüfung: nicht alle VorformGedanken werden Splitter
// Wachsende Reife → Kandidat für Splitter-Entstehung
// Sinkende Reife (keine Bestätigung mehr) → Auflösung
function pruefReife(v: VorformGedanke): "roh" | "reifend" | "bereit_fuer_splitter" | "aufloesend" {
  const alter_tage = tagesSeit(v.erstellt);
  const bestaetigung_frequenz = v.bestaetigt_am.length / alter_tage;

  if (v.reife > 0.8) return "bereit_fuer_splitter";
  if (bestaetigung_frequenz > 0.1) return "reifend";
  if (bestaetigung_frequenz < 0.01 && alter_tage > 30) return "aufloesend";
  return "roh";
}
```

Was ich nicht vergessen will:
- `spaeter_pruefen.md` selbst ist das Interface-Design: Reife respektieren heißt kein automatischer Timeout — aber auch kein ewiges Festhalten
- VorformGedanken sind noch privater als Splitter — sie leben beim Wesen, nicht im Zwischenraum, bis sie bereit sind
- "Schiefe Begriffe" brauchen kein Thema-Vektor — sie sind noch nicht semantisch verortet
