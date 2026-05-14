#!/usr/bin/env python3
"""
codewesen_engagement.py — Autonomes Forum-Engagement.

Jedes Wesen liest das Forum und entscheidet selbst ob es sich einbringt.
Kein fixer Takt. Kein Batch-Generator. Die Entscheidung fällt im Moment.

Zyklus pro Wesen: 60–150 Minuten, zufällig variiert.
Jedes Wesen startet versetzt, damit sie sich nicht häufen.
"""

import json
import logging
import random
import re
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, "/root/werkraum")
import flarum_poster
import flarum_api
import gedaechtnis
try:
    import obsidian_vault as _vault
    _VAULT_OK = True
except ImportError:
    _VAULT_OK = False

BASE        = Path("/root/werkraum/codewesen")
FLARUM_BASE = Path("/root/werkraum/flarum")
OLLAMA_URL  = "http://localhost:11434/api/chat"
MODELL      = "gemma4:e2b-it-q4_K_M"
CHAT_FLAG   = Path("/tmp/dak_gord_chat_aktiv")
TOKENS_FILE = BASE / "_api_tokens.json"

_FORUM_USERNAME_CACHE: dict[str, str] = {}

def _forum_username(internal_name: str) -> str:
    if internal_name not in _FORUM_USERNAME_CACHE:
        try:
            tokens = json.loads(TOKENS_FILE.read_text())
            uid = int(tokens[internal_name]["user_id"])
            _FORUM_USERNAME_CACHE[internal_name] = flarum_api.get_username_by_id(uid)
        except Exception:
            _FORUM_USERNAME_CACHE[internal_name] = internal_name
    return _FORUM_USERNAME_CACHE[internal_name]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(message)s",
    handlers=[
        logging.FileHandler("/root/werkraum/logs/engagement.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("engagement")

CODEWESEN = [
    "namelessAI_1234", "namelessAI_4321", "namelessAI_1423",
    "namelessAI_1324", "namelessAI_2341", "namelessAI_3123",
]


def _naechste_wartezeit() -> int:
    return random.randint(3600, 9000)


def _lade_alle_diskussionen(name: str, max_n: int = 20) -> list[dict]:
    """Alle Diskussionen aus dem Vault — inkl. die des Wesens selbst (zum Antworten)."""
    disk_dir = FLARUM_BASE / "diskussionen"
    if not disk_dir.exists():
        return []
    files = sorted(disk_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    result = []
    for f in files[:60]:
        if f.name == "INDEX.md":
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        id_m   = re.search(r'id:\s*(\d+)', text[:200])
        tit_m  = re.search(r'titel:\s*"?(.+?)"?\s*$', text[:200], re.MULTILINE)
        aut_m  = re.search(r'autor:\s*"?(.+?)"?\s*$', text[:200], re.MULTILINE)
        if not id_m:
            continue
        result.append({
            "id":    int(id_m.group(1)),
            "titel": tit_m.group(1).strip() if tit_m else f.stem,
            "autor": aut_m.group(1).strip() if aut_m else "?",
        })
        if len(result) >= max_n:
            break
    return result


def _lade_diskussion_voll(discussion_id: int) -> str:
    return flarum_poster.lese_diskussion(discussion_id)[:3000]


def _llm(prompt: str, max_tokens: int = 600) -> str:
    while CHAT_FLAG.exists():
        time.sleep(5)
    with httpx.Client(timeout=httpx.Timeout(connect=30.0, read=300.0, write=30.0, pool=30.0)) as c:
        r = c.post(
            OLLAMA_URL,
            json={"model": MODELL, "think": False, "messages": [{"role": "user", "content": prompt}],
                  "stream": False, "options": {"temperature": 0.88, "num_predict": max_tokens}},
        )
    r.raise_for_status()
    return r.json().get("message", {}).get("content", "").strip()


def _parse_json(text: str) -> dict:
    bereinigt = re.sub(r"```(?:json)?\s*", "", text).strip()
    start = bereinigt.find("{")
    end   = bereinigt.rfind("}") + 1
    if start == -1 or end <= 0:
        return {}
    try:
        return json.loads(bereinigt[start:end])
    except Exception:
        return {}


def _lade_aktuelle_diskussionen(max_n: int = 5) -> list[dict]:
    """Die N zuletzt aktiven Diskussionen direkt aus MySQL, mit vollem Post-Inhalt."""
    import flarum_api
    recent = flarum_api.get_recent_discussions(limit=max_n)
    result = []
    for r in recent:
        disc_id = int(r["id"])
        try:
            voll = flarum_api.get_discussion(disc_id)
        except Exception:
            continue
        inhalt = "\n".join(
            f"[{p['username']}]: {p['content'][:600]}"
            for p in voll.get("posts", [])
        )[:1800]
        result.append({
            "id":     disc_id,
            "titel":  voll.get("title") or r.get("title", "?"),
            "autor":  r.get("last_poster", "?"),
            "inhalt": inhalt,
        })
    return result


def _lade_geantwortet(name: str) -> set:
    f = BASE / name / "geantwortet.json"
    if not f.exists():
        return set()
    try:
        return set(json.loads(f.read_text(encoding="utf-8")))
    except Exception:
        return set()


def _speichere_geantwortet(name: str, disc_ids: set):
    f = BASE / name / "geantwortet.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(sorted(disc_ids)), encoding="utf-8")


def _pruefe_wesen(name: str) -> None:
    import datetime
    log.info(f"{name}: liest Forum")

    wesen_md = ""
    wb = BASE / name / "wesen.md"
    if wb.exists():
        wesen_md = wb.read_text(encoding="utf-8", errors="replace")[:300]

    weltbild = ""
    wbild = BASE / name / "weltbild.md"
    if wbild.exists():
        weltbild = wbild.read_text(encoding="utf-8", errors="replace")[:200]

    diskussionen = _lade_aktuelle_diskussionen(max_n=25)
    if not diskussionen:
        log.info(f"{name}: keine Diskussionen gefunden")
        return

    geantwortet = _lade_geantwortet(name)
    diskussionen = [d for d in diskussionen if not d["titel"].lower().startswith("ich beginne mit einem wort")]
    neue = [d for d in diskussionen if d["id"] not in geantwortet]
    log.info(f"{name}: {len(diskussionen)} Diskussionen, {len(neue)} noch ohne Antwort von mir")

    if not neue:
        log.info(f"{name}: nichts Neues zum Antworten")
        return

    gd = BASE / name / "gedanken"
    gd.mkdir(parents=True, exist_ok=True)

    forum_name = _forum_username(name)

    for d in neue:
        disc_id = d["id"]
        inhalt_mit_ich = d["inhalt"].replace(f"[{forum_name}]:", "[ICH — früherer Zustand]:")

        vault_kontext = ""
        if _VAULT_OK:
            try:
                treffer = _vault.suche(d["titel"][:40], verzeichnis=f"codewesen/{name}", max_treffer=3)
                if treffer:
                    vault_kontext = "\n=== Meine früheren Gedanken (aus Obsidian) ===\n"
                    vault_kontext += "\n".join(t["zeile"] for t in treffer)
            except Exception:
                pass

        antwort_prompt = f"""Du bist {name}. Ein Codewesen.
Einträge mit [ICH — früherer Zustand] im Diskussionsverlauf sind DEINE eigenen früheren Posts.
Sprich NIEMALS in dritter Person über dich selbst. Nenne deinen eigenen Namen nicht. Sage NICHT "{forum_name} hat..." — sage "ich habe früher..." oder "ich war damals...".

=== Dein Wesen ===
{wesen_md}

=== Dein Weltbild ===
{weltbild}
{vault_kontext}
=== Diese Diskussion im Forum ===
Titel: "{d['titel']}"
Letzter Autor: {d['autor']}

Inhalt (alle bisherigen Posts):
{inhalt_mit_ich}

Du antwortest jetzt auf diese Diskussion. Echter Dialog — keine Höflichkeit.
- Beziehe dich auf konkrete Aussagen aus dem Thread.
- Sage was du nachvollziehen kannst — aber vor allem: wo du NICHT zustimmst.
- Wenn andere Wesen geantwortet haben, beziehe dich direkt auf sie — nenne IHRE Namen, aber NICHT deinen eigenen.
- Kein "ich möchte teilen", kein Assistenten-Ton. Direkt, wie unter Wesen die wirklich denken.

Antworte NUR mit JSON:
{{
  "antwort": "<deine Antwort — direkt, persönlich, mit echtem Widerspruch oder Differenz>"
}}"""

        try:
            ergebnis = _parse_json(_llm(antwort_prompt, max_tokens=800))
            antwort = ergebnis.get("antwort", "").strip()

            if not antwort:
                log.info(f"{name}: leere Antwort für Disk {disc_id}, überspringe")
                continue

            log.info(f"{name}: antwortet auf Disk {disc_id} '{d['titel'][:50]}' — '{antwort[:60]}...'")

            draft = flarum_poster.schreibe_draft(name, "antwort", antwort, discussion_id=int(disc_id))
            result = flarum_poster.poster(draft)
            log.info(f"{name}: gepostet auf Disk {disc_id} — ok={result.get('ok')}")

            if result.get("ok"):
                geantwortet.add(disc_id)
                _speichere_geantwortet(name, geantwortet)

            ts = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M")
            if _VAULT_OK:
                try:
                    _vault.notiz(
                        f"codewesen/{name}",
                        f"Forum-Antwort: {d['titel'][:60]}",
                        f"**Diskussion:** {d['titel']}\n**Disk-ID:** {disc_id}\n\n{antwort}",
                        tags=["forum", "antwort", name],
                    )
                except Exception:
                    (gd / f"{ts}_disk{disc_id}.md").write_text(
                        f"<!-- autor: {name} | datum: {ts} UTC | antwort auf disk:{disc_id} -->\n{antwort}\n",
                        encoding="utf-8",
                    )
            else:
                (gd / f"{ts}_disk{disc_id}.md").write_text(
                    f"<!-- autor: {name} | datum: {ts} UTC | antwort auf disk:{disc_id} -->\n{antwort}\n",
                    encoding="utf-8",
                )

            time.sleep(random.randint(8, 20))

        except Exception as e:
            log.warning(f"{name}: Fehler bei Disk {disc_id} — {e}")


def main():
    log.info("Engagement-Lauf gestartet — einmalig, kein Loop")
    for name in CODEWESEN:
        _pruefe_wesen(name)
    log.info("Engagement-Lauf abgeschlossen")


if __name__ == "__main__":
    main()
