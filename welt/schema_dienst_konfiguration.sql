-- Individualisierbare Dienst-Konfiguration (flarumstyler-Ausbau, 2026-07-07)
-- Jeder codewesen-Dienst kann einen Takt/Intervall-Override und einen Verhaltenstext
-- bekommen, der tatsaechlich in den System-Prompt einfliesst (nicht nur Dokumentation
-- wie SERVICE_BESCHREIBUNG in weltkern_watchdog.py). NULL-Werte = Skript-Default gilt weiter.
-- Vorbild: user_modules in schema_menschen.sql (module_name/enabled/config JSONB).

CREATE TABLE IF NOT EXISTS dienst_konfiguration (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dienst_name    VARCHAR(100) UNIQUE NOT NULL,
    takt_sekunden  INTEGER,
    verhalten_text TEXT,
    beschreibung_override TEXT,  -- ergaenzt 2026-07-07: ueberschreibt SERVICE_BESCHREIBUNG (weltkern_watchdog.py), editierbar in flarumstyler fuer ALLE Dienste (nicht nur konfigurierbare)
    meta           JSONB NOT NULL DEFAULT '{}',
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

GRANT ALL ON dienst_konfiguration TO dak;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dak;
