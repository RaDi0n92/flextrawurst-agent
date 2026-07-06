import os, tempfile, asyncio, json, threading, zipfile, html, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import edge_tts

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

VOICE = "de-DE-Florian:DragonHDLatestNeural"
MAX_CHARS = 1111111
LIBRARY_PATH = Path("/root/werkraum/welt/tts_library.json")
_pool = ThreadPoolExecutor(max_workers=4)
_library_lock = threading.Lock()
AZURE_HD_VOICES = [
    {
        "name": "de-DE-Florian:DragonHDLatestNeural",
        "gender": "Male",
        "locale": "de-DE",
        "display": "Microsoft Florian DragonHDLatest (Azure HD) - German (Germany)",
        "provider": "azure",
    },
    {
        "name": "de-DE-Seraphina:DragonHDLatestNeural",
        "gender": "Female",
        "locale": "de-DE",
        "display": "Microsoft Seraphina DragonHDLatest (Azure HD) - German (Germany)",
        "provider": "azure",
    },
]

def _azure_speech_config() -> tuple[str, str]:
    key = os.environ.get("AZURE_SPEECH_KEY", "").strip()
    region = os.environ.get("AZURE_SPEECH_REGION", "").strip()
    return key, region

def _is_azure_voice(voice: str) -> bool:
    return voice in {v["name"] for v in AZURE_HD_VOICES}

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

def _sync_generate_edge(text: str, voice: str, rate: str) -> str:
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

def _sync_generate_azure(text: str, voice: str, rate: str) -> str:
    key, region = _azure_speech_config()
    if not key or not region:
        raise RuntimeError("Azure Speech fehlt: AZURE_SPEECH_KEY und AZURE_SPEECH_REGION setzen.")
    endpoint = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False, dir="/tmp")
    tmp.close()
    pct = str(rate or "+0%")
    escaped_text = html.escape(text, quote=False)
    escaped_voice = html.escape(voice, quote=True)
    ssml = (
        "<speak version='1.0' xml:lang='de-DE' "
        "xmlns='http://www.w3.org/2001/10/synthesis'>"
        f"<voice name='{escaped_voice}'><prosody rate='{html.escape(pct, quote=True)}'>"
        f"{escaped_text}</prosody></voice></speak>"
    ).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=ssml,
        headers={
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
            "User-Agent": "flextrawurst-tts",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            Path(tmp.name).write_bytes(res.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"Azure Speech HTTP {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Azure Speech Netzwerkfehler: {e.reason}") from e
    return tmp.name

def _sync_generate(text: str, voice: str, rate: str) -> str:
    if _is_azure_voice(voice):
        return _sync_generate_azure(text, voice, rate)
    return _sync_generate_edge(text, voice, rate)

@app.post("/speak")
async def speak(req: TTSRequest):
    text = req.text[:MAX_CHARS].strip()
    if not text:
        return {"error": "kein text"}
    loop = asyncio.get_event_loop()
    try:
        path = await loop.run_in_executor(_pool, _sync_generate, text, req.voice, req.rate)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    return FileResponse(path, media_type="audio/mpeg", filename="tts.mp3",
                        background=None)

@app.get("/voices")
async def voices():
    v = await edge_tts.list_voices()
    edge_voices = [
        {
            "name": x["ShortName"],
            "gender": x["Gender"],
            "locale": x["Locale"],
            "display": x.get("FriendlyName") or x["ShortName"],
            "provider": "edge",
        }
        for x in v
    ]
    existing = {x["name"] for x in edge_voices}
    hd = [x for x in AZURE_HD_VOICES if x["name"] not in existing]
    return hd + edge_voices

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
            try:
                path = await asyncio.get_event_loop().run_in_executor(_pool, _sync_generate, text, voice, rate)
            except RuntimeError as e:
                raise HTTPException(status_code=503, detail=str(e)) from e
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
