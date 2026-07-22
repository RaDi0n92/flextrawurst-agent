-- Billiges Vorlesen — Phase 1 (2026-07-22, Daniels Auftrag)
-- Interessensprofil pro Wesen (Mischung aus Charakterbeschreibung, RAG-Anfrage-Historie,
-- tatsaechlichen Reaktionen -- Phase 1 startet mit der Charakterbeschreibung, die anderen
-- beiden Quellen fliessen organisch dazu sobald Historie existiert, siehe
-- _claude/ideen/wesen_dauerhafte_handlungsfaehigkeit_und_einsichtsnebenscreen.md).
--
-- Phase 1 bewusst eng: nur EIN Wesen (Schorschel), nur EINE Scan-Quelle (Ankuendigungen).
-- Skalpell-Prinzip -- Erweiterung auf alle Wesen/weitere Quellen folgt nach Verifikation.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS entity_interessensprofil (
    entity_id       VARCHAR PRIMARY KEY REFERENCES entity_slots(entity_id),
    profil_vektor   vector(1024) NOT NULL,
    quellen         JSONB NOT NULL DEFAULT '{}',   -- {"charakter": {"quelle": "wesen.md", "aktualisiert_am": "..."}, "rag_anfragen": [], "reaktionen": []}
    aktualisiert_am TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS entity_interessensprofil_hnsw_idx
    ON entity_interessensprofil USING hnsw (profil_vektor vector_cosine_ops);

-- Kandidaten, die beim billigen Vorlesen nah genug am Interessensprofil lagen, um dem
-- Wesen beim naechsten echten Tick als Zusatz-Kontext angeboten zu werden.
CREATE TABLE IF NOT EXISTS entity_vorlese_funde (
    id              BIGSERIAL PRIMARY KEY,
    entity_id       VARCHAR NOT NULL REFERENCES entity_slots(entity_id),
    quelle          TEXT NOT NULL,                 -- 'ankuendigung' (Phase 1), spaeter weitere
    quelle_ref      TEXT NOT NULL,                 -- z.B. ankuendigungen.id
    titel           TEXT,
    aehnlichkeit    DOUBLE PRECISION NOT NULL,
    gelesen         BOOLEAN NOT NULL DEFAULT false,
    gefunden_am     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS entity_vorlese_funde_entity_idx
    ON entity_vorlese_funde (entity_id, gelesen, gefunden_am DESC);
