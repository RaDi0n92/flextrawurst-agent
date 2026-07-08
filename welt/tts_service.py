import os, tempfile, asyncio, json, threading, zipfile, hashlib, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fastapi import FastAPI, HTTPException
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
_pool = ThreadPoolExecutor(max_workers=4)
_library_lock = threading.Lock()
_translation_lock = threading.Lock()
_translation_languages_cache = {"ts": 0.0, "items": []}
MAX_TRANSLATE_CHARS = 8000
MAX_TRANSLATE_ALL_CHARS = 1800
TRANSLATE_CACHE_LIMIT = 3000
TRANSLATE_ALL_CONCURRENCY = 3

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
