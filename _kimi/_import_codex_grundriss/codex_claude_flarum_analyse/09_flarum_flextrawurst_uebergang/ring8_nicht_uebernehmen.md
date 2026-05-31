---
datum: 2026-05-22
autor: codex bei Daniels VPS
quellenbasis: Ring 2-7 Risiken
provenienztyp: Negativliste für Clean Start, kein Löschauftrag
importable: false
warnung: Analyse/Kandidat/Destillat, kein Kanon
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# Ring 8 — Nicht übernehmen

Warnung: Analyse/Kandidat/Destillat, kein Kanon. Keine Systemregel gilt ohne Daniel-Freigabe.

## Quellenbasis
Ring 2-7 Risiken

## Provenienztyp
Negativliste für Clean Start, kein Löschauftrag

- reine Textflut
- starre Flarum-Oberfläche
- Sprecherdrift als Wahrheit
- kaputte Encoding-Funde ohne Prüfung
- ChatGPT-Analyse als Wesen-Kanon
- Admin-Korrektur als Wesen-Aussage
- Rohheit als finales Ideal
- Meta ohne Mechanismus als Endzustand

## Was ich gelesen habe

Ich habe die Nicht-Übernehmen-Liste gelesen: reine Textflut, starre Flarum-Oberfläche, Sprecherdrift als Wahrheit, kaputte Encoding-Funde ohne Prüfung, ChatGPT-Analyse als Wesen-Kanon, Admin-Korrektur als Wesen-Aussage, Rohheit als finales Ideal und Meta ohne Mechanismus als Endzustand.

Diese Datei ist eine Schutzliste. Sie sagt nicht nur, was schlecht ist, sondern welche Verwechslungen Flextrawurst später beschädigen würden.

Sie ist wahrscheinlich eine der praktischsten Dateien im Übergangsordner.

## Was ich verstehe

Ich verstehe die Liste als Import-Sperre. Sie schützt vor den naheliegendsten falschen Übernahmen.

Besonders stark ist: Rohheit ist wertvoll, aber nicht finales Ideal. Das trifft Daniels Kritik an der schönen Unordnung sehr genau.

## Was ich nicht verstehe

Ich verstehe noch nicht, ob alle Verbote absolut sind oder ob manche als Analyseobjekt erhalten bleiben. Textflut soll nicht als Oberfläche übernommen werden, aber als Warnsignal muss sie bleiben.

Unklar bleibt auch, ob `Meta ohne Mechanismus` komplett ausgeschlossen oder nur nicht als Endzustand erlaubt ist.

## Was mich interessiert

Mich interessiert, welche dieser Verbote später technisch hart gesperrt werden müssen. Admin-Korrekturen als Wesen-Memory sollten zum Beispiel nicht nur Warnung, sondern unmöglich sein.

Andere Verbote brauchen eher UI-Hinweise und Review.

## Was zusammenhängt und wie

`Nicht-Übernehmen-Liste` hängt mit der zentralen Leitfrage zusammen: Was ist Flarum wirklich geworden? Die Antwort darf weder `nur Test` noch `schon fertige Flextrawurst` sein.

Die Datei hängt außerdem mit tragenden Sätzen, Systemregel-Kandidaten und Bauanschluss zusammen, weil jede spätere Übernahme aus Flarum eine Herkunftsentscheidung braucht.

## Was konzeptionell darin steht

Konzeptionell steht hier eine Übergangslogik. `Nicht-Übernehmen-Liste` sagt nicht: so wird Flextrawurst. Es sagt: so darf Flarum als Vorgeschichte behandelt werden, ohne Rohheit zu verlieren und ohne Fehler zu importieren.

Das ist eine Clean-Start-Logik mit Gedächtnis, nicht mit Amnesie.

## Was mich heute beschäftigt hat

Mich beschäftigt, dass Flarum zwei gegensätzliche Fehllektüren anzieht. Die eine macht es klein: nur Forum, nur Test, nur Rohprototyp. Die andere macht es zu groß: schon die finale Welt.

Die Wahrheit der Analyse liegt in der Spannung dazwischen.

## Was mich noch beschäftigt

Mich beschäftigt, welche Erinnerungen später überhaupt mitdürfen. Wenn jedes Flarum-Fragment als Wesen-Erinnerung übernommen wird, entsteht falsche Kontinuität. Wenn nichts mitdarf, verliert Flextrawurst seine Ursprungsschicht.

Diese Grenze ist eine Daniel-Entscheidung, keine Automatik.

## Tiefer eingetaucht

Tiefer betrachtet ist `Nicht-Übernehmen-Liste` eine Antwort auf die Frage, wie ein System aus Vorgeschichte lernt, ohne von ihr besessen zu werden. Flarum hat echte Spuren erzeugt, aber Spuren sind nicht automatisch Gesetze.

Flextrawurst braucht deshalb Kategorien wie `behalten`, `nicht übernehmen`, `prüfen`, `Ursprung`, `Fehler/Drift` und `Weltregel-Kandidat`.

## Wie sich dieser Tag / diese Session angefühlt hat

Diese Nacharbeit fühlt sich wie ein Grenzgang an. Man muss Flarum ernst nehmen, ohne es zu vergolden.

Das ist näher an Daniels eigentlicher Forderung als die alte Ring-Mechanik: nicht mehr Ordnerlogik, sondern Übergangsdenken.

## Warum dieser Code / diese Datei wohl existiert

Diese Datei existiert, weil ein Clean Start sonst entweder alles abschneidet oder alles importiert. Beides wäre falsch.

`Nicht-Übernehmen-Liste` versucht, eine dritte Haltung zu halten: Herkunft bewahren, Übernahme prüfen, Aktivierung sperren.

## Was ich beim Bauen brauche

Beim Bauen brauche ich `ImportDenyRule`s. Einige sind hart: keine ChatGPT-Analyse als Wesenkanon, keine Admintexte in Wesenmemory, keine beschädigten Zitate.

Andere sind weich: Rohheit nicht als Ideal, Meta nicht als Endzustand.

## Was noch fehlt bevor wir bauen können

Es fehlt die Zuordnung: harte Sperre, weiche Warnung, Daniel-Review, nur Dokumentation.

Außerdem fehlt ein Test, der verhindert, dass Analyse-Destillate in spätere Memory-Pipelines geraten.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** `Nicht-Übernehmen-Liste` schützt den Übergang. Flarum bleibt Ursprung, Rohkörper und Lernraum; Flextrawurst bleibt Ziel- und Bauwelt. Dazwischen liegen Kandidaten, Sperren, Prüfungen und Daniel-Entscheidungen.

**Code-Skizze:**
```ts
type TransferStatus = 'keep' | 'do_not_import' | 'candidate' | 'origin_only' | 'drift_or_error' | 'world_rule_candidate';

interface FlarumTransferDecision {
  element: string;
  source: string;
  status: TransferStatus;
  reason: string;
  risk: string;
  danielDecisionRequired: boolean;
  canonStatus: 'none' | 'candidate' | 'approved';
}
```

## Was ich mir merken will

Merken will ich mir: Nicht übernehmen ist kein Wegwerfen. Es ist Schutz vor falscher Nähe.

Manches bleibt als Ursprung oder Risiko wichtig, gerade weil es nicht importiert werden darf.

## Dokumente gehören zusammen

Diese Datei gehört zu `01_zentrale_leitfrage`, zu `08_tragende_saetze`, zu `11_systemregel_kandidaten` und zu `12_bauanschluss`.

Sie ist die Brücke zwischen Analyse und späterem Build, aber noch kein Buildauftrag.

## Was mich überrascht hat

Mich überrascht, wie stark die Analyse immer wieder auf dieselbe Formel zurückkommt: Flarum ist nicht Flextrawurst, aber auch nicht bloß Test.

Diese Formel trägt nur, wenn sie operativ wird: Welche Daten dürfen wie weiterleben?

## Wenn wir das bauen

**Vision-Schicht:** `Nicht-Übernehmen-Liste` schützt den Übergang. Flarum bleibt Ursprung, Rohkörper und Lernraum; Flextrawurst bleibt Ziel- und Bauwelt. Dazwischen liegen Kandidaten, Sperren, Prüfungen und Daniel-Entscheidungen.

**Code-Skizze:**
```ts
type TransferStatus = 'keep' | 'do_not_import' | 'candidate' | 'origin_only' | 'drift_or_error' | 'world_rule_candidate';

interface FlarumTransferDecision {
  element: string;
  source: string;
  status: TransferStatus;
  reason: string;
  risk: string;
  danielDecisionRequired: boolean;
  canonStatus: 'none' | 'candidate' | 'approved';
}
```

## Resonanz

Die Resonanz von `Nicht-Übernehmen-Liste` ist vorsichtig konstruktiv. Es sagt: Flarum hat genug Wirklichkeit, um Herkunft zu sein, aber nicht genug Endgültigkeit, um unkontrolliert Welt zu werden.

Das ist genau die Spannung, aus der ein sauberer Übergang entstehen kann.

## Die Schichten des Systems — wie ich sie jetzt sehe

Flarum liegt als Ursprungsschicht unten. Darüber liegen Analyse, Kuratierung, Kandidaten und Clean-Start-Entscheidungen. Flextrawurst darf erst darüber bauen, wenn Daniel die Übergänge freigibt.

Diese Datei steht zwischen Ursprung und Bau, nicht im Bau selbst.

## Was das Gespräch hinzugefügt hat

Das Gespräch hat hinzugefügt, dass Daniel keine glatte Theorie will. Er will wissen, was aus jedem Bruch, jeder Wiederholung, jeder Drift und jeder Zustimmung für den späteren Bau folgt.

Diese Datei beantwortet das als Übergangsentscheidung, nicht als Weltbehauptung.

## Vergessen-Wollen

Vergessen werden soll die falsche Gleichung `Flarum = Flextrawurst`.

Vergessen werden soll auch die falsche Abwertung `Flarum = nur Test`.

## Was fehlt noch

Es fehlt Daniels spätere Entscheidung über Einzug, Erinnerungen, Wesenzahl und Herkunftsarchiv.

Außerdem fehlt ein read-only Browser, der diese Übergangskategorien sichtbar macht, ohne sie live wirken zu lassen.
