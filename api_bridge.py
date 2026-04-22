import os
import subprocess
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

API_KEY = os.environ.get("BRIDGE_API_KEY", "BITTE_SETZEN")
WERKRAUM = Path("/root/werkraum")

app = FastAPI(title="VPS API Bridge")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def _check_key(key: str | None):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Ungueltiger API-Key")

class FileReadRequest(BaseModel):
    path: str

class FileWriteRequest(BaseModel):
    path: str
    content: str
    create_dirs: bool = True

class FileListRequest(BaseModel):
    path: str = "."
    recursive: bool = False
    max_depth: int = 3

class ExecRequest(BaseModel):
    command: str
    cwd: str = "/root/werkraum"
    timeout: int = 30

@app.get("/api/status")
def status(x_api_key: str | None = Header(None)):
    _check_key(x_api_key)
    return {"status": "online", "werkraum": str(WERKRAUM), "exists": WERKRAUM.exists()}

@app.post("/api/files/read")
def read_file(req: FileReadRequest, x_api_key: str | None = Header(None)):
    _check_key(x_api_key)
    target = (WERKRAUM / req.path).resolve()
    if not str(target).startswith(str(WERKRAUM.resolve())):
        raise HTTPException(400, "Pfad ausserhalb von werkraum")
    if not target.exists():
        raise HTTPException(404, f"Datei nicht gefunden: {req.path}")
    if not target.is_file():
        raise HTTPException(400, f"Keine regulaere Datei: {req.path}")
    try:
        content = target.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        raise HTTPException(500, f"Lesefehler: {e}")
    return {"path": req.path, "content": content, "size": target.stat().st_size}

@app.post("/api/files/write")
def write_file(req: FileWriteRequest, x_api_key: str | None = Header(None)):
    _check_key(x_api_key)
    target = (WERKRAUM / req.path).resolve()
    if not str(target).startswith(str(WERKRAUM.resolve())):
        raise HTTPException(400, "Pfad ausserhalb von werkraum")
    if req.create_dirs:
        target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(req.content, encoding="utf-8")
    return {"path": req.path, "written": len(req.content), "success": True}

@app.post("/api/files/list")
def list_files(req: FileListRequest, x_api_key: str | None = Header(None)):
    _check_key(x_api_key)
    target = (WERKRAUM / req.path).resolve()
    if not str(target).startswith(str(WERKRAUM.resolve())):
        raise HTTPException(400, "Pfad ausserhalb von werkraum")
    if not target.exists():
        raise HTTPException(404, f"Verzeichnis nicht gefunden: {req.path}")
    items = []
    if req.recursive:
        for p in sorted(target.rglob("*")):
            rel = p.relative_to(WERKRAUM)
            depth = len(rel.parts)
            if depth > req.max_depth:
                continue
            if p.name.startswith(".") or "__pycache__" in str(p) or "node_modules" in str(p) or ".git" in str(p):
                continue
            items.append({"path": str(rel), "type": "dir" if p.is_dir() else "file", "size": p.stat().st_size if p.is_file() else None})
    else:
        for p in sorted(target.iterdir()):
            if p.name.startswith(".") or p.name == "__pycache__" or p.name == "node_modules":
                continue
            rel = p.relative_to(WERKRAUM)
            items.append({"path": str(rel), "type": "dir" if p.is_dir() else "file", "size": p.stat().st_size if p.is_file() else None})
    return {"path": req.path, "items": items, "count": len(items)}

@app.post("/api/exec")
def exec_command(req: ExecRequest, x_api_key: str | None = Header(None)):
    _check_key(x_api_key)
    try:
        result = subprocess.run(req.command, shell=True, capture_output=True, text=True, timeout=req.timeout, cwd=req.cwd)
        return {"stdout": result.stdout[-10000:], "stderr": result.stderr[-5000:], "returncode": result.returncode, "success": result.returncode == 0}
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": f"Timeout nach {req.timeout}s", "returncode": -1, "success": False}
    except Exception as e:
        raise HTTPException(500, f"Ausfuehrungsfehler: {e}")
