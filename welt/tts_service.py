import os, tempfile, asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import edge_tts

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

VOICE = "de-DE-FlorianMultilingualNeural"
MAX_CHARS = 1111111
_pool = ThreadPoolExecutor(max_workers=4)

class TTSRequest(BaseModel):
    text: str
    voice: str = VOICE
    rate: str = "+0%"   # z.B. "+50%" für 1.5x

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
    de = [x for x in v if x["Locale"].startswith("de-DE")]
    return [{"name": x["ShortName"], "gender": x["Gender"]} for x in de]

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
    uvicorn.run("tts_service:app", host="0.0.0.0", port=8035, workers=2)
