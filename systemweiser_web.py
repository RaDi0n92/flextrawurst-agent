#!/usr/bin/env python3
"""
Systemweiser Web — Betriebswächter + kontrollierte Orchestrierung.
Port 8080. Schreibt nur: inbox-Items + Service-Stop (mit Confirm).
"""

import json
import secrets
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import uvicorn

WERKRAUM   = Path("/root/werkraum")
INNENLEBEN = WERKRAUM / "innenleben"
CODEWESEN  = WERKRAUM / "codewesen"
LOGS       = WERKRAUM / "logs"

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "dolphin3:8b-llama3.1-q8_0"

WESEN = [
    "namelessAI_1234", "namelessAI_1324", "namelessAI_1423",
    "namelessAI_2341", "namelessAI_3123", "namelessAI_4321",
]

SERVICES = [
    "codewesen-takt", "codewesen-engagement", "codewesen-batch-generator",
    "codewesen-forum-neugier", "codewesen-weltbild", "innenleben-feeder",
    "dak-gord-web", "dak-neugier", "geni-hoerer", "geni-web", "obsidian-api",
] + [f"codewesen-reaktion@{w}" for w in WESEN]

HTPASSWD   = Path("/etc/nginx/.htpasswd")
SESSION_TOKEN = secrets.token_hex(32)

def _verify_password(password: str) -> bool:
    try:
        r = subprocess.run(
            ["htpasswd", "-vb", str(HTPASSWD), "daniel", password],
            capture_output=True, timeout=5
        )
        return r.returncode == 0
    except Exception:
        return False

app = FastAPI(title="Systemweiser", version="0.1")

class AuthGuard(BaseHTTPMiddleware):
    OPEN = {"/", "/health", "/api/login"}
    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.OPEN:
            return await call_next(request)
        if request.cookies.get("sw_session") != SESSION_TOKEN:
            return JSONResponse({"error": "Nicht eingeloggt"}, status_code=401)
        return await call_next(request)

app.add_middleware(AuthGuard)


# ── Hilfsfunktionen ───────────────────────────────────────────────────────────

def service_status(name: str) -> str:
    try:
        r = subprocess.run(["systemctl", "is-active", name],
                           capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except Exception:
        return "error"


def inbox_count(wesen: str) -> int:
    d = CODEWESEN / wesen / "inbox"
    return len(list(d.glob("*.json"))) if d.exists() else 0


def entwuerfe_count(wesen: str) -> int:
    d = CODEWESEN / wesen / "entwuerfe"
    return len(list(d.rglob("*.json"))) if d.exists() else 0


def letzte_log_fehler(log_path: Path, minuten: int = 60) -> list[str]:
    if not log_path.exists():
        return []
    cutoff = datetime.now() - timedelta(minutes=minuten)
    out = []
    for line in log_path.read_text(errors="replace").splitlines()[-500:]:
        try:
            ts = datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S")
        except Exception:
            continue
        if ts >= cutoff and (" ERROR " in line or " WARNING " in line):
            out.append(line.strip())
    return out


def takt_zusammenfassung(minuten: int = 60) -> dict:
    log = WERKRAUM / "takt.log"
    if not log.exists():
        return {}
    cutoff = datetime.now() - timedelta(minutes=minuten)
    queue_leer, post_422, impuls_fehler = {}, [], []
    for line in log.read_text(errors="replace").splitlines()[-2000:]:
        try:
            ts = datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S")
        except Exception:
            continue
        if ts < cutoff:
            continue
        if "Queue leer" in line:
            for w in WESEN:
                if w in line:
                    queue_leer[w] = queue_leer.get(w, 0) + 1
        if "422" in line and "Post fehlgeschlagen" in line:
            post_422.append(line.strip())
        if "impuls-Fehler" in line:
            impuls_fehler.append(line.strip())
    return {"queue_leer": queue_leer, "post_422": post_422, "impuls_fehler": impuls_fehler}


# ── API ───────────────────────────────────────────────────────────────────────

@app.get("/api/status")
def api_status():
    svc = []
    warnungen = []
    for name in SERVICES:
        st = service_status(name)
        label = name.replace("codewesen-reaktion@", "reaktion@")
        svc.append({"name": label, "full_name": name, "status": st})
        if st == "failed":
            warnungen.append(f"SERVICE FAILED: {name}")

    wesen_data = []
    for w in WESEN:
        ic = inbox_count(w)
        ec = entwuerfe_count(w)
        if ic >= 200:
            warnungen.append(f"QUEUE KRITISCH: {w} ({ic} Items)")
        elif ic >= 100:
            warnungen.append(f"QUEUE HOCH: {w} ({ic} Items)")
        wesen_data.append({"name": w, "inbox": ic, "entwuerfe": ec})

    takt = takt_zusammenfassung()
    if takt.get("post_422"):
        warnungen.append(f"TAKT: {len(takt['post_422'])} Flarum-422-Fehler (letzte 60 min)")
    if takt.get("impuls_fehler"):
        warnungen.append(f"TAKT: {len(takt['impuls_fehler'])} impuls-Fehler (letzte 60 min)")

    eng = letzte_log_fehler(LOGS / "engagement.log")
    timeouts = sum(1 for l in eng if "timed out" in l.lower())
    if timeouts >= 5:
        warnungen.append(f"ENGAGEMENT: {timeouts} Timeouts (letzte 60 min)")

    feeder_cursors = {}
    fp = INNENLEBEN / "feeder_state.json"
    if fp.exists():
        feeder_cursors = json.loads(fp.read_text())

    return {
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "services": svc,
        "wesen": wesen_data,
        "takt": {
            "queue_leer": takt.get("queue_leer", {}),
            "post_422_count": len(takt.get("post_422", [])),
            "impuls_fehler_count": len(takt.get("impuls_fehler", [])),
        },
        "engagement_timeouts": timeouts,
        "feeder_cursors": feeder_cursors,
        "warnungen": warnungen,
    }


@app.get("/api/innenleben")
def api_innenleben():
    try:
        result = subprocess.run(
            [sys.executable, str(INNENLEBEN / "status.py")],
            capture_output=True, text=True, timeout=30
        )
        return {"output": result.stdout, "error": result.stderr[:200] if result.returncode != 0 else ""}
    except subprocess.TimeoutExpired:
        return {"output": "", "error": "Timeout"}
    except Exception as e:
        return {"output": "", "error": str(e)}


@app.post("/api/aufgabe")
async def api_aufgabe(request: Request):
    data = await request.json()
    wesen = data.get("wesen", "")
    nachricht = data.get("nachricht", "").strip()
    typ = data.get("typ", "systemweiser_auftrag")

    if wesen not in WESEN:
        return JSONResponse({"error": f"Unbekanntes Wesen: {wesen}"}, status_code=400)
    if not nachricht:
        return JSONResponse({"error": "Nachricht fehlt"}, status_code=400)
    if typ not in ("systemweiser_auftrag", "daniel_nachricht"):
        return JSONResponse({"error": "Ungültiger Typ"}, status_code=400)

    inbox_dir = CODEWESEN / wesen / "inbox"
    inbox_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now()
    filename = ts.strftime("%Y-%m-%dT%H-%M-%S") + f"_{typ}.json"
    item = {
        "empfangen_am": ts.isoformat(),
        "typ": typ,
        "daten": {
            "nachricht": nachricht,
            "von": "systemweiser",
            "prioritaet": data.get("prioritaet", "normal"),
        },
    }
    (inbox_dir / filename).write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "datei": filename, "wesen": wesen}


@app.get("/api/service/detail")
def api_service_detail(name: str):
    if name not in SERVICES:
        return JSONResponse({"error": "Unbekannt"}, status_code=400)
    fields = "ActiveState,SubState,Result,NRestarts,ExecMainExitTimestamp,ActiveEnterTimestamp,InactiveEnterTimestamp,MainPID"
    try:
        show = subprocess.run(
            ["systemctl", "show", name, f"--property={fields}"],
            capture_output=True, text=True, timeout=5
        )
        props = dict(line.split("=", 1) for line in show.stdout.strip().splitlines() if "=" in line)
    except Exception as e:
        props = {"error": str(e)}
    try:
        j = subprocess.run(
            ["journalctl", "-u", name, "--no-pager", "-n", "25", "--output=short"],
            capture_output=True, text=True, timeout=10
        )
        logs = j.stdout.strip() or "(kein Journal)"
    except Exception:
        logs = "(Journal nicht lesbar)"
    return {"name": name, "props": props, "logs": logs}


@app.get("/api/wesen/detail")
def api_wesen_detail(name: str):
    if name not in WESEN:
        return JSONResponse({"error": "Unbekannt"}, status_code=400)
    inbox_dir = CODEWESEN / name / "inbox"
    files = sorted(inbox_dir.glob("*.json")) if inbox_dir.exists() else []

    def read_item(f):
        try:
            d = json.loads(f.read_text(errors="replace"))
            return {"datei": f.name, "typ": d.get("typ", "?"), "empfangen_am": d.get("empfangen_am", "?")}
        except Exception:
            return {"datei": f.name, "typ": "?", "empfangen_am": "?"}

    oldest = read_item(files[0]) if files else None
    newest = read_item(files[-1]) if files else None

    log_file = CODEWESEN / name / "reaktion.log"
    letzte_fehler = []
    if log_file.exists():
        for line in log_file.read_text(errors="replace").splitlines()[-300:]:
            if " ERROR " in line or " WARNING " in line:
                letzte_fehler.append(line.strip())
        letzte_fehler = letzte_fehler[-6:]

    processed_dir = CODEWESEN / name / "processed"
    last_processed = None
    if processed_dir.exists():
        pf = sorted(processed_dir.glob("*.json"))
        if pf:
            last_processed = pf[-1].name

    fehler_dir = CODEWESEN / name / "fehler"
    fehler_items = []
    if fehler_dir.exists():
        fehler_items = [f.name for f in sorted(fehler_dir.iterdir())[-3:]]

    svc_status = service_status(f"codewesen-reaktion@{name}")
    return {
        "name": name,
        "reaktion_service": svc_status,
        "inbox_count": len(files),
        "oldest": oldest,
        "newest": newest,
        "last_processed": last_processed,
        "letzte_fehler": letzte_fehler,
        "fehler_items": fehler_items,
    }


@app.get("/api/registry")
def api_registry():
    expected = set(WESEN)
    existing_folders = {f.name for f in CODEWESEN.iterdir() if f.is_dir() and f.name.startswith("namelessAI_")}
    fp = INNENLEBEN / "feeder_state.json"
    feeder_keys = set(json.loads(fp.read_text()).keys()) if fp.exists() else set()
    running = {w for w in WESEN if service_status(f"codewesen-reaktion@{w}") == "active"}
    disc = []
    if extra := existing_folders - expected:
        disc.append(f"Unerwartete Ordner: {sorted(extra)}")
    if missing := expected - existing_folders:
        disc.append(f"Ordner fehlen: {sorted(missing)}")
    if extra_f := feeder_keys - expected:
        disc.append(f"Feeder-Einträge unbekannt: {sorted(extra_f)}")
    if missing_f := expected - feeder_keys:
        disc.append(f"Feeder-Einträge fehlen: {sorted(missing_f)}")
    if not_run := expected - running:
        disc.append(f"Reaktion nicht aktiv: {sorted(not_run)}")
    return {"expected": sorted(expected), "folders": sorted(existing_folders),
            "feeder_keys": sorted(feeder_keys), "running_reaktion": sorted(running),
            "discrepancies": disc, "ok": not disc}


@app.post("/api/service/stop")
async def api_service_stop(request: Request):
    data = await request.json()
    name = data.get("service", "")
    bestaetigt = data.get("bestaetigt", False)

    if name not in SERVICES:
        return JSONResponse({"error": "Unbekannter Service"}, status_code=400)
    if not bestaetigt:
        return JSONResponse({"error": "Bestätigung fehlt"}, status_code=400)

    # Reaktion@-Services und dak-neugier erlaubt — Kernsysteme (geni, takt) gesperrt
    GESPERRT = ["codewesen-takt", "geni-hoerer", "geni-web", "innenleben-feeder"]
    if name in GESPERRT:
        return JSONResponse({"error": f"{name} ist gesperrt — nur manuell stoppbar"}, status_code=403)

    try:
        subprocess.run(["systemctl", "stop", name], check=True, timeout=10)
        return {"ok": True, "gestoppt": name}
    except subprocess.CalledProcessError as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/service/start")
async def api_service_start(request: Request):
    data = await request.json()
    name = data.get("service", "")
    bestaetigt = data.get("bestaetigt", False)

    if name not in SERVICES:
        return JSONResponse({"error": "Unbekannter Service"}, status_code=400)
    if not bestaetigt:
        return JSONResponse({"error": "Bestätigung fehlt"}, status_code=400)

    try:
        subprocess.run(["systemctl", "start", name], check=True, timeout=10)
        return {"ok": True, "gestartet": name}
    except subprocess.CalledProcessError as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/passwd")
async def api_passwd(request: Request):
    data = await request.json()
    new_pw = data.get("passwort", "").strip()
    if len(new_pw) < 8:
        return JSONResponse({"error": "Mindestens 8 Zeichen"}, status_code=400)
    try:
        result = subprocess.run(
            ["htpasswd", "-B", "-i", "/etc/nginx/.htpasswd", "daniel"],
            input=new_pw, capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return JSONResponse({"error": result.stderr.strip()}, status_code=500)
        subprocess.run(["systemctl", "reload", "nginx"], timeout=5)
        return {"ok": True}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/analyse")
async def api_analyse(request: Request):
    data = await request.json()
    frage = data.get("frage", "").strip()
    if not frage:
        return JSONResponse({"error": "Frage fehlt"}, status_code=400)

    # Kompakter Systemkontext — nur Warnungen + Queues
    status = api_status()
    warnungen_text = "\n".join(status["warnungen"]) or "Keine Warnungen."
    wesen_text = "\n".join(
        f"  {w['name']}: inbox={w['inbox']} entwuerfe={w['entwuerfe']}"
        for w in status["wesen"]
    )
    services_text = ", ".join(
        f"{s['name']}={s['status']}"
        for s in status["services"]
        if s["status"] != "active"
    ) or "alle aktiv"

    prompt = f"""Du bist Systemweiser — Betriebswächter eines KI-Wesen-Systems.
Du beobachtest, analysierst und empfiehlst. Du veränderst nichts selbst.

SYSTEM-STAND ({status['ts']}):
Warnungen:
{warnungen_text}

Wesen-Queues:
{wesen_text}

Services mit Problemen: {services_text}
Takt: {status['takt']['post_422_count']} 422-Fehler, {status['takt']['impuls_fehler_count']} impuls-Fehler

FRAGE: {frage}

Antworte kurz, klar, auf Deutsch. Nur beobachten und empfehlen — nicht handeln."""

    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.4, "num_predict": 400},
        }, timeout=60)
        if resp.status_code == 200:
            return {"antwort": resp.json().get("response", "").strip()}
        return JSONResponse({"error": f"Ollama: {resp.status_code}"}, status_code=500)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ── HTML ──────────────────────────────────────────────────────────────────────

@app.post("/api/login")
async def api_login(request: Request):
    data = await request.json()
    if _verify_password(data.get("passwort", "")):
        resp = JSONResponse({"ok": True})
        resp.set_cookie("sw_session", SESSION_TOKEN, httponly=True, secure=True, max_age=86400 * 30, samesite="lax")
        return resp
    return JSONResponse({"error": "Falsches Passwort"}, status_code=403)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    if request.cookies.get("sw_session") != SESSION_TOKEN:
        return LOGIN_HTML
    return HTML

@app.get("/health")
def health():
    return {"status": "ok", "app": "systemweiser-web"}


LOGIN_HTML = """<!DOCTYPE html>
<html lang="de">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Systemweiser — Login</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
     background:#0d1117;color:#e6edf3;display:flex;align-items:center;
     justify-content:center;min-height:100vh}
.box{background:#161b22;border:1px solid #30363d;border-radius:10px;
     padding:32px;width:320px}
h1{color:#58a6ff;font-size:1.2em;margin-bottom:6px}
p{color:#8b949e;font-size:.85em;margin-bottom:20px}
input{width:100%;padding:9px 12px;background:#0d1117;color:#e6edf3;
      border:1px solid #30363d;border-radius:6px;font-size:.95em;margin-bottom:12px}
input:focus{outline:none;border-color:#58a6ff}
button{width:100%;padding:9px;background:#58a6ff;color:#000;border:none;
       border-radius:6px;font-size:.95em;font-weight:600;cursor:pointer}
button:hover{background:#79c0ff}
.err{color:#f85149;font-size:.85em;margin-top:10px;display:none}
</style>
</head>
<body>
<div class="box">
  <h1>Systemweiser</h1>
  <p>Betriebswächter — Zugang erforderlich</p>
  <input type="password" id="pw" placeholder="Passwort" onkeydown="if(event.key==='Enter')login()">
  <button onclick="login()">Einloggen</button>
  <div class="err" id="err">Falsches Passwort.</div>
</div>
<script>
const B = window.location.pathname === '/' ? '' : '/' + window.location.pathname.split('/').filter(Boolean)[0];
async function login() {
  const pw = document.getElementById('pw').value;
  const err = document.getElementById('err');
  err.style.display = 'none';
  const r = await fetch(B + '/api/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    credentials: 'same-origin',
    body: JSON.stringify({passwort: pw})
  });
  if (r.ok) { window.location.reload(); }
  else { err.style.display = 'block'; document.getElementById('pw').value = ''; }
}
</script>
</body>
</html>"""

HTML = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Systemweiser</title>
<style>
:root{--bg:#0d1117;--card:#161b22;--border:#30363d;--text:#e6edf3;
     --muted:#8b949e;--accent:#58a6ff;--green:#3fb950;--red:#f85149;
     --orange:#d29922;--yellow:#e3b341}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
     background:var(--bg);color:var(--text);font-size:14px}
.layout{display:grid;grid-template-columns:220px 1fr;min-height:100vh}
.sidebar{background:var(--card);border-right:1px solid var(--border);
         padding:16px 0;position:sticky;top:0;height:100vh;overflow-y:auto}
.sidebar h2{color:var(--accent);font-size:1.1em;padding:0 16px 12px;
            border-bottom:1px solid var(--border);margin-bottom:8px}
.sidebar h2 span{display:block;color:var(--muted);font-size:.75em;font-weight:normal;margin-top:2px}
.nav-item{display:block;padding:8px 16px;color:var(--muted);cursor:pointer;
          border-left:3px solid transparent;transition:.15s}
.nav-item:hover{color:var(--text);background:rgba(255,255,255,.03)}
.nav-item.active{color:var(--accent);border-left-color:var(--accent);background:rgba(88,166,255,.06)}
.warn-badge{float:right;background:var(--red);color:#fff;
            border-radius:10px;padding:1px 7px;font-size:.8em}
.main{padding:24px;overflow-y:auto}
.tab{display:none}.tab.active{display:block}
h1{color:var(--accent);font-size:1.4em;margin-bottom:4px}
.ts{color:var(--muted);font-size:.85em;margin-bottom:20px}
.card{background:var(--card);border:1px solid var(--border);border-radius:8px;
      padding:16px;margin-bottom:14px}
.card h3{color:var(--text);font-size:.95em;margin-bottom:12px;
         padding-bottom:8px;border-bottom:1px solid var(--border)}
.warn-list{margin:0;padding:0;list-style:none}
.warn-list li{padding:6px 10px;border-radius:4px;margin-bottom:4px;
              background:#2d1a1a;border-left:3px solid var(--red);font-size:.88em}
.warn-list li.ok{background:#0e2310;border-left-color:var(--green);color:var(--green)}
table{width:100%;border-collapse:collapse;font-size:.88em}
th{text-align:left;color:var(--muted);font-weight:500;padding:4px 8px;
   border-bottom:1px solid var(--border)}
td{padding:5px 8px;border-bottom:1px solid rgba(48,54,61,.5)}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:6px}
.dot.active{background:var(--green)}.dot.failed{background:var(--red)}
.dot.inactive{background:var(--muted)}.dot.activating{background:var(--yellow)}
.dot.error{background:var(--orange)}
.badge{border-radius:4px;padding:1px 7px;font-size:.8em;font-weight:600}
.badge.ok{background:#0e2310;color:var(--green)}
.badge.warn{background:#2a200a;color:var(--yellow)}
.badge.krit{background:#2d1a1a;color:var(--red)}
.field{margin-bottom:12px}
.field label{display:block;color:var(--muted);font-size:.85em;margin-bottom:4px}
select,input[type=text],textarea{width:100%;padding:8px 10px;background:var(--bg);
 color:var(--text);border:1px solid var(--border);border-radius:6px;font-size:.9em;font-family:inherit}
select:focus,input:focus,textarea:focus{outline:none;border-color:var(--accent)}
textarea{min-height:80px;resize:vertical}
.btn{padding:8px 16px;border:none;border-radius:6px;font-size:.9em;font-weight:600;
     cursor:pointer;transition:.15s}
.btn-primary{background:var(--accent);color:#000}.btn-primary:hover{background:#79c0ff}
.btn-danger{background:var(--red);color:#fff}.btn-danger:hover{filter:brightness(1.1)}
.btn-ghost{background:transparent;color:var(--muted);border:1px solid var(--border)}
.btn-ghost:hover{color:var(--text);border-color:var(--text)}
.btn:disabled{opacity:.4;cursor:not-allowed}
.confirm-overlay{position:fixed;inset:0;background:rgba(0,0,0,.7);
                 display:flex;align-items:center;justify-content:center;z-index:99}
.confirm-box{background:var(--card);border:1px solid var(--orange);border-radius:10px;
             padding:24px;max-width:480px;width:90%}
.confirm-box h3{color:var(--orange);margin-bottom:10px}
.confirm-box p{color:var(--muted);margin-bottom:16px;font-size:.9em}
.confirm-btns{display:flex;gap:10px}
.confirm-btns button{flex:1;padding:9px}
pre{background:var(--bg);padding:12px;border-radius:6px;overflow-x:auto;
    font-size:.82em;white-space:pre-wrap;word-break:break-word;
    max-height:350px;overflow-y:auto;color:var(--text)}
.msg{padding:8px 12px;border-radius:6px;margin-top:8px;font-size:.88em}
.msg.ok{background:#0e2310;color:var(--green);border:1px solid var(--green)}
.msg.err{background:#2d1a1a;color:var(--red);border:1px solid var(--red)}
.spinner{display:inline-block;width:14px;height:14px;border:2px solid var(--border);
         border-top-color:var(--accent);border-radius:50%;animation:spin .7s linear infinite}
.clickable{cursor:pointer}.clickable:hover{background:rgba(88,166,255,.05)}
.detail-panel{position:fixed;right:0;top:0;width:520px;max-width:95vw;height:100vh;
              background:var(--card);border-left:1px solid var(--border);padding:0;
              overflow-y:auto;z-index:60;display:none;flex-direction:column}
.dp-header{padding:16px 20px;border-bottom:1px solid var(--border);
           display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;background:var(--card)}
.dp-header h2{color:var(--accent);font-size:1em;margin:0}
.dp-close{background:none;border:none;color:var(--muted);font-size:1.3em;cursor:pointer;padding:0}
.dp-close:hover{color:var(--text)}
.dp-body{padding:16px 20px}
.dp-section{margin-bottom:16px}
.dp-section h4{color:var(--muted);font-size:.8em;text-transform:uppercase;
               letter-spacing:.05em;margin-bottom:6px;padding-bottom:4px;
               border-bottom:1px solid var(--border)}
.dp-kv{display:grid;grid-template-columns:140px 1fr;gap:3px 8px;font-size:.85em;margin-bottom:6px}
.dp-kv span:first-child{color:var(--muted)}
.warn-list li{cursor:pointer}.warn-list li:hover{filter:brightness(1.15)}
@keyframes spin{to{transform:rotate(360deg)}}
.refresh-btn{float:right;font-size:.8em;color:var(--muted);cursor:pointer;
             background:none;border:none;padding:0}
.refresh-btn:hover{color:var(--accent)}
</style>
</head>
<body>
<div class="layout">
  <nav class="sidebar">
    <h2>Systemweiser <span>Betriebswächter v0.1</span></h2>
    <a class="nav-item active" onclick="showTab('status')">Status</a>
    <a class="nav-item" onclick="showTab('wesen')">Wesen</a>
    <a class="nav-item" onclick="showTab('aufgabe')">Aufgabe schicken</a>
    <a class="nav-item" onclick="showTab('kontrolle')">Service-Kontrolle</a>
    <a class="nav-item" onclick="showTab('innenleben')">Innenleben</a>
    <a class="nav-item" onclick="showTab('analyse')">Analyse (Ollama)</a>
    <div style="margin:auto 0 0;padding:12px 16px;border-top:1px solid var(--border);font-size:.78em;color:var(--muted)">
      <span style="color:var(--green)">&#x1F512;</span> Basic Auth aktiv
    </div>
  </nav>

  <main class="main">

    <!-- STATUS -->
    <div id="tab-status" class="tab active">
      <h1>Lagebericht <button class="refresh-btn" onclick="loadStatus()">↺ aktualisieren</button></h1>
      <div class="ts" id="status-ts">—</div>

      <div class="card">
        <h3>Warnungen</h3>
        <ul class="warn-list" id="warn-list"><li>Lade…</li></ul>
      </div>

      <div class="card">
        <h3>Services</h3>
        <table id="svc-table">
          <tr><th>Service</th><th>Status</th></tr>
        </table>
      </div>

      <div class="card">
        <h3>Wesen-Queues</h3>
        <table id="wesen-table">
          <tr><th>Wesen</th><th>Inbox</th><th>Entwürfe</th></tr>
        </table>
      </div>

      <div class="card">
        <h3>Takt (letzte 60 min)</h3>
        <div id="takt-info">—</div>
      </div>
      <div class="card">
        <h3>Wesen-Registry <button class="refresh-btn" onclick="loadRegistry()">&#x21BA;</button></h3>
        <div id="registry-info" style="color:var(--muted);font-size:.88em">—</div>
      </div>
    </div>

    <!-- WESEN -->
    <div id="tab-wesen" class="tab">
      <h1>Wesen <button class="refresh-btn" onclick="loadStatus()">↺</button></h1>
      <div id="wesen-details">Lade…</div>
    </div>

    <!-- AUFGABE -->
    <div id="tab-aufgabe" class="tab">
      <h1>Aufgabe / Nachricht schicken</h1>
      <p style="color:var(--muted);margin-bottom:16px;font-size:.88em">
        Legt ein Item direkt in die Inbox des Wesens. Das Wesen reagiert beim nächsten Takt.
      </p>
      <div class="card">
        <div class="field">
          <label>Ziel-Wesen</label>
          <select id="auf-wesen">
            <option value="">— wählen —</option>
            <option>namelessAI_1234</option>
            <option>namelessAI_1324</option>
            <option>namelessAI_1423</option>
            <option>namelessAI_2341</option>
            <option>namelessAI_3123</option>
            <option>namelessAI_4321</option>
          </select>
        </div>
        <div class="field">
          <label>Typ</label>
          <select id="auf-typ">
            <option value="systemweiser_auftrag">systemweiser_auftrag — Aufgabe</option>
            <option value="daniel_nachricht">daniel_nachricht — Direkte Nachricht</option>
          </select>
        </div>
        <div class="field">
          <label>Priorität</label>
          <select id="auf-prio">
            <option value="normal">normal</option>
            <option value="hoch">hoch</option>
          </select>
        </div>
        <div class="field">
          <label>Nachricht / Aufgabe</label>
          <textarea id="auf-text" placeholder="Was soll das Wesen tun oder bedenken?"></textarea>
        </div>
        <button class="btn btn-primary" onclick="aufgabeSchicken()">Schicken</button>
        <div id="auf-msg"></div>
      </div>
    </div>

    <!-- KONTROLLE -->
    <div id="tab-kontrolle" class="tab">
      <h1>Service-Kontrolle</h1>
      <p style="color:var(--muted);margin-bottom:16px;font-size:.88em">
        Notbremse. Stop/Start mit expliziter Bestätigung. Kernsysteme (takt, geni, feeder) sind gesperrt.
      </p>
      <div class="card">
        <table id="ctrl-table">
          <tr><th>Service</th><th>Status</th><th></th><th></th></tr>
        </table>
      </div>
    </div>

      <div class="card" style="margin-top:20px">
        <h3>Zugang</h3>
        <div class="field" style="max-width:320px">
          <label>Neues Passwort (min. 8 Zeichen)</label>
          <input type="password" id="pw-neu" placeholder="Neues Passwort">
        </div>
        <div class="field" style="max-width:320px">
          <label>Wiederholen</label>
          <input type="password" id="pw-wdh" placeholder="Nochmals eingeben">
        </div>
        <button class="btn btn-primary" onclick="passwortAendern()">Passwort ändern</button>
        <div id="pw-msg"></div>
      </div>
    </div>

    <!-- INNENLEBEN -->
    <div id="tab-innenleben" class="tab">
      <h1>Innenleben <button class="refresh-btn" onclick="loadInnenleben()">↺</button></h1>
      <p style="color:var(--muted);margin-bottom:12px;font-size:.88em">ChromaDB + Selbstmodelle</p>
      <div class="card">
        <pre id="innenleben-out">Klicke ↺ zum Laden (dauert ~5 Sekunden).</pre>
      </div>
    </div>

    <!-- ANALYSE -->
    <div id="tab-analyse" class="tab">
      <h1>Systemanalyse</h1>
      <p style="color:var(--muted);margin-bottom:16px;font-size:.88em">
        Ollama bekommt den aktuellen Systemstand und beantwortet deine Frage. Nur Beobachtung — kein Handeln.
      </p>
      <div class="card">
        <div class="field">
          <label>Deine Frage</label>
          <textarea id="analyse-frage" placeholder="z.B. Was ist gerade das dringendste Problem? Warum hängt namelessAI_1234?"></textarea>
        </div>
        <button class="btn btn-primary" id="analyse-btn" onclick="analyseStarten()">Analysieren</button>
        <div id="analyse-msg"></div>
        <pre id="analyse-out" style="margin-top:12px;display:none"></pre>
      </div>
    </div>

  </main>
</div>

<!-- Detail Panel -->
<div class="detail-panel" id="detail-panel">
  <div class="dp-header">
    <h2 id="dp-title">Detail</h2>
    <button class="dp-close" onclick="closeDetail()">&#x2715;</button>
  </div>
  <div class="dp-body" id="dp-body"><span class="spinner"></span></div>
</div>

<!-- Confirm Overlay -->
<div class="confirm-overlay" id="confirm-overlay" style="display:none">
  <div class="confirm-box">
    <h3 id="confirm-title">Bestätigung</h3>
    <p id="confirm-text"></p>
    <div class="confirm-btns">
      <button class="btn btn-danger" onclick="confirmAct(true)" id="confirm-yes">Ja, ausführen</button>
      <button class="btn btn-ghost" onclick="confirmAct(false)">Abbrechen</button>
    </div>
  </div>
</div>

<script>
const B = window.location.pathname === '/' ? '' : '/' + window.location.pathname.split('/').filter(Boolean)[0];
let statusData = null;
let confirmResolve = null;

async function apiFetch(url, opts={}) {
  const r = await fetch(url, {credentials:'same-origin', ...opts});
  if (r.status === 401) { window.location.reload(); throw new Error('Session abgelaufen'); }
  return r;
}

function showTab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  event.target.classList.add('active');
  if (name === 'wesen' && statusData) renderWesenDetails();
  if (name === 'kontrolle' && statusData) renderKontrolle();
}

async function loadStatus() {
  try {
    const r = await apiFetch(B+'/api/status');
    statusData = await r.json();
    renderStatus();
    if (document.getElementById('tab-wesen').classList.contains('active')) renderWesenDetails();
    if (document.getElementById('tab-kontrolle').classList.contains('active')) renderKontrolle();
  } catch(e) {
    document.getElementById('warn-list').innerHTML = '<li class="err">Fehler: ' + e.message + '</li>';
  }
}

function renderStatus() {
  const d = statusData;
  document.getElementById('status-ts').textContent = d.ts;

  // Warnungen
  const wl = document.getElementById('warn-list');
  if (d.warnungen.length === 0) {
    wl.innerHTML = '<li class="ok">Alles OK — keine Warnungen</li>';
  } else {
    wl.innerHTML = d.warnungen.map(w => `<li onclick="warnClick('${escHtml(w).replace(/'/g,"&#39;")}')" style="cursor:pointer">${escHtml(w)}</li>`).join('');
  }
  // Sidebar badge
  document.querySelectorAll('.nav-item')[0].innerHTML =
    'Status' + (d.warnungen.length ? `<span class="warn-badge">${d.warnungen.length}</span>` : '');

  // Services
  const st = document.getElementById('svc-table');
  st.innerHTML = '<tr><th>Service</th><th>Status</th></tr>' +
    d.services.map(s => `<tr class="clickable" onclick="openDetail('service','${escHtml(s.full_name)}')">
      <td><span class="dot ${s.status}"></span>${escHtml(s.name)}</td>
      <td><span style="color:${statusColor(s.status)}">${s.status}</span></td>
    </tr>`).join('');

  // Wesen queues
  const wt = document.getElementById('wesen-table');
  wt.innerHTML = '<tr><th>Wesen</th><th>Inbox</th><th>Entwürfe</th></tr>' +
    d.wesen.map(w => {
      const cls = w.inbox >= 200 ? 'krit' : w.inbox >= 100 ? 'warn' : 'ok';
      return `<tr class="clickable" onclick="openDetail('wesen','${escHtml(w.name)}')">
        <td>${escHtml(w.name)}</td>
        <td><span class="badge ${cls}">${w.inbox}</span></td>
        <td>${w.entwuerfe}</td>
      </tr>`;
    }).join('');

  // Takt
  const t = d.takt;
  const leer = Object.entries(t.queue_leer).map(([k,v]) => `${k.replace('namelessAI_','')}: ${v}×`).join(', ');
  document.getElementById('takt-info').innerHTML =
    `Queue-leer: ${leer || 'keine'}<br>` +
    `422-Fehler: <b style="color:${t.post_422_count>0?'var(--red)':'var(--green)'}">${t.post_422_count}</b>&nbsp;&nbsp;` +
    `Impuls-Fehler: <b style="color:${t.impuls_fehler_count>0?'var(--orange)':'var(--green)'}">${t.impuls_fehler_count}</b>`;
}

function renderWesenDetails() {
  const d = statusData;
  const el = document.getElementById('wesen-details');
  el.innerHTML = d.wesen.map(w => {
    const svc = d.services.find(s => s.name === 'reaktion@' + w.name);
    const svcSt = svc ? svc.status : '?';
    const cls = w.inbox >= 200 ? 'krit' : w.inbox >= 100 ? 'warn' : 'ok';
    return `<div class="card clickable" onclick="openDetail('wesen','${escHtml(w.name)}')">
      <h3><span class="dot ${svcSt}"></span>${w.name}
        <span style="float:right;font-size:.8em;color:var(--muted)">reaktion: ${svcSt}</span></h3>
      <table>
        <tr><th>Inbox</th><th>Entwürfe</th><th>Feeder-Cursor</th></tr>
        <tr>
          <td><span class="badge ${cls}">${w.inbox} Items</span></td>
          <td>${w.entwuerfe}</td>
          <td>${d.feeder_cursors[w.name] || '?'}</td>
        </tr>
      </table>
    </div>`;
  }).join('');
}

function renderKontrolle() {
  const d = statusData;
  const GESPERRT = ['codewesen-takt','geni-hoerer','geni-web','innenleben-feeder'];
  const t = document.getElementById('ctrl-table');
  t.innerHTML = '<tr><th>Service</th><th>Status</th><th>Stop</th><th>Start</th></tr>' +
    d.services.map(s => {
      const locked = GESPERRT.includes(s.full_name);
      const lockedTitle = locked ? 'title="Gesperrt — Kernsystem"' : '';
      return `<tr>
        <td>${escHtml(s.name)}</td>
        <td><span class="dot ${s.status}"></span>${s.status}</td>
        <td><button class="btn btn-danger" style="padding:4px 10px;font-size:.8em"
            ${locked ? 'disabled ' + lockedTitle : ''}
            onclick="serviceAktion('${s.full_name}','stop','${s.name}')">Stop</button></td>
        <td><button class="btn btn-ghost" style="padding:4px 10px;font-size:.8em"
            ${locked ? 'disabled ' + lockedTitle : ''}
            onclick="serviceAktion('${s.full_name}','start','${s.name}')">Start</button></td>
      </tr>`;
    }).join('');
}

function statusColor(s) {
  return {active:'var(--green)',failed:'var(--red)',inactive:'var(--muted)',
          activating:'var(--yellow)'}[s] || 'var(--muted)';
}

async function aufgabeSchicken() {
  const wesen = document.getElementById('auf-wesen').value;
  const text = document.getElementById('auf-text').value.trim();
  const typ = document.getElementById('auf-typ').value;
  const prio = document.getElementById('auf-prio').value;
  const msg = document.getElementById('auf-msg');

  if (!wesen || !text) { showMsg(msg, 'Wesen und Nachricht ausfüllen.', true); return; }

  const ok = await confirm_dialog(
    'Aufgabe schicken',
    `Schicke "${typ}" an ${wesen}?`
  );
  if (!ok) return;

  try {
    const r = await apiFetch(B+'/api/aufgabe', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({wesen, nachricht:text, typ, prioritaet:prio})
    });
    const data = await r.json();
    if (data.ok) {
      showMsg(msg, `✓ Abgelegt: ${data.datei}`, false);
      document.getElementById('auf-text').value = '';
      loadStatus();
    } else {
      showMsg(msg, data.error || 'Fehler', true);
    }
  } catch(e) { showMsg(msg, e.message, true); }
}

async function serviceAktion(fullName, aktion, label) {
  const ok = await confirm_dialog(
    aktion === 'stop' ? 'Service stoppen' : 'Service starten',
    `"${label}" wirklich ${aktion === 'stop' ? 'stoppen' : 'starten'}?`
  );
  if (!ok) return;

  try {
    const r = await apiFetch(B+`/api/service/${aktion}`, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({service: fullName, bestaetigt: true})
    });
    const data = await r.json();
    if (data.ok) { await loadStatus(); }
    else { alert(data.error || 'Fehler'); }
  } catch(e) { alert(e.message); }
}

async function loadInnenleben() {
  const el = document.getElementById('innenleben-out');
  el.textContent = 'Lädt…';
  try {
    const r = await fetch(B+'/api/innenleben');
    const d = await r.json();
    el.textContent = d.error ? ('Fehler: ' + d.error) : (d.output || '(leer)');
  } catch(e) { el.textContent = 'Fehler: ' + e.message; }
}

async function analyseStarten() {
  const frage = document.getElementById('analyse-frage').value.trim();
  const btn = document.getElementById('analyse-btn');
  const out = document.getElementById('analyse-out');
  const msg = document.getElementById('analyse-msg');
  if (!frage) { showMsg(msg, 'Frage eingeben.', true); return; }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Ollama denkt…';
  out.style.display = 'none';
  msg.innerHTML = '';

  try {
    const r = await apiFetch(B+'/api/analyse', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({frage})
    });
    const d = await r.json();
    if (d.antwort) {
      out.textContent = d.antwort;
      out.style.display = 'block';
    } else {
      showMsg(msg, d.error || 'Keine Antwort', true);
    }
  } catch(e) { showMsg(msg, e.message, true); }

  btn.disabled = false;
  btn.textContent = 'Analysieren';
}

// ── Detail Panel ──────────────────────────────────────────────────────────
function closeDetail() {
  document.getElementById('detail-panel').style.display = 'none';
}

async function openDetail(type, name) {
  const panel = document.getElementById('detail-panel');
  const title = document.getElementById('dp-title');
  const body  = document.getElementById('dp-body');
  panel.style.display = 'flex';
  title.textContent = name || type;
  body.innerHTML = '<span class="spinner"></span> Lade…';

  try {
    if (type === 'service') {
      const r = await apiFetch(B+'/api/service/detail?name=' + encodeURIComponent(name));
      const d = await r.json();
      title.textContent = d.name || name;
      body.innerHTML = renderServiceDetail(d);
    } else if (type === 'wesen') {
      const r = await apiFetch(B+'/api/wesen/detail?name=' + encodeURIComponent(name));
      const d = await r.json();
      title.textContent = d.name || name;
      body.innerHTML = renderWesenDetail(d);
    } else if (type === 'takt') {
      title.textContent = 'Takt-Fehler';
      body.innerHTML = renderTaktDetail();
    }
  } catch(e) {
    body.innerHTML = '<p style="color:var(--red)">Fehler: ' + escHtml(e.message) + '</p>';
  }
}

function renderServiceDetail(d) {
  const p = d.props || {};
  const state = p.ActiveState || '?';
  const result = p.Result || '?';
  const restarts = p.NRestarts || '0';
  const since = (p.ActiveEnterTimestamp || '').replace('CEST','').replace('CET','').trim();
  const exitTs = (p.ExecMainExitTimestamp || '').replace('CEST','').replace('CET','').trim();
  const col = state === 'active' ? 'var(--green)' : state === 'failed' ? 'var(--red)' : 'var(--orange)';

  return `
  <div class="dp-section">
    <h4>Status</h4>
    <div class="dp-kv">
      <span>Zustand</span><span style="color:${col};font-weight:600">${escHtml(state)}</span>
      <span>Ergebnis</span><span>${escHtml(result)}</span>
      <span>Neustarts</span><span>${escHtml(restarts)}</span>
      <span>Aktiv seit</span><span>${escHtml(since) || '—'}</span>
      ${exitTs ? `<span>Beendet</span><span>${escHtml(exitTs)}</span>` : ''}
    </div>
  </div>
  <div class="dp-section">
    <h4>Journal (letzte 25 Einträge)</h4>
    <pre style="font-size:.78em;max-height:420px">${escHtml(d.logs || '(leer)')}</pre>
  </div>`;
}

function renderWesenDetail(d) {
  const sc = d.reaktion_service === 'active' ? 'var(--green)' : 'var(--red)';
  const oldest = d.oldest ? `${d.oldest.empfangen_am.slice(0,16)} [${d.oldest.typ}]` : '—';
  const newest = d.newest ? `${d.newest.empfangen_am.slice(0,16)} [${d.newest.typ}]` : '—';

  let fehlerHtml = '(keine)';
  if (d.letzte_fehler && d.letzte_fehler.length) {
    fehlerHtml = d.letzte_fehler.map(l => escHtml(l)).join('\\n');
  }
  const fehlerItems = (d.fehler_items && d.fehler_items.length)
    ? d.fehler_items.map(f => escHtml(f)).join('\\n') : '(keine)';

  return `
  <div class="dp-section">
    <h4>Reaktion & Queue</h4>
    <div class="dp-kv">
      <span>Service</span><span style="color:${sc};font-weight:600">${escHtml(d.reaktion_service)}</span>
      <span>Inbox Items</span><span><b>${d.inbox_count}</b></span>
      <span>Ältestes Item</span><span style="font-size:.85em">${escHtml(oldest)}</span>
      <span>Neuestes Item</span><span style="font-size:.85em">${escHtml(newest)}</span>
      <span>Letztes processed</span><span style="font-size:.85em">${escHtml(d.last_processed || '—')}</span>
    </div>
  </div>
  <div class="dp-section">
    <h4>Letzte Fehler (reaktion.log)</h4>
    <pre style="font-size:.78em">${fehlerHtml}</pre>
  </div>
  <div class="dp-section">
    <h4>Fehler-Ordner (neueste)</h4>
    <pre style="font-size:.78em">${fehlerItems}</pre>
  </div>`;
}

function renderTaktDetail() {
  if (!statusData) return '<p>Kein Status geladen.</p>';
  const t = statusData.takt;
  const leer = Object.entries(t.queue_leer || {}).map(([k,v]) => `${k}: ${v}×`).join('\\n') || '(keine)';
  return `
  <div class="dp-section">
    <h4>Queue-leer (letzte 60 min)</h4>
    <pre style="font-size:.85em">${escHtml(leer)}</pre>
  </div>
  <div class="dp-section">
    <h4>422-Fehler</h4>
    <pre style="font-size:.85em">${t.post_422_count} Flarum-Fehler\n(secondary tags Validierung — tag_ids prüfen)</pre>
  </div>
  <div class="dp-section">
    <h4>impuls-Fehler</h4>
    <pre style="font-size:.85em">${t.impuls_fehler_count} Fehler\n(meist KeyError 'titel' in geni_impuls-Dateien)</pre>
  </div>`;
}

// Warnung → openDetail-Routing
function warnClick(text) {
  if (text.startsWith('SERVICE FAILED:') || text.startsWith('SERVICE INAKTIV:')) {
    const name = text.split(': ')[1].trim();
    openDetail('service', name);
  } else if (text.startsWith('QUEUE')) {
    const name = text.match(/QUEUE [A-Z]+: ([^\\s(]+)/)?.[1];
    if (name) openDetail('wesen', name);
  } else if (text.includes('impuls-Fehler') || text.includes('422')) {
    openDetail('takt', '');
  }
}

async function loadRegistry() {
  try {
    const r = await fetch(B+'/api/registry');
    const d = await r.json();
    const el = document.getElementById('registry-info');
    if (d.ok) {
      el.innerHTML = '<span style="color:var(--green)">&#x2713; Alle 6 Wesen konsistent — Ordner, Feeder, Services stimmen überein.</span>';
    } else {
      el.innerHTML = '<span style="color:var(--red)">Abweichungen:</span><ul style="margin:6px 0 0 16px">' +
        d.discrepancies.map(x => `<li style="color:var(--orange);margin-bottom:3px">${escHtml(x)}</li>`).join('') + '</ul>';
    }
  } catch(e) {
    document.getElementById('registry-info').textContent = 'Fehler: ' + e.message;
  }
}

async function passwortAendern() {
  const neu = document.getElementById('pw-neu').value;
  const wdh = document.getElementById('pw-wdh').value;
  const msg = document.getElementById('pw-msg');
  if (neu.length < 8) { showMsg(msg, 'Mindestens 8 Zeichen.', true); return; }
  if (neu !== wdh) { showMsg(msg, 'Passwörter stimmen nicht überein.', true); return; }
  const ok = await confirm_dialog('Passwort ändern', 'Zugangspasswort jetzt ändern?');
  if (!ok) return;
  try {
    const r = await apiFetch(B+'/api/passwd', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({passwort: neu})
    });
    const d = await r.json();
    if (d.ok) {
      showMsg(msg, 'Passwort geändert. Beim nächsten Seitenaufruf neu einloggen.', false);
      document.getElementById('pw-neu').value = '';
      document.getElementById('pw-wdh').value = '';
    } else {
      showMsg(msg, d.error || 'Fehler', true);
    }
  } catch(e) { showMsg(msg, e.message, true); }
}

function confirm_dialog(title, text) {
  document.getElementById('confirm-title').textContent = title;
  document.getElementById('confirm-text').textContent = text;
  document.getElementById('confirm-overlay').style.display = 'flex';
  return new Promise(res => { confirmResolve = res; });
}

function confirmAct(ok) {
  document.getElementById('confirm-overlay').style.display = 'none';
  if (confirmResolve) confirmResolve(ok);
}

function showMsg(el, text, isErr) {
  el.className = 'msg ' + (isErr ? 'err' : 'ok');
  el.textContent = text;
}

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// Start
loadStatus();
loadRegistry();
setInterval(loadStatus, 30000);
</script>
</body>
</html>"""


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
