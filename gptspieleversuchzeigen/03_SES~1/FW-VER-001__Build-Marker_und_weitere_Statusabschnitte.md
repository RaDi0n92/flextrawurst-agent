---
id: FW-VER-001
status: BESTAETIGT
typ: source
themenraum: VER
version: v21
tags: [beziehung, dust, fahrzeug, fragen, geld, kollision, mastery, material, playwright, provenienz, redteam, simulation, skill, test, v14, v21, ver, welt, zeit]
---

# Build-Marker und weitere Statusabschnitte

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:MAXUS_DUST_VERTRAG/10_BUILD_MARKER.md" sha256="639c11f23ea45e69e7525479120462abe5ac3ccafdc7916f8cee45f59a1b8046" order="1" -->
# Build-Marker

Die Analyse, Primärsetzung, 222 beantworteten Pflichtfragen, Architektur, Testplan, Redteam und Abnahmekriterien wurden vor neuem Spielcode geschrieben.

**Freigabemarker:**

`MAXUS++++++++++++++++ DUSTÖKOLOGIE – VERTRAG VOLLSTÄNDIG, BAU BEGINNT ERST JETZT`

<!-- SOURCE_SEGMENT_END source="v21:MAXUS_DUST_VERTRAG/10_BUILD_MARKER.md" order="1" -->

<!-- SOURCE_SEGMENT_BEGIN source="v21:MAXUS_PLUS_VERTRAG/08_BUILD_MARKER.md" sha256="8b63ed1cacd8d9a8887f18f19328b578eab60e962ce590b3968f8b878c7b867d" order="1" -->
# Bau-Marker

Der Vertragskörper wurde vollständig geschrieben, bevor der Code für Bauring 2 verändert wurde.

**MAXUS++++++++++++++++ BAURING 2 – VERTRAG VOLLSTÄNDIG, BAU BEGINNT ERST JETZT.**

<!-- SOURCE_SEGMENT_END source="v21:MAXUS_PLUS_VERTRAG/08_BUILD_MARKER.md" order="1" -->

<!-- SOURCE_SEGMENT_BEGIN source="v21:docs/15_VERBESSERUNG_V14_2.md" sha256="315780d0a7d6e0e95f08a7945569b564c236e638fe69c446d4438ce74568d41a" order="1" -->
# Verbesserung des bestehenden Kerns vor neuem Ausbau

## Umgesetzt

- autoritative Weltuhr im Hauptloop
- Testgeschwindigkeit wirkt auf Simulation
- Tagesphasen und Tageszähler
- langsame Langzeitticks
- Toleranzbereich vor funktionaler Netzdegradation
- Bauverschleiß und Reparaturbiografie
- Fahrzeugzustand aus zurückgelegter Distanz
- Fahrzeugreparatur mit Materialkosten und Historie
- Beziehungsmeilensteine
- fünf freiwillige, ortsgebundene Verweiltätigkeiten
- Abklingzeit ohne Streak oder Echtgeldlogik
- neues Lebens-/Verweilen-Panel
- Weltzeit und Wartung im Systemkörper
- neue Testzugänge für Zeit, Aktivität und Reparatur

## Nicht als Endprodukt ausgegeben

Diese Reparatur ist der stabilisierte v14-Kern. Sie ist noch nicht der nachfolgende große Bauring. Der große Ausbau beginnt erst nach dem folgenden MAXUS++++++++++++++++++++-Auftrag.

<!-- SOURCE_SEGMENT_END source="v21:docs/15_VERBESSERUNG_V14_2.md" order="1" -->

<!-- SOURCE_SEGMENT_BEGIN source="v21:docs_v21/00_BAUPROZESS_GATEVERTRAG.md" sha256="e0cb71bf76e91ac4ae3316df6907947086d530f46ec82399a731c4cc58865a97" order="1" -->
# v21 · Bauprozess mit unmittelbaren Playwright-Gates

## Status

**[AKTIVE NUTZERSETZUNG · HÖCHSTER PROZESSRANG]**

Der Spielkörper wird nach ausdrücklicher Baufreigabe tatsächlich gebaut. Der Bau darf jedoch nicht als großer ungetesteter Block entstehen.

## Unveränderliche Gate-Reihenfolge

Jeder integrierte Bauabschnitt durchläuft vollständig:

1. **Vorbaufragen:** Alle für den Abschnitt relevanten Fragen aus dem 2.717-Fragen-Körper werden einzeln beantwortet. Nicht relevante Fragen werden nicht gelöscht, sondern mit begründetem Nichtbezug markiert.
2. **Kleiner kohärenter Bau:** Ein zusammenhängender Systemkörper wird integriert. Kein Featurehaufen und kein bloßer Menüeintrag.
3. **Sofortiger Playwright-Lauf:** Der neue Körper wird direkt im echten Browser ausgelöst, beobachtet, gespeichert, geladen und auf Fehlwege geprüft.
4. **Nachbaufragen:** Dieselben Fragen werden gegen das tatsächlich gebaute Verhalten erneut beantwortet. Behauptungen benötigen Test-, Zustands- oder Screenshotbeleg.
5. **Gate-Entscheidung:** Nur ein vollständig bestandenes Gate darf den nächsten Bauabschnitt freigeben.

Ein späterer Gesamttest ersetzt niemals einen fehlenden Gate-Test.

## Fragenkörper

Verbindliche Quellen:

- `source_contract/12_DOMAENFRAGEN_150_BEREICHE.md` · 1.200 Domänenfragen
- `source_contract/00_CROSS_SYSTEM_200_PAARE_1200_FRAGEN.md` · 1.200 Kollisionsfragen
- `source_contract/05_FINALER_SUPERMAXIMALMAXIKINGMEGA_PROMPT.md` · weitere Pflicht-, Redteam- und Reihenfolgefragen

Der Endkörper enthält zusätzlich eine vollständige Fragenabdeckung, in der jede Frage mindestens einem Gate, einem offenen Knoten oder einem begründeten Nichtbezug zugeordnet wird.

## OUTRO.md

Neben README, Manifest und Testberichten ist ein abschließendes `OUTRO.md` Pflicht. Es ist kein dekoratives Nachwort, sondern das Resonanzfeld aller Dateien. Für jede Datei muss es nennen:

- Pfad und Dateityp
- konkreten Inhalt
- Provenienz und Ursprungsauftrag
- Abhängigkeiten und geschützte Nachfolger
- Warum die Datei existiert
- Warum sie wichtig ist
- Welche Verflachung oder welcher Verlust ohne sie droht
- Warum sie erhalten, versioniert oder ausdrücklich als ersetzbar markiert werden muss
- zugehörige Tests, Screenshots, Fragen und Entscheidungen

`OUTRO.md` wird erst aus dem realen Endbestand erzeugt. Danach wird es manuell redteamt, damit automatisch erzeugte Dateibeschreibungen keine Bedeutung erfinden oder Rohquellen zu bloßen Dateimetadaten degradieren.

## Ergänzung R20 – Skillentwurf vor Fortsetzung der großen Simulation

Vor der Fortsetzung der roten Mastery-Simulation sind verbindlich zu lesen:

1. `31_ROHINPUT_R20_SKILLBAEUME_LEVEL_AI_FAehIGKEITEN_WORTNAH.md`
2. `32_SIMULATIONSPLAN_NACH_BAU_VOR_ABSCHLUSS.md`
3. `33_SKILLBAUM_ARCHITEKTUR_GEBRAUCH_GESAMTLEVEL_PUNKTE.md`
4. `34_SKILLBAUM_KATALOG_KLASSISCH_TECHNISCH_MAGISCH_AI.md`
5. `35_SKILLBAUM_SIMULATIONS_UND_REDTEAMPLAN.md`
6. `36_OFFENE_ENTSCHEIDUNGEN_SKILLS_MASTERIES_AI.md`

Die große Simulation darf nicht mehr den alten 13-Baum-Prototyp als vollständiges Zielmodell behandeln. Erst wird der neue Skillkörper entworfen und kleinteilig getestet; danach wird die umfassende Simulation wiederholt.

<!-- SOURCE_SEGMENT_END source="v21:docs_v21/00_BAUPROZESS_GATEVERTRAG.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](00_INDEX.md) · `FW-INDEX-VER`
- [Nächster Knoten](FW-VER-002__Verbesserungsring_nach_Redteam_v14.0_v14.1.md) · `FW-VER-002`
- [Verwandt: Abnahmekriterien Bauring 3 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-008__Abnahmekriterien_Bauring_3_und_weitere_Statusabschnitte.md) · `FW-TEST-008`
- [Verwandt: Audit aller auffindbaren Simulations- und Redteam-Artefakte vor v22 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-001__Audit_aller_auffindbaren_Simulations-_und_Redteam-Artefakte_vor_v22_und_weiter.md) · `FW-TEST-001`
- [Verwandt: 8. Daniels Ideen-Redteam](../09_SKILLS_MASTERIES_MAGIE_AI/FW-SKILL-021__8._Daniels_Ideen-Redteam.md) · `FW-SKILL-021`
- [Verwandt: FLEXTRAWURST – FINALER SUPERMAXIMALMAXIKINGMEGA++++++++++++++++++++-PROMPT](../09_SKILLS_MASTERIES_MAGIE_AI/FW-SKILL-022__FLEXTRAWURST_FINALER_SUPERMAXIMALMAXIKINGMEGA++++++++++++++++++++-PROMPT.md) · `FW-SKILL-022`
- [Versionsspur v14](FW-VERSION-14__VERSIONSKARTE_V14.md) · `FW-VERSION-14`
- [Versionsspur v21](FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
