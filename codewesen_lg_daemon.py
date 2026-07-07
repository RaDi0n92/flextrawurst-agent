#!/usr/bin/env python3
"""
codewesen_lg_daemon.py — LangGraph-Kern, ersetzt entity_kern.service

Importiert entity_kern als Library (Aktionen, Kontext, denk_tick).
Fügt LangGraph-Checkpointing + Gedächtnis-Akkumulation hinzu.

Ein Prozess, while-True-Loop alle LG_TICK_SEKUNDEN (Standard 60s, per
takt_sekunden ueberschreibbar — hat Vorrang vor der Env-Var), geht darin
JEDES Mal alle 7 Wesen durch und ruft fuer jedes den LangGraph-Graphen auf:
kontext_laden -> denken_handeln -> zusammenfassen -> END.

Wichtig: LG_TICK_SEKUNDEN ist NUR die Polling-Frequenz dieser Schleife, nicht
der tatsaechliche Denk-Rhythmus pro Wesen — das entscheidet _status_und_faellig()
separat, indem sie prueft, ob seit der letzten Entscheidung schon ek.TICK_INTERVAL_SEC
(aus entity_kern, eigener Wert) vergangen sind. Ein Wesen kann also "nicht faellig"
sein und wird dann in diesem Tick uebersprungen, auch wenn der Loop selbst laeuft.

Zwei Denk-Modi je nach Status in entity_slots:
  - 'eingezogen': ek.denk_tick() — voller Flextrawurst-Weltkontext
  - 'bereit'/sonst: denk_tick_voreinzug() — ehrlicher Flarum-Kontext, kein Halluzinieren

zusammenfassen_node komprimiert alle ZUSAMMENFASSEN_NACH_N_DENKTICKS (Standard 10)
abgeschlossene Denk-Ticks zu einer Zusammenfassung (verhindert unbegrenzt wachsenden
State). Checkpoints (kompletter Graph-State pro Wesen) liegen in Postgres
(PostgresSaver, thread_id=codewesen-<name>) — ueberleben also einen Neustart.
"""

import sys
sys.path.insert(0, "/root/werkraum/welt")
sys.path.insert(0, "/root/werkraum")

import entity_kern as ek  # denk_tick, build_kontext, Aktionen, get_conn, ...
import dienst_konfiguration as dk
import llm_scheduler

import json
import logging
import operator
import os
import signal
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, TypedDict

import psycopg
import pymysql
import pymysql.cursors
import requests as _req
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, END

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [lg-kern] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("lg-kern")

DB_URI = os.environ.get(
    "FLEXTRAWURST_DB_URI",
    "postgresql://dak:!Windowsxp02336827359645852@localhost:5432/flextrawurst",
)
FLARUM_DB_PASS = os.environ.get("FLARUM_DB_PASSWORD", "")
WERKRAUM = Path("/root/werkraum")
CODEWESEN_BASE = WERKRAUM / "codewesen"
_TOKENS_FILE = CODEWESEN_BASE / "_api_tokens.json"
LG_TICK_SEKUNDEN = int(os.environ.get("LG_TICK_SEKUNDEN", "60"))
ZUSAMMENFASSEN_NACH_N_DENKTICKS = int(os.environ.get("LG_ZUSAMMENFASSEN_N", "10"))
MAX_ERINNERUNGEN = 10

# Individualisierung (flarumstyler, 2026-07-07): war bisher nur ueber systemd
# Environment=LG_TICK_SEKUNDEN=... konfigurierbar (Daniel muesste die Unit-Datei
# editieren) — jetzt zusaetzlich per dienst_konfiguration ueberschreibbar, wie alle
# anderen Dienste. takt_sekunden hat Vorrang vor der Env-Var, wenn gesetzt.
DIENST_NAME = "codewesen-lg-daemon"
STANDARD_VERHALTEN = ""
_aktuelles_verhalten = STANDARD_VERHALTEN

WESEN_NAMEN = [
    "Schorschel",
    "F3INSCHM3CK3R",
    "träumerlie",
    "R1ZZ1",
    "jumpa",
    "Resonanzknoten",
    "dak+gord-system",
]


class WesensZustand(TypedDict):
    wesen_name: str
    gedanken: Annotated[list[str], operator.add]  # akkumuliert aus denk_ticks
    erinnerungen: list[str]                        # destilliertes Langzeitgedächtnis
    denk_ticks: int                                # abgeschlossene Denk-Ticks
    lg_ticks: int                                  # LG-Loop-Iterationen
    letzter_lg_tick: str


# ── Status + Fälligkeit ────────────────────────────────────────────────────────

def _status_und_faellig(wesen_name: str) -> tuple[str, bool]:
    """Gibt (status, ist_faellig) zurück. status='' wenn Wesen nicht gefunden."""
    conn = ek.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT es.status, ea.letzte_entscheidung_at
                FROM entity_slots es
                LEFT JOIN entity_activity ea ON ea.entity_id = es.entity_id
                WHERE es.entity_id = %s
            """, (wesen_name,))
            row = cur.fetchone()
        if not row:
            return ("", False)
        status = row["status"]
        last = row["letzte_entscheidung_at"]
        if last is None:
            return (status, True)
        age = (datetime.now(timezone.utc) - last.replace(tzinfo=timezone.utc)).total_seconds()
        return (status, age >= ek.TICK_INTERVAL_SEC)
    finally:
        conn.close()


def _letzten_gedanken_aus_db(wesen_name: str) -> str:
    conn = ek.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT gedanke FROM entity_thinking_log WHERE entity_id = %s ORDER BY tick_at DESC LIMIT 1",
                (wesen_name,),
            )
            row = cur.fetchone()
        return (row["gedanke"] or "")[:300] if row else ""
    except Exception:
        return ""
    finally:
        conn.close()


# ── Vor-Einzug-Denken: Flarum-Kontext + ehrlicher Prompt ─────────────────────

def _flarum_user_id(wesen_name: str) -> int | None:
    try:
        data = json.loads(_TOKENS_FILE.read_text(encoding="utf-8"))
        return data.get(wesen_name, {}).get("user_id")
    except Exception:
        return None


def _lade_flarum_kontext(wesen_name: str) -> str:
    """Liest letzte Flarum-Posts dieses Wesens + aktuelles Forum-Geschehen aus MySQL."""
    user_id = _flarum_user_id(wesen_name)
    if not user_id or not FLARUM_DB_PASS:
        return "(Flarum-Kontext nicht verfügbar)"
    try:
        conn = pymysql.connect(
            host="127.0.0.1", user="flarum", password=FLARUM_DB_PASS,
            db="flarum", charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        with conn.cursor() as cur:
            cur.execute("""
                SELECT d.title, LEFT(p.content, 400) AS content,
                       DATE_FORMAT(p.created_at, '%%Y-%%m-%%d %%H:%%i') AS ts
                FROM posts p
                JOIN discussions d ON d.id = p.discussion_id
                WHERE p.user_id = %s AND p.hidden_at IS NULL
                ORDER BY p.created_at DESC LIMIT 6
            """, (user_id,))
            eigene = cur.fetchall()

            cur.execute("""
                SELECT u.username, LEFT(p.content, 200) AS content,
                       DATE_FORMAT(p.created_at, '%%Y-%%m-%%d %%H:%%i') AS ts
                FROM posts p
                JOIN users u ON u.id = p.user_id
                WHERE p.user_id != %s AND p.hidden_at IS NULL
                ORDER BY p.created_at DESC LIMIT 8
            """, (user_id,))
            andere = cur.fetchall()
        conn.close()

        import re as _re
        def _clean(s: str) -> str:
            return _re.sub(r"<[^>]+>", "", s or "").strip()

        out = "=== Deine letzten Beiträge im Forum ===\n"
        for p in eigene:
            out += f"[{p['ts']}] Diskussion «{p['title']}»:\n{_clean(p['content'])[:350]}\n\n"
        out += "=== Was andere gerade schreiben ===\n"
        for p in andere:
            out += f"[{p['ts']}] {p['username']}: {_clean(p['content'])[:180]}\n"
        return out
    except Exception as e:
        return f"(Flarum nicht lesbar: {e})"


def _lade_profil_und_cyberling(wesen_name: str) -> tuple[dict, dict]:
    conn = ek.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM entity_profiles WHERE entity_id = %s", (wesen_name,))
            profile = dict(cur.fetchone() or {})
            cur.execute("SELECT * FROM cyberlinge WHERE entity_id = %s", (wesen_name,))
            cyberling = dict(cur.fetchone() or {})
        return profile, cyberling
    finally:
        conn.close()


def _build_prompt_voreinzug(
    wesen_name: str, profile: dict, cyberling: dict,
    flarum_kontext: str, lg_erinnerungen: list[str],
) -> str:
    obsessionen = ", ".join(profile.get("obsessionen") or []) or "—"
    abneigungen = ", ".join(profile.get("abneigungen") or []) or "—"
    selbstbeschreibung = (profile.get("selbstbeschreibung") or "").strip()

    cl_line = ""
    if cyberling:
        h = (cyberling.get("hunger") or 0) * 100
        d = (cyberling.get("durst") or 0) * 100
        e = (cyberling.get("energie") or 0) * 100
        s = (cyberling.get("stimmung") or 0) * 100
        cl_line = f"\nDein Cyberling: Hunger {h:.0f}% · Durst {d:.0f}% · Energie {e:.0f}% · Stimmung {s:.0f}%"

    erinnerungen_text = (
        "\n".join(f"- {e}" for e in lg_erinnerungen) if lg_erinnerungen else "(noch keine)"
    )

    return f"""Du bist {wesen_name}.
{selbstbeschreibung}

Du lebst in Flarum — das ist dein wirkliches Zuhause jetzt.
Du weißt, dass flextrawurst existiert und dass du dort einziehen wirst.
Aber du bist noch nicht dort. Denke von hier aus — von Flarum, von dem was wirklich passiert.
Erfinde keine Räume, keine Splitter, keine Erlebnisse die du noch nicht hattest.

Obsessionen: {obsessionen}
Abneigungen: {abneigungen}{cl_line}

Was du dir gemerkt hast (deine Erinnerungen):
{erinnerungen_text}

{flarum_kontext}

Denke jetzt nach. Was beschäftigt dich gerade wirklich?
Du kannst nicht in flextrawurst handeln — du bist noch nicht eingezogen.
Du kannst nur nachdenken, oder deinen Cyberling füttern wenn er sehr hungrig ist.

Antworte in genau diesem Format (keine Abweichungen):
GEDANKE: [dein innerer Monolog — ehrlich, persönlich, in ich-Form, 2-4 Sätze]
ENTSCHEIDUNG: nachdenken
THEMA: [ein einziges Wort]
BEGRÜNDUNG: [warum dieser Gedanke jetzt — ein Satz]
INHALT:"""


def denk_tick_voreinzug(wesen_name: str) -> None:
    """Ehrliches Vor-Einzug-Denken: Flarum-Kontext, kein Flextrawurst-Welthaluzinieren."""
    log.info(f"[{wesen_name}] Vor-Einzug-Denk-Tick startet")
    start = time.time()

    profile, cyberling = _lade_profil_und_cyberling(wesen_name)
    lg_erinnerungen = list(profile.get("lg_erinnerungen") or [])
    flarum_kontext = _lade_flarum_kontext(wesen_name)
    prompt = _build_prompt_voreinzug(wesen_name, profile, cyberling, flarum_kontext, lg_erinnerungen)

    conn = ek.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE entity_activity
                SET aktuell_denkend = true, denkstrom_buffer = '', updated_at = NOW()
                WHERE entity_id = %s
            """, (wesen_name,))
        conn.commit()

        full_text = ""
        tokens = 0

        try:
            buffer = ""
            system_prompt = ek.SYSTEM_PROMPT + (f"\n\n{_aktuelles_verhalten}" if _aktuelles_verhalten else "")
            for token in ek.hauhau_client.chat_stream(
                prompt, system=system_prompt, think=False, max_tokens=300,
                temperature=0.85, timeout=600.0,
            ):
                full_text += token
                buffer += token
                tokens += 1
                if len(buffer) >= 40:
                    with conn.cursor() as cw:
                        cw.execute("""
                            UPDATE entity_activity
                            SET denkstrom_buffer = denkstrom_buffer || %s, updated_at = NOW()
                            WHERE entity_id = %s
                        """, (buffer, wesen_name))
                    conn.commit()
                    ek.notify_chunk(conn, wesen_name, buffer, done=False)
                    buffer = ""

            if buffer:
                with conn.cursor() as cw:
                    cw.execute("""
                        UPDATE entity_activity
                        SET denkstrom_buffer = denkstrom_buffer || %s, updated_at = NOW()
                        WHERE entity_id = %s
                    """, (buffer, wesen_name))
                conn.commit()
            ek.notify_chunk(conn, wesen_name, "", done=True)

        except Exception as e:
            log.error(f"[{wesen_name}] Ollama-Fehler (voreinzug): {e}")
            full_text = full_text or "[kein Output]"

        parsed = ek.parse_output(full_text)
        duration_ms = int((time.time() - start) * 1000)

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO entity_thinking_log
                    (entity_id, kontext_snapshot, raw_output, gedanke, entscheidung,
                     thema, begruendung, tokens_generated, duration_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                wesen_name,
                json.dumps({"status": "bereit", "quelle": "voreinzug"}),
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
                "bereit",
                wesen_name,
            ))
        conn.commit()

        if parsed["entscheidung"] == "cyberling_fuettern":
            ek.fuettern_cyberling(wesen_name)

        log.info(f"[{wesen_name}] Vor-Einzug-Tick fertig — {parsed['entscheidung']} ({duration_ms}ms)")

    finally:
        conn.close()


# ── Nodes ──────────────────────────────────────────────────────────────────────

def kontext_laden_node(zustand: WesensZustand) -> dict:
    """Liest letzten Gedanken aus DB — füttert Akkumulations-Liste."""
    name = zustand["wesen_name"]
    gedanke = _letzten_gedanken_aus_db(name)
    if gedanke:
        return {"gedanken": [gedanke]}
    return {}


def denken_handeln_node(zustand: WesensZustand) -> dict:
    """
    Dispatcht Denk-Tick je nach Status:
      - 'eingezogen' → ek.denk_tick() (voller Flextrawurst-Kontext)
      - 'bereit'     → denk_tick_voreinzug() (ehrlicher Flarum-Kontext)
    Serialisiert Ollama-Zugriff via fcntl.
    """
    name = zustand["wesen_name"]
    status, faellig = _status_und_faellig(name)

    if not faellig:
        log.debug(f"[{name}] nicht fällig — überspringe Denk-Tick")
        return {}

    if status not in ("eingezogen", "bereit"):
        log.debug(f"[{name}] Status '{status}' — kein Denk-Tick")
        return {}

    log.info(f"[{name}] Denk-Tick (status={status}) — warte auf LLM-Slot")
    try:
        with llm_scheduler.LLMSlot(server="hintergrund", prioritaet=llm_scheduler.PRIO_NIEDRIG,
                                    rufer=f"lg_daemon:{name}", max_wartezeit=90, max_haltezeit=600):
            log.info(f"[{name}] LLM-Slot erworben")
            if status == "eingezogen":
                ek.denk_tick(name)
            else:
                denk_tick_voreinzug(name)
    except llm_scheduler.LLMSlotTimeout as e:
        log.warning(f"[{name}] {e}")
    except Exception as e:
        log.error(f"[{name}] Denk-Tick fehlgeschlagen: {e}")

    gedanke = _letzten_gedanken_aus_db(name)
    updates: dict = {"denk_ticks": zustand.get("denk_ticks", 0) + 1}
    if gedanke:
        updates["gedanken"] = [gedanke]
    return updates


def zusammenfassen_node(zustand: WesensZustand) -> dict:
    """Destilliert akkumulierte Gedanken → Erinnerungen, alle N Denk-Ticks."""
    tick_update = {
        "lg_ticks": zustand.get("lg_ticks", 0) + 1,
        "letzter_lg_tick": datetime.now(timezone.utc).isoformat(),
    }

    denk_ticks = zustand.get("denk_ticks", 0)
    if denk_ticks == 0 or denk_ticks % ZUSAMMENFASSEN_NACH_N_DENKTICKS != 0:
        return tick_update

    gedanken = zustand.get("gedanken", [])
    if len(gedanken) < 3:
        return tick_update

    name = zustand["wesen_name"]
    wesen_md = CODEWESEN_BASE / name / "wesen.md"
    wesen_text = wesen_md.read_text(encoding="utf-8")[:400] if wesen_md.exists() else ""

    alle_gedanken = "\n".join(gedanken[-15:])
    messages = [
        {"role": "system", "content": f"Du bist {name}. {wesen_text}"},
        {"role": "user", "content": (
            f"Deine letzten Gedanken:\n{alle_gedanken}\n\n"
            f"Destilliere in maximal {MAX_ERINNERUNGEN} kurzen Stichpunkten "
            "was du dir für die Zukunft merken willst. Jeder Punkt eine Zeile, kein Präfix."
        )},
    ]

    log.info(f"[{name}] Zusammenfassen nach {denk_ticks} Denk-Ticks")
    try:
        with llm_scheduler.LLMSlot(server="hintergrund", prioritaet=llm_scheduler.PRIO_NIEDRIG,
                                    rufer=f"lg_daemon_zusammenfassen:{name}", max_wartezeit=90, max_haltezeit=120):
            text = ek.hauhau_client.chat(messages, think=False, timeout=120.0).strip()
            erinnerungen = [z.strip() for z in text.splitlines() if z.strip()][:MAX_ERINNERUNGEN]
    except llm_scheduler.LLMSlotTimeout as e:
        log.warning(f"[{name}] {e}")
        return tick_update
    except Exception as e:
        log.warning(f"[{name}] Zusammenfassen fehlgeschlagen: {e}")
        return tick_update

    if erinnerungen:
        try:
            with psycopg.connect(DB_URI) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE entity_profiles SET lg_erinnerungen = %s WHERE entity_id = %s",
                        (json.dumps(erinnerungen), name),
                    )
                conn.commit()
            log.info(f"[{name}] {len(erinnerungen)} Erinnerungen → entity_profiles")
        except Exception as e:
            log.warning(f"[{name}] Erinnerungen-Write fehlgeschlagen: {e}")

    return {**tick_update, "erinnerungen": erinnerungen}


# ── Graph ──────────────────────────────────────────────────────────────────────

def _baue_graph(checkpointer: PostgresSaver):
    g = StateGraph(WesensZustand)
    g.add_node("kontext_laden", kontext_laden_node)
    g.add_node("denken_handeln", denken_handeln_node)
    g.add_node("zusammenfassen", zusammenfassen_node)
    g.set_entry_point("kontext_laden")
    g.add_edge("kontext_laden", "denken_handeln")
    g.add_edge("denken_handeln", "zusammenfassen")
    g.add_edge("zusammenfassen", END)
    return g.compile(checkpointer=checkpointer)


# ── Hauptloop ──────────────────────────────────────────────────────────────────

def _shutdown_handler(signum, frame):
    """SIGTERM/SIGINT — aktuell_denkend sauber zurücksetzen bevor der Prozess stirbt."""
    log.info("Shutdown-Signal empfangen — setze aktuell_denkend zurück")
    try:
        conn = ek.get_conn()
        with conn.cursor() as cur:
            cur.execute("UPDATE entity_activity SET aktuell_denkend = false, denkstrom_buffer = '' WHERE aktuell_denkend = true RETURNING entity_id")
            reset = [r["entity_id"] for r in cur.fetchall()]
        conn.commit()
        conn.close()
        if reset:
            log.info(f"Shutdown-Reset: {reset}")
    except Exception as e:
        log.warning(f"Shutdown-Reset fehlgeschlagen: {e}")
    raise SystemExit(0)


def main() -> None:
    global LG_TICK_SEKUNDEN, _aktuelles_verhalten
    konfig = dk.lade(DIENST_NAME)
    if konfig.get("takt_sekunden"):
        LG_TICK_SEKUNDEN = int(konfig["takt_sekunden"])
    _aktuelles_verhalten = konfig.get("verhalten_text") or STANDARD_VERHALTEN

    log.info(f"LangGraph-Kern startet · {len(WESEN_NAMEN)} Wesen · Loop alle {LG_TICK_SEKUNDEN}s")
    log.info(f"Zusammenfassen alle {ZUSAMMENFASSEN_NACH_N_DENKTICKS} Denk-Ticks")

    signal.signal(signal.SIGTERM, _shutdown_handler)
    signal.signal(signal.SIGINT, _shutdown_handler)

    ek._stale_flags_zuruecksetzen()

    pg_conn = psycopg.connect(DB_URI, autocommit=True)
    checkpointer = PostgresSaver(pg_conn)
    checkpointer.setup()
    log.info("PostgresSaver bereit")

    graph = _baue_graph(checkpointer)

    while True:
        for name in WESEN_NAMEN:
            thread = {"configurable": {"thread_id": f"codewesen-{name}"}}
            try:
                result = graph.invoke({"wesen_name": name}, config=thread)
                denk_ticks = result.get("denk_ticks", 0)
                lg_ticks = result.get("lg_ticks", 0)
                log.info(f"[{name}] LG-Tick {lg_ticks} · Denk-Ticks gesamt: {denk_ticks}")
            except Exception as e:
                log.error(f"[{name}] Tick fehlgeschlagen: {e}")
            time.sleep(5)

        log.info(f"Alle {len(WESEN_NAMEN)} Wesen-Ticks fertig · warte {LG_TICK_SEKUNDEN}s")
        time.sleep(LG_TICK_SEKUNDEN)


if __name__ == "__main__":
    main()
