---
id: FW-QUEST-002
status: BESTAETIGT
typ: source
themenraum: QUEST
version: v22
tags: [echo, kollision, quest, v22, welt, wesen, zeit]
---

# Echo-Datenmodell und Kristallisierung

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v22:02_questarchitektur/02_ECHO_DATENMODELL_UND_KRISTALLISIERUNG.md" sha256="16559d920988891581884e4943ffa81aa7ade8ff9c745e3b597f8851472f3082" order="1" -->
# Echo-Datenmodell und Kristallisierung

## EchoEvent

| Feld | Funktion |
|---|---|
| `echo_id` | stabile Identität |
| `parent_echo_ids` | frühere Echos, aus denen dieses Echo hervorging |
| `origin_event_id` | reale Handlung, Unterlassung oder Weltveränderung |
| `actor_ids` | aktive Ursprungskörper |
| `affected_ids` | direkt oder indirekt betroffene Körper |
| `observer_ids` | Wesen oder Systeme mit eigener Deutung |
| `place_id` | räumliche Herkunft |
| `time_address` | Zeit-, Epochen- und Rekonstruktionsadresse |
| `frequencies` | materielle, biologische, digitale, magische, relationale, zeitliche und emotionale Anteile |
| `amplitude` | momentane Stärke |
| `persistence` | Abkling- oder Speicherverhalten |
| `interpretations` | mehrere, gegebenenfalls widersprüchliche Lesarten |
| `privacy_scope` | öffentlich, geteilt, privat, unbekannt |
| `rights_constraints` | Zustimmung, Besitz, Schutz und Verweigerung |
| `world_state_hash` | nachvollziehbarer Zustand bei Entstehung |

## ResonanceContact

Ein Echo berührt einen Resonanzkörper. Der Kontakt speichert:

- warum dieser Körper reagieren konnte;
- wie er das Echo wahrnimmt;
- was er falsch versteht;
- welche Ziele, Ängste, Neugierden oder Erinnerungen aktiviert werden;
- welche anderen Körper durch ihn erreicht werden;
- ob die Reaktion sichtbar, verzögert oder geheim bleibt.

## QuestCrystal

Eine Quest kristallisiert erst, wenn ein auslösender Spannungsgraph vorliegt. Pflichtfelder:

- `quest_id`;
- `origin_echo_ids`;
- `crystallization_reason`;
- `participants` mit eigenen Zielen;
- `stakes` für Welt, Wesen, Ort, Zeit und Objekte;
- mindestens drei aktive Handlungsorgane;
- alle zwölf Spielorgane als mögliche Anschlussachsen;
- mindestens drei unterscheidbare Pfade;
- mindestens eine nichtgewaltsame und eine nichtgehorsame Lösung;
- autonome Fortsetzung;
- Auflösungs-, Scheiter-, Vertagungs- und Transformationszustände;
- bleibende Echo-Nachwirkung.

## Kristallisierungsregeln

1. Ein einzelner niedriger Zahlenwert genügt nie.
2. Wiederholung kann ein Meso-Echo erzeugen, darf aber keine XP-Farm sein.
3. Seltene Kollisionen dürfen niedrige Amplitude besitzen und trotzdem kristallisieren.
4. Schweigen, Abwesenheit und Nichtentscheidung sind mögliche Ursachen.
5. Private Echos dürfen nicht ohne Rechteprüfung öffentlich werden.
6. Widersprüchliche Deutungen werden nicht vor Questbeginn zu einer offiziellen Wahrheit geglättet.

<!-- SOURCE_SEGMENT_END source="v22:02_questarchitektur/02_ECHO_DATENMODELL_UND_KRISTALLISIERUNG.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-QUEST-001__Dust-Echo-Grundgesetz_des_Questkosmos_und_weitere_Statusabschnitte.md) · `FW-QUEST-001`
- [Nächster Knoten](FW-QUEST-003__Lebenszyklus_eines_Questkorpers.md) · `FW-QUEST-003`
- [Themenindex](00_INDEX.md) · `FW-INDEX-QUEST`
- [Verwandt: ROHINPUT R22 – Das Dust-Echo-Quest-System](../02_DANIELS_ROHTEXTE_ISOLIERT/FW-RAW-002__ROHINPUT_R22_Das_Dust-Echo-Quest-System.md) · `FW-RAW-002`
- [Verwandt: Quellabschnitt](../15_NETZWERK_INDIZES_QUERVERWEISE/FW-NET-035__Quellabschnitt.md) · `FW-NET-035`
- [Verwandt: D36 – Save/Load und Determinismus](../12_FRAGEN_KOLLISIONEN_ENTSCHEIDUNGEN/FW-QUESTION-003__D36_Save_Load_und_Determinismus.md) · `FW-QUESTION-003`
- [Verwandt: Audit aller auffindbaren Simulations- und Redteam-Artefakte vor v22 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-001__Audit_aller_auffindbaren_Simulations-_und_Redteam-Artefakte_vor_v22_und_weiter.md) · `FW-TEST-001`
- [Versionsspur v22](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-22__VERSIONSKARTE_V22.md) · `FW-VERSION-22`
