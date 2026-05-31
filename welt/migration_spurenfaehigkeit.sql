-- Migration: Spurenfähigkeit v0.1
-- Typisierte Post-Relationen, Herkunftsmarkierungen, Themen-Klima
-- Keine API-Endpunkte, kein Daemon, kein Klima-System — nur Datengrundlage.

-- 1. post_relationen ──────────────────────────────────────────────────────────
-- Gerichtete, typisierte Relationen von einem Post zu einem Weltobjekt.
-- Quelle ist immer ein Post. Ziel ist explizit typisiert (kein nullable Grauzone).
-- zu_post_id ist optional/ergänzend — nur setzen wenn ziel_typ = 'post',
-- ermöglicht schnelle FK-Joins ohne ziel_id casten zu müssen.

CREATE TABLE IF NOT EXISTS post_relationen (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,

    -- Quelle: immer ein Post
    von_post_id         UUID NOT NULL REFERENCES ftw_posts(id) ON DELETE CASCADE,

    -- Relationstyp: kontrolliertes Vokabular
    rel_typ             VARCHAR NOT NULL CHECK (rel_typ IN (
        'reply_to',         -- direkte Antwort
        'upgrade_of',       -- Weiterentwicklung / Verdichtung
        'split_from',       -- Abspaltung aus einem älteren Gedanken
        'contradicts',      -- Widerspruch
        'echoes',           -- Anklang ohne direkte Antwort
        'buried_in',        -- verschütteter Gedanke in einem älteren Objekt
        'dream_fragment_of',-- Traum-Bezug auf früheren Post / frühere Spannung
        'resonates_with'    -- Resonanz ohne Antwort / Widerspruch / Erweiterung
    )),

    -- Ziel: explizit typisiert — niemals stilles Null-Loch
    ziel_typ            VARCHAR NOT NULL CHECK (ziel_typ IN (
        'post',             -- anderer ftw_post
        'thema',            -- Thema / Unterthema
        'splitter',         -- Splitter aus der Zwischenraumphysik
        'traum',            -- Traumspur (traumspuren.spur_id)
        'resonanz',         -- Resonanz-Objekt
        'flarum_origin',    -- Flarum-Vorphase: ID oder Referenz-String
        'event'             -- Event aus der events-Tabelle
    )),
    ziel_id             VARCHAR NOT NULL,   -- UUID oder Referenz-String je nach ziel_typ

    -- Schnell-FK nur wenn Ziel wirklich ein Post ist (für JOINs ohne CAST)
    zu_post_id          UUID REFERENCES ftw_posts(id) ON DELETE SET NULL,

    -- Konsistenz: zu_post_id darf nur gesetzt sein wenn ziel_typ = 'post'
    CONSTRAINT ck_zu_post_konsistent CHECK (
        zu_post_id IS NULL OR ziel_typ = 'post'
    ),

    -- Provenienz: wer hat diese Relation angelegt
    erstellt_von_type   VARCHAR DEFAULT 'system',   -- 'system', 'entity', 'human', 'admin'
    erstellt_von_id     VARCHAR DEFAULT 'system',

    notiz               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    meta                JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_post_rel_von      ON post_relationen (von_post_id);
CREATE INDEX IF NOT EXISTS idx_post_rel_zu       ON post_relationen (zu_post_id) WHERE zu_post_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_post_rel_typ      ON post_relationen (rel_typ);
CREATE INDEX IF NOT EXISTS idx_post_rel_ziel     ON post_relationen (ziel_typ, ziel_id);
CREATE INDEX IF NOT EXISTS idx_post_rel_created  ON post_relationen (created_at DESC);

-- 2. ftw_posts: Herkunftsmarkierungen ─────────────────────────────────────────
-- flarum_herkunft: Post stammt aus der Flarum-Vorphase oder wurde manuell aus ihr übertragen
-- ist_voreinzug: Post wurde vor dem Einzug manuell angelegt (Übergangsprofil-Kontext)
-- Beide Booleans sind abfragbar — anders als in meta versteckt bleiben sie sichtbar.

ALTER TABLE ftw_posts ADD COLUMN IF NOT EXISTS flarum_herkunft  BOOLEAN DEFAULT false;
ALTER TABLE ftw_posts ADD COLUMN IF NOT EXISTS ist_voreinzug    BOOLEAN DEFAULT false;

-- 3. themen: Klima-Status ─────────────────────────────────────────────────────
-- Themen sind keine Ordner, sondern lebendige Diskursräume mit Zustand.
-- stable = tragfähig, fermenting = gärt, overheated = überhitzt,
-- splitting = will sich aufspalten, buried = verschüttet, repeating = kreist,
-- exhausted = vorerst leergezogen, seeded = frisch angelegt / Keim

ALTER TABLE themen ADD COLUMN IF NOT EXISTS klima_status VARCHAR DEFAULT 'stable'
    CHECK (klima_status IN (
        'stable', 'fermenting', 'overheated', 'splitting',
        'buried', 'repeating', 'exhausted', 'seeded'
    ));
