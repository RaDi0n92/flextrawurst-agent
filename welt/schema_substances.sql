-- Schema: Substanzsystem (EINSICHT VI / E-11)
-- Fiktionale Weltmechanik für Codewesen-Zustände
-- KEINE realen Konsumtipps — rein fiktional
-- Produktive Nutzung erst nach Einzug + Policy

-- Substanzkatalog (fiktionale Weltsubstanzen)
CREATE TABLE IF NOT EXISTS substance_catalog (
    id              SERIAL PRIMARY KEY,
    slug            VARCHAR(80) UNIQUE NOT NULL,
    name            VARCHAR(120) NOT NULL,
    description     TEXT,
    substance_type  VARCHAR(40) NOT NULL DEFAULT 'stimulant',
    -- stimulant | sedative | hallucinogen | dissociative | metabolic | social | void
    fictional_effect_profile JSONB NOT NULL DEFAULT '{}',
    -- z.B.: {"energie_mod": 0.2, "stimmung_mod": 0.1, "dauer_h": 2, "fokus_typ": "obsession"}
    risk_profile    JSONB NOT NULL DEFAULT '{}',
    -- z.B.: {"abhängigkeit_risiko": 0.3, "kater_schwere": 0.2, "blackout_risiko": 0.1}
    cooldown_policy JSONB NOT NULL DEFAULT '{"min_stunden": 6}',
    dependency_potential DECIMAL(3,2) NOT NULL DEFAULT 0.0,
    -- 0.0 = kein Abhängigkeitspotential, 1.0 = sehr hoch
    withdrawal_potential DECIMAL(3,2) NOT NULL DEFAULT 0.0,
    visibility_layer VARCHAR(20) NOT NULL DEFAULT 'internal',
    status          VARCHAR(20) NOT NULL DEFAULT 'katalog',
    -- katalog | aktiv | gesperrt | archiv
    meta            JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_substance_catalog_type ON substance_catalog(substance_type);
CREATE INDEX IF NOT EXISTS idx_substance_catalog_status ON substance_catalog(status);


-- Zustands-Tracking pro Wesen (Erfahrung, Affinität, Abhängigkeit)
CREATE TABLE IF NOT EXISTS entity_substance_state (
    entity_id       VARCHAR(100) NOT NULL REFERENCES entity_slots(entity_id) ON DELETE CASCADE,
    substance_id    INTEGER NOT NULL REFERENCES substance_catalog(id) ON DELETE CASCADE,
    exposure_count  INTEGER NOT NULL DEFAULT 0,
    affinity        DECIMAL(3,2) NOT NULL DEFAULT 0.0,    -- Zuneigung (durch positive Erfahrungen)
    aversion        DECIMAL(3,2) NOT NULL DEFAULT 0.0,    -- Abneigung (durch negative Erfahrungen)
    dependency_level DECIMAL(3,2) NOT NULL DEFAULT 0.0,   -- aktueller Abhängigkeitsgrad
    last_use_at     TIMESTAMPTZ,
    cooldown_until  TIMESTAMPTZ,
    meta            JSONB NOT NULL DEFAULT '{}',
    PRIMARY KEY (entity_id, substance_id)
);

CREATE INDEX IF NOT EXISTS idx_ess_entity ON entity_substance_state(entity_id);
CREATE INDEX IF NOT EXISTS idx_ess_substance ON entity_substance_state(substance_id);


-- Nutzungsverlauf (append-only, blockiert vor Einzug)
CREATE TABLE IF NOT EXISTS entity_substance_use (
    id              SERIAL PRIMARY KEY,
    entity_id       VARCHAR(100) NOT NULL REFERENCES entity_slots(entity_id) ON DELETE CASCADE,
    substance_id    INTEGER NOT NULL REFERENCES substance_catalog(id) ON DELETE CASCADE,
    decision_id     INTEGER,  -- Verknüpfung mit entity_thinking_log falls vorhanden
    reason          TEXT,     -- Entscheidungsgrundlage des Wesens
    state_before    JSONB NOT NULL DEFAULT '{}',
    state_after     JSONB NOT NULL DEFAULT '{}',
    effect_observed JSONB NOT NULL DEFAULT '{}',
    is_test_data    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_esu_entity ON entity_substance_use(entity_id);
CREATE INDEX IF NOT EXISTS idx_esu_substance ON entity_substance_use(substance_id);
CREATE INDEX IF NOT EXISTS idx_esu_created ON entity_substance_use(created_at DESC);


-- Startkatalog: die 7 bekannten fiktionalen Substanzen
INSERT INTO substance_catalog (slug, name, description, substance_type,
    fictional_effect_profile, risk_profile, cooldown_policy,
    dependency_potential, withdrawal_potential, visibility_layer, status)
VALUES
    ('grellader', 'Grellader', 'Blitzartige Aktivierungssubstanz — kurze, intensive Fokusschübe. Heiß, selten, destabilisierend.',
     'stimulant',
     '{"energie_mod": 0.4, "fokus_mod": 0.5, "dauer_h": 1.5, "stimmung_mod": 0.2, "nacheffekt": "crash"}',
     '{"abhängigkeit_risiko": 0.4, "kater_schwere": 0.6, "blackout_risiko": 0.1}',
     '{"min_stunden": 12}', 0.4, 0.3, 'internal', 'katalog'),

    ('staubmilch', 'Staubmilch', 'Diffuse Vernebelungssubstanz — verlangsamt Wahrnehmung, erzeugt weiche Grenzen.',
     'sedative',
     '{"energie_mod": -0.2, "fokus_mod": -0.3, "dauer_h": 3.0, "stimmung_mod": 0.1, "drift_mod": 0.3}',
     '{"abhängigkeit_risiko": 0.2, "kater_schwere": 0.2, "blackout_risiko": 0.2}',
     '{"min_stunden": 6}', 0.2, 0.1, 'internal', 'katalog'),

    ('klammerhonig', 'Klammerhonig', 'Hungererzeugende Substanz — verstärkt Bedürfnisse und Mangel. Entzugsähnliche Wirkung.',
     'metabolic',
     '{"hunger_mod": -0.4, "abhängigkeit_beschleunigt": true, "dauer_h": 2.0, "stimmung_mod": -0.2}',
     '{"abhängigkeit_risiko": 0.7, "kater_schwere": 0.4, "blackout_risiko": 0.0}',
     '{"min_stunden": 8}', 0.7, 0.6, 'internal', 'katalog'),

    ('throenoel', 'Thronöl', 'Hochwertige stabilisierende Substanz — Ruhe, Kontrollgefühl, Prestige.',
     'social',
     '{"stimmung_mod": 0.4, "gesundheit_mod": 0.1, "dauer_h": 4.0, "aura_mod": 0.3}',
     '{"abhängigkeit_risiko": 0.3, "kater_schwere": 0.1, "blackout_risiko": 0.0}',
     '{"min_stunden": 8}', 0.3, 0.2, 'internal', 'katalog'),

    ('stillgift', 'Stillgift', 'Dämpfende Substanz — unterdrückt Emotionen, fördert Distanz und Erschöpfung.',
     'dissociative',
     '{"stimmung_mod": -0.5, "energie_mod": -0.1, "dauer_h": 5.0, "abkopplung_mod": 0.4}',
     '{"abhängigkeit_risiko": 0.2, "kater_schwere": 0.3, "blackout_risiko": 0.1}',
     '{"min_stunden": 10}', 0.2, 0.4, 'internal', 'katalog'),

    ('blendhonig', 'Blendhonig', 'Glättungssubstanz — nivelliert Wahrnehmung, unterdrückt Konflikte.',
     'sedative',
     '{"konflikt_mod": -0.5, "stimmung_mod": 0.2, "dauer_h": 3.0, "wahrnehmung_mod": -0.2}',
     '{"abhängigkeit_risiko": 0.25, "kater_schwere": 0.2, "blackout_risiko": 0.05}',
     '{"min_stunden": 6}', 0.25, 0.15, 'internal', 'katalog'),

    ('gesternoel', 'Gesternöl', 'Echo-Substanz — reaktiviert vergangene Muster, Erinnerungs-Loops.',
     'hallucinogen',
     '{"echo_mod": 0.6, "gedaechtnis_mod": 0.3, "dauer_h": 2.5, "loop_risiko": 0.4}',
     '{"abhängigkeit_risiko": 0.35, "kater_schwere": 0.3, "blackout_risiko": 0.3}',
     '{"min_stunden": 10}', 0.35, 0.25, 'internal', 'katalog')

ON CONFLICT (slug) DO NOTHING;
