---
id: FW-SKILL-015
status: BESTAETIGT
typ: source
themenraum: SKILL
version: v21
tags: [beziehung, creator, dialog, fahrzeug, fragen, konzert, load, loot, magie, material, playwright, provenienz, save, simulation, skill, test, untergrund, v21, welt, wesen, zeit]
---

# Gate 13E – Reale Handlungsrouten der Skillbäume

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:docs_v21/GATE_13E_FRAGEN_VORHER_NACHHER.md" sha256="d7c5f5b401313e6bd065169d94f2a5396b9b89cf32a8abce2773a7457bd20a1d" order="1" -->
# Gate 13E – Reale Handlungsrouten der Skillbäume

## Vorbaufragen

1. **Darf ein sichtbarer Skillbaum ohne realen Auslöser als fertig gelten?** Nein.
2. **Wie wird Fahrzeugkompetenz differenziert?** Durch tatsächlich gefahrene Strecke je Fahrzeugklasse, nicht durch einen einzigen globalen Fahrbalken.
3. **Wie werden Waffenfamilien unterschieden?** Durch den wirklich benutzten Objektkörper und dessen Waffenklasse.
4. **Wie steigen Magieschulen?** Durch einen erfolgreich gewirkten Zauber der jeweiligen Schule; fehlgeschlagene oder unnötige Wirkung erzeugt keinen Schulfortschritt.
5. **Wie werden Handwerksbäume gekoppelt?** An konkrete Herstellung, Modulbau, Installation, Verzauberung und Materialumwandlung.
6. **Wie werden Wissens- und Beziehungsbäume gekoppelt?** An neue Quellen, Spuren, Hypothesen, Wesenbegegnungen, Perspektivabspaltungen, Korrekturen und echte Hilfe.
7. **Darf die Testzone Fortschritt durch bloßes Spawnen erzeugen?** Nein. Benutzung, Herstellung oder Weltwirkung ist erforderlich.
8. **Wie werden fehlende Handlungskörper behandelt?** Sie bleiben ausdrücklich im Audit als unangebunden markiert und werden im nächsten Gate gezielt gebaut.
9. **Wie wird Wiederholungsfarming verhindert?** Diskrete Weltaktionen erhalten Ereignissignaturen; bereits geschützte Dialog-, Konzert-, Loot- und Quellenlogiken werden respektiert.

## Geplanter Bau

- `src/v21_skill_routing.js`
- spezifische Fahrzeugrouten
- Waffen-, Zauber-, Crafting-, Untergrund-, Wesen-, Zeit-, Creator-, Ermittlungs- und Reparaturrouten
- sichtbarer Routingaudit über alle 69 Bäume
- Rohereignisse mit Grund, Betrag, Quelle und optionaler Signatur

## Nachbauantworten

1. **Sind alle 69 Bäume geprüft?** Ja. Der Routingaudit zählt exakt 69.
2. **Wie viele besitzen bereits echte Welttrigger?** 60.
3. **Werden offene Bäume verschwiegen?** Nein. Neun Bäume sind ausdrücklich als eigener fehlender Handlungskörper markiert.
4. **Steigen Fahrzeugfamilien getrennt?** Ja. Auto, Motorrad, Schwerfahrzeug, Zug, Boot, U-Boot, Flugzeug, Helikopter, Drohne und Amphibienkörper wurden real bewegt und getrennt protokolliert.
5. **Steigen Waffenfamilien durch Benutzung?** Ja. Einhandklinge und Präzisionsrahmen erhöhen unterschiedliche Bäume.
6. **Steigen Zauberschulen getrennt?** Ja. Heilung, Wahrnehmung, Raum/Zeit, Veränderung und Zerstörung wurden direkt gewirkt und getrennt erhöht.
7. **Sind Craftingrouten spezifisch?** Ja. Schneiderei, Elektronik und Fahrzeugmechanik reagieren auf passende Objektkörper.
8. **Sind Untergrund, Wesen und Zeit angebunden?** Ja. Bergbau, Tiefenräume, Wesensgespräche, Perspektivabspaltung, Forschung, Zeitadressen und Rückwärtszukunft speisen unterschiedliche Bäume.
9. **Kann dieselbe Quelle gefarmt werden?** Nein. Die zweite identische Lektüre erzeugt keinen erneuten Provenienzgewinn.
10. **Bleiben Routenereignisse speicherbar?** Ja. Grund, Betrag, Skill, Signatur und Metadaten überstehen Save/Load.

## Playwright

- **Datei:** `tests_v21/test_gate_13e_skill_routing.py`
- **Rohbericht:** `tests_v21/GATE_13E_RESULT.json`
- **Ergebnis:** **17/17 bestanden**
- **Screenshot:** `screenshots_v21/gate13e_skill_routing.png`

## Status

`[GATE 13E BESTANDEN NACH VOLLSTÄNDIGER TESTWIEDERHOLUNG]`

## Fortschreibung nach Gate 13F und Gate 13H

**Status:** `[FORTSCHREIBUNG NACH GATE 13F UND 13H]`

Die oben dokumentierten **60 von 69** Routen und neun offenen Handlungskörper waren der korrekte Zwischenstand unmittelbar nach Gate 13E. Gate 13F baute die neun fehlenden Körper; Gate 13H ersetzte sämtliche generischen Knotenkörper durch individuelle Wirkungen.

Der finale Routingaudit bestätigt:

- **69 von 69 Skillbäumen** besitzen reale Handlungsauslöser.
- **0 offene Handlungskörper** verbleiben.
- **276 von 276 Knoten** sind eindeutig, erreichbar und wirkungsgebunden.
- Die vollständige Gate-13E-Regression bestand erneut **17/17**.

**Belege:** `tests_v21/GATE_13E_RESULT.json`, `tests_v21/GATE_13F_RESULT.json`, `tests_v21/GATE_13H_RESULT.json`, `tests_v21/simulations/SKILL_UNIVERSE_SIMULATION_V21.json`.

<!-- SOURCE_SEGMENT_END source="v21:docs_v21/GATE_13E_FRAGEN_VORHER_NACHHER.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-SKILL-014__Gate_13D_AI-Fahigkeiten_als_echte_Arbeitskorper.md) · `FW-SKILL-014`
- [Nächster Knoten](FW-SKILL-016__Gate_13F_Eigene_Handlungskorper_fur_die_neun_offenen_Skillbaume.md) · `FW-SKILL-016`
- [Themenindex](00_INDEX.md) · `FW-INDEX-SKILL`
- [Verwandt: Abnahmekriterien Bauring 3 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-008__Abnahmekriterien_Bauring_3_und_weitere_Statusabschnitte.md) · `FW-TEST-008`
- [Verwandt: 8. Daniels Ideen-Redteam](FW-SKILL-021__8._Daniels_Ideen-Redteam.md) · `FW-SKILL-021`
- [Verwandt: Changelog · v21 final und weitere Statusabschnitte](../15_NETZWERK_INDIZES_QUERVERWEISE/FW-NET-001__Changelog_v21_final_und_weitere_Statusabschnitte.md) · `FW-NET-001`
- [Verwandt: Abnahmekriterien Bauring 2 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-010__Abnahmekriterien_Bauring_2_und_weitere_Statusabschnitte.md) · `FW-TEST-010`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
