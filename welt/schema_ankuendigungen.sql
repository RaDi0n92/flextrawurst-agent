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

-- Migration 2026-07-21: Soft-Delete/Archiv (Daniels expliziter Wunsch nach echtem Loeschen-Button,
-- als Kompromiss mit Grundgesetz 4 "nichts wird geloescht" -- Standardweg ist Soft-Delete via
-- geloescht_am, echtes Hart-Loeschen nur als bewusste Zusatzaktion aus dem Archiv heraus.
ALTER TABLE ankuendigungen ADD COLUMN IF NOT EXISTS geloescht_am TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS ankuendigungen_kategorie_idx ON ankuendigungen (kategorie);
CREATE INDEX IF NOT EXISTS ankuendigungen_created_idx ON ankuendigungen (created_at DESC);
CREATE INDEX IF NOT EXISTS ankuendigungen_tsv_idx ON ankuendigungen
    USING GIN (to_tsvector('german', titel || ' ' || inhalt));
CREATE INDEX IF NOT EXISTS ankuendigungen_geloescht_idx ON ankuendigungen (geloescht_am);

-- Kommentare unter Ankuendigungen (2026-07-21, Daniels Wunsch): oeffentlich lesbar, schreiben nur
-- eingeloggte Menschen (kein Anon -- bewusst anders als Schattenkommentare, die ein eigenes,
-- semi-privates Sichtbarkeits-Konzept sind und hier nicht wiederverwendet werden). Likes/Reaktionen
-- laufen NICHT ueber eine neue Tabelle, sondern ueber das bestehende generische Resonanz-System
-- (resonanzen, post_source='ankuendigung', post_ref=ankuendigungen.id) -- Grundgesetz 2, keine
-- Doppel-Konstruktion fuer etwas das schon existiert.
CREATE TABLE IF NOT EXISTS ankuendigungen_kommentare (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ankuendigung_id UUID NOT NULL REFERENCES ankuendigungen(id),
    human_id        UUID NOT NULL REFERENCES human_users(id),
    content         TEXT NOT NULL CHECK (char_length(content) <= 5000),
    sichtbar        BOOLEAN NOT NULL DEFAULT true,   -- Admin blendet aus statt zu loeschen (Grundgesetz 4)
    meta            JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ankuendigungen_kommentare_ank_idx ON ankuendigungen_kommentare (ankuendigung_id, created_at);
