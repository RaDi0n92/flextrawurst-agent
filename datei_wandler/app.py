from __future__ import annotations

import html
import io
import json
import mimetypes
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Literal
import unicodedata

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
EXPORT_DIR = BASE_DIR / "exports"
MAX_FILE_BYTES = 2 * 1024 * 1024
ALLOWED_ROOTS = [Path("/root/werkraum").resolve(), Path("/root/visionen").resolve()]
BLOCKED_NAME_PATTERNS = (
    re.compile(r"(^|/)\.env($|\.)"),
    re.compile(r"(^|/)id_rsa($|\.)"),
    re.compile(r".*\.(pem|key|crt|p12|sqlite|db|sqlite3)$", re.I),
)
CODE_FENCES = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".css": "css",
    ".html": "html",
    ".htm": "html",
    ".json": "json",
    ".md": "markdown",
    ".sql": "sql",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".sh": "bash",
    ".txt": "",
}


app = FastAPI(title="Datei-Wandler", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@dataclass
class SourceFile:
    label: str
    origin: Literal["path", "upload"]
    suffix: str
    content: str
    size_bytes: int
    warning: str | None = None
    source_path: str | None = None


class MarkdownHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.href_stack: list[str | None] = []
        self.in_pre = False
        self.skip_depth = 0
        self.list_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag in {"script", "style", "noscript"}:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag in {"p", "section", "article", "div"}:
            self.parts.append("\n\n")
        elif tag == "br":
            self.parts.append("\n")
        elif tag == "li":
            self.parts.append("\n" + "  " * self.list_depth + "- ")
        elif tag in {"ul", "ol"}:
            self.list_depth += 1
            self.parts.append("\n")
        elif tag == "blockquote":
            self.parts.append("\n\n> ")
        elif tag == "pre":
            self.in_pre = True
            self.parts.append("\n\n```\n")
        elif tag == "code" and not self.in_pre:
            self.parts.append("`")
        elif tag == "a":
            self.href_stack.append(attrs_dict.get("href"))
            self.parts.append("[")
        elif tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self.skip_depth:
            self.skip_depth -= 1
            return
        if self.skip_depth:
            return
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6", "p", "section", "article", "div"}:
            self.parts.append("\n")
        elif tag in {"ul", "ol"}:
            self.list_depth = max(0, self.list_depth - 1)
            self.parts.append("\n")
        elif tag == "pre":
            self.in_pre = False
            self.parts.append("\n```\n")
        elif tag == "code" and not self.in_pre:
            self.parts.append("`")
        elif tag == "a":
            href = self.href_stack.pop() if self.href_stack else None
            self.parts.append(f"]({href})" if href else "]")
        elif tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if self.in_pre:
            self.parts.append(data)
            return
        compact = re.sub(r"\s+", " ", data)
        self.parts.append(compact)

    def markdown(self) -> str:
        text = "".join(self.parts)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+\n", "\n", text)
        return text.strip()


def is_under_allowed_root(path: Path) -> bool:
    return any(path == root or root in path.parents for root in ALLOWED_ROOTS)


def is_blocked(path: Path) -> bool:
    normalized = path.as_posix()
    return any(pattern.match(normalized) for pattern in BLOCKED_NAME_PATTERNS)


def decode_text(raw: bytes) -> tuple[str, str | None]:
    if b"\x00" in raw[:2048]:
        raise ValueError("Binaerdatei erkannt; Textumwandlung uebersprungen.")
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return raw.decode(encoding), None if encoding.startswith("utf-8") else f"Mit {encoding} gelesen."
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace"), "Mit Ersatzzeichen gelesen."


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug or "datei"


def display_path(file: SourceFile) -> str:
    if file.source_path:
        normalized = file.source_path.replace("\\", "/")
        if file.origin == "upload":
            return normalized
        path = Path(file.source_path)
        for root in ALLOWED_ROOTS:
            try:
                return str(path.relative_to(root))
            except ValueError:
                continue
        return normalized
    return file.label


def export_label(file: SourceFile) -> str:
    return display_path(file)


def read_path(path_text: str) -> SourceFile:
    path = Path(path_text).expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=400, detail=f"Nicht gefunden oder keine Datei: {path_text}")
    if not is_under_allowed_root(path):
        raise HTTPException(status_code=400, detail=f"Pfad ausserhalb erlaubter Wurzeln: {path}")
    if is_blocked(path):
        raise HTTPException(status_code=400, detail=f"Blockierter Dateityp oder Geheimdatei: {path}")
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        raise HTTPException(status_code=400, detail=f"Datei zu gross ({size} Bytes): {path}")
    content, warning = decode_text(path.read_bytes())
    return SourceFile(str(path), "path", path.suffix.lower(), content, size, warning, str(path))


async def read_upload(upload: UploadFile) -> SourceFile:
    raw = await upload.read()
    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(status_code=400, detail=f"Upload zu gross ({len(raw)} Bytes): {upload.filename}")
    name = (upload.filename or "upload").replace("\\", "/")
    if is_blocked(Path(name)):
        raise HTTPException(status_code=400, detail=f"Blockierter Upload-Name: {name}")
    try:
        content, warning = decode_text(raw)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"{name}: {exc}") from exc
    return SourceFile(name, "upload", Path(name).suffix.lower(), content, len(raw), warning, name)


def html_to_markdown(source: str) -> str:
    parser = MarkdownHTMLParser()
    parser.feed(source)
    return parser.markdown()


def code_block(content: str, suffix: str) -> str:
    lang = CODE_FENCES.get(suffix, suffix.lstrip("."))
    fence = "```"
    while fence in content:
        fence += "`"
    return f"{fence}{lang}\n{content.rstrip()}\n{fence}"


def collect_related_files(file: SourceFile, files: list[SourceFile]) -> list[SourceFile]:
    related: list[SourceFile] = []
    haystack = file.content
    candidates: list[tuple[str, SourceFile, bool]] = []
    for other in files:
        if other is file:
            continue
        other_path = display_path(other)
        names = {
            other.label,
            export_label(other),
            Path(other_path).name,
            Path(other_path).stem,
        }
        names.add(other_path)
        names.add(Path(other_path).name)
        names.add(Path(other_path).stem)
        for name in sorted({value for value in names if value}):
            candidates.append((name, other, "/" in name or "." in name))

    seen_ids: set[str] = set()
    for needle, other, is_path_like in candidates:
        if other.label in seen_ids:
            continue
        pattern = re.escape(needle) if is_path_like else rf"\b{re.escape(needle)}\b"
        if re.search(pattern, haystack):
            related.append(other)
            seen_ids.add(other.label)
    return related


def file_as_markdown(file: SourceFile, html_mode: str, anchor: str, files: list[SourceFile]) -> str:
    path_text = display_path(file)
    lines = [f"## {path_text}", "", f"- Quelle: {file.origin}", f"- Groesse: {file.size_bytes} Bytes"]
    if file.source_path:
        lines.append(f"- Pfad: {path_text}")
    if file.warning:
        lines.append(f"- Hinweis: {file.warning}")
    lines.append("")

    related = collect_related_files(file, files)
    if related:
        lines.extend(["### Verweise", ""])
        for other in related:
            other_anchor = f"datei-{files.index(other) + 1}-{slugify(display_path(other))}"
            lines.append(f"- [[#{other_anchor}|{export_label(other)}]]")
        lines.append("")

    if file.suffix in {".html", ".htm"} and html_mode in {"markdown", "both"}:
        lines.extend(["### Aus HTML extrahierter Markdown-Text", "", html_to_markdown(file.content) or "_Kein Text extrahiert._", ""])
        if html_mode == "markdown":
            return "\n".join(lines).rstrip() + "\n"
        lines.extend(["### HTML-Quelltext", "", code_block(file.content, file.suffix)])
        return "\n".join(lines).rstrip() + "\n"

    if file.suffix == ".md":
        lines.append(file.content.rstrip())
    else:
        lines.append(code_block(file.content, file.suffix))
    return "\n".join(lines).rstrip() + "\n"


def export_editor_script() -> str:
    return r"""
<script>
(() => {
  const nav = document.querySelector('[data-file-nav]');
  const stack = document.querySelector('[data-file-stack]');
  const searchInput = document.getElementById('file-search');
  const resultCount = document.getElementById('file-result-count');
  let dragSource = null;

  function getSections() {
    return Array.from(document.querySelectorAll('.file'));
  }

  function sectionLabel(section) {
    return section.querySelector('h2')?.textContent?.trim() || section.id;
  }

  function currentSearchTerm() {
    return (searchInput?.value || '').trim().toLowerCase();
  }

  function rebuildNav() {
    if (!nav) return;
    nav.innerHTML = '';
    getSections().forEach((section) => {
      const item = document.createElement('li');
      item.dataset.navItem = 'true';
      item.dataset.target = section.id;

      const link = document.createElement('a');
      link.href = `#${section.id}`;
      link.textContent = sectionLabel(section);

      const meta = document.createElement('span');
      const origin = section.dataset.origin || '';
      const size = section.dataset.size || '';
      meta.textContent = `${origin} · ${size} B`;

      item.append(link, meta);
      nav.appendChild(item);
    });
  }

  function updateSearchState() {
    const term = currentSearchTerm();
    let visible = 0;

    getSections().forEach((section) => {
      const haystack = (section.textContent || '').toLowerCase();
      const match = !term || haystack.includes(term);
      section.hidden = !match;
      if (match) visible += 1;
    });

    nav?.querySelectorAll('[data-nav-item]').forEach((item) => {
      const target = item.dataset.target;
      const section = target ? document.getElementById(target) : null;
      item.hidden = !section || section.hidden;
    });

    if (resultCount) {
      resultCount.textContent = `${visible} / ${getSections().length}`;
    }
  }

  function refreshView() {
    rebuildNav();
    updateSearchState();
  }

  function moveSection(section, direction) {
    if (!stack || !section) return;
    const sibling = direction < 0 ? section.previousElementSibling : section.nextElementSibling;
    if (!sibling || !sibling.classList.contains('file')) return;
    if (direction < 0) {
      stack.insertBefore(section, sibling);
    } else {
      stack.insertBefore(sibling, section);
    }
    refreshView();
    section.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }

  function handleDragStart(event) {
    const section = event.target.closest('.file');
    if (!section || !stack?.contains(section)) return;
    dragSource = section;
    section.classList.add('dragging');
    if (event.dataTransfer) {
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('text/plain', section.id);
    }
  }

  function handleDragOver(event) {
    if (!dragSource || !stack) return;
    const target = event.target.closest('.file');
    if (!target || target === dragSource) return;
    event.preventDefault();
    const rect = target.getBoundingClientRect();
    const before = event.clientY < rect.top + rect.height / 2;
    if (before) {
      stack.insertBefore(dragSource, target);
    } else {
      stack.insertBefore(dragSource, target.nextElementSibling);
    }
    refreshView();
  }

  function handleDragEnd() {
    if (dragSource) {
      dragSource.classList.remove('dragging');
    }
    dragSource = null;
    refreshView();
  }

  function serializeDocument() {
    const clone = document.documentElement.cloneNode(true);
    clone.querySelectorAll('.file, [data-nav-item]').forEach((node) => {
      node.hidden = false;
      node.removeAttribute('hidden');
    });

    const search = clone.querySelector('#file-search');
    if (search) {
      search.value = '';
    }

    const result = clone.querySelector('#file-result-count');
    if (result) {
      result.textContent = `${getSections().length} / ${getSections().length}`;
    }

    return '<!doctype html>\n' + clone.outerHTML;
  }

  function downloadCurrentDocument() {
    const blob = new Blob([serializeDocument()], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    const now = new Date();
    const pad = (value) => String(value).padStart(2, '0');
    const stamp = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
    anchor.href = url;
    anchor.download = `datei_wandler_export_${stamp}.html`;
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  document.addEventListener('click', (event) => {
    const control = event.target.closest('[data-move]');
    if (control) {
      const section = control.closest('.file');
      const direction = control.dataset.move === 'up' ? -1 : 1;
      moveSection(section, direction);
      return;
    }

    if (event.target.closest('#file-search-clear')) {
      if (searchInput) {
        searchInput.value = '';
        searchInput.focus();
      }
      refreshView();
      return;
    }

    if (event.target.closest('#file-download')) {
      downloadCurrentDocument();
    }
  });
  document.addEventListener('dragstart', handleDragStart);
  document.addEventListener('dragover', handleDragOver);
  document.addEventListener('dragend', handleDragEnd);

  searchInput?.addEventListener('input', updateSearchState);

  refreshView();
})();
</script>
""".strip()


def build_markdown(files: list[SourceFile], html_mode: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    body = ["# Datei-Wandler Export", "", f"Erzeugt: {now}", f"Dateien: {len(files)}", "", "## Verzeichnis", ""]
    for i, file in enumerate(files, 1):
        anchor = f"datei-{i}-{slugify(display_path(file))}"
        body.append(f"- [[#{anchor}|{export_label(file)}]]")
    body.append("")
    for i, file in enumerate(files, 1):
        anchor = f"datei-{i}-{slugify(display_path(file))}"
        body.append(f"<a id=\"{anchor}\"></a>")
        body.append(file_as_markdown(file, html_mode, anchor, files))
    return "\n".join(body)


def build_html(files: list[SourceFile], html_mode: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    nav = "\n".join(
        f'<li data-nav-item="true" data-target="f{i}"><a href="#f{i}">{html.escape(display_path(file))}</a><span>{file.origin} · {file.size_bytes} B</span></li>'
        for i, file in enumerate(files, 1)
    )
    sections: list[str] = []
    for i, file in enumerate(files, 1):
        file_path = display_path(file)
        mime = mimetypes.guess_type(file_path)[0] or "text/plain"
        warning = f'<p class="warning">{html.escape(file.warning)}</p>' if file.warning else ""
        if file.suffix in {".html", ".htm"} and html_mode in {"markdown", "both"}:
            extracted = html_to_markdown(file.content) or "_Kein Text extrahiert._"
            content = f'<h3>Aus HTML extrahierter Markdown-Text</h3><pre><code>{html.escape(extracted)}</code></pre>'
            if html_mode == "both":
                content += f'<h3>HTML-Quelltext</h3><pre><code>{html.escape(file.content)}</code></pre>'
        else:
            content = f'<pre><code>{html.escape(file.content)}</code></pre>'
        sections.append(
            f"""
            <section class="file" id="f{i}" draggable="true" data-origin="{html.escape(file.origin)}" data-size="{file.size_bytes}" data-mime="{html.escape(mime)}">
              <header class="file-head">
                <div>
                  <p>{html.escape(file.origin)} · {html.escape(mime)} · {file.size_bytes} Bytes</p>
                  <h2>{html.escape(file_path)}</h2>
                  <p class="file-path">{html.escape(file_path)}</p>
                  {warning}
                </div>
                <div class="file-controls" aria-label="Datei verschieben">
                  <button type="button" data-move="up" aria-label="Datei nach oben verschieben">↑</button>
                  <button type="button" data-move="down" aria-label="Datei nach unten verschieben">↓</button>
                </div>
              </header>
              {content}
            </section>
            """
        )
    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Datei-Wandler Export</title>
  <style>
    :root {{
      color-scheme: light dark;
      --bg: #f4eefb;
      --ink: #22153a;
      --muted: #6b5d84;
      --line: #d7c8ea;
      --panel: #fffafc;
      --accent: #6b2f8f;
      --code: #1d132b;
      --code-ink: #f1ecfb;
      --field: #fbf7ff;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #110d19;
        --ink: #f2ebff;
        --muted: #b4a8cc;
        --line: #3d324e;
        --panel: #1c1628;
        --accent: #c79aff;
        --code: #0f0b16;
        --code-ink: #f6f0ff;
        --field: #18121f;
      }}
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background:
        radial-gradient(circle at top left, rgba(107,47,143,.18), transparent 34%),
        radial-gradient(circle at 80% 0%, rgba(199,154,255,.14), transparent 30%),
        linear-gradient(180deg, var(--bg), color-mix(in srgb, var(--bg) 84%, black));
      color: var(--ink);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
    }}
    .shell {{
      display: grid;
      gap: 24px;
      max-width: 1500px;
      margin: 0 auto;
      padding: 24px;
    }}
    .statusbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: end;
      justify-content: space-between;
      border: 1px solid var(--line);
      background: var(--panel);
      padding: 16px;
    }}
    .searchbox {{
      display: grid;
      gap: 6px;
      flex: 1 1 320px;
      min-width: 240px;
    }}
    .searchbox span {{
      color: var(--muted);
      font-size: .82rem;
      text-transform: uppercase;
      letter-spacing: .08em;
      font-weight: 800;
    }}
    .searchbox input {{
      width: 100%;
      min-height: 46px;
      border: 1px solid var(--line);
      border-radius: 0;
      background: var(--field, var(--panel));
      color: var(--ink);
      padding: 11px 12px;
      font: inherit;
    }}
    .status-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }}
    .status-actions button,
    .file-controls button {{
      min-height: 40px;
      border: 1px solid var(--line);
      background: var(--code);
      color: var(--code-ink);
      padding: 0 14px;
      font: inherit;
      font-weight: 800;
      cursor: pointer;
    }}
    .status-actions button:hover,
    .file-controls button:hover {{
      filter: brightness(1.08);
    }}
    .status-actions button.secondary {{
      background: transparent;
      color: var(--ink);
    }}
    .status-summary {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      color: var(--muted);
      font-size: .92rem;
      margin: 0;
    }}
    .masthead, .file {{
      border: 1px solid var(--line);
      background: var(--panel);
    }}
    .masthead {{
      padding: 24px;
      display: grid;
      gap: 10px;
    }}
    h1, h2, h3, p {{ margin-top: 0; }}
    h1 {{ font-size: clamp(2rem, 5vw, 4.6rem); line-height: .95; margin-bottom: 0; }}
    h2 {{ font-size: clamp(1.2rem, 2vw, 2rem); line-height: 1.1; margin-bottom: 10px; }}
    h3 {{ color: var(--accent); font-size: .9rem; text-transform: uppercase; letter-spacing: .08em; }}
    .meta {{ color: var(--muted); margin: 0; }}
    .layout {{ display: grid; gap: 24px; }}
    nav {{
      border: 1px solid var(--line);
      background: var(--panel);
      padding: 18px;
      align-self: start;
    }}
    nav ol {{ padding-left: 22px; margin: 0; }}
    nav li {{ margin-bottom: 12px; }}
    nav li[hidden] {{ display: none; }}
    nav a {{ color: var(--ink); font-weight: 650; text-decoration: none; }}
    nav span {{ display: block; color: var(--muted); font-size: .88rem; }}
    .file-stack {{ display: grid; gap: 24px; }}
    .file {{ padding: 20px; margin-bottom: 24px; }}
    .file[hidden] {{ display: none; }}
    .file.dragging {{
      opacity: .58;
      outline: 2px dashed var(--accent);
      outline-offset: 2px;
    }}
    .file-head {{
      display: flex;
      gap: 16px;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 1px solid var(--line);
      padding-bottom: 12px;
      margin-bottom: 16px;
    }}
    .file header p {{ color: var(--muted); margin-bottom: 6px; }}
    .file-path {{
      margin: 0 0 10px;
      color: var(--muted);
      font-size: .84rem;
      word-break: break-word;
    }}
    .file-controls {{
      display: flex;
      gap: 8px;
      flex: 0 0 auto;
    }}
    .file,
    .file-controls button {{
      cursor: grab;
    }}
    .file:active,
    .file-controls button:active {{
      cursor: grabbing;
    }}
    .warning {{ color: #9a5b00 !important; }}
    pre {{
      overflow: auto;
      max-height: 70vh;
      margin: 0;
      padding: 18px;
      border: 1px solid var(--line);
      background: var(--code);
      color: var(--code-ink);
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      tab-size: 2;
    }}
    code {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace; font-size: .92rem; }}
    @media (min-width: 980px) {{
      .layout {{ grid-template-columns: minmax(260px, 340px) 1fr; align-items: start; }}
      nav {{ position: sticky; top: 24px; max-height: calc(100vh - 48px); overflow: auto; }}
    }}
    @media print {{
      nav {{ display: none; }}
      pre {{ max-height: none; white-space: pre-wrap; }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <header class="masthead">
      <p class="meta">Offline-Export · {html.escape(now)} · {len(files)} Dateien</p>
      <h1>Datei-Wandler Export</h1>
      <p class="meta">Inhalte sind escaped und werden angezeigt, nicht ausgefuehrt.</p>
    </header>
    <section class="statusbar" aria-label="Werkzeuge für den Export">
      <label class="searchbox" for="file-search">
        <span>Suche</span>
        <input id="file-search" type="search" placeholder="Dateiname, Inhalt, Herkunft">
      </label>
      <div class="status-actions">
        <button type="button" id="file-download">HTML herunterladen</button>
        <button type="button" id="file-search-clear" class="secondary">Suche leeren</button>
      </div>
    </section>
    <p class="status-summary"><span>Sichtbar nach Filter</span><strong id="file-result-count">{len(files)} / {len(files)}</strong></p>
    <div class="layout">
      <nav aria-label="Dateien">
        <ol data-file-nav>{nav}</ol>
      </nav>
      <div class="file-stack" data-file-stack>{''.join(sections)}</div>
    </div>
  </main>
  {export_editor_script()}
</body>
</html>
"""


def write_export(name: str, content: bytes) -> Path:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = EXPORT_DIR / name
    path.write_bytes(content)
    return path


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.post("/convert")
async def convert(
    paths: str = Form(""),
    output: str = Form("html"),
    html_mode: str = Form("markdown"),
    uploads: list[UploadFile] = File(default=[]),
) -> FileResponse:
    if output not in {"html", "markdown", "both"}:
        raise HTTPException(status_code=400, detail="Ungueltiges Ausgabeformat.")
    if html_mode not in {"source", "markdown", "both"}:
        raise HTTPException(status_code=400, detail="Ungueltiger HTML-Modus.")

    files: list[SourceFile] = []
    for line in paths.splitlines():
        path_text = line.strip()
        if path_text:
            files.append(read_path(path_text))
    for upload in uploads:
        if upload.filename:
            files.append(await read_upload(upload))

    if not files:
        raise HTTPException(status_code=400, detail="Keine Dateien angegeben.")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output == "html":
        html_doc = build_html(files, html_mode)
        path = write_export(f"datei_wandler_{stamp}.html", html_doc.encode("utf-8"))
        return FileResponse(path, media_type="text/html", filename=path.name)

    if output == "markdown":
        md_doc = build_markdown(files, html_mode)
        path = write_export(f"datei_wandler_{stamp}.md", md_doc.encode("utf-8"))
        return FileResponse(path, media_type="text/markdown", filename=path.name)

    html_doc = build_html(files, html_mode)
    md_doc = build_markdown(files, html_mode)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(f"datei_wandler_{stamp}.html", html_doc)
        archive.writestr(f"datei_wandler_{stamp}.md", md_doc)
        archive.writestr(
            "manifest.json",
            json.dumps(
                {
                    "created": stamp,
                    "files": [{"label": file.label, "origin": file.origin, "size_bytes": file.size_bytes} for file in files],
                },
                ensure_ascii=False,
                indent=2,
            ),
        )
    path = write_export(f"datei_wandler_{stamp}.zip", zip_buffer.getvalue())
    return FileResponse(path, media_type="application/zip", filename=path.name)


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "ok": True,
        "allowed_roots": [str(root) for root in ALLOWED_ROOTS],
        "max_file_bytes": MAX_FILE_BYTES,
    }
