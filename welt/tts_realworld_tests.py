#!/usr/bin/env python3
import json
import mimetypes
import os
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE = os.environ.get("TTS_BASE", "http://127.0.0.1:8035").rstrip("/")
REPORT_PATH = Path(os.environ.get("TTS_REALWORLD_REPORT", "/tmp/tts_realworld_report.json"))
REAL_DOC = Path(os.environ.get("TTS_REAL_DOC", "/root/werkraum/geni/README.md"))
VISION_IMAGE = Path(os.environ.get("TTS_VISION_IMAGE", "/root/visionen/ChatGPT Image 21. Mai 2026, 23_30_02.png"))


def http_json(method: str, path: str, payload: dict | None = None, timeout: int = 60) -> dict:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def http_multipart(path: str, field: str, files: list[Path], extra: dict[str, str] | None = None, timeout: int = 120):
    boundary = f"----tts-realworld-{int(time.time() * 1000)}"
    chunks: list[bytes] = []
    for key, value in (extra or {}).items():
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode())
        chunks.append(str(value).encode("utf-8"))
        chunks.append(b"\r\n")
    for file_path in files:
        mime = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(
            f'Content-Disposition: form-data; name="{field}"; filename="{file_path.name}"\r\n'
            f"Content-Type: {mime}\r\n\r\n".encode()
        )
        chunks.append(file_path.read_bytes())
        chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode())
    body = b"".join(chunks)
    req = urllib.request.Request(
        BASE + path,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "Content-Length": str(len(body))},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def check(name: str, ok: bool, detail: str, report: list[dict]) -> None:
    report.append({"name": name, "ok": bool(ok), "detail": detail})


def make_ocr_truth_image(path: Path) -> str:
    truth = "Flextrawurst OCR Wahrheit 4279\nDaniel testet echte Bild OCR."
    img = Image.new("RGB", (1400, 420), "white")
    draw = ImageDraw.Draw(img)
    font = None
    for candidate in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"):
        if Path(candidate).exists():
            font = ImageFont.truetype(candidate, 54)
            break
    draw.text((60, 90), truth, fill="black", font=font)
    img.save(path)
    return truth


def main() -> int:
    report: list[dict] = []
    created_docs: list[str] = []
    created_ocr: list[str] = []
    created_snaps: list[str] = []
    created_forms: list[str] = []
    tmpdir = Path(tempfile.mkdtemp(prefix="tts-realworld-"))
    try:
        status = http_json("GET", "/ocr/status")
        check("ocr_status_tesseract", status.get("tesseract") is True, json.dumps(status, ensure_ascii=False), report)
        check("ocr_status_pdftotext", status.get("pdftotext") is True, json.dumps(status, ensure_ascii=False), report)

        ocr_image = tmpdir / "ocr_truth.png"
        truth = make_ocr_truth_image(ocr_image)
        ocr_job = http_multipart("/ocr/jobs", "file", [ocr_image], {"language": "deu"}, timeout=120)
        created_ocr.append(ocr_job["id"])
        ocr_text = str(ocr_job.get("text") or "")
        check(
            "image_ocr_truth",
            ocr_job.get("status") == "done" and "Flextrawurst" in ocr_text and "4279" in ocr_text and int(ocr_job.get("quality", {}).get("chars") or 0) > 20,
            f"status={ocr_job.get('status')} quality={ocr_job.get('quality')} text={ocr_text[:220]!r} truth={truth!r}",
            report,
        )

        if VISION_IMAGE.exists():
            vision_job = http_multipart("/ocr/jobs", "file", [VISION_IMAGE], {"language": "deu"}, timeout=180)
            created_ocr.append(vision_job["id"])
            vision_text = str(vision_job.get("text") or "")
            check(
                "image_ocr_real_vision_nonempty",
                vision_job.get("status") in {"done", "empty"} and len(vision_text.strip()) >= 0,
                f"status={vision_job.get('status')} chars={len(vision_text)} error={vision_job.get('error') or ''}",
                report,
            )

        if not REAL_DOC.exists():
            raise RuntimeError(f"REAL_DOC fehlt: {REAL_DOC}")
        doc_created = http_multipart("/documents", "files", [REAL_DOC], timeout=120)
        doc = doc_created[0]
        created_docs.append(doc["id"])
        raw_size = len(REAL_DOC.read_text(encoding="utf-8", errors="ignore"))
        check(
            "document_import_real_markdown",
            doc.get("status") == "done" and doc.get("quality", {}).get("usable") is True and int(doc.get("text_chars") or 0) > min(500, raw_size // 2),
            f"status={doc.get('status')} quality={doc.get('quality')} text_chars={doc.get('text_chars')} raw_size={raw_size} chunks={doc.get('chunk_count')}",
            report,
        )
        search = http_json("POST", "/documents/search", {"query": "GENI", "document_ids": [doc["id"]], "limit": 8})
        check("document_search_real", int(search.get("count") or 0) > 0, json.dumps(search, ensure_ascii=False)[:500], report)
        chunk_index = int((doc.get("chunks") or [{"index": 1}])[0].get("index") or 1)
        edited = http_json("PUT", f"/documents/{urllib.parse.quote(doc['id'])}/chunks/{chunk_index}", {"text": "REALWORLD CHUNK EDIT 9917"})
        check(
            "document_chunk_edit",
            any("9917" in str(chunk.get("text") or "") for chunk in edited.get("chunks", [])),
            json.dumps({"chunk_count": edited.get("chunk_count"), "preview": edited.get("preview")}, ensure_ascii=False),
            report,
        )

        form_template = """
        <form>
          <input name="name" value="">
          <input id="email">
          <textarea name="address"></textarea>
          <p>{{firma}}</p>
        </form>
        """
        form_fill = http_json("POST", "/forms/fill", {
            "template": form_template,
            "fields": {
                "name": "Daniel Realtest",
                "email": "daniel@example.test",
                "address": "Werkraum 1",
                "firma": "Flextrawurst",
            }
        })
        preview = str(form_fill.get("preview") or "")
        check(
            "form_fill_html_and_placeholders",
            'value="Daniel Realtest"' in preview and 'value="daniel@example.test"' in preview and "Werkraum 1" in preview and "Flextrawurst" in preview and not form_fill.get("quality", {}).get("unfilled_placeholders"),
            f"quality={form_fill.get('quality')} preview={preview}",
            report,
        )
        form_saved = http_json("POST", "/forms/profiles", {
            "profile": "realworld-test",
            "name": "Daniel Realtest",
            "email": "daniel@example.test",
            "address": "Werkraum 1",
            "template": form_template,
            "preview": preview,
            "extra_fields": {"firma": "Flextrawurst"},
        })
        created_forms.append(form_saved["id"])
        check("form_profile_save", bool(form_saved.get("id")), json.dumps(form_saved, ensure_ascii=False)[:500], report)

        try:
            snap = http_json("POST", "/webarchive/snapshots", {
                "url": "https://flextrawurst.de/",
                "title": "realworld-flextrawurst",
                "max_pages": 5,
            }, timeout=180)
            created_snaps.append(snap["id"])
            check(
                "webarchive_real_flextrawurst",
                snap.get("status") == "done" and snap.get("quality", {}).get("usable") is True and int(snap.get("page_count") or 0) >= 1 and len(str(snap.get("text_preview") or "")) > 200,
                json.dumps({
                    "status": snap.get("status"),
                    "page_count": snap.get("page_count"),
                    "quality": snap.get("quality"),
                    "resolved_url": snap.get("resolved_url"),
                    "preview_chars": len(str(snap.get("text_preview") or "")),
                    "error": snap.get("error") or "",
                }, ensure_ascii=False),
                report,
            )
        except Exception as exc:
            check("webarchive_real_flextrawurst", False, f"{type(exc).__name__}: {exc}", report)

    finally:
        for form_id in created_forms:
            try:
                http_json("DELETE", f"/forms/profiles/{urllib.parse.quote(form_id)}")
            except Exception:
                pass
        for snap_id in created_snaps:
            try:
                http_json("DELETE", f"/webarchive/snapshots/{urllib.parse.quote(snap_id)}")
            except Exception:
                pass
        for doc_id in created_docs:
            try:
                http_json("DELETE", f"/documents/{urllib.parse.quote(doc_id)}")
            except Exception:
                pass
        for job_id in created_ocr:
            try:
                http_json("DELETE", f"/ocr/jobs/{urllib.parse.quote(job_id)}")
            except Exception:
                pass

    ok = all(item["ok"] for item in report)
    payload = {
        "ok": ok,
        "base": BASE,
        "report": report,
        "created_cleanup": {
            "documents": created_docs,
            "ocr_jobs": created_ocr,
            "snapshots": created_snaps,
            "forms": created_forms,
        },
    }
    REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
