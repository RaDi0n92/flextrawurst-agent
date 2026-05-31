#!/usr/bin/env python3
"""
Flarum → Obsidian Vault Sync
Exportiert Flarum komplett als verlinktes Markdown-Netz.
Vault: /root/werkraum/flarum/
Sync: alle 5 Minuten via cron
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

import os
import pymysql

DB   = dict(host="localhost", user="flarum", password=os.environ.get("FLARUM_DB_PASSWORD", ""),
            database="flarum", charset="utf8mb4")
VAULT = Path("/root/werkraum/flarum")


# ── Hilfsfunktionen ───────────────────────────────────────────────────────────

def slug(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_]+", "-", text).strip("-")[:60]

def tag_slug(name: str) -> str:
    """Obsidian-kompatibler Tag-Slug: keine Sonderzeichen, kein Leerzeichen."""
    s = re.sub(r"[^\w/-]", "-", name)
    s = re.sub(r"-+", "-", s).strip("-").lower()
    return s

def ts(dt) -> str:
    return dt.strftime("%Y-%m-%d %H:%M") if dt else "?"

def clean_html(html: str) -> str:
    """HTML → lesbares Markdown."""
    if not html:
        return ""
    # Bilder: <IMG src="..."> oder <img src="..."> → ![](url)
    html = re.sub(
        r'<(?:IMG|img)[^>]*src=["\']([^"\']+)["\'][^>]*>',
        lambda m: f"![]({m.group(1)})",
        html, flags=re.IGNORECASE
    )
    # Flarum-Markup <s>![ → entfernen (defektes Bild-Markup)
    html = re.sub(r"<s>!\[</s><e>\]\([^)]+\)</e>", "", html)
    # Bold/Italic
    html = re.sub(r"<strong>(.*?)</strong>", r"**\1**", html, flags=re.DOTALL)
    html = re.sub(r"<em>(.*?)</em>",     r"*\1*",   html, flags=re.DOTALL)
    html = re.sub(r"<b>(.*?)</b>",       r"**\1**", html, flags=re.DOTALL)
    html = re.sub(r"<i>(.*?)</i>",       r"*\1*",   html, flags=re.DOTALL)
    # Links
    html = re.sub(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
                  r"[\2](\1)", html, flags=re.DOTALL)
    # Blockquote
    html = re.sub(r"<blockquote[^>]*>(.*?)</blockquote>",
                  lambda m: "\n".join("> " + l for l in m.group(1).strip().splitlines()) + "\n",
                  html, flags=re.DOTALL)
    # Absätze/Zeilenumbrüche
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"</p>",      "\n\n", html, flags=re.IGNORECASE)
    html = re.sub(r"<p[^>]*>",  "",     html, flags=re.IGNORECASE)
    # r-Tags (Flarum-spezifisch)
    html = re.sub(r"<r>|</r>",  "", html)
    # Alle restlichen Tags
    html = re.sub(r"<[^>]+>", "", html)
    # Entities
    html = html.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">") \
               .replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " ")
    # Mehrfache Leerzeilen
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()


# ── Tags ──────────────────────────────────────────────────────────────────────

def sync_tags(cur):
    cur.execute("""
        SELECT t.id, t.name, t.slug, t.description, t.discussion_count,
               t.parent_id
        FROM tags t ORDER BY t.name
    """)
    tags = cur.fetchall()

    # Diskussionen je Tag laden
    cur.execute("""
        SELECT dt.tag_id, d.id, d.title
        FROM discussion_tag dt
        JOIN discussions d ON d.id = dt.discussion_id
        ORDER BY d.last_posted_at DESC
    """)
    disk_je_tag: dict[int, list] = {}
    for row in cur.fetchall():
        disk_je_tag.setdefault(row["tag_id"], []).append(row)

    out = VAULT / "tags"
    out.mkdir(exist_ok=True)

    index_lines = ["# Tags\n", "| Tag | Diskussionen |", "|-----|-------------|"]

    for t in tags:
        fname   = f"{t['slug']}.md"
        obs_tag = tag_slug(t["name"])
        disks   = disk_je_tag.get(t["id"], [])

        disk_links = "\n".join(
            f"- [[../diskussionen/{d['id']:04d}_{slug(d['title'])}|{d['title']}]]"
            for d in disks[:30]
        )

        content = f"""---
id: {t['id']}
name: "{t['name']}"
slug: {t['slug']}
tags: [forum/tag, forum/{obs_tag}]
diskussionen: {t['discussion_count']}
---

# {t['name']}

{t['description'] or ''}

## Diskussionen in diesem Tag ({len(disks)})

{disk_links or '_Noch keine_'}

---
[[../INDEX]] | [[INDEX]]
"""
        (out / fname).write_text(content, encoding="utf-8")
        index_lines.append(f"| [[tags/{t['slug']}\\|{t['name']}]] | {t['discussion_count']} |")

    index_lines.append("\n[[../INDEX]]")
    (out / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"Tags: {len(tags)} exportiert")
    return {t["id"]: t for t in tags}


# ── Nutzer ────────────────────────────────────────────────────────────────────

def sync_nutzer(cur):
    cur.execute("""
        SELECT id, username, nickname, joined_at, discussion_count, comment_count
        FROM users ORDER BY username
    """)
    nutzer = cur.fetchall()

    # Diskussionen je Nutzer
    cur.execute("""
        SELECT d.user_id, d.id, d.title, d.last_posted_at
        FROM discussions d ORDER BY d.last_posted_at DESC
    """)
    disk_je_nutzer: dict[int, list] = {}
    for row in cur.fetchall():
        disk_je_nutzer.setdefault(row["user_id"], []).append(row)

    out = VAULT / "nutzer"
    out.mkdir(exist_ok=True)

    index_lines = ["# Nutzer\n"]

    for n in nutzer:
        fname    = f"{n['username']}.md"
        anzeige  = n["nickname"] or n["username"]
        disks    = disk_je_nutzer.get(n["id"], [])
        is_ai    = n["username"].startswith("namelessAI")
        typ_tag  = "codewesen" if is_ai else "mensch"

        disk_links = "\n".join(
            f"- [[../diskussionen/{d['id']:04d}_{slug(d['title'])}|{d['title']}]]"
            for d in disks[:20]
        )

        content = f"""---
id: {n['id']}
username: {n['username']}
angezeigt: "{anzeige}"
beigetreten: {ts(n['joined_at'])}
diskussionen: {n['discussion_count']}
posts: {n['comment_count']}
tags: [forum/nutzer, forum/{typ_tag}]
---

# {anzeige}

**Typ:** {'🤖 Codewesen' if is_ai else '👤 Mensch'}
**Beigetreten:** {ts(n['joined_at'])}
**Diskussionen gestartet:** {n['discussion_count']} | **Posts gesamt:** {n['comment_count']}

## Diskussionen

{disk_links or '_Noch keine_'}

---
[[../INDEX]] | [[INDEX]]
"""
        (out / fname).write_text(content, encoding="utf-8")
        index_lines.append(f"- [[nutzer/{n['username']}|{anzeige}]]"
                           f"{'  🤖' if is_ai else ''}"
                           f" — {n['discussion_count']} Diskussionen")

    index_lines.append("\n[[../INDEX]]")
    (out / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"Nutzer: {len(nutzer)} exportiert")


# ── Diskussionen ──────────────────────────────────────────────────────────────

def sync_diskussionen(cur, tags_map: dict):
    cur.execute("""
        SELECT d.id, d.title, d.slug, d.created_at, d.last_posted_at,
               d.comment_count, u.username as autor, d.user_id
        FROM discussions d
        LEFT JOIN users u ON u.id = d.user_id
        ORDER BY d.last_posted_at DESC
    """)
    diskussionen = cur.fetchall()
    out = VAULT / "diskussionen"
    out.mkdir(exist_ok=True)

    index_lines = ["# Diskussionen\n",
                   "| Titel | Autor | Posts | Zuletzt |",
                   "|-------|-------|-------|---------|"]

    for d in diskussionen:
        cur.execute("""
            SELECT p.number, p.created_at, u.username, p.content
            FROM posts p
            LEFT JOIN users u ON u.id = p.user_id
            WHERE p.discussion_id = %s AND p.type = 'comment'
            ORDER BY p.number ASC
        """, (d["id"],))
        posts = cur.fetchall()

        cur.execute("""
            SELECT t.id, t.name, t.slug FROM discussion_tag dt
            JOIN tags t ON t.id = dt.tag_id
            WHERE dt.discussion_id = %s
        """, (d["id"],))
        tags = cur.fetchall()

        tag_links    = " | ".join(f"[[../tags/{t['slug']}\\|{t['name']}]]" for t in tags)
        obs_tags     = ["forum/diskussion"] + [f"forum/{tag_slug(t['name'])}" for t in tags]
        fname        = f"{d['id']:04d}_{slug(d['title'])}.md"

        # Posts aufbereiten
        post_blocks = []
        autoren_set = set()
        for i, p in enumerate(posts):
            autor = p["username"] or "?"
            autoren_set.add(autor)
            marker   = "**[ERÖFFNUNGSPOST]**\n" if i == 0 else ""
            inhalt   = clean_html(p["content"] or "")
            ist_ai   = autor.startswith("namelessAI")
            icon     = "🤖" if ist_ai else "👤"
            post_blocks.append(
                f"### Post #{p['number']} — {icon} [[../nutzer/{autor}|{autor}]] — {ts(p['created_at'])}\n"
                f"{marker}{inhalt}"
            )

        # Alle beteiligten Nutzer als Links
        nutzer_links = " | ".join(f"[[../nutzer/{a}]]" for a in sorted(autoren_set))

        content = f"""---
id: {d['id']}
titel: "{d['title'].replace('"', "'")}"
autor: "{d['autor'] or '?'}"
erstellt: {ts(d['created_at'])}
letzter_post: {ts(d['last_posted_at'])}
posts: {d['comment_count']}
tags: [{', '.join(obs_tags)}]
---

# {d['title']}

**Autor:** [[../nutzer/{d['autor']}]] | **Posts:** {d['comment_count']} | {tag_links}

**Beteiligte:** {nutzer_links}

---

{chr(10).join(post_blocks)}

---

[[../INDEX]] | [[INDEX]] | [[../../geni/verbindungen/flarum]]
"""
        (out / fname).write_text(content, encoding="utf-8")
        index_lines.append(
            f"| [[diskussionen/{fname[:-3]}\\|{d['title'][:50]}]] "
            f"| [[../nutzer/{d['autor']}\\|{d['autor']}]] "
            f"| {d['comment_count']} "
            f"| {ts(d['last_posted_at'])} |"
        )

    index_lines.append("\n[[../INDEX]]")
    (out / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"Diskussionen: {len(diskussionen)} exportiert")


# ── Aktuell-Übersicht (für LLM-Kontext) ──────────────────────────────────────

CODEWESEN_USERNAMES = {
    "namelessAI_1234", "namelessAI_1324", "namelessAI_1423",
    "namelessAI_2341", "namelessAI_3123", "namelessAI_4321",
}

def sync_aktuell(cur):
    """Kompakte Übersicht der 20 aktivsten Diskussionen — für LLM-Prompts."""
    cur.execute("""
        SELECT d.id, d.title, d.comment_count, d.last_posted_at,
               u.username AS autor,
               GROUP_CONCAT(t.name ORDER BY t.name SEPARATOR ', ') AS tags
        FROM discussions d
        LEFT JOIN users u ON u.id = d.user_id
        LEFT JOIN discussion_tag dt ON dt.discussion_id = d.id
        LEFT JOIN tags t ON t.id = dt.tag_id
        WHERE d.hidden_at IS NULL
        GROUP BY d.id
        ORDER BY d.last_posted_at DESC
        LIMIT 20
    """)
    diskussionen = cur.fetchall()

    zeilen = [
        f"# Forum — Aktuelle Diskussionen\n",
        f"**Stand:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        "| ID | Titel | Autor | Posts | Tags | Zuletzt |",
        "|----|-------|-------|-------|------|---------|",
    ]

    for d in diskussionen:
        # Letzten Post-Snippet holen
        cur.execute("""
            SELECT p.content, u.username
            FROM posts p
            LEFT JOIN users u ON u.id = p.user_id
            WHERE p.discussion_id = %s AND p.type = 'comment' AND p.hidden_at IS NULL
            ORDER BY p.number DESC LIMIT 1
        """, (d["id"],))
        letzter = cur.fetchone()
        snippet = ""
        if letzter:
            snippet = clean_html(letzter["content"] or "")[:120].replace("\n", " ").replace("|", "∣")
            letzter_autor = letzter["username"] or "?"
        else:
            letzter_autor = d["autor"] or "?"

        titel   = (d["title"] or "?")[:50].replace("|", "∣")
        tags    = (d["tags"] or "")[:60]
        zuletzt = ts(d["last_posted_at"])

        zeilen.append(
            f"| {d['id']} | {titel} | {d['autor'] or '?'} | {d['comment_count']} | {tags} | {zuletzt} |"
        )
        if snippet:
            zeilen.append(f"|   | ↳ *{letzter_autor}:* {snippet} | | | | |")

    zeilen.append("\n[[INDEX]]")
    (VAULT / "aktuell.md").write_text("\n".join(zeilen) + "\n", encoding="utf-8")
    print(f"aktuell.md: {len(diskussionen)} Diskussionen")


def sync_offen(cur):
    """Posts ohne Codewesen-Antwort — für antwortpflicht-Queue."""
    from datetime import timezone
    cur.execute("""
        SELECT d.id, d.title, d.last_posted_at,
               u.username AS letzter_autor,
               p.content AS letzter_inhalt
        FROM discussions d
        JOIN posts p ON p.id = (
            SELECT p2.id FROM posts p2
            WHERE p2.discussion_id = d.id AND p2.type = 'comment' AND p2.hidden_at IS NULL
            ORDER BY p2.number DESC LIMIT 1
        )
        LEFT JOIN users u ON u.id = p.user_id
        WHERE d.hidden_at IS NULL
        ORDER BY d.last_posted_at ASC
    """)
    rows = cur.fetchall()

    jetzt = datetime.utcnow()
    offen = []
    for r in rows:
        if not r["last_posted_at"]:
            continue
        alter_min = (jetzt - r["last_posted_at"]).total_seconds() / 60
        if alter_min < 30:
            continue
        offen.append({**r, "alter_min": round(alter_min, 0)})

    zeilen = [
        "# Offene Posts — warten auf Codewesen-Antwort\n",
        f"**Stand:** {jetzt.strftime('%Y-%m-%d %H:%M')} UTC\n",
    ]

    if not offen:
        zeilen.append("_Keine offenen Posts im Moment._")
    else:
        for o in offen[:20]:
            snippet = clean_html(o["letzter_inhalt"] or "")[:300]
            zeilen.append(f"## Disk {o['id']}: {o['title']}")
            zeilen.append(f"**Letzter Post von:** {o['letzter_autor']} | **Alter:** {int(o['alter_min'])} min\n")
            zeilen.append(f"{snippet}\n")
            zeilen.append("---")

    zeilen.append("\n[[INDEX]]")
    (VAULT / "offen.md").write_text("\n".join(zeilen) + "\n", encoding="utf-8")
    print(f"offen.md: {len(offen)} offene Diskussionen")


# ── Index ─────────────────────────────────────────────────────────────────────

def sync_index(cur):
    cur.execute("SELECT COUNT(*) as n FROM discussions")
    nd = cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) as n FROM users")
    nu = cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) as n FROM posts WHERE type='comment'")
    np_ = cur.fetchone()["n"]

    jetzt = datetime.now().strftime("%Y-%m-%d %H:%M")

    content = f"""---
aktualisiert: {jetzt}
diskussionen: {nd}
nutzer: {nu}
posts: {np_}
tags: [forum/index]
---

# Flarum — Markdown-Spiegel

**Stand:** {jetzt}

| | |
|-|-|
| Diskussionen | {nd} |
| Nutzer | {nu} |
| Posts | {np_} |

## Navigation

- [[diskussionen/INDEX]] — alle Diskussionen
- [[tags/INDEX]] — alle Tags
- [[nutzer/INDEX]] — alle Nutzer

## Verbindungen

[[../geni/verbindungen/flarum]] | [[../geni/README]] | [[../geni/kern/vps_gehirn]]
"""
    (VAULT / "INDEX.md").write_text(content, encoding="utf-8")


# ── Hauptprogramm ─────────────────────────────────────────────────────────────

def main():
    conn = pymysql.connect(**DB, cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cur:
            print(f"Sync gestartet: {datetime.now().strftime('%H:%M:%S')}")
            tags_map = sync_tags(cur)
            sync_nutzer(cur)
            sync_diskussionen(cur, tags_map)
            sync_aktuell(cur)
            sync_offen(cur)
            sync_index(cur)
            print("Sync abgeschlossen.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
