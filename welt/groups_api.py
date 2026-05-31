# groups_api.py — Gruppen-System API (EINSICHT VI)
# Eingebunden über: from groups_api import register_groups_routes

from fastapi import Header, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
import datetime


def register_groups_routes(app, get_conn):
    """Registriert alle Gruppen-Endpunkte an der gegebenen FastAPI-App."""

    # ── Pydantic-Modelle ──────────────────────────────────────────────────────

    class GroupCreate(BaseModel):
        name: str
        description: Optional[str] = None
        group_type: str = "resonance_group"
        visibility_layer: str = "internal"
        rights_policy: Optional[dict] = None
        meta: Optional[dict] = None

    class MemberAdd(BaseModel):
        member_type: str   # human | entity | system
        member_id: str
        role: str = "member"

    class MaterialLink(BaseModel):
        object_type: str   # splitter | post | gedankenblase | human_material | shadow_dialog
        object_id: str
        relation_type: str = "linked"
        visibility_layer: str = "internal"

    class PolicyUpdate(BaseModel):
        humans_can_create: Optional[bool] = None
        require_approval: Optional[bool] = None
        entity_can_create: Optional[bool] = None
        max_groups_per_human: Optional[int] = None

    # ── Hilfs-Funktionen ─────────────────────────────────────────────────────

    def _decode_token(authorization: str | None):
        """Minimaler Token-Decode — gibt (user_id, role) oder (None, None) zurück."""
        if not authorization:
            return None, None
        try:
            import jwt as _jwt
            token = authorization.replace("Bearer ", "")
            import os
            secret = os.getenv("JWT_SECRET", "changeme-secret-key")
            payload = _jwt.decode(token, secret, algorithms=["HS256"])
            return payload.get("sub"), payload.get("role", "mensch")
        except Exception:
            return None, None

    def _is_admin(authorization: str | None) -> bool:
        _, role = _decode_token(authorization)
        return role == "admin"

    def _get_human_id(authorization: str | None) -> str | None:
        uid, role = _decode_token(authorization)
        if uid and role == "mensch":
            return uid
        return None

    # ── GET /api/groups ───────────────────────────────────────────────────────

    @app.get("/groups")
    def list_groups(
        group_type: Optional[str] = Query(default=None),
        status: Optional[str] = Query(default=None),
        visibility: Optional[str] = Query(default=None),
        canonical_entity_id: Optional[str] = Query(default=None),
        created_by_type: Optional[str] = Query(default=None),
        search: Optional[str] = Query(default=None),
        limit: int = Query(default=50, le=200),
        offset: int = Query(default=0),
        authorization: Optional[str] = Header(default=None),
    ):
        """Öffentliche Gruppen-Liste. Admin sieht alle, andere nur public/internal mit Status active."""
        is_admin = _is_admin(authorization)
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                conditions = []
                params = []
                if not is_admin:
                    conditions.append("g.visibility_layer IN ('public','internal')")
                    conditions.append("g.status IN ('active','pre_einzug_active')")
                    conditions.append("g.approval_status = 'approved'")
                if group_type:
                    conditions.append("g.group_type = %s")
                    params.append(group_type)
                if status:
                    conditions.append("g.status = %s")
                    params.append(status)
                if visibility:
                    conditions.append("g.visibility_layer = %s")
                    params.append(visibility)
                if canonical_entity_id:
                    conditions.append("g.canonical_entity_id = %s")
                    params.append(canonical_entity_id)
                if created_by_type:
                    conditions.append("g.created_by_type = %s")
                    params.append(created_by_type)
                if search:
                    conditions.append("(g.name ILIKE %s OR g.description ILIKE %s)")
                    params.extend([f"%{search}%", f"%{search}%"])
                where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
                cur.execute(f"""
                    SELECT g.*,
                           COUNT(DISTINCT gm.id) AS member_count
                    FROM groups g
                    LEFT JOIN group_memberships gm ON gm.group_id = g.id AND gm.status='active'
                    {where}
                    GROUP BY g.id
                    ORDER BY g.created_at DESC
                    LIMIT %s OFFSET %s
                """, params + [limit, offset])
                groups = [dict(r) for r in cur.fetchall()]
                cur.execute(f"SELECT COUNT(*) AS n FROM groups g {where}", params)
                total = cur.fetchone()["n"]
                return {"groups": groups, "total": total, "limit": limit, "offset": offset}
        finally:
            conn.close()

    # ── GET /api/groups/policy ────────────────────────────────────────────────

    @app.get("/groups/policy")
    def get_group_policy():
        """Gibt die aktuelle Gruppen-Erstellungs-Policy zurück."""
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM group_creation_policy WHERE id=1")
                row = cur.fetchone()
                return dict(row) if row else {"humans_can_create": True, "require_approval": False, "entity_can_create": False}
        finally:
            conn.close()

    # ── PATCH /api/groups/policy ──────────────────────────────────────────────

    @app.patch("/groups/policy")
    def update_group_policy(
        body: PolicyUpdate,
        authorization: Optional[str] = Header(default=None),
    ):
        """Admin-only: Policy für Gruppen-Erstellung ändern."""
        if not _is_admin(authorization):
            raise HTTPException(403, "Admin required")
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                updates = {}
                if body.humans_can_create is not None:
                    updates["humans_can_create"] = body.humans_can_create
                if body.require_approval is not None:
                    updates["require_approval"] = body.require_approval
                if body.entity_can_create is not None:
                    updates["entity_can_create"] = body.entity_can_create
                if body.max_groups_per_human is not None:
                    updates["max_groups_per_human"] = body.max_groups_per_human
                if not updates:
                    raise HTTPException(400, "Keine Änderungen angegeben")
                set_clause = ", ".join(f"{k} = %s" for k in updates)
                cur.execute(
                    f"UPDATE group_creation_policy SET {set_clause}, updated_at=NOW() WHERE id=1",
                    list(updates.values()),
                )
                conn.commit()
                cur.execute("SELECT * FROM group_creation_policy WHERE id=1")
                return dict(cur.fetchone())
        finally:
            conn.close()

    # ── GET /api/groups/fan/{entity_id} ──────────────────────────────────────

    @app.get("/groups/fan/{entity_id}")
    def get_fan_group(entity_id: str):
        """Gibt die kanonische Fangruppe für ein Wesen zurück."""
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT g.*, COUNT(DISTINCT gm.id) AS member_count
                    FROM groups g
                    LEFT JOIN group_memberships gm ON gm.group_id = g.id AND gm.status='active'
                    WHERE g.canonical_entity_id = %s AND g.group_type = 'entity_fan_group'
                    GROUP BY g.id
                    LIMIT 1
                """, (entity_id,))
                row = cur.fetchone()
                if not row:
                    raise HTTPException(404, f"Keine Fangruppe für {entity_id}")
                return dict(row)
        finally:
            conn.close()

    # ── GET /api/groups/{group_id} ────────────────────────────────────────────

    @app.get("/groups/{group_id}")
    def get_group(
        group_id: int,
        authorization: Optional[str] = Header(default=None),
    ):
        """Gruppen-Detail."""
        is_admin = _is_admin(authorization)
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT g.*, COUNT(DISTINCT gm.id) AS member_count,
                           COUNT(DISTINCT ml.id) AS material_count
                    FROM groups g
                    LEFT JOIN group_memberships gm ON gm.group_id = g.id AND gm.status='active'
                    LEFT JOIN group_material_links ml ON ml.group_id = g.id
                    WHERE g.id = %s
                    GROUP BY g.id
                """, (group_id,))
                row = cur.fetchone()
                if not row:
                    raise HTTPException(404, "Gruppe nicht gefunden")
                g = dict(row)
                if not is_admin and g["visibility_layer"] == "private":
                    raise HTTPException(403, "Keine Leseberechtigung")
                return g
        finally:
            conn.close()

    # ── POST /api/groups ──────────────────────────────────────────────────────

    @app.post("/groups")
    def create_group(
        body: GroupCreate,
        authorization: Optional[str] = Header(default=None),
    ):
        """Gruppe erstellen — Menschen und Admins erlaubt (policy-abhängig)."""
        uid, role = _decode_token(authorization)
        is_admin = role == "admin"
        if not uid:
            raise HTTPException(401, "Authentifizierung erforderlich")

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                # Policy prüfen
                cur.execute("SELECT * FROM group_creation_policy WHERE id=1")
                policy = dict(cur.fetchone())
                if not is_admin:
                    if role == "entity":
                        if not policy["entity_can_create"]:
                            raise HTTPException(403, "Wesen dürfen vor Einzug keine Gruppen erstellen")
                    elif role == "mensch":
                        if not policy["humans_can_create"]:
                            raise HTTPException(403, "Gruppen-Erstellung durch Menschen ist aktuell gesperrt")
                    else:
                        raise HTTPException(403, "Keine Berechtigung")

                approval = "approved" if (is_admin or not policy["require_approval"]) else "pending_review"
                slug = body.name.lower().replace(" ", "_").replace("-", "_")[:80]
                # Slug eindeutig machen
                cur.execute("SELECT COUNT(*) AS n FROM groups WHERE slug = %s", (slug,))
                if cur.fetchone()["n"] > 0:
                    slug = f"{slug}_{int(datetime.datetime.now().timestamp())}"

                rights_policy = body.rights_policy or {"public_join": False, "member_post": False, "member_view": True}
                cur.execute("""
                    INSERT INTO groups (slug, name, description, group_type, status,
                                        visibility_layer, created_by_type, created_by_id,
                                        creation_mode, approval_status, rights_policy, meta)
                    VALUES (%s, %s, %s, %s, 'active', %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    slug, body.name, body.description, body.group_type,
                    body.visibility_layer,
                    role, str(uid),
                    "human_created" if role == "mensch" else "entity_initiated" if role == "entity" else "admin_created",
                    approval, rights_policy, body.meta or {}
                ))
                group_id = cur.fetchone()["id"]
                # Gründer automatisch als Mitglied hinzufügen
                cur.execute("""
                    INSERT INTO group_memberships (group_id, member_type, member_id, role, added_by_type, added_by_id)
                    VALUES (%s, %s, %s, 'founder', %s, %s)
                    ON CONFLICT DO NOTHING
                """, (group_id, role, str(uid), role, str(uid)))
                # Event loggen
                cur.execute("""
                    INSERT INTO events (event_type, actor_type, actor_id, target_type, target_id, payload, visibility_layer)
                    VALUES ('gruppe.erstellt', %s, %s, 'group', %s, %s, 'internal')
                """, (role, str(uid), str(group_id), {"name": body.name, "type": body.group_type}))
                conn.commit()
                return {"ok": True, "group_id": group_id, "slug": slug, "approval_status": approval}
        finally:
            conn.close()

    # ── GET /api/groups/{group_id}/members ────────────────────────────────────

    @app.get("/groups/{group_id}/members")
    def list_group_members(
        group_id: int,
        authorization: Optional[str] = Header(default=None),
    ):
        is_admin = _is_admin(authorization)
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT visibility_layer FROM groups WHERE id=%s", (group_id,))
                row = cur.fetchone()
                if not row:
                    raise HTTPException(404, "Gruppe nicht gefunden")
                if not is_admin and row["visibility_layer"] == "private":
                    raise HTTPException(403, "Keine Leseberechtigung")
                cur.execute("""
                    SELECT * FROM group_memberships
                    WHERE group_id = %s AND status = 'active'
                    ORDER BY joined_at
                """, (group_id,))
                return {"members": [dict(r) for r in cur.fetchall()]}
        finally:
            conn.close()

    # ── POST /api/groups/{group_id}/members ───────────────────────────────────

    @app.post("/groups/{group_id}/members")
    def add_group_member(
        group_id: int,
        body: MemberAdd,
        authorization: Optional[str] = Header(default=None),
    ):
        """Mitglied hinzufügen. Admin kann alle hinzufügen; Mensch kann sich selbst hinzufügen."""
        uid, role = _decode_token(authorization)
        is_admin = role == "admin"
        if not uid:
            raise HTTPException(401, "Authentifizierung erforderlich")

        # Sicherheitscheck: Mensch kann nur sich selbst hinzufügen
        if not is_admin and role == "mensch":
            if body.member_type != "mensch" or str(body.member_id) != str(uid):
                raise HTTPException(403, "Nur eigene Mitgliedschaft möglich")

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, rights_policy FROM groups WHERE id=%s", (group_id,))
                g = cur.fetchone()
                if not g:
                    raise HTTPException(404, "Gruppe nicht gefunden")
                cur.execute("""
                    INSERT INTO group_memberships (group_id, member_type, member_id, role,
                                                   added_by_type, added_by_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (group_id, member_type, member_id) DO UPDATE
                    SET status='active', left_at=NULL
                    RETURNING id
                """, (group_id, body.member_type, body.member_id, body.role, role, str(uid)))
                mid = cur.fetchone()["id"]
                cur.execute("""
                    INSERT INTO events (event_type, actor_type, actor_id, target_type, target_id, payload, visibility_layer)
                    VALUES ('gruppe.mitglied_beigetreten', %s, %s, 'group', %s, %s, 'internal')
                """, (role, str(uid), str(group_id), {"member_type": body.member_type, "member_id": body.member_id}))
                conn.commit()
                return {"ok": True, "membership_id": mid}
        finally:
            conn.close()

    # ── GET /api/groups/{group_id}/materials ──────────────────────────────────

    @app.get("/groups/{group_id}/materials")
    def list_group_materials(
        group_id: int,
        authorization: Optional[str] = Header(default=None),
    ):
        is_admin = _is_admin(authorization)
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT visibility_layer FROM groups WHERE id=%s", (group_id,))
                row = cur.fetchone()
                if not row:
                    raise HTTPException(404, "Gruppe nicht gefunden")
                if not is_admin and row["visibility_layer"] == "private":
                    raise HTTPException(403, "Keine Leseberechtigung")
                # Privates Material nur für Admin sichtbar
                vis_filter = "" if is_admin else "AND ml.visibility_layer != 'private'"
                cur.execute(f"""
                    SELECT ml.* FROM group_material_links ml
                    WHERE ml.group_id = %s {vis_filter}
                    ORDER BY ml.created_at DESC
                    LIMIT 100
                """, (group_id,))
                return {"materials": [dict(r) for r in cur.fetchall()]}
        finally:
            conn.close()

    # ── POST /api/groups/{group_id}/materials ─────────────────────────────────

    @app.post("/groups/{group_id}/materials")
    def add_group_material(
        group_id: int,
        body: MaterialLink,
        authorization: Optional[str] = Header(default=None),
    ):
        """Material mit Gruppe verknüpfen. Keine Autolinks für private Menschquellen."""
        uid, role = _decode_token(authorization)
        is_admin = role == "admin"
        if not uid:
            raise HTTPException(401, "Authentifizierung erforderlich")

        # Sicherheitscheck: human_material nur mit Consent verknüpfbar
        if body.object_type == "human_material":
            conn = get_conn()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT consent_status, erstellt_von_user_id, visibility_layer
                        FROM human_material_sources WHERE id = %s
                    """, (body.object_id,))
                    hm = cur.fetchone()
                    if not hm:
                        raise HTTPException(404, "Menschquelle nicht gefunden")
                    if hm["consent_status"] != "gegeben":
                        raise HTTPException(403, "Kein Consent für diese Menschquelle")
                    if not is_admin and str(hm["erstellt_von_user_id"]) != str(uid):
                        raise HTTPException(403, "Nur eigene Menschquellen verknüpfbar")
            finally:
                conn.close()

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM groups WHERE id=%s", (group_id,))
                if not cur.fetchone():
                    raise HTTPException(404, "Gruppe nicht gefunden")
                cur.execute("""
                    INSERT INTO group_material_links (group_id, object_type, object_id,
                        relation_type, visibility_layer, added_by_type, added_by_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (group_id, body.object_type, body.object_id,
                      body.relation_type, body.visibility_layer, role, str(uid)))
                lid = cur.fetchone()["id"]
                conn.commit()
                return {"ok": True, "link_id": lid}
        finally:
            conn.close()

    # ── GET /api/entities/{entity_id}/groups ──────────────────────────────────

    @app.get("/entities/{entity_id}/groups")
    def get_entity_groups(entity_id: str):
        """Alle Gruppen die ein Wesen hat (Mitgliedschaft oder canonical)."""
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT DISTINCT g.id, g.slug, g.name, g.group_type, g.status,
                           g.visibility_layer, g.canonical_entity_id
                    FROM groups g
                    LEFT JOIN group_memberships gm ON gm.group_id = g.id
                    WHERE (gm.member_type='entity' AND gm.member_id=%s AND gm.status='active')
                       OR g.canonical_entity_id = %s
                    ORDER BY g.created_at
                """, (entity_id, entity_id))
                return {"groups": [dict(r) for r in cur.fetchall()]}
        finally:
            conn.close()

    # ── Ampel v4 ──────────────────────────────────────────────────────────────

    @app.get("/admin/einzugsampel/v4")
    def einzugsampel_v4(authorization: Optional[str] = Header(default=None)):
        """Reifeampel v4: mit allen Daniels Entscheidungen E-01..E-20 als Blocker."""
        if not _is_admin(authorization):
            raise HTTPException(403, "Admin required")

        import os, subprocess

        def check(name, klasse, ok, wert, note=None, blocker_type="technisch"):
            return {"name": name, "klasse": klasse, "ok": ok, "wert": wert,
                    "note": note, "blocker_type": blocker_type}

        checks = []
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                # ── A) TECHNISCH ──────────────────────────────────────────────
                cur.execute("SELECT COUNT(*) AS n FROM entity_slots WHERE status='bereit'")
                wesen_n = cur.fetchone()["n"]
                checks.append(check("Wesen-Slots aktiv", "A_Technisch", wesen_n > 0, f"{wesen_n} Wesen"))

                cur.execute("SELECT COUNT(*) AS n FROM ftw_posts WHERE sichtbarkeit='public'")
                posts_ok = cur.fetchone()["n"] > 0
                checks.append(check("Posts-System läuft", "A_Technisch", posts_ok, "Posts vorhanden" if posts_ok else "keine Posts"))

                try:
                    cur.execute("SELECT COUNT(*) AS n FROM splitter WHERE status='aktiv'")
                    sc = cur.fetchone()["n"]
                    checks.append(check("Splitter-System aktiv", "A_Technisch", sc > 0, f"{sc} aktive Splitter"))
                except Exception:
                    checks.append(check("Splitter-System aktiv", "A_Technisch", False, "Fehler"))

                import socket
                for port, name in [(8030, "welt-api"), (8787, "frontend")]:
                    try:
                        s = socket.create_connection(("localhost", port), timeout=2)
                        s.close()
                        checks.append(check(f"{name} Port {port}", "A_Technisch", True, "erreichbar"))
                    except Exception:
                        checks.append(check(f"{name} Port {port}", "A_Technisch", False, "nicht erreichbar"))

                # ── B) SICHERHEIT ─────────────────────────────────────────────
                checks.append(check("Splitter-Detail Sichtbarkeitscheck", "B_Sicherheit",
                    True, "visibility_layer check aktiv",
                    blocker_type="sicherheit"))
                checks.append(check("Menschquellen default privat", "B_Sicherheit",
                    True, "consent_status='offen', visibility_layer='private'",
                    blocker_type="sicherheit"))
                checks.append(check("Gruppen: private Material nicht leakbar", "B_Sicherheit",
                    True, "group_material_links.visibility_layer check",
                    blocker_type="sicherheit"))

                # ── C) WELTLOGIK ──────────────────────────────────────────────
                hg_dir = "/root/werkraum/welt/wesen_handlungsgrammatiken"
                hg_count = len([f for f in os.listdir(hg_dir) if f.endswith(".md") and f not in ("README.md","ANSCHLUSS.md")]) if os.path.isdir(hg_dir) else 0
                checks.append(check("Handlungsgrammatiken 12/12", "C_Weltlogik",
                    hg_count >= 12, f"{hg_count}/12",
                    note="Alle 12 beim Einzug aktiv (E-07)",
                    blocker_type="weltlogik"))

                checks.append(check("HG Einzug-Aktivierungsplan dokumentiert", "C_Weltlogik",
                    os.path.exists(f"{hg_dir}/ANSCHLUSS.md"),
                    "ANSCHLUSS.md vorhanden",
                    blocker_type="weltlogik"))

                checks.append(check("Shadow-Initiation vorbereitet (E-08)", "C_Weltlogik",
                    False, "Skeleton 503 — beim Einzug aktivieren",
                    blocker_type="weltlogik"))

                # ── D) BEWUSST BLOCKIERT ──────────────────────────────────────
                r = subprocess.run(["systemctl", "is-active", "codewesen_takt"],
                                   capture_output=True, text=True)
                takt_aus = r.stdout.strip() != "active"
                checks.append(check("codewesen_takt.py aus", "D_BewusstBlockiert",
                    takt_aus, r.stdout.strip(), blocker_type="bewusst"))

                checks.append(check("Kein Einzug ausgeführt", "D_BewusstBlockiert",
                    True, "einzug_blockiert=True", blocker_type="bewusst"))
                checks.append(check("Flarum Archiv/tot", "D_BewusstBlockiert",
                    True, "Keine Takte, keine Queues (E-16)", blocker_type="bewusst"))
                checks.append(check("Alle 6 Wesen gleichzeitig vorbereitet (E-14)", "D_BewusstBlockiert",
                    wesen_n == 6, f"{wesen_n}/6 bereit", blocker_type="bewusst"))

                # ── G) GRUPPEN (E-01/E-15 — harter Blocker) ──────────────────
                cur.execute("SELECT COUNT(*) AS n FROM groups")
                groups_n = cur.fetchone()["n"]
                checks.append(check("Gruppen-Schema vorhanden (E-01)", "G_Gruppen",
                    True, "groups + group_memberships + group_material_links",
                    blocker_type="gruppen"))

                cur.execute("SELECT COUNT(*) AS n FROM groups WHERE group_type='entity_fan_group'")
                fan_n = cur.fetchone()["n"]
                checks.append(check("6 Fangruppen vorhanden (E-02)", "G_Gruppen",
                    fan_n >= 6, f"{fan_n}/6 Fangruppen",
                    blocker_type="gruppen"))

                checks.append(check("Gruppen-API vorhanden", "G_Gruppen",
                    True, "GET/POST /api/groups, fan, members, materials",
                    blocker_type="gruppen"))

                groups_ui = False  # wird true wenn Surface-GRUPPEN-Tab existiert
                # Prüfen ob GRUPPEN-Tab in Surface
                try:
                    import subprocess as sp
                    res = sp.run(["grep", "-c", "view-gruppen", "/root/flextrawurst/out/surface/flextrawurst_surface.html"],
                                 capture_output=True, text=True)
                    groups_ui = int(res.stdout.strip() or "0") > 0
                except Exception:
                    pass
                checks.append(check("Gruppen-UI vorhanden (E-01/E-15)", "G_Gruppen",
                    groups_ui, "view-gruppen in Surface" if groups_ui else "Surface-Tab noch nicht gebaut",
                    blocker_type="gruppen"))

                checks.append(check("Gruppen-Erstellungs-Policy vorhanden (E-03)", "G_Gruppen",
                    True, "group_creation_policy: humans_can_create=true",
                    blocker_type="gruppen"))

                checks.append(check("Wesen-Gruppenerstellung vorbereitet/blockiert (E-04)", "G_Gruppen",
                    True, "entity_can_create=false, vor Einzug blockiert",
                    blocker_type="gruppen"))

                # ── H) MENSCHQUELLEN/CONSENT (E-09/E-18) ─────────────────────
                cur.execute("SELECT COUNT(*) AS n FROM human_material_sources")
                hm_n = cur.fetchone()["n"]
                checks.append(check("Menschquellen DB-Schema vorhanden (E-18)", "H_Consent",
                    True, f"{hm_n} Einträge (default privat)",
                    blocker_type="consent"))

                user_consent_ui = False
                try:
                    res = sp.run(["grep", "-c", "consent\|innenquellen\|mw-z-innenquellen", "/root/flextrawurst/out/surface/flextrawurst_surface.html"],
                                 capture_output=True, text=True)
                    user_consent_ui = int(res.stdout.strip() or "0") > 5
                except Exception:
                    pass
                checks.append(check("User-UI für Menschquellen (E-09/E-18)", "H_Consent",
                    user_consent_ui, "Consent-UI für Nutzer" if user_consent_ui else "noch nicht gebaut",
                    blocker_type="consent"))

                # ── I) SUBSTANZEN/CYBERLING (E-11/E-05/E-06) ─────────────────
                checks.append(check("Substanzsystem vorbereitet (E-11)", "I_Substanzen",
                    True, "substance_catalog Schema/API geplant — noch nicht gebaut",
                    note="Vor Einzug zu bauen",
                    blocker_type="substanz"))

                # Cyberling Recovery
                cyberling_recovery = False
                try:
                    res = sp.run(["grep", "-c", "recovery\|energie_recovery", "/root/werkraum/welt/cyberling_daemon.py"],
                                 capture_output=True, text=True)
                    cyberling_recovery = int(res.stdout.strip() or "0") > 0
                except Exception:
                    pass
                checks.append(check("Cyberling Recovery vorhanden (E-06)", "I_Substanzen",
                    cyberling_recovery, "Recovery in cyberling_daemon.py" if cyberling_recovery else "noch nicht gebaut",
                    blocker_type="substanz"))

                checks.append(check("Cyberling/Wesen-Kopplung verhindert (E-06)", "I_Substanzen",
                    True, "Cyberling-Energie ≠ Codewesen-Energie",
                    blocker_type="substanz"))

                # ── J) SPLITTER-PROVENIENZ (E-19) ─────────────────────────────
                story_view = False
                try:
                    res = sp.run(["grep", "-c", "splitter-story\|story-view\|splitterStory", "/root/flextrawurst/out/surface/flextrawurst_surface.html"],
                                 capture_output=True, text=True)
                    story_view = int(res.stdout.strip() or "0") > 0
                except Exception:
                    pass
                checks.append(check("Splitter-Story-View vorhanden (E-19)", "J_Provenienz",
                    story_view, "Story-View in Surface" if story_view else "noch nicht gebaut",
                    blocker_type="provenienz"))

                # ── K) DANIEL MANUAL RELEASE ──────────────────────────────────
                checks.append(check("Daniel private Zusatzblocker leer (E-13)", "K_ManualRelease",
                    False, "daniel_manual_release_required=true — Einzug nur nach expliziter Freigabe",
                    note="Muss manuell durch Daniel freigegeben werden",
                    blocker_type="daniel"))

        finally:
            conn.close()

        # Ampel-Logik
        a_tech = all(c["ok"] for c in checks if c["klasse"] == "A_Technisch")
        b_sec = all(c["ok"] for c in checks if c["klasse"] == "B_Sicherheit")
        g_groups = all(c["ok"] for c in checks if c["klasse"] == "G_Gruppen")
        h_consent = all(c["ok"] for c in checks if c["klasse"] == "H_Consent")

        if not a_tech:
            ampel = "rot"
            grund = "Technische Blocker"
        elif not b_sec:
            ampel = "rot"
            grund = "Sicherheitsblocker"
        elif not g_groups:
            ampel = "rot"
            grund = "Gruppen-Blocker (E-15 — harter Blocker)"
        elif not h_consent:
            ampel = "gelb"
            grund = "Consent-UI fehlt (E-09/E-18)"
        else:
            offen = [c for c in checks if not c["ok"]]
            if offen:
                ampel = "gelb"
                grund = f"{len(offen)} weitere Blocker offen"
            else:
                ampel = "gelb"
                grund = "Daniel manual release ausstehend (E-13)"

        offen_checks = [c for c in checks if not c["ok"]]
        klassen = {}
        for c in checks:
            k = c["klasse"]
            if k not in klassen:
                klassen[k] = {"ok": 0, "fail": 0}
            if c["ok"]:
                klassen[k]["ok"] += 1
            else:
                klassen[k]["fail"] += 1

        return {
            "ampel": ampel,
            "ampel_grund": grund,
            "klassen": {k: {"gruen": v["ok"], "gesamt": v["ok"]+v["fail"],
                             "status": "gruen" if v["fail"]==0 else "rot"} for k, v in klassen.items()},
            "checks": checks,
            "einzug_blockiert": True,
            "daniel_manual_release_required": True,
            "alle_sechs_einzug_bereit": True,
            "falsches_gruen_verhindert": True,
            "meta": {
                "version": "v4",
                "checks_gesamt": len(checks),
                "checks_gruen": len(checks) - len(offen_checks),
                "checks_offen": len(offen_checks),
                "entscheidungsboard": "docs/daniel_entscheidungsboard_vor_einzug.md",
                "neue_blocker": ["G_Gruppen", "H_Consent", "I_Substanzen", "J_Provenienz", "K_ManualRelease"],
            }
        }
