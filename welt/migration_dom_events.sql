-- rrweb-Live-Spiegel (2026-07-21, Daniels "Menschen-Auge-Ebene" aus Grundgesetz 1 /
-- dreiergespann_dom_theorie.md, konkretisiert in DOM-FLEXTRAWUST/*.md): DOM-Mutations-
-- Events statt Screenshots, live rekonstruiert im Browser des Zuschauers.
--
-- Gleiches Cross-Prozess-Muster wie migration_denkstream.sql (browser_agent.py und
-- welt-api.py sind getrennte Prozesse, NOTIFY ist die Bruecke) -- ABER bewusst OHNE
-- den Event-Inhalt im NOTIFY-Payload: rrweb-FullSnapshot-Events (beim Start jeder
-- Aufnahme) koennen den 8000-Byte-Payload-Limit von PostgreSQL NOTIFY leicht
-- ueberschreiten, anders als die kurzen Text-Chunks bei entity_denkstream. Der
-- SSE-Endpunkt bekommt nur id+entity_id zugerufen und holt sich den eigentlichen
-- Event-Inhalt per SELECT.

CREATE TABLE IF NOT EXISTS entity_dom_events (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    entity_id   VARCHAR REFERENCES entity_slots(entity_id),
    stream_id   UUID DEFAULT gen_random_uuid(),
    event_json  JSONB NOT NULL,
    seq         INTEGER DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dom_events_entity_at
    ON entity_dom_events(entity_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_dom_events_stream
    ON entity_dom_events(stream_id, seq);

CREATE OR REPLACE FUNCTION notify_dom_events() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify(
        'entity_dom_events',
        json_build_object('id', NEW.id, 'entity_id', NEW.entity_id)::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_notify_dom_events ON entity_dom_events;
CREATE TRIGGER trg_notify_dom_events
    AFTER INSERT ON entity_dom_events
    FOR EACH ROW EXECUTE FUNCTION notify_dom_events();
