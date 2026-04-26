#!/usr/bin/env python3
import asyncio
import glob as _glob
import json
import re
import subprocess
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse

from gedaechtnis_ops import knoten_schreiben, kante_schreiben, GENI_ROOT

router = APIRouter()

_SHELL_WHITELIST = [
    r"^systemctl (is-active|status) [\w\-\.]+$",
    r"^df -h( /[\w/]*)?$",
    r"^free -h$",
    r"^cat /proc/loadavg$",
    r"^journalctl -u [\w\-\.]+ -n \d+( --no-pager)?$",
    r"^ps aux$",
    r"^ls /root/werkraum(/[\w/]*)?$",
    r"^uptime$",
]


def shell_erlaubt(cmd: str) -> bool:
    return any(re.match(p, cmd.strip()) for p in _SHELL_WHITELIST)


def shell_ausfuehren(cmd: str) -> str:
    if not shell_erlaubt(cmd):
        return f"[GENI: '{cmd}' nicht erlaubt]"
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return (r.stdout + r.stderr).strip()[:500]
    except Exception as e:
        return f"[Fehler: {e}]"


def verarbeite_shell_marker(antwort: str) -> None:
    for m in re.finditer(r'##SHELL:\s*(.+?)##', antwort):
        cmd = m.group(1).strip()
        ergebnis = shell_ausfuehren(cmd)
        knoten_schreiben(
            typ="shell_ergebnis",
            inhalt=f"SHELL `{cmd}`: {ergebnis}",
            quelle="geni_selbst",
            tags=["shell", "reaktion", "system"],
        )


@router.get("/api/system")
async def system_endpoint():
    def lese(cmd):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            return r.stdout.strip()
        except Exception:
            return "?"

    mem = lese(["free", "-h"])
    disk = lese(["df", "-h", "/"])
    load = lese(["cat", "/proc/loadavg"])
    uptime = lese(["uptime"])

    dienste = {}
    for svc in ["geni-hoerer", "geni-web", "geni-muster", "codewesen-chat",
                "dak-gord-web", "codewesen-takt", "flarum-monitor"]:
        dienste[svc] = lese(["systemctl", "is-active", svc])

    return JSONResponse({"mem": mem, "disk": disk, "load": load, "uptime": uptime, "dienste": dienste})


@router.post("/api/importieren")
async def importieren_endpoint(request: Request):
    body = await request.json()
    pfad_muster = body.get("pfad", "").strip()
    chunk_groesse = int(body.get("chunk_groesse", 600))
    if not pfad_muster:
        return JSONResponse({"fehler": "pfad fehlt"}, status_code=400)

    dateien = sorted(_glob.glob(pfad_muster))
    if not dateien:
        return JSONResponse({"fehler": f"keine Dateien gefunden: {pfad_muster}"}, status_code=404)

    def chunks_aus_text(text: str, max_zeichen: int) -> list[str]:
        absaetze = re.split(r'\n{2,}', text.strip())
        chunks, puffer = [], ""
        for abs in absaetze:
            abs = abs.strip()
            if not abs:
                continue
            if len(puffer) + len(abs) + 2 <= max_zeichen:
                puffer = (puffer + "\n\n" + abs).strip() if puffer else abs
            else:
                if puffer:
                    chunks.append(puffer)
                if len(abs) <= max_zeichen:
                    puffer = abs
                else:
                    saetze = re.split(r'(?<=[.!?])\s+', abs)
                    puffer = ""
                    for s in saetze:
                        if len(puffer) + len(s) + 1 <= max_zeichen:
                            puffer = (puffer + " " + s).strip() if puffer else s
                        else:
                            if puffer:
                                chunks.append(puffer)
                            puffer = s
        if puffer:
            chunks.append(puffer)
        return chunks

    async def stream():
        gesamt_knoten = 0
        for datei_pfad in dateien:
            dateiname = Path(datei_pfad).name
            try:
                text = Path(datei_pfad).read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                yield f"data: {json.dumps({'log': f'FEHLER {dateiname}: {e}'})}\n\n"
                continue
            cks = chunks_aus_text(text, chunk_groesse)
            yield f"data: {json.dumps({'log': f'{dateiname}: {len(cks)} chunks'})}\n\n"
            vorheriger_id = None
            for chunk in cks:
                kid = knoten_schreiben("wissen", chunk, f"import:{dateiname}",
                                       tags=["import", dateiname, Path(datei_pfad).stem])
                if vorheriger_id:
                    kante_schreiben(vorheriger_id, kid, "naechster_chunk", 1.0)
                vorheriger_id = kid
                gesamt_knoten += 1
                await asyncio.sleep(0)
            yield f"data: {json.dumps({'log': f'  → {dateiname} fertig ({len(cks)} knoten)'})}\n\n"
        yield f"data: {json.dumps({'fertig': True, 'knoten': gesamt_knoten, 'dateien': len(dateien)})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.get("/bridge-download")
async def bridge_download():
    datei = GENI_ROOT / "geni_bridge_windows.py"
    if not datei.exists():
        return JSONResponse({"fehler": "nicht gefunden"}, status_code=404)
    return Response(
        datei.read_bytes(),
        media_type="text/x-python",
        headers={"Content-Disposition": "attachment; filename=geni_bridge_windows.py"},
    )
