#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "flextrawurst_systemdoku_komplett.html"


MOJIBAKE = {
    "Ã¤": "ä",
    "Ã¶": "ö",
    "Ã¼": "ü",
    "Ã": "Ä",
    "Ã": "Ö",
    "Ã": "Ü",
    "Ã": "ß",
    "â": "—",
    "â": "–",
    "â": "←",
    "â": "→",
    "â": "↔",
    "â": "✅",
    "â¬": "⬜",
    "â": "„",
    "â": "“",
    "â": "”",
    "â": "’",
    "â¦": "…",
    "Ã": "×",
}


@dataclass
class Doc:
    path: Path
    slug: str
    title: str
    typ: str
    source: str
    body: str
    headings: list[tuple[int, str, str]]


def clean_text(text: str) -> str:
    for bad, good in MOJIBAKE.items():
        text = text.replace(bad, good)
    return text


def slugify(value: str) -> str:
    value = clean_text(value).lower()
    value = value.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "abschnitt"


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    text = clean_text(text)
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, body


def inline_md(text: str, doc_slugs: dict[str, str]) -> str:
    text = html.escape(text)

    def wiki(match: re.Match[str]) -> str:
        raw = html.unescape(match.group(1)).strip()
        target, label = (raw.split("|", 1) + [raw])[:2] if "|" in raw else (raw, raw)
        key = target.strip().replace(".md", "")
        slug = doc_slugs.get(key, slugify(key))
        return f'<a href="#doc-{slug}" data-jump="{slug}">{html.escape(label.strip())}</a>'

    text = re.sub(r"\[\[([^\]]+)\]\]", wiki, text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*\n]+)\*", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def is_table(lines: list[str], i: int) -> bool:
    return (
        i + 1 < len(lines)
        and "|" in lines[i]
        and re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", lines[i + 1])
        is not None
    )


def render_table(lines: list[str], i: int, doc_slugs: dict[str, str]) -> tuple[str, int]:
    rows: list[list[str]] = []
    j = i
    while j < len(lines) and "|" in lines[j].strip():
        row = [c.strip() for c in lines[j].strip().strip("|").split("|")]
        rows.append(row)
        j += 1
    if len(rows) < 2:
        return "", i
    header = rows[0]
    body = rows[2:]
    out = ["<div class=\"table-wrap\"><table><thead><tr>"]
    out.extend(f"<th>{inline_md(c, doc_slugs)}</th>" for c in header)
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>")
        for idx in range(len(header)):
            value = row[idx] if idx < len(row) else ""
            out.append(f"<td>{inline_md(value, doc_slugs)}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out), j


def render_markdown(body: str, doc: Doc, doc_slugs: dict[str, str]) -> str:
    lines = clean_text(body).splitlines()
    out: list[str] = []
    i = 0
    in_ul = False
    in_ol = False

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            close_lists()
            i += 1
            continue

        if stripped == "---":
            close_lists()
            out.append("<hr>")
            i += 1
            continue

        fence = re.match(r"^```(\w+)?\s*$", stripped)
        if fence:
            close_lists()
            lang = fence.group(1) or ""
            code: list[str] = []
            i += 1
            while i < len(lines) and lines[i].strip() != "```":
                code.append(lines[i])
                i += 1
            i += 1
            lang_class = f" language-{html.escape(lang)}" if lang else ""
            out.append(
                f'<div class="code-block"><div class="code-head"><span>{html.escape(lang or "code")}</span>'
                '<button type="button" class="copy-btn" title="Code kopieren">Kopieren</button></div>'
                f'<pre><code class="{lang_class}">{html.escape(chr(10).join(code))}</code></pre></div>'
            )
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            close_lists()
            level = min(len(heading.group(1)) + 1, 6)
            text = clean_text(heading.group(2)).strip()
            base = slugify(text)
            hid = f"{doc.slug}-{base}"
            out.append(
                f'<h{level} id="{hid}"><a class="anchor" href="#{hid}">#</a>{inline_md(text, doc_slugs)}</h{level}>'
            )
            i += 1
            continue

        if is_table(lines, i):
            close_lists()
            table, i = render_table(lines, i, doc_slugs)
            out.append(table)
            continue

        if stripped.startswith("> "):
            close_lists()
            quote: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                quote.append(lines[i].strip()[2:])
                i += 1
            out.append(f'<blockquote>{"<br>".join(inline_md(q, doc_slugs) for q in quote)}</blockquote>')
            continue

        bullet = re.match(r"^[-*]\s+(.+)$", stripped)
        if bullet:
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline_md(bullet.group(1), doc_slugs)}</li>")
            i += 1
            continue

        numbered = re.match(r"^\d+\.\s+(.+)$", stripped)
        if numbered:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{inline_md(numbered.group(1), doc_slugs)}</li>")
            i += 1
            continue

        close_lists()
        para = [stripped]
        i += 1
        while (
            i < len(lines)
            and lines[i].strip()
            and not re.match(r"^(#{1,6})\s+", lines[i].strip())
            and not re.match(r"^```", lines[i].strip())
            and not is_table(lines, i)
            and not re.match(r"^[-*]\s+", lines[i].strip())
            and not re.match(r"^\d+\.\s+", lines[i].strip())
            and not lines[i].strip().startswith("> ")
            and lines[i].strip() != "---"
        ):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline_md(' '.join(para), doc_slugs)}</p>")

    close_lists()
    return "\n".join(out)


def load_docs() -> list[Doc]:
    docs: list[Doc] = []
    for path in sorted(ROOT.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        meta, body = split_frontmatter(raw)
        title = meta.get("titel") or re.sub(r"^\d+_", "", path.stem).replace("_", " ").title()
        typ = meta.get("typ", "doku")
        headings: list[tuple[int, str, str]] = []
        for line in body.splitlines():
            match = re.match(r"^(#{1,4})\s+(.+)$", line.strip())
            if match:
                text = clean_text(match.group(2)).strip()
                headings.append((len(match.group(1)), text, slugify(text)))
        docs.append(Doc(path=path, slug=slugify(path.stem), title=title, typ=typ, source=path.name, body=body, headings=headings))
    return docs


def build_html(docs: list[Doc]) -> str:
    doc_slugs = {doc.path.stem: doc.slug for doc in docs}
    nav = "\n".join(
        f'<button class="tab-btn" type="button" data-tab="{doc.slug}"><span>{html.escape(doc.source[:2] if doc.source[:2].isdigit() else "IX")}</span>{html.escape(doc.title)}</button>'
        for doc in docs
    )
    panels = []
    for doc in docs:
        toc = "\n".join(
            f'<a href="#{doc.slug}-{hid}" class="toc-l{level}">{html.escape(text)}</a>'
            for level, text, hid in doc.headings[:80]
        )
        panels.append(
            f'''
<article class="doc-panel" id="doc-{doc.slug}" data-title="{html.escape(doc.title.lower())}" data-source="{html.escape(doc.source.lower())}">
  <header class="doc-header">
    <div>
      <p class="eyebrow">{html.escape(doc.typ)} · {html.escape(doc.source)}</p>
      <h1>{html.escape(doc.title)}</h1>
    </div>
    <a class="source-link" href="{html.escape(doc.source)}">Markdown öffnen</a>
  </header>
  <div class="doc-layout">
    <aside class="toc">{toc}</aside>
    <section class="doc-content">{render_markdown(doc.body, doc, doc_slugs)}</section>
  </div>
</article>'''
        )

    index_cards = "\n".join(
        f'<a class="index-card" href="#doc-{doc.slug}" data-jump="{doc.slug}"><b>{html.escape(doc.title)}</b><span>{html.escape(doc.source)}</span></a>'
        for doc in docs
    )
    stats = {
        "docs": len(docs),
        "lines": sum(len(doc.body.splitlines()) for doc in docs),
        "headings": sum(len(doc.headings) for doc in docs),
        "generated": "2026-05-26",
    }
    stats_json = html.escape(json.dumps(stats, ensure_ascii=False))

    return f'''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>flextrawurst Systemdokumentation</title>
<meta name="description" content="Eine einzige klickbare HTML-Dokumentation aus allen Markdown-Dateien der flextrawurst-Systemdoku.">
<style>
:root {{
  color-scheme: dark;
  --bg:#0b0d10; --panel:#11151a; --panel-2:#171d23; --panel-3:#0f1318;
  --text:#e7ecef; --muted:#9aa8b2; --faint:#64727d; --line:#28333d;
  --cyan:#3bd9d9; --green:#63d77c; --amber:#f0b84f; --red:#ff6b5e; --blue:#8fb7ff;
  --code:#07090c; --shadow:rgba(0,0,0,.28);
}}
* {{ box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{ margin:0; background:var(--bg); color:var(--text); font:15px/1.65 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
a {{ color:var(--cyan); text-decoration:none; }}
a:hover {{ text-decoration:underline; }}
.shell {{ min-height:100vh; display:grid; grid-template-columns:320px minmax(0,1fr); }}
.sidebar {{ position:sticky; top:0; height:100vh; overflow:auto; border-right:1px solid var(--line); background:linear-gradient(180deg,#0d1116,#090b0e); padding:18px 14px; }}
.brand {{ padding:6px 8px 18px; border-bottom:1px solid var(--line); margin-bottom:14px; }}
.brand h1 {{ margin:0; font-size:24px; line-height:1.05; letter-spacing:0; }}
.brand p {{ margin:8px 0 0; color:var(--muted); font-size:13px; }}
.stats {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; margin:14px 0; }}
.stat {{ border:1px solid var(--line); background:var(--panel); padding:8px; min-height:58px; }}
.stat b {{ display:block; font-size:19px; color:var(--green); }}
.stat span {{ color:var(--muted); font-size:12px; }}
.search {{ width:100%; min-height:44px; border:1px solid var(--line); background:#070a0d; color:var(--text); padding:10px 12px; font:inherit; border-radius:4px; }}
.nav {{ display:flex; flex-direction:column; gap:5px; margin-top:12px; }}
.tab-btn {{ width:100%; min-height:44px; display:grid; grid-template-columns:32px 1fr; gap:8px; align-items:center; text-align:left; border:1px solid var(--line); background:var(--panel); color:var(--text); padding:8px 10px; border-radius:4px; cursor:pointer; font:inherit; }}
.tab-btn span {{ color:var(--amber); font:700 12px/1 ui-monospace, SFMono-Regular, Menlo, monospace; }}
.tab-btn:hover, .tab-btn.active {{ border-color:var(--cyan); background:#112026; }}
.main {{ min-width:0; }}
.topbar {{ position:sticky; top:0; z-index:20; min-height:58px; display:flex; align-items:center; justify-content:space-between; gap:12px; border-bottom:1px solid var(--line); background:rgba(11,13,16,.92); backdrop-filter:blur(12px); padding:10px 22px; }}
.crumb {{ color:var(--muted); font-size:13px; }}
.tools {{ display:flex; gap:8px; flex-wrap:wrap; }}
.tool-btn, .source-link, .copy-btn {{ border:1px solid var(--line); background:var(--panel-2); color:var(--text); border-radius:4px; min-height:36px; padding:7px 10px; cursor:pointer; font:inherit; font-size:13px; }}
.tool-btn:hover, .source-link:hover, .copy-btn:hover {{ border-color:var(--cyan); text-decoration:none; }}
.overview {{ padding:24px 22px 0; }}
.overview h2 {{ margin:0 0 10px; font-size:18px; }}
.index-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:10px; }}
.index-card {{ border:1px solid var(--line); background:var(--panel); border-radius:4px; padding:12px; color:var(--text); min-height:82px; }}
.index-card b {{ display:block; line-height:1.25; }}
.index-card span {{ color:var(--muted); font-size:12px; }}
.doc-panel {{ display:none; padding:28px 22px 80px; max-width:1480px; }}
.doc-panel.active {{ display:block; }}
.doc-header {{ display:flex; align-items:flex-start; justify-content:space-between; gap:16px; border-bottom:1px solid var(--line); padding-bottom:18px; margin-bottom:18px; }}
.doc-header h1 {{ margin:0; font-size:clamp(28px,4vw,52px); line-height:1; letter-spacing:0; max-width:980px; }}
.eyebrow {{ color:var(--amber); text-transform:uppercase; font:700 12px/1.2 ui-monospace, SFMono-Regular, Menlo, monospace; margin:0 0 9px; }}
.doc-layout {{ display:grid; grid-template-columns:260px minmax(0,920px); gap:28px; align-items:start; }}
.toc {{ position:sticky; top:80px; max-height:calc(100vh - 100px); overflow:auto; border:1px solid var(--line); background:var(--panel); padding:10px; border-radius:4px; }}
.toc a {{ display:block; color:var(--muted); padding:5px 6px; border-left:2px solid transparent; font-size:12px; line-height:1.35; }}
.toc a:hover {{ color:var(--text); border-left-color:var(--cyan); text-decoration:none; }}
.toc-l2 {{ margin-left:0; }} .toc-l3 {{ margin-left:10px; }} .toc-l4 {{ margin-left:20px; }}
.doc-content {{ min-width:0; }}
.doc-content h2, .doc-content h3, .doc-content h4, .doc-content h5, .doc-content h6 {{ line-height:1.2; letter-spacing:0; margin:30px 0 10px; scroll-margin-top:80px; }}
.doc-content h2 {{ font-size:28px; color:var(--cyan); border-top:1px solid var(--line); padding-top:22px; }}
.doc-content h3 {{ font-size:21px; color:var(--blue); }}
.doc-content h4 {{ font-size:17px; color:var(--green); }}
.anchor {{ color:var(--faint); margin-right:8px; font-weight:400; }}
p {{ margin:10px 0; max-width:82ch; }}
ul, ol {{ margin:10px 0 14px; padding-left:24px; max-width:88ch; }}
li {{ margin:4px 0; }}
hr {{ border:0; border-top:1px solid var(--line); margin:24px 0; }}
blockquote {{ margin:14px 0; border-left:3px solid var(--amber); background:var(--panel); padding:12px 14px; color:#f3ddaa; }}
.table-wrap {{ overflow:auto; margin:14px 0 20px; border:1px solid var(--line); border-radius:4px; }}
table {{ width:100%; border-collapse:collapse; min-width:680px; }}
th, td {{ border-bottom:1px solid var(--line); border-right:1px solid var(--line); padding:9px 10px; vertical-align:top; }}
th {{ background:var(--panel-2); color:var(--text); text-align:left; position:sticky; top:58px; z-index:2; }}
td {{ background:rgba(17,21,26,.72); }}
tr:nth-child(even) td {{ background:rgba(23,29,35,.7); }}
code {{ font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:.92em; background:#091116; color:#9be7e7; padding:.12em .34em; border-radius:3px; }}
.code-block {{ border:1px solid var(--line); background:var(--code); border-radius:4px; margin:14px 0 20px; overflow:hidden; box-shadow:0 10px 30px var(--shadow); }}
.code-head {{ min-height:38px; display:flex; align-items:center; justify-content:space-between; padding:6px 8px 6px 12px; border-bottom:1px solid var(--line); color:var(--muted); font:700 12px/1 ui-monospace,SFMono-Regular,Menlo,monospace; }}
pre {{ margin:0; padding:14px 16px; overflow:auto; }}
pre code {{ display:block; background:transparent; padding:0; color:#dfe8ef; white-space:pre; }}
.highlight {{ outline:2px solid var(--amber); background:rgba(240,184,79,.1); }}
.hidden-by-search {{ display:none !important; }}
@media (max-width:980px) {{
  .shell {{ grid-template-columns:1fr; }}
  .sidebar {{ position:relative; height:auto; max-height:68vh; }}
  .topbar {{ top:0; }}
  .doc-layout {{ grid-template-columns:1fr; }}
  .toc {{ position:relative; top:auto; max-height:none; }}
}}
@media print {{
  .sidebar,.topbar,.overview,.toc,.copy-btn {{ display:none !important; }}
  .shell,.doc-layout {{ display:block; }}
  .doc-panel {{ display:block; page-break-before:always; }}
  body {{ background:#fff; color:#000; }}
}}
</style>
</head>
<body data-stats="{stats_json}">
<div class="shell">
  <aside class="sidebar">
    <div class="brand">
      <h1>flextrawurst<br>Systemdoku</h1>
      <p>Eine HTML aus allen Markdown-Dateien in <code>docs/systemdoku</code>.</p>
      <div class="stats">
        <div class="stat"><b>{stats["docs"]}</b><span>Markdown-Dateien</span></div>
        <div class="stat"><b>{stats["lines"]}</b><span>Quellzeilen</span></div>
        <div class="stat"><b>{stats["headings"]}</b><span>Überschriften</span></div>
        <div class="stat"><b>{stats["generated"]}</b><span>Stand</span></div>
      </div>
      <input class="search" id="search" type="search" placeholder="Suche in Titeln und Text...">
    </div>
    <nav class="nav" aria-label="Dokumente">{nav}</nav>
  </aside>
  <main class="main">
    <div class="topbar">
      <div class="crumb" id="crumb">Index</div>
      <div class="tools">
        <button class="tool-btn" id="show-index" type="button">Index</button>
        <button class="tool-btn" id="expand-all" type="button">Alle anzeigen</button>
        <button class="tool-btn" onclick="window.print()" type="button">Drucken</button>
      </div>
    </div>
    <section class="overview" id="overview">
      <h2>Dokumente</h2>
      <div class="index-grid">{index_cards}</div>
    </section>
    {''.join(panels)}
  </main>
</div>
<script>
const buttons = [...document.querySelectorAll('.tab-btn')];
const panels = [...document.querySelectorAll('.doc-panel')];
const overview = document.getElementById('overview');
const crumb = document.getElementById('crumb');
function activate(slug, push=true) {{
  overview.style.display = 'none';
  panels.forEach(p => p.classList.toggle('active', p.id === 'doc-' + slug));
  buttons.forEach(b => b.classList.toggle('active', b.dataset.tab === slug));
  const panel = document.getElementById('doc-' + slug);
  crumb.textContent = panel ? panel.querySelector('h1').textContent : 'Index';
  if (push) history.replaceState(null, '', '#doc-' + slug);
  window.scrollTo({{top: 0, behavior: 'smooth'}});
}}
function showIndex() {{
  panels.forEach(p => p.classList.remove('active'));
  buttons.forEach(b => b.classList.remove('active'));
  overview.style.display = '';
  crumb.textContent = 'Index';
  history.replaceState(null, '', location.pathname);
}}
buttons.forEach(b => b.addEventListener('click', () => activate(b.dataset.tab)));
document.querySelectorAll('[data-jump]').forEach(a => a.addEventListener('click', ev => {{
  const slug = a.dataset.jump;
  if (document.getElementById('doc-' + slug)) {{
    ev.preventDefault();
    activate(slug);
  }}
}}));
document.getElementById('show-index').addEventListener('click', showIndex);
document.getElementById('expand-all').addEventListener('click', () => {{
  overview.style.display = 'none';
  panels.forEach(p => p.classList.add('active'));
  buttons.forEach(b => b.classList.remove('active'));
  crumb.textContent = 'Alle Dokumente';
  history.replaceState(null, '', '#alle');
}});
document.querySelectorAll('.copy-btn').forEach(btn => btn.addEventListener('click', async () => {{
  const code = btn.closest('.code-block').querySelector('code').innerText;
  await navigator.clipboard.writeText(code);
  btn.textContent = 'Kopiert';
  setTimeout(() => btn.textContent = 'Kopieren', 900);
}}));
document.getElementById('search').addEventListener('input', e => {{
  const q = e.target.value.trim().toLowerCase();
  panels.forEach(p => {{
    const hit = !q || p.innerText.toLowerCase().includes(q) || p.dataset.title.includes(q) || p.dataset.source.includes(q);
    p.classList.toggle('hidden-by-search', !hit);
  }});
  buttons.forEach(b => {{
    const panel = document.getElementById('doc-' + b.dataset.tab);
    b.classList.toggle('hidden-by-search', q && panel && panel.classList.contains('hidden-by-search'));
  }});
}});
if (location.hash.startsWith('#doc-')) {{
  activate(location.hash.replace('#doc-', ''), false);
}} else {{
  showIndex();
}}
</script>
</body>
</html>
'''


def main() -> None:
    docs = load_docs()
    OUT.write_text(build_html(docs), encoding="utf-8")
    print(f"written {OUT} ({len(docs)} markdown files)")


if __name__ == "__main__":
    main()
