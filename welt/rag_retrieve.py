#!/usr/bin/env python3
"""
RAG Ring 1 — Hybride Suche (2.4) + Abrufprotokoll (2.6).
Kombiniert pgvector-Kosinusaehnlichkeit mit PostgreSQL-Volltextsuche, filterbar nach Wesen/Quelle.

Usage:
  python3 rag_retrieve.py "<anfrage>" [--wesen NAME] [--quelle wissen|flarum_diskussion] [-n 5]
"""
import json
import os
import sys

import psycopg2
import psycopg2.extras
import requests

DB_URI = os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")
OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
EMBED_MODELL = "bge-m3"


def embed(text: str) -> list[float]:
    resp = requests.post(OLLAMA_EMBED_URL, json={"model": EMBED_MODELL, "input": text}, timeout=60)
    resp.raise_for_status()
    return resp.json()["embeddings"][0]


def suche(anfrage: str, wesen: str = None, quelle: str = None, n: int = 5, wesen_der_anfrage: str = None, anlass: str = None):
    vektor = embed(anfrage)
    conn = psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO rag_retrieval_runs (wesen, anlass, anfrage_text)
                VALUES (%s, %s, %s) RETURNING id
            """, (wesen_der_anfrage, anlass, anfrage))
            run_id = cur.fetchone()["id"]

            bedingungen = []
            params = {"vektor": str(vektor), "anfrage": anfrage, "n": n}
            if wesen:
                # Post-Ebene hat Vorrang (flarum_diskussion): wenn kein Post-Wesen gesetzt ist
                # (z.B. wissen-Korpus, dort chunk-meta leer), auf Quellobjekt-Ebene zurueckfallen.
                bedingungen.append("coalesce(c.meta->>'wesen', so.wesen) = %(wesen_filter)s")
                params["wesen_filter"] = wesen
            if quelle:
                bedingungen.append("so.quelle = %(quelle_filter)s")
                params["quelle_filter"] = quelle
            where = ("AND " + " AND ".join(bedingungen)) if bedingungen else ""

            cur.execute(f"""
                SELECT
                    c.id AS chunk_id, so.titel, so.quelle, so.herkunftsort,
                    coalesce(c.meta->>'wesen', so.wesen) AS wesen,
                    c.ueberschrift, c.inhalt,
                    1 - (e.embedding <=> %(vektor)s) AS semantische_naehe,
                    ts_rank(c.inhalt_tsv, plainto_tsquery('german', %(anfrage)s)) AS volltext_rang
                FROM rag_source_chunks c
                JOIN rag_source_objects so ON so.id = c.source_object_id
                JOIN rag_embeddings e ON e.chunk_id = c.id AND e.modell = '{EMBED_MODELL}'
                WHERE true {where}
                ORDER BY (1 - (e.embedding <=> %(vektor)s)) * 0.7
                       + ts_rank(c.inhalt_tsv, plainto_tsquery('german', %(anfrage)s)) * 0.3 DESC
                LIMIT %(n)s
            """, params)
            ergebnisse = cur.fetchall()

            for rang, r in enumerate(ergebnisse, start=1):
                cur.execute("""
                    INSERT INTO rag_retrieval_results (run_id, chunk_id, rang, score)
                    VALUES (%s, %s, %s, %s)
                """, (run_id, r["chunk_id"], rang, r["semantische_naehe"]))
    conn.close()
    return ergebnisse


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    anfrage = sys.argv[1]
    wesen = sys.argv[sys.argv.index("--wesen") + 1] if "--wesen" in sys.argv else None
    quelle = sys.argv[sys.argv.index("--quelle") + 1] if "--quelle" in sys.argv else None
    n = int(sys.argv[sys.argv.index("-n") + 1]) if "-n" in sys.argv else 5

    for r in suche(anfrage, wesen=wesen, quelle=quelle, n=n):
        print(f"\n[{r['semantische_naehe']:.3f}] {r['titel']} — {r['ueberschrift']} (wesen={r['wesen']}, quelle={r['quelle']})")
        print(f"  {r['inhalt'][:200]}")
