#!/usr/bin/env python3
"""
flarum_export.py — Flarum-Export: EINE einzige self-contained HTML-Datei

Alles in einer Datei:
  - JSON mit allen Diskussionen + Posts eingebettet
  - Tag-Tabs, Suche, Diskussion-Ansicht — alles client-side JS
  - Kein Server, keine anderen Dateien nötig

Aufruf:
  python3 flarum_export.py [ausgabedatei]
  Standard: /root/werkraum/flarum-export/flarum.html
"""

import html as H
import json
import os
import re
import sys
import pymysql
from datetime import datetime
from pathlib import Path

DB = dict(
    host="localhost", port=3306,
    user="flarum", password=os.environ.get("FLARUM_DB_PASSWORD", ""),
    database="flarum", charset="utf8mb4",
)
DEFAULT_OUT = "/root/werkraum/flarum-export/flarum.html"

# ── Flarum XML → sauberes HTML ────────────────────────────────────────────────

def flarum_to_html(xml: str) -> str:
    if not xml:
        return ""
    t = H.unescape(xml)
    t = re.sub(r'<s>[^<]*</s>', '', t)
    t = re.sub(r'<e>[^<]*</e>', '', t)
    t = re.sub(r'</?r>', '', t)
    t = re.sub(r'<BLOCKQUOTE>', '<blockquote>', t, flags=re.IGNORECASE)
    t = re.sub(r'</BLOCKQUOTE>', '</blockquote>', t, flags=re.IGNORECASE)
    for n in range(1, 7):
        t = re.sub(rf'<H{n}>(.*?)</H{n}>', rf'<h{n}>\1</h{n}>', t, flags=re.DOTALL|re.IGNORECASE)
    for tag in ['strong','em','del','code','pre','p','li','ul','ol']:
        t = re.sub(rf'<{tag}>', f'<{tag}>', t, flags=re.IGNORECASE)
        t = re.sub(rf'</{tag}>', f'</{tag}>', t, flags=re.IGNORECASE)
    t = re.sub(r'<pre><code[^>]*>(.*?)</code></pre>', r'<pre><code>\1</code></pre>', t, flags=re.DOTALL|re.IGNORECASE)
    t = re.sub(r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>', r'<a href="\1" rel="noopener">\2</a>', t, flags=re.DOTALL|re.IGNORECASE)
    t = re.sub(r'<MENTION[^>]+username="([^"]+)"[^/]*/?>',
               r'<span class="mention">@\1</span>', t, flags=re.IGNORECASE)
    t = re.sub(r'<BR\s*/?>', '<br>', t, flags=re.IGNORECASE)
    t = re.sub(r'<P>(.*?)</P>', r'<p>\1</p>', t, flags=re.DOTALL|re.IGNORECASE)
    return t.strip()


# ── Hauptprogramm ──────────────────────────────────────────────────────────────

def main():
    out_path = Path(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print("Verbinde mit MySQL...")
    conn = pymysql.connect(**DB, cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()

    cur.execute("SELECT id, username FROM users")
    users = {r['id']: r['username'] for r in cur.fetchall()}

    cur.execute("""
        SELECT dt.discussion_id, t.name FROM discussion_tag dt
        JOIN tags t ON t.id = dt.tag_id
    """)
    disc_tags: dict[int, list[str]] = {}
    for r in cur.fetchall():
        disc_tags.setdefault(r['discussion_id'], []).append(r['name'])

    cur.execute("""
        SELECT id, title, slug, comment_count, participant_count,
               created_at, last_posted_at, is_locked, is_sticky, hidden_at
        FROM discussions ORDER BY created_at ASC
    """)
    discussions = cur.fetchall()
    total = len(discussions)
    print(f"  {total} Diskussionen, {len(users)} User")

    print("  Lade Posts...")
    cur.execute("""
        SELECT discussion_id, number, created_at, user_id,
               content, edited_at, edited_user_id, hidden_at
        FROM posts WHERE type='comment'
        ORDER BY discussion_id ASC, number ASC
    """)
    all_posts: dict[int, list] = {}
    for r in cur.fetchall():
        all_posts.setdefault(r['discussion_id'], []).append(r)
    conn.close()

    print("  Baue Datensatz...")
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    data = []
    for disc in discussions:
        did = disc['id']
        tags = disc_tags.get(did, [])
        posts = all_posts.get(did, [])
        data.append({
            "id": did,
            "title": disc['title'],
            "slug": disc['slug'],
            "tags": tags,
            "date": str(disc['created_at'])[:10],
            "created_at": str(disc['created_at']),
            "last_posted_at": str(disc.get('last_posted_at', '') or ''),
            "post_count": len(posts),
            "is_locked": bool(disc['is_locked']),
            "is_sticky": bool(disc['is_sticky']),
            "hidden": bool(disc['hidden_at']),
            "url": f"http://217.154.14.29/d/{did}-{disc['slug']}",
            "posts": [
                {
                    "n": p['number'],
                    "a": users.get(p['user_id'], f"uid_{p['user_id']}"),
                    "t": str(p['created_at']),
                    "h": flarum_to_html(p['content'] or ""),
                    "hidden": bool(p['hidden_at']),
                    "edited": str(p['edited_at'])[:16] if p.get('edited_at') else None,
                }
                for p in posts
            ]
        })

    total_posts = sum(len(d['posts']) for d in data)
    all_tags = sorted(set(t for d in data for t in d['tags']))
    json_blob = json.dumps({
        "meta": {"generated": now, "total_disc": total, "total_posts": total_posts},
        "users": {str(k): v for k, v in users.items()},
        "discussions": data
    }, ensure_ascii=False, separators=(',', ':'))

    print(f"  Schreibe HTML ({len(json_blob)//1024} KB JSON)...")

    html_doc = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Flarum Export</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:system-ui,sans-serif;font-size:15px;line-height:1.6;color:#1a1a1a;background:#f0f0ee}}
a{{color:#2563eb;text-decoration:none}}
a:hover{{text-decoration:underline}}
#app{{display:grid;grid-template-rows:auto auto auto 1fr;height:100vh;overflow:hidden}}
#topbar{{background:#1a1a1a;color:#fff;padding:10px 20px;display:flex;align-items:center;gap:16px;flex-shrink:0}}
#topbar h1{{font-size:1rem;font-weight:600}}
#topbar .meta{{font-size:0.78rem;opacity:0.55}}
#search{{border:none;border-bottom:1px solid #ddd;padding:10px 20px;font-size:0.95rem;background:#fafafa;outline:none;width:100%;flex-shrink:0}}
#search:focus{{background:#fff}}
#tabs{{display:flex;flex-wrap:wrap;gap:5px;padding:10px 20px;background:#fff;border-bottom:1px solid #e5e7eb;flex-shrink:0;overflow-x:auto}}
#tabs button{{padding:4px 11px;border:1px solid #d1d5db;border-radius:20px;background:#fff;cursor:pointer;font-size:0.78rem;white-space:nowrap}}
#tabs button.active{{background:#1a1a1a;color:#fff;border-color:#1a1a1a}}
#body{{display:flex;overflow:hidden;height:100%}}
#list{{width:340px;flex-shrink:0;overflow-y:auto;border-right:1px solid #e5e7eb;background:#fff}}
.disc-row{{padding:10px 14px;border-bottom:1px solid #f5f5f5;cursor:pointer;display:block}}
.disc-row:hover{{background:#f9f9f9}}
.disc-row.active{{background:#eff6ff;border-left:3px solid #2563eb}}
.disc-row .rtitle{{font-size:0.88rem;font-weight:500;margin-bottom:3px}}
.disc-row .rmeta{{font-size:0.75rem;color:#9ca3af}}
.tag{{display:inline-block;padding:0 6px;border-radius:10px;font-size:0.72rem;background:#f3f4f6;color:#374151;margin:1px}}
.hidden-badge{{background:#fee2e2;color:#991b1b}}
#detail{{flex:1;overflow-y:auto;padding:24px}}
#detail-inner{{max-width:760px;margin:0 auto}}
.disc-header{{background:#fff;border-radius:8px;padding:16px 20px;margin-bottom:12px;border:1px solid #e5e7eb}}
.disc-header h2{{font-size:1.1rem;margin-bottom:6px}}
.disc-header .dmeta{{font-size:0.8rem;color:#6b7280}}
.post{{background:#fff;border-radius:8px;margin-bottom:8px;border:1px solid #e5e7eb;overflow:hidden}}
.post-hd{{padding:9px 16px;background:#fafafa;border-bottom:1px solid #f0f0f0;font-size:0.8rem;color:#6b7280;display:flex;gap:10px;align-items:baseline}}
.post-hd .pnum{{background:#e5e7eb;border-radius:4px;padding:0 5px;font-size:0.72rem}}
.post-hd .pauth{{font-weight:600;color:#374151}}
.post-body{{padding:14px 16px}}
.post-body p{{margin-bottom:0.65em}}
.post-body p:last-child{{margin-bottom:0}}
.post-body blockquote{{border-left:3px solid #d1d5db;padding-left:12px;color:#6b7280;margin:8px 0}}
.post-body code{{background:#f3f4f6;padding:1px 4px;border-radius:3px;font-size:0.85em}}
.post-body pre{{background:#1e1e1e;color:#d4d4d4;padding:12px;border-radius:6px;overflow-x:auto;margin:8px 0}}
.post-body pre code{{background:none;color:inherit}}
.post-body .mention{{color:#7c3aed;font-weight:500}}
.post.post-hidden{{opacity:0.5}}
#empty{{padding:40px 20px;text-align:center;color:#9ca3af;font-size:0.9rem}}
#welcome{{padding:40px 20px;text-align:center;color:#9ca3af}}
#welcome h3{{font-size:1rem;margin-bottom:8px;color:#374151}}
</style>
</head>
<body>
<div id="app">
  <div id="topbar">
    <h1>Flarum Export</h1>
    <span class="meta" id="totalmeta"></span>
  </div>
  <input id="search" type="search" placeholder="Suchen in Titeln und Tags…" autocomplete="off">
  <div id="tabs"></div>
  <div id="body">
    <div id="list"></div>
    <div id="detail"><div id="detail-inner"><div id="welcome">
      <h3>Flarum Export</h3>
      <p>Diskussion aus der Liste auswählen</p>
    </div></div></div>
  </div>
</div>

<script type="application/json" id="ftw-data">
{json_blob}
</script>
<script>
const RAW = JSON.parse(document.getElementById('ftw-data').textContent);
const DISCS = RAW.discussions;
const META = RAW.meta;
document.getElementById('totalmeta').textContent =
  `${{META.generated}} · ${{META.total_disc}} Diskussionen · ${{META.total_posts}} Posts`;

// Tags
const allTags = [...new Set(DISCS.flatMap(d => d.tags))].sort();
const tabsEl = document.getElementById('tabs');
let activeTag = '';
function mkTab(label, tag) {{
  const b = document.createElement('button');
  b.textContent = label;
  b.dataset.tag = tag;
  if (tag === '') b.classList.add('active');
  b.onclick = () => {{
    activeTag = tag;
    tabsEl.querySelectorAll('button').forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    render();
  }};
  tabsEl.appendChild(b);
}}
mkTab('Alle', '');
const tagCounts = {{}};
DISCS.forEach(d => d.tags.forEach(t => tagCounts[t] = (tagCounts[t]||0)+1));
allTags.forEach(t => mkTab(`${{t}} ${{tagCounts[t]}}`, t));

// Suche
const searchEl = document.getElementById('search');
searchEl.oninput = render;

// Liste
const listEl = document.getElementById('list');
let activeId = null;

function escH(s) {{
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

function render() {{
  const q = searchEl.value.toLowerCase();
  const rows = DISCS.filter(d => {{
    if (activeTag && !d.tags.includes(activeTag)) return false;
    if (q) {{
      const hay = (d.title + ' ' + d.tags.join(' ')).toLowerCase();
      if (!hay.includes(q)) return false;
    }}
    return true;
  }});
  if (rows.length === 0) {{
    listEl.innerHTML = '<div id="empty">Keine Diskussionen</div>';
    return;
  }}
  listEl.innerHTML = rows.map(d => {{
    const tags = d.tags.map(t => `<span class="tag">${{escH(t)}}</span>`).join('');
    const hid = d.hidden ? '<span class="tag hidden-badge">versteckt</span>' : '';
    const act = d.id === activeId ? ' active' : '';
    return `<div class="disc-row${{act}}" data-id="${{d.id}}" onclick="showDisc(${{d.id}})">
      <div class="rtitle">${{escH(d.title)}}${{hid}}</div>
      <div class="rmeta">${{d.date}} · ${{d.post_count}} Posts ${{tags}}</div>
    </div>`;
  }}).join('');
}}

// Diskussion anzeigen
const detailInner = document.getElementById('detail-inner');
function showDisc(id) {{
  activeId = id;
  // aktive Klasse setzen
  listEl.querySelectorAll('.disc-row').forEach(r => {{
    r.classList.toggle('active', Number(r.dataset.id) === id);
  }});

  const d = DISCS.find(x => x.id === id);
  if (!d) return;

  const tags = d.tags.map(t => `<span class="tag">${{escH(t)}}</span>`).join(' ');
  const hid = d.hidden ? '<span class="tag hidden-badge">versteckt</span>' : '';
  const locked = d.is_locked ? '<span class="tag">gesperrt</span>' : '';

  const postsHtml = d.posts.map(p => {{
    const hidCls = p.hidden ? ' post-hidden' : '';
    const edited = p.edited ? ` <span style="opacity:.6;font-size:.72rem">(bearbeitet ${{p.edited}})</span>` : '';
    return `<div class="post${{hidCls}}" data-post="${{p.n}}" data-author="${{escH(p.a)}}">
      <div class="post-hd">
        <span class="pnum">#${{p.n}}</span>
        <span class="pauth">${{escH(p.a)}}</span>
        <span>${{p.t}}</span>
        ${{edited}}
      </div>
      <div class="post-body">${{p.h || '<em>(kein Inhalt)</em>'}}</div>
    </div>`;
  }}).join('');

  detailInner.innerHTML = `
    <div class="disc-header">
      <h2>${{escH(d.title)}} ${{hid}} ${{locked}}</h2>
      <div class="dmeta">
        ${{tags}}
        <span style="margin-left:8px">
          ${{d.date}} · ${{d.post_count}} Posts ·
          <a href="${{d.url}}" rel="noopener">Flarum ↗</a>
        </span>
      </div>
    </div>
    ${{postsHtml || '<div class="post"><div class="post-body"><em>keine Posts</em></div></div>'}}
  `;
  document.getElementById('detail').scrollTop = 0;
}}

render();
</script>
</body>
</html>"""

    out_path.write_text(html_doc, encoding='utf-8')
    size_mb = out_path.stat().st_size / 1_048_576
    print(f"\nFertig: {out_path}")
    print(f"  Größe: {size_mb:.1f} MB — eine einzige Datei, kein Server nötig")
    print(f"  {total} Diskussionen, {total_posts} Posts")


if __name__ == "__main__":
    main()
