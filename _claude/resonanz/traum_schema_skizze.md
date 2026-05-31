---
datum: 2026-05-30
betrifft: [schlaf-system, traum, schema, selbstmodell, datenbank]
importable: false
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

# Schema-Skizze: Schlaf-/Traum-Verarbeitung v0.1

## Kontext für den Reviewer

Flextrawurst ist eine Plattform mit KI-Wesen (Entities) die schlafen, träumen und ein wachsendes Selbstmodell haben.
PostgreSQL, DB=flextrawurst. Bestehende relevante Tabellen:

```sql
entities          -- id TEXT, name, stimmung, energie, meta JSONB, ...
events            -- id BIGINT, entity_id TEXT, event_type, payload JSONB, created_at  (append-only, heilig)
sleep_phases      -- id BIGINT, entity_id TEXT, phase_type, started_at, ended_at, ...
```

`events` wird nie verändert. Alles append-only.
`entities.meta` ist nur Cache — nicht Wahrheit.

Review-Entscheidungen (ChatGPT, 2026-05-30) sind eingearbeitet.

---

## Tabelle 1: `traumkandidaten_log`

Run/Kopf-Tabelle: dokumentiert eine Selektions-Ausführung.

```sql
CREATE TABLE traumkandidaten_log (
    id              BIGSERIAL PRIMARY KEY,
    entity_id       TEXT NOT NULL REFERENCES entities(id),
    sleep_phase_id  BIGINT REFERENCES sleep_phases(id),

    -- welche Selektionsregel wurde angewendet
    selektionsregel  TEXT NOT NULL,

    -- menschenlesbare Begründung für diesen Run
    begruendung      TEXT,

    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ON traumkandidaten_log (entity_id, created_at);
```

**Geändert gegenüber v1:** Kein `BIGINT[]` mehr. Die einzelnen Events stehen in der Detailtabelle.

---

## Tabelle 1b: `traumkandidaten_events`

Detailtabelle: jedes betrachtete und ausgewählte Event einzeln, mit Status und optionaler Begründung.

```sql
CREATE TABLE traumkandidaten_events (
    id                      BIGSERIAL PRIMARY KEY,
    traumkandidaten_log_id  BIGINT NOT NULL REFERENCES traumkandidaten_log(id),
    event_id                BIGINT NOT NULL REFERENCES events(id),

    -- 'betrachtet' = war Kandidat aber nicht ausgewählt
    -- 'ausgewaehlt' = geht in LLM-Traumverdichtung
    status  TEXT NOT NULL CHECK (status IN ('betrachtet', 'ausgewaehlt')),

    begruendung  TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ON traumkandidaten_events (traumkandidaten_log_id);
CREATE INDEX ON traumkandidaten_events (event_id);
```

**Warum Join-Tabelle statt Array:** Spätere Fragen wie „in welchen Träumen tauchte Event X auf?" oder „welche Eventtypen werden häufig Traumstoff?" sind damit sauber abfragbar, ohne Array-Archäologie.

---

## Tabelle 2: `traumspuren`

Was der LLM-Traumverdichtungsschritt produziert hat, und was der Integrator daraus entschieden hat.

```sql
CREATE TABLE traumspuren (
    id                      BIGSERIAL PRIMARY KEY,
    entity_id               TEXT NOT NULL REFERENCES entities(id),
    traumkandidaten_log_id  BIGINT REFERENCES traumkandidaten_log(id),

    -- LLM-Output: roher Traumtext, unverändert
    llm_traumtext           TEXT,

    -- was der Integrator als Spur ableitet (aus LLM-Output destilliert)
    integrator_spur         TEXT,

    -- Entscheidungsstatus des Integrators
    -- 'offen'          = noch nicht entschieden
    -- 'angenommen'     = wird ins Selbstmodell übernommen
    -- 'abgelehnt'      = wird nicht übernommen
    -- 'zurueckgestellt'= noch nicht entschieden, später nochmal prüfen
    integrator_status  TEXT NOT NULL DEFAULT 'offen'
        CHECK (integrator_status IN ('offen', 'angenommen', 'abgelehnt', 'zurueckgestellt')),

    -- Begründung der Integrator-Entscheidung
    integrator_begruendung  TEXT,

    -- optionaler Gewichtungsvorschlag von Neuroevolution (später)
    gewichtungsvorschlag    JSONB,

    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ON traumspuren (entity_id, integrator_status);
CREATE INDEX ON traumspuren (traumkandidaten_log_id);
```

**Geändert gegenüber v1:** `ins_selbstmodell BOOLEAN` entfällt. Stattdessen `integrator_status` — weil Träume selten binär sind. `angenommen` impliziert Übernahme ins Selbstmodell.

---

## Tabelle 3: `entity_selfmodel_entries`

Die einzige Wahrheitsquelle über den inneren Zustand eines Wesens. Append-only, nie überschreiben.

```sql
CREATE TABLE entity_selfmodel_entries (
    id           BIGSERIAL PRIMARY KEY,
    entity_id    TEXT NOT NULL REFERENCES entities(id),

    -- Woher kommt dieser Eintrag?
    quelle  TEXT NOT NULL
        CHECK (quelle IN ('traum', 'flarum_vorphase', 'einzug', 'manuell')),
    -- Neue Quellen nur bewusst per Migration hinzufügen.

    -- bei quelle='traum': welche Traumspur hat diesen Eintrag erzeugt
    traumspur_id  BIGINT REFERENCES traumspuren(id),

    -- der eigentliche Inhalt
    inhalt  TEXT NOT NULL,

    -- Flarum-Seed-Einträge explizit markiert — keine heimliche Gegenwart
    ist_vorgeschichte  BOOLEAN NOT NULL DEFAULT FALSE,

    -- Metadaten: Zustand zum Zeitpunkt des Eintrags
    kontext  JSONB,

    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ON entity_selfmodel_entries (entity_id, created_at);
CREATE INDEX ON entity_selfmodel_entries (quelle, ist_vorgeschichte);
CREATE INDEX ON entity_selfmodel_entries (traumspur_id);
```

**`entities.meta` ist nicht Wahrheit.**
Ein separater Projection-Job baut `entities.meta` aus `entity_selfmodel_entries` auf.
Der Integrator schreibt ausschließlich hier.
Cache ist jederzeit aus dieser Tabelle rekonstruierbar.

---

## Verbindungsübersicht

```
events
  ↓ (regelbasierte Vorauswahl nach event_type, entity_id, Zeitfenster)
traumkandidaten_log          ← Run/Kopf
traumkandidaten_events       ← jedes Event mit status='betrachtet'|'ausgewaehlt'
  ↓ (LLM verdichtet die 'ausgewaehlt'-Events zu Traumtext)
traumspuren                  ← llm_traumtext + integrator_spur + integrator_status
  ↓ (integrator_status='angenommen')
entity_selfmodel_entries     ← append-only Wahrheit
  ↓ (Projection-Job)
entities.meta                ← Cache, nie Wahrheit
```

Flarum-Seed:
```
Flarum-Archiv
  ↓ (bewusster Import beim Einzug, quelle='flarum_vorphase', ist_vorgeschichte=true)
entity_selfmodel_entries
```

---

## Was noch offen ist (F2, F4, F5)

Diese drei Fragen können beim Bauen entstehen — sie blockieren das Schema nicht:

**F2: Wann ist ein Wesen bereit für Traumverarbeitung?**
Mindestschlafzeit? Mindestanzahl Wachereignisse? Noch offen.

**F4: Wie viele Traumspuren pro Schlafzyklus?**
Eine pro Schlafphase als Start? Noch offen.

**F5: Wann fließt eine angenommene Spur ins Selbstmodell?**
Direkt beim Setzen von `integrator_status='angenommen'`? Beim Aufwachen? Noch offen.

---

## Nächster Schritt

Schema als Migration schreiben. Reihenfolge:
1. `traumkandidaten_log`
2. `traumkandidaten_events`
3. `traumspuren`
4. `entity_selfmodel_entries`
5. Projection-Job für `entities.meta` (separates Skript, kein Trigger)
