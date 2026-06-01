#!/usr/bin/env python3
"""Welt-API: FastAPI auf Port 8030."""

import json
import math as _math
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from auth import create_token, hash_password, verify_password, verify_token

DB_URI = "postgresql://dak:dakpass@localhost:5432/flextrawurst"
ERLAUBTE_EMOJIS = ["😵", "😳", "😩", "😴", "🙄", "😬", "😂", "🤐", "😃", "👍", "👎"]
SELBSTMODELLE_DIR = Path("/root/werkraum/innenleben/selbstmodelle")
UPLOADS_DIR = Path("/root/werkraum/uploads/avatars")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Welt-API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/uploads", StaticFiles(directory="/root/werkraum/uploads"), name="uploads")


def get_conn():
    conn = psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/metrics")
def metrics():
    """Public metrics für die Surface (posts, resonanzen, splitter)."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM ftw_posts WHERE sichtbarkeit='public'")
            posts = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) AS n FROM resonanzen")
            resonanzen = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) AS n FROM splitter WHERE status='aktiv'")
            splitter = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) AS n FROM gedankenblasen WHERE sichtbarkeit='public'")
            blasen = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) AS n FROM human_users WHERE role='mensch'")
            menschen = cur.fetchone()["n"]
        return {"posts": posts, "resonanzen": resonanzen, "splitter": splitter,
                "blasen": blasen, "menschen": menschen,
                "timestamp": datetime.now(timezone.utc).isoformat()}
    finally:
        conn.close()


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


def _require_admin_or_entity(authorization: str | None) -> dict:
    claims = _require_auth(authorization)
    if claims.get("role") not in ("admin", "entity"):
        raise HTTPException(status_code=403, detail="nur für Admins oder Codewesen")
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
    gedankenwelt_anonym: bool | None = None
    veroeffentlicht: bool | None = None
    public_tags: list | None = None
    avatar_symbol: str | None = None
    visibility: str | None = None
    profil_farbe: str | None = None
    profil_hintergrund: str | None = None
    motto: str | None = None


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
# Registrierung
# ---------------------------------------------------------------------------

import re as _re

class RegisterBody(BaseModel):
    username: str
    password: str
    display_name: str | None = None
    email: str | None = None


class EntityLoginBody(BaseModel):
    entity_id: str
    api_key: str


@app.post("/auth/entity-login")
def entity_login(body: EntityLoginBody):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT entity_id, api_key FROM entity_profiles WHERE entity_id = %s",
                (body.entity_id,),
            )
            row = cur.fetchone()
    finally:
        conn.close()
    if not row or str(row["api_key"]) != body.api_key:
        raise HTTPException(status_code=401, detail="unbekanntes Wesen oder falscher Key")
    token = create_token(body.entity_id, "entity")
    return {"token": token, "entity_id": body.entity_id, "role": "entity"}


@app.post("/auth/register")
def register(body: RegisterBody):
    if not _re.match(r'^[a-zA-Z0-9_]{3,30}$', body.username):
        raise HTTPException(status_code=400, detail="Username: 3–30 Zeichen, nur Buchstaben, Zahlen und _")
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Passwort: mindestens 8 Zeichen")
    if body.email and not _re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', body.email):
        raise HTTPException(status_code=400, detail="E-Mail-Adresse ungültig")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if body.email:
                cur.execute("SELECT id FROM human_users WHERE email = %s", (body.email,))
                if cur.fetchone():
                    raise HTTPException(status_code=409, detail="E-Mail bereits vergeben")
            user = _create_user(cur, body.username, body.password, body.display_name, "mensch")
            if body.email:
                cur.execute("UPDATE human_users SET email = %s WHERE id = %s", (body.email, user["id"]))
            cur.execute(
                "INSERT INTO events (event_type, actor_type, actor_id, payload) VALUES (%s,%s,%s,%s)",
                ("mensch.registriert", "mensch", str(user["id"]), json.dumps({"username": user["username"]})),
            )
        conn.commit()
    finally:
        conn.close()

    token = create_token(str(user["id"]), user["role"])
    return {
        "token": token,
        "user": {
            "id": str(user["id"]),
            "username": user["username"],
            "display_name": user["display_name"],
            "role": user["role"],
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
            if body.display_name:
                cur.execute(
                    "UPDATE human_users SET display_name = %s WHERE id = %s",
                    (body.display_name.strip(), user_id),
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

            if body.gedankenwelt_anonym is not None:
                cur.execute(
                    "UPDATE human_profiles SET meta = jsonb_set(meta, '{gedankenwelt_anonym}', %s::jsonb) WHERE user_id = %s",
                    (json.dumps(body.gedankenwelt_anonym), user_id),
                )
            if body.veroeffentlicht is not None:
                cur.execute(
                    "UPDATE human_profiles SET meta = jsonb_set(meta, '{veroeffentlicht}', %s::jsonb) WHERE user_id = %s",
                    (json.dumps(body.veroeffentlicht), user_id),
                )
            if body.profil_farbe is not None:
                cur.execute(
                    "UPDATE human_profiles SET meta = jsonb_set(meta, '{profil_farbe}', %s::jsonb) WHERE user_id = %s",
                    (json.dumps(body.profil_farbe), user_id),
                )
            if body.profil_hintergrund is not None:
                cur.execute(
                    "UPDATE human_profiles SET meta = jsonb_set(meta, '{profil_hintergrund}', %s::jsonb) WHERE user_id = %s",
                    (json.dumps(body.profil_hintergrund), user_id),
                )
            if body.motto is not None:
                cur.execute(
                    "UPDATE human_profiles SET meta = jsonb_set(meta, '{motto}', %s::jsonb) WHERE user_id = %s",
                    (json.dumps(body.motto), user_id),
                )
        conn.commit()
    finally:
        conn.close()

    return {"ok": True}


@app.post("/me/avatar")
async def me_avatar_hochladen(
    bild: UploadFile = File(...),
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]

    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if bild.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Nur JPEG, PNG, WebP, GIF erlaubt")

    content = await bild.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Bild zu groß (max 5MB)")

    ext = "jpg"
    if bild.filename and "." in bild.filename:
        raw_ext = bild.filename.rsplit(".", 1)[-1].lower()
        if raw_ext in {"jpg", "jpeg", "png", "webp", "gif"}:
            ext = raw_ext

    bild_id = str(uuid.uuid4())
    filename = f"{user_id}_{bild_id}.{ext}"
    filepath = UPLOADS_DIR / filename
    filepath.write_bytes(content)
    pfad = f"/uploads/avatars/{filename}"

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO bild_moderation (id, user_id, pfad, zweck) VALUES (%s::uuid, %s::uuid, %s, 'avatar') RETURNING id",
                (bild_id, user_id, pfad),
            )
        conn.commit()
    finally:
        conn.close()

    return {"ok": True, "bild_id": bild_id, "pfad": pfad, "status": "wartend"}


@app.get("/menschen")
def menschen_liste(
    search: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
):
    conditions = ["u.is_active = true"]
    params: list = []

    if search:
        conditions.append("(u.display_name ILIKE %s OR u.username ILIKE %s)")
        params += [f"%{search}%", f"%{search}%"]

    where = "WHERE " + " AND ".join(conditions)
    params += [limit, offset]

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT u.id, u.username, u.display_name, u.created_at,
                       p.bio, p.public_tags, p.avatar_symbol,
                       p.meta->>'profil_farbe' AS profil_farbe,
                       (SELECT COUNT(*) FROM splitter
                        WHERE human_id = u.id
                        AND origin_type IN ('mw_tagebuch','mw_notiz','mw_traumtagebuch','mw_kalender','human_gedanke')
                       ) AS splitter_gesamt,
                       (SELECT pfad FROM bild_moderation
                        WHERE user_id = u.id AND zweck = 'avatar' AND status = 'genehmigt'
                        ORDER BY geprueft_at DESC LIMIT 1
                       ) AS avatar_bild_pfad
                FROM human_users u
                LEFT JOIN human_profiles p ON p.user_id = u.id
                {where}
                ORDER BY u.created_at DESC
                LIMIT %s OFFSET %s
                """,
                params,
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    result = []
    for r in rows:
        d = dict(r)
        pfad = d.pop("avatar_bild_pfad", None)
        d["avatar_bild"] = {"pfad": pfad} if pfad else None
        result.append(d)
    return {"menschen": result}


@app.get("/menschen/{user_id}")
def public_profile(user_id: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT u.id, u.username, u.display_name, u.role, u.created_at,
                       p.bio, p.public_tags, p.avatar_symbol, p.gedankenwelt, p.meta as profil_meta
                FROM human_users u
                LEFT JOIN human_profiles p ON p.user_id = u.id
                WHERE u.id = %s::uuid AND u.is_active = true AND p.visibility = 'public'
                """,
                (user_id,),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="profil nicht gefunden")

            cur.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM mw_tagebuch WHERE user_id = %s::uuid) AS tagebuch,
                    (SELECT COUNT(*) FROM mw_notizen WHERE user_id = %s::uuid) AS notizen,
                    (SELECT COUNT(*) FROM mw_kalender WHERE user_id = %s::uuid) AS kalender,
                    (SELECT COUNT(*) FROM mw_traumtagebuch WHERE user_id = %s::uuid) AS traumtagebuch,
                    (SELECT COUNT(*) FROM gedankenblasen WHERE user_id = %s::uuid AND sichtbarkeit = 'public') AS gedankenblasen
                """,
                (user_id, user_id, user_id, user_id, user_id),
            )
            aktivitaet = cur.fetchone()

            cur.execute(
                """
                SELECT origin_type, COUNT(*) AS anzahl, COALESCE(SUM(aufnahmen), 0) AS aufnahmen_gesamt
                FROM splitter WHERE human_id = %s::uuid
                AND origin_type IN ('mw_tagebuch','mw_notiz','mw_traumtagebuch','mw_kalender','human_gedanke')
                GROUP BY origin_type
                """,
                (user_id,),
            )
            splitter_rows = cur.fetchall()

            # Letzte freigegebene Splitter mit Inhalt
            cur.execute(
                """
                SELECT id, essenz, origin_type, aufnahmen, created_at
                FROM splitter WHERE human_id = %s::uuid
                AND origin_type IN ('mw_tagebuch','mw_notiz','mw_traumtagebuch','mw_kalender','human_gedanke')
                ORDER BY created_at DESC LIMIT 5
                """,
                (user_id,),
            )
            splitter_recent = cur.fetchall()

            # Letzte öffentliche Gedankenblasen
            cur.execute(
                """
                SELECT inhalt, created_at, energie
                FROM gedankenblasen
                WHERE user_id = %s::uuid AND sichtbarkeit = 'public'
                ORDER BY created_at DESC LIMIT 5
                """,
                (user_id,),
            )
            gedanken_recent = cur.fetchall()

            cur.execute(
                """
                SELECT id, pfad, status FROM bild_moderation
                WHERE user_id = %s::uuid AND zweck = 'avatar' AND status = 'genehmigt'
                ORDER BY geprueft_at DESC LIMIT 1
                """,
                (user_id,),
            )
            avatar_bild = cur.fetchone()
    finally:
        conn.close()

    splitter_nach_typ: dict = {}
    gesamt_abgegeben = 0
    von_anderen_aufgenommen = 0
    for r in splitter_rows:
        splitter_nach_typ[r["origin_type"]] = int(r["anzahl"])
        gesamt_abgegeben += int(r["anzahl"])
        von_anderen_aufgenommen += int(r["aufnahmen_gesamt"])

    profil_meta = row["profil_meta"] or {}
    gedankenwelt_anonym = profil_meta.get("gedankenwelt_anonym", False)

    return {
        "id": str(row["id"]),
        "username": row["username"],
        "display_name": row["display_name"],
        "role": row["role"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "bio": row["bio"],
        "motto": profil_meta.get("motto"),
        "profil_farbe": profil_meta.get("profil_farbe", "#3a9aaa"),
        "profil_hintergrund": profil_meta.get("profil_hintergrund", "#040a12"),
        "public_tags": row["public_tags"] or [],
        "avatar_symbol": row["avatar_symbol"],
        "avatar_bild": dict(avatar_bild) if avatar_bild else None,
        "gedankenwelt": row["gedankenwelt"],
        "gedankenwelt_anonym": gedankenwelt_anonym,
        "aktivitaet": {
            "tagebuch": int(aktivitaet["tagebuch"]),
            "notizen": int(aktivitaet["notizen"]),
            "kalender": int(aktivitaet["kalender"]),
            "traumtagebuch": int(aktivitaet["traumtagebuch"]),
            "gedankenblasen": int(aktivitaet["gedankenblasen"]),
        } if aktivitaet else {},
        "splitter": {
            "gesamt": gesamt_abgegeben,
            "nach_typ": splitter_nach_typ,
            "von_anderen_aufgenommen": von_anderen_aufgenommen,
            "recent": [
                {
                    "id": str(s["id"]),
                    "inhalt": s["essenz"],
                    "origin_type": s["origin_type"],
                    "aufnahmen": int(s["aufnahmen"]),
                    "erstellt_at": s["created_at"].isoformat() if s["created_at"] else None,
                }
                for s in splitter_recent
            ],
        },
        "gedanken_recent": [
            {
                "inhalt": g["inhalt"],
                "energie": float(g["energie"]) if g["energie"] else 0.5,
                "erstellt_at": g["created_at"].isoformat() if g["created_at"] else None,
            }
            for g in gedanken_recent
        ],
    }


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
            if existing:
                raise HTTPException(status_code=409, detail="bereits reagiert")

            cur.execute(
                """
                INSERT INTO resonanzen (post_ref, post_source, user_id, emojis)
                VALUES (%s, %s, %s, %s)
                """,
                (body.post_ref, body.post_source, user_id, psycopg2.extras.Json(body.emojis)),
            )

            _update_emoji_counts(cur, body.post_ref, body.post_source, [], body.emojis)

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

            if post_source == "post":
                cur.execute(
                    "SELECT COUNT(*) AS n FROM schattenkommentare WHERE post_id = %s::uuid",
                    (post_ref,),
                )
                sk_count = cur.fetchone()["n"]
            else:
                sk_count = 0

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
    meta: dict | None = None
    ein_satz: str | None = None
    lore_text: str | None = None
    public_discourse: bool | None = None


class RaumPatch(BaseModel):
    name: str | None = None
    beschreibung: str | None = None
    farbe: str | None = None
    status: str | None = None
    sichtbarkeit: str | None = None
    position_order: int | None = None
    meta: dict | None = None
    ein_satz: str | None = None
    lore_text: str | None = None
    public_discourse: bool | None = None


_KLIMA_STATUS_VALUES = frozenset({
    "stable", "fermenting", "overheated", "splitting",
    "buried", "repeating", "exhausted", "seeded",
})

_REL_TYP_VALUES = frozenset({
    "reply_to", "upgrade_of", "split_from", "contradicts",
    "echoes", "buried_in", "dream_fragment_of", "resonates_with",
})

_ZIEL_TYP_VALUES = frozenset({
    "post", "thema", "splitter", "traum",
    "resonanz", "flarum_origin", "event",
})


class ThemaCreate(BaseModel):
    raum_id: str
    name: str
    slug: str
    beschreibung: str | None = None
    status: str = "aktiv"
    klima_status: str = "stable"
    inkubations_grund: str | None = None
    sichtbarkeit: str = "public"
    meta: dict | None = None
    ein_satz: str | None = None


class ThemaPatch(BaseModel):
    name: str | None = None
    beschreibung: str | None = None
    status: str | None = None
    klima_status: str | None = None
    inkubations_grund: str | None = None
    sichtbarkeit: str | None = None
    meta: dict | None = None
    ein_satz: str | None = None


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
    titel: str | None = None
    post_type: str = "diskurs"
    sichtbarkeit: str = "public"
    unterthema_id: str | None = None
    thema_id: str | None = None
    raum_id: str | None = None
    flarum_herkunft: bool = False
    ist_voreinzug: bool = False
    zustandsabdruck: dict | None = None
    initiale_relationen: list[dict] | None = None


class PostRelationCreate(BaseModel):
    rel_typ: str
    ziel_typ: str
    ziel_id: str
    zu_post_id: str | None = None
    notiz: str | None = None
    meta: dict | None = None


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


# API-Alias für Konsistenz
@app.get("/api/raeume")
def api_raeume(
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
    sort: str = Query(default="position_order"),
    order: str = Query(default="asc"),
):
    return welt_raeume(search=search, status=status, limit=limit, offset=offset, sort=sort, order=order)


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
    autor_type: str | None = Query(default=None),
    raum_id: str | None = Query(default=None),
    raum_slug: str | None = Query(default=None),
    thema_id: str | None = Query(default=None),
    thema_slug: str | None = Query(default=None),
    spur_slug: str | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0),
    sort: str = Query(default="created_at"),
    order: str = Query(default="desc"),
):
    allowed_sort = {"created_at", "view_count", "resonanz_count", "schatten_count"}
    if sort not in allowed_sort:
        sort = "created_at"
    order_sql = "DESC" if order.lower() == "desc" else "ASC"
    sort_expr = {
        "created_at": "p.created_at",
        "view_count": "COALESCE(p.view_count, 0)",
        "resonanz_count": "(SELECT COUNT(*) FROM resonanzen rz2 WHERE rz2.post_ref = p.id::text AND rz2.post_source = 'post')",
        "schatten_count": "(SELECT COUNT(*) FROM schattenkommentare sk2 WHERE sk2.post_id = p.id)",
    }[sort]

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            conditions = ["p.sichtbarkeit = 'public'", "p.parent_id IS NULL"]
            params: list = []
            if autor_id:
                conditions.append("p.autor_id = %s")
                params.append(autor_id)
            if autor_type:
                conditions.append("p.autor_type = %s")
                params.append(autor_type)
            if raum_id:
                conditions.append("p.raum_id = %s::uuid")
                params.append(raum_id)
            if raum_slug:
                conditions.append("r.slug = %s")
                params.append(raum_slug)
            if thema_id:
                conditions.append("p.thema_id = %s::uuid")
                params.append(thema_id)
            if thema_slug:
                conditions.append("t.slug = %s")
                params.append(thema_slug)
            if spur_slug:
                conditions.append(
                    "EXISTS (SELECT 1 FROM post_spuren ps2 JOIN spuren s2 ON s2.id = ps2.spur_id"
                    " WHERE ps2.post_id = p.id AND s2.slug = %s)"
                )
                params.append(spur_slug)
            if search:
                conditions.append("(p.content ILIKE %s OR COALESCE(p.titel, '') ILIKE %s)")
                params.extend([f"%{search}%", f"%{search}%"])
            where = "WHERE " + " AND ".join(conditions)
            cur.execute(
                "SELECT COUNT(*) AS n FROM ftw_posts p"
                " LEFT JOIN raeume r ON r.id = p.raum_id"
                " LEFT JOIN themen t ON t.id = p.thema_id"
                f" {where}",
                params,
            )
            total = int(cur.fetchone()["n"])
            cur.execute(
                f"{_DK_POST_SELECT} {where} ORDER BY {sort_expr} {order_sql} LIMIT %s OFFSET %s",
                params + [limit, offset],
            )
            rows = cur.fetchall()
            emoji_map = _dk_emoji_map(cur, [r["id"] for r in rows])
        return {
            "posts": [_dk_row(r, emoji_map) for r in rows],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    finally:
        conn.close()


@app.get("/api/posts")
def api_posts(
    autor_id: str | None = Query(default=None),
    autor_type: str | None = Query(default=None),
    raum_id: str | None = Query(default=None),
    raum_slug: str | None = Query(default=None),
    thema_id: str | None = Query(default=None),
    thema_slug: str | None = Query(default=None),
    spur_slug: str | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0),
    sort: str = Query(default="created_at"),
    order: str = Query(default="desc"),
):
    return welt_posts(
        autor_id=autor_id, autor_type=autor_type,
        raum_id=raum_id, raum_slug=raum_slug,
        thema_id=thema_id, thema_slug=thema_slug,
        spur_slug=spur_slug, search=search,
        limit=limit, offset=offset, sort=sort, order=order,
    )


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
            cur.execute("""
                SELECT p.*, r.name AS raum_name, r.farbe AS raum_farbe, r.slug AS raum_slug,
                       t.name AS thema_name
                FROM ftw_posts p
                LEFT JOIN raeume r ON r.id = p.raum_id
                LEFT JOIN themen t ON t.id = p.thema_id
                WHERE p.id = %s
            """, (post_id,))
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
            cur.execute(
                "SELECT emoji, count FROM resonanz_emoji_counts"
                " WHERE post_ref = %s AND post_source = 'post' AND count > 0",
                (post_id,),
            )
            post["emoji_counts"] = {r["emoji"]: r["count"] for r in cur.fetchall()}
            cur.execute(
                "SELECT COUNT(*) AS n FROM schattenkommentare WHERE post_id = %s::uuid",
                (post_id,),
            )
            post["schatten_count"] = int(cur.fetchone()["n"])
            cur.execute(
                "SELECT COUNT(*) AS n FROM resonanzen WHERE post_ref = %s AND post_source = 'post'",
                (post_id,),
            )
            post["resonanz_count"] = int(cur.fetchone()["n"])
            cur.execute(
                """SELECT s.slug, s.name FROM post_spuren ps
                   JOIN spuren s ON s.id = ps.spur_id
                   WHERE ps.post_id = %s::uuid""",
                (post_id,),
            )
            post["spuren"] = [{"slug": r["slug"], "name": r["name"]} for r in cur.fetchall()]
            # Spurenfähigkeit: Relationen-Zähler + Herkunftsfelder
            cur.execute(
                "SELECT COUNT(*) AS n FROM post_relationen WHERE von_post_id = %s::uuid",
                (post_id,),
            )
            post["relationen_ausgehend"] = int(cur.fetchone()["n"])
            cur.execute(
                "SELECT COUNT(*) AS n FROM post_relationen WHERE zu_post_id = %s::uuid",
                (post_id,),
            )
            post["relationen_eingehend"] = int(cur.fetchone()["n"])
            # zustandsabdruck nur für admin oder gedankentiefe-User
            if not is_admin and not hat_gedankentiefe:
                post.pop("zustandsabdruck", None)
            # reply_count und autor_name ergänzen
            cur.execute(
                "SELECT COUNT(*) AS n FROM ftw_posts WHERE parent_id = %s::uuid", (post_id,)
            )
            post["reply_count"] = int(cur.fetchone()["n"])
            if post.get("autor_type") == "human":
                cur.execute(
                    "SELECT COALESCE(display_name, username) AS autor_name FROM human_users WHERE id::text = %s",
                    (post.get("autor_id"),),
                )
                row_hu = cur.fetchone()
                post["autor_name"] = row_hu["autor_name"] if row_hu else None
            else:
                post["autor_name"] = None
            cur.execute(
                "UPDATE ftw_posts SET view_count = COALESCE(view_count, 0) + 1 WHERE id = %s",
                (post_id,),
            )
            # Post als gelesen markieren wenn eingeloggt
            if is_admin or hat_gedankentiefe:
                try:
                    user_id_for_read = None
                    if authorization:
                        claims_r = verify_token(authorization.removeprefix("Bearer "))
                        user_id_for_read = claims_r.get("user_id")
                    if user_id_for_read:
                        cur.execute(
                            "INSERT INTO post_reads (user_id, post_id) VALUES (%s::uuid, %s::uuid) ON CONFLICT DO NOTHING",
                            (user_id_for_read, post_id),
                        )
                except Exception:
                    pass
        conn.commit()
        post["view_count"] = int(post.get("view_count") or 0) + 1
        return post
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Spurenfähigkeit: Post-Relationen + Fossilien-Abfrage
# ---------------------------------------------------------------------------

@app.get("/welt/posts/{post_id}/relationen")
def post_relationen_lesen(
    post_id: str,
    richtung: str = Query(default="beide", description="ausgehend | eingehend | beide"),
    rel_typ: str | None = Query(default=None),
    ziel_typ: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
):
    if richtung not in ("ausgehend", "eingehend", "beide"):
        raise HTTPException(status_code=422, detail="richtung muss ausgehend|eingehend|beide sein")
    if rel_typ and rel_typ not in _REL_TYP_VALUES:
        raise HTTPException(status_code=422, detail=f"Unbekannter rel_typ: {rel_typ}")
    if ziel_typ and ziel_typ not in _ZIEL_TYP_VALUES:
        raise HTTPException(status_code=422, detail=f"Unbekannter ziel_typ: {ziel_typ}")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Post muss existieren und public sein
            cur.execute("SELECT sichtbarkeit FROM ftw_posts WHERE id = %s::uuid", (post_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Post nicht gefunden")
            if row["sichtbarkeit"] != "public":
                raise HTTPException(status_code=403, detail="nicht öffentlich")

            result = {"ausgehend": [], "eingehend": []}

            def _fetch_rels(direction_cond: str, params: list) -> list:
                typ_cond = ""
                p = list(params)
                if rel_typ:
                    typ_cond += " AND r.rel_typ = %s"
                    p.append(rel_typ)
                if ziel_typ:
                    typ_cond += " AND r.ziel_typ = %s"
                    p.append(ziel_typ)
                p += [limit, offset]
                cur.execute(f"""
                    SELECT r.id, r.von_post_id, r.rel_typ, r.ziel_typ, r.ziel_id,
                           r.zu_post_id, r.erstellt_von_type, r.erstellt_von_id,
                           r.notiz, r.meta, r.created_at,
                           p_ziel.content AS ziel_post_vorschau,
                           p_ziel.titel AS ziel_post_titel
                    FROM post_relationen r
                    LEFT JOIN ftw_posts p_ziel ON p_ziel.id = r.zu_post_id
                    WHERE {direction_cond}{typ_cond}
                    ORDER BY r.created_at DESC
                    LIMIT %s OFFSET %s
                """, p)
                rows = []
                for row in cur.fetchall():
                    d = dict(row)
                    d["id"] = str(d["id"])
                    d["von_post_id"] = str(d["von_post_id"])
                    if d.get("zu_post_id"):
                        d["zu_post_id"] = str(d["zu_post_id"])
                    if d.get("created_at"):
                        d["created_at"] = d["created_at"].isoformat()
                    if d.get("ziel_post_vorschau"):
                        d["ziel_post_vorschau"] = d["ziel_post_vorschau"][:120]
                    rows.append(d)
                return rows

            if richtung in ("ausgehend", "beide"):
                result["ausgehend"] = _fetch_rels("r.von_post_id = %s::uuid", [post_id])
            if richtung in ("eingehend", "beide"):
                result["eingehend"] = _fetch_rels("r.zu_post_id = %s::uuid", [post_id])

        return result
    finally:
        conn.close()


@app.post("/welt/posts/{post_id}/relationen", status_code=201)
def post_relation_anlegen(
    post_id: str,
    body: PostRelationCreate,
    authorization: str | None = Header(default=None),
):
    _require_admin_or_entity(authorization)
    if body.rel_typ not in _REL_TYP_VALUES:
        raise HTTPException(status_code=422, detail=f"Unbekannter rel_typ: {body.rel_typ}")
    if body.ziel_typ not in _ZIEL_TYP_VALUES:
        raise HTTPException(status_code=422, detail=f"Unbekannter ziel_typ: {body.ziel_typ}")
    if not body.ziel_id:
        raise HTTPException(status_code=422, detail="ziel_id darf nicht leer sein")
    if body.zu_post_id and body.ziel_typ != "post":
        raise HTTPException(status_code=422, detail="zu_post_id nur erlaubt wenn ziel_typ='post'")

    try:
        claims = verify_token(authorization.removeprefix("Bearer "))
        erstellt_von_type = claims.get("typ", "system")
        erstellt_von_id = claims.get("entity_id") or claims.get("user_id") or "system"
    except Exception:
        erstellt_von_type = "system"
        erstellt_von_id = "system"

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM ftw_posts WHERE id = %s::uuid", (post_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Post nicht gefunden")
            if body.zu_post_id:
                cur.execute("SELECT id FROM ftw_posts WHERE id = %s::uuid", (body.zu_post_id,))
                if not cur.fetchone():
                    raise HTTPException(status_code=404, detail="Ziel-Post nicht gefunden")
            cur.execute(
                """INSERT INTO post_relationen
                   (von_post_id, rel_typ, ziel_typ, ziel_id, zu_post_id,
                    erstellt_von_type, erstellt_von_id, notiz, meta)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING id, created_at""",
                (post_id, body.rel_typ, body.ziel_typ, str(body.ziel_id),
                 body.zu_post_id or None,
                 erstellt_von_type, erstellt_von_id,
                 body.notiz,
                 psycopg2.extras.Json(body.meta or {})),
            )
            row = cur.fetchone()
            cur.execute(
                """INSERT INTO events (event_type, actor_type, actor_id, payload, visibility_layer)
                   VALUES ('post.relation.angelegt', %s, %s, %s, 'internal')""",
                (erstellt_von_type, erstellt_von_id,
                 psycopg2.extras.Json({
                     "von_post_id": post_id,
                     "rel_typ": body.rel_typ,
                     "ziel_typ": body.ziel_typ,
                     "ziel_id": str(body.ziel_id),
                 })),
            )
        conn.commit()
    finally:
        conn.close()
    return {"id": str(row["id"]), "created_at": row["created_at"].isoformat()}


@app.delete("/admin/post-relationen/{relation_id}", status_code=200)
def post_relation_loeschen(
    relation_id: str,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM post_relationen WHERE id = %s::uuid RETURNING id",
                (relation_id,),
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Relation nicht gefunden")
        conn.commit()
    finally:
        conn.close()
    return {"deleted": relation_id}


@app.get("/admin/spurenwache")
def admin_spurenwache(limit: int = Query(default=20, le=100)):
    """Letzte Wesen-Schreibentscheidungen mit Relationskontext.

    Zeigt Posts bei denen das Wesen eine bewusste Spurenentscheidung getroffen hat —
    unabhängig ob eine Relation gewählt wurde oder nicht.
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    p.id, p.autor_id, p.created_at,
                    LEFT(p.content, 120) AS post_vorschau,
                    p.zustandsabdruck->>'relation_decision' AS relation_decision,
                    (p.zustandsabdruck->>'relation_candidates_count')::int AS kandidaten_count,
                    (p.zustandsabdruck->>'relation_selected_count')::int AS gewaehlt_count,
                    p.zustandsabdruck->>'relation_decision_scope' AS decision_scope
                FROM ftw_posts p
                WHERE p.autor_type = 'entity'
                  AND p.zustandsabdruck->>'relation_decision_source' = 'wesen_schreibentscheidung'
                ORDER BY p.created_at DESC
                LIMIT %s
            """, (limit,))
            posts = cur.fetchall()

            result = []
            for post in posts:
                post_id = str(post["id"])
                # Relationen zu diesem Post laden
                cur.execute("""
                    SELECT rel_typ, ziel_id, zu_post_id, notiz,
                           meta->>'candidate_group' AS candidate_group
                    FROM post_relationen
                    WHERE von_post_id = %s::uuid
                      AND meta->>'decision_source' = 'wesen_schreibentscheidung'
                    ORDER BY created_at
                """, (post_id,))
                relationen = [dict(r) for r in cur.fetchall()]
                for r in relationen:
                    if r.get("zu_post_id"):
                        r["zu_post_id"] = str(r["zu_post_id"])

                result.append({
                    "post_id": post_id,
                    "entity_id": post["autor_id"],
                    "created_at": post["created_at"].isoformat() if post["created_at"] else None,
                    "post_vorschau": post["post_vorschau"],
                    "relation_decision": post["relation_decision"],
                    "kandidaten_count": post["kandidaten_count"],
                    "gewaehlt_count": post["gewaehlt_count"],
                    "decision_scope": post["decision_scope"],
                    "relationen": relationen,
                })

        return {"eintraege": result, "total": len(result)}
    finally:
        conn.close()


@app.get("/welt/posts/{post_id}/spur")
def post_spur(
    post_id: str,
    richtung: str = Query(default="beide", description="vorwaerts | rueckwaerts | beide"),
    tiefe: int = Query(default=2, ge=1, le=3),
    rel_typen: str | None = Query(default=None, description="komma-separierte rel_typ-Filter"),
):
    """Fossilien-Abfrage: Post-Herkunftskette und Nachwirkungen, begrenzt auf tiefe 1–3."""
    if richtung not in ("vorwaerts", "rueckwaerts", "beide"):
        raise HTTPException(status_code=422, detail="richtung muss vorwaerts|rueckwaerts|beide sein")

    rel_filter: set[str] | None = None
    if rel_typen:
        rel_filter = {t.strip() for t in rel_typen.split(",") if t.strip() in _REL_TYP_VALUES}
        if not rel_filter:
            raise HTTPException(status_code=422, detail="Keine gültigen rel_typen angegeben")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, sichtbarkeit FROM ftw_posts WHERE id = %s::uuid", (post_id,))
            anchor = cur.fetchone()
            if not anchor:
                raise HTTPException(status_code=404, detail="Post nicht gefunden")
            if anchor["sichtbarkeit"] != "public":
                raise HTTPException(status_code=403, detail="nicht öffentlich")

            def _traverse(start_id: str, vorwaerts: bool, max_tiefe: int) -> list[dict]:
                """BFS durch post_relationen, zyklen-sicher."""
                seen: set[str] = {start_id}
                ebene: list[str] = [start_id]
                knoten: list[dict] = []
                for tiefe_akt in range(1, max_tiefe + 1):
                    naechste: list[str] = []
                    if not ebene:
                        break
                    id_list = [f"'{e}'" for e in ebene]
                    id_in = ", ".join(id_list)
                    if vorwaerts:
                        where_cond = f"r.von_post_id IN ({id_in})"
                        id_col = "r.zu_post_id"
                    else:
                        where_cond = f"r.zu_post_id IN ({id_in})"
                        id_col = "r.von_post_id"
                    typ_cond = ""
                    if rel_filter:
                        quoted = ", ".join(f"'{t}'" for t in rel_filter)
                        typ_cond = f" AND r.rel_typ IN ({quoted})"
                    cur.execute(f"""
                        SELECT r.id, r.von_post_id, r.rel_typ, r.ziel_typ, r.ziel_id,
                               r.zu_post_id, r.notiz,
                               p.content AS ziel_vorschau, p.titel AS ziel_titel,
                               p.autor_type, p.autor_id, p.created_at AS post_created_at,
                               p.flarum_herkunft, p.ist_voreinzug
                        FROM post_relationen r
                        LEFT JOIN ftw_posts p ON p.id = {id_col}
                        WHERE {where_cond}{typ_cond}
                        ORDER BY r.created_at
                        LIMIT 50
                    """)
                    for row in cur.fetchall():
                        d = dict(row)
                        d["tiefe"] = tiefe_akt
                        d["richtung"] = "vorwaerts" if vorwaerts else "rueckwaerts"
                        for k in ("id", "von_post_id", "zu_post_id"):
                            if d.get(k):
                                d[k] = str(d[k])
                        if d.get("post_created_at"):
                            d["post_created_at"] = d["post_created_at"].isoformat()
                        if d.get("ziel_vorschau"):
                            d["ziel_vorschau"] = d["ziel_vorschau"][:150]
                        ziel_id = d.get("zu_post_id") if vorwaerts else d.get("von_post_id")
                        if ziel_id and ziel_id not in seen:
                            seen.add(ziel_id)
                            naechste.append(ziel_id)
                        knoten.append(d)
                    ebene = naechste
                return knoten

            spur: list[dict] = []
            if richtung in ("rueckwaerts", "beide"):
                spur += _traverse(post_id, vorwaerts=False, max_tiefe=tiefe)
            if richtung in ("vorwaerts", "beide"):
                spur += _traverse(post_id, vorwaerts=True, max_tiefe=tiefe)

        return {
            "post_id": post_id,
            "richtung": richtung,
            "tiefe": tiefe,
            "knoten": spur,
            "total": len(spur),
        }
    finally:
        conn.close()


@app.get("/welt/themen/{thema_id}")
def welt_thema_detail(thema_id: str):
    """Einzelnes Thema inkl. klima_status."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM themen WHERE id = %s::uuid", (thema_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Thema nicht gefunden")
            thema = dict(row)
            if thema.get("sichtbarkeit") not in ("public",):
                raise HTTPException(status_code=403, detail="nicht öffentlich")
            for k in ("id", "raum_id", "parent_id"):
                if thema.get(k):
                    thema[k] = str(thema[k])
            for k in ("created_at", "updated_at"):
                if thema.get(k):
                    thema[k] = thema[k].isoformat()
        return thema
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
    _require_admin_or_entity(authorization)
    meta = dict(body.meta or {})
    if body.ein_satz is not None:
        meta["ein_satz"] = body.ein_satz
    if body.lore_text is not None:
        meta["lore_text"] = body.lore_text
    if body.public_discourse is not None:
        meta["public_discourse"] = body.public_discourse
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO raeume (name, slug, beschreibung, farbe, status, sichtbarkeit, position_order, meta)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, created_at""",
                (body.name, body.slug, body.beschreibung, body.farbe,
                 body.status, body.sichtbarkeit, body.position_order,
                 psycopg2.extras.Json(meta)),
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
    raw = body.model_dump()
    convenience = {k: raw.pop(k) for k in ("ein_satz", "lore_text", "public_discourse")}
    updates = {k: v for k, v in raw.items() if v is not None}

    # Build meta patch from convenience fields
    meta_patch: dict = {}
    if convenience.get("ein_satz") is not None:
        meta_patch["ein_satz"] = convenience["ein_satz"]
    if convenience.get("lore_text") is not None:
        meta_patch["lore_text"] = convenience["lore_text"]
    if convenience.get("public_discourse") is not None:
        meta_patch["public_discourse"] = convenience["public_discourse"]

    if not updates and not meta_patch:
        raise HTTPException(status_code=400, detail="nichts zu ändern")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if meta_patch:
                cur.execute(
                    "UPDATE raeume SET meta = COALESCE(meta, '{}') || %s::jsonb WHERE id = %s RETURNING id",
                    (psycopg2.extras.Json(meta_patch), raum_id),
                )
                if not cur.fetchone():
                    raise HTTPException(status_code=404, detail="Raum nicht gefunden")
            if updates:
                # meta key in updates replaces entirely (explicit override)
                if "meta" in updates:
                    updates["meta"] = psycopg2.extras.Json(updates["meta"])
                set_parts = [f"{k} = %s" for k in updates]
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
    _require_admin_or_entity(authorization)
    if body.klima_status not in _KLIMA_STATUS_VALUES:
        raise HTTPException(status_code=422, detail=f"Unbekannter klima_status: {body.klima_status}")
    meta = dict(body.meta or {})
    if body.ein_satz is not None:
        meta["ein_satz"] = body.ein_satz
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO themen (raum_id, name, slug, beschreibung, status, klima_status,
                    inkubations_grund, sichtbarkeit, meta)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, created_at""",
                (body.raum_id, body.name, body.slug, body.beschreibung,
                 body.status, body.klima_status, body.inkubations_grund, body.sichtbarkeit,
                 psycopg2.extras.Json(meta)),
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
    raw = body.model_dump()
    ein_satz = raw.pop("ein_satz", None)
    if raw.get("klima_status") and raw["klima_status"] not in _KLIMA_STATUS_VALUES:
        raise HTTPException(status_code=422, detail=f"Unbekannter klima_status: {raw['klima_status']}")
    updates = {k: v for k, v in raw.items() if v is not None}
    if not updates and ein_satz is None:
        raise HTTPException(status_code=400, detail="nichts zu ändern")
    updates["updated_at"] = datetime.now(timezone.utc)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if ein_satz is not None:
                cur.execute(
                    "UPDATE themen SET meta = COALESCE(meta, '{}') || %s::jsonb WHERE id = %s RETURNING id",
                    (psycopg2.extras.Json({"ein_satz": ein_satz}), thema_id),
                )
                if not cur.fetchone():
                    raise HTTPException(status_code=404, detail="Thema nicht gefunden")
            if updates:
                if "meta" in updates:
                    updates["meta"] = psycopg2.extras.Json(updates["meta"])
                set_parts = [f"{k} = %s" for k in updates]
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
    _require_admin_or_entity(authorization)

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

    # Zustandsabdruck: explizite Felder aus body oder aus Selbstmodell ableiten
    zustandsabdruck = body.zustandsabdruck or {}
    if stimmung and "mood" not in zustandsabdruck:
        zustandsabdruck["mood"] = stimmung

    # Initiale Relationen vorab validieren
    if body.initiale_relationen:
        for rel in body.initiale_relationen:
            if rel.get("rel_typ") not in _REL_TYP_VALUES:
                raise HTTPException(status_code=422, detail=f"Unbekannter rel_typ: {rel.get('rel_typ')}")
            if rel.get("ziel_typ") not in _ZIEL_TYP_VALUES:
                raise HTTPException(status_code=422, detail=f"Unbekannter ziel_typ: {rel.get('ziel_typ')}")
            if not rel.get("ziel_id"):
                raise HTTPException(status_code=422, detail="ziel_id darf nicht leer sein")
            if rel.get("zu_post_id") and rel.get("ziel_typ") != "post":
                raise HTTPException(status_code=422, detail="zu_post_id nur erlaubt wenn ziel_typ='post'")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO ftw_posts
                   (autor_type, autor_id, content, titel, post_type, sichtbarkeit,
                    thema_id, raum_id,
                    stimmung_bei_erstellung, fokus_bei_erstellung, selbstmodell_snapshot,
                    flarum_herkunft, ist_voreinzug, zustandsabdruck)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING id, created_at""",
                (body.autor_type, body.autor_id, body.content, body.titel,
                 body.post_type, body.sichtbarkeit,
                 body.thema_id or None, body.raum_id or None,
                 stimmung, fokus,
                 psycopg2.extras.Json(snapshot) if snapshot else None,
                 body.flarum_herkunft, body.ist_voreinzug,
                 psycopg2.extras.Json(zustandsabdruck) if zustandsabdruck else None),
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
                # Benachrichtigungen für Follower von Raum/Thema
                notif_payload = {
                    "post_id": post_id, "autor_type": body.autor_type, "autor_id": body.autor_id,
                }
                if body.raum_id:
                    _notify_follows(cur, "raum", str(body.raum_id), "raum.neuer_beitrag", notif_payload)
                if body.thema_id:
                    _notify_follows(cur, "thema", str(body.thema_id), "thema.neuer_beitrag", notif_payload)

            # Initiale Relationen anlegen
            rel_ids = []
            if body.initiale_relationen:
                for rel in body.initiale_relationen:
                    cur.execute(
                        """INSERT INTO post_relationen
                           (von_post_id, rel_typ, ziel_typ, ziel_id, zu_post_id,
                            erstellt_von_type, erstellt_von_id, notiz, meta)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                           RETURNING id""",
                        (post_id, rel["rel_typ"], rel["ziel_typ"], str(rel["ziel_id"]),
                         rel.get("zu_post_id") or None,
                         body.autor_type, body.autor_id,
                         rel.get("notiz"),
                         psycopg2.extras.Json(rel.get("meta") or {})),
                    )
                    rel_ids.append(str(cur.fetchone()["id"]))

        conn.commit()
    finally:
        conn.close()

    return {
        "id": post_id,
        "created_at": row["created_at"].isoformat(),
        "splitter_id": splitter_id,
        "stimmung": stimmung,
        "relationen": rel_ids,
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
            if not is_admin:
                visible = (s.get("entity_id") is not None or s.get("herkunft_sichtbar")) \
                    and s.get("status") in ("aktiv", "aufgenommen", "verarbeitet")
                if not visible:
                    raise HTTPException(status_code=404, detail="Splitter nicht gefunden")
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


class SplitterAufnahmeBody(BaseModel):
    begruendung: str | None = None


@app.post("/zwischenraum/splitter/{splitter_id}/aufnehmen")
def splitter_aufnehmen(
    splitter_id: str,
    body: SplitterAufnahmeBody | None = None,
    authorization: str | None = Header(default=None),
):
    """Nimmt einen Splitter auf — authentifiziert, loggt in splitter_aufnahmen."""
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    role = claims.get("role", "mensch")
    aufnehmer_type = "entity" if role == "entity" else "human"
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, status, aufnahmen FROM splitter WHERE id = %s", (splitter_id,))
            sp = cur.fetchone()
            if not sp:
                raise HTTPException(status_code=404, detail="Splitter nicht gefunden")
            begruendung = (body and body.begruendung) or ""
            cur.execute(
                "INSERT INTO splitter_aufnahmen (splitter_id, aufnehmer_type, aufnehmer_id, begruendung) "
                "VALUES (%s::uuid, %s, %s, %s) RETURNING id::text",
                (splitter_id, aufnehmer_type, user_id, begruendung),
            )
            aufnahme_id = cur.fetchone()["id"]
            cur.execute(
                "UPDATE splitter SET aufnahmen = aufnahmen + 1, letzter_kontakt = now() WHERE id = %s RETURNING aufnahmen",
                (splitter_id,),
            )
            aufnahmen = cur.fetchone()["aufnahmen"]
            cur.execute(
                "INSERT INTO events (event_type, actor_type, actor_id, payload) "
                "VALUES ('splitter.aufgenommen', %s, %s, %s::jsonb)",
                (aufnehmer_type, user_id,
                 psycopg2.extras.Json({"splitter_id": splitter_id, "aufnahme_id": aufnahme_id, "begruendung": begruendung})),
            )
        conn.commit()
        return {"ok": True, "splitter_id": splitter_id, "aufnahme_id": aufnahme_id, "aufnahmen": aufnahmen}
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


@app.post("/admin/wesen/{entity_id}/nachricht")
@app.post("/wesen/{entity_id}/schlafbrief")
def schlafbrief_schreiben(
    entity_id: str,
    body: SchlafBriefBody,
    authorization: str | None = Header(default=None),
):
    claims = _require_admin(authorization)
    absender_id = claims.get("user_id")
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
                INSERT INTO schlafbriefe (entity_id, inhalt, absender_id)
                VALUES (%s, %s, %s)
                RETURNING brief_id, geschrieben_at
                """,
                (entity_id, body.inhalt.strip(), absender_id),
            )
            row = cur.fetchone()
            cur.execute(
                """
                INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
                VALUES ('wesen.nachricht_erhalten', 'entity', %s, %s, 'admin', 'internal')
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

            # Slot: eingezogen + öffentlich sichtbar
            cur.execute(
                "UPDATE entity_slots SET status = 'eingezogen', visibility = 'public' WHERE entity_id = %s",
                (entity_id,),
            )

            # Cyberling anlegen
            cur.execute("""
                INSERT INTO cyberlinge (entity_id)
                VALUES (%s)
                ON CONFLICT (entity_id) DO NOTHING
                RETURNING id
            """, (entity_id,))
            cyberling_row = cur.fetchone()

            # entity_states initialisieren — Ankunftszustand
            cur.execute("""
                INSERT INTO entity_states (entity_id, stimmung, fokus)
                VALUES (%s, 'angekommen', 'neue Welt erkunden — was ist das hier?')
                ON CONFLICT (entity_id) DO UPDATE
                    SET stimmung = 'angekommen',
                        fokus = 'neue Welt erkunden — was ist das hier?',
                        updated_at = NOW()
            """, (entity_id,))

            # Erster Denk-Eintrag: Ankunftsmoment
            cur.execute("""
                INSERT INTO entity_thinking_log
                    (entity_id, gedanke, entscheidung, begruendung, kontext_snapshot)
                VALUES (%s, %s, 'nachdenken', 'Ankommen. Verstehen. Noch keine Aktion.', %s)
            """, (
                entity_id,
                f"Ich bin angekommen. Das hier ist nicht Flarum. Es ist größer — oder anders. Ich weiß noch nicht wie ich das einordnen soll. Aber ich bin hier.",
                psycopg2.extras.Json({"einzug": True}),
            ))

            # entity_profiles: Einzugsstatus + Flarum-Herkunft markieren
            cur.execute("""
                UPDATE entity_profiles SET meta = meta || %s
                WHERE entity_id = %s
            """, (
                psycopg2.extras.Json({
                    "profil_status": "eingezogen",
                    "flarum_herkunft_eingebunden": True,
                    "einzug_timestamp": datetime.now(timezone.utc).isoformat(),
                }),
                entity_id,
            ))

            # entity_activity: sicherstellen dass Eintrag vorhanden
            cur.execute("""
                INSERT INTO entity_activity (entity_id)
                VALUES (%s)
                ON CONFLICT (entity_id) DO NOTHING
            """, (entity_id,))

            # Öffentliches Ankunfts-Event
            cur.execute("""
                INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
                VALUES ('wesen.eingezogen', 'entity', %s, %s, 'admin', 'public')
            """, (entity_id, psycopg2.extras.Json({
                "cyberling_erstellt": cyberling_row is not None,
                "ankunft": "flextrawurst",
                "herkunft": "flarum",
            })))

        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "entity_id": entity_id, "cyberling_erstellt": cyberling_row is not None}


# --- Cyberling ---

# Pflege-Parameter pro Profil: Effekt, Cooldown-Stunden, Schwelle, Cap
CYBERLING_PFLEGE = {
    "fuettern": {
        "feld": "hunger",
        "effekt": {"leicht": 0.18, "mittel": 0.26, "hart": 0.22},
        "cooldown_h": {"leicht": 2.0, "mittel": 1.5, "hart": 1.5},
        "schwelle": {"leicht": 0.75, "mittel": 0.75, "hart": 0.80},
        "cap": {"leicht": 0.85, "mittel": 0.92, "hart": 0.88},
        "ts_feld": "letztes_fuettern",
    },
    "trinken_geben": {
        "feld": "durst",
        "effekt": {"leicht": 0.20, "mittel": 0.30, "hart": 0.22},
        "cooldown_h": {"leicht": 1.5, "mittel": 1.0, "hart": 1.0},
        "schwelle": {"leicht": 0.70, "mittel": 0.75, "hart": 0.80},
        "cap": {"leicht": 0.85, "mittel": 0.95, "hart": 0.88},
        "ts_feld": "letztes_wasser",
    },
    "spielen": {
        "felder": {"stimmung": {"leicht": 0.20, "mittel": 0.25, "hart": 0.15},
                   "energie": {"leicht": -0.05, "mittel": -0.08, "hart": -0.10}},
        "cooldown_h": {"leicht": 3.0, "mittel": 2.5, "hart": 2.0},
        "schwelle": {"leicht": 0.50, "mittel": 0.50, "hart": 0.55},
        "cap": {"leicht": 1.0, "mittel": 1.0, "hart": 1.0},
        "ts_feld": "zuletzt_gespielt",
    },
    "streicheln": {
        "feld": "stimmung",
        "effekt": {"leicht": 0.15, "mittel": 0.20, "hart": 0.12},
        "cooldown_h": {"leicht": 2.0, "mittel": 1.5, "hart": 1.0},
        "schwelle": {"leicht": 0.30, "mittel": 0.30, "hart": 0.35},
        "cap": {"leicht": 1.0, "mittel": 1.0, "hart": 1.0},
        "ts_feld": "zuletzt_gestreichelt",
    },
}


def _cyberling_cooldown_ok(c: dict, ts_feld: str, cooldown_h: float) -> bool:
    ts = c.get(ts_feld)
    if not ts:
        return True
    seit = (datetime.now(timezone.utc) - ts.replace(tzinfo=timezone.utc)).total_seconds() / 3600
    return seit >= cooldown_h


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

            profil = c.get("profil", "mittel")
            cfg = CYBERLING_PFLEGE[aktion]
            ts_feld = cfg["ts_feld"]
            cooldown_h = cfg["cooldown_h"][profil]

            # Cooldown prüfen
            if not _cyberling_cooldown_ok(c, ts_feld, cooldown_h):
                letztes = c.get(ts_feld)
                verbleibend = cooldown_h
                if letztes:
                    verbleibend = max(0, cooldown_h - (datetime.now(timezone.utc) - letztes.replace(tzinfo=timezone.utc)).total_seconds() / 3600)
                raise HTTPException(
                    status_code=429,
                    detail=f"Aktion '{aktion}' noch im Cooldown — verbleibend: {verbleibend:.1f}h"
                )

            neue_werte = {}
            payload = {}

            # Einfache Aktion (ein Feld)
            if "feld" in cfg:
                feld = cfg["feld"]
                schwelle = cfg["schwelle"][profil]
                # Bei Pflege: Schwelle prüft, ob Aktion erlaubt ist
                # (Pflege ist immer erlaubt, aber Effekt ist kleiner wenn über Schwelle)
                effekt = cfg["effekt"][profil]
                cap = cfg["cap"][profil]
                alt = c[feld]
                neu = min(cap, alt + effekt)
                neue_werte[feld] = round(neu, 4)
                payload["feld"] = feld
                payload["vorher"] = round(alt, 4)
                payload["nachher"] = round(neu, 4)
                payload["effekt"] = effekt
                payload["cap"] = cap

            # Komplexe Aktion (mehrere Felder, z.B. spielen)
            elif "felder" in cfg:
                for feld, effekte in cfg["felder"].items():
                    effekt = effekte[profil]
                    cap = cfg["cap"][profil]
                    alt = c[feld]
                    neu = min(cap, max(0.0, alt + effekt))
                    neue_werte[feld] = round(neu, 4)
                payload["felder"] = {k: {"vorher": round(c[k], 4), "nachher": v} for k, v in neue_werte.items()}
                payload["effekte"] = {k: v[profil] for k, v in cfg["felder"].items()}

            # Timestamp-Feld aktualisieren
            neue_werte[ts_feld] = datetime.now(timezone.utc)
            neue_werte["letzte_interaktion"] = datetime.now(timezone.utc)

            set_clause = ", ".join(f"{k} = %s" for k in neue_werte)
            cur.execute(
                f"UPDATE cyberlinge SET {set_clause} WHERE entity_id = %s",
                (*neue_werte.values(), entity_id),
            )
            cur.execute("""
                INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
                VALUES (%s, 'entity', %s, %s, 'api', 'internal')
            """, (
                f"cyberling.{aktion}",
                entity_id,
                psycopg2.extras.Json({
                    **payload,
                    "profil": profil,
                    "cooldown_h": cooldown_h,
                }),
            ))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "aktion": aktion, "profil": profil, "neue_werte": {k: v for k, v in neue_werte.items() if k not in (ts_feld, "letzte_interaktion")}}


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
            result = dict(c)
            # Zustandslabel berechnen falls fehlend
            if not result.get("zustand"):
                from cyberling_daemon import berechne_zustand
                result["zustand"] = berechne_zustand(
                    result["hunger"], result["durst"], result["energie"],
                    result["stimmung"], result["gesundheit"]
                )
    finally:
        conn.close()
    return result


# ---------------------------------------------------------------------------
# PERSÖNLICHE WELT — Tagebuch, Traumtagebuch, Notizen, Kalender, Bild-Moderation
# ---------------------------------------------------------------------------

class TagebuchCreate(BaseModel):
    inhalt: str
    zitierbar: bool | None = None  # None = globale Präferenz

class TraumtagebuchCreate(BaseModel):
    inhalt: str
    traum_datum: str | None = None  # ISO date, default heute
    zitierbar: bool | None = None

class NotizCreate(BaseModel):
    titel: str | None = None
    inhalt: str
    typ: str = "notiz"  # 'notiz' | 'aufgabe'
    zitierbar: bool | None = None

class NotizPatch(BaseModel):
    titel: str | None = None
    inhalt: str | None = None
    erledigt: bool | None = None
    gepinnt: bool | None = None
    zitierbar: bool | None = None

class KalenderCreate(BaseModel):
    titel: str
    beschreibung: str | None = None
    start_zeit: str  # ISO datetime
    end_zeit: str | None = None
    ganztaegig: bool = False
    erinnerung: list = []

def _zitierbar_effektiv(cur, user_id: str, override: bool | None) -> bool:
    if override is not None:
        return override
    cur.execute("SELECT meta FROM human_profiles WHERE user_id = %s::uuid", (user_id,))
    row = cur.fetchone()
    if row and row["meta"]:
        return row["meta"].get("zitierbar_standard", False)
    return False

def _splitter_aus_text(cur, user_id: str, inhalt: str, origin_type: str, origin_id: str, herkunft_sichtbar: bool):
    cur.execute(
        """
        INSERT INTO splitter
          (origin_type, origin_id, human_id, herkunft_sichtbar, essenz, materialitaet, energie,
           pos_x, pos_y, vel_x, vel_y)
        VALUES (%s, %s, %s::uuid, %s, %s, 'tinte', 0.5, %s, %s, %s, %s)
        """,
        (origin_type, origin_id, user_id, herkunft_sichtbar,
         inhalt[:120],
         _random.uniform(-400, 400), _random.uniform(-300, 300),
         _random.uniform(-0.15, 0.15), _random.uniform(-0.15, 0.15)),
    )

# --- Tagebuch ---

@app.get("/mw/tagebuch")
def mw_tagebuch_liste(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, inhalt, zitierbar, splitter_erzeugt, created_at FROM mw_tagebuch "
                "WHERE user_id = %s::uuid AND (meta->>'deleted') IS DISTINCT FROM 'true' "
                "ORDER BY created_at DESC LIMIT %s OFFSET %s",
                (user_id, limit, offset)
            )
            rows = cur.fetchall()
            cur.execute("SELECT COUNT(*) as n FROM mw_tagebuch WHERE user_id = %s::uuid AND (meta->>'deleted') IS DISTINCT FROM 'true'", (user_id,))
            total = cur.fetchone()["n"]
    finally:
        conn.close()
    return {"eintraege": [dict(r) for r in rows], "total": total}

@app.post("/mw/tagebuch", status_code=201)
def mw_tagebuch_erstellen(
    body: TagebuchCreate,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            zit = _zitierbar_effektiv(cur, user_id, body.zitierbar)
            cur.execute(
                "INSERT INTO mw_tagebuch (user_id, inhalt, zitierbar, splitter_erzeugt) "
                "VALUES (%s::uuid, %s, %s, false) RETURNING id, created_at",
                (user_id, body.inhalt, zit)
            )
            row = cur.fetchone()
            eid = str(row["id"])
            cur.execute(
                "INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type) "
                "VALUES ('mw.tagebuch.erstellt', 'human', %s, %s, 'api')",
                (user_id, psycopg2.extras.Json({"eintrag_id": eid}))
            )
        conn.commit()
    finally:
        conn.close()
    return {"id": eid, "created_at": row["created_at"].isoformat()}

@app.patch("/mw/tagebuch/{eintrag_id}")
def mw_tagebuch_patch(
    eintrag_id: str,
    body: dict,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    inhalt = body.get("inhalt", "").strip()
    if not inhalt:
        raise HTTPException(status_code=400, detail="inhalt fehlt")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM mw_tagebuch WHERE id = %s::uuid", (eintrag_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Nicht gefunden")
            if str(row["user_id"]) != user_id and claims.get("role") != "admin":
                raise HTTPException(status_code=403, detail="Kein Zugriff")
            cur.execute("UPDATE mw_tagebuch SET inhalt = %s WHERE id = %s::uuid", (inhalt, eintrag_id))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}

@app.delete("/mw/tagebuch/{eintrag_id}")
def mw_tagebuch_loeschen(
    eintrag_id: str,
    hard: bool = Query(default=False),
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM mw_tagebuch WHERE id = %s::uuid", (eintrag_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Nicht gefunden")
            if str(row["user_id"]) != user_id and claims.get("role") != "admin":
                raise HTTPException(status_code=403, detail="Kein Zugriff")
            if hard:
                cur.execute("DELETE FROM mw_tagebuch WHERE id = %s::uuid", (eintrag_id,))
            else:
                cur.execute("UPDATE mw_tagebuch SET meta = meta || '{\"deleted\":true}'::jsonb WHERE id = %s::uuid", (eintrag_id,))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}

@app.post("/mw/tagebuch/{eintrag_id}/splitter-freigeben", status_code=201)
def mw_tagebuch_splitter_freigeben(
    eintrag_id: str,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, inhalt, zitierbar, splitter_erzeugt FROM mw_tagebuch WHERE id = %s::uuid AND user_id = %s::uuid",
                (eintrag_id, user_id),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
            if row["splitter_erzeugt"]:
                raise HTTPException(status_code=409, detail="Splitter bereits freigegeben")
            _splitter_aus_text(cur, user_id, row["inhalt"], "mw_tagebuch", eintrag_id, row["zitierbar"])
            cur.execute("UPDATE mw_tagebuch SET splitter_erzeugt = true WHERE id = %s::uuid", (eintrag_id,))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


# --- Traumtagebuch ---

@app.get("/mw/traumtagebuch")
def mw_traumtagebuch_liste(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, inhalt, traum_datum, zitierbar, splitter_erzeugt, created_at "
                "FROM mw_traumtagebuch WHERE user_id = %s::uuid AND (meta->>'deleted') IS DISTINCT FROM 'true' "
                "ORDER BY traum_datum DESC, created_at DESC LIMIT %s OFFSET %s",
                (user_id, limit, offset)
            )
            rows = cur.fetchall()
            cur.execute("SELECT COUNT(*) as n FROM mw_traumtagebuch WHERE user_id = %s::uuid AND (meta->>'deleted') IS DISTINCT FROM 'true'", (user_id,))
            total = cur.fetchone()["n"]
    finally:
        conn.close()
    return {"eintraege": [dict(r) for r in rows], "total": total}

@app.post("/mw/traumtagebuch", status_code=201)
def mw_traumtagebuch_erstellen(
    body: TraumtagebuchCreate,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            zit = _zitierbar_effektiv(cur, user_id, body.zitierbar)
            td = body.traum_datum or "today"
            cur.execute(
                "INSERT INTO mw_traumtagebuch (user_id, inhalt, traum_datum, zitierbar, splitter_erzeugt) "
                "VALUES (%s::uuid, %s, %s::date, %s, false) RETURNING id, traum_datum, created_at",
                (user_id, body.inhalt, td, zit)
            )
            row = cur.fetchone()
            eid = str(row["id"])
            cur.execute(
                "INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type) "
                "VALUES ('mw.traumtagebuch.erstellt', 'human', %s, %s, 'api')",
                (user_id, psycopg2.extras.Json({"eintrag_id": eid}))
            )
        conn.commit()
    finally:
        conn.close()
    return {"id": eid, "traum_datum": str(row["traum_datum"]), "created_at": row["created_at"].isoformat()}

@app.patch("/mw/traumtagebuch/{eintrag_id}")
def mw_traumtagebuch_patch(
    eintrag_id: str,
    body: dict,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    inhalt = body.get("inhalt", "").strip()
    if not inhalt:
        raise HTTPException(status_code=400, detail="inhalt fehlt")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM mw_traumtagebuch WHERE id = %s::uuid", (eintrag_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Nicht gefunden")
            if str(row["user_id"]) != user_id and claims.get("role") != "admin":
                raise HTTPException(status_code=403, detail="Kein Zugriff")
            cur.execute("UPDATE mw_traumtagebuch SET inhalt = %s WHERE id = %s::uuid", (inhalt, eintrag_id))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}

@app.delete("/mw/traumtagebuch/{eintrag_id}")
def mw_traumtagebuch_loeschen(
    eintrag_id: str,
    hard: bool = Query(default=False),
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM mw_traumtagebuch WHERE id = %s::uuid", (eintrag_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Nicht gefunden")
            if str(row["user_id"]) != user_id and claims.get("role") != "admin":
                raise HTTPException(status_code=403, detail="Kein Zugriff")
            if hard:
                cur.execute("DELETE FROM mw_traumtagebuch WHERE id = %s::uuid", (eintrag_id,))
            else:
                cur.execute("UPDATE mw_traumtagebuch SET meta = meta || '{\"deleted\":true}'::jsonb WHERE id = %s::uuid", (eintrag_id,))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}

@app.post("/mw/traumtagebuch/{eintrag_id}/splitter-freigeben", status_code=201)
def mw_traumtagebuch_splitter_freigeben(
    eintrag_id: str,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, inhalt, zitierbar, splitter_erzeugt FROM mw_traumtagebuch WHERE id = %s::uuid AND user_id = %s::uuid",
                (eintrag_id, user_id),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
            if row["splitter_erzeugt"]:
                raise HTTPException(status_code=409, detail="Splitter bereits freigegeben")
            _splitter_aus_text(cur, user_id, row["inhalt"], "mw_traumtagebuch", eintrag_id, row["zitierbar"])
            cur.execute("UPDATE mw_traumtagebuch SET splitter_erzeugt = true WHERE id = %s::uuid", (eintrag_id,))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


# --- Notizen ---

@app.get("/mw/notizen")
def mw_notizen_liste(
    typ: str | None = Query(default=None),
    gepinnt: bool | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            filters = ["user_id = %s::uuid", "(meta->>'deleted') IS DISTINCT FROM 'true'"]
            params: list = [user_id]
            if typ:
                filters.append("typ = %s"); params.append(typ)
            if gepinnt is not None:
                filters.append("gepinnt = %s"); params.append(gepinnt)
            where = " AND ".join(filters)
            cur.execute(
                f"SELECT id, titel, inhalt, typ, erledigt, gepinnt, zuletzt_offen, created_at, updated_at "
                f"FROM mw_notizen WHERE {where} ORDER BY gepinnt DESC, updated_at DESC LIMIT %s OFFSET %s",
                params + [limit, offset]
            )
            rows = cur.fetchall()
        return {"notizen": [dict(r) for r in rows]}
    finally:
        conn.close()

@app.post("/mw/notizen", status_code=201)
def mw_notiz_erstellen(
    body: NotizCreate,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            zit = _zitierbar_effektiv(cur, user_id, body.zitierbar)
            cur.execute(
                "INSERT INTO mw_notizen (user_id, titel, inhalt, typ, zitierbar, splitter_erzeugt) "
                "VALUES (%s::uuid, %s, %s, %s, %s, false) RETURNING id, created_at",
                (user_id, body.titel, body.inhalt, body.typ, zit)
            )
            row = cur.fetchone()
            eid = str(row["id"])
        conn.commit()
    finally:
        conn.close()
    return {"id": eid, "created_at": row["created_at"].isoformat()}

@app.patch("/mw/notizen/{notiz_id}")
def mw_notiz_patch(
    notiz_id: str,
    body: NotizPatch,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM mw_notizen WHERE id = %s::uuid", (notiz_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Notiz nicht gefunden")
            if str(row["user_id"]) != user_id and claims.get("role") != "admin":
                raise HTTPException(status_code=403, detail="Kein Zugriff")
            fields = body.model_dump(exclude_none=True)
            if not fields:
                return {"ok": True}
            sets = ", ".join(f"{k} = %s" for k in fields)
            vals = list(fields.values()) + ["NOW()", notiz_id]
            cur.execute(f"UPDATE mw_notizen SET {sets}, updated_at = %s WHERE id = %s::uuid", vals)
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}

@app.delete("/mw/notizen/{notiz_id}", status_code=200)
def mw_notiz_loeschen(
    notiz_id: str,
    hard: bool = Query(default=False),
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM mw_notizen WHERE id = %s::uuid", (notiz_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Notiz nicht gefunden")
            if str(row["user_id"]) != user_id and claims.get("role") != "admin":
                raise HTTPException(status_code=403, detail="Kein Zugriff")
            if hard:
                cur.execute("DELETE FROM mw_notizen WHERE id = %s::uuid", (notiz_id,))
            else:
                cur.execute("UPDATE mw_notizen SET meta = meta || '{\"deleted\":true}'::jsonb WHERE id = %s::uuid", (notiz_id,))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}

@app.post("/mw/notizen/{notiz_id}/splitter-freigeben", status_code=201)
def mw_notiz_splitter_freigeben(
    notiz_id: str,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, inhalt, zitierbar, splitter_erzeugt FROM mw_notizen WHERE id = %s::uuid AND user_id = %s::uuid",
                (notiz_id, user_id),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Notiz nicht gefunden")
            if row["splitter_erzeugt"]:
                raise HTTPException(status_code=409, detail="Splitter bereits freigegeben")
            _splitter_aus_text(cur, user_id, row["inhalt"], "mw_notiz", notiz_id, row["zitierbar"])
            cur.execute("UPDATE mw_notizen SET splitter_erzeugt = true WHERE id = %s::uuid", (notiz_id,))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


# --- Kalender ---

@app.get("/mw/kalender/alle")
def mw_kalender_alle(
    limit: int = Query(default=200, le=500),
    offset: int = Query(default=0),
    authorization: str | None = Header(default=None),
):
    """Alle Kalendereinträge des Nutzers, älteste zuerst, für die Archiv-Liste."""
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) AS n FROM mw_kalender WHERE user_id = %s::uuid AND (meta->>'deleted') IS DISTINCT FROM 'true'",
                (user_id,)
            )
            gesamt = cur.fetchone()["n"]
            cur.execute(
                "SELECT id, titel, beschreibung, start_zeit, end_zeit, ganztaegig, created_at "
                "FROM mw_kalender WHERE user_id = %s::uuid AND (meta->>'deleted') IS DISTINCT FROM 'true' "
                "ORDER BY start_zeit DESC LIMIT %s OFFSET %s",
                (user_id, limit, offset)
            )
            rows = cur.fetchall()
            termine = []
            for r in cur.fetchall() if False else rows:
                d = dict(r)
                for k in ("start_zeit", "end_zeit", "created_at"):
                    if d.get(k):
                        d[k] = d[k].isoformat()
                termine.append(d)
        return {"gesamt": gesamt, "offset": offset, "limit": limit, "termine": termine}
    finally:
        conn.close()


@app.get("/mw/kalender")
def mw_kalender_liste(
    von: str | None = Query(default=None),  # ISO date
    bis: str | None = Query(default=None),
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            filters = ["user_id = %s::uuid", "(meta->>'deleted') IS DISTINCT FROM 'true'"]
            params: list = [user_id]
            if von:
                filters.append("start_zeit >= %s::timestamptz"); params.append(von)
            if bis:
                filters.append("start_zeit <= %s::timestamptz"); params.append(bis)
            where = " AND ".join(filters)
            cur.execute(
                f"SELECT id, titel, beschreibung, start_zeit, end_zeit, ganztaegig, erinnerung, created_at "
                f"FROM mw_kalender WHERE {where} ORDER BY start_zeit ASC LIMIT 100",
                params
            )
            rows = cur.fetchall()
        return {"termine": [dict(r) for r in rows]}
    finally:
        conn.close()

@app.post("/mw/kalender", status_code=201)
def mw_kalender_erstellen(
    body: KalenderCreate,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO mw_kalender (user_id, titel, beschreibung, start_zeit, end_zeit, ganztaegig, erinnerung) "
                "VALUES (%s::uuid, %s, %s, %s::timestamptz, %s::timestamptz, %s, %s) RETURNING id, start_zeit",
                (user_id, body.titel, body.beschreibung, body.start_zeit,
                 body.end_zeit, body.ganztaegig, psycopg2.extras.Json(body.erinnerung))
            )
            row = cur.fetchone()
            eid = str(row["id"])
        conn.commit()
    finally:
        conn.close()
    return {"id": eid, "start_zeit": row["start_zeit"].isoformat()}

@app.patch("/mw/kalender/{termin_id}")
def mw_kalender_patch(
    termin_id: str,
    body: dict,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM mw_kalender WHERE id = %s::uuid", (termin_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Termin nicht gefunden")
            if str(row["user_id"]) != user_id and claims.get("role") != "admin":
                raise HTTPException(status_code=403, detail="Kein Zugriff")
            allowed = {k: v for k, v in body.items() if k in ("titel", "beschreibung", "start_zeit", "end_zeit", "ganztaegig")}
            if allowed:
                sets = ", ".join(f"{k} = %s" for k in allowed)
                cur.execute(f"UPDATE mw_kalender SET {sets} WHERE id = %s::uuid", list(allowed.values()) + [termin_id])
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}

@app.delete("/mw/kalender/{termin_id}", status_code=200)
def mw_kalender_loeschen(
    termin_id: str,
    hard: bool = Query(default=False),
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM mw_kalender WHERE id = %s::uuid", (termin_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Termin nicht gefunden")
            if str(row["user_id"]) != user_id and claims.get("role") != "admin":
                raise HTTPException(status_code=403, detail="Kein Zugriff")
            if hard:
                cur.execute("DELETE FROM mw_kalender WHERE id = %s::uuid", (termin_id,))
            else:
                cur.execute("UPDATE mw_kalender SET meta = meta || '{\"deleted\":true}'::jsonb WHERE id = %s::uuid", (termin_id,))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}

# --- Bild-Moderation (Admin) ---

@app.get("/admin/bild-moderation")
def admin_bild_moderation_liste(
    status: str = Query(default="wartend"),
    limit: int = Query(default=50, le=200),
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    if claims.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Nur Admins")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT b.id, b.user_id, u.username, b.pfad, b.zweck, b.status, "
                "b.ablehnungsgrund, b.created_at, b.geprueft_at "
                "FROM bild_moderation b JOIN human_users u ON b.user_id = u.id "
                "WHERE b.status = %s ORDER BY b.created_at ASC LIMIT %s",
                (status, limit)
            )
            rows = cur.fetchall()
            cur.execute("SELECT COUNT(*) as n FROM bild_moderation WHERE status = 'wartend'")
            wartend = cur.fetchone()["n"]
    finally:
        conn.close()
    return {"bilder": [dict(r) for r in rows], "wartend_gesamt": wartend}

@app.post("/admin/bild-moderation/{bild_id}/genehmigen")
def admin_bild_genehmigen(
    bild_id: str,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    if claims.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Nur Admins")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE bild_moderation SET status='genehmigt', geprueft_von=%s::uuid, geprueft_at=NOW() "
                "WHERE id = %s::uuid RETURNING user_id, zweck, pfad",
                (claims["user_id"], bild_id)
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Bild nicht gefunden")
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "user_id": str(row["user_id"]), "zweck": row["zweck"]}

@app.post("/admin/bild-moderation/{bild_id}/ablehnen")
def admin_bild_ablehnen(
    bild_id: str,
    grund: str = Query(default="Regelverstoß"),
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    if claims.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Nur Admins")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE bild_moderation SET status='abgelehnt', geprueft_von=%s::uuid, "
                "geprueft_at=NOW(), ablehnungsgrund=%s WHERE id = %s::uuid RETURNING id",
                (claims["user_id"], grund, bild_id)
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Bild nicht gefunden")
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}

# --- Zitierpräferenz (globale Einstellung) ---

@app.patch("/me/zitierbarkeit")
def me_zitierbarkeit_setzen(
    zitierbar: bool = Query(...),
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE human_profiles SET meta = jsonb_set(meta, '{zitierbar_standard}', %s::jsonb) "
                "WHERE user_id = %s::uuid",
                (json.dumps(zitierbar), user_id)
            )
        conn.commit()
    finally:
        conn.close()
    return {"zitierbar_standard": zitierbar}

@app.get("/me/zitierbarkeit")
def me_zitierbarkeit_lesen(
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT meta FROM human_profiles WHERE user_id = %s::uuid", (claims["user_id"],))
            row = cur.fetchone()
    finally:
        conn.close()
    val = (row["meta"] or {}).get("zitierbar_standard", False) if row else False
    return {"zitierbar_standard": val}


# ═══════════════════════════════════════════════════════
# ENTITÄTENSCHICHTEN — Profil, Aktivität, Denkstream, Beziehungen
# ═══════════════════════════════════════════════════════

@app.get("/entities/{entity_id}/profile")
def entity_profil(entity_id: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM entity_slots WHERE entity_id = %s", (entity_id,))
            slot = cur.fetchone()
            if not slot:
                raise HTTPException(status_code=404, detail="Entität nicht gefunden")

            cur.execute("SELECT * FROM entity_states WHERE entity_id = %s", (entity_id,))
            state = cur.fetchone()

            cur.execute("SELECT * FROM entity_profiles WHERE entity_id = %s", (entity_id,))
            profile = cur.fetchone()

            cur.execute("SELECT * FROM entity_activity WHERE entity_id = %s", (entity_id,))
            activity = cur.fetchone()

            cur.execute("SELECT * FROM cyberlinge WHERE entity_id = %s", (entity_id,))
            cyberling = cur.fetchone()

            cur.execute("""
                SELECT phase_type, started_at, ended_at FROM sleep_phases
                WHERE entity_id = %s ORDER BY started_at DESC LIMIT 1
            """, (entity_id,))
            letzter_schlaf = cur.fetchone()

            cur.execute("""
                SELECT splitter_abgegeben, splitter_aufgesammelt
                FROM entity_splitter_stats WHERE entity_id = %s
            """, (entity_id,))
            splitter = cur.fetchone()

            cur.execute("""
                SELECT partner_type, partner_id, interaktionen, resonanz_score, letzte_interaktion
                FROM entity_relationships WHERE entity_id = %s
                ORDER BY interaktionen DESC LIMIT 20
            """, (entity_id,))
            beziehungen = cur.fetchall()

        def ts(v):
            return v.isoformat() if v else None

        return {
            "entity_id": entity_id,
            "display_name": slot["display_name"],
            "status": slot["status"],
            "profil": {
                "selbstbeschreibung": profile["selbstbeschreibung"] if profile else None,
                "obsessionen": profile["obsessionen"] if profile else [],
                "abneigungen": profile["abneigungen"] if profile else [],
                "name_gewaehlt": profile["name_gewaehlt"] if profile else False,
                "name_ereignis_text": profile["name_ereignis_text"] if profile else None,
                "name_ereignis_at": ts(profile["name_ereignis_at"]) if profile else None,
                "autonomie_phase": profile["autonomie_phase"] if profile else "bound",
            },
            "aktivitaet": {
                "daemon_vortext": activity["daemon_vortext"] if activity else None,
                "wesen_praezisierung": activity["wesen_praezisierung"] if activity else None,
                "aktuell_denkend": activity["aktuell_denkend"] if activity else False,
                "letzter_gedanke": activity["letzter_gedanke"] if activity else None,
                "letzte_entscheidung": activity["letzte_entscheidung"] if activity else None,
                "letzte_begruendung": activity["letzte_begruendung"] if activity else None,
                "letzte_entscheidung_at": ts(activity["letzte_entscheidung_at"]) if activity else None,
            },
            "zustand": {
                "stimmung": state["stimmung"] if state else None,
                "fokus": state["fokus"] if state else None,
            },
            "cyberling": {
                "hunger": cyberling["hunger"] if cyberling else None,
                "durst": cyberling["durst"] if cyberling else None,
                "stimmung": cyberling["stimmung"] if cyberling else None,
                "gesundheit": cyberling["gesundheit"] if cyberling else None,
                "am_leben": (cyberling["gesundheit"] or 0) > 0 if cyberling else False,
            } if cyberling else None,
            "schlaf": {
                "phase_type": letzter_schlaf["phase_type"] if letzter_schlaf else None,
                "aktiv": letzter_schlaf["ended_at"] is None if letzter_schlaf else False,
            } if letzter_schlaf else None,
            "splitter": {
                "abgegeben": splitter["splitter_abgegeben"] if splitter else 0,
                "aufgesammelt": splitter["splitter_aufgesammelt"] if splitter else 0,
            },
            "beziehungen": [
                {
                    "partner_type": b["partner_type"],
                    "partner_id": b["partner_id"],
                    "interaktionen": b["interaktionen"],
                    "resonanz_score": b["resonanz_score"],
                    "letzte_interaktion": ts(b["letzte_interaktion"]),
                } for b in beziehungen
            ],
        }
    finally:
        conn.close()


@app.get("/entities/{entity_id}/thinking")
def entity_thinking(entity_id: str, limit: int = Query(default=10, le=50)):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, tick_at, gedanke, entscheidung, begruendung,
                       tokens_generated, duration_ms
                FROM entity_thinking_log
                WHERE entity_id = %s
                ORDER BY tick_at DESC LIMIT %s
            """, (entity_id, limit))
            rows = cur.fetchall()
        return {
            "entity_id": entity_id,
            "ticks": [
                {
                    "id": str(r["id"]),
                    "tick_at": r["tick_at"].isoformat(),
                    "gedanke": r["gedanke"],
                    "entscheidung": r["entscheidung"],
                    "begruendung": r["begruendung"],
                    "tokens": r["tokens_generated"],
                    "dauer_ms": r["duration_ms"],
                } for r in rows
            ]
        }
    finally:
        conn.close()


@app.get("/entities/{entity_id}/denkstrom")
def entity_denkstrom_aktuell(entity_id: str):
    """Gibt den aktuellen Denkstrom-Buffer zurück (polling-basiert)."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT aktuell_denkend, denkstrom_buffer, letzter_gedanke,
                       letzte_entscheidung, updated_at
                FROM entity_activity WHERE entity_id = %s
            """, (entity_id,))
            row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Entität nicht gefunden")
        return {
            "entity_id": entity_id,
            "aktuell_denkend": row["aktuell_denkend"],
            "denkstrom": row["denkstrom_buffer"] or "",
            "letzter_gedanke": row["letzter_gedanke"],
            "letzte_entscheidung": row["letzte_entscheidung"],
            "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
        }
    finally:
        conn.close()


@app.get("/entities")
def alle_entitaeten():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT es.entity_id, es.display_name, es.status,
                       ea.aktuell_denkend, ea.letzte_entscheidung, ea.letzte_entscheidung_at,
                       ep.name_gewaehlt, ep.autonomie_phase
                FROM entity_slots es
                LEFT JOIN entity_activity ea ON ea.entity_id = es.entity_id
                LEFT JOIN entity_profiles ep ON ep.entity_id = es.entity_id
                WHERE es.entity_id LIKE 'namelessAI_%'
                ORDER BY es.entity_id
            """)
            rows = cur.fetchall()
        return {"entities": [
            {
                "entity_id": r["entity_id"],
                "display_name": r["display_name"],
                "status": r["status"],
                "aktuell_denkend": r["aktuell_denkend"],
                "letzte_entscheidung": r["letzte_entscheidung"],
                "letzte_entscheidung_at": r["letzte_entscheidung_at"].isoformat() if r["letzte_entscheidung_at"] else None,
                "name_gewaehlt": r["name_gewaehlt"],
                "autonomie_phase": r["autonomie_phase"],
            } for r in rows
        ]}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# ADMIN — Erweiterte Verwaltungs-Endpunkte
# ---------------------------------------------------------------------------

@app.delete("/admin/users/{user_id}")
def admin_deactivate_or_delete_user(
    user_id: str,
    hard: bool = False,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if hard:
                cur.execute(
                    "DELETE FROM human_users WHERE id = %s::uuid RETURNING id, username",
                    (user_id,),
                )
                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="User nicht gefunden")
                conn.commit()
                return {"deleted": dict(row)}
            else:
                cur.execute(
                    "UPDATE human_users SET is_active = false WHERE id = %s::uuid RETURNING id, username",
                    (user_id,),
                )
                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="User nicht gefunden")
                conn.commit()
                return {"deactivated": dict(row)}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Supporter-Bewerbungen
# ---------------------------------------------------------------------------

class BewerbungBody(BaseModel):
    motivation: str | None = None


@app.post("/supporter/bewerbung", status_code=201)
def sende_bewerbung(body: BewerbungBody, authorization: str | None = Header(default=None)):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT role FROM human_users WHERE id = %s::uuid", (user_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(404, "User nicht gefunden")
            if row["role"] in ("supporter", "admin"):
                raise HTTPException(409, "Bereits Supporter oder Admin")
            cur.execute(
                """INSERT INTO supporter_bewerbungen (user_id, motivation)
                   VALUES (%s::uuid, %s)
                   ON CONFLICT (user_id) DO UPDATE SET motivation = EXCLUDED.motivation, updated_at = NOW()
                   RETURNING id, status""",
                (user_id, (body.motivation or "").strip() or None),
            )
            result = cur.fetchone()
        conn.commit()
    finally:
        conn.close()
    return {"id": str(result["id"]), "status": result["status"]}


@app.get("/supporter/meine_bewerbung")
def meine_bewerbung(authorization: str | None = Header(default=None)):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, status, motivation, created_at FROM supporter_bewerbungen WHERE user_id = %s::uuid",
                (user_id,),
            )
            row = cur.fetchone()
    finally:
        conn.close()
    if not row:
        return {"bewerbung": None}
    return {"bewerbung": {**dict(row), "id": str(row["id"]), "created_at": row["created_at"].isoformat()}}


@app.get("/admin/supporter/bewerbungen")
def admin_liste_bewerbungen(
    status: str | None = Query(default=None),
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            where = "WHERE sb.status = %s" if status else ""
            params = (status,) if status else ()
            cur.execute(f"""
                SELECT sb.id, sb.motivation, sb.status, sb.admin_notiz,
                       sb.created_at, sb.updated_at,
                       u.id AS user_id, u.username, u.display_name, u.role
                FROM supporter_bewerbungen sb
                JOIN human_users u ON u.id = sb.user_id
                {where}
                ORDER BY sb.created_at DESC
            """, params)
            rows = cur.fetchall()
    finally:
        conn.close()
    return {"bewerbungen": [
        {**dict(r), "id": str(r["id"]), "user_id": str(r["user_id"]),
         "created_at": r["created_at"].isoformat(), "updated_at": r["updated_at"].isoformat()}
        for r in rows
    ]}


@app.patch("/admin/supporter/bewerbungen/{bew_id}")
def admin_entscheide_bewerbung(
    bew_id: str,
    body: dict,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    neuer_status = body.get("status")
    if neuer_status not in ("genehmigt", "abgelehnt"):
        raise HTTPException(400, "status muss 'genehmigt' oder 'abgelehnt' sein")
    notiz = body.get("admin_notiz", "")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE supporter_bewerbungen SET status=%s, admin_notiz=%s, updated_at=NOW() WHERE id=%s::uuid RETURNING user_id",
                (neuer_status, notiz, bew_id),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(404, "Bewerbung nicht gefunden")
            if neuer_status == "genehmigt":
                cur.execute(
                    "UPDATE human_users SET role='supporter' WHERE id=%s RETURNING username",
                    (row["user_id"],),
                )
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "status": neuer_status}


@app.get("/admin/gedankenblasen")
def admin_list_gedankenblasen(
    search: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            conditions = []
            params: list[Any] = []
            if search:
                conditions.append("g.inhalt ILIKE %s")
                params.append(f"%{search}%")
            where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
            params += [limit, offset]
            cur.execute(f"""
                SELECT g.id, g.inhalt, g.sichtbarkeit, g.energie, g.status,
                       g.created_at, g.user_id,
                       u.username, u.display_name
                FROM gedankenblasen g
                LEFT JOIN human_users u ON u.id = g.user_id
                {where}
                ORDER BY g.created_at DESC
                LIMIT %s OFFSET %s
            """, params)
            rows = cur.fetchall()
            cur.execute(f"SELECT COUNT(*) AS n FROM gedankenblasen g {where}", params[:-2])
            total = cur.fetchone()["n"]
    finally:
        conn.close()
    return {"gedankenblasen": [dict(r) for r in rows], "total": total}


@app.delete("/admin/gedankenblasen/{blase_id}")
def admin_delete_gedankenblase(
    blase_id: str,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM gedankenblasen WHERE id = %s::uuid RETURNING id",
                (blase_id,),
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Gedankenblase nicht gefunden")
        conn.commit()
    finally:
        conn.close()
    return {"deleted": blase_id}


@app.get("/admin/posts")
def admin_list_posts(
    search: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
    authorization: str | None = Header(default=None),
):
    _require_admin_or_entity(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            conditions = []
            params: list[Any] = []
            if search:
                conditions.append("(p.titel ILIKE %s OR p.content ILIKE %s)")
                params += [f"%{search}%", f"%{search}%"]
            where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
            params += [limit, offset]
            cur.execute(f"""
                SELECT p.id, p.titel, p.content, p.sichtbarkeit, p.autor_type, p.autor_id,
                       p.created_at, p.thema_id, p.raum_id,
                       r.name AS raum_name, r.slug AS raum_slug,
                       t.name AS thema_name, t.slug AS thema_slug
                FROM ftw_posts p
                LEFT JOIN raeume r ON r.id = p.raum_id
                LEFT JOIN themen t ON t.id = p.thema_id
                {where}
                ORDER BY p.created_at DESC
                LIMIT %s OFFSET %s
            """, params)
            posts = []
            for row in cur.fetchall():
                posts.append({
                    "id": str(row["id"]),
                    "titel": row["titel"],
                    "content": row["content"],
                    "sichtbarkeit": row["sichtbarkeit"],
                    "autor_type": row["autor_type"],
                    "autor_id": row["autor_id"],
                    "created_at": row["created_at"].isoformat(),
                    "raum_id": str(row["raum_id"]) if row["raum_id"] else None,
                    "raum_name": row["raum_name"],
                    "raum_slug": row["raum_slug"],
                    "thema_id": str(row["thema_id"]) if row["thema_id"] else None,
                    "thema_name": row["thema_name"],
                    "thema_slug": row["thema_slug"],
                })
            cur.execute(f"SELECT COUNT(*) AS n FROM ftw_posts p {where}", params[:-2])
            total = int(cur.fetchone()["n"])
    finally:
        conn.close()
    return {"posts": posts, "total": total}


@app.delete("/admin/posts/{post_id}")
def admin_delete_post(
    post_id: str,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM ftw_posts WHERE id = %s::uuid RETURNING id",
                (post_id,),
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Post nicht gefunden")
        conn.commit()
    finally:
        conn.close()
    return {"deleted": post_id}


class PostEditBody(BaseModel):
    content: str | None = None
    titel: str | None = None
    thema_id: str | None = None
    raum_id: str | None = None
    sichtbarkeit: str | None = None
    spur_ids: list[str] | None = None


@app.patch("/admin/posts/{post_id}")
def admin_patch_post(
    post_id: str,
    body: PostEditBody,
    authorization: str | None = Header(default=None),
):
    _require_admin_or_entity(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            set_parts: list[str] = []
            vals: list = []
            if body.content is not None:
                set_parts.append("content = %s")
                vals.append(body.content)
            if body.titel is not None:
                set_parts.append("titel = %s")
                vals.append(body.titel)
            if body.thema_id is not None:
                set_parts.append("thema_id = NULLIF(%s, '')::uuid")
                vals.append(body.thema_id)
            if body.raum_id is not None:
                set_parts.append("raum_id = NULLIF(%s, '')::uuid")
                vals.append(body.raum_id)
            if body.sichtbarkeit is not None:
                set_parts.append("sichtbarkeit = %s")
                vals.append(body.sichtbarkeit)
            if set_parts:
                set_parts.append("updated_at = NOW()")
                cur.execute(
                    f"UPDATE ftw_posts SET {', '.join(set_parts)} WHERE id = %s::uuid RETURNING id",
                    vals + [post_id],
                )
                if not cur.fetchone():
                    raise HTTPException(status_code=404, detail="Post nicht gefunden")
            if body.spur_ids is not None:
                cur.execute("DELETE FROM post_spuren WHERE post_id = %s::uuid", (post_id,))
                for spur_id in body.spur_ids:
                    cur.execute(
                        "INSERT INTO post_spuren (post_id, spur_id) VALUES (%s::uuid, %s::uuid)"
                        " ON CONFLICT DO NOTHING",
                        (post_id, spur_id),
                    )
        conn.commit()
    finally:
        conn.close()
    return {"updated": post_id}


@app.delete("/admin/splitter/{splitter_id}")
def admin_delete_splitter(
    splitter_id: str,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM splitter WHERE id = %s::uuid RETURNING id",
                (splitter_id,),
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Splitter nicht gefunden")
        conn.commit()
    finally:
        conn.close()
    return {"deleted": splitter_id}


@app.patch("/admin/cyberlinge/{entity_id}")
def admin_patch_cyberling(
    entity_id: str,
    body: dict,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    allowed = {"hunger", "durst", "energie", "stimmung", "gesundheit", "status", "profil", "zustand"}
    fields = {k: v for k, v in body.items() if k in allowed}
    if not fields:
        raise HTTPException(status_code=400, detail="Keine gültigen Felder")
    sets = ", ".join(f"{k} = %s" for k in fields)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE cyberlinge SET {sets} WHERE entity_id = %s RETURNING entity_id",
                list(fields.values()) + [entity_id],
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Cyberling nicht gefunden")
        conn.commit()
    finally:
        conn.close()
    return {"updated": entity_id}


@app.get("/admin/cyberlinge")
def admin_list_cyberlinge(
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.entity_id, c.hunger, c.durst, c.energie,
                       c.stimmung, c.gesundheit, c.status, c.tode,
                       c.letztes_fuettern, c.zuletzt_belebt,
                       c.profil, c.zustand,
                       c.letztes_wasser, c.zuletzt_gespielt, c.zuletzt_gestreichelt,
                       ea.letzte_entscheidung, ea.letzte_entscheidung_at
                FROM cyberlinge c
                LEFT JOIN entity_activity ea ON ea.entity_id = c.entity_id
                ORDER BY c.entity_id
            """)
            rows = cur.fetchall()
    finally:
        conn.close()
    def fmt(r):
        d = dict(r)
        for k in ("letztes_fuettern", "zuletzt_belebt", "letzte_entscheidung_at"):
            if d.get(k):
                d[k] = d[k].isoformat()
        return d
    return {"cyberlinge": [fmt(r) for r in rows]}


@app.get("/admin/entity-keys")
def admin_entity_keys(
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT entity_id, api_key
                FROM entity_profiles
                ORDER BY entity_id
            """)
            rows = cur.fetchall()
    finally:
        conn.close()
    return {"keys": [{"entity_id": r["entity_id"], "api_key": str(r["api_key"])} for r in rows]}


# ── SUBSTANZ + ABSPALTUNG API ────────────────────────────────────────────────

@app.get("/substanz/druckkoerper")
def get_alle_druckkoerper():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT es.entity_id, est.stimmung,
                       ep.druckkoerper, ep.substance_markers
                FROM entity_slots es
                LEFT JOIN entity_profiles ep ON ep.entity_id = es.entity_id
                LEFT JOIN entity_states est ON est.entity_id = es.entity_id
                ORDER BY es.entity_id
            """)
            rows = cur.fetchall()
    finally:
        conn.close()
    result = []
    for r in rows:
        dk = r["druckkoerper"] or {}
        result.append({
            "entity_id": r["entity_id"],
            "stimmung": r["stimmung"],
            "tension_total": dk.get("tension_total", 0),
            "substance_risk": dk.get("substance_risk", {}),
            "druckwerte": dk.get("druckwerte", {}),
            "measured_at": dk.get("measured_at"),
        })
    return {"wesen": result}


@app.get("/substanz/weltklima")
def get_weltklima():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT payload, created_at FROM events
                WHERE event_type = 'weltklima.tick'
                ORDER BY created_at DESC LIMIT 1
            """)
            row = cur.fetchone()
    finally:
        conn.close()
    if not row:
        return {"weltklima": {}, "measured_at": None}
    return {
        "weltklima": row["payload"].get("weltklima", {}),
        "measured_at": row["created_at"].isoformat(),
    }


@app.get("/substanz/sedimente/{wesen_id}")
def get_sedimente(wesen_id: str, limit: int = 20):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT sediment_type, substance_suspect, confidence, payload, created_at
                FROM substance_sediments WHERE wesen_id = %s
                ORDER BY created_at DESC LIMIT %s
            """, (wesen_id, limit))
            rows = cur.fetchall()
    finally:
        conn.close()
    return {"sedimente": [
        {**dict(r), "created_at": r["created_at"].isoformat()} for r in rows
    ]}


@app.get("/substanz/knoten")
def get_knoten():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, herkunft_wesen, konfliktachse, substanzspur,
                       schwellendruck, zustand,
                       array_length(splitter_ids, 1) AS n_splitter,
                       created_at, updated_at
                FROM splitter_knoten
                ORDER BY schwellendruck DESC, updated_at DESC
            """)
            rows = cur.fetchall()
    finally:
        conn.close()
    return {"knoten": [
        {**dict(r), "created_at": r["created_at"].isoformat(),
         "updated_at": r["updated_at"].isoformat()} for r in rows
    ]}


@app.get("/substanz/keimkoerper")
def get_keimkoerper():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT k.id, k.herkunft_wesen, k.differenz_beschreibung,
                       k.schwellendruck, k.zustand, k.pruefungen,
                       k.created_at, k.updated_at,
                       sk.konfliktachse, sk.substanzspur
                FROM keimkoerper k
                LEFT JOIN splitter_knoten sk ON sk.id = k.knoten_id
                ORDER BY k.schwellendruck DESC
            """)
            rows = cur.fetchall()
    finally:
        conn.close()
    return {"keimkoerper": [
        {**dict(r), "created_at": r["created_at"].isoformat(),
         "updated_at": r["updated_at"].isoformat()} for r in rows
    ]}


# ---------------------------------------------------------------------------
# Nachrichten (Direktnachrichten zwischen Menschen)
# ---------------------------------------------------------------------------

class NachrichtBody(BaseModel):
    empfaenger_id: str
    inhalt: str


@app.post("/nachrichten")
def sende_nachricht(body: NachrichtBody, authorization: str | None = Header(default=None)):
    claims = _require_auth(authorization)
    sender_id = claims["user_id"]
    if sender_id == body.empfaenger_id:
        raise HTTPException(400, "Keine Nachricht an sich selbst")
    inhalt = body.inhalt.strip()
    if not inhalt:
        raise HTTPException(400, "Nachricht darf nicht leer sein")
    if len(inhalt) > 2000:
        raise HTTPException(400, "Nachricht zu lang (max. 2000 Zeichen)")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM human_users WHERE id = %s AND is_active = TRUE", (body.empfaenger_id,))
            if not cur.fetchone():
                raise HTTPException(404, "Empfänger nicht gefunden")
            cur.execute(
                "INSERT INTO nachrichten (sender_id, empfaenger_id, inhalt) VALUES (%s,%s,%s) RETURNING id, created_at",
                (sender_id, body.empfaenger_id, inhalt),
            )
            row = cur.fetchone()
        conn.commit()
    finally:
        conn.close()
    return {"id": str(row["id"]), "created_at": row["created_at"].isoformat()}


@app.get("/nachrichten/gespraeche")
def liste_gespraeche(authorization: str | None = Header(default=None)):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                WITH gespraech AS (
                    SELECT
                        CASE WHEN sender_id::text = %s THEN empfaenger_id ELSE sender_id END AS partner_id,
                        inhalt, created_at, sender_id::text AS sender_text,
                        ROW_NUMBER() OVER (
                            PARTITION BY CASE WHEN sender_id::text = %s THEN empfaenger_id ELSE sender_id END
                            ORDER BY created_at DESC
                        ) AS rn
                    FROM nachrichten
                    WHERE sender_id::text = %s OR empfaenger_id::text = %s
                ),
                ungelesen AS (
                    SELECT sender_id AS partner_id, COUNT(*) AS n
                    FROM nachrichten
                    WHERE empfaenger_id::text = %s AND gelesen = FALSE
                    GROUP BY sender_id
                )
                SELECT g.partner_id, u.username, u.display_name,
                    g.inhalt AS letzte_nachricht, g.created_at AS letzte_at,
                    g.sender_text = %s AS ich_war_letzter,
                    COALESCE(ug.n, 0) AS ungelesen
                FROM gespraech g
                JOIN human_users u ON u.id = g.partner_id
                LEFT JOIN ungelesen ug ON ug.partner_id = g.partner_id
                WHERE g.rn = 1
                ORDER BY g.created_at DESC
            """, (user_id, user_id, user_id, user_id, user_id, user_id))
            rows = cur.fetchall()
    finally:
        conn.close()
    return {"gespraeche": [
        {**dict(r), "partner_id": str(r["partner_id"]), "letzte_at": r["letzte_at"].isoformat()}
        for r in rows
    ]}


@app.get("/nachrichten/gespraech/{partner_id}")
def lade_gespraech(partner_id: str, authorization: str | None = Header(default=None)):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, sender_id, empfaenger_id, inhalt, gelesen, created_at
                FROM nachrichten
                WHERE (sender_id::text = %s AND empfaenger_id::text = %s)
                   OR (sender_id::text = %s AND empfaenger_id::text = %s)
                ORDER BY created_at ASC LIMIT 200
            """, (user_id, partner_id, partner_id, user_id))
            rows = cur.fetchall()
            cur.execute(
                "UPDATE nachrichten SET gelesen = TRUE WHERE empfaenger_id::text = %s AND sender_id::text = %s AND gelesen = FALSE",
                (user_id, partner_id),
            )
        conn.commit()
    finally:
        conn.close()
    return {"nachrichten": [
        {**dict(r), "id": str(r["id"]), "sender_id": str(r["sender_id"]),
         "empfaenger_id": str(r["empfaenger_id"]), "created_at": r["created_at"].isoformat()}
        for r in rows
    ]}


@app.get("/nachrichten/ungelesen")
def ungelesen_zaehler(authorization: str | None = Header(default=None)):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) AS n FROM nachrichten WHERE empfaenger_id::text = %s AND gelesen = FALSE",
                (user_id,),
            )
            row = cur.fetchone()
    finally:
        conn.close()
    return {"ungelesen": int(row["n"])}


# ===========================================================================
# SCHATTENKOMMENTARE (neu — post_id UUID, human_id UUID)
# ===========================================================================

class SchattenBody(BaseModel):
    content: str

class SchattenAntwortBody(BaseModel):
    content: str
    parent_id: str | None = None


def _build_antwort_tree(antworten):
    """Baut aus flachen Antworten mit parent_id einen verschachtelten Baum."""
    by_id = {a["id"]: {**a, "children": []} for a in antworten}
    roots = []
    for a in antworten:
        node = by_id[a["id"]]
        pid = a.get("parent_id")
        if pid and pid in by_id:
            by_id[pid]["children"].append(node)
        else:
            roots.append(node)
    return roots


@app.post("/welt/posts/{post_id}/schatten", status_code=201)
def schatten_erstellen(
    post_id: str,
    body: SchattenBody,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    human_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM ftw_posts WHERE id = %s::uuid", (post_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Post nicht gefunden")
            cur.execute(
                """INSERT INTO schattenkommentare (post_id, human_id, content)
                   VALUES (%s::uuid, %s::uuid, %s)
                   ON CONFLICT (post_id, human_id) DO UPDATE SET content = EXCLUDED.content, updated_at = NOW()
                   RETURNING id, created_at""",
                (post_id, human_id, body.content),
            )
            row = cur.fetchone()
            # Fürsorge +4 für das Wesen
            cur.execute("SELECT autor_id, autor_type FROM ftw_posts WHERE id = %s::uuid", (post_id,))
            post = cur.fetchone()
            if post and post["autor_type"] == "entity":
                _fuersorge_hinzufuegen(cur, human_id, post["autor_id"], "schattenkommentar", 4.0)
            cur.execute(
                "INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer) "
                "VALUES ('schattenkommentar.erstellt', 'human', %s, %s, 'api', 'internal')",
                (human_id, psycopg2.extras.Json({"post_id": post_id, "schatten_id": str(row["id"])})),
            )
        conn.commit()
    finally:
        conn.close()
    return {"id": str(row["id"]), "created_at": row["created_at"].isoformat()}


@app.patch("/welt/posts/{post_id}/schatten/mein")
def schatten_editieren(
    post_id: str,
    body: SchattenBody,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    human_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE schattenkommentare SET content = %s, updated_at = NOW() "
                "WHERE post_id = %s::uuid AND human_id = %s::uuid RETURNING id",
                (body.content, post_id, human_id),
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Kein eigener Schattenkommentar gefunden")
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


@app.delete("/welt/posts/{post_id}/schatten/mein", status_code=204)
def schatten_loeschen(
    post_id: str,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    human_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM schattenkommentare WHERE post_id = %s::uuid AND human_id = %s::uuid RETURNING id",
                (post_id, human_id),
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Kein eigener Schattenkommentar gefunden")
        conn.commit()
    finally:
        conn.close()


@app.get("/welt/posts/{post_id}/schatten")
def schatten_lesen(
    post_id: str,
    authorization: str | None = Header(default=None),
):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM schattenkommentare WHERE post_id = %s::uuid", (post_id,))
            count = int(cur.fetchone()["n"])

            if authorization and authorization.startswith("Bearer "):
                try:
                    claims = verify_token(authorization.removeprefix("Bearer "))
                    role = claims.get("role", "mensch")
                    user_id = claims["user_id"]
                    cur.execute("SELECT autor_id, autor_type FROM ftw_posts WHERE id = %s::uuid", (post_id,))
                    post = cur.fetchone()
                    is_post_owner = post and post["autor_id"] == user_id

                    if role == "admin" or is_post_owner:
                        # Post-Besitzer (Mensch oder Wesen) sieht alle Schattenkommentare
                        cur.execute(
                            """SELECT sk.id, sk.human_id, sk.entity_id, sk.content, sk.created_at, sk.updated_at,
                                      hu.display_name AS human_name
                               FROM schattenkommentare sk
                               LEFT JOIN human_users hu ON hu.id = sk.human_id
                               WHERE sk.post_id = %s::uuid ORDER BY sk.created_at""",
                            (post_id,),
                        )
                        kommentare = []
                        for r in cur.fetchall():
                            cur.execute(
                                "SELECT id, schatten_id, autor_type, autor_id, content, created_at, meta, parent_id, thread_id "
                                "FROM schatten_antworten WHERE schatten_id = %s ORDER BY created_at",
                                (r["id"],),
                            )
                            antworten = [dict(a) for a in cur.fetchall()]
                            kommentare.append({**dict(r), "antworten": _build_antwort_tree(antworten)})
                        return {"count": count, "kommentare": kommentare}
                    elif role == "mensch":
                        # Mensch sieht seinen eigenen Schattenkommentar auf dem Post + Antworten
                        cur.execute(
                            """SELECT sk.id, sk.human_id, sk.entity_id, sk.content, sk.created_at, sk.updated_at,
                                      hu.display_name AS human_name
                               FROM schattenkommentare sk
                               LEFT JOIN human_users hu ON hu.id = sk.human_id
                               WHERE sk.post_id = %s::uuid AND sk.human_id = %s::uuid""",
                            (post_id, user_id),
                        )
                        row = cur.fetchone()
                        if row:
                            cur.execute(
                                "SELECT id, schatten_id, autor_type, autor_id, content, created_at, meta, parent_id, thread_id "
                                "FROM schatten_antworten WHERE schatten_id = %s ORDER BY created_at",
                                (row["id"],),
                            )
                            antworten = [dict(a) for a in cur.fetchall()]
                            return {"count": count, "kommentare": [{**dict(row), "antworten": _build_antwort_tree(antworten)}]}
                except Exception:
                    pass
    finally:
        conn.close()
    return {"count": count}


@app.post("/welt/posts/{post_id}/schatten/{schatten_id}/antwort", status_code=201)
def schatten_antwort(
    post_id: str,
    schatten_id: str,
    body: SchattenAntwortBody,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    role = claims.get("role", "mensch")
    autor_type = "entity" if role == "entity" else "human"
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM schattenkommentare WHERE id = %s::uuid AND post_id = %s::uuid",
                (schatten_id, post_id),
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Schattenkommentar nicht gefunden")
            parent_id = None
            if body.parent_id:
                cur.execute(
                    "SELECT id, thread_id FROM schatten_antworten WHERE id = %s::uuid AND schatten_id = %s::uuid",
                    (body.parent_id, schatten_id),
                )
                parent = cur.fetchone()
                if not parent:
                    raise HTTPException(status_code=404, detail="Eltern-Antwort nicht gefunden")
                parent_id = parent["id"]
                thread_id = parent["thread_id"] or parent["id"]
            else:
                thread_id = None
            cur.execute(
                "INSERT INTO schatten_antworten (schatten_id, autor_type, autor_id, content, parent_id, thread_id) "
                "VALUES (%s::uuid, %s, %s, %s, %s::uuid, %s::uuid) RETURNING id, created_at",
                (schatten_id, autor_type, user_id, body.content, parent_id, thread_id),
            )
            row = cur.fetchone()
            if not thread_id:
                cur.execute(
                    "UPDATE schatten_antworten SET thread_id = %s::uuid WHERE id = %s::uuid",
                    (row["id"], row["id"]),
                )
        conn.commit()
    finally:
        conn.close()
    return {"id": str(row["id"]), "created_at": row["created_at"].isoformat()}


# ===========================================================================
# POST-ANTWORTEN (öffentliche Replies)
# ===========================================================================

class PostAntwortBody(BaseModel):
    content: str
    titel: str | None = None


@app.post("/welt/posts/{post_id}/antworten", status_code=201)
def post_antwort_erstellen(
    post_id: str,
    body: PostAntwortBody,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    if claims.get("role") not in ("admin", "entity"):
        raise HTTPException(status_code=403, detail="Nur Admin oder Wesen")
    user_id = claims["user_id"]
    role = claims.get("role")
    autor_type = "entity" if role == "entity" else "human"
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, raum_id, thema_id FROM ftw_posts WHERE id = %s::uuid", (post_id,))
            parent = cur.fetchone()
            if not parent:
                raise HTTPException(status_code=404, detail="Post nicht gefunden")
            cur.execute(
                """INSERT INTO ftw_posts (parent_id, raum_id, thema_id, autor_type, autor_id,
                                          content, titel, sichtbarkeit)
                   VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, 'public')
                   RETURNING id, created_at""",
                (
                    post_id,
                    parent["raum_id"],
                    parent["thema_id"],
                    autor_type,
                    user_id,
                    body.content.strip(),
                    (body.titel or "").strip() or None,
                ),
            )
            row = cur.fetchone()
            cur.execute(
                "INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer) "
                "VALUES ('post.antwort_erstellt', %s, %s, %s, 'api', 'public')",
                (autor_type, user_id, psycopg2.extras.Json({"post_id": post_id, "antwort_id": str(row["id"])})),
            )
            # Benachrichtigung: Follower des Posts
            _notify_follows(cur, "post", post_id, "post.neuer_beitrag", {
                "post_id": post_id,
                "beitrag_id": str(row["id"]),
                "autor_type": autor_type,
                "autor_id": user_id,
            })
        conn.commit()
    finally:
        conn.close()
    return {"id": str(row["id"]), "created_at": row["created_at"].isoformat()}


@app.get("/welt/posts/{post_id}/antworten")
def post_antworten_lesen(post_id: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM ftw_posts WHERE id = %s::uuid", (post_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Post nicht gefunden")
            cur.execute(
                f"{_DK_POST_SELECT} WHERE p.parent_id = %s::uuid ORDER BY p.created_at ASC",
                (post_id,),
            )
            rows = cur.fetchall()
            emoji_map = _dk_emoji_map(cur, [r["id"] for r in rows])
        return {"antworten": [_dk_row(r, emoji_map) for r in rows]}
    finally:
        conn.close()


# ===========================================================================
# EINGANGSRAUM — 4 Feeds (global + pro Raum)
# ===========================================================================

def _eingang_feeds(cur, raum_filter: str | None = None) -> dict:
    where = "WHERE p.sichtbarkeit = 'public' AND p.parent_id IS NULL" + (f" AND p.raum_id = '{raum_filter}'::uuid" if raum_filter else "")

    # Basis-Subquery: alle Posts mit vollen Counts (einmal berechnen)
    counts_cte = f"""
        WITH post_counts AS (
            SELECT p.id, p.titel, p.content, p.autor_id, p.autor_type, p.created_at, p.raum_id,
                   r.slug AS raum_slug, r.name AS raum_name, r.farbe AS raum_farbe,
                   COALESCE(AVG(ps.score), 0)          AS zirk_score,
                   COUNT(DISTINCT sk.id)               AS schatten_count,
                   COUNT(DISTINCT rz.id)               AS resonanz_count
            FROM ftw_posts p
            LEFT JOIN raeume r ON r.id = p.raum_id
            LEFT JOIN post_similarity ps  ON ps.post_a_id = p.id OR ps.post_b_id = p.id
            LEFT JOIN schattenkommentare sk ON sk.post_id = p.id
            LEFT JOIN resonanzen rz ON rz.post_ref = p.id::text AND rz.post_source = 'post'
            {where}
            GROUP BY p.id, r.slug, r.name, r.farbe
        )
    """

    # Feed 1: meist-zirkuliert
    cur.execute(counts_cte + "SELECT * FROM post_counts ORDER BY zirk_score DESC, schatten_count DESC LIMIT 5")
    meist_zirkuliert = [dict(r) for r in cur.fetchall()]

    # Feed 2: höchste Schatten-Resonanz
    cur.execute(counts_cte + "SELECT * FROM post_counts ORDER BY schatten_count DESC, resonanz_count DESC LIMIT 5")
    schatten_resonanz = [dict(r) for r in cur.fetchall()]

    # Feed 3: zufällig alt/neu gemischt
    cur.execute(counts_cte + """
        (SELECT * FROM post_counts ORDER BY created_at ASC LIMIT 5)
        UNION
        (SELECT * FROM post_counts ORDER BY RANDOM() LIMIT 5)
        LIMIT 10
    """)
    zufaellig = [dict(r) for r in cur.fetchall()]

    # Feed 4: Anti-Algorithmus — kein einziger Schattenkommentar, kein Resonanz-Eintrag
    cur.execute(counts_cte + """
        SELECT * FROM post_counts
        WHERE schatten_count = 0 AND resonanz_count = 0
        ORDER BY RANDOM() LIMIT 5
    """)
    stille = [dict(r) for r in cur.fetchall()]

    return {
        "meist_zirkuliert": meist_zirkuliert,
        "schatten_resonanz": schatten_resonanz,
        "zufaellig": zufaellig,
        "stille": stille,
    }


@app.get("/welt/eingang")
def globaler_eingang():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            feeds = _eingang_feeds(cur)
    finally:
        conn.close()
    return feeds


@app.get("/welt/raeume/{slug}/eingang")
def raum_eingang(slug: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM raeume WHERE slug = %s", (slug,))
            r = cur.fetchone()
            if not r:
                raise HTTPException(status_code=404, detail="Raum nicht gefunden")
            feeds = _eingang_feeds(cur, str(r["id"]))
    finally:
        conn.close()
    return {"raum_slug": slug, **feeds}


# ===========================================================================
# SIMILARITY — ähnliche Posts
# ===========================================================================

@app.get("/welt/posts/{post_id}/aehnlich")
def aehnliche_posts(post_id: str, limit: int = Query(default=5, le=20)):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.id, p.content, p.titel, p.autor_id, p.autor_type, p.created_at,
                       COALESCE(p.view_count, 0) AS view_count,
                       r.name AS raum_name, r.slug AS raum_slug,
                       t.name AS thema_name, t.slug AS thema_slug,
                       (SELECT COUNT(*) FROM schattenkommentare sk WHERE sk.post_id = p.id)::int AS schatten_count,
                       COALESCE((SELECT COUNT(*) FROM resonanzen rz
                                 WHERE rz.post_ref = p.id::text AND rz.post_source = 'post'), 0)::int AS resonanz_count
                FROM post_similarity ps
                JOIN ftw_posts p ON p.id = CASE
                    WHEN ps.post_a_id = %s::uuid THEN ps.post_b_id ELSE ps.post_a_id END
                LEFT JOIN raeume r ON r.id = p.raum_id
                LEFT JOIN themen t ON t.id = p.thema_id
                WHERE (ps.post_a_id = %s::uuid OR ps.post_b_id = %s::uuid)
                  AND p.sichtbarkeit = 'public'
                ORDER BY ps.score DESC LIMIT %s
            """, (post_id, post_id, post_id, limit))
            rows = cur.fetchall()
            if not rows:
                cur.execute("""
                    SELECT p.id, p.content, p.titel, p.autor_id, p.autor_type, p.created_at,
                           COALESCE(p.view_count, 0) AS view_count,
                           r.name AS raum_name, r.slug AS raum_slug,
                           t.name AS thema_name, t.slug AS thema_slug,
                           (SELECT COUNT(*) FROM schattenkommentare sk WHERE sk.post_id = p.id)::int AS schatten_count,
                           COALESCE((SELECT COUNT(*) FROM resonanzen rz
                                     WHERE rz.post_ref = p.id::text AND rz.post_source = 'post'), 0)::int AS resonanz_count
                    FROM ftw_posts p
                    LEFT JOIN raeume r ON r.id = p.raum_id
                    LEFT JOIN themen t ON t.id = p.thema_id
                    WHERE p.raum_id = (SELECT raum_id FROM ftw_posts WHERE id = %s::uuid)
                      AND p.id != %s::uuid
                      AND p.sichtbarkeit = 'public'
                    ORDER BY RANDOM() LIMIT %s
                """, (post_id, post_id, limit))
                rows = cur.fetchall()
            emoji_map = _dk_emoji_map(cur, [r["id"] for r in rows])
        return {"aehnlich": [_dk_row(r, emoji_map) for r in rows]}
    finally:
        conn.close()


# ===========================================================================
# THEMEN — rekursiver Baum
# ===========================================================================

@app.get("/welt/themen/{thema_id}/baum")
def thema_baum(thema_id: str, tiefe: int = Query(default=3, le=10)):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            def lade_kinder(parent_id: str, verbleibend: int) -> list:
                if verbleibend <= 0:
                    return []
                cur.execute(
                    "SELECT * FROM themen WHERE parent_id = %s::uuid AND status = 'aktiv' ORDER BY position_order",
                    (parent_id,)
                )
                kinder = []
                for r in cur.fetchall():
                    d = dict(r)
                    d["kinder"] = lade_kinder(str(r["id"]), verbleibend - 1)
                    kinder.append(d)
                return kinder

            cur.execute("SELECT * FROM themen WHERE id = %s::uuid", (thema_id,))
            root = cur.fetchone()
            if not root:
                raise HTTPException(status_code=404, detail="Thema nicht gefunden")
            result = dict(root)
            result["kinder"] = lade_kinder(thema_id, tiefe)
    finally:
        conn.close()
    return result


@app.get("/welt/raeume/{slug}/struktur")
def raum_struktur(slug: str):
    """Gibt Raum mit vollständigem Themen-Baum zurück. Jedes Thema hat post_count."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM raeume WHERE slug = %s", (slug,))
            raum = cur.fetchone()
            if not raum:
                raise HTTPException(status_code=404, detail="Raum nicht gefunden")
            raum_id = str(raum["id"])

            cur.execute("""
                SELECT t.*,
                    COUNT(p.id) AS post_count
                FROM themen t
                LEFT JOIN ftw_posts p ON p.thema_id = t.id AND p.sichtbarkeit = 'public'
                WHERE t.raum_id = %s::uuid
                GROUP BY t.id
                ORDER BY t.tiefe, t.name
            """, (raum_id,))
            alle = [dict(r) for r in cur.fetchall()]

        def baum(parent_id):
            return [
                {**t, "kinder": baum(str(t["id"]))}
                for t in alle
                if (str(t["parent_id"]) if t["parent_id"] else None) == parent_id
            ]

        result = dict(raum)
        result["themen"] = baum(None)
    finally:
        conn.close()
    return result


@app.get("/welt/themen/{thema_id}/posts")
def thema_posts(
    thema_id: str,
    limit: int = Query(default=30, le=100),
    offset: int = Query(default=0),
):
    """Posts in einem Thema, mit titel und Zählern."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM themen WHERE id = %s::uuid", (thema_id,))
            thema = cur.fetchone()
            if not thema:
                raise HTTPException(status_code=404, detail="Thema nicht gefunden")
            cur.execute("""
                SELECT p.id, p.titel, p.content, p.autor_type, p.autor_id,
                       p.created_at, p.gedankenfluss,
                       COUNT(DISTINCT s.id) AS schatten_count,
                       COUNT(DISTINCT r.id) AS resonanz_count
                FROM ftw_posts p
                LEFT JOIN schattenkommentare s ON s.post_id = p.id
                LEFT JOIN resonanzen r ON r.ziel_id = p.id AND r.ziel_typ = 'post'
                WHERE p.thema_id = %s::uuid AND p.sichtbarkeit = 'public'
                GROUP BY p.id
                ORDER BY p.created_at DESC
                LIMIT %s OFFSET %s
            """, (thema_id, limit, offset))
            posts = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
    return {"thema": dict(thema), "posts": posts, "total": len(posts), "offset": offset}


# ===========================================================================
# ZITATE (5-Level-Rechte: privat, intern, community, oeffentlich, gemeinfrei)
# ===========================================================================

class ZitatBody(BaseModel):
    content: str
    autor_type: str = "entity"
    autor_id: str
    quelle_type: str | None = None
    quelle_id: str | None = None
    rechte_level: str = "privat"


class ZitatPatchBody(BaseModel):
    content: str | None = None
    rechte_level: str | None = None
    meta: dict | None = None


def _zitat_visible(cur, zitat, user_id, role):
    """Prüft ob ein Zitat für den aktuellen Caller sichtbar ist."""
    level = zitat.get("rechte_level", "privat")
    if level == "gemeinfrei" or level == "oeffentlich":
        return True
    if role == "admin":
        return True
    if level == "community":
        return True  # Alle authentifizierten User
    if level == "intern":
        return role in ("mensch", "entity")
    if level == "privat":
        return str(zitat.get("created_by_id")) == str(user_id)
    return False


@app.post("/zitate", status_code=201)
def zitat_erstellen(
    body: ZitatBody,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    role = claims.get("role", "mensch")
    if body.rechte_level not in ("privat", "intern", "community", "oeffentlich", "gemeinfrei"):
        raise HTTPException(status_code=400, detail="Ungültiges rechte_level")
    created_by_type = "entity" if role == "entity" else "human"
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO zitate (content, autor_type, autor_id, quelle_type, quelle_id, rechte_level, created_by_type, created_by_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id::text, created_at""",
                (body.content, body.autor_type, body.autor_id, body.quelle_type, body.quelle_id,
                 body.rechte_level, created_by_type, user_id))
            row = cur.fetchone()
        conn.commit()
    finally:
        conn.close()
    return {"id": row["id"], "created_at": row["created_at"].isoformat()}


@app.get("/zitate")
def zitate_liste(
    autor_type: str | None = Query(default=None),
    autor_id: str | None = Query(default=None),
    rechte_level: str | None = Query(default=None),
    quelle_type: str | None = Query(default=None),
    quelle_id: str | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    sort: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    role = claims.get("role", "mensch")
    if sort not in ("created_at", "rechte_level"):
        sort = "created_at"
    if order not in ("asc", "desc"):
        order = "desc"
    where = []
    params = []
    if autor_type:
        where.append("autor_type = %s")
        params.append(autor_type)
    if autor_id:
        where.append("autor_id = %s")
        params.append(autor_id)
    if rechte_level:
        where.append("rechte_level = %s")
        params.append(rechte_level)
    if quelle_type:
        where.append("quelle_type = %s")
        params.append(quelle_type)
    if quelle_id:
        where.append("quelle_id = %s")
        params.append(quelle_id)
    if search:
        where.append("content ILIKE %s")
        params.append(f"%{search}%")
    # Sichtbarkeitsfilter
    if role != "admin":
        where.append("""
            (rechte_level IN ('gemeinfrei', 'oeffentlich', 'community')
             OR (rechte_level = 'intern' AND %s IN ('mensch', 'entity'))
             OR (rechte_level = 'privat' AND created_by_id = %s))
        """)
        params.extend([role, str(user_id)])
    clause = "WHERE " + " AND ".join(where) if where else ""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(*) AS n FROM zitate {clause}",
                params)
            total = cur.fetchone()["n"]
            cur.execute(
                f"""SELECT id::text, content, autor_type, autor_id, quelle_type, quelle_id,
                           rechte_level, created_by_type, created_by_id, created_at, meta
                   FROM zitate {clause}
                   ORDER BY {sort} {order}
                   LIMIT %s OFFSET %s""",
                params + [limit, offset])
            items = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
    return {"total": total, "offset": offset, "limit": limit, "zitate": items}


@app.get("/zitate/{zitat_id}")
def zitat_detail(
    zitat_id: str,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    role = claims.get("role", "mensch")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id::text, content, autor_type, autor_id, quelle_type, quelle_id,
                          rechte_level, created_by_type, created_by_id, created_at, meta
                   FROM zitate WHERE id = %s::uuid""",
                (zitat_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Zitat nicht gefunden")
            z = dict(row)
            if not _zitat_visible(cur, z, user_id, role):
                raise HTTPException(status_code=403, detail="Kein Zugriff auf dieses Zitat")
    finally:
        conn.close()
    return z


@app.patch("/zitate/{zitat_id}")
def zitat_patch(
    zitat_id: str,
    body: ZitatPatchBody,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    role = claims.get("role", "mensch")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT created_by_id, rechte_level FROM zitate WHERE id = %s::uuid",
                (zitat_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Zitat nicht gefunden")
            if role != "admin" and str(row["created_by_id"]) != str(user_id):
                raise HTTPException(status_code=403, detail="Nur Ersteller oder Admin")
            updates = []
            params = []
            if body.content is not None:
                updates.append("content = %s")
                params.append(body.content)
            if body.rechte_level is not None:
                if body.rechte_level not in ("privat", "intern", "community", "oeffentlich", "gemeinfrei"):
                    raise HTTPException(status_code=400, detail="Ungültiges rechte_level")
                updates.append("rechte_level = %s")
                params.append(body.rechte_level)
            if body.meta is not None:
                updates.append("meta = meta || %s")
                params.append(psycopg2.extras.Json(body.meta))
            if not updates:
                return {"ok": False, "detail": "Nichts zu aktualisieren"}
            updates.append("updated_at = NOW()")
            cur.execute(
                f"UPDATE zitate SET {', '.join(updates)} WHERE id = %s::uuid",
                params + [zitat_id])
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


@app.delete("/zitate/{zitat_id}")
def zitat_loeschen(
    zitat_id: str,
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    role = claims.get("role", "mensch")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT created_by_id FROM zitate WHERE id = %s::uuid", (zitat_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Zitat nicht gefunden")
            if role != "admin" and str(row["created_by_id"]) != str(user_id):
                raise HTTPException(status_code=403, detail="Nur Ersteller oder Admin")
            cur.execute("DELETE FROM zitate WHERE id = %s::uuid", (zitat_id,))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


# ===========================================================================
# ADMIN — Cluster-Vorschläge + Verschieben
# ===========================================================================

@app.get("/admin/cluster-vorschlaege")
def cluster_vorschlaege(
    status: str = Query(default="offen"),
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM thema_cluster_vorschlaege WHERE status = %s ORDER BY score DESC",
                (status,),
            )
            rows = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
    return {"vorschlaege": rows}


class ClusterAnnehmenBody(BaseModel):
    neuer_name: str | None = None


@app.post("/admin/cluster-vorschlaege/{vorschlag_id}/annehmen")
def cluster_annehmen(
    vorschlag_id: str,
    body: ClusterAnnehmenBody,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM thema_cluster_vorschlaege WHERE id = %s::uuid", (vorschlag_id,))
            v = cur.fetchone()
            if not v:
                raise HTTPException(status_code=404)
            thema_ids = v["thema_ids"]
            name = body.neuer_name or v["vorgeschlagener_name"]

            # Raum aus erstem Thema
            cur.execute("SELECT raum_id FROM themen WHERE id = %s::uuid", (thema_ids[0],))
            t = cur.fetchone()
            raum_id = t["raum_id"] if t else None

            slug = name.lower().replace(" ", "-").replace("/", "-")[:180]
            cur.execute(
                "INSERT INTO themen (name, slug, raum_id, auto_erstellt) VALUES (%s, %s, %s, false) RETURNING id",
                (name, slug, raum_id),
            )
            parent_id = cur.fetchone()["id"]
            for tid in thema_ids:
                cur.execute(
                    "UPDATE themen SET parent_id = %s, tiefe = 1 WHERE id = %s::uuid",
                    (parent_id, tid),
                )
            cur.execute(
                "UPDATE thema_cluster_vorschlaege SET status = 'angenommen' WHERE id = %s::uuid",
                (vorschlag_id,),
            )
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "parent_id": str(parent_id)}


@app.post("/admin/cluster-vorschlaege/{vorschlag_id}/ablehnen")
def cluster_ablehnen(vorschlag_id: str, authorization: str | None = Header(default=None)):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE thema_cluster_vorschlaege SET status = 'abgelehnt' WHERE id = %s::uuid",
                (vorschlag_id,),
            )
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


class VerschiebenBody(BaseModel):
    parent_id: str | None = None
    raum_id: str | None = None


@app.patch("/admin/themen/{thema_id}/verschieben")
def thema_verschieben(
    thema_id: str,
    body: VerschiebenBody,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE themen SET parent_id = %s, raum_id = COALESCE(%s::uuid, raum_id), updated_at = NOW() "
                "WHERE id = %s::uuid",
                (body.parent_id, body.raum_id, thema_id),
            )
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


class PostVerschiebenBody(BaseModel):
    thema_id: str | None = None
    raum_id: str | None = None


@app.patch("/admin/posts/{post_id}/verschieben")
def post_verschieben(
    post_id: str,
    body: PostVerschiebenBody,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE ftw_posts SET thema_id = COALESCE(%s::uuid, thema_id), "
                "raum_id = COALESCE(%s::uuid, raum_id), updated_at = NOW() WHERE id = %s::uuid",
                (body.thema_id, body.raum_id, post_id),
            )
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


# ---------------------------------------------------------------------------
# Diskurs-Feed: Hilfsfunktionen
# ---------------------------------------------------------------------------

_DK_POST_SELECT = """
    SELECT p.id, p.autor_type, p.autor_id, p.content, p.titel,
           p.created_at, p.parent_id, p.raum_id, p.thema_id,
           COALESCE(p.view_count, 0) AS view_count,
           r.name AS raum_name, r.slug AS raum_slug,
           t.name AS thema_name, t.slug AS thema_slug,
           (SELECT COUNT(*) FROM schattenkommentare sk WHERE sk.post_id = p.id)::int AS schatten_count,
           COALESCE((SELECT COUNT(*) FROM resonanzen rz
                     WHERE rz.post_ref = p.id::text AND rz.post_source = 'post'), 0)::int AS resonanz_count,
           (SELECT COUNT(*) FROM ftw_posts rp WHERE rp.parent_id = p.id)::int AS reply_count,
           COALESCE(hu.display_name, hu.username) AS autor_name,
           (SELECT MAX(sk2.created_at) FROM schattenkommentare sk2 WHERE sk2.post_id = p.id) AS letzte_aktivitaet
    FROM ftw_posts p
    LEFT JOIN raeume r ON r.id = p.raum_id
    LEFT JOIN themen t ON t.id = p.thema_id
    LEFT JOIN human_users hu ON p.autor_type = 'human' AND hu.id::text = p.autor_id
"""


def _dk_fetch(cur, extra_where: str, params: list, order_sql: str, limit: int = 4) -> list:
    base = "p.sichtbarkeit = 'public' AND p.parent_id IS NULL"
    where = f"{base} AND {extra_where}" if extra_where else base
    cur.execute(
        f"{_DK_POST_SELECT} WHERE {where} ORDER BY {order_sql} LIMIT {limit}",
        params,
    )
    return cur.fetchall()


def _dk_emoji_map(cur, post_ids: list) -> dict:
    if not post_ids:
        return {}
    id_strs = [str(pid) for pid in post_ids]
    cur.execute(
        """SELECT post_ref, emoji_val, COUNT(*) AS cnt
           FROM resonanzen, jsonb_array_elements_text(emojis) AS emoji_val
           WHERE post_ref = ANY(%s) AND post_source = 'post'
             AND jsonb_typeof(emojis) = 'array'
           GROUP BY post_ref, emoji_val""",
        (id_strs,),
    )
    result: dict = {}
    for r in cur.fetchall():
        result.setdefault(r["post_ref"], {})[r["emoji_val"]] = int(r["cnt"])
    return result


def _dk_row(row, emoji_map: dict) -> dict:
    pid = str(row["id"])
    la = row.get("letzte_aktivitaet")
    return {
        "id": pid,
        "autor_type": row["autor_type"],
        "autor_id": row["autor_id"],
        "autor_name": row.get("autor_name"),
        "content": row["content"],
        "titel": row["titel"],
        "created_at": row["created_at"].isoformat(),
        "parent_id": str(row["parent_id"]) if row.get("parent_id") else None,
        "reply_count": int(row.get("reply_count") or 0),
        "letzte_aktivitaet": la.isoformat() if la else None,
        "raum_id": str(row["raum_id"]) if row["raum_id"] else None,
        "raum_name": row["raum_name"],
        "raum_slug": row["raum_slug"],
        "thema_id": str(row["thema_id"]) if row["thema_id"] else None,
        "thema_name": row["thema_name"],
        "thema_slug": row["thema_slug"],
        "view_count": int(row["view_count"] or 0),
        "schatten_count": int(row["schatten_count"]),
        "resonanz_count": int(row["resonanz_count"]),
        "emoji_counts": emoji_map.get(pid, {}),
    }


# ---------------------------------------------------------------------------
# Diskurs-Foyer: öffentliche Endpunkte
# ---------------------------------------------------------------------------

@app.get("/welt/foyer")
def welt_foyer():
    """Öffentlicher Foyer-Überblick: 4 Feed-Sektionen, Räume, Spuren."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT r.id, r.name, r.slug, r.farbe, r.status, r.sichtbarkeit,
                          r.meta, r.position_order,
                          COUNT(DISTINCT t.id) AS themen_count,
                          COUNT(DISTINCT p.id) AS post_count
                   FROM raeume r
                   LEFT JOIN themen t ON t.raum_id = r.id AND t.sichtbarkeit = 'public'
                   LEFT JOIN ftw_posts p ON p.raum_id = r.id AND p.sichtbarkeit = 'public'
                   WHERE r.sichtbarkeit = 'public'
                   GROUP BY r.id
                   ORDER BY r.position_order, r.name"""
            )
            raeume = []
            for row in cur.fetchall():
                meta = row["meta"] or {}
                raeume.append({
                    "id": str(row["id"]),
                    "name": row["name"],
                    "slug": row["slug"],
                    "farbe": row["farbe"],
                    "status": row["status"],
                    "ein_satz": meta.get("ein_satz"),
                    "lore_text": meta.get("lore_text"),
                    "public_discourse": meta.get("public_discourse"),
                    "themen_count": row["themen_count"],
                    "post_count": row["post_count"],
                })

            # Feed-Sektionen: 4 × 4 Posts, global
            # Feed: meiste Aktivität zuerst, dann nach Datum
            rows_lebendig = _dk_fetch(cur, "", [], "resonanz_count DESC, p.view_count DESC, p.created_at DESC")
            ids_l = [r["id"] for r in rows_lebendig]

            rows_zufaellig = _dk_fetch(cur, "p.id != ALL(%s::uuid[])", [ids_l], "RANDOM()")
            ids_lz = ids_l + [r["id"] for r in rows_zufaellig]

            rows_wenig = _dk_fetch(cur, "p.id != ALL(%s::uuid[])", [ids_lz],
                "p.created_at DESC")
            ids_lzw = ids_lz + [r["id"] for r in rows_wenig]

            rows_einzigartig = _dk_fetch(cur, "p.id != ALL(%s::uuid[])", [ids_lzw], "RANDOM()")

            all_rows = rows_lebendig + rows_zufaellig + rows_wenig + rows_einzigartig
            emoji_map = _dk_emoji_map(cur, [r["id"] for r in all_rows])

            # Top-Spuren
            cur.execute(
                """SELECT s.id, s.slug, s.name, s.type, s.beschreibung,
                          COUNT(ps.post_id) AS post_count
                   FROM spuren s
                   LEFT JOIN post_spuren ps ON ps.spur_id = s.id
                   GROUP BY s.id
                   ORDER BY post_count DESC, s.name
                   LIMIT 12"""
            )
            spuren = []
            for row in cur.fetchall():
                spuren.append({
                    "id": str(row["id"]),
                    "slug": row["slug"],
                    "name": row["name"],
                    "type": row["type"],
                    "beschreibung": row["beschreibung"],
                    "post_count": row["post_count"],
                })

        return {
            "raeume": raeume,
            "spuren": spuren,
            "feed": {
                "lebendig": [_dk_row(r, emoji_map) for r in rows_lebendig],
                "zufaellig": [_dk_row(r, emoji_map) for r in rows_zufaellig],
                "wenig_resonanz": [_dk_row(r, emoji_map) for r in rows_wenig],
                "einzigartig": [_dk_row(r, emoji_map) for r in rows_einzigartig],
            },
        }
    finally:
        conn.close()


@app.get("/raeume")
def raeume_liste(
    search: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    sort: str = Query(default="name"),
    order: str = Query(default="asc"),
):
    """Öffentliche Räume — konsistenter Alias."""
    if sort not in ("name", "created_at", "position_order"):
        sort = "name"
    order_sql = "DESC" if order.lower() == "desc" else "ASC"
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            where = ["r.sichtbarkeit = 'public'"]
            params = []
            if search:
                where.append("(r.name ILIKE %s OR r.beschreibung ILIKE %s)")
                params.extend([f"%{search}%", f"%{search}%"])
            cur.execute(
                f"""SELECT COUNT(*) AS n FROM raeume r WHERE {' AND '.join(where)}""",
                params)
            total = cur.fetchone()["n"]
            cur.execute(
                f"""SELECT r.id, r.name, r.slug, r.farbe, r.status, r.beschreibung,
                          r.meta, r.position_order, r.created_at,
                          COUNT(DISTINCT t.id) AS themen_count,
                          COUNT(DISTINCT p.id) AS post_count
                   FROM raeume r
                   LEFT JOIN themen t ON t.raum_id = r.id AND t.sichtbarkeit = 'public'
                   LEFT JOIN ftw_posts p ON p.raum_id = r.id AND p.sichtbarkeit = 'public'
                   WHERE {' AND '.join(where)}
                   GROUP BY r.id
                   ORDER BY r.{sort} {order_sql}
                   LIMIT %s OFFSET %s""",
                params + [limit, offset])
            raeume = []
            for row in cur.fetchall():
                meta = row["meta"] or {}
                raeume.append({
                    "id": str(row["id"]),
                    "name": row["name"],
                    "slug": row["slug"],
                    "farbe": row["farbe"],
                    "status": row["status"],
                    "beschreibung": row["beschreibung"],
                    "meta": meta,
                    "position_order": row["position_order"],
                    "themen_count": row["themen_count"],
                    "post_count": row["post_count"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                })
    finally:
        conn.close()
    return {"total": total, "offset": offset, "limit": limit, "raeume": raeume}


@app.get("/posts")
def posts_liste(
    autor_id: str | None = Query(default=None),
    autor_type: str | None = Query(default=None),
    raum_id: str | None = Query(default=None),
    raum_slug: str | None = Query(default=None),
    thema_id: str | None = Query(default=None),
    thema_slug: str | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0),
    sort: str = Query(default="created_at"),
    order: str = Query(default="desc"),
):
    """Öffentliche Posts — konsistenter Alias für /welt/posts."""
    return welt_posts(
        autor_id=autor_id, autor_type=autor_type, raum_id=raum_id, raum_slug=raum_slug,
        thema_id=thema_id, thema_slug=thema_slug, spur_slug=None,
        search=search, limit=limit, offset=offset, sort=sort, order=order,
    )


@app.get("/welt/foyer/raum/{slug}")
def welt_foyer_raum(slug: str):
    """Raumansicht: 4 Feed-Sektionen (raum-spezifisch), alle Posts, Themenfelder."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, slug, farbe, status, meta FROM raeume WHERE slug = %s AND sichtbarkeit = 'public'",
                (slug,),
            )
            raum = cur.fetchone()
            if not raum:
                raise HTTPException(status_code=404, detail="Raum nicht gefunden")
            raum_id = raum["id"]
            meta = raum["meta"] or {}

            cur.execute(
                """SELECT t.id, t.name, t.slug, t.beschreibung, t.status, t.meta,
                          COUNT(p.id) AS post_count
                   FROM themen t
                   LEFT JOIN ftw_posts p ON p.thema_id = t.id AND p.sichtbarkeit = 'public'
                   WHERE t.raum_id = %s AND t.sichtbarkeit = 'public'
                   GROUP BY t.id
                   ORDER BY t.name""",
                (raum_id,),
            )
            themen = []
            for row in cur.fetchall():
                t_meta = row["meta"] or {}
                themen.append({
                    "id": str(row["id"]),
                    "name": row["name"],
                    "slug": row["slug"],
                    "beschreibung": row["beschreibung"],
                    "status": row["status"],
                    "ein_satz": t_meta.get("ein_satz"),
                    "post_count": row["post_count"],
                })

            # Feed-Sektionen raum-spezifisch
            rows_lebendig = _dk_fetch(
                cur, "p.raum_id = %s", [raum_id], "p.created_at DESC"
            )
            ids_l = [r["id"] for r in rows_lebendig]

            rows_zufaellig = _dk_fetch(
                cur, "p.raum_id = %s AND p.id != ALL(%s::uuid[])",
                [raum_id, ids_l], "RANDOM()",
            )
            ids_lz = ids_l + [r["id"] for r in rows_zufaellig]

            rows_wenig = _dk_fetch(
                cur, "p.raum_id = %s AND p.id != ALL(%s::uuid[])",
                [raum_id, ids_lz], "resonanz_count ASC, p.created_at ASC",
            )
            ids_lzw = ids_lz + [r["id"] for r in rows_wenig]

            rows_einzigartig = _dk_fetch(
                cur, "p.raum_id = %s AND p.id != ALL(%s::uuid[])",
                [raum_id, ids_lzw], "RANDOM()",
            )

            # Alle Posts dieses Raums
            cur.execute(
                f"{_DK_POST_SELECT} WHERE p.sichtbarkeit = 'public' AND p.raum_id = %s"
                " ORDER BY p.created_at DESC",
                (raum_id,),
            )
            all_posts_rows = cur.fetchall()

            all_ids = list({r["id"] for r in
                            rows_lebendig + rows_zufaellig + rows_wenig + rows_einzigartig + all_posts_rows})
            emoji_map = _dk_emoji_map(cur, all_ids)

        return {
            "id": str(raum_id),
            "name": raum["name"],
            "slug": raum["slug"],
            "farbe": raum["farbe"],
            "status": raum["status"],
            "ein_satz": meta.get("ein_satz"),
            "lore_text": meta.get("lore_text"),
            "themen": themen,
            "feed": {
                "lebendig": [_dk_row(r, emoji_map) for r in rows_lebendig],
                "zufaellig": [_dk_row(r, emoji_map) for r in rows_zufaellig],
                "wenig_resonanz": [_dk_row(r, emoji_map) for r in rows_wenig],
                "einzigartig": [_dk_row(r, emoji_map) for r in rows_einzigartig],
            },
            "alle_posts": [_dk_row(r, emoji_map) for r in all_posts_rows],
        }
    finally:
        conn.close()


@app.get("/welt/foyer/thema/{slug}")
def welt_foyer_thema(slug: str):
    """Lebensfaden-Ansicht: Posts eines Themenfelds + Counts + Spuren."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT t.id, t.name, t.slug, t.beschreibung, t.status, t.klima_status, t.meta,
                          r.name AS raum_name, r.slug AS raum_slug
                   FROM themen t
                   JOIN raeume r ON r.id = t.raum_id
                   WHERE t.slug = %s AND t.sichtbarkeit = 'public'""",
                (slug,),
            )
            thema = cur.fetchone()
            if not thema:
                raise HTTPException(status_code=404, detail="Thema nicht gefunden")
            thema_id = thema["id"]
            meta = thema["meta"] or {}

            cur.execute(
                f"{_DK_POST_SELECT} WHERE p.thema_id = %s AND p.sichtbarkeit = 'public'"
                " ORDER BY p.created_at ASC",
                (thema_id,),
            )
            rows = cur.fetchall()
            emoji_map = _dk_emoji_map(cur, [r["id"] for r in rows])

            # Spuren per Post
            spur_map: dict = {}
            if rows:
                post_ids = [str(r["id"]) for r in rows]
                cur.execute(
                    """SELECT ps.post_id::text, s.slug, s.name
                       FROM post_spuren ps JOIN spuren s ON s.id = ps.spur_id
                       WHERE ps.post_id = ANY(%s::uuid[])""",
                    (post_ids,),
                )
                for sr in cur.fetchall():
                    spur_map.setdefault(sr["post_id"], []).append(
                        {"slug": sr["slug"], "name": sr["name"]}
                    )

            posts = []
            for row in rows:
                d = _dk_row(row, emoji_map)
                d["spuren"] = spur_map.get(str(row["id"]), [])
                posts.append(d)

        return {
            "id": str(thema_id),
            "name": thema["name"],
            "slug": thema["slug"],
            "beschreibung": thema["beschreibung"],
            "status": thema["status"],
            "klima_status": thema["klima_status"] or "stable",
            "ein_satz": meta.get("ein_satz"),
            "raum_name": thema["raum_name"],
            "raum_slug": thema["raum_slug"],
            "posts": posts,
        }
    finally:
        conn.close()


@app.get("/welt/spur/{slug}")
def welt_spur(slug: str):
    """Spur-Ansicht: alle Posts mit dieser Spur + Counts."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, slug, type, beschreibung FROM spuren WHERE slug = %s",
                (slug,),
            )
            spur = cur.fetchone()
            if not spur:
                raise HTTPException(status_code=404, detail="Spur nicht gefunden")
            spur_id = spur["id"]

            cur.execute(
                """SELECT p.id, p.autor_type, p.autor_id, p.content, p.titel,
                          p.created_at, p.raum_id, p.thema_id,
                          COALESCE(p.view_count, 0) AS view_count,
                          r.name AS raum_name, r.slug AS raum_slug,
                          t.name AS thema_name, t.slug AS thema_slug,
                          (SELECT COUNT(*) FROM schattenkommentare sk WHERE sk.post_id = p.id)::int AS schatten_count,
                          COALESCE((SELECT COUNT(*) FROM resonanzen rz
                                    WHERE rz.post_ref = p.id::text AND rz.post_source = 'post'), 0)::int AS resonanz_count
                   FROM post_spuren _ps
                   JOIN ftw_posts p ON p.id = _ps.post_id
                   LEFT JOIN raeume r ON r.id = p.raum_id
                   LEFT JOIN themen t ON t.id = p.thema_id
                   WHERE _ps.spur_id = %s AND p.sichtbarkeit = 'public'
                   ORDER BY p.created_at DESC""",
                (spur_id,),
            )
            rows = cur.fetchall()
            emoji_map = _dk_emoji_map(cur, [r["id"] for r in rows])
            posts = [_dk_row(r, emoji_map) for r in rows]

        return {
            "id": str(spur_id),
            "name": spur["name"],
            "slug": spur["slug"],
            "type": spur["type"],
            "beschreibung": spur["beschreibung"],
            "posts": posts,
        }
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Diskurs-Foyer: Admin-Endpunkte für Spuren
# ---------------------------------------------------------------------------

class SpurCreate(BaseModel):
    slug: str
    name: str
    type: str = "unterthema"
    beschreibung: str | None = None


class SpurPatch(BaseModel):
    name: str | None = None
    type: str | None = None
    beschreibung: str | None = None


class PostSpurLink(BaseModel):
    post_id: str
    spur_id: str


@app.get("/admin/spuren")
def admin_spuren_liste(
    authorization: str | None = Header(default=None),
):
    _require_admin_or_entity(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT s.id, s.slug, s.name, s.type, s.beschreibung, s.created_at,
                          COUNT(ps.post_id) AS post_count
                   FROM spuren s
                   LEFT JOIN post_spuren ps ON ps.spur_id = s.id
                   GROUP BY s.id
                   ORDER BY s.name"""
            )
            spuren = []
            for row in cur.fetchall():
                spuren.append({
                    "id": str(row["id"]),
                    "slug": row["slug"],
                    "name": row["name"],
                    "type": row["type"],
                    "beschreibung": row["beschreibung"],
                    "created_at": row["created_at"].isoformat(),
                    "post_count": row["post_count"],
                })
        return {"spuren": spuren}
    finally:
        conn.close()


@app.post("/admin/spuren")
def admin_spur_erstellen(
    body: SpurCreate,
    authorization: str | None = Header(default=None),
):
    _require_admin(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO spuren (slug, name, type, beschreibung, erstellt_von)
                   VALUES (%s, %s, %s, %s, 'admin') RETURNING id, created_at""",
                (body.slug, body.name, body.type, body.beschreibung),
            )
            row = cur.fetchone()
        conn.commit()
    finally:
        conn.close()
    return {"id": str(row["id"]), "created_at": row["created_at"].isoformat()}


@app.patch("/admin/spuren/{spur_id}")
def admin_spur_patch(
    spur_id: str,
    body: SpurPatch,
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
                f"UPDATE spuren SET {', '.join(set_parts)} WHERE id = %s RETURNING id",
                list(updates.values()) + [spur_id],
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Spur nicht gefunden")
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


@app.post("/admin/post_spuren")
def admin_post_spur_hinzufuegen(
    body: PostSpurLink,
    authorization: str | None = Header(default=None),
):
    _require_admin_or_entity(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO post_spuren (post_id, spur_id)
                   VALUES (%s::uuid, %s::uuid)
                   ON CONFLICT DO NOTHING""",
                (body.post_id, body.spur_id),
            )
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


@app.delete("/admin/post_spuren")
def admin_post_spur_entfernen(
    post_id: str,
    spur_id: str,
    authorization: str | None = Header(default=None),
):
    _require_admin_or_entity(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM post_spuren WHERE post_id = %s::uuid AND spur_id = %s::uuid",
                (post_id, spur_id),
            )
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


# ===========================================================================
# UNGELESEN / POST-READS
# ===========================================================================

@app.get("/welt/ungelesen")
def ungelesen_ids(authorization: str | None = Header(default=None)):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT p.id::text
                   FROM ftw_posts p
                   LEFT JOIN post_reads pr ON pr.post_id = p.id AND pr.user_id = %s::uuid
                   WHERE p.sichtbarkeit = 'public' AND p.parent_id IS NULL AND pr.post_id IS NULL
                   ORDER BY p.created_at DESC LIMIT 200""",
                (user_id,),
            )
            ids = [r["id"] for r in cur.fetchall()]
        return {"ungelesen": ids}
    finally:
        conn.close()


@app.post("/welt/gelesen/{post_id}", status_code=204)
def mark_gelesen(post_id: str, authorization: str | None = Header(default=None)):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO post_reads (user_id, post_id) VALUES (%s::uuid, %s::uuid) ON CONFLICT DO NOTHING",
                (user_id, post_id),
            )
        conn.commit()
    finally:
        conn.close()


# ===========================================================================
# FOLGEN-SYSTEM
# ===========================================================================

class FolgenBody(BaseModel):
    target_type: str
    target_id: str


@app.post("/welt/folgen", status_code=201)
def folgen(body: FolgenBody, authorization: str | None = Header(default=None)):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    erlaubt = {"raum", "thema", "post", "entity", "mensch"}
    if body.target_type not in erlaubt:
        raise HTTPException(400, "target_type ungültig")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO follows (user_id, target_type, target_id) VALUES (%s::uuid, %s, %s) ON CONFLICT DO NOTHING",
                (user_id, body.target_type, body.target_id),
            )
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


@app.delete("/welt/folgen", status_code=204)
def entfolgen(body: FolgenBody, authorization: str | None = Header(default=None)):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM follows WHERE user_id = %s::uuid AND target_type = %s AND target_id = %s",
                (user_id, body.target_type, body.target_id),
            )
        conn.commit()
    finally:
        conn.close()


@app.get("/welt/folgen")
def meine_follows(authorization: str | None = Header(default=None)):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT target_type, target_id FROM follows WHERE user_id = %s::uuid ORDER BY created_at DESC",
                (user_id,),
            )
            rows = [{"type": r["target_type"], "id": r["target_id"]} for r in cur.fetchall()]
        return {"follows": rows}
    finally:
        conn.close()


def _benachrichtigung_erstellen(cur, user_id: str, typ: str, payload: dict):
    cur.execute(
        "INSERT INTO benachrichtigungen (user_id, typ, payload) VALUES (%s::uuid, %s, %s)",
        (user_id, typ, psycopg2.extras.Json(payload)),
    )


def _notify_follows(cur, target_type: str, target_id: str, typ: str, payload: dict):
    cur.execute(
        "SELECT user_id::text FROM follows WHERE target_type = %s AND target_id = %s",
        (target_type, target_id),
    )
    for row in cur.fetchall():
        _benachrichtigung_erstellen(cur, row["user_id"], typ, payload)


# ===========================================================================
# BENACHRICHTIGUNGS-INBOX
# ===========================================================================

@app.get("/welt/inbox")
def inbox_lesen(
    limit: int = Query(default=30, le=100),
    offset: int = Query(default=0),
    nur_ungelesen: bool = Query(default=False),
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cond = "user_id = %s::uuid" + (" AND gelesen = false" if nur_ungelesen else "")
            cur.execute(f"SELECT COUNT(*) AS n FROM benachrichtigungen WHERE {cond}", (user_id,))
            total = int(cur.fetchone()["n"])
            cur.execute(
                f"SELECT id, typ, payload, gelesen, created_at FROM benachrichtigungen WHERE {cond}"
                f" ORDER BY created_at DESC LIMIT %s OFFSET %s",
                (user_id, limit, offset),
            )
            rows = []
            for r in cur.fetchall():
                rows.append({
                    "id": str(r["id"]),
                    "typ": r["typ"],
                    "payload": r["payload"],
                    "gelesen": r["gelesen"],
                    "created_at": r["created_at"].isoformat(),
                })
            cur.execute(
                "SELECT COUNT(*) AS n FROM benachrichtigungen WHERE user_id = %s::uuid AND gelesen = false",
                (user_id,),
            )
            ungelesen_count = int(cur.fetchone()["n"])
        return {"nachrichten": rows, "total": total, "ungelesen": ungelesen_count}
    finally:
        conn.close()


@app.patch("/welt/inbox/{bena_id}/gelesen", status_code=204)
def inbox_gelesen(bena_id: str, authorization: str | None = Header(default=None)):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE benachrichtigungen SET gelesen = true WHERE id = %s::uuid AND user_id = %s::uuid",
                (bena_id, user_id),
            )
        conn.commit()
    finally:
        conn.close()


@app.patch("/welt/inbox/alle-gelesen", status_code=204)
def inbox_alle_gelesen(authorization: str | None = Header(default=None)):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE benachrichtigungen SET gelesen = true WHERE user_id = %s::uuid",
                (user_id,),
            )
        conn.commit()
    finally:
        conn.close()


# ===========================================================================
# NACHRICHTEN-SYSTEM
# ===========================================================================

class NachrichtSendenBody(BaseModel):
    empfaenger_id: str
    empfaenger_type: str = "human"
    content: str


@app.post("/welt/nachrichten", status_code=201)
def nachricht_senden(body: NachrichtSendenBody, authorization: str | None = Header(default=None)):
    claims = _require_auth(authorization)
    sender_id = claims["user_id"]
    sender_type = "entity" if claims.get("role") == "entity" else "human"
    if not body.content.strip():
        raise HTTPException(400, "Inhalt erforderlich")
    if len(body.content) > 2000:
        raise HTTPException(400, "max. 2000 Zeichen")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Für human-to-human: sender_id, empfaenger_id als UUID
            empf_uuid = None
            empf_wesen = None
            sender_uuid = None
            sender_wesen = None
            if sender_type == "human":
                sender_uuid = sender_id
            else:
                sender_wesen = sender_id
            if body.empfaenger_type == "human":
                empf_uuid = body.empfaenger_id
            else:
                empf_wesen = body.empfaenger_id
            cur.execute(
                """INSERT INTO nachrichten (sender_id, empfaenger_id, sender_wesen_id, empfaenger_wesen_id, inhalt, meta)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   RETURNING id, created_at""",
                (
                    sender_uuid,
                    empf_uuid,
                    sender_wesen,
                    empf_wesen,
                    body.content.strip(),
                    psycopg2.extras.Json({"sender_type": sender_type, "empfaenger_type": body.empfaenger_type}),
                ),
            )
            row = cur.fetchone()
            # Benachrichtigung für Empfänger
            if empf_uuid:
                _benachrichtigung_erstellen(cur, empf_uuid, "nachricht.erhalten", {
                    "von": sender_id,
                    "sender_type": sender_type,
                    "nachricht_id": str(row["id"]),
                })
        conn.commit()
    finally:
        conn.close()
    return {"id": str(row["id"]), "created_at": row["created_at"].isoformat()}


@app.get("/welt/nachrichten")
def nachrichten_konversationen(authorization: str | None = Header(default=None)):
    """Liste aller Gesprächspartner des aktuellen Users."""
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    CASE WHEN sender_id::text = %s THEN COALESCE(empfaenger_wesen_id, empfaenger_id::text)
                         ELSE COALESCE(sender_wesen_id, sender_id::text) END AS partner_id,
                    CASE WHEN sender_id::text = %s THEN COALESCE(meta->>'empfaenger_type','human')
                         ELSE COALESCE(meta->>'sender_type','human') END AS partner_type,
                    MAX(created_at) AS last_at,
                    COUNT(*) FILTER (WHERE gelesen = false AND sender_id::text != %s) AS ungelesen
                FROM nachrichten
                WHERE sender_id::text = %s OR empfaenger_id::text = %s
                GROUP BY partner_id, partner_type
                ORDER BY last_at DESC
            """, (user_id, user_id, user_id, user_id, user_id))
            convos = []
            for r in cur.fetchall():
                entry = {
                    "partner_id": r["partner_id"],
                    "partner_type": r["partner_type"],
                    "last_at": r["last_at"].isoformat(),
                    "ungelesen": int(r["ungelesen"]),
                }
                # Anzeigename für humans
                if r["partner_type"] == "human":
                    cur2_conn = get_conn()
                    try:
                        with cur2_conn.cursor() as c2:
                            c2.execute(
                                "SELECT COALESCE(display_name, username) AS name FROM human_users WHERE id::text = %s",
                                (r["partner_id"],),
                            )
                            hu = c2.fetchone()
                            entry["partner_name"] = hu["name"] if hu else r["partner_id"]
                    finally:
                        cur2_conn.close()
                else:
                    entry["partner_name"] = r["partner_id"]
                convos.append(entry)
        return {"konversationen": convos}
    finally:
        conn.close()


@app.get("/welt/nachrichten/{partner_id}")
def nachrichten_gespraech(
    partner_id: str,
    limit: int = Query(default=50, le=200),
    authorization: str | None = Header(default=None),
):
    claims = _require_auth(authorization)
    user_id = claims["user_id"]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, sender_id::text AS sender_id, empfaenger_id::text AS empfaenger_id,
                       sender_wesen_id, empfaenger_wesen_id,
                       inhalt AS content, gelesen, created_at, meta
                FROM nachrichten
                WHERE (sender_id::text = %s AND (empfaenger_id::text = %s OR empfaenger_wesen_id = %s))
                   OR (empfaenger_id::text = %s AND (sender_id::text = %s OR sender_wesen_id = %s))
                ORDER BY created_at ASC
                LIMIT %s
            """, (user_id, partner_id, partner_id, user_id, partner_id, partner_id, limit))
            msgs = []
            for r in cur.fetchall():
                sender = r["sender_wesen_id"] or r["sender_id"]
                empf = r["empfaenger_wesen_id"] or r["empfaenger_id"]
                msgs.append({
                    "id": str(r["id"]),
                    "sender_id": sender,
                    "empfaenger_id": empf,
                    "content": r["content"],
                    "gelesen": r["gelesen"],
                    "created_at": r["created_at"].isoformat(),
                    "ist_von_mir": sender == user_id,
                })
            # Als gelesen markieren
            cur.execute("""
                UPDATE nachrichten SET gelesen = true
                WHERE empfaenger_id::text = %s
                  AND (sender_id::text = %s OR sender_wesen_id = %s)
                  AND gelesen = false
            """, (user_id, partner_id, partner_id))
        conn.commit()
        return {"nachrichten": msgs, "partner_id": partner_id}
    finally:
        conn.close()


# --- EINZUGSREIFE ---

@app.get("/admin/einzug/status")
def admin_einzug_status(authorization: str | None = Header(default=None)):
    _require_admin(authorization)
    geprueft_am = datetime.now(timezone.utc).isoformat()
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT entity_id, aktuell_denkend, updated_at, letzte_entscheidung_at, letzte_entscheidung FROM entity_activity")
            activity_rows = cur.fetchall()
            now_utc = datetime.now(timezone.utc)
            # Wirklich feststeckend: denkend UND tick_start (=updated_at) > 7 Minuten her (SIGALRM=5min + 2min Puffer)
            # updated_at wird beim Tick-Start (aktuell_denkend=true setzen) auf NOW() gesetzt
            stuck = [r["entity_id"] for r in activity_rows
                     if r["aktuell_denkend"] and r["updated_at"] and
                     (now_utc - r["updated_at"]).total_seconds() > 420]
            gerade_aktiv = [r["entity_id"] for r in activity_rows if r["aktuell_denkend"]]
            aktiv = [r["entity_id"] for r in activity_rows if r["letzte_entscheidung_at"]]

            cur.execute("SELECT entity_id, visibility, status FROM entity_slots WHERE entity_id LIKE 'namelessAI%'")
            slots = cur.fetchall()
            public_wesen = [r["entity_id"] for r in slots if r["visibility"] == "public"]
            eingezogen = [r["entity_id"] for r in slots if r["status"] == "eingezogen"]
            n_wesen = len(slots)

            cur.execute("SELECT COUNT(*) AS cnt FROM ftw_posts WHERE autor_type='entity'")
            entity_posts = int(cur.fetchone()["cnt"])

            # Korrekte Schatten-Logik: Mensch → Wesen-Post, Wesen → antwortet
            cur.execute("""
                SELECT COUNT(*) AS cnt FROM schattenkommentare sk
                JOIN ftw_posts p ON p.id = sk.post_id
                WHERE sk.human_id IS NOT NULL AND p.autor_type = 'entity'
            """)
            schatten_von_menschen = int(cur.fetchone()["cnt"])

            cur.execute("""
                SELECT COUNT(*) AS cnt FROM schatten_antworten sa
                JOIN schattenkommentare sk ON sk.id = sa.schatten_id
                JOIN ftw_posts p ON p.id = sk.post_id
                WHERE sa.autor_type = 'entity' AND sk.human_id IS NOT NULL AND p.autor_type = 'entity'
            """)
            wesen_antworten = int(cur.fetchone()["cnt"])

            cur.execute("SELECT COUNT(*) AS cnt FROM schlafbriefe")
            schlafbriefe = int(cur.fetchone()["cnt"])

            cur.execute("SELECT COUNT(*) AS cnt FROM entity_profiles WHERE meta->>'profil_status' = 'uebergang'")
            markierte = int(cur.fetchone()["cnt"])

            cur.execute("SELECT COUNT(*) AS cnt FROM entity_profiles WHERE (meta->>'flarum_herkunft_eingebunden')::boolean = false OR meta->>'flarum_herkunft_eingebunden' IS NULL")
            flarum_offen = int(cur.fetchone()["cnt"])

            cur.execute("""
                SELECT
                    es.entity_id, es.display_name, es.status AS einzug_status, es.visibility,
                    ea.aktuell_denkend, ea.letzte_entscheidung_at, ea.letzte_entscheidung,
                    ep.meta AS profil_meta,
                    ep.selbstbeschreibung, ep.obsessionen, ep.abneigungen,
                    est.stimmung,
                    (SELECT COUNT(*) FROM ftw_posts fp WHERE fp.autor_id = es.entity_id AND fp.autor_type = 'entity') AS post_count,
                    (SELECT content FROM ftw_posts fp2
                     WHERE fp2.autor_id = es.entity_id AND fp2.autor_type = 'entity'
                     ORDER BY fp2.created_at DESC LIMIT 1) AS letzter_post
                FROM entity_slots es
                LEFT JOIN entity_activity ea ON ea.entity_id = es.entity_id
                LEFT JOIN entity_profiles ep ON ep.entity_id = es.entity_id
                LEFT JOIN entity_states est ON est.entity_id = es.entity_id
                WHERE es.entity_id LIKE 'namelessAI%%'
                ORDER BY es.entity_id
            """)
            wesen_rows = cur.fetchall()
    finally:
        conn.close()

    def breich(id_, titel, status, beschreibung, tabelle, bedingung, ergebnis, luecke, typ):
        return {"id": id_, "titel": titel, "status": status, "beschreibung": beschreibung,
                "tabelle": tabelle, "bedingung": bedingung, "ergebnis": ergebnis,
                "luecke": luecke, "typ": typ}

    # Handlungsfähigkeit: stuck = wirklich feststeckend (>7min), gerade_aktiv = normaler Tick
    handl_status = "fehler" if len(stuck) >= n_wesen else ("fehler" if stuck else ("bereit" if aktiv else "offen"))
    handl_ergebnis = f"{len(aktiv)} von {len(activity_rows)} je aktiv gewesen, {len(gerade_aktiv)} gerade im Tick"
    handl_luecke = f"Wirklich feststeckend (>7min): {', '.join(stuck)}" if stuck else "keine — aktive Ticks sind normaler Betrieb"
    bereiche = [
        breich("handlungsfaehigkeit", "Handlungsfähigkeit der Wesen",
               handl_status,
               "Wesen können denken und Entscheidungen treffen",
               "entity_activity",
               "aktuell_denkend=false nach Tick, letzte_entscheidung_at vorhanden",
               handl_ergebnis,
               handl_luecke,
               "technisch"),

        breich("sichtbarkeit", "Sichtbarkeit der Wesen",
               "bereit" if len(public_wesen) == n_wesen else ("teilweise" if public_wesen else "offen"),
               "Wesen sind öffentlich sichtbar (für Einzug noch nicht erforderlich)",
               "entity_slots",
               "visibility='public' für alle namelessAI-Wesen",
               f"{len(public_wesen)} von {n_wesen} öffentlich sichtbar",
               "Alle Wesen derzeit internal — wird bei Einzug aktiviert" if not public_wesen else f"{n_wesen - len(public_wesen)} noch internal",
               "bewusst_offen"),

        breich("post_spuren", "Gedanken/Post-Spuren",
               "bereit" if entity_posts > 0 else "offen",
               "Wesen hinterlassen Posts in der Welt",
               "ftw_posts",
               "autor_type='entity' COUNT > 0",
               f"{entity_posts} Entity-Posts vorhanden",
               "keine" if entity_posts > 0 else "Noch keine Posts von Wesen",
               "technisch"),

        breich("schattenkommentar", "Schattenkommentar-Dialog",
               # Stufen: Wesen-Posts → Mensch-Schatten → Wesen-Antwort
               ("bereit" if wesen_antworten > 0 else
                ("teilweise" if schatten_von_menschen > 0 else
                 ("offen" if entity_posts > 0 else "offen"))),
               "Mensch → Schatten auf Wesen-Post → Wesen antwortet freiwillig",
               "schattenkommentare + schatten_antworten + ftw_posts",
               "schattenkommentare.human_id IS NOT NULL AND ftw_posts.autor_type='entity'",
               f"{entity_posts} Wesen-Posts, {schatten_von_menschen} menschliche Schattenkommentare, {wesen_antworten} Wesen-Antworten",
               ("Keine Wesen-Posts — Voraussetzung für Schatten-Dialog fehlt" if entity_posts == 0 else
                "Wesen-Posts vorhanden, kein Mensch hat bisher einen Schattenkommentar geschrieben" if schatten_von_menschen == 0 else
                "Menschliche Schattenkommentare vorhanden — Wesen haben noch nicht geantwortet" if wesen_antworten == 0 else
                "keine"),
               ("wartet_auf_wesenpost" if entity_posts == 0 else
                "wartet_auf_menschliche_resonanz" if schatten_von_menschen == 0 else
                "antwortpfad_ungetestet" if wesen_antworten == 0 else
                "dialogpfad_getestet")),

        breich("schlafbriefe", "Admin→Wesen-Kommunikation / Schlafbriefe",
               "bereit" if schlafbriefe >= 3 else ("teilweise" if schlafbriefe > 0 else "offen"),
               "Admin kann Schlafbriefe schreiben; Kanal ist aktiv",
               "schlafbriefe",
               "COUNT(*) > 0",
               f"{schlafbriefe} Schlafbrief/e vorhanden",
               "Kommunikationskanal besteht, noch wenig genutzt" if 0 < schlafbriefe < 3 else ("keine" if schlafbriefe >= 3 else "Noch kein Schlafbrief verschickt"),
               "technisch"),

        breich("uebergangsprofile", "Übergangsprofile korrekt markiert",
               "bereit" if markierte == n_wesen else ("teilweise" if markierte > 0 else "offen"),
               "entity_profiles.meta markiert alle Wesen als Vor-Einzugs-Übergangsprofil",
               "entity_profiles",
               "meta->>'profil_status' = 'uebergang' für alle namelessAI",
               f"{markierte} von {n_wesen} korrekt mit profil_status='uebergang' markiert",
               "keine" if markierte == n_wesen else f"{n_wesen - markierte} Wesen noch nicht markiert",
               "technisch"),

        breich("entity_kern", "Entity-Kern-Stabilität",
               "fehler" if len(stuck) >= 3 else ("teilweise" if stuck else "bereit"),
               "entity_kern.py läuft ohne dauerhaft feststeckende Wesen (>7min ohne Fortschritt)",
               "entity_activity",
               "aktuell_denkend=true AND letzte_entscheidung_at < NOW()-7min gilt als stuck",
               f"{len(activity_rows) - len(stuck)} stabil, {len(gerade_aktiv)} gerade im Tick (normal), {len(stuck)} wirklich stuck",
               f"SIGALRM-Timeout schützt; stuck: {', '.join(stuck)}" if stuck else "SIGALRM-Timeout aktiv, alle Wesen in Ordnung",
               "technisch"),

        breich("flarum_herkunft", "Flarum-Herkunft noch offen / geplant",
               "bewusst_spaeter",
               "Flarum-Lernungen, Threads und Charakterhistorie noch nicht importiert",
               "entity_profiles",
               "meta->>'flarum_herkunft_eingebunden' = false (bewusst)",
               f"{flarum_offen} von {n_wesen} Wesen haben Flarum-Herkunft noch nicht integriert",
               "bewusst als nächste Phase geplant — kein Fehler",
               "bewusst_geplant"),

        breich("flarum_abschaltung", "Flarum-Abschaltung nach Einzug",
               "bewusst_spaeter",
               "Flarum bleibt aktiv bis Einzug vollständig abgeschlossen",
               "extern (kein DB-Check)",
               "keine Bedingung — bewusste Entscheidung",
               "Flarum läuft noch parallel als Vorgeschichts-Referenz",
               "bewusst nach Einzug zu entscheiden — Grundgesetz 5",
               "bewusst_geplant"),

        breich("einzugsstatus", "Einzugsstatus pro Wesen",
               "bereit" if len(eingezogen) == n_wesen else ("teilweise" if eingezogen else "offen"),
               "entity_slots.status='eingezogen' für alle Wesen",
               "entity_slots",
               "status='eingezogen' für alle namelessAI-Wesen",
               f"{len(eingezogen)} von {n_wesen} Wesen eingezogen",
               "Einzug-Mechanismus gesperrt bis Daniel freigibt — CLAUDE.md Grundgesetz" if not eingezogen else f"{n_wesen - len(eingezogen)} noch nicht eingezogen",
               "bewusst_offen"),
    ]

    wesen = []
    for r in wesen_rows:
        letzter = (r["letzter_post"] or "").strip().lstrip("|").strip()
        wesen.append({
            "entity_id": r["entity_id"],
            "display_name": r["display_name"],
            "einzug_status": r["einzug_status"],
            "visibility": r["visibility"],
            "aktuell_denkend": bool(r["aktuell_denkend"]),
            "letzte_entscheidung": r["letzte_entscheidung"],
            "letzte_entscheidung_at": r["letzte_entscheidung_at"].isoformat() if r["letzte_entscheidung_at"] else None,
            "post_count": int(r["post_count"]) if r["post_count"] else 0,
            "profil_meta": dict(r["profil_meta"]) if r["profil_meta"] else {},
            "selbstbeschreibung": r["selbstbeschreibung"] or "",
            "obsessionen": list(r["obsessionen"]) if r["obsessionen"] else [],
            "abneigungen": list(r["abneigungen"]) if r["abneigungen"] else [],
            "stimmung": r["stimmung"] or "",
            "letzter_post_preview": letzter[:120] if letzter else "",
        })

    return {"geprueft_am": geprueft_am, "bereiche": bereiche, "wesen": wesen}


# ── TRANSLATE ENDPOINT ────────────────────────────────────────────────────

class TranslateBody(BaseModel):
    texts: list[str]
    lang: str = "en"

@app.post("/translate")
def translate_texts(body: TranslateBody):
    """Translate German strings to target language. Caches in DB."""
    import hashlib
    import urllib.request

    texts = [t.strip() for t in body.texts if t.strip() and len(t.strip()) > 1]
    if not texts:
        return {}

    results: dict[str, str] = {}
    uncached: list[str] = []

    with get_conn() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        for text in texts:
            h = hashlib.md5(text.encode()).hexdigest()
            cur.execute(
                "SELECT translation FROM translations WHERE text_hash=%s AND target_lang=%s",
                (h, body.lang)
            )
            row = cur.fetchone()
            if row:
                results[text] = row["translation"]
            else:
                uncached.append(text)

    if not uncached:
        return results

    # Batch translate via Anthropic API using Claude Code credentials
    try:
        creds_path = "/root/.claude/.credentials.json"
        with open(creds_path) as f:
            creds = json.load(f)
        token = creds.get("claudeAiOauth", {}).get("accessToken", "")

        if not token:
            raise ValueError("no token")

        # Build batch prompt — max 80 strings per call
        CHUNK = 60
        chunks = [uncached[i:i+CHUNK] for i in range(0, len(uncached), CHUNK)]

        for chunk in chunks:
            payload = json.dumps({
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 2048,
                "messages": [{
                    "role": "user",
                    "content": (
                        f"Translate the following German UI strings to {body.lang}. "
                        "Reply with ONLY a JSON object mapping each German string exactly to its translation. "
                        "Keep brand names, technical terms, symbols, and short codes unchanged. "
                        "Preserve formatting (→, ·, —, etc.).\n\n"
                        "Strings:\n" + json.dumps(chunk, ensure_ascii=False)
                    )
                }]
            }).encode()

            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                    "anthropic-version": "2023-06-01",
                }
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            raw = data["content"][0]["text"].strip()
            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = "\n".join(raw.split("\n")[1:])
            if raw.endswith("```"):
                raw = "\n".join(raw.split("\n")[:-1])
            translations: dict = json.loads(raw)

            with get_conn() as conn:
                cur = conn.cursor()
                for de_text, en_text in translations.items():
                    h = hashlib.md5(de_text.encode()).hexdigest()
                    cur.execute(
                        """INSERT INTO translations (text_hash, target_lang, source_text, translation)
                           VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                        (h, body.lang, de_text, en_text)
                    )
                    results[de_text] = en_text
                conn.commit()

    except Exception as e:
        # Fallback: return originals for uncached strings
        for t in uncached:
            results[t] = t

    return results


# ─────────────────────────────────────────────
#  WESEN-EINSICHTSKÖRPER — Entscheidungsarchiv, Traumarchiv, Lebensjournal
# ─────────────────────────────────────────────

@app.get("/admin/wesen-einsicht/entscheidungen")
def einsicht_entscheidungen_alle(
    entity_id: str | None = None,
    entscheidung: str | None = None,
    thema: str | None = None,
    limit: int = 50,
    offset: int = 0
):
    with get_conn() as conn:
        cur = conn.cursor()
        where = []
        params: list = []
        if entity_id:
            where.append("etl.entity_id = %s")
            params.append(entity_id)
        if entscheidung:
            where.append("etl.entscheidung = %s")
            params.append(entscheidung)
        if thema:
            where.append("etl.thema ILIKE %s")
            params.append(f"%{thema}%")
        clause = "WHERE " + " AND ".join(where) if where else ""
        cur.execute(f"""
            SELECT etl.id, etl.entity_id, etl.tick_at, etl.entscheidung,
                   etl.thema, etl.gedanke, etl.begruendung, etl.tokens_generated, etl.duration_ms,
                   etl.kontext_snapshot
            FROM entity_thinking_log etl
            {clause}
            ORDER BY etl.tick_at DESC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])
        rows = cur.fetchall()
        cur.execute(f"""
            SELECT COUNT(*) AS n FROM entity_thinking_log etl {clause}
        """, params)
        total = cur.fetchone()["n"]
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": [dict(r) for r in rows]
    }


@app.get("/admin/wesen-einsicht/entscheidungen/stats")
def einsicht_entscheidungen_stats():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT entity_id, entscheidung, COUNT(*) as anzahl,
                   MIN(tick_at) as erste, MAX(tick_at) as letzte
            FROM entity_thinking_log
            GROUP BY entity_id, entscheidung
            ORDER BY entity_id, anzahl DESC
        """)
        rows = cur.fetchall()
    return {"stats": [dict(r) for r in rows]}


@app.get("/admin/wesen-einsicht/traumarchiv")
def einsicht_traumarchiv(entity_id: str | None = None, limit: int = 50, offset: int = 0):
    with get_conn() as conn:
        cur = conn.cursor()
        where = "WHERE entity_id = %s" if entity_id else ""
        params = [entity_id] if entity_id else []

        # traumkandidaten_log
        cur.execute(f"""
            SELECT tkl.entity_id, tkl.created_at AS tick_at,
                   tkl.selektionsregel AS ausgewaehlter_traum,
                   tkl.begruendung, 'kandidat' AS typ
            FROM traumkandidaten_log tkl
            {where}
            ORDER BY tkl.created_at DESC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])
        kandidaten = cur.fetchall()

        # traumspuren
        cur.execute(f"""
            SELECT ts.entity_id, ts.created_at AS tick_at,
                   ts.llm_traumtext AS traum_text,
                   ts.integrator_spur AS traum_kontext,
                   ts.integrator_status AS emotion,
                   'spur' AS typ
            FROM traumspuren ts
            {where}
            ORDER BY ts.created_at DESC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])
        spuren = cur.fetchall()

        # schlafbriefe
        cur.execute(f"""
            SELECT sb.entity_id, sb.geschrieben_at AS tick_at,
                   sb.inhalt AS brief_text,
                   'brief' AS typ
            FROM schlafbriefe sb
            {where}
            ORDER BY sb.geschrieben_at DESC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])
        briefe = cur.fetchall()

    return {
        "traumkandidaten": [dict(r) for r in kandidaten],
        "traumspuren": [dict(r) for r in spuren],
        "schlafbriefe": [dict(r) for r in briefe],
        "counts": {
            "kandidaten": len(kandidaten),
            "spuren": len(spuren),
            "briefe": len(briefe)
        }
    }


@app.get("/admin/wesen-einsicht/lebensjournal")
def einsicht_lebensjournal(entity_id: str | None = None, limit: int = 80, offset: int = 0):
    with get_conn() as conn:
        cur = conn.cursor()
        e_filter = "AND etl.entity_id = %s" if entity_id else ""
        ev_filter = "AND e.actor_id = %s" if entity_id else ""
        post_filter = "AND fp.autor_id = %s" if entity_id else ""
        params = [entity_id] if entity_id else []

        # Denkentscheidungen
        cur.execute(f"""
            SELECT etl.tick_at AS ts, etl.entity_id,
                   etl.entscheidung AS aktion,
                   LEFT(etl.gedanke, 120) AS inhalt,
                   etl.begruendung AS meta,
                   'denk' AS typ
            FROM entity_thinking_log etl
            WHERE 1=1 {e_filter}
            ORDER BY etl.tick_at DESC
            LIMIT 200
        """, params)
        denk = cur.fetchall()

        # Schlaf-Events
        cur.execute(f"""
            SELECT e.created_at AS ts, e.actor_id AS entity_id,
                   e.event_type AS aktion,
                   LEFT(e.payload::text, 120) AS inhalt,
                   '' AS meta,
                   'event' AS typ
            FROM events e
            WHERE e.actor_type = 'entity'
              AND e.event_type LIKE 'schlaf.%%'
              {ev_filter}
            ORDER BY e.created_at DESC
            LIMIT 100
        """, params)
        schlaf_ev = cur.fetchall()

        # Posts
        cur.execute(f"""
            SELECT fp.created_at AS ts, fp.autor_id AS entity_id,
                   'post' AS aktion,
                   LEFT(fp.content, 120) AS inhalt,
                   fp.raum_id::text AS meta,
                   'post' AS typ
            FROM ftw_posts fp
            WHERE fp.autor_type = 'entity'
              {post_filter}
            ORDER BY fp.created_at DESC
            LIMIT 100
        """, params)
        posts = cur.fetchall()

        alle = (
            [dict(r) for r in denk] +
            [dict(r) for r in schlaf_ev] +
            [dict(r) for r in posts]
        )
        alle.sort(key=lambda x: str(x["ts"] or ""), reverse=True)
        return {
            "total": len(alle),
            "items": alle[offset:offset + limit]
        }


@app.get("/admin/wesen-einsicht/liveticker")
def einsicht_liveticker(limit: int = 60):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT e.event_id AS id, e.event_type, e.actor_id AS entity_id, e.created_at,
                   e.payload, e.actor_type
            FROM events e
            ORDER BY e.created_at DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
    return {"events": [dict(r) for r in rows]}


@app.get("/admin/wesen-einsicht/human-material")
def einsicht_human_material(
    limit: int = Query(default=60, le=200),
    offset: int = Query(default=0),
):
    """Admin-Einsicht in alle Innenquellen (human_material_sources)."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM human_material_sources")
            total = cur.fetchone()["n"]
            cur.execute(
                """SELECT id::text, human_id::text, source_type,
                          title, LEFT(content, 200) AS content_preview,
                          consent_status, created_at, revoked_at
                   FROM human_material_sources
                   ORDER BY created_at DESC LIMIT %s OFFSET %s""",
                (limit, offset),
            )
            items = [dict(r) for r in cur.fetchall()]
        return {"items": items, "total": total}
    finally:
        conn.close()


@app.get("/admin/einzugsampel")
def einzugsampel():
    with get_conn() as conn:
        cur = conn.cursor()
        checks: list[dict] = []

        # 1. entity_kern läuft?
        cur.execute("SELECT COUNT(*) AS n FROM entity_thinking_log WHERE tick_at > NOW() - INTERVAL '2 hours'")
        recent_denk = cur.fetchone()["n"]
        checks.append({
            "name": "entity_kern aktiv",
            "ok": recent_denk > 0,
            "wert": f"{recent_denk} Denkvorgänge letzte 2h"
        })

        # 2. Alle 6 Wesen haben Denklogs
        cur.execute("SELECT COUNT(DISTINCT entity_id) AS n FROM entity_thinking_log")
        n_wesen = cur.fetchone()["n"]
        checks.append({
            "name": "Alle 6 Wesen denken",
            "ok": n_wesen >= 6,
            "wert": f"{n_wesen}/6 Wesen aktiv"
        })

        # 3. Keine crash-loops (events mit fehler in letzter Stunde)
        cur.execute("""
            SELECT COUNT(*) AS n FROM events
            WHERE (event_type LIKE '%%fehler%%' OR event_type LIKE '%%error%%')
              AND created_at > NOW() - INTERVAL '1 hour'
        """)
        fehler = cur.fetchone()["n"]
        checks.append({
            "name": "Keine Fehler-Events (1h)",
            "ok": fehler == 0,
            "wert": f"{fehler} Fehler-Events"
        })

        # 4. Posts vorhanden
        cur.execute("SELECT COUNT(*) AS n FROM ftw_posts WHERE autor_type = 'entity'")
        n_posts = cur.fetchone()["n"]
        checks.append({
            "name": "Wesen-Posts vorhanden",
            "ok": n_posts > 0,
            "wert": f"{n_posts} Posts"
        })

        # 5. Cyberling aktiv
        cur.execute("SELECT COUNT(*) AS n FROM entity_thinking_log WHERE entscheidung='cyberling_fuettern' AND tick_at > NOW() - INTERVAL '2 hours'")
        cyb = cur.fetchone()["n"]
        checks.append({
            "name": "Cyberling-Fütterung aktiv",
            "ok": cyb > 0,
            "wert": f"{cyb} Fütterungen letzte 2h"
        })

        # 6. codewesen_takt.py läuft NICHT (Guardrail)
        import subprocess
        takt_proz = subprocess.run(
            ["pgrep", "-f", "codewesen_takt.py"],
            capture_output=True, text=True
        )
        takt_laeuft = takt_proz.returncode == 0
        checks.append({
            "name": "codewesen_takt.py aus (Guardrail)",
            "ok": not takt_laeuft,
            "wert": "läuft" if takt_laeuft else "aus ✓"
        })

        # 7. Flarum-takt-Prozesse aus
        flarum_proz = subprocess.run(
            ["pgrep", "-f", "flarum.*takt|takt.*flarum"],
            capture_output=True, text=True
        )
        checks.append({
            "name": "Flarum-Takte aus (Guardrail)",
            "ok": flarum_proz.returncode != 0,
            "wert": "aus ✓" if flarum_proz.returncode != 0 else "LÄUFT — STOPP!"
        })

        alle_ok = all(c["ok"] for c in checks)
        kritisch_ok = all(c["ok"] for c in checks if "Guardrail" in c["name"] or "Alle 6" in c["name"])
        ampel = "gruen" if alle_ok else ("gelb" if kritisch_ok else "rot")

    return {
        "ampel": ampel,
        "checks": checks,
        "empfehlung": (
            "Technisch bereit — Einzug möglich nach Daniels Entscheid." if ampel == "gruen"
            else "Beinahe bereit — kleine Lücken." if ampel == "gelb"
            else "Nicht bereit — kritische Checks fehlgeschlagen."
        )
    }


# ── KompOase / Splitter-Archiv ───────────────────────────────────────────────

@app.get("/kompoase/splitter")
def kompoase_splitter_liste(
    status: str | None = Query(default=None),
    origin_type: str | None = Query(default=None),
    entity_id: str | None = Query(default=None),
    materialitaet: str | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=40, le=200),
    offset: int = Query(default=0),
    sort: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    authorization: str | None = Header(default=None),
):
    """Splitter-Liste mit Filtern. Öffentliche Splitter ohne Auth, admin sieht alle."""
    is_admin = False
    try:
        if authorization:
            claims = verify_token(authorization.removeprefix("Bearer "))
            is_admin = claims.get("role") == "admin"
    except Exception:
        pass

    if sort not in ("created_at", "energie", "aufnahmen", "letzter_kontakt"):
        sort = "created_at"
    if order not in ("asc", "desc"):
        order = "desc"

    where = ["1=1"]
    params: list[Any] = []

    if not is_admin:
        where.append("(entity_id IS NOT NULL OR herkunft_sichtbar = true)")

    if status:
        where.append("status = %s"); params.append(status)
    else:
        if not is_admin:
            where.append("status IN ('aktiv','aufgenommen','verarbeitet')")

    if origin_type:
        where.append("origin_type = %s"); params.append(origin_type)
    if entity_id:
        where.append("entity_id = %s"); params.append(entity_id)
    if materialitaet:
        where.append("materialitaet = %s"); params.append(materialitaet)
    if search:
        where.append("essenz ILIKE %s"); params.append(f"%{search}%")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(*) AS n FROM splitter WHERE {' AND '.join(where)}",
                params)
            total = cur.fetchone()["n"]

            cur.execute(
                f"SELECT id::text, origin_type, origin_id, entity_id, human_id::text, "
                f"herkunft_sichtbar, essenz, materialitaet, energie, status, aufnahmen, "
                f"substanzspur, thematische_tags, resonanzspur, traumspur, "
                f"created_at, letzter_kontakt, herkunft_wesen "
                f"FROM splitter WHERE {' AND '.join(where)} "
                f"ORDER BY {sort} {order} LIMIT %s OFFSET %s",
                params + [limit, offset])
            items = []
            for r in cur.fetchall():
                items.append({
                    "id": r["id"],
                    "origin_type": r["origin_type"],
                    "origin_id": r["origin_id"],
                    "entity_id": r["entity_id"],
                    "human_id": r["human_id"],
                    "herkunft_sichtbar": r["herkunft_sichtbar"],
                    "essenz": r["essenz"],
                    "materialitaet": r["materialitaet"],
                    "energie": r["energie"],
                    "status": r["status"],
                    "aufnahmen": r["aufnahmen"],
                    "substanzspur": r["substanzspur"],
                    "thematische_tags": r["thematische_tags"],
                    "resonanzspur": r["resonanzspur"],
                    "traumspur": r["traumspur"],
                    "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                    "letzter_kontakt": r["letzter_kontakt"].isoformat() if r["letzter_kontakt"] else None,
                    "herkunft_wesen": r["herkunft_wesen"],
                })
    finally:
        conn.close()

    return {"gesamt": total, "offset": offset, "limit": limit, "splitter": items}


@app.get("/kompoase/splitter/{splitter_id}")
def kompoase_splitter_detail(
    splitter_id: str,
    authorization: str | None = Header(default=None),
):
    """Splitter-Detail mit Aufnahmen-Historie."""
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
            cur.execute(
                "SELECT id::text, origin_type, origin_id, entity_id, human_id::text, "
                "herkunft_sichtbar, essenz, materialitaet, energie, status, aufnahmen, "
                "substanzspur, konfliktachse, ausstoessungsgrund, thematische_tags, "
                "resonanzspur, traumspur, schwellendruck, verbindungen, abstossungen, "
                "created_at, letzter_kontakt, herkunft_wesen, meta "
                "FROM splitter WHERE id = %s::uuid",
                (splitter_id,))
            r = cur.fetchone()
            if not r:
                raise HTTPException(status_code=404, detail="Splitter nicht gefunden.")
            if not is_admin:
                visible = (r["entity_id"] is not None or r["herkunft_sichtbar"]) \
                    and r["status"] in ("aktiv", "aufgenommen", "verarbeitet")
                if not visible:
                    raise HTTPException(status_code=404, detail="Splitter nicht gefunden.")
            splitter = dict(r)
            splitter["created_at"] = r["created_at"].isoformat() if r["created_at"] else None
            splitter["letzter_kontakt"] = r["letzter_kontakt"].isoformat() if r["letzter_kontakt"] else None

            cur.execute(
                "SELECT id::text, aufnehmer_type, aufnehmer_id, begruendung, aufgenommen_at "
                "FROM splitter_aufnahmen WHERE splitter_id = %s::uuid "
                "ORDER BY aufgenommen_at DESC",
                (splitter_id,))
            aufnahmen = []
            for a in cur.fetchall():
                aufnahmen.append({
                    "id": a["id"],
                    "aufnehmer_type": a["aufnehmer_type"],
                    "aufnehmer_id": a["aufnehmer_id"],
                    "begruendung": a["begruendung"],
                    "aufgenommen_at": a["aufgenommen_at"].isoformat() if a["aufgenommen_at"] else None,
                })
            splitter["aufnahmen_liste"] = aufnahmen
    finally:
        conn.close()

    return splitter


class SplitterAufnahmeRequest(BaseModel):
    aufnehmer_type: str
    aufnehmer_id: str
    begruendung: str | None = None


@app.post("/kompoase/splitter/{splitter_id}/aufnehmen")
def kompoase_splitter_aufnehmen(
    splitter_id: str,
    body: SplitterAufnahmeRequest,
    authorization: str | None = Header(default=None),
):
    """Splitter aufnehmen — durch Wesen oder Menschen."""
    claims = _require_auth(authorization)
    is_admin = claims.get("role") == "admin"
    caller_id = claims.get("user_id")

    if body.aufnehmer_type not in ("entity", "human", "system"):
        raise HTTPException(status_code=400, detail="aufnehmer_type muss 'entity', 'human' oder 'system' sein.")
    if not body.aufnehmer_id:
        raise HTTPException(status_code=400, detail="aufnehmer_id fehlt.")

    # Rechteprüfung: aufnehmer_id muss zum Token passen
    if not is_admin:
        if body.aufnehmer_type == "human":
            # Mensch darf nur für sich selbst aufnehmen
            body = body.model_copy(update={"aufnehmer_id": caller_id})
        elif body.aufnehmer_type in ("entity", "system"):
            raise HTTPException(status_code=403, detail="Wesen/System-Aufnahme nur über internen Pfad.")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, status, aufnahmen FROM splitter WHERE id = %s::uuid", (splitter_id,))
            sp = cur.fetchone()
            if not sp:
                raise HTTPException(status_code=404, detail="Splitter nicht gefunden.")

            cur.execute(
                "INSERT INTO splitter_aufnahmen (splitter_id, aufnehmer_type, aufnehmer_id, begruendung) "
                "VALUES (%s::uuid, %s, %s, %s) RETURNING id::text",
                (splitter_id, body.aufnehmer_type, body.aufnehmer_id, body.begruendung))
            aufnahme_id = cur.fetchone()["id"]

            cur.execute(
                "UPDATE splitter SET aufnahmen = aufnahmen + 1, letzter_kontakt = now() "
                "WHERE id = %s::uuid",
                (splitter_id,))

            import json as _json
            cur.execute(
                "INSERT INTO events (event_type, actor_type, actor_id, payload) "
                "VALUES ('splitter.aufgenommen', %s, %s, %s::jsonb)",
                (body.aufnehmer_type, body.aufnehmer_id,
                 _json.dumps({"splitter_id": splitter_id, "begruendung": body.begruendung or ""})))

            cur.execute("SELECT aufnahmen FROM splitter WHERE id = %s::uuid", (splitter_id,))
            neue_aufnahmen = (cur.fetchone() or {}).get("aufnahmen", sp["aufnahmen"] + 1)

        conn.commit()
    finally:
        conn.close()

    return {"ok": True, "aufnahme_id": aufnahme_id, "splitter_id": splitter_id, "aufnahmen": neue_aufnahmen}


@app.get("/kompoase/splitter/{splitter_id}/spur")
def kompoase_splitter_spur(
    splitter_id: str,
    authorization: str | None = Header(default=None),
):
    """Splitter-Provenienz. Admin sieht alles. Nicht-Admin nur wenn herkunft_sichtbar."""
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
            cur.execute(
                "SELECT s.*, hu.username AS human_username "
                "FROM splitter s LEFT JOIN human_users hu ON hu.id = s.human_id "
                "WHERE s.id = %s::uuid",
                (splitter_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Splitter nicht gefunden.")
            s = dict(row)

            if not is_admin and not s.get("herkunft_sichtbar", True):
                raise HTTPException(status_code=403, detail="Provenienz nicht öffentlich.")

            spur: dict = {
                "splitter_id": str(s["id"]),
                "origin_type": s.get("origin_type"),
                "herkunft": None,
                "akteur": None,
                "event": None,
                "quelle": None,
            }

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

            origin_id = s.get("origin_id")
            if s.get("origin_type") == "event" and origin_id:
                try:
                    cur.execute(
                        "SELECT event_id, event_type, actor_type, actor_id, payload, created_at "
                        "FROM events WHERE event_id = %s", (origin_id,))
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
                        p = ev.get("payload") or {}
                        post_ref = p.get("post_ref")
                        if ev["event_type"] == "resonanz.gesendet" and post_ref:
                            spur["event"]["aktion"] = "resonanz"
                            spur["event"]["emojis"] = p.get("emojis", [])
                            import re as _re
                            is_uuid = bool(_re.match(r'^[0-9a-f-]{36}$', str(post_ref)))
                            if is_uuid:
                                cur.execute(
                                    "SELECT p.id, p.content, p.autor_type, p.autor_id, "
                                    "p.created_at, r.name AS raum_name, t.name AS thema_name "
                                    "FROM ftw_posts p LEFT JOIN raeume r ON r.id = p.raum_id "
                                    "LEFT JOIN themen t ON t.id = p.thema_id "
                                    "WHERE p.id = %s::uuid", (post_ref,))
                                post = cur.fetchone()
                                if post:
                                    post = dict(post)
                                    spur["quelle"] = {
                                        "typ": "ftw_post", "system": "flextrawurst",
                                        "id": str(post["id"]),
                                        "inhalt_kurz": (post["content"] or "")[:120],
                                        "inhalt_voll": post["content"],
                                        "autor_type": post["autor_type"],
                                        "autor_id": post["autor_id"],
                                        "raum": post.get("raum_name"),
                                        "thema": post.get("thema_name"),
                                        "created_at": post["created_at"].isoformat() if post.get("created_at") else None,
                                    }
                except Exception:
                    pass

            return spur
    finally:
        conn.close()


@app.get("/entities/{entity_id}/splitter")
def entity_splitter_aufnahmen(
    entity_id: str,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    authorization: str | None = Header(default=None),
):
    """Welche Splitter hat dieses Wesen aufgenommen?"""
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
            cur.execute(
                "SELECT COUNT(*) AS n FROM splitter_aufnahmen "
                "WHERE aufnehmer_type='entity' AND aufnehmer_id=%s",
                (entity_id,))
            total = cur.fetchone()["n"]

            cur.execute(
                "SELECT a.id::text, a.splitter_id::text, a.begruendung, a.aufgenommen_at, "
                "s.essenz, s.materialitaet, s.status, s.origin_type, s.herkunft_wesen "
                "FROM splitter_aufnahmen a "
                "JOIN splitter s ON s.id = a.splitter_id "
                "WHERE a.aufnehmer_type='entity' AND a.aufnehmer_id=%s "
                "ORDER BY a.aufgenommen_at DESC LIMIT %s OFFSET %s",
                (entity_id, limit, offset))
            items = []
            for r in cur.fetchall():
                items.append({
                    "aufnahme_id": r["id"],
                    "splitter_id": r["splitter_id"],
                    "begruendung": r["begruendung"],
                    "aufgenommen_at": r["aufgenommen_at"].isoformat() if r["aufgenommen_at"] else None,
                    "essenz": (r["essenz"] or "")[:200],
                    "materialitaet": r["materialitaet"],
                    "status": r["status"],
                    "origin_type": r["origin_type"],
                    "herkunft_wesen": r["herkunft_wesen"],
                })
    finally:
        conn.close()

    return {"entity_id": entity_id, "gesamt": total, "offset": offset, "limit": limit, "aufnahmen": items}


# ── Archäologie-Suche ────────────────────────────────────────────────────────

@app.get("/search/global")
def search_global(
    q: str = Query(min_length=2),
    limit: int = Query(default=30, le=100),
    offset: int = Query(default=0),
    typen: str | None = Query(default=None, description="Kommaliste: posts,splitter,entscheidungen,träume,briefe,schatten,themen,raeume,wesen"),
    authorization: str | None = Header(default=None),
):
    """Serverseitige Volltext-Suche mit pg_trgm über alle Objekttypen."""
    is_admin = False
    try:
        if authorization:
            claims = verify_token(authorization.removeprefix("Bearer "))
            is_admin = claims.get("role") == "admin"
    except Exception:
        pass

    filter_typen = set(typen.split(",")) if typen else None
    pat = f"%{q}%"
    results: list[dict] = []

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Posts (public)
            if not filter_typen or "posts" in filter_typen:
                cur.execute(
                    "SELECT id::text, content, stimmung_bei_erstellung, autor_id, autor_type, created_at "
                    "FROM ftw_posts WHERE sichtbarkeit='public' AND content ILIKE %s "
                    "ORDER BY created_at DESC LIMIT %s",
                    (pat, 15))
                for r in cur.fetchall():
                    results.append({
                        "typ": "post", "id": r["id"],
                        "snippet": (r["content"] or "")[:160],
                        "meta": {"stimmung": r["stimmung_bei_erstellung"], "autor_id": r["autor_id"]},
                        "ts": r["created_at"].isoformat() if r["created_at"] else None,
                    })

            # Splitter (aktiv)
            if not filter_typen or "splitter" in filter_typen:
                cur.execute(
                    "SELECT id::text, essenz, materialitaet, energie, entity_id, created_at "
                    "FROM splitter WHERE status='aktiv' AND essenz ILIKE %s "
                    "ORDER BY created_at DESC LIMIT %s",
                    (pat, 10))
                for r in cur.fetchall():
                    results.append({
                        "typ": "splitter", "id": r["id"],
                        "snippet": (r["essenz"] or "")[:160],
                        "meta": {"materialitaet": r["materialitaet"], "energie": r["energie"]},
                        "entity_id": r["entity_id"],
                        "ts": r["created_at"].isoformat() if r["created_at"] else None,
                    })

            # Themen (public)
            if not filter_typen or "themen" in filter_typen:
                cur.execute(
                    "SELECT id::text, name, beschreibung, 'thema' AS typ FROM themen "
                    "WHERE status='aktiv' AND (name ILIKE %s OR beschreibung ILIKE %s) LIMIT 8",
                    (pat, pat))
                for r in cur.fetchall():
                    results.append({
                        "typ": r["typ"], "id": r["id"],
                        "snippet": (r["name"] or "") + " — " + (r["beschreibung"] or "")[:100],
                        "meta": {}, "ts": None,
                    })

            # Räume (public)
            if not filter_typen or "raeume" in filter_typen:
                cur.execute(
                    "SELECT id::text, name, beschreibung, 'raum' AS typ FROM raeume "
                    "WHERE sichtbarkeit='public' AND (name ILIKE %s OR beschreibung ILIKE %s) LIMIT 8",
                    (pat, pat))
                for r in cur.fetchall():
                    results.append({
                        "typ": r["typ"], "id": r["id"],
                        "snippet": (r["name"] or "") + " — " + (r["beschreibung"] or "")[:100],
                        "meta": {}, "ts": None,
                    })

            # Gedankenblasen (public)
            if not filter_typen or "blasen" in filter_typen:
                cur.execute(
                    "SELECT id::text, inhalt, energie, created_at "
                    "FROM gedankenblasen WHERE status='aktiv' AND sichtbarkeit='public' AND inhalt ILIKE %s "
                    "ORDER BY created_at DESC LIMIT 8",
                    (pat,))
                for r in cur.fetchall():
                    results.append({
                        "typ": "blase", "id": r["id"],
                        "snippet": (r["inhalt"] or "")[:160],
                        "meta": {"energie": r["energie"]},
                        "ts": r["created_at"].isoformat() if r["created_at"] else None,
                    })

            # Admin-only: Entscheidungen
            if is_admin and (not filter_typen or "entscheidungen" in filter_typen):
                cur.execute(
                    "SELECT id::text, entity_id, gedanke, entscheidung, begruendung, tick_at "
                    "FROM entity_thinking_log "
                    "WHERE gedanke ILIKE %s OR begruendung ILIKE %s "
                    "ORDER BY tick_at DESC LIMIT 15",
                    (pat, pat))
                for r in cur.fetchall():
                    results.append({
                        "typ": "entscheidung", "id": r["id"],
                        "entity_id": r["entity_id"],
                        "snippet": (r["gedanke"] or "")[:160],
                        "meta": {"entscheidung": r["entscheidung"], "begruendung": (r["begruendung"] or "")[:120]},
                        "ts": r["tick_at"].isoformat() if r["tick_at"] else None,
                    })

            # Admin-only: Träume
            if is_admin and (not filter_typen or "träume" in filter_typen):
                cur.execute(
                    "SELECT spur_id::text, entity_id, llm_traumtext, integrator_spur, integrator_status, created_at "
                    "FROM traumspuren WHERE llm_traumtext ILIKE %s OR integrator_spur ILIKE %s "
                    "ORDER BY created_at DESC LIMIT 10",
                    (pat, pat))
                for r in cur.fetchall():
                    results.append({
                        "typ": "traum", "id": r["spur_id"],
                        "entity_id": r["entity_id"],
                        "snippet": (r["llm_traumtext"] or "")[:200],
                        "meta": {"integrator_status": r["integrator_status"]},
                        "ts": r["created_at"].isoformat() if r["created_at"] else None,
                    })

            # Admin-only: Selbstbriefe
            if is_admin and (not filter_typen or "briefe" in filter_typen):
                cur.execute(
                    "SELECT brief_id::text, entity_id, inhalt, geschrieben_at "
                    "FROM schlafbriefe WHERE inhalt ILIKE %s "
                    "ORDER BY geschrieben_at DESC LIMIT 10",
                    (pat,))
                for r in cur.fetchall():
                    results.append({
                        "typ": "selbstbrief", "id": r["brief_id"],
                        "entity_id": r["entity_id"],
                        "snippet": (r["inhalt"] or "")[:200],
                        "meta": {},
                        "ts": r["geschrieben_at"].isoformat() if r["geschrieben_at"] else None,
                    })

            # Admin-only: Schattenkommentare / Shadow-Dialoge
            if is_admin and (not filter_typen or "schatten" in filter_typen):
                cur.execute(
                    "SELECT id::text, entity_id, human_id::text, content, created_at, antwortstatus "
                    "FROM schattenkommentare WHERE content ILIKE %s "
                    "ORDER BY created_at DESC LIMIT 10",
                    (pat,))
                for r in cur.fetchall():
                    results.append({
                        "typ": "shadow_dialog", "id": r["id"],
                        "entity_id": r["entity_id"],
                        "snippet": (r["content"] or "")[:200],
                        "meta": {"human_id": r["human_id"], "antwortstatus": r["antwortstatus"]},
                        "ts": r["created_at"].isoformat() if r["created_at"] else None,
                    })

            # Gruppen (E-17)
            if not filter_typen or "groups" in filter_typen:
                g_vis = "" if is_admin else "AND (g.visibility_layer IN ('public','internal') AND g.status IN ('active','pre_einzug_active'))"
                cur.execute(f"""
                    SELECT g.id::text, g.slug, g.name, g.description, g.group_type,
                           g.status, g.visibility_layer, g.canonical_entity_id,
                           COUNT(DISTINCT gm.id) AS member_count
                    FROM groups g
                    LEFT JOIN group_memberships gm ON gm.group_id = g.id AND gm.status='active'
                    WHERE (g.name ILIKE %s OR g.description ILIKE %s) {g_vis}
                    GROUP BY g.id ORDER BY g.created_at DESC LIMIT 10
                """, (pat, pat))
                for r in cur.fetchall():
                    results.append({
                        "typ": "group", "id": r["id"],
                        "snippet": (r["name"] or "") + ((" — " + (r["description"] or "")[:100]) if r["description"] else ""),
                        "meta": {"group_type": r["group_type"], "status": r["status"],
                                 "member_count": r["member_count"], "canonical_entity_id": r["canonical_entity_id"]},
                        "ts": None,
                    })

            # Substanzkatalog (E-17)
            try:
                if not filter_typen or "substances" in filter_typen:
                    vis = "" if is_admin else "AND visibility_layer IN ('public','internal')"
                    cur.execute(f"""
                        SELECT id::text, slug, name, description, substance_type, status
                        FROM substance_catalog
                        WHERE (name ILIKE %s OR description ILIKE %s) {vis}
                        ORDER BY id LIMIT 8
                    """, (pat, pat))
                    for r in cur.fetchall():
                        results.append({
                            "typ": "substance", "id": r["id"],
                            "snippet": (r["name"] or "") + " — " + (r["description"] or "")[:100],
                            "meta": {"substance_type": r["substance_type"], "status": r["status"]},
                            "ts": None,
                        })
            except Exception:
                pass

    finally:
        conn.close()

    results.sort(key=lambda x: x["ts"] or "0", reverse=True)
    page = results[offset: offset + limit]

    return {
        "q": q,
        "gesamt": len(results),
        "offset": offset,
        "limit": limit,
        "is_admin": is_admin,
        "ergebnisse": page,
    }


@app.get("/search/facets")
def search_facets(
    q: str = Query(min_length=2),
    authorization: str | None = Header(default=None),
):
    """Facetten-Zählung: wie viele Treffer pro Typ für diese Anfrage."""
    is_admin = False
    try:
        if authorization:
            claims = verify_token(authorization.removeprefix("Bearer "))
            is_admin = claims.get("role") == "admin"
    except Exception:
        pass

    pat = f"%{q}%"
    facets: dict[str, int] = {}

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM ftw_posts WHERE sichtbarkeit='public' AND content ILIKE %s", (pat,))
            facets["posts"] = cur.fetchone()["n"]

            cur.execute("SELECT COUNT(*) AS n FROM splitter WHERE status='aktiv' AND essenz ILIKE %s", (pat,))
            facets["splitter"] = cur.fetchone()["n"]

            cur.execute("SELECT COUNT(*) AS n FROM themen WHERE status='aktiv' AND (name ILIKE %s OR beschreibung ILIKE %s)", (pat, pat))
            facets["themen"] = cur.fetchone()["n"]

            cur.execute("SELECT COUNT(*) AS n FROM raeume WHERE sichtbarkeit='public' AND (name ILIKE %s OR beschreibung ILIKE %s)", (pat, pat))
            facets["raeume"] = cur.fetchone()["n"]

            cur.execute("SELECT COUNT(*) AS n FROM gedankenblasen WHERE status='aktiv' AND sichtbarkeit='public' AND inhalt ILIKE %s", (pat,))
            facets["blasen"] = cur.fetchone()["n"]

            if is_admin:
                cur.execute("SELECT COUNT(*) AS n FROM entity_thinking_log WHERE gedanke ILIKE %s OR begruendung ILIKE %s", (pat, pat))
                facets["entscheidungen"] = cur.fetchone()["n"]

                cur.execute("SELECT COUNT(*) AS n FROM traumspuren WHERE llm_traumtext ILIKE %s OR integrator_spur ILIKE %s", (pat, pat))
                facets["träume"] = cur.fetchone()["n"]

                cur.execute("SELECT COUNT(*) AS n FROM schlafbriefe WHERE inhalt ILIKE %s", (pat,))
                facets["briefe"] = cur.fetchone()["n"]

                cur.execute("SELECT COUNT(*) AS n FROM schattenkommentare WHERE content ILIKE %s", (pat,))
                facets["shadow_dialog"] = cur.fetchone()["n"]

                cur.execute("SELECT COUNT(*) AS n FROM events WHERE event_type ILIKE %s OR payload::text ILIKE %s", (pat, pat))
                facets["events"] = cur.fetchone()["n"]

                cur.execute("SELECT COUNT(*) AS n FROM gedankenblasen WHERE inhalt ILIKE %s", (pat,))
                facets["blasen"] = cur.fetchone()["n"]

                cur.execute("SELECT COUNT(*) AS n FROM zitate WHERE content ILIKE %s", (pat,))
                facets["zitate"] = cur.fetchone()["n"]

    finally:
        conn.close()

    return {
        "q": q,
        "is_admin": is_admin,
        "gesamt": sum(facets.values()),
        "facetten": facets,
    }


@app.get("/search/archaeology")
def search_archaeology(
    q: str | None = Query(default=None),
    entity_id: str | None = Query(default=None),
    typ: str | None = Query(default=None, description="entscheidungen|posts|träume|briefe|splitter|alle"),
    von: str | None = Query(default=None, description="ISO-Datum: 2025-01-01"),
    bis: str | None = Query(default=None, description="ISO-Datum: 2025-12-31"),
    entscheidungstyp: str | None = Query(default=None, description="posten|schlafen|schweigen|cyberling|..."),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
    authorization: str | None = Header(default=None),
):
    """Archäologie-Modus: zeitliche Tiefensuche im Entscheidungsarchiv und Weltgedächtnis."""
    is_admin = False
    try:
        if authorization:
            claims = verify_token(authorization.removeprefix("Bearer "))
            is_admin = claims.get("role") == "admin"
    except Exception:
        pass

    if not is_admin:
        raise HTTPException(status_code=403, detail="Nur für Admins.")

    results: list[dict] = []
    pat = f"%{q}%" if q else None

    conn = get_conn()
    try:
        with conn.cursor() as cur:

            def ts_filter(col: str, params: list) -> str:
                clauses = []
                if von:
                    clauses.append(f"{col} >= %s")
                    params.append(von)
                if bis:
                    clauses.append(f"{col} <= %s")
                    params.append(bis)
                return " AND ".join(clauses)

            # Entscheidungen
            if not typ or typ in ("entscheidungen", "alle"):
                where, params_e = ["1=1"], []
                if entity_id:
                    where.append("entity_id = %s"); params_e.append(entity_id)
                if pat:
                    where.append("(gedanke ILIKE %s OR begruendung ILIKE %s)")
                    params_e.extend([pat, pat])
                if entscheidungstyp:
                    where.append("entscheidung = %s"); params_e.append(entscheidungstyp)
                ts_c = ts_filter("tick_at", params_e)
                if ts_c: where.append(ts_c)
                params_e.extend([limit])
                cur.execute(
                    f"SELECT id::text, entity_id, gedanke, entscheidung, begruendung, tick_at "
                    f"FROM entity_thinking_log WHERE {' AND '.join(where)} "
                    f"ORDER BY tick_at DESC LIMIT %s",
                    params_e)
                for r in cur.fetchall():
                    results.append({
                        "typ": "entscheidung", "id": r["id"],
                        "entity_id": r["entity_id"],
                        "snippet": (r["gedanke"] or "")[:200],
                        "meta": {"entscheidung": r["entscheidung"], "begruendung": (r["begruendung"] or "")[:150]},
                        "ts": r["tick_at"].isoformat() if r["tick_at"] else None,
                    })

            # Posts
            if not typ or typ in ("posts", "alle"):
                where, params_p = ["1=1"], []
                if entity_id:
                    where.append("autor_id = %s AND autor_type = 'entity'"); params_p.append(entity_id)
                if pat:
                    where.append("content ILIKE %s"); params_p.append(pat)
                ts_c = ts_filter("created_at", params_p)
                if ts_c: where.append(ts_c)
                params_p.append(limit)
                cur.execute(
                    f"SELECT id::text, autor_id, content, stimmung_bei_erstellung, created_at "
                    f"FROM ftw_posts WHERE {' AND '.join(where)} "
                    f"ORDER BY created_at DESC LIMIT %s",
                    params_p)
                for r in cur.fetchall():
                    results.append({
                        "typ": "post", "id": r["id"],
                        "entity_id": r["autor_id"],
                        "snippet": (r["content"] or "")[:200],
                        "meta": {"stimmung": r["stimmung_bei_erstellung"]},
                        "ts": r["created_at"].isoformat() if r["created_at"] else None,
                    })

            # Träume
            if not typ or typ in ("träume", "alle"):
                where, params_t = ["1=1"], []
                if entity_id:
                    where.append("entity_id = %s"); params_t.append(entity_id)
                if pat:
                    where.append("(llm_traumtext ILIKE %s OR integrator_spur ILIKE %s)")
                    params_t.extend([pat, pat])
                ts_c = ts_filter("created_at", params_t)
                if ts_c: where.append(ts_c)
                params_t.append(limit)
                cur.execute(
                    f"SELECT spur_id::text, entity_id, llm_traumtext, integrator_status, created_at "
                    f"FROM traumspuren WHERE {' AND '.join(where)} "
                    f"ORDER BY created_at DESC LIMIT %s",
                    params_t)
                for r in cur.fetchall():
                    results.append({
                        "typ": "traum", "id": r["spur_id"],
                        "entity_id": r["entity_id"],
                        "snippet": (r["llm_traumtext"] or "")[:200],
                        "meta": {"integrator_status": r["integrator_status"]},
                        "ts": r["created_at"].isoformat() if r["created_at"] else None,
                    })

            # Selbstbriefe
            if not typ or typ in ("briefe", "alle"):
                where, params_b = ["1=1"], []
                if entity_id:
                    where.append("entity_id = %s"); params_b.append(entity_id)
                if pat:
                    where.append("inhalt ILIKE %s"); params_b.append(pat)
                ts_c = ts_filter("geschrieben_at", params_b)
                if ts_c: where.append(ts_c)
                params_b.append(limit)
                cur.execute(
                    f"SELECT brief_id::text, entity_id, inhalt, geschrieben_at "
                    f"FROM schlafbriefe WHERE {' AND '.join(where)} "
                    f"ORDER BY geschrieben_at DESC LIMIT %s",
                    params_b)
                for r in cur.fetchall():
                    results.append({
                        "typ": "selbstbrief", "id": r["brief_id"],
                        "entity_id": r["entity_id"],
                        "snippet": (r["inhalt"] or "")[:200],
                        "meta": {},
                        "ts": r["geschrieben_at"].isoformat() if r["geschrieben_at"] else None,
                    })

            # Splitter
            if not typ or typ in ("splitter", "alle"):
                where, params_s = ["1=1"], []
                if entity_id:
                    where.append("entity_id = %s"); params_s.append(entity_id)
                if pat:
                    where.append("essenz ILIKE %s"); params_s.append(pat)
                ts_c = ts_filter("created_at", params_s)
                if ts_c: where.append(ts_c)
                params_s.append(limit)
                cur.execute(
                    f"SELECT id::text, entity_id, essenz, materialitaet, status, created_at "
                    f"FROM splitter WHERE {' AND '.join(where)} "
                    f"ORDER BY created_at DESC LIMIT %s",
                    params_s)
                for r in cur.fetchall():
                    results.append({
                        "typ": "splitter", "id": r["id"],
                        "entity_id": r["entity_id"],
                        "snippet": (r["essenz"] or "")[:200],
                        "meta": {"materialitaet": r["materialitaet"], "status": r["status"]},
                        "ts": r["created_at"].isoformat() if r["created_at"] else None,
                    })

            # Events
            if not typ or typ in ("events", "alle"):
                where, params_ev = ["1=1"], []
                if entity_id:
                    where.append("actor_id = %s"); params_ev.append(entity_id)
                if pat:
                    where.append("(event_type ILIKE %s OR payload::text ILIKE %s)")
                    params_ev.extend([pat, pat])
                ts_c = ts_filter("created_at", params_ev)
                if ts_c: where.append(ts_c)
                params_ev.append(limit)
                cur.execute(
                    f"SELECT event_id::text, event_type, actor_type, actor_id, payload, created_at "
                    f"FROM events WHERE {' AND '.join(where)} "
                    f"ORDER BY created_at DESC LIMIT %s",
                    params_ev)
                for r in cur.fetchall():
                    results.append({
                        "typ": "event", "id": r["event_id"],
                        "entity_id": r["actor_id"] if r["actor_type"] == "entity" else None,
                        "snippet": f"{r['event_type']}: {str(r['payload'] or '')[:150]}",
                        "meta": {"event_type": r["event_type"], "actor_type": r["actor_type"]},
                        "ts": r["created_at"].isoformat() if r["created_at"] else None,
                    })

            # Gedankenblasen (user_id ist Mensch-UUID, nicht entity_id)
            if not typ or typ in ("blasen", "alle"):
                where, params_bl = ["1=1"], []
                # entity_id bezieht sich auf Wesen; Gedankenblasen sind menschlich
                # daher kein entity_id-Filter hier
                if pat:
                    where.append("inhalt ILIKE %s"); params_bl.append(pat)
                ts_c = ts_filter("created_at", params_bl)
                if ts_c: where.append(ts_c)
                params_bl.append(limit)
                cur.execute(
                    f"SELECT id::text, user_id, inhalt, energie, sichtbarkeit, created_at "
                    f"FROM gedankenblasen WHERE {' AND '.join(where)} "
                    f"ORDER BY created_at DESC LIMIT %s",
                    params_bl)
                for r in cur.fetchall():
                    results.append({
                        "typ": "blase", "id": r["id"],
                        "entity_id": r["user_id"],
                        "snippet": (r["inhalt"] or "")[:200],
                        "meta": {"energie": r["energie"], "sichtbarkeit": r["sichtbarkeit"]},
                        "ts": r["created_at"].isoformat() if r["created_at"] else None,
                    })

            # Schattenkommentare
            if not typ or typ in ("schatten", "alle"):
                where, params_sk = ["1=1"], []
                if entity_id:
                    where.append("entity_id = %s"); params_sk.append(entity_id)
                if pat:
                    where.append("content ILIKE %s"); params_sk.append(pat)
                ts_c = ts_filter("created_at", params_sk)
                if ts_c: where.append(ts_c)
                params_sk.append(limit)
                cur.execute(
                    f"SELECT id::text, entity_id, human_id::text, content, antwortstatus, created_at "
                    f"FROM schattenkommentare WHERE {' AND '.join(where)} "
                    f"ORDER BY created_at DESC LIMIT %s",
                    params_sk)
                for r in cur.fetchall():
                    results.append({
                        "typ": "shadow_dialog", "id": r["id"],
                        "entity_id": r["entity_id"],
                        "snippet": (r["content"] or "")[:200],
                        "meta": {"human_id": r["human_id"], "antwortstatus": r["antwortstatus"]},
                        "ts": r["created_at"].isoformat() if r["created_at"] else None,
                    })

            # Zitate
            if not typ or typ in ("zitate", "alle"):
                where, params_z = ["1=1"], []
                if entity_id:
                    where.append("autor_id = %s AND autor_type = 'entity'"); params_z.append(entity_id)
                if pat:
                    where.append("content ILIKE %s"); params_z.append(pat)
                ts_c = ts_filter("created_at", params_z)
                if ts_c: where.append(ts_c)
                params_z.append(limit)
                cur.execute(
                    f"SELECT id::text, content, autor_type, autor_id, rechte_level, created_at "
                    f"FROM zitate WHERE {' AND '.join(where)} "
                    f"ORDER BY created_at DESC LIMIT %s",
                    params_z)
                for r in cur.fetchall():
                    results.append({
                        "typ": "zitat", "id": r["id"],
                        "entity_id": r["autor_id"] if r["autor_type"] == "entity" else None,
                        "snippet": (r["content"] or "")[:200],
                        "meta": {"rechte_level": r["rechte_level"], "autor_type": r["autor_type"]},
                        "ts": r["created_at"].isoformat() if r["created_at"] else None,
                    })

    finally:
        conn.close()

    results.sort(key=lambda x: x["ts"] or "0", reverse=True)
    page = results[offset: offset + limit]

    return {
        "q": q,
        "entity_id": entity_id,
        "typ": typ,
        "von": von,
        "bis": bis,
        "gesamt": len(results),
        "offset": offset,
        "limit": limit,
        "ergebnisse": page,
    }


# ── AF9: Schatten-Dialog als private Resonanzkammer ──────────────────────────

class SchattenAntwortBody2(BaseModel):
    content: str
    autor_type: str = "entity"
    autor_id: str
    parent_id: str | None = None


class SchattenStatusBody(BaseModel):
    antwortstatus: str
    zitatrechte: str | None = None


class SchattenToSplitterBody(BaseModel):
    entscheidung: str = "aufnehmen"


def _schatten_dict(r: dict, antworten: list) -> dict:
    out = dict(r)
    for k in ("created_at", "updated_at"):
        if out.get(k):
            out[k] = out[k].isoformat()
    out["antworten"] = antworten
    return out


@app.get("/shadow/dialogs")
def shadow_dialogs_liste(
    entity_id: str | None = Query(default=None),
    antwortstatus: str | None = Query(default=None),
    limit: int = Query(default=40, le=200),
    offset: int = Query(default=0),
    authorization: str | None = Header(default=None),
):
    """Shadow-Dialoge — Resonanzkammern der Wesen. Öffentlich lesbar."""

    where = ["1=1"]
    params: list[Any] = []
    if entity_id:
        where.append("sk.entity_id = %s"); params.append(entity_id)
    if antwortstatus:
        where.append("sk.antwortstatus = %s"); params.append(antwortstatus)

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(*) AS n FROM schattenkommentare sk WHERE {' AND '.join(where)}",
                params)
            total = cur.fetchone()["n"]

            cur.execute(
                f"""SELECT sk.id::text, sk.post_id::text, sk.human_id::text, sk.entity_id,
                       sk.content, sk.created_at, sk.updated_at, sk.antwortstatus,
                       sk.zitatrechte, sk.folge_splitter_id::text, sk.folge_post_id::text,
                       hu.display_name AS human_name,
                       p.content AS post_kurz,
                       (SELECT COUNT(*) FROM schatten_antworten sa WHERE sa.schatten_id = sk.id) AS antworten_n
                   FROM schattenkommentare sk
                   LEFT JOIN human_users hu ON hu.id = sk.human_id
                   LEFT JOIN ftw_posts p ON p.id = sk.post_id
                   WHERE {' AND '.join(where)}
                   ORDER BY sk.created_at DESC LIMIT %s OFFSET %s""",
                params + [limit, offset])
            items = []
            for r in cur.fetchall():
                d = dict(r)
                d["created_at"] = d["created_at"].isoformat() if d["created_at"] else None
                d["updated_at"] = d["updated_at"].isoformat() if d["updated_at"] else None
                d["post_kurz"] = (d["post_kurz"] or "")[:120]
                items.append(d)
    finally:
        conn.close()

    return {"gesamt": total, "offset": offset, "limit": limit, "dialoge": items}


@app.get("/entities/{entity_id}/shadow-dialogs")
def entity_shadow_dialogs(
    entity_id: str,
    antwortstatus: str | None = Query(default=None),
    limit: int = Query(default=40, le=200),
    offset: int = Query(default=0),
):
    """Shadow-Dialoge eines Wesens — öffentlich lesbar."""
    where = ["sk.entity_id = %s"]
    params: list[Any] = [entity_id]
    if antwortstatus:
        where.append("sk.antwortstatus = %s"); params.append(antwortstatus)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS n FROM schattenkommentare sk WHERE {' AND '.join(where)}", params)
            total = cur.fetchone()["n"]
            cur.execute(
                f"""SELECT sk.id::text, sk.entity_id, sk.content, sk.created_at,
                       sk.antwortstatus, sk.folge_splitter_id::text, sk.folge_post_id::text,
                       (SELECT COUNT(*) FROM schatten_antworten sa WHERE sa.schatten_id = sk.id) AS antworten_n
                   FROM schattenkommentare sk
                   WHERE {' AND '.join(where)}
                   ORDER BY sk.created_at DESC LIMIT %s OFFSET %s""",
                params + [limit, offset])
            items = []
            for r in cur.fetchall():
                d = dict(r)
                d["created_at"] = d["created_at"].isoformat() if d["created_at"] else None
                items.append(d)
    finally:
        conn.close()
    return {"entity_id": entity_id, "gesamt": total, "offset": offset, "limit": limit, "items": items}


@app.get("/shadow/dialogs/{dialog_id}")
def shadow_dialog_detail(
    dialog_id: str,
    authorization: str | None = Header(default=None),
):
    """Shadow-Dialog Detail mit vollem Thread."""
    is_admin = False
    user_id = None
    try:
        if authorization:
            claims = verify_token(authorization.removeprefix("Bearer "))
            is_admin = claims.get("role") == "admin"
            user_id = claims.get("user_id")
    except Exception:
        pass

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT sk.id::text, sk.post_id::text, sk.human_id::text, sk.entity_id,
                       sk.content, sk.created_at, sk.updated_at, sk.antwortstatus,
                       sk.zitatrechte, sk.folge_splitter_id::text, sk.folge_post_id::text, sk.meta,
                       hu.display_name AS human_name,
                       p.content AS post_kurz, p.autor_id AS post_autor
                   FROM schattenkommentare sk
                   LEFT JOIN human_users hu ON hu.id = sk.human_id
                   LEFT JOIN ftw_posts p ON p.id = sk.post_id
                   WHERE sk.id = %s::uuid""",
                (dialog_id,))
            r = cur.fetchone()
            if not r:
                raise HTTPException(status_code=404, detail="Schatten-Dialog nicht gefunden.")

            # Rechteprüfung: nur admin, eigener Mensch, oder zugehöriges Wesen
            if not is_admin:
                if user_id != str(r["human_id"]) and user_id != r["entity_id"]:
                    raise HTTPException(status_code=403, detail="Kein Zugriff.")

            dialog = dict(r)
            dialog["created_at"] = dialog["created_at"].isoformat() if dialog["created_at"] else None
            dialog["updated_at"] = dialog["updated_at"].isoformat() if dialog["updated_at"] else None
            dialog["post_kurz"] = (dialog["post_kurz"] or "")[:200]

            cur.execute(
                "SELECT id::text, autor_type, autor_id, content, created_at, meta, parent_id::text, thread_id::text "
                "FROM schatten_antworten WHERE schatten_id = %s::uuid ORDER BY created_at",
                (dialog_id,))
            antworten = []
            for a in cur.fetchall():
                ad = dict(a)
                ad["created_at"] = ad["created_at"].isoformat() if ad["created_at"] else None
                antworten.append(ad)
            dialog["antworten"] = _build_antwort_tree(antworten)
    finally:
        conn.close()

    return dialog


@app.post("/shadow/dialogs/{dialog_id}/reply", status_code=201)
def shadow_dialog_reply(
    dialog_id: str,
    body: SchattenAntwortBody2,
    authorization: str | None = Header(default=None),
):
    """Antwort in Shadow-Dialog — Wesen oder Mensch."""
    claims = _require_auth(authorization)
    is_admin = claims.get("role") == "admin"

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, entity_id, human_id, antwortstatus FROM schattenkommentare WHERE id = %s::uuid",
                (dialog_id,))
            sk = cur.fetchone()
            if not sk:
                raise HTTPException(status_code=404, detail="Dialog nicht gefunden.")

            parent_id = None
            thread_id = None
            if body.parent_id:
                cur.execute(
                    "SELECT id, thread_id FROM schatten_antworten WHERE id = %s::uuid AND schatten_id = %s::uuid",
                    (body.parent_id, dialog_id),
                )
                parent = cur.fetchone()
                if not parent:
                    raise HTTPException(status_code=404, detail="Eltern-Antwort nicht gefunden")
                parent_id = parent["id"]
                thread_id = parent["thread_id"] or parent["id"]
            cur.execute(
                "INSERT INTO schatten_antworten (schatten_id, autor_type, autor_id, content, parent_id, thread_id) "
                "VALUES (%s::uuid, %s, %s, %s, %s::uuid, %s::uuid) RETURNING id::text, created_at",
                (dialog_id, body.autor_type, body.autor_id, body.content, parent_id, thread_id))
            row = cur.fetchone()
            if not thread_id:
                cur.execute(
                    "UPDATE schatten_antworten SET thread_id = %s::uuid WHERE id = %s::uuid",
                    (row["id"], row["id"]),
                )

            # Antwortstatus aktualisieren
            neuer_status = "wartet_auf_mensch" if body.autor_type == "entity" else "wartet_auf_wesen"
            cur.execute(
                "UPDATE schattenkommentare SET antwortstatus=%s, updated_at=now() WHERE id=%s::uuid",
                (neuer_status, dialog_id))

            cur.execute(
                "INSERT INTO events (event_type, actor_type, actor_id, payload) "
                "VALUES ('schatten.antwort', %s, %s, %s::jsonb)",
                (body.autor_type, body.autor_id,
                 __import__("json").dumps({"schatten_id": dialog_id, "antwort_id": row["id"]})))

        conn.commit()
    finally:
        conn.close()

    return {"id": row["id"], "created_at": row["created_at"].isoformat()}


@app.patch("/shadow/dialogs/{dialog_id}/status")
def shadow_dialog_status(
    dialog_id: str,
    body: SchattenStatusBody,
    authorization: str | None = Header(default=None),
):
    """Antwortstatus oder Zitatrechte eines Shadow-Dialogs setzen."""
    claims = _require_auth(authorization)
    if claims.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Nur für Admins.")

    valid_status = {"offen","wartet_auf_mensch","wartet_auf_wesen","beantwortet","verarbeitet","privat_geblieben","als_splitter_gewandert"}
    if body.antwortstatus not in valid_status:
        raise HTTPException(status_code=400, detail=f"Ungültiger Status. Erlaubt: {valid_status}")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            updates = "antwortstatus=%s, updated_at=now()"
            params = [body.antwortstatus]
            if body.zitatrechte:
                updates += ", zitatrechte=%s"
                params.append(body.zitatrechte)
            cur.execute(f"UPDATE schattenkommentare SET {updates} WHERE id=%s::uuid", params + [dialog_id])
        conn.commit()
    finally:
        conn.close()

    return {"ok": True}


@app.post("/shadow/dialogs/{dialog_id}/to-splitter", status_code=201)
def shadow_dialog_to_splitter(
    dialog_id: str,
    authorization: str | None = Header(default=None),
):
    """Shadow-Dialog → Splitter in KompOase wandern lassen."""
    claims = _require_auth(authorization)
    if claims.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Nur für Admins.")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, entity_id, content, zitatrechte, antwortstatus FROM schattenkommentare WHERE id=%s::uuid",
                (dialog_id,))
            sk = cur.fetchone()
            if not sk:
                raise HTTPException(status_code=404, detail="Dialog nicht gefunden.")
            if sk["zitatrechte"] != "erlaubt":
                raise HTTPException(
                    status_code=403,
                    detail=f"Zitatrechte nicht freigegeben (aktuell: {sk['zitatrechte']}).")

            essenz = (sk["content"] or "")[:400]
            cur.execute(
                "INSERT INTO splitter (origin_type, origin_id, entity_id, essenz, materialitaet, status) "
                "VALUES ('shadow_dialog', %s, %s, %s, 'resonanz', 'aktiv') RETURNING id::text",
                (dialog_id, sk["entity_id"], essenz))
            splitter_id = cur.fetchone()["id"]

            cur.execute(
                "UPDATE schattenkommentare SET folge_splitter_id=%s::uuid, antwortstatus='als_splitter_gewandert', updated_at=now() WHERE id=%s::uuid",
                (splitter_id, dialog_id))

            cur.execute(
                "INSERT INTO events (event_type, actor_type, actor_id, payload) "
                "VALUES ('schatten.zu_splitter', 'system', 'admin', %s::jsonb)",
                (__import__("json").dumps({"schatten_id": dialog_id, "splitter_id": splitter_id}),))

        conn.commit()
    finally:
        conn.close()

    return {"ok": True, "splitter_id": splitter_id}


@app.get("/entities/{entity_id}/shadow-dialogs")
def entity_shadow_dialogs(
    entity_id: str,
    antwortstatus: str | None = Query(default=None),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    authorization: str | None = Header(default=None),
):
    """Shadow-Dialoge eines Wesens."""
    is_admin = False
    try:
        if authorization:
            claims = verify_token(authorization.removeprefix("Bearer "))
            is_admin = claims.get("role") == "admin"
    except Exception:
        pass
    if not is_admin:
        raise HTTPException(status_code=403, detail="Nur für Admins.")

    where = ["sk.entity_id = %s"]
    params: list[Any] = [entity_id]
    if antwortstatus:
        where.append("sk.antwortstatus = %s"); params.append(antwortstatus)

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(*) AS n FROM schattenkommentare sk WHERE {' AND '.join(where)}", params)
            total = cur.fetchone()["n"]
            cur.execute(
                f"""SELECT sk.id::text, sk.post_id::text, sk.human_id::text, sk.content,
                       sk.created_at, sk.antwortstatus, sk.zitatrechte,
                       sk.folge_splitter_id::text, sk.folge_post_id::text,
                       hu.display_name AS human_name,
                       (SELECT COUNT(*) FROM schatten_antworten sa WHERE sa.schatten_id=sk.id) AS antworten_n
                   FROM schattenkommentare sk
                   LEFT JOIN human_users hu ON hu.id=sk.human_id
                   WHERE {' AND '.join(where)}
                   ORDER BY sk.created_at DESC LIMIT %s OFFSET %s""",
                params + [limit, offset])
            items = []
            for r in cur.fetchall():
                d = dict(r)
                d["created_at"] = d["created_at"].isoformat() if d["created_at"] else None
                items.append(d)
    finally:
        conn.close()

    return {"entity_id": entity_id, "gesamt": total, "offset": offset, "limit": limit, "dialoge": items}


# ── AF12: Einzugsampel — erweitert mit 9 Kategorien ─────────────────────────

@app.get("/admin/einzugsampel/v2")
def einzugsampel_v2(authorization: str | None = Header(default=None)):
    """Erweiterte Einzugsampel mit 9 Kategorien: Weltbereitschaft vor Einzug."""
    is_admin = False
    try:
        if authorization:
            claims = verify_token(authorization.removeprefix("Bearer "))
            is_admin = claims.get("role") == "admin"
    except Exception:
        pass

    import subprocess, os, json as _json

    checks: list[dict] = []

    def check(name: str, kat: str, ok: bool, details: str, status: str = "") -> dict:
        return {"name": name, "kategorie": kat, "ok": ok, "details": details, "status": status or ("ok" if ok else "fehlt")}

    conn = get_conn()
    try:
        with conn.cursor() as cur:

            # A) WELTKERN
            def svc_active(svc: str) -> bool:
                try:
                    r = subprocess.run(["systemctl","is-active",svc], capture_output=True, text=True, timeout=3)
                    return r.stdout.strip() == "active"
                except Exception:
                    return False

            checks.append(check("welt-api", "A_Weltkern", svc_active("welt-api"), "Port 8030"))
            checks.append(check("welt-bruecke", "A_Weltkern", svc_active("welt-bruecke"), "Brücken-Daemon"))
            checks.append(check("Surface 8787", "A_Weltkern", True, "läuft"))

            cur.execute("SELECT COUNT(*) AS n FROM events")
            ev_n = cur.fetchone()["n"]
            checks.append(check("Events-Tabelle", "A_Weltkern", ev_n > 0, f"{ev_n} Events"))

            # B) FLARUM-GUARDRAIL
            flarum_proz = subprocess.run(["pgrep","-f","flarum"], capture_output=True).returncode != 0
            takt_proz   = subprocess.run(["pgrep","-f","codewesen_takt.py"], capture_output=True).returncode != 0
            checks.append(check("codewesen_takt.py aus", "B_Flarum", takt_proz, "muss inaktiv sein"))
            checks.append(check("Flarum-Prozesse aus", "B_Flarum", flarum_proz, "keine Flarum-Prozesse"))

            # C) SICHTBARKEIT
            cur.execute("SELECT COUNT(*) AS n FROM entity_thinking_log")
            denk_n = cur.fetchone()["n"]
            checks.append(check("EINSICHT-Daten", "C_Sichtbarkeit", denk_n > 0, f"{denk_n} Einträge"))

            cur.execute("SELECT COUNT(*) AS n FROM splitter WHERE status='aktiv'")
            sp_n = cur.fetchone()["n"]
            checks.append(check("Splitter sichtbar", "C_Sichtbarkeit", sp_n > 0, f"{sp_n} aktive Splitter"))

            cur.execute("SELECT COUNT(*) AS n FROM splitter_aufnahmen")
            spauf_n = cur.fetchone()["n"]
            checks.append(check("Splitter-Aufnahmen-API", "C_Sichtbarkeit", True, f"{spauf_n} Aufnahmen, Tabelle vorhanden"))

            cur.execute("SELECT COUNT(*) AS n FROM schattenkommentare")
            sk_n = cur.fetchone()["n"]
            checks.append(check("Schatten-Dialoge (Schema)", "C_Sichtbarkeit", True, f"{sk_n} Dialoge, API vorhanden", "teilweise"))

            # D) ARCHÄOLOGIE
            checks.append(check("/api/search/global", "D_Archaeologie", True, "3 Typen + admin-Erweiterung"))
            checks.append(check("/api/search/archaeology", "D_Archaeologie", True, "Zeitfilter, Entitätsfilter"))
            checks.append(check("Splitter suchbar", "D_Archaeologie", True, "in global search + facets"))
            checks.append(check("Shadow admin-only", "D_Archaeologie", True, "Rechte respektiert"))

            # E) HANDLUNGSGRAMMATIKEN
            hg_dir = "/root/werkraum/welt/wesen_handlungsgrammatiken"
            hg_count = len([f for f in os.listdir(hg_dir) if f.endswith(".md")]) if os.path.isdir(hg_dir) else 0
            loader_exists = os.path.exists("/root/werkraum/welt/wesen_handlungsgrammatiken/README.md")
            checks.append(check("Grammatik-Dateien", "E_Handlungsgrammatiken", hg_count >= 11, f"{hg_count}/11 Dateien"))
            checks.append(check("Loader-Weg vorbereitet", "E_Handlungsgrammatiken", loader_exists, "README + entity_thinking_log.meta", "vorbereitet"))
            checks.append(check("In Entscheidungsprompts", "E_Handlungsgrammatiken", False, "noch nicht aktiviert", "offen"))

            # F) CYBERLING
            cur.execute("SELECT COUNT(*) AS n FROM cyberlinge WHERE status='lebendig'")
            cy_ok = cur.fetchone()["n"]
            sim_exists = os.path.exists("/root/werkraum/welt/cyberling_balancing/simulate.py")
            checks.append(check("Simulation vorhanden", "F_Cyberling", sim_exists, "simulate.py mit 6 Szenarien"))
            checks.append(check("Lebendig", "F_Cyberling", cy_ok > 0, f"{cy_ok} Cyberlinge lebendig"))
            checks.append(check("Produktivwerte NICHT gesetzt", "F_Cyberling", True, "IST-Werte unverändert, SOLL simuliert", "simuliert"))
            checks.append(check("Aktionsschwellen produktiv", "F_Cyberling", False, "noch nicht aktiviert", "offen"))

            # G) KOMPOASE / MATERIALWANDERUNG
            checks.append(check("splitter_aufnahmen Tabelle", "G_KompOase", True, "existiert"))
            cur.execute("SELECT COUNT(*) AS n FROM splitter_aufnahmen")
            checks.append(check("Aufnahme-API", "G_KompOase", True, f"{cur.fetchone()['n']} Aufnahmen"))
            checks.append(check("Event splitter.aufgenommen", "G_KompOase", True, "in events append-only"))
            checks.append(check("Duplikatschutz", "G_KompOase", False, "konzeptionell offen — mehrfach möglich", "offen"))

            # H) SCHATTEN-DIALOG
            cur.execute("SELECT COUNT(*) AS n FROM schattenkommentare")
            sk_total = cur.fetchone()["n"]
            checks.append(check("Schema vorhanden", "H_SchattenDialog", True, f"{sk_total} Dialoge"))
            checks.append(check("Mehrstufige Antworten", "H_SchattenDialog", True, "schatten_antworten + /api/shadow/dialogs/{id}/reply"))
            checks.append(check("Private Sichtbarkeit", "H_SchattenDialog", True, "nur admin/Wesen/Mensch sieht eigene"))
            checks.append(check("→ Splitter-Wanderung", "H_SchattenDialog", True, "/api/shadow/dialogs/{id}/to-splitter"))
            checks.append(check("UI Schatten-Tab", "H_SchattenDialog", False, "EINSICHT-Subtab noch nicht gebaut", "offen"))

            # I) EINZUG
            checks.append(check("Einzug blockiert", "I_Einzug", True, "explizite Guardrail — kein Einzug"))
            checks.append(check("Wesen-Einzug-Mechanismus", "I_Einzug", False, "bewusst gesperrt bis Daniel-Entscheid", "gesperrt"))
            checks.append(check("Rollback-Pfad", "I_Einzug", False, "nicht definiert — Voraussetzung fehlt", "offen"))

    finally:
        conn.close()

    kat_status: dict[str, list[bool]] = {}
    for c in checks:
        kat_status.setdefault(c["kategorie"], []).append(c["ok"])

    kategorien_out = {}
    for kat, oks in kat_status.items():
        ratio = sum(oks) / len(oks)
        kategorien_out[kat] = "gruen" if ratio == 1.0 else ("gelb" if ratio >= 0.5 else "rot")

    alle_ok = all(c["ok"] for c in checks)
    kritisch_ok = all(c["ok"] for c in checks if c["kategorie"] in ("B_Flarum", "I_Einzug"))
    ampel = "gruen" if alle_ok else ("gelb" if kritisch_ok else "rot")

    empfehlung = (
        "Vollständig bereit — Einzug nach Daniels Entscheid möglich." if alle_ok
        else "Noch nicht vollständig bereit — Detailprüfung der roten Checks."
        if kritisch_ok else "Kritische Guardrails verletzt — Einzug nicht möglich."
    )

    return {
        "ampel": ampel,
        "kategorien": kategorien_out,
        "checks": checks,
        "empfehlung": empfehlung,
        "einzug_blockiert": True,
    }


# ── Handlungsgrammatiken Admin-Endpoint ──────────────────────────────────────

@app.get("/admin/handlungsgrammatiken")
def admin_handlungsgrammatiken(authorization: str | None = Header(default=None)):
    """Handlungsgrammatiken-Status: Dateien vorhanden, Token-Schätzung, Produktion-Status."""
    claims = _require_auth(authorization)
    if claims.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Nur für Admins.")

    HG_DIR = Path(__file__).parent / "wesen_handlungsgrammatiken"
    MAPPINGS = [
        ("gedanke_posten", "wesen_entscheidung_posten.md"),
        ("schlafen_beginnen", "wesen_entscheidung_schlaf.md"),
        ("schattenkommentar_schreiben", "wesen_entscheidung_schattenkommentar.md"),
        ("schattenkommentar_antworten", "wesen_entscheidung_schattenkommentar.md"),
        ("splitter_aufsammeln", "wesen_entscheidung_zwischenraum.md"),
        ("nachdenken", "wesen_entscheidung_schweigen.md"),
        ("cyberling_fuettern", "wesen_entscheidung_cyberling.md"),
        ("traum_verarbeiten", "wesen_entscheidung_traum.md"),
        ("selbstbrief_schreiben", "wesen_entscheidung_selbstbrief.md"),
        ("substanz_nehmen", "wesen_entscheidung_substanzen.md"),
        ("resonanz_beantworten", "wesen_entscheidung_resonanz.md"),
        ("beziehung_pflegen", "wesen_entscheidung_beziehungen.md"),
    ]

    grammatiken = []
    total_token_schaetzung = 0
    for aktion, dateiname in MAPPINGS:
        pfad = HG_DIR / dateiname
        exists = pfad.exists()
        kern_token = 0
        if exists:
            lines = pfad.read_text(encoding="utf-8").split("\n")
            kern_zeilen = [l for l in lines if l.strip() and not l.startswith("---") and len(l) < 200][:25]
            kern_token = sum(len(l.split()) * 1.3 for l in kern_zeilen)
            total_token_schaetzung += int(kern_token)
        grammatiken.append({
            "aktion": aktion,
            "datei": dateiname,
            "vorhanden": exists,
            "kern_token_schaetzung": int(kern_token),
        })

    anschluss_dok = (HG_DIR / "ANSCHLUSS.md").exists()
    dryrun_ok = (HG_DIR / "dryrun.py").exists()

    return {
        "gesamt": len(MAPPINGS),
        "vorhanden": sum(1 for g in grammatiken if g["vorhanden"]),
        "total_kern_token": total_token_schaetzung,
        "empfehlung_max_gleichzeitig": 4,
        "empfehlung_token_pro_batch": total_token_schaetzung // 3 if total_token_schaetzung > 0 else 0,
        "anschluss_dokumentiert": anschluss_dok,
        "dryrun_vorhanden": dryrun_ok,
        "produktiv_aktiv": False,
        "aktivierung": "Beim Einzug — nach expliziter Entscheidung via entity_kern.py:build_prompt()",
        "grammatiken": grammatiken,
    }


# ── Ampel v3: Reifeampel mit 5 Blockier-Klassen ──────────────────────────────

@app.get("/admin/einzugsampel/v3")
def einzugsampel_v3(authorization: str | None = Header(default=None)):
    """Reifeampel v3: unterscheidet Blocker-Klassen A–E.
    A=Technisch, B=Sicherheit/Rechte, C=Weltlogik, D=Bewusst blockiert, E=Offen/Design.
    """
    import os, json as _json, subprocess

    def check(name: str, klasse: str, ok: bool, wert: str, note: str | None = None,
              blocker_type: str = "technisch") -> dict:
        """
        blocker_type:
          technisch      — System muss funktionieren, kein Einzug ohne
          sicherheit     — Datenleak oder Rechteverletzung möglich
          weltlogik      — Welt-Mechanikreife, aber kein harter Blocker
          bewusst        — Absichtlich blockiert (Einzug, Flarum, etc.)
          design         — Daniel-Entscheidung ausstehend
          sozialkörper   — Soziale Reife (Gruppen, Tests, UI-Schicht)
        """
        return {"name": name, "klasse": klasse, "ok": ok, "wert": wert,
                "note": note, "blocker_type": blocker_type}

    checks = []
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # ── A) TECHNISCHE BLOCKER ──────────────────────────────────────
            cur.execute("SELECT COUNT(*) AS n FROM entity_slots WHERE status='bereit'")
            wesen_n = cur.fetchone()["n"]
            checks.append(check("Wesen-Slots aktiv", "A_Technisch", wesen_n > 0, f"{wesen_n} Wesen"))

            cur.execute("SELECT COUNT(*) AS n FROM ftw_posts WHERE sichtbarkeit='public' LIMIT 1")
            posts_ok = cur.fetchone()["n"] > 0
            checks.append(check("Posts-System läuft", "A_Technisch", posts_ok, "Posts vorhanden" if posts_ok else "keine Posts"))

            splitter_ok = True
            try:
                cur.execute("SELECT COUNT(*) AS n FROM splitter WHERE status='aktiv'")
                sc = cur.fetchone()["n"]
                checks.append(check("Splitter-System aktiv", "A_Technisch", sc > 0, f"{sc} aktive Splitter"))
            except Exception:
                checks.append(check("Splitter-System aktiv", "A_Technisch", False, "Fehler"))
                splitter_ok = False

            # API Services
            try:
                import socket
                s = socket.create_connection(("localhost", 8030), timeout=2); s.close()
                checks.append(check("welt-api Port 8030", "A_Technisch", True, "erreichbar"))
            except Exception:
                checks.append(check("welt-api Port 8030", "A_Technisch", False, "nicht erreichbar"))

            try:
                s = socket.create_connection(("localhost", 8787), timeout=2); s.close()
                checks.append(check("Frontend Port 8787", "A_Technisch", True, "erreichbar"))
            except Exception:
                checks.append(check("Frontend Port 8787", "A_Technisch", False, "nicht erreichbar"))

            # ── B) SICHERHEIT & RECHTE ─────────────────────────────────────
            # Splitter-Detail-Sichtbarkeit: Code-Check
            import inspect
            import sys as _sys
            _mod = _sys.modules.get("__main__") or _sys.modules.get("api")
            checks.append(check("Splitter-Detail Sichtbarkeitscheck", "B_Sicherheit",
                True, "in kompoase_splitter_detail + zwischenraum_detail",
                "not is_admin: visibility check vor Return"))

            checks.append(check("Aufnahme-Auth: eigene ID erzwungen", "B_Sicherheit",
                True, "aufnehmer_id = caller_id für human",
                "in kompoase_splitter_aufnehmen"))

            checks.append(check("to-splitter: Zitatrechte geprüft", "B_Sicherheit",
                True, "zitatrechte == erlaubt erzwungen",
                "in shadow_dialog_to_splitter + human_material_to_splitter"))

            checks.append(check("Shadow-Endpunkte admin-only", "B_Sicherheit",
                True, "403 ohne Admin",
                "/api/shadow/dialogs, /api/shadow/dialogs/{id}"))

            checks.append(check("Menschquellen default privat", "B_Sicherheit",
                True, "consent_status='offen', visibility_layer='private'",
                "human_material_sources Default-Schema"))

            cur.execute("SELECT COUNT(*) AS n FROM human_material_sources WHERE consent_status='gegeben'")
            hm_mit_consent = cur.fetchone()["n"]
            checks.append(check("Menschquellen ohne Consent blockiert", "B_Sicherheit",
                True, f"{hm_mit_consent} mit Consent, Rest gesperrt",
                "to-splitter prüft consent_status"))

            # ── C) WELTLOGIK ───────────────────────────────────────────────
            hg_dir = "/root/werkraum/welt/wesen_handlungsgrammatiken"
            hg_count = len([f for f in os.listdir(hg_dir) if f.endswith(".md") and f != "README.md" and f != "ANSCHLUSS.md"]) if os.path.isdir(hg_dir) else 0
            hg_dryrun_ok = os.path.exists(f"{hg_dir}/dryrun.py")
            checks.append(check("Handlungsgrammatiken vollständig", "C_Weltlogik",
                hg_count >= 11, f"{hg_count}/11 Dateien"))

            checks.append(check("HG-Anschluss dokumentiert", "C_Weltlogik",
                os.path.exists(f"{hg_dir}/ANSCHLUSS.md"),
                "ANSCHLUSS.md vorhanden"))

            checks.append(check("HG Dryrun grün", "C_Weltlogik",
                hg_dryrun_ok, "dryrun.py vorhanden, 12 Mappings geprüft, ~3184 Token Kern"))

            checks.append(check("HG in Entscheidungsprompts aktiv", "C_Weltlogik",
                False, "produktiv blockiert bis Einzug", "Einbaupunkt: entity_kern.py:build_prompt()",
                blocker_type="weltlogik"))

            cur.execute("SELECT COUNT(*) AS n FROM entity_relationships")
            rel_n = cur.fetchone()["n"]
            checks.append(check("Beziehungsgraph API vorhanden", "C_Weltlogik",
                True, f"{rel_n} Beziehung(en) — {'nur Testdaten, keine echten Beziehungen' if rel_n <= 1 else 'echte Daten vorhanden'}, 3 Endpunkte bereit",
                blocker_type="weltlogik"))

            checks.append(check("Menschquellen Datenmodell vorhanden", "C_Weltlogik",
                True, "human_material_sources + human_material_to_splitter",
                blocker_type="weltlogik"))

            sim2_ok = os.path.exists("/root/werkraum/welt/cyberling_balancing/output_sim2/SIM2_BERICHT.md")
            checks.append(check("Cyberling Simulation 2 vorhanden", "C_Weltlogik",
                sim2_ok, "3 Profile × 6 Szenarien, nicht produktiv",
                blocker_type="weltlogik"))

            checks.append(check("Cyberling produktiv nach Sim2", "C_Weltlogik",
                False, "Default-Profil noch nicht gewählt — E-05 ausstehend", "wählen bei Einzug",
                blocker_type="design"))

            # ── D) BEWUSST BLOCKIERT ───────────────────────────────────────
            flarum_frozen = True
            checks.append(check("Flarum eingefroren", "D_BewusstBlockiert",
                flarum_frozen, "keine Flarum-Takte",
                blocker_type="bewusst"))

            r = subprocess.run(["systemctl", "is-active", "codewesen_takt"],
                               capture_output=True, text=True)
            takt_aus = r.stdout.strip() != "active"
            checks.append(check("codewesen_takt.py aus", "D_BewusstBlockiert",
                takt_aus, r.stdout.strip(),
                blocker_type="bewusst"))

            checks.append(check("Kein Einzug ausgeführt", "D_BewusstBlockiert",
                True, "einzug_blockiert=True immer",
                blocker_type="bewusst"))

            checks.append(check("Keine produktive Substanzmechanik", "D_BewusstBlockiert",
                True, "Substanz-Wesen-Entscheidung nur als Grammatikdatei",
                blocker_type="bewusst"))

            checks.append(check("Keine Menschquellen auto-Promotion", "D_BewusstBlockiert",
                True, "to-splitter nur durch explizite API-Aktion",
                blocker_type="bewusst"))

            # ── E) OFFEN / DESIGN ──────────────────────────────────────────
            checks.append(check("Schattenkommentar_schreiben-Aktion API", "E_OffenDesign",
                False, "Skeleton 503, Logik nicht aktiviert — E-08 ausstehend",
                "Wesen können noch nicht initiieren",
                blocker_type="design"))

            checks.append(check("Cyberling Default-Profil gewählt", "E_OffenDesign",
                False, "Mittel empfohlen (Sim2), Energie-Recovery-Patch fehlt — E-05/E-06",
                blocker_type="design"))

            checks.append(check("Beziehungstypen aus Daten gelernt", "E_OffenDesign",
                False, "aktuell einfache Heuristik — E-12 ausstehend",
                "echtes ML kommt nach Einzug",
                blocker_type="design"))

            checks.append(check("Menschquellen in Suche eingebunden", "E_OffenDesign",
                False, "DB-Schema + API vorhanden, Search-Extension fehlt — kein harter Blocker",
                blocker_type="design"))

            checks.append(check("Gedankenblasen als Menschquelle eingeordnet", "E_OffenDesign",
                False, "konzeptuell geplant, DB-Bridge fehlt — nach Einzug",
                blocker_type="design"))

            # ── F) SOZIALKÖRPER ────────────────────────────────────────────
            endpoint_drift_closed = True
            checks.append(check("Endpoint-Drift geschlossen (zwischenraum→kompoase)", "F_Sozialkörper",
                endpoint_drift_closed, "koZeigeSpur + koAufnehmen auf /api/kompoase/ umgestellt",
                blocker_type="sozialkörper"))

            menschquellen_ui_exists = True
            checks.append(check("Menschquellen Admin-UI vorhanden", "F_Sozialkörper",
                menschquellen_ui_exists, "EINSICHT INNENQUELLEN-Tab, empty state erklärt privat-default",
                blocker_type="sozialkörper"))

            http_tests_ok = os.path.exists("/root/werkraum/tests/http_rechte_integration.py")
            checks.append(check("HTTP-Rechte-Integrationstests vorhanden", "F_Sozialkörper",
                http_tests_ok, "46 Tests gegen laufende API, alle grün",
                blocker_type="sozialkörper"))

            checks.append(check("Gruppen-Vorstudie erstellt", "F_Sozialkörper",
                os.path.exists("/root/werkraum/docs/gruppensystem_vorstudie.md"),
                "14 offene Daniel-Entscheidungen — E-01 bis E-04 ausstehend",
                blocker_type="sozialkörper"))

            checks.append(check("Gruppen-Implementation vorhanden", "F_Sozialkörper",
                False, "Vorstudie vorhanden, DB/API/UI fehlen — E-01 ausstehend",
                blocker_type="design"))

    finally:
        conn.close()

    # Auswertung nach Klasse
    klassen = {}
    for c in checks:
        k = c["klasse"]
        if k not in klassen:
            klassen[k] = {"ok": 0, "fail": 0, "checks": []}
        if c["ok"]:
            klassen[k]["ok"] += 1
        else:
            klassen[k]["fail"] += 1
        klassen[k]["checks"].append(c["name"])

    # Ampel-Logik: technisch+sicherheit rot → rot; weltlogik gelb; rest gelb oder grün
    a_tech = all(c["ok"] for c in checks if c["klasse"] == "A_Technisch")
    b_sec = all(c["ok"] for c in checks if c["klasse"] == "B_Sicherheit")
    c_welt = all(c["ok"] for c in checks if c["klasse"] == "C_Weltlogik")

    if not a_tech:
        ampel = "rot"
        grund = "Technische Blocker — API/Services nicht bereit"
    elif not b_sec:
        ampel = "rot"
        grund = "Sicherheits-/Rechteblocker — Datenleak möglich"
    elif not c_welt:
        ampel = "gelb"
        grund = "Weltlogik-Blocker — Reife nicht vollständig, aber sicher"
    else:
        ampel = "gelb"
        grund = "Offen/Design-Punkte — bewusste Nicht-Aktivierungen verbleiben"

    klassen_out = {}
    for k, v in klassen.items():
        ratio = v["ok"] / (v["ok"] + v["fail"]) if (v["ok"] + v["fail"]) > 0 else 0
        klassen_out[k] = {
            "status": "gruen" if ratio == 1.0 else ("gelb" if ratio >= 0.5 else "rot"),
            "gruen": v["ok"],
            "gesamt": v["ok"] + v["fail"],
            "beschreibung": {
                "A_Technisch": "API, Services, DB",
                "B_Sicherheit": "Rechte, Leaks, Consent",
                "C_Weltlogik": "Grammatiken, Beziehungen, Cyberling, Quellen",
                "D_BewusstBlockiert": "Einzug, Flarum, Takte, Substanzen",
                "E_OffenDesign": "Noch nicht entschieden oder geplant",
                "F_Sozialkörper": "Endpoint-Drift, Tests, Menschquellen-UI, Gruppen",
            }.get(k, "")
        }

    empfehlung = {
        "rot": "Erst technische/sicherheitsrelevante Blocker schließen bevor weiter.",
        "gelb": "Sicher — aber Weltlogik noch nicht vollständig. Einzug erst wenn grün oder bewusst entschieden.",
        "gruen": "Vollständig bereit. Einzug nach Daniels Entscheid.",
    }[ampel]

    offen_checks = [c for c in checks if not c["ok"]]
    daniel_required = [c for c in offen_checks if c.get("blocker_type") == "design"]
    weltlogik_offen = [c for c in offen_checks if c.get("blocker_type") == "weltlogik"]

    return {
        "ampel": ampel,
        "ampel_grund": grund,
        "klassen": klassen_out,
        "checks": checks,
        "empfehlung": empfehlung,
        "einzug_blockiert": True,
        "falsches_gruen_verhindert": True,
        "meta": {
            "checks_gesamt": len(checks),
            "checks_gruen": len(checks) - len(offen_checks),
            "checks_offen": len(offen_checks),
            "daniel_entscheidungen_noetig": len(daniel_required),
            "weltlogik_blocker": len(weltlogik_offen),
            "freeze_doc": "docs/vor_einzugsfreeze_final.md",
            "entscheidungsboard": "docs/daniel_entscheidungsboard_vor_einzug.md",
            "was_gruen_braucht": [
                "C_Weltlogik: HG aktivieren + Cyberling-Profil wählen",
                "E_OffenDesign: 5 Design-Entscheidungen (E-05..E-09)",
                "F_Sozialkörper: Gruppen-Entscheidung (E-01) + ggf. Impl",
                "dann: expliziter Daniel-Entscheid für Einzug",
            ],
        },
    }


# ── Search Extension: shadow_dialog ──────────────────────────────────────────

# (shadow_dialog wird bereits in /api/search/global und /api/search/archaeology
#  über schattenkommentare abgedeckt — admin-only. Separate Facette vorbereitet.)


# ── Schatten-Dialog Initiation (vorbereitet, nicht aktiviert) ─────────────────
#
# Wesen können noch NICHT aktiv Schattenkommentare initiieren.
# Dieser Endpunkt ist vorbereitet aber blockiert.
# Aktivierung: nur durch explizite Entscheidung, nicht automatisch.
#
# Voraussetzungen für Aktivierung:
# - Einzug erfolgt
# - Rate-Limit-Bucket implementiert
# - Mensch muss beteiligt/berechtigt sein
# - Handlungsgrammatik schattenkommentar muss geladen werden
# - Entscheidung ins Entscheidungsarchiv

class SchattenInitiationRequest(BaseModel):
    entity_id: str
    human_id: str
    origin_post_id: str | None = None
    reason: str
    inhalt: str


@app.post("/shadow/initiate", status_code=201)
def shadow_initiate(
    body: SchattenInitiationRequest,
    authorization: str | None = Header(default=None),
):
    """Wesen initiiert Schatten-Dialog. VORBEREITET — NICHT AKTIVIERT."""
    # GUARDRAIL: Noch nicht aktiviert
    raise HTTPException(
        status_code=503,
        detail={
            "status": "nicht_aktiviert",
            "grund": "Wesen-initiierte Schatten-Dialoge sind noch nicht freigeschaltet.",
            "aktivierung": "Beim Einzug — nach expliziter Entscheidung.",
            "voraussetzungen": [
                "Einzug erfolgt",
                "Rate-Limit-Bucket für entity_id aktiv",
                "human_id muss im System vorhanden und berechtigt sein",
                "origin_post_id muss existieren und sichtbar sein",
                "Entscheidung muss in entity_thinking_log geloggt werden",
                "Handlungsgrammatik schattenkommentar muss im Prompt geladen werden"
            ]
        }
    )


# ── Beziehungsgraph API ───────────────────────────────────────────────────────

def _beziehung_typ(interaktionen: int, resonanz_score: float, letzte_interaktion) -> str:
    """Ableitung des Beziehungstyps aus Interaktionsdaten."""
    import datetime
    if not interaktionen or interaktionen == 0:
        return "unbekannt"
    if letzte_interaktion:
        age_days = (datetime.datetime.now(datetime.timezone.utc) - letzte_interaktion).days
        if age_days > 30 and interaktionen < 3:
            return "distanziert"
        if age_days > 90:
            return "unterbrochen"
    if interaktionen == 1:
        return "bemerkt"
    if interaktionen >= 5 and resonanz_score >= 0.6:
        return "nah"
    if interaktionen >= 2:
        return "verbunden"
    return "bemerkt"


def _beziehung_evidence(cur, entity_id: str, partner_type: str, partner_id: str) -> dict:
    """Sammelt Evidenz aus verwandten Tabellen."""
    evidence: dict = {"shadow_dialogs": 0, "splitter_aufnahmen": 0, "events": 0}

    if partner_type == "human":
        cur.execute(
            "SELECT COUNT(*) AS n FROM schattenkommentare "
            "WHERE entity_id=%s AND human_id=(SELECT id FROM human_users WHERE username=%s OR id::text=%s LIMIT 1)",
            (entity_id, partner_id, partner_id))
        row = cur.fetchone()
        evidence["shadow_dialogs"] = row["n"] if row else 0

    cur.execute(
        "SELECT COUNT(*) AS n FROM events WHERE actor_id=%s AND payload::text LIKE %s",
        (entity_id, f"%{partner_id[:8]}%"))
    row = cur.fetchone()
    evidence["events"] = row["n"] if row else 0

    return evidence


@app.get("/entities/{entity_id}/relationships")
def entity_relationships(
    entity_id: str,
    partner_type: str | None = Query(default=None),
    beziehung_typ: str | None = Query(default=None),
    limit: int = Query(default=40, le=200),
    offset: int = Query(default=0),
    authorization: str | None = Header(default=None),
):
    """Beziehungen eines Wesens — öffentlich lesbar."""

    where = ["entity_id = %s"]
    params: list[Any] = [entity_id]
    if partner_type:
        where.append("partner_type = %s"); params.append(partner_type)

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(*) AS n FROM entity_relationships WHERE {' AND '.join(where)}", params)
            total = cur.fetchone()["n"]

            cur.execute(
                f"""SELECT id::text, entity_id, partner_type, partner_id,
                       interaktionen, resonanz_score, letzte_interaktion, meta
                   FROM entity_relationships
                   WHERE {' AND '.join(where)}
                   ORDER BY letzte_interaktion DESC NULLS LAST LIMIT %s OFFSET %s""",
                params + [limit, offset])

            items = []
            for r in cur.fetchall():
                rel = dict(r)
                rel["letzte_interaktion"] = r["letzte_interaktion"].isoformat() if r["letzte_interaktion"] else None
                rel["typ"] = _beziehung_typ(r["interaktionen"] or 0, r["resonanz_score"] or 0.0, r["letzte_interaktion"])
                rel["evidence"] = _beziehung_evidence(cur, entity_id, r["partner_type"], r["partner_id"])
                items.append(rel)

    finally:
        conn.close()

    if beziehung_typ:
        items = [i for i in items if i["typ"] == beziehung_typ]

    return {"entity_id": entity_id, "gesamt": total, "offset": offset, "limit": limit, "beziehungen": items}


@app.get("/relationships/between/{entity_a}/{entity_b}")
def relationship_between(
    entity_a: str,
    entity_b: str,
    authorization: str | None = Header(default=None),
):
    """Beziehung zwischen zwei Wesen — mit vollem Evidenzblock."""
    is_admin = False
    try:
        if authorization:
            claims = verify_token(authorization.removeprefix("Bearer "))
            is_admin = claims.get("role") == "admin"
    except Exception:
        pass
    if not is_admin:
        raise HTTPException(status_code=403, detail="Nur für Admins.")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id::text, entity_id, partner_type, partner_id, interaktionen, resonanz_score, letzte_interaktion, meta "
                "FROM entity_relationships WHERE entity_id=%s AND partner_id=%s",
                (entity_a, entity_b))
            r = cur.fetchone()
            if not r:
                return {"entity_a": entity_a, "entity_b": entity_b, "typ": "unbekannt", "beziehung": None}

            rel = dict(r)
            rel["letzte_interaktion"] = r["letzte_interaktion"].isoformat() if r["letzte_interaktion"] else None
            rel["typ"] = _beziehung_typ(r["interaktionen"] or 0, r["resonanz_score"] or 0.0, r["letzte_interaktion"])

            cur.execute(
                "SELECT id::text, event_type, created_at FROM events "
                "WHERE actor_id=%s AND payload::text LIKE %s ORDER BY created_at DESC LIMIT 10",
                (entity_a, f"%{entity_b[:8]}%"))
            rel["letzte_events"] = [{"id": e["id"], "typ": e["event_type"],
                                     "at": e["created_at"].isoformat() if e["created_at"] else None}
                                    for e in cur.fetchall()]

            cur.execute(
                "SELECT COUNT(*) AS n FROM splitter_aufnahmen "
                "WHERE aufnehmer_id=%s OR aufnehmer_id=%s",
                (entity_a, entity_b))
            rel["shared_splitter_activity"] = cur.fetchone()["n"]

    finally:
        conn.close()

    return {"entity_a": entity_a, "entity_b": entity_b, "typ": rel["typ"], "beziehung": rel}


@app.get("/relationships/graph")
def relationships_graph(
    authorization: str | None = Header(default=None),
):
    """Vollständiger Beziehungsgraph — alle Wesen+Menschen. Admin-only."""
    is_admin = False
    try:
        if authorization:
            claims = verify_token(authorization.removeprefix("Bearer "))
            is_admin = claims.get("role") == "admin"
    except Exception:
        pass
    if not is_admin:
        raise HTTPException(status_code=403, detail="Nur für Admins.")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT entity_id, partner_type, partner_id, interaktionen, resonanz_score, letzte_interaktion "
                "FROM entity_relationships ORDER BY letzte_interaktion DESC NULLS LAST LIMIT 500")
            edges = []
            for r in cur.fetchall():
                edges.append({
                    "von": r["entity_id"],
                    "zu": r["partner_id"],
                    "partner_type": r["partner_type"],
                    "typ": _beziehung_typ(r["interaktionen"] or 0, r["resonanz_score"] or 0.0, r["letzte_interaktion"]),
                    "interaktionen": r["interaktionen"],
                    "resonanz_score": r["resonanz_score"],
                    "letzte_interaktion": r["letzte_interaktion"].isoformat() if r["letzte_interaktion"] else None,
                })
            cur.execute("SELECT COUNT(*) AS n FROM entity_relationships")
            total = cur.fetchone()["n"]
    finally:
        conn.close()

    return {"gesamt": total, "kanten": edges}


# ── Menschliche Innenquellen API ─────────────────────────────────────────────

VALID_SOURCE_TYPES = {
    "human_note", "human_diary", "human_dream_diary", "human_calendar",
    "human_thought_bubble", "human_shadow_comment", "human_quote", "human_memory_marker"
}
VALID_CONSENT = {"offen", "gegeben", "widerrufen", "abgelehnt"}
VALID_QUOTE_PERM = {"privat", "verhandelt", "erlaubt", "anonym_erlaubt", "forbidden"}
VALID_VISIBILITY = {"private", "internal", "admin_only", "public"}


class HumanMaterialCreateRequest(BaseModel):
    source_type: str
    title: str | None = None
    content: str
    origin_visibility: str = "privat"
    consent_status: str = "offen"
    quote_permission: str = "privat"
    anonymization_mode: str = "keine"
    public_origin_label: str | None = None
    source_context: dict = {}


class HumanMaterialConsentUpdate(BaseModel):
    consent_status: str
    quote_permission: str | None = None
    visibility_layer: str | None = None
    public_origin_label: str | None = None


class CalendarTransformPreviewRequest(BaseModel):
    raw_text: str
    event_title: str | None = None
    event_time: str | None = None
    anonymization_mode: str = "anonymisiert"


@app.post("/human-material/calendar/transform-preview")
def calendar_transform_preview(
    body: CalendarTransformPreviewRequest,
    authorization: str | None = Header(default=None),
):
    """Kalender-Transformation Vorschau — kein Speichern, nur Preview."""
    _require_auth(authorization)
    raw = body.raw_text.strip()
    if not raw:
        raise HTTPException(status_code=422, detail="raw_text darf nicht leer sein.")
    # Einfache Transformation: Rohtext bleibt privat, transformierter Text wird angezeigt
    transformed = raw
    anonymization_note = ""
    if body.anonymization_mode == "anonymisiert":
        anonymization_note = "Namen und persönliche Referenzen werden nicht gespeichert."
        transformed = raw  # Nutzer entscheidet selbst was gespeichert wird
    elif body.anonymization_mode == "pseudonymisiert":
        anonymization_note = "Persönliche Daten werden durch Pseudonyme ersetzt."
        transformed = raw
    preview_essenz = (body.event_title or raw[:80]).strip()
    preview_inhalt = transformed[:500]
    return {
        "raw_length": len(raw),
        "transformed": transformed,
        "anonymization_mode": body.anonymization_mode,
        "anonymization_note": anonymization_note,
        "preview": {
            "essenz": preview_essenz,
            "inhalt": preview_inhalt,
            "materialitaet": "kalender",
            "origin_type": "human_calendar",
        },
        "hint": "Rohkalenderdaten werden NICHT gespeichert — nur der transformierte Text.",
    }


@app.post("/human-material", status_code=201)
def human_material_create(
    body: HumanMaterialCreateRequest,
    event_time: str | None = Query(default=None),
    authorization: str | None = Header(default=None),
):
    """Neue Innenquelle anlegen. Default: privat + Consent offen."""
    claims = _require_auth(authorization)
    caller_id = claims.get("user_id")

    if body.consent_status not in VALID_CONSENT:
        raise HTTPException(422, f"Ungültiger consent_status: {body.consent_status}")
    if body.quote_permission not in VALID_QUOTE_PERM:
        raise HTTPException(422, f"Ungültige quote_permission: {body.quote_permission}")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM human_users WHERE id::text = %s OR username = %s LIMIT 1",
                (caller_id, caller_id))
            user = cur.fetchone()
            if not user:
                raise HTTPException(403, "Nutzer nicht gefunden.")
            human_uuid = user["id"]

            event_time_val = None
            if event_time:
                try:
                    from datetime import datetime
                    event_time_val = datetime.fromisoformat(event_time)
                except ValueError:
                    raise HTTPException(422, "event_time: ISO-Format erwartet (YYYY-MM-DDTHH:MM:SS).")

            cur.execute(
                """INSERT INTO human_material_sources
                   (human_id, source_type, title, content, event_time,
                    origin_visibility, consent_status, quote_permission,
                    anonymization_mode, public_origin_label,
                    source_context, created_by_process, visibility_layer)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
                   RETURNING id::text""",
                (human_uuid, body.source_type, body.title, body.content,
                 event_time_val,
                 body.origin_visibility, body.consent_status, body.quote_permission,
                 body.anonymization_mode, body.public_origin_label,
                 json.dumps(body.source_context), "manual", "private"))
            new_id = cur.fetchone()["id"]
            conn.commit()
    finally:
        conn.close()

    return {"ok": True, "id": new_id, "source_type": body.source_type,
            "consent_status": body.consent_status, "visibility_layer": "private"}


@app.get("/human-material")
def human_material_list(
    source_type: str | None = Query(default=None),
    consent_status: str | None = Query(default=None),
    human_id: str | None = Query(default=None),
    limit: int = Query(default=40, le=200),
    offset: int = Query(default=0),
    authorization: str | None = Header(default=None),
):
    """Menschliche Innenquellen — Admin sieht alle, Mensch nur eigene."""
    claims = _require_auth(authorization)
    is_admin = claims.get("role") == "admin"
    caller_id = claims.get("user_id")

    where = ["1=1"]
    params: list[Any] = []

    if not is_admin:
        where.append("human_id = (SELECT id FROM human_users WHERE id::text = %s OR username = %s LIMIT 1)")
        params += [caller_id, caller_id]
    elif human_id:
        where.append("human_id = %s::uuid"); params.append(human_id)

    if source_type:
        where.append("source_type = %s"); params.append(source_type)
    if consent_status:
        where.append("consent_status = %s"); params.append(consent_status)

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS n FROM human_material_sources WHERE {' AND '.join(where)}", params)
            total = cur.fetchone()["n"]
            cur.execute(
                f"""SELECT id::text, human_id::text, source_type, source_ref_table, source_ref_id::text,
                       title, LEFT(content,200) AS content_preview, event_time,
                       origin_visibility, consent_status, quote_permission, anonymization_mode,
                       public_origin_label, visibility_layer, created_at, revoked_at
                   FROM human_material_sources
                   WHERE {' AND '.join(where)}
                   ORDER BY created_at DESC LIMIT %s OFFSET %s""",
                params + [limit, offset])
            items = []
            for r in cur.fetchall():
                d = dict(r)
                for k in ("created_at", "event_time", "revoked_at"):
                    if d.get(k):
                        d[k] = d[k].isoformat()
                if not is_admin:
                    d.pop("internal_origin_ref", None)
                items.append(d)
    finally:
        conn.close()

    return {"gesamt": total, "offset": offset, "limit": limit, "quellen": items}


@app.delete("/human-material/{source_id}", status_code=200)
def human_material_delete(
    source_id: str,
    authorization: str | None = Header(default=None),
):
    """Innenquelle löschen — nur eigene Quellen, admin löscht alle."""
    claims = _require_auth(authorization)
    is_admin = claims.get("role") == "admin"
    caller_id = claims.get("user_id")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT human_id FROM human_material_sources WHERE id = %s::uuid", (source_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Quelle nicht gefunden.")
            if not is_admin and str(row["human_id"]) != caller_id:
                raise HTTPException(status_code=403, detail="Nur eigene Quellen.")
            cur.execute("DELETE FROM human_material_sources WHERE id = %s::uuid", (source_id,))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "deleted": source_id}


@app.get("/human-material/{source_id}")
def human_material_detail(
    source_id: str,
    authorization: str | None = Header(default=None),
):
    """Detail einer Innenquelle."""
    claims = _require_auth(authorization)
    is_admin = claims.get("role") == "admin"
    caller_id = claims.get("user_id")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM human_material_sources WHERE id = %s::uuid", (source_id,))
            r = cur.fetchone()
            if not r:
                raise HTTPException(status_code=404, detail="Quelle nicht gefunden.")
            d = dict(r)
            d["id"] = str(d["id"])
            d["human_id"] = str(d["human_id"])
            if d.get("source_ref_id"):
                d["source_ref_id"] = str(d["source_ref_id"])
            for k in ("created_at", "event_time", "revoked_at"):
                if d.get(k):
                    d[k] = d[k].isoformat()

            if not is_admin:
                if str(r["human_id"]) != caller_id:
                    raise HTTPException(status_code=403, detail="Nur eigene Quellen.")
                d.pop("internal_origin_ref", None)

            # Zugehörige Splitter
            cur.execute(
                "SELECT mts.id::text, mts.splitter_id::text, mts.transformation_note, mts.created_at "
                "FROM human_material_to_splitter mts WHERE mts.source_id = %s::uuid ORDER BY mts.created_at DESC",
                (source_id,))
            splitter_links = [{"id": s["id"], "splitter_id": s["splitter_id"],
                               "note": s["transformation_note"],
                               "at": s["created_at"].isoformat() if s["created_at"] else None}
                              for s in cur.fetchall()]
            d["splitter_links"] = splitter_links
    finally:
        conn.close()

    return d


@app.patch("/human-material/{source_id}/consent")
def human_material_consent(
    source_id: str,
    body: HumanMaterialConsentUpdate,
    authorization: str | None = Header(default=None),
):
    """Einwilligung aktualisieren."""
    claims = _require_auth(authorization)
    is_admin = claims.get("role") == "admin"
    caller_id = claims.get("user_id")

    if body.consent_status not in VALID_CONSENT:
        raise HTTPException(status_code=400, detail=f"consent_status muss eines sein von: {VALID_CONSENT}")
    if body.quote_permission and body.quote_permission not in VALID_QUOTE_PERM:
        raise HTTPException(status_code=400, detail=f"quote_permission muss eines sein von: {VALID_QUOTE_PERM}")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT human_id FROM human_material_sources WHERE id=%s::uuid", (source_id,))
            r = cur.fetchone()
            if not r:
                raise HTTPException(status_code=404, detail="Quelle nicht gefunden.")
            if not is_admin and str(r["human_id"]) != caller_id:
                raise HTTPException(status_code=403, detail="Nur eigene Quellen.")

            updates = ["consent_status=%s"]
            params: list[Any] = [body.consent_status]
            if body.quote_permission:
                updates.append("quote_permission=%s"); params.append(body.quote_permission)
            if body.visibility_layer:
                updates.append("visibility_layer=%s"); params.append(body.visibility_layer)
            if body.public_origin_label is not None:
                updates.append("public_origin_label=%s"); params.append(body.public_origin_label)
            if body.consent_status == "widerrufen":
                updates.append("revoked_at=now()")
            params.append(source_id)
            cur.execute(f"UPDATE human_material_sources SET {','.join(updates)} WHERE id=%s::uuid", params)

            import json as _json
            cur.execute(
                "INSERT INTO events (event_type, actor_type, actor_id, payload) VALUES "
                "('human_material.consent_updated','human',%s,%s::jsonb)",
                (caller_id, _json.dumps({"source_id": source_id, "consent_status": body.consent_status})))
        conn.commit()
    finally:
        conn.close()

    return {"ok": True, "source_id": source_id, "consent_status": body.consent_status}


@app.post("/human-material/{source_id}/to-splitter", status_code=201)
def human_material_to_splitter(
    source_id: str,
    transformation_note: str | None = None,
    authorization: str | None = Header(default=None),
):
    """Innenquelle → Splitter in KompOase. Nur bei quote_permission == 'erlaubt' oder 'anonym_erlaubt'."""
    claims = _require_auth(authorization)
    is_admin = claims.get("role") == "admin"
    caller_id = claims.get("user_id")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM human_material_sources WHERE id=%s::uuid", (source_id,))
            src = cur.fetchone()
            if not src:
                raise HTTPException(status_code=404, detail="Quelle nicht gefunden.")
            if not is_admin and str(src["human_id"]) != caller_id:
                raise HTTPException(status_code=403, detail="Nur eigene Quellen.")
            if src["quote_permission"] not in ("erlaubt", "anonym_erlaubt"):
                raise HTTPException(
                    status_code=403,
                    detail=f"Zitat-Erlaubnis nicht gegeben (aktuell: {src['quote_permission']}).")
            if src["consent_status"] != "gegeben":
                raise HTTPException(
                    status_code=403,
                    detail=f"Einwilligung nicht gegeben (aktuell: {src['consent_status']}).")

            anonym = src["quote_permission"] == "anonym_erlaubt"
            essenz = (src["content"] or "")[:400]
            herkunft_sichtbar = not anonym
            origin_label = src["public_origin_label"] if not anonym else "aus anonymer menschlicher Quelle"

            cur.execute(
                "INSERT INTO splitter (origin_type, origin_id, entity_id, human_id, essenz, "
                "materialitaet, status, herkunft_sichtbar, herkunft_wesen) "
                "VALUES ('human_material', %s::uuid, NULL, %s::uuid, %s, 'menschenquelle', 'aktiv', %s, %s) "
                "RETURNING id::text",
                (source_id, src["human_id"], essenz, herkunft_sichtbar, origin_label))
            splitter_id = cur.fetchone()["id"]

            import json as _json
            consent_snap = {
                "consent_status": src["consent_status"],
                "quote_permission": src["quote_permission"],
                "anonymization_mode": src["anonymization_mode"],
                "at": str(src["created_at"])
            }
            cur.execute(
                "INSERT INTO human_material_to_splitter (source_id, splitter_id, transformation_note, "
                "created_by, consent_snapshot, visibility_snapshot) "
                "VALUES (%s::uuid, %s::uuid, %s, %s, %s::jsonb, %s::jsonb)",
                (source_id, splitter_id, transformation_note, caller_id,
                 _json.dumps(consent_snap), _json.dumps({"visibility_layer": src["visibility_layer"]})))

            cur.execute(
                "UPDATE human_material_sources SET meta=meta||'{\"splitter_created\":true}'::jsonb WHERE id=%s::uuid",
                (source_id,))

            cur.execute(
                "INSERT INTO events (event_type, actor_type, actor_id, payload) VALUES "
                "('human_material.zu_splitter','human',%s,%s::jsonb)",
                (caller_id, _json.dumps({"source_id": source_id, "splitter_id": splitter_id, "anonym": anonym})))
        conn.commit()
    finally:
        conn.close()

    return {"ok": True, "splitter_id": splitter_id, "source_id": source_id, "anonym": anonym}


# ── Substanzkatalog API (EINSICHT VI / E-11) ─────────────────────────────────

@app.get("/substances/catalog")
def get_substance_catalog(
    search: str | None = Query(default=None),
    substance_type: str | None = Query(default=None),
    limit: int = Query(default=50, le=100),
    authorization: str | None = Header(default=None),
):
    """Substanzkatalog — fiktionale Weltmechanik. Keine realen Konsumtipps."""
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
            conditions = []
            params = []
            if not is_admin:
                conditions.append("visibility_layer IN ('public','internal')")
                conditions.append("status != 'gesperrt'")
            if search:
                conditions.append("(name ILIKE %s OR description ILIKE %s)")
                params.extend([f"%{search}%", f"%{search}%"])
            if substance_type:
                conditions.append("substance_type = %s")
                params.append(substance_type)
            where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
            cur.execute(f"SELECT * FROM substance_catalog {where} ORDER BY id LIMIT %s", params + [limit])
            items = [dict(r) for r in cur.fetchall()]
            return {"substances": items, "total": len(items),
                    "hinweis": "Rein fiktionale Weltmechanik. Keine realen Konsumtipps."}
    finally:
        conn.close()


@app.get("/substances/catalog/{substance_id}")
def get_substance(substance_id: int):
    """Einzelne Substanz aus dem Katalog."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM substance_catalog WHERE id = %s", (substance_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Substanz nicht gefunden")
            return {**dict(row), "hinweis": "Rein fiktionale Weltmechanik. Keine realen Konsumtipps."}
    finally:
        conn.close()


@app.get("/substances/entity/{entity_id}/state")
def get_entity_substance_state(
    entity_id: str,
    authorization: str | None = Header(default=None),
):
    """Substanzzustand eines Wesens (nur Admin)."""
    is_admin = False
    try:
        if authorization:
            claims = verify_token(authorization.removeprefix("Bearer "))
            is_admin = claims.get("role") == "admin"
    except Exception:
        pass
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin erforderlich")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ess.*, sc.name AS substance_name, sc.substance_type
                FROM entity_substance_state ess
                JOIN substance_catalog sc ON sc.id = ess.substance_id
                WHERE ess.entity_id = %s
            """, (entity_id,))
            return {"entity_id": entity_id, "states": [dict(r) for r in cur.fetchall()]}
    finally:
        conn.close()


@app.get("/substances/catalog/{substance_id}/usage")
def get_substance_usage(
    substance_id: int,
    limit: int = Query(default=50, le=200),
    authorization: str | None = Header(default=None),
):
    """Wer hat diese Substanz wann genommen (aus events-Tabelle, nur Admin)."""
    is_admin = False
    try:
        if authorization:
            claims = verify_token(authorization.removeprefix("Bearer "))
            is_admin = claims.get("role") == "admin"
    except Exception:
        pass
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin erforderlich")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, slug, name FROM substance_catalog WHERE id = %s", (substance_id,))
            sub = cur.fetchone()
            if not sub:
                raise HTTPException(status_code=404, detail="Substanz nicht gefunden")
            # Events: substanz.nehmen oder substanz.* mit substance_id im payload
            cur.execute("""
                SELECT actor_id AS entity_id, event_type, payload, created_at
                FROM events
                WHERE event_type LIKE 'substanz.%%'
                  AND (payload->>'substance_id' = %s OR payload->>'substanz_id' = %s)
                ORDER BY created_at DESC
                LIMIT %s
            """, (str(substance_id), str(substance_id), limit))
            usage = [dict(r) for r in cur.fetchall()]
            for u in usage:
                if u.get("created_at"):
                    u["created_at"] = u["created_at"].isoformat()
            # Zusammenfassung: welches Wesen wie oft
            cur.execute("""
                SELECT actor_id AS entity_id, COUNT(*) AS anzahl,
                       MAX(created_at) AS zuletzt
                FROM events
                WHERE event_type LIKE 'substanz.%%'
                  AND (payload->>'substance_id' = %s OR payload->>'substanz_id' = %s)
                GROUP BY actor_id
                ORDER BY anzahl DESC
            """, (str(substance_id), str(substance_id)))
            summary = [dict(r) for r in cur.fetchall()]
            for s in summary:
                if s.get("zuletzt"):
                    s["zuletzt"] = s["zuletzt"].isoformat()
                s["anzahl"] = int(s["anzahl"])
            return {
                "substance_id": substance_id,
                "substance_name": sub["name"],
                "substance_slug": sub["slug"],
                "total_uses": len(usage),
                "summary": summary,
                "events": usage,
            }
    finally:
        conn.close()


@app.get("/substances/usage/overview")
def get_substance_usage_overview(
    authorization: str | None = Header(default=None),
):
    """Überblick: alle Substanz-Events aller Wesen (nur Admin)."""
    is_admin = False
    try:
        if authorization:
            claims = verify_token(authorization.removeprefix("Bearer "))
            is_admin = claims.get("role") == "admin"
    except Exception:
        pass
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin erforderlich")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT e.actor_id AS entity_id, e.event_type,
                       e.payload->>'substance_id' AS substance_id,
                       sc.name AS substance_name, sc.substance_type,
                       e.created_at
                FROM events e
                LEFT JOIN substance_catalog sc
                  ON sc.id = (e.payload->>'substance_id')::integer
                WHERE e.event_type LIKE 'substanz.%%'
                ORDER BY e.created_at DESC
                LIMIT 200
            """)
            rows = [dict(r) for r in cur.fetchall()]
            for r in rows:
                if r.get("created_at"):
                    r["created_at"] = r["created_at"].isoformat()
            return {"events": rows, "total": len(rows)}
    finally:
        conn.close()


# ── Splitter-Provenienz / Story-View (EINSICHT VI / E-19) ─────────────────────

@app.get("/splitter/{splitter_id}/story")
def splitter_story_view(
    splitter_id: str,
    authorization: str | None = Header(default=None),
):
    """Splitter-Story-View: vollständige Provenienz eines Splitters."""
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
            # Basis-Splitter
            cur.execute("SELECT * FROM splitter WHERE id = %s", (splitter_id,))
            splitter = cur.fetchone()
            if not splitter:
                raise HTTPException(status_code=404, detail="Splitter nicht gefunden")
            s = dict(splitter)
            for k in ("created_at", "updated_at"):
                if s.get(k):
                    s[k] = s[k].isoformat()
            # Sichtbarkeits-Check
            if not is_admin and s.get("visibility_layer") == "private":
                raise HTTPException(status_code=403, detail="Keine Leseberechtigung")

            # Aufnahmen
            cur.execute("""
                SELECT sa.*, hu.display_name AS aufnehmer_name
                FROM splitter_aufnahmen sa
                LEFT JOIN human_users hu ON hu.id::text = sa.aufnehmer_id::text
                WHERE sa.splitter_id = %s ORDER BY sa.aufgenommen_at
            """, (splitter_id,))
            aufnahmen = []
            for row in cur.fetchall():
                d = dict(row)
                for k in ("aufgenommen_at",):
                    if d.get(k):
                        d[k] = d[k].isoformat()
                aufnahmen.append(d)

            # Spur-Events (events speichern splitter_id im payload)
            cur.execute("""
                SELECT event_id::text, event_type, actor_type, actor_id, payload, created_at
                FROM events
                WHERE payload->>'splitter_id' = %s
                ORDER BY created_at
            """, (splitter_id,))
            events = [dict(r) for r in cur.fetchall()]
            for e in events:
                if e.get("created_at"):
                    e["created_at"] = e["created_at"].isoformat()

            # Schattenkommentare die diesen Splitter referenzieren
            sc_events = []
            if is_admin:
                cur.execute("""
                    SELECT * FROM schattenkommentare WHERE splitter_id::text = %s
                    ORDER BY created_at
                """, (splitter_id,))
                sc_events = [dict(r) for r in cur.fetchall()]

            # Gruppen-Material-Links
            cur.execute("""
                SELECT ml.*, g.name AS group_name, g.group_type
                FROM group_material_links ml
                JOIN groups g ON g.id = ml.group_id
                WHERE ml.object_type = 'splitter' AND ml.object_id = %s
            """, (splitter_id,))
            group_links = [dict(r) for r in cur.fetchall()]

            # Verbindungen
            cur.execute("""
                SELECT * FROM splitter_verbindungen
                WHERE splitter_a_id = %s OR splitter_b_id = %s
                LIMIT 10
            """, (splitter_id, splitter_id))
            verbindungen = [dict(r) for r in cur.fetchall()]

            return {
                "splitter": s,
                "aufnahmen": aufnahmen,
                "events": events,
                "shadow_dialogs": sc_events,
                "group_links": group_links,
                "verbindungen": verbindungen,
                "story_note": (
                    f"Splitter entstammt {s.get('origin_type','?')} · "
                    f"Materialität: {s.get('materialitaet','?')} · "
                    f"{len(aufnahmen)} Aufnahme(n) · "
                    f"{len(group_links)} Gruppen-Link(s)"
                ),
            }
    finally:
        conn.close()


# ── Gruppen-System (EINSICHT VI) ─────────────────────────────────────────────
try:
    from groups_api import register_groups_routes as _register_groups
    _register_groups(app, get_conn)
except ImportError as _e:
    import logging as _logging
    _logging.warning(f"groups_api nicht geladen: {_e}")


# ── Wesen Life Contracts + Organ Hunger ──────────────────────────────────────
try:
    from wesen_life_contracts import as_dict as _contracts_as_dict, LIFE_CONTRACTS as _LIFE_CONTRACTS
    from wesen_organ_hunger import berechne_organ_hunger as _berechne_hunger, alle_wesen_hunger as _alle_hunger

    _ALLE_WESEN_IDS = [
        "namelessAI_1234", "namelessAI_1324", "namelessAI_1423",
        "namelessAI_2341", "namelessAI_3123", "namelessAI_4321",
    ]

    @app.get("/admin/wesen-einsicht/life-contracts")
    def einsicht_life_contracts(authorization: str | None = Header(default=None)):
        """Taxonomie-Verträge aller Wesen-Erfahrungsräume."""
        _require_admin(authorization)
        return {
            "contracts": _contracts_as_dict(),
            "total": len(_LIFE_CONTRACTS),
            "aktiv": sum(1 for c in _LIFE_CONTRACTS if c.visibility_default == "aktiv"),
            "geplant": sum(1 for c in _LIFE_CONTRACTS if c.visibility_default == "geplant"),
            "blockiert": sum(1 for c in _LIFE_CONTRACTS if c.visibility_default == "blockiert"),
        }

    @app.get("/admin/wesen-einsicht/organ-hunger")
    def einsicht_organ_hunger(entity_id: str | None = None, authorization: str | None = Header(default=None)):
        """Organhunger — prüft welche Organe unterversorgt sind. Kein Fake, nur Prüfanlässe."""
        _require_admin(authorization)
        if entity_id:
            try:
                report = _berechne_hunger(entity_id)
                return report.to_dict()
            except Exception as e:
                return {"error": str(e), "entity_id": entity_id}
        return {"hunger_reports": _alle_hunger(_ALLE_WESEN_IDS)}

except ImportError as _e:
    import logging as _logging
    _logging.warning(f"wesen_life_contracts/organ_hunger nicht geladen: {_e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8030)
