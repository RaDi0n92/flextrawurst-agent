---
id: FW-SKILL-011
status: BESTAETIGT
typ: source
themenraum: SKILL
version: v21
tags: [fragen, load, magie, mastery, playwright, save, skill, test, v21, welt]
---

# Gate 13A – Gesamtlevel, freie Skillpunkte und universeller Skillkatalog

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:docs_v21/GATE_13A_FRAGEN_VORHER_NACHHER.md" sha256="bf70119bde9911c93de41bf2b0b9adc4ae5b50509370c19de763bee142aebc8f" order="1" -->
# Gate 13A – Gesamtlevel, freie Skillpunkte und universeller Skillkatalog

## Vorbaufragen

1. **Wie wird die Skyrim-nahe Gebrauchsmastery erhalten?** Einzelstufen steigen weiterhin nur durch `gainSkillUse` aus tatsächlichen Handlungen.
2. **Wie entsteht das Gesamtlevel?** Neue Einzelstufen geben gewichtete Charaktererfahrung; Levelschwellen steigen progressiv.
3. **Woher kommen Skillpunkte?** Drei Startpunkte plus ein Punkt pro Gesamtlevel; jeder zehnte Level gibt zusätzlich einen Weltpunkt.
4. **Sind Startklassen nötig?** Nein. Alle Bäume sind sichtbar und Basisknoten grundsätzlich früh anwählbar.
5. **Wie werden bestehende 13 Bäume geschützt?** Sie bleiben erhalten und werden in den größeren Katalog integriert.
6. **Wie wird Save/Load behandelt?** Gesamtlevel, Erfahrung, Punkte, Knotenhistorie und Freischaltungen liegen im persistenten Zustand.
7. **Was verhindert Negativ- oder Nullfortschritt?** Nichtpositive Gebrauchswerte werden abgewiesen.
8. **Wie werden AI-Fähigkeiten eingebunden?** Als gleichwertige sichtbare Bäume, nicht als geheime Metawerte.

## Gebaut

- `src/v21_skill_universe.js`
- 69 sichtbare Skillbäume
- `skillUniverse21` mit Gesamtlevel, Charaktererfahrung, freien Skillpunkten, Weltpunkten und Knotenhistorie
- globale Knotenfreischaltung mit Stufen- und Vorgängervoraussetzungen
- neue Skilluniversum-Oberfläche

## Nachbaufragen und Belege

1. **Ist der Katalog wirklich groß?** Ja, 69 Bäume im Browserzustand.
2. **Sind alle von Anfang an vorhanden?** Ja, 69 Zustände direkt nach Reset/Start.
3. **Existieren klassische und AI-Bäume gemeinsam?** Ja, unter anderem leichte/schwere Rüstung, Schleichen, Pistolen, Laser, Magieschulen, Kochen, Fliegen, Kontextführung, Kontextfenster, Werkzeuge und Forschung.
4. **Steigt nur der benutzte Baum?** Ja. Leichte Rüstung stieg, schwere Rüstung blieb unverändert.
5. **Speisen Einzelstufen das Gesamtlevel?** Ja. Der deterministische Gebrauchslauf erhöhte das Gesamtlevel von 1 auf 3.
6. **Entstehen freie Punkte?** Ja. Die Punkte stiegen von 3 auf 5.
7. **Kann früh ein beliebiger AI-Baum gewählt werden?** Ja. `Kontextführung: Kontextanker` (`cs_anchor`) wurde ohne Klassenwahl freigeschaltet. Die frühere Platzhalter-ID `contextSteering_foundation` ist ausdrücklich ersetzt.
8. **Werden Punkte global verbraucht?** Ja. Der globale Vorrat sank exakt um die Knotenkosten.
9. **Sind Doppelkäufe verhindert?** Ja.
10. **Greifen Stufen- und Vorgängervoraussetzungen?** Ja.
11. **Bleibt alles nach Save/Load?** Ja.
12. **Browserfehler?** Keine.

## Playwright

- **Datei:** `tests_v21/test_gate_13a_skill_universe.py`
- **Rohbericht:** `tests_v21/GATE_13A_RESULT.json`
- **Ergebnis:** **15/15 bestanden**
- **Screenshot:** `screenshots_v21/gate13a_skill_universe.png`

## Status

`[GATE 13A BESTANDEN]`

<!-- SOURCE_SEGMENT_END source="v21:docs_v21/GATE_13A_FRAGEN_VORHER_NACHHER.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-SKILL-010__K024-Q1_K024_Bauen_Ressourcen.md) · `FW-SKILL-010`
- [Nächster Knoten](FW-SKILL-012__Gate_13B_Kuratierte_Skillbaume_und_Knotengraphen.md) · `FW-SKILL-012`
- [Themenindex](00_INDEX.md) · `FW-INDEX-SKILL`
- [Verwandt: Gate 03 · Gebrauchsmastery, Skillbäume, Handwerk, Verzauberung und echte Dust-Magie](FW-SKILL-009__Gate_03_Gebrauchsmastery_Skillbaume_Handwerk_Verzauberung_und_echte_Dust-Magie.md) · `FW-SKILL-009`
- [Verwandt: Gate 13H – Vollständige individuelle Knoten und operative Wirkungen](FW-SKILL-018__Gate_13H_Vollstandige_individuelle_Knoten_und_operative_Wirkungen.md) · `FW-SKILL-018`
- [Verwandt: Abnahmekriterien Bauring 3 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-008__Abnahmekriterien_Bauring_3_und_weitere_Statusabschnitte.md) · `FW-TEST-008`
- [Verwandt: Skillbaum-Simulations- und Redteamplan](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-017__Skillbaum-Simulations-_und_Redteamplan.md) · `FW-TEST-017`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
