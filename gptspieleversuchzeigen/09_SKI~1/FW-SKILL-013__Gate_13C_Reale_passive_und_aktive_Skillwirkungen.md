---
id: FW-SKILL-013
status: BESTAETIGT
typ: source
themenraum: SKILL
version: v21
tags: [fragen, load, magie, playwright, provenienz, save, skill, test, v21, welt, zeit]
---

# Gate 13C – Reale passive und aktive Skillwirkungen

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:docs_v21/GATE_13C_FRAGEN_VORHER_NACHHER.md" sha256="d8e86e570ccaa773ef8971b8b89a2a145a9eb7b8d5af4ae2f3188b4579d85ad9" order="1" -->
# Gate 13C – Reale passive und aktive Skillwirkungen

## Vorbaufragen

1. **Reicht eine freigeschaltete Knoten-ID?** Nein. Jeder geprüfte Knoten muss einen realen Spielzustand verändern.
2. **Wie werden passive Effekte bewiesen?** Durch Vergleich identischer Handlungen vor und nach Freischaltung.
3. **Wie werden aktive Effekte geschützt?** Freischaltung, räumliche Wirkung, Abklingzeit, Kosten und Save/Load.
4. **Darf Heilungsmagie auf volle Ziele gegrindet werden?** Nein.
5. **Wie bleibt Magie sichtbar?** Zeitgebundene Effekte werden als Weltgeometrie gerendert.
6. **Wie werden AI-Aktionen behandelt?** Kontext- und Forschungsaktionen benötigen reale Provenienz- und Experimentkörper.

## Gebaut

- `src/v21_skill_effects.js`
- passive Bonusaggregation
- aktive Fähigkeiten mit Abklingzeiten
- Leichtrüstungsbewegung und Ausweichfaden
- Wiederherstellungswelle
- Schutzblase
- geformte Zerstörung
- gemeinsamer Tisch
- Kontextwiederherstellung
- Werkzeugkette
- reproduzierbares Experiment
- Provenienzöffnung
- begrenzter positiver-Virus-Versuch
- drei zusätzliche Magieschulzauber

## Reparatur

Die Kontextwiederherstellung griff zunächst auf `state.records` zu. Der tatsächliche Ereigniskörper heißt `state.chronicle`. Der Fehler wurde im Spielcode korrigiert und das Gate vollständig wiederholt.

## Playwright

- **Datei:** `tests_v21/test_gate_13c_skill_effects.py`
- **Rohbericht:** `tests_v21/GATE_13C_RESULT.json`
- **Ergebnis:** **11/11 bestanden**
- **Screenshot:** `screenshots_v21/gate13c_skill_effects.png`

## Status

`[GATE 13C BESTANDEN NACH REPARATUR]`

<!-- SOURCE_SEGMENT_END source="v21:docs_v21/GATE_13C_FRAGEN_VORHER_NACHHER.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-SKILL-012__Gate_13B_Kuratierte_Skillbaume_und_Knotengraphen.md) · `FW-SKILL-012`
- [Nächster Knoten](FW-SKILL-014__Gate_13D_AI-Fahigkeiten_als_echte_Arbeitskorper.md) · `FW-SKILL-014`
- [Themenindex](00_INDEX.md) · `FW-INDEX-SKILL`
- [Verwandt: Skillbaum-Simulations- und Redteamplan](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-017__Skillbaum-Simulations-_und_Redteamplan.md) · `FW-TEST-017`
- [Verwandt: K024-Q1 · K024 · Bauen × Ressourcen](FW-SKILL-010__K024-Q1_K024_Bauen_Ressourcen.md) · `FW-SKILL-010`
- [Verwandt: Gate 13E – Reale Handlungsrouten der Skillbäume](FW-SKILL-015__Gate_13E_Reale_Handlungsrouten_der_Skillbaume.md) · `FW-SKILL-015`
- [Verwandt: K120-Q1 · Nachbauprüfung](../08_BAUEN_HANDWERK_MODULARITAET/FW-BUILD-028__K120-Q1_Nachbauprufung.md) · `FW-BUILD-028`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
