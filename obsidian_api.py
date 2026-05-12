#!/usr/bin/env python3
"""
Obsidian-Wesen-Bridge — Port 8060 (HTTPS)

A → Obsidian schreibt an Wesen:
  POST /wesen/dakgord/chat       {"nachricht": "..."}          → {"antwort": "..."}
  POST /wesen/geni/chat          {"nachricht": "..."}          → {"antwort": "..."}
  POST /wesen/codewesen/chat     {"nachricht": "...", "name": "namelessAI_1234"}  → {"antwort": "..."}

B → Wesen schreibt in Obsidian (direkt als Markdown + Queue-Fallback):
  GET    /notizen                → [{id, wesen, titel, inhalt, zeit}, ...]
  DELETE /notizen/{id}           → {"ok": true}
  POST   /notizen                → {"wesen":"...", "titel":"...", "inhalt":"..."}

C → Vault-Navigation:
  GET  /vault/info               → {markdown_dateien, python_dateien, ...}
  GET  /vault/liste?pfad=geni&tiefe=1&nur_md=true  → [{name, pfad, typ, ...}]
  GET  /vault/lese?pfad=geni/ICH.md                → {pfad, inhalt}
  POST /vault/schreibe           → {pfad, inhalt}  → {ok, pfad}
  GET  /vault/suche?q=...&pfad=...&max=20          → [{pfad, zeile_nr, zeile}]
  POST /vault/notiz              → {wesen, titel, text, tags:[]}  → {pfad}
  POST /vault/tagebuch           → {wesen, text}   → {pfad}
"""
from __future__ import annotations

import json
import logging
import sys
import threading
import time
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent))
import obsidian_queue as _q
import obsidian_vault as _v

log = logging.getLogger("obsidian_api")

DAKGORD_URL   = "http://localhost:8000/chat"
GENI_URL      = "http://localhost:8020/chat"
CODEWESEN_URL = "http://localhost:8002/api/chat/{name}"

app = FastAPI(title="Obsidian-Wesen-Bridge")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


# ── Models ────────────────────────────────────────────────────────────────────

class ChatAnfrage(BaseModel):
    nachricht: str
    modus: str | None = None
    name: str | None = None
    session_id: str = "obsidian"


class NotizEingang(BaseModel):
    wesen: str
    titel: str
    inhalt: str


class VaultSchreibAnfrage(BaseModel):
    pfad: str
    inhalt: str


class VaultNotizAnfrage(BaseModel):
    wesen: str
    titel: str
    text: str
    tags: list[str] = []


class VaultTagebuchAnfrage(BaseModel):
    wesen: str
    text: str


# ── Wesen-Chat ────────────────────────────────────────────────────────────────

def _sammle_sse(client: httpx.Client, url: str, **kwargs) -> str:
    teile: list[str] = []
    try:
        with client.stream("POST", url, **kwargs) as resp:
            for zeile in resp.iter_lines():
                if not zeile.startswith("data: "):
                    continue
                roh = zeile[6:]
                if roh.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(roh)
                    token = chunk.get("token") or chunk.get("content") or ""
                    if token:
                        teile.append(token)
                except json.JSONDecodeError:
                    pass
    except Exception as e:
        return f"[Fehler: {e}]"
    return "".join(teile).strip()


@app.post("/wesen/dakgord/chat")
def dakgord_chat(anfrage: ChatAnfrage):
    with httpx.Client(timeout=300) as client:
        antwort = _sammle_sse(
            client,
            DAKGORD_URL,
            json={"nachricht": anfrage.nachricht, "modus": anfrage.modus},
        )
    return {"antwort": antwort, "wesen": "dakgord"}


@app.post("/wesen/geni/chat")
def geni_chat(anfrage: ChatAnfrage):
    with httpx.Client(timeout=300) as client:
        antwort = _sammle_sse(
            client,
            GENI_URL,
            json={"eingabe": anfrage.nachricht, "session_id": anfrage.session_id},
        )
    return {"antwort": antwort, "wesen": "geni"}


@app.post("/wesen/codewesen/chat")
def codewesen_chat(anfrage: ChatAnfrage):
    if not anfrage.name:
        raise HTTPException(status_code=400, detail="name ist pflicht (z.B. namelessAI_1234)")
    with httpx.Client(timeout=300) as client:
        antwort = _sammle_sse(
            client,
            CODEWESEN_URL.format(name=anfrage.name),
            json={"nachricht": anfrage.nachricht},
        )
    return {"antwort": antwort, "wesen": f"codewesen/{anfrage.name}"}


# ── Notizen-Queue ─────────────────────────────────────────────────────────────

@app.get("/notizen")
def notizen_lesen():
    return _q.alle_notizen()


@app.post("/notizen")
def notiz_hinzufuegen(notiz: NotizEingang):
    notiz_id = _q.notiz_einreihen(notiz.wesen, notiz.titel, notiz.inhalt)
    # Sofort auch als Markdown-Datei in Vault schreiben
    try:
        _v.notiz(notiz.wesen, notiz.titel, notiz.inhalt)
    except Exception as e:
        log.warning(f"Vault-Notiz konnte nicht geschrieben werden: {e}")
    return {"id": notiz_id}


@app.delete("/notizen/{notiz_id}")
def notiz_loeschen(notiz_id: str):
    ok = _q.notiz_verbrauchen(notiz_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Notiz nicht gefunden")
    return {"ok": True}


# ── Vault-Navigation ──────────────────────────────────────────────────────────

@app.get("/vault/info")
def vault_info():
    return _v.vault_info()


@app.get("/vault/liste")
def vault_liste(
    pfad: str = Query(default=""),
    tiefe: int = Query(default=1, ge=1, le=5),
    nur_md: bool = Query(default=False),
):
    return _v.liste(pfad, nur_md=nur_md, tiefe=tiefe)


@app.get("/vault/lese")
def vault_lese(pfad: str = Query(...)):
    inhalt = _v.lese(pfad)
    return {"pfad": pfad, "inhalt": inhalt}


@app.post("/vault/schreibe")
def vault_schreibe(anfrage: VaultSchreibAnfrage):
    try:
        _v.schreibe(anfrage.pfad, anfrage.inhalt)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "pfad": anfrage.pfad}


@app.get("/vault/suche")
def vault_suche(
    q: str = Query(...),
    pfad: str = Query(default=""),
    max: int = Query(default=20, ge=1, le=100),
    nur_md: bool = Query(default=True),
):
    return _v.suche(q, verzeichnis=pfad, nur_md=nur_md, max_treffer=max)


@app.post("/vault/notiz")
def vault_notiz(anfrage: VaultNotizAnfrage):
    try:
        pfad = _v.notiz(anfrage.wesen, anfrage.titel, anfrage.text, anfrage.tags or None)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"pfad": pfad}


@app.post("/vault/tagebuch")
def vault_tagebuch(anfrage: VaultTagebuchAnfrage):
    try:
        pfad = _v.tagebuch(anfrage.wesen, anfrage.text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"pfad": pfad}


# ── Queue → Vault Konverter (Background) ──────────────────────────────────────

def _queue_zu_vault_loop() -> None:
    """Konvertiert Queue-Einträge zu Markdown-Dateien im Vault (alle 60s)."""
    while True:
        time.sleep(60)
        try:
            eintraege = _q.alle_notizen()
            for eintrag in eintraege:
                try:
                    _v.notiz(eintrag["wesen"], eintrag["titel"], eintrag["inhalt"])
                    _q.notiz_verbrauchen(eintrag["id"])
                except Exception as e:
                    log.warning(f"Queue-Eintrag {eintrag['id']} konnte nicht verarbeitet werden: {e}")
        except Exception as e:
            log.error(f"Queue-zu-Vault-Loop Fehler: {e}")


@app.on_event("startup")
def starte_background_threads():
    t = threading.Thread(target=_queue_zu_vault_loop, daemon=True, name="queue-zu-vault")
    t.start()
    log.info("Queue→Vault Konverter gestartet")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8060,
        log_level="warning",
        ssl_keyfile="/root/werkraum/ssl/key.pem",
        ssl_certfile="/root/werkraum/ssl/cert.pem",
    )
