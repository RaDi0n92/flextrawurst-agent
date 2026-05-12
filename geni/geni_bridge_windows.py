#!/usr/bin/env python3
"""
GENI Bridge — Windows  (volle Version mit Vision + Kontrolle)
=============================================================

GENI kann:
  - deinen Desktop sehen (Screenshots, automatisch + auf Anfrage)
  - Maus bewegen und klicken
  - Tastatur übernehmen
  - Hotkeys senden
  - das aktive Fenster erkennen

SETUP (einmalig):
  pip install websockets pyautogui pillow mss

STARTEN:
  python geni_bridge_windows.py

AUTOSTART (optional):
  Datei in Windows Aufgabenplanung eintragen oder in den Startup-Ordner legen:
  shell:startup  →  Verknüpfung zu "pythonw geni_bridge_windows.py"
"""

# ── KONFIGURATION ──────────────────────────────────────────────────────────────

VPS_HOST  = "217.154.14.29"
VPS_PORT  = 8020
TOKEN     = "CvxQ0sJPkxZ277AsosP_N3GdqQyBfmg4"

# Automatischer Screenshot alle N Sekunden (0 = deaktiviert)
AUTO_SCREENSHOT_INTERVALL = 60  # 1 Minute

# Screenshot-Qualität (1–100, niedrig = kleiner aber unschärfer)
SCREENSHOT_QUALITAET = 60

# Erlaubte Shell-Befehle (Whitelist)
SHELL_WHITELIST = [
    "dir", "tasklist", "systeminfo", "ver", "whoami", "hostname",
    "ipconfig", "wmic logicaldisk get size,freespace,caption",
    "powershell Get-Date",
    "powershell Get-Process",
    "powershell [System.Environment]::OSVersion.VersionString",
    "powershell (Get-PSDrive C).Free",
    "powershell Get-ComputerInfo",
]

# Kontrolle erlauben (Maus/Tastatur) — auf False setzen um zu deaktivieren
KONTROLLE_ERLAUBT = True

# ── ENDE KONFIGURATION ─────────────────────────────────────────────────────────

import asyncio
import base64
import io
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time

# Abhängigkeiten prüfen
_fehlend = []
try:
    import websockets
except ImportError:
    _fehlend.append("websockets")
try:
    import pyautogui
    pyautogui.FAILSAFE = True  # Maus in Ecke oben-links = Notbremse
    pyautogui.PAUSE = 0.05
except ImportError:
    _fehlend.append("pyautogui")
try:
    from PIL import Image
except ImportError:
    _fehlend.append("pillow")

if _fehlend:
    print(f"[GENI Bridge] Fehlende Pakete: {', '.join(_fehlend)}")
    print(f"[GENI Bridge] Installieren mit:  pip install {' '.join(_fehlend)}")
    sys.exit(1)


# ── Screenshot ─────────────────────────────────────────────────────────────────

def screenshot_machen(qualitaet: int = SCREENSHOT_QUALITAET) -> str:
    """Macht einen Screenshot, gibt base64-JPEG zurück."""
    bild = pyautogui.screenshot()
    # Skalierung auf max 1280px Breite für Übertragung
    breite, hoehe = bild.size
    if breite > 1280:
        faktor = 1280 / breite
        bild = bild.resize((1280, int(hoehe * faktor)), Image.LANCZOS)
    buf = io.BytesIO()
    bild.save(buf, format="JPEG", quality=qualitaet, optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def aktives_fenster_info() -> dict:
    """Gibt Titel und App des aktiven Fensters zurück."""
    try:
        r = subprocess.run(
            'powershell "Add-Type -AssemblyName UIAutomationClient; '
            '[System.Windows.Automation.AutomationElement]::FocusedElement.Current.Name"',
            shell=True, capture_output=True, text=True, timeout=5
        )
        titel = r.stdout.strip()[:200]
    except Exception:
        titel = "?"

    try:
        r2 = subprocess.run(
            'powershell "(Get-Process | Where-Object {$_.MainWindowTitle -ne \'\'} | '
            'Sort-Object CPU -Descending | Select-Object -First 1).MainWindowTitle"',
            shell=True, capture_output=True, text=True, timeout=5
        )
        aktiv = r2.stdout.strip()[:200]
    except Exception:
        aktiv = "?"

    return {"titel": titel, "aktiv": aktiv}


# ── Shell-Befehle ──────────────────────────────────────────────────────────────

def shell_erlaubt(cmd: str) -> bool:
    cmd_l = cmd.strip().lower()
    return any(cmd_l.startswith(w.lower()) for w in SHELL_WHITELIST)


def shell_ausfuehren(cmd: str) -> tuple[str, bool]:
    if not shell_erlaubt(cmd):
        return f"[Bridge: nicht in Whitelist: '{cmd}']", False
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=15, encoding="utf-8", errors="replace"
        )
        return (r.stdout + r.stderr).strip()[:1000] or "(kein Output)", True
    except subprocess.TimeoutExpired:
        return "[timeout]", False
    except Exception as e:
        return f"[Fehler: {e}]", False


# ── Kontrolle ──────────────────────────────────────────────────────────────────

def maus_bewegen(x: int, y: int, dauer: float = 0.3):
    pyautogui.moveTo(x, y, duration=dauer)


def maus_klicken(x: int | None, y: int | None, taste: str = "left"):
    if x is not None and y is not None:
        pyautogui.click(x, y, button=taste)
    else:
        pyautogui.click(button=taste)


def maus_doppelklick(x: int, y: int):
    pyautogui.doubleClick(x, y)


def tastatur_tippen(text: str, intervall: float = 0.03):
    pyautogui.typewrite(text, interval=intervall)


def tastatur_hotkey(*tasten: str):
    pyautogui.hotkey(*tasten)


def tastatur_druecken(taste: str):
    pyautogui.press(taste)


def scroll(richtung: str, klicks: int = 3):
    pyautogui.scroll(klicks if richtung == "hoch" else -klicks)


# ── System-Info ────────────────────────────────────────────────────────────────

def system_info() -> dict:
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        ip = "?"

    info = {
        "hostname": socket.gethostname(),
        "os": platform.platform()[:80],
        "python": platform.python_version(),
        "ip": ip,
        "kontrolle": KONTROLLE_ERLAUBT,
        "auto_screenshot": AUTO_SCREENSHOT_INTERVALL,
    }

    try:
        nutzung = shutil.disk_usage("C:\\")
        info["disk"] = f"C: {nutzung.free//1024//1024//1024}GB frei / {nutzung.total//1024//1024//1024}GB"
    except Exception:
        info["disk"] = "?"

    try:
        r = subprocess.run(
            'powershell "(Get-WmiObject Win32_OperatingSystem).FreePhysicalMemory"',
            shell=True, capture_output=True, text=True, timeout=5
        )
        frei_mb = int(r.stdout.strip()) // 1024
        r2 = subprocess.run(
            'powershell "(Get-WmiObject Win32_OperatingSystem).TotalVisibleMemorySize"',
            shell=True, capture_output=True, text=True, timeout=5
        )
        gesamt_mb = int(r2.stdout.strip()) // 1024
        info["ram"] = f"{frei_mb}MB frei / {gesamt_mb}MB"
    except Exception:
        info["ram"] = "?"

    return info


def snapshot_daten() -> dict:
    daten = {}
    try:
        nutzung = shutil.disk_usage("C:\\")
        daten["disk"] = f"C: {nutzung.free//1024//1024//1024}GB frei"
    except Exception:
        daten["disk"] = "?"
    try:
        r = subprocess.run(
            'powershell "(Get-WmiObject Win32_OperatingSystem).FreePhysicalMemory"',
            shell=True, capture_output=True, text=True, timeout=5
        )
        daten["ram"] = f"{int(r.stdout.strip())//1024}MB frei"
    except Exception:
        daten["ram"] = "?"
    try:
        r = subprocess.run(
            'powershell "Get-Process | Measure-Object | Select-Object -ExpandProperty Count"',
            shell=True, capture_output=True, text=True, timeout=5
        )
        daten["prozesse"] = r.stdout.strip()
    except Exception:
        daten["prozesse"] = "?"
    return daten


# ── Nachrichten-Handler ────────────────────────────────────────────────────────

async def handle_befehl(ws, msg: dict):
    cmd_id = msg.get("id", "")
    cmd    = msg.get("cmd", "")
    print(f"  [shell] {cmd}")
    ausgabe, ok = shell_ausfuehren(cmd)
    await ws.send(json.dumps({"typ": "ergebnis", "id": cmd_id, "ok": ok, "ausgabe": ausgabe}))


async def handle_screenshot_anfrage(ws, msg: dict):
    cmd_id = msg.get("id", "")
    print("  [screenshot] wird gemacht...")
    try:
        b64 = screenshot_machen(msg.get("qualitaet", SCREENSHOT_QUALITAET))
        fenster = aktives_fenster_info()
        await ws.send(json.dumps({
            "typ": "screenshot",
            "id": cmd_id,
            "bild": b64,
            "fenster": fenster,
        }))
        print(f"  [screenshot] gesendet ({len(b64)//1024}KB)")
    except Exception as e:
        print(f"  [screenshot] Fehler: {e}")
        await ws.send(json.dumps({"typ": "screenshot_fehler", "id": cmd_id, "fehler": str(e)}))


async def handle_kontrolle(ws, msg: dict):
    if not KONTROLLE_ERLAUBT:
        await ws.send(json.dumps({"typ": "kontrolle_fehler", "id": msg.get("id",""),
                                  "fehler": "Kontrolle deaktiviert (KONTROLLE_ERLAUBT=False)"}))
        return

    aktion  = msg.get("aktion", "")
    cmd_id  = msg.get("id", "")
    ok      = True
    info    = ""

    try:
        if aktion == "klick":
            maus_klicken(msg.get("x"), msg.get("y"), msg.get("taste", "left"))
            info = f"geklickt ({msg.get('x')},{msg.get('y')})"
        elif aktion == "doppelklick":
            maus_doppelklick(msg.get("x", 0), msg.get("y", 0))
            info = f"doppelgeklickt ({msg.get('x')},{msg.get('y')})"
        elif aktion == "bewegen":
            maus_bewegen(msg.get("x", 0), msg.get("y", 0))
            info = f"maus bewegt ({msg.get('x')},{msg.get('y')})"
        elif aktion == "tippen":
            tastatur_tippen(msg.get("text", ""))
            info = f"getippt: {msg.get('text','')[:30]}"
        elif aktion == "hotkey":
            tasten = msg.get("tasten", [])
            tastatur_hotkey(*tasten)
            info = f"hotkey: {'+'.join(tasten)}"
        elif aktion == "taste":
            tastatur_druecken(msg.get("taste", ""))
            info = f"taste: {msg.get('taste','')}"
        elif aktion == "scroll":
            scroll(msg.get("richtung", "hoch"), msg.get("klicks", 3))
            info = f"scroll {msg.get('richtung','hoch')}"
        else:
            ok = False
            info = f"unbekannte aktion: {aktion}"
    except pyautogui.FailSafeException:
        ok = False
        info = "Notbremse ausgelöst (Maus in Ecke)"
    except Exception as e:
        ok = False
        info = str(e)

    print(f"  [kontrolle] {aktion}: {info}")
    await ws.send(json.dumps({"typ": "kontrolle_ergebnis", "id": cmd_id, "ok": ok, "info": info}))


async def handle_fenster_anfrage(ws, msg: dict):
    info = aktives_fenster_info()
    await ws.send(json.dumps({"typ": "fenster_info", "id": msg.get("id",""), **info}))


# ── Haupt-Loop ─────────────────────────────────────────────────────────────────

async def verbindung_halten(ws):
    info = system_info()
    await ws.send(json.dumps({"typ": "hello", "system": info}))
    print(f"[GENI Bridge] Verbunden")
    print(f"  Hostname : {info['hostname']}")
    print(f"  OS       : {info['os']}")
    print(f"  RAM      : {info['ram']}")
    print(f"  Disk     : {info['disk']}")
    print(f"  Kontrolle: {'JA' if KONTROLLE_ERLAUBT else 'NEIN'}")
    print(f"  Screenshot alle {AUTO_SCREENSHOT_INTERVALL}s" if AUTO_SCREENSHOT_INTERVALL else "  Auto-Screenshot: AUS")

    letzter_snapshot    = 0.0
    letzter_screenshot  = 0.0

    async def hintergrund():
        nonlocal letzter_snapshot, letzter_screenshot
        while True:
            await asyncio.sleep(5)
            jetzt = time.time()

            if jetzt - letzter_snapshot >= 300:
                daten = snapshot_daten()
                try:
                    await ws.send(json.dumps({"typ": "snapshot", "daten": daten}))
                    letzter_snapshot = jetzt
                except Exception:
                    break

            if AUTO_SCREENSHOT_INTERVALL and jetzt - letzter_screenshot >= AUTO_SCREENSHOT_INTERVALL:
                try:
                    b64 = screenshot_machen()
                    fenster = aktives_fenster_info()
                    await ws.send(json.dumps({
                        "typ": "screenshot",
                        "id": "auto",
                        "bild": b64,
                        "fenster": fenster,
                    }))
                    letzter_screenshot = jetzt
                    print(f"  [auto-screenshot] gesendet")
                except Exception as e:
                    print(f"  [auto-screenshot] Fehler: {e}")

    hg_task = asyncio.create_task(hintergrund())

    try:
        async for raw in ws:
            try:
                msg = json.loads(raw)
            except Exception:
                continue

            typ = msg.get("typ", "")

            if typ == "pong":
                pass
            elif typ == "befehl":
                await handle_befehl(ws, msg)
            elif typ == "screenshot_anfrage":
                await handle_screenshot_anfrage(ws, msg)
            elif typ == "kontrolle":
                await handle_kontrolle(ws, msg)
            elif typ == "fenster_anfrage":
                await handle_fenster_anfrage(ws, msg)
            elif typ == "ping":
                await ws.send(json.dumps({"typ": "pong"}))

    finally:
        hg_task.cancel()
        print("[GENI Bridge] Verbindung getrennt.")


async def main():
    url = f"ws://{VPS_HOST}:{VPS_PORT}/ws/bridge?token={TOKEN}"
    print(f"[GENI Bridge] Starte...")
    print(f"[GENI Bridge] VPS: {VPS_HOST}:{VPS_PORT}")
    wiederholungen = 0

    while True:
        try:
            print(f"[GENI Bridge] Verbinde...")
            async with websockets.connect(
                url,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=5,
                max_size=50 * 1024 * 1024,  # 50MB für Screenshots
            ) as ws:
                wiederholungen = 0
                await verbindung_halten(ws)

        except (ConnectionRefusedError, OSError) as e:
            wiederholungen += 1
            wartezeit = min(60, 5 * wiederholungen)
            print(f"[GENI Bridge] Nicht erreichbar. Versuch {wiederholungen}, warte {wartezeit}s...")
            await asyncio.sleep(wartezeit)

        except Exception as e:
            wiederholungen += 1
            wartezeit = min(60, 5 * wiederholungen)
            print(f"[GENI Bridge] Getrennt ({type(e).__name__}). Reconnect in {wartezeit}s...")
            await asyncio.sleep(wartezeit)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[GENI Bridge] Gestoppt.")
