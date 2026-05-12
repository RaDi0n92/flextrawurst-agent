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
