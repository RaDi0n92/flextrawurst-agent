-- Migration: Spurenfähigkeit v0.1 Ergänzung
-- Zustandsabdruck-Feld in ftw_posts

-- Separates JSONB für den Weltzustand beim Schreiben.
-- Trennt operativen Zustand (mood, pressure, conflict_level, refs)
-- vom Selbstmodell-Snapshot (selbstmodell_snapshot) der Entität.
ALTER TABLE ftw_posts ADD COLUMN IF NOT EXISTS zustandsabdruck JSONB;

-- Struktur des zustandsabdruck-Feldes (nicht erzwungen, aber konventionell):
-- {
--   "mood":                VARCHAR,   -- Stimmungslage beim Schreiben
--   "pressure":            FLOAT,     -- Innerer/systemischer Druck (0.0–1.0)
--   "active_traits":       TEXT[],    -- Aktive Wesenszüge oder Muster
--   "conflict_level":      FLOAT,     -- Konfliktintensität (0.0–1.0)
--   "resonance_context":   TEXT,      -- Aktive Resonanz-/Schattenkommentar-Kontexte
--   "cyberling_state_ref": UUID,      -- Cyberling-Zustand zum Schreibzeitpunkt
--   "substance_trace_ref": UUID,      -- Substanzspur-Referenz
--   "dream_ref":           UUID,      -- Traum/Traumfragment-Referenz
--   "flarum_origin_ref":   VARCHAR,   -- Flarum-Thread/Post-Referenz
--   "manual_transition_flag": BOOLEAN -- Post als manuelles Übergangsprofil markiert
-- }
