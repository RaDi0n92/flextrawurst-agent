#!/usr/bin/env python3
import json
import os
import tempfile
import time
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright, expect


BASE = os.environ.get("TTS_BASE", "http://127.0.0.1:8035").rstrip("/")
REPORT_PATH = Path(os.environ.get("TTS_BROWSER_REPORT", "/tmp/tts_browser_e2e_report.json"))


def http_json(method: str, path: str):
    req = urllib.request.Request(BASE + path, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def ids(path: str) -> set[str]:
    data = http_json("GET", path)
    if isinstance(data, list):
        return {str(item.get("id")) for item in data if item.get("id")}
    return set()


def delete_new(path: str, before: set[str]) -> list[str]:
    after = ids(path)
    created = sorted(after - before)
    for item_id in created:
        try:
            http_json("DELETE", f"{path}/{item_id}")
        except Exception:
            pass
    return created


def make_ocr_image(path: Path) -> str:
    truth = "Browser OCR Wahrheit 7319"
    img = Image.new("RGB", (1100, 260), "white")
    draw = ImageDraw.Draw(img)
    font = None
    candidate = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    if candidate.exists():
        font = ImageFont.truetype(str(candidate), 52)
    draw.text((50, 80), truth, fill="black", font=font)
    img.save(path)
    return truth


def main() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="tts-browser-e2e-"))
    report: list[dict] = []

    def record(name: str, ok: bool, detail: str = "") -> None:
        report.append({"name": name, "ok": bool(ok), "detail": detail})

    doc_path = tmpdir / "browser_doc.txt"
    doc_path.write_text(
        "Browser Dokument Wahrheit 8421.\n\n"
        "GENI steht hier als Suchwort.\n\n"
        "Dritter Absatz fuer Chunk-Navigation.",
        encoding="utf-8",
    )
    image_path = tmpdir / "browser_ocr.png"
    ocr_truth = make_ocr_image(image_path)
    before_ocr = ids("/ocr/jobs")
    before_documents = ids("/documents")
    before_snapshots = ids("/webarchive/snapshots")

    cleanup = {}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            page.on("console", lambda msg: record("browser_console", msg.type != "error", msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda exc: record("browser_pageerror", False, str(exc)))
            page.goto(BASE + "/?tab=tts", wait_until="networkidle")
            expect(page.locator('[data-tab-panel="tts"]')).to_be_visible()
            record("load_tts_page", True, page.title())

            for tab in ["soundboard", "translate", "ocr", "documents", "webarchive", "forms", "logs"]:
                page.locator(f'[data-tab-target="{tab}"]').click()
                expect(page.locator(f'[data-tab-panel="{tab}"]')).to_be_visible()
                hidden_tts = page.locator('[data-tab-panel="tts"]').is_hidden() if tab != "tts" else False
                record(f"tab_{tab}_switch", hidden_tts or tab == "tts", "active panel visible")

            page.locator('[data-tab-target="ocr"]').click()
            expect(page.locator("#ocr-status")).to_contain_text("Bild-OCR: bereit", timeout=10000)
            page.locator("#ocr-source").set_input_files(str(image_path))
            page.locator("#btn-ocr-save").click()
            page.wait_for_function("document.querySelector('#ocr-input').value.includes('Browser OCR')", timeout=90000)
            ocr_text = page.locator("#ocr-input").input_value()
            record("ocr_ui_real_image", "7319" in ocr_text, ocr_text[:200])

            page.locator('[data-tab-target="documents"]').click()
            page.locator("#documents-upload").set_input_files(str(doc_path))
            page.locator("#btn-documents-add").click()
            page.wait_for_function("document.querySelector('#documents-output').value.includes('browser_doc.txt')", timeout=30000)
            page.locator("#documents-search").fill("GENI")
            page.wait_for_timeout(600)
            expect(page.locator("#documents-list")).to_contain_text("GENI", timeout=10000)
            page.locator("#btn-documents-scope-clear").click()
            page.wait_for_function("document.querySelector('#documents-output').value.includes('Scope geleert')", timeout=10000)
            page.locator('#documents-list button[data-act="load-document"]').first.click()
            page.wait_for_function("document.querySelector('#documents-output').value.includes('Browser Dokument Wahrheit')", timeout=10000)
            page.locator('#documents-chunks button[data-act="load-document-chunk"]').first.click()
            page.wait_for_function("document.querySelector('#documents-output').value.includes('Chunk')", timeout=10000)
            page.locator("#btn-documents-full").click()
            page.wait_for_function("document.querySelector('#full-modal').classList.contains('on')")
            page.locator("#btn-full-close").click()
            record("documents_ui_import_search_scope_chunk_full", True, "document UI flow completed")

            page.locator('[data-tab-target="forms"]').click()
            page.locator("#forms-name").fill("Browser Daniel")
            page.locator("#forms-email").fill("browser@example.test")
            page.locator("#forms-address").fill("Browser Werkraum")
            page.locator("#forms-extra").fill("firma: Flextrawurst")
            page.locator("#forms-template").fill('<form><input name="name"><input id="email"><textarea name="address"></textarea><p>{{firma}}</p></form>')
            page.locator("#btn-forms-preview").click()
            page.wait_for_function("document.querySelector('#forms-preview').value.includes('Browser Daniel')", timeout=10000)
            preview = page.locator("#forms-preview").input_value()
            record("forms_ui_server_fill", "browser@example.test" in preview and "Flextrawurst" in preview, preview)

            page.locator('[data-tab-target="webarchive"]').click()
            page.locator("#webarchive-url").fill(BASE + "/")
            page.locator("#webarchive-title").fill("browser-local-snapshot")
            page.locator("#webarchive-pages").fill("2")
            page.locator("#btn-webarchive-save").click()
            page.wait_for_function("document.querySelector('#webarchive-output').value.includes('Seiten:')", timeout=30000)
            expect(page.locator("#webarchive-list")).to_contain_text("browser-local-snapshot", timeout=10000)
            page.locator("#btn-webarchive-full").click()
            page.wait_for_function("document.querySelector('#full-modal').classList.contains('on')")
            page.locator("#btn-full-close").click()
            record("webarchive_ui_snapshot_full", True, page.locator("#webarchive-output").input_value()[:300])

            browser.close()
    finally:
        cleanup = {
            "ocr_jobs": delete_new("/ocr/jobs", before_ocr),
            "documents": delete_new("/documents", before_documents),
            "snapshots": delete_new("/webarchive/snapshots", before_snapshots),
        }

    ok = all(item["ok"] for item in report)
    payload = {"ok": ok, "base": BASE, "report": report, "cleanup": cleanup, "ts": time.time()}
    REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
