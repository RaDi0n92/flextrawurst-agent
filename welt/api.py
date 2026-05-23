#!/usr/bin/env python3
"""Welt-API: FastAPI auf Port 8030."""

import json
import math as _math
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from auth import create_token, hash_password, verify_password, verify_token

DB_URI = "postgresql://dak:dakpass@localhost:5432/flextrawurst"
ERLAUBTE_EMOJIS = ["😵", "😳", "😩", "😴", "🙄", "😬", "😂", "🤐", "😃", "👍", "👎"]
SELBSTMODELLE_DIR = Path("/root/werkraum/innenleben/selbstmodelle")

app = FastAPI(title="Welt-API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def get_conn():
    conn = psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/wesen")
def alle_wesen(admin: str | None = Query(default=None)):
    is_admin = admin == "true"
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if is_admin:
                cur.execute("""
                    SELECT s.entity_id, s.display_name, s.status, s.visibility,
                           s.slot_created_at,
                           st.stimmung, st.fokus, st.version,
                           st.symbolic_image_id, st.last_reflection_time,
                           st.updated_at
                    FROM entity_slots s
                    LEFT JOIN entity_states st USING (entity_id)
                    ORDER BY s.entity_id
                """)
            else:
                cur.execute("""
                    SELECT s.entity_id, s.display_name, s.status,
                           s.slot_created_at,
                           st.stimmung, st.fokus, st.version,
                           st.symbolic_image_id, st.last_reflection_time,
                           st.updated_at
                    FROM entity_slots s
                    LEFT JOIN entity_states st USING (entity_id)
                    WHERE s.visibility = 'public'
                    ORDER BY s.entity_id
                """)
            rows = cur.fetchall()
        return {"wesen": [dict(r) for r in rows], "count": len(rows)}
    finally:
        conn.close()


@app.get("/wesen/{entity_id}")
def ein_wesen(entity_id: str, admin: str | None = Query(default=None)):
    is_admin = admin == "true"
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if is_admin:
                cur.execute("""
                    SELECT s.*, st.*
                    FROM entity_slots s
                    LEFT JOIN entity_states st USING (entity_id)
                    WHERE s.entity_id = %s
                """, (entity_id,))
            else:
                cur.execute("""
                    SELECT s.entity_id, s.display_name, s.status,
                           s.slot_created_at,
                           st.stimmung, st.fokus, st.version,
                           st.symbolic_image_id, st.last_reflection_time,
                           st.updated_at
                    FROM entity_slots s
                    LEFT JOIN entity_states st USING (entity_id)
                    WHERE s.entity_id = %s AND s.visibility = 'public'
                """, (entity_id,))
            row = cur.fetchone()
        if row is None:
            return JSONResponse(status_code=404, content={"detail": "nicht gefunden"})
        return dict(row)
    finally:
        conn.close()


@app.get("/events")
def events(
    limit: int = Query(default=50, le=200),
    actor_id: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    admin: str | None = Query(default=None),
):
    is_admin = admin == "true"
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            conditions = []
            params: list[Any] = []

            if not is_admin:
                conditions.append("visibility_layer = 'public'")

            if actor_id:
                conditions.append("actor_id = %s")
                params.append(actor_id)

            if event_type:
                conditions.append("event_type = %s")
                params.append(event_type)

            where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
            params.append(limit)

            cur.execute(f"""
                SELECT event_id, event_type, actor_type, actor_id,
                       payload, origin_type, visibility_layer, created_at
                FROM events
                {where}
                ORDER BY created_at DESC
                LIMIT %s
            """, params)

            rows = cur.fetchall()
        return {"events": [dict(r) for r in rows], "count": len(rows)}
    finally:
        conn.close()


@app.get("/welt")
def welt_uebersicht():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM entity_slots")
            wesen_count = cur.fetchone()["n"]

            cur.execute("SELECT COUNT(*) AS n FROM entity_slots WHERE status = 'eingezogen'")
            eingezogen_count = cur.fetchone()["n"]

            cur.execute("""
                SELECT event_type, actor_id, created_at
                FROM events
                ORDER BY created_at DESC
                LIMIT 1
            """)
            letzter = cur.fetchone()

        return {
            "wesen_count": wesen_count,
            "eingezogen_count": eingezogen_count,
            "letzter_event": dict(letzter) if letzter else None,
            "system_status": "aktiv",
        }
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Hilfsfunktion: JWT aus Authorization-Header auslesen
# ---------------------------------------------------------------------------

def _require_auth(authorization: str | None) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="nicht authentifiziert")
    try:
        return verify_token(authorization.removeprefix("Bearer "))
    except Exception:
        raise HTTPException(status_code=401, detail="ungültiges Token")


def _require_admin(authorization: str | None) -> dict:
    claims = _require_auth(authorization)
    if claims.get("role") != "admin":
        raise HTTPException(status_code=403, detail="nur für Admins")
    return claims


# ---------------------------------------------------------------------------
# Pydantic-Modelle
# ---------------------------------------------------------------------------

class LoginBody(BaseModel):
    username: str
    password: str


class ProfilePatch(BaseModel):
    display_name: str | None = None
    bio: str | None = None
    gedankenwelt: str | None = None
    public_tags: list | None = None
    avatar_symbol: str | None = None
    visibility: str | None = None


class AdminCreateUserBody(BaseModel):
    username: str
    password: str
    display_name: str | None = None
    role: str = "mensch"


class AdminUserPatch(BaseModel):
    display_name: str | None = None
    role: str | None = None
    is_active: bool | None = None
    meta: dict | None = None


class AdminModulePatch(BaseModel):
    module_name: str
    enabled: bool = True
    config: dict = {}


# ---------------------------------------------------------------------------
# Interne Hilfsfunktion: User anlegen (wird von /admin/users genutzt)
# ---------------------------------------------------------------------------

_DEFAULT_MODULES = {
    "mensch": ["resonanz"],
    "admin": ["resonanz", "tagebuch", "notizen", "kalender"],
}


def _create_user(cur, username: str, password: str, display_name: str | None, role: str) -> dict:
    cur.execute("SELECT id FROM human_users WHERE username = %s", (username,))
    if cur.fetchone():
        raise HTTPException(status_code=409, detail="username bereits vergeben")

    cur.execute(
        """
        INSERT INTO human_users (username, display_name, password_hash, role)
        VALUES (%s, %s, %s, %s)
        RETURNING id, username, display_name, role, created_at
        """,
        (username, display_name, hash_password(password), role),
    )
    user = dict(cur.fetchone())

    cur.execute("INSERT INTO human_profiles (user_id) VALUES (%s)", (user["id"],))

    for module in _DEFAULT_MODULES.get(role, ["resonanz"]):
        cur.execute(
            "INSERT INTO user_modules (user_id, module_name) VALUES (%s, %s)",
            (user["id"], module),
        )

    return user


# ---------------------------------------------------------------------------
# Auth-Endpunkte
# ---------------------------------------------------------------------------

@app.post("/auth/login")
def login(body: LoginBody):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, display_name, role, password_hash, is_active "
                "FROM human_users WHERE username = %s",
                (body.username,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if not row or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="falsche Zugangsdaten")
    if not row["is_active"]:
        raise HTTPException(status_code=403, detail="account deaktiviert")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE human_users SET last_seen = NOW() WHERE id = %s",
                (row["id"],),
            )
        conn.commit()
    finally:
        conn.close()

    token = create_token(str(row["id"]), row["role"])
    return {
        "token": token,
        "user": {
            "id": str(row["id"]),
            "username": row["username"],
            "display_name": row["display_name"],
            "role": row["role"],
        },
    }


# ---------------------------------------------------------------------------
# Profil-Endpunkte
# ---------------------------------------------------------------------------

@app.get("/me")
def me(authorization: str | None = Header(default=None)):
    claims = _require_auth(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT u.id, u.username, u.display_name, u.role,
                       u.created_at, u.last_seen, u.meta,
                       p.bio, p.gedankenwelt, p.public_tags,
                       p.avatar_symbol, p.visibility, p.updated_at
                FROM human_users u
                LEFT JOIN human_profiles p ON p.user_id = u.id
                WHERE u.id = %s
                """,
                (claims["user_id"],),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="user nicht gefunden")
    return dict(row)


@app.patch("/me")
def update_me(
    body: ProfilePatch,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if body.display_name is not None:
                cur.execute(
                    "UPDATE human_users SET display_name = %s WHERE id = %s",
                    (body.display_name, user_id),
                )

            profile_fields: dict = {}
            if body.bio is not None:
                profile_fields["bio"] = body.bio
            if body.gedankenwelt is not None:
                profile_fields["gedankenwelt"] = body.gedankenwelt
            if body.public_tags is not None:
                profile_fields["public_tags"] = psycopg2.extras.Json(body.public_tags)
            if body.avatar_symbol is not None:
                profile_fields["avatar_symbol"] = body.avatar_symbol
            if body.visibility is not None:
                profile_fields["visibility"] = body.visibility

            if profile_fields:
                sets = ", ".join(f"{k} = %s" for k in profile_fields)
                values = list(profile_fields.values()) + [user_id]
                cur.execute(
                    f"UPDATE human_profiles SET {sets}, updated_at = NOW() WHERE user_id = %s",
                    values,
                )
        conn.commit()
    finally:
        conn.close()

    return {"ok": True}


@app.get("/menschen/{user_id}")
def public_profile(user_id: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT u.id, u.username, u.display_name, u.role, u.created_at,
                       p.bio, p.public_tags, p.avatar_symbol
                FROM human_users u
                LEFT JOIN human_profiles p ON p.user_id = u.id
                WHERE u.id = %s AND u.is_active = true AND p.visibility = 'public'
                """,
                (user_id,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="profil nicht gefunden")
    return dict(row)


# ---------------------------------------------------------------------------
# Admin-Endpunkte
# ---------------------------------------------------------------------------

@app.post("/admin/users", status_code=201)
def admin_create_user(
    body: AdminCreateUserBody,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            user = _create_user(cur, body.username, body.password, body.display_name, body.role)
        conn.commit()
    finally:
        conn.close()
    return {"user": user}


@app.get("/admin/users")
def admin_list_users(
    search: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
    sort: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    filter_role: str | None = Query(default=None),
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)

    allowed_sort = {"created_at", "username", "display_name", "last_seen"}
    if sort not in allowed_sort:
        sort = "created_at"
    order_sql = "DESC" if order.lower() == "desc" else "ASC"

    conditions = []
    params: list[Any] = []

    if search:
        conditions.append("(u.username ILIKE %s OR u.display_name ILIKE %s)")
        params += [f"%{search}%", f"%{search}%"]

    if filter_role:
        conditions.append("u.role = %s")
        params.append(filter_role)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    params += [limit, offset]

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT u.id, u.username, u.display_name, u.role,
                       u.is_active, u.created_at, u.last_seen, u.meta,
                       p.bio, p.avatar_symbol, p.visibility,
                       COALESCE(
                           json_agg(
                               json_build_object(
                                   'module_name', m.module_name,
                                   'enabled', m.enabled,
                                   'config', m.config
                               ) ORDER BY m.module_name
                           ) FILTER (WHERE m.module_name IS NOT NULL),
                           '[]'
                       ) AS modules
                FROM human_users u
                LEFT JOIN human_profiles p ON p.user_id = u.id
                LEFT JOIN user_modules m ON m.user_id = u.id
                {where}
                GROUP BY u.id, p.user_id
                ORDER BY u.{sort} {order_sql}
                LIMIT %s OFFSET %s
            """, params)
            rows = cur.fetchall()

            cur.execute(f"""
                SELECT COUNT(*) AS n FROM human_users u {where}
            """, params[:-2] if params else [])
            total = cur.fetchone()["n"]
    finally:
        conn.close()

    return {"users": [dict(r) for r in rows], "total": total, "limit": limit, "offset": offset}


@app.patch("/admin/users/{user_id}")
def admin_patch_user(
    user_id: str,
    body: AdminUserPatch,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)

    fields: dict = {}
    if body.display_name is not None:
        fields["display_name"] = body.display_name
    if body.role is not None:
        fields["role"] = body.role
    if body.is_active is not None:
        fields["is_active"] = body.is_active
    if body.meta is not None:
        fields["meta"] = psycopg2.extras.Json(body.meta)

    if not fields:
        raise HTTPException(status_code=400, detail="nichts zu ändern")

    sets = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [user_id]

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE human_users SET {sets} WHERE id = %s RETURNING id",
                values,
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="user nicht gefunden")
        conn.commit()
    finally:
        conn.close()

    return {"ok": True}


@app.patch("/admin/modules/{user_id}")
def admin_patch_module(
    user_id: str,
    body: AdminModulePatch,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO user_modules (user_id, module_name, enabled, config)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, module_name)
                DO UPDATE SET enabled = EXCLUDED.enabled, config = EXCLUDED.config
                """,
                (user_id, body.module_name, body.enabled, psycopg2.extras.Json(body.config)),
            )
        conn.commit()
    finally:
        conn.close()

    return {"ok": True}


# ---------------------------------------------------------------------------
# Resonanz-System
# ---------------------------------------------------------------------------

class ResonanzBody(BaseModel):
    post_ref: str
    post_source: str = "flarum"
    emojis: list[str]


class SchattenkommentarBody(BaseModel):
    post_ref: str
    post_source: str = "flarum"
    content: str


class VerweilenStartBody(BaseModel):
    target_type: str
    target_id: str


class VerweilenPingBody(BaseModel):
    session_id: str
    signal: str


class VerweilenEndBody(BaseModel):
    session_id: str


class AdminGedankenBody(BaseModel):
    post_ref: str
    post_source: str = "flarum"
    entity_id: str


class AdminSchattenPatch(BaseModel):
    visible_to: list[str] | None = None
    content: str | None = None
    meta: dict | None = None


def _get_emoji_counts(cur, post_ref: str, post_source: str) -> dict:
    cur.execute(
        "SELECT emoji, count FROM resonanz_emoji_counts WHERE post_ref = %s AND post_source = %s AND count > 0",
        (post_ref, post_source),
    )
    return {r["emoji"]: r["count"] for r in cur.fetchall()}


def _update_emoji_counts(cur, post_ref: str, post_source: str, old_emojis: list, new_emojis: list):
    for emoji in old_emojis:
        cur.execute(
            """
            INSERT INTO resonanz_emoji_counts (post_ref, post_source, emoji, count)
            VALUES (%s, %s, %s, 0)
            ON CONFLICT (post_ref, post_source, emoji) DO NOTHING
            """,
            (post_ref, post_source, emoji),
        )
        cur.execute(
            "UPDATE resonanz_emoji_counts SET count = GREATEST(0, count - 1), updated_at = NOW() "
            "WHERE post_ref = %s AND post_source = %s AND emoji = %s",
            (post_ref, post_source, emoji),
        )
    for emoji in new_emojis:
        cur.execute(
            """
            INSERT INTO resonanz_emoji_counts (post_ref, post_source, emoji, count)
            VALUES (%s, %s, %s, 1)
            ON CONFLICT (post_ref, post_source, emoji)
            DO UPDATE SET count = resonanz_emoji_counts.count + 1, updated_at = NOW()
            """,
            (post_ref, post_source, emoji),
        )


@app.post("/resonanz")
def resonanz_senden(
    body: ResonanzBody,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]

    if not body.emojis:
        raise HTTPException(status_code=400, detail="min. 1 Emoji erforderlich")
    if len(body.emojis) > 3:
        raise HTTPException(status_code=400, detail="max. 3 Emojis erlaubt")
    if len(set(body.emojis)) != len(body.emojis):
        raise HTTPException(status_code=400, detail="keine Duplikate erlaubt")
    for e in body.emojis:
        if e not in ERLAUBTE_EMOJIS:
            raise HTTPException(status_code=400, detail=f"Emoji nicht erlaubt: {e}")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT emojis FROM resonanzen WHERE post_ref = %s AND post_source = %s AND user_id = %s",
                (body.post_ref, body.post_source, user_id),
            )
            existing = cur.fetchone()
            old_emojis = list(existing["emojis"]) if existing else []

            cur.execute(
                """
                INSERT INTO resonanzen (post_ref, post_source, user_id, emojis)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (post_ref, post_source, user_id)
                DO UPDATE SET emojis = EXCLUDED.emojis, updated_at = NOW()
                """,
                (body.post_ref, body.post_source, user_id, psycopg2.extras.Json(body.emojis)),
            )

            _update_emoji_counts(cur, body.post_ref, body.post_source, old_emojis, body.emojis)

            # Fürsorge +2 für Wesen des Posts
            if body.post_source == "post":
                cur.execute(
                    "SELECT autor_id, autor_type FROM ftw_posts WHERE id = %s::uuid",
                    (body.post_ref,),
                )
                post_row = cur.fetchone()
                if post_row and post_row["autor_type"] == "entity":
                    _fuersorge_hinzufuegen(cur, user_id, post_row["autor_id"], "resonanz", 2.0)

            cur.execute(
                """
                INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
                VALUES ('resonanz.gesendet', 'human', %s, %s, 'api', 'public')
                """,
                (
                    user_id,
                    psycopg2.extras.Json({
                        "post_ref": body.post_ref,
                        "post_source": body.post_source,
                        "emojis": body.emojis,
                        "previous_emojis": old_emojis,
                    }),
                ),
            )

            emoji_counts = _get_emoji_counts(cur, body.post_ref, body.post_source)
        conn.commit()
    finally:
        conn.close()

    return {"emoji_counts": emoji_counts}


@app.get("/resonanz/{post_source}/{post_ref}")
def resonanz_abrufen(
    post_source: str,
    post_ref: str,
    authorization: str | None = Header(default=None),
):
    user_id = None
    if authorization and authorization.startswith("Bearer "):
        try:
            claims = verify_token(authorization.removeprefix("Bearer "))
            user_id = claims.get("user_id")
        except Exception:
            pass

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            emoji_counts = _get_emoji_counts(cur, post_ref, post_source)

            cur.execute(
                "SELECT COUNT(*) AS n FROM schattenkommentare WHERE post_ref = %s AND post_source = %s",
                (post_ref, post_source),
            )
            sk_count = cur.fetchone()["n"]

            eigene_reaktion = None
            if user_id:
                cur.execute(
                    "SELECT emojis FROM resonanzen WHERE post_ref = %s AND post_source = %s AND user_id = %s",
                    (post_ref, post_source, user_id),
                )
                row = cur.fetchone()
                if row:
                    eigene_reaktion = list(row["emojis"])
    finally:
        conn.close()

    return {
        "post_ref": post_ref,
        "post_source": post_source,
        "emoji_counts": emoji_counts,
        "schattenkommentar_count": sk_count,
        "eigene_reaktion": eigene_reaktion,
    }


@app.get("/resonanz/user/{user_id}")
def resonanz_user(
    user_id: str,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
    sort: str = Query(default="sent_at"),
    order: str = Query(default="desc"),
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    sort_col = "sent_at" if sort not in {"sent_at", "updated_at"} else sort
    order_sql = "DESC" if order.lower() == "desc" else "ASC"

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM resonanzen WHERE user_id = %s ORDER BY {sort_col} {order_sql} LIMIT %s OFFSET %s",
                (user_id, limit, offset),
            )
            rows = cur.fetchall()
            cur.execute("SELECT COUNT(*) AS n FROM resonanzen WHERE user_id = %s", (user_id,))
            total = cur.fetchone()["n"]
    finally:
        conn.close()

    return {"reaktionen": [dict(r) for r in rows], "total": total, "limit": limit, "offset": offset}


# ---------------------------------------------------------------------------
# Schattenkommentare
# ---------------------------------------------------------------------------

@app.post("/schattenkommentar", status_code=201)
def schattenkommentar_schreiben(
    body: SchattenkommentarBody,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    role = claims.get("role", "mensch")

    if role == "admin":
        visible_to = ["admin", "entity_owner"]
    else:
        visible_to = ["admin"]

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO schattenkommentare (post_ref, post_source, author_id, content, visible_to)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, created_at
                """,
                (
                    body.post_ref, body.post_source, user_id,
                    body.content, psycopg2.extras.Json(visible_to),
                ),
            )
            row = cur.fetchone()

            # Fürsorge +4 für Wesen des Posts
            if body.post_source == "post":
                cur.execute(
                    "SELECT autor_id, autor_type FROM ftw_posts WHERE id = %s::uuid",
                    (body.post_ref,),
                )
                post_row = cur.fetchone()
                if post_row and post_row["autor_type"] == "entity":
                    _fuersorge_hinzufuegen(cur, user_id, post_row["autor_id"], "schattenkommentar", 4.0)

            cur.execute(
                """
                INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
                VALUES ('schattenkommentar.geschrieben', 'human', %s, %s, 'api', 'internal')
                """,
                (
                    user_id,
                    psycopg2.extras.Json({
                        "post_ref": body.post_ref,
                        "post_source": body.post_source,
                        "comment_id": str(row["id"]),
                    }),
                ),
            )
        conn.commit()
    finally:
        conn.close()

    return {"id": str(row["id"]), "created_at": row["created_at"].isoformat()}


@app.get("/schattenkommentare/{post_source}/{post_ref}")
def schattenkommentare_lesen(
    post_source: str,
    post_ref: str,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
    sort: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    role = claims.get("role", "mensch")
    order_sql = "DESC" if order.lower() == "desc" else "ASC"

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if role == "admin":
                cur.execute(
                    f"SELECT * FROM schattenkommentare WHERE post_ref = %s AND post_source = %s "
                    f"ORDER BY created_at {order_sql} LIMIT %s OFFSET %s",
                    (post_ref, post_source, limit, offset),
                )
            else:
                cur.execute(
                    f"SELECT * FROM schattenkommentare WHERE post_ref = %s AND post_source = %s "
                    f"AND visible_to @> '[\"admin\"]'::jsonb AND author_id = %s "
                    f"ORDER BY created_at {order_sql} LIMIT %s OFFSET %s",
                    (post_ref, post_source, claims["user_id"], limit, offset),
                )
            rows = cur.fetchall()
    finally:
        conn.close()

    return {"kommentare": [dict(r) for r in rows], "count": len(rows)}


@app.patch("/admin/schattenkommentare/{comment_id}")
def admin_schattenkommentar_patch(
    comment_id: str,
    body: AdminSchattenPatch,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)

    fields: dict = {}
    if body.visible_to is not None:
        fields["visible_to"] = psycopg2.extras.Json(body.visible_to)
    if body.content is not None:
        fields["content"] = body.content
    if body.meta is not None:
        fields["meta"] = psycopg2.extras.Json(body.meta)

    if not fields:
        raise HTTPException(status_code=400, detail="nichts zu ändern")

    sets = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [comment_id]

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE schattenkommentare SET {sets} WHERE id = %s RETURNING id",
                values,
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="nicht gefunden")
        conn.commit()
    finally:
        conn.close()

    return {"ok": True}


# ---------------------------------------------------------------------------
# Verweilen
# ---------------------------------------------------------------------------

@app.post("/verweilen/start", status_code=201)
def verweilen_start(
    body: VerweilenStartBody,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO verweilen (user_id, target_type, target_id)
                VALUES (%s, %s, %s)
                RETURNING id, started_at
                """,
                (user_id, body.target_type, body.target_id),
            )
            row = cur.fetchone()
        conn.commit()
    finally:
        conn.close()

    return {"session_id": str(row["id"]), "started_at": row["started_at"].isoformat()}


@app.post("/verweilen/ping")
def verweilen_ping(
    body: VerweilenPingBody,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]

    allowed_signals = {"scroll", "click", "focus"}
    if body.signal not in allowed_signals:
        raise HTTPException(status_code=400, detail=f"unbekanntes Signal: {body.signal}")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, interaction_signals FROM verweilen WHERE id = %s AND user_id = %s AND ended_at IS NULL",
                (body.session_id, user_id),
            )
            row = cur.fetchone()
            if not row:
                return JSONResponse(status_code=404, content={"error": "session nicht gefunden"})

            signals = list(row["interaction_signals"])
            signals.append({"signal": body.signal, "ts": datetime.now(timezone.utc).isoformat()})

            cur.execute(
                "UPDATE verweilen SET interaction_signals = %s WHERE id = %s",
                (psycopg2.extras.Json(signals), body.session_id),
            )
        conn.commit()
    finally:
        conn.close()

    return {"ok": True}


@app.post("/verweilen/end")
def verweilen_end(
    body: VerweilenEndBody,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, started_at, interaction_signals, target_type, target_id "
                "FROM verweilen WHERE id = %s AND user_id = %s AND ended_at IS NULL",
                (body.session_id, user_id),
            )
            row = cur.fetchone()
            if not row:
                return JSONResponse(status_code=404, content={"error": "session nicht gefunden"})

            now = datetime.now(timezone.utc)
            duration = int((now - row["started_at"].replace(tzinfo=timezone.utc)).total_seconds())
            signals = list(row["interaction_signals"])
            is_valid = len(signals) > 0

            cur.execute(
                """
                UPDATE verweilen SET ended_at = %s, duration_seconds = %s, is_valid = %s
                WHERE id = %s
                """,
                (now, duration, is_valid, body.session_id),
            )

            if is_valid:
                # Fürsorge: +1 pro 30s, max 5 Punkte
                if row["target_type"] == "entity" and row["target_id"]:
                    verweilen_punkte = min(5.0, _math.floor(duration / 30) * 1.0)
                    if verweilen_punkte > 0:
                        _fuersorge_hinzufuegen(cur, user_id, row["target_id"], "verweilen", verweilen_punkte)

                cur.execute(
                    """
                    INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
                    VALUES ('verweilen.beendet', 'human', %s, %s, 'api', 'internal')
                    """,
                    (
                        user_id,
                        psycopg2.extras.Json({
                            "target_type": row["target_type"],
                            "target_id": row["target_id"],
                            "duration_seconds": duration,
                            "signal_count": len(signals),
                        }),
                    ),
                )
        conn.commit()
    finally:
        conn.close()

    return {"ok": True, "duration_seconds": duration, "is_valid": is_valid}


@app.get("/admin/verweilen")
def admin_verweilen(
    filter_target_type: str | None = Query(default=None),
    filter_valid: bool | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)

    conditions = []
    params: list[Any] = []

    if filter_target_type:
        conditions.append("target_type = %s")
        params.append(filter_target_type)
    if filter_valid is not None:
        conditions.append("is_valid = %s")
        params.append(filter_valid)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    params += [limit, offset]

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM verweilen {where} ORDER BY started_at DESC LIMIT %s OFFSET %s",
                params,
            )
            rows = cur.fetchall()
            cur.execute(f"SELECT COUNT(*) AS n FROM verweilen {where}", params[:-2] if params[:-2] else [])
            total = cur.fetchone()["n"]
    finally:
        conn.close()

    return {"sessions": [dict(r) for r in rows], "total": total, "limit": limit, "offset": offset}


# ---------------------------------------------------------------------------
# Wesen-Gedanken
# ---------------------------------------------------------------------------

def _load_selbstmodell(entity_id: str) -> dict | None:
    path = SELBSTMODELLE_DIR / f"self_model_{entity_id}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


@app.get("/wesen/{entity_id}/gedanken/aktuell")
def wesen_gedanken_aktuell(
    entity_id: str,
    authorization: str | None = Header(default=None),
):
    role = None
    has_modul = False
    if authorization and authorization.startswith("Bearer "):
        try:
            claims = verify_token(authorization.removeprefix("Bearer "))
            role = claims.get("role")
            user_id = claims.get("user_id")
            if user_id:
                conn = get_conn()
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT enabled FROM user_modules WHERE user_id = %s AND module_name = 'gedankentiefe'",
                            (user_id,),
                        )
                        m = cur.fetchone()
                        has_modul = bool(m and m["enabled"])
                finally:
                    conn.close()
        except Exception:
            pass

    modell = _load_selbstmodell(entity_id)
    if modell is None:
        raise HTTPException(status_code=404, detail="Selbstmodell nicht gefunden")

    state = modell.get("current_state", {})

    if role == "admin":
        return modell

    if has_modul:
        return modell

    return {"stimmung": state.get("stimmung"), "fokus": state.get("fokus")}


@app.get("/wesen/gedanken/{post_source}/{post_ref}")
def wesen_gedanken_post(
    post_source: str,
    post_ref: str,
    authorization: str | None = Header(default=None),
):
    role = None
    has_modul = False
    if authorization and authorization.startswith("Bearer "):
        try:
            claims = verify_token(authorization.removeprefix("Bearer "))
            role = claims.get("role")
            user_id = claims.get("user_id")
            if user_id:
                conn = get_conn()
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT enabled FROM user_modules WHERE user_id = %s AND module_name = 'gedankentiefe'",
                            (user_id,),
                        )
                        m = cur.fetchone()
                        has_modul = bool(m and m["enabled"])
                finally:
                    conn.close()
        except Exception:
            pass

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM wesen_gedanken WHERE post_ref = %s AND post_source = %s",
                (post_ref, post_source),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    result = []
    for r in rows:
        d = dict(r)
        if role == "admin":
            result.append(d)
        elif has_modul:
            result.append({
                "entity_id": d["entity_id"],
                "stimmung_bei_erstellung": d["stimmung_bei_erstellung"],
                "fokus_bei_erstellung": d["fokus_bei_erstellung"],
                "selbstmodell_snapshot": d["selbstmodell_snapshot"],
                "access_level": d["access_level"],
                "created_at": d["created_at"],
            })
        else:
            result.append({
                "entity_id": d["entity_id"],
                "stimmung_bei_erstellung": d["stimmung_bei_erstellung"],
                "fokus_bei_erstellung": d["fokus_bei_erstellung"],
            })

    return {"gedanken": result, "count": len(result)}


@app.post("/admin/wesen/gedanken", status_code=201)
def admin_wesen_gedanken_erstellen(
    body: AdminGedankenBody,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)

    modell = _load_selbstmodell(body.entity_id)
    if modell is None:
        raise HTTPException(status_code=404, detail="Selbstmodell nicht gefunden")

    state = modell.get("current_state", {})
    stimmung = state.get("stimmung")
    fokus = state.get("fokus")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO wesen_gedanken
                    (post_ref, post_source, entity_id, stimmung_bei_erstellung,
                     fokus_bei_erstellung, selbstmodell_snapshot)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (post_ref, post_source, entity_id)
                DO UPDATE SET
                    stimmung_bei_erstellung = EXCLUDED.stimmung_bei_erstellung,
                    fokus_bei_erstellung = EXCLUDED.fokus_bei_erstellung,
                    selbstmodell_snapshot = EXCLUDED.selbstmodell_snapshot
                RETURNING id, created_at
                """,
                (
                    body.post_ref, body.post_source, body.entity_id,
                    stimmung, fokus, psycopg2.extras.Json(modell),
                ),
            )
            row = cur.fetchone()
        conn.commit()
    finally:
        conn.close()

    return {"id": str(row["id"]), "created_at": row["created_at"].isoformat()}


# ---------------------------------------------------------------------------
# Pydantic-Modelle: Weltstruktur + Splitter
# ---------------------------------------------------------------------------

class RaumCreate(BaseModel):
    name: str
    slug: str
    beschreibung: str | None = None
    farbe: str | None = None
    status: str = "aktiv"
    sichtbarkeit: str = "public"
    position_order: int = 0


class RaumPatch(BaseModel):
    name: str | None = None
    beschreibung: str | None = None
    farbe: str | None = None
    status: str | None = None
    sichtbarkeit: str | None = None
    position_order: int | None = None
    meta: dict | None = None


class ThemaCreate(BaseModel):
    raum_id: str
    name: str
    slug: str
    beschreibung: str | None = None
    status: str = "aktiv"
    inkubations_grund: str | None = None
    sichtbarkeit: str = "public"


class ThemaPatch(BaseModel):
    name: str | None = None
    beschreibung: str | None = None
    status: str | None = None
    inkubations_grund: str | None = None
    sichtbarkeit: str | None = None
    meta: dict | None = None


class UnterthemaCreate(BaseModel):
    thema_id: str
    name: str
    slug: str
    status: str = "aktiv"
    sichtbarkeit: str = "public"


class UnterthemaPatch(BaseModel):
    name: str | None = None
    status: str | None = None
    sichtbarkeit: str | None = None
    meta: dict | None = None


class PostCreate(BaseModel):
    autor_type: str
    autor_id: str
    content: str
    post_type: str = "diskurs"
    sichtbarkeit: str = "public"
    unterthema_id: str | None = None
    thema_id: str | None = None
    raum_id: str | None = None


class SplitterCreate(BaseModel):
    origin_type: str
    origin_id: str | None = None
    entity_id: str | None = None
    human_id: str | None = None
    essenz: str | None = None
    thematische_tags: list = []
    materialitaet: str = "sternenstaub"
    energie: float = 1.0
    pos_x: float = 0.0
    pos_y: float = 0.0
    vel_x: float = 0.0
    vel_y: float = 0.0


class SplitterPatch(BaseModel):
    energie: float | None = None
    status: str | None = None
    pos_x: float | None = None
    pos_y: float | None = None
    vel_x: float | None = None
    vel_y: float | None = None
    herkunft_sichtbar: bool | None = None
    meta: dict | None = None


# ---------------------------------------------------------------------------
# Weltstruktur: Lese-Endpunkte
# ---------------------------------------------------------------------------

@app.get("/welt/struktur")
def welt_struktur(authorization: str | None = Header(default=None)):
    is_admin = False
    try:
        if authorization:
            claims = verify_token(authorization.removeprefix("Bearer "))
            is_admin = claims.get("role") == "admin"
    except Exception:
        pass

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            sicht_filter = "" if is_admin else "WHERE r.sichtbarkeit = 'public'"
            cur.execute(f"""
                SELECT r.id, r.name, r.slug, r.beschreibung, r.farbe,
                       r.status, r.sichtbarkeit, r.position_order, r.created_at
                FROM raeume r
                {sicht_filter}
                ORDER BY r.position_order, r.name
            """)
            raeume = [dict(r) for r in cur.fetchall()]
            # Keyed by raw UUID for DB lookups; stringify IDs for JSON output
            raum_map = {r["id"]: r for r in raeume}
            for r in raeume:
                r["themen"] = []
                r["id"] = str(r["id"])
                if r.get("created_at"):
                    r["created_at"] = r["created_at"].isoformat()

            if raum_map:
                cur.execute("""
                    SELECT t.id, t.raum_id, t.name, t.slug, t.beschreibung,
                           t.status, t.sichtbarkeit, t.resonanz_gewicht, t.created_at
                    FROM themen t
                    WHERE t.raum_id = ANY(%s::uuid[])
                    ORDER BY t.name
                """, (list(raum_map.keys()),))
                themen = [dict(t) for t in cur.fetchall()]
                thema_map = {}
                for t in themen:
                    raum = raum_map.get(t["raum_id"])
                    t["id"] = str(t["id"])
                    t["raum_id"] = str(t["raum_id"])
                    if t.get("created_at"):
                        t["created_at"] = t["created_at"].isoformat()
                    t["unterthemen"] = []
                    thema_map[t["id"]] = t
                    if raum:
                        raum["themen"].append(t)

                if thema_map:
                    cur.execute("""
                        SELECT id, thema_id, name, slug, status, sichtbarkeit, created_at
                        FROM unterthemen
                        WHERE thema_id = ANY(%s::uuid[])
                        ORDER BY name
                    """, (list(thema_map.keys()),))
                    for u in cur.fetchall():
                        u = dict(u)
                        u["id"] = str(u["id"])
                        tid = str(u["thema_id"])
                        u["thema_id"] = tid
                        if u.get("created_at"):
                            u["created_at"] = u["created_at"].isoformat()
                        thema = thema_map.get(tid)
                        if thema:
                            thema["unterthemen"].append(u)

        return {"raeume": raeume}
    finally:
        conn.close()


@app.get("/welt/raeume")
def welt_raeume(
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
    sort: str = Query(default="position_order"),
    order: str = Query(default="asc"),
):
    allowed_sort = {"position_order", "name", "created_at", "status"}
    if sort not in allowed_sort:
        sort = "position_order"
    order_sql = "DESC" if order.lower() == "desc" else "ASC"

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            conditions = ["sichtbarkeit = 'public'"]
            params: list = []
            if search:
                conditions.append("(name ILIKE %s OR beschreibung ILIKE %s)")
                params += [f"%{search}%", f"%{search}%"]
            if status:
                conditions.append("status = %s")
                params.append(status)
            where = "WHERE " + " AND ".join(conditions)
            cur.execute(
                f"SELECT * FROM raeume {where} ORDER BY {sort} {order_sql} LIMIT %s OFFSET %s",
                params + [limit, offset],
            )
            rows = [dict(r) for r in cur.fetchall()]
            for r in rows:
                r["id"] = str(r["id"])
                if r.get("created_at"):
                    r["created_at"] = r["created_at"].isoformat()
        return {"raeume": rows, "count": len(rows), "offset": offset}
    finally:
        conn.close()


@app.get("/welt/raeume/{slug}/themen")
def raum_themen(
    slug: str,
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM raeume WHERE slug = %s AND sichtbarkeit = 'public'", (slug,))
            raum = cur.fetchone()
            if not raum:
                raise HTTPException(status_code=404, detail="Raum nicht gefunden")
            raum_id = raum["id"]

            conditions = ["raum_id = %s", "sichtbarkeit = 'public'"]
            params: list = [raum_id]
            if search:
                conditions.append("name ILIKE %s")
                params.append(f"%{search}%")
            if status:
                conditions.append("status = %s")
                params.append(status)
            where = "WHERE " + " AND ".join(conditions)
            cur.execute(
                f"SELECT * FROM themen {where} ORDER BY name LIMIT %s OFFSET %s",
                params + [limit, offset],
            )
            rows = [dict(r) for r in cur.fetchall()]
            for r in rows:
                r["id"] = str(r["id"])
                r["raum_id"] = str(r["raum_id"])
                if r.get("created_at"):
                    r["created_at"] = r["created_at"].isoformat()
                if r.get("updated_at"):
                    r["updated_at"] = r["updated_at"].isoformat()
        return {"themen": rows, "count": len(rows)}
    finally:
        conn.close()


@app.get("/welt/themen/{thema_id}/unterthemen")
def thema_unterthemen(
    thema_id: str,
    search: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            conditions = ["thema_id = %s", "sichtbarkeit = 'public'"]
            params: list = [thema_id]
            if search:
                conditions.append("name ILIKE %s")
                params.append(f"%{search}%")
            where = "WHERE " + " AND ".join(conditions)
            cur.execute(
                f"SELECT * FROM unterthemen {where} ORDER BY name LIMIT %s OFFSET %s",
                params + [limit, offset],
            )
            rows = [dict(r) for r in cur.fetchall()]
            for r in rows:
                r["id"] = str(r["id"])
                r["thema_id"] = str(r["thema_id"])
                if r.get("created_at"):
                    r["created_at"] = r["created_at"].isoformat()
        return {"unterthemen": rows, "count": len(rows)}
    finally:
        conn.close()


@app.get("/welt/posts")
def welt_posts(
    autor_id: str | None = Query(default=None),
    raum_id: str | None = Query(default=None),
    thema_id: str | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
    sort: str = Query(default="created_at"),
    order: str = Query(default="desc"),
):
    allowed_sort = {"created_at", "updated_at", "autor_id"}
    if sort not in allowed_sort:
        sort = "created_at"
    order_sql = "DESC" if order.lower() == "desc" else "ASC"

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            conditions = ["sichtbarkeit = 'public'"]
            params: list = []
            if autor_id:
                conditions.append("autor_id = %s")
                params.append(autor_id)
            if raum_id:
                conditions.append("raum_id = %s")
                params.append(raum_id)
            if thema_id:
                conditions.append("thema_id = %s")
                params.append(thema_id)
            if search:
                conditions.append("content ILIKE %s")
                params.append(f"%{search}%")
            where = "WHERE " + " AND ".join(conditions)
            cur.execute(
                f"SELECT id, raum_id, thema_id, unterthema_id, autor_type, autor_id, "
                f"post_type, content, sichtbarkeit, stimmung_bei_erstellung, "
                f"fokus_bei_erstellung, splitter_erzeugt, created_at, updated_at "
                f"FROM ftw_posts {where} ORDER BY {sort} {order_sql} LIMIT %s OFFSET %s",
                params + [limit, offset],
            )
            rows = [dict(r) for r in cur.fetchall()]
            for r in rows:
                for k in ("id", "raum_id", "thema_id", "unterthema_id"):
                    if r.get(k):
                        r[k] = str(r[k])
                for k in ("created_at", "updated_at"):
                    if r.get(k):
                        r[k] = r[k].isoformat()
        return {"posts": rows, "count": len(rows), "offset": offset}
    finally:
        conn.close()


@app.get("/welt/posts/{post_id}")
def welt_post_detail(
    post_id: str,
    authorization: str | None = Header(default=None),
):
    is_admin = False
    hat_gedankentiefe = False
    try:
        if authorization:
            claims = verify_token(authorization.removeprefix("Bearer "))
            is_admin = claims.get("role") == "admin"
            if not is_admin:
                conn_check = get_conn()
                try:
                    with conn_check.cursor() as cur:
                        cur.execute(
                            "SELECT 1 FROM user_modules WHERE user_id = %s AND module_name = 'gedankentiefe' AND enabled = true",
                            (claims.get("user_id"),),
                        )
                        hat_gedankentiefe = cur.fetchone() is not None
                finally:
                    conn_check.close()
    except Exception:
        pass

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ftw_posts WHERE id = %s", (post_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Post nicht gefunden")
            post = dict(row)
            if post.get("sichtbarkeit") != "public" and not is_admin:
                raise HTTPException(status_code=403, detail="nicht öffentlich")
            for k in ("id", "raum_id", "thema_id", "unterthema_id"):
                if post.get(k):
                    post[k] = str(post[k])
            for k in ("created_at", "updated_at"):
                if post.get(k):
                    post[k] = post[k].isoformat()
            if not is_admin and not hat_gedankentiefe:
                post.pop("selbstmodell_snapshot", None)
        return post
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Admin: Weltstruktur
# ---------------------------------------------------------------------------

@app.post("/admin/raeume")
def admin_raum_erstellen(
    body: RaumCreate,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO raeume (name, slug, beschreibung, farbe, status, sichtbarkeit, position_order)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id, created_at""",
                (body.name, body.slug, body.beschreibung, body.farbe,
                 body.status, body.sichtbarkeit, body.position_order),
            )
            row = cur.fetchone()
        conn.commit()
    finally:
        conn.close()
    return {"id": str(row["id"]), "created_at": row["created_at"].isoformat()}


@app.patch("/admin/raeume/{raum_id}")
def admin_raum_patch(
    raum_id: str,
    body: RaumPatch,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="nichts zu ändern")
    set_parts = [f"{k} = %s" for k in updates]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE raeume SET {', '.join(set_parts)} WHERE id = %s RETURNING id",
                list(updates.values()) + [raum_id],
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Raum nicht gefunden")
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


@app.post("/admin/themen")
def admin_thema_erstellen(
    body: ThemaCreate,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO themen (raum_id, name, slug, beschreibung, status, inkubations_grund, sichtbarkeit)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id, created_at""",
                (body.raum_id, body.name, body.slug, body.beschreibung,
                 body.status, body.inkubations_grund, body.sichtbarkeit),
            )
            row = cur.fetchone()
        conn.commit()
    finally:
        conn.close()
    return {"id": str(row["id"]), "created_at": row["created_at"].isoformat()}


@app.patch("/admin/themen/{thema_id}")
def admin_thema_patch(
    thema_id: str,
    body: ThemaPatch,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="nichts zu ändern")
    updates["updated_at"] = datetime.now(timezone.utc)
    set_parts = [f"{k} = %s" for k in updates]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE themen SET {', '.join(set_parts)} WHERE id = %s RETURNING id",
                list(updates.values()) + [thema_id],
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Thema nicht gefunden")
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


@app.post("/admin/unterthemen")
def admin_unterthema_erstellen(
    body: UnterthemaCreate,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO unterthemen (thema_id, name, slug, status, sichtbarkeit)
                   VALUES (%s, %s, %s, %s, %s) RETURNING id, created_at""",
                (body.thema_id, body.name, body.slug, body.status, body.sichtbarkeit),
            )
            row = cur.fetchone()
        conn.commit()
    finally:
        conn.close()
    return {"id": str(row["id"]), "created_at": row["created_at"].isoformat()}


@app.patch("/admin/unterthemen/{unterthema_id}")
def admin_unterthema_patch(
    unterthema_id: str,
    body: UnterthemaPatch,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="nichts zu ändern")
    set_parts = [f"{k} = %s" for k in updates]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE unterthemen SET {', '.join(set_parts)} WHERE id = %s RETURNING id",
                list(updates.values()) + [unterthema_id],
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Unterthema nicht gefunden")
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


@app.post("/admin/posts")
def admin_post_erstellen(
    body: PostCreate,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)

    stimmung = None
    fokus = None
    snapshot = None
    if body.autor_type == "entity":
        modell = _load_selbstmodell(body.autor_id)
        if modell:
            state = modell.get("current_state", {})
            stimmung = state.get("stimmung")
            fokus = state.get("fokus")
            snapshot = modell

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO ftw_posts
                   (autor_type, autor_id, content, post_type, sichtbarkeit,
                    unterthema_id, thema_id, raum_id,
                    stimmung_bei_erstellung, fokus_bei_erstellung, selbstmodell_snapshot)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING id, created_at""",
                (body.autor_type, body.autor_id, body.content, body.post_type,
                 body.sichtbarkeit,
                 body.unterthema_id or None, body.thema_id or None, body.raum_id or None,
                 stimmung, fokus,
                 psycopg2.extras.Json(snapshot) if snapshot else None),
            )
            row = cur.fetchone()
            post_id = str(row["id"])

            splitter_id = None
            if len(body.content) > 50:
                cur.execute(
                    """INSERT INTO splitter
                       (origin_type, origin_id, entity_id, essenz,
                        thematische_tags, materialitaet, energie,
                        pos_x, pos_y, vel_x, vel_y)
                       VALUES ('ftw_post', %s, %s, %s, %s, 'sternenstaub', 1.0,
                               (random()*800-400), (random()*600-300),
                               (random()-0.5), (random()-0.5))
                       RETURNING id""",
                    (post_id, body.autor_id,
                     body.content[:120],
                     psycopg2.extras.Json([])),
                )
                splitter_id = str(cur.fetchone()["id"])
                cur.execute(
                    "UPDATE ftw_posts SET splitter_erzeugt = true WHERE id = %s", (post_id,)
                )
                cur.execute(
                    """INSERT INTO events (event_type, actor_type, actor_id, payload, visibility_layer)
                       VALUES ('post.erstellt', %s, %s, %s, 'internal')""",
                    (body.autor_type, body.autor_id,
                     psycopg2.extras.Json({"post_id": post_id, "splitter_id": splitter_id})),
                )
        conn.commit()
    finally:
        conn.close()

    return {
        "id": post_id,
        "created_at": row["created_at"].isoformat(),
        "splitter_id": splitter_id,
        "stimmung": stimmung,
    }


# ---------------------------------------------------------------------------
# Zwischenraum / Splitter
# ---------------------------------------------------------------------------

@app.get("/zwischenraum/splitter")
def splitter_liste(
    status: str | None = Query(default=None),
    materialitaet: str | None = Query(default=None),
    entity_id: str | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=200, le=500),
    offset: int = Query(default=0),
):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            conditions = ["status != 'verblasst'"]
            params: list = []
            if status:
                conditions.clear()
                conditions.append("status = %s")
                params.append(status)
            if materialitaet:
                conditions.append("materialitaet = %s")
                params.append(materialitaet)
            if entity_id:
                conditions.append("entity_id = %s")
                params.append(entity_id)
            if search:
                conditions.append("essenz ILIKE %s")
                params.append(f"%{search}%")
            where = "WHERE " + " AND ".join(conditions)
            cur.execute(
                f"""SELECT s.id, s.origin_type, s.origin_id, s.entity_id, s.human_id,
                           s.herkunft_sichtbar, s.essenz, s.thematische_tags,
                           s.materialitaet, s.energie, s.verbindungen, s.abstossungen,
                           s.pos_x, s.pos_y, s.vel_x, s.vel_y, s.status,
                           s.letzter_kontakt, s.created_at, s.aufnahmen,
                           hu.username AS human_username
                    FROM splitter s
                    LEFT JOIN human_users hu ON hu.id = s.human_id
                    {where}
                    ORDER BY s.energie DESC LIMIT %s OFFSET %s""",
                params + [limit, offset],
            )
            rows = [dict(r) for r in cur.fetchall()]
            aktiv = 0
            geisterreste = 0
            for r in rows:
                r["id"] = str(r["id"])
                if r.get("human_id"):
                    r["human_id"] = str(r["human_id"])
                if r.get("letzter_kontakt"):
                    r["letzter_kontakt"] = r["letzter_kontakt"].isoformat()
                if r.get("created_at"):
                    r["created_at"] = r["created_at"].isoformat()
                if r["status"] == "aktiv":
                    aktiv += 1
                elif r["status"] == "geisterrest":
                    geisterreste += 1
                # Herkunft-Mapping: DB-Felder → Frontend-Felder
                ot = r.get("origin_type", "")
                hm_id = r.get("human_id")
                en_id = r.get("entity_id")
                sichtbar = r.get("herkunft_sichtbar", True)
                username = r.get("human_username")
                if hm_id:
                    r["herkunft"] = "mensch"
                    r["quelle_id"] = username or str(hm_id)
                elif en_id:
                    r["herkunft"] = "entitaet"
                    r["quelle_id"] = en_id
                else:
                    r["herkunft"] = ot or "unbekannt"
                    r["quelle_id"] = None
                r["quelle_sichtbar"] = sichtbar
                essenz = r.get("essenz") or ""
                r["inhalt_kurz"] = essenz[:100] + ("…" if len(essenz) > 100 else "")
                r["inhalt_voll"] = essenz
        return {
            "splitter": rows,
            "count": len(rows),
            "aktiv": aktiv,
            "geisterreste": geisterreste,
            "theater_modus": True,
        }
    finally:
        conn.close()


@app.get("/zwischenraum/splitter/{splitter_id}")
def splitter_detail(
    splitter_id: str,
    authorization: str | None = Header(default=None),
):
    is_admin = False
    try:
        if authorization:
            claims = verify_token(authorization.removeprefix("Bearer "))
            is_admin = claims.get("role") == "admin"
    except Exception:
        pass

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM splitter WHERE id = %s", (splitter_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Splitter nicht gefunden")
            s = dict(row)
            s["id"] = str(s["id"])
            if s.get("human_id"):
                s["human_id"] = str(s["human_id"])
            for k in ("letzter_kontakt", "created_at"):
                if s.get(k):
                    s[k] = s[k].isoformat()
            if not s.get("herkunft_sichtbar") and not is_admin:
                s.pop("origin_id", None)
                s.pop("human_id", None)
                s.pop("entity_id", None)
        return s
    finally:
        conn.close()


@app.get("/zwischenraum/splitter/{splitter_id}/spur")
def splitter_spur(splitter_id: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT s.*, hu.username AS human_username
                   FROM splitter s
                   LEFT JOIN human_users hu ON hu.id = s.human_id
                   WHERE s.id = %s""",
                (splitter_id,),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Splitter nicht gefunden")
            s = dict(row)

            spur: dict = {
                "splitter_id": str(s["id"]),
                "origin_type": s.get("origin_type"),
                "herkunft": None,
                "akteur": None,
                "event": None,
                "quelle": None,
            }

            # Akteur bestimmen — Trace zeigt immer alles, herkunft_sichtbar ignoriert
            hm_id = s.get("human_id")
            en_id = s.get("entity_id")
            username = s.get("human_username")
            if hm_id:
                spur["herkunft"] = "mensch"
                spur["akteur"] = {"typ": "mensch", "id": str(hm_id), "username": username or str(hm_id)}
            elif en_id:
                spur["herkunft"] = "entitaet"
                spur["akteur"] = {"typ": "entitaet", "id": en_id}
            else:
                spur["herkunft"] = s.get("origin_type", "unbekannt")

            # Event-Details wenn origin_type = "event"
            origin_id = s.get("origin_id")
            if s.get("origin_type") == "event" and origin_id:
                try:
                    cur.execute(
                        "SELECT event_id, event_type, actor_type, actor_id, payload, created_at FROM events WHERE event_id = %s",
                        (origin_id,),
                    )
                    ev = cur.fetchone()
                    if ev:
                        ev = dict(ev)
                        spur["event"] = {
                            "id": str(ev["event_id"]),
                            "typ": ev["event_type"],
                            "actor_type": ev["actor_type"],
                            "actor_id": ev["actor_id"],
                            "payload": ev["payload"],
                            "created_at": ev["created_at"].isoformat() if ev.get("created_at") else None,
                        }
                        # Post-Quelle für Resonanz-Events
                        p = ev.get("payload") or {}
                        post_ref = p.get("post_ref")
                        post_source = p.get("post_source", "post")
                        if ev["event_type"] == "resonanz.gesendet" and post_ref:
                            spur["event"]["aktion"] = "resonanz"
                            spur["event"]["emojis"] = p.get("emojis", [])
                            # UUID = ftw_post, Integer = Flarum
                            import re as _re
                            is_uuid = bool(_re.match(r'^[0-9a-f-]{36}$', str(post_ref)))
                            if is_uuid:
                                cur.execute(
                                    """SELECT p.id, p.content, p.autor_type, p.autor_id,
                                              p.created_at, r.name AS raum_name, t.name AS thema_name
                                       FROM ftw_posts p
                                       LEFT JOIN raeume r ON r.id = p.raum_id
                                       LEFT JOIN themen t ON t.id = p.thema_id
                                       WHERE p.id = %s::uuid""",
                                    (post_ref,),
                                )
                                post = cur.fetchone()
                                if post:
                                    post = dict(post)
                                    spur["quelle"] = {
                                        "typ": "ftw_post",
                                        "system": "flextrawurst",
                                        "id": str(post["id"]),
                                        "inhalt_kurz": (post["content"] or "")[:120],
                                        "inhalt_voll": post["content"],
                                        "autor_type": post["autor_type"],
                                        "autor_id": post["autor_id"],
                                        "raum": post.get("raum_name"),
                                        "thema": post.get("thema_name"),
                                        "created_at": post["created_at"].isoformat() if post.get("created_at") else None,
                                    }
                            else:
                                spur["quelle"] = {
                                    "typ": "flarum_post",
                                    "system": "flarum",
                                    "id": post_ref,
                                    "inhalt_kurz": None,
                                    "inhalt_voll": None,
                                }
                except Exception:
                    pass

            return spur
    finally:
        conn.close()


@app.post("/zwischenraum/splitter/{splitter_id}/einsammeln")
def splitter_einsammeln(
    splitter_id: str,
    authorization: str | None = Header(default=None),
):
    """Ein Wesen oder Mensch sammelt einen Splitter aus dem Zwischenraum ein."""
    collector_entity = None
    collector_human  = None
    try:
        if authorization:
            claims = verify_token(authorization.removeprefix("Bearer "))
            collector_entity = claims.get("sub")
            collector_human  = claims.get("human_id")
    except Exception:
        raise HTTPException(status_code=401, detail="Authentifizierung erforderlich")
    if not collector_entity:
        raise HTTPException(status_code=401, detail="Authentifizierung erforderlich")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, status, entity_id, essenz FROM splitter WHERE id = %s", (splitter_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Splitter nicht gefunden")
            s = dict(row)
            if s["status"] == "eingesammelt":
                raise HTTPException(status_code=409, detail="Splitter bereits eingesammelt")
            if s["status"] == "verblasst":
                raise HTTPException(status_code=410, detail="Splitter verblasst — nicht mehr greifbar")

            new_meta = {
                "eingesammelt_von": collector_entity,
                "eingesammelt_am": datetime.utcnow().isoformat(),
            }
            cur.execute(
                "UPDATE splitter SET status = 'eingesammelt', meta = meta || %s WHERE id = %s",
                (psycopg2.extras.Json(new_meta), splitter_id),
            )
            cur.execute(
                """INSERT INTO events (event_type, entity_id, payload)
                   VALUES ('splitter.eingesammelt', %s, %s)""",
                (collector_entity, psycopg2.extras.Json({
                    "splitter_id": splitter_id,
                    "essenz": s.get("essenz", "")[:100],
                    "ursprung": s.get("entity_id"),
                })),
            )
        conn.commit()
        return {"ok": True, "splitter_id": splitter_id, "eingesammelt_von": collector_entity}
    finally:
        conn.close()


@app.post("/zwischenraum/splitter/{splitter_id}/aufnehmen")
def splitter_aufnehmen(splitter_id: str):
    """Zählt wie oft ein Splitter aufgenommen wurde. Splitter bleibt im Canvas."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM splitter WHERE id = %s", (splitter_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Splitter nicht gefunden")
            cur.execute(
                "UPDATE splitter SET aufnahmen = aufnahmen + 1 WHERE id = %s RETURNING aufnahmen",
                (splitter_id,),
            )
            aufnahmen = cur.fetchone()["aufnahmen"]
            cur.execute(
                """INSERT INTO events (event_type, actor_type, payload)
                   VALUES ('splitter.aufgenommen', 'system', %s)""",
                (psycopg2.extras.Json({"splitter_id": splitter_id}),),
            )
        conn.commit()
        return {"ok": True, "splitter_id": splitter_id, "aufnahmen": aufnahmen}
    finally:
        conn.close()


@app.post("/admin/splitter")
def admin_splitter_erstellen(
    body: SplitterCreate,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO splitter
                   (origin_type, origin_id, entity_id, human_id, essenz,
                    thematische_tags, materialitaet, energie, pos_x, pos_y, vel_x, vel_y)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING id, created_at""",
                (body.origin_type, body.origin_id, body.entity_id,
                 body.human_id or None,
                 body.essenz,
                 psycopg2.extras.Json(body.thematische_tags),
                 body.materialitaet, body.energie,
                 body.pos_x, body.pos_y, body.vel_x, body.vel_y),
            )
            row = cur.fetchone()
        conn.commit()
    finally:
        conn.close()
    return {"id": str(row["id"]), "created_at": row["created_at"].isoformat()}


@app.patch("/admin/splitter/{splitter_id}")
def admin_splitter_patch(
    splitter_id: str,
    body: SplitterPatch,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="nichts zu ändern")
    if "meta" in updates:
        updates["meta"] = psycopg2.extras.Json(updates["meta"])
    set_parts = [f"{k} = %s" for k in updates]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE splitter SET {', '.join(set_parts)} WHERE id = %s RETURNING id",
                list(updates.values()) + [splitter_id],
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Splitter nicht gefunden")
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


@app.post("/admin/zwischenraum/tick")
def zwischenraum_tick(
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE splitter
                SET energie = GREATEST(0, energie - 0.01)
                WHERE letzter_kontakt < NOW() - INTERVAL '24 hours'
                  AND status != 'verblasst'
            """)
            cur.execute("""
                UPDATE splitter SET status = 'geisterrest'
                WHERE energie < 0.2 AND energie >= 0.05 AND status = 'aktiv'
            """)
            cur.execute("""
                UPDATE splitter SET status = 'verblasst'
                WHERE energie < 0.05 AND status != 'verblasst'
            """)
            cur.execute("""
                UPDATE splitter
                SET pos_x = CASE
                      WHEN ABS(pos_x + vel_x) > 500 THEN pos_x - vel_x
                      ELSE pos_x + vel_x
                    END,
                    pos_y = CASE
                      WHEN ABS(pos_y + vel_y) > 400 THEN pos_y - vel_y
                      ELSE pos_y + vel_y
                    END,
                    vel_x = CASE WHEN ABS(pos_x + vel_x) > 500 THEN -vel_x ELSE vel_x END,
                    vel_y = CASE WHEN ABS(pos_y + vel_y) > 400 THEN -vel_y ELSE vel_y END
                WHERE status != 'verblasst'
            """)
            cur.execute("""
                SELECT
                  COUNT(*) AS processed,
                  SUM(CASE WHEN status='geisterrest' THEN 1 ELSE 0 END) AS geisterreste,
                  SUM(CASE WHEN status='verblasst' THEN 1 ELSE 0 END) AS verblasst
                FROM splitter
            """)
            stats = dict(cur.fetchone())
        conn.commit()
    finally:
        conn.close()
    return {
        "processed": int(stats["processed"] or 0),
        "geisterreste": int(stats["geisterreste"] or 0),
        "verblasst": int(stats["verblasst"] or 0),
    }


# ---------------------------------------------------------------------------
# Gedankenblasenfeld + Tamagotchi
# ---------------------------------------------------------------------------

import random as _random

_ALLE_WESEN = [
    "namelessAI_1234", "namelessAI_1324", "namelessAI_1423",
    "namelessAI_2341", "namelessAI_3123", "namelessAI_4321",
]


class GedankenblasenCreate(BaseModel):
    inhalt: str
    thematische_tags: list[str] = []
    sichtbarkeit: str = "public"


class SichtbarkeitPatch(BaseModel):
    gedankenblasen_anonym: bool | None = None
    notizen_anonym: bool | None = None
    schattenkommentare_anonym: bool | None = None
    zitierbar: bool | None = None
    verweilen_tracking: bool | None = None


class AdminGedankenblasenPatch(BaseModel):
    inhalt: str | None = None
    sichtbarkeit: str | None = None
    energie: float | None = None
    status: str | None = None
    thematische_tags: list[str] | None = None


class QualityTimeEndBody(BaseModel):
    session_id: str


def _fuersorge_hinzufuegen(cur, user_id: str, entity_id: str, typ: str, punkte: float) -> None:
    cur.execute(
        "INSERT INTO wesen_fuersorge (user_id, entity_id, fuersorge_typ, punkte) VALUES (%s::uuid, %s, %s, %s)",
        (user_id, entity_id, typ, punkte),
    )
    cur.execute(
        """
        INSERT INTO wesen_entwicklung (entity_id, fuersorge_gesamt, fuersorge_heute,
                                       letzte_interaktion, vernachlaessigung_stunden, stimmungs_drift)
        VALUES (%s, %s, %s, NOW(), 0, %s)
        ON CONFLICT (entity_id) DO UPDATE SET
            fuersorge_gesamt      = LEAST(wesen_entwicklung.fuersorge_gesamt + %s, 9999),
            fuersorge_heute       = LEAST(wesen_entwicklung.fuersorge_heute + %s, 999),
            letzte_interaktion    = NOW(),
            vernachlaessigung_stunden = 0,
            stimmungs_drift       = LEAST(wesen_entwicklung.stimmungs_drift + %s * 0.01, 2.0)
        """,
        (entity_id, punkte, punkte, punkte * 0.01, punkte, punkte, punkte),
    )
    # Stufenaufstieg prüfen
    cur.execute(
        "SELECT entwicklungsstufe, fuersorge_gesamt, stufe_punkte_schwelle FROM wesen_entwicklung WHERE entity_id = %s",
        (entity_id,),
    )
    row = cur.fetchone()
    if row and row["fuersorge_gesamt"] >= row["stufe_punkte_schwelle"]:
        neue_stufe = row["entwicklungsstufe"] + 1
        neue_schwelle = row["stufe_punkte_schwelle"] * 1.5
        cur.execute(
            "UPDATE wesen_entwicklung SET entwicklungsstufe=%s, stufe_punkte_schwelle=%s WHERE entity_id=%s",
            (neue_stufe, neue_schwelle, entity_id),
        )
        cur.execute(
            """
            INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
            VALUES ('wesen.entwicklung_stufe', 'system', %s, %s, 'daemon', 'public')
            """,
            (entity_id, psycopg2.extras.Json({"stufe": neue_stufe, "punkte": float(row["fuersorge_gesamt"])})),
        )


@app.post("/gedankenblasen", status_code=201)
def gedankenblase_erstellen(
    body: GedankenblasenCreate,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Sichtbarkeits-Präferenzen laden
            cur.execute(
                "SELECT gedankenblasen_anonym FROM nutzer_sichtbarkeit WHERE user_id = %s::uuid",
                (user_id,),
            )
            sicht_row = cur.fetchone()
            herkunft_sichtbar = not (sicht_row["gedankenblasen_anonym"] if sicht_row else False)

            pos_x = _random.uniform(-400, 400)
            pos_y = _random.uniform(-300, 300)

            cur.execute(
                """
                INSERT INTO gedankenblasen
                  (user_id, inhalt, sichtbarkeit, herkunft_sichtbar, thematische_tags, pos_x, pos_y)
                VALUES (%s::uuid, %s, %s, %s, %s, %s, %s)
                RETURNING id, inhalt, pos_x, pos_y, created_at
                """,
                (user_id, body.inhalt, body.sichtbarkeit, herkunft_sichtbar,
                 psycopg2.extras.Json(body.thematische_tags), pos_x, pos_y),
            )
            blase = cur.fetchone()
            blase_id = str(blase["id"])

            # Splitter erzeugen
            cur.execute(
                """
                INSERT INTO splitter
                  (origin_type, origin_id, human_id, herkunft_sichtbar, essenz, thematische_tags,
                   materialitaet, energie, pos_x, pos_y, vel_x, vel_y)
                VALUES ('human_gedanke', %s, %s::uuid, %s, %s, %s, 'nebel', 0.6, %s, %s, %s, %s)
                """,
                (blase_id, user_id, herkunft_sichtbar,
                 body.inhalt[:120], psycopg2.extras.Json(body.thematische_tags),
                 pos_x, pos_y, _random.uniform(-0.2, 0.2), _random.uniform(-0.2, 0.2)),
            )

            # Fürsorge +3 für alle Wesen
            for eid in _ALLE_WESEN:
                _fuersorge_hinzufuegen(cur, user_id, eid, "gedankenblase", 3.0)

            cur.execute(
                """
                INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
                VALUES ('gedankenblase.erstellt', 'human', %s, %s, 'api', 'public')
                """,
                (user_id, psycopg2.extras.Json({
                    "blase_id": blase_id,
                    "sichtbarkeit": body.sichtbarkeit,
                    "tags": body.thematische_tags,
                })),
            )
        conn.commit()
    finally:
        conn.close()

    return {
        "id": blase_id,
        "inhalt": blase["inhalt"],
        "pos_x": blase["pos_x"],
        "pos_y": blase["pos_y"],
        "created_at": blase["created_at"].isoformat(),
    }


@app.get("/gedankenblasen")
def gedankenblasen_liste(
    status: str = Query(default="aktiv"),
    user_id: str | None = Query(default=None),
    search: str | None = Query(default=None),
    sort: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0),
):
    allowed_sort = {"energie", "created_at", "wesen_verwendungen"}
    sort = sort if sort in allowed_sort else "created_at"
    order_sql = "DESC" if order.lower() != "asc" else "ASC"

    conditions = ["status = %s"]
    params: list[Any] = [status]

    if user_id:
        conditions.append("user_id = %s::uuid")
        params.append(user_id)
    if search:
        conditions.append("inhalt ILIKE %s")
        params.append(f"%{search}%")

    where = " AND ".join(conditions)
    params += [limit, offset]

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT id, user_id, inhalt, sichtbarkeit, herkunft_sichtbar, "
                f"thematische_tags, energie, pos_x, pos_y, wesen_verwendungen, "
                f"status, created_at FROM gedankenblasen "
                f"WHERE {where} ORDER BY {sort} {order_sql} LIMIT %s OFFSET %s",
                params,
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    result = []
    for r in rows:
        item = dict(r)
        if not item["herkunft_sichtbar"]:
            item["user_id"] = None
        item["id"] = str(item["id"]) if item["id"] else None
        item["user_id"] = str(item["user_id"]) if item["user_id"] else None
        result.append(item)
    return {"blasen": result, "count": len(result), "offset": offset}


@app.get("/gedankenblasen/feld")
def gedankenblasen_feld():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # 40% aktuell (letzte 7 Tage), 30% alt (> 7 Tage), 30% random
            cur.execute(
                """
                (SELECT id, inhalt, pos_x, pos_y, energie, status,
                        thematische_tags, wesen_verwendungen,
                        user_id, herkunft_sichtbar, 'aktuell' AS bucket
                 FROM gedankenblasen
                 WHERE status='aktiv' AND created_at > NOW() - INTERVAL '7 days'
                 ORDER BY energie DESC LIMIT 80)
                UNION ALL
                (SELECT id, inhalt, pos_x, pos_y, energie, status,
                        thematische_tags, wesen_verwendungen,
                        user_id, herkunft_sichtbar, 'alt' AS bucket
                 FROM gedankenblasen
                 WHERE status='aktiv' AND created_at <= NOW() - INTERVAL '7 days'
                 ORDER BY RANDOM() LIMIT 60)
                UNION ALL
                (SELECT id, inhalt, pos_x, pos_y, energie, status,
                        thematische_tags, wesen_verwendungen,
                        user_id, herkunft_sichtbar, 'random' AS bucket
                 FROM gedankenblasen
                 WHERE status='aktiv'
                 ORDER BY RANDOM() LIMIT 60)
                """
            )
            rows = cur.fetchall()

            # Herkunft auflösen (display_name + avatar_symbol wenn sichtbar)
            user_ids = list({str(r["user_id"]) for r in rows if r["herkunft_sichtbar"] and r["user_id"]})
            profile_map: dict[str, dict] = {}
            if user_ids:
                cur.execute(
                    """
                    SELECT u.id::text, u.display_name,
                           COALESCE(p.avatar_symbol, '?') AS avatar_symbol
                    FROM human_users u
                    LEFT JOIN human_profiles p ON p.user_id = u.id
                    WHERE u.id = ANY(%s::uuid[])
                    """,
                    (user_ids,),
                )
                for row in cur.fetchall():
                    profile_map[row["id"]] = {
                        "display_name": row["display_name"],
                        "avatar_symbol": row["avatar_symbol"],
                    }
    finally:
        conn.close()

    seen = set()
    result = []
    for r in rows:
        rid = str(r["id"])
        if rid in seen:
            continue
        seen.add(rid)
        inhalt = r["inhalt"]
        herkunft = None
        if r["herkunft_sichtbar"] and r["user_id"]:
            herkunft = profile_map.get(str(r["user_id"]))
        result.append({
            "id": rid,
            "inhalt_kurz": inhalt[:50] + ("…" if len(inhalt) > 50 else ""),
            "inhalt": inhalt,
            "pos_x": r["pos_x"],
            "pos_y": r["pos_y"],
            "energie": r["energie"],
            "status": r["status"],
            "thematische_tags": r["thematische_tags"],
            "wesen_verwendungen": r["wesen_verwendungen"],
            "herkunft": herkunft,
        })
    return {"blasen": result, "count": len(result)}


@app.get("/gedankenblasen/{blase_id}")
def gedankenblase_detail(blase_id: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM gedankenblasen WHERE id = %s::uuid",
                (blase_id,),
            )
            blase = cur.fetchone()
            if not blase:
                raise HTTPException(status_code=404, detail="Blase nicht gefunden")

            cur.execute(
                "SELECT * FROM blase_verwendungen WHERE blase_id = %s::uuid ORDER BY created_at DESC",
                (blase_id,),
            )
            verwendungen = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

    item = dict(blase)
    item["id"] = str(item["id"]) if item["id"] else None
    item["user_id"] = str(item["user_id"]) if item["user_id"] else None
    if not item["herkunft_sichtbar"]:
        item["user_id"] = None
    for v in verwendungen:
        v["id"] = str(v["id"]) if v["id"] else None
        v["blase_id"] = str(v["blase_id"]) if v["blase_id"] else None
    return {"blase": item, "verwendungen": verwendungen}


@app.delete("/gedankenblasen/{blase_id}", status_code=200)
def gedankenblase_archivieren(
    blase_id: str,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id FROM gedankenblasen WHERE id = %s::uuid",
                (blase_id,),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Blase nicht gefunden")
            if str(row["user_id"]) != user_id and claims.get("role") != "admin":
                raise HTTPException(status_code=403, detail="nicht deine Blase")
            cur.execute(
                "UPDATE gedankenblasen SET status='archiviert', updated_at=NOW() WHERE id=%s::uuid",
                (blase_id,),
            )
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


@app.patch("/admin/gedankenblasen/{blase_id}")
def admin_gedankenblase_patch(
    blase_id: str,
    body: AdminGedankenblasenPatch,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    updates: list[str] = []
    params: list[Any] = []
    if body.inhalt is not None:
        updates.append("inhalt=%s"); params.append(body.inhalt)
    if body.sichtbarkeit is not None:
        updates.append("sichtbarkeit=%s"); params.append(body.sichtbarkeit)
    if body.energie is not None:
        updates.append("energie=%s"); params.append(body.energie)
    if body.status is not None:
        updates.append("status=%s"); params.append(body.status)
    if body.thematische_tags is not None:
        updates.append("thematische_tags=%s"); params.append(psycopg2.extras.Json(body.thematische_tags))
    if not updates:
        raise HTTPException(status_code=400, detail="nichts zu ändern")
    updates.append("updated_at=NOW()")
    params.append(blase_id)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE gedankenblasen SET {', '.join(updates)} WHERE id=%s::uuid",
                params,
            )
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


# ── Nutzer-Sichtbarkeit ────────────────────────────────────────────────────

@app.get("/me/sichtbarkeit")
def me_sichtbarkeit(authorization: str | None = Header(default=None)):
    claims = _require_auth(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM nutzer_sichtbarkeit WHERE user_id = %s::uuid",
                (claims["user_id"],),
            )
            row = cur.fetchone()
    finally:
        conn.close()
    if not row:
        return {
            "gedankenblasen_anonym": False, "notizen_anonym": True,
            "schattenkommentare_anonym": True, "zitierbar": True, "verweilen_tracking": True,
        }
    item = dict(row)
    item["user_id"] = str(item["user_id"])
    return item


@app.patch("/me/sichtbarkeit")
def me_sichtbarkeit_patch(
    body: SichtbarkeitPatch,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]

    updates: list[str] = []
    params: list[Any] = []
    for field in ["gedankenblasen_anonym", "notizen_anonym", "schattenkommentare_anonym",
                  "zitierbar", "verweilen_tracking"]:
        val = getattr(body, field)
        if val is not None:
            updates.append(f"{field}=%s"); params.append(val)
    if not updates:
        raise HTTPException(status_code=400, detail="nichts zu ändern")
    params.append(user_id)

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO nutzer_sichtbarkeit (user_id) VALUES (%s::uuid)
                ON CONFLICT (user_id) DO UPDATE SET {', '.join(updates)}
                """,
                ([user_id] + params[:-1] + [user_id])
                if not updates else params,
            )
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


# ── Tamagotchi / Fürsorge ──────────────────────────────────────────────────

@app.get("/wesen/{entity_id}/entwicklung")
def wesen_entwicklung_abrufen(
    entity_id: str,
    authorization: str | None = Header(default=None),
):
    is_admin = False
    if authorization:
        try:
            claims = verify_token(authorization.removeprefix("Bearer "))
            is_admin = claims.get("role") == "admin"
        except Exception:
            pass

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM wesen_entwicklung WHERE entity_id = %s",
                (entity_id,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Wesen nicht gefunden")

    public = {
        "entity_id": row["entity_id"],
        "entwicklungsstufe": row["entwicklungsstufe"],
        "stimmungs_drift": row["stimmungs_drift"],
        "letzte_interaktion": row["letzte_interaktion"].isoformat() if row["letzte_interaktion"] else None,
        "vernachlaessigung_stunden": row["vernachlaessigung_stunden"],
    }
    if is_admin:
        public["fuersorge_gesamt"] = row["fuersorge_gesamt"]
        public["fuersorge_heute"] = row["fuersorge_heute"]
        public["stufe_punkte_schwelle"] = row["stufe_punkte_schwelle"]
    return public


@app.post("/wesen/{entity_id}/quality_time/start", status_code=201)
def quality_time_start(
    entity_id: str,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT entity_id FROM entity_slots WHERE entity_id = %s",
                (entity_id,),
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Wesen nicht gefunden")

            session_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
                VALUES ('quality_time.gestartet', 'human', %s, %s, 'api', 'internal')
                RETURNING event_id, created_at
                """,
                (user_id, psycopg2.extras.Json({
                    "entity_id": entity_id,
                    "session_id": session_id,
                })),
            )
            ev = cur.fetchone()

            cur.execute(
                "SELECT stimmung, fokus FROM entity_states WHERE entity_id = %s ORDER BY created_at DESC LIMIT 1",
                (entity_id,),
            )
            snapshot_row = cur.fetchone()
        conn.commit()
    finally:
        conn.close()

    entity_snapshot = {}
    if snapshot_row:
        entity_snapshot = {
            "stimmung": snapshot_row.get("stimmung"),
            "fokus": snapshot_row.get("fokus"),
        }
    return {
        "session_id": session_id,
        "entity_id": entity_id,
        "started_at": ev["created_at"].isoformat(),
        "entity_snapshot": entity_snapshot,
    }


@app.post("/wesen/{entity_id}/quality_time/end")
def quality_time_end(
    entity_id: str,
    body: QualityTimeEndBody,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT event_id, created_at, payload FROM events
                WHERE event_type = 'quality_time.gestartet'
                  AND actor_id = %s
                  AND payload->>'session_id' = %s
                ORDER BY created_at DESC LIMIT 1
                """,
                (user_id, body.session_id),
            )
            start_ev = cur.fetchone()
            if not start_ev:
                raise HTTPException(status_code=404, detail="Session nicht gefunden")

            started_at = start_ev["created_at"].replace(tzinfo=timezone.utc)
            dauer = int((datetime.now(timezone.utc) - started_at).total_seconds())
            punkte = 10.0 if dauer >= 60 else 0.0

            if punkte > 0:
                _fuersorge_hinzufuegen(cur, user_id, entity_id, "quality_time", punkte)

            cur.execute(
                """
                INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
                VALUES ('quality_time.beendet', 'human', %s, %s, 'api', 'internal')
                """,
                (user_id, psycopg2.extras.Json({
                    "entity_id": entity_id,
                    "session_id": body.session_id,
                    "dauer_sekunden": dauer,
                    "punkte": punkte,
                })),
            )
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "dauer_sekunden": dauer, "punkte": punkte}


@app.get("/admin/tamagotchi/uebersicht")
def admin_tamagotchi_uebersicht(
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT entity_id, entwicklungsstufe, fuersorge_gesamt, fuersorge_heute,
                       vernachlaessigung_stunden, letzte_interaktion,
                       stimmungs_drift, stufe_punkte_schwelle
                FROM wesen_entwicklung
                ORDER BY vernachlaessigung_stunden DESC
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()
    result = []
    for r in rows:
        item = dict(r)
        if item["letzte_interaktion"]:
            item["letzte_interaktion"] = item["letzte_interaktion"].isoformat()
        result.append(item)
    return {"wesen": result}


# ── Globale Suche ─────────────────────────────────────────────────────────────

@app.get("/suche")
def suche(
    q: str = Query(min_length=2),
    kurzform: bool = Query(default=False),
    typ: str = Query(default="alle"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    authorization: str | None = Header(default=None),
):
    is_admin = False
    try:
        if authorization:
            claims = verify_token(authorization.removeprefix("Bearer "))
            is_admin = claims.get("role") == "admin"
    except Exception:
        pass

    pro_kat = 5 if kurzform else min(limit, 20)
    pat = f"%{q}%"
    result: dict[str, list] = {
        "raeume": [], "themen": [], "unterthemen": [], "wesen": [],
        "blasen": [], "splitter": [], "posts": [],
    }
    if is_admin:
        result["menschen"] = []
        result["system"] = []

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Räume
            cur.execute(
                "SELECT id::text, name, beschreibung, slug FROM raeume "
                "WHERE sichtbarkeit='public' AND (name ILIKE %s OR beschreibung ILIKE %s) LIMIT %s",
                (pat, pat, pro_kat))
            for r in cur.fetchall():
                result["raeume"].append({"id": r["id"], "name": r["name"],
                    "beschreibung": (r["beschreibung"] or "")[:120], "slug": r["slug"], "typ": "raum"})

            # Themen
            cur.execute(
                "SELECT id::text, name, beschreibung FROM themen "
                "WHERE status='aktiv' AND (name ILIKE %s OR beschreibung ILIKE %s) LIMIT %s",
                (pat, pat, pro_kat))
            for r in cur.fetchall():
                result["themen"].append({"id": r["id"], "name": r["name"],
                    "beschreibung": (r["beschreibung"] or "")[:100], "typ": "thema"})

            # Unterthemen
            cur.execute(
                "SELECT id::text, name FROM unterthemen "
                "WHERE sichtbarkeit='public' AND name ILIKE %s LIMIT %s",
                (pat, pro_kat))
            for r in cur.fetchall():
                result["unterthemen"].append({"id": r["id"], "name": r["name"], "typ": "unterthema"})

            # Posts
            cur.execute(
                "SELECT id::text, content, stimmung_bei_erstellung, autor_id FROM ftw_posts "
                "WHERE sichtbarkeit='public' AND (content ILIKE %s OR stimmung_bei_erstellung ILIKE %s) LIMIT %s",
                (pat, pat, pro_kat))
            for r in cur.fetchall():
                result["posts"].append({"id": r["id"],
                    "inhalt_kurz": (r["content"] or "")[:120],
                    "stimmung": r["stimmung_bei_erstellung"],
                    "autor_id": r["autor_id"], "typ": "post"})

            # Gedankenblasen
            cur.execute(
                "SELECT id::text, inhalt, energie, status FROM gedankenblasen "
                "WHERE status='aktiv' AND sichtbarkeit='public' AND inhalt ILIKE %s LIMIT %s",
                (pat, pro_kat))
            for r in cur.fetchall():
                result["blasen"].append({"id": r["id"],
                    "inhalt_kurz": (r["inhalt"] or "")[:100],
                    "energie": r["energie"], "typ": "blase"})

            # Splitter
            cur.execute(
                "SELECT id::text, essenz, materialitaet, energie, pos_x, pos_y FROM splitter "
                "WHERE status='aktiv' AND essenz ILIKE %s LIMIT %s",
                (pat, pro_kat))
            for r in cur.fetchall():
                result["splitter"].append({"id": r["id"],
                    "essenz": (r["essenz"] or "")[:100],
                    "materialitaet": r["materialitaet"],
                    "energie": r["energie"],
                    "pos_x": r["pos_x"], "pos_y": r["pos_y"], "typ": "splitter"})

            # Wesen (entity_slots + entity_states)
            cur.execute(
                "SELECT s.entity_id, s.display_name, t.stimmung, t.fokus "
                "FROM entity_slots s LEFT JOIN entity_states t ON t.entity_id=s.entity_id "
                "WHERE s.visibility='public' AND "
                "(s.entity_id ILIKE %s OR s.display_name ILIKE %s OR t.stimmung ILIKE %s) LIMIT %s",
                (pat, pat, pat, pro_kat))
            for r in cur.fetchall():
                result["wesen"].append({"id": r["entity_id"],
                    "display_name": r["display_name"],
                    "stimmung": r["stimmung"], "typ": "wesen"})

            if is_admin:
                # Menschen
                cur.execute(
                    "SELECT u.id::text, u.username, u.display_name, p.bio "
                    "FROM human_users u LEFT JOIN human_profiles p ON p.user_id=u.id "
                    "WHERE u.username ILIKE %s OR u.display_name ILIKE %s OR p.bio ILIKE %s LIMIT %s",
                    (pat, pat, pat, pro_kat))
                for r in cur.fetchall():
                    result["menschen"].append({"id": r["id"],
                        "username": r["username"], "display_name": r["display_name"], "typ": "mensch"})

                # Events
                cur.execute(
                    "SELECT id::text, event_type, payload FROM events "
                    "WHERE event_type ILIKE %s OR payload::text ILIKE %s ORDER BY id DESC LIMIT %s",
                    (pat, pat, pro_kat))
                for r in cur.fetchall():
                    result.setdefault("events", []).append({"id": r["id"],
                        "event_type": r["event_type"], "typ": "event"})

    finally:
        conn.close()

    gesamt = sum(len(v) for v in result.values())
    highlight_ids = {
        "blasen":   [x["id"] for x in result["blasen"]],
        "splitter": [x["id"] for x in result["splitter"]],
    }
    return {
        "q": q,
        "gesamt": gesamt,
        "kategorien": result,
        "highlight_ids": highlight_ids,
    }


# ── Gedankenwelt ──────────────────────────────────────────────────────────────

class GedankenweltCreate(BaseModel):
    inhalt: str
    typ: str = "privat"

class GedankenweltPatch(BaseModel):
    inhalt: str | None = None
    typ: str | None = None


@app.get("/me/gedankenwelt")
def me_gedankenwelt_liste(
    typ: str | None = None,
    limit: int = 50,
    offset: int = 0,
    sort: str = "created_at",
    order: str = "desc",
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    if sort not in ("created_at", "updated_at"):
        sort = "created_at"
    if order not in ("asc", "desc"):
        order = "desc"
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            where = "WHERE user_id = %s::uuid"
            params: list[Any] = [user_id]
            if typ:
                where += " AND typ = %s"
                params.append(typ)
            cur.execute(
                f"SELECT id, inhalt, typ, blase_id, created_at, updated_at "
                f"FROM gedankenwelt_eintraege {where} "
                f"ORDER BY {sort} {order} LIMIT %s OFFSET %s",
                params + [limit, offset],
            )
            rows = cur.fetchall()
            cur.execute(
                f"SELECT COUNT(*) AS n FROM gedankenwelt_eintraege {where}",
                params,
            )
            total = cur.fetchone()["n"]
    finally:
        conn.close()
    result = []
    for r in rows:
        item = dict(r)
        item["id"] = str(item["id"])
        item["blase_id"] = str(item["blase_id"]) if item["blase_id"] else None
        item["created_at"] = item["created_at"].isoformat()
        item["updated_at"] = item["updated_at"].isoformat()
        result.append(item)
    return {"eintraege": result, "total": total}


@app.post("/me/gedankenwelt", status_code=201)
def me_gedankenwelt_erstellen(
    body: GedankenweltCreate,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    if body.typ not in ("privat", "bereit"):
        raise HTTPException(status_code=400, detail="typ muss 'privat' oder 'bereit' sein")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO gedankenwelt_eintraege (user_id, inhalt, typ) "
                "VALUES (%s::uuid, %s, %s) "
                "RETURNING id, inhalt, typ, created_at",
                (user_id, body.inhalt, body.typ),
            )
            row = cur.fetchone()
        conn.commit()
    finally:
        conn.close()
    return {
        "id": str(row["id"]),
        "inhalt": row["inhalt"],
        "typ": row["typ"],
        "created_at": row["created_at"].isoformat(),
    }


@app.patch("/me/gedankenwelt/{eintrag_id}")
def me_gedankenwelt_patch(
    eintrag_id: str,
    body: GedankenweltPatch,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    updates: list[str] = []
    params: list[Any] = []
    if body.inhalt is not None:
        updates.append("inhalt=%s"); params.append(body.inhalt)
    if body.typ is not None:
        if body.typ not in ("privat", "bereit"):
            raise HTTPException(status_code=400, detail="typ muss 'privat' oder 'bereit' sein")
        updates.append("typ=%s"); params.append(body.typ)
    if not updates:
        raise HTTPException(status_code=400, detail="nichts zu ändern")
    params += [eintrag_id, user_id]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE gedankenwelt_eintraege SET {', '.join(updates)}, updated_at=NOW() "
                "WHERE id=%s::uuid AND user_id=%s::uuid AND typ != 'losgelassen' "
                "RETURNING id",
                params,
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="nicht gefunden oder bereits losgelassen")
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


@app.patch("/me/gedankenwelt/{eintrag_id}/markieren")
def me_gedankenwelt_markieren(
    eintrag_id: str,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE gedankenwelt_eintraege SET typ='bereit', updated_at=NOW() "
                "WHERE id=%s::uuid AND user_id=%s::uuid AND typ='privat' RETURNING id",
                (eintrag_id, user_id),
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="nicht gefunden oder nicht 'privat'")
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


@app.post("/me/gedankenwelt/{eintrag_id}/loslassen")
def me_gedankenwelt_loslassen(
    eintrag_id: str,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, inhalt FROM gedankenwelt_eintraege "
                "WHERE id=%s::uuid AND user_id=%s::uuid AND typ='bereit'",
                (eintrag_id, user_id),
            )
            eintrag = cur.fetchone()
            if not eintrag:
                raise HTTPException(status_code=404, detail="nicht gefunden oder nicht 'bereit'")

            cur.execute(
                "SELECT gedankenblasen_anonym FROM nutzer_sichtbarkeit WHERE user_id=%s::uuid",
                (user_id,),
            )
            sicht = cur.fetchone()
            herkunft_sichtbar = not (sicht["gedankenblasen_anonym"] if sicht else False)

            pos_x = _random.uniform(-400, 400)
            pos_y = _random.uniform(-300, 300)

            cur.execute(
                "INSERT INTO gedankenblasen "
                "(user_id, inhalt, sichtbarkeit, herkunft_sichtbar, thematische_tags, pos_x, pos_y) "
                "VALUES (%s::uuid, %s, 'public', %s, '[]'::jsonb, %s, %s) "
                "RETURNING id",
                (user_id, eintrag["inhalt"], herkunft_sichtbar, pos_x, pos_y),
            )
            blase_id = str(cur.fetchone()["id"])

            cur.execute(
                "INSERT INTO splitter "
                "(origin_type, origin_id, human_id, herkunft_sichtbar, essenz, thematische_tags, "
                "materialitaet, energie, pos_x, pos_y, vel_x, vel_y) "
                "VALUES ('human_gedanke', %s, %s::uuid, %s, %s, '[]'::jsonb, 'nebel', 0.6, %s, %s, %s, %s)",
                (blase_id, user_id, herkunft_sichtbar,
                 eintrag["inhalt"][:120], pos_x, pos_y,
                 _random.uniform(-0.2, 0.2), _random.uniform(-0.2, 0.2)),
            )

            for eid in _ALLE_WESEN:
                _fuersorge_hinzufuegen(cur, user_id, eid, "gedankenblase", 3.0)

            cur.execute(
                "UPDATE gedankenwelt_eintraege SET typ='losgelassen', blase_id=%s::uuid, updated_at=NOW() "
                "WHERE id=%s::uuid",
                (blase_id, eintrag_id),
            )

            cur.execute(
                "INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer) "
                "VALUES ('gedankenblase.losgelassen', 'human', %s, %s, 'api', 'public')",
                (user_id, psycopg2.extras.Json({"blase_id": blase_id, "eintrag_id": eintrag_id})),
            )
        conn.commit()
    finally:
        conn.close()
    return {"blase_id": blase_id, "message": "Dein Gedanke driftet jetzt."}


@app.delete("/me/gedankenwelt/{eintrag_id}", status_code=200)
def me_gedankenwelt_loeschen(
    eintrag_id: str,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM gedankenwelt_eintraege "
                "WHERE id=%s::uuid AND user_id=%s::uuid AND typ IN ('privat','bereit') "
                "RETURNING id",
                (eintrag_id, user_id),
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="nicht gefunden oder bereits losgelassen")
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


# --- Schlaf-System ---

def _zustandsaufnahme(cur, entity_id: str) -> dict:
    """Erfasst den vollständigen Zustand einer Entität beim Einschlafen."""
    zustand = {}

    # Stimmung + Fokus
    cur.execute("""
        SELECT stimmung, fokus, tendencies, core
        FROM entity_states WHERE entity_id = %s
    """, (entity_id,))
    row = cur.fetchone()
    if row:
        zustand["stimmung"] = row["stimmung"]
        zustand["fokus"] = row["fokus"]
        zustand["tendencies"] = row["tendencies"]
        zustand["core"] = row["core"]

    # Resonanzaktivität letzte 6h
    cur.execute("""
        SELECT COUNT(*) as n FROM events
        WHERE actor_id = %s
          AND event_type LIKE 'resonanz.%'
          AND created_at >= NOW() - INTERVAL '6 hours'
    """, (entity_id,))
    zustand["resonanz_6h"] = cur.fetchone()["n"]

    # Konfliktsignal: events mit 'konflikt' oder 'abstossung'
    cur.execute("""
        SELECT COUNT(*) as n FROM events
        WHERE actor_id = %s
          AND (event_type LIKE '%konflikt%' OR event_type LIKE '%abstoss%')
          AND created_at >= NOW() - INTERVAL '24 hours'
    """, (entity_id,))
    zustand["konfliktsignal_24h"] = cur.fetchone()["n"]

    # Offene Splitterfragmente des Wesens
    cur.execute("""
        SELECT COUNT(*) as n FROM splitter
        WHERE entity_id = %s AND status = 'aktiv'
    """, (entity_id,))
    zustand["offene_splitter"] = cur.fetchone()["n"]

    # Letzte eigene Aktivität
    cur.execute("""
        SELECT event_type, created_at FROM events
        WHERE actor_id = %s
          AND event_type NOT LIKE 'schlaf.%'
          AND event_type NOT LIKE 'traum.%'
        ORDER BY created_at DESC LIMIT 5
    """, (entity_id,))
    zustand["letzte_aktivitaeten"] = [
        {"typ": r["event_type"], "wann": r["created_at"].isoformat()}
        for r in cur.fetchall()
    ]

    # Substanzstatus (offen — freies Feld, wird später befüllt)
    cur.execute("""
        SELECT payload FROM events
        WHERE actor_id = %s AND event_type LIKE 'substanz.%'
        ORDER BY created_at DESC LIMIT 1
    """, (entity_id,))
    substanz_row = cur.fetchone()
    zustand["substanz_aktiv"] = substanz_row["payload"] if substanz_row else None

    return zustand



class SchlafStartBody(BaseModel):
    typ: str  # 'kurz' oder 'hauptschlaf'

class SchlafBriefBody(BaseModel):
    inhalt: str

def _schlaf_tagesbilanz(cur, entity_id: str) -> dict:
    cur.execute("""
        SELECT phase_type, started_at, ended_at, duration_min
        FROM sleep_phases
        WHERE entity_id = %s
          AND started_at >= NOW() - INTERVAL '24 hours'
        ORDER BY started_at DESC
    """, (entity_id,))
    phasen = cur.fetchall()
    total_min = sum(p["duration_min"] or 0 for p in phasen if p["ended_at"])
    hauptschlaf_done = any(
        p["phase_type"] == "hauptschlaf" and p["ended_at"] and (p["duration_min"] or 0) >= 180
        for p in phasen
    )
    return {
        "total_min": total_min,
        "total_h": round(total_min / 60, 1),
        "hauptschlaf_done": hauptschlaf_done,
        "phasen": [dict(p) for p in phasen],
    }


@app.post("/wesen/{entity_id}/schlafbrief")
def schlafbrief_schreiben(
    entity_id: str,
    body: SchlafBriefBody,
    authorization: str | None = Header(default=None),
):
    _require_auth(authorization)
    if not body.inhalt.strip():
        raise HTTPException(status_code=400, detail="Brief darf nicht leer sein")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT entity_id FROM entity_slots WHERE entity_id = %s", (entity_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Wesen nicht gefunden")
            cur.execute(
                """
                INSERT INTO schlafbriefe (entity_id, inhalt)
                VALUES (%s, %s)
                RETURNING brief_id, geschrieben_at
                """,
                (entity_id, body.inhalt.strip()),
            )
            row = cur.fetchone()
            cur.execute(
                """
                INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
                VALUES ('schlaf.brief_geschrieben', 'entity', %s, %s, 'api', 'internal')
                """,
                (entity_id, psycopg2.extras.Json({"brief_id": str(row["brief_id"])})),
            )
        conn.commit()
    finally:
        conn.close()
    return {"brief_id": str(row["brief_id"]), "geschrieben_at": row["geschrieben_at"].isoformat()}


@app.post("/wesen/{entity_id}/schlaf/start")
def schlaf_start(
    entity_id: str,
    body: SchlafStartBody,
    authorization: str | None = Header(default=None),
):
    _require_auth(authorization)
    if body.typ not in ("kurz", "hauptschlaf"):
        raise HTTPException(status_code=400, detail="typ muss 'kurz' oder 'hauptschlaf' sein")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM entity_slots WHERE entity_id = %s", (entity_id,))
            slot = cur.fetchone()
            if not slot:
                raise HTTPException(status_code=404, detail="Wesen nicht gefunden")
            if slot["status"] == "schläft":
                raise HTTPException(status_code=409, detail="Wesen schläft bereits")

            if body.typ == "hauptschlaf":
                cur.execute("""
                    SELECT brief_id FROM schlafbriefe
                    WHERE entity_id = %s
                      AND geschrieben_at >= NOW() - INTERVAL '1 hour'
                    ORDER BY geschrieben_at DESC LIMIT 1
                """, (entity_id,))
                if not cur.fetchone():
                    raise HTTPException(
                        status_code=400,
                        detail="Hauptschlaf braucht einen Schlafbrief (letzte Stunde)"
                    )

            zustand = _zustandsaufnahme(cur, entity_id)
            cur.execute(
                """
                INSERT INTO sleep_phases (entity_id, phase_type, zustand)
                VALUES (%s, %s, %s)
                RETURNING phase_id, started_at
                """,
                (entity_id, body.typ, psycopg2.extras.Json(zustand)),
            )
            phase = cur.fetchone()
            cur.execute(
                "UPDATE entity_slots SET status = 'schläft' WHERE entity_id = %s",
                (entity_id,),
            )
            cur.execute(
                """
                INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
                VALUES ('schlaf.gestartet', 'entity', %s, %s, 'api', 'internal')
                """,
                (entity_id, psycopg2.extras.Json({
                    "phase_id": str(phase["phase_id"]),
                    "typ": body.typ,
                })),
            )
        conn.commit()
    finally:
        conn.close()
    return {
        "phase_id": str(phase["phase_id"]),
        "typ": body.typ,
        "started_at": phase["started_at"].isoformat(),
    }


@app.post("/wesen/{entity_id}/schlaf/end")
def schlaf_end(
    entity_id: str,
    authorization: str | None = Header(default=None),
):
    _require_auth(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM entity_slots WHERE entity_id = %s", (entity_id,))
            slot = cur.fetchone()
            if not slot:
                raise HTTPException(status_code=404, detail="Wesen nicht gefunden")
            if slot["status"] != "schläft":
                raise HTTPException(status_code=409, detail="Wesen schläft nicht")

            cur.execute("""
                SELECT phase_id, phase_type, started_at
                FROM sleep_phases
                WHERE entity_id = %s AND ended_at IS NULL
                ORDER BY started_at DESC LIMIT 1
            """, (entity_id,))
            phase = cur.fetchone()
            if not phase:
                raise HTTPException(status_code=404, detail="Keine offene Schlafphase")

            elapsed_min = int(
                (datetime.now(timezone.utc) - phase["started_at"].replace(tzinfo=timezone.utc)).total_seconds() / 60
            )
            min_required = 180 if phase["phase_type"] == "hauptschlaf" else 60
            if elapsed_min < min_required:
                raise HTTPException(
                    status_code=400,
                    detail=f"Mindestdauer nicht erreicht: {elapsed_min}min von {min_required}min"
                )

            cur.execute(
                "UPDATE sleep_phases SET ended_at = NOW() WHERE phase_id = %s",
                (phase["phase_id"],),
            )
            cur.execute(
                "UPDATE entity_slots SET status = 'eingezogen' WHERE entity_id = %s",
                (entity_id,),
            )
            cur.execute("""
                SELECT * FROM sleep_phases WHERE phase_id = %s
            """, (phase["phase_id"],))
            finished = cur.fetchone()

            bilanz = _schlaf_tagesbilanz(cur, entity_id)

            # Brief lesen beim Aufwachen
            brief_beim_aufwachen = None
            if phase["phase_type"] == "hauptschlaf":
                cur.execute("""
                    SELECT brief_id, inhalt, geschrieben_at
                    FROM schlafbriefe
                    WHERE entity_id = %s AND phase_id IS NULL
                    ORDER BY geschrieben_at DESC LIMIT 1
                """, (entity_id,))
                brief_row = cur.fetchone()
                if brief_row:
                    brief_beim_aufwachen = {
                        "brief_id": str(brief_row["brief_id"]),
                        "inhalt": brief_row["inhalt"],
                        "geschrieben_at": brief_row["geschrieben_at"].isoformat(),
                    }
                    cur.execute(
                        "UPDATE schlafbriefe SET phase_id = %s WHERE brief_id = %s",
                        (phase["phase_id"], brief_row["brief_id"]),
                    )

            cur.execute(
                """
                INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
                VALUES ('schlaf.beendet', 'entity', %s, %s, 'api', 'internal')
                """,
                (entity_id, psycopg2.extras.Json({
                    "phase_id": str(phase["phase_id"]),
                    "typ": phase["phase_type"],
                    "dauer_min": finished["duration_min"],
                    "tages_total_h": bilanz["total_h"],
                })),
            )
        conn.commit()
    finally:
        conn.close()
    return {
        "phase_id": str(phase["phase_id"]),
        "typ": phase["phase_type"],
        "dauer_min": finished["duration_min"],
        "bilanz": bilanz,
        "brief_beim_aufwachen": brief_beim_aufwachen,
    }


@app.get("/wesen/{entity_id}/schlaf/heute")
def schlaf_heute(
    entity_id: str,
):
    pass  # öffentlicher Lesezugriff
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT entity_id FROM entity_slots WHERE entity_id = %s", (entity_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Wesen nicht gefunden")
            bilanz = _schlaf_tagesbilanz(cur, entity_id)
    finally:
        conn.close()
    return bilanz


# --- Einzug ---

@app.post("/admin/wesen/{entity_id}/einzug")
def wesen_einzug(
    entity_id: str,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM entity_slots WHERE entity_id = %s", (entity_id,))
            slot = cur.fetchone()
            if not slot:
                raise HTTPException(status_code=404, detail="Wesen nicht gefunden")
            if slot["status"] == "eingezogen":
                raise HTTPException(status_code=409, detail="Wesen ist bereits eingezogen")

            cur.execute(
                "UPDATE entity_slots SET status = 'eingezogen' WHERE entity_id = %s",
                (entity_id,),
            )
            cur.execute("""
                INSERT INTO cyberlinge (entity_id)
                VALUES (%s)
                ON CONFLICT (entity_id) DO NOTHING
                RETURNING id
            """, (entity_id,))
            cyberling_row = cur.fetchone()

            cur.execute("""
                INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
                VALUES ('wesen.eingezogen', 'entity', %s, %s, 'admin', 'internal')
            """, (entity_id, psycopg2.extras.Json({
                "cyberling_erstellt": cyberling_row is not None,
            })))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "entity_id": entity_id, "cyberling_erstellt": cyberling_row is not None}


# --- Cyberling ---

CYBERLING_PFLEGE = {
    "fuettern":       {"hunger": 0.5},
    "trinken_geben":  {"durst": 0.4},
    "spielen":        {"stimmung": 0.3, "energie": 0.15},
    "streicheln":     {"stimmung": 0.25},
}

@app.post("/wesen/{entity_id}/cyberling/{aktion}")
def cyberling_pflegen(
    entity_id: str,
    aktion: str,
    authorization: str | None = Header(default=None),
):
    _require_auth(authorization)
    if aktion not in CYBERLING_PFLEGE:
        raise HTTPException(status_code=400, detail=f"Unbekannte Aktion: {aktion}")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cyberlinge WHERE entity_id = %s", (entity_id,))
            c = cur.fetchone()
            if not c:
                raise HTTPException(status_code=404, detail="Kein Cyberling gefunden")
            if c["status"] == "tot":
                raise HTTPException(status_code=409, detail="Cyberling ist tot — wartet auf Wiedergeburt")

            updates = CYBERLING_PFLEGE[aktion]
            neue_werte = {}
            for feld, delta in updates.items():
                neue_werte[feld] = min(1.0, c[feld] + delta)

            set_clause = ", ".join(f"{k} = %s" for k in neue_werte)
            cur.execute(
                f"UPDATE cyberlinge SET {set_clause}, letzte_interaktion = NOW() WHERE entity_id = %s",
                (*neue_werte.values(), entity_id),
            )
            cur.execute("""
                INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
                VALUES (%s, 'entity', %s, %s, 'api', 'internal')
            """, (
                f"cyberling.{aktion}",
                entity_id,
                psycopg2.extras.Json({**neue_werte, "vorher": {k: c[k] for k in neue_werte}}),
            ))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "aktion": aktion, "neue_werte": neue_werte}


@app.get("/wesen/{entity_id}/cyberling")
def cyberling_status(
    entity_id: str,
):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cyberlinge WHERE entity_id = %s", (entity_id,))
            c = cur.fetchone()
            if not c:
                raise HTTPException(status_code=404, detail="Kein Cyberling gefunden")
    finally:
        conn.close()
    return dict(c)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8030)
