"""
Similarity-Daemon: berechnet Post- und Thema-Ähnlichkeit via tsvector,
schlägt Cluster vor und setzt sie automatisch um.
Läuft alle 120s.
"""
import time, json, logging
import psycopg2
from psycopg2.extras import RealDictCursor

DB_URI = "postgresql://dak:dakpass@localhost:5432/flextrawurst"
INTERVAL = 120
CLUSTER_THRESHOLD = 0.3  # ab hier Vorschlag
CLUSTER_AUTO_THRESHOLD = 0.6  # ab hier automatisch zusammenführen
MIN_POSTS_FOR_CLUSTER = 2

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("similarity")


def get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=RealDictCursor)


def update_post_similarity(conn):
    """Berechnet ts_rank zwischen allen Post-Paaren, schreibt post_similarity."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO post_similarity (post_a_id, post_b_id, score, updated_at)
            SELECT
                a.id,
                b.id,
                ts_rank(a.tsv, to_tsquery('german', replace(b.content, ' ', ' & '))),
                NOW()
            FROM ftw_posts a
            JOIN ftw_posts b ON a.id < b.id
            WHERE a.tsv IS NOT NULL AND b.content IS NOT NULL
            ON CONFLICT (post_a_id, post_b_id) DO UPDATE
                SET score = EXCLUDED.score, updated_at = NOW()
        """)
        inserted = cur.rowcount
    conn.commit()
    log.info(f"post_similarity: {inserted} Einträge aktualisiert")


def update_thema_similarity(conn):
    """Berechnet Ähnlichkeit zwischen Themen."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO thema_similarity (thema_a_id, thema_b_id, score, updated_at)
            SELECT
                a.id,
                b.id,
                word_similarity(a.name, b.name),
                NOW()
            FROM themen a
            JOIN themen b ON a.id < b.id
            WHERE a.name IS NOT NULL AND b.name IS NOT NULL
            ON CONFLICT (thema_a_id, thema_b_id) DO UPDATE
                SET score = EXCLUDED.score, updated_at = NOW()
        """)
    conn.commit()


def propose_and_auto_cluster(conn):
    """
    Findet Themen-Paare über CLUSTER_THRESHOLD.
    Über AUTO_THRESHOLD: erstellt automatisch ein Eltern-Thema.
    Darunter: schreibt Vorschlag in thema_cluster_vorschlaege.
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT ts.thema_a_id, ts.thema_b_id, ts.score,
                   a.name AS name_a, a.raum_id AS raum_a, a.parent_id AS parent_a,
                   b.name AS name_b, b.raum_id AS raum_b, b.parent_id AS parent_b
            FROM thema_similarity ts
            JOIN themen a ON a.id = ts.thema_a_id
            JOIN themen b ON b.id = ts.thema_b_id
            WHERE ts.score >= %s
              AND a.parent_id IS NULL AND b.parent_id IS NULL
              AND a.id != b.id
        """, (CLUSTER_THRESHOLD,))
        pairs = cur.fetchall()

    for p in pairs:
        if p["parent_a"] is not None or p["parent_b"] is not None:
            continue  # schon eingeordnet

        if p["score"] >= CLUSTER_AUTO_THRESHOLD:
            _auto_merge(conn, p)
        else:
            _propose_cluster(conn, p)


def _auto_merge(conn, p):
    """Erstellt Eltern-Thema und hängt beide darunter."""
    raum_id = p["raum_a"] or p["raum_b"]
    parent_name = f"{p['name_a']} & {p['name_b']}"
    slug = parent_name.lower().replace(" ", "-").replace("&", "und")[:180]

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO themen (name, slug, raum_id, auto_erstellt, tiefe, sichtbarkeit)
            VALUES (%s, %s, %s, true, 0, 'public')
            ON CONFLICT DO NOTHING
            RETURNING id
        """, (parent_name, slug, raum_id))
        row = cur.fetchone()
        if not row:
            return
        parent_id = row["id"]

        cur.execute("""
            UPDATE themen SET parent_id = %s, tiefe = 1
            WHERE id IN (%s, %s) AND parent_id IS NULL
        """, (parent_id, p["thema_a_id"], p["thema_b_id"]))

    conn.commit()
    log.info(f"Auto-Cluster erstellt: '{parent_name}' für {p['name_a']} + {p['name_b']}")


def _propose_cluster(conn, p):
    """Schreibt Vorschlag in thema_cluster_vorschlaege, falls noch nicht vorhanden."""
    ids = sorted([str(p["thema_a_id"]), str(p["thema_b_id"])])
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id FROM thema_cluster_vorschlaege
            WHERE thema_ids @> %s::jsonb AND status = 'offen'
        """, (json.dumps(ids),))
        if cur.fetchone():
            return
        name = f"{p['name_a']} / {p['name_b']}"
        cur.execute("""
            INSERT INTO thema_cluster_vorschlaege (thema_ids, vorgeschlagener_name, score)
            VALUES (%s, %s, %s)
        """, (json.dumps(ids), name, float(p["score"])))
    conn.commit()
    log.info(f"Cluster-Vorschlag: '{name}' (score={p['score']:.2f})")


def run_once():
    log.info("Similarity-Daemon gestartet (einmalig)")
    try:
        conn = get_conn()
        update_post_similarity(conn)
        update_thema_similarity(conn)
        propose_and_auto_cluster(conn)
        conn.close()
        log.info("Einmalig-Lauf abgeschlossen")
    except Exception as e:
        log.error(f"Fehler: {e}")


def run():
    log.info("Similarity-Daemon gestartet")
    while True:
        try:
            conn = get_conn()
            update_post_similarity(conn)
            update_thema_similarity(conn)
            propose_and_auto_cluster(conn)
            conn.close()
        except Exception as e:
            log.error(f"Fehler: {e}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    import sys
    if "--once" in sys.argv:
        run_once()
    else:
        run()
