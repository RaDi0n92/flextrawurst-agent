---
id: FW-SKILL-016
status: BESTAETIGT
typ: source
themenraum: SKILL
version: v21
tags: [beziehung, dust, fragen, kampf, load, loot, magie, playwright, save, skill, test, v21, welt, wesen, zeit]
---

# Gate 13F – Eigene Handlungskörper für die neun offenen Skillbäume

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:docs_v21/GATE_13F_FRAGEN_VORHER_NACHHER.md" sha256="bca702a4d8bb33c61c42b2f7e29ff5272f14896fbea5bc3bf754afdf2df2fd2b" order="1" -->
# Gate 13F – Eigene Handlungskörper für die neun offenen Skillbäume

## Vorbaufragen

1. **Welche Bäume waren nach Gate 13E noch unangebunden?** Pistolen, Maschinengewehre, Laserwaffen, Zweihandwaffen, unbewaffnete Formen, Explosivsysteme, Beschwörungsmagie, Taschendiebstahl und Lehren.
2. **Dürfen sie durch einen generischen Trainingsknopf geschlossen werden?** Nein.
3. **Was unterscheidet die neuen Waffen?** Reichweite, Kadenz, Burst, Wärme, Energieverbrauch, Erholungszeit, Rückstoß und Flächenwirkung.
4. **Wie werden Wesenrechte bei Flächenwirkung geschützt?** Nicht zustimmende empfindungsfähige Zielkörper werden aus der Flächenwirkung technisch ausgenommen.
5. **Was bedeutet unbewaffneter Kampf?** Ein eigener körpergebundener Treffer mit Reichweite, Erholung, Zustimmung und Weltprotokoll.
6. **Was bedeutet Beschwörung?** Ein freiwilliger, zeitlich begrenzter Werkzeug- oder Erinnerungsformkörper ohne Besitzbehauptung.
7. **Wie funktioniert Taschendiebstahl?** Als endliche riskante Besitzhandlung mit Erfolg oder Scheitern, Beziehungsschaden, konkreter Spur und möglicher Rückgabe. Kein unendlicher Lootbeutel.
8. **Wann ist Lehren erfolgreich?** Nur wenn Beziehung, eigene Erfahrung, konkretes Beispiel und überprüfbarer Selbstcheck vorhanden sind und beim Gegenüber ein gespeicherter Lernzuwachs entsteht.
9. **Wie wird Wiederholungsfarming verhindert?** Besitzspuren sind endlich; identische Lektionen werden abgewiesen; Waffenkörper besitzen Kosten, Wärme oder Erholung.

## Geplanter Bau

- `src/v21_skill_action_bodies.js`
- fünf neue herstellbare Waffenkörper
- unterschiedliche Feuer-, Wärme-, Energie-, Rückstoß- und Flächenmechaniken
- unbewaffneter Trefferkörper
- freiwilliger Formruf
- endliche Besitzspuren und Rückgabe
- überprüfbare Wesenlektionen
- sichtbare Laser-, Explosions- und Beschwörungsgeometrie

## Nachbauantworten

1. **Sind alle neun zuvor offenen Skillbäume jetzt an echte Handlungen gebunden?** Ja. Der Routing-Audit meldet 69 von 69 abgedeckte Bäume und keine offene Route.
2. **Unterscheiden sich die fünf neuen Waffenkörper systemisch?** Ja. Pistole, Burst-Rahmen, Laser, Zweihandhammer und Dust-Ladung unterscheiden sich in Kadenz, Mehrfachimpuls, Energie, Wärme, Rückstoß, Erholung, Reichweite und Flächenwirkung.
3. **Ist der Laser wirklich sichtbar?** Ja. Der erste Test entdeckte, dass die Datenlogik eine vom Renderer nicht unterstützte `beam`-Form erzeugte. Diese wurde durch zwölf unterstützte prismatische Strahlsegmente ersetzt. Der vollständige Gate-Lauf wurde danach erneut ausgeführt.
4. **Bleiben Wesenrechte bei Explosiv- und Nahkampfwirkung erhalten?** Ja. Nicht zustimmende empfindungsfähige Zielkörper werden aus der Flächenwirkung ausgeschlossen; unbewaffnete Gewalt wird bei verweigernden Wesen technisch blockiert.
5. **Ist Beschwörung Besitz?** Nein. Der gerufene Werkzeugfalter ist zeitlich begrenzt, besitzt `owner: null` und den Zustimmungsstatus `self-limited`.
6. **Kann Taschendiebstahl endlos gefarmt werden?** Nein. Jede Besitzspur ist endlich, ein zweiter identischer Versuch wird abgewiesen, Vertrauen sinkt, und eine Rückgabe wird als eigene Spur gespeichert.
7. **Kann Lehren durch Wiederholung gefarmt werden?** Nein. Eine Lektion braucht Beziehung, eigene Erfahrung, Titel, Beispiel und Selbstcheck. Eine identische Lektion erzeugt keinen weiteren Fortschritt.
8. **Bleiben die neuen Zustände speicherbar?** Ja. Wärme, Beschwörungen, Besitzspuren, Lektionen und unbewaffnete Historie wurden nach Save/Load vollständig wiederhergestellt.
9. **Playwright-Beleg:** `tests_v21/GATE_13F_RESULT.json` – 15/15 bestanden, 0 Browserfehler, 0 Konsolenfehler.
10. **Screenshot-Beleg:** `screenshots_v21/gate13f_skill_action_bodies.png`.

## Status

`[GATE 13F BESTANDEN – 15/15 PLAYWRIGHT-PRÜFUNGEN]`

<!-- SOURCE_SEGMENT_END source="v21:docs_v21/GATE_13F_FRAGEN_VORHER_NACHHER.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-SKILL-015__Gate_13E_Reale_Handlungsrouten_der_Skillbaume.md) · `FW-SKILL-015`
- [Nächster Knoten](FW-SKILL-017__Gate_13G_Einheitliche_Skillpunktokonomie_und_Legacy-Wirkung.md) · `FW-SKILL-017`
- [Themenindex](00_INDEX.md) · `FW-INDEX-SKILL`
- [Verwandt: Abnahmekriterien Bauring 3 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-008__Abnahmekriterien_Bauring_3_und_weitere_Statusabschnitte.md) · `FW-TEST-008`
- [Verwandt: Audit aller auffindbaren Simulations- und Redteam-Artefakte vor v22 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-001__Audit_aller_auffindbaren_Simulations-_und_Redteam-Artefakte_vor_v22_und_weiter.md) · `FW-TEST-001`
- [Verwandt: K045-Q5 · K045 · Fehlurteil × Beziehungen](../07_BEWEGUNG_FAHRZEUGE_KAMPF_LOOT/FW-MOVE-023__K045-Q5_K045_Fehlurteil_Beziehungen.md) · `FW-MOVE-023`
- [Verwandt: Abnahmekriterien Bauring 2 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-010__Abnahmekriterien_Bauring_2_und_weitere_Statusabschnitte.md) · `FW-TEST-010`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
