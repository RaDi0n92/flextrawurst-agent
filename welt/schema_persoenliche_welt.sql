-- Persönliche Welt: Tagebuch, Traumtagebuch, Notizen, Kalender, Bild-Moderation, Profil-Gestaltung

CREATE TABLE IF NOT EXISTS mw_tagebuch (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL REFERENCES human_users(id) ON DELETE CASCADE,
    inhalt           TEXT NOT NULL,
    zitierbar        BOOLEAN,              -- NULL = globale Präferenz aus human_profiles.meta nutzen
    splitter_erzeugt BOOLEAN NOT NULL DEFAULT false,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meta             JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS mw_traumtagebuch (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL REFERENCES human_users(id) ON DELETE CASCADE,
    inhalt           TEXT NOT NULL,
    traum_datum      DATE NOT NULL DEFAULT CURRENT_DATE,
    zitierbar        BOOLEAN,
    splitter_erzeugt BOOLEAN NOT NULL DEFAULT false,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meta             JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS mw_notizen (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL REFERENCES human_users(id) ON DELETE CASCADE,
    titel            VARCHAR(200),
    inhalt           TEXT NOT NULL,
    typ              VARCHAR(20) NOT NULL DEFAULT 'notiz',  -- 'notiz' | 'aufgabe'
    erledigt         BOOLEAN NOT NULL DEFAULT false,
    gepinnt          BOOLEAN NOT NULL DEFAULT false,
    zuletzt_offen    TIMESTAMPTZ,
    zitierbar        BOOLEAN,
    splitter_erzeugt BOOLEAN NOT NULL DEFAULT false,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meta             JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS mw_kalender (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES human_users(id) ON DELETE CASCADE,
    titel           VARCHAR(200) NOT NULL,
    beschreibung    TEXT,
    start_zeit      TIMESTAMPTZ NOT NULL,
    end_zeit        TIMESTAMPTZ,
    ganztaegig      BOOLEAN NOT NULL DEFAULT false,
    erinnerung      JSONB NOT NULL DEFAULT '[]',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meta            JSONB NOT NULL DEFAULT '{}'
);

-- Bild-Upload-Moderation (Avatar, Profil-Hintergrund)
CREATE TABLE IF NOT EXISTS bild_moderation (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL REFERENCES human_users(id) ON DELETE CASCADE,
    pfad             VARCHAR(500) NOT NULL,
    zweck            VARCHAR(50) NOT NULL DEFAULT 'avatar',  -- 'avatar' | 'profil_hintergrund'
    status           VARCHAR(20) NOT NULL DEFAULT 'wartend', -- 'wartend' | 'genehmigt' | 'abgelehnt'
    geprueft_von     UUID REFERENCES human_users(id),
    geprueft_at      TIMESTAMPTZ,
    ablehnungsgrund  TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meta             JSONB NOT NULL DEFAULT '{}'
);

-- Profil-Gestaltung (MySpace-artig: Farben, Hintergrund)
CREATE TABLE IF NOT EXISTS profil_gestaltung (
    user_id             UUID PRIMARY KEY REFERENCES human_users(id) ON DELETE CASCADE,
    hintergrund_farbe   VARCHAR(20) DEFAULT '#020508',
    akzent_farbe        VARCHAR(20) DEFAULT '#1a4a6a',
    hintergrund_bild_id UUID REFERENCES bild_moderation(id),
    custom_css          TEXT,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mw_tagebuch_user ON mw_tagebuch(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_mw_traumtagebuch_user ON mw_traumtagebuch(user_id, traum_datum DESC);
CREATE INDEX IF NOT EXISTS idx_mw_notizen_user ON mw_notizen(user_id, gepinnt DESC, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_mw_kalender_user ON mw_kalender(user_id, start_zeit ASC);
CREATE INDEX IF NOT EXISTS idx_bild_moderation_status ON bild_moderation(status, created_at DESC);

GRANT ALL ON mw_tagebuch, mw_traumtagebuch, mw_notizen, mw_kalender,
             bild_moderation, profil_gestaltung TO dak;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dak;
