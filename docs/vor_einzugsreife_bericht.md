# VOR-EINZUGSREIFEKÖRPER — Abschlussbericht
**Datum:** 2026-05-31
**Stand:** Ampel GELB — sicher, nicht vollständig

---

## Gesamtlage

Flextrawurst hat vor diesem Bericht eine strukturelle Reifeschicht erhalten,
die technische Solidität, Sicherheitskontrakte und Weltlogik-Vorbereitungen vereint.
Der Einzug der Wesen ist weiterhin **blockiert** — bewusst und korrekt.
Die Ampel zeigt GELB: kein roter Blocker, aber offene Weltlogik-Entscheidungen.

---

## Was wurde gebaut

### TEIL 1 — Sicherheit (Security-Fixes)

| Nr | Fix | Status |
|:---|:----|:-------|
| A | Splitter-Detail-Visibility-Check (kompoase + zwischenraum) | ✓ |
| A2 | Zweiter Splitter-Endpunkt identisch abgesichert | ✓ |
| B | Aufnahme-Auth: human=eigene ID erzwungen, entity/system nur Admin | ✓ |
| D | to-splitter: Zitatrechte-Prüfung (zitatrechte=='erlaubt' vorausgesetzt) | ✓ |

### TEIL 2 — Menschliche Innenquellen (Datenmodell)

- `human_material_sources` Tabelle mit vollständigem Consent-Schema
- `human_material_to_splitter` Junction-Tabelle
- 4 API-Endpunkte: GET Liste, GET Detail, PATCH Consent, POST to-splitter
- Default: `consent_status='offen'`, `visibility_layer='private'` — nichts automatisch
- Doku: `docs/menschliche_innenquellen.md` — vollständiges Konzeptdokument

### TEIL 5 — Beziehungsgraph API

- `GET /api/entities/{id}/relationships` — Beziehungen eines Wesens
- `GET /api/relationships/between/{a}/{b}` — Direktvergleich
- `GET /api/relationships/graph` — Admin-Graphübersicht
- Helfer: `_beziehung_typ()` (6 Stufen), `_beziehung_evidence()` (shadow_dialogs + splitter + events)

### TEIL 6 — Grammatik Dry-Run Tool

- `wesen_handlungsgrammatiken/dryrun.py` — kein Produktivcode
- 12 Aktions-Grammatik-Mappings geprüft, alle vorhanden
- Token-Schätzung: ~3184 Kern-Token für alle Grammatiken gleichzeitig
- Empfehlung: maximal 3–4 gleichzeitig laden

### TEIL 7 — Schatten-Initiation API (Skeleton)

- `POST /api/shadow/initiate` — immer 503, mit klarem Log
- Endpunkt existiert, Logik nicht aktiv, kein Aktivierungspfad ohne Daniel

### TEIL 8 — Cyberling Simulation 2

- `welt/cyberling_balancing/simulate2.py` — kein Produktivcode
- 3 Profile: Leicht / Mittel / Hart
- 6 Szenarien: perfekt / normal / leicht verspätet / 12h / 24h / 48h vernachlässigt
- 18 CSVs + `SIM2_BERICHT.md` in `output_sim2/`
- **Empfehlung:** Mittel als Default — Energie nicht dekorativ, Tod erst bei 48h+

### TEIL 9 — Ampel v3

- `GET /admin/einzugsampel/v3` — 5 Klassen A–E, 28 Prüfungen
- Klasse A (Technisch): 5/5 ✓
- Klasse B (Sicherheit): 6/6 ✓
- Klasse C (Weltlogik): 5/7 — 2 offen (HG-Aktivierung, Cyberling-Profil)
- Klasse D (BewusstBlockiert): 5/5 ✓ — alle Sperren halten
- Klasse E (OffenDesign): 0/5 — bewusst unentschieden

### TEIL 10 — Semantische Rechte-Tests

- `tests/world_os_ring_23_semantic_rights.test.ts` — 38 Tests, alle grün
- 7 Test-Suiten:
  - Splitter-Sichtbarkeitsmatrix (5 Tests)
  - Consent-Zustandsautomat (6 Tests)
  - Beziehungstyp-Ableitung (7 Tests)
  - Grammatik-Mapping-Vollständigkeit (5 Tests)
  - Ampel-v3-Klassenstruktur (8 Tests)
  - Schatten-Initiations-Sperre (3 Tests)
  - Suchtyp-Definitionen (4 Tests)

### TEIL 11 — Surface

- BEZIEHUNGEN-Subtab: Ladeliste + `eiZeigeBeziehung()` Detail-Panel
- Ampeldetail auf v3: 5-Klassen-Raster mit A–E-Labels und Blocker-Visualisierung
- `eiLadeAmpel()` → `/admin/einzugsampel/v3`
- 308 i18n-Keys, 23/23 Surface-Tests grün

---

## Was bewusst NICHT gebaut wurde

| Was | Warum |
|:----|:------|
| Wesen-Einzug | Daniel-Entscheidung ausstehend |
| HG-Aktivierung in Entscheidungsprompts | Braucht Daniel-Auftrag, ANSCHLUSS.md dokumentiert Einbaupunkt |
| Cyberling Profil-Aktivierung | Sim2-Ergebnis liegt vor, Entscheidung bei Daniel |
| Gedankenblasen→human_material Bridge | Konzept fertig, DB-Bridge braucht Auftrag |
| Menschquellen in Suche | Schema vorhanden, Search-Extension braucht Auftrag |
| Schattenkommentar-Aktion API | Initiations-Skeleton gebaut, Logik gesperrt |
| Flarum-Import | Eingefroren |
| codewesen_takt.py | Deaktiviert |

---

## Ampel-Zusammenfassung

```
◑ GELB — Einzug blockiert, sicher
  ● A Technisch     5/5
  ● B Sicherheit    6/6
  ◑ C Weltlogik     5/7  (HG nicht aktiv, Cyberling-Profil nicht gewählt)
  ● D BewusstBlockiert 5/5  (alle Sperren halten)
  ○ E OffenDesign   0/5  (5 offene Designfragen)
```

**Was grün bräuchte:**
- C: HG in Entscheidungsprompts aktivieren + Cyberling Default-Profil wählen
- E: 5 Design-Entscheidungen treffen (Schattenkommentar-API, Cyberling-Profil, Beziehungslernen, Menschquellen-Suche, Gedankenblasen-Bridge)

---

## Nächste mögliche Schritte (nach Entscheidung)

1. **Cyberling Default-Profil** → Mittel in `cyberling_daemon.py` aktivieren
2. **HG aktivieren** → `_lade_grammatik_kontext()` in `entity_kern.py` einbauen (ANSCHLUSS.md zeigt wie)
3. **Gedankenblasen-Bridge** → Bridge von `gedankenblasen` zu `human_material_sources`
4. **Menschquellen in Suche** → `human_material` als Search-Typ
5. **Wesen-Einzug** → Erst wenn Daniel sagt: "jetzt"

---

## Was die Welt jetzt trägt

- 301 aktive Splitter im Zwischenraum
- 1 Beziehung in entity_relationships (Testdaten)
- 0 menschliche Materialquellen mit Consent (korrekt — niemand hat zugestimmt)
- 11/11 Handlungsgrammatiken vorhanden, nicht aktiv
- Alle 5 Sperren halten: Flarum ✓, Takt ✓, Einzug ✓, Substanzen ✓, Auto-Promotion ✓

---

*Dieser Körper ist kein Sprint-Ergebnis — er ist eine Reifeschicht.*
*Er sagt nicht "bereit". Er sagt "sicher, ehrlich, gut vorbereitet".*
