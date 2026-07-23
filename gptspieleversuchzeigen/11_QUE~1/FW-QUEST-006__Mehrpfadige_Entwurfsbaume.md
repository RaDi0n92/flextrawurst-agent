---
id: FW-QUEST-006
status: BESTAETIGT
typ: source
themenraum: QUEST
version: v22
tags: [dialog, dust, echo, provenienz, quest, redteam, test, v22, welt, wesen]
---

# Mehrpfadige Entwurfsbäume

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v22:02_questarchitektur/08_MEHRPFADIGE_ENTWURFSBAEUME.md" sha256="36ecb78dbd8d39fb4ca511e45395234fa625247d17f4eb58c55e0e6fc30e7955" order="1" -->
# Mehrpfadige Entwurfsbäume

Dieses Dokument veröffentlicht Alternativen, Kriterien und Entscheidungen. Es enthält keine private Gedankenkette.

## Architektur A – reine Vorlagenkombination

**Stärke:** kontrollierbar und leicht testbar.  
**Schwäche:** erzeugt schnell austauschbare Aufgaben mit wechselnden Namen.  
**Entscheidung:** nur als sprachliche Oberflächenhilfe verwenden.

## Architektur B – vollständig freie Agentenerzählung

**Stärke:** überraschend und dialogreich.  
**Schwäche:** schwache Kausalität, schwer reproduzierbar, hohe Halluzinations- und Provenienzgefahr.  
**Entscheidung:** nicht als Wahrheitskern verwenden; Agenten dürfen nur deuten und formulieren.

## Architektur C – globaler Questdirector

**Stärke:** gute Dramaturgie und Pacingkontrolle.  
**Schwäche:** Welt wird heimlich um den Spieler inszeniert; Wesenautonomie wird Theater.  
**Entscheidung:** Director darf Spannung aus vorhandenen Echos lesen, aber keine Herkunft erfinden.

## Architektur D – Dust-Echo-Kristallisator

**Stärke:** kausal, weltgebunden, autonom, reproduzierbar und offen für Emergenz.  
**Schwäche:** benötigt starke Datenmodelle und kann ohne Dramaturgieschicht trocken werden.  
**Entscheidung:** gewählt als Kern.

## Architektur E – Hybrid

Gewählter Gesamtweg:

1. Ereignisse und Echos sind autoritative Weltquelle.
2. Wesen deuten Echos aus ihrer Perspektive.
3. Kristallisator erzeugt Queststruktur und Pfade.
4. Dramaturgieschicht ordnet Spannung, ohne Ursachen umzuschreiben.
5. Sprachschicht erzeugt Dialoge aus bestätigten Perspektiven.
6. Redteam prüft Grind, Scheinvielfalt, Rechte, Kausalität und Flextrawurst-Identität.

<!-- SOURCE_SEGMENT_END source="v22:02_questarchitektur/08_MEHRPFADIGE_ENTWURFSBAEUME.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-QUEST-005__Autonome_Fortsetzung_und_Spielerabwesenheit.md) · `FW-QUEST-005`
- [Nächster Knoten](FW-QUEST-007__Belohnungen_Masteries_und_Freischaltungen.md) · `FW-QUEST-007`
- [Themenindex](00_INDEX.md) · `FW-INDEX-QUEST`
- [Verwandt: Quellabschnitt](../15_NETZWERK_INDIZES_QUERVERWEISE/FW-NET-035__Quellabschnitt.md) · `FW-NET-035`
- [Verwandt: Audit aller auffindbaren Simulations- und Redteam-Artefakte vor v22 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-001__Audit_aller_auffindbaren_Simulations-_und_Redteam-Artefakte_vor_v22_und_weiter.md) · `FW-TEST-001`
- [Verwandt: Dust-Echo-Grundgesetz des Questkosmos und weitere Statusabschnitte](FW-QUEST-001__Dust-Echo-Grundgesetz_des_Questkosmos_und_weitere_Statusabschnitte.md) · `FW-QUEST-001`
- [Verwandt: D36 – Save/Load und Determinismus](../12_FRAGEN_KOLLISIONEN_ENTSCHEIDUNGEN/FW-QUESTION-003__D36_Save_Load_und_Determinismus.md) · `FW-QUESTION-003`
- [Versionsspur v22](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-22__VERSIONSKARTE_V22.md) · `FW-VERSION-22`
