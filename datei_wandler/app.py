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
    return SourceFile(str(path), "path", path.suffix.lower(), content, size, warning)


async def read_upload(upload: UploadFile) -> SourceFile:
    raw = await upload.read()
    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(status_code=400, detail=f"Upload zu gross ({len(raw)} Bytes): {upload.filename}")
    name = upload.filename or "upload"
    if is_blocked(Path(name)):
        raise HTTPException(status_code=400, detail=f"Blockierter Upload-Name: {name}")
    try:
        content, warning = decode_text(raw)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"{name}: {exc}") from exc
    return SourceFile(name, "upload", Path(name).suffix.lower(), content, len(raw), warning)


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


def file_as_markdown(file: SourceFile, html_mode: str) -> str:
    lines = [f"## {file.label}", "", f"- Quelle: {file.origin}", f"- Groesse: {file.size_bytes} Bytes"]
    if file.warning:
        lines.append(f"- Hinweis: {file.warning}")
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


def build_markdown(files: list[SourceFile], html_mode: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    body = ["# Datei-Wandler Export", "", f"Erzeugt: {now}", f"Dateien: {len(files)}", ""]
    for file in files:
        body.append(file_as_markdown(file, html_mode))
    return "\n".join(body)


def build_html(files: list[SourceFile], html_mode: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    nav = "\n".join(
        f'<li><a href="#f{i}">{html.escape(file.label)}</a><span>{file.origin} · {file.size_bytes} B</span></li>'
        for i, file in enumerate(files, 1)
    )
    sections: list[str] = []
    for i, file in enumerate(files, 1):
        mime = mimetypes.guess_type(file.label)[0] or "text/plain"
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
            <section class="file" id="f{i}">
              <header>
                <p>{html.escape(file.origin)} · {html.escape(mime)} · {file.size_bytes} Bytes</p>
                <h2>{html.escape(file.label)}</h2>
                {warning}
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
      --bg: #f6f5f2;
      --ink: #171717;
      --muted: #62615d;
      --line: #d8d5ce;
      --panel: #ffffff;
      --accent: #0c6b58;
      --code: #111;
      --code-ink: #e9ece8;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #161716;
        --ink: #e9e8e2;
        --muted: #a9a79e;
        --line: #3a3b37;
        --panel: #20211f;
        --accent: #69c5a8;
        --code: #0c0d0c;
        --code-ink: #e9ece8;
      }}
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
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
    nav a {{ color: var(--ink); font-weight: 650; text-decoration: none; }}
    nav span {{ display: block; color: var(--muted); font-size: .88rem; }}
    .file {{ padding: 20px; margin-bottom: 24px; }}
    .file header p {{ color: var(--muted); margin-bottom: 6px; }}
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
    <div class="layout">
      <nav aria-label="Dateien"><ol>{nav}</ol></nav>
      <div>{''.join(sections)}</div>
    </div>
  </main>
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
