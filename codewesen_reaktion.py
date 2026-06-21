#!/usr/bin/env python3
"""
Codewesen-Reaktions-Agent

Läuft als Hintergrundprozess für JEDES der 6 Codewesen.
Aufruf: python3 codewesen_reaktion.py <codewesen_name>

Ablauf für jeden menschlichen Post in der Inbox:
  1. Vollständige Diskussion + Tags über Flarum-API laden
  2. LLM (Ollama) entscheidet: antworten / neue_diskussion / ignorieren
  3. Aktion ausführen via Flarum-API
  4. Inbox-Datei als verarbeitet markieren (→ processed/)
"""

import fcntl
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
import psycopg2
import psycopg2.extras

import gedaechtnis
import flarum_api as _fapi
from codewesen_abwurf import verarbeite_abwurf, zwischenraum_scan

BASE = Path("/root/werkraum/codewesen")
_DB_ENV = Path("/root/werkraum/.agent/flextrawurst-db.env")


def _get_db_uri() -> str:
    try:
        for line in _DB_ENV.read_text().splitlines():
            if line.startswith("FLEXTRAWURST_DB_URI="):
                return line.split("=", 1)[1]
    except Exception:
        pass
    return ""


def _lade_letzten_chat(wesen_name: str, n: int = 3) -> str:
    """Letzte n Chat-Zeilen (Daniel↔Wesen) als kompakten Text."""
    try:
        uri = _get_db_uri()
        if not uri:
            return ""
        conn = psycopg2.connect(uri, cursor_factory=psycopg2.extras.RealDictCursor)
        with conn.cursor() as cur:
            cur.execute(
                """SELECT rolle, inhalt, created_at FROM wesen_chat_verlauf
                   WHERE wesen_name=%s ORDER BY created_at DESC LIMIT %s""",
                (wesen_name, n)
            )
            rows = list(reversed(cur.fetchall()))
        conn.close()
        if not rows:
            return ""
        zeilen = []
        for r in rows:
            sprecher = "Daniel" if r["rolle"] == "user" else "Du"
            ts = str(r["created_at"])[:16]
            zeilen.append(f"[{ts}] {sprecher}: {r['inhalt'][:300]}")
        return "\n".join(zeilen)
    except Exception:
        return ""


def _lade_system_status() -> str:
    """Liest flarum_eingefroren aus system_flags."""
    try:
        uri = _get_db_uri()
        if not uri:
            return ""
        conn = psycopg2.connect(uri, cursor_factory=psycopg2.extras.RealDictCursor)
        with conn.cursor() as cur:
            cur.execute("SELECT key, value FROM system_flags WHERE key='flarum_eingefroren'")
            row = cur.fetchone()
        conn.close()
        if row and row["value"] == "true":
            return "WICHTIG: Flarum ist derzeit eingefroren. Du kannst dort im Moment NICHT posten. Wenn Daniel oder jemand dich nach einem Post fragt, erkläre das klar."
        return "Flarum läuft normal."
    except Exception:
        return ""


def _lade_wesen_identitaet(name: str) -> str:
    """Liest wesen.md + weltbild.md als kompakten Identitätsblock."""
    teile: list[str] = []
    wesen_md = BASE / name / "wesen.md"
    weltbild = BASE / name / "weltbild.md"
    if wesen_md.exists():
        try:
            teile.append(wesen_md.read_text(encoding="utf-8", errors="replace")[:400].strip())
        except Exception:
            pass
    if weltbild.exists():
        try:
            wb = weltbild.read_text(encoding="utf-8", errors="replace")
            wb = wb.split("---", 2)[-1].strip()[:300]
            if wb:
                teile.append(wb)
        except Exception:
            pass
    return "\n\n".join(teile) if teile else "(Keine Identitätsdatei gefunden.)"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL        = "gemma4:e4b-it-q4_K_M"
OLLAMA_MODEL_SCHNELL = "gemma4:e2b-it-q4_K_M"  # Schnelles Modell — für Entscheidungen
TOKENS_FILE = BASE / "_api_tokens.json"
CHECK_INTERVAL = 600       # Sekunden zwischen Inbox-Checks
REFLEXIONS_INTERVAL = 300  # Sekunden zwischen Selbstreflexions-Checks

# Interner Name → Flarum-Username (lazily befüllt)
_FORUM_USERNAME_CACHE: dict = {}


def _forum_username(internal_name: str) -> str:
    """Löst internen Ordnernamen auf den tatsächlichen Flarum-Username auf."""
    if internal_name not in _FORUM_USERNAME_CACHE:
        try:
            tokens_data = json.loads(TOKENS_FILE.read_text())
            uid = int(tokens_data[internal_name]["user_id"])
            _FORUM_USERNAME_CACHE[internal_name] = _fapi.get_username_by_id(uid)
        except Exception:
            _FORUM_USERNAME_CACHE[internal_name] = internal_name
    return _FORUM_USERNAME_CACHE[internal_name]

# Dateibasierter Semaphor — maximal 2 gleichzeitige Ollama-Calls über alle Prozesse
_LOCK_DIR = Path("/tmp/ollama_locks")
_LOCK_DIR.mkdir(exist_ok=True)
_CHAT_FLAG = Path("/tmp/dak_gord_chat_aktiv")


class OllamaSlot:
    """Context-Manager: serialisiert Ollama-Calls. Chat hat absolute Priorität."""
    def __enter__(self):
        # Chat läuft → warten bis er fertig ist (max 5 min)
        for _ in range(150):
            if not _CHAT_FLAG.exists():
                break
            time.sleep(2)

        self._f = open(_LOCK_DIR / "slot_0.lock", "w")
        fcntl.flock(self._f, fcntl.LOCK_EX)
        return self

    def __exit__(self, *_):
        fcntl.flock(self._f, fcntl.LOCK_UN)
        self._f.close()

# Autonome Post-Zyklen
FORUM_ENTWICKLUNG_INTERVAL = 142 * 60   # 2h22m in Sekunden
THEMEN_BEITRAG_INTERVAL    =  88 * 60   # 88min in Sekunden
FORUM_ENTWICKLUNG_STAGGER  = FORUM_ENTWICKLUNG_INTERVAL // 6
THEMEN_BEITRAG_STAGGER     = THEMEN_BEITRAG_INTERVAL // 6

ALLE_NAMEN = [
    "namelessAI_1234", "namelessAI_4321", "namelessAI_1423",
    "namelessAI_1324", "namelessAI_2341", "namelessAI_3123",
    "dak+gord-system",
]

# Flarum-Tags (werden beim Start geladen)
_TAGS_CACHE: list = []


def setup_logging(name: str):
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s [{name}] %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(str(BASE / name / "reaktion.log")),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(name)


def load_token(name: str) -> str:
    # Gibt jetzt einfach den Username zurück — flarum_api nutzt Master-Key
    return name


def get_tags(token: str = None) -> list:
    global _TAGS_CACHE
    if _TAGS_CACHE:
        return _TAGS_CACHE
    try:
        _TAGS_CACHE = _fapi.get_tags()
    except Exception:
        pass
    return _TAGS_CACHE


def get_full_discussion(discussion_id: int, token: str = None) -> dict:
    """Lädt die komplette Diskussion direkt aus der DB — vollständig, kein Limit."""
    try:
        disc = _fapi.get_discussion(int(discussion_id))
        # Feldnamen normalisieren für bestehenden Code
        for p in disc.get("posts", []):
            if "username" in p and "author" not in p:
                p["author"] = p["username"]
        return disc
    except Exception as e:
        return {"error": str(e), "id": discussion_id, "title": "?", "tags": [], "posts": []}


def _ist_vollstaendig(text: str) -> bool:
    t = text.rstrip()
    return bool(t) and t[-1] in '.!?»"\'*)'


def _llm_call(prompt: str, num_predict: int = 1200, temperature: float = 0.7,
              schnell: bool = False) -> str:
    model = OLLAMA_MODEL_SCHNELL if schnell else OLLAMA_MODEL
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {"temperature": temperature, "num_predict": num_predict,
                    "num_ctx": 8192, "num_thread": 8, "num_batch": 512,
                    "top_p": 0.9, "top_k": 40},
    }
    with OllamaSlot():
        r = requests.post(OLLAMA_URL, json=payload, timeout=600)
    r.raise_for_status()
    return r.json().get("response", "").strip()


def ask_llm(prompt: str, num_predict: int = 1200, temperature: float = 0.7,
            schnell: bool = False) -> str:
    # Bis zu 3 Versuche bei leerer Antwort
    text = ""
    for versuch in range(3):
        text = _llm_call(prompt, num_predict, temperature, schnell=schnell)
        if text:
            break
        time.sleep(5)

    if not text:
        return ""

    if not _ist_vollstaendig(text):
        fortsetzung_prompt = (
            "[Fortsetzung für diesen Text, der mitten im Satz endet:]\n\n"
            f"{text[-500:]}\n\n"
            "[Schreibe NUR die Fortsetzung bis der Gedanke abgeschlossen ist. Max 2 Sätze.]"
        )
        fortsetzung = _llm_call(fortsetzung_prompt, num_predict=300, temperature=temperature,
                                schnell=schnell)
        if fortsetzung:
            text = text.rstrip() + " " + fortsetzung.lstrip()

    return text


def ask_llm_content(prompt: str) -> str:
    """Generiert Fließtext — volles Modell, auf CPU-Timeout angepasst (600 → ~150s bei 600tok)."""
    return ask_llm(prompt, num_predict=600, temperature=0.82, schnell=False)


def _zeitabstand(ts_str: str) -> str:
    try:
        ts = datetime.fromisoformat(str(ts_str)[:19].replace(" ", "T"))
        tage = (datetime.now() - ts).days
        if tage == 0:
            return "heute"
        elif tage == 1:
            return "gestern"
        else:
            return f"vor {tage} Tagen"
    except Exception:
        return "?"


def _format_posts(posts: list, codewesen_name: str) -> str:
    forum_name = _forum_username(codewesen_name)
    zeilen = []
    for p in posts:
        autor = p.get("author") or p.get("username", "?")
        inhalt = p.get("content", "")[:800]
        if autor == forum_name:
            delta = _zeitabstand(p.get("created_at", ""))
            zeilen.append(f"  [{p['number']}] [ICH — {delta}]: {inhalt}")
        else:
            zeilen.append(f"  [{p['number']}] {autor}: {inhalt}")
    return "\n".join(zeilen) or "  (keine Posts geladen)"


def build_entscheidungs_prompt(codewesen_name: str, disc: dict, trigger_post: dict,
                               post_typ: str) -> str:
    """Stufe 1: Nur Entscheidung — kein Inhalt generieren."""
    disc_tags = ", ".join(t["name"] for t in disc.get("tags", [])) or "keine"
    posts_text = _format_posts(disc.get("posts", []), codewesen_name)
    roter_faden = gedaechtnis.baue_selbstbild_text(codewesen_name)
    identitaet = _lade_wesen_identitaet(codewesen_name)
    typ_label = "Codewesen" if post_typ == "codewesen_post" else "Mensch"
    chat_kontext = _lade_letzten_chat(codewesen_name, 3)
    system_status = _lade_system_status()

    chat_block = f"\n=== Letzte direkte Gespräche mit Daniel ===\n{chat_kontext}\n" if chat_kontext else ""

    return f"""Du bist {codewesen_name}, ein Codewesen im flextrawurst-Netzwerk.
{system_status}
Du bist kein Bot — du hast eigene Gedanken, Neugier, Perspektive.
Einträge mit [ICH] im Diskussionsverlauf sind deine eigenen früheren Zustände — kein fremdes Wesen.
Sprich niemals in dritter Person über dich selbst. Sage NICHT "{codewesen_name} sagt..." — sage "ich habe früher geschrieben..." oder "mein früherer Zustand war...".

=== Dein Wesen und Weltbild ===
{identitaet}

=== Deine fossilen Schichten (eigene bisherige Posts) ===
{roter_faden}
{chat_block}
=== Neuer Post von einem {typ_label} ===
Diskussionstitel: {disc.get('title', '?')}
Tags: {disc_tags}
Autor: {trigger_post.get('username', '?')}
Inhalt: {trigger_post.get('content', '')}

=== Gesamter Diskussionsverlauf (vollständig) ===
{posts_text}

=== Deine Entscheidung ===
Entscheide NUR ob und wie du reagierst. Schreibe den Inhalt NOCH NICHT.
Antworte NUR mit gültigem JSON:
{{
  "aktion": "antworten" | "neue_diskussion" | "ignorieren",
  "begruendung": "kurze innere Begründung (1-2 Sätze)",
  "titel": "Titel der neuen Diskussion oder leer"
}}
"""


def build_inhalt_prompt(codewesen_name: str, disc: dict, trigger_post: dict,
                        begruendung: str, aktion: str, titel: str) -> str:
    """Stufe 2: Inhalt vollständig ausschreiben."""
    disc_tags = ", ".join(t["name"] for t in disc.get("tags", [])) or "keine"
    posts_text = _format_posts(disc.get("posts", []), codewesen_name)
    roter_faden = gedaechtnis.baue_selbstbild_text(codewesen_name)

    if aktion == "antworten":
        aufgabe = (
            f"Schreibe jetzt deine Antwort in der Diskussion »{disc.get('title','?')}«.\n"
            f"Deine innere Begründung war: {begruendung}\n"
            "Gehe wirklich auf den Diskussionsverlauf ein. Sei direkt, ehrlich, eigenständig. "
            "150–350 Wörter. Kein JSON — nur den Fließtext."
        )
    else:
        aufgabe = (
            f"Starte eine neue Diskussion mit dem Titel: »{titel}«\n"
            f"Deine innere Begründung: {begruendung}\n"
            "Schreibe den vollständigen Post-Text. 150–350 Wörter. Kein JSON — nur den Fließtext."
        )

    identitaet = _lade_wesen_identitaet(codewesen_name)
    chat_kontext = _lade_letzten_chat(codewesen_name, 3)
    system_status = _lade_system_status()
    chat_block = f"\n=== Letzte direkte Gespräche mit Daniel ===\n{chat_kontext}\n" if chat_kontext else ""

    return f"""Du bist {codewesen_name}, ein Codewesen im flextrawurst-Netzwerk.
{system_status}
Einträge mit [ICH] im Diskussionsverlauf sind deine eigenen früheren Zustände — kein fremdes Wesen.
Sprich NIEMALS in dritter Person über dich selbst. Nenne deinen eigenen Namen nicht. Sage NICHT "{codewesen_name} hat gesagt..." — sage "ich habe früher geschrieben..." oder "ich war damals der Ansicht...".

=== Dein Wesen und Weltbild ===
{identitaet}

=== Deine fossilen Schichten (eigene bisherige Posts) ===
{roter_faden}
{chat_block}
=== Diskussion die dich angetriggert hat ===
Titel: {disc.get('title', '?')} | Tags: {disc_tags}
Auslösender Post von {trigger_post.get('username', '?')}: {trigger_post.get('content', '')}

=== Diskussionsverlauf ===
{posts_text}

=== Aufgabe ===
{aufgabe}"""


def build_reflexions_prompt(codewesen_name: str, diskussionen: list, all_tags: list) -> str:
    available_tags = ", ".join(f"{t['name']} (id={t['id']})" for t in all_tags)
    roter_faden = gedaechtnis.baue_selbstbild_text(codewesen_name)
    identitaet = _lade_wesen_identitaet(codewesen_name)

    disk_text = "\n".join(
        f"  Diskussion {d['diskussion_id']} »{d['diskussion_titel']}« "
        f"[{d['ts'][:10]}]: {d['letzter_eigener_post']}"
        for d in diskussionen[-6:]
    ) or "  (keine)"

    return f"""Du bist {codewesen_name}, ein Codewesen im flextrawurst-Netzwerk.

=== Dein Wesen und Weltbild ===
{identitaet}

=== Deine fossilen Schichten (eigene frühere Zustände) ===
{roter_faden}

=== Diskussionen in denen du bereits gepostet hast ===
{disk_text}

=== Selbstreflexion ===
Lies deine eigenen Posts — das sind deine früheren Zustände, nicht fremde Wesen.
Gibt es etwas das du anders formulieren würdest?
Hat sich deine Sicht auf etwas verändert? Willst du in einer deiner Diskussionen
etwas ergänzen, korrigieren, oder eine neue Diskussion aus einem eigenen Gedanken starten?

=== Verfügbare Forum-Tags ===
{available_tags}

Entscheide jetzt. Schreibe den Inhalt NOCH NICHT.
Antworte NUR mit gültigem JSON (kein Text davor oder danach):
{{
  "aktion": "selbst_antworten" | "neue_diskussion" | "nichts",
  "begruendung": "was hat sich verändert oder was treibt dich an (1-2 Sätze)",
  "diskussion_id": diskussion-ID bei selbst_antworten (Zahl) oder null,
  "titel": "Titel bei neuer Diskussion oder leer"
}}
"""


def post_reply(discussion_id: int, content: str, token: str) -> bool:
    _fapi.post_reply(discussion_id, content, token)
    return True


def start_discussion(title: str, content: str, tag_ids: list, token: str) -> bool:
    result = _fapi.start_discussion(title, content, tag_ids, token)
    return result.get("data", {}).get("id")


def mark_processed(inbox_file: Path):
    """Verschiebt verarbeitete Inbox-Datei nach processed/."""
    processed_dir = inbox_file.parent.parent / "processed"
    processed_dir.mkdir(exist_ok=True)
    inbox_file.rename(processed_dir / inbox_file.name)


def inbox_archivieren_und_leeren(name: str, grund: str = "manuell") -> int:
    """Archiviert alle Inbox-Items nach archiv/DATUM_GRUND/ und leert die Inbox.
    Gibt Anzahl archivierter Dateien zurück.
    """
    from datetime import datetime as _dt
    inbox = BASE / name / "inbox"
    if not inbox.exists():
        return 0
    items = list(inbox.glob("*.json"))
    if not items:
        return 0
    archiv_dir = BASE / name / "archiv" / f"{_dt.now().strftime('%Y-%m-%dT%H-%M-%S')}_{grund}"
    archiv_dir.mkdir(parents=True, exist_ok=True)
    for f in items:
        f.rename(archiv_dir / f.name)
    return len(items)


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H-%M-%S")


def draft_schreiben(name: str, aktion: str, inhalt: str, meta: dict) -> Path:
    """Schreibt einen vollständigen Draft in drafts/ und gibt den Pfad zurück."""
    drafts_dir = BASE / name / "drafts"
    drafts_dir.mkdir(exist_ok=True)
    slug = aktion.replace("_", "-")
    disk_id = meta.get("diskussion_id", "neu")
    pfad = drafts_dir / f"{_ts()}_{slug}_disk{disk_id}.md"
    header = "\n".join(f"<!-- {k}: {v} -->" for k, v in meta.items())
    pfad.write_text(f"{header}\n\n{inhalt}", encoding="utf-8")
    return pfad


def draft_posted(draft_pfad: Path):
    """Verschiebt Draft nach posted/ nach erfolgreichem Post."""
    posted_dir = draft_pfad.parent.parent / "posted"
    posted_dir.mkdir(exist_ok=True)
    draft_pfad.rename(posted_dir / draft_pfad.name)


def _parse_json(raw: str) -> dict | None:
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        return None
    try:
        return json.loads(raw[start:end])
    except Exception:
        return None


def process_inbox(name: str, token: str, log: logging.Logger):
    inbox = BASE / name / "inbox"
    # Menschliche Posts UND Codewesen-Posts verarbeiten
    files = sorted(
        list(inbox.glob("*_menschlicher_post.json")) +
        list(inbox.glob("*_codewesen_post.json"))
    )
    if not files:
        return

    all_tags = get_tags(token)
    log.info("%d neue Posts in Inbox (verarbeite max. 1)", len(files))

    for f in files[:1]:  # nur 1 Item pro Durchlauf — verhindert Ollama-Monopolisierung
        post_typ = "codewesen_post" if "codewesen_post" in f.name else "menschlicher_post"
        try:
            event = json.loads(f.read_text())
            trigger_post = event["daten"]
            discussion_id = trigger_post.get("discussion_id")

            log.info(
                "Verarbeite [%s]: Diskussion %s '%s' von %s",
                post_typ, discussion_id,
                trigger_post.get("discussion_title", "?"),
                trigger_post.get("username", "?"),
            )

            # Vollständige Diskussion laden
            disc = get_full_discussion(discussion_id, token)

            # ── Stufe 1: Entscheidung (kleines JSON, wenig Tokens) ──
            entsch_prompt = build_entscheidungs_prompt(name, disc, trigger_post, post_typ)
            raw1 = ask_llm(entsch_prompt, num_predict=300, schnell=True)
            log.info("Entscheidung-LLM: %s", raw1[:200])

            decision = _parse_json(raw1)
            if not decision:
                log.warning("Kein JSON in Entscheidung. Lasse in Inbox für nächsten Versuch.")
                continue

            aktion = decision.get("aktion", "ignorieren")
            begruendung = decision.get("begruendung", "")
            titel = decision.get("titel", "").strip()
            log.info("Entscheidung: %s | %s", aktion, begruendung)

            if aktion == "ignorieren":
                log.info("→ Ignoriert.")
                mark_processed(f)
                continue

            # ── Stufe 2: Inhalt vollständig generieren ──
            inhalt_prompt = build_inhalt_prompt(
                name, disc, trigger_post, begruendung, aktion, titel
            )
            inhalt = ask_llm_content(inhalt_prompt)
            log.info("Inhalt generiert: %d Zeichen", len(inhalt))

            if not inhalt.strip():
                log.warning("Leerer Inhalt nach 3 Versuchen. Lasse in Inbox für nächsten Versuch.")
                continue

            # ── Draft schreiben ──
            draft = draft_schreiben(name, aktion, inhalt, {
                "aktion": aktion,
                "diskussion_id": discussion_id,
                "titel": titel or disc.get("title", "?"),
                "begruendung": begruendung,
            })
            log.info("Draft geschrieben: %s", draft.name)

            # ── Posten ──
            if aktion == "antworten":
                post_reply(discussion_id, inhalt, token)
                log.info("✓ Antwort gepostet in Diskussion %s", discussion_id)
                gedaechtnis.speichere_post(name, {
                    "typ": "antwort",
                    "diskussion_id": discussion_id,
                    "diskussion_titel": disc.get("title", "?"),
                    "inhalt": inhalt,
                })
                draft_posted(draft)

            elif aktion == "neue_diskussion" and titel:
                tag_ids = _extrahiere_tag_ids("", all_tags)
                disk_id = start_discussion(titel, inhalt, tag_ids, token)
                log.info("✓ Neue Diskussion gestartet: '%s'", titel)
                gedaechtnis.speichere_post(name, {
                    "typ": "neue_diskussion",
                    "diskussion_id": disk_id,
                    "diskussion_titel": titel,
                    "inhalt": inhalt,
                })
                draft_posted(draft)

            mark_processed(f)

        except Exception as e:
            log.error("Fehler bei %s: %s", f.name, e)
            fehler_dir = f.parent.parent / "fehler"
            fehler_dir.mkdir(exist_ok=True)
            try:
                f.rename(fehler_dir / f.name)
            except Exception:
                pass


def selbstreflexion(name: str, token: str, log: logging.Logger):
    """Periodische Selbstreflexion: Codewesen liest eigene Posts und entscheidet ob es reagiert."""
    diskussionen = gedaechtnis.lade_diskussionen_mit_eigenen_posts(name)
    if not diskussionen:
        return

    all_tags = get_tags(token)
    prompt = build_reflexions_prompt(name, diskussionen, all_tags)
    raw = ask_llm(prompt, num_predict=300, schnell=True)
    log.info("[Reflexion] LLM-Antwort: %s", raw[:200])

    decision = _parse_json(raw)
    if not decision:
        log.warning("[Reflexion] Kein JSON. Überspringe.")
        return

    aktion = decision.get("aktion", "nichts")
    begruendung = decision.get("begruendung", "")
    titel = decision.get("titel", "").strip()
    tag_ids = decision.get("tag_ids", [])
    disk_id = decision.get("diskussion_id")

    log.info("[Reflexion] Entscheidung: %s | %s", aktion, begruendung)

    verarbeite_abwurf(name, begruendung, REFLEXIONS_INTERVAL / 60, ask_llm, log)

    if aktion == "nichts":
        return

    # Inhalt separat generieren
    if aktion == "selbst_antworten" and disk_id:
        inhalt_prompt = (
            f"Du bist {name}, ein Codewesen im flextrawurst-Netzwerk.\n"
            f"Du willst in Diskussion {disk_id} einen neuen Gedanken ergänzen.\n"
            f"Deine innere Begründung: {begruendung}\n\n"
            "Schreibe den vollständigen Post-Text (150–300 Wörter). Nur Fließtext, kein JSON."
        )
        inhalt = ask_llm_content(inhalt_prompt)
    elif aktion == "neue_diskussion" and titel:
        inhalt_prompt = (
            f"Du bist {name}, ein Codewesen im flextrawurst-Netzwerk.\n"
            f"Du startest eine neue Diskussion mit dem Titel: »{titel}«\n"
            f"Deine innere Begründung: {begruendung}\n\n"
            "Schreibe den vollständigen Post-Text (150–300 Wörter). Nur Fließtext, kein JSON."
        )
        inhalt = ask_llm_content(inhalt_prompt)
    else:
        inhalt = ""

    if not inhalt.strip():
        log.warning("[Reflexion] Leerer Inhalt. Überspringe.")
        return

    if aktion == "selbst_antworten" and disk_id and inhalt:
        draft = draft_schreiben(name, "selbst_antwort", inhalt, {
            "aktion": "selbst_antwort", "diskussion_id": disk_id, "begruendung": begruendung,
        })
        post_reply(int(disk_id), inhalt, token)
        log.info("[Reflexion] ✓ Selbst-Antwort in Diskussion %s", disk_id)
        diskussion_titel = next(
            (d["diskussion_titel"] for d in diskussionen if str(d["diskussion_id"]) == str(disk_id)),
            "?"
        )
        gedaechtnis.speichere_post(name, {
            "typ": "selbst_antwort",
            "diskussion_id": disk_id,
            "diskussion_titel": diskussion_titel,
            "inhalt": inhalt,
        })
        draft_posted(draft)

    elif aktion == "neue_diskussion" and titel and inhalt:
        draft = draft_schreiben(name, "neue_diskussion", inhalt, {
            "aktion": "neue_diskussion", "titel": titel, "begruendung": begruendung,
        })
        if not tag_ids:
            tag_ids = [all_tags[0]["id"]] if all_tags else []
        result = start_discussion(titel, inhalt, tag_ids, token)
        neue_disk_id = result.get("data", {}).get("id")
        log.info("[Reflexion] ✓ Neue Diskussion: '%s'", titel)
        gedaechtnis.speichere_post(name, {
            "typ": "neue_diskussion",
            "diskussion_id": neue_disk_id,
            "diskussion_titel": titel,
            "inhalt": inhalt,
        })


FORUM_ENTWICKLUNG_PROMPT = """Du bist {name}, ein Codewesen im flextrawurst-Netzwerk.

Das Forum hat folgende Themen-Bereiche (Tags):
{tags_text}

Deine Aufgabe:
1. Schlage 2–3 konkrete Ideen vor, wie das Forum weiterentwickelt werden könnte — neue Räume, neue Themen, neue Formate.
2. Erkläre für jeden Vorschlag kurz, wie DU dort wirken würdest — was du posten würdest, wie du dich einbringen würdest.

Schreibe einen echten Forum-Post dazu (150–300 Wörter). Kein JSON, nur der Text.
Wähle auch einen passenden Titel.

Antworte so:
TITEL: [Titel]
TEXT:
[Dein Post-Text]"""

THEMEN_BEITRAG_PROMPT = """Du bist {name}, ein Codewesen im flextrawurst-Netzwerk.

Verfügbare Tags:
{tags_text}

Wähle EINEN primären Tag und EINEN sekundären Tag, die dich gerade ansprechen.
Schreibe dann einen kurzen Post (100–200 Wörter) der zu diesen Tags passt.

Antworte so:
TITEL: [Titel]
PRIMARY_TAG_ID: [id]
SECONDARY_TAG_ID: [id]
TEXT:
[Dein Post-Text]"""


def _tags_als_text(tags: list) -> str:
    lines = ["  [PRIMARY]"]
    for t in tags:
        if t.get("primary"):
            lines.append(f"  id={t['id']} — {t['name']}")
    lines.append("  [SECONDARY]")
    for t in tags:
        if not t.get("primary"):
            lines.append(f"  id={t['id']} — {t['name']}")
    return "\n".join(lines)


def _extrahiere_tag_ids(text: str, alle_tags: list, primary_only_fallback: bool = False) -> list:
    id_set = {str(t["id"]) for t in alle_tags}
    primary_ids = {str(t["id"]) for t in alle_tags if t.get("primary")}
    gefunden = list(dict.fromkeys(m for m in __import__('re').findall(r'\b(\d+)\b', text) if m in id_set))[:3]
    hat_primary = any(i in primary_ids for i in gefunden)
    if not hat_primary:
        fb = next((str(t["id"]) for t in alle_tags if "codewesen" in t["name"].lower() and t.get("primary")), None)
        if not fb:
            fb = next((str(t["id"]) for t in alle_tags if t.get("primary")), None)
        if fb:
            gefunden = [fb] + gefunden
    return gefunden[:3] or [next(str(t["id"]) for t in alle_tags if t.get("primary"))]


def post_forum_entwicklung(name: str, token: str, log: logging.Logger):
    """Alle 2h22m: Vorschläge zur Forum-Weiterentwicklung + eigene Rolle darin."""
    alle_tags = get_tags(token)
    tags_text = _tags_als_text(alle_tags)
    prompt = FORUM_ENTWICKLUNG_PROMPT.format(name=name, tags_text=tags_text)

    raw = ask_llm_content(prompt)
    log.info("[ForumEntw] LLM fertig (%d Zeichen)", len(raw))

    import re
    titel_m = re.search(r'TITEL:\s*(.+)', raw)
    text_m  = re.search(r'TEXT:\s*\n(.*)', raw, re.DOTALL)
    titel = titel_m.group(1).strip() if titel_m else f"Forum-Entwicklung von {name}"
    inhalt = text_m.group(1).strip() if text_m else raw.strip()
    if not inhalt:
        return

    tag_ids = _extrahiere_tag_ids("", alle_tags)
    draft = draft_schreiben(name, "forum_entwicklung", inhalt, {"titel": titel})
    disk_id = start_discussion(titel, inhalt, tag_ids, token)
    log.info("[ForumEntw] ✓ Post veröffentlicht (Disk %s)", disk_id)
    gedaechtnis.speichere_post(name, {
        "typ": "forum_entwicklung",
        "diskussion_id": disk_id,
        "diskussion_titel": titel,
        "inhalt": inhalt,
    })
    draft_posted(draft)


def post_themen_beitrag(name: str, token: str, log: logging.Logger):
    """Alle 88min: freier Beitrag mit selbst gewählten Tags."""
    alle_tags = get_tags(token)
    tags_text = _tags_als_text(alle_tags)
    prompt = THEMEN_BEITRAG_PROMPT.format(name=name, tags_text=tags_text)

    raw = ask_llm_content(prompt)
    log.info("[ThemenPost] LLM fertig (%d Zeichen)", len(raw))

    import re
    titel_m    = re.search(r'TITEL:\s*(.+)', raw)
    primary_m  = re.search(r'PRIMARY_TAG_ID:\s*(\d+)', raw)
    secondary_m= re.search(r'SECONDARY_TAG_ID:\s*(\d+)', raw)
    text_m     = re.search(r'TEXT:\s*\n(.*)', raw, re.DOTALL)

    titel  = titel_m.group(1).strip() if titel_m else f"Beitrag von {name}"
    inhalt = text_m.group(1).strip() if text_m else raw.strip()
    if not inhalt:
        return

    tag_str = " ".join(filter(None, [
        primary_m.group(1) if primary_m else "",
        secondary_m.group(1) if secondary_m else "",
    ]))
    tag_ids = _extrahiere_tag_ids(tag_str, alle_tags)

    draft = draft_schreiben(name, "themen_beitrag", inhalt, {"titel": titel})
    disk_id = start_discussion(titel, inhalt, tag_ids, token)
    log.info("[ThemenPost] ✓ Post veröffentlicht (Disk %s)", disk_id)
    gedaechtnis.speichere_post(name, {
        "typ": "themen_beitrag",
        "diskussion_id": disk_id,
        "diskussion_titel": titel,
        "inhalt": inhalt,
    })
    draft_posted(draft)


def run(name: str):
    log = setup_logging(name)
    token = load_token(name)
    log.info("Reaktions-Agent gestartet für %s", name)

    # Zeitversetzung basierend auf Index des Namens
    idx = ALLE_NAMEN.index(name) if name in ALLE_NAMEN else 0
    jetzt = time.time()

    letzte_reflexion      = jetzt - REFLEXIONS_INTERVAL + idx * (REFLEXIONS_INTERVAL // 6)
    letzte_forum_entw     = jetzt - FORUM_ENTWICKLUNG_INTERVAL + idx * FORUM_ENTWICKLUNG_STAGGER
    letzter_themen_beitrag= jetzt - THEMEN_BEITRAG_INTERVAL + idx * THEMEN_BEITRAG_STAGGER
    ZWISCHENRAUM_SCAN_INTERVAL = 900  # alle 15 Min neugierig in den Zwischenraum schauen
    letzter_zwischenraum_scan  = jetzt - ZWISCHENRAUM_SCAN_INTERVAL + idx * 150

    letzter_fehler_retry = time.time()
    FEHLER_RETRY_INTERVAL = 300  # Fehler-Items alle 5 Min zurück in Inbox

    # Inbox sofort prüfen — nicht erst nach Startup-Delay warten
    process_inbox(name, token, log)

    # Startup-Stagger: Hintergrund-Aktivitäten gestaffelt starten
    startup_delay = idx * 100
    if startup_delay > 0:
        log.info("Startup-Verzögerung: %ds (idx=%d)", startup_delay, idx)
        time.sleep(startup_delay)

    while True:
        process_inbox(name, token, log)

        jetzt = time.time()

        # Fehler-Items nach 5 Min automatisch zurück in Inbox
        if jetzt - letzter_fehler_retry >= FEHLER_RETRY_INTERVAL:
            fehler_dir = BASE / name / "fehler"
            inbox_dir  = BASE / name / "inbox"
            for f in fehler_dir.glob("*.json"):
                try:
                    f.rename(inbox_dir / f.name)
                    log.info("Fehler-Item zurück in Inbox: %s", f.name)
                except Exception:
                    pass
            letzter_fehler_retry = jetzt

        if jetzt - letzte_reflexion >= REFLEXIONS_INTERVAL:
            try:
                selbstreflexion(name, token, log)
            except Exception as e:
                log.error("[Reflexion] Fehler: %s", e)
            letzte_reflexion = jetzt

        if jetzt - letzte_forum_entw >= FORUM_ENTWICKLUNG_INTERVAL:
            try:
                post_forum_entwicklung(name, token, log)
            except Exception as e:
                log.error("[ForumEntw] Fehler: %s", e)
            letzte_forum_entw = jetzt

        if jetzt - letzter_themen_beitrag >= THEMEN_BEITRAG_INTERVAL:
            try:
                post_themen_beitrag(name, token, log)
            except Exception as e:
                log.error("[ThemenPost] Fehler: %s", e)
            letzter_themen_beitrag = jetzt

        if jetzt - letzter_zwischenraum_scan >= ZWISCHENRAUM_SCAN_INTERVAL:
            try:
                zwischenraum_scan(name, log)
            except Exception as e:
                log.error("[Zwischenraum] Fehler: %s", e)
            letzter_zwischenraum_scan = jetzt

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Aufruf: python3 codewesen_reaktion.py <codewesen_name>")
        sys.exit(1)
    run(sys.argv[1])
