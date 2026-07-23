---
id: FW-TEST-007
status: BESTAETIGT
typ: source
themenraum: TEST
version: v21
tags: [88888, archiv, beziehung, dialog, dust, material, redteam, test, v21, welt, wesen]
---

# Redteam vor dem Bau

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:MAXUS_DUST_VERTRAG/08_REDTEAM_VOR_BAU.md" sha256="38f952e1ddc9a86f0165008ab152cfab2f2f8458dfba3ba74f696bef9b8a32fa" order="1" -->
# Redteam vor dem Bau

## Angriff: 88.888 als Marketingzahl

**Risiko:** Nur `total=88888` im Code, aber keine stabilen Identitäten oder Auswirkungen.

**Gegenmaßnahme:** Verteilung, deterministische IDs, Sektorrückkehr, Deltas, Beziehungen und Langzyklus werden separat getestet.

## Angriff: acht Anker bleiben heimlich das Zentrum

**Risiko:** Das UI nennt alle generierten Wesen nur „Umwelt“, während acht AI-Wesen als einzige Personen gelten.

**Gegenmaßnahme:** Dust-UI, Interaktionen und Chronik verwenden dieselbe Wesenbegrifflichkeit für alle Körperfamilien. Die acht Anker werden als hochaufgelöst, nicht als vollständig bezeichnet.

## Angriff: alles bekommt denselben Dialogkasten

**Risiko:** Scheinvielfalt durch Namen, während jede Form `talk()` ausführt.

**Gegenmaßnahme:** Familien besitzen verschiedene Zustände, Aktionen und Reaktionen; nichtsprachliche Formen werden nicht vermenschlicht.

## Angriff: Pokédex durch Hintertür

**Risiko:** „88.888 Wesen“ wird zur Sammelquote.

**Gegenmaßnahme:** Keine unbekannten Slots, keine Restzahl, keine Vollständigkeit, kein Fangstatus. Lokale Begegnungsarchive bleiben offen.

## Angriff: prozedurale Bedeutungslosigkeit

**Risiko:** Namen und Farben werden gewürfelt, aber Wesen haben keine Geschichte.

**Gegenmaßnahme:** Herkunft, Sektorprofil, Ausdruck, Rechte, Beziehungen und Ereignisbereitschaft werden deterministisch gekoppelt.

## Angriff: Fernregister ist bloß Datenbankfriedhof

**Risiko:** Nicht materialisierte Wesen verändern nichts.

**Gegenmaßnahme:** Cursorbasierte Langzyklen erzeugen kausale Ereigniskanten und sichtbare spätere Zustände.

## Angriff: Performance-Lüge

**Risiko:** Vollregister wird als 88.888 JS-Objekte angelegt und friert Browser ein.

**Gegenmaßnahme:** Lazy Generator, begrenzte lokale Materialisierung, Delta-Speicherung und Performance-Test.

## Angriff: zwölf Spiele als Nachbericht

**Risiko:** Dokument behauptet Organe, Screens und Spielpfad zeigen sie nicht.

**Gegenmaßnahme:** Blindtest-Matrix mit Szene, Handlung, Hintergrund und Cross-System-Folge pro Organ.

<!-- SOURCE_SEGMENT_END source="v21:MAXUS_DUST_VERTRAG/08_REDTEAM_VOR_BAU.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-TEST-006__Playwright-_und_Systemtestplan_vor_dem_Bau.md) · `FW-TEST-006`
- [Nächster Knoten](FW-TEST-008__Abnahmekriterien_Bauring_3_und_weitere_Statusabschnitte.md) · `FW-TEST-008`
- [Themenindex](00_INDEX.md) · `FW-INDEX-TEST`
- [Verwandt: Test, Redteam, Abnahme](../07_BEWEGUNG_FAHRZEUGE_KAMPF_LOOT/FW-MOVE-001__Test_Redteam_Abnahme.md) · `FW-MOVE-001`
- [Verwandt: 8. Daniels Ideen-Redteam](../09_SKILLS_MASTERIES_MAGIE_AI/FW-SKILL-021__8._Daniels_Ideen-Redteam.md) · `FW-SKILL-021`
- [Verwandt: FLEXTRAWURST – FINALER SUPERMAXIMALMAXIKINGMEGA++++++++++++++++++++-PROMPT](../09_SKILLS_MASTERIES_MAGIE_AI/FW-SKILL-022__FLEXTRAWURST_FINALER_SUPERMAXIMALMAXIKINGMEGA++++++++++++++++++++-PROMPT.md) · `FW-SKILL-022`
- [Verwandt: Dust-Echo-Grundgesetz des Questkosmos und weitere Statusabschnitte](../11_QUESTKOSMOS_ECHOS_SPIELERSPIEGEL/FW-QUEST-001__Dust-Echo-Grundgesetz_des_Questkosmos_und_weitere_Statusabschnitte.md) · `FW-QUEST-001`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
