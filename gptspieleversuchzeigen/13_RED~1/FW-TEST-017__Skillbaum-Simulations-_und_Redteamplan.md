---
id: FW-TEST-017
status: BESTAETIGT
typ: source
themenraum: TEST
version: v21
tags: [dialog, fragen, load, magie, objektbiografie, playwright, provenienz, redteam, save, simulation, skill, test, v21, welt, zeit]
---

# Skillbaum-Simulations- und Redteamplan

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:docs_v21/35_SKILLBAUM_SIMULATIONS_UND_REDTEAMPLAN.md" sha256="d3f2b2f75feda92fb57c9ffd000ccea719d814e65038437c8c05b244a88ee44a" order="1" -->
# Skillbaum-Simulations- und Redteamplan

## Ziel

Der Skillkörper soll nicht nur vollständig aussehen. Er muss über lange Entwicklung, extreme Spezialisierung, Mischformen, Save/Load, Abspaltungen, Rechte und Missbrauch tragfähig bleiben.

## Phase 1 – Strukturprüfung

- jeder Skill besitzt eindeutige ID, Familie, Gebrauchsauslöser und sichtbare Weltwirkung
- jeder Knoten besitzt Typ: passiv, aktiv oder transformativ
- Voraussetzungen bilden einen azyklischen Graphen
- kein unerreichbarer Knoten
- kein Knoten ohne tatsächliche Wirkung
- keine zwei Bäume sind nur umbenannte Kopien

## Phase 2 – Gebrauchszuwachs

Für jeden Skill werden mindestens 100 passende und 100 unpassende Handlungen simuliert.

Bestanden, wenn:

- passende Handlungen steigen,
- unpassende Handlungen nicht steigen,
- bedeutungslose Wiederholung gedrosselt wird,
- schwierige oder neue Situationen stärker beitragen,
- Testmodus klar markiert bleibt.

## Phase 3 – Gesamtlevel

10.000 Charakterpfade:

- reine Spezialisten
- breite Generalisten
- Magier
- Kämpfer
- Handwerker
- Fahrer und Piloten
- soziale Figuren
- AI-/Kontextforscher
- nichtmenschliche Körper

Geprüft werden:

- Fortschrittsgeschwindigkeit
- Punktmenge
- Totzonen
- dominanteste Exploits
- benachteiligte friedliche Spielweisen

## Phase 4 – Punkte und freie Wahl

- Start mit mehreren freien Punkten
- Investition in jeden sichtbaren Baum möglich
- Mindeststufen und Knotenvoraussetzungen funktionieren
- Punkte können nicht doppelt ausgegeben werden
- Save/Load während Investition ist atomar
- keine Menüspam-Punkte

## Phase 5 – Aktive und passive Wirkung

Jeder Knoten wird einzeln in Playwright ausgelöst und gegen mindestens einen Gegenfall geprüft.

Beispiele:

- Schutzzauber reduziert tatsächlich Schaden
- Pilotenknoten verändert Landung
- Kontextanker verhindert nachweisbare Drift in einem definierten Test
- Schmiedeknoten verändert Haltbarkeit und Objektbiografie

## Phase 6 – Cross-System-Knoten

Mindestens 64 Kombinationen aus mehreren Skillbäumen werden simuliert.

Redteamfragen:

- wird ein Hybrid stärker als alle Einzelsysteme zusammen?
- entsteht Gratisenergie oder Gratisheilung?
- werden Rechte durch Technik oder Magie umgangen?
- kann eine AI durch Kontextskills Allwissen vortäuschen?
- kann eine schwere Rüstung das Fallschirmsystem physikalisch ignorieren?

## Phase 7 – Abspaltung und Verschmelzung

- 333 Abspaltungen mit getrenntem Gebrauch
- 128 freiwillige Reintegration
- 128 selektive Reintegration
- 64 verweigerte Reintegration
- 64 Verschmelzungen mit Konflikt-Skills

## Phase 8 – Langzeit und Stufe 100

- Skills über Stufe 100 hinaus als Biografietiefe
- keine lineare Unendlichkeit
- keine unbesiegbaren Endzustände
- hohe Meisterschaft erzeugt neue Verantwortung und Weltwirkung

## Phase 9 – AI-Skills

### Kontextführung

- lange Dialogketten
- Themenwechsel
- widersprüchliche Quellen
- absichtlich fehlende Informationen
- korrekte Verlustmarkierung statt Erfindung

### Werkzeuggebrauch

- falsche Toolausgabe
- widersprüchliche Tools
- fehlgeschlagene Aufrufe
- mehrstufige Werkzeugketten

### Forschung

- Hypothese, Gegenhypothese, Experiment, Replikation, Unsicherheit

### Provenienz

- Rohinput gegen spätere Zusammenfassung
- Kopie gegen Original
- wiederholte falsche Aussage gegen eine Primärquelle

## Phase 10 – Balance ohne Gleichmacherei

Das Ziel ist nicht, alle Bäume numerisch gleich zu machen. Geprüft wird:

- jeder Baum besitzt eine eigene starke Identität,
- jeder Baum hat sinnvolle Schwächen,
- friedliche und soziale Wege können Gesamtlevel erzeugen,
- Kämpfen ist nicht die einzige schnelle Entwicklung,
- AI- und Weltfähigkeiten sind nicht bloße Bonusmenüs.

## Ausgabekörper

- `SKILL_TREE_SCHEMA.json`
- `SKILL_TREE_NODES.json`
- `SKILL_SIMULATION_RAW.json`
- `SKILL_BALANCE_FINDINGS.md`
- `SKILL_REDTEAM.md`
- `SKILL_REPAIRS.md`
- Playwright-Ergebnis pro Skillfamilie
- erneuter Gesamtregressionsbericht

<!-- SOURCE_SEGMENT_END source="v21:docs_v21/35_SKILLBAUM_SIMULATIONS_UND_REDTEAMPLAN.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-TEST-016__Selbst-Redteam_des_MAXUS++++++++++++++++++++-Auftrags.md) · `FW-TEST-016`
- [Nächster Knoten](FW-TEST-018__Skilluniversum-Simulation_v21.md) · `FW-TEST-018`
- [Themenindex](00_INDEX.md) · `FW-INDEX-TEST`
- [Verwandt: Abnahmekriterien Bauring 3 und weitere Statusabschnitte](FW-TEST-008__Abnahmekriterien_Bauring_3_und_weitere_Statusabschnitte.md) · `FW-TEST-008`
- [Verwandt: Gate 13E – Reale Handlungsrouten der Skillbäume](../09_SKILLS_MASTERIES_MAGIE_AI/FW-SKILL-015__Gate_13E_Reale_Handlungsrouten_der_Skillbaume.md) · `FW-SKILL-015`
- [Verwandt: Abnahmekriterien Bauring 2 und weitere Statusabschnitte](FW-TEST-010__Abnahmekriterien_Bauring_2_und_weitere_Statusabschnitte.md) · `FW-TEST-010`
- [Verwandt: D136-Q06 · D136 · Playwright/Automation](../05_DUST_WESEN_BEZIEHUNGEN/FW-DUST-022__D136-Q06_D136_Playwright_Automation.md) · `FW-DUST-022`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
