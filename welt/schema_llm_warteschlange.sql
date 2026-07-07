-- LLM-Scheduler (2026-07-07): Prioritaets-Warteschlange fuer die gemeinsam genutzten
-- llama-server-Instanzen (2 echte Slots je Server, siehe --parallel 2 in den systemd-Units).
-- Ersetzt das alte slot_0.lock-Dateisystem-Semaphor (1 Lock fuer alles, keine Prioritaet,
-- meist unbegrenzte Wartezeit, siehe docs/systemdoku fuer die Analyse vom 2026-07-07).
--
-- Selbstheilend: eine Zeile zaehlt nur als "aktiv" solange slot_bis in der Zukunft liegt —
-- stirbt ein Prozess waehrend er einen Slot haelt, faellt der Slot automatisch frei sobald
-- slot_bis verstreicht, ganz ohne Aufraeum-Logik.

CREATE TABLE IF NOT EXISTS llm_warteschlange (
    id           BIGSERIAL PRIMARY KEY,
    server       VARCHAR(20) NOT NULL,
    prioritaet   SMALLINT NOT NULL,
    rufer        VARCHAR(100) NOT NULL,
    angefragt_um TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    slot_bis     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_llm_warteschlange_server ON llm_warteschlange (server);

GRANT ALL ON llm_warteschlange TO dak;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dak;
