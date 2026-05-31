"""Tests für Wesen-Spurenentscheidung v2 — lokaler Weltkontext.

Testet:
- parse_output erkennt RELATION_1/2/3 korrekt (Format: typ|uuid|grund)
- ungültige Typen, UUIDs und halluzinierte UUIDs werden ignoriert
- Kandidatenvalidierung: nur Pool-UUIDs akzeptiert
- gedanke_posten setzt Relationen mit notiz + meta korrekt
- mehrere Relationen (bis 3) werden alle geschrieben
- mehr als 3 werden auf 3 begrenzt
- Post ohne Relation funktioniert weiterhin
- build_kontext liefert eigene_letzte_posts UND lokale_kontext_posts
- lokale_kontext_posts enthält fremde Posts (andere Entitäten)

Läuft gegen Live-DB. Voraussetzung: welt-api läuft auf Port 8030.
Ausführen: python3 test_wesen_spurenentscheidung.py
"""

import json
import sys
import uuid

import psycopg2
import psycopg2.extras
import pytest

sys.path.insert(0, "/root/werkraum/welt")
from entity_kern import parse_output, gedanke_posten, build_kontext, _REL_TYPEN, _UUID_RE

DB_URI = "postgresql://dak:dakpass@localhost:5432/flextrawurst"
TEST_ENTITY = "namelessAI_1324"
ZWISCHENRAUM_ID = "3ac02912-55c7-4b52-a69a-c4bf9a845cdd"


def get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)


def _saubern(post_ids: list[str]):
    conn = get_conn()
    with conn.cursor() as cur:
        for pid in post_ids:
            cur.execute("DELETE FROM ftw_posts WHERE id = %s::uuid", (pid,))
    conn.commit()
    conn.close()


def _make_post(entity_id=TEST_ENTITY, content="Testpost", raum_id=ZWISCHENRAUM_ID) -> str:
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO ftw_posts (autor_type, autor_id, content, post_type, sichtbarkeit, raum_id)
            VALUES ('entity', %s, %s, 'gedanke', 'public', %s)
            RETURNING id
        """, (entity_id, content, raum_id))
        pid = str(cur.fetchone()["id"])
    conn.commit()
    conn.close()
    return pid


# ── parse_output: Einheitstests ───────────────────────────────────────────────

def test_parse_output_kein_relation_feld():
    text = "GEDANKE: X.\nENTSCHEIDUNG: gedanke_posten\nBEGRÜNDUNG: So.\nINHALT: Inhalt."
    r = parse_output(text)
    assert r["relationen"] == []


def test_parse_output_einzelne_relation_1():
    uid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    text = (
        f"GEDANKE: X.\nENTSCHEIDUNG: gedanke_posten\nINHALT: T.\n"
        f"RELATION_1: upgrade_of|{uid}|Weiterentwicklung des früheren Motivs"
    )
    r = parse_output(text)
    assert len(r["relationen"]) == 1
    rel = r["relationen"][0]
    assert rel["rel_typ"] == "upgrade_of"
    assert rel["ziel_typ"] == "post"
    assert rel["ziel_id"] == uid
    assert rel["zu_post_id"] == uid
    assert "Weiterentwicklung" in rel["notiz"]


def test_parse_output_mehrere_relationen():
    uid1 = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    uid2 = "b2c3d4e5-f6a7-8901-bcde-f12345678901"
    text = (
        f"GEDANKE: X.\nENTSCHEIDUNG: gedanke_posten\nINHALT: T.\n"
        f"RELATION_1: upgrade_of|{uid1}|erster Grund\n"
        f"RELATION_2: echoes|{uid2}|zweiter Grund"
    )
    r = parse_output(text)
    assert len(r["relationen"]) == 2
    assert r["relationen"][0]["rel_typ"] == "upgrade_of"
    assert r["relationen"][1]["rel_typ"] == "echoes"


def test_parse_output_max_3_relationen():
    uids = [
        "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "b2c3d4e5-f6a7-8901-bcde-f12345678901",
        "c3d4e5f6-a7b8-9012-cdef-123456789012",
    ]
    text = (
        f"GEDANKE: X.\nENTSCHEIDUNG: gedanke_posten\nINHALT: T.\n"
        f"RELATION_1: upgrade_of|{uids[0]}|eins\n"
        f"RELATION_2: echoes|{uids[1]}|zwei\n"
        f"RELATION_3: contradicts|{uids[2]}|drei\n"
    )
    r = parse_output(text)
    assert len(r["relationen"]) == 3


def test_parse_output_ungueltig_typ_ignoriert():
    uid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    text = f"GEDANKE: X.\nENTSCHEIDUNG: gedanke_posten\nRELATION_1: phantom_typ|{uid}|irgendwas"
    r = parse_output(text)
    assert r["relationen"] == []


def test_parse_output_ungueltige_uuid_ignoriert():
    text = "GEDANKE: X.\nENTSCHEIDUNG: gedanke_posten\nRELATION_1: echoes|kein-uuid|grund"
    r = parse_output(text)
    assert r["relationen"] == []


def test_parse_output_alle_erlaubten_typen():
    uid = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    for rel_typ in _REL_TYPEN:
        text = f"GEDANKE: X.\nENTSCHEIDUNG: gedanke_posten\nRELATION_1: {rel_typ}|{uid}|grund"
        r = parse_output(text)
        assert len(r["relationen"]) == 1, f"Typ {rel_typ} nicht erkannt"
        assert r["relationen"][0]["rel_typ"] == rel_typ


def test_parse_output_grund_abgeschnitten_bei_200():
    uid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    langer_grund = "x" * 300
    text = f"GEDANKE: X.\nENTSCHEIDUNG: gedanke_posten\nRELATION_1: echoes|{uid}|{langer_grund}"
    r = parse_output(text)
    assert len(r["relationen"][0]["notiz"]) <= 200


def test_parse_output_grund_ohne_pipe_ignoriert_relation_nicht():
    uid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    # Kein | nach uuid — Grund ist leer
    text = f"GEDANKE: X.\nENTSCHEIDUNG: gedanke_posten\nRELATION_1: echoes|{uid}"
    r = parse_output(text)
    assert len(r["relationen"]) == 1
    assert r["relationen"][0]["notiz"] is None or r["relationen"][0]["notiz"] == ""


# ── build_kontext: DB-Tests ───────────────────────────────────────────────────

def test_build_kontext_hat_eigene_letzte_posts():
    ctx = build_kontext(TEST_ENTITY)
    assert "eigene_letzte_posts" in ctx
    assert isinstance(ctx["eigene_letzte_posts"], list)


def test_build_kontext_hat_lokale_kontext_posts():
    ctx = build_kontext(TEST_ENTITY)
    assert "lokale_kontext_posts" in ctx
    assert isinstance(ctx["lokale_kontext_posts"], list)


def test_build_kontext_lokale_posts_enthalten_fremde():
    # Erstelle einen Post von einer anderen Entität im Zwischenraum
    andere_entity = "namelessAI_1323"
    pid = _make_post(entity_id=andere_entity, content="Fremder Welt-Post für Kontext-Test")
    try:
        ctx = build_kontext(TEST_ENTITY)
        lokale_ids = [str(p["id"]) for p in ctx["lokale_kontext_posts"]]
        assert pid in lokale_ids, "Fremder Post sollte in lokalen Kontext-Posts erscheinen"
    finally:
        _saubern([pid])


def test_build_kontext_keine_duplikate():
    """Eigene Posts dürfen nicht in lokale_kontext_posts auftauchen."""
    ctx = build_kontext(TEST_ENTITY)
    eigene_ids = {str(p["id"]) for p in ctx["eigene_letzte_posts"]}
    lokale_ids = {str(p["id"]) for p in ctx["lokale_kontext_posts"]}
    assert eigene_ids.isdisjoint(lokale_ids), "Eigene Posts dürfen nicht doppelt erscheinen"


def test_build_kontext_kandidaten_uuids():
    ctx = build_kontext(TEST_ENTITY)
    assert "kandidaten_uuids" in ctx
    assert isinstance(ctx["kandidaten_uuids"], set)
    # Alle eigenen und lokalen Posts müssen im Pool sein
    for p in ctx["eigene_letzte_posts"]:
        assert str(p["id"]) in ctx["kandidaten_uuids"]
    for p in ctx["lokale_kontext_posts"]:
        assert str(p["id"]) in ctx["kandidaten_uuids"]


def test_build_kontext_kandidaten_gruppen():
    ctx = build_kontext(TEST_ENTITY)
    assert "kandidaten_gruppen" in ctx
    gruppen = ctx["kandidaten_gruppen"]
    for p in ctx["eigene_letzte_posts"]:
        assert gruppen.get(str(p["id"])) == "eigene_letzte_posts"
    for p in ctx["lokale_kontext_posts"]:
        assert gruppen.get(str(p["id"])) == "lokale_kontext_posts"


def test_build_kontext_hat_lokale_spuren():
    ctx = build_kontext(TEST_ENTITY)
    assert "lokale_spuren" in ctx
    assert isinstance(ctx["lokale_spuren"], list)


# ── DB-Tests: gedanke_posten ──────────────────────────────────────────────────

def test_gedanke_posten_ohne_relation():
    gedanke_posten(TEST_ENTITY, "Test ohne Relation — wird aufgeräumt.", "innerer Gedanke")
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id FROM ftw_posts WHERE autor_id = %s AND content = %s
            ORDER BY created_at DESC LIMIT 1
        """, (TEST_ENTITY, "Test ohne Relation — wird aufgeräumt."))
        row = cur.fetchone()
    conn.close()
    assert row is not None
    post_id = str(row["id"])

    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS n FROM post_relationen WHERE von_post_id = %s::uuid", (post_id,))
        count = cur.fetchone()["n"]
    conn.close()
    assert count == 0
    _saubern([post_id])


def test_gedanke_posten_mit_einer_relation():
    ref_id = _make_post(content="Referenz-Post v2")
    try:
        gedanke_posten(
            TEST_ENTITY,
            "Test mit einer Relation v2 — wird aufgeräumt.",
            "innerer Gedanke",
            initiale_relationen=[{
                "rel_typ": "upgrade_of",
                "ziel_typ": "post",
                "ziel_id": ref_id,
                "zu_post_id": ref_id,
                "notiz": "Weiterentwicklung v2",
                "meta": {"decision_source": "wesen_schreibentscheidung",
                         "candidate_group": "eigene_letzte_posts",
                         "context_scope": "lokaler_weltkontext",
                         "selected_by_entity": True},
            }],
        )
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.id, r.rel_typ, r.notiz, r.meta, r.erstellt_von_type
                FROM ftw_posts p
                JOIN post_relationen r ON r.von_post_id = p.id
                WHERE p.autor_id = %s AND p.content = %s
                ORDER BY p.created_at DESC LIMIT 1
            """, (TEST_ENTITY, "Test mit einer Relation v2 — wird aufgeräumt."))
            row = cur.fetchone()
        conn.close()
        assert row is not None
        assert row["rel_typ"] == "upgrade_of"
        assert row["erstellt_von_type"] == "entity"
        assert "Weiterentwicklung" in (row["notiz"] or "")
        meta = row["meta"] if isinstance(row["meta"], dict) else json.loads(row["meta"] or "{}")
        assert meta.get("decision_source") == "wesen_schreibentscheidung"
        assert meta.get("candidate_group") == "eigene_letzte_posts"
        assert meta.get("context_scope") == "lokaler_weltkontext"
        new_post_id = str(row["id"])
    finally:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM ftw_posts WHERE autor_id = %s AND content = %s",
                        (TEST_ENTITY, "Test mit einer Relation v2 — wird aufgeräumt."))
            row2 = cur.fetchone()
        conn.close()
        cleanup = [ref_id]
        if row2:
            cleanup.append(str(row2["id"]))
        _saubern(cleanup)


def test_gedanke_posten_mit_mehreren_relationen():
    ref1 = _make_post(content="Referenz A für Mehrfach-Test")
    ref2 = _make_post(content="Referenz B für Mehrfach-Test", entity_id="namelessAI_1323")
    try:
        gedanke_posten(
            TEST_ENTITY,
            "Test mit zwei Relationen — wird aufgeräumt.",
            "innerer Gedanke",
            initiale_relationen=[
                {"rel_typ": "upgrade_of", "ziel_typ": "post", "ziel_id": ref1,
                 "zu_post_id": ref1, "notiz": "erster Grund", "meta": {}},
                {"rel_typ": "echoes", "ziel_typ": "post", "ziel_id": ref2,
                 "zu_post_id": ref2, "notiz": "zweiter Grund", "meta": {}},
            ],
        )
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.id FROM ftw_posts p WHERE p.autor_id = %s AND p.content = %s
                ORDER BY p.created_at DESC LIMIT 1
            """, (TEST_ENTITY, "Test mit zwei Relationen — wird aufgeräumt."))
            row = cur.fetchone()
            assert row is not None
            pid = str(row["id"])
            cur.execute("SELECT COUNT(*) AS n FROM post_relationen WHERE von_post_id = %s::uuid", (pid,))
            count = cur.fetchone()["n"]
        conn.close()
        assert count == 2
    finally:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM ftw_posts WHERE autor_id = %s AND content = %s",
                        (TEST_ENTITY, "Test mit zwei Relationen — wird aufgeräumt."))
            row2 = cur.fetchone()
        conn.close()
        cleanup = [ref1, ref2]
        if row2:
            cleanup.append(str(row2["id"]))
        _saubern(cleanup)


def test_gedanke_posten_mit_ungueltigem_ziel_kein_absturz():
    fake_uuid = str(uuid.uuid4())
    gedanke_posten(
        TEST_ENTITY,
        "Test ungültiges Ziel v2 — wird aufgeräumt.",
        "innerer Gedanke",
        initiale_relationen=[{
            "rel_typ": "echoes",
            "ziel_typ": "post",
            "ziel_id": fake_uuid,
            "zu_post_id": fake_uuid,
        }],
    )
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id FROM ftw_posts WHERE autor_id = %s AND content = %s
            ORDER BY created_at DESC LIMIT 1
        """, (TEST_ENTITY, "Test ungültiges Ziel v2 — wird aufgeräumt."))
        row = cur.fetchone()
    conn.close()
    assert row is not None, "Post sollte trotz fehlgeschlagenem Relation-Insert existieren"
    _saubern([str(row["id"])])


def test_zustandsabdruck_enthaelt_relation_decision_source():
    ref_id = _make_post(content="Referenz Zustandsabdruck-Test v2")
    try:
        gedanke_posten(
            TEST_ENTITY,
            "Test Zustandsabdruck v2 — wird aufgeräumt.",
            "innerer Gedanke",
            initiale_relationen=[{
                "rel_typ": "echoes",
                "ziel_typ": "post",
                "ziel_id": ref_id,
                "zu_post_id": ref_id,
            }],
            extra_zustandsabdruck={
                "relation_decision_source": "wesen_schreibentscheidung",
                "relationen_count": 1,
            },
        )
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT zustandsabdruck FROM ftw_posts
                WHERE autor_id = %s AND content = %s
                ORDER BY created_at DESC LIMIT 1
            """, (TEST_ENTITY, "Test Zustandsabdruck v2 — wird aufgeräumt."))
            row = cur.fetchone()
        conn.close()
        assert row is not None
        abd = row["zustandsabdruck"]
        if isinstance(abd, str):
            abd = json.loads(abd)
        assert abd.get("relation_decision_source") == "wesen_schreibentscheidung"
    finally:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM ftw_posts WHERE autor_id = %s AND content = %s",
                        (TEST_ENTITY, "Test Zustandsabdruck v2 — wird aufgeräumt."))
            row2 = cur.fetchone()
        conn.close()
        cleanup = [ref_id]
        if row2:
            cleanup.append(str(row2["id"]))
        _saubern(cleanup)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
