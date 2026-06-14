from __future__ import annotations

import asyncio
import os
import signal
import subprocess
import sys
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import edge_tts
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent))

try:
    import obsidian_vault as _vault
    _VAULT_OK = True
except ImportError:
    _VAULT_OK = False

from agent.dak_gord_system.graphen.gespraechsgraf import (
    baue_graf,
    setze_stream_callback,
    setze_modell_override,
    setze_bild,
    setze_organ_manager,
)
from agent.dak_gord_system.herz.postgres_herz import postgres_kontext
from agent.dak_gord_system.kerne.beziehungsorgan import Beziehungsorgan
from agent.dak_gord_system.kerne.organ_manager import OrganManager

_graf = None
_beziehungsorgan = Beziehungsorgan()
_organ_manager = OrganManager()
_verlauf: list[str] = []
_anfrage_lock = asyncio.Lock()
FADEN_ID = "hauptfaden"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _graf, _verlauf
    _organ_manager.laden()
    setze_organ_manager(_organ_manager)
    ctx = postgres_kontext()
    checkpointer = ctx.__enter__()
    try:
        checkpointer.setup()
        _graf = baue_graf(checkpointer)
        # Letzten Gesprächsverlauf aus PostgreSQL-Checkpoint wiederherstellen
        try:
            checkpoint = checkpointer.get({"configurable": {"thread_id": FADEN_ID}})
            if checkpoint and checkpoint.get("channel_values", {}).get("nachrichten"):
                _verlauf = list(checkpoint["channel_values"]["nachrichten"])
                print(f"[System] Verlauf wiederhergestellt: {len(_verlauf)} Nachrichten")
        except Exception as e:
            print(f"[System] Kein Verlauf gefunden: {e}")
        yield
    finally:
        ctx.__exit__(None, None, None)


app = FastAPI(title="dak+gord-system", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ChatAnfrage(BaseModel):
    nachricht: str
    modus: str | None = None
    bild_b64: str | None = None
    bild_name: str | None = None


class TtsAnfrage(BaseModel):
    text: str
    maennlich: bool = False


_STIMME_WEIBLICH = "de-DE-KatjaNeural"
_STIMME_MAENNLICH = "de-DE-ConradNeural"


_GEDAECHTNIS = Path("/root/werkraum/agent/dak_gord_system/gedaechtnis_daten")


@app.post("/api/tts")
async def tts_endpoint(anfrage: TtsAnfrage):
    voice = _STIMME_MAENNLICH if anfrage.maennlich else _STIMME_WEIBLICH
    try:
        communicate = edge_tts.Communicate(anfrage.text[:600], voice)
        audio = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio += chunk["data"]
        return Response(content=audio, media_type="audio/mpeg")
    except Exception:
        return Response(content=b"", media_type="audio/mpeg")


@app.get("/api/organe")
async def organe_endpoint():
    def lese(datei: str) -> list:
        p = _GEDAECHTNIS / datei
        if not p.exists():
            return []
        try:
            import json as _json
            return _json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return []

    from fastapi.responses import JSONResponse as _JR
    return _JR({
        "erinnerungen": lese("erinnerungen.json")[-5:],
        "zukunft": lese("zukunft.json")[-3:],
        "zwischenraum": lese("zwischenraum.json")[-4:],
        "abwaegungen": lese("abwaegungen.json")[-3:],
    })


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(HTML_SEITE)


@app.post("/chat")
async def chat_stream(anfrage: ChatAnfrage):
    return StreamingResponse(
        _generiere_antwort(anfrage.nachricht, anfrage.modus, anfrage.bild_b64),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def _generiere_antwort(
    nachricht: str, modus_override: str | None, bild_b64: str | None = None
) -> AsyncGenerator[str, None]:
    global _verlauf

    async for token in _generiere_antwort_intern(nachricht, modus_override, bild_b64):
        yield token


async def _generiere_antwort_intern(
    nachricht: str, modus_override: str | None, bild_b64: str | None = None
) -> AsyncGenerator[str, None]:
    global _verlauf

    token_queue: asyncio.Queue[str | None] = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def _token_cb(token: str) -> None:
        loop.call_soon_threadsafe(token_queue.put_nowait, token)

    _SYSTEMD_BLOCKER = [
        "innenleben-feeder.service",
        "codewesen-engagement.service",
        "codewesen-weltbild.service",
        "codewesen-batch-generator.service",
        "codewesen-forum-neugier.service",
        "codewesen-vokabel-takt.service",
        "codewesen-takt.service",
        "dak-neugier.service",
        "entity-kern.service",
        "entity-takt.service",
        "wesen-webbesucher.service",
        "codewesen-reaktion@namelessAI_1234.service",
        "codewesen-reaktion@namelessAI_1423.service",
        "codewesen-reaktion@namelessAI_1324.service",
        "codewesen-reaktion@namelessAI_2341.service",
        "codewesen-reaktion@namelessAI_3123.service",
        "codewesen-reaktion@namelessAI_4321.service",
    ]

    def _dak_geschuetzte_web_pids() -> set:
        """PIDs der drei interaktiven Chat-Webserver — niemals killen."""
        import re as _re
        schutz_ports = {8000, 8002, 8020}
        pids = set()
        try:
            r = subprocess.run(["ss", "-tlnp", "--no-header"], capture_output=True, text=True, timeout=5)
            for zeile in r.stdout.splitlines():
                for port in schutz_ports:
                    if f":{port} " in zeile or f":{port}\t" in zeile or zeile.endswith(f":{port}"):
                        m = _re.search(r"pid=(\d+)", zeile)
                        if m:
                            pids.add(int(m.group(1)))
        except Exception:
            pass
        return pids

    def _kill_ollama_fremde() -> None:
        """Killt Python-Prozesse die Ollama als Clients nutzen (Ollama selbst wird geschont)."""
        eigene_pid = os.getpid()
        geschuetzt = _dak_geschuetzte_web_pids()
        try:
            import re as _re
            r = subprocess.run(
                ["ss", "-tp", "--no-header"],
                capture_output=True, text=True, timeout=5
            )
            for zeile in r.stdout.splitlines():
                if "11434" not in zeile:
                    continue
                # Nur CLIENT-Verbindungen killen (lokaler Port != 11434)
                # Server-Zeilen haben "127.0.0.1:11434" als lokale Adresse
                if "127.0.0.1:11434 " in zeile or " 0.0.0.0:11434" in zeile:
                    continue
                m = _re.search(r"pid=(\d+)", zeile)
                if not m:
                    continue
                # Ollama-Prozess nie killen
                proc_name = subprocess.run(
                    ["ps", "-p", m.group(1), "-o", "comm="],
                    capture_output=True, text=True
                ).stdout.strip()
                if "ollama" in proc_name.lower():
                    continue
                pid = int(m.group(1))
                if pid == eigene_pid or pid in geschuetzt:
                    continue
                try:
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
        except Exception:
            pass

    _OLLAMA_BEREIT = threading.Event()

    def _stoppe_dienste_parallel(dienste: list) -> None:
        procs = [
            subprocess.Popen(["systemctl", "stop", d], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            for d in dienste
        ]
        for p in procs:
            try:
                p.wait(timeout=7)
            except subprocess.TimeoutExpired:
                p.kill()

    def _ollama_waechter(chat_flag: Path) -> None:
        """Stoppt Konkurrenten, wartet 3s bis Ollama frei ist, startet nur vorher aktive neu."""
        import time as _t
        vorher_aktiv = [
            d for d in _SYSTEMD_BLOCKER
            if subprocess.run(["systemctl", "is-active", d], capture_output=True).returncode == 0
        ]
        _stoppe_dienste_parallel(_SYSTEMD_BLOCKER)
        _kill_ollama_fremde()
        _t.sleep(3)
        _OLLAMA_BEREIT.set()
        while chat_flag.exists():
            _t.sleep(5)
        for dienst in vorher_aktiv:
            try:
                subprocess.run(["systemctl", "start", dienst], capture_output=True, timeout=10)
            except Exception:
                pass

    def _llm_thread() -> None:
        from pathlib import Path
        chat_flag = Path("/tmp/dak_gord_chat_aktiv")
        chat_flag.touch()
        _OLLAMA_BEREIT.clear()
        waechter = threading.Thread(target=_ollama_waechter, args=(chat_flag,), daemon=True)
        waechter.start()
        _OLLAMA_BEREIT.wait(timeout=30)  # max 30s warten bis Ollama-Konkurrenz weg ist
        setze_stream_callback(_token_cb)
        setze_modell_override(modus_override)
        setze_bild(bild_b64)
        try:
            _beziehungsorgan.lese_hinweis(nachricht)

            verlauf = list(_verlauf)
            verlauf.append(nachricht)

            result = _graf.invoke(
                {"nachrichten": verlauf},
                config={"configurable": {"thread_id": FADEN_ID}},
            )
            neue_nachrichten = result["nachrichten"]
            _verlauf[:] = neue_nachrichten
            # Feedback-Loop: LLM-Antwort zurück ins Beziehungsorgan
            if neue_nachrichten:
                _beziehungsorgan.lese_antwort_hinweis(neue_nachrichten[-1])
        except Exception as exc:
            loop.call_soon_threadsafe(
                token_queue.put_nowait, f"\n[Fehler: {exc}]"
            )
        finally:
            setze_stream_callback(None)
            setze_modell_override(None)
            setze_bild(None)
            chat_flag.unlink(missing_ok=True)
            loop.call_soon_threadsafe(token_queue.put_nowait, None)

    thread = threading.Thread(target=_llm_thread, daemon=True)
    thread.start()

    gesammelt: list[str] = []
    while True:
        token = await token_queue.get()
        if token is None:
            break
        gesammelt.append(token)
        yield f"data: {token}\n\n"

    yield "data: [DONE]\n\n"

    if _VAULT_OK and gesammelt:
        antwort_text = "".join(gesammelt).strip()
        if antwort_text and len(antwort_text) > 20:
            try:
                eintrag = f"**Daniel:** {nachricht[:400]}\n\n**dak+gord:** {antwort_text[:800]}"
                _vault.tagebuch("agent/dak_gord_system", eintrag)
            except Exception:
                pass


HTML_SEITE = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>dak+gord-system</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0d0d0d; color: #e8e8e8; font-family: 'Courier New', monospace;
         height: 100vh; display: flex; flex-direction: column; }
  #header { padding: 10px 20px; border-bottom: 1px solid #1a1a1a;
            display: flex; align-items: center; gap: 12px; flex-shrink: 0; }
  #header h1 { font-size: 13px; color: #666; font-weight: normal; letter-spacing: 2px; }
  .modell-badge { font-size: 11px; padding: 2px 8px; border-radius: 3px;
                  background: #111; color: #555; border: 1px solid #222; }
  .modell-badge.aktiv { color: #4CAF50; border-color: #2a4a2a; }
  #modus-select { background: #111; color: #666; border: 1px solid #222; padding: 3px 8px;
                  font-family: inherit; font-size: 12px; border-radius: 3px; cursor: pointer; }
  #tts-btn { background: none; border: 1px solid #222; color: #555; padding: 3px 8px;
             border-radius: 3px; cursor: pointer; font-size: 14px; line-height: 1; }
  #tts-btn:hover { border-color: #444; color: #888; }
  #tts-btn.aus { opacity: 0.3; }
  #main { flex: 1; display: flex; overflow: hidden; }
  #chat-bereich { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
  #verlauf { flex: 1; overflow-y: auto; padding: 20px;
             display: flex; flex-direction: column; gap: 14px; }
  .nachricht { max-width: 820px; line-height: 1.6; }
  .nachricht.daniel { align-self: flex-end; }
  .nachricht.agent { align-self: flex-start; }
  .nachricht-kopf { font-size: 10px; color: #444; margin-bottom: 3px; letter-spacing: 1px; }
  .nachricht.daniel .nachricht-kopf { text-align: right; }
  .nachricht-text { padding: 10px 14px; border-radius: 6px; white-space: pre-wrap;
                    word-break: break-word; font-size: 14px; line-height: 1.6; }
  .nachricht.daniel .nachricht-text { background: #141428; border: 1px solid #22224a; color: #b8b8d8; }
  .nachricht.agent .nachricht-text { background: #0d180d; border: 1px solid #163016; color: #b8d8b8; }
  .msg-bild { max-width: 220px; border-radius: 4px; margin-top: 6px; display: block; }
  #eingabe-bereich { border-top: 1px solid #1a1a1a; padding: 10px 16px 12px; flex-shrink: 0; }
  #bild-zeile { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; min-height: 24px; }
  #btn-bild { background: none; border: 1px solid #1a1a1a; color: #333; padding: 2px 8px;
              font-family: inherit; font-size: 11px; cursor: pointer; border-radius: 3px; }
  #btn-bild:hover { border-color: #333; color: #666; }
  #bild-vorschau { max-height: 32px; border-radius: 3px; display: none; }
  #bild-name-txt { font-size: 10px; color: #333; }
  #btn-bild-leer { background: none; border: none; color: #333; cursor: pointer;
                   font-size: 11px; display: none; padding: 0 2px; }
  #eingabe-zeile { display: flex; gap: 8px; align-items: flex-end; }
  #eingabe { flex: 1; background: #0f0f0f; color: #e0e0e0; border: 1px solid #222;
             border-radius: 6px; padding: 9px 12px; font-family: inherit; font-size: 14px;
             resize: none; min-height: 42px; max-height: 200px; line-height: 1.5; }
  #eingabe:focus { outline: none; border-color: #3a3a3a; }
  #senden-btn { background: #0f1f0f; color: #4a9a4a; border: 1px solid #1a3a1a;
                padding: 9px 16px; border-radius: 6px; cursor: pointer;
                font-family: inherit; font-size: 13px; white-space: nowrap; }
  #senden-btn:hover { background: #162616; }
  #senden-btn:disabled { opacity: 0.35; cursor: not-allowed; }
  #stop-btn { background: #1f0f0f; color: #d04040; border: 1px solid #3a1a1a;
              padding: 9px 16px; border-radius: 6px; cursor: pointer;
              font-family: inherit; font-size: 13px; white-space: nowrap; display: none; }
  .cursor { display: inline-block; animation: blink 1s step-end infinite; }
  @keyframes blink { 50% { opacity: 0; } }
  code { background: #141414; padding: 1px 5px; border-radius: 3px; font-size: 13px; }
  pre { background: #0f0f0f; padding: 12px; border-radius: 6px; overflow-x: auto;
        margin: 8px 0; border: 1px solid #1a1a1a; }
  pre code { background: none; padding: 0; }
  #organ-panel { width: 230px; border-left: 1px solid #0f0f0f;
                 display: flex; flex-direction: column; overflow: hidden; }
  #op-header { padding: 10px 12px; font-size: 9px; letter-spacing: 3px; color: #222;
               border-bottom: 1px solid #0f0f0f; flex-shrink: 0; }
  #op-inhalt { flex: 1; overflow-y: auto; padding: 8px;
               display: flex; flex-direction: column; gap: 5px; }
  .op-block { border: 1px solid #0f0f0f; border-radius: 3px; padding: 5px 7px; }
  .op-block-titel { font-size: 9px; letter-spacing: 2px; color: #253a25; margin-bottom: 3px; }
  .op-item { padding: 2px 0; border-bottom: 1px solid #0a0a0a; font-size: 10px; }
  .op-item:last-child { border-bottom: none; }
  .op-item-art { font-size: 9px; color: #253a25; letter-spacing: 1px; margin-bottom: 1px; }
  .op-item-text { color: #3a3a3a; line-height: 1.3; }
</style>
</head>
<body>
<div id="header">
  <h1>DAK+GORD-SYSTEM</h1>
  <span class="modell-badge aktiv" id="modell-anzeige">auto</span>
  <select id="modus-select">
    <option value="">auto</option>
    <option value="mittel">gemma4 e4b</option>
    <option value="schnell">gemma4 e2b</option>
  </select>
  <button id="tts-btn" title="Stimme an/aus">🔊</button>
</div>
<div id="main">
  <div id="chat-bereich">
    <div id="verlauf"></div>
    <div id="eingabe-bereich">
      <div id="bild-zeile">
        <button id="btn-bild" onclick="document.getElementById('bild-input').click()">+ bild</button>
        <img id="bild-vorschau" alt="">
        <span id="bild-name-txt"></span>
        <button id="btn-bild-leer" onclick="bildLeeren()">✕</button>
      </div>
      <div id="eingabe-zeile">
        <textarea id="eingabe" placeholder="Schreib etwas…" rows="1"></textarea>
        <button id="senden-btn">senden</button>
        <button id="stop-btn">stop</button>
      </div>
      <input type="file" id="bild-input" accept="image/*" style="display:none">
    </div>
  </div>
  <div id="organ-panel">
    <div id="op-header">ORGANE</div>
    <div id="op-inhalt"><div style="color:#1a1a1a;font-size:10px;text-align:center;margin-top:20px;">laden…</div></div>
  </div>
</div>

<script>
const verlauf = document.getElementById('verlauf');
const eingabe = document.getElementById('eingabe');
const sendenBtn = document.getElementById('senden-btn');
const stopBtn = document.getElementById('stop-btn');
const modusSelect = document.getElementById('modus-select');
const modellAnzeige = document.getElementById('modell-anzeige');
const ttsBtn = document.getElementById('tts-btn');
let abortController = null;
let aktuellesModell = '';
let ttsAktiv = true;
let aktuellesBildB64 = null;
let aktuellerBildName = null;

stopBtn.addEventListener('click', () => { if (abortController) abortController.abort(); });

ttsBtn.addEventListener('click', () => {
  ttsAktiv = !ttsAktiv;
  ttsBtn.classList.toggle('aus', !ttsAktiv);
  ttsBtn.textContent = ttsAktiv ? '🔊' : '🔇';
});

// ── Bild-Upload ────────────────────────────────────────────────────────────────
document.getElementById('bild-input').addEventListener('change', function() {
  const file = this.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(e) {
    aktuellesBildB64 = e.target.result.split(',')[1];
    aktuellerBildName = file.name;
    const vorschau = document.getElementById('bild-vorschau');
    vorschau.src = e.target.result;
    vorschau.style.display = 'inline-block';
    document.getElementById('bild-name-txt').textContent = file.name;
    document.getElementById('btn-bild-leer').style.display = 'inline';
  };
  reader.readAsDataURL(file);
});

function bildLeeren() {
  aktuellesBildB64 = null; aktuellerBildName = null;
  document.getElementById('bild-input').value = '';
  const v = document.getElementById('bild-vorschau');
  v.src = ''; v.style.display = 'none';
  document.getElementById('bild-name-txt').textContent = '';
  document.getElementById('btn-bild-leer').style.display = 'none';
}

// ── Organ-Panel ────────────────────────────────────────────────────────────────
function ladeOrgane() {
  fetch('/api/organe').then(r => r.json()).then(d => {
    const opI = document.getElementById('op-inhalt');
    opI.innerHTML = '';
    function block(titel, items, artFn, textFn) {
      if (!items || !items.length) return;
      const b = document.createElement('div'); b.className = 'op-block';
      const t = document.createElement('div'); t.className = 'op-block-titel'; t.textContent = titel;
      b.appendChild(t);
      items.forEach(it => {
        const item = document.createElement('div'); item.className = 'op-item';
        const art = document.createElement('div'); art.className = 'op-item-art'; art.textContent = artFn(it);
        const tx = document.createElement('div'); tx.className = 'op-item-text'; tx.textContent = textFn(it);
        item.appendChild(art); item.appendChild(tx); b.appendChild(item);
      });
      opI.appendChild(b);
    }
    block('ERINNERUNGEN', d.erinnerungen, it => it.art || 'fakt', it => it.text || '');
    block('ZUKUNFT', d.zukunft, it => it.heute || '', it => it.spaeter || '');
    block('ZWISCHENRAUM', d.zwischenraum,
      it => it.art || 'schwebend',
      it => it.text || (typeof it === 'string' ? it : JSON.stringify(it)));
    block('ABWÄGUNGEN', d.abwaegungen, it => 'abwägen', it => it.frage || it.text || JSON.stringify(it));
    if (!opI.children.length) {
      opI.innerHTML = '<div style="color:#1a1a1a;font-size:10px;text-align:center;margin-top:20px;">leer</div>';
    }
  }).catch(() => {});
}
ladeOrgane();
setInterval(ladeOrgane, 30000);

// ── TTS ───────────────────────────────────────────────────────────────────────
function reinigeFuerTts(text) {
  return text
    .replace(/\[denkt[^\]]*\]/gi, '')
    .replace(/\[dak\+gord[^\]]*\]/gi, '')
    .replace(/##[A-Z_]+[^#]*##/g, '')
    .replace(/```[\s\S]*?```/g, '')
    .replace(/`[^`]+`/g, '')
    .replace(/\[TOOL[^\]]*\][\s\S]*?\[\/TOOL[^\]]*\]/g, '')
    .replace(/\n{3,}/g, '\n')
    .trim()
    .substring(0, 600);
}

function sprichText(text) {
  if (!ttsAktiv || text.trim().length < 5) return;
  const reinText = reinigeFuerTts(text);
  if (reinText.length < 5) return;
  fetch('/api/tts', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text: reinText, maennlich: true})
  }).then(r => r.blob()).then(blob => {
    if (blob.size < 100) return;
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    audio.play().catch(() => {});
    audio.onended = () => URL.revokeObjectURL(url);
  }).catch(() => {});
}

// ── Chat ──────────────────────────────────────────────────────────────────────
function jetzt() {
  const n = new Date();
  return n.toLocaleDateString('de-DE', {day:'2-digit',month:'2-digit',year:'numeric'}) + ' '
       + n.toLocaleTimeString('de-DE', {hour:'2-digit',minute:'2-digit'});
}
function fuegeNachrichtEin(rolle, kopf) {
  const wrap = document.createElement('div');
  wrap.className = `nachricht ${rolle}`;
  const k = document.createElement('div');
  k.className = 'nachricht-kopf';
  k.textContent = kopf + '  ' + jetzt();
  const t = document.createElement('div');
  t.className = 'nachricht-text';
  wrap.appendChild(k);
  wrap.appendChild(t);
  verlauf.appendChild(wrap);
  verlauf.scrollTop = verlauf.scrollHeight;
  return t;
}

function formatText(text) {
  return text
    .replace(/##MERKEN\s[^#]*##/g, '')
    .replace(/##SP(?:Ä|AE?)TER\s[^#]*##/g, '')
    .replace(/##ZWISCHENRAUM\s[^#]*##/g, '')
    .replace(/##ABW(?:Ä|AE?)GEN\s[^#]*##/g, '')
    .replace(/##LESEN:\s*[^#]+##/g, '')
    .replace(/##SCHREIBEN:\s*[^#]+##[\s\S]*?##SCHREIBEN_ENDE##/g, '')
    .replace(/##CODE_START##[\s\S]*?##CODE_ENDE##/g, '')
    .replace(/\*+\s*$/, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>');
}

eingabe.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); senden(); }
});
eingabe.addEventListener('input', () => {
  eingabe.style.height = 'auto';
  eingabe.style.height = Math.min(eingabe.scrollHeight, 200) + 'px';
});
sendenBtn.addEventListener('click', senden);

async function senden() {
  const text = eingabe.value.trim();
  if (!text && !aktuellesBildB64 || sendenBtn.disabled) return;

  const bildB64 = aktuellesBildB64;
  const bildName = aktuellerBildName;
  eingabe.value = '';
  eingabe.style.height = 'auto';
  if (bildB64) bildLeeren();
  sendenBtn.disabled = true;
  sendenBtn.style.display = 'none';
  stopBtn.style.display = 'inline-block';
  abortController = new AbortController();
  const notfall_timeout = setTimeout(() => { abortController.abort(); }, 600000);

  // Daniel-Nachricht
  const danielEl = fuegeNachrichtEin('daniel', 'Daniel');
  if (text) danielEl.textContent = text;
  if (bildB64) {
    const img = document.createElement('img');
    img.className = 'msg-bild';
    img.src = 'data:image/jpeg;base64,' + bildB64;
    danielEl.appendChild(img);
  }

  const modus = modusSelect.value || null;
  modellAnzeige.textContent = modus || 'auto';

  const agentTextEl = fuegeNachrichtEin('agent', 'dak+gord-system');
  const cursor = document.createElement('span');
  cursor.className = 'cursor';
  cursor.textContent = '▋';
  agentTextEl.appendChild(cursor);

  let puffer = '';

  try {
    const body = {nachricht: text || '', modus};
    if (bildB64) { body.bild_b64 = bildB64; body.bild_name = bildName; }

    const resp = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(body),
      signal: abortController.signal
    });

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let rohrRest = '';

    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      rohrRest += decoder.decode(value, {stream: true});
      const zeilen = rohrRest.split('\n');
      rohrRest = zeilen.pop();
      for (const zeile of zeilen) {
        if (!zeile.startsWith('data: ')) continue;
        const token = zeile.slice(6);
        if (token === '[DONE]') break;
        if (token.startsWith('\n[dak+gord-system')) {
          const match = token.match(/\| ([^\]]+)\]/);
          if (match) {
            aktuellesModell = match[1];
            modellAnzeige.textContent = match[1];
            const neuKopf = agentTextEl.previousElementSibling;
            if (neuKopf) neuKopf.textContent = 'dak+gord-system [' + match[1] + ']  ' + jetzt();
          }
          continue;
        }
        puffer += token;
        agentTextEl.innerHTML = formatText(puffer);
        agentTextEl.appendChild(cursor);
        verlauf.scrollTop = verlauf.scrollHeight;
      }
    }
  } catch (err) {
    agentTextEl.innerHTML += '\n[Verbindungsfehler: ' + err.message + ']';
  } finally {
    clearTimeout(notfall_timeout);
    cursor.remove();
    abortController = null;
    stopBtn.style.display = 'none';
    sendenBtn.style.display = '';
    sendenBtn.disabled = false;
    eingabe.focus();
    setTimeout(ladeOrgane, 1500);
    if (puffer.trim().length > 10) sprichText(puffer);
  }
}
</script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
