"""
Remote control server for Claude Code.
Spawns Claude Code in a PTY and bridges it to a WebSocket terminal in the browser.

Usage:
    REMOTE_TOKEN=mysecret uvicorn remote_control.server:app --host 0.0.0.0 --port 8765
"""

import asyncio
import fcntl
import os
import pty
import shutil
import signal
import struct
import termios
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

TOKEN: str = os.environ.get("REMOTE_TOKEN", "changeme")
STATIC_DIR = Path(__file__).parent / "static"

master_fd: Optional[int] = None
child_pid: Optional[int] = None
clients: set[WebSocket] = set()
# Rolling output buffer so new clients see recent history
output_buffer: list[bytes] = []
MAX_BUFFER_CHUNKS = 400


def _set_nonblocking(fd: int) -> None:
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)


def _set_pty_size(fd: int, cols: int, rows: int) -> None:
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))


def _find_claude() -> str:
    # Honour explicit override first
    explicit = os.environ.get("CLAUDE_BIN")
    if explicit:
        return explicit
    found = shutil.which("claude")
    if found:
        return found
    # Common install locations as fallback
    for candidate in [
        "/root/.local/bin/claude",
        "/usr/local/bin/claude",
        "/usr/bin/claude",
    ]:
        if os.path.isfile(candidate):
            return candidate
    raise RuntimeError("claude binary not found — set CLAUDE_BIN=/path/to/claude")


async def _spawn_claude() -> None:
    global master_fd, child_pid
    claude_bin = _find_claude()
    pid, fd = pty.fork()
    if pid == 0:
        os.execv(claude_bin, [claude_bin])
        os._exit(1)
    master_fd = fd
    child_pid = pid
    _set_nonblocking(fd)
    _set_pty_size(fd, 220, 50)
    asyncio.get_running_loop().add_reader(fd, _on_pty_readable)


def _on_pty_readable() -> None:
    try:
        data = os.read(master_fd, 4096)
    except OSError:
        return
    output_buffer.append(data)
    if len(output_buffer) > MAX_BUFFER_CHUNKS:
        output_buffer.pop(0)
    asyncio.ensure_future(_broadcast(data))


async def _broadcast(data: bytes) -> None:
    dead: set[WebSocket] = set()
    for ws in list(clients):
        try:
            await ws.send_bytes(data)
        except Exception:
            dead.add(ws)
    clients.difference_update(dead)


def _check_auth(token: str) -> None:
    if token != TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _spawn_claude()
    yield
    if child_pid is not None:
        try:
            os.kill(child_pid, signal.SIGTERM)
        except ProcessLookupError:
            pass


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root() -> HTMLResponse:
    return HTMLResponse((STATIC_DIR / "index.html").read_text())


@app.get("/status")
async def status(token: str = Query(...)) -> dict:
    _check_auth(token)
    alive = False
    if child_pid is not None:
        try:
            os.kill(child_pid, 0)
            alive = True
        except ProcessLookupError:
            pass
    return {"running": alive, "pid": child_pid, "clients": len(clients)}


@app.post("/resize")
async def resize(cols: int, rows: int, token: str = Query(...)) -> dict:
    _check_auth(token)
    if master_fd is not None:
        try:
            _set_pty_size(master_fd, cols, rows)
        except OSError:
            pass
    return {"ok": True}


@app.post("/restart")
async def restart(token: str = Query(...)) -> dict:
    """Kill and respawn the Claude Code process."""
    _check_auth(token)
    global master_fd, child_pid
    loop = asyncio.get_running_loop()
    if master_fd is not None:
        try:
            loop.remove_reader(master_fd)
        except Exception:
            pass
        try:
            os.close(master_fd)
        except OSError:
            pass
    if child_pid is not None:
        try:
            os.kill(child_pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    master_fd = None
    child_pid = None
    output_buffer.clear()
    await _spawn_claude()
    return {"ok": True}


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket, token: str = Query(...)) -> None:
    if token != TOKEN:
        await websocket.close(code=4001)
        return
    await websocket.accept()
    clients.add(websocket)
    # Replay buffered output so the new client sees context
    for chunk in list(output_buffer):
        try:
            await websocket.send_bytes(chunk)
        except Exception:
            clients.discard(websocket)
            return
    try:
        while True:
            data = await websocket.receive_bytes()
            if master_fd is not None:
                try:
                    os.write(master_fd, data)
                except OSError:
                    break
    except WebSocketDisconnect:
        pass
    finally:
        clients.discard(websocket)
