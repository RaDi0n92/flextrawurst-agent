-- Menschenprofil-System: Kern + Module
-- Bestehende Tabellen (users, entity_slots, etc.) werden nicht berührt.

CREATE TABLE IF NOT EXISTS human_users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username      VARCHAR(50) UNIQUE NOT NULL,
    display_name  VARCHAR(100),
    role          VARCHAR(20) NOT NULL DEFAULT 'mensch',
    password_hash VARCHAR NOT NULL,
    is_active     BOOLEAN NOT NULL DEFAULT true,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen     TIMESTAMPTZ,
    meta          JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS human_profiles (
    user_id        UUID PRIMARY KEY REFERENCES human_users(id) ON DELETE CASCADE,
    bio            TEXT,
    gedankenwelt   TEXT,
    public_tags    JSONB NOT NULL DEFAULT '[]',
    avatar_symbol  VARCHAR(50),
    visibility     VARCHAR(20) NOT NULL DEFAULT 'public',
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meta           JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS user_modules (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES human_users(id) ON DELETE CASCADE,
    module_name  VARCHAR(50) NOT NULL,
    enabled      BOOLEAN NOT NULL DEFAULT true,
    config       JSONB NOT NULL DEFAULT '{}',
    activated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, module_name)
);

GRANT ALL ON human_users, human_profiles, user_modules TO dak;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dak;
