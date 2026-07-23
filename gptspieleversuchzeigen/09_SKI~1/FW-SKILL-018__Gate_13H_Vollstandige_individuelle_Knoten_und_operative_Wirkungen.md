---
id: FW-SKILL-018
status: BESTAETIGT
typ: source
themenraum: SKILL
version: v21
tags: [beziehung, fahrzeug, fragen, kampf, load, magie, mastery, playwright, save, simulation, skill, test, v21, welt, zeit]
---

# Gate 13H – Vollständige individuelle Knoten und operative Wirkungen

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:docs_v21/GATE_13H_FRAGEN_VORHER_NACHHER.md" sha256="52e03db4145cf32ff0829831eeb07363b9bb1747e398611b882627ff6c8335df" order="1" -->
# Gate 13H – Vollständige individuelle Knoten und operative Wirkungen

## Vorbaufragen

1. **Was hat die erste 10.000er-Simulation als rot erkannt?** 164 generische Knoten, 53 nicht ausführbare aktive Knoten und 148 passive oder transformative Knoten ohne operative Wirkung.
2. **Darf ein Baum aus vier umbenannten Standardknoten bestehen?** Nein. Jeder Baum braucht eine zum tatsächlichen Handlungsfeld passende innere Entwicklung.
3. **Was muss ein aktiver Knoten tun?** Eine konkrete Handlung mit Kosten, Zustand, Abklingzeit, sichtbarer Weltspur und Save-/Load-fähigem Ereignis auslösen.
4. **Was muss ein passiver Knoten tun?** Eine vom Spiel tatsächlich gelesene operative Eigenschaft verändern, etwa Kontrolle, Effizienz, Sicherheit, Erkenntnis, Beziehung, Präzision oder Widerstand.
5. **Was muss ein transformativer Knoten tun?** Eine dauerhafte, sichtbare und protokollierte Verbindung zwischen Skill und Welt herstellen.
6. **Wie bleiben alte Krallenhaken-, Schirm- und Handwerkswirkungen geschützt?** Ihre IDs bleiben erhalten und werden in die vollständigen neuen Bäume integriert.
7. **Wie wird verhindert, dass alle aktiven Fähigkeiten trotz anderer Namen gleich sind?** Die Wirkungsschicht unterscheidet Bewegungs-, Fahrzeug-, Magie-, Kampf-, Heimlichkeits-, Handwerks-, Welt-, Beziehungs- und Erkenntniskörper.
8. **Was wird direkt geprüft?** Vollständigkeit aller 69 Graphen, Effektkörper, Abklingzeiten, sichtbare Geometrie, passive Nutzung, Transformation, Legacy-Wirkung und Speicherung.

## Geplanter Bau

- `src/v21_skill_nodes_complete.js`
- 41 vollständig neu entworfene bisher generische Bäume
- vollständige aktive Wirkungsschicht für alle noch offenen Knoten
- operative passive Bonusfamilien
- sichtbare transformative Weltmarker
- eigener Playwright-Gate-Test

## Nachbauantworten

1. **Sind generische Knotenkörper übrig?** Nein. Der vollständige Katalog enthält keinen der früheren `_foundation`, `_practice`, `_active` oder `_mastery`-Platzhalter mehr.
2. **Besitzt jeder aktive Knoten einen Wirkungscode?** Ja. 69 Bäume wurden vollständig geprüft.
3. **Besitzen passive und transformative Knoten operative Effekte?** Ja. Ein erster Lauf fand noch den einzelnen Alt-Knoten `rm_need` ohne Effekt. Er erhielt die zugesagte Heilungseffizienz; danach wurde das gesamte Gate erneut ausgeführt.
4. **Sind die Graphen geschlossen?** Ja. Keine doppelten IDs, fehlenden Voraussetzungen oder unerreichbaren Knoten.
5. **Verändern passive Boni reale Handlungen?** Ja. Freigeschaltete Kontrolle und Effizienz wurden in der operativen Bonusfamilie gelesen; Handwerk erzeugte einen Objektkörper über Zustand 100 mit eigener Qualitätsbiografie.
6. **Sind aktive Wirkungen verschieden?** Ja. Bewegung, Fahrzeug, Magie, Kampf, Handwerk, Welt, Beziehung und Erkenntnis erzeugten getrennte Zustands- und Ereigniskörper.
7. **Gibt es Abklingzeiten?** Ja. Sofortige Wiederholung einer aktiven Fähigkeit wurde abgewiesen.
8. **Erzeugen Transformationen Weltspuren?** Ja. Transformative Knoten erzeugen gespeicherte und sichtbare Marker.
9. **Bleiben Legacy-Wirkungen erhalten?** Ja. Fernanker beeinflusst weiterhin die reale Seilphysik.
10. **Bleibt alles speicherbar?** Ja. Aktive Ereignisse und Transformationen wurden nach Save/Load vollständig wiederhergestellt.
11. **Playwright-Beleg:** `tests_v21/GATE_13H_RESULT.json` – 15/15 bestanden, 0 Browserfehler, 0 Konsolenfehler.
12. **Screenshot-Beleg:** `screenshots_v21/gate13h_complete_skill_nodes.png`.

## Status

`[GATE 13H BESTANDEN – 15/15 PLAYWRIGHT-PRÜFUNGEN]`

<!-- SOURCE_SEGMENT_END source="v21:docs_v21/GATE_13H_FRAGEN_VORHER_NACHHER.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-SKILL-017__Gate_13G_Einheitliche_Skillpunktokonomie_und_Legacy-Wirkung.md) · `FW-SKILL-017`
- [Nächster Knoten](FW-SKILL-019__1._Dust-Ontologie.md) · `FW-SKILL-019`
- [Themenindex](00_INDEX.md) · `FW-INDEX-SKILL`
- [Verwandt: Abnahmekriterien Bauring 3 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-008__Abnahmekriterien_Bauring_3_und_weitere_Statusabschnitte.md) · `FW-TEST-008`
- [Verwandt: Audit aller auffindbaren Simulations- und Redteam-Artefakte vor v22 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-001__Audit_aller_auffindbaren_Simulations-_und_Redteam-Artefakte_vor_v22_und_weiter.md) · `FW-TEST-001`
- [Verwandt: Abnahmekriterien Bauring 2 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-010__Abnahmekriterien_Bauring_2_und_weitere_Statusabschnitte.md) · `FW-TEST-010`
- [Verwandt: Gate 13E – Reale Handlungsrouten der Skillbäume](FW-SKILL-015__Gate_13E_Reale_Handlungsrouten_der_Skillbaume.md) · `FW-SKILL-015`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
