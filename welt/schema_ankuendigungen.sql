-- Admin-News/Ankündigungen/History-Bereich, direkt links neben "Was ist das?" in der Surface.
-- Nur Admins duerfen posten (Grundgesetz 4), oeffentlich lesbar, durchsuchbar (Grundgesetz 3),
-- nichts wird geloescht nur deaktiviert (Grundgesetz 4), erweiterbar per meta JSONB (Grundgesetz 2).

CREATE TABLE IF NOT EXISTS ankuendigungen (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titel           TEXT NOT NULL,
    inhalt          TEXT NOT NULL,
    kategorie       TEXT NOT NULL DEFAULT 'news',   -- 'news' | 'ankuendigung' | 'history' | ... (bewusst kein Enum, Grundgesetz 2)
    bild_url        TEXT,                            -- /uploads/ankuendigungen/... , optional, austauschbar
    autor_id        UUID NOT NULL REFERENCES human_users(id),
    veroeffentlicht BOOLEAN NOT NULL DEFAULT true,
    angepinnt       BOOLEAN NOT NULL DEFAULT false,
    meta            JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Migration fuer bereits bestehende Tabellen (2026-07-20, Bild-Feature nachtraeglich):
ALTER TABLE ankuendigungen ADD COLUMN IF NOT EXISTS bild_url TEXT;

CREATE INDEX IF NOT EXISTS ankuendigungen_kategorie_idx ON ankuendigungen (kategorie);
CREATE INDEX IF NOT EXISTS ankuendigungen_created_idx ON ankuendigungen (created_at DESC);
CREATE INDEX IF NOT EXISTS ankuendigungen_tsv_idx ON ankuendigungen
    USING GIN (to_tsvector('german', titel || ' ' || inhalt));
