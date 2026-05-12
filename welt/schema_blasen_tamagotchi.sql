-- Gedankenblasenfeld + Tamagotchi-Kern
-- Anwenden: psql -h localhost -U dak -d flextrawurst -f schema_blasen_tamagotchi.sql

-- ── Gedankenblasen ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gedankenblasen (
    id               UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id          UUID REFERENCES human_users(id) ON DELETE SET NULL,
    inhalt           TEXT NOT NULL CHECK (length(inhalt) <= 280),
    sichtbarkeit     VARCHAR DEFAULT 'public',
    herkunft_sichtbar BOOLEAN DEFAULT true,
    thematische_tags JSONB DEFAULT '[]',
    energie          FLOAT DEFAULT 1.0,
    pos_x            FLOAT DEFAULT 0,
    pos_y            FLOAT DEFAULT 0,
    wesen_verwendungen INTEGER DEFAULT 0,
    status           VARCHAR DEFAULT 'aktiv',
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW(),
    meta             JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS blase_verwendungen (
    id               UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    blase_id         UUID REFERENCES gedankenblasen(id) ON DELETE CASCADE,
    entity_id        VARCHAR NOT NULL,
    verwendungs_typ  VARCHAR,
    post_ref         VARCHAR,
    anonym           BOOLEAN DEFAULT true,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

-- ── Tamagotchi ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS wesen_fuersorge (
    id               UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id          UUID REFERENCES human_users(id) ON DELETE CASCADE,
    entity_id        VARCHAR NOT NULL,
    fuersorge_typ    VARCHAR NOT NULL,
    punkte           FLOAT DEFAULT 1.0,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    meta             JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS wesen_entwicklung (
    entity_id              VARCHAR PRIMARY KEY,
    fuersorge_gesamt       FLOAT DEFAULT 0.0,
    fuersorge_heute        FLOAT DEFAULT 0.0,
    vernachlaessigung_stunden INTEGER DEFAULT 0,
    letzte_interaktion     TIMESTAMPTZ,
    entwicklungsstufe      INTEGER DEFAULT 1,
    stufe_punkte_schwelle  FLOAT DEFAULT 100.0,
    stimmungs_drift        FLOAT DEFAULT 0.0,
    meta                   JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS nutzer_sichtbarkeit (
    user_id                    UUID PRIMARY KEY REFERENCES human_users(id) ON DELETE CASCADE,
    gedankenblasen_anonym      BOOLEAN DEFAULT false,
    notizen_anonym             BOOLEAN DEFAULT true,
    schattenkommentare_anonym  BOOLEAN DEFAULT true,
    zitierbar                  BOOLEAN DEFAULT true,
    verweilen_tracking         BOOLEAN DEFAULT true,
    meta                       JSONB DEFAULT '{}'
);

-- ── Indizes ───────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_gedankenblasen_tags     ON gedankenblasen USING gin(thematische_tags);
CREATE INDEX IF NOT EXISTS idx_gedankenblasen_status   ON gedankenblasen (status, created_at DESC, energie DESC);
CREATE INDEX IF NOT EXISTS idx_fuersorge_entity        ON wesen_fuersorge (entity_id);
CREATE INDEX IF NOT EXISTS idx_fuersorge_user          ON wesen_fuersorge (user_id);
CREATE INDEX IF NOT EXISTS idx_fuersorge_created       ON wesen_fuersorge (created_at DESC);
