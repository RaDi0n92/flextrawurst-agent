import os, tempfile, asyncio, json, threading, zipfile, hashlib, time, urllib.parse, urllib.request, urllib.error, shutil, subprocess, re, html, difflib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import edge_tts

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

VOICE = "de-DE-FlorianMultilingualNeural"
MAX_CHARS = 1111111
LIBRARY_PATH = Path("/root/werkraum/welt/tts_library.json")
TRANSLATION_CACHE_PATH = Path("/root/werkraum/welt/tts_translation_cache.json")
OCR_JOBS_PATH = Path("/root/werkraum/welt/tts_ocr_jobs.json")
OCR_UPLOAD_DIR = Path("/root/werkraum/welt/tts_ocr_uploads")
DOCUMENTS_PATH = Path("/root/werkraum/welt/tts_documents.json")
DOCUMENTS_UPLOAD_DIR = Path("/root/werkraum/welt/tts_documents_uploads")
DOCUMENTS_TEXT_DIR = Path("/root/werkraum/welt/tts_documents_text")
WEBARCHIVE_PATH = Path("/root/werkraum/welt/tts_webarchive.json")
WEBARCHIVE_HTML_DIR = Path("/root/werkraum/welt/tts_webarchive_html")
WEBARCHIVE_TEXT_DIR = Path("/root/werkraum/welt/tts_webarchive_text")
FORMS_PATH = Path("/root/werkraum/welt/tts_forms.json")
LOGS_PATH = Path("/root/werkraum/welt/tts_logs.json")
LOGS_UPLOAD_DIR = Path("/root/werkraum/welt/tts_logs_uploads")
_pool = ThreadPoolExecutor(max_workers=4)
_library_lock = threading.Lock()
_translation_lock = threading.Lock()
_ocr_lock = threading.Lock()
_documents_lock = threading.Lock()
_webarchive_lock = threading.Lock()
_forms_lock = threading.Lock()
_logs_lock = threading.Lock()
_translation_languages_cache = {"ts": 0.0, "items": []}
MAX_TRANSLATE_CHARS = 8000
MAX_TRANSLATE_ALL_CHARS = 1800
TRANSLATE_CACHE_LIMIT = 3000
TRANSLATE_ALL_CONCURRENCY = 3
OCR_TEXT_LIMIT = 200000
DOCUMENT_TEXT_LIMIT = 400000
DOCUMENT_CHUNK_LIMIT = 120
DOCUMENT_RESULT_LIMIT = 20
WEBARCHIVE_TEXT_LIMIT = 250000
LOG_TEXT_LIMIT = 250000
OLLAMA_BASE = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")

class TTSRequest(BaseModel):
    text: str
    voice: str = VOICE
    rate: str = "+0%"   # z.B. "+50%" für 1.5x

class LibraryPayload(BaseModel):
    categories: list[str] = ["Allgemein"]
    clips: list[dict] = []
    voiceFavorites: list[str] = []

class AudioExportRequest(BaseModel):
    ids: list[str]
    format: str = "mp3"

class TranslateRequest(BaseModel):
    text: str
    target_lang: str
    source_lang: str = "auto"

class TranslateAllRequest(BaseModel):
    text: str
    source_lang: str = "auto"

class DocumentSearchRequest(BaseModel):
    query: str = ""
    limit: int = 12
    document_ids: list[str] = []

class DocumentChatRequest(BaseModel):
    question: str
    model: str = ""
    document_ids: list[str] = []
    limit: int = 6

class OcrToDocumentRequest(BaseModel):
    ocr_job_id: str
    filename: str = ""

class WebSnapshotPayload(BaseModel):
    url: str
    title: str = ""

class FormProfilePayload(BaseModel):
    profile: str
    name: str = ""
    email: str = ""
    address: str = ""
    template: str = ""
    preview: str = ""
    extra_fields: dict[str, str] = {}

class LogAnalyzeRequest(BaseModel):
    text: str
    profile: str = ""
    filename: str = ""

class LogExplainRequest(BaseModel):
    text: str
    question: str = ""
    model: str = ""

class WebarchiveSearchRequest(BaseModel):
    query: str = ""
    limit: int = 12

class WebarchiveCompareRequest(BaseModel):
    snapshot_a: str
    snapshot_b: str

def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def _safe_name(name: str) -> str:
    clean = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in str(name or "upload"))
    clean = clean.strip(".-") or "upload"
    return clean[:120]

def _normalize_ocr_job(job: dict) -> dict:
    return {
        "id": str(job.get("id") or ""),
        "filename": str(job.get("filename") or "upload"),
        "stored_name": str(job.get("stored_name") or ""),
        "mime_type": str(job.get("mime_type") or "application/octet-stream"),
        "language": str(job.get("language") or "auto"),
        "engine": str(job.get("engine") or ""),
        "status": str(job.get("status") or "pending"),
        "text": str(job.get("text") or "")[:OCR_TEXT_LIMIT],
        "error": str(job.get("error") or ""),
        "size": int(job.get("size") or 0),
        "created_at": str(job.get("created_at") or _now_iso()),
    }

def _read_ocr_jobs() -> list[dict]:
    with _ocr_lock:
        if not OCR_JOBS_PATH.exists():
            return []
        try:
            data = json.loads(OCR_JOBS_PATH.read_text(encoding="utf-8"))
            return [_normalize_ocr_job(x) for x in data] if isinstance(data, list) else []
        except Exception:
            return []

def _write_ocr_jobs(jobs: list[dict]) -> list[dict]:
    cleaned = [_normalize_ocr_job(x) for x in jobs]
    with _ocr_lock:
        OCR_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        tmp = OCR_JOBS_PATH.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, OCR_JOBS_PATH)
    return cleaned

def _ocr_lang_code(language: str) -> str:
    lang = str(language or "auto").strip().lower()
    if lang in ("", "auto"):
        return "deu+eng"
    if lang == "deu":
        return "deu"
    if lang == "eng":
        return "eng"
    return "deu+eng"

def _extract_text_pdf(path: Path) -> tuple[str, str]:
    proc = subprocess.run(
        ["pdftotext", str(path), "-"],
        check=False,
        capture_output=True,
        text=True,
    )
    text = (proc.stdout or "").strip()
    if text:
        return text[:OCR_TEXT_LIMIT], "pdftotext"
    return "", ""

def _extract_text_image(path: Path, language: str) -> tuple[str, str]:
    tesseract = shutil.which("tesseract")
    if not tesseract:
        raise RuntimeError("Bild-OCR braucht tesseract-ocr auf dem Server.")
    proc = subprocess.run(
        [tesseract, str(path), "stdout", "-l", _ocr_lang_code(language)],
        check=False,
        capture_output=True,
        text=True,
    )
    text = (proc.stdout or "").strip()
    if proc.returncode != 0 and not text:
        raise RuntimeError((proc.stderr or "tesseract fehlgeschlagen").strip())
    return text[:OCR_TEXT_LIMIT], "tesseract"

def _sync_ocr_extract(path: Path, mime_type: str, language: str) -> tuple[str, str]:
    mime = str(mime_type or "").lower()
    suffix = path.suffix.lower()
    if mime == "application/pdf" or suffix == ".pdf":
        text, engine = _extract_text_pdf(path)
        if text:
            return text, engine
        if shutil.which("tesseract"):
            raise RuntimeError("PDF enthält keinen eingebetteten Text. Scan-OCR für PDFs ist noch nicht verdrahtet.")
        raise RuntimeError("PDF enthält keinen eingebetteten Text und tesseract-ocr fehlt.")
    return _extract_text_image(path, language)

def _read_json_list(path: Path, lock: threading.Lock, normalize) -> list[dict]:
    with lock:
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return [normalize(x) for x in data] if isinstance(data, list) else []
        except Exception:
            return []

def _write_json_list(path: Path, lock: threading.Lock, items: list[dict], normalize, parent: Path | None = None) -> list[dict]:
    cleaned = [normalize(x) for x in items]
    with lock:
        if parent:
            parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, path)
    return cleaned

def _html_to_text(raw: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", raw or "")
    text = re.sub(r"(?is)<br\s*/?>", "\n", text)
    text = re.sub(r"(?is)</(p|div|section|article|h[1-6]|li|tr)>", "\n", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = html.unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def _document_chunks(text: str, limit: int = 900, max_chunks: int = DOCUMENT_CHUNK_LIMIT) -> list[dict]:
    parts: list[str] = []
    for block in re.split(r"\n\s*\n", text or ""):
        block = re.sub(r"\s+", " ", block).strip()
        if not block:
            continue
        while len(block) > limit:
            cut = block.rfind(" ", 0, limit)
            if cut < 200:
                cut = limit
            parts.append(block[:cut].strip())
            block = block[cut:].strip()
        if block:
            parts.append(block)
        if len(parts) >= max_chunks:
            break
    if not parts and text.strip():
        parts = [short for short in (text.strip()[:limit],) if short]
    return [{"index": idx, "text": chunk} for idx, chunk in enumerate(parts[:max_chunks], 1)]

def _extract_text_docx(path: Path) -> tuple[str, str]:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml").decode("utf-8", "ignore")
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<[^>]+>", " ", xml)
    text = html.unescape(xml)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text[:DOCUMENT_TEXT_LIMIT], "docx-xml"

def _extract_text_plain(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return text[:DOCUMENT_TEXT_LIMIT], "plain-text"

def _extract_text_html(path: Path) -> tuple[str, str]:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    return _html_to_text(raw)[:DOCUMENT_TEXT_LIMIT], "html-text"

def _sync_document_extract(path: Path, mime_type: str) -> tuple[str, str]:
    mime = str(mime_type or "").lower()
    suffix = path.suffix.lower()
    if mime == "application/pdf" or suffix == ".pdf":
        text, engine = _extract_text_pdf(path)
        if text:
            return text[:DOCUMENT_TEXT_LIMIT], engine
        raise RuntimeError("PDF enthält keinen eingebetteten Text.")
    if suffix == ".docx" or "wordprocessingml.document" in mime:
        return _extract_text_docx(path)
    if suffix in {".html", ".htm"} or "text/html" in mime:
        return _extract_text_html(path)
    if suffix in {".txt", ".md", ".json", ".csv", ".log", ".py", ".js", ".ts", ".yaml", ".yml", ".ini"} or mime.startswith("text/") or mime in {"application/json", "application/xml"}:
        return _extract_text_plain(path)
    raise RuntimeError(f"Dateityp aktuell nicht unterstützt: {suffix or mime or 'unbekannt'}")

def _normalize_document(doc: dict) -> dict:
    chunks = doc.get("chunks") if isinstance(doc.get("chunks"), list) else []
    clean_chunks = []
    for chunk in chunks[:DOCUMENT_CHUNK_LIMIT]:
        if not isinstance(chunk, dict):
            continue
        clean_chunks.append({
            "index": int(chunk.get("index") or len(clean_chunks) + 1),
            "text": str(chunk.get("text") or "")[:1200],
        })
    return {
        "id": str(doc.get("id") or ""),
        "filename": str(doc.get("filename") or "upload"),
        "stored_name": str(doc.get("stored_name") or ""),
        "mime_type": str(doc.get("mime_type") or "application/octet-stream"),
        "extractor": str(doc.get("extractor") or ""),
        "status": str(doc.get("status") or "pending"),
        "size": int(doc.get("size") or 0),
        "preview": str(doc.get("preview") or "")[:1200],
        "text_path": str(doc.get("text_path") or ""),
        "text_chars": int(doc.get("text_chars") or 0),
        "chunk_count": int(doc.get("chunk_count") or len(clean_chunks)),
        "chunks": clean_chunks,
        "error": str(doc.get("error") or ""),
        "created_at": str(doc.get("created_at") or _now_iso()),
    }

def _read_documents() -> list[dict]:
    return _read_json_list(DOCUMENTS_PATH, _documents_lock, _normalize_document)

def _write_documents(items: list[dict]) -> list[dict]:
    return _write_json_list(DOCUMENTS_PATH, _documents_lock, items, _normalize_document, DOCUMENTS_UPLOAD_DIR)

def _document_tokens(text: str) -> list[str]:
    return [tok for tok in re.findall(r"[a-z0-9äöüß]{2,}", (text or "").lower()) if tok]

def _search_document_hits(query: str, documents: list[dict], limit: int = 12, document_ids: list[str] | None = None) -> list[dict]:
    query = str(query or "").strip()
    if not query:
        return []
    selected = set(document_ids or [])
    tokens = _document_tokens(query)
    full = query.lower()
    hits = []
    for doc in documents:
        if selected and doc["id"] not in selected:
            continue
        fn = doc["filename"].lower()
        for chunk in doc.get("chunks", []):
            text = str(chunk.get("text") or "")
            low = text.lower()
            score = low.count(full) * 8 + fn.count(full) * 5
            score += sum(low.count(tok) for tok in tokens)
            score += sum(fn.count(tok) for tok in tokens) * 2
            if score <= 0:
                continue
            hits.append({
                "document_id": doc["id"],
                "filename": doc["filename"],
                "created_at": doc["created_at"],
                "chunk_index": int(chunk.get("index") or 0),
                "chunk_text": text,
                "preview": short if (short := text[:220].strip()) else doc["preview"],
                "score": score,
            })
    hits.sort(key=lambda item: (-item["score"], item["filename"], item["chunk_index"]))
    return hits[:max(1, min(limit, DOCUMENT_RESULT_LIMIT))]

def _ollama_request(path: str, payload: dict | None = None) -> dict:
    url = f"{OLLAMA_BASE}{path}"
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8"))

def _ollama_models() -> list[str]:
    data = _ollama_request("/api/tags")
    models = data.get("models") if isinstance(data, dict) else []
    if not isinstance(models, list):
        return []
    return [str(item.get("name") or "").strip() for item in models if str(item.get("name") or "").strip()]

def _ollama_generate(model: str, prompt: str) -> str:
    data = _ollama_request("/api/generate", {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2},
    })
    return str(data.get("response") or "").strip()

def _normalize_websnapshot(item: dict) -> dict:
    return {
        "id": str(item.get("id") or ""),
        "url": str(item.get("url") or ""),
        "resolved_url": str(item.get("resolved_url") or item.get("url") or ""),
        "title": str(item.get("title") or ""),
        "html_path": str(item.get("html_path") or ""),
        "text_path": str(item.get("text_path") or ""),
        "text_preview": str(item.get("text_preview") or "")[:1200],
        "status": str(item.get("status") or "pending"),
        "error": str(item.get("error") or ""),
        "fetched_at": str(item.get("fetched_at") or _now_iso()),
    }

def _read_websnapshots() -> list[dict]:
    return _read_json_list(WEBARCHIVE_PATH, _webarchive_lock, _normalize_websnapshot)

def _write_websnapshots(items: list[dict]) -> list[dict]:
    return _write_json_list(WEBARCHIVE_PATH, _webarchive_lock, items, _normalize_websnapshot, WEBARCHIVE_HTML_DIR)

def _sync_fetch_snapshot(url: str) -> dict:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise RuntimeError("Nur http/https-URLs sind erlaubt.")
    req = urllib.request.Request(url, headers={"User-Agent": "flextrawurst-webarchiv/1.0"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        raw = resp.read()
        final_url = resp.geturl()
        content_type = resp.headers.get("Content-Type", "")
    encoding_match = re.search(r"charset=([a-zA-Z0-9._-]+)", content_type)
    encoding = encoding_match.group(1) if encoding_match else "utf-8"
    html_text = raw.decode(encoding, errors="ignore")
    title_match = re.search(r"(?is)<title[^>]*>(.*?)</title>", html_text)
    title = html.unescape(title_match.group(1).strip()) if title_match else ""
    text = _html_to_text(html_text)[:WEBARCHIVE_TEXT_LIMIT]
    return {"html": html_text, "text": text, "resolved_url": final_url, "title": title}

def _search_websnapshots(query: str, items: list[dict], limit: int = 12) -> list[dict]:
    query = str(query or "").strip().lower()
    if not query:
        return []
    tokens = [tok for tok in re.findall(r"[a-z0-9äöüß]{2,}", query) if tok]
    hits = []
    for item in items:
        haystacks = [
            str(item.get("title") or ""),
            str(item.get("url") or ""),
            str(item.get("resolved_url") or ""),
            str(item.get("text_preview") or ""),
        ]
        text_path = item.get("text_path")
        if text_path and Path(text_path).exists():
            try:
                haystacks.append(Path(text_path).read_text(encoding="utf-8", errors="ignore")[:WEBARCHIVE_TEXT_LIMIT])
            except Exception:
                pass
        joined = "\n".join(haystacks).lower()
        score = joined.count(query) * 8 + sum(joined.count(tok) for tok in tokens)
        if score <= 0:
            continue
        hits.append({
            **item,
            "score": score,
        })
    hits.sort(key=lambda item: (-item["score"], str(item.get("title") or ""), str(item.get("resolved_url") or "")))
    return hits[:max(1, min(limit, 30))]

def _websnapshot_versions(item: dict, items: list[dict]) -> list[dict]:
    needle = str(item.get("resolved_url") or item.get("url") or "").strip()
    if not needle:
        return []
    versions = []
    for entry in items:
        current = str(entry.get("resolved_url") or entry.get("url") or "").strip()
        if current != needle:
            continue
        versions.append({
            "id": entry.get("id"),
            "title": entry.get("title") or entry.get("resolved_url") or entry.get("url") or "",
            "fetched_at": entry.get("fetched_at") or "",
            "status": entry.get("status") or "",
        })
    versions.sort(key=lambda entry: str(entry.get("fetched_at") or ""), reverse=True)
    return versions[:20]

def _websnapshot_text(item: dict) -> str:
    text_path = item.get("text_path")
    if text_path and Path(text_path).exists():
        try:
            return Path(text_path).read_text(encoding="utf-8", errors="ignore")[:WEBARCHIVE_TEXT_LIMIT]
        except Exception:
            return ""
    return ""

def _compare_websnapshots(item_a: dict, item_b: dict) -> dict:
    text_a = _websnapshot_text(item_a)
    text_b = _websnapshot_text(item_b)
    lines_a = [line.strip() for line in text_a.splitlines() if line.strip()]
    lines_b = [line.strip() for line in text_b.splitlines() if line.strip()]
    added = [line for line in lines_b if line not in lines_a]
    removed = [line for line in lines_a if line not in lines_b]
    diff_lines = list(difflib.unified_diff(
        lines_a[:400],
        lines_b[:400],
        fromfile=str(item_a.get("id") or "a"),
        tofile=str(item_b.get("id") or "b"),
        lineterm=""
    ))
    return {
        "snapshot_a": {
            "id": item_a.get("id"),
            "title": item_a.get("title") or item_a.get("resolved_url") or item_a.get("url") or "",
            "fetched_at": item_a.get("fetched_at") or "",
        },
        "snapshot_b": {
            "id": item_b.get("id"),
            "title": item_b.get("title") or item_b.get("resolved_url") or item_b.get("url") or "",
            "fetched_at": item_b.get("fetched_at") or "",
        },
        "summary": {
            "chars_a": len(text_a),
            "chars_b": len(text_b),
            "lines_a": len(lines_a),
            "lines_b": len(lines_b),
            "added_count": len(added),
            "removed_count": len(removed),
        },
        "added": added[:20],
        "removed": removed[:20],
        "diff": "\n".join(diff_lines[:240]),
    }

def _normalize_form_profile(item: dict) -> dict:
    extra_fields = item.get("extra_fields") if isinstance(item.get("extra_fields"), dict) else {}
    clean_fields = {}
    for key, value in extra_fields.items():
        k = str(key or "").strip()[:80]
        if not k:
            continue
        clean_fields[k] = str(value or "")[:5000]
    return {
        "id": str(item.get("id") or ""),
        "profile": str(item.get("profile") or "Profil"),
        "name": str(item.get("name") or ""),
        "email": str(item.get("email") or ""),
        "address": str(item.get("address") or ""),
        "template": str(item.get("template") or "")[:20000],
        "preview": str(item.get("preview") or "")[:20000],
        "extra_fields": clean_fields,
        "created_at": str(item.get("created_at") or _now_iso()),
    }

def _read_forms() -> list[dict]:
    return _read_json_list(FORMS_PATH, _forms_lock, _normalize_form_profile)

def _write_forms(items: list[dict]) -> list[dict]:
    return _write_json_list(FORMS_PATH, _forms_lock, items, _normalize_form_profile, FORMS_PATH.parent)

def _form_export_html(item: dict) -> str:
    profile = html.escape(str(item.get("profile") or "Profil"))
    preview = html.escape(str(item.get("preview") or ""))
    extras = item.get("extra_fields") if isinstance(item.get("extra_fields"), dict) else {}
    extras_html = ""
    if extras:
        extras_html = "<ul>" + "".join(
            f"<li><strong>{html.escape(str(key))}</strong>: {html.escape(str(value))}</li>"
            for key, value in extras.items()
        ) + "</ul>"
    return (
        "<!DOCTYPE html><html lang=\"de\"><head><meta charset=\"utf-8\">"
        f"<title>{profile}</title>"
        "<style>body{font-family:system-ui,sans-serif;max-width:920px;margin:32px auto;padding:0 20px;line-height:1.55;color:#1f1f1f}"
        "pre{white-space:pre-wrap;background:#f6f6f6;padding:16px;border-radius:8px;border:1px solid #ddd}"
        "h1{font-size:1.4rem}h2{font-size:1rem;margin-top:1.5rem}</style></head><body>"
        f"<h1>{profile}</h1><pre>{preview}</pre>"
        f"{('<h2>Zusatzfelder</h2>' + extras_html) if extras_html else ''}"
        "</body></html>"
    )

def _normalize_log_entry(item: dict) -> dict:
    groups = item.get("groups") if isinstance(item.get("groups"), list) else []
    clean_groups = []
    for group in groups[:40]:
        if not isinstance(group, dict):
            continue
        clean_groups.append({
            "signature": str(group.get("signature") or "")[:300],
            "count": int(group.get("count") or 0),
            "level": str(group.get("level") or ""),
            "preview": str(group.get("preview") or "")[:500],
        })
    return {
        "id": str(item.get("id") or ""),
        "profile": str(item.get("profile") or ""),
        "filename": str(item.get("filename") or ""),
        "status": str(item.get("status") or "done"),
        "counts": item.get("counts") if isinstance(item.get("counts"), dict) else {},
        "summary": item.get("summary") if isinstance(item.get("summary"), list) else [],
        "groups": clean_groups,
        "text_preview": str(item.get("text_preview") or "")[:1200],
        "created_at": str(item.get("created_at") or _now_iso()),
    }

def _read_logs() -> list[dict]:
    return _read_json_list(LOGS_PATH, _logs_lock, _normalize_log_entry)

def _write_logs(items: list[dict]) -> list[dict]:
    return _write_json_list(LOGS_PATH, _logs_lock, items, _normalize_log_entry, LOGS_UPLOAD_DIR)

def _normalize_log_signature(line: str) -> str:
    line = re.sub(r"\b\d{4}-\d{2}-\d{2}[T ][0-9:.+-Z]+\b", "<time>", line)
    line = re.sub(r"\b0x[0-9a-f]+\b", "<hex>", line, flags=re.I)
    line = re.sub(r"\b\d+\b", "<n>", line)
    return line[:240]

def _sync_analyze_log(text: str, profile: str, filename: str) -> dict:
    lines = text.splitlines()
    counts = {"lines": len(lines), "errors": 0, "warnings": 0, "tracebacks": 0, "http_5xx": 0}
    groups: dict[str, dict] = {}
    idx = 0
    while idx < len(lines):
        raw = lines[idx]
        line = raw.strip()
        low = line.lower()
        block = [line] if line else []
        if line.startswith("Traceback (most recent call last):"):
            counts["tracebacks"] += 1
            idx += 1
            while idx < len(lines):
                nxt = lines[idx].rstrip()
                if not nxt.strip():
                    break
                block.append(nxt.strip())
                idx += 1
            line = " | ".join(block)
            low = line.lower()
        level = ""
        if any(tag in low for tag in [" error", "error ", "exception", "fatal", "critical", "traceback"]):
            level = "error"
            counts["errors"] += 1
        elif any(tag in low for tag in [" warn", "warning", "[warn]"]):
            level = "warning"
            counts["warnings"] += 1
        status_match = re.search(r"\b([45]\d{2})\b", line)
        if status_match and status_match.group(1).startswith("5"):
            level = level or "error"
            counts["http_5xx"] += 1
        if level:
            signature = _normalize_log_signature(line)
            group = groups.setdefault(signature, {
                "signature": signature,
                "count": 0,
                "level": level,
                "preview": line[:500],
            })
            group["count"] += 1
        idx += 1
    ordered_groups = sorted(groups.values(), key=lambda item: (-item["count"], item["signature"]))[:30]
    summary = [
        f"Zeilen: {counts['lines']}",
        f"Fehler: {counts['errors']}",
        f"Warnungen: {counts['warnings']}",
        f"Tracebacks: {counts['tracebacks']}",
        f"HTTP-5xx: {counts['http_5xx']}",
    ]
    if ordered_groups:
        top = ordered_groups[0]
        summary.append(f"Häufigster Block: {top['signature']} ({top['count']}x)")
    return {
        "id": f"log-{int(time.time() * 1000)}",
        "profile": profile,
        "filename": filename,
        "status": "done",
        "counts": counts,
        "summary": summary,
        "groups": ordered_groups,
        "text_preview": text[:1200],
        "created_at": _now_iso(),
    }

def _sync_explain_log(text: str, question: str, model: str) -> dict:
    models = _ollama_models()
    chosen = model.strip() or (models[0] if models else "")
    if not chosen:
        raise RuntimeError("Kein Chat-Modell gefunden.")
    prompt = (
        "Erkläre diesen Logblock knapp und technisch sauber. "
        "Nenne wahrscheinliche Ursache, was sicher belegt ist, was nur Vermutung ist, "
        "und zwei nächste Prüfungen. Erfinde nichts außerhalb des Blocks.\n\n"
        f"Frage:\n{question.strip() or 'Was ist hier los?'}\n\n"
        f"Logblock:\n{text.strip()[:6000]}\n\n"
        "Antwort:"
    )
    answer = _ollama_generate(chosen, prompt)
    return {"answer": answer, "model": chosen}

def _normalize_library(data: dict) -> dict:
    categories = data.get("categories")
    clips = data.get("clips")
    voice_favorites = data.get("voiceFavorites")
    if not isinstance(categories, list):
        categories = ["Allgemein"]
    if not isinstance(clips, list):
        clips = []
    if not isinstance(voice_favorites, list):
        voice_favorites = []
    categories = [str(x).strip() for x in categories if str(x).strip()]
    voice_favorites = [str(x).strip() for x in voice_favorites if str(x).strip()]
    return {
        "categories": list(dict.fromkeys(["Allgemein", *categories])),
        "clips": clips,
        "voiceFavorites": list(dict.fromkeys(voice_favorites)),
    }

def _read_library() -> dict:
    with _library_lock:
        if not LIBRARY_PATH.exists():
            return _normalize_library({})
        try:
            return _normalize_library(json.loads(LIBRARY_PATH.read_text(encoding="utf-8")))
        except Exception:
            return _normalize_library({})

def _write_library(data: dict) -> dict:
    library = _normalize_library(data)
    with _library_lock:
        tmp = LIBRARY_PATH.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(library, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, LIBRARY_PATH)
    return library

def _translation_lang_from_locale(locale: str) -> str:
    loc = str(locale or "").strip().replace("_", "-")
    low = loc.lower()
    if low.startswith("zh-cn") or low.startswith("zh-sg"):
        return "zh-CN"
    if low.startswith("zh-tw") or low.startswith("zh-hk"):
        return "zh-TW"
    if low.startswith("pt-br"):
        return "pt"
    if low.startswith("fil-"):
        return "tl"
    if low.startswith("nb-"):
        return "no"
    return low.split("-")[0]

def _translation_label(locale: str) -> str:
    return str(locale or "").strip() or "unknown"

def _normalize_translate_target(target: str) -> str:
    target = str(target or "").strip()
    if not target:
        raise HTTPException(status_code=400, detail="target_lang fehlt.")
    return _translation_lang_from_locale(target)

def _read_translation_cache() -> dict:
    with _translation_lock:
        if not TRANSLATION_CACHE_PATH.exists():
            return {}
        try:
            data = json.loads(TRANSLATION_CACHE_PATH.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

def _write_translation_cache(cache: dict) -> None:
    with _translation_lock:
        if len(cache) > TRANSLATE_CACHE_LIMIT:
            ordered = sorted(cache.items(), key=lambda kv: kv[1].get("ts", 0), reverse=True)
            cache = dict(ordered[:TRANSLATE_CACHE_LIMIT])
        tmp = TRANSLATION_CACHE_PATH.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, TRANSLATION_CACHE_PATH)

def _translation_cache_key(text: str, source_lang: str, target_lang: str) -> str:
    payload = json.dumps([source_lang or "auto", target_lang, text], ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def _split_translation_chunks(text: str, limit: int = 1400) -> list[str]:
    chunks = []
    rest = text.strip()
    while rest:
        if len(rest) <= limit:
            chunks.append(rest)
            break
        cut = max(rest.rfind(". ", 0, limit), rest.rfind("! ", 0, limit), rest.rfind("? ", 0, limit))
        if cut < 200:
            cut = rest.rfind(" ", 0, limit)
        if cut < 100:
            cut = limit
        chunks.append(rest[:cut + 1].strip())
        rest = rest[cut + 1:].strip()
    return [c for c in chunks if c]

def _google_translate_chunk(text: str, source_lang: str, target_lang: str) -> dict:
    params = urllib.parse.urlencode({
        "client": "gtx",
        "sl": source_lang or "auto",
        "tl": target_lang,
        "dt": "t",
        "q": text,
    })
    url = "https://translate.googleapis.com/translate_a/single?" + params
    req = urllib.request.Request(url, headers={"User-Agent": "flextrawurst-tts/1.0"})
    with urllib.request.urlopen(req, timeout=12) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    parts = data[0] if isinstance(data, list) and data else []
    detected_source = data[2] if isinstance(data, list) and len(data) > 2 else ""
    return {
        "translated": "".join(str(part[0]) for part in parts if isinstance(part, list) and part and part[0]),
        "detected_source_lang": str(detected_source or source_lang or "auto"),
    }

def _sync_translate_result(text: str, source_lang: str, target_lang: str) -> dict:
    text = text[:MAX_TRANSLATE_CHARS].strip()
    if not text:
        return {"translated": "", "detected_source_lang": source_lang or "auto"}
    source_lang = source_lang or "auto"
    target_lang = _normalize_translate_target(target_lang)
    key = _translation_cache_key(text, source_lang, target_lang)
    cache = _read_translation_cache()
    cached = cache.get(key)
    if cached and isinstance(cached.get("translated"), str) and cached.get("detected_source_lang"):
        cached["ts"] = time.time()
        _write_translation_cache(cache)
        return {
            "translated": cached["translated"],
            "detected_source_lang": cached["detected_source_lang"],
        }
    chunk_results = [_google_translate_chunk(chunk, source_lang, target_lang)
                     for chunk in _split_translation_chunks(text)]
    translated = "\n\n".join(item["translated"] for item in chunk_results)
    detected_source = next((item["detected_source_lang"] for item in chunk_results
                            if item.get("detected_source_lang")), source_lang)
    cache[key] = {
        "source_lang": source_lang,
        "detected_source_lang": detected_source,
        "target_lang": target_lang,
        "translated": translated,
        "ts": time.time(),
    }
    _write_translation_cache(cache)
    return {"translated": translated, "detected_source_lang": detected_source}

def _sync_translate(text: str, source_lang: str, target_lang: str) -> str:
    return _sync_translate_result(text, source_lang, target_lang)["translated"]

async def _translation_languages() -> list[dict]:
    now = time.time()
    if _translation_languages_cache["items"] and now - _translation_languages_cache["ts"] < 3600:
        return _translation_languages_cache["items"]
    voices = await edge_tts.list_voices()
    by_lang: dict[str, dict] = {}
    for voice in voices:
        locale = voice.get("Locale") or ""
        target = _translation_lang_from_locale(locale)
        if not target:
            continue
        item = by_lang.setdefault(target, {
            "target_lang": target,
            "label": _translation_label(locale),
            "locales": [],
            "voices": [],
        })
        if locale and locale not in item["locales"]:
            item["locales"].append(locale)
        short = voice.get("ShortName")
        if short and len(item["voices"]) < 8:
            item["voices"].append(short)
    items = sorted(by_lang.values(), key=lambda x: (x["label"], x["target_lang"]))
    _translation_languages_cache["ts"] = now
    _translation_languages_cache["items"] = items
    return items

def _sync_generate(text: str, voice: str, rate: str) -> str:
    """Runs in thread — eigener Event Loop damit edge-tts nicht den Haupt-Loop blockiert."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False, dir="/tmp")
        tmp.close()
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        loop.run_until_complete(communicate.save(tmp.name))
        return tmp.name
    finally:
        loop.close()

@app.post("/speak")
async def speak(req: TTSRequest):
    text = req.text[:MAX_CHARS].strip()
    if not text:
        return {"error": "kein text"}
    loop = asyncio.get_event_loop()
    path = await loop.run_in_executor(_pool, _sync_generate, text, req.voice, req.rate)
    return FileResponse(path, media_type="audio/mpeg", filename="tts.mp3",
                        background=None)

@app.get("/voices")
async def voices():
    v = await edge_tts.list_voices()
    return [
        {
            "name": x["ShortName"],
            "gender": x["Gender"],
            "locale": x["Locale"],
            "display": x.get("FriendlyName") or x["ShortName"],
        }
        for x in v
    ]

@app.get("/translation-languages")
async def translation_languages():
    return await _translation_languages()

@app.get("/ocr/jobs")
async def get_ocr_jobs():
    return _read_ocr_jobs()

@app.post("/ocr/jobs")
async def create_ocr_job(
    file: UploadFile = File(...),
    language: str = Form("auto"),
):
    filename = _safe_name(file.filename or "upload")
    job_id = f"ocr-{int(time.time() * 1000)}-{hashlib.sha1(filename.encode('utf-8')).hexdigest()[:8]}"
    stored_name = f"{job_id}-{filename}"
    OCR_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored_path = OCR_UPLOAD_DIR / stored_name
    payload = await file.read()
    stored_path.write_bytes(payload)
    job = {
        "id": job_id,
        "filename": filename,
        "stored_name": stored_name,
        "mime_type": file.content_type or "application/octet-stream",
        "language": language or "auto",
        "engine": "",
        "status": "processing",
        "text": "",
        "error": "",
        "size": len(payload),
        "created_at": _now_iso(),
    }
    jobs = _read_ocr_jobs()
    jobs.append(job)
    _write_ocr_jobs(jobs)
    try:
        loop = asyncio.get_event_loop()
        text, engine = await loop.run_in_executor(
            _pool,
            _sync_ocr_extract,
            stored_path,
            file.content_type or "application/octet-stream",
            language or "auto",
        )
        job["text"] = text
        job["engine"] = engine
        job["status"] = "done" if text else "empty"
        if not text:
            job["error"] = "Kein Text erkannt."
    except Exception as exc:
        job["status"] = "error"
        job["error"] = str(exc)
    jobs = [job if x.get("id") == job_id else x for x in jobs]
    _write_ocr_jobs(jobs)
    return _normalize_ocr_job(job)

@app.post("/ocr/jobs/to-document")
async def create_document_from_ocr(req: OcrToDocumentRequest):
    ocr_job_id = req.ocr_job_id.strip()
    if not ocr_job_id:
        raise HTTPException(status_code=400, detail="ocr_job_id fehlt.")
    job = next((item for item in _read_ocr_jobs() if item.get("id") == ocr_job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="OCR-Job nicht gefunden.")
    text = str(job.get("text") or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="OCR-Job enthält keinen Text.")
    base_name = _safe_name(req.filename.strip() or job.get("filename") or f"{ocr_job_id}.txt")
    if "." not in base_name:
        base_name = f"{base_name}.txt"
    doc_id = f"doc-{int(time.time() * 1000)}-{hashlib.sha1((ocr_job_id + base_name).encode('utf-8')).hexdigest()[:8]}"
    stored_name = f"{doc_id}-{base_name}"
    DOCUMENTS_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    DOCUMENTS_TEXT_DIR.mkdir(parents=True, exist_ok=True)
    stored_path = DOCUMENTS_UPLOAD_DIR / stored_name
    text_path = DOCUMENTS_TEXT_DIR / f"{doc_id}.txt"
    stored_path.write_text(text, encoding="utf-8")
    text_path.write_text(text[:DOCUMENT_TEXT_LIMIT], encoding="utf-8")
    chunks = _document_chunks(text[:DOCUMENT_TEXT_LIMIT])
    doc = {
        "id": doc_id,
        "filename": base_name,
        "stored_name": stored_name,
        "mime_type": "text/plain",
        "extractor": f"ocr:{job.get('engine') or 'text'}",
        "status": "done",
        "size": len(text.encode("utf-8")),
        "preview": text[:600],
        "text_path": str(text_path),
        "text_chars": len(text[:DOCUMENT_TEXT_LIMIT]),
        "chunk_count": len(chunks),
        "chunks": chunks,
        "error": "",
        "created_at": _now_iso(),
    }
    documents = _read_documents()
    documents.append(doc)
    _write_documents(documents)
    return _normalize_document(doc)

@app.get("/documents")
async def get_documents():
    return _read_documents()

@app.get("/documents/models")
async def get_document_models():
    try:
        return {"models": _ollama_models()}
    except Exception as exc:
        return {"models": [], "error": str(exc)}

@app.post("/documents")
async def create_documents(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="Keine Dateien erhalten.")
    documents = _read_documents()
    created = []
    for file in files[:50]:
        filename = _safe_name(file.filename or "upload")
        doc_id = f"doc-{int(time.time() * 1000)}-{hashlib.sha1((filename + str(time.time())).encode('utf-8')).hexdigest()[:8]}"
        stored_name = f"{doc_id}-{filename}"
        DOCUMENTS_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        DOCUMENTS_TEXT_DIR.mkdir(parents=True, exist_ok=True)
        stored_path = DOCUMENTS_UPLOAD_DIR / stored_name
        payload = await file.read()
        stored_path.write_bytes(payload)
        doc = {
            "id": doc_id,
            "filename": filename,
            "stored_name": stored_name,
            "mime_type": file.content_type or "application/octet-stream",
            "extractor": "",
            "status": "processing",
            "size": len(payload),
            "preview": "",
            "text_path": str(DOCUMENTS_TEXT_DIR / f"{doc_id}.txt"),
            "text_chars": 0,
            "chunk_count": 0,
            "chunks": [],
            "error": "",
            "created_at": _now_iso(),
        }
        documents.append(doc)
        _write_documents(documents)
        try:
            loop = asyncio.get_event_loop()
            text, extractor = await loop.run_in_executor(
                _pool, _sync_document_extract, stored_path, file.content_type or "application/octet-stream"
            )
            text = text[:DOCUMENT_TEXT_LIMIT].strip()
            Path(doc["text_path"]).write_text(text, encoding="utf-8")
            chunks = _document_chunks(text)
            doc["extractor"] = extractor
            doc["status"] = "done" if text else "empty"
            doc["preview"] = text[:600]
            doc["text_chars"] = len(text)
            doc["chunk_count"] = len(chunks)
            doc["chunks"] = chunks
            if not text:
                doc["error"] = "Kein Text extrahiert."
        except Exception as exc:
            doc["status"] = "error"
            doc["error"] = str(exc)
        documents = [doc if item.get("id") == doc_id else item for item in documents]
        _write_documents(documents)
        created.append(_normalize_document(doc))
    return created

@app.post("/documents/search")
async def search_documents(req: DocumentSearchRequest):
    documents = _read_documents()
    hits = _search_document_hits(req.query, documents, req.limit, req.document_ids)
    return {"hits": hits, "count": len(hits)}

@app.post("/documents/chat")
async def chat_documents(req: DocumentChatRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Frage fehlt.")
    documents = _read_documents()
    hits = _search_document_hits(question, documents, req.limit or 6, req.document_ids)
    if not hits:
        return {"answer": "", "sources": [], "model": req.model, "note": "Keine passenden Textstellen gefunden."}
    try:
        models = _ollama_models()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Ollama nicht erreichbar: {exc}")
    model = req.model.strip() or (models[0] if models else "")
    if not model:
        raise HTTPException(status_code=503, detail="Kein Chat-Modell gefunden.")
    context = "\n\n".join(
        f"[Quelle {idx}] Datei: {hit['filename']} | Chunk {hit['chunk_index']}\n{hit['chunk_text']}"
        for idx, hit in enumerate(hits, 1)
    )
    prompt = (
        "Beantworte die Frage nur aus den gelieferten Dokumentauszügen. "
        "Wenn etwas nicht belegt ist, sag es klar. Antworte knapp und nenne die Quellen in Klammern.\n\n"
        f"Frage:\n{question}\n\n"
        f"Dokumentauszüge:\n{context}\n\n"
        "Antwort:"
    )
    try:
        answer = await asyncio.get_event_loop().run_in_executor(_pool, _ollama_generate, model, prompt)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Chat fehlgeschlagen: {exc}")
    return {"answer": answer, "sources": hits, "model": model}

@app.get("/documents/{document_id}")
async def get_document(document_id: str):
    item = next((entry for entry in _read_documents() if entry["id"] == document_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Dokument nicht gefunden.")
    text = ""
    text_path = item.get("text_path")
    if text_path and Path(text_path).exists():
        text = Path(text_path).read_text(encoding="utf-8", errors="ignore")
    return {**item, "text": text[:DOCUMENT_TEXT_LIMIT]}

@app.get("/webarchive/snapshots")
async def get_websnapshots():
    return _read_websnapshots()

@app.post("/webarchive/search")
async def search_websnapshots(req: WebarchiveSearchRequest):
    hits = _search_websnapshots(req.query, _read_websnapshots(), req.limit or 12)
    return {"hits": hits, "count": len(hits)}

@app.post("/webarchive/compare")
async def compare_websnapshots(req: WebarchiveCompareRequest):
    items = _read_websnapshots()
    item_a = next((entry for entry in items if entry["id"] == req.snapshot_a.strip()), None)
    item_b = next((entry for entry in items if entry["id"] == req.snapshot_b.strip()), None)
    if not item_a or not item_b:
        raise HTTPException(status_code=404, detail="Ein oder beide Snapshots nicht gefunden.")
    return _compare_websnapshots(item_a, item_b)

@app.get("/webarchive/snapshots/{snapshot_id}")
async def get_websnapshot(snapshot_id: str):
    items = _read_websnapshots()
    item = next((entry for entry in items if entry["id"] == snapshot_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Snapshot nicht gefunden.")
    text = ""
    text_path = item.get("text_path")
    if text_path and Path(text_path).exists():
        text = Path(text_path).read_text(encoding="utf-8", errors="ignore")
    return {
        **item,
        "text": text[:WEBARCHIVE_TEXT_LIMIT],
        "versions": _websnapshot_versions(item, items),
        "html_url": f"/webarchive/snapshots/{snapshot_id}/raw/html",
        "text_url": f"/webarchive/snapshots/{snapshot_id}/raw/text",
    }

@app.get("/webarchive/snapshots/{snapshot_id}/raw/{kind}")
async def get_websnapshot_raw(snapshot_id: str, kind: str):
    item = next((entry for entry in _read_websnapshots() if entry["id"] == snapshot_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Snapshot nicht gefunden.")
    if kind == "html":
        path = item.get("html_path") or ""
        media_type = "text/html"
        filename = f"{snapshot_id}.html"
    elif kind == "text":
        path = item.get("text_path") or ""
        media_type = "text/plain; charset=utf-8"
        filename = f"{snapshot_id}.txt"
    else:
        raise HTTPException(status_code=400, detail="Nur html oder text erlaubt.")
    file_path = Path(path)
    if not path or not file_path.exists():
        raise HTTPException(status_code=404, detail="Rohdatei nicht gefunden.")
    return FileResponse(str(file_path), media_type=media_type, filename=filename)

@app.post("/webarchive/snapshots")
async def create_websnapshot(payload: WebSnapshotPayload):
    url = payload.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL fehlt.")
    snapshot_id = f"snap-{int(time.time() * 1000)}"
    item = {
        "id": snapshot_id,
        "url": url,
        "resolved_url": url,
        "title": payload.title.strip(),
        "html_path": str(WEBARCHIVE_HTML_DIR / f"{snapshot_id}.html"),
        "text_path": str(WEBARCHIVE_TEXT_DIR / f"{snapshot_id}.txt"),
        "text_preview": "",
        "status": "processing",
        "error": "",
        "fetched_at": _now_iso(),
    }
    items = _read_websnapshots()
    items.append(item)
    _write_websnapshots(items)
    try:
        WEBARCHIVE_HTML_DIR.mkdir(parents=True, exist_ok=True)
        WEBARCHIVE_TEXT_DIR.mkdir(parents=True, exist_ok=True)
        data = await asyncio.get_event_loop().run_in_executor(_pool, _sync_fetch_snapshot, url)
        Path(item["html_path"]).write_text(data["html"], encoding="utf-8")
        Path(item["text_path"]).write_text(data["text"], encoding="utf-8")
        item["resolved_url"] = data["resolved_url"]
        item["title"] = item["title"] or data["title"] or data["resolved_url"]
        item["text_preview"] = data["text"][:600]
        item["status"] = "done"
    except Exception as exc:
        item["status"] = "error"
        item["error"] = str(exc)
    items = [item if entry.get("id") == snapshot_id else entry for entry in items]
    _write_websnapshots(items)
    return _normalize_websnapshot(item)

@app.get("/forms/profiles")
async def get_form_profiles():
    return _read_forms()

@app.post("/forms/profiles")
async def create_form_profile(payload: FormProfilePayload):
    entry = {
        "id": f"form-{int(time.time() * 1000)}",
        "profile": payload.profile.strip() or "Profil",
        "name": payload.name.strip(),
        "email": payload.email.strip(),
        "address": payload.address.strip(),
        "template": payload.template,
        "preview": payload.preview,
        "extra_fields": payload.extra_fields,
        "created_at": _now_iso(),
    }
    items = _read_forms()
    items.append(entry)
    _write_forms(items)
    return _normalize_form_profile(entry)

@app.get("/forms/profiles/{form_id}/export/{fmt}")
async def export_form_profile(form_id: str, fmt: str):
    item = next((entry for entry in _read_forms() if entry["id"] == form_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Formularprofil nicht gefunden.")
    safe_name = _safe_name(item.get("profile") or "formular")
    if fmt == "txt":
        tmp = tempfile.NamedTemporaryFile(suffix=".txt", delete=False, dir="/tmp")
        tmp.write((str(item.get("preview") or "") + "\n").encode("utf-8"))
        tmp.close()
        return FileResponse(tmp.name, media_type="text/plain; charset=utf-8", filename=f"{safe_name}.txt")
    if fmt == "html":
        tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False, dir="/tmp")
        tmp.write(_form_export_html(item).encode("utf-8"))
        tmp.close()
        return FileResponse(tmp.name, media_type="text/html; charset=utf-8", filename=f"{safe_name}.html")
    raise HTTPException(status_code=400, detail="Nur txt oder html erlaubt.")

@app.get("/logs/analyses")
async def get_log_analyses():
    return _read_logs()

@app.post("/logs/analyze")
async def analyze_log(req: LogAnalyzeRequest):
    text = req.text[:LOG_TEXT_LIMIT].strip()
    if not text:
        raise HTTPException(status_code=400, detail="Logtext fehlt.")
    entry = await asyncio.get_event_loop().run_in_executor(
        _pool, _sync_analyze_log, text, req.profile.strip(), req.filename.strip()
    )
    items = _read_logs()
    items.append(entry)
    _write_logs(items)
    return _normalize_log_entry(entry)

@app.post("/logs/explain")
async def explain_log(req: LogExplainRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Kein Logblock zum Erklären erhalten.")
    try:
        result = await asyncio.get_event_loop().run_in_executor(
            _pool, _sync_explain_log, text, req.question, req.model
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Log-Erklärung fehlgeschlagen: {exc}")

@app.post("/translate")
async def translate(req: TranslateRequest):
    text = req.text[:MAX_TRANSLATE_CHARS].strip()
    if not text:
        return {"translated": "", "target_lang": _normalize_translate_target(req.target_lang)}
    target = _normalize_translate_target(req.target_lang)
    result = await asyncio.get_event_loop().run_in_executor(
        _pool, _sync_translate_result, text, req.source_lang, target
    )
    return {
        "source_lang": req.source_lang or "auto",
        "detected_source_lang": result["detected_source_lang"],
        "target_lang": target,
        "translated": result["translated"],
    }

@app.post("/translate-all")
async def translate_all(req: TranslateAllRequest):
    text = req.text[:MAX_TRANSLATE_ALL_CHARS].strip()
    if not text:
        return {"results": [], "limit": MAX_TRANSLATE_ALL_CHARS}
    languages = await _translation_languages()
    sem = asyncio.Semaphore(TRANSLATE_ALL_CONCURRENCY)

    async def one(lang: dict) -> dict:
        target = lang["target_lang"]
        async with sem:
            try:
                translated = await asyncio.get_event_loop().run_in_executor(
                    _pool, _sync_translate, text, req.source_lang, target
                )
                return {**lang, "translated": translated, "ok": True}
            except Exception as exc:
                return {**lang, "translated": "", "ok": False, "error": str(exc)}

    results = await asyncio.gather(*(one(lang) for lang in languages))
    return {
        "source_lang": req.source_lang or "auto",
        "limit": MAX_TRANSLATE_ALL_CHARS,
        "results": results,
    }

@app.get("/library")
async def get_library():
    return _read_library()

@app.put("/library")
async def put_library(payload: LibraryPayload):
    data = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    return _write_library(data)

@app.get("/offline.html")
async def offline_html():
    return FileResponse(
        "/root/werkraum/welt/tts_ui.html",
        media_type="text/html",
        filename="tts-soundboard-offline.html",
    )

@app.post("/export-audio")
async def export_audio(req: AudioExportRequest):
    if req.format.lower() != "mp3":
        raise HTTPException(status_code=400, detail="Batch-Export unterstützt serverseitig aktuell MP3.")
    library = _read_library()
    wanted = set(req.ids[:200])
    clips = [c for c in library["clips"] if str(c.get("id")) in wanted]
    if not clips:
        raise HTTPException(status_code=404, detail="Keine Clips gefunden.")
    zip_tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False, dir="/tmp")
    zip_tmp.close()
    with zipfile.ZipFile(zip_tmp.name, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for i, clip in enumerate(clips, 1):
            text = str(clip.get("text") or "")[:MAX_CHARS].strip()
            if not text:
                continue
            voice = str(clip.get("voice") or VOICE)
            rate = str(clip.get("rate") or "+0%")
            path = await asyncio.get_event_loop().run_in_executor(_pool, _sync_generate, text, voice, rate)
            title = str(clip.get("title") or f"clip-{i}")
            safe = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in title).strip("-") or f"clip-{i}"
            zf.write(path, f"{i:03d}-{safe[:80]}.mp3")
            try:
                os.unlink(path)
            except OSError:
                pass
    return FileResponse(zip_tmp.name, media_type="application/zip", filename="tts-clips-mp3.zip")

@app.get("/", response_class=HTMLResponse)
async def ui():
    from fastapi.responses import Response
    with open("/root/werkraum/welt/tts_ui.html", encoding="utf-8") as f:
        content = f.read()
    return Response(content=content, media_type="text/html", headers={
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("tts_service:app", host="0.0.0.0", port=8035, workers=1)
