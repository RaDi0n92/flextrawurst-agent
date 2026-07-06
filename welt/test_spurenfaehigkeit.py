"""Tests für Spurenfähigkeit v0.1 — Post-Relationen, Zustandsabdruck, Themen-Klima.

Läuft gegen die Live-DB. Voraussetzung: welt-api läuft auf Port 8030.
Ausführen: python3 test_spurenfaehigkeit.py
"""
import json
import sys
import uuid
import psycopg2
import psycopg2.extras
import requests

BASE = "http://localhost:8030"
import os as _os; DB_DSN = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")


def get_conn():
    conn = psycopg2.connect(DB_DSN)
    conn.cursor_factory = psycopg2.extras.RealDictCursor
    return conn


def _first_public_post_id() -> str | None:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM ftw_posts WHERE sichtbarkeit='public' LIMIT 1")
            row = cur.fetchone()
            return str(row["id"]) if row else None
    finally:
        conn.close()


def _first_public_thema_id() -> str | None:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM themen WHERE sichtbarkeit='public' LIMIT 1")
            row = cur.fetchone()
            return str(row["id"]) if row else None
    finally:
        conn.close()


# ── Schema-Tests (ohne HTTP) ─────────────────────────────────────────────────

def test_post_relationen_tabelle_existiert():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM post_relationen")
            assert cur.fetchone()["n"] >= 0
    finally:
        conn.close()
    print("✓ post_relationen Tabelle existiert")


def test_rel_typ_check_constraint():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            post_id = _first_public_post_id()
            if not post_id:
                print("⚠ Kein Post vorhanden — überspringe rel_typ-Test")
                return
            try:
                cur.execute(
                    """INSERT INTO post_relationen (von_post_id, rel_typ, ziel_typ, ziel_id)
                       VALUES (%s, 'ungueltig_typ', 'post', %s)""",
                    (post_id, post_id),
                )
                conn.rollback()
                assert False, "CHECK-Constraint hätte greifen sollen"
            except psycopg2.errors.CheckViolation:
                conn.rollback()
    finally:
        conn.close()
    print("✓ rel_typ CHECK-Constraint schlägt bei ungültigem Wert an")


def test_ziel_typ_check_constraint():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            post_id = _first_public_post_id()
            if not post_id:
                print("⚠ Kein Post vorhanden — überspringe ziel_typ-Test")
                return
            try:
                cur.execute(
                    """INSERT INTO post_relationen (von_post_id, rel_typ, ziel_typ, ziel_id)
                       VALUES (%s, 'echoes', 'ungueltig_ziel', 'irgendwas')""",
                    (post_id,),
                )
                conn.rollback()
                assert False, "CHECK-Constraint hätte greifen sollen"
            except psycopg2.errors.CheckViolation:
                conn.rollback()
    finally:
        conn.close()
    print("✓ ziel_typ CHECK-Constraint schlägt bei ungültigem Wert an")


def test_zu_post_id_konsistenz_constraint():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            post_id = _first_public_post_id()
            if not post_id:
                print("⚠ Kein Post vorhanden — überspringe Konsistenz-Test")
                return
            try:
                cur.execute(
                    """INSERT INTO post_relationen
                       (von_post_id, rel_typ, ziel_typ, ziel_id, zu_post_id)
                       VALUES (%s, 'echoes', 'thema', 'irgendwas', %s)""",
                    (post_id, post_id),
                )
                conn.rollback()
                assert False, "ck_zu_post_konsistent hätte greifen sollen"
            except psycopg2.errors.CheckViolation:
                conn.rollback()
    finally:
        conn.close()
    print("✓ ck_zu_post_konsistent schlägt an: zu_post_id bei ziel_typ≠post verboten")


def test_thema_klima_status_check():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) AS n FROM themen
                WHERE klima_status NOT IN
                    ('stable','fermenting','overheated','splitting',
                     'buried','repeating','exhausted','seeded')
            """)
            ungueltig = cur.fetchone()["n"]
            assert ungueltig == 0, f"{ungueltig} Themen mit ungültigem klima_status"
    finally:
        conn.close()
    print("✓ Alle themen.klima_status-Werte sind gültig")


def test_thema_klima_default_stable():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM themen WHERE klima_status = 'stable'")
            n = cur.fetchone()["n"]
            assert n > 0, "Kein einziges Thema hat klima_status='stable'"
    finally:
        conn.close()
    print("✓ Mindestens ein Thema mit klima_status='stable' (Default-Check)")


def test_ftw_posts_neue_spalten():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'ftw_posts'
                  AND column_name IN ('flarum_herkunft','ist_voreinzug','zustandsabdruck')
            """)
            gefunden = {r["column_name"] for r in cur.fetchall()}
            fehlend = {"flarum_herkunft", "ist_voreinzug", "zustandsabdruck"} - gefunden
            assert not fehlend, f"Fehlende Spalten in ftw_posts: {fehlend}"
    finally:
        conn.close()
    print("✓ ftw_posts hat flarum_herkunft, ist_voreinzug, zustandsabdruck")


# ── HTTP-Tests ───────────────────────────────────────────────────────────────

def test_relationen_endpunkt_leer():
    post_id = _first_public_post_id()
    if not post_id:
        print("⚠ Kein Post — überspringe HTTP-Test")
        return
    r = requests.get(f"{BASE}/welt/posts/{post_id}/relationen", timeout=5)
    assert r.status_code == 200, f"Status {r.status_code}: {r.text[:200]}"
    data = r.json()
    assert "ausgehend" in data and "eingehend" in data
    print("✓ GET /welt/posts/{id}/relationen antwortet mit ausgehend+eingehend")


def test_spur_endpunkt():
    post_id = _first_public_post_id()
    if not post_id:
        print("⚠ Kein Post — überspringe Spur-Test")
        return
    r = requests.get(f"{BASE}/welt/posts/{post_id}/spur?tiefe=1", timeout=5)
    assert r.status_code == 200, f"Status {r.status_code}: {r.text[:200]}"
    data = r.json()
    assert "knoten" in data and "total" in data and "tiefe" in data
    print("✓ GET /welt/posts/{id}/spur antwortet mit knoten+total+tiefe")


def test_spur_ungueltige_richtung():
    post_id = _first_public_post_id()
    if not post_id:
        print("⚠ Kein Post — überspringe")
        return
    r = requests.get(f"{BASE}/welt/posts/{post_id}/spur?richtung=diagonal", timeout=5)
    assert r.status_code == 422
    print("✓ GET /spur mit ungültiger Richtung → 422")


def test_thema_detail_klima():
    thema_id = _first_public_thema_id()
    if not thema_id:
        print("⚠ Kein Thema — überspringe")
        return
    r = requests.get(f"{BASE}/welt/themen/{thema_id}", timeout=5)
    assert r.status_code == 200, f"Status {r.status_code}: {r.text[:200]}"
    data = r.json()
    assert "klima_status" in data
    assert data["klima_status"] in (
        "stable", "fermenting", "overheated", "splitting",
        "buried", "repeating", "exhausted", "seeded",
    )
    print(f"✓ GET /welt/themen/{{id}} enthält klima_status='{data['klima_status']}'")


def test_relationen_filter_ungueltig():
    post_id = _first_public_post_id()
    if not post_id:
        print("⚠ Kein Post — überspringe")
        return
    r = requests.get(
        f"{BASE}/welt/posts/{post_id}/relationen?rel_typ=kein_echter_typ",
        timeout=5,
    )
    assert r.status_code == 422
    print("✓ GET /relationen mit ungültigem rel_typ → 422")


def test_post_detail_hat_relationen_count():
    post_id = _first_public_post_id()
    if not post_id:
        print("⚠ Kein Post — überspringe")
        return
    r = requests.get(f"{BASE}/welt/posts/{post_id}", timeout=5)
    assert r.status_code == 200, f"Status {r.status_code}: {r.text[:200]}"
    data = r.json()
    assert "relationen_ausgehend" in data
    assert "relationen_eingehend" in data
    print("✓ GET /welt/posts/{id} enthält relationen_ausgehend und relationen_eingehend")


def test_relation_anlegen_und_lesen():
    """Legt eine echte Relation in DB an und liest sie zurück."""
    post_id = _first_public_post_id()
    if not post_id:
        print("⚠ Kein Post — überspringe")
        return

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Relation direkt in DB einfügen (kein Admin-Token nötig)
            cur.execute(
                """INSERT INTO post_relationen
                   (von_post_id, rel_typ, ziel_typ, ziel_id, zu_post_id,
                    erstellt_von_type, erstellt_von_id, notiz)
                   VALUES (%s, 'echoes', 'post', %s, %s, 'system', 'test', 'Testrelation')
                   RETURNING id""",
                (post_id, post_id, post_id),
            )
            rel_id = str(cur.fetchone()["id"])
        conn.commit()
    finally:
        conn.close()

    # Via HTTP abrufen
    r = requests.get(f"{BASE}/welt/posts/{post_id}/relationen", timeout=5)
    assert r.status_code == 200
    data = r.json()
    ids_ausgehend = [item["id"] for item in data["ausgehend"]]
    assert rel_id in ids_ausgehend, "Angelegte Relation nicht in ausgehend gefunden"

    # Aufräumen
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM post_relationen WHERE id = %s::uuid", (rel_id,))
        conn.commit()
    finally:
        conn.close()

    print("✓ Relation anlegen → via /relationen lesbar → aufgeräumt")


if __name__ == "__main__":
    tests = [
        test_post_relationen_tabelle_existiert,
        test_rel_typ_check_constraint,
        test_ziel_typ_check_constraint,
        test_zu_post_id_konsistenz_constraint,
        test_thema_klima_status_check,
        test_thema_klima_default_stable,
        test_ftw_posts_neue_spalten,
        test_relationen_endpunkt_leer,
        test_spur_endpunkt,
        test_spur_ungueltige_richtung,
        test_thema_detail_klima,
        test_relationen_filter_ungueltig,
        test_post_detail_hat_relationen_count,
        test_relation_anlegen_und_lesen,
    ]
    fehlgeschlagen = []
    for t in tests:
        try:
            t()
        except Exception as e:
            print(f"✗ {t.__name__}: {e}")
            fehlgeschlagen.append(t.__name__)
    print(f"\n{len(tests) - len(fehlgeschlagen)}/{len(tests)} Tests bestanden.")
    if fehlgeschlagen:
        print("Fehlgeschlagen:", fehlgeschlagen)
        sys.exit(1)


# ── Spurenwache + Keine-Relation-Sichtbarkeit (v0.3 Abschluss) ───────────────

def _get_conn():
    return psycopg2.connect(DB_DSN, cursor_factory=psycopg2.extras.RealDictCursor)


def _cleanup(post_ids: list):
    conn = _get_conn()
    with conn.cursor() as cur:
        for pid in post_ids:
            cur.execute("DELETE FROM ftw_posts WHERE id = %s::uuid", (pid,))
    conn.commit()
    conn.close()


def _make_entity_post(content: str, zustandsabdruck: dict | None = None) -> str:
    conn = _get_conn()
    import psycopg2.extras as ex
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO ftw_posts
                (autor_type, autor_id, content, post_type, sichtbarkeit, raum_id, zustandsabdruck)
            VALUES ('entity', 'F3INSCHM3CK3R', %s, 'gedanke', 'public',
                    '3ac02912-55c7-4b52-a69a-c4bf9a845cdd', %s)
            RETURNING id
        """, (content, ex.Json(zustandsabdruck or {})))
        pid = str(cur.fetchone()["id"])
    conn.commit()
    conn.close()
    return pid


def test_post_ohne_relation_hat_entscheidungsmetadaten():
    """gedanke_posten via denk_tick-Metadaten: relation_decision='none' ist im zustandsabdruck."""
    pid = _make_entity_post(
        "Test keine Relation Metadaten — aufräumen",
        zustandsabdruck={
            "relation_decision_source": "wesen_schreibentscheidung",
            "relation_decision_scope": "lokaler_weltkontext",
            "relation_candidates_count": 23,
            "relation_selected_count": 0,
            "relation_decision": "none",
        }
    )
    try:
        conn = _get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT zustandsabdruck FROM ftw_posts WHERE id = %s::uuid", (pid,))
            abd = cur.fetchone()["zustandsabdruck"]
        conn.close()
        assert abd["relation_decision"] == "none"
        assert abd["relation_candidates_count"] == 23
        assert abd["relation_selected_count"] == 0
        assert abd["relation_decision_source"] == "wesen_schreibentscheidung"
    finally:
        _cleanup([pid])


def test_post_mit_relation_hat_entscheidungsmetadaten():
    """Post mit gewählter Relation hat relation_decision='chosen' im zustandsabdruck."""
    pid = _make_entity_post(
        "Test Relation Metadaten — aufräumen",
        zustandsabdruck={
            "relation_decision_source": "wesen_schreibentscheidung",
            "relation_decision_scope": "lokaler_weltkontext",
            "relation_candidates_count": 23,
            "relation_selected_count": 1,
            "relation_decision": "chosen",
        }
    )
    try:
        conn = _get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT zustandsabdruck FROM ftw_posts WHERE id = %s::uuid", (pid,))
            abd = cur.fetchone()["zustandsabdruck"]
        conn.close()
        assert abd["relation_decision"] == "chosen"
        assert abd["relation_selected_count"] == 1
    finally:
        _cleanup([pid])


def test_spurenwache_endpoint_erreichbar():
    """GET /admin/spurenwache antwortet mit korrekter Struktur."""
    r = requests.get(f"{BASE}/admin/spurenwache?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert "eintraege" in data
    assert "total" in data
    assert isinstance(data["eintraege"], list)


def test_spurenwache_zeigt_keine_relation_entscheidung():
    """Posts mit relation_decision='none' erscheinen in der Spurenwache."""
    pid = _make_entity_post(
        "Test Spurenwache none — aufräumen",
        zustandsabdruck={
            "relation_decision_source": "wesen_schreibentscheidung",
            "relation_decision_scope": "lokaler_weltkontext",
            "relation_candidates_count": 10,
            "relation_selected_count": 0,
            "relation_decision": "none",
        }
    )
    try:
        r = requests.get(f"{BASE}/admin/spurenwache?limit=100")
        data = r.json()
        post_ids = [e["post_id"] for e in data["eintraege"]]
        assert pid in post_ids, "Post mit relation_decision=none muss in Spurenwache erscheinen"
        eintrag = next(e for e in data["eintraege"] if e["post_id"] == pid)
        assert eintrag["relation_decision"] == "none"
        assert eintrag["kandidaten_count"] == 10
        assert eintrag["gewaehlt_count"] == 0
        assert eintrag["relationen"] == []
    finally:
        _cleanup([pid])


def test_spurenwache_zeigt_gewaehlte_relation():
    """Posts mit relation_decision='chosen' erscheinen in Spurenwache mit Relation-Eintrag."""
    # Referenz-Post anlegen
    ref_pid = _make_entity_post("Referenz für Spurenwache-chosen-Test")
    # Haupt-Post anlegen
    main_pid = _make_entity_post(
        "Test Spurenwache chosen — aufräumen",
        zustandsabdruck={
            "relation_decision_source": "wesen_schreibentscheidung",
            "relation_decision_scope": "lokaler_weltkontext",
            "relation_candidates_count": 10,
            "relation_selected_count": 1,
            "relation_decision": "chosen",
        }
    )
    try:
        # Relation eintragen
        conn = _get_conn()
        import psycopg2.extras as ex
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO post_relationen
                    (von_post_id, rel_typ, ziel_typ, ziel_id, zu_post_id,
                     erstellt_von_type, erstellt_von_id, notiz, meta)
                VALUES (%s::uuid, 'echoes', 'post', %s, %s::uuid,
                        'entity', 'F3INSCHM3CK3R', 'Testnotiz', %s)
            """, (main_pid, ref_pid, ref_pid,
                  ex.Json({"decision_source": "wesen_schreibentscheidung",
                           "candidate_group": "eigene_letzte_posts"})))
        conn.commit()
        conn.close()

        r = requests.get(f"{BASE}/admin/spurenwache?limit=100")
        data = r.json()
        eintraege = {e["post_id"]: e for e in data["eintraege"]}
        assert main_pid in eintraege, "Haupt-Post muss in Spurenwache erscheinen"
        e = eintraege[main_pid]
        assert e["relation_decision"] == "chosen"
        assert e["gewaehlt_count"] == 1
        assert len(e["relationen"]) == 1
        assert e["relationen"][0]["rel_typ"] == "echoes"
        assert e["relationen"][0]["candidate_group"] == "eigene_letzte_posts"
    finally:
        _cleanup([main_pid, ref_pid])


def test_kandidaten_count_korrekt_gespeichert():
    """kandidaten_count in Spurenwache entspricht dem gespeicherten Wert."""
    pid = _make_entity_post(
        "Test kandidaten count — aufräumen",
        zustandsabdruck={
            "relation_decision_source": "wesen_schreibentscheidung",
            "relation_decision_scope": "lokaler_weltkontext",
            "relation_candidates_count": 17,
            "relation_selected_count": 0,
            "relation_decision": "none",
        }
    )
    try:
        r = requests.get(f"{BASE}/admin/spurenwache?limit=100")
        data = r.json()
        eintraege = {e["post_id"]: e for e in data["eintraege"]}
        assert pid in eintraege
        assert eintraege[pid]["kandidaten_count"] == 17
    finally:
        _cleanup([pid])
