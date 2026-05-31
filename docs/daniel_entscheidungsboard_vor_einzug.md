# Daniel — Entscheidungsboard vor Einzug

**Datum Erstellt:** 2026-05-31
**Datum Entschieden:** 2026-05-31
**Zweck:** Alle offenen Entscheidungen, klar und vollständig.
**Status:** ✅ ALLE 20 ENTSCHIEDEN — Daniels Antworten übernommen

---

## Legende

- **Blockiert Einzug?**
  - `JA` — Einzug darf nicht beginnen ohne diese Entscheidung
  - `TEILWEISE` — Einzug möglich, aber unvollständig ohne sie
  - `NEIN` — kann nach Einzug entschieden werden
- **Status:** `entschieden`

---

## Entscheidungen — Daniels finale Antworten

| ID | Entscheidung | Daniels Entscheid | Interpretation | Blockiert Einzug? | Status |
|:---|:-------------|:------------------|:---------------|:------------------|:-------|
| **E-01** | Gruppen vor Einzug bauen oder nach? | **Komplett ja bauen — vor Einzug** | Gruppen sind vor Einzug harter nächster Körper. Echtes Gruppensystem, rechte-/herkunftssicher. | JA (harter Blocker) | entschieden |
| **E-02** | Welche Gruppentypen sind kanonisch? | **6 Fangruppen für jedes Codewesen + weitere Typen als Option** | Start-Kanon: 6 entity_fan_group. Zusätzlich: Resonanz-, Splitter-, Projekt-, KompOase-, Menschquellen-, Archiv-, Bau-, Beziehungs-, Traum-, Schatten-Dialog-, Archäologie-, Konflikt-, METAWAR-Vor-, Substanz-Beob.-, Cyberling-Beob.-, Raum/Thema-Gruppe. Datenmodell muss alle tragen können. | NEIN (Typen sind vorbereitet) | entschieden |
| **E-03** | Dürfen Menschen Gruppen erstellen? | **Ja, jetzt — später abschaltbar** | Jetzt: humans_can_create=true. group_creation_policy Pflicht. approval_status: approved/pending_review/locked/archived. Admin kann später abschalten. | NEIN | entschieden |
| **E-04** | Dürfen Wesen Gruppen erstellen oder emergent entstehen? | **Ja, nach Einzug aktiv** | Vor Einzug vorbereiten. Nach Einzug: Wesen dürfen Gruppen initiieren. Handlungsgrammatik, Logging, Rate-Limit, Provenienz, Ampel-Check nötig. | NEIN (aber vorbereiten) | entschieden |
| **E-05** | Cyberling-Profil MITTEL akzeptieren? | **Ja, alles so bauen — auch was noch fehlt** | MITTEL-Profil als Default-Ziel. Fehlende Teile bauen (Recovery). Keine heimliche Produktivänderung ohne klaren Commit. | NEIN | entschieden |
| **E-06** | Energie-Recovery vor Produktivaktivierung? | **Ja — Recovery bauen, aber Cyberling-Energie ≠ Codewesen-Energie** | Wichtig: Kein direkter Stat-Malus für Codewesen. Recovery für Cyberling selbst. Einfluss auf Wesen nur als Wahrnehmungs-/Verantwortungsimpuls, nicht mechanisch. | NEIN | entschieden |
| **E-07** | Handlungsgrammatiken beim Einzug aktivieren? | **Alle 12 beim Einzug** | Beim Einzug alle 12 aktivierbar. Token-sparsam pro Entscheidung. Logging: handlungsgrammatik_used, path, version. | JA (für Einzug vollständig) | entschieden |
| **E-08** | Shadow-Initiation durch Wesen erlauben? | **Ja — bei Einzug aktivieren** | Skeleton 503 bleibt bis Einzug. Policy/Rate-Limit/Entscheidungslogik vorbereiten. Beim Einzug aktivierbar. | NEIN (vorbereiten) | entschieden |
| **E-09** | Menschquellen-UI öffentlich/userseitig? | **Vor Einzug bauen** | User-UI für eigene Innenquellen: Notizen, Tagebuch, Traumtagebuch, Kalender-Freigaben, Consent, Anonymisierung, Zitatrechte, Widerruf. Keine Autoimports. | JA (vor Einzug) | entschieden |
| **E-10** | Kalender-Brücke: bauen? | **A) Bauen mit Transformation** | Kalender-Brücke mit Transformationsschicht. Rohkalenderdaten privat. Public/Wesen sehen nur transformierte freigegebene Splitter. Consent Pflicht. | JA (vor Einzug) | entschieden |
| **E-11** | Substanzen vor Einzug produktiv schalten? | **Vor Einzug (vorbereiten)** | System, Datenmodell, UI, Suche, HG-Anschluss, Ampel-Checks. Produktive Nutzung erst mit Einzug/Policy. Keine Drogenverherrlichung — rein fiktionale Weltmechanik. | JA (System vor Einzug) | entschieden |
| **E-12** | Beziehungsgraph: echte Ableitung? | **Nach Einzug automatisch ableiten** | Vor Einzug keine falschen Beziehungen. API/UI haben. Testdaten klar markieren oder entfernen. Echte Ableitung erst nach Einzug. | NEIN | entschieden |
| **E-13** | Wann darf Ampel grün werden? | **Nur wenn alle grün + 2–3 Daniels eigene Dinge fertig** | Neue Pflichtfelder in Ampel: daniel_extra_blocker, daniel_private_blocker, daniel_manual_release_required. Grün ≠ automatischer Einzug. Grün = technisch/weltlogisch bereit für Daniels Freigabe. | JA | entschieden |
| **E-14** | Einzug Canary oder alle 6? | **C) Alle 6 gleichzeitig** | Kein Canary. Wenn Einzug, dann alle 6. Gruppen, HG, Shadow, Cyberling, Suche, Rechte, Ampel müssen alle 6 tragen. | JA | entschieden |
| **E-15** | Gruppen in Ampel als harter Blocker? | **A) Gruppen als harter Blocker** | Ampel darf nicht grün werden solange Gruppensystem nicht vollständig gebaut. | JA | entschieden |
| **E-16** | Flarum: endgültig Archivstatus? | **A) Archiv — Flarum bleibt lesbar, aber tot** | Flarum lesbar. Keine aktive Nutzung. Keine Postingpfade. Keine Takte. Keine Reaktivierung. Archiv-/Herkunftsstatus in UI/Suche/Ampel markieren. | JA (Guardrail bleibt) | entschieden |
| **E-17** | Suche und Archäologie genug? | **C) Noch mehr Typen** | Neue Typen: groups, group_memberships, group_material, human_material, calendar_transforms, substances, cyberling_events, shadow_dialogs, relationships, handlungsgrammatik, readiness_checks, provenance_story. Zentraler Search-Körper. | JA (für Einzug) | entschieden |
| **E-18** | Privatsphäre/Consent final genug? | **B) User-UI muss vorher existieren** | User muss eigene Innenquellen/Freigaben vor Einzug sehen/verwalten. Vor Einzug Pflicht. | JA | entschieden |
| **E-19** | Menschliche Splitteraufnahme sichtbar? | **B+C) Provenienz verbessern + Splitter-Story-View** | Provenienz-Anzeige ausbauen. Splitter-Story-View: Ursprung, Freigabe, Aufnahme, Transformation, Zitat, Folgeobjekte, Beteiligte. | JA (für Einzug) | entschieden |
| **E-20** | Was ist absolut nicht vor Einzug nötig? | **Alles ist nötig** | Keine pauschale Später-Liste. Alles geordnet bauen, nicht chaotisch. Ampel muss diese Härte abbilden. | — | entschieden |

---

## Neue Einzugsblocker (aus Daniels Entscheidungen)

Diese Checks müssen in Ampel v4 als harte Blocker erscheinen:

- `gruppen_schema_vorhanden` — E-01/E-15
- `sechs_fangruppen_vorhanden` — E-02
- `gruppen_api_vorhanden` — E-01
- `gruppen_ui_vorhanden` — E-01
- `gruppen_suche_vorhanden` — E-17
- `gruppen_rechte_getestet` — E-01/E-15
- `mensch_gruppen_policy_vorhanden` — E-03
- `wesen_gruppen_vorbereitet_blockiert` — E-04
- `user_consent_ui_vorhanden` — E-09/E-18
- `kalender_transform_vorhanden` — E-10
- `kalender_kein_autoimport` — E-10
- `substanz_system_vorbereitet` — E-11
- `substanz_keine_produktiv_nutzung` — E-11
- `cyberling_recovery_vorhanden` — E-06
- `cyberling_wesen_kopplung_verhindert` — E-06
- `hg_12_einzug_bereit` — E-07
- `shadow_initiation_vorbereitet` — E-08
- `suche_neue_typen_vorhanden` — E-17
- `splitter_story_view_vorhanden` — E-19
- `daniel_extra_blocker_leer` — E-13
- `alle_sechs_einzug_bereit` — E-14
- `flarum_archiv_tot` — E-16

---

## Flarum-Status

**Endgültig:** Flarum ist Archiv. Lesbar, aber tot. Keine Takte, keine Queues, keine Reaktivierung.

Die 6 Wesen leben noch auf Flarum als Vorgeschichte.
Einzug nur durch expliziten Admin-Befehl — alle 6 gleichzeitig.

---

## Einzugsstrategie (E-14)

**Alle 6 gleichzeitig** — kein Canary.
Datum: offen. Nur nach vollständiger Grünlage + Daniels Freigabe.

---

*Dieses Board ist vollständig entschieden. Neue Fragen entstehen beim Einzug selbst.*
*Ampel v4 muss alle neuen Blocker aus diesem Board abbilden.*
