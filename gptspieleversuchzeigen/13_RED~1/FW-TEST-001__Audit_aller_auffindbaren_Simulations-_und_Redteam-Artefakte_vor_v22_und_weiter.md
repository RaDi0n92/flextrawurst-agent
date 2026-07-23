---
id: FW-TEST-001
status: BESTAETIGT
typ: source
themenraum: TEST
version: v22
tags: [111111, 13333337, archiv, beziehung, boss, dust, echo, fahrzeug, jahreszeit, kampf, katastrophe, klima, load, magie, mastery, material, playwright, provenienz, quest, redteam, save, simulation, skill, test, v09, v12, v13, v14, v15, v19, v20, v21, v22, welt, wesen, wetter, wirtschaft, zeit]
---

# Audit aller auffindbaren Simulations- und Redteam-Artefakte vor v22 und weitere Statusabschnitte

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v22:01_audit/02_PRIOR_SIMULATION_REDTEAM_GESAMTBEFUND.md" sha256="7c4440f7e725da57d03f1503ba2402268c16c58d8a9d6ebd7b122c8f3ab7832a" order="1" -->
# Audit aller auffindbaren Simulations- und Redteam-Artefakte vor v22
## Umfang
- Inventarisierte Treffer: **62**
- Lesbare Text-/JSON-Artefakte: **59**
- Archive/Binärtreffer oder Duplikate: **3**
- Der Audit bezieht sich auf alle im aktuellen Container auffindbaren Dateien mit Simulation-, Redteam-, Playwright-Ergebnis- oder Auditbezug. Er behauptet nicht, verlorene historische Dateien gelesen zu haben.

## Themenabdeckung über alle Artefakte
- **skill:** 997 Signalvorkommen
- **beziehung_wesen:** 936 Signalvorkommen
- **zeit:** 691 Signalvorkommen
- **provenienz:** 626 Signalvorkommen
- **rechte_zustimmung:** 413 Signalvorkommen
- **bewegung_fahrzeug:** 384 Signalvorkommen
- **weltfolge:** 243 Signalvorkommen
- **offenheit:** 231 Signalvorkommen
- **anti_grind:** 188 Signalvorkommen
- **quest:** 182 Signalvorkommen
- **material_bau:** 150 Signalvorkommen
- **test_isolation:** 81 Signalvorkommen

## Wiederkehrende Stärken
- Provenienz, Zeit, Zustimmung, Testisolation und Weltfolgen wurden in späteren Ringen deutlich stärker als reine Featureexistenz behandelt.
- Mehrere reale Fehler wurden durch Tests entdeckt: nicht laufende Weltzeit, zu schnelle Wartungsalterung, falsche Assemblierung, Belohnungsfarmen, Testzonen-Duplikate, wirkungslose Skillknoten und veraltete Prüfkörper.
- Die spätere Disziplin, rote Tests nicht schönzurechnen, ist als Schutzprinzip tragfähig.
- Save/Load, Testforks und maschinenlesbare Ergebnisse wurden zunehmend als eigene Beweiskörper geführt.

## Wiederkehrende Schwächen und Drift
- Frühe Simulationen prüften häufig vorhandene Setzungen gegen sich selbst. Dadurch konnte ein sauber formulierter Vertrag als „bestanden“ gelten, ohne dass ein realer Spielkörper existierte.
- Mehrere Berichte waren stärker als ihre maschinenlesbaren Belege oder verwendeten später veraltete Zwischenstände weiter.
- Die zwölf Spielorgane wurden oft einzeln geprüft, aber selten als gleichzeitig kollidierende Quest- und Weltkörper.
- Spannung, Dramaturgie, Überraschung, emotionale Nachwirkung und autonome Fortsetzung waren kein durchgängiger Prüfkern.
- Die meisten Simulationen prüften Systemzustände, aber noch keinen massiven Questkosmos, der aus Handlungsechos entsteht.
- „Bestanden“ sagte teilweise nur: kein technischer Widerspruch. Es sagte nicht automatisch: eigenständig, überraschend, spielerisch tief oder Flextrawurst-artig.

## Flextrawurst-Schärfung für v22
1. Jede Simulation muss zwischen **technisch gültig**, **systemisch kausal**, **spielerisch spannend** und **Flextrawurst-eigen** unterscheiden.
2. Jede generierte Geschichte benötigt sichtbare Herkunft, widersprüchliche Perspektiven, autonome Beteiligte und Nachleben.
3. Ein Questkörper darf nicht nur Endzustände prüfen. Er muss Spannungskurven, Eskalationen, Gegenreaktionen, Abwesenheit und unerwartete Lösungen durchlaufen.
4. Die zwölf Spielorgane werden nicht als Checkliste, sondern als miteinander kollidierende Handlungsgrammatiken geprüft.
5. Ergebnisse werden als strukturierte Rohdaten, Hashes, Fehlerklassen und repräsentative Vollspuren gesichert.

## Einzeldateien mit erhöhtem Zusammenfassungsrisiko
- `/mnt/data/flextrawurst_finaler_supermaximalmaxikingmega_prompt_2026-07-22_v20/06_PROMPT_SELBSTREDTEAM.md` (2377 Bytes)
- `/mnt/data/flextrawurst_gesamtintegration_sokrates_111_redteam_2026-07-21_v9/91_redteam_gesamtintegration/91c_redteam_gesamtbericht.md` (1307 Bytes)
- `/mnt/data/flextrawurst_spielewelt_supermaximal_bauring4_v21/docs_v21/41_POSTBUILD_WORLD_SIMULATIONS_FINAL.md` (1271 Bytes)
- `/mnt/data/flextrawurst_zeitwelt_abspaltungskoerper_normalisiert/KERN_NACH_111_RED_TEAM.md` (3747 Bytes)
- `/mnt/data/flextrawurst_zeitwelt_abspaltungskoerper_normalisiert/RED_TEAM_111_GESAMTBERICHT.md` (2584 Bytes)
- `/mnt/data/v21_full/flextrawurst_spielewelt_supermaximal_bauring4_v21/docs/15_REDTEAM_ZWEITER_PASS.md` (1663 Bytes)
- `/mnt/data/v21_full/flextrawurst_spielewelt_supermaximal_bauring4_v21/docs_v21/41_POSTBUILD_WORLD_SIMULATIONS_FINAL.md` (1271 Bytes)
- `/mnt/data/v21_full/flextrawurst_spielewelt_supermaximal_bauring4_v21/tests/REDTEAM_V15_AFTER.json` (3634 Bytes)
- `/mnt/data/v21_full/flextrawurst_spielewelt_supermaximal_bauring4_v21/tests/REDTEAM_V15_BEFORE.json` (3823 Bytes)

## Versions-/Körpergruppen
- **flextrawurst_finaler_supermaximalmaxikingmega_prompt_2026-07-22_v20:** 2 Treffer
- **flextrawurst_gesamtintegration_sokrates_111_redteam_2026-07-21_v9:** 2 Treffer
- **flextrawurst_gesamtintegration_sokrates_111_redteam_2026-07-21_v9 (1).zip:** 1 Treffer
- **flextrawurst_gesamtintegration_sokrates_111_redteam_2026-07-21_v9.zip:** 1 Treffer
- **flextrawurst_maxus_bauvertrag_2026-07-22_v13:** 1 Treffer
- **flextrawurst_rohideen_spielanalysen_promptfundament_2026-07-22_v19_1:** 1 Treffer
- **flextrawurst_rohideen_spielanalysen_promptfundament_2026-07-22_v19_2:** 2 Treffer
- **flextrawurst_rohideen_spielanalysen_promptfundament_2026-07-22_v19_3:** 1 Treffer
- **flextrawurst_spielewelt_maxus_bauring1_v14:** 3 Treffer
- **flextrawurst_spielewelt_maxus_bauring2_v15:** 3 Treffer
- **flextrawurst_spielewelt_supermaximal_bauring4_v21:** 7 Treffer
- **flextrawurst_v12_redteam_verbessert_2026-07-21:** 1 Treffer
- **flextrawurst_v12_redteam_verbessert_2026-07-21.zip:** 1 Treffer
- **ohne_explizite_version:** 7 Treffer
- **v21_full:** 29 Treffer

<!-- SOURCE_SEGMENT_END source="v22:01_audit/02_PRIOR_SIMULATION_REDTEAM_GESAMTBEFUND.md" order="1" -->

<!-- SOURCE_SEGMENT_BEGIN source="v22:04_simulation/01_SIMULATIONSMODELL_111111_X_99.md" sha256="a38eee275cee6f62b38c27ca19cef677edcf64c3c408ec749b3cfec1df68c42b" order="1" -->
# Simulationsmodell – 111.111 Questkeime × 99 Varianten

## Umfang

- Questkeime: **111,111**
- Sieben-Akt-Ketten: **15,873**
- Spielstile: **9** (Vermittler, Zerstörer, Baumeister, Entdecker, Ermittler, Händler, Magier, Schleicher, Abwesender/autonome Welt)
- Weltstörungen: **11** (Basislage, tiefe Nacht, harter Winter, Extremsturm, Katastrophenhöhepunkt, akute Knappheit, Wirtschaftsboom, Schuldendruck, feindselige Beziehungen, tiefes Vertrauen, Zeitparadox)
- Varianten je Quest: **99**
- Varianten je vollständigem Pass: **10,999,989**
- zwei vollständige Pässe: ungeschärft und redteam-geschärft

Jede Quest wird in jeder Kombination aus Spielstil und Weltstörung ausgeführt. Die Simulation speichert pro Quest Mindest-, Mittel- und Höchstwerte, Fehlerzahlen, wirtschaftliche Spannweite, einen Hash über alle 99 Varianten und repräsentative Vollspuren. Die elf Millionen Einzelverläufe werden nicht als elf Millionen Romandateien dupliziert; ihre Zustände fließen vollständig in die Aggregationen und Hashes ein.

<!-- SOURCE_SEGMENT_END source="v22:04_simulation/01_SIMULATIONSMODELL_111111_X_99.md" order="1" -->

<!-- SOURCE_SEGMENT_BEGIN source="v22:05_redteam/04_QUESTKOSMOS_FINAL_REDTEAM.md" sha256="49d5b028dd1f6e26ed30194c65954ba494ccbf5e836b4e8217e3fabd34fcd814" order="1" -->
# Finales Questkosmos-Redteam

## Angriffe

1. reine Sammel- und Abgabequests;
2. Boss = großer Lebensbalken;
3. Wetter nur als Bildfilter;
4. Jahreszeiten ohne materielle Wirkung;
5. Katastrophen als unsichtbare Zufallsstrafe;
6. garantierter Questgewinn;
7. unlesbare Wirtschaftsverluste;
8. Save/Load-Belohnungsduplikation;
9. Wesen als Auftragsterminals;
10. Queststillstand bei Spielerabwesenheit;
11. zwölf Spielorgane als Namensliste;
12. Masterybelohnung ohne tatsächliche Benutzung;
13. Dust-Spiegelung in jeder Quest;
14. Tötung als einzig ernsthafte Lösung;
15. Zeitreise ohne Gegenwartsfolge;
16. Wiederholung als 13.333.337-Stunden-Ersatz.

## Ergebnis nach Schärfung

- reine Fetchkörper: **0**
- ohne Nichtkampfpfad: **0**
- ohne autonome Fortsetzung: **0**
- ohne Klima-/Zeitwirkung: **0**
- ohne Wirtschaftsprovenienz: **0**
- unter drei Organen: **0**
- unter drei Pfaden: **0**
- Questkörper mit roten 111er-Checks: **0**

<!-- SOURCE_SEGMENT_END source="v22:05_redteam/04_QUESTKOSMOS_FINAL_REDTEAM.md" order="1" -->

<!-- SOURCE_SEGMENT_BEGIN source="v22:06_ergebnisse/02_QUEST_REDTEAM_UND_SCHAERFUNGEN.md" sha256="46ccc6b5d98307cd2618ee4e094ec536d1fc29fb9ae1800fd0d25fcaae78afcd" order="1" -->
# Quest-Redteam und Schärfungen

- **pure_fetch_quests:** 13,494 → **0**
- **quests_without_noncombat_path:** 46,621 → **0**
- **quests_without_autonomous_continuation:** 42,406 → **0**
- **quests_without_climate_hook:** 50,040 → **0**
- **quests_without_economy_provenance:** 37,967 → **0**
- **quests_without_rights_path:** 31,041 → **0**
- **quests_below_three_organs:** 31,440 → **0**
- **quests_below_three_branches:** 18,599 → **0**
- **failed_quest_checks:** 111,111 → **0**

<!-- SOURCE_SEGMENT_END source="v22:06_ergebnisse/02_QUEST_REDTEAM_UND_SCHAERFUNGEN.md" order="1" -->

<!-- SOURCE_SEGMENT_BEGIN source="v22:06_ergebnisse/09_PROOF_OF_RUN.md" sha256="7e2390fc176bc4cb6ef421d9e2537a72b301283cc942e64cfc93f883707aa6af" order="1" -->
# Ausführungsbeleg

```json
{
  "generated_at_utc": "2026-07-22T11:20:47Z",
  "quest_count": 111111,
  "variants_per_quest": 99,
  "passes": 2,
  "variant_evaluations_total": 21999978,
  "questions": 777,
  "compiled_checks_per_quest": 111,
  "quest_check_evaluations_total": 24666642,
  "chains": 15873,
  "chain_variant_evaluations": 1571427,
  "pass_a_hash64": "7316937665393652337",
  "pass_b_hash64": "5198860123197608131",
  "pass_a_duration_seconds": 3.13,
  "pass_b_duration_seconds": 3.496,
  "database_sha256": "3203f7a03c64a6cd5d80820f3bb064fd0dfd2cacba7e62b616fda9dc2d7ee987",
  "catalog_sha256": "037ac822963292b977d939120a66dc2c87e4632bdfa4f8128c8918d16bd8dba4",
  "traces_sha256": "92f50f9426d7b8e86325620ffa4494af7fffd00a0f367749066027cf4702ed37"
}
```

<!-- SOURCE_SEGMENT_END source="v22:06_ergebnisse/09_PROOF_OF_RUN.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](00_INDEX.md) · `FW-INDEX-TEST`
- [Nächster Knoten](FW-TEST-002__Einzelakten_Redteam_aller_auffindbaren_fruheren_Simulations-_und_Prufartefakte.md) · `FW-TEST-002`
- [Verwandt: Dust-Echo-Grundgesetz des Questkosmos und weitere Statusabschnitte](../11_QUESTKOSMOS_ECHOS_SPIELERSPIEGEL/FW-QUEST-001__Dust-Echo-Grundgesetz_des_Questkosmos_und_weitere_Statusabschnitte.md) · `FW-QUEST-001`
- [Verwandt: Abnahmekriterien Bauring 3 und weitere Statusabschnitte](FW-TEST-008__Abnahmekriterien_Bauring_3_und_weitere_Statusabschnitte.md) · `FW-TEST-008`
- [Verwandt: Abnahmekriterien Bauring 2 und weitere Statusabschnitte](FW-TEST-010__Abnahmekriterien_Bauring_2_und_weitere_Statusabschnitte.md) · `FW-TEST-010`
- [Verwandt: FLEXTRAWURST – FINALER SUPERMAXIMALMAXIKINGMEGA++++++++++++++++++++-PROMPT](../09_SKILLS_MASTERIES_MAGIE_AI/FW-SKILL-022__FLEXTRAWURST_FINALER_SUPERMAXIMALMAXIKINGMEGA++++++++++++++++++++-PROMPT.md) · `FW-SKILL-022`
- [Versionsspur v12](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-12__VERSIONSKARTE_V12.md) · `FW-VERSION-12`
- [Versionsspur v13](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-13__VERSIONSKARTE_V13.md) · `FW-VERSION-13`
- [Versionsspur v14](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-14__VERSIONSKARTE_V14.md) · `FW-VERSION-14`
- [Versionsspur v15](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-15__VERSIONSKARTE_V15.md) · `FW-VERSION-15`
- [Versionsspur v19](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-19__VERSIONSKARTE_V19.md) · `FW-VERSION-19`
- [Versionsspur v20](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-20__VERSIONSKARTE_V20.md) · `FW-VERSION-20`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
- [Versionsspur v22](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-22__VERSIONSKARTE_V22.md) · `FW-VERSION-22`
- [Versionsspur v9](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-09__VERSIONSKARTE_V9.md) · `FW-VERSION-09`
