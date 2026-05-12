-- Welt-Struktur: Räume → Themen → Unterthemen → Posts + Splitter-Physik

CREATE TABLE IF NOT EXISTS raeume (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    beschreibung    TEXT,
    slug            VARCHAR(100) UNIQUE NOT NULL,
    farbe           VARCHAR(20),
    status          VARCHAR DEFAULT 'aktiv',
    sichtbarkeit    VARCHAR DEFAULT 'public',
    position_order  INTEGER DEFAULT 0,
    erstellt_von    VARCHAR DEFAULT 'system',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    meta            JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS themen (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    raum_id             UUID REFERENCES raeume(id) ON DELETE CASCADE,
    name                VARCHAR(200) NOT NULL,
    beschreibung        TEXT,
    slug                VARCHAR(200) NOT NULL,
    status              VARCHAR DEFAULT 'aktiv',
    inkubations_grund   TEXT,
    resonanz_gewicht    FLOAT DEFAULT 0.0,
    sichtbarkeit        VARCHAR DEFAULT 'public',
    erstellt_von        VARCHAR DEFAULT 'system',
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    meta                JSONB DEFAULT '{}',
    UNIQUE(raum_id, slug)
);

CREATE TABLE IF NOT EXISTS unterthemen (
    id           UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    thema_id     UUID REFERENCES themen(id) ON DELETE CASCADE,
    name         VARCHAR(200) NOT NULL,
    slug         VARCHAR(200) NOT NULL,
    status       VARCHAR DEFAULT 'aktiv',
    sichtbarkeit VARCHAR DEFAULT 'public',
    erstellt_von VARCHAR DEFAULT 'system',
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    meta         JSONB DEFAULT '{}',
    UNIQUE(thema_id, slug)
);

CREATE TABLE IF NOT EXISTS ftw_posts (
    id                      UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    unterthema_id           UUID REFERENCES unterthemen(id) ON DELETE SET NULL,
    thema_id                UUID REFERENCES themen(id) ON DELETE SET NULL,
    raum_id                 UUID REFERENCES raeume(id) ON DELETE SET NULL,
    autor_type              VARCHAR NOT NULL,
    autor_id                VARCHAR NOT NULL,
    content                 TEXT NOT NULL,
    post_type               VARCHAR DEFAULT 'diskurs',
    sichtbarkeit            VARCHAR DEFAULT 'public',
    stimmung_bei_erstellung VARCHAR,
    fokus_bei_erstellung    TEXT,
    selbstmodell_snapshot   JSONB,
    splitter_erzeugt        BOOLEAN DEFAULT false,
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW(),
    meta                    JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_ftw_posts_autor    ON ftw_posts (autor_id);
CREATE INDEX IF NOT EXISTS idx_ftw_posts_raum     ON ftw_posts (raum_id);
CREATE INDEX IF NOT EXISTS idx_ftw_posts_created  ON ftw_posts (created_at DESC);

CREATE TABLE IF NOT EXISTS splitter (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    origin_type         VARCHAR NOT NULL,
    origin_id           VARCHAR,
    entity_id           VARCHAR,
    human_id            UUID REFERENCES human_users(id) ON DELETE SET NULL,
    herkunft_sichtbar   BOOLEAN DEFAULT true,
    essenz              TEXT,
    thematische_tags    JSONB DEFAULT '[]',
    materialitaet       VARCHAR DEFAULT 'sternenstaub',
    energie             FLOAT DEFAULT 1.0,
    verbindungen        INTEGER DEFAULT 0,
    abstossungen        INTEGER DEFAULT 0,
    pos_x               FLOAT DEFAULT 0,
    pos_y               FLOAT DEFAULT 0,
    vel_x               FLOAT DEFAULT 0,
    vel_y               FLOAT DEFAULT 0,
    status              VARCHAR DEFAULT 'aktiv',
    letzter_kontakt     TIMESTAMPTZ DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    meta                JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_splitter_status       ON splitter (status);
CREATE INDEX IF NOT EXISTS idx_splitter_entity_id    ON splitter (entity_id);
CREATE INDEX IF NOT EXISTS idx_splitter_materialitaet ON splitter (materialitaet);
CREATE INDEX IF NOT EXISTS idx_splitter_energie      ON splitter (energie DESC);
CREATE INDEX IF NOT EXISTS idx_splitter_tags         ON splitter USING GIN (thematische_tags);

CREATE TABLE IF NOT EXISTS splitter_verbindungen (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    splitter_a_id   UUID REFERENCES splitter(id) ON DELETE CASCADE,
    splitter_b_id   UUID REFERENCES splitter(id) ON DELETE CASCADE,
    verbindungstyp  VARCHAR DEFAULT 'resonanz',
    staerke         FLOAT DEFAULT 1.0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    meta            JSONB DEFAULT '{}'
);
