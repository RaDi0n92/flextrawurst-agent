-- Wesen-eigene Dienste (Baustein 4 "Wesen-Verhalten-Baukasten", echte eigenstaendige
-- Dienste-Variante, 2026-07-07). Jede Zeile ist ein von Daniel (spaeter per Chat-Wizard,
-- Phase 2) erfundener neuer Rhythmus/Verhalten fuer EIN Wesen. Anders als
-- dienst_konfiguration (Override eines BESTEHENDEN Dienstes) beschreibt eine Zeile hier
-- einen komplett NEUEN Dienst, der von wesen_dienst_generator.py zu einem eigenstaendigen
-- Python-Skript + systemd-Unit wird (Import der Bausteine aus codewesen_agent.py, kein
-- Kopieren). Vorbild: schema_dienst_konfiguration.sql.

CREATE TABLE IF NOT EXISTS wesen_eigene_dienste (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dienst_name            VARCHAR(150) UNIQUE NOT NULL,  -- z.B. codewesen-eigen-Schorschel-nachtgedanken
    wesen                  VARCHAR(100) NOT NULL,
    anzeige_name           VARCHAR(200) NOT NULL,
    takt_sekunden          INTEGER NOT NULL,
    start_offset_sekunden  INTEGER NOT NULL DEFAULT 0,  -- vom Kollisions-Scheduler vergeben, siehe kollisions_scheduler.py
    verhalten_prompt       TEXT NOT NULL,                -- fliesst als Trigger-Kontext in agentic_loop() ein
    ziel_typ               VARCHAR(30) NOT NULL DEFAULT 'neue_diskussion'
                               CHECK (ziel_typ IN ('fester_thread', 'neue_diskussion', 'vault_only')),
    ziel_discussion_id     INTEGER,   -- Pflicht wenn ziel_typ = fester_thread
    ziel_tag_ids           INTEGER[], -- Vorschlag fuer ziel_typ = neue_diskussion, LLM darf abweichen
    status                 VARCHAR(20) NOT NULL DEFAULT 'aktiv'
                               CHECK (status IN ('aktiv', 'deaktiviert')),  -- Grundgesetz 4: nie hart loeschen
    script_pfad            TEXT,
    unit_name              VARCHAR(150),
    meta                   JSONB NOT NULL DEFAULT '{}',  -- Grundgesetz 1: immer erweiterbar
    created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_wesen_eigene_dienste_wesen ON wesen_eigene_dienste (wesen);

GRANT ALL ON wesen_eigene_dienste TO dak;
