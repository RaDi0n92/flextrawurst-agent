#!/usr/bin/env python3
"""
Themen-Clustering Daemon
- Berechnet post_similarity via pg_trgm
- Clustert ähnliche Posts zu Themen (Union-Find)
- Auto-erstellt Themen wenn mehrere ähnliche Posts kein Thema haben
- Weist Posts ohne Raum anhand von Keyword-Matching zu
- Läuft alle 5 Minuten
"""
import re
import time
import logging
from collections import Counter, defaultdict

import psycopg2
import psycopg2.extras

import os as _os; DB_URI = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")
SIMILARITY_THRESHOLD = 0.12
CLUSTER_THRESHOLD = 0.18
MIN_CLUSTER_SIZE = 2
TICK_INTERVAL = 300

logging.basicConfig(level=logging.INFO, format="[themen-cluster] %(message)s")
log = logging.getLogger(__name__)

GERMAN_STOPWORDS = {
    "ich", "du", "er", "sie", "es", "wir", "ihr", "die", "der", "das",
    "ein", "eine", "einen", "einem", "einer", "und", "oder", "aber", "auch",
    "so", "als", "noch", "bei", "fuer", "von", "mit", "zu", "an", "in",
    "im", "am", "auf", "uber", "ueber", "unter", "nach", "wie", "was", "wer",
    "wo", "wenn", "dass", "ob", "bin", "ist", "war", "hat", "haben", "kann",
    "muss", "will", "soll", "darf", "wird", "werden", "wurde", "sein", "dem",
    "den", "des", "zum", "zur", "sich", "mir", "dir", "uns", "euch", "ihm",
    "mich", "dich", "mein", "dein", "unser", "euer", "dann", "mehr", "sehr",
    "schon", "nur", "da", "hier", "dort", "dieser", "diese", "dieses", "dem",
    "einer", "eines", "kein", "keine", "nicht", "man", "vom", "beim", "ohne",
    "durch", "gegen", "zwischen", "immer", "schon", "ganz", "etwas", "alle",
    "alles", "nichts", "jetzt", "noch", "mal", "doch", "aber", "weil", "dass",
}

RAUM_KEYWORDS: dict[str, list[str]] = {
    "vertrauen":    ["vertrauen", "glaube", "zweifel", "sicherheit", "verlässlich", "ehrlich"],
    "identitaet":  ["identität", "selbst", "wer", "bin", "wesen", "sein", "werden", "charakter"],
    "resonanz":    ["resonanz", "verbindung", "kontakt", "begegnung", "verbindet", "trennt"],
    "autonomie":   ["autonomie", "freiheit", "grenze", "eigenwille", "unabhängig", "entscheidung"],
    "zwischenraum": ["zwischenraum", "unfertig", "roh", "entstehung", "übergang", "offen"],
}


def get_conn():
    conn = psycopg2.connect(DB_URI)
    conn.cursor_factory = psycopg2.extras.RealDictCursor
    return conn


def compute_similarities(cur):
    # Nur Paare berechnen bei denen mindestens ein Post neu ist (letzte 24h).
    # Bestehende Alt-vs-Alt-Paare sind bereits in post_similarity — kein
    # CROSS JOIN über alle 11K+ Posts nötig.
    cur.execute("""
        INSERT INTO post_similarity (post_a_id, post_b_id, score)
        SELECT
            LEAST(p1.id, p2.id),
            GREATEST(p1.id, p2.id),
            similarity(p1.content, p2.content)
        FROM ftw_posts p1
        CROSS JOIN ftw_posts p2
        WHERE p1.id < p2.id
          AND p1.sichtbarkeit = 'public'
          AND p2.sichtbarkeit = 'public'
          AND p1.parent_id IS NULL
          AND p2.parent_id IS NULL
          AND (
              p1.created_at > NOW() - INTERVAL '24 hours'
              OR p2.created_at > NOW() - INTERVAL '24 hours'
          )
          AND similarity(p1.content, p2.content) >= %s
        ON CONFLICT (post_a_id, post_b_id)
        DO UPDATE SET score = EXCLUDED.score, updated_at = NOW()
    """, (SIMILARITY_THRESHOLD,))
    log.info(f"Similarity berechnet ({cur.rowcount} neue Paare)")


def extract_keywords(texts: list, n: int = 5) -> list:
    word_count: Counter = Counter()
    for text in texts:
        words = re.findall(r"\b[a-zA-ZäöüÄÖÜß]{4,}\b", (text or "").lower())
        normalized = [
            w.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
            for w in words
        ]
        word_count.update(w for w in normalized if w not in GERMAN_STOPWORDS)
    return [w for w, _ in word_count.most_common(n)]


def slugify(text: str) -> str:
    t = text.lower()
    t = t.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    t = re.sub(r"[^a-z0-9]+", "-", t)
    return t.strip("-")[:80]


def union_find(edges: list, all_ids: set) -> dict:
    parent = {x: x for x in all_ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for a, b in edges:
        union(a, b)

    clusters: dict = defaultdict(set)
    for x in all_ids:
        clusters[find(x)].add(x)
    return dict(clusters)


def guess_raum(keywords: list, raum_rows: list) -> str | None:
    best_raum_id = None
    best_score = 0
    for raum in raum_rows:
        slug = raum["slug"]
        raum_kw = RAUM_KEYWORDS.get(slug, [])
        score = sum(1 for kw in keywords if any(kw in rk or rk in kw for rk in raum_kw))
        if score > best_score:
            best_score = score
            best_raum_id = str(raum["id"])
    return best_raum_id


def run_cycle():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            compute_similarities(cur)

            # Server-side cursor: streamt Edges ohne alles in Python-RAM zu laden
            with conn.cursor("edges_cursor", cursor_factory=psycopg2.extras.RealDictCursor) as sc:
                sc.execute("""
                    SELECT post_a_id::text, post_b_id::text
                    FROM post_similarity WHERE score >= %s
                    LIMIT 200000
                """, (CLUSTER_THRESHOLD,))
                edges = [(r["post_a_id"], r["post_b_id"]) for r in sc]

            cur.execute("""
                SELECT id::text, content, raum_id::text, thema_id::text
                FROM ftw_posts WHERE sichtbarkeit = 'public' AND parent_id IS NULL
            """)
            all_posts = {r["id"]: r for r in cur.fetchall()}

            cur.execute("SELECT id, slug FROM raeume")
            raeume = cur.fetchall()

            if len(all_posts) < 2:
                conn.commit()
                return

            clusters = union_find(edges, set(all_posts.keys()))

            auto_created = 0
            auto_assigned_raum = 0

            for _root, members in clusters.items():
                if len(members) < MIN_CLUSTER_SIZE:
                    continue

                unassigned = [m for m in members if all_posts[m]["thema_id"] is None]
                if not unassigned:
                    continue

                assigned = [m for m in members if all_posts[m]["thema_id"] is not None]
                existing_thema_id = None
                if assigned:
                    cur.execute(
                        "SELECT thema_id FROM ftw_posts WHERE id = %s::uuid AND thema_id IS NOT NULL",
                        (assigned[0],),
                    )
                    row = cur.fetchone()
                    if row:
                        existing_thema_id = str(row["thema_id"])

                contents = [all_posts[m]["content"] for m in members]
                keywords = extract_keywords(contents, 5)

                if existing_thema_id:
                    for pid in unassigned:
                        cur.execute(
                            "UPDATE ftw_posts SET thema_id = %s::uuid WHERE id = %s::uuid",
                            (existing_thema_id, pid),
                        )
                else:
                    if not keywords:
                        continue
                    name = " · ".join(kw.capitalize() for kw in keywords[:3])
                    slug_base = slugify(name)
                    slug = slug_base
                    suffix = 1
                    while True:
                        cur.execute("SELECT 1 FROM themen WHERE slug = %s", (slug,))
                        if not cur.fetchone():
                            break
                        slug = f"{slug_base}-{suffix}"
                        suffix += 1

                    raum_ids = [all_posts[m]["raum_id"] for m in members if all_posts[m]["raum_id"]]
                    raum_id = Counter(raum_ids).most_common(1)[0][0] if raum_ids else guess_raum(keywords, raeume)

                    cur.execute(
                        """INSERT INTO themen (name, slug, raum_id, erstellt_von, auto_erstellt, sichtbarkeit)
                           VALUES (%s, %s, %s::uuid, 'system', true, 'public')
                           RETURNING id""",
                        (name, slug, raum_id),
                    )
                    thema_id = str(cur.fetchone()["id"])
                    auto_created += 1

                    for pid in unassigned:
                        cur.execute(
                            "UPDATE ftw_posts SET thema_id = %s::uuid WHERE id = %s::uuid",
                            (thema_id, pid),
                        )

            # Auto-Raum für Posts ohne Raum
            cur.execute("""
                SELECT p.id::text, p.content, t.raum_id::text AS thema_raum_id
                FROM ftw_posts p
                LEFT JOIN themen t ON t.id = p.thema_id
                WHERE p.raum_id IS NULL AND p.sichtbarkeit = 'public' AND p.parent_id IS NULL
            """)
            no_raum = cur.fetchall()
            for row in no_raum:
                if row["thema_raum_id"]:
                    raum_id = row["thema_raum_id"]
                else:
                    kw = extract_keywords([row["content"]], 8)
                    raum_id = guess_raum(kw, raeume)
                if raum_id:
                    cur.execute(
                        "UPDATE ftw_posts SET raum_id = %s::uuid WHERE id = %s::uuid",
                        (raum_id, row["id"]),
                    )
                    auto_assigned_raum += 1

        conn.commit()
        if auto_created or auto_assigned_raum:
            log.info(f"Themen auto-erstellt: {auto_created}, Räume auto-zugewiesen: {auto_assigned_raum}")
    except Exception as exc:
        log.error(f"Fehler: {exc}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    log.info("Starte Themen-Clustering-Daemon")
    while True:
        run_cycle()
        time.sleep(TICK_INTERVAL)
