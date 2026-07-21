-- Roentgenblick-Overlay (2026-07-21, Daniels bestaetigter Bauauftrag nach rrweb
-- Aufnahme+Wiedergabe): welches Element betrachtet/anfasst ein Wesen gerade.
--
-- entity_dom_events (migration_dom_events.sql) ist reiner passiver rrweb-Rohstrom
-- (fast nur Mutation-Events) -- daraus laesst sich kein "Wesen klickt X" ableiten.
-- entity_fokus_events ist der kuratierte Gegenpart: browser_agent.py schreibt hier
-- direkt an der Stelle, wo ein Playwright-Locator vor der Aktion aufgeloest wird
-- (_klicke_und_zeige in fuehre_aktion_aus), mit Selektor/Text/Bounding-Box.
--
-- Payload ist klein genug (Selektor + Text + 4 Zahlen), um komplett im NOTIFY
-- mitzuschicken -- anders als bei entity_dom_events kein zusaetzlicher SELECT noetig.

CREATE TABLE IF NOT EXISTS entity_fokus_events (
    id           UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    entity_id    VARCHAR REFERENCES entity_slots(entity_id),
    aktion       VARCHAR NOT NULL,
    selektor     TEXT,
    element_text TEXT,
    box          JSONB,
    meta         JSONB DEFAULT '{}',
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fokus_events_entity_at
    ON entity_fokus_events(entity_id, created_at DESC);

CREATE OR REPLACE FUNCTION notify_fokus_events() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify(
        'entity_fokus_events',
        json_build_object(
            'entity_id',    NEW.entity_id,
            'aktion',       NEW.aktion,
            'selektor',     NEW.selektor,
            'element_text', NEW.element_text,
            'box',          NEW.box
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_notify_fokus_events ON entity_fokus_events;
CREATE TRIGGER trg_notify_fokus_events
    AFTER INSERT ON entity_fokus_events
    FOR EACH ROW EXECUTE FUNCTION notify_fokus_events();
