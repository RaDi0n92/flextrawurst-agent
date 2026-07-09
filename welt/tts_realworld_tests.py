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
HARD_DOC = Path(os.environ.get("TTS_HARD_DOC", "/root/werkraum/welt/api.py"))
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


def make_hard_ocr_image(path: Path) -> str:
    truth = "Schwieriger OCR Test 98431\nkleine Schrift, Rauschen, leichte Drehung\nFlextrawurst bleibt lesbar"
    img = Image.new("RGB", (1500, 520), (247, 244, 235))
    draw = ImageDraw.Draw(img)
    font = None
    font_small = None
    candidate = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    if candidate.exists():
        font = ImageFont.truetype(str(candidate), 38)
        font_small = ImageFont.truetype(str(candidate), 28)
    for x in range(0, 1500, 17):
        draw.line((x, 0, x + 210, 520), fill=(226, 222, 212), width=1)
    draw.text((80, 70), "Schwieriger OCR Test 98431", fill=(25, 25, 25), font=font)
    draw.text((80, 160), "kleine Schrift, Rauschen, leichte Drehung", fill=(40, 40, 40), font=font_small)
    draw.text((80, 235), "Flextrawurst bleibt lesbar", fill=(25, 25, 25), font=font)
    for i in range(800):
        x = (i * 37) % 1500
        y = (i * 91) % 520
        draw.point((x, y), fill=(90, 85, 80))
    img = img.rotate(-2.0, expand=True, fillcolor=(247, 244, 235))
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

        hard_image = tmpdir / "ocr_hard.png"
        hard_truth = make_hard_ocr_image(hard_image)
        hard_job = http_multipart("/ocr/jobs", "file", [hard_image], {"language": "deu"}, timeout=180)
        created_ocr.append(hard_job["id"])
        hard_text = str(hard_job.get("text") or "")
        hard_quality = http_json("POST", "/quality/text", {
            "expected": hard_truth,
            "actual": hard_text,
            "required_terms": ["Schwieriger", "98431", "Flextrawurst"],
        })
        check(
            "image_ocr_hard_noisy_rotated",
            hard_job.get("status") == "done"
            and hard_quality.get("required_coverage", 0) >= 0.66
            and hard_quality.get("word_coverage", 0) >= 0.45,
            f"status={hard_job.get('status')} quality={hard_job.get('quality')} text_quality={hard_quality} text={hard_text[:300]!r}",
            report,
        )

        if VISION_IMAGE.exists():
            vision_job = http_multipart("/ocr/jobs", "file", [VISION_IMAGE], {"language": "deu"}, timeout=180)
            created_ocr.append(vision_job["id"])
            vision_text = str(vision_job.get("text") or "")
            vision_quality = http_json("POST", "/quality/text", {
                "expected": "Flextrawurst Zwischenraum Gärküche Werkraum Archivluft Streitstrom GENI Splitter Obsidian Inspektor Resonanz",
                "actual": vision_text,
                "required_terms": ["Flextrawurst", "Zwischenraum", "Werkraum", "GENI", "Splitter", "Resonanz"],
            })
            check(
                "image_ocr_real_vision_groundtruth_terms",
                vision_job.get("status") == "done"
                and int(vision_quality.get("chars") or 0) > 1000
                and float(vision_quality.get("required_coverage") or 0) >= 0.5,
                f"status={vision_job.get('status')} quality={vision_job.get('quality')} vision_quality={vision_quality} sample={vision_text[:500]!r}",
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

        if HARD_DOC.exists():
            hard_doc_created = http_multipart("/documents", "files", [HARD_DOC], timeout=180)
            hard_doc = hard_doc_created[0]
            created_docs.append(hard_doc["id"])
            hard_raw_size = len(HARD_DOC.read_text(encoding="utf-8", errors="ignore"))
            check(
                "document_import_large_code_file",
                hard_doc.get("status") == "done"
                and hard_doc.get("quality", {}).get("usable") is True
                and int(hard_doc.get("text_chars") or 0) > 100000
                and int(hard_doc.get("chunk_count") or 0) > 100,
                f"status={hard_doc.get('status')} quality={hard_doc.get('quality')} raw_size={hard_raw_size}",
                report,
            )
            hard_search = http_json("POST", "/documents/search", {"query": "FastAPI events visibility", "document_ids": [hard_doc["id"]], "limit": 12})
            check(
                "document_search_large_code_file",
                int(hard_search.get("count") or 0) > 0,
                json.dumps(hard_search, ensure_ascii=False)[:600],
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
        form_scan = http_json("POST", "/forms/scan", {"template": form_template})
        expected_field_keys = {field["key"] for field in form_scan.get("fields", [])}
        check(
            "form_scan_derives_expectations",
            expected_field_keys == {"name", "email", "address", "firma"},
            json.dumps(form_scan, ensure_ascii=False),
            report,
        )
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
                "title": "realworld-flextrawurst-deep",
                "max_pages": 20,
                "render_mode": "http",
            }, timeout=300)
            created_snaps.append(snap["id"])
            check(
                "webarchive_real_flextrawurst",
                snap.get("status") == "done"
                and snap.get("quality", {}).get("usable") is True
                and int(snap.get("page_count") or 0) >= 11
                and int(snap.get("quality", {}).get("text_chars") or 0) > 100000
                and float(snap.get("quality", {}).get("replacement_ratio", 1)) < 0.01
                and float(snap.get("quality", {}).get("symbolic_noise_ratio", 1)) < 0.08,
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

        try:
            rendered = http_json("POST", "/webarchive/snapshots", {
                "url": "http://127.0.0.1:8035/",
                "title": "realworld-browser-rendered-local",
                "max_pages": 1,
                "render_mode": "browser",
            }, timeout=120)
            created_snaps.append(rendered["id"])
            check(
                "webarchive_browser_rendered_snapshot",
                rendered.get("status") == "done"
                and rendered.get("quality", {}).get("usable") is True
                and int(rendered.get("quality", {}).get("text_chars") or 0) > 1000,
                json.dumps({
                    "status": rendered.get("status"),
                    "quality": rendered.get("quality"),
                    "resolved_url": rendered.get("resolved_url"),
                }, ensure_ascii=False),
                report,
            )
        except Exception as exc:
            check("webarchive_browser_rendered_snapshot", False, f"{type(exc).__name__}: {exc}", report)

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
