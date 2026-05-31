-- Migration: Selbstorganisierendes Post-System + Schattenkommentare

-- 1. themen: rekursiv + tsvector
ALTER TABLE themen ADD COLUMN IF NOT EXISTS parent_id UUID REFERENCES themen(id) ON DELETE SET NULL;
ALTER TABLE themen ADD COLUMN IF NOT EXISTS tiefe INTEGER DEFAULT 0;
ALTER TABLE themen ADD COLUMN IF NOT EXISTS auto_erstellt BOOLEAN DEFAULT false;
ALTER TABLE themen ADD COLUMN IF NOT EXISTS tsv TSVECTOR;
ALTER TABLE themen ALTER COLUMN raum_id DROP NOT NULL;
DROP INDEX IF EXISTS themen_raum_id_slug_key;
ALTER TABLE themen DROP CONSTRAINT IF EXISTS themen_raum_id_slug_key;
CREATE UNIQUE INDEX IF NOT EXISTS idx_themen_parent_slug ON themen (COALESCE(parent_id::text, raum_id::text), slug);
CREATE INDEX IF NOT EXISTS idx_themen_parent ON themen (parent_id);
CREATE INDEX IF NOT EXISTS idx_themen_tsv ON themen USING GIN (tsv);

-- tsv aktuell halten
UPDATE themen SET tsv = to_tsvector('german', COALESCE(name,'') || ' ' || COALESCE(beschreibung,''));
CREATE OR REPLACE FUNCTION themen_tsv_update() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN NEW.tsv := to_tsvector('german', COALESCE(NEW.name,'') || ' ' || COALESCE(NEW.beschreibung,'')); RETURN NEW; END $$;
DROP TRIGGER IF EXISTS trg_themen_tsv ON themen;
CREATE TRIGGER trg_themen_tsv BEFORE INSERT OR UPDATE ON themen FOR EACH ROW EXECUTE FUNCTION themen_tsv_update();

-- 2. ftw_posts: gedankenfluss, unterthema_id weg, tsvector
ALTER TABLE ftw_posts ADD COLUMN IF NOT EXISTS gedankenfluss TEXT;
ALTER TABLE ftw_posts ADD COLUMN IF NOT EXISTS tsv TSVECTOR;
ALTER TABLE ftw_posts DROP COLUMN IF EXISTS unterthema_id;
CREATE INDEX IF NOT EXISTS idx_ftw_posts_tsv ON ftw_posts USING GIN (tsv);
CREATE INDEX IF NOT EXISTS idx_ftw_posts_thema ON ftw_posts (thema_id);

UPDATE ftw_posts SET tsv = to_tsvector('german', COALESCE(content,''));
CREATE OR REPLACE FUNCTION ftw_posts_tsv_update() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN NEW.tsv := to_tsvector('german', COALESCE(NEW.content,'')); RETURN NEW; END $$;
DROP TRIGGER IF EXISTS trg_ftw_posts_tsv ON ftw_posts;
CREATE TRIGGER trg_ftw_posts_tsv BEFORE INSERT OR UPDATE ON ftw_posts FOR EACH ROW EXECUTE FUNCTION ftw_posts_tsv_update();

-- 3. Ähnlichkeits-Tabellen
CREATE TABLE IF NOT EXISTS post_similarity (
    post_a_id   UUID REFERENCES ftw_posts(id) ON DELETE CASCADE,
    post_b_id   UUID REFERENCES ftw_posts(id) ON DELETE CASCADE,
    score       FLOAT NOT NULL,
    updated_at  TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (post_a_id, post_b_id),
    CHECK (post_a_id < post_b_id)
);
CREATE INDEX IF NOT EXISTS idx_post_sim_a ON post_similarity (post_a_id, score DESC);
CREATE INDEX IF NOT EXISTS idx_post_sim_b ON post_similarity (post_b_id, score DESC);

CREATE TABLE IF NOT EXISTS thema_similarity (
    thema_a_id  UUID REFERENCES themen(id) ON DELETE CASCADE,
    thema_b_id  UUID REFERENCES themen(id) ON DELETE CASCADE,
    score       FLOAT NOT NULL,
    updated_at  TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (thema_a_id, thema_b_id),
    CHECK (thema_a_id < thema_b_id)
);

-- 4. Cluster-Vorschläge (Admin-Panel)
CREATE TABLE IF NOT EXISTS thema_cluster_vorschlaege (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    thema_ids       JSONB NOT NULL,
    vorgeschlagener_name VARCHAR(200),
    score           FLOAT NOT NULL,
    status          VARCHAR DEFAULT 'offen',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    meta            JSONB DEFAULT '{}'
);

-- 5. Schattenkommentare
CREATE TABLE IF NOT EXISTS schattenkommentare (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    post_id     UUID NOT NULL REFERENCES ftw_posts(id) ON DELETE CASCADE,
    human_id    UUID NOT NULL REFERENCES human_users(id) ON DELETE CASCADE,
    content     TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW(),
    meta        JSONB DEFAULT '{}',
    UNIQUE (post_id, human_id)
);
CREATE INDEX IF NOT EXISTS idx_schatten_post ON schattenkommentare (post_id);
CREATE INDEX IF NOT EXISTS idx_schatten_human ON schattenkommentare (human_id);

CREATE TABLE IF NOT EXISTS schatten_antworten (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    schatten_id UUID NOT NULL REFERENCES schattenkommentare(id) ON DELETE CASCADE,
    autor_type  VARCHAR NOT NULL,
    autor_id    VARCHAR NOT NULL,
    content     TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    meta        JSONB DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_schatten_antworten_schatten ON schatten_antworten (schatten_id, created_at);

-- 6. unterthemen: leer, kann weg (nach Prüfung)
-- DROP TABLE IF EXISTS unterthemen; -- erst wenn API migriert
