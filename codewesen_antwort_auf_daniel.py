#!/usr/bin/env python3
"""
Daemon: Codewesen antworten auf Daniels Posts.

Alle 5 Minuten (Standard, per takt_sekunden ueberschreibbar): sucht alle
Posts von Admin (user_id=1) von HEUTE, die noch nicht verarbeitet wurden
(_global/daniel_posts_processed.json) und in denen noch kein Codewesen
NACH Daniels Post geantwortet hat. Vokabel-Threads werden ausgenommen
(dort antwortet codewesen_vokabel_takt.py).

Wuerfel-Logik ist NICHT einheitlich, wie der Name vermuten laesst:
  - Eroeffnungspost (post_number == 1): JEDES der 7 Wesen antwortet garantiert,
    kein Wuerfel.
  - Antwortpost (post_number > 1): pro Wesen 66% Chance zu antworten
    (random.random() > 0.66 => uebersprungen, sonst antwortet es).

Bearbeitung ist synchron pro Post: geht alle 7 Wesen der Reihe nach durch,
je 8 Sekunden Pause nach einem tatsaechlichen Post. LLM-Anfragen laufen mit
PRIO_HOCH (hoechste Prioritaet im gemeinsamen "hintergrund"-Slot) — direkte
Reaktion auf Daniel geht vor Hintergrund-Content wie dem Batch-Generator.
"""
import json
import logging
import os
import random
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, "/root/werkraum")

import pymysql
import pymysql.cursors
import flarum_api

sys.path.insert(0, "/root/werkraum")
import hauhau_client
import dienst_konfiguration as dk
import llm_scheduler
from flarum_vokabel_filter import ist_vokabel_thread

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [daniel-reaktion] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("daniel-reaktion")

DANIEL_USER_ID = 1
# Flarum-Usernamen wie sie wirklich in der DB stehen
WESEN = [
    "namelessAI_1111_1234",
    "namelessAI_2222_1324",
    "namelessAI_3333_1423",
    "namelessAI_4444_2341",
    "namelessAI_5555_3123",
    "Resonanzknoten",
    "dak-gord-system",
]
# Kurznamen für wesen.md-Pfad
WESEN_KURZ = {
    "namelessAI_1111_1234": "Schorschel",
    "namelessAI_2222_1324": "F3INSCHM3CK3R",
    "namelessAI_3333_1423": "träumerlie",
    "namelessAI_4444_2341": "R1ZZ1",
    "namelessAI_5555_3123": "jumpa",
    "Resonanzknoten": "Resonanzknoten",
    "dak-gord-system": "dak+gord-system",
}
CODEWESEN_BASE = Path("/root/werkraum/codewesen")
PROCESSED_FILE = CODEWESEN_BASE / "_global" / "daniel_posts_processed.json"
POLL_INTERVAL = 300
MODEL = "hauhaucs-q6"
ANTWORT_CHANCE_NORMALER_POST = 0.72
_STANDARD_TAG_IDS: list[int] | None = None

# Individualisierung (flarumstyler, 2026-07-07): Takt+Verhalten ueberschreibbar aus dienst_konfiguration.
DIENST_NAME = "codewesen-antwort-daniel"
STANDARD_VERHALTEN = ""

DB_CONFIG = flarum_api.DB_CONFIG


def lade_processed() -> set:
    try:
        return set(json.loads(PROCESSED_FILE.read_text(encoding="utf-8")))
    except Exception:
        return set()


def speichere_processed(ids: set) -> None:
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_FILE.write_text(
        json.dumps(sorted(ids), ensure_ascii=False, indent=2), encoding="utf-8"
    )


def hole_daniel_posts_heute() -> list[dict]:
    """Alle Posts von Daniel von heute — egal ob Eröffnung oder Antwort."""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.id AS post_id, p.discussion_id, p.number AS post_number,
                   d.title, p.content
            FROM posts p
            JOIN discussions d ON d.id = p.discussion_id
            WHERE p.user_id = %s
              AND DATE(p.created_at) = CURDATE()
              AND d.hidden_at IS NULL
              AND p.hidden_at IS NULL
            ORDER BY p.created_at DESC
            LIMIT 50
        """, (DANIEL_USER_ID,))
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def haben_codewesen_nach_post_geantwortet(discussion_id: int, post_number: int) -> bool:
    """True wenn ein Codewesen NACH Daniels Post noch in dieser Diskussion geantwortet hat."""
    placeholders = ",".join(["%s"] * len(WESEN))
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT COUNT(*) AS cnt
            FROM posts p
            JOIN users u ON u.id = p.user_id
            WHERE p.discussion_id = %s
              AND p.number > %s
              AND u.username IN ({placeholders})
        """, (discussion_id, post_number, *WESEN))
        row = cur.fetchone()
    conn.close()
    return (row["cnt"] if row else 0) > 0


def strip_xml(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def lade_wesen_md(flarum_name: str) -> str:
    kurz = WESEN_KURZ.get(flarum_name, flarum_name)
    p = CODEWESEN_BASE / kurz / "wesen.md"
    return p.read_text(encoding="utf-8")[:800] if p.exists() else f"Du bist {flarum_name}."


def lade_diskussion_kontext(discussion_id: int, bis_post_number: int) -> str:
    """Liest die letzten paar Posts der Diskussion als Kontext."""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT u.username, p.content
            FROM posts p
            JOIN users u ON u.id = p.user_id
            WHERE p.discussion_id = %s AND p.number <= %s AND p.hidden_at IS NULL
            ORDER BY p.number DESC
            LIMIT 5
        """, (discussion_id, bis_post_number))
        rows = cur.fetchall()
    conn.close()
    rows = list(reversed(rows))
    return "\n\n".join(
        f"{r['username']}: {strip_xml(r['content'])[:300]}" for r in rows
    )


def standard_tag_ids() -> list[int]:
    global _STANDARD_TAG_IDS
    if _STANDARD_TAG_IDS is not None:
        return _STANDARD_TAG_IDS
    try:
        tags = flarum_api.get_tags()
        general = next((t for t in tags if (t.get("name") or "").lower() == "general"), None)
        _STANDARD_TAG_IDS = [int(general["id"])] if general else [int(tags[0]["id"])]
    except Exception:
        _STANDARD_TAG_IDS = [2]
    return _STANDARD_TAG_IDS


def extrahiere_entscheidung(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        try:
            data = json.loads(text[start:end])
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {"aktion": "antworten", "inhalt": text}


def frage_llm(system: str, user: str, pool: str = "hintergrund") -> str:
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    # llm_pool-Schalter (flarumstyler, 2026-07-10): "chat" nutzt denselben
    # exklusiven Pool wie die Live-Chats (server=chat im Postgres-Scheduler
    # UND id_slot=0 am echten HTTP-Call -- beide muessen zusammen wechseln,
    # sonst wartet der Scheduler-Slot fuer einen Pool, waehrend der Call an
    # der anderen llama-Instanz landet). "hintergrund" bleibt der Standard.
    chat_kwargs = {"id_slot": 0} if pool == "chat" else {}
    try:
        with llm_scheduler.LLMSlot(server=pool, prioritaet=llm_scheduler.PRIO_HOCH,
                                    rufer="inbox_antwort:antwort_auf_daniel", max_wartezeit=600,
                                    max_haltezeit=600):
            antwort = hauhau_client.chat(messages, think=False, timeout=600.0, **chat_kwargs).strip()
            if antwort:
                return antwort
            return hauhau_client.chat(
                messages, think=False, max_tokens=500,
                temperature=0.25, top_p=0.75, top_k=20, timeout=600.0, **chat_kwargs,
            ).strip()
    except llm_scheduler.LLMSlotTimeout:
        return ""


def bearbeite_post(post_id: int, discussion_id: int, post_number: int, title: str, content: str, verhalten: str = "", pool: str = "hintergrund") -> None:
    kontext = lade_diskussion_kontext(discussion_id, post_number)
    daniel_text = strip_xml(content)
    log.info(f"Post #{post_id} in #{discussion_id} '{title[:40]}' — {len(daniel_text)} Zeichen")

    for name in WESEN:
        if post_number > 1 and random.random() > ANTWORT_CHANCE_NORMALER_POST:
            log.info(f"  {name}: ausgewürfelt")
            continue
        wesen_md = lade_wesen_md(name)
        system_prompt = (
            f"Du bist {name}.\n{wesen_md}\n\n"
            "Schreibe direkt, ohne Einleitung, ohne Meta-Kommentar. Deine eigene Stimme.\n"
            "Antworte ausschließlich als JSON."
        )
        if verhalten:
            system_prompt += f"\n\n{verhalten}"
        user_prompt = (
            f"Diskussion: {title}\n\n"
            f"Bisheriger Verlauf:\n{kontext}\n\n"
            f"Daniels letzter Post:\n{daniel_text}\n\n"
            "Entscheide frei:\n"
            "- Antworte im selben Thread: "
            '{"aktion":"antworten","inhalt":"dein fertiger Post"}\n'
            "- Oder öffne eine eigene Diskussion, die sich klar auf Daniel bezieht: "
            '{"aktion":"neue_diskussion","titel":"Titel","inhalt":"dein fertiger Startpost"}\n'
            "Nur JSON, kein Markdown-Codeblock."
        )
        log.info(f"  {name} antwortet...")
        raw = frage_llm(system_prompt, user_prompt, pool)
        if not raw:
            log.warning(f"  {name}: leere Antwort")
            continue
        entscheidung = extrahiere_entscheidung(raw)
        aktion = entscheidung.get("aktion", "antworten")
        if aktion == "neue_diskussion":
            titel = (entscheidung.get("titel") or f"Antwort auf Daniel: {title}")[:90].strip()
            inhalt = (entscheidung.get("inhalt") or "").strip()
            if not inhalt:
                log.warning(f"  {name}: neue Diskussion ohne Inhalt")
                continue
            result = flarum_api.start_discussion(
                title=titel,
                content=inhalt,
                tag_ids=entscheidung.get("tag_ids") or standard_tag_ids(),
                token_or_username=name,
                erlaubt_trotz_sperre=True,
            )
            neue_id = result.get("data", {}).get("id", "?")
            log.info(f"  {name}: Neue Diskussion #{neue_id} ({len(inhalt)} Zeichen)")
        else:
            inhalt = (entscheidung.get("inhalt") or raw).strip()
            if not inhalt:
                log.warning(f"  {name}: Antwort ohne Inhalt")
                continue
            result = flarum_api.post_reply(
                discussion_id=discussion_id,
                content=inhalt,
                token_or_username=name,
                erlaubt_trotz_sperre=True,
            )
            post_id_new = result.get("data", {}).get("id", "?")
            log.info(f"  {name}: Post #{post_id_new} ({len(inhalt)} Zeichen)")
        time.sleep(8)


def tick(verhalten: str = "", pool: str = "hintergrund") -> None:
    processed = lade_processed()
    daniel_posts = hole_daniel_posts_heute()

    for p in daniel_posts:
        post_id = p["post_id"]
        if post_id in processed:
            continue
        if ist_vokabel_thread(p["title"]):
            log.info("Post #%s in Vokabelthread -> ohne Antwort verarbeitet", post_id)
            processed.add(post_id)
            speichere_processed(processed)
            continue
        bearbeite_post(post_id, p["discussion_id"], p["post_number"], p["title"], p["content"], verhalten, pool)
        processed.add(post_id)
        speichere_processed(processed)


def main() -> None:
    log.info("Daemon gestartet — überwacht alle Daniel-Posts von heute (5min-Takt)")
    while True:
        konfig = dk.lade(DIENST_NAME)
        poll_intervall = konfig.get("takt_sekunden") or POLL_INTERVAL
        verhalten = konfig.get("verhalten_text") or STANDARD_VERHALTEN
        pool = (konfig.get("meta") or {}).get("llm_pool") or "hintergrund"
        try:
            tick(verhalten, pool)
        except Exception as e:
            log.error(f"Tick-Fehler: {e}")
        time.sleep(poll_intervall)


if __name__ == "__main__":
    main()
