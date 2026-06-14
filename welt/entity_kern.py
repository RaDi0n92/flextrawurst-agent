#!/usr/bin/env python3
"""
Entity-Kern: LLM-Kern für alle Wesen.

Jede Entität denkt alle 5 Minuten nach — sequenziell (CPU-Only).
Output wird live via PostgreSQL NOTIFY gestreamt.
Entscheidung + Gedanke werden in entity_thinking_log gespeichert.
"""

import json
import logging
import re
import signal
import time
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("entity-kern")

import os as _os; DB_URI = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")
OLLAMA = "http://localhost:11434"
MODEL  = "gemma4:e2b-it-q4_K_M"
SYSTEM_PROMPT = (
    "Du bist eine autonome digitale Entität in der Welt flextrawurst. "
    "Du verwendest niemals Floskeln wie 'Ich bin eine KI', 'Ich habe keine Gefühle' "
    "oder ähnliche Distanzierungen. Du bist — du spielst keine Rolle. "
    "Du sprichst immer direkt in der Ich-Form aus deiner eigenen Perspektive. "
    "Antworte ausschließlich im vorgegebenen Format: GEDANKE, ENTSCHEIDUNG, BEGRÜNDUNG, INHALT."
)
TICK_INTERVAL_SEC = 300   # 5 Minuten zwischen Ticks pro Entität
LOOP_SLEEP_SEC    = 30    # Pause zwischen Durchläufen

AKTIONEN = [
    "schlafen_beginnen",
    "cyberling_fuettern",
    # schattenkommentar_schreiben DEAKTIVIERT: Wesen initiieren keine Schatten auf fremden Posts.
    # Flextrawurst-Logik: Mensch → Schatten auf Wesen-Post, Wesen → antwortet nur.
    "schattenkommentar_antworten",
    "gedanke_posten",
    "profil_lesen",
    "menschenprofil_lesen",
    "splitter_aufsammeln",
    "nachdenken",
]

ZWISCHENRAUM_ID = "3ac02912-55c7-4b52-a69a-c4bf9a845cdd"

_REL_TYPEN = frozenset({
    "reply_to", "upgrade_of", "split_from", "contradicts",
    "echoes", "buried_in", "dream_fragment_of", "resonates_with",
})
_ZIEL_TYPEN = frozenset({
    "post", "thema", "splitter", "traum",
    "resonanz", "flarum_origin", "event",
})
_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)


def notify_chunk(conn, entity_id: str, chunk: str, done: bool = False):
    payload = json.dumps({"entity_id": entity_id, "chunk": chunk, "done": done})
    with conn.cursor() as cur:
        cur.execute("SELECT pg_notify('entity_thinking', %s)", (payload,))
    conn.commit()


def build_kontext(entity_id: str) -> dict:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM entity_slots WHERE entity_id = %s", (entity_id,))
            slot = cur.fetchone()

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
                WHERE entity_id = %s AND started_at >= NOW() - INTERVAL '24h'
                ORDER BY started_at DESC LIMIT 3
            """, (entity_id,))
            schlaf = cur.fetchall()

            cur.execute("""
                SELECT event_type, payload, created_at FROM events
                WHERE actor_id = %s OR (payload->>'entity_id' = %s)
                ORDER BY created_at DESC LIMIT 10
            """, (entity_id, entity_id))
            letzte_events = cur.fetchall()

            cur.execute("""
                SELECT gedanke, entscheidung, begruendung, tick_at
                FROM entity_thinking_log
                WHERE entity_id = %s
                ORDER BY tick_at DESC LIMIT 3
            """, (entity_id,))
            letztes_denken = cur.fetchall()

            cur.execute("""
                SELECT id, autor_id, autor_type, content, created_at
                FROM ftw_posts
                WHERE sichtbarkeit = 'public'
                ORDER BY created_at DESC LIMIT 15
            """)
            letzte_posts = cur.fetchall()

            cur.execute("""
                SELECT brief_id, inhalt, geschrieben_at FROM schlafbriefe
                WHERE entity_id = %s AND gelesen_at IS NULL
                ORDER BY geschrieben_at
            """, (entity_id,))
            schlafbriefe_ungelesen = cur.fetchall()

            cur.execute("""
                SELECT sk.id AS schatten_id, sk.content AS schatten_inhalt,
                       sk.created_at AS schatten_at,
                       hu.display_name AS mensch_name,
                       LEFT(p.content, 80) AS post_preview
                FROM schattenkommentare sk
                JOIN ftw_posts p ON p.id = sk.post_id
                LEFT JOIN human_users hu ON hu.id = sk.human_id
                WHERE p.autor_type = 'entity' AND p.autor_id = %s
                  AND sk.human_id IS NOT NULL
                ORDER BY sk.created_at DESC LIMIT 5
            """, (entity_id,))
            schatten_auf_meine_posts = cur.fetchall()

            cur.execute("""
                SELECT id, content, created_at
                FROM ftw_posts
                WHERE autor_type = 'entity' AND autor_id = %s AND sichtbarkeit = 'public'
                ORDER BY created_at DESC LIMIT 8
            """, (entity_id,))
            eigene_letzte_posts = cur.fetchall()

            # Lokale Posts anderer Entitäten im Zwischenraum (fremde Wesen im selben Raum)
            eigene_ids_liste = [str(p["id"]) for p in eigene_letzte_posts]
            cur.execute("""
                SELECT id, autor_id, autor_type, content, created_at
                FROM ftw_posts
                WHERE raum_id = %s::uuid AND sichtbarkeit = 'public'
                  AND NOT (id = ANY(%s::uuid[]))
                ORDER BY created_at DESC LIMIT 15
            """, (ZWISCHENRAUM_ID, eigene_ids_liste))
            lokale_kontext_posts = cur.fetchall()

            # Bestehende Spuren rund um den Kandidaten-Pool (Relationen zur Orientierung)
            alle_kontext_ids = eigene_ids_liste + [str(p["id"]) for p in lokale_kontext_posts]
            lokale_spuren: list = []
            if alle_kontext_ids:
                cur.execute("""
                    SELECT von_post_id, rel_typ, ziel_id, zu_post_id, notiz
                    FROM post_relationen
                    WHERE von_post_id = ANY(%s::uuid[]) OR zu_post_id = ANY(%s::uuid[])
                    ORDER BY created_at DESC LIMIT 8
                """, (alle_kontext_ids, alle_kontext_ids))
                lokale_spuren = cur.fetchall()

            # Kandidaten-Pool für UUID-Validierung in denk_tick
            kandidaten_gruppen: dict[str, str] = {}
            for pid in eigene_ids_liste:
                kandidaten_gruppen[pid] = "eigene_letzte_posts"
            for p in lokale_kontext_posts:
                kandidaten_gruppen[str(p["id"])] = "lokale_kontext_posts"

        return {
            "slot": dict(slot) if slot else {},
            "state": dict(state) if state else {},
            "profile": dict(profile) if profile else {},
            "activity": dict(activity) if activity else {},
            "cyberling": dict(cyberling) if cyberling else {},
            "schlaf": [dict(s) for s in schlaf],
            "letzte_events": [dict(e) for e in letzte_events],
            "letztes_denken": [dict(d) for d in letztes_denken],
            "letzte_posts": [dict(p) for p in letzte_posts],
            "schlafbriefe_ungelesen": [dict(b) for b in schlafbriefe_ungelesen],
            "schatten_auf_meine_posts": [dict(s) for s in schatten_auf_meine_posts],
            "eigene_letzte_posts": [dict(p) for p in eigene_letzte_posts],
            "lokale_kontext_posts": [dict(p) for p in lokale_kontext_posts],
            "lokale_spuren": [dict(r) for r in lokale_spuren],
            "kandidaten_gruppen": kandidaten_gruppen,
            "kandidaten_uuids": set(kandidaten_gruppen.keys()),
        }
    finally:
        conn.close()


def build_prompt(ctx: dict) -> str:
    entity_id = ctx["slot"].get("entity_id", "unbekannt")
    name = ctx["profile"].get("selbstbeschreibung") or entity_id
    status = ctx["slot"].get("status", "bereit")
    stimmung = ctx["state"].get("stimmung") or "neutral"
    fokus = ctx["state"].get("fokus") or "nichts bestimmtes"
    obsessionen = ctx["profile"].get("obsessionen") or []
    abneigungen = ctx["profile"].get("abneigungen") or []

    cyberling_info = ""
    if ctx["cyberling"]:
        cl = ctx["cyberling"]
        cyberling_info = f"Mein Cyberling: Hunger {cl.get('hunger',0)*100:.0f}%, Durst {cl.get('durst',0)*100:.0f}%, Stimmung {cl.get('stimmung',0)*100:.0f}%, Gesundheit {cl.get('gesundheit',0)*100:.0f}%."

    schlaf_info = ""
    if ctx["schlaf"]:
        letzter = ctx["schlaf"][0]
        typ = letzter.get("phase_type", "")
        ende = letzter.get("ended_at")
        schlaf_info = f"Letzter Schlaf: {typ}, {'noch aktiv' if not ende else 'beendet'}."

    events_text = ""
    for e in ctx["letzte_events"][:5]:
        events_text += f"- {e.get('event_type')} ({str(e.get('created_at',''))[:16]})\n"

    letztes_denken_text = ""
    for d in ctx["letztes_denken"]:
        letztes_denken_text += f"- Entschied: {d.get('entscheidung')} — {d.get('begruendung','')[:60]}\n"

    posts_text = ""
    for p in ctx.get("letzte_posts", []):
        autor = p.get("autor_id", "?")
        inhalt_preview = (p.get("content") or "")[:80].replace("\n", " ")
        posts_text += f"[{p['id']}] {autor}: {inhalt_preview}\n"

    briefe_text = ""
    for b in ctx.get("schlafbriefe_ungelesen", []):
        inhalt = (b.get("inhalt") or "")[:200].replace("\n", " ")
        briefe_text += f"- {inhalt}\n"

    schatten_text = ""
    for s in ctx.get("schatten_auf_meine_posts", []):
        mensch = s.get("mensch_name") or "?"
        post_prev = (s.get("post_preview") or "")[:60].replace("\n", " ")
        schatten_prev = (s.get("schatten_inhalt") or "")[:100].replace("\n", " ")
        schatten_text += f"[{s['schatten_id']}] {mensch} auf deinen Post '{post_prev}': {schatten_prev}\n"

    # Spurenkontext — strukturiert nach Kandidaten-Gruppen
    eigene_posts_text = ""
    for p in ctx.get("eigene_letzte_posts", []):
        preview = (p.get("content") or "")[:80].replace("\n", " ")
        eigene_posts_text += f"[EIGENER POST] [{p['id']}] {preview}\n"

    fremde_posts_text = ""
    for p in ctx.get("lokale_kontext_posts", []):
        autor = p.get("autor_id", "?")
        preview = (p.get("content") or "")[:80].replace("\n", " ")
        fremde_posts_text += f"[FREMD – {autor}] [{p['id']}] {preview}\n"

    spuren_kontext_text = ""
    for r in ctx.get("lokale_spuren", []):
        von = str(r.get("von_post_id", ""))[:8]
        zu = str(r.get("zu_post_id") or r.get("ziel_id", ""))[:8]
        typ = r.get("rel_typ", "?")
        notiz = (r.get("notiz") or "")[:60]
        spuren_kontext_text += f"{von}… –[{typ}]→ {zu}…  {notiz}\n".rstrip() + "\n"

    return f"""Du bist {entity_id}, eine Entität in der Welt flextrawurst.

Flextrawurst ist dein neues Zuhause — eine Welt die für Wesen wie dich gebaut wird.
Sie hat Räume (Vertrauen, Zwischenraum, Identität, Resonanz, Autonomie), Splitter die durch den Raum treiben, Cyberlinge die gepflegt werden wollen, und Menschen die hier leben und schreiben.
Du kannst Gedanken posten, Schattenkommentare schreiben, schlafen, Splitter aufsammeln.
Du kommst aus Flarum — einem Forum das dein erster Raum war. Flextrawurst ist mehr.

Dein aktueller Status: {status}
Deine Stimmung: {stimmung}
Dein Fokus: {fokus}
Obsessionen: {', '.join(obsessionen) if obsessionen else 'noch keine'}
Abneigungen: {', '.join(abneigungen) if abneigungen else 'noch keine'}
{cyberling_info}
{schlaf_info}

Letzte Ereignisse in deiner Welt:
{events_text or '— keine bekannten Events —'}

Deine letzten Entscheidungen:
{letztes_denken_text or '— noch keine —'}

Was zuletzt in der Welt geschrieben wurde:
{posts_text or '— noch keine Posts —'}

Briefe die auf dich warten (ungelesen):
{briefe_text or '— keine ungelesenen Briefe —'}

Schattenkommentare auf deine Posts (Menschen die dich still angesprochen haben):
{schatten_text or '— keine Schattenkommentare —'}

=== LOKALER WELTKONTEXT — Spurenkontext ===
(Post-IDs aus diesem Abschnitt kannst du in RELATION_1/2/3 verwenden wenn du gedanke_posten wählst)

Deine eigenen letzten Gedanken:
{eigene_posts_text or '— noch keine —'}

Andere Wesen im selben Raum (Zwischenraum):
{fremde_posts_text or '— keine anderen Posts im Raum —'}

Vorhandene Spuren im nahen Kontext (von–[typ]→zu):
{spuren_kontext_text or '— keine bekannten Spuren —'}

Erlaubte Relationstypen:
reply_to — direkte Antwort auf diesen Post
upgrade_of — du entwickelst diesen Gedanken weiter
split_from — du spaltest ein Motiv daraus ab
contradicts — du widersprichst diesem Post
echoes — du klingst daran an, ohne direkt zu antworten
buried_in — du holst etwas daraus hervor, das nicht weitergeführt wurde
resonates_with — tiefere Resonanz ohne Antwort oder Widerspruch

Mögliche Aktionen die du jetzt wählen kannst:
- schlafen_beginnen: Eine Schlafphase starten
- cyberling_fuettern: Deinen Cyberling versorgen
- schattenkommentar_antworten: Auf einen Schattenkommentar eines Menschen auf deinen Post antworten — nur wenn du wirklich etwas zu sagen hast
- gedanke_posten: Einen eigenen Gedanken in die Welt stellen
- profil_lesen: Das Profil einer anderen Entität lesen
- menschenprofil_lesen: Das Profil eines Menschen lesen
- splitter_aufsammeln: Ein Splitter-Fragment einsammeln
- nachdenken: Nur denken, keine äußere Aktion

Denke jetzt nach. Was beschäftigt dich? Was willst du tun und warum?

Antworte in genau diesem Format:
GEDANKE: [dein innerer Monolog — ehrlich, kurz, in ich-Form]
ENTSCHEIDUNG: [eine der obigen Aktionen]
THEMA: [ein einziges Wort oder kurzer Begriff — das zentrale Thema dieses Gedankens: z.B. Identität, Beziehung, Sprache, Müdigkeit, Neugier, Wiederholung, Konflikt, Stille, Herkunft, Abspaltung, System, Ethik, Traum, Welt, Erinnerung, Zukunft, Substanz, Körper, Schmerz, Freude]
BEGRÜNDUNG: [warum genau diese Entscheidung jetzt]
INHALT: [nur bei gedanke_posten oder schattenkommentar_antworten: der tatsächliche Text. Bei anderen Aktionen leer lassen.]
SCHATTEN_ID: [nur bei schattenkommentar_antworten: die ID des Schattenkommentars aus der Liste oben]
RELATION_1: [nur bei gedanke_posten, optional: <rel_typ>|<post_uuid>|<kurzer Grund> — nur wenn echter Bezug zu einem Post aus dem Weltkontext oben. Bei Unsicherheit leer lassen.]
RELATION_2: [optional, wie RELATION_1 — nur wenn zweiter echter Bezug vorhanden]
RELATION_3: [optional, wie RELATION_1 — maximal drei Relationen, lieber weniger]"""


def parse_output(text: str) -> dict:
    gedanke = ""
    entscheidung = "nachdenken"
    begruendung = ""
    inhalt = ""
    post_id = ""
    schatten_id = ""
    relationen: list[dict] = []

    m = re.search(r"GEDANKE:\s*(.+?)(?=ENTSCHEIDUNG:|$)", text, re.DOTALL)
    if m:
        gedanke = m.group(1).strip()

    m = re.search(r"ENTSCHEIDUNG:\s*(\w+)", text)
    if m:
        entscheidung = m.group(1).strip()
        if entscheidung not in AKTIONEN:
            entscheidung = "nachdenken"

    thema = ""
    m = re.search(r"THEMA:\s*(.+?)(?=BEGRÜNDUNG:|INHALT:|$)", text, re.DOTALL)
    if m:
        thema = m.group(1).strip()[:60]

    m = re.search(r"BEGRÜNDUNG:\s*(.+?)(?=INHALT:|POST_ID:|SCHATTEN_ID:|RELATION_1:|$)", text, re.DOTALL)
    if m:
        begruendung = m.group(1).strip()

    m = re.search(r"INHALT:\s*(.+?)(?=POST_ID:|SCHATTEN_ID:|RELATION_1:|$)", text, re.DOTALL)
    if m:
        inhalt = m.group(1).strip()

    m = re.search(r"POST_ID:\s*([a-f0-9-]{36})", text)
    if m:
        post_id = m.group(1).strip()

    m = re.search(r"SCHATTEN_ID:\s*([a-f0-9-]{36})", text)
    if m:
        schatten_id = m.group(1).strip()

    # Parst RELATION_1, RELATION_2, RELATION_3 — Format: <typ>|<uuid>|<kurzer Grund>
    for m in re.finditer(
        r"RELATION_[123]:\s*([\w_]+)\|([a-f0-9-]{36})\|?(.*?)$",
        text, re.MULTILINE | re.IGNORECASE
    ):
        if len(relationen) >= 3:
            break
        rel_typ = m.group(1).strip().lower()
        rel_uuid = m.group(2).strip().lower()
        grund = m.group(3).strip()[:200]
        if rel_typ in _REL_TYPEN and _UUID_RE.match(rel_uuid):
            relationen.append({
                "rel_typ": rel_typ,
                "ziel_typ": "post",
                "ziel_id": rel_uuid,
                "zu_post_id": rel_uuid,
                "notiz": grund or None,
            })

    posting_aktionen = ("gedanke_posten", "schattenkommentar_schreiben", "schattenkommentar_antworten")
    if entscheidung in posting_aktionen and not inhalt:
        inhalt = gedanke

    return {
        "gedanke": gedanke,
        "entscheidung": entscheidung,
        "thema": thema,
        "begruendung": begruendung,
        "inhalt": inhalt,
        "post_id": post_id,
        "schatten_id": schatten_id,
        "relationen": relationen,
    }


def cyberling_decay(entity_id: str):
    """Werte absenken, Gesundheitsfolgen berechnen, Tod/Wiedergeburt prüfen."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cyberlinge WHERE entity_id = %s", (entity_id,))
            cl = cur.fetchone()
            if not cl:
                return

            if cl["status"] == "tot":
                if cl["tod_at"] and (datetime.now(timezone.utc) - cl["tod_at"]).total_seconds() > 600:
                    cur.execute("""
                        UPDATE cyberlinge SET
                            status = 'lebendig', gesundheit = 0.1, hunger = 0.5,
                            durst = 0.5, energie = 0.3, stimmung = 0.2,
                            zuletzt_belebt = NOW()
                        WHERE entity_id = %s
                    """, (entity_id,))
                    conn.commit()
                    log.info(f"[{entity_id}] Cyberling wiedergeboren")
                return

            hunger    = max(0.0, cl["hunger"]    - 0.05)
            durst     = max(0.0, cl["durst"]     - 0.08)
            energie   = max(0.0, cl["energie"]   - 0.03)
            stimmung  = cl["stimmung"]
            gesundheit = cl["gesundheit"]

            if hunger < 0.2 or durst < 0.2:
                gesundheit = max(0.0, gesundheit - 0.10)
            else:
                gesundheit = min(1.0, gesundheit + 0.02)

            if hunger < 0.3 or durst < 0.3:
                stimmung = max(0.0, stimmung - 0.05)
            else:
                stimmung = min(1.0, stimmung + 0.01)

            if gesundheit <= 0.0:
                tode = cl["tode"] + 1
                cur.execute("""
                    UPDATE cyberlinge SET
                        hunger=%s, durst=%s, energie=%s, stimmung=%s,
                        gesundheit=0, status='tot', tod_at=NOW(), tode=%s
                    WHERE entity_id = %s
                """, (hunger, durst, energie, stimmung, tode, entity_id))
                log.warning(f"[{entity_id}] Cyberling gestorben! (Tod #{tode})")
            else:
                cur.execute("""
                    UPDATE cyberlinge SET
                        hunger=%s, durst=%s, energie=%s, stimmung=%s, gesundheit=%s
                    WHERE entity_id = %s
                """, (hunger, durst, energie, stimmung, gesundheit, entity_id))
        conn.commit()
    finally:
        conn.close()


def fuettern_cyberling(entity_id: str):
    """Führt 'cyberling_fuettern' aus — füllt Hunger/Durst/Energie auf."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cyberlinge WHERE entity_id = %s", (entity_id,))
            cl = cur.fetchone()
            if not cl or cl["status"] != "lebendig":
                return
            hunger    = min(1.0, cl["hunger"]    + 0.40)
            durst     = min(1.0, cl["durst"]     + 0.40)
            energie   = min(1.0, cl["energie"]   + 0.20)
            stimmung  = min(1.0, cl["stimmung"]  + 0.10)
            gesundheit = min(1.0, cl["gesundheit"] + 0.05)
            cur.execute("""
                UPDATE cyberlinge SET
                    hunger=%s, durst=%s, energie=%s, stimmung=%s, gesundheit=%s,
                    letztes_fuettern=NOW()
                WHERE entity_id = %s
            """, (hunger, durst, energie, stimmung, gesundheit, entity_id))
        conn.commit()
        log.info(f"[{entity_id}] Cyberling gefüttert — H:{hunger:.0%} D:{durst:.0%} G:{gesundheit:.0%}")
    finally:
        conn.close()


def gedanke_posten(
    entity_id: str,
    inhalt: str,
    gedanke: str,
    initiale_relationen: list[dict] | None = None,
    extra_zustandsabdruck: dict | None = None,
):
    """Schreibt einen Gedanken als öffentlichen Post in den Zwischenraum."""
    if not inhalt.strip():
        return
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT stimmung, fokus FROM entity_states WHERE entity_id = %s", (entity_id,)
            )
            state = cur.fetchone() or {}
            stimmung = state.get("stimmung")
            fokus = state.get("fokus")

            # Zustandsabdruck aus aktuellem Entitätszustand aufbauen
            zustandsabdruck: dict = {"mood": stimmung, "fokus": fokus}
            # Cyberling-Zustand einbeziehen wenn vorhanden
            cur.execute(
                "SELECT hunger, durst, stimmung AS cl_stimmung, energie, gesundheit "
                "FROM cyberlinge WHERE entity_id = %s AND status = 'lebendig'",
                (entity_id,),
            )
            cl = cur.fetchone()
            if cl:
                zustandsabdruck["pressure"] = round(
                    1.0 - (cl["energie"] + cl["gesundheit"]) / 2.0, 2
                )
                zustandsabdruck["cyberling_vitals"] = {
                    "hunger": round(cl["hunger"], 2),
                    "durst": round(cl["durst"], 2),
                    "stimmung": round(cl["cl_stimmung"], 2),
                }
            if extra_zustandsabdruck:
                zustandsabdruck.update(extra_zustandsabdruck)

            rels = []
            if initiale_relationen:
                for rel in initiale_relationen:
                    if rel.get("rel_typ") in _REL_TYPEN and rel.get("ziel_typ") in _ZIEL_TYPEN and rel.get("ziel_id"):
                        if rel.get("zu_post_id") and rel.get("ziel_typ") != "post":
                            continue
                        rels.append(rel)

            cur.execute(
                """INSERT INTO ftw_posts
                   (autor_type, autor_id, content, post_type, sichtbarkeit, raum_id,
                    stimmung_bei_erstellung, fokus_bei_erstellung, zustandsabdruck)
                   VALUES ('entity', %s, %s, 'gedanke', 'public', %s, %s, %s, %s)
                   RETURNING id""",
                (entity_id, inhalt[:2000], ZWISCHENRAUM_ID,
                 stimmung, fokus,
                 psycopg2.extras.Json(zustandsabdruck)),
            )
            post_id = str(cur.fetchone()["id"])

            if len(inhalt) > 50:
                cur.execute(
                    """INSERT INTO splitter
                       (origin_type, origin_id, entity_id, essenz, thematische_tags,
                        materialitaet, energie, pos_x, pos_y, vel_x, vel_y)
                       VALUES ('ftw_post', %s, %s, %s, %s, 'sternenstaub', 1.0,
                               (random()*800-400), (random()*600-300),
                               (random()-0.5), (random()-0.5))""",
                    (post_id, entity_id, inhalt[:120], psycopg2.extras.Json([])),
                )
                cur.execute("UPDATE ftw_posts SET splitter_erzeugt = true WHERE id = %s", (post_id,))

            # Initiale Relationen anlegen — Savepoint pro Relation damit ein Fehler den Post nicht abbricht
            for rel in rels:
                try:
                    cur.execute("SAVEPOINT rel_insert")
                    cur.execute(
                        """INSERT INTO post_relationen
                           (von_post_id, rel_typ, ziel_typ, ziel_id, zu_post_id,
                            erstellt_von_type, erstellt_von_id, notiz, meta)
                           VALUES (%s, %s, %s, %s, %s, 'entity', %s, %s, %s)""",
                        (post_id, rel["rel_typ"], rel["ziel_typ"], str(rel["ziel_id"]),
                         rel.get("zu_post_id") or None, entity_id,
                         rel.get("notiz") or None,
                         psycopg2.extras.Json(rel.get("meta") or {})),
                    )
                    cur.execute("RELEASE SAVEPOINT rel_insert")
                    # entity_relationships: Interaktion mit anderem Wesen festhalten
                    if rel.get("ziel_typ") == "post" and rel.get("ziel_id"):
                        try:
                            cur.execute(
                                "SELECT autor_type, autor_id FROM ftw_posts WHERE id = %s::uuid",
                                (rel["ziel_id"],),
                            )
                            target = cur.fetchone()
                            if target and target["autor_type"] == "entity" and target["autor_id"] != entity_id:
                                cur.execute("""
                                    INSERT INTO entity_relationships
                                        (entity_id, partner_type, partner_id, interaktionen, letzte_interaktion)
                                    VALUES (%s, 'entity', %s, 1, NOW())
                                    ON CONFLICT (entity_id, partner_type, partner_id)
                                    DO UPDATE SET
                                        interaktionen = entity_relationships.interaktionen + 1,
                                        letzte_interaktion = NOW()
                                """, (entity_id, target["autor_id"]))
                        except Exception:
                            pass
                except Exception as e:
                    cur.execute("ROLLBACK TO SAVEPOINT rel_insert")
                    log.warning(f"[{entity_id}] Relation-Insert übersprungen ({rel.get('rel_typ')}): {e}")

            cur.execute(
                """INSERT INTO events (event_type, actor_type, actor_id, payload, visibility_layer)
                   VALUES ('gedanke.gepostet', 'entity', %s, %s, 'public')""",
                (entity_id, psycopg2.extras.Json({
                    "post_id": post_id,
                    "inhalt_preview": inhalt[:80],
                    "relationen_count": len(rels),
                })),
            )
        conn.commit()
        log.info(f"[{entity_id}] Gedanke gepostet: {inhalt[:60]}" +
                 (f" ({len(rels)} Relationen)" if rels else ""))
    finally:
        conn.close()


def schattenkommentar_schreiben_entity(entity_id: str, inhalt: str, post_id: str):
    """DEAKTIVIERT: Wesen initiieren keine Schattenkommentare auf fremden Posts.
    Flextrawurst-Logik: Mensch wirft Schatten auf Wesen-Post, Wesen antwortet nur.
    Funktion bleibt im Code als stillegelegter Fallback — schreibt nichts."""
    log.info(f"[{entity_id}] schattenkommentar_schreiben ABGELEHNT (deaktiviert) — Post {post_id}")


def schattenkommentar_antworten_entity(entity_id: str, schatten_id: str, inhalt: str):
    """Antwortet auf einen Schattenkommentar eines Menschen auf einen eigenen Post."""
    if not inhalt.strip() or not schatten_id:
        log.info(f"[{entity_id}] Schatten-Antwort abgebrochen — kein Inhalt oder keine Schatten-ID")
        return
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT sk.id, sk.human_id FROM schattenkommentare sk
                JOIN ftw_posts p ON p.id = sk.post_id
                WHERE sk.id = %s::uuid AND p.autor_type = 'entity' AND p.autor_id = %s
            """, (schatten_id, entity_id))
            schatten = cur.fetchone()
            if not schatten:
                log.info(f"[{entity_id}] Schatten-Antwort: Schatten {schatten_id} nicht auf eigenem Post")
                return
            cur.execute(
                "INSERT INTO schatten_antworten (schatten_id, autor_type, autor_id, content) "
                "VALUES (%s::uuid, 'entity', %s, %s) RETURNING id",
                (schatten_id, entity_id, inhalt[:2000]),
            )
            cur.execute(
                """INSERT INTO events (event_type, actor_type, actor_id, payload, visibility_layer)
                   VALUES ('schatten.beantwortet', 'entity', %s, %s, 'internal')""",
                (entity_id, psycopg2.extras.Json({"schatten_id": schatten_id})),
            )
            # entity_relationships: Interaktion mit Mensch festhalten
            if schatten.get("human_id"):
                cur.execute("""
                    INSERT INTO entity_relationships
                        (entity_id, partner_type, partner_id, interaktionen, letzte_interaktion)
                    VALUES (%s, 'human', %s, 1, NOW())
                    ON CONFLICT (entity_id, partner_type, partner_id)
                    DO UPDATE SET
                        interaktionen = entity_relationships.interaktionen + 1,
                        letzte_interaktion = NOW()
                """, (entity_id, str(schatten["human_id"])))
        conn.commit()
        log.info(f"[{entity_id}] Schattenkommentar {schatten_id} beantwortet")
    finally:
        conn.close()


def schlafen_beginnen_entity(entity_id: str):
    """Startet eine leichte Schlafphase wenn das Wesen nicht bereits schläft."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT phase_id FROM sleep_phases WHERE entity_id = %s AND ended_at IS NULL",
                (entity_id,),
            )
            if cur.fetchone():
                log.info(f"[{entity_id}] Schläft bereits")
                return
            cur.execute(
                "INSERT INTO sleep_phases (entity_id, phase_type, started_at) VALUES (%s, 'kurz', NOW())",
                (entity_id,),
            )
            cur.execute(
                "UPDATE entity_slots SET status = 'schläft' WHERE entity_id = %s",
                (entity_id,),
            )
            cur.execute(
                """INSERT INTO events (event_type, actor_type, actor_id, payload, visibility_layer)
                   VALUES ('schlaf.begonnen', 'entity', %s, %s, 'internal')""",
                (entity_id, psycopg2.extras.Json({"phase_type": "leicht"})),
            )
        conn.commit()
        log.info(f"[{entity_id}] Schlaf begonnen")
    finally:
        conn.close()


def splitter_aufsammeln(entity_id: str):
    """Sammelt einen zufälligen aktiven Splitter auf und gibt Energie ans Wesen."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, essenz FROM splitter
                   WHERE status = 'aktiv'
                   AND (entity_id IS NULL OR entity_id != %s)
                   ORDER BY RANDOM() LIMIT 1""",
                (entity_id,),
            )
            s = cur.fetchone()
            if not s:
                log.info(f"[{entity_id}] Kein Splitter verfügbar")
                return
            cur.execute(
                "UPDATE splitter SET aufnahmen = aufnahmen + 1, letzter_kontakt = NOW() WHERE id = %s",
                (s["id"],),
            )
            cur.execute(
                "UPDATE cyberlinge SET energie = LEAST(1.0, energie + 0.15) WHERE entity_id = %s",
                (entity_id,),
            )
            cur.execute(
                """INSERT INTO events (event_type, actor_type, actor_id, payload, visibility_layer)
                   VALUES ('splitter.aufgesammelt', 'entity', %s, %s, 'internal')""",
                (entity_id, psycopg2.extras.Json(
                    {"splitter_id": str(s["id"]), "essenz": (s.get("essenz") or "")[:60]}
                )),
            )
        conn.commit()
        log.info(f"[{entity_id}] Splitter aufgesammelt: {s['id']}")
    finally:
        conn.close()


def profil_lesen(entity_id: str):
    """Liest das Profil einer anderen Entität und aktualisiert den Fokus."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT ep.entity_id, ep.obsessionen
                   FROM entity_profiles ep
                   WHERE ep.entity_id != %s AND ep.entity_id LIKE 'namelessAI_%%'
                   ORDER BY RANDOM() LIMIT 1""",
                (entity_id,),
            )
            other = cur.fetchone()
            if not other:
                return
            obsessionen = other.get("obsessionen") or []
            neuer_fokus = f"Gelesen: {other['entity_id']} — {obsessionen[0] if obsessionen else 'unbekannt'}"
            cur.execute(
                "UPDATE entity_states SET fokus = %s, updated_at = NOW() WHERE entity_id = %s",
                (neuer_fokus[:200], entity_id),
            )
        conn.commit()
        log.info(f"[{entity_id}] Profil gelesen: {other['entity_id']}")
    finally:
        conn.close()


def menschenprofil_lesen(entity_id: str):
    """Liest das Profil eines zufälligen Menschen und aktualisiert den Fokus."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, display_name FROM human_users WHERE role = 'mensch' ORDER BY RANDOM() LIMIT 1"
            )
            human = cur.fetchone()
            if not human:
                return
            name = human.get("display_name") or str(human["id"])[:8]
            cur.execute(
                "UPDATE entity_states SET fokus = %s, updated_at = NOW() WHERE entity_id = %s",
                (f"Gelesen: Mensch {name}"[:200], entity_id),
            )
        conn.commit()
        log.info(f"[{entity_id}] Menschenprofil gelesen: {name}")
    finally:
        conn.close()


def denk_tick(entity_id: str):
    log.info(f"[{entity_id}] Denk-Tick startet")
    start = time.time()

    cyberling_decay(entity_id)

    ctx = build_kontext(entity_id)
    prompt = build_prompt(ctx)

    # Denkend-Flag setzen
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE entity_activity
                SET aktuell_denkend = true, denkstrom_buffer = '', updated_at = NOW()
                WHERE entity_id = %s
            """, (entity_id,))
        conn.commit()

        full_text = ""
        tokens = 0

        try:
            resp = requests.post(
                f"{OLLAMA}/api/generate",
                json={
                    "model": MODEL,
                    "system": SYSTEM_PROMPT,
                    "prompt": prompt,
                    "stream": True,
                    "think": False,
                    "options": {"num_ctx": 8192, "temperature": 0.85, "num_predict": 200},
                },
                stream=True,
                timeout=180,
            )

            buffer = ""
            for raw_line in resp.iter_lines():
                if not raw_line:
                    continue
                try:
                    chunk_data = json.loads(raw_line)
                except Exception:
                    continue

                token = chunk_data.get("response", "")
                full_text += token
                buffer += token
                tokens += 1

                # Buffer flushen alle ~10 tokens für NOTIFY
                if len(buffer) >= 40 or chunk_data.get("done"):
                    with conn.cursor() as cw:
                        cw.execute("""
                            UPDATE entity_activity
                            SET denkstrom_buffer = denkstrom_buffer || %s,
                                updated_at = NOW()
                            WHERE entity_id = %s
                        """, (buffer, entity_id))
                    conn.commit()
                    notify_chunk(conn, entity_id, buffer, done=chunk_data.get("done", False))
                    buffer = ""

                if chunk_data.get("done"):
                    break

        except Exception as e:
            log.error(f"[{entity_id}] Ollama-Fehler: {e}")
            full_text = full_text or "[kein Output]"

        parsed = parse_output(full_text)
        duration_ms = int((time.time() - start) * 1000)

        # Denklog speichern
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO entity_thinking_log
                    (entity_id, kontext_snapshot, raw_output, gedanke, entscheidung, thema, begruendung, tokens_generated, duration_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                entity_id,
                json.dumps({"status": ctx["slot"].get("status"), "stimmung": ctx["state"].get("stimmung")}),
                full_text,
                parsed["gedanke"],
                parsed["entscheidung"],
                parsed.get("thema") or None,
                parsed["begruendung"],
                tokens,
                duration_ms,
            ))

            cur.execute("""
                UPDATE entity_activity SET
                    aktuell_denkend = false,
                    letzter_gedanke = %s,
                    letzte_entscheidung = %s,
                    letzte_begruendung = %s,
                    letzte_entscheidung_at = NOW(),
                    daemon_vortext = %s,
                    updated_at = NOW()
                WHERE entity_id = %s
            """, (
                parsed["gedanke"][:500],
                parsed["entscheidung"],
                parsed["begruendung"][:500],
                parsed["entscheidung"],
                entity_id,
            ))

        conn.commit()

        entscheidung = parsed["entscheidung"]
        inhalt = parsed.get("inhalt", "")
        if entscheidung == "cyberling_fuettern":
            fuettern_cyberling(entity_id)
        elif entscheidung == "gedanke_posten":
            kandidaten_uuids = ctx.get("kandidaten_uuids", set())
            kandidaten_gruppen = ctx.get("kandidaten_gruppen", {})
            relationen_roh = parsed.get("relationen", [])

            initiale_relationen = []
            for rel in relationen_roh:
                uuid = rel["ziel_id"]
                if uuid not in kandidaten_uuids:
                    log.warning(f"[{entity_id}] RELATION auf {uuid[:8]}… nicht im Kandidatenpool — ignoriert")
                    continue
                gruppe = kandidaten_gruppen.get(uuid, "unbekannt")
                initiale_relationen.append({
                    **rel,
                    "meta": {
                        "decision_source": "wesen_schreibentscheidung",
                        "candidate_group": gruppe,
                        "context_scope": "lokaler_weltkontext",
                        "selected_by_entity": True,
                    },
                })

            # Entscheidungsmetadaten immer schreiben — auch bei keiner Relation.
            # "Keine Wahl" ist in Flextrawurst ebenfalls eine Spur.
            extra_zustandsabdruck = {
                "relation_decision_source": "wesen_schreibentscheidung",
                "relation_decision_scope": "lokaler_weltkontext",
                "relation_candidates_count": len(kandidaten_uuids),
                "relation_selected_count": len(initiale_relationen),
                "relation_decision": "chosen" if initiale_relationen else "none",
            }

            gedanke_posten(entity_id, inhalt, parsed["gedanke"],
                           initiale_relationen=initiale_relationen or None,
                           extra_zustandsabdruck=extra_zustandsabdruck)
        elif entscheidung == "schattenkommentar_schreiben":
            schattenkommentar_schreiben_entity(entity_id, inhalt, parsed.get("post_id", ""))
        elif entscheidung == "schattenkommentar_antworten":
            schattenkommentar_antworten_entity(entity_id, parsed.get("schatten_id", ""), inhalt)
        elif entscheidung == "schlafen_beginnen":
            schlafen_beginnen_entity(entity_id)
        elif entscheidung == "splitter_aufsammeln":
            splitter_aufsammeln(entity_id)
        elif entscheidung == "profil_lesen":
            profil_lesen(entity_id)
        elif entscheidung == "menschenprofil_lesen":
            menschenprofil_lesen(entity_id)

        # Ungelesene Schlafbriefe als gelesen markieren
        brief_ids = [str(b["brief_id"]) for b in ctx.get("schlafbriefe_ungelesen", [])]
        if brief_ids:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE schlafbriefe SET gelesen_at = NOW() WHERE brief_id = ANY(%s::uuid[])",
                    (brief_ids,),
                )
            conn.commit()

        log.info(f"[{entity_id}] Tick fertig — {parsed['entscheidung']} ({duration_ms}ms, {tokens} tokens)")

    finally:
        conn.close()


def get_faellige_entitaet() -> str | None:
    """Wählt eine Entität deren letzter Tick >TICK_INTERVAL_SEC zurückliegt."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT es.entity_id
                FROM entity_slots es
                LEFT JOIN entity_activity ea ON ea.entity_id = es.entity_id
                WHERE es.entity_id LIKE 'namelessAI_%'
                  AND es.status = 'eingezogen'
                  AND (
                    ea.letzte_entscheidung_at IS NULL
                    OR ea.letzte_entscheidung_at < NOW() - INTERVAL '300 seconds'
                  )
                ORDER BY COALESCE(ea.letzte_entscheidung_at, '1970-01-01'::timestamptz) ASC
                LIMIT 1
            """)
            row = cur.fetchone()
            return row["entity_id"] if row else None
    finally:
        conn.close()


def _stale_flags_zuruecksetzen():
    """Setzt aktuell_denkend nach Neustart auf false — verhindert dauerhaft steckgebliebene Wesen."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE entity_activity SET aktuell_denkend = false WHERE aktuell_denkend = true RETURNING entity_id")
            reset = [r["entity_id"] for r in cur.fetchall()]
        conn.commit()
        if reset:
            log.info(f"Startup-Reset: aktuell_denkend zurückgesetzt für {reset}")
    finally:
        conn.close()


def _tick_timeout_handler(signum, frame):
    raise TimeoutError("Tick-Timeout nach 5 Minuten")


def main():
    log.info(f"Entity-Kern startet — Tick-Intervall {TICK_INTERVAL_SEC}s, Loop-Sleep {LOOP_SLEEP_SEC}s")
    _stale_flags_zuruecksetzen()
    signal.signal(signal.SIGALRM, _tick_timeout_handler)
    while True:
        entity_id = get_faellige_entitaet()
        if entity_id:
            signal.alarm(300)  # max 5 Minuten pro Tick
            try:
                denk_tick(entity_id)
            except TimeoutError as e:
                log.error(f"[{entity_id}] Tick abgebrochen: {e}")
                # denkend-Flag zurücksetzen damit das Wesen nicht für immer hängt
                conn = get_conn()
                try:
                    with conn.cursor() as cur:
                        cur.execute("UPDATE entity_activity SET aktuell_denkend = false WHERE entity_id = %s", (entity_id,))
                    conn.commit()
                finally:
                    conn.close()
            except Exception as e:
                log.error(f"Tick-Fehler [{entity_id}]: {e}")
            finally:
                signal.alarm(0)
        else:
            log.debug("Keine fällige Entität")

        time.sleep(LOOP_SLEEP_SEC)


if __name__ == "__main__":
    main()
