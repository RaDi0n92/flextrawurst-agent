---
id: FW-TEST-012
status: BESTAETIGT
typ: source
themenraum: TEST
version: v21
tags: [archiv, beziehung, dialog, fahrzeug, load, material, playwright, provenienz, save, test, v14, v21, welt, zeit]
---

# Playwright-Gesamttest – MAXUS-Bauring 1 v14.1

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:docs/09_PLAYWRIGHT_TESTBERICHT.md" sha256="b7220feac857fcd281e08d53d2e354016fc6fe265f91e60885e873b455c34891" order="1" -->
# Playwright-Gesamttest – MAXUS-Bauring 1 v14.1

## Ergebnis

- **Bestanden:** 56
- **Fehlgeschlagen:** 0
- **Laufzeit:** 13.46 Sekunden
- **Seitenfehler:** 0
- **Konsolenfehler:** 0
- **Browser:** Chromium, headless, 1440 × 900
- **Ausführung:** vollständige Ein-Datei-Fassung über `page.set_content`, weil lokale URLs in der Arbeitsumgebung administrativ blockiert sind

`page.set_content` führt denselben HTML-, CSS- und JavaScript-Körper in Chromium aus. Der sichere Speicherrückfall wird absichtlich benutzt, damit Save/Load auch in restriktiven Dokumentkontexten getestet werden kann.

## Testarten

1. normaler räumlicher Spielerpfad,
2. UI- und Dialogpfade,
3. deterministische Zustandsinjektion für seltene Grenzfälle,
4. Fehler- und Missbrauchspfade,
5. Save-/Import-/Test-Fork-Isolation,
6. statische Ausschlussprüfung der Plattformorgane,
7. Renderer-, Seiten- und Konsolenüberwachung.

## Einzelchecks

| Nr. | Prüfung | Ergebnis | Detail |
|---:|---|---|---|
| 1 | Prolog sichtbar | BESTANDEN |  |
| 2 | Spielstart | BESTANDEN |  |
| 3 | Renderer ohne Fehler | BESTANDEN |  |
| 4 | Normale WASD-Bewegung | BESTANDEN | Distanz 3.60 |
| 5 | AI-Begegnung räumlich | BESTANDEN |  |
| 6 | AI erklärt Herkunft/Körper/Fähigkeit/Grenze | BESTANDEN |  |
| 7 | Wiederholte AI-Frage erzeugt keinen Beziehungsgrind | BESTANDEN | {"before": {"trust": 6, "respect": 8, "zumutung": 0}, "after": {"trust": 6, "respect": 7, "zumutung": 4}} |
| 8 | AI kann Hilfe verweigern | BESTANDEN |  |
| 9 | Materialherkunft gespeichert | BESTANDEN |  |
| 10 | Materialknoten ist endlich statt Grind-Brunnen | BESTANDEN | 12->16 |
| 11 | Bauabhängigkeit verhindert Relais ohne Netz | BESTANDEN |  |
| 12 | Bau foundation | BESTANDEN |  |
| 13 | Bau power | BESTANDEN |  |
| 14 | Bau archive | BESTANDEN |  |
| 15 | Bau relay | BESTANDEN |  |
| 16 | Bau consent | BESTANDEN |  |
| 17 | Bau workshop | BESTANDEN |  |
| 18 | Bau dock | BESTANDEN |  |
| 19 | Bau airpad | BESTANDEN |  |
| 20 | Bau habitat | BESTANDEN |  |
| 21 | Consent-Verbindungsnetz funktional | BESTANDEN | {"power": 20, "link": 15, "archive": 15, "consent": 1, "transport": 20, "production": 10, "civic": 12} |
| 22 | Vergangenheitsportal blockiert ungestützte Rekonstruktion | BESTANDEN |  |
| 23 | Fernfeld blockiert unverdiente Abkürzung | BESTANDEN |  |
| 24 | Fahrzeug spawn pedal | BESTANDEN |  |
| 25 | Fahrzeug spawn hauler | BESTANDEN |  |
| 26 | Fahrzeug spawn amphib | BESTANDEN |  |
| 27 | Fahrzeug spawn skiff | BESTANDEN |  |
| 28 | Fahrzeug spawn sub | BESTANDEN |  |
| 29 | Fahrzeug spawn glider | BESTANDEN |  |
| 30 | Fahrzeug spawn vtol | BESTANDEN |  |
| 31 | Sieben systemische Fahrzeugklassen | BESTANDEN |  |
| 32 | Landfahrzeug fährt | BESTANDEN |  |
| 33 | Wasserfahrzeug verweigert Land | BESTANDEN |  |
| 34 | Wasserfahrzeug fährt im Wasser | BESTANDEN |  |
| 35 | VTOL steigt vertikal | BESTANDEN | 2->4.324700000000001 |
| 36 | VTOL verbraucht Ladung statt Gratisflug | BESTANDEN | 78.86->78.02 |
| 37 | Gleiter verliert ohne Fahrt Höhe | BESTANDEN | 9.00->8.55 |
| 38 | Drei verschiedene Provenienzquellen | BESTANDEN |  |
| 39 | Vergangenheit als Rekonstruktion geöffnet | BESTANDEN |  |
| 40 | +333 bestätigte Endlinie geöffnet | BESTANDEN |  |
| 41 | Selektive Reintegration | BESTANDEN |  |
| 42 | Private Notiz nicht automatisch übertragen | BESTANDEN |  |
| 43 | Autonome Abspaltung kann Vollmerge verweigern | BESTANDEN |  |
| 44 | Nach Verweigerung bleibt selektive Einigung möglich | BESTANDEN |  |
| 45 | Slots räumlich erreichbar | BESTANDEN |  |
| 46 | Slots erzeugen Drang und sichtbare Quoten | BESTANDEN |  |
| 47 | Selbstsperre aktiviert | BESTANDEN |  |
| 48 | Selbstsperre technisch durchgesetzt | BESTANDEN |  |
| 49 | Alternative Zukunft liest Rechtsentscheidung | BESTANDEN |  |
| 50 | Speichern/Laden stellt Zustand wieder her | BESTANDEN |  |
| 51 | Defekter Snapshot wird ohne Zustandskorruption abgewiesen | BESTANDEN |  |
| 52 | Test-Fork markiert und freigeschaltet | BESTANDEN |  |
| 53 | Normalstand nach Test-Fork unverändert | BESTANDEN |  |
| 54 | Keine Plattformorgane im Spielcode | BESTANDEN | [] |
| 55 | Keine Browser-/Konsolenfehler | BESTANDEN |  |
| 56 | Renderer nach Gesamtpfad aktiv | BESTANDEN |  |

## Belegdateien

- Rohbericht: `tests/PLAYWRIGHT_RESULT.json`
- Testskript: `tests/playwright_full_test.py`
- Screenshots: `screenshots/00_prologue.png` bis `screenshots/09_test_mode.png`

## Interpretation

56/56 bedeutet: Die im Ring behaupteten Pfade wurden in dieser Fassung reproduzierbar ausgelöst. Es bedeutet nicht, dass ein Browser-Vertikalschnitt bereits Produktionsreife, vollständige Barrierefreiheit, Langzeitbalance oder Millionen emergenter Weltstunden besitzt.

<!-- SOURCE_SEGMENT_END source="v21:docs/09_PLAYWRIGHT_TESTBERICHT.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-TEST-011__Testplan_vor_dem_Bau.md) · `FW-TEST-011`
- [Nächster Knoten](FW-TEST-013__Zweiter_Gesamtaudit_von_MAXUS-Bauring_1_v14.1.md) · `FW-TEST-013`
- [Themenindex](00_INDEX.md) · `FW-INDEX-TEST`
- [Verwandt: Abnahmekriterien Bauring 3 und weitere Statusabschnitte](FW-TEST-008__Abnahmekriterien_Bauring_3_und_weitere_Statusabschnitte.md) · `FW-TEST-008`
- [Verwandt: Abnahmekriterien Bauring 2 und weitere Statusabschnitte](FW-TEST-010__Abnahmekriterien_Bauring_2_und_weitere_Statusabschnitte.md) · `FW-TEST-010`
- [Verwandt: Gate 13E – Reale Handlungsrouten der Skillbäume](../09_SKILLS_MASTERIES_MAGIE_AI/FW-SKILL-015__Gate_13E_Reale_Handlungsrouten_der_Skillbaume.md) · `FW-SKILL-015`
- [Verwandt: Audit aller auffindbaren Simulations- und Redteam-Artefakte vor v22 und weitere Statusabschnitte](FW-TEST-001__Audit_aller_auffindbaren_Simulations-_und_Redteam-Artefakte_vor_v22_und_weiter.md) · `FW-TEST-001`
- [Versionsspur v14](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-14__VERSIONSKARTE_V14.md) · `FW-VERSION-14`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
