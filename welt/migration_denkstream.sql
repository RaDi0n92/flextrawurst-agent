-- Denkstream: Live-Chunks während LLM-Generierung
-- Jeder Chunk kommt als PostgreSQL NOTIFY rein → SSE weiterleiten

CREATE TABLE IF NOT EXISTS entity_denkstream (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    entity_id   VARCHAR REFERENCES entity_slots(entity_id),
    stream_id   UUID DEFAULT gen_random_uuid(),
    chunk       TEXT NOT NULL,
    seq         INTEGER DEFAULT 0,
    done        BOOLEAN DEFAULT false,
    url         TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_denkstream_entity_at
    ON entity_denkstream(entity_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_denkstream_stream
    ON entity_denkstream(stream_id, seq);

-- Trigger: bei jedem INSERT NOTIFY senden
CREATE OR REPLACE FUNCTION notify_denkstream() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify(
        'entity_denkstream',
        json_build_object(
            'entity_id', NEW.entity_id,
            'stream_id', NEW.stream_id,
            'chunk',     NEW.chunk,
            'seq',       NEW.seq,
            'done',      NEW.done,
            'url',       NEW.url
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_notify_denkstream ON entity_denkstream;
CREATE TRIGGER trg_notify_denkstream
    AFTER INSERT ON entity_denkstream
    FOR EACH ROW EXECUTE FUNCTION notify_denkstream();

-- Screenshot-Tabelle: aktueller Screenshot pro Wesen
CREATE TABLE IF NOT EXISTS entity_screenshots (
    entity_id   VARCHAR PRIMARY KEY REFERENCES entity_slots(entity_id),
    screenshot  BYTEA,
    url         TEXT,
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);
