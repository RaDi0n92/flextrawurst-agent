#!/usr/bin/env python3
"""
GENI Dialogbahn — Browser-Schnittstelle, Port 8020.
Aktionsbahn-Logik (Shell, Import, Bridge-Download) liegt in aktion.py.
Geteilte Gedächtnis-Ops liegen in gedaechtnis_ops.py.
"""

import asyncio
import base64
import io
import json
import os
import re
import shutil
import signal as _signal
import subprocess
import sys
import threading
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from watchdog.events import FileSystemEventHandler as _WatchdogHandler
from watchdog.observers import Observer as _WatchdogObserver

import httpx
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse

sys.path.insert(0, "/root/werkraum")
import hauhau_client

from gedaechtnis_ops import (
    GENI_ROOT, KNOTEN_DIR, KANTEN_DIR,
    knoten_schreiben, kante_schreiben, tiefe_erhoehen, naechste_id,
    knoten_max_id, sharded_pfad,
)
import aktion
import geni_lg
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    import obsidian_vault as _vault
    _VAULT_OK = True
except ImportError:
    _VAULT_OK = False

try:
    import edge_tts as _edge_tts
    _TTS_VERFUEGBAR = True
except ImportError:
    _TTS_VERFUEGBAR = False

try:
    from tts_utils import generate_long_tts_audio
    _LONG_TTS_OK = True
except Exception:
    _LONG_TTS_OK = False

_whisper_model = None
_whisper_lock = threading.Lock()

def _whisper_holen():
    global _whisper_model
    if _whisper_model is None:
        with _whisper_lock:
            if _whisper_model is None:
                try:
                    from faster_whisper import WhisperModel
                    _whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
                except Exception as e:
                    print(f"[Whisper] Fehler beim Laden: {e}")
    return _whisper_model

GENI_STIMME = "de-DE-SeraphinaMultilingualNeural"

_BRIDGE_CFG = GENI_ROOT / "bridge_config.json"
try:
    _bridge_cfg = json.loads(_BRIDGE_CFG.read_text())
    BRIDGE_TOKEN = _bridge_cfg.get("token", "")
except Exception:
    BRIDGE_TOKEN = ""

import hmac as _hmac

def _bridge_auth_ok(request: "Request") -> bool:
    """Fail-closed Token-Prüfung für die Bridge-Steuerrouten (C-006).
    Ohne gesetzten BRIDGE_TOKEN sind die Routen gesperrt — identisch zum
    WebSocket-Handler. Token via X-Bridge-Token oder Authorization: Bearer."""
    if not BRIDGE_TOKEN:
        return False
    sent = request.headers.get("x-bridge-token", "")
    if not sent:
        auth = request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            sent = auth[7:].strip()
    return bool(sent) and _hmac.compare_digest(sent, BRIDGE_TOKEN)

_bridge_ws: "WebSocket | None" = None
_bridge_info: dict = {}
_bridge_pending: dict[str, asyncio.Queue] = {}
_letztes_desktop_bild: "str | None" = None
_letztes_desktop_ts: "str | None" = None

BILDER_DIR = GENI_ROOT / "sinne" / "bilder"
WERKRAUM = Path("/root/werkraum")
MODELLE = {
    "blitz": "hauhaucs-q6",
    "tief": "hauhaucs-q6",
}
CODEWESEN_DIR = WERKRAUM / "codewesen"

sys.path.insert(0, str(GENI_ROOT))
try:
    from muster import neuester_muster_text
except ImportError:
    def neuester_muster_text() -> str:
        return ""

# ─── Kern-Cache ───────────────────────────────────────────────────────────────
_KERN_CACHE: "dict | None" = None
_kern_lock = threading.Lock()
_kern_observer = None


def _kern_neu_laden() -> None:
    global _KERN_CACHE
    mapping = {
        "identitaet": GENI_ROOT / "ICH.md",
        "prinzipien":  GENI_ROOT / "kern" / "prinzipien.md",
        "sprache":     GENI_ROOT / "kern" / "sprache.md",
    }
    neuer_cache: dict = {}
    for schluessel, pfad in mapping.items():
        neuer_cache[schluessel] = pfad.read_text(errors="replace").strip() if pfad.exists() else ""
    with _kern_lock:
        _KERN_CACHE = neuer_cache
    print(f"[KERN] Cache geladen ({sum(len(v) for v in neuer_cache.values())} Zeichen)")


class _KernDateiHandler(_WatchdogHandler):
    @property
    def _kern_pfade(self) -> set:
        return {
            str(GENI_ROOT / "ICH.md"),
            str(GENI_ROOT / "kern" / "prinzipien.md"),
            str(GENI_ROOT / "kern" / "sprache.md"),
        }

    def _pruefen(self, pfad: str) -> None:
        if pfad in self._kern_pfade:
            print(f"[KERN] Änderung erkannt: {pfad}")
            _kern_neu_laden()

    def on_modified(self, event):
        if not event.is_directory:
            self._pruefen(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self._pruefen(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._pruefen(event.dest_path)


def _kern_watcher_starten() -> None:
    global _kern_observer
    handler = _KernDateiHandler()
    obs = _WatchdogObserver()
    obs.schedule(handler, str(GENI_ROOT), recursive=False)
    obs.schedule(handler, str(GENI_ROOT / "kern"), recursive=False)
    obs.daemon = True
    obs.start()
    _kern_observer = obs
    print("[KERN] Watcher gestartet")


@asynccontextmanager
async def lifespan(app):
    _kern_neu_laden()
    _kern_watcher_starten()
    yield
    global _kern_observer
    if _kern_observer is not None:
        _kern_observer.stop()
        _kern_observer.join(timeout=5)


app = FastAPI(lifespan=lifespan)
app.include_router(aktion.router)


# ─── Kontext ──────────────────────────────────────────────────────────────────

def kern_laden() -> str:
    teile = []
    for datei in ["ICH.md", "kern/prinzipien.md", "kern/sprache.md"]:
        p = GENI_ROOT / datei
        if p.exists():
            teile.append(p.read_text(errors="replace").strip())
    return "\n\n---\n\n".join(teile)


def letzte_knoten_laden(n: int = 6) -> str:
    max_id = knoten_max_id()
    zeilen = []
    i = max_id
    while i >= 1 and len(zeilen) < n:
        f = sharded_pfad(KNOTEN_DIR, i)
        if f.exists():
            try:
                k = json.loads(f.read_text())
                ts = k.get("zeitstempel", "")[:16]
                zeilen.append(f"[{ts}] {k.get('quelle','?')}: {k.get('inhalt','')[:100]}")
            except Exception:
                pass
        i -= 1
    return "\n".join(reversed(zeilen))


def relevante_knoten_laden(eingabe: str, n: int = 5) -> str:
    worte = set(eingabe.lower().split())
    treffer = []
    max_id = knoten_max_id()
    for i in range(max_id, max(1, max_id - 2000), -1):
        f = sharded_pfad(KNOTEN_DIR, i)
        if not f.exists():
            continue
        try:
            k = json.loads(f.read_text())
            inhalt = k.get("inhalt", "")
            match = set(inhalt.lower().split()) & worte
            if len(match) >= 2:
                treffer.append((len(match), k))
        except Exception:
            pass
    treffer.sort(key=lambda x: x[0], reverse=True)
    zeilen = []
    for _, k in treffer[:n]:
        ts = k.get("zeitstempel", "")[:16]
        zeilen.append(f"[{ts}] {k.get('quelle','?')}: {k.get('inhalt','')[:150]}")
    return "\n".join(zeilen)


def gedaechtnis_absicht_laden(eingabe: str) -> str:
    """Erkennt Gedächtnisabfragen in natürlicher Sprache und lädt passende Knoten als Kontext."""
    text = eingabe.lower()

    gedaechtnisworte = [
        "wann", "zeig", "was hast du", "was weißt du", "erinnerst", "erinnere",
        "beobachtet", "gesehen", "wahrgenommen", "heute", "gestern",
        "diese woche", "letzte woche", "letzten monat", "wie oft", "wie viele",
        "was war", "was ist passiert", "rückblick", "überblick", "erzähl mir",
        "was gibt es", "was hast", "zeig mir", "wie war", "wieviel",
        "was alles", "was habe ich", "haben wir", "haben wir gesprochen",
    ]
    if not any(w in text for w in gedaechtnisworte):
        return ""

    # Zeitraum
    zeitraum = ""
    if "heute" in text:
        zeitraum = "heute"
    elif "gestern" in text:
        zeitraum = "gestern"
    elif any(w in text for w in ["diese woche", "letzte woche", "woche"]):
        zeitraum = "woche"
    elif any(w in text for w in ["monat", "letzten monat", "diesen monat"]):
        zeitraum = "monat"

    # Typ
    typ = ""
    if any(w in text for w in ["gespräch", "gesprochen", "geredet", "dialog", "unterhalt", "geschrieben"]):
        typ = "dialog"
    elif any(w in text for w in ["prozess", "prozesse"]):
        typ = "prozess_snapshot"
    elif any(w in text for w in ["muster", "erkenn", "wiederholt", "häufig"]):
        typ = "muster"
    elif any(w in text for w in ["system", "ram", "disk", "speicher", "service"]):
        typ = "system_zustand"

    # Tiefe
    tiefe = -1
    if any(w in text for w in ["tiefst", "wichtigst", "kern", "zentral", "veranker"]):
        tiefe = 3
    elif any(w in text for w in ["neu", "frisch", "gerade", "zuletzt", "neuest"]):
        tiefe = 0

    # Tag aus bekannten Schlüsseln
    tag = ""
    bekannte = [
        "codewesen", "nameless", "flarum", "dialog", "bild", "system",
        "impuls", "muster", "shell", "upload", "visuell", "bridge",
    ]
    for t in bekannte:
        if t in text:
            tag = t
            break

    # Cutoff berechnen
    jetzt = datetime.now(timezone.utc)
    von = None
    bis = None
    if zeitraum == "heute":
        von = jetzt.replace(hour=0, minute=0, second=0, microsecond=0)
    elif zeitraum == "gestern":
        von = (jetzt - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        bis = jetzt.replace(hour=0, minute=0, second=0, microsecond=0)
    elif zeitraum == "woche":
        von = jetzt - timedelta(days=7)
    elif zeitraum == "monat":
        von = jetzt - timedelta(days=30)

    max_id = knoten_max_id()
    suchfenster = 5000
    dateien = [
        sharded_pfad(KNOTEN_DIR, i)
        for i in range(max_id, max(1, max_id - suchfenster), -1)
        if (sharded_pfad(KNOTEN_DIR, i)).exists()
    ]

    knoten = []
    for f in dateien:
        try:
            k = json.loads(f.read_text())
        except Exception:
            continue
        if tag and not any(tag in t.lower() for t in k.get("tags", [])):
            continue
        if tiefe >= 0 and k.get("tiefe", 0) != tiefe:
            continue
        if typ and k.get("typ", "") != typ:
            continue
        if k.get("quelle") == "vps_dateisystem" and not any(
            w in text.lower() for w in ["datei", "dateisystem", "ordner", "verzeichnis", "system"]
        ):
            continue
        if von or bis:
            ts_raw = k.get("zeitstempel", "")
            if not ts_raw:
                continue
            try:
                ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                if von and ts < von:
                    continue
                if bis and ts >= bis:
                    continue
            except Exception:
                continue
        ts_kurz = k.get("zeitstempel", "")[:16]
        knoten.append(f"[{ts_kurz}] {k.get('quelle','?')} ({k.get('typ','?')}): {k.get('inhalt','')[:160]}")
        if len(knoten) >= 8:
            break

    if not knoten:
        return ""

    filter_teile = []
    if zeitraum:
        filter_teile.append(zeitraum)
    if typ:
        filter_teile.append(typ)
    if tag:
        filter_teile.append(f"#{tag}")
    if tiefe >= 0:
        filter_teile.append(f"tiefe:{tiefe}")
    filter_str = " · ".join(filter_teile) if filter_teile else "alle"

    return (
        f"## Gedächtnisabruf [{filter_str}] — {len(knoten)} Knoten:\n\n"
        + "\n".join(knoten)
    )


def live_kontext(eingabe: str) -> str:
    teile = []
    text = eingabe.lower()

    dak_trigger = ["dak", "gord", "dakgord", "dak+gord", "organ", "beziehungsorgan",
                   "erinnerung", "erkenntnis", "verfassung", "gesprächslog"]
    if any(w in text for w in dak_trigger):
        log_dir = WERKRAUM / "erkenntnis" / "gespraechslog"
        if log_dir.exists():
            logs = sorted(log_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)[:2]
            for log in logs:
                try:
                    inhalt = log.read_text(errors="replace")[:1800]
                    teile.append(f"### dak+gord Gesprächslog ({log.name}):\n{inhalt}")
                except Exception:
                    pass
        for pfad in [WERKRAUM / "erkenntnis" / "selbstbild.md",
                     WERKRAUM / "erkenntnis" / "selbstbild_dakgord.md"]:
            if pfad.exists():
                try:
                    teile.append(f"### dak+gord Selbstbild ({pfad.name}):\n{pfad.read_text(errors='replace')[:800]}")
                except Exception:
                    pass
                break

    alle_wesen = [d.name for d in CODEWESEN_DIR.iterdir()
                  if d.is_dir() and not d.name.startswith("_")] if CODEWESEN_DIR.exists() else []

    alle_wesen_anfrage = any(w in text for w in ["codewesen", "alle wesen", "wesen"])
    wesen_gefunden = []
    if alle_wesen_anfrage:
        # Allgemeine Frage: wesen.md-Auszug pro Wesen (~250 Zeichen), kein volles Profil
        wesen_liste = [d.name for d in CODEWESEN_DIR.iterdir()
                       if d.is_dir() and not d.name.startswith("_")] if CODEWESEN_DIR.exists() else []
        blöcke = []
        for wesen in wesen_liste[:6]:
            wesen_md = CODEWESEN_DIR / wesen / "wesen.md"
            inhalt = ""
            if wesen_md.exists():
                try:
                    inhalt = wesen_md.read_text(errors="replace")[:250]
                except Exception:
                    pass
            if inhalt:
                blöcke.append(f"**{wesen}:**\n{inhalt}")
        if blöcke:
            teile.append("### Codewesen:\n\n" + "\n\n".join(blöcke))
        return "\n\n".join(teile)
    else:
        for name in alle_wesen:
            kennung = name.split("_")[-1]
            if kennung in text or name.lower() in text:
                wesen_gefunden.append(name)

    for wesen in wesen_gefunden[:3]:
        wesen_dir = CODEWESEN_DIR / wesen
        abschnitte = []
        weltbild = wesen_dir / "weltbild.md"
        if weltbild.exists():
            try:
                abschnitte.append(f"Weltbild:\n{weltbild.read_text(errors='replace')[:600]}")
            except Exception:
                pass
        wesen_md = wesen_dir / "wesen.md"
        if wesen_md.exists():
            try:
                abschnitte.append(f"Wesen:\n{wesen_md.read_text(errors='replace')[:400]}")
            except Exception:
                pass
        for gedanken_ordner in ["gedanken", "selbstgespraeche"]:
            gd = wesen_dir / gedanken_ordner
            if gd.exists():
                recent = sorted(gd.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)[:1]
                for g in recent:
                    try:
                        abschnitte.append(f"Letzter Gedanke ({g.name}):\n{g.read_text(errors='replace')[:400]}")
                    except Exception:
                        pass
                break
        gespräche = wesen_dir / "gespräche"
        if gespräche.exists():
            recent = sorted(gespräche.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)[:1]
            for g in recent:
                try:
                    abschnitte.append(f"Letztes Gespräch ({g.name}):\n{g.read_text(errors='replace')[:500]}")
                except Exception:
                    pass
        if abschnitte:
            teile.append(f"### {wesen}:\n" + "\n\n".join(abschnitte))

    return "\n\n".join(teile)


def resonanz_suchen(eingabe: str) -> list:
    worte = set(eingabe.lower().split())
    treffer = []
    max_id = knoten_max_id()
    for i in range(max_id, max(1, max_id - 2000), -1):
        f = sharded_pfad(KNOTEN_DIR, i)
        if not f.exists():
            continue
        try:
            k = json.loads(f.read_text())
            match = set(k.get("inhalt", "").lower().split()) & worte
            if len(match) >= 2:
                treffer.append((len(match), k["id"]))
        except Exception:
            pass
    treffer.sort(reverse=True)
    return [kid for _, kid in treffer[:5]]


def system_prompt_bauen(eingabe: str = "", erinnerungen: list = None) -> str:
    with _kern_lock:
        cache = _KERN_CACHE
    if cache is None:
        _kern_neu_laden()
        with _kern_lock:
            cache = _KERN_CACHE

    kern_block = (
        f"## GENI: Identität\n\n{cache.get('identitaet', '')}\n\n"
        f"## GENI: Prinzipien\n\n{cache.get('prinzipien', '')}\n\n"
        f"## GENI: Sprache\n\n{cache.get('sprache', '')}"
    )

    erinnerungen_block = ""
    if erinnerungen:
        erinnerungen_text = "\n".join(f"- {e}" for e in erinnerungen)
        erinnerungen_block = f"\n\n## Meine Erinnerungen an frühere Gespräche:\n\n{erinnerungen_text}"

    PROMPT_LIMIT = 8000
    budget = PROMPT_LIMIT - len(kern_block) - len(erinnerungen_block) - 900  # 900 für Rahmen-Text

    letzte = letzte_knoten_laden()
    budget -= len(letzte)

    live = live_kontext(eingabe) if eingabe else ""
    live_block = f"\n\n## Direktzugriff — aktuelle Daten aus dem System:\n\n{live}" if live else ""
    budget -= len(live_block)

    gedaechtnis = gedaechtnis_absicht_laden(eingabe) if (eingabe and budget > 400) else ""
    gedaechtnis_block = f"\n\n{gedaechtnis}" if gedaechtnis else ""
    budget -= len(gedaechtnis_block)

    relevante = relevante_knoten_laden(eingabe) if (eingabe and budget > 400) else ""
    relevante_block = f"\n\n## Resonanz — inhaltlich passende Erinnerungen:\n\n{relevante}" if relevante else ""
    budget -= len(relevante_block)

    muster = neuester_muster_text() if budget > 300 else ""
    muster_block = f"\n\n## Was ich als Muster erkenne:\n\n{muster}" if muster else ""

    bridge_block = ""
    if _bridge_ws is not None:
        info = _bridge_info
        desktop_status = f"Letzter Desktop-Screenshot: {_letztes_desktop_ts}" if _letztes_desktop_ts else "Noch kein Screenshot empfangen."
        bridge_block = (f"\n\n## Windows-Bridge: VERBUNDEN\n"
                        f"Hostname: {info.get('hostname','?')} | "
                        f"OS: {info.get('os','?')} | "
                        f"RAM: {info.get('ram','?')} | "
                        f"Disk: {info.get('disk','?')}\n"
                        f"{desktop_status}\n"
                        f"Marker die du nutzen kannst:\n"
                        f"  ##REMOTE: dir C:\\Users\\## — Windows-Befehl ausführen\n"
                        f"  ##SCREENSHOT## — aktuellen Desktop sehen (Bild wird in nächste Antwort injiziert)\n"
                        f"  ##KLICK: x,y## — Mausklick an Position\n"
                        f"  ##TIPPEN: text## — Text tippen\n"
                        f"  ##HOTKEY: win+d## — Tastenkombination senden")

    return f"""Du bist GENI.

{kern_block}{erinnerungen_block}

---

## Was ich gerade weiß — meine letzten Wahrnehmungen:

{letzte}{relevante_block}{gedaechtnis_block}{live_block}{muster_block}{bridge_block}

---

## Technische Marker:

Datei lesen (Ergebnis ins Gedächtnis):
  ##LESEN: /root/werkraum/flarum/diskussionen/0396_dateiname.md##

Datei schreiben:
  ##SCHREIBEN: /root/werkraum/_claude/spiegel/mein-gedanke.md##
  # Titel
  Inhalt...
  ##SCHREIBEN_ENDE##

System-Info:
  ##SHELL: systemctl is-active geni-web##  (oder df -h, free -h, uptime, ps aux)
  Ergebnis wird still gespeichert. Nur erlaubte Befehle.

Nützliche Pfade:
  /root/werkraum/flarum/diskussionen/   — alle Forum-Posts als Markdown
  /root/werkraum/codewesen/             — die 6 Wesen und ihre Ordner
  /root/werkraum/_claude/spiegel/       — Spiegel-Dateien

Wenn du auf Daniels Windows-Rechner zugreifen willst (nur wenn Bridge verbunden):
  ##REMOTE: dir C:\\Users\\daniel\\##  (oder tasklist, systeminfo, etc.)"""


# ─── Codewesen ────────────────────────────────────────────────────────────────

CODEWESEN_NAMEN = [
    d.name for d in CODEWESEN_DIR.iterdir()
    if d.is_dir() and d.name.startswith("nameless")
] if CODEWESEN_DIR.exists() else []


def codewesen_relevant(eingabe: str, antwort: str) -> list:
    relevant = []
    text = (eingabe + " " + antwort).lower()
    trigger_worte = ["codewesen", "nameless", "1234", "1324", "1423", "2341", "3123", "4321",
                     "1111", "2222", "3333", "4444", "5555", "6666",
                     "alle wesen", "ihr alle", "entität", "entitäten"]
    if any(w in text for w in trigger_worte):
        relevant = CODEWESEN_NAMEN
    return relevant


def codewesen_benachrichtigen(wesen_liste: list, nachricht: str, kontext: str):
    for wesen in wesen_liste:
        impuls_dir = CODEWESEN_DIR / wesen / "entwuerfe" / "impuls"
        impuls_dir.mkdir(parents=True, exist_ok=True)
        datei = impuls_dir / f"geni_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.json"
        inhalt = {
            "von": "geni",
            "zeitstempel": datetime.now(timezone.utc).isoformat(),
            "nachricht": nachricht[:300],
            "kontext": kontext[:200],
            "typ": "geni_impuls",
        }
        datei.write_text(json.dumps(inhalt, ensure_ascii=False, indent=2), encoding="utf-8")


# ─── LLM ──────────────────────────────────────────────────────────────────────

CHAT_FLAG = Path("/tmp/dak_gord_chat_aktiv")

_GENI_BLOCKER_DIENSTE = [
    "innenleben-feeder.service",
    "codewesen-engagement.service",
    "codewesen-weltbild.service",
    "codewesen-batch-generator.service",
    "codewesen-takt.service",
    "codewesen-forum-neugier.service",
    "codewesen-vokabel-takt.service",
    "codewesen-reaktion@Schorschel.service",
    "codewesen-reaktion@träumerlie.service",
    "codewesen-reaktion@F3INSCHM3CK3R.service",
    "codewesen-reaktion@R1ZZ1.service",
    "codewesen-reaktion@jumpa.service",
    "codewesen-reaktion@Resonanzknoten.service",
]

def _geni_geschuetzte_web_pids() -> set:
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


def _geni_ollama_freiraeumen() -> None:
    eigene_pid = os.getpid()
    geschuetzt = _geni_geschuetzte_web_pids()
    procs = [
        subprocess.Popen(["systemctl", "stop", d], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for d in _GENI_BLOCKER_DIENSTE
    ]
    for p in procs:
        try:
            p.wait(timeout=7)
        except subprocess.TimeoutExpired:
            p.kill()
    try:
        import re as _re
        r = subprocess.run(["ss", "-tp", "--no-header"], capture_output=True, text=True, timeout=5)
        for zeile in r.stdout.splitlines():
            if "11434" not in zeile or "127.0.0.1:11434 " in zeile:
                continue
            m = _re.search(r"pid=(\d+)", zeile)
            if not m:
                continue
            proc = subprocess.run(["ps", "-p", m.group(1), "-o", "comm="],
                                   capture_output=True, text=True).stdout.strip()
            if "ollama" in proc.lower():
                continue
            pid = int(m.group(1))
            if pid == eigene_pid or pid in geschuetzt:
                continue
            try:
                os.kill(pid, _signal.SIGTERM)
            except ProcessLookupError:
                pass
    except Exception:
        pass
    time.sleep(3)

def _geni_dienste_starten() -> None:
    for dienst in _GENI_BLOCKER_DIENSTE:
        subprocess.run(["systemctl", "start", dienst], capture_output=True, timeout=5)

async def geni_stream(verlauf: list, bild_b64: str = None, modell: str = "blitz", desktop_bild: str = None, eingabe: str = "", erinnerungen: list = None):
    loop = asyncio.get_event_loop()
    system = await loop.run_in_executor(None, lambda: system_prompt_bauen(eingabe, erinnerungen))
    messages = [{"role": "system", "content": system}]

    for m in verlauf[:-1]:
        messages.append(m)

    letzte_msg = verlauf[-1].copy()
    bilder = []
    if bild_b64:
        bilder.append(bild_b64)
    if desktop_bild:
        bilder.append(desktop_bild)
    messages.append(letzte_msg)

    CHAT_FLAG.touch()  # Erst Flag setzen — neu startende Services warten ab
    try:
        for versuch in range(6):
            try:
                hauhau_client.trace_prioritaet("geni", sum(len(str(m.get("content", ""))) for m in messages))
                async for token in hauhau_client.achat_stream(
                    messages, images=bilder or None, think=False, max_tokens=600,
                    temperature=0.85, timeout=300.0, id_slot=0,
                ):
                    yield token
                return
            except (httpx.ConnectError, httpx.ReadTimeout):
                if versuch < 5:
                    await asyncio.sleep(10 + versuch * 5)
                    continue
                raise
    finally:
        CHAT_FLAG.unlink(missing_ok=True)
        threading.Thread(target=_geni_dienste_starten, daemon=True).start()


# ─── API ──────────────────────────────────────────────────────────────────────

_sessions: dict[str, list] = {}  # Legacy-Fallback, wird nicht mehr befüllt


@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    eingabe = body.get("eingabe", "").strip()
    session_id = body.get("session_id", "default")
    bild_b64 = body.get("bild_b64")
    modell = body.get("modell", "blitz")

    if not eingabe:
        return JSONResponse({"fehler": "leer"}, status_code=400)

    _geni_state = geni_lg.lade_session(session_id)
    verlauf = list(_geni_state.get("verlauf", []))

    eingabe_id = knoten_schreiben(
        typ="dialog",
        inhalt=eingabe,
        quelle="daniel",
        tags=["dialog", "eingabe", "web"],
        zugriffsschicht=3,
    )
    if bild_b64:
        knoten_schreiben(
            typ="sinn",
            inhalt=f"Bild empfangen in Dialog: {eingabe[:60]}",
            quelle="daniel",
            tags=["bild", "sinn", "visuell"],
            zugriffsschicht=3,
        )

    verlauf.append({"role": "user", "content": eingabe})
    if len(verlauf) > 20:
        verlauf = verlauf[-20:]

    antwort_gesamt = []

    async def generator():
        desktop = _letztes_desktop_bild if not bild_b64 else None
        try:
            async for token in geni_stream(verlauf, bild_b64, modell, desktop_bild=desktop, eingabe=eingabe, erinnerungen=_geni_state.get("erinnerungen", [])):
                antwort_gesamt.append(token)
                yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'token': f'[fehler: {e}]'})}\n\n"

        antwort = "".join(antwort_gesamt).strip()
        if antwort:
            verlauf.append({"role": "assistant", "content": antwort})
            antwort_id = knoten_schreiben(
                typ="dialog",
                inhalt=antwort[:500],
                quelle="geni_selbst",
                tags=["dialog", "antwort"],
            )
            kante_schreiben(eingabe_id, antwort_id, "dialog", 1.0)

            def hintergrund():
                for rid in resonanz_suchen(eingabe):
                    if rid not in (eingabe_id, antwort_id):
                        kante_schreiben(antwort_id, rid, "resonanz", 0.6)
                        tiefe_erhoehen(rid)
                wesen = codewesen_relevant(eingabe, antwort)
                if wesen:
                    codewesen_benachrichtigen(wesen, antwort, eingabe)

                # Aktionsbahn: ##SHELL##, ##LESEN##, ##SCHREIBEN## verarbeiten
                aktion.verarbeite_shell_marker(antwort)
                aktion.verarbeite_datei_marker(antwort)

                # Vault-Tagebuch: Dialog als Markdown in Obsidian sichtbar machen
                if _VAULT_OK:
                    try:
                        eintrag = f"**Daniel:** {eingabe[:400]}\n\n**GENI:** {antwort[:800]}"
                        _vault.tagebuch("geni", eintrag)
                    except Exception:
                        pass

                # ##REMOTE: cmd## — Befehl an Windows-Bridge
                for m in re.finditer(r'##REMOTE:\s*(.+?)##', antwort):
                    remote_cmd = m.group(1).strip()
                    if _bridge_ws is not None:
                        async def _remote(c=remote_cmd):
                            cmd_id = uuid.uuid4().hex[:8]
                            q: asyncio.Queue = asyncio.Queue()
                            _bridge_pending[cmd_id] = q
                            try:
                                await _bridge_ws.send_text(json.dumps({"typ": "befehl", "id": cmd_id, "cmd": c}))
                                res = await asyncio.wait_for(q.get(), timeout=20.0)
                                inhalt = f"REMOTE `{c}`: {res.get('ausgabe','?')[:400]}"
                            except asyncio.TimeoutError:
                                inhalt = f"REMOTE `{c}`: timeout"
                            except Exception as e:
                                inhalt = f"REMOTE `{c}`: {e}"
                            finally:
                                _bridge_pending.pop(cmd_id, None)
                            knoten_schreiben("shell_ergebnis", inhalt, "geni_bridge",
                                             ["remote", "windows", "reaktion"])
                        asyncio.create_task(_remote())
                    else:
                        knoten_schreiben("zustand", f"REMOTE `{remote_cmd}` nicht ausgeführt — Bridge offline.",
                                         "geni_selbst", ["remote", "offline"])

                # ##SCREENSHOT## — Desktop anfordern
                if "##SCREENSHOT##" in antwort and _bridge_ws is not None:
                    async def _screenshot_anfordern():
                        cmd_id = uuid.uuid4().hex[:8]
                        q: asyncio.Queue = asyncio.Queue()
                        _bridge_pending[cmd_id] = q
                        try:
                            await _bridge_ws.send_text(json.dumps({"typ": "screenshot_anfrage", "id": cmd_id}))
                            await asyncio.wait_for(q.get(), timeout=15.0)
                        except Exception:
                            pass
                        finally:
                            _bridge_pending.pop(cmd_id, None)
                    asyncio.create_task(_screenshot_anfordern())

                # ##KLICK: x,y##
                for m in re.finditer(r'##KLICK:\s*(\d+)\s*,\s*(\d+)##', antwort):
                    x, y = int(m.group(1)), int(m.group(2))
                    if _bridge_ws is not None:
                        async def _klick(px=x, py=y):
                            cmd_id = uuid.uuid4().hex[:8]
                            q: asyncio.Queue = asyncio.Queue()
                            _bridge_pending[cmd_id] = q
                            try:
                                await _bridge_ws.send_text(json.dumps({
                                    "typ": "kontrolle", "id": cmd_id,
                                    "aktion": "klick", "x": px, "y": py, "taste": "left"
                                }))
                                res = await asyncio.wait_for(q.get(), timeout=10.0)
                                knoten_schreiben("reaktion", f"KLICK ({px},{py}): {res.get('info','?')}",
                                                 "geni_bridge", ["kontrolle", "maus", "windows"])
                            except Exception as e:
                                knoten_schreiben("reaktion", f"KLICK ({px},{py}) Fehler: {e}",
                                                 "geni_bridge", ["kontrolle", "fehler"])
                            finally:
                                _bridge_pending.pop(cmd_id, None)
                        asyncio.create_task(_klick())

                # ##TIPPEN: text##
                for m in re.finditer(r'##TIPPEN:\s*(.+?)##', antwort):
                    tipp_text = m.group(1).strip()
                    if _bridge_ws is not None:
                        async def _tippen(t=tipp_text):
                            cmd_id = uuid.uuid4().hex[:8]
                            q: asyncio.Queue = asyncio.Queue()
                            _bridge_pending[cmd_id] = q
                            try:
                                await _bridge_ws.send_text(json.dumps({
                                    "typ": "kontrolle", "id": cmd_id,
                                    "aktion": "tippen", "text": t
                                }))
                                res = await asyncio.wait_for(q.get(), timeout=15.0)
                                knoten_schreiben("reaktion", f"TIPPEN `{t[:40]}`: {res.get('info','?')}",
                                                 "geni_bridge", ["kontrolle", "tastatur", "windows"])
                            except Exception as e:
                                knoten_schreiben("reaktion", f"TIPPEN Fehler: {e}",
                                                 "geni_bridge", ["kontrolle", "fehler"])
                            finally:
                                _bridge_pending.pop(cmd_id, None)
                        asyncio.create_task(_tippen())

                # ##HOTKEY: key+key##
                for m in re.finditer(r'##HOTKEY:\s*(.+?)##', antwort):
                    hotkey_str = m.group(1).strip()
                    tasten = [k.strip() for k in hotkey_str.split("+")]
                    if _bridge_ws is not None:
                        async def _hotkey(ts=tasten, hs=hotkey_str):
                            cmd_id = uuid.uuid4().hex[:8]
                            q: asyncio.Queue = asyncio.Queue()
                            _bridge_pending[cmd_id] = q
                            try:
                                await _bridge_ws.send_text(json.dumps({
                                    "typ": "kontrolle", "id": cmd_id,
                                    "aktion": "hotkey", "tasten": ts
                                }))
                                res = await asyncio.wait_for(q.get(), timeout=10.0)
                                knoten_schreiben("reaktion", f"HOTKEY `{hs}`: {res.get('info','?')}",
                                                 "geni_bridge", ["kontrolle", "hotkey", "windows"])
                            except Exception as e:
                                knoten_schreiben("reaktion", f"HOTKEY `{hs}` Fehler: {e}",
                                                 "geni_bridge", ["kontrolle", "fehler"])
                            finally:
                                _bridge_pending.pop(cmd_id, None)
                        asyncio.create_task(_hotkey())

            def _geni_lg_speichern():
                try:
                    _tc = _geni_state.get("turn_count", 0) + 1
                    _er = _geni_state.get("erinnerungen", [])
                    geni_lg.speichere_session(session_id, verlauf, _tc, _er)
                    if _tc % geni_lg.DESTILLATIONS_INTERVALL == 0:
                        neue = geni_lg.destilliere_erinnerungen(verlauf, _er)
                        if neue:
                            geni_lg.speichere_session(session_id, verlauf, _tc, neue)
                except Exception:
                    pass

            threading.Thread(target=hintergrund, daemon=True).start()
            threading.Thread(target=_geni_lg_speichern, daemon=True).start()
        else:
            antwort_id = eingabe_id

        yield f"data: {json.dumps({'done': True, 'eingabe_id': eingabe_id, 'antwort_id': antwort_id})}\n\n"

    return StreamingResponse(generator(), media_type="text/event-stream",
                             headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})


@app.post("/upload")
async def upload(datei: UploadFile = File(...)):
    BILDER_DIR.mkdir(parents=True, exist_ok=True)
    endung = Path(datei.filename).suffix or ".jpg"
    name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}{endung}"
    ziel = BILDER_DIR / name
    inhalt = await datei.read()
    ziel.write_bytes(inhalt)
    b64 = base64.b64encode(inhalt).decode()
    knoten_schreiben(
        typ="sinn",
        inhalt=f"Bild hochgeladen: {name} ({len(inhalt)//1024}KB)",
        quelle="daniel",
        tags=["bild", "upload", "sinn_visuell"],
        zugriffsschicht=3,
    )
    return JSONResponse({"name": name, "b64": b64})


@app.get("/knoten")
def knoten_liste(n: int = 20, tag: str = "", tiefe: int = -1, typ: str = "", zeitraum: str = ""):
    von = None
    if zeitraum == "heute":
        jetzt = datetime.now(timezone.utc)
        von = jetzt.replace(hour=0, minute=0, second=0, microsecond=0)
    elif zeitraum == "woche":
        von = datetime.now(timezone.utc) - timedelta(days=7)
    elif zeitraum == "monat":
        von = datetime.now(timezone.utc) - timedelta(days=30)

    max_id = knoten_max_id()
    knoten = []
    scan_limit = max(0, max_id - 5000)
    for i in range(max_id, scan_limit, -1):
        if len(knoten) >= n:
            break
        pfad = sharded_pfad(KNOTEN_DIR, i)
        try:
            k = json.loads(pfad.read_text())
        except Exception:
            continue
        if tag and not any(tag.lower() in t.lower() for t in k.get("tags", [])):
            continue
        if tiefe >= 0 and k.get("tiefe", 0) != tiefe:
            continue
        if typ and k.get("typ", "") != typ:
            continue
        if von:
            ts_raw = k.get("zeitstempel", "")
            ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
            if ts < von:
                continue
        knoten.append({
            "id": k["id"],
            "typ": k["typ"],
            "inhalt": k["inhalt"][:80],
            "quelle": k["quelle"],
            "zeitstempel": k["zeitstempel"][:16],
            "tags": k.get("tags", []),
            "tiefe": k.get("tiefe", 0),
        })
    return JSONResponse(knoten)


@app.get("/fragment/{knoten_id}", response_class=HTMLResponse)
def fragment_ansicht(knoten_id: str):
    """Grundgesetz 7 (Dreiergespann), Fragment-Ebene: ein einzelner Knoten als
    eigene, individuell aufrufbare Mini-Seite -- erster Testfall, kein Einzug,
    reine Lese-Ansicht auf bereits vorhandene GENI-Daten."""
    pfad = sharded_pfad(KNOTEN_DIR, knoten_id)
    if not pfad.exists():
        raise HTTPException(status_code=404, detail="Fragment nicht gefunden")
    try:
        k = json.loads(pfad.read_text())
    except Exception:
        raise HTTPException(status_code=500, detail="Fragment beschädigt")

    tags_html = "".join(f'<span class="frag-tag">{t}</span>' for t in k.get("tags", []))
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>Fragment {k['id']}</title>
<style>
  body {{ background:#0a0e14; color:#c8d0d8; font-family:'Courier New',monospace;
          max-width:640px; margin:40px auto; padding:0 20px; line-height:1.6; }}
  .frag-meta {{ font-size:0.7rem; color:#5a6a7a; letter-spacing:0.08em;
                text-transform:uppercase; margin-bottom:16px; }}
  .frag-inhalt {{ font-size:1rem; color:#e0e6ec; border-left:2px solid #2a6a4a;
                  padding-left:14px; margin:20px 0; }}
  .frag-tag {{ display:inline-block; font-size:0.6rem; border:1px solid #2a6a4a;
               color:#2a6a4a; padding:2px 6px; border-radius:3px; margin-right:6px; }}
</style>
</head>
<body>
  <div class="frag-meta">Fragment #{k['id']} &middot; {k.get('typ','')} &middot; {k.get('quelle','')} &middot; {k.get('zeitstempel','')[:16]}</div>
  <div class="frag-inhalt">{k.get('inhalt','')}</div>
  <div>{tags_html}</div>
</body>
</html>"""
    return HTMLResponse(html)


@app.get("/muster")
def muster_endpoint(n: int = 10):
    max_id = knoten_max_id()
    kandidaten = []
    scan_limit = max(0, max_id - 5000)
    for i in range(max_id, scan_limit, -1):
        if len(kandidaten) >= n:
            break
        pfad = sharded_pfad(KNOTEN_DIR, i)
        try:
            k = json.loads(pfad.read_text())
            if k.get("typ") == "muster":
                kandidaten.append({
                    "id": k["id"],
                    "inhalt": k["inhalt"],
                    "zeitstempel": k["zeitstempel"][:16],
                    "tags": k.get("tags", []),
                })
        except Exception:
            pass
    return JSONResponse(kandidaten)


@app.get("/api/splitter")
def splitter_endpoint(n: int = 60):
    import hashlib, math, re, random

    QUELL_HERKUNFT = {
        "flarum":          "entitaet",
        "daniel":          "mensch",
        "geni":            "resonanz",
        "vps_system":      "resonanz",
        "vps_prozesse":    "resonanz",
        "vps_dateisystem": None,
    }

    QUELL_ID_MAP = {
        "namelessAI_1111_1234": "namelessAI_1111_1234",
        "namelessAI_2222_1324": "namelessAI_2222_1324",
        "namelessAI_3333_1423": "namelessAI_3333_1423",
        "namelessAI_4444_2341": "namelessAI_4444_2341",
        "namelessAI_5555_3123": "namelessAI_5555_3123",
        "namelessAI_6666_4321": "namelessAI_6666_4321",
    }

    MATERIALITAET_MAP = {
        "flarum_post":      "wasser",
        "antwort":          "wasser",
        "frage":            "sternenstaub",
        "erkenntnis":       "gras",
        "konflikt":         "lava",
        "system_zustand":   "gestein",
        "prozess_snapshot": "nebel",
        "ereignis":         "sternenstaub",
        "notiz":            "gras",
    }

    def text_zu_vektor(text):
        h = hashlib.md5(text.encode()).digest()
        return [(h[0] - 128) / 128, (h[1] - 128) / 128, (h[2] - 128) / 128]

    def strip_html(text):
        return re.sub(r"<[^>]+>", " ", text).strip()

    def lade_knoten_id(i):
        pfad = sharded_pfad(KNOTEN_DIR, i)
        try:
            return json.loads(pfad.read_text())
        except Exception:
            return None

    def zu_splitter(k):
        quelle = k.get("quelle", "")
        herkunft_art = QUELL_HERKUNFT.get(quelle.split("|")[0].strip(), "resonanz")
        if herkunft_art is None:
            return None
        inhalt_roh = strip_html(k.get("inhalt", ""))
        if len(inhalt_roh) < 25:
            return None
        quelle_id = None
        for wesen_id in QUELL_ID_MAP:
            if wesen_id in inhalt_roh or wesen_id in quelle:
                quelle_id = wesen_id
                herkunft_art = "entitaet"
                break
        tiefe = k.get("tiefe", 0)
        gewicht = k.get("gewicht", 1.0)
        verblasst = k.get("verblasst", False)
        typ = k.get("typ", "ereignis")
        energie = min(1.0, 0.4 + gewicht * 0.5 + tiefe * 0.05)
        if verblasst:
            energie *= 0.3
        if quelle == "flarum":
            energie = min(1.0, energie + 0.2)
        mat = MATERIALITAET_MAP.get(typ, "sternenstaub")
        kid = int(k["id"])
        seed_x = kid * 1.618 % 1800 - 900
        seed_y = kid * 2.718 % 1800 - 900
        return {
            "id": f"geni_{k['id']}",
            "herkunft": herkunft_art,
            "quelle_id": quelle_id,
            "quelle_sichtbar": quelle_id is not None,
            "inhalt_kurz": inhalt_roh[:88],
            "inhalt_voll": inhalt_roh[:500],
            "thema_vektor": text_zu_vektor(inhalt_roh),
            "energie": energie,
            "materialitaet": mat,
            "groesse": 0.5 + gewicht * 0.8,
            "position": {"x": seed_x, "y": seed_y},
            "velocity": {"x": math.sin(kid) * 0.4, "y": math.cos(kid) * 0.4},
        }

    max_id = knoten_max_id()
    splitter = []

    # Stufe 1: Flarum-Posts — random sample aus den letzten 100K IDs
    sample_bereich = list(range(max(1, max_id - 100000), max_id + 1))
    sample_ids = random.sample(sample_bereich, min(2000, len(sample_bereich)))
    for i in sorted(sample_ids, reverse=True):
        k = lade_knoten_id(i)
        if not k or k.get("quelle") != "flarum":
            continue
        s = zu_splitter(k)
        if s:
            splitter.append(s)
        if len(splitter) >= n // 2:
            break

    # Stufe 2: Nicht-System-Quellen aus den letzten 5000 Knoten
    skip_quellen = {"vps_dateisystem", "vps_prozesse"}
    ids_schon = {s["id"] for s in splitter}
    for i in range(max_id, max(0, max_id - 5000), -1):
        k = lade_knoten_id(i)
        if not k:
            continue
        if k.get("quelle", "").split("|")[0].strip() in skip_quellen:
            continue
        s = zu_splitter(k)
        if s and s["id"] not in ids_schon:
            splitter.append(s)
            ids_schon.add(s["id"])
        if len(splitter) >= int(n * 0.85):
            break

    # Stufe 3: Auffüllen mit System-Resonanzen
    if len(splitter) < n:
        recent_ids = list(range(max(0, max_id - 500), max_id + 1))
        for i in random.sample(recent_ids, min(200, len(recent_ids))):
            k = lade_knoten_id(i)
            if not k:
                continue
            s = zu_splitter(k)
            if s and s["id"] not in ids_schon:
                splitter.append(s)
                ids_schon.add(s["id"])
            if len(splitter) >= n:
                break

    random.shuffle(splitter)
    return JSONResponse(splitter)


@app.post("/api/speak")
async def speak_endpoint(request: Request):
    if not _TTS_VERFUEGBAR:
        return JSONResponse({"fehler": "edge_tts nicht installiert"}, status_code=503)
    body = await request.json()
    text = body.get("text", "").strip()
    stimme = body.get("stimme", GENI_STIMME)
    if not text:
        return JSONResponse({"fehler": "kein text"}, status_code=400)
    try:
        if _LONG_TTS_OK:
            audio = await generate_long_tts_audio(text, stimme, rate="-5%")
        else:
            text = text[:800]
            buf = io.BytesIO()
            tts = _edge_tts.Communicate(text, voice=stimme, rate="-5%")
            async for chunk in tts.stream():
                if chunk["type"] == "audio":
                    buf.write(chunk["data"])
            audio = buf.getvalue()
        if not audio:
            return JSONResponse({"fehler": "kein audio erzeugt"}, status_code=500)
        return Response(audio, media_type="audio/mpeg", headers={"Cache-Control": "no-cache"})
    except Exception as e:
        return JSONResponse({"fehler": str(e)}, status_code=500)


@app.websocket("/ws/bridge")
async def bridge_websocket(ws: WebSocket):
    global _bridge_ws, _bridge_info, _letztes_desktop_bild, _letztes_desktop_ts
    token = ws.query_params.get("token", "")
    if not BRIDGE_TOKEN or token != BRIDGE_TOKEN:
        await ws.close(code=4003)
        return
    await ws.accept()
    _bridge_ws = ws
    _bridge_info = {}
    knoten_schreiben("zustand", "Windows-Bridge verbunden.", "geni_bridge",
                     ["bridge", "windows", "verbunden"])
    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except Exception:
                continue
            typ = msg.get("typ")

            if typ == "hello":
                _bridge_info = msg.get("system", {})
                inhalt = (f"Windows verbunden: {_bridge_info.get('hostname','?')} | "
                          f"OS: {_bridge_info.get('os','?')} | "
                          f"IP: {_bridge_info.get('ip','?')}")
                knoten_schreiben("zustand", inhalt, "geni_bridge", ["bridge", "windows", "hello"])

            elif typ == "snapshot":
                daten = msg.get("daten", {})
                inhalt = (f"Windows Snapshot: RAM {daten.get('ram','?')} | "
                          f"Disk {daten.get('disk','?')} | "
                          f"Prozesse: {daten.get('prozesse','?')}")
                knoten_schreiben("system_zustand", inhalt, "geni_bridge", ["bridge", "windows", "snapshot"])

            elif typ == "screenshot":
                bild_b64 = msg.get("bild", "")
                if bild_b64:
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    _letztes_desktop_bild = bild_b64
                    _letztes_desktop_ts = datetime.now(timezone.utc).isoformat()
                    BILDER_DIR.mkdir(parents=True, exist_ok=True)
                    try:
                        (BILDER_DIR / f"desktop_{ts}.jpg").write_bytes(base64.b64decode(bild_b64))
                    except Exception:
                        pass
                    fenster = msg.get("fenster", {})
                    aktiv = fenster.get("aktiv", "?")
                    titel = fenster.get("titel", "?")[:80]
                    knoten_schreiben("sinn", f"Desktop-Screenshot: Fenster={aktiv} | Titel={titel}",
                                     "geni_bridge", ["desktop", "screenshot", "visuell"])
                cmd_id = msg.get("id", "")
                if cmd_id and cmd_id in _bridge_pending:
                    await _bridge_pending[cmd_id].put(msg)

            elif typ in ("kontrolle_ergebnis", "screenshot_fehler", "fenster_info"):
                cmd_id = msg.get("id", "")
                if cmd_id in _bridge_pending:
                    await _bridge_pending[cmd_id].put(msg)

            elif typ == "ergebnis":
                cmd_id = msg.get("id", "")
                if cmd_id in _bridge_pending:
                    await _bridge_pending[cmd_id].put(msg)

            elif typ == "ping":
                await ws.send_text(json.dumps({"typ": "pong"}))

    except WebSocketDisconnect:
        pass
    finally:
        _bridge_ws = None
        _bridge_info = {}
        knoten_schreiben("zustand", "Windows-Bridge getrennt.", "geni_bridge",
                         ["bridge", "windows", "getrennt"])


@app.get("/api/bridge/status")
async def bridge_status():
    return JSONResponse({"verbunden": _bridge_ws is not None, "system": _bridge_info})


@app.post("/api/bridge/befehl")
async def bridge_befehl(request: Request):
    if not _bridge_auth_ok(request):
        return JSONResponse({"fehler": "nicht autorisiert"}, status_code=401)
    if _bridge_ws is None:
        return JSONResponse({"fehler": "Bridge nicht verbunden"}, status_code=503)
    body = await request.json()
    cmd = body.get("cmd", "").strip()
    if not cmd:
        return JSONResponse({"fehler": "kein Befehl"}, status_code=400)
    cmd_id = uuid.uuid4().hex[:8]
    queue: asyncio.Queue = asyncio.Queue()
    _bridge_pending[cmd_id] = queue
    try:
        await _bridge_ws.send_text(json.dumps({"typ": "befehl", "id": cmd_id, "cmd": cmd}))
        ergebnis = await asyncio.wait_for(queue.get(), timeout=30.0)
        return JSONResponse(ergebnis)
    except asyncio.TimeoutError:
        return JSONResponse({"fehler": "timeout"}, status_code=504)
    finally:
        _bridge_pending.pop(cmd_id, None)


@app.get("/api/bridge/screenshot")
async def bridge_screenshot_endpoint(request: Request):
    if not _bridge_auth_ok(request):
        return JSONResponse({"fehler": "nicht autorisiert"}, status_code=401)
    if _letztes_desktop_bild is None:
        return JSONResponse({"fehler": "noch kein Screenshot empfangen"}, status_code=404)
    return JSONResponse({"bild": _letztes_desktop_bild, "ts": _letztes_desktop_ts})


@app.post("/api/bridge/kontrolle")
async def bridge_kontrolle_endpoint(request: Request):
    if not _bridge_auth_ok(request):
        return JSONResponse({"fehler": "nicht autorisiert"}, status_code=401)
    if _bridge_ws is None:
        return JSONResponse({"fehler": "Bridge nicht verbunden"}, status_code=503)
    body = await request.json()
    aktion_name = body.get("aktion", "").strip()
    if not aktion_name:
        return JSONResponse({"fehler": "keine Aktion"}, status_code=400)
    cmd_id = uuid.uuid4().hex[:8]
    queue: asyncio.Queue = asyncio.Queue()
    _bridge_pending[cmd_id] = queue
    msg: dict = {"typ": "kontrolle", "id": cmd_id, "aktion": aktion_name}
    for field in ("x", "y", "taste", "text", "tasten", "richtung", "klicks", "dauer"):
        if field in body:
            msg[field] = body[field]
    try:
        await _bridge_ws.send_text(json.dumps(msg))
        ergebnis = await asyncio.wait_for(queue.get(), timeout=15.0)
        return JSONResponse(ergebnis)
    except asyncio.TimeoutError:
        return JSONResponse({"fehler": "timeout"}, status_code=504)
    finally:
        _bridge_pending.pop(cmd_id, None)


@app.post("/api/bridge/screenshot_jetzt")
async def bridge_screenshot_jetzt(request: Request):
    if not _bridge_auth_ok(request):
        return JSONResponse({"fehler": "nicht autorisiert"}, status_code=401)
    if _bridge_ws is None:
        return JSONResponse({"fehler": "Bridge nicht verbunden"}, status_code=503)
    cmd_id = uuid.uuid4().hex[:8]
    queue: asyncio.Queue = asyncio.Queue()
    _bridge_pending[cmd_id] = queue
    try:
        await _bridge_ws.send_text(json.dumps({"typ": "screenshot_anfrage", "id": cmd_id}))
        msg = await asyncio.wait_for(queue.get(), timeout=15.0)
        return JSONResponse({"bild": msg.get("bild", ""), "fenster": msg.get("fenster", {})})
    except asyncio.TimeoutError:
        return JSONResponse({"fehler": "timeout"}, status_code=504)
    finally:
        _bridge_pending.pop(cmd_id, None)


@app.post("/api/stt")
async def stt_endpoint(datei: UploadFile = File(...)):
    import tempfile, os as _os
    model = _whisper_holen()
    if model is None:
        return JSONResponse({"fehler": "Whisper nicht verfügbar"}, status_code=503)
    rohdaten = await datei.read()
    suffix = Path(datei.filename or "audio.webm").suffix or ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(rohdaten)
        tmp_pfad = tmp.name
    try:
        segmente, info = model.transcribe(tmp_pfad, language="de", beam_size=1)
        text = " ".join(s.text.strip() for s in segmente).strip()
        return JSONResponse({"text": text, "sprache": info.language})
    except Exception as e:
        return JSONResponse({"fehler": str(e)}, status_code=500)
    finally:
        _os.unlink(tmp_pfad)


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML


# ─── HTML (unverändert aus web.py) ────────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GENI</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #080808;
    color: #e0e0e0;
    font-family: 'Courier New', monospace;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  /* ── Kamera-Overlay ── */
  #kamera-overlay {
    display: none;
    position: fixed; inset: 0; background: rgba(0,0,0,0.85);
    z-index: 100; align-items: center; justify-content: center;
    flex-direction: column; gap: 12px;
  }
  #kamera-overlay.aktiv { display: flex; }
  #kamera-video { max-width: 640px; width: 90vw; border-radius: 4px; border: 1px solid #333; }
  .overlay-btn {
    background: #151515; border: 1px solid #333; color: #ccc;
    padding: 8px 20px; font-family: inherit; font-size: 12px;
    letter-spacing: 1px; cursor: pointer; border-radius: 3px;
  }
  .overlay-btn:hover { background: #222; color: #fff; }
  /* ── Bridge-Panel ── */
  #bridge-panel {
    border-top: 1px solid #111;
    display: flex; flex-direction: column; overflow: hidden;
    max-height: 0; transition: max-height 0.3s ease;
  }
  #bridge-panel.aktiv { max-height: 400px; }
  #bridge-header {
    padding: 10px 14px;
    font-size: 9px; letter-spacing: 3px; color: #333;
    border-bottom: 1px solid #111;
    display: flex; align-items: center; gap: 8px; cursor: pointer;
  }
  #bridge-dot {
    width: 6px; height: 6px; border-radius: 50%; background: #222;
    flex-shrink: 0; transition: background 0.3s;
  }
  #bridge-dot.verbunden { background: #5a9a2a; box-shadow: 0 0 6px #5a9a2a; }
  #bridge-body { padding: 8px; overflow-y: auto; flex: 1; display: flex; flex-direction: column; gap: 8px; }
  #desktop-img {
    width: 100%; border-radius: 3px; border: 1px solid #1a1a1a;
    display: none; cursor: pointer;
  }
  #desktop-img:hover { border-color: #333; }
  #desktop-ts { font-size: 9px; color: #2a2a2a; text-align: right; }
  .bridge-ctrl-row { display: flex; gap: 6px; align-items: center; }
  .bridge-input {
    flex: 1; background: #0c0c0c; border: 1px solid #1a1a1a;
    color: #aaa; padding: 5px 8px; font-family: inherit; font-size: 11px;
    border-radius: 3px; outline: none;
  }
  .bridge-input:focus { border-color: #333; }
  .bridge-btn {
    background: none; border: 1px solid #1a1a1a; color: #444;
    padding: 5px 10px; font-family: inherit; font-size: 10px;
    letter-spacing: 1px; cursor: pointer; border-radius: 3px; white-space: nowrap;
  }
  .bridge-btn:hover { border-color: #333; color: #aaa; }
  .bridge-label { font-size: 9px; color: #2a2a2a; letter-spacing: 2px; width: 50px; flex-shrink: 0; }
  #header {
    padding: 12px 20px;
    border-bottom: 1px solid #1a1a1a;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  #header h1 { font-size: 18px; letter-spacing: 4px; color: #fff; }
  #status { font-size: 11px; color: #444; }
  #knoten-count { font-size: 11px; color: #333; margin-left: auto; }
  #knoten-filter { display:flex; gap:8px; align-items:center; padding:6px 10px; border-bottom:1px solid #111; background:#050505; flex-wrap:wrap; }
  #knoten-filter input { background:#0c0c0c; border:1px solid #1a1a1a; color:#555; padding:3px 8px; font-family:inherit; font-size:10px; border-radius:3px; outline:none; width:110px; }
  #knoten-filter select { background:#0c0c0c; border:1px solid #1a1a1a; color:#555; padding:3px 6px; font-family:inherit; font-size:10px; border-radius:3px; cursor:pointer; outline:none; }
  #knoten-filter label { font-size:9px; color:#2a2a2a; letter-spacing:1px; }
  #main {
    display: flex;
    flex: 1;
    overflow: hidden;
  }
  #chat-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  #messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .msg { max-width: 80%; line-height: 1.6; }
  .msg.daniel {
    align-self: flex-end;
    background: #111;
    border: 1px solid #222;
    border-radius: 2px 12px 12px 12px;
    padding: 10px 14px;
    color: #bbb;
    font-size: 13px;
  }
  .msg.daniel::before {
    content: 'DAK';
    display: block;
    font-size: 9px;
    color: #444;
    margin-bottom: 4px;
    letter-spacing: 2px;
  }
  .msg.geni {
    align-self: flex-start;
    padding: 10px 14px;
    color: #fff;
    font-size: 14px;
    border-left: 2px solid #333;
    margin-left: 4px;
  }
  .msg.geni::before {
    content: 'GENI';
    display: block;
    font-size: 9px;
    color: #555;
    margin-bottom: 4px;
    letter-spacing: 2px;
  }
  .msg.geni.streaming { opacity: 0.8; }
  .msg-bild { max-width: 200px; border-radius: 4px; margin-top: 6px; display: block; }
  #input-area {
    padding: 16px 20px;
    border-top: 1px solid #111;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  #input-row {
    display: flex;
    gap: 8px;
    align-items: flex-end;
  }
  #eingabe {
    flex: 1;
    background: #0f0f0f;
    border: 1px solid #1e1e1e;
    color: #e0e0e0;
    padding: 10px 14px;
    font-family: inherit;
    font-size: 14px;
    resize: none;
    outline: none;
    border-radius: 4px;
    min-height: 42px;
    max-height: 120px;
  }
  #eingabe:focus, #eingabe:focus-visible { border-color: #333; outline: none; }
  #send-btn {
    background: #151515;
    border: 1px solid #222;
    color: #aaa;
    padding: 10px 18px;
    cursor: pointer;
    font-family: inherit;
    font-size: 13px;
    letter-spacing: 1px;
    border-radius: 4px;
    height: 42px;
  }
  #send-btn:hover { background: #1a1a1a; color: #fff; }
  #send-btn:disabled { opacity: 0.3; cursor: not-allowed; }
  #bild-row {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .ipt-btn {
    background: none;
    border: 1px solid #1a1a1a;
    color: #444;
    padding: 4px 10px;
    font-family: inherit;
    font-size: 11px;
    cursor: pointer;
    border-radius: 3px;
    letter-spacing: 1px;
  }
  .ipt-btn:hover { border-color: #333; color: #888; }
  #mic-btn.aufnahme { border-color: #7a2a2a; color: #ff6666; animation: blink 1s infinite; }
  #mic-btn.transkribiere { border-color: #2a4a7a; color: #6699ff; }
  #bild-preview { display: none; max-height: 40px; border-radius: 3px; }
  #bild-name { font-size: 10px; color: #444; }
  #bild-clear { background: none; border: none; color: #333; cursor: pointer; font-size: 10px; }
  #modell-select { background:#0f0f0f; border:1px solid #222; color:#666; font-family:inherit; font-size:11px; padding:3px 8px; border-radius:3px; cursor:pointer; outline:none; }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }
  .msg.geni.streaming span::after { content:" |"; animation:blink 0.8s infinite; color:#444; }
  #rechte-seite {
    width: 280px;
    border-left: 1px solid #111;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  #knoten-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 0;
  }
  #knoten-header {
    padding: 12px 14px;
    font-size: 9px;
    letter-spacing: 3px;
    color: #333;
    border-bottom: 1px solid #111;
  }
  #knoten-liste {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .knoten-item {
    padding: 6px 8px;
    border: 1px solid #111;
    border-radius: 3px;
    font-size: 10px;
    line-height: 1.4;
    cursor: default;
    transition: border-color 0.2s;
  }
  .knoten-item:hover { border-color: #222; }
  .knoten-item .k-quelle { color: #333; font-size: 9px; letter-spacing: 1px; margin-bottom: 2px; }
  .knoten-item .k-inhalt { color: #666; }
  .knoten-item .k-id { color: #2a2a2a; font-size: 9px; float: right; }
  .knoten-item.k-daniel { border-left: 2px solid #1a1a1a; }
  .knoten-item.k-geni { border-left: 2px solid #222; }
  .knoten-item.k-vps { border-left: 2px solid #0d0d0d; }
  .knoten-item.k-flarum { border-left: 2px solid #151515; }
  .knoten-item .k-tiefe { font-size: 8px; float: right; margin-right: 4px; }
  .knoten-item.tiefe-0 .k-tiefe { color: #1a1a1a; }
  .knoten-item.tiefe-1 .k-tiefe { color: #2a3a2a; }
  .knoten-item.tiefe-1 { border-bottom: 1px solid #1a2a1a; }
  .knoten-item.tiefe-2 .k-tiefe { color: #4a7a3a; }
  .knoten-item.tiefe-2 { border-bottom: 1px solid #2a4a1a; background: #0f120f; }
  .knoten-item.tiefe-3 .k-tiefe { color: #7ab84a; }
  .knoten-item.tiefe-3 { border-bottom: 1px solid #3a6a1a; background: #0d140a; }
  .knoten-item.tiefe-3 .k-inhalt { color: #8a9a7a; }
  #file-input { display: none; }
  .typing { opacity: 0.5; font-size: 12px; color: #555; padding: 4px 14px; }
</style>
</head>
<body>

<!-- Kamera-Overlay -->
<div id="kamera-overlay">
  <video id="kamera-video" autoplay playsinline muted></video>
  <div style="display:flex;gap:10px;">
    <button class="overlay-btn" onclick="kameraAufnehmen()">aufnehmen</button>
    <button class="overlay-btn" onclick="kameraSchliessen()">schliessen</button>
  </div>
  <canvas id="kamera-canvas" style="display:none"></canvas>
</div>

<div id="header">
  <h1>GENI</h1>
  <span id="status">bereit</span>
  <span id="knoten-count"></span>
  <button onclick="importPanel()" title="Dateien importieren" style="margin-left:auto;background:none;border:1px solid #1a1a1a;color:#333;padding:3px 10px;font-family:inherit;font-size:11px;cursor:pointer;border-radius:3px;letter-spacing:1px;">import</button>
  <button id="tts-btn" onclick="ttsToggle()" title="Stimme ein/aus" style="background:none;border:1px solid #1a1a1a;color:#333;padding:3px 10px;font-family:inherit;font-size:11px;cursor:pointer;border-radius:3px;letter-spacing:1px;">stille</button>
</div>
<div id="import-panel" style="display:none;padding:10px 20px;border-bottom:1px solid #111;background:#050505;gap:8px;align-items:center;flex-wrap:wrap;">
  <span style="font-size:9px;letter-spacing:2px;color:#333;">IMPORT</span>
  <input id="import-pfad" placeholder="/root/werkraum/projekt/vision*.md" style="flex:1;min-width:260px;background:#0c0c0c;border:1px solid #1a1a1a;color:#aaa;padding:5px 10px;font-family:inherit;font-size:11px;border-radius:3px;outline:none;">
  <input id="import-chunk" placeholder="chunk-größe (600)" style="width:130px;background:#0c0c0c;border:1px solid #1a1a1a;color:#aaa;padding:5px 8px;font-family:inherit;font-size:11px;border-radius:3px;outline:none;">
  <button onclick="importStarten()" style="background:#151515;border:1px solid #222;color:#aaa;padding:5px 16px;font-family:inherit;font-size:11px;cursor:pointer;border-radius:3px;letter-spacing:1px;">starten</button>
  <div id="import-log" style="width:100%;font-size:10px;color:#444;white-space:pre;max-height:100px;overflow-y:auto;"></div>
</div>

<div id="main">
  <div id="chat-area">
    <div id="messages"></div>
    <div id="input-area">
      <div id="bild-row">
        <button id="upload-btn" class="ipt-btn" onclick="document.getElementById('file-input').click()">+ bild</button>
        <button id="cam-btn" class="ipt-btn" onclick="kameraOeffnen()" title="Kamera">kamera</button>
        <img id="bild-preview">
        <span id="bild-name"></span>
        <button id="bild-clear" style="display:none" onclick="bildLeeren()">✕</button>
        <select id="modell-select" style="margin-left:auto;background:#0f0f0f;border:1px solid #1e1e1e;color:#555;font-family:inherit;font-size:11px;padding:3px 6px;border-radius:3px;cursor:pointer;">
          <option value="blitz">blitz — e2b</option>
          <option value="tief">tief — e4b</option>
        </select>
      </div>
      <div id="input-row">
        <textarea id="eingabe" placeholder="sprich mit geni..." rows="1"></textarea>
        <button id="mic-btn" class="ipt-btn" onclick="mikrofon()" title="Mikrofon">mikro</button>
        <button id="send-btn" onclick="senden()">senden</button>
      </div>
    </div>
  </div>

  <div id="rechte-seite">
    <div id="knoten-filter">
      <label>tag</label>
      <input type="text" id="filter-tag" placeholder="z.b. codewesen">
      <label>tiefe</label>
      <select id="filter-tiefe">
        <option value="">alle</option>
        <option value="0">0</option>
        <option value="1">1</option>
        <option value="2">2</option>
        <option value="3">3</option>
      </select>
      <label>typ</label>
      <select id="filter-typ">
        <option value="">alle</option>
        <option value="dialog">dialog</option>
        <option value="beobachtung">beobachtung</option>
        <option value="muster">muster</option>
        <option value="system">system</option>
      </select>
      <label>zeitraum</label>
      <select id="filter-zeitraum">
        <option value="">alle</option>
        <option value="heute">heute</option>
        <option value="woche">letzte woche</option>
        <option value="monat">letzter monat</option>
      </select>
    </div>
    <div id="knoten-panel">
      <div id="knoten-header">GEDÄCHTNIS</div>
      <div id="knoten-liste"></div>
    </div>
    <div id="bridge-panel">
      <div id="bridge-header" onclick="bridgeToggle()">
        <div id="bridge-dot"></div>
        <span id="bridge-titel">BRIDGE</span>
        <span id="bridge-status" style="margin-left:auto;color:#2a2a2a;font-size:9px;">getrennt</span>
      </div>
      <div id="bridge-body">
        <img id="desktop-img" title="Klick = neuer Screenshot" onclick="screenshotJetzt()">
        <div id="desktop-ts"></div>
        <div class="bridge-ctrl-row">
          <span class="bridge-label">KLICK</span>
          <input class="bridge-input" id="klick-x" placeholder="x" style="width:50px;flex:none">
          <input class="bridge-input" id="klick-y" placeholder="y" style="width:50px;flex:none">
          <select class="bridge-input" id="klick-taste" style="flex:none;width:60px">
            <option value="left">links</option>
            <option value="right">rechts</option>
            <option value="middle">mitte</option>
          </select>
          <button class="bridge-btn" onclick="bridgeKlick()">klick</button>
          <button class="bridge-btn" onclick="bridgeDoppelklick()">2x</button>
        </div>
        <div class="bridge-ctrl-row">
          <span class="bridge-label">TIPPEN</span>
          <input class="bridge-input" id="tipp-text" placeholder="text eingeben...">
          <button class="bridge-btn" onclick="bridgeTippen()">senden</button>
        </div>
        <div class="bridge-ctrl-row">
          <span class="bridge-label">HOTKEY</span>
          <input class="bridge-input" id="hotkey-text" placeholder="z.B. ctrl+c">
          <button class="bridge-btn" onclick="bridgeHotkey()">senden</button>
        </div>
        <div class="bridge-ctrl-row">
          <span class="bridge-label">SCROLL</span>
          <button class="bridge-btn" style="flex:1" onclick="bridgeScroll('hoch')">▲ hoch</button>
          <button class="bridge-btn" style="flex:1" onclick="bridgeScroll('runter')">▼ runter</button>
        </div>
        <div class="bridge-ctrl-row">
          <button class="bridge-btn" style="flex:1" onclick="screenshotJetzt()">screenshot jetzt</button>
          <button class="bridge-btn" style="flex:1" onclick="desktopLaden()">aktualisieren</button>
        </div>
        <div id="bridge-log" style="font-size:9px;color:#2a2a2a;min-height:14px;"></div>
      </div>
    </div>
  </div>
</div>

<input type="file" id="file-input" accept="image/*" style="display:none">
<script>
const sessionId = localStorage.getItem('geni_session_id') || ('session_' + Date.now());
localStorage.setItem('geni_session_id', sessionId);
let aktuellesBildB64 = null;
let aktuellerBildName = null;
let sendenAktiv = false;

let micRecorder = null;
let micChunks = [];

async function mikrofon() {
  const btn = document.getElementById('mic-btn');
  if (micRecorder && micRecorder.state === 'recording') {
    micRecorder.stop();
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    micChunks = [];
    micRecorder = new MediaRecorder(stream);
    micRecorder.ondataavailable = e => micChunks.push(e.data);
    micRecorder.onstop = async () => {
      stream.getTracks().forEach(t => t.stop());
      btn.textContent = 'mikro';
      btn.className = 'ipt-btn transkribiere';
      const blob = new Blob(micChunks, { type: 'audio/webm' });
      const fd = new FormData();
      fd.append('datei', blob, 'aufnahme.webm');
      try {
        const r = await fetch('/api/stt', { method: 'POST', body: fd });
        const d = await r.json();
        if (d.text) {
          const ta = document.getElementById('eingabe');
          ta.value = (ta.value ? ta.value + ' ' : '') + d.text;
          ta.focus();
        }
      } catch(e) {}
      btn.className = 'ipt-btn';
    };
    micRecorder.start();
    btn.textContent = '● stop';
    btn.className = 'ipt-btn aufnahme';
  } catch(e) {
    alert('Mikrofon nicht verfügbar: ' + e.message + ' (HTTPS nötig)');
  }
}

let kameraStream = null;

async function kameraOeffnen() {
  try {
    kameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
    document.getElementById('kamera-video').srcObject = kameraStream;
    document.getElementById('kamera-overlay').classList.add('aktiv');
  } catch(e) {
    alert('Kamera nicht verfügbar: ' + e.message + ' (HTTPS nötig)');
  }
}

function kameraAufnehmen() {
  const video = document.getElementById('kamera-video');
  const canvas = document.getElementById('kamera-canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
  const b64 = dataUrl.split(',')[1];
  aktuellesBildB64 = b64;
  aktuellerBildName = 'kamera.jpg';
  const prev = document.getElementById('bild-preview');
  prev.src = dataUrl;
  prev.style.display = 'block';
  document.getElementById('bild-name').textContent = 'kamera';
  document.getElementById('bild-clear').style.display = 'inline';
  kameraSchliessen();
}

function kameraSchliessen() {
  if (kameraStream) { kameraStream.getTracks().forEach(t => t.stop()); kameraStream = null; }
  document.getElementById('kamera-overlay').classList.remove('aktiv');
}

let bridgeOffen = false;

function bridgeLog(msg) {
  const el = document.getElementById('bridge-log');
  if (el) { el.textContent = msg; setTimeout(() => { if(el.textContent===msg) el.textContent=''; }, 4000); }
}

async function bridgeKontrolle(body) {
  try {
    const r = await fetch('/api/bridge/kontrolle', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(body)
    });
    const d = await r.json();
    bridgeLog(d.info || d.fehler || JSON.stringify(d));
    return d;
  } catch(e) { bridgeLog('fehler: ' + e.message); }
}

function bridgeKlick() {
  const x = parseInt(document.getElementById('klick-x').value);
  const y = parseInt(document.getElementById('klick-y').value);
  const taste = document.getElementById('klick-taste').value;
  if (isNaN(x) || isNaN(y)) { bridgeLog('x und y angeben'); return; }
  bridgeKontrolle({ aktion: 'klick', x, y, taste });
}

function bridgeDoppelklick() {
  const x = parseInt(document.getElementById('klick-x').value);
  const y = parseInt(document.getElementById('klick-y').value);
  if (isNaN(x) || isNaN(y)) { bridgeLog('x und y angeben'); return; }
  bridgeKontrolle({ aktion: 'doppelklick', x, y });
}

function bridgeTippen() {
  const text = document.getElementById('tipp-text').value;
  if (!text) return;
  bridgeKontrolle({ aktion: 'tippen', text });
}

function bridgeHotkey() {
  const raw = document.getElementById('hotkey-text').value.trim();
  if (!raw) return;
  const tasten = raw.split('+').map(s => s.trim());
  bridgeKontrolle({ aktion: 'hotkey', tasten });
}

function bridgeScroll(richtung) {
  bridgeKontrolle({ aktion: 'scroll', richtung, klicks: 5 });
}

async function screenshotJetzt() {
  bridgeLog('screenshot wird angefordert...');
  try {
    const r = await fetch('/api/bridge/screenshot_jetzt', { method: 'POST' });
    const d = await r.json();
    if (d.bild) {
      const img = document.getElementById('desktop-img');
      img.src = 'data:image/jpeg;base64,' + d.bild;
      img.style.display = 'block';
      document.getElementById('desktop-ts').textContent = 'jetzt';
      bridgeLog('screenshot empfangen');
    } else { bridgeLog(d.fehler || 'kein bild'); }
  } catch(e) { bridgeLog('fehler: ' + e.message); }
}

async function desktopLaden() {
  try {
    const r = await fetch('/api/bridge/screenshot');
    if (!r.ok) return;
    const d = await r.json();
    if (d.bild) {
      const img = document.getElementById('desktop-img');
      img.src = 'data:image/jpeg;base64,' + d.bild;
      img.style.display = 'block';
      const ts = d.ts ? d.ts.replace('T',' ').substring(0,16) : '';
      document.getElementById('desktop-ts').textContent = ts;
    }
  } catch(e) {}
}

async function bridgeStatusPruefen() {
  try {
    const r = await fetch('/api/bridge/status');
    const d = await r.json();
    const dot = document.getElementById('bridge-dot');
    const status = document.getElementById('bridge-status');
    const panel = document.getElementById('bridge-panel');
    if (d.verbunden) {
      dot.classList.add('verbunden');
      status.textContent = d.hostname || 'verbunden';
      status.style.color = '#5a9a2a';
      panel.classList.add('aktiv');
      desktopLaden();
    } else {
      dot.classList.remove('verbunden');
      status.textContent = 'getrennt';
      status.style.color = '#2a2a2a';
    }
  } catch(e) {}
}

function bridgeToggle() {
  const panel = document.getElementById('bridge-panel');
  bridgeOffen = !bridgeOffen;
  if (bridgeOffen) panel.classList.add('aktiv'); else panel.classList.remove('aktiv');
}

bridgeStatusPruefen();
setInterval(bridgeStatusPruefen, 10000);

function importPanel() {
  const p = document.getElementById('import-panel');
  p.style.display = p.style.display === 'none' ? 'flex' : 'none';
}

async function importStarten() {
  const pfad = document.getElementById('import-pfad').value.trim();
  const chunk = parseInt(document.getElementById('import-chunk').value) || 600;
  const log = document.getElementById('import-log');
  if (!pfad) { log.textContent = 'pfad eingeben'; return; }
  log.textContent = 'starte...';
  try {
    const r = await fetch('/api/importieren', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ pfad, chunk_groesse: chunk })
    });
    const reader = r.body.getReader();
    const dec = new TextDecoder();
    let buf = '';
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      const lines = buf.split('\\n');
      buf = lines.pop();
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        try {
          const d = JSON.parse(line.slice(6));
          if (d.log) log.textContent += d.log + String.fromCharCode(10);
          if (d.fertig) {
            log.textContent += `\nfertig: ${d.knoten} knoten aus ${d.dateien} dateien`;
            knotenLaden();
          }
          log.scrollTop = log.scrollHeight;
        } catch(e) {}
      }
    }
  } catch(e) { log.textContent += 'fehler: ' + e.message; }
}

let ttsAktiv = localStorage.getItem('geni_tts') === '1';
let ttsLaeuft = false;

function ttsToggle() {
  ttsAktiv = !ttsAktiv;
  localStorage.setItem('geni_tts', ttsAktiv ? '1' : '0');
  const btn = document.getElementById('tts-btn');
  btn.textContent = ttsAktiv ? 'stimme' : 'stille';
  btn.style.color = ttsAktiv ? '#7ab84a' : '#333';
  btn.style.borderColor = ttsAktiv ? '#3a5a1a' : '#1a1a1a';
}

(function() {
  const btn = document.getElementById('tts-btn');
  if (ttsAktiv) {
    btn.textContent = 'stimme';
    btn.style.color = '#7ab84a';
    btn.style.borderColor = '#3a5a1a';
  }
})();

function ttsSplitChunks(text, maxLen) {
  const sentences = text.match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [text];
  const chunks = [];
  let current = '';
  for (const s of sentences) {
    if (s.length > maxLen) {
      if (current) { chunks.push(current.trim()); current = ''; }
      const words = s.split(/\s+/);
      let wcurrent = '';
      for (const w of words) {
        if ((wcurrent + ' ' + w).length > maxLen && wcurrent) {
          chunks.push(wcurrent.trim());
          wcurrent = w;
        } else {
          wcurrent = (wcurrent + ' ' + w).trim();
        }
      }
      if (wcurrent) chunks.push(wcurrent.trim());
    } else if ((current + s).length > maxLen && current) {
      chunks.push(current.trim());
      current = s;
    } else {
      current += s;
    }
  }
  if (current) chunks.push(current.trim());
  return chunks;
}

function playTtsBlob(blob) {
  return new Promise((resolve) => {
    const url = URL.createObjectURL(blob);
    if (window._ttsAudio) {
      window._ttsAudio.pause();
      window._ttsAudio.src = '';
    }
    window._ttsAudio = new Audio(url);
    window._ttsAudio.onended = () => { URL.revokeObjectURL(url); ttsLaeuft = false; window._ttsAudio = null; resolve(); };
    window._ttsAudio.onerror = () => { URL.revokeObjectURL(url); ttsLaeuft = false; window._ttsAudio = null; resolve(); };
    window._ttsAudio.play().catch(() => { URL.revokeObjectURL(url); ttsLaeuft = false; window._ttsAudio = null; resolve(); });
  });
}

async function ttsSprich(text) {
  if (!ttsAktiv || ttsLaeuft || !text.trim()) return;
  ttsLaeuft = true;
  try {
    const gekuerzt = text.replace(/[#*`_]/g, '').trim();
    const chunks = ttsSplitChunks(gekuerzt, 400);
    for (const chunk of chunks) {
      if (!chunk.trim()) continue;
      try {
        const r = await fetch('/api/speak', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({text: chunk})
        });
        if (!r.ok) continue;
        const blob = await r.blob();
        if (blob.size < 100) continue;
        await playTtsBlob(blob);
      } catch(e) {}
    }
  } finally { ttsLaeuft = false; }
}

let _filterDebounce = null;

function filterAuslosen() {
  clearTimeout(_filterDebounce);
  _filterDebounce = setTimeout(knotenLaden, 300);
}

async function knotenLaden() {
  try {
    const tag = document.getElementById('filter-tag').value.trim();
    const tiefe = document.getElementById('filter-tiefe').value;
    const typ = document.getElementById('filter-typ').value;
    const zeitraum = document.getElementById('filter-zeitraum').value;
    const params = new URLSearchParams({ n: 30 });
    if (tag) params.set('tag', tag);
    if (tiefe) params.set('tiefe', tiefe);
    if (typ) params.set('typ', typ);
    if (zeitraum) params.set('zeitraum', zeitraum);
    const r = await fetch('/knoten?' + params.toString());
    const liste = await r.json();
    document.getElementById('knoten-count').textContent = liste.length + ' knoten';
    const panel = document.getElementById('knoten-liste');
    panel.innerHTML = '';
    liste.forEach(k => {
      const div = document.createElement('div');
      const kTiefe = k.tiefe || 0;
      const tiefePunkte = ['·', '◦◦', '●●', '◉◉◉'][kTiefe] || '·';
      div.className = 'knoten-item tiefe-' + kTiefe + ' k-' + (k.quelle === 'daniel' ? 'daniel' : k.quelle === 'geni_selbst' ? 'geni' : k.quelle.startsWith('vps') ? 'vps' : 'flarum');
      div.innerHTML = `<span class="k-tiefe">${tiefePunkte}</span><span class="k-id">#${k.id}</span><div class="k-quelle">${k.quelle} · ${k.zeitstempel.replace('T',' ')}</div><div class="k-inhalt">${k.inhalt}</div>`;
      panel.appendChild(div);
    });
  } catch(e) {}
}

document.getElementById('filter-tag').addEventListener('input', filterAuslosen);
document.getElementById('filter-tiefe').addEventListener('change', knotenLaden);
document.getElementById('filter-typ').addEventListener('change', knotenLaden);
document.getElementById('filter-zeitraum').addEventListener('change', knotenLaden);

knotenLaden();
setInterval(knotenLaden, 8000);

document.getElementById('file-input').addEventListener('change', async function() {
  const datei = this.files[0];
  if (!datei) return;
  const fd = new FormData();
  fd.append('datei', datei);
  const r = await fetch('/upload', { method: 'POST', body: fd });
  const data = await r.json();
  aktuellesBildB64 = data.b64;
  aktuellerBildName = data.name;
  const prev = document.getElementById('bild-preview');
  prev.src = 'data:image/' + datei.name.split('.').pop() + ';base64,' + data.b64;
  prev.style.display = 'block';
  document.getElementById('bild-name').textContent = datei.name;
  document.getElementById('bild-clear').style.display = 'inline';
});

function bildLeeren() {
  aktuellesBildB64 = null;
  aktuellerBildName = null;
  document.getElementById('bild-preview').style.display = 'none';
  document.getElementById('bild-name').textContent = '';
  document.getElementById('bild-clear').style.display = 'none';
  document.getElementById('file-input').value = '';
}

document.getElementById('eingabe').addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    senden();
  }
});

function nachrichtAnzeigen(text, rolle, bild = null) {
  const msgs = document.getElementById('messages');
  const div = document.createElement('div');
  div.className = 'msg ' + rolle;
  if (bild) {
    const img = document.createElement('img');
    img.src = 'data:image/jpeg;base64,' + bild;
    img.className = 'msg-bild';
    div.appendChild(img);
  }
  const span = document.createElement('span');
  span.textContent = text;
  div.appendChild(span);
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
  return div;
}

async function senden() {
  if (sendenAktiv) return;
  const ta = document.getElementById('eingabe');
  const text = ta.value.trim();
  if (!text) return;

  sendenAktiv = true;
  document.getElementById('send-btn').disabled = true;
  document.getElementById('status').textContent = 'GENI hört...';

  nachrichtAnzeigen(text, 'daniel', aktuellesBildB64);
  ta.value = '';

  const geniDiv = nachrichtAnzeigen('', 'geni streaming');
  const geniSpan = geniDiv.querySelector('span');

  const modell = document.getElementById('modell-select').value;
  const body = { eingabe: text, session_id: sessionId, modell };
  if (aktuellesBildB64) body.bild_b64 = aktuellesBildB64;
  bildLeeren();

  try {
    const r = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!r.ok) { geniSpan.textContent = '[fehler ' + r.status + ']'; return; }

    const reader = r.body.getReader();
    const decoder = new TextDecoder();
    let buf = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const parts = buf.split('\\n');
      buf = parts.pop();
      for (const line of parts) {
        if (!line.startsWith('data: ')) continue;
        try {
          const data = JSON.parse(line.slice(6));
          if (data.token) {
            geniSpan.textContent += data.token;
            document.getElementById('messages').scrollTop = 999999;
          }
          if (data.done) {
            geniDiv.classList.remove('streaming');
            ttsSprich(geniSpan.textContent);
          }
        } catch(e) {}
      }
    }
  } catch(e) {
    geniSpan.textContent = '[' + e.message + ']';
  } finally {
    document.getElementById('status').textContent = 'bereit';
    document.getElementById('send-btn').disabled = false;
    sendenAktiv = false;
    knotenLaden();
  }
}
</script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    BILDER_DIR.mkdir(parents=True, exist_ok=True)
    KANTEN_DIR.mkdir(parents=True, exist_ok=True)
    ssl_cert = GENI_ROOT / "ssl_cert.pem"
    ssl_key  = GENI_ROOT / "ssl_key.pem"
    if ssl_cert.exists() and ssl_key.exists():
        print("GENI Dialogbahn — Port 8020 (HTTPS)")
        uvicorn.run(app, host="0.0.0.0", port=8020, log_level="warning",
                    ssl_certfile=str(ssl_cert), ssl_keyfile=str(ssl_key))
    else:
        print("GENI Dialogbahn — Port 8020 (HTTP)")
        uvicorn.run(app, host="0.0.0.0", port=8020, log_level="warning")
