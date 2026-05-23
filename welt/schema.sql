-- Welt-Schema: Entitäts-Slots, Zustände und Events

CREATE TABLE IF NOT EXISTS entity_slots (
    entity_id       VARCHAR PRIMARY KEY,
    display_name    VARCHAR,
    status          VARCHAR DEFAULT 'bereit'
                        CHECK (status IN ('bereit', 'eingezogen', 'schläft')),
    visibility      VARCHAR DEFAULT 'internal'
                        CHECK (visibility IN ('internal', 'public')),
    slot_created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS entity_states (
    entity_id              VARCHAR PRIMARY KEY
                               REFERENCES entity_slots(entity_id),
    stimmung               VARCHAR,
    fokus                  TEXT,
    version                INTEGER,
    core                   JSONB DEFAULT '{}',
    tendencies             JSONB DEFAULT '{}',
    relationships          JSONB DEFAULT '{}',
    symbolic_image_id      VARCHAR,
    last_reflection_time   TIMESTAMPTZ,
    raw_model              JSONB,
    visibility             VARCHAR DEFAULT 'internal',
    updated_at             TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS events (
    event_id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    event_type       VARCHAR NOT NULL,
    actor_type       VARCHAR NOT NULL,
    actor_id         VARCHAR,
    payload          JSONB DEFAULT '{}',
    origin_type      VARCHAR DEFAULT 'live_world',
    visibility_layer VARCHAR DEFAULT 'internal',
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_created_at
    ON events (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_events_actor_id
    ON events (actor_id);

CREATE INDEX IF NOT EXISTS idx_events_event_type
    ON events (event_type);

-- Schlaf-System

CREATE TABLE IF NOT EXISTS sleep_phases (
    phase_id        UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    entity_id       VARCHAR NOT NULL REFERENCES entity_slots(entity_id),
    phase_type      VARCHAR NOT NULL
                        CHECK (phase_type IN ('kurz', 'hauptschlaf')),
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at        TIMESTAMPTZ,
    duration_min    INTEGER GENERATED ALWAYS AS (
                        EXTRACT(EPOCH FROM (ended_at - started_at)) / 60
                    ) STORED
);

CREATE INDEX IF NOT EXISTS idx_sleep_phases_entity
    ON sleep_phases (entity_id, started_at DESC);

-- Cyberlinge (individuelle Pflegewesen pro Entität)

CREATE TABLE IF NOT EXISTS cyberlinge (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    entity_id       VARCHAR NOT NULL UNIQUE REFERENCES entity_slots(entity_id),
    name            VARCHAR,
    geboren_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tode            INTEGER NOT NULL DEFAULT 0,
    zuletzt_belebt  TIMESTAMPTZ,
    status          VARCHAR NOT NULL DEFAULT 'lebendig'
                        CHECK (status IN ('lebendig', 'tot', 'schlafend')),
    hunger          FLOAT NOT NULL DEFAULT 1.0 CHECK (hunger BETWEEN 0 AND 1),
    gesundheit      FLOAT NOT NULL DEFAULT 1.0 CHECK (gesundheit BETWEEN 0 AND 1),
    stimmung        FLOAT NOT NULL DEFAULT 1.0 CHECK (stimmung BETWEEN 0 AND 1),
    energie         FLOAT NOT NULL DEFAULT 1.0 CHECK (energie BETWEEN 0 AND 1),
    letztes_fuettern    TIMESTAMPTZ,
    letzte_pflege       TIMESTAMPTZ,
    letzte_interaktion  TIMESTAMPTZ DEFAULT NOW(),
    meta            JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_cyberlinge_entity ON cyberlinge (entity_id);

CREATE TABLE IF NOT EXISTS schlafbriefe (
    brief_id        UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    entity_id       VARCHAR NOT NULL REFERENCES entity_slots(entity_id),
    phase_id        UUID REFERENCES sleep_phases(phase_id),
    inhalt          TEXT NOT NULL,
    geschrieben_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
