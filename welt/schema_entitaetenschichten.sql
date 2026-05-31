-- Entitätenschichten: Profil, Aktivität, Denklog, Beziehungen

-- Statisches Profil einer Entität (halb-automatisch, halb vom Wesen selbst)
CREATE TABLE IF NOT EXISTS entity_profiles (
    entity_id           VARCHAR PRIMARY KEY REFERENCES entity_slots(entity_id),
    selbstbeschreibung  TEXT,
    obsessionen         TEXT[] DEFAULT '{}',
    abneigungen         TEXT[] DEFAULT '{}',
    name_gewaehlt       BOOLEAN DEFAULT false,
    name_ereignis_text  TEXT,
    name_ereignis_at    TIMESTAMPTZ,
    autonomie_phase     VARCHAR DEFAULT 'bound'
                            CHECK (autonomie_phase IN ('bound', 'semi_autonomous', 'autonomous')),
    meta                JSONB DEFAULT '{}'
);

-- Aktuelle Aktivität — was das Wesen grade tut (Daemon-Vortext + Wesen-Präzisierung)
CREATE TABLE IF NOT EXISTS entity_activity (
    entity_id               VARCHAR PRIMARY KEY REFERENCES entity_slots(entity_id),
    daemon_vortext          VARCHAR,
    wesen_praezisierung     TEXT,
    aktuell_denkend         BOOLEAN DEFAULT false,
    letzter_gedanke         TEXT,
    letzte_entscheidung     VARCHAR,
    letzte_begruendung      TEXT,
    letzte_entscheidung_at  TIMESTAMPTZ,
    denkstrom_buffer        TEXT DEFAULT '',
    updated_at              TIMESTAMPTZ DEFAULT NOW(),
    meta                    JSONB DEFAULT '{}'
);

-- Pro-Tick Denklog — vollständiger LLM-Output + extrahierte Entscheidung
CREATE TABLE IF NOT EXISTS entity_thinking_log (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    entity_id           VARCHAR REFERENCES entity_slots(entity_id),
    tick_at             TIMESTAMPTZ DEFAULT NOW(),
    kontext_snapshot    JSONB DEFAULT '{}',
    raw_output          TEXT,
    gedanke             TEXT,
    entscheidung        VARCHAR,
    begruendung         TEXT,
    tokens_generated    INTEGER DEFAULT 0,
    duration_ms         INTEGER DEFAULT 0,
    meta                JSONB DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_thinking_log_entity_at
    ON entity_thinking_log(entity_id, tick_at DESC);

-- Beziehungsschicht — Entität↔Entität und Entität↔Mensch
CREATE TABLE IF NOT EXISTS entity_relationships (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    entity_id           VARCHAR REFERENCES entity_slots(entity_id),
    partner_type        VARCHAR NOT NULL CHECK (partner_type IN ('entity', 'human')),
    partner_id          VARCHAR NOT NULL,
    interaktionen       INTEGER DEFAULT 0,
    resonanz_score      FLOAT DEFAULT 0.0,
    letzte_interaktion  TIMESTAMPTZ,
    meta                JSONB DEFAULT '{}'
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_entity_relationships_unique
    ON entity_relationships(entity_id, partner_type, partner_id);

-- Splitter-Stats View: wie viele Splitter abgegeben / aufgesammelt
CREATE OR REPLACE VIEW entity_splitter_stats AS
SELECT
    e.entity_id,
    COALESCE(abgegeben.anzahl, 0) AS splitter_abgegeben,
    COALESCE(aufgesammelt.anzahl, 0) AS splitter_aufgesammelt
FROM entity_slots e
LEFT JOIN (
    SELECT actor_id AS entity_id, COUNT(*) AS anzahl
    FROM events
    WHERE event_type = 'splitter.abgegeben'
    GROUP BY actor_id
) abgegeben ON abgegeben.entity_id = e.entity_id
LEFT JOIN (
    SELECT actor_id AS entity_id, COUNT(*) AS anzahl
    FROM events
    WHERE event_type = 'splitter.aufgesammelt'
    GROUP BY actor_id
) aufgesammelt ON aufgesammelt.entity_id = e.entity_id;
