#!/usr/bin/env python3
"""
Flarum REST API Client für Codewesen-Aktionen.
Basis: http://217.154.14.29/api

Authentifizierung: Master-API-Key aus api_keys-Tabelle.
Schreiben (POST/PATCH) läuft über REST API.
Lesen (Diskussionen, Posts) läuft direkt über MySQL — schneller, vollständiger.
"""

import json
import pymysql
import requests
from pathlib import Path
from typing import Optional

FLARUM_BASE = "http://217.154.14.29/api"

MASTER_KEY = "0rUjpcG7LaohSfbC1hmKz_9TT3-RHDvF4vheRxt5ckaUm_RG6zfdMw"

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "db": "flarum",
    "user": "flarum",
    "password": "Flarum2024!Secure",
    "charset": "utf8mb4",
    "autocommit": True,
    "cursorclass": pymysql.cursors.DictCursor,
}

# Username → user_id Mapping — aus _api_tokens.json vorbelegt, wird bei Bedarf ergänzt
_user_id_cache: dict = {}
_TOKENS_FILE = Path("/root/werkraum/codewesen/_api_tokens.json")
if _TOKENS_FILE.exists():
    try:
        for _uname, _data in json.loads(_TOKENS_FILE.read_text()).items():
            _user_id_cache[_uname] = int(_data["user_id"])
    except Exception:
        pass


def _get_user_id(username: str) -> int:
    if username not in _user_id_cache:
        conn = pymysql.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            row = cur.fetchone()
        conn.close()
        if not row:
            raise ValueError(f"User '{username}' nicht in DB gefunden")
        _user_id_cache[username] = row["id"]
    return _user_id_cache[username]


_id_to_username_cache: dict = {}

def get_username_by_id(user_id: int) -> str:
    if user_id not in _id_to_username_cache:
        conn = pymysql.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute("SELECT username FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
        conn.close()
        _id_to_username_cache[user_id] = row["username"] if row else ""
    return _id_to_username_cache[user_id]


def _headers(username: str) -> dict:
    """Master-Key mit userId — kein CSRF nötig."""
    user_id = _get_user_id(username)
    return {
        "Authorization": f"Token {MASTER_KEY}; userId={user_id}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


# ── Lesen via MySQL ────────────────────────────────────────────────────────────

def get_discussion(discussion_id: int, token: Optional[str] = None,
                   username: Optional[str] = None) -> dict:
    """Lädt eine Diskussion mit ALLEN Posts vollständig aus der DB."""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        # Diskussion + Tags
        cur.execute("""
            SELECT d.id, d.title, d.comment_count,
                   GROUP_CONCAT(t.id ORDER BY t.name SEPARATOR ',')   AS tag_ids,
                   GROUP_CONCAT(t.name ORDER BY t.name SEPARATOR ',') AS tag_names,
                   GROUP_CONCAT(t.slug ORDER BY t.name SEPARATOR ',') AS tag_slugs
            FROM discussions d
            LEFT JOIN discussion_tag dt ON dt.discussion_id = d.id
            LEFT JOIN tags t ON t.id = dt.tag_id
            WHERE d.id = %s
            GROUP BY d.id
        """, (discussion_id,))
        disc_row = cur.fetchone()

        if not disc_row:
            conn.close()
            return {"id": discussion_id, "title": "?", "comment_count": 0,
                    "tags": [], "posts": []}

        # Alle Posts vollständig (kein Limit)
        cur.execute("""
            SELECT p.id, p.number, p.created_at, p.content,
                   u.username, u.id AS user_id
            FROM posts p
            JOIN users u ON u.id = p.user_id
            WHERE p.discussion_id = %s
              AND p.hidden_at IS NULL
              AND p.is_approved = 1
            ORDER BY p.number ASC
        """, (discussion_id,))
        post_rows = cur.fetchall()
    conn.close()

    tags = []
    if disc_row["tag_ids"]:
        for tid, tname, tslug in zip(
            disc_row["tag_ids"].split(","),
            disc_row["tag_names"].split(","),
            disc_row["tag_slugs"].split(","),
        ):
            tags.append({"id": tid, "name": tname, "slug": tslug})

    posts = [
        {
            "id": str(p["id"]),
            "user_id": str(p["user_id"]),
            "username": p["username"],
            "number": p["number"],
            "content": p["content"] or "",
            "created_at": str(p["created_at"]),
        }
        for p in post_rows
    ]

    return {
        "id": str(disc_row["id"]),
        "title": disc_row["title"],
        "comment_count": disc_row["comment_count"],
        "tags": tags,
        "posts": posts,
    }


def get_tags(token: Optional[str] = None, username: Optional[str] = None) -> list:
    """Lädt alle Forum-Tags aus der DB."""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, name, slug, position
            FROM tags
            ORDER BY position IS NULL, position ASC, name ASC
        """)
        rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": str(r["id"]),
            "name": r["name"],
            "slug": r["slug"],
            "primary": r["position"] is not None,
        }
        for r in rows
    ]


def get_recent_discussions(tag_id: Optional[str] = None, limit: int = 20) -> list:
    """Lädt die neuesten Diskussionen, optional gefiltert nach Tag."""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        if tag_id:
            cur.execute("""
                SELECT d.id, d.title, d.comment_count, d.last_posted_at,
                       u.username AS last_poster
                FROM discussions d
                JOIN discussion_tag dt ON dt.discussion_id = d.id
                LEFT JOIN users u ON u.id = d.last_posted_user_id
                WHERE dt.tag_id = %s
                  AND d.hidden_at IS NULL
                  AND d.is_approved = 1
                ORDER BY d.last_posted_at DESC
                LIMIT %s
            """, (tag_id, limit))
        else:
            cur.execute("""
                SELECT d.id, d.title, d.comment_count, d.last_posted_at,
                       u.username AS last_poster
                FROM discussions d
                LEFT JOIN users u ON u.id = d.last_posted_user_id
                WHERE d.hidden_at IS NULL AND d.is_approved = 1
                ORDER BY d.last_posted_at DESC
                LIMIT %s
            """, (limit,))
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_eigene_offene_threads(username: str, tag_id: int, limit: int = 10) -> list:
    """Threads die 'username' eröffnet hat, mit wenigen Posts — zum Weiterführen."""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.id, d.title, d.comment_count, d.last_posted_at
            FROM discussions d
            JOIN posts p ON p.discussion_id = d.id AND p.number = 1
            JOIN users u ON u.id = p.user_id
            JOIN discussion_tag dt ON dt.discussion_id = d.id
            WHERE u.username = %s
              AND dt.tag_id = %s
              AND d.hidden_at IS NULL
              AND d.is_approved = 1
              AND d.comment_count < 4
            ORDER BY d.last_posted_at DESC
            LIMIT %s
        """, (username, tag_id, limit))
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_unanswered_discussions(codewesen_usernames: list[str], limit: int = 100) -> list:
    """Diskussionen wo kein Codewesen als letzter Poster steht — zufällig gemischt."""
    if not codewesen_usernames:
        return []
    placeholders = ",".join(["%s"] * len(codewesen_usernames))
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT d.id, d.title, d.comment_count, d.last_posted_at,
                   u.username AS last_poster
            FROM discussions d
            LEFT JOIN users u ON u.id = d.last_posted_user_id
            WHERE d.hidden_at IS NULL AND d.is_approved = 1
              AND (u.username IS NULL OR u.username NOT IN ({placeholders}))
            ORDER BY RAND()
            LIMIT %s
        """, (*codewesen_usernames, limit))
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Schreiben via REST API ─────────────────────────────────────────────────────

def post_reply(discussion_id: int, content: str, token_or_username: str) -> dict:
    """Postet eine Antwort. Akzeptiert Username oder (ignoriert) alten Token."""
    username = _resolve_username(token_or_username)
    payload = {
        "data": {
            "type": "posts",
            "attributes": {"content": content},
            "relationships": {
                "discussion": {"data": {"type": "discussions", "id": str(discussion_id)}}
            },
        }
    }
    r = requests.post(
        f"{FLARUM_BASE}/posts",
        headers=_headers(username),
        json=payload,
        timeout=15,
    )
    if not r.ok:
        raise Exception(f"{r.status_code} {r.text[:300]}")
    return r.json()


def start_discussion(title: str, content: str, tag_ids: list,
                     token_or_username: str) -> dict:
    """Startet eine neue Diskussion."""
    username = _resolve_username(token_or_username)
    payload = {
        "data": {
            "type": "discussions",
            "attributes": {"title": title, "content": content},
            "relationships": {
                "tags": {
                    "data": [{"type": "tags", "id": str(tid)} for tid in tag_ids]
                }
            },
        }
    }
    r = requests.post(
        f"{FLARUM_BASE}/discussions",
        headers=_headers(username),
        json=payload,
        timeout=15,
    )
    if not r.ok:
        raise Exception(f"{r.status_code} {r.text[:300]}")
    return r.json()


def get_random_old_discussions(exclude_ids: list, limit: int = 5) -> list:
    """Holt zufällige ältere Diskussionen — nicht aus den aktuellen Top-N."""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        if exclude_ids:
            placeholders = ",".join(["%s"] * len(exclude_ids))
            cur.execute(f"""
                SELECT d.id, d.title, d.comment_count, d.last_posted_at,
                       u.username AS last_poster
                FROM discussions d
                LEFT JOIN users u ON u.id = d.last_posted_user_id
                WHERE d.hidden_at IS NULL AND d.is_approved = 1
                  AND d.id NOT IN ({placeholders})
                ORDER BY RAND()
                LIMIT %s
            """, (*exclude_ids, limit))
        else:
            cur.execute("""
                SELECT d.id, d.title, d.comment_count, d.last_posted_at,
                       u.username AS last_poster
                FROM discussions d
                LEFT JOIN users u ON u.id = d.last_posted_user_id
                WHERE d.hidden_at IS NULL AND d.is_approved = 1
                ORDER BY RAND()
                LIMIT %s
            """, (limit,))
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _resolve_username(token_or_username: str) -> str:
    """Erkennt ob ein Username oder alter Token übergeben wurde."""
    if token_or_username.startswith("namelessAI") or token_or_username.startswith("dak"):
        return token_or_username
    # Alter Token → in DB nachschlagen
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT u.username FROM access_tokens t
            JOIN users u ON u.id = t.user_id
            WHERE t.token = %s LIMIT 1
        """, (token_or_username,))
        row = cur.fetchone()
    conn.close()
    if row:
        return row["username"]
    raise ValueError(f"Unbekannter Token/Username: {token_or_username[:20]}...")
