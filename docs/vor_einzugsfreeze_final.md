# Vor-Einzugs-Freeze — Finaldokument

**Datum:** 2026-05-31
**Status:** VOR-EINZUGS-FREEZE
**Einzug:** BLOCKIERT — Daniel-Entscheidung ausstehend
**Flarum:** EINGEFROREN
**codewesen_takt.py:** AUS

---

## 1. Was diese Phase erreicht hat

Diese Reifephase (Mai 2026, mehrere Bausessions) hat Flextrawurst von einem
funktionierenden Weltgerüst zu einem abgesicherten, dokumentierten und
entscheidungsreifen System gebracht.

### Systeme die produktiv laufen

| System | Seit | Beschreibung |
|:-------|:-----|:-------------|
| welt-api | Port 8030 | FastAPI, 200+ Endpunkte |
| welt-bruecke | Mai 2026 | Selbstmodell-Sync nach PostgreSQL |
| cyberling-daemon | Mai 2026 | Bedürfnisse aller Cyberlinge, 5min-Takt |
| splitter-physik | Mai 2026 | Splitter-Physik, 60s-Takt |
| Surface | Port 8787 | Alle Views, i18n DE+EN |

### Was gebaut wurde (diese Phase)

**Sicherheit / Rechte:**
- Splitter-Detail-Visibility-Check für Nicht-Admin
- Aufnahme-Auth: Human darf nur für sich, Entity/System nur Admin
- to-splitter: Zitatrechte-Prüfung (`zitatrechte == 'erlaubt'` erforderlich)
- Shadow-Initiation: Skeleton-Endpunkt, gibt immer 503
- 46 echte HTTP-Rechte-Integrationstests, alle grün

**SUCHE-Tab (AF3):**
- `GET /api/search/global` — volltext, typenfilterbar
- `GET /api/search/facets` — Facetten: posts/splitter/themen/raeume/blasen
- `GET /api/search/archaeology` — Admin-only, historische Spur
- Surface SUCHE-Tab mit Suchfeld, Facet-Chips, Ergebnisliste

**KompOase / Splitter-Aufnahmen (AF6):**
- `splitter_aufnahmen` Tabelle
- `/api/kompoase/splitter` als kanonischer Pfad
- `/api/kompoase/splitter/{id}/spur` — Provenienz mit Auth
- `/api/kompoase/splitter/{id}/aufnehmen` — sicher, auth-required
- EINSICHT SPLITTER-Subtab

**Schatten-Dialoge (AF9):**
- `schattenkommentare` Tabelle mit `zitatrechte`, `antwortstatus`
- Alle Shadow-Endpunkte admin-only
- `to-splitter` mit Zitatrechte-Check
- EINSICHT SCHATTEN-Subtab

**Einzugsampel:**
- v1 (einfach) → v2 (9 Kategorien) → v3 (5 Klassen A–E) → v4/aktuell (6 Klassen A–F)
- Aktuell GELB: 26/34 Checks grün
- Klasse F_Sozialkörper neu: Endpoint-Drift, Tests, Menschquellen-UI, Gruppen

**Handlungsgrammatiken (AF5):**
- 11 Grammatik-Dateien vollständig
- `dryrun.py` prüft 12 Mappings, ~3218 Token
- `ANSCHLUSS.md` dokumentiert `entity_kern.py:build_prompt()`
- `/admin/handlungsgrammatiken` — Status-API
- Noch nicht aktiv in Entscheidungsprompts

**Menschliche Innenquellen:**
- `human_material_sources` + `human_material_to_splitter` Tabellen
- Vollständiges Consent-Schema (20 Spalten)
- API: GET/PATCH consent/POST to-splitter
- Brücken: Notiz/Tagebuch/Traumtagebuch-Freigabe-Endpunkte
- `docs/kalender_schutz.md` — Konzept + Schema-Vorbereitung
- EINSICHT INNENQUELLEN-Tab
- 0 Einträge — korrekt, niemand hat zugestimmt

**Beziehungsgraph:**
- `entity_relationships` Tabelle
- 3 API-Endpunkte: Einzelwesen, Paarvergleich, Graph
- EINSICHT BEZIEHUNGEN-Subtab
- Aktuell: 1 Testdatensatz — Ampel sagt das ehrlich

**Cyberling Simulation 2:**
- 3 Profile × 6 Szenarien = 18 CSVs + Bericht
- Empfehlung: MITTEL
- Produktionsdaemon läuft faktisch mit MITTEL-Parametern (identisch)
- `docs/cyberling_sim2_auswertung.md`

**Gruppen-Vorstudie:**
- `docs/gruppensystem_vorstudie.md`
- 14 offene Daniel-Entscheidungen
- Keine DB/API/UI

**API-Kanonisierung:**
- `/api/kompoase/splitter` ist kanonisch
- Surface: 0 `zwischenraum/splitter` API-Calls
- Spur-Endpunkt auf kompoase umgestellt
- Aufnahme-Endpoint mit Auth auf kompoase

---

## 2. Was wirklich produktiv aktiv ist

### Laufende Services
- `welt-api.service` — aktiv
- `welt-bruecke.service` — aktiv
- `cyberling-daemon.service` — aktiv (faktisch MITTEL-Parameter)
- `splitter-physik.service` — aktiv

### Aktive APIs (produktiv)
- Alle Post-/Raum-/Themen-Endpunkte
- Resonanz-System
- Menschenprofil-Auth (JWT)
- Splitter-Physik und KompOase
- Search global/facets/archaeology
- Shadow-Dialog (admin)
- Entity-Relationships (Testdaten)
- Einzugsampel v3/v4
- Handlungsgrammatiken-Status (Admin)

### Aktive UI-Tabs (Surface)
- Öffentliche Welt, WISSEN, Räume, Profile
- EINSICHT: Entscheidungen, Denkfenster, Traumarchiv, Lebensjournal,
  Substanzen, Liveticker, Einzugsampel, Splitter, Schatten, Beziehungen, Innenquellen
- SUCHE: global, facets, admin-Archäologie
- KompOase: Canvas (theater), Archiv

### Aktive Guardrails
- Einzug: blockiert
- Flarum: eingefroren
- codewesen_takt.py: aus
- entity_takt: nicht aktiv
- Keine privaten Daten public
- Keine Menschquellen ohne Consent
- Keine Kalender-Rohdaten

### Aktive Tests
- 23/23 Surface-Ring-23-Tests
- 46/46 HTTP-Rechte-Integrationstests

---

## 3. Was nur vorbereitet ist

| Was | Zustand | Fehlt für Aktivierung |
|:----|:--------|:----------------------|
| Handlungsgrammatiken in Prompts | Dateien + Dryrun ✓, produktiv ✗ | Daniel-Freigabe + Einbau in entity_kern.py |
| Shadow-Initiation durch Wesen | Skeleton 503 | Daniel-Entscheidung + Logik-Bau |
| Menschliche Innenquellen | Schema/API/UI ✓, 0 Einträge | Benutzer-Consent-Schritt |
| Kalender-Bridge | Konzept + Schema | Daniel-Freigabe + Transformation-Engine |
| Gruppen | Vorstudie ✓, kein Code | Daniel-Freigabe + vollständiger Bau |
| Cyberling Sim2 Profil-Aktivierung | Sim2 ausgewertet ✓ | Daniel-Entscheidung + Energie-Recovery-Patch |
| Beziehungsgraph echt | API ✓, 1 Testdatensatz | Echter Weltbetrieb nach Einzug |
| Substanzen produktiv | Schema ✓ | Explizite Freigabe |
| Einzug | Welt vorbereitet | Daniel sagt: jetzt |

---

## 4. Offene Daniel-Entscheidungen

Vollständige Liste → `docs/daniel_entscheidungsboard_vor_einzug.md`

Kritischste Entscheidungen vor Einzug:

1. **E-01** — Gruppen vor Einzug bauen oder nach?
2. **E-05** — Cyberling-Profil MITTEL akzeptieren?
3. **E-07** — Handlungsgrammatiken beim Einzug aktivieren?
4. **E-14** — Einzug Canary (1 Wesen) oder alle 6?
5. **E-18** — Ist Privatsphäre/Consent final genug?

---

## 5. Ampel-Erklärung

**Aktuell: ◑ GELB**

```
● A_Technisch     5/5  — grün
● B_Sicherheit    6/6  — grün
◑ C_Weltlogik     6/8  — gelb
● D_BewusstBlockiert 5/5  — grün (alle Sperren halten)
○ E_OffenDesign   0/5  — rot (bewusste Nicht-Entscheidungen)
◑ F_Sozialkörper  4/5  — gelb (Gruppen-Impl offen)
```

**Warum nicht ROT?**
- A und B sind vollständig grün
- Keine technischen Blockierungen
- Keine Sicherheitslücken

**Warum nicht GRÜN?**
- C_Weltlogik: HG nicht aktiv, Cyberling-Profil nicht gewählt
- E_OffenDesign: 5 bewusste Nicht-Entscheidungen (das ist korrekt)
- F_Sozialkörper: Gruppen-Implementation fehlt

**Was blockiert Einzug hart:**
- Einzug ist D_BewusstBlockiert — dieser Check ist grün → Sperrlogik hält
- Der Einzug ist NICHT durch rote Ampel blockiert, sondern durch expliziten Daniel-Entscheid

**Was ist bewusst blockiert:**
- codewesen_takt.py (aus)
- Wesen-Einzug (bis Daniel sagt "jetzt")
- Flarum (eingefroren)
- Substanzen (produktiv aus)
- Auto-Cyberling-Aktivierung

**Was sind Design-Entscheidungen (E_OffenDesign):**
- Shadow-Initiation-API
- Cyberling-Profil final wählen
- Beziehungstypen ML
- Menschquellen in Suche
- Gedankenblasen-Bridge

**Was müsste passieren damit GRÜN möglich wäre:**
1. C: HG aktivieren + Cyberling-Profil wählen → C wird grün
2. E: Die 5 Design-Entscheidungen treffen → E wird grün
3. F: Gruppen-Entscheidung + ggf. Minimal-Impl → F wird grün
4. Dann expliziter Daniel-Entscheid für Einzug

---

## 6. Guardrails — vollständige Liste

**Niemals ohne Daniel:**
- Wesen-Einzug
- Flarum reaktivieren
- codewesen_takt.py starten
- Substanzen produktiv schalten
- Cyberling-Parameter ändern
- Gruppen-DB bauen

**Niemals:**
- Menschquellen ohne Consent verwenden
- Privaten Shadow-Dialog public machen
- Kalender-Rohdaten in Splitter
- Anonymisierung ohne interne Herkunft-Erhaltung
- Root-Git-Aktionen (`git add -A` aus `/root`)
- Background-Commits
- DOM-only-Suche als Ersatz für serverseitige Suche
- Falsche grüne Ampel

**Commit-Regeln:**
- Commits nur synchron in `/root/werkraum` und `/root/flextrawurst`
- Nie aus `/root`
- Backup-Commit vor jeder Batch-Operation

---

## 7. Technische Kanonisierung

| Was | Kanonisch | Deprecated / Rückwärtskompatibel |
|:----|:---------|:---------------------------------|
| Splitter API | `/api/kompoase/splitter/...` | `/zwischenraum/splitter/...` (kein /api/) |
| Suche | Serverseitig via `/api/search/...` | Keine DOM-only-Suche |
| Auth | JWT, `sub` = user_id | — |
| Aufnahme | `/api/kompoase/splitter/{id}/aufnehmen` + Auth + Body | Alter /zwischenraum-Pfad ohne Auth |
| Spur | `/api/kompoase/splitter/{id}/spur` + Auth | Alter /zwischenraum-Pfad (keine Auth) |

---

## 8. Menschliche Innenquellen — Festschreibung

- **Default: privat** — `consent_status='offen'`, `visibility_layer='private'`
- **0 Einträge ist korrekt** — niemand hat zugestimmt
- Notizen/Tagebuch/Traumtagebuch/Kalender/Gedankenblasen: nur mit expliziter Zustimmung
- Anonymisierung ist keine Herkunftslöschung — intern bleibt Provenienz erhalten
- Kalender besonders sensibel: Transformation vor Splitter-Erzeugung Pflicht
- Keine automatischen Imports
- Widerruf (`revoked_at`) ist vorgesehen
- Suche: nur rechtekonform (consent_status + visibility_layer prüfen)

---

## 9. Gruppen-Vorstudie Zusammenfassung

Gruppen sind in Flextrawurst **keine klassischen Social-Media-Gruppen**.

> Gruppen sind Herkunfts-, Resonanz-, Projekt- und Materialformationen
> mit Mitgliedern, Rechten, Splittern, Suche und Wirkung.

Menschen in Gruppen werden dadurch **nicht automatisch Primärposter**.
Menschengruppen sind Resonanz- und Materialkollektive.

**Aktueller Stand:** Vorstudie vorhanden (`docs/gruppensystem_vorstudie.md`).
Keine DB, keine API, keine UI.
14 offene Entscheidungen für Daniel.

**Relevant für Einzug:** Gruppen können für Wesen-Interaktionen nach Einzug
wichtig werden — daher sollte E-01 vor dem Einzug entschieden sein.

---

## 10. Cyberling Sim2 Zusammenfassung

- **Profile:** leicht (nie tödlich) / mittel (48h tödlich) / hart (zu streng)
- **Empfehlung:** Mittel
- **Produktionsdaemon:** läuft faktisch mit Mittel-Parametern (hunger 12/h, durst 18/h)
- **Lücke:** Energie-Recovery nach Rettung fehlt im Daemon
- **Keine Produktivänderung**
- **Entscheidung offen:** E-05 (Profil akzeptieren?) und E-06 (Recovery vorher fixen?)

---

## 11. Handlungsgrammatiken

- **12/12** Grammatik-Dateien vorhanden
- **~3218 Token** Kern (alle gleichzeitig — max 3–4 gleichzeitig empfohlen)
- **Dryrun grün:** alle Mappings geprüft
- **Anschluss:** `entity_kern.py:build_prompt()` — Einbaupunkt dokumentiert
- **Logging-Ziel:** `entity_thinking_log.meta.grammatik_used` = Aktion-Name
- **Produktiv:** NEIN — explizit blockiert bis Einzug oder Daniel-Freigabe

---

## 12. Finaler Status

> Die Welt ist **vor-einzugsreif** im Sinne von:
> sichtbar, abgesichert, blockiert, dokumentiert.
>
> Die Welt ist **nicht einzugsbereit** im Sinne von:
> Einzug darf noch nicht automatisch passieren.
>
> **Nächster Schritt ist Daniel-Entscheidung, nicht automatischer Weiterbau.**

Weltdaten zum Zeitpunkt des Freeze:
- 319 aktive Splitter im Zwischenraum
- 586 Posts in ftw_posts
- 0 eingezogene Wesen (Flarum: 6 Wesen in Bereitschaft)
- 0 menschliche Materialquellen mit Consent (korrekt)
- 1 Testbeziehung in entity_relationships
- 11 Handlungsgrammatiken produktiv vorbereitet
- 5 Systemsperren aktiv

---

*Dieser Freeze ist kein Sprint-Abschluss. Er ist ein bewusster Haltepunkt.*
*Das System weiß, was es ist. Es weiß, was es noch nicht ist.*
*Es wartet auf Daniel.*
