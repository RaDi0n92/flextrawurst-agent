---
id: FW-SKILL-017
status: BESTAETIGT
typ: source
themenraum: SKILL
version: v21
tags: [fragen, load, playwright, save, skill, test, v21, welt]
---

# Gate 13G – Einheitliche Skillpunktökonomie und Legacy-Wirkung

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:docs_v21/GATE_13G_FRAGEN_VORHER_NACHHER.md" sha256="96b7d3e70763a243ff244da37229da95c7910e5d5705799b388d1dfcbc708994" order="1" -->
# Gate 13G – Einheitliche Skillpunktökonomie und Legacy-Wirkung

## Vorbaufragen

1. **Welche Punktequelle hat Daniel gesetzt?** Frei verteilbare Skillpunkte entstehen beim Aufstieg des Gesamtlevels.
2. **Was erzeugt die Benutzung eines einzelnen Baums?** Sie erhöht Gebrauch und Stufe genau dieses Baums und speist dadurch das Gesamtlevel.
3. **Dürfen parallel bauminterne Ausbaupunkte entstehen?** Nein. Zwei Punkteökonomien würden dieselbe Handlung doppelt belohnen und die freie Verteilung unterlaufen.
4. **Was geschieht mit alten Skyrim-artigen Perks wie Fernanker und Windlesen?** Sie bleiben als Knoten im neuen Graphen erhalten und müssen bei globaler Freischaltung weiterhin ihre reale ältere Wirkung auslösen.
5. **Wie werden alte Speicherstände behandelt?** Bereits gesetzte Legacy-Perks werden in den globalen Knotenzustand migriert; nichts wird still gelöscht.
6. **Darf ein Menüzugriff Fortschritt erzeugen?** Nein.
7. **Wie wird das Gate geprüft?** Direkter Playwright-Lauf gegen Punktefluss, Knotenvoraussetzungen, Legacy-API, reale Krallenhakenwirkung und Save/Load.

## Geplanter Bau

- `src/v21_skill_economy_guard.js`
- eine globale Punkteökonomie
- Migration alter Perkzustände
- Wirkungsspiegel zwischen globalen Knoten und älteren Physik-/Weltabfragen
- eigener Playwright-Gate-Test

## Nachbauantworten

1. **Ist nur noch eine Punkteökonomie aktiv?** Ja. Bauminterne `perkPoints` werden auf null normalisiert; frei verteilbare Punkte entstehen ausschließlich aus Gesamtleveln.
2. **Steigt nur der benutzte Baum?** Ja. Der direkte Browserlauf erhöhte Krallenhakenführung, während Schirmgleiten unverändert blieb.
3. **Speisen Baumaufstiege das Gesamtlevel?** Ja. Vier Baumaufstiege erzeugten den ersten Gesamtlevelaufstieg und einen zusätzlichen freien Punkt.
4. **Funktionieren alte Perk-IDs weiter?** Ja. `longline` und `windread` werden in den globalen Knotenstatus und in die ältere Wirkungsschicht gespiegelt. Der Fernanker verkürzte die reale Seillänge.
5. **Bleiben Voraussetzungen aktiv?** Ja. `reel` wurde auf zu niedriger Skillstufe korrekt abgewiesen.
6. **Bleibt die Migration nach Save/Load erhalten?** Ja. Punkte, globale Knoten und Legacy-Wirkung wurden vollständig wiederhergestellt.
7. **Playwright-Beleg:** `tests_v21/GATE_13G_RESULT.json` – 13/13 bestanden, 0 Browserfehler, 0 Konsolenfehler.
8. **Screenshot-Beleg:** `screenshots_v21/gate13g_skill_economy.png`.

## Status

`[GATE 13G BESTANDEN – 13/13 PLAYWRIGHT-PRÜFUNGEN]`

<!-- SOURCE_SEGMENT_END source="v21:docs_v21/GATE_13G_FRAGEN_VORHER_NACHHER.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-SKILL-016__Gate_13F_Eigene_Handlungskorper_fur_die_neun_offenen_Skillbaume.md) · `FW-SKILL-016`
- [Nächster Knoten](FW-SKILL-018__Gate_13H_Vollstandige_individuelle_Knoten_und_operative_Wirkungen.md) · `FW-SKILL-018`
- [Themenindex](00_INDEX.md) · `FW-INDEX-SKILL`
- [Verwandt: D062-Q06 · Nachbauprüfung](../08_BAUEN_HANDWERK_MODULARITAET/FW-BUILD-023__D062-Q06_Nachbauprufung.md) · `FW-BUILD-023`
- [Verwandt: D135-Q05 · Nachbauprüfung](../08_BAUEN_HANDWERK_MODULARITAET/FW-BUILD-025__D135-Q05_Nachbauprufung.md) · `FW-BUILD-025`
- [Verwandt: Fortschreibung nach Gate 13H](../08_BAUEN_HANDWERK_MODULARITAET/FW-BUILD-026__Fortschreibung_nach_Gate_13H.md) · `FW-BUILD-026`
- [Verwandt: K120-Q1 · Nachbauprüfung](../08_BAUEN_HANDWERK_MODULARITAET/FW-BUILD-028__K120-Q1_Nachbauprufung.md) · `FW-BUILD-028`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
