-- Traum-/Selbstmodell-Schema v0.1
-- Alle Tabellen append-only. Kein UPDATE, kein DELETE.

-- 1. Run/Kopf: eine Selektions-Ausführung pro Schlafphase
CREATE TABLE IF NOT EXISTS traumkandidaten_log (
    log_id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    entity_id       VARCHAR NOT NULL REFERENCES entity_slots(entity_id),
    sleep_phase_id  UUID REFERENCES sleep_phases(phase_id),
    selektionsregel VARCHAR NOT NULL,
    begruendung     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_traumkandidaten_log_entity
    ON traumkandidaten_log (entity_id, created_at DESC);

-- 2. Detail: jedes betrachtete/ausgewählte Event einzeln
CREATE TABLE IF NOT EXISTS traumkandidaten_events (
    id      BIGSERIAL PRIMARY KEY,
    log_id  UUID NOT NULL REFERENCES traumkandidaten_log(log_id),
    event_id UUID NOT NULL REFERENCES events(event_id),
    status  VARCHAR NOT NULL CHECK (status IN ('betrachtet', 'ausgewaehlt')),
    begruendung TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_traumkandidaten_events_log
    ON traumkandidaten_events (log_id);

CREATE INDEX IF NOT EXISTS idx_traumkandidaten_events_event
    ON traumkandidaten_events (event_id);

-- 3. Traumspuren: LLM-Output + Integrator-Entscheidung
CREATE TABLE IF NOT EXISTS traumspuren (
    spur_id                 UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    entity_id               VARCHAR NOT NULL REFERENCES entity_slots(entity_id),
    log_id                  UUID REFERENCES traumkandidaten_log(log_id),
    llm_traumtext           TEXT,
    integrator_spur         TEXT,
    integrator_status       VARCHAR NOT NULL DEFAULT 'offen'
        CHECK (integrator_status IN ('offen', 'angenommen', 'abgelehnt', 'zurueckgestellt')),
    integrator_begruendung  TEXT,
    gewichtungsvorschlag    JSONB,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_traumspuren_entity_status
    ON traumspuren (entity_id, integrator_status);

CREATE INDEX IF NOT EXISTS idx_traumspuren_log
    ON traumspuren (log_id);

-- 4. Selbstmodell: append-only Wahrheit. entities.meta ist nur Cache.
CREATE TABLE IF NOT EXISTS entity_selfmodel_entries (
    entry_id    UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    entity_id   VARCHAR NOT NULL REFERENCES entity_slots(entity_id),
    quelle      VARCHAR NOT NULL
        CHECK (quelle IN ('traum', 'flarum_vorphase', 'einzug', 'manuell')),
    spur_id     UUID REFERENCES traumspuren(spur_id),
    inhalt      TEXT NOT NULL,
    ist_vorgeschichte BOOLEAN NOT NULL DEFAULT FALSE,
    kontext     JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_selfmodel_entity
    ON entity_selfmodel_entries (entity_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_selfmodel_quelle
    ON entity_selfmodel_entries (quelle, ist_vorgeschichte);

CREATE INDEX IF NOT EXISTS idx_selfmodel_spur
    ON entity_selfmodel_entries (spur_id);
