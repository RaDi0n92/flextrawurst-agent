---
id: FW-VER-002
status: BESTAETIGT
typ: source
themenraum: VER
version: v21
tags: [bauen, beziehung, fahrzeug, fragen, playwright, quest, redteam, region, test, v14, v21, ver, welt, wesen]
---

# Verbesserungsring nach Redteam – v14.0 → v14.1

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:docs/08_VERBESSERUNGSRING.md" sha256="c4698d20c23499ce1443c5c899a8156bdb9cdf2062710a53f845cbc76adc86dd" order="1" -->
# Verbesserungsring nach Redteam – v14.0 → v14.1

## Durchgeführte Änderungen

| ID | Problem | Änderung | Nachweis |
|---|---|---|---|
| V-01 | Spieler hinter Gebäuden nicht zuverlässig sichtbar | Welt-Halo und finaler Screen-Marker; Kamera weiter/höher | `screenshots/01_world_start.png` |
| V-02 | Netze überlagerten die Welt permanent | Sichtbarkeit nur im Bau-/Testmodus oder in Netznähe; reduzierte Deckkraft | `screenshots/03_build_network.png` |
| V-03 | Regionen aus der Ferne zu ähnlich | sechs unterschiedlich geformte und gefärbte Landmarkenbaken | Weltstart und Reisepfade |
| V-04 | Zielsuche teilweise unnötig hermetisch | kontextuelle Richtung, Distanz und Zielname im Spurhinweis | HUD in normalem Spielerpfad |
| V-05 | identische AI-Fragen konnten Vertrauen farmen | Wiederholung bricht vor Antwortbelohnung ab und erhöht Zumutung | Playwright-Check „kein Beziehungsgrind“ |
| V-06 | Redteam deckte zu wenig Grenzfälle ab | Testmatrix von 47 auf 56 Checks erweitert | `tests/PLAYWRIGHT_RESULT.json` |
| V-07 | Dokumentation sprach von zehn statt elf Baumodulen | Quellenmatrix und Testplan korrigiert | `docs/01...`, `docs/06...` |
| V-08 | Versionsstand unterschied Verbesserung nicht | Runtime und Testbericht auf 14.1.0 angehoben | `src/data.js`, JSON-Testbericht |

## Nicht vorgenommene „Verbesserungen“

Folgende bequemen Kürzungen wurden bewusst verworfen:

- AI-Wesen zu gewöhnlichen Quest-NPCs reduzieren,
- den Atlas mit Fangquote oder Vollständigkeitsprozent versehen,
- Bauen zu dekorativer Würfelplatzierung machen,
- alle Fahrzeuge auf ein gemeinsames Fahrmodell reduzieren,
- +333 in eine Cutscene verwandeln,
- Reintegration automatisch durchführen,
- Slots entfernen, statt ihre Attraktivität und Risiken systemisch sichtbar zu machen,
- Testmodus als versteckte Entwicklerkonsole auslagern,
- die Welt mit einem dauerhaften Navigationspfeil überziehen.

## Ergebnis

Der verbesserte Körper bleibt technisch überschaubar, aber seine Gesetze sind klarer sichtbar:

- Nähe und Ort bleiben relevant.
- Beziehungen können nicht durch Knopfwiederholung optimiert werden.
- Netze sind funktional und lesbar, ohne dauerhaft die Welt zu übermalen.
- Bewegung zwischen Regionen besitzt stärkere visuelle Anker.
- technische Voraussetzungen werden nicht nur dokumentiert, sondern blockieren unzulässige Abkürzungen.
- Testzustände bleiben vom Normalstand getrennt.

<!-- SOURCE_SEGMENT_END source="v21:docs/08_VERBESSERUNGSRING.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-VER-001__Build-Marker_und_weitere_Statusabschnitte.md) · `FW-VER-001`
- [Nächster Knoten](FW-VER-003__v14-Erneutanalyse_vor_Bauring_2.md) · `FW-VER-003`
- [Themenindex](00_INDEX.md) · `FW-INDEX-VER`
- [Verwandt: Abnahmekriterien Bauring 2 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-010__Abnahmekriterien_Bauring_2_und_weitere_Statusabschnitte.md) · `FW-TEST-010`
- [Verwandt: COPY-PASTE-MASTERPROMPT – MAXUS++++++++++++++++ Bauring 2](../10_CREATORWELTEN_EREIGNISSE_ARCHIVE/FW-CREATOR-001__COPY-PASTE-MASTERPROMPT_MAXUS++++++++++++++++_Bauring_2.md) · `FW-CREATOR-001`
- [Verwandt: MAXUS++++++++++++++++++++ Masterauftrag für Bauring 2](../10_CREATORWELTEN_EREIGNISSE_ARCHIVE/FW-CREATOR-002__MAXUS++++++++++++++++++++_Masterauftrag_fur_Bauring_2.md) · `FW-CREATOR-002`
- [Verwandt: K045-Q5 · K045 · Fehlurteil × Beziehungen](../07_BEWEGUNG_FAHRZEUGE_KAMPF_LOOT/FW-MOVE-023__K045-Q5_K045_Fehlurteil_Beziehungen.md) · `FW-MOVE-023`
- [Versionsspur v14](FW-VERSION-14__VERSIONSKARTE_V14.md) · `FW-VERSION-14`
- [Versionsspur v21](FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
