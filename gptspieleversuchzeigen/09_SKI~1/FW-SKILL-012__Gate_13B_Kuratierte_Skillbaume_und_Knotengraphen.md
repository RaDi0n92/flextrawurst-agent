---
id: FW-SKILL-012
status: BESTAETIGT
typ: source
themenraum: SKILL
version: v21
tags: [fahrzeug, fragen, magie, playwright, provenienz, skill, test, v21, welt]
---

# Gate 13B – Kuratierte Skillbäume und Knotengraphen

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:docs_v21/GATE_13B_FRAGEN_VORHER_NACHHER.md" sha256="996029909fa0576f6325902e6325f86f25eee4a78f6a2f322fd1e82b87e98c85" order="1" -->
# Gate 13B – Kuratierte Skillbäume und Knotengraphen

## Vorbaufragen

1. **Dürfen 69 Bäume aus vier identischen Platzhaltern bestehen?** Nein. Die ausdrücklich verlangten Kernbäume benötigen individuelle Knoten, Wirkungsbilder und Verantwortungen.
2. **Welche Knotentypen sind Pflicht?** Passive, aktive und transformative Knoten.
3. **Wie bleibt freie Wahl erhalten?** Jeder Baum besitzt mindestens einen Basisknoten ab Stufe 1.
4. **Wie wird Beliebigkeit verhindert?** Höhere Knoten benötigen Vorgänger und konkrete Skillstufen.
5. **Wie werden AI-Skills behandelt?** Kontext, Werkzeuge, Forschung, Provenienz und positiver Virus erhalten echte eigenständige Bäume.
6. **Wie wird Graphqualität geprüft?** Eindeutige IDs, interne Voraussetzungen, Zyklenfreiheit und topologische Erreichbarkeit.

## Gebaut

- `src/v21_skill_nodes.js`
- 22 vollständig kuratierte Kernbäume
- mindestens vier Knoten pro Baum im Gesamtkatalog
- spezifische Knoten für Rüstungen, Heimlichkeit, Waffen, Magieschulen, Kochen, Fahrzeuge, Kontext, Tools, Forschung, Provenienz und positiven Virus

## Nachbaufragen und Belege

- 22 Kernbäume individuell kuratiert
- alle explizit verlangten Kernbäume vorhanden
- alle 69 Bäume besitzen mindestens vier Knoten
- Knoten-IDs weltweit eindeutig
- Voraussetzungen bleiben innerhalb ihres Baums
- keine direkten oder topologischen Zyklen
- passive, aktive und transformative Typen vorhanden
- 174 unterschiedliche Knotenbeschreibungen
- frühe Punkte quer über Körper, Magie, Handwerk und AI investierbar
- kuratierte Namen erscheinen in der realen UI

## Playwright

- **Datei:** `tests_v21/test_gate_13b_skill_graph.py`
- **Rohbericht:** `tests_v21/GATE_13B_RESULT.json`
- **Ergebnis:** **12/12 bestanden**
- **Screenshot:** `screenshots_v21/gate13b_skill_graph.png`

## Testkorrektur

Der erste Prüflauf suchte mit `inner_text()` auch Inhalte geschlossener `<details>`. Playwright behandelt diese korrekt als nicht sichtbar. Der Prüfkörper wurde auf `text_content()` korrigiert. Der Spielkörper musste dafür nicht verändert werden.

## Status

`[GATE 13B BESTANDEN]`

<!-- SOURCE_SEGMENT_END source="v21:docs_v21/GATE_13B_FRAGEN_VORHER_NACHHER.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-SKILL-011__Gate_13A_Gesamtlevel_freie_Skillpunkte_und_universeller_Skillkatalog.md) · `FW-SKILL-011`
- [Nächster Knoten](FW-SKILL-013__Gate_13C_Reale_passive_und_aktive_Skillwirkungen.md) · `FW-SKILL-013`
- [Themenindex](00_INDEX.md) · `FW-INDEX-SKILL`
- [Verwandt: K024-Q1 · K024 · Bauen × Ressourcen](FW-SKILL-010__K024-Q1_K024_Bauen_Ressourcen.md) · `FW-SKILL-010`
- [Verwandt: Gate 13E – Reale Handlungsrouten der Skillbäume](FW-SKILL-015__Gate_13E_Reale_Handlungsrouten_der_Skillbaume.md) · `FW-SKILL-015`
- [Verwandt: K120-Q1 · Nachbauprüfung](../08_BAUEN_HANDWERK_MODULARITAET/FW-BUILD-028__K120-Q1_Nachbauprufung.md) · `FW-BUILD-028`
- [Verwandt: Changelog · v21 final und weitere Statusabschnitte](../15_NETZWERK_INDIZES_QUERVERWEISE/FW-NET-001__Changelog_v21_final_und_weitere_Statusabschnitte.md) · `FW-NET-001`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
