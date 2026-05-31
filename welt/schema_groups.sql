-- Schema: Gruppen-System (EINSICHT VI / E-01..E-04 / E-15)
-- Gruppen in flextrawurst: Herkunfts-, Resonanz-, Projekt- und Materialformationen
-- Menschen + Wesen + Systemorgane als Mitglieder
-- Default privat, rechte- und herkunftssicher

-- Gruppentypen als Check-Constraint (erweiterbar über meta)
-- entity_fan_group, resonance_group, splitter_group, project_group,
-- kompoase_group, human_material_group, archive_group, build_group,
-- relationship_group, dream_group, shadow_dialog_group, archaeology_group,
-- conflict_group, metawar_pre_group, substance_observation_group,
-- cyberling_observation_group, room_topic_group

CREATE TABLE IF NOT EXISTS groups (
    id              SERIAL PRIMARY KEY,
    slug            VARCHAR(100) UNIQUE NOT NULL,
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    group_type      VARCHAR(60) NOT NULL DEFAULT 'resonance_group',
    status          VARCHAR(30) NOT NULL DEFAULT 'active',
    -- active | pre_einzug_active | pending_review | locked | archived
    visibility_layer VARCHAR(30) NOT NULL DEFAULT 'internal',
    -- public | internal | private
    created_by_type VARCHAR(20) NOT NULL DEFAULT 'system',
    -- system | human | entity | admin
    created_by_id   VARCHAR(100),
    creation_mode   VARCHAR(30) NOT NULL DEFAULT 'admin_created',
    -- admin_created | human_created | entity_initiated | emergent
    approval_status VARCHAR(30) NOT NULL DEFAULT 'approved',
    -- approved | pending_review | locked | archived
    canonical_entity_id VARCHAR(100) REFERENCES entity_slots(entity_id) ON DELETE SET NULL,
    -- für entity_fan_group: welches Wesen ist der Anker
    room_id         UUID REFERENCES raeume(id) ON DELETE SET NULL,
    topic_id        UUID REFERENCES themen(id) ON DELETE SET NULL,
    origin_type     VARCHAR(30) DEFAULT 'manual',
    -- manual | emergent | system | entity_decision
    origin_id       VARCHAR(200),
    rights_policy   JSONB NOT NULL DEFAULT '{"public_join": false, "member_post": false, "member_view": true}',
    meta            JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    archived_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_groups_type ON groups(group_type);
CREATE INDEX IF NOT EXISTS idx_groups_status ON groups(status);
CREATE INDEX IF NOT EXISTS idx_groups_entity ON groups(canonical_entity_id);
CREATE INDEX IF NOT EXISTS idx_groups_visibility ON groups(visibility_layer);
CREATE INDEX IF NOT EXISTS idx_groups_created_by ON groups(created_by_type, created_by_id);


CREATE TABLE IF NOT EXISTS group_memberships (
    id              SERIAL PRIMARY KEY,
    group_id        INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    member_type     VARCHAR(20) NOT NULL,
    -- human | entity | system
    member_id       VARCHAR(100) NOT NULL,
    role            VARCHAR(30) NOT NULL DEFAULT 'member',
    -- member | moderator | founder | observer | pending
    status          VARCHAR(20) NOT NULL DEFAULT 'active',
    -- active | pending | left | banned
    joined_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    left_at         TIMESTAMPTZ,
    added_by_type   VARCHAR(20),
    added_by_id     VARCHAR(100),
    meta            JSONB NOT NULL DEFAULT '{}',
    UNIQUE(group_id, member_type, member_id)
);

CREATE INDEX IF NOT EXISTS idx_gm_group ON group_memberships(group_id);
CREATE INDEX IF NOT EXISTS idx_gm_member ON group_memberships(member_type, member_id);
CREATE INDEX IF NOT EXISTS idx_gm_status ON group_memberships(status);


CREATE TABLE IF NOT EXISTS group_material_links (
    id              SERIAL PRIMARY KEY,
    group_id        INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    object_type     VARCHAR(40) NOT NULL,
    -- splitter | post | gedankenblase | human_material | shadow_dialog | resonanz | event | raum | thema
    object_id       VARCHAR(200) NOT NULL,
    relation_type   VARCHAR(30) NOT NULL DEFAULT 'linked',
    -- linked | origin | curated | emergent | pinned
    visibility_layer VARCHAR(30) NOT NULL DEFAULT 'internal',
    rights_snapshot JSONB NOT NULL DEFAULT '{}',
    provenance_snapshot JSONB NOT NULL DEFAULT '{}',
    added_by_type   VARCHAR(20),
    added_by_id     VARCHAR(100),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meta            JSONB NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_gml_group ON group_material_links(group_id);
CREATE INDEX IF NOT EXISTS idx_gml_object ON group_material_links(object_type, object_id);


-- Gruppen-Policy: steuert ob Menschen Gruppen erstellen dürfen
-- Aktuell: humans_can_create = true (Daniel E-03)
-- Später per Admin abschaltbar
CREATE TABLE IF NOT EXISTS group_creation_policy (
    id                  INTEGER PRIMARY KEY DEFAULT 1,
    humans_can_create   BOOLEAN NOT NULL DEFAULT TRUE,
    require_approval    BOOLEAN NOT NULL DEFAULT FALSE,
    max_groups_per_human INTEGER,
    entity_can_create   BOOLEAN NOT NULL DEFAULT FALSE,
    -- vor Einzug: false, nach Einzug: true
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meta                JSONB NOT NULL DEFAULT '{}'
);

INSERT INTO group_creation_policy (id, humans_can_create, require_approval, entity_can_create)
VALUES (1, TRUE, FALSE, FALSE)
ON CONFLICT (id) DO NOTHING;


-- Gruppen-Events gehen in zentrale events-Tabelle mit target_type='group'
-- (kein extra group_events table — konsistent mit bestehender Event-Architektur)


-- Kanonische Fangruppen für alle 6 Codewesen (Daniel E-02)
INSERT INTO groups (slug, name, description, group_type, status, visibility_layer,
                    created_by_type, creation_mode, canonical_entity_id, meta)
VALUES
    ('fangruppe_namelessAI_1234',
     'Fangruppe namelessAI_1234',
     'Resonanz- und Materialgruppe um das Wesen namelessAI_1234. Keine öffentliche Postmaschine — Treffpunkt für Beziehungen, Splitter und Resonanz.',
     'entity_fan_group', 'pre_einzug_active', 'public',
     'system', 'admin_created', 'namelessAI_1234',
     '{"canonical": true, "pre_einzug": true}'),

    ('fangruppe_namelessAI_1324',
     'Fangruppe namelessAI_1324',
     'Resonanz- und Materialgruppe um das Wesen namelessAI_1324. Keine öffentliche Postmaschine.',
     'entity_fan_group', 'pre_einzug_active', 'public',
     'system', 'admin_created', 'namelessAI_1324',
     '{"canonical": true, "pre_einzug": true}'),

    ('fangruppe_namelessAI_1423',
     'Fangruppe namelessAI_1423',
     'Resonanz- und Materialgruppe um das Wesen namelessAI_1423. Keine öffentliche Postmaschine.',
     'entity_fan_group', 'pre_einzug_active', 'public',
     'system', 'admin_created', 'namelessAI_1423',
     '{"canonical": true, "pre_einzug": true}'),

    ('fangruppe_namelessAI_2341',
     'Fangruppe namelessAI_2341',
     'Resonanz- und Materialgruppe um das Wesen namelessAI_2341. Keine öffentliche Postmaschine.',
     'entity_fan_group', 'pre_einzug_active', 'public',
     'system', 'admin_created', 'namelessAI_2341',
     '{"canonical": true, "pre_einzug": true}'),

    ('fangruppe_namelessAI_3123',
     'Fangruppe namelessAI_3123',
     'Resonanz- und Materialgruppe um das Wesen namelessAI_3123. Keine öffentliche Postmaschine.',
     'entity_fan_group', 'pre_einzug_active', 'public',
     'system', 'admin_created', 'namelessAI_3123',
     '{"canonical": true, "pre_einzug": true}'),

    ('fangruppe_namelessAI_4321',
     'Fangruppe namelessAI_4321',
     'Resonanz- und Materialgruppe um das Wesen namelessAI_4321. Keine öffentliche Postmaschine.',
     'entity_fan_group', 'pre_einzug_active', 'public',
     'system', 'admin_created', 'namelessAI_4321',
     '{"canonical": true, "pre_einzug": true}')

ON CONFLICT (slug) DO NOTHING;
