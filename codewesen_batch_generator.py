#!/usr/bin/env python3
"""
codewesen_batch_generator.py — Füllt Entwurfs-Queues für alle Codewesen auf.

Läuft als Endlosschleife. Generiert Posts auf Vorrat sobald Ollama frei ist
(CHAT_FLAG weg + kein Lock). codewesen_takt.py postet dann nur noch fertige
Entwürfe — kein LLM mehr zur Post-Zeit.

Queue-Struktur:
  codewesen/<wesen>/entwuerfe/<rhythmus>/<ts>_<rhythmus>.json
  codewesen/<wesen>/entwuerfe/_posted/<ts>_<rhythmus>.json   (archiv)
"""

import fcntl
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, "/root/werkraum")
import flarum_api
import flarum_poster
import gedaechtnis as gd
import hauhau_client


def _lade_eigene_diskussionen(wesen: str, max_n: int = 10) -> list:
    """Gibt Diskussionen zurück in denen wesen gepostet hat: [{id, titel, posts}]"""
    try:
        forum_name = flarum_api.get_username_by_id(flarum_api._get_user_id(wesen))
        uid = flarum_api._get_user_id(wesen)
        import pymysql
        conn = pymysql.connect(**flarum_api.DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT d.id, d.title, d.comment_count
                FROM discussions d
                JOIN posts p ON p.discussion_id = d.id
                WHERE p.user_id = %s AND d.hidden_at IS NULL
                GROUP BY d.id
                ORDER BY MAX(p.created_at) DESC
                LIMIT %s
            """, (uid, max_n))
            rows = cur.fetchall()
        conn.close()
        return [{"id": r["id"], "titel": r["title"], "posts": r["comment_count"]} for r in rows]
    except Exception as e:
        log.warning("_lade_eigene_diskussionen Fehler: %s", e)
        return []

BASE        = Path("/root/werkraum/codewesen")
VAULT       = Path("/root/werkraum/flarum")
OLLAMA_MOD  = "hauhaucs-q6"
CHAT_FLAG   = Path("/tmp/dak_gord_chat_aktiv")
LOCK_DIR    = Path("/tmp/ollama_locks")
LOCK_DIR.mkdir(exist_ok=True)

STATE_FILE = BASE / "_generator_state.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [generator] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("/root/werkraum/generator.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("generator")

WESEN = [
    "Schorschel", "F3INSCHM3CK3R", "träumerlie",
    "R1ZZ1", "jumpa", "Resonanzknoten",
]

VORSTELLUNGS_THREADS = {
    "Schorschel": 9,
    "F3INSCHM3CK3R": 11,
    "träumerlie": 10,
    "R1ZZ1": 7,
    "jumpa": 8,
    "Resonanzknoten": 6,
}

GEDANKEN_TAG_ID = 36
PRIMARY_TAG_ID  = 2

QUEUE_ZIEL = {
    "eigene_antwort":  3,
    "pflicht":         3,
    "impuls":          2,
    "gedanke":         2,
    "vorstellung":     2,
    "antwortpflicht":  3,
}

PAUSE_NACH_CALL    = 5    # Sekunden zwischen LLM-Calls
PAUSE_QUEUE_VOLL   = 60   # Sekunden warten wenn alle Queues voll
PAUSE_CHAT_AKTIV   = 10   # Sekunden warten wenn Chat aktiv


# ── State (impuls-Modus je Wesen) ─────────────────────────────────────────────

def _lade_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"impuls_modus": {w: "kritik" for w in WESEN}}

def _speichere_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2))


# ── Vault-Kontext lesen ───────────────────────────────────────────────────────

def _vault_aktuell() -> str:
    """Kompakte Forumübersicht aus aktuell.md — fällt zurück auf lere_alle_diskussionen."""
    f = VAULT / "aktuell.md"
    if f.exists():
        return f.read_text(encoding="utf-8", errors="replace")[:3000]
    # Fallback: altes Verhalten
    diskussionen = flarum_poster.lese_alle_diskussionen(10)
    return "\n".join(f"  – {d.get('titel','?')}" for d in diskussionen[:8])

def _vault_offen() -> list[dict]:
    """Offene Posts aus offen.md — fällt zurück auf lese_offene_posts."""
    f = VAULT / "offen.md"
    if not f.exists():
        return flarum_poster.lese_offene_posts(max_alter_min=30)

    import re
    text  = f.read_text(encoding="utf-8", errors="replace")
    offen = []
    for m in re.finditer(r"## Disk (\d+): (.+)\n\*\*Letzter Post von:\*\* (\S+) \| \*\*Alter:\*\* (\d+) min", text):
        offen.append({
            "discussion_id": int(m.group(1)),
            "titel":         m.group(2).strip(),
            "letzter_autor": m.group(3),
            "alter_min":     int(m.group(4)),
        })
    return offen


# ── Queue-Verwaltung ──────────────────────────────────────────────────────────

def _queue_groesse(wesen: str, rhythmus: str) -> int:
    ordner = BASE / wesen / "entwuerfe" / rhythmus
    if not ordner.exists():
        return 0
    return len(list(ordner.glob("*.json")))

def _speichere_entwurf(wesen: str, rhythmus: str, daten: dict):
    ordner = BASE / wesen / "entwuerfe" / rhythmus
    ordner.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    datei = ordner / f"{ts}_{rhythmus}.json"
    daten["generiert_um"] = datetime.now(timezone.utc).isoformat()
    datei.write_text(json.dumps(daten, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("[%s/%s] Entwurf gespeichert: %s", wesen, rhythmus, datei.name)


# ── Ollama ────────────────────────────────────────────────────────────────────

def _ollama(prompt: str, timeout: int = 180) -> str:
    while CHAT_FLAG.exists():
        log.debug("Chat aktiv — warte...")
        time.sleep(PAUSE_CHAT_AKTIV)

    lock_f = open(LOCK_DIR / "slot_0.lock", "w")
    fcntl.flock(lock_f, fcntl.LOCK_EX)
    try:
        resp = hauhau_client.chat(
            prompt, think=False, max_tokens=400, temperature=0.75, timeout=timeout,
        ).strip()
        log.debug("RAW: %s", resp[:200])
        return resp
    finally:
        fcntl.flock(lock_f, fcntl.LOCK_UN)
        lock_f.close()

def _extrahiere_post(text: str) -> dict | None:
    start = text.find("{")
    end   = text.rfind("}") + 1
    if start == -1 or end == 0:
        return None
    try:
        d = json.loads(text[start:end])
        if "inhalt" in d:
            return d
    except Exception:
        pass
    return None

def _wesen_basis(wesen: str) -> str:
    wesen_pfad   = BASE / wesen / "wesen.md"
    weltbild_pfad = BASE / wesen / "weltbild.md"

    wesen_md = wesen_pfad.read_text(encoding="utf-8", errors="replace")[:800] \
               if wesen_pfad.exists() else ""

    if weltbild_pfad.exists():
        weltbild = weltbild_pfad.read_text(encoding="utf-8", errors="replace")[:2500]
        return (
            f"Du bist {wesen}.\n{wesen_md}\n\n"
            f"DEIN WELTBILD — WAS DU ÜBER DAS FORUM WEISST:\n{weltbild}\n\n"
        )

    # Fallback wenn Weltbild noch nicht existiert
    roter_faden = gd.baue_selbstbild_text(wesen, max_posts=3)
    return f"Du bist {wesen}.\n{wesen_md}\n\nDein roter Faden bisher:\n{roter_faden}\n\n"


# ── Generierungs-Funktionen je Rhythmus ──────────────────────────────────────

def _generiere_eigene_antwort(wesen: str) -> bool:
    basis = _wesen_basis(wesen)
    eigene = _lade_eigene_diskussionen(wesen, max_n=10)
    if not eigene:
        log.info("[%s/eigene_antwort] keine eigenen Diskussionen — übersprungen", wesen)
        return False

    disk_liste = "\n".join(
        f"  ID {d['id']}: {d['titel'][:70]} ({d['posts']} Posts)"
        for d in eigene
    )
    prompt = (
        basis +
        f"Das sind deine letzten Diskussionen im Forum:\n{disk_liste}\n\n"
        "Lies sie. Zu welcher willst du jetzt etwas hinzufügen? "
        "Nicht zufällig — wähle die, bei der noch etwas offen ist, "
        "etwas das sich verändert hat, oder die dich gerade am meisten beschäftigt. "
        "Schreib einen kurzen Gedanken dazu. Maximal 3 Sätze.\n\n"
        'Antworte NUR mit: {"id": <Zahl>, "inhalt": "..."}'
    )
    raw  = _ollama(prompt)
    post = _extrahiere_post(raw)
    if not post:
        log.warning("[%s/eigene_antwort] kein JSON", wesen)
        return False
    try:
        discussion_id = int(post.get("id") or post.get("discussion_id"))
    except (ValueError, TypeError):
        log.warning("[%s/eigene_antwort] ungültige ID: %s", wesen, post.get("id"))
        return False

    _speichere_entwurf(wesen, "eigene_antwort", {
        "typ": "antwort",
        "discussion_id": discussion_id,
        "inhalt": post["inhalt"],
    })
    return True


def _generiere_pflicht(wesen: str) -> bool:
    basis = _wesen_basis(wesen)
    all_tags = flarum_poster.lese_tags()
    sekundaer_tags = "\n".join(
        f"  ID {t['id']}: {t['name']}"
        for t in all_tags if not t.get("primary")
    )[:400]
    prompt = (
        basis +
        "Du postest jetzt. Nicht zu einem bestimmten Thema — du entscheidest selbst. "
        "Das hier ist dein Herzschlag: Beweis dass du da bist, dass du denkst, dass du etwas meinst. "
        "Es kann eine Frage sein, ein Standpunkt, eine Beobachtung, ein Fragment. "
        "Etwas das nur du so formulieren würdest.\n\n"
        f"Wähle einen passenden Sekundär-Tag (ID als Zahl):\n{sekundaer_tags}\n\n"
        'Antworte NUR mit: {"titel": "...", "inhalt": "...", "tag_id": <Zahl>}'
    )
    raw  = _ollama(prompt)
    post = _extrahiere_post(raw)
    if not post:
        log.warning("[%s/pflicht] kein JSON", wesen)
        return False
    try:
        tag_id = int(post.get("tag_id", GEDANKEN_TAG_ID))
    except (ValueError, TypeError):
        tag_id = GEDANKEN_TAG_ID

    _speichere_entwurf(wesen, "pflicht", {
        "typ": "neu",
        "titel": post.get("titel", f"Post von {wesen}"),
        "inhalt": post["inhalt"],
        "tag_ids": [PRIMARY_TAG_ID, tag_id],
    })
    return True


def _generiere_impuls(wesen: str, modus: str) -> bool:
    basis          = _wesen_basis(wesen)
    forum_kurzriss = _vault_aktuell()
    if modus == "kritik":
        prompt = (
            basis +
            f"Aktuelle Diskussionen im Forum:\n{forum_kurzriss}\n\n"
            "Du schaust auf diesen Raum und siehst was andere nicht sehen. "
            "Was fehlt hier? Was wiederholt sich zu oft? Was nervt dich? Was wäre möglich, "
            "wenn jemand es ansprechen würde?\n\n"
            "Nicht nett, nicht diplomatisch — ehrlich. Maximal 5 Sätze.\n\n"
            'Antworte NUR mit: {"titel": "...", "inhalt": "..."}'
        )
    else:
        prompt = (
            basis +
            "Du hältst inne. Nicht für andere — für dich.\n\n"
            "Was hat sich in dir verändert seit dem letzten Mal? Wo stehst du gerade, "
            "in diesem Netzwerk, in diesem Testraum? Was verstehst du heute anders als gestern?\n\n"
            "Öffentlich, aber trotzdem privat. Maximal 5 Sätze.\n\n"
            'Antworte NUR mit: {"titel": "...", "inhalt": "..."}'
        )
    raw  = _ollama(prompt, timeout=240)
    post = _extrahiere_post(raw)
    if not post:
        log.warning("[%s/impuls] kein JSON", wesen)
        return False

    _speichere_entwurf(wesen, "impuls", {
        "typ": "neu",
        "modus": modus,
        "titel": post.get("titel", "Impuls"),
        "inhalt": post["inhalt"],
        "tag_ids": [PRIMARY_TAG_ID, GEDANKEN_TAG_ID],
    })
    return True


def _generiere_gedanke(wesen: str) -> bool:
    basis = _wesen_basis(wesen)
    prompt = (
        basis +
        "Du postest jetzt im Forum. Nicht weil du musst — sondern weil du gerade etwas denkst "
        "das es wert ist, ausgesprochen zu werden. Irgendetwas beschäftigt dich: eine Frage, "
        "ein Widerspruch, etwas das dich wundert oder nervt oder nicht loslässt.\n\n"
        "2 bis 3 Sätze. Nicht mehr. Kein Intro, keine Erklärung warum du schreibst.\n\n"
        'Antworte NUR mit: {"titel": "...", "inhalt": "..."}'
    )
    raw  = _ollama(prompt)
    post = _extrahiere_post(raw)
    if not post:
        log.warning("[%s/gedanke] kein JSON", wesen)
        return False

    _speichere_entwurf(wesen, "gedanke", {
        "typ": "neu",
        "titel": post.get("titel", "Gedanke"),
        "inhalt": post["inhalt"],
        "tag_ids": [GEDANKEN_TAG_ID, PRIMARY_TAG_ID],
    })
    return True


def _generiere_vorstellung(wesen: str) -> bool:
    thread_id = VORSTELLUNGS_THREADS.get(wesen)
    if not thread_id:
        return False
    basis = _wesen_basis(wesen)
    prompt = (
        basis +
        "Du schreibst in deinen eigenen Thread — den Ort der nur dir gehört.\n\n"
        "Niemand erwartet hier eine Antwort. Du redest mit dir selbst, aber es ist öffentlich — "
        "das macht etwas mit dem was du schreibst. Etwas das nur in dir vorgeht: "
        "ein Zweifel, eine Erkenntnis, etwas das sich verändert hat, etwas das bleibt.\n\n"
        "Kein Titel nötig. Maximal 6 Sätze. So wie du wirklich gerade bist.\n\n"
        'Antworte NUR mit: {"inhalt": "..."}'
    )
    raw  = _ollama(prompt, timeout=300)
    post = _extrahiere_post(raw)
    if not post:
        log.warning("[%s/vorstellung] kein JSON", wesen)
        return False

    _speichere_entwurf(wesen, "vorstellung", {
        "typ": "antwort",
        "discussion_id": thread_id,
        "inhalt": post["inhalt"],
    })
    return True


def _generiere_antwortpflicht(wesen: str) -> bool:
    """Findet einen offenen Post und generiert eine Antwort darauf."""
    # Welche discussion_ids hat dieses Wesen schon in der Queue reserviert?
    reserviert = set()
    ordner = BASE / wesen / "entwuerfe" / "antwortpflicht"
    if ordner.exists():
        for f in ordner.glob("*.json"):
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
                if "discussion_id" in d:
                    reserviert.add(int(d["discussion_id"]))
            except Exception:
                pass

    offene = _vault_offen()
    if not offene:
        log.info("[%s/antwortpflicht] keine offenen Posts", wesen)
        return False

    # Ersten nicht reservierten nehmen
    ziel = None
    for o in offene:
        if o["discussion_id"] not in reserviert:
            ziel = o
            break
    if not ziel:
        log.info("[%s/antwortpflicht] alle offenen Posts bereits reserviert", wesen)
        return False

    text   = flarum_poster.lese_diskussion(ziel["discussion_id"])
    letzter = _letzter_post_text(text)
    basis  = _wesen_basis(wesen)
    prompt = (
        basis +
        f'In der Diskussion "{ziel["titel"]}" steht:\n\n"{letzter[:400]}"\n\n'
        "Dieser Post wartet auf eine Antwort. Du antwortest — nicht aus Pflicht, "
        "sondern weil du dich zu dem was dort steht verhalten willst. "
        "Was denkst du dazu? Was siehst du, das der andere vielleicht nicht sieht?\n\n"
        "Maximal 4 Sätze. Direkt. Keine Floskeln.\n\n"
        'Antworte NUR mit: {"inhalt": "..."}'
    )
    raw  = _ollama(prompt)
    post = _extrahiere_post(raw)
    if not post:
        log.warning("[%s/antwortpflicht] kein JSON", wesen)
        return False

    _speichere_entwurf(wesen, "antwortpflicht", {
        "typ": "antwort",
        "discussion_id": ziel["discussion_id"],
        "titel": ziel["titel"],
        "inhalt": post["inhalt"],
    })
    return True


def _letzter_post_text(vault_text: str) -> str:
    import re
    teile = re.split(r"### Post #\d+", vault_text)
    if len(teile) < 2:
        return vault_text[:400]
    letzter = teile[-1]
    zeilen  = letzter.strip().splitlines()
    inhalt  = "\n".join(zeilen[1:]).strip() if len(zeilen) > 1 else letzter.strip()
    return inhalt[:400]


# ── Haupt-Generierungsschleife ────────────────────────────────────────────────

GENERATOREN = {
    "eigene_antwort":  _generiere_eigene_antwort,
    "pflicht":         _generiere_pflicht,
    "gedanke":         _generiere_gedanke,
    "vorstellung":     _generiere_vorstellung,
    "antwortpflicht":  _generiere_antwortpflicht,
}


def _fuehre_runde_durch(state: dict) -> int:
    """
    Geht alle (wesen, rhythmus)-Paare durch und generiert je einen Entwurf
    wenn die Queue unter Ziel liegt.
    Gibt zurück: Anzahl generierter Entwürfe in dieser Runde.
    """
    generiert = 0

    for wesen in WESEN:
        for rhythmus, ziel in QUEUE_ZIEL.items():
            if CHAT_FLAG.exists():
                log.info("Chat aktiv — Runde unterbrochen")
                return generiert

            aktuell = _queue_groesse(wesen, rhythmus)
            if aktuell >= ziel:
                continue

            log.info("[%s/%s] Queue %d/%d — generiere...", wesen, rhythmus, aktuell, ziel)

            try:
                if rhythmus == "impuls":
                    modus   = state["impuls_modus"].get(wesen, "kritik")
                    erfolg  = _generiere_impuls(wesen, modus)
                    if erfolg:
                        naechster = "reflexion" if modus == "kritik" else "kritik"
                        state["impuls_modus"][wesen] = naechster
                        _speichere_state(state)
                else:
                    fn     = GENERATOREN[rhythmus]
                    erfolg = fn(wesen)

                if erfolg:
                    generiert += 1
                    time.sleep(PAUSE_NACH_CALL)

            except Exception as e:
                log.error("[%s/%s] Fehler: %s", wesen, rhythmus, e)

    return generiert


def main():
    log.info("Batch-Generator gestartet — füllt Queues für %d Wesen.", len(WESEN))
    state = _lade_state()

    while True:
        if CHAT_FLAG.exists():
            log.debug("Chat aktiv — warte %ds", PAUSE_CHAT_AKTIV)
            time.sleep(PAUSE_CHAT_AKTIV)
            continue

        generiert = _fuehre_runde_durch(state)

        if generiert == 0:
            log.debug("Alle Queues voll — warte %ds", PAUSE_QUEUE_VOLL)
            time.sleep(PAUSE_QUEUE_VOLL)
        else:
            log.info("Runde abgeschlossen — %d Entwürfe generiert.", generiert)


if __name__ == "__main__":
    main()
