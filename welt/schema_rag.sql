-- RAG Ring 1 (Basis-RAG) — Schema
-- Quelle: _claude/konzepte/DURCHF~1.ODT ("Durchführbare RAG-, Erinnerungs- und Resonanzarchitektur")
-- Korpora fuer diesen ersten Ausbau: Flarum-Archiv pro Wesen + geteiltes Weltwissen (wissen/).
-- GENI-Gedaechtnis (gedaechtnis/knoten, ~19 Mio. Dateien) bewusst NICHT Teil dieses Rings — Daniel-Entscheidung 2026-07-20.

CREATE EXTENSION IF NOT EXISTS vector;

-- Unveraenderte Ursprungsobjekte (2.1 Einspeisung)
CREATE TABLE IF NOT EXISTS rag_source_objects (
    id BIGSERIAL PRIMARY KEY,
    external_id TEXT NOT NULL UNIQUE,          -- z.B. 'flarum:diskussion:3035' oder 'wissen:system/foo.md'
    quelle TEXT NOT NULL,                      -- 'flarum_diskussion' | 'flarum_nutzer' | 'wissen'
    wesen TEXT,                                -- zugeordnetes Wesen, NULL bei geteiltem Weltwissen
    titel TEXT,
    inhalt TEXT NOT NULL,                      -- vollstaendiger, unveraenderter Ursprungstext
    erstellungszeit TIMESTAMPTZ,                -- Zeitpunkt des Ursprungsereignisses, falls bekannt
    urheber TEXT,
    herkunftsort TEXT NOT NULL,                 -- Dateipfad
    sichtbarkeit TEXT NOT NULL DEFAULT 'welt',
    ereignistyp TEXT NOT NULL,
    wahrheitsstatus TEXT NOT NULL DEFAULT 'aus_datei_abgeleitet',
    inhalt_pruefsumme TEXT NOT NULL,            -- sha256, fuer Change-Detection beim Re-Indizieren
    meta JSONB NOT NULL DEFAULT '{}',
    erstellt_am TIMESTAMPTZ NOT NULL DEFAULT now(),
    aktualisiert_am TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS rag_source_objects_wesen_idx ON rag_source_objects (wesen);
CREATE INDEX IF NOT EXISTS rag_source_objects_quelle_idx ON rag_source_objects (quelle);

-- Strukturbezogene Abschnitte (2.2 Zerlegung) — nie blind 200-500 Woerter, sondern an Struktur orientiert
CREATE TABLE IF NOT EXISTS rag_source_chunks (
    id BIGSERIAL PRIMARY KEY,
    source_object_id BIGINT NOT NULL REFERENCES rag_source_objects(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    ueberschrift TEXT,
    inhalt TEXT NOT NULL,
    inhalt_tsv tsvector GENERATED ALWAYS AS (to_tsvector('german', coalesce(ueberschrift,'') || ' ' || inhalt)) STORED,
    meta JSONB NOT NULL DEFAULT '{}',
    erstellt_am TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(source_object_id, chunk_index)
);
CREATE INDEX IF NOT EXISTS rag_source_chunks_tsv_idx ON rag_source_chunks USING GIN (inhalt_tsv);

-- Suchvektoren (2.3 Embeddings) — reine mathematische Suchposition, kein Wahrheitswert
CREATE TABLE IF NOT EXISTS rag_embeddings (
    id BIGSERIAL PRIMARY KEY,
    chunk_id BIGINT NOT NULL REFERENCES rag_source_chunks(id) ON DELETE CASCADE,
    modell TEXT NOT NULL,
    embedding vector(1024) NOT NULL,
    meta JSONB NOT NULL DEFAULT '{}',
    erstellt_am TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(chunk_id, modell)
);
CREATE INDEX IF NOT EXISTS rag_embeddings_hnsw_idx ON rag_embeddings USING hnsw (embedding vector_cosine_ops);

-- Abrufprotokolle (2.6 Rueckschreiben) — jede Suche wird nachvollziehbar, Original bleibt unveraendert
CREATE TABLE IF NOT EXISTS rag_retrieval_runs (
    id BIGSERIAL PRIMARY KEY,
    wesen TEXT,
    anlass TEXT,
    anfrage_text TEXT NOT NULL,
    meta JSONB NOT NULL DEFAULT '{}',
    erstellt_am TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS rag_retrieval_runs_wesen_idx ON rag_retrieval_runs (wesen);

CREATE TABLE IF NOT EXISTS rag_retrieval_results (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES rag_retrieval_runs(id) ON DELETE CASCADE,
    chunk_id BIGINT NOT NULL REFERENCES rag_source_chunks(id),
    rang INT NOT NULL,
    score DOUBLE PRECISION,
    tatsaechlich_verwendet BOOLEAN NOT NULL DEFAULT false,
    meta JSONB NOT NULL DEFAULT '{}',
    erstellt_am TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS rag_retrieval_results_run_idx ON rag_retrieval_results (run_id);
