-- Resonanz-System: Emojis, Schattenkommentare, Verweilen, Wesen-Gedanken

CREATE TABLE IF NOT EXISTS resonanzen (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    post_ref    VARCHAR NOT NULL,
    post_source VARCHAR NOT NULL DEFAULT 'flarum',
    user_id     UUID NOT NULL REFERENCES human_users(id) ON DELETE CASCADE,
    emojis      JSONB NOT NULL,
    sent_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meta        JSONB NOT NULL DEFAULT '{}',
    UNIQUE (post_ref, post_source, user_id)
);

CREATE INDEX IF NOT EXISTS idx_resonanzen_post ON resonanzen (post_ref, post_source);
CREATE INDEX IF NOT EXISTS idx_resonanzen_user ON resonanzen (user_id);

CREATE TABLE IF NOT EXISTS resonanz_emoji_counts (
    post_ref    VARCHAR NOT NULL,
    post_source VARCHAR NOT NULL,
    emoji       VARCHAR(10) NOT NULL,
    count       INTEGER NOT NULL DEFAULT 0,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (post_ref, post_source, emoji)
);

CREATE TABLE IF NOT EXISTS schattenkommentare (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    post_ref    VARCHAR NOT NULL,
    post_source VARCHAR NOT NULL DEFAULT 'flarum',
    author_id   UUID REFERENCES human_users(id) ON DELETE SET NULL,
    author_type VARCHAR NOT NULL DEFAULT 'human',
    content     TEXT NOT NULL,
    visible_to  JSONB NOT NULL DEFAULT '["admin"]',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meta        JSONB NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_schattenkommentare_post   ON schattenkommentare (post_ref, post_source);
CREATE INDEX IF NOT EXISTS idx_schattenkommentare_author ON schattenkommentare (author_id);

CREATE TABLE IF NOT EXISTS verweilen (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id             UUID NOT NULL REFERENCES human_users(id) ON DELETE CASCADE,
    target_type         VARCHAR NOT NULL,
    target_id           VARCHAR NOT NULL,
    started_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at            TIMESTAMPTZ,
    duration_seconds    INTEGER,
    interaction_signals JSONB NOT NULL DEFAULT '[]',
    is_valid            BOOLEAN NOT NULL DEFAULT false,
    meta                JSONB NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_verweilen_user   ON verweilen (user_id);
CREATE INDEX IF NOT EXISTS idx_verweilen_target ON verweilen (target_type, target_id);

CREATE TABLE IF NOT EXISTS wesen_gedanken (
    id                      UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    post_ref                VARCHAR NOT NULL,
    post_source             VARCHAR NOT NULL DEFAULT 'flarum',
    entity_id               VARCHAR NOT NULL,
    stimmung_bei_erstellung VARCHAR,
    fokus_bei_erstellung    TEXT,
    selbstmodell_snapshot   JSONB,
    access_level            VARCHAR NOT NULL DEFAULT 'unlocked',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meta                    JSONB NOT NULL DEFAULT '{}',
    UNIQUE (post_ref, post_source, entity_id)
);

CREATE INDEX IF NOT EXISTS idx_wesen_gedanken_entity ON wesen_gedanken (entity_id);
CREATE INDEX IF NOT EXISTS idx_wesen_gedanken_post   ON wesen_gedanken (post_ref, post_source);
