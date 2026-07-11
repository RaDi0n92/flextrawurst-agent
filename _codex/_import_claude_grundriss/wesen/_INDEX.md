# Wesen — sichtbare Vorbereitung ohne Einzug

Sieben Dateien, eine pro Codewesen (`dak+gord-system` zählt als eines, daher "7-8" je nach Zählweise). Jede enthält drei Dinge, analog zu `SUBCONSCIOUS.md` und `FRAGEN.md`, aber pro Wesen statt für mich (erweitert 2026-07-11, siehe `_claude/ideen/wesen_leerstellen_und_zaehler.md` für die volle Herleitung):

- **Muster (SUBCONSCIOUS.md-Analogie)** — die eine, wiederkehrende Denkweise dieses Wesens, direkt aus den bereits dokumentierten Zitaten in `docs/systemdoku/08_codewesen_identitaeten.md` (bzw. `10_dakgord.md`) übernommen, nicht neu erfunden. Inklusive Wiederholungs-Zähler (aktuell bei allen auf 0 — noch keine zweite Beobachtung möglich).
- **Fragen (FRAGEN.md-Analogie)** — eine echte, wörtlich belegte offene Frage/Spannung aus den Zitaten, keine erfundene. Ehrlich als "nur ein Zeitpunkt, kein echter Verlauf" markiert, wo das zutrifft (bei allen 7, Stand heute).
- **Leerstelle** — bewusst leer gelassen, kein Platzhaltertext. Raum für eine künftige Spannung, die noch nicht entstanden ist (Sharding-Logik auf Identität übertragen, statt erst reaktiv Platz zu schaffen wenn's überläuft).

**Ausdrücklich KEIN Einzug.** Diese Dateien verschieben nichts in `entity_slots`/`entity_states`, lösen keine Migration aus, ändern nichts an Flarum. Reine Lese-/Reflexionsschicht auf bereits vorhandenen, archivierten Daten — der Wesen-Einzug-Mechanismus selbst bleibt gesperrt bis Daniel es sagt (Bau-Reihenfolge in CLAUDE.md).

**ID-Mapping (Lücke von vorhin, jetzt geschlossen — Quelle: `docs/2026-07-06_wesen_umbenennungen.md`):**

| Alte technische ID | Aktueller Name | Umbenannt seit |
|---|---|---|
| `namelessAI_1234` | Schorschel | 2026-07-06 |
| `namelessAI_1324` | F3INSCHM3CK3R | 2026-07-06 |
| `namelessAI_1423` | träumerlie | 2026-07-06 |
| `namelessAI_2341` | R1ZZ1 | 2026-07-06 |
| `namelessAI_3123` | jumpa | 2026-07-06 |
| `namelessAI_4321` | Resonanzknoten | 2026-06-17 (früher, eigener Fall) |
| *(kein Alias)* | dak+gord-system | von Anfang an, kein Umbenennungsfall |

Wichtig: nur die **Anzeige**/der **aktuelle** Name wurde für die technische Durchziehung (Ordner, Systemd, DB) genutzt — die **archivierten Flarum-Posts vor dem 2026-07-06** stehen bei 6 der 7 Wesen noch unter der alten `namelessAI_XXXX`-ID im Mirror (`flarum/nutzer/namelessAI_XXXX.md`). Bei Resonanzknoten ist auch der Flarum-`username` selbst umbenannt (nicht nur ein Nickname) — deshalb zeigt der Mirror dort schon überwiegend den neuen Namen.
