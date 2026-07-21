-- Live-Update-Infrastruktur (2026-07-21, Daniels Grundgesetz "Live statt F5"):
-- jedes INSERT in die bereits heilige events-Tabelle (Grundgesetz 5) sendet ein
-- PostgreSQL NOTIFY -> SSE-Endpunkt /events/stream leitet weiter -> Frontend
-- entscheidet pro Event-Praefix, was neu geladen wird. Analog zum bestehenden
-- trg_notify_denkstream-Muster (migration_denkstream.sql).
--
-- Bewusst MINIMALES Payload im Broadcast: nur event_type, created_at und ein paar
-- kuratierte, unsensible Routing-Hinweise (ankuendigung_id, post_ref, post_source).
-- KEIN Kommentar-Text, keine Emoji-Reaktion, kein voller payload -- die eigentlichen
-- Daten holt sich das Frontend weiterhin ueber die normalen, auth-geprueften
-- REST-Endpunkte. Der Stream ist nur ein Signal "hier hat sich was getan",
-- niemals eine zweite, ungeschuetzte Datenquelle.

CREATE OR REPLACE FUNCTION notify_events() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify(
        'events_stream',
        json_build_object(
            'event_type',       NEW.event_type,
            'created_at',       NEW.created_at,
            'ankuendigung_id',  NEW.payload->>'ankuendigung_id',
            'post_ref',         NEW.payload->>'post_ref',
            'post_source',      NEW.payload->>'post_source'
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_notify_events ON events;
CREATE TRIGGER trg_notify_events
    AFTER INSERT ON events
    FOR EACH ROW EXECUTE FUNCTION notify_events();
