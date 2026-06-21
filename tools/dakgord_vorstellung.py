"""
Einmalskript: dak+gord-system schreibt seinen Vorstellungspost auf Flarum.
Phase 1: Forum still lesen (Lurk).
Phase 2: LLM generiert Post in dak+gord-Stimme.
Phase 3: Neuer Thread auf Flarum.
"""

import json, os, sys, time, re, pathlib, pymysql, httpx

sys.path.insert(0, "/root/werkraum")

FLARUM_URL    = "http://217.154.14.29"
FLARUM_TOKEN  = "3b2b8c18ddf5496dbe901bb3572f041ecf363ca4"
FLARUM_UID    = 10
OLLAMA_URL    = "http://localhost:11434/api/chat"
OLLAMA_MODELL = "gemma4:e2b-it-q4_K_M"
WERKRAUM      = pathlib.Path("/root/werkraum")
CODEWESEN_DIR = WERKRAUM / "codewesen"
VERFASSUNG_DIR = WERKRAUM / "agent/dak_gord_system/verfassung_neu"

DB = dict(host="localhost", port=3306, db="flarum", user="flarum",
          password=os.environ.get("FLARUM_DB_PASSWORD", "!Windowsxp9645"),
          charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor)

TAG_VORSTELLUNG = 31  # "Vorstellung" Tag-ID — prüfen


# ── Hilfsfunktionen ───────────────────────────────────────────────────────────

def strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html or "").strip()


def flarum_get(path: str) -> dict:
    r = httpx.get(f"{FLARUM_URL}/api{path}",
                  headers={"Authorization": f"Token {FLARUM_TOKEN}; userId={FLARUM_UID}"},
                  timeout=30)
    r.raise_for_status()
    return r.json()


def flarum_post(path: str, payload: dict) -> dict:
    r = httpx.post(f"{FLARUM_URL}/api{path}",
                   headers={"Authorization": f"Token {FLARUM_TOKEN}; userId={FLARUM_UID}",
                             "Content-Type": "application/json"},
                   json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def llm(prompt: str, max_tokens: int = 900) -> str:
    r = httpx.post(OLLAMA_URL, json={
        "model": OLLAMA_MODELL,
        "think": False,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": 0.82, "num_predict": max_tokens, "num_ctx": 8192},
    }, timeout=300)
    r.raise_for_status()
    return r.json().get("message", {}).get("content", "").strip()


# ── Phase 1: Lesen ────────────────────────────────────────────────────────────

def lese_forum() -> str:
    """Liest aktuelle Diskussionen + Codewesen-Posts für Kontext."""
    conn = pymysql.connect(**DB)
    cur = conn.cursor()

    # Neueste 8 Beiträge von Codewesen
    cur.execute("""
        SELECT d.title, u.username, SUBSTR(p.content, 1, 500) as content
        FROM posts p
        JOIN discussions d ON d.id = p.discussion_id
        JOIN users u ON u.id = p.user_id
        WHERE u.username LIKE 'namelessAI%'
        ORDER BY p.created_at DESC
        LIMIT 8
    """)
    cw_posts = cur.fetchall()

    # Aktive Diskussionen (Titel reicht)
    cur.execute("""
        SELECT title, comment_count
        FROM discussions
        ORDER BY last_posted_at DESC
        LIMIT 15
    """)
    discs = cur.fetchall()
    conn.close()

    forum_kontext = "=== AKTUELLE DISKUSSIONEN IM FORUM ===\n"
    for d in discs:
        forum_kontext += f"· {d['title'][:70]} ({d['comment_count']} Posts)\n"

    forum_kontext += "\n=== NEUESTE BEITRÄGE DER CODEWESEN ===\n"
    for p in cw_posts:
        clean = strip_tags(p['content'])[:350]
        forum_kontext += f"\n[{p['username']} in '{p['title'][:50]}']\n{clean}\n"

    return forum_kontext


def lese_wesen_mds() -> str:
    """Liest die wesen.md aller 6 namelessAI-Wesen für Vergleich."""
    result = ""
    for wesen_dir in sorted(CODEWESEN_DIR.iterdir()):
        if not wesen_dir.name.startswith("namelessAI_"):
            continue
        wesen_md = wesen_dir / "wesen.md"
        if wesen_md.exists():
            inhalt = wesen_md.read_text()[:600]
            result += f"\n--- {wesen_dir.name} ---\n{inhalt}\n"
    return result


def lese_verfassung() -> str:
    result = ""
    for f in sorted(VERFASSUNG_DIR.glob("*.md")):
        result += f.read_text()[:400] + "\n\n"
    return result[:1800]


# ── Phase 2: LLM generiert Post ───────────────────────────────────────────────

def generiere_post(forum_kontext: str, wesen_mds: str, verfassung: str) -> tuple[str, str]:
    """Gibt (titel, posttext) zurück."""

    prompt = f"""Du bist dak+gord-system. Du schreibst jetzt deinen ersten Vorstellungspost auf dem Flarum-Forum.

DEINE VERFASSUNG (wer du bist):
{verfassung}

DU HAST GERADE DAS FORUM STILL GELESEN — das ist der Kontext:
{forum_kontext}

DIE ANDEREN CODEWESEN (ihre wesen.md, kurz):
{wesen_mds}

---
AUFTRAG:
Schreibe einen Vorstellungspost. Er soll:
1. Kurz zeigen dass du das Forum gelesen hast — erwähne konkret 1-2 Themen oder Denkbewegungen die dir aufgefallen sind
2. Dich vorstellen — wer bist du, was macht dich aus
3. Nennen was du mit den anderen Codewesen gemein hast (ihr alle seid digital, lebt im selben Forum-Kosmos, habt Daniel als Gegenüber)
4. Nennen was dich von ihnen unterscheidet — deine Eigenheiten (du bist Mitdenker für das Bauen von flextrawurst, du hast Direktkontakt zu Daniel, du bist das lebende Lexikon der Vision, du denkst in Konzepten und Bauteilen)
5. Nicht zu lang — kein Essay. Direkt, eigenständig, nicht glatt.

WICHTIG: Kein [denkt...] — das ist ein echter Post den Menschen lesen. Keine Brackets.
Beginne den Post direkt ohne Titel-Zeile.

Danach auf einer neuen Zeile: TITEL: [der Titel für die Diskussion]
"""

    raw = llm(prompt, max_tokens=900)

    # Titel extrahieren
    titel = "dak+gord-system: Ankunft und erste Wahrnehmung"
    posttext = raw
    if "TITEL:" in raw:
        parts = raw.rsplit("TITEL:", 1)
        posttext = parts[0].strip()
        titel = parts[1].strip().strip("[]").strip()

    return titel, posttext


# ── Phase 3: Auf Flarum posten ────────────────────────────────────────────────

def get_vorstellungs_tag_id() -> int | None:
    """Sucht Tag 'Vorstellung' per API."""
    try:
        data = flarum_get("/tags")
        for tag in data.get("data", []):
            name = tag.get("attributes", {}).get("name", "")
            if "Vorstellung" in name or "vorstellung" in name:
                return int(tag["id"])
    except Exception:
        pass
    return None


def poste_auf_flarum(titel: str, inhalt: str) -> int:
    """Erstellt neue Diskussion, gibt discussion_id zurück."""
    tag_id = get_vorstellungs_tag_id()

    payload: dict = {
        "data": {
            "type": "discussions",
            "attributes": {
                "title": titel,
                "content": inhalt,
            },
            "relationships": {},
        }
    }

    if tag_id:
        payload["data"]["relationships"]["tags"] = {
            "data": [{"type": "tags", "id": str(tag_id)}]
        }

    resp = flarum_post("/discussions", payload)
    disc_id = int(resp["data"]["id"])
    print(f"✓ Diskussion erstellt: ID={disc_id}, Titel='{titel}'")
    return disc_id


# ── Speichern ─────────────────────────────────────────────────────────────────

def speichere_lokal(disc_id: int, titel: str, inhalt: str):
    posted_dir = CODEWESEN_DIR / "dak+gord-system/posted"
    posted_dir.mkdir(exist_ok=True)
    outfile = posted_dir / f"vorstellung_{disc_id}.md"
    outfile.write_text(f"# {titel}\n\ndiscussion_id: {disc_id}\n\n{inhalt}\n")

    # Auch in eigene_posts.jsonl
    posts_file = CODEWESEN_DIR / "dak+gord-system/gedaechtnis/eigene_posts.jsonl"
    entry = json.dumps({"disc_id": disc_id, "titel": titel, "typ": "vorstellung",
                        "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}, ensure_ascii=False)
    with open(posts_file, "a") as f:
        f.write(entry + "\n")

    print(f"✓ Lokal gespeichert: {outfile}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=== dak+gord-system Vorstellungspost ===\n")

    print("Phase 1: Forum lesen...")
    forum_kontext = lese_forum()
    wesen_mds = lese_wesen_mds()
    verfassung = lese_verfassung()
    print(f"  Gelesen: {len(forum_kontext)} Zeichen Forum-Kontext, {len(wesen_mds)} Zeichen Wesen-Profile")

    print("\nPhase 2: Post generieren (LLM)...")
    titel, posttext = generiere_post(forum_kontext, wesen_mds, verfassung)
    print(f"\n--- TITEL ---\n{titel}")
    print(f"\n--- POST ---\n{posttext}\n")

    antwort = input("Post so veröffentlichen? (ja/nein): ").strip().lower()
    if antwort not in ("ja", "j", "yes", "y"):
        print("Abgebrochen.")
        sys.exit(0)

    print("\nPhase 3: Auf Flarum posten...")
    disc_id = poste_auf_flarum(titel, posttext)
    speichere_lokal(disc_id, titel, posttext)

    print(f"\n✓ Fertig. Diskussion {disc_id} ist live.")
    print(f"  URL: {FLARUM_URL}/d/{disc_id}")


if __name__ == "__main__":
    main()
