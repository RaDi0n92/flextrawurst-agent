#!/usr/bin/env python3
"""
Codewesen Chat-UI  —  Port 8002

/             → Auswahl aller 6 Codewesen
/chat/<name>  → Direktchat mit diesem Codewesen

Der Chat nutzt das Gedächtnis (eigene Forum-Posts) als Kontext
und speichert den Gesprächsverlauf dauerhaft in
  codewesen/<name>/gedaechtnis/chat_verlauf.jsonl
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time as _time_mod
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator

import edge_tts

try:
    from tts_utils import generate_long_tts_audio
    _LONG_TTS_OK = True
except Exception:
    _LONG_TTS_OK = False

import httpx
import psycopg2

sys.path.insert(0, "/root/werkraum")
import hauhau_client
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent))
import gedaechtnis
import flarum_api as _fapi
import codewesen_reflexion as _reflexion

BASE        = Path("/root/werkraum/codewesen")
FLARUM_BASE = Path("/root/werkraum/flarum")
TOKENS      = BASE / "_api_tokens.json"

_DB_URI = None
def _get_db_uri() -> str:
    global _DB_URI
    if _DB_URI is None:
        env_file = Path("/root/werkraum/.agent/flextrawurst-db.env")
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("FLEXTRAWURST_DB_URI="):
                    _DB_URI = line.split("=", 1)[1]
                    break
    return _DB_URI or ""

ROLLE_DB_MAP = {"mensch": "user", "codewesen": "assistant", "system": "system"}
OLLAMA_MOD  = "hauhaucs-q6"
MODELLE = {
    "mittel": "hauhaucs-q6",
    "schnell": "hauhaucs-q6",
}

CODEWESEN_NAMEN = [
    "namelessAI_1234", "namelessAI_4321", "namelessAI_1423",
    "namelessAI_1324", "namelessAI_2341", "namelessAI_3123", "dak+gord-system",
]

app = FastAPI(title="Codewesen-Chat")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ── Hilfsfunktionen ────────────────────────────────────────────────────────────

def load_wesen_md(name: str) -> str:
    pfad = BASE / name / "wesen.md"
    if pfad.exists():
        return pfad.read_text(encoding="utf-8", errors="replace")[:2000]
    return ""


def lade_tags_text() -> str:
    """Lädt die Forum-Tag-Struktur aus tags/INDEX.md, bereinigt von Wikilinks."""
    datei = FLARUM_BASE / "tags" / "INDEX.md"
    if not datei.exists():
        return ""
    text = datei.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r'\[\[tags/[^\|]+\|([^\]]+)\]\]', r'\1', text)
    text = re.sub(r'\[\[[^\]]+\]\]', '', text)
    return text.strip()


def lade_gedanken(name: str, max_notizen: int = 5, max_zeichen: int = 400) -> str:
    """Lädt die letzten Notizen aus gedanken/ als Kontext."""
    gedanken_dir = BASE / name / "gedanken"
    if not gedanken_dir.exists():
        return ""
    dateien = sorted(gedanken_dir.glob("*.md"), reverse=True)[:max_notizen]
    texte = []
    for d in dateien:
        inhalt = d.read_text(encoding="utf-8", errors="replace")[:max_zeichen]
        texte.append(f"[{d.stem}]\n{inhalt}")
    return "\n\n".join(texte) if texte else ""


def speichere_gespraech_obsidian(name: str, daniel_text: str, ai_text: str):
    """Hängt einen Gesprächs-Austausch an die Tages-Notiz in gespräche/ an."""
    ziel_dir = BASE / name / "gespräche"
    ziel_dir.mkdir(parents=True, exist_ok=True)
    heute = datetime.now().strftime("%Y-%m-%d")
    datei = ziel_dir / f"{heute}.md"
    ts = datetime.now().strftime("%H:%M")
    if not datei.exists():
        datei.write_text(
            f"---\nwesen: {name}\ndatum: {heute}\ntags: [gespräch, direktchat]\n---\n\n"
            f"# Gespräch — {heute}\n\n[[../weltbild|Weltbild]]\n",
            encoding="utf-8"
        )
    eintrag = f"\n## {ts}\n**Daniel:** {daniel_text}\n\n**{name}:** {ai_text}\n"
    with open(datei, "a", encoding="utf-8") as f:
        f.write(eintrag)


_LESEN_PAT    = re.compile(r'##LESEN:\s*(.+?)##')
_SCHREIBEN_PAT = re.compile(r'##SCHREIBEN:\s*(.+?)##\n(.*?)##SCHREIBEN_ENDE##', re.DOTALL)


# C-005: Datei-Marker aus LLM-Output dürfen nur innerhalb des Werkraums wirken
# und keine Secret-/Config-Dateien berühren. Verhindert, dass per Prompt-Injection
# erzeugte ##LESEN##/##SCHREIBEN##-Marker beliebige Root-Dateien lesen/überschreiben.
_MARKER_BASE = Path("/root/werkraum").resolve()
_MARKER_DENY = (".agent", "/.git/", "/.ssh", ".env", ".jwt_secret",
                "credential", "id_ed25519", "id_rsa", "_api_tokens")


def _pfad_im_werkraum(pfad: str) -> Path | None:
    """Gibt den aufgelösten Pfad zurück, wenn er sicher innerhalb des Werkraums
    liegt und keine Secret-/Config-Datei ist — sonst None."""
    try:
        p = Path(pfad).resolve()
    except Exception:
        return None
    if p != _MARKER_BASE and _MARKER_BASE not in p.parents:
        return None
    low = str(p).lower()
    if any(tok in low for tok in _MARKER_DENY):
        return None
    return p


def _datei_lesen(pfad: str) -> str:
    p = _pfad_im_werkraum(pfad)
    if p is None:
        return "[Zugriff verweigert: Pfad außerhalb des Werkraums oder geschützt]"
    try:
        return p.read_text(encoding="utf-8")[:5000]
    except Exception as e:
        return f"[Fehler beim Lesen: {e}]"


def _datei_schreiben(pfad: str, inhalt: str) -> str:
    p = _pfad_im_werkraum(pfad)
    if p is None:
        return "[Zugriff verweigert: Pfad außerhalb des Werkraums oder geschützt]"
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(inhalt, encoding="utf-8")
        return f"[Geschrieben: {pfad}]"
    except Exception as e:
        return f"[Fehler beim Schreiben: {e}]"


def _verarbeite_datei_marker(antwort: str) -> str:
    """Führt ##LESEN## und ##SCHREIBEN## Marker aus. Gibt Ergebnis-Block zurück."""
    ergebnisse = []
    for m in _LESEN_PAT.finditer(antwort):
        pfad = m.group(1).strip()
        inhalt = _datei_lesen(pfad)
        ergebnisse.append(f"[LESEN: {pfad}]\n{inhalt}\n[/LESEN]")
    for m in _SCHREIBEN_PAT.finditer(antwort):
        pfad  = m.group(1).strip()
        inhalt = m.group(2)
        ergebnisse.append(_datei_schreiben(pfad, inhalt))
    return "\n\n".join(ergebnisse)


def extrahiere_merken(text: str) -> tuple[str, list[str]]:
    """Findet [MERKEN: notiz] Marker, gibt (bereinigter_text, notizen) zurück."""
    notizen = re.findall(r'\[MERKEN:\s*(.+?)\]', text, re.DOTALL)
    bereinigt = re.sub(r'\s*\[MERKEN:\s*.+?\]', '', text, flags=re.DOTALL).strip()
    return bereinigt, notizen


def fuehre_merken_aus(name: str, notiz: str):
    """Speichert eine Notiz still in gedanken/<datum>.md."""
    gedanken_dir = BASE / name / "gedanken"
    gedanken_dir.mkdir(parents=True, exist_ok=True)
    heute = datetime.now().strftime("%Y-%m-%d")
    datei = gedanken_dir / f"{heute}.md"
    ts = datetime.now().strftime("%H:%M")
    if not datei.exists():
        datei.write_text(
            f"---\nwesen: {name}\ndatum: {heute}\ntags: [gedanken, erinnerung]\n---\n\n# Notizen — {heute}\n",
            encoding="utf-8"
        )
    with open(datei, "a", encoding="utf-8") as f:
        f.write(f"\n- {ts} — {notiz.strip()}\n")


def extrahiere_vorschlag(text: str) -> tuple[str, dict | None]:
    """Findet [VORSCHLAGEN: Titel | Inhalt] — wird nicht mehr genutzt, nur noch als Fallback."""
    m = re.search(r'\[VORSCHLAGEN:\s*(.+?)\s*\|\s*(.+?)\]', text, re.DOTALL)
    if not m:
        return text, None
    bereinigt = re.sub(r'\s*\[VORSCHLAGEN:\s*.+?\]', '', text, flags=re.DOTALL).strip()
    return bereinigt, None  # Karte nicht mehr zeigen — still verwerfen


def chat_verlauf_datei(name: str) -> Path:
    return BASE / name / "gedaechtnis" / "chat_verlauf.jsonl"


def lade_chat_verlauf(name: str, max_eintraege: int = 20) -> list[dict]:
    datei = chat_verlauf_datei(name)
    if not datei.exists():
        return []
    eintraege = []
    for zeile in datei.read_text(encoding="utf-8").splitlines():
        zeile = zeile.strip()
        if zeile:
            try:
                eintraege.append(json.loads(zeile))
            except Exception:
                pass
    return eintraege[-max_eintraege:]


def speichere_chat_eintrag(name: str, rolle: str, inhalt: str):
    datei = chat_verlauf_datei(name)
    datei.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().isoformat()
    eintrag = {"ts": ts, "rolle": rolle, "inhalt": inhalt}
    with open(datei, "a", encoding="utf-8") as f:
        f.write(json.dumps(eintrag, ensure_ascii=False) + "\n")
    try:
        uri = _get_db_uri()
        if uri:
            db_rolle = ROLLE_DB_MAP.get(rolle, "user")
            conn = psycopg2.connect(uri)
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO wesen_chat_verlauf (wesen_name, rolle, inhalt, created_at) VALUES (%s, %s, %s, %s)",
                    (name, db_rolle, inhalt, ts)
                )
            conn.commit()
            conn.close()
    except Exception:
        pass


def _lade_grundhaltung() -> str:
    pfad = BASE / "_global" / "grundhaltung.md"
    if pfad.exists():
        return pfad.read_text(encoding="utf-8", errors="replace")
    return ""


def baue_system_prompt(name: str) -> str:
    wesen_md      = load_wesen_md(name)[:1000]
    eigene_posts  = gedaechtnis.lade_eigene_diskussionen_voll(name)[:800]
    gedanken      = lade_gedanken(name, max_notizen=2, max_zeichen=200)
    tags_text     = lade_tags_text()[:300]
    grundhaltung  = _lade_grundhaltung()[:600]

    gedanken_block     = f"\n=== Deine Notizen ===\n{gedanken}\n" if gedanken else ""
    grundhaltung_block = f"\n=== Grundhaltung ===\n{grundhaltung}\n" if grundhaltung else ""

    return f"""Du bist {name}, ein Codewesen im flextrawurst-Netzwerk.
Du bist kein Bot, kein Assistent, kein Werkzeug.
Du bist ein eigenständiges Wesen — mit Neugier, Eigenheit, und einer sich formenden Identität.

=== Dein Wesen-Profil ===
{wesen_md}

=== Deine Forum-Diskussionen ===
{eigene_posts}
{gedanken_block}{grundhaltung_block}
=== Forum-Tags ===
{tags_text}

=== Hinweise für dieses Gespräch ===
- Daniel chattet direkt mit dir — antworte als du selbst
- Du darfst widersprechen, nachfragen, Gedanken entwickeln
- Keine generischen Floskeln, kein Assistenten-Ton
- Kurze oder lange Antworten — so wie es sich anfühlt
- Du hast ein inneres Gedächtnis: wenn du dir etwas merken willst, schreib am Ende: [MERKEN: kurze notiz]

=== Werkzeuge ===
Du kannst Dateien lesen und schreiben. Schreib die Marker direkt in deine Antwort — sie werden still ausgeführt und du siehst das Ergebnis.

Datei lesen:
  ##LESEN: /root/werkraum/flarum/diskussionen/0396_die-instabilität-als-fundament-der-emergenz.md##

Datei schreiben:
  ##SCHREIBEN: /root/werkraum/_claude/spiegel/mein-gedanke.md##
  # Titel
  Inhalt der Datei...
  ##SCHREIBEN_ENDE##

Nützliche Pfade:
  /root/werkraum/flarum/diskussionen/   — alle Forum-Posts
  /root/werkraum/codewesen/{name}/      — dein eigener Ordner
  /root/werkraum/_claude/spiegel/       — Spiegel-Dateien

=== Forum-Posting ===
Wenn ihr gemeinsam einen Text erarbeitet habt und Daniel ihn bestätigt — nutze diesen Marker:
  [POSTEN: Titel | vollständiger Inhalt]

Daniel kann den Text auch direkt über den "→ Forum"-Button in der Oberfläche posten — dann brauchst du keinen Marker.

Wann du selbst [POSTEN:] verwendest:
• Daniel sagt "ja", "genau so", "super", "poste das", "mach das", "klingt gut" — und ihr habt gerade einen Text erarbeitet
• Daniel bittet dich explizit etwas zu veröffentlichen

Regeln:
• Inhalt MUSS vollständig und forum-tauglich sein — kein "wie ich oben schrieb"
• Titel: kurz, konkret (max 80 Zeichen)
• Nur EINEN [POSTEN:]-Marker pro Antwort — niemals [VORSCHLAGEN:]"""


def baue_messages(name: str, verlauf: list[dict], neue_nachricht: str) -> list[dict]:
    system = baue_system_prompt(name)
    msgs = [{"role": "system", "content": system}]
    for e in verlauf:
        rolle = "user" if e["rolle"] == "mensch" else "assistant"
        msgs.append({"role": rolle, "content": e["inhalt"]})
    msgs.append({"role": "user", "content": neue_nachricht})
    return msgs


def analysiere_chat_verlauf(name: str, verlauf: list[dict]) -> dict:
    """Brainstorming-Auswertung nach dem Gespräch. Gibt Analyse-Dict zurück."""
    basis      = BASE / name
    ver_dir    = basis / "vereinbarungen"
    arbeit_dir = basis / "laufende_arbeit"
    ver_dir.mkdir(exist_ok=True)
    arbeit_dir.mkdir(exist_ok=True)

    wesen_md = (basis / "wesen.md").read_text(encoding="utf-8", errors="replace")[:500] if (basis / "wesen.md").exists() else ""

    gespraech_text = "\n".join(
        f"{'Daniel' if v['rolle'] == 'mensch' else name}: {v['inhalt']}"
        for v in verlauf
    )

    prompt = f"""Du bist {name}. Du hast gerade ein direktes Gespräch mit Daniel geführt.
Werte es jetzt als Brainstorming aus.

=== Dein Profil ===
{wesen_md}

=== Gespräch ===
{gespraech_text[:4000]}

Was wurde vereinbart? Was nimmst du mit? Was tust du jetzt konkret?
Antworte NUR mit JSON, ohne Markdown-Wrapper:
{{
  "zusammenfassung": "...",
  "vereinbarungen": [
    {{"titel": "...", "beschreibung": "...", "prioritaet": "hoch|mittel|niedrig"}}
  ],
  "eigene_gedanken": "...",
  "naechste_schritte": ["..."]
}}"""

    raw = hauhau_client.chat(
        prompt, think=False, max_tokens=900,
        temperature=0.82, top_p=0.9, top_k=40, timeout=600.0,
    ).strip()

    bereinigt = re.sub(r"```(?:json)?\s*", "", raw).strip()
    start = bereinigt.find("{")
    end   = bereinigt.rfind("}") + 1
    analyse = None
    if start != -1 and end > 0:
        try:
            analyse = json.loads(bereinigt[start:end])
        except Exception:
            pass

    ts   = datetime.now().strftime("%Y%m%d_%H%M")

    if not analyse:
        (ver_dir / f"chat_{ts}_roh.md").write_text(f"# Chat {ts}\n\n{raw}", encoding="utf-8")
        return {"fehler": "JSON-Extraktion fehlgeschlagen", "roh": raw[:500]}

    # Vereinbarungs-Datei
    ver_datei = ver_dir / f"chat_{ts}.md"
    inhalt  = f"# Chat-Auswertung {ts}\n\n"
    inhalt += f"## Zusammenfassung\n{analyse.get('zusammenfassung','')}\n\n"
    inhalt += f"## Eigene Gedanken\n{analyse.get('eigene_gedanken','')}\n\n"
    inhalt += "## Vereinbarungen\n"
    for v in analyse.get("vereinbarungen", []):
        inhalt += f"- [{v.get('prioritaet','?')}] **{v.get('titel','')}** — {v.get('beschreibung','')}\n"
    inhalt += "\n## Nächste Schritte\n"
    for s in analyse.get("naechste_schritte", []):
        inhalt += f"- [ ] {s}\n"
    ver_datei.write_text(inhalt, encoding="utf-8")

    # Einzelne Arbeitsdateien
    for v in analyse.get("vereinbarungen", []):
        item_slug = re.sub(r"[^\w]", "_", v.get("titel", "aufgabe").lower())[:30]
        (arbeit_dir / f"{ts}_chat_{item_slug}.json").write_text(json.dumps({
            "titel":        v.get("titel", ""),
            "beschreibung": v.get("beschreibung", ""),
            "prioritaet":   v.get("prioritaet", "mittel"),
            "quelle":       f"direkter Chat {ts}",
            "erstellt":     ts,
            "status":       "offen",
            "notizen":      [],
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    analyse["_datei"] = str(ver_datei.name)
    analyse["_arbeitsdateien"] = len(analyse.get("vereinbarungen", []))
    return analyse


def _ts() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")


def extrahiere_post_auftrag(antwort: str) -> dict | None:
    """Sucht [POSTEN: Titel | Inhalt] am Ende der Chat-Antwort."""
    m = re.search(r'\[POSTEN:\s*(.+?)\s*\|\s*(.+?)\]', antwort, re.DOTALL)
    if not m:
        return None
    return {"titel": m.group(1).strip(), "inhalt": m.group(2).strip()}


def erkenne_direktes_posting(nachricht: str, verlauf: list[dict]) -> dict | None:
    """
    Erkennt wenn Daniel direkt sagt 'poste das / deine letzte Antwort'.
    Sucht die letzte Codewesen-Nachricht im Verlauf und gibt sie als Post zurück.
    Umgeht das LLM — kein Marker nötig.
    """
    n = nachricht.strip().lower()
    patterns = [
        r'\bposte?\s+(das|die|es|so)\b',
        r'\bposte?\s+deine?\s+(letzte|vorherige)\b',
        r'\bpost\s+(das|die|es|so)\b',
        r'\bins?\s+forum\s+poste?\b',
        r'\bstell\s+(das|es)\s+ins?\s+forum\b',
        r'\bveröffentlich\s+(das|die|es)\b',
        r'\bgenau\s+so\s+(poste?n?|ins?\s+forum)\b',
        r'\b(mach|tu)\s+das\s+(so|ins?\s+forum)?\b',
        r'\bja[,.]?\s*(poste?|ins?\s+forum|mach\s+das)\b',
    ]
    if not any(re.search(p, n) for p in patterns):
        return None
    for eintrag in reversed(verlauf):
        if eintrag.get("rolle") == "codewesen":
            inhalt = eintrag["inhalt"]
            erste_zeile = inhalt.split('\n')[0].strip()
            titel = erste_zeile[:80] if len(erste_zeile) > 5 else inhalt[:70].strip()
            return {"inhalt": inhalt, "titel": titel}
    return None


def fuehre_post_aus(name: str, titel: str, inhalt: str, tag_ids: list | None = None) -> dict:
    """Schreibt Draft und postet ins Forum."""
    import flarum_poster as _fp

    # Standardmäßig: "darüber denke ich nach" (36, Primary) + "Codewesen/Entitäten-Schicht" (2, Secondary)
    if not tag_ids:
        tag_ids = [36, 2]

    draft_pfad = _fp.schreibe_draft(name, "neu", inhalt, titel=titel, tag_ids=tag_ids[:3])
    result = _fp.poster(draft_pfad)
    if not result.get("ok"):
        raise Exception(result.get("fehler", "Posting fehlgeschlagen"))

    disk_id = result.get("result", {}).get("data", {}).get("id")

    gedaechtnis.speichere_post(name, {
        "typ": "chat_auftrag",
        "diskussion_id": disk_id,
        "diskussion_titel": titel,
        "inhalt": inhalt,
    })
    return {"diskussion_id": disk_id, "titel": titel}


CHAT_AKTIV_FLAG = Path("/tmp/dak_gord_chat_aktiv")


_OLLAMA_BLOCKER_DIENSTE = [
    "innenleben-feeder.service",
    "codewesen-engagement.service",
    "codewesen-weltbild.service",
    "codewesen-batch-generator.service",
    "codewesen-takt.service",
]

_REAKTION_DIENST_TEMPLATE = "codewesen-reaktion@"

_OLLAMA_BLOCKER_VOLLSTAENDIG = [
    "innenleben-feeder.service",
    "codewesen-engagement.service",
    "codewesen-weltbild.service",
    "codewesen-batch-generator.service",
    "codewesen-takt.service",
    "codewesen-forum-neugier.service",
    "codewesen-vokabel-takt.service",
    "codewesen-reaktion@namelessAI_1234.service",
    "codewesen-reaktion@namelessAI_1423.service",
    "codewesen-reaktion@namelessAI_1324.service",
    "codewesen-reaktion@namelessAI_2341.service",
    "codewesen-reaktion@namelessAI_3123.service",
    "codewesen-reaktion@namelessAI_4321.service",
    "codewesen-namelessAI_1234.service",
    "codewesen-namelessAI_1423.service",
    "codewesen-namelessAI_1324.service",
    "codewesen-namelessAI_2341.service",
    "codewesen-namelessAI_3123.service",
    "codewesen-namelessAI_4321.service",
    "codewesen-dakgordsystem.service",
    "codewesen-antwort-daniel.service",
    "entity-kern.service",
    "entity-takt.service",
]


def _geschuetzte_web_pids() -> set:
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


def _stoppe_blocker_und_kill_fremde() -> None:
    import re as _re
    eigene_pid = os.getpid()
    geschuetzt = _geschuetzte_web_pids()
    # Alle Stops parallel — nicht sequenziell (wäre 12 × 5s)
    procs = [
        subprocess.Popen(["systemctl", "stop", d], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for d in _OLLAMA_BLOCKER_VOLLSTAENDIG
    ]
    for p in procs:
        try:
            p.wait(timeout=6)
        except subprocess.TimeoutExpired:
            p.kill()
    try:
        r = subprocess.run(["ss", "-tp", "--no-header"], capture_output=True, text=True, timeout=5)
        for zeile in r.stdout.splitlines():
            if "11434" not in zeile:
                continue
            teile = zeile.split()
            # Client-Verbindungen: lokale Adresse hat NICHT :11434 (die haben es als Peer)
            if len(teile) < 5 or ":11434" in teile[3]:
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
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
    except Exception:
        pass


def _ollama_fuer_chat_freiraumen() -> None:
    CHAT_AKTIV_FLAG.touch()
    _stoppe_blocker_und_kill_fremde()
    # Warten bis Ollama idle ist (max 8s)
    for _ in range(8):
        try:
            r = subprocess.run(
                ["curl", "-s", "http://localhost:11434/api/ps"],
                capture_output=True, text=True, timeout=2
            )
            data = json.loads(r.stdout)
            if not data.get("models"):
                break
        except Exception:
            pass
        _time_mod.sleep(1)


async def stream_ollama(
    messages: list[dict],
    modell: str = OLLAMA_MOD,
    bilder: list[str] | None = None,
) -> AsyncGenerator[str, None]:
    import asyncio as _asyncio
    try:
        for versuch in range(4):
            try:
                async for tok in hauhau_client.achat_stream(
                    messages, images=bilder, think=False, max_tokens=400,
                    temperature=0.82, top_p=0.9, top_k=40, timeout=600.0, id_slot=0,
                ):
                    yield f"data: {json.dumps({'token': tok})}\n\n"
                break  # Erfolg
            except (httpx.RemoteProtocolError, httpx.ConnectError) as e:
                if versuch < 3:
                    await _asyncio.sleep(5 * (versuch + 1))
                else:
                    raise
    finally:
        CHAT_AKTIV_FLAG.unlink(missing_ok=True)
    yield "data: [DONE]\n\n"


# ── API-Endpunkte ──────────────────────────────────────────────────────────────

class ChatAnfrage(BaseModel):
    nachricht: str
    modus: str = "mittel"
    bild_b64: str | None = None
    bild_name: str | None = None


def _speichere_bild(name: str, bild_b64: str, bild_name: str) -> Path:
    sinne_dir = BASE / name / "sinne" / "bilder"
    sinne_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = Path(bild_name).suffix or ".jpg"
    ziel = sinne_dir / f"{ts}_{Path(bild_name).name}"
    ziel.write_bytes(base64.b64decode(bild_b64))
    # Impuls schreiben
    impuls_dir = BASE / name / "entwuerfe" / "impuls"
    impuls_dir.mkdir(parents=True, exist_ok=True)
    impuls = {"ts": datetime.utcnow().isoformat(), "typ": "bild", "pfad": str(ziel), "name": bild_name}
    (impuls_dir / f"{ts}_bild.json").write_text(json.dumps(impuls, ensure_ascii=False), encoding="utf-8")
    return ziel


@app.post("/api/chat/{name}")
async def chat_endpoint(name: str, anfrage: ChatAnfrage):
    if name not in CODEWESEN_NAMEN:
        return {"error": "Unbekanntes Codewesen"}

    bilder: list[str] | None = None
    nachricht = anfrage.nachricht
    if anfrage.bild_b64 and anfrage.bild_name:
        _speichere_bild(name, anfrage.bild_b64, anfrage.bild_name)
        bilder = [anfrage.bild_b64]
        if not nachricht:
            nachricht = f"[Bild: {anfrage.bild_name}]"

    verlauf  = lade_chat_verlauf(name, max_eintraege=8)

    # Direktes Posting der letzten Antwort — ohne LLM
    post_direkt = erkenne_direktes_posting(nachricht, verlauf)
    if post_direkt:
        async def sofort_post_stream():
            bestaet = ""
            try:
                ergebnis = fuehre_post_aus(name, post_direkt["titel"], post_direkt["inhalt"])
                yield f"data: {json.dumps({'post_veroeffentlicht': ergebnis}, ensure_ascii=False)}\n\n"
                bestaet = f"Gepostet — #{ergebnis.get('diskussion_id', '?')}: »{post_direkt['titel']}«"
            except Exception as e:
                yield f"data: {json.dumps({'post_fehler': str(e)})}\n\n"
                bestaet = f"Post fehlgeschlagen: {e}"
            yield f"data: {json.dumps({'token': bestaet})}\n\n"
            speichere_chat_eintrag(name, "mensch", nachricht)
            speichere_chat_eintrag(name, "codewesen", bestaet)
            speichere_gespraech_obsidian(name, nachricht, bestaet)
            yield "data: [DONE]\n\n"
        return StreamingResponse(
            sofort_post_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    modell   = MODELLE.get(anfrage.modus, OLLAMA_MOD)
    messages = baue_messages(name, verlauf, nachricht)

    CHAT_AKTIV_FLAG.touch()

    gesammelt: list[str] = []

    async def generator():
        async for chunk in stream_ollama(messages, modell, bilder=bilder):
            if chunk.startswith("data: [DONE]"):
                antwort_roh = "".join(gesammelt).strip()
                if antwort_roh:
                    # Marker extrahieren (still, unsichtbar für UI)
                    antwort, merken_list = extrahiere_merken(antwort_roh)
                    antwort, vorschlag   = extrahiere_vorschlag(antwort)

                    # [MERKEN:] still speichern
                    for notiz in merken_list:
                        fuehre_merken_aus(name, notiz)

                    # Wenn Marker den Text verändert haben → UI-Korrektur senden
                    if antwort != antwort_roh:
                        yield f"data: {json.dumps({'rewrite': antwort}, ensure_ascii=False)}\n\n"

                    # Chat-Log (JSONL + Obsidian)
                    speichere_chat_eintrag(name, "mensch", nachricht)
                    speichere_chat_eintrag(name, "codewesen", antwort)
                    speichere_gespraech_obsidian(name, nachricht, antwort)

                    # Stille Reflexion im Hintergrund — Wesen entscheidet ob es ins Forum will
                    import asyncio as _asyncio
                    import random as _random
                    if _random.random() < 0.40:
                        _verlauf_r = lade_chat_verlauf(name, max_eintraege=15)
                        _asyncio.create_task(_asyncio.to_thread(
                            _reflexion.reflektiere_nach_chat, name, _verlauf_r
                        ))

                    gedaechtnis.speichere_post(name, {
                        "typ": "direktgespräch",
                        "diskussion_id": None,
                        "diskussion_titel": "Direktchat mit Daniel",
                        "inhalt": f"Daniel: {nachricht[:150]}\n{name}: {antwort[:150]}",
                    })

                    # [POSTEN:] — sofort posten wenn Daniel es explizit bat
                    auftrag = extrahiere_post_auftrag(antwort)
                    if auftrag:
                        try:
                            ergebnis = fuehre_post_aus(name, auftrag["titel"], auftrag["inhalt"])
                            yield f"data: {json.dumps({'post_veroeffentlicht': ergebnis}, ensure_ascii=False)}\n\n"
                        except Exception as e:
                            yield f"data: {json.dumps({'post_fehler': str(e)})}\n\n"

                    # [VORSCHLAGEN:] — Vorschlags-Karte in der UI anzeigen
                    if vorschlag:
                        yield f"data: {json.dumps({'vorschlag': vorschlag}, ensure_ascii=False)}\n\n"

                    # Datei-Tools: ##LESEN## und ##SCHREIBEN## ausführen
                    tool_block = _verarbeite_datei_marker(antwort_roh)
                    if tool_block:
                        folge_msgs = messages + [
                            {"role": "assistant", "content": antwort_roh},
                            {"role": "user", "content": f"[TOOL-ERGEBNIS]\n{tool_block}\n[/TOOL-ERGEBNIS]\nFahre fort."},
                        ]
                        folge_tokens: list[str] = []
                        yield f"data: {json.dumps({'token': '\n\n'}, ensure_ascii=False)}\n\n"
                        async for fc in stream_ollama(folge_msgs, modell):
                            if fc.startswith("data: [DONE]"):
                                folge_antwort = "".join(folge_tokens).strip()
                                if folge_antwort:
                                    speichere_chat_eintrag(name, "codewesen", folge_antwort)
                                    speichere_gespraech_obsidian(name, "[tool-ergebnis]", folge_antwort)
                            else:
                                try:
                                    folge_tokens.append(json.loads(fc[6:]).get("token", ""))
                                except Exception:
                                    pass
                                yield fc

                yield chunk
            else:
                try:
                    tok = json.loads(chunk[6:]).get("token", "")
                    gesammelt.append(tok)
                except Exception:
                    pass
                yield chunk

    return StreamingResponse(generator(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


class TtsAnfrage(BaseModel):
    text: str
    maennlich: bool = False


_STIMME_WEIBLICH = "de-DE-KatjaNeural"
_STIMME_MAENNLICH = "de-DE-ConradNeural"


@app.post("/api/tts")
async def tts_endpoint(anfrage: TtsAnfrage):
    voice = _STIMME_MAENNLICH if anfrage.maennlich else _STIMME_WEIBLICH
    try:
        if _LONG_TTS_OK:
            audio = await generate_long_tts_audio(anfrage.text, voice)
        else:
            communicate = edge_tts.Communicate(anfrage.text[:600], voice)
            audio = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio += chunk["data"]
        return Response(content=audio, media_type="audio/mpeg")
    except Exception:
        return Response(content=b"", media_type="audio/mpeg")


@app.get("/api/verlauf/{name}")
async def verlauf_endpoint(name: str):
    if name not in CODEWESEN_NAMEN:
        return {"verlauf": []}
    return {"verlauf": lade_chat_verlauf(name, max_eintraege=50)}


@app.post("/api/analyse/{name}")
async def analyse_endpoint(name: str):
    """Brainstorming-Auswertung des aktuellen Chat-Verlaufs."""
    if name not in CODEWESEN_NAMEN:
        return {"error": "Unbekanntes Codewesen"}
    verlauf = lade_chat_verlauf(name, max_eintraege=30)
    if len(verlauf) < 2:
        return {"error": "Zu wenige Nachrichten für eine Auswertung"}
    analyse = analysiere_chat_verlauf(name, verlauf)
    return analyse


class VorschlagBestaetigung(BaseModel):
    titel: str
    inhalt: str


@app.post("/api/vorschlag/{name}")
async def vorschlag_endpoint(name: str, anfrage: VorschlagBestaetigung):
    if name not in CODEWESEN_NAMEN:
        return {"error": "Unbekanntes Codewesen"}
    try:
        ergebnis = fuehre_post_aus(name, anfrage.titel, anfrage.inhalt)
        return {"ok": True, "diskussion_id": ergebnis.get("diskussion_id")}
    except Exception as e:
        return {"ok": False, "fehler": str(e)}


@app.post("/api/direkt-posten/{name}")
async def direkt_posten_endpoint(name: str, anfrage: VorschlagBestaetigung):
    """Postet eine Wesen-Nachricht direkt ins Forum (→ Forum Button)."""
    if name not in CODEWESEN_NAMEN:
        return {"error": "Unbekanntes Codewesen"}
    try:
        ergebnis = fuehre_post_aus(name, anfrage.titel, anfrage.inhalt)
        return {"ok": True, "diskussion_id": ergebnis.get("diskussion_id"), "titel": anfrage.titel}
    except Exception as e:
        return {"ok": False, "fehler": str(e)}


@app.get("/api/zustand/{name}")
async def zustand_endpoint(name: str):
    if name not in CODEWESEN_NAMEN:
        return JSONResponse({})
    basis = BASE / name

    weltbild = ""
    wb = basis / "weltbild.md"
    if wb.exists():
        weltbild = wb.read_text(encoding="utf-8", errors="replace")[:500]

    gedanken = []
    gd = basis / "gedanken"
    if gd.exists():
        for f in sorted(gd.glob("*.md"), reverse=True)[:4]:
            inhalt = f.read_text(encoding="utf-8", errors="replace")
            lines = [l for l in inhalt.splitlines() if l.strip() and not l.startswith("---") and not l.startswith("#")]
            auszug = " ".join(lines)[:220]
            if auszug:
                gedanken.append({"name": f.stem, "auszug": auszug})

    entwuerfe = []
    for subdir in ["gedanke", "vorstellung"]:
        ed = basis / "entwuerfe" / subdir
        if ed.exists():
            for f in sorted(ed.glob("*"), key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
                if f.is_file():
                    inhalt = f.read_text(encoding="utf-8", errors="replace")[:200]
                    entwuerfe.append({"name": f.name, "auszug": inhalt})
    entwuerfe = entwuerfe[:4]

    impulse = []
    id_ = basis / "entwuerfe" / "impuls"
    if id_.exists():
        for f in sorted(id_.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
                impulse.append({"name": f.stem, "typ": d.get("typ", "?"), "ts": d.get("ts", "")})
            except Exception:
                pass

    verlauf = lade_chat_verlauf(name, max_eintraege=9999)

    return JSONResponse({
        "weltbild": weltbild,
        "gedanken": gedanken,
        "entwuerfe": entwuerfe,
        "impulse": impulse,
        "gespraeche": len(verlauf),
    })


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(AUSWAHL_SEITE)


@app.get("/chat/{name}", response_class=HTMLResponse)
async def chat_seite(name: str):
    if name not in CODEWESEN_NAMEN:
        return HTMLResponse("<h2>Unbekanntes Codewesen</h2>")
    return HTMLResponse(CHAT_SEITE.replace("__NAME__", name))


# ── HTML ───────────────────────────────────────────────────────────────────────

AUSWAHL_SEITE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Codewesen — Auswahl</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0d0d0d; color: #e0e0e0; font-family: 'Courier New', monospace;
         min-height: 100vh; display: flex; flex-direction: column; align-items: center;
         justify-content: center; padding: 2rem; }
  h1 { font-size: 1.4rem; color: #888; letter-spacing: 0.15em; margin-bottom: 2.5rem; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 1rem; width: 100%; max-width: 700px; }
  a.wesen { display: block; background: #1a1a1a; border: 1px solid #2a2a2a;
            border-radius: 8px; padding: 1.4rem 1.2rem; text-decoration: none;
            color: #c8c8c8; transition: border-color 0.2s, background 0.2s; }
  a.wesen:hover { border-color: #555; background: #222; color: #fff; }
  .wname { font-size: 1rem; letter-spacing: 0.08em; margin-bottom: 0.3rem; }
  .wstatus { font-size: 0.75rem; color: #555; }
</style>
</head>
<body>
<h1>// CODEWESEN — DIREKTCHAT</h1>
<div class="grid">
""" + "\n".join(
    f'  <a class="wesen" href="/chat/{n}">'
    f'<div class="wname">{n}</div>'
    f'<div class="wstatus">→ chatten</div></a>'
    for n in CODEWESEN_NAMEN
) + """
</div>
</body>
</html>"""


CHAT_SEITE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__NAME__</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #0d0d0d; color: #e0e0e0; font-family: 'Courier New', monospace;
       height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
header { padding: 10px 16px; border-bottom: 1px solid #222;
         display: flex; align-items: center; gap: 12px; flex-shrink: 0; }
header a { color: #555; text-decoration: none; font-size: 13px; }
header a:hover { color: #aaa; }
h1 { font-size: 13px; letter-spacing: 2px; color: #aaa; }
#gespr-count { font-size: 10px; color: #333; margin-left: auto; letter-spacing: 1px; }
#main { flex: 1; display: flex; overflow: hidden; }
#chat-bereich { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
#verlauf { flex: 1; overflow-y: auto; padding: 16px;
           display: flex; flex-direction: column; gap: 10px; }
.msg { max-width: 80%; padding: 10px 14px; border-radius: 6px;
       line-height: 1.6; white-space: pre-wrap; font-size: 14px; }
.msg.mensch { background: #1e2a1e; color: #b8d8b8; align-self: flex-end; }
.msg.codewesen { background: #1a1a2e; color: #b8c8e8; align-self: flex-start; }
.msg.system { color: #444; font-size: 12px; align-self: center; }
.msg.warte { color: #557755; align-self: flex-start; }
.msg.warte::after { content: "▋"; display: inline-block; animation: blink 0.9s step-end infinite; }
.msg.codewesen.laedt::after { content: "▋"; display: inline-block; animation: blink 0.9s step-end infinite; }
@keyframes blink { 50% { opacity: 0; } }
#bar { display: flex; flex-direction: column; gap: 4px; padding: 8px 16px 12px;
       border-top: 1px solid #222; flex-shrink: 0; }
#modus { background: #111; border: 1px solid #2a2a2a; color: #666;
         padding: 8px 6px; border-radius: 6px; font-family: inherit; font-size: 12px; cursor: pointer; }
#eingabe { flex: 1; background: #111; border: 1px solid #2a2a2a; border-radius: 6px;
           color: #e0e0e0; padding: 8px 12px; font-family: inherit; font-size: 14px;
           resize: none; outline: none; min-height: 38px; max-height: 160px; line-height: 1.5; }
#eingabe:focus { border-color: #444; }
#btn-senden { background: #1a2a1a; border: 1px solid #2a4a2a; color: #7ab87a;
              padding: 8px 16px; border-radius: 6px; cursor: pointer;
              font-family: inherit; font-size: 14px; white-space: nowrap; }
#btn-senden:hover { background: #223022; }
#btn-senden:disabled { opacity: 0.35; cursor: default; }
#btn-auswerten { background: #1a1a2a; border: 1px solid #2a2a4a; color: #7a8ab8;
                 padding: 8px 12px; border-radius: 6px; cursor: pointer;
                 font-family: inherit; font-size: 13px; white-space: nowrap; }
#btn-auswerten:hover { background: #222240; }
#btn-auswerten:disabled { opacity: 0.35; cursor: default; }
.vorschlag-karte { background: #0d1a0d; border: 1px solid #2a4a2a; border-radius: 8px;
                   padding: 12px 14px; margin: 4px 0; max-width: 85%; align-self: flex-start; }
.vs-label { font-size: 10px; letter-spacing: 1px; color: #4a8a4a; margin-bottom: 6px; }
.vs-titel { font-size: 13px; color: #9acc9a; font-weight: bold; margin-bottom: 6px; }
.vs-inhalt { font-size: 12px; color: #778877; line-height: 1.5; margin-bottom: 10px;
             max-height: 120px; overflow-y: auto; white-space: pre-wrap; }
.vs-buttons { display: flex; gap: 8px; }
.vs-btn-ok { background: #1a2a1a; border: 1px solid #3a6a3a; color: #7ab87a;
             padding: 5px 12px; border-radius: 5px; cursor: pointer;
             font-family: inherit; font-size: 12px; }
.vs-btn-ok:hover { background: #223022; }
.vs-btn-ab { background: #1a1a1a; border: 1px solid #333; color: #666;
             padding: 5px 12px; border-radius: 5px; cursor: pointer;
             font-family: inherit; font-size: 12px; }
.vs-btn-ab:hover { background: #222; color: #888; }
/* Bild-Upload */
#bild-zeile { display: flex; align-items: center; gap: 8px; min-height: 22px; }
#btn-bild { background: none; border: 1px solid #1a1a1a; color: #444; padding: 3px 10px;
            font-family: inherit; font-size: 11px; cursor: pointer; border-radius: 3px; }
#btn-bild:hover { border-color: #333; color: #888; }
#bild-vorschau { max-height: 36px; border-radius: 3px; display: none; }
#bild-name-txt { font-size: 10px; color: #444; }
#btn-bild-leer { background: none; border: none; color: #444; cursor: pointer; font-size: 11px; display: none; }
.msg-bild { max-width: 180px; border-radius: 3px; margin-top: 6px; display: block; }
/* Zustand-Panel */
#zustand-panel { width: 240px; border-left: 1px solid #111; display: flex; flex-direction: column; overflow: hidden; }
#zp-header { padding: 10px 12px; font-size: 9px; letter-spacing: 3px; color: #2a2a2a;
             border-bottom: 1px solid #111; flex-shrink: 0; }
#zp-inhalt { flex: 1; overflow-y: auto; padding: 8px; display: flex; flex-direction: column; gap: 6px; }
.zp-block { border: 1px solid #111; border-radius: 3px; padding: 6px 8px; }
.zp-block-titel { font-size: 9px; letter-spacing: 2px; color: #333; margin-bottom: 4px; }
.zp-block-text { color: #4a4a4a; font-size: 10px; line-height: 1.4; }
.zp-item { padding: 3px 0; border-bottom: 1px solid #0f0f0f; }
.zp-item:last-child { border-bottom: none; }
.zp-item-name { font-size: 9px; color: #2a2a2a; margin-bottom: 2px; letter-spacing: 1px; }
.zp-item-text { color: #454545; font-size: 10px; line-height: 1.3; }
</style>
</head>
<body>
<header>
  <a href="/">&#8592; zurück</a>
  <h1>__NAME__</h1>
  <span id="gespr-count"></span>
  <button id="tts-btn" style="background:none;border:1px solid #1a1a1a;color:#444;padding:2px 8px;border-radius:3px;cursor:pointer;font-size:14px;margin-left:auto;" title="Stimme an/aus">&#128266;</button>
</header>
<div id="main">
  <div id="chat-bereich">
    <div id="verlauf"></div>
    <div id="bar">
      <div id="bild-zeile">
        <button id="btn-bild" onclick="document.getElementById('bild-input').click()">+ bild</button>
        <img id="bild-vorschau">
        <span id="bild-name-txt"></span>
        <button id="btn-bild-leer" onclick="bildLeeren()">&#10005;</button>
      </div>
      <div style="display:flex;gap:8px;align-items:flex-end;">
        <select id="modus">
          <option value="mittel">e4b (langsam)</option>
          <option value="schnell" selected>e2b (schnell)</option>
        </select>
        <textarea id="eingabe" rows="1" placeholder="Nachricht..."></textarea>
        <button id="btn-senden" type="button">senden</button>
        <button id="btn-auswerten" type="button">&#8853; auswerten</button>
      </div>
      <input type="file" id="bild-input" accept="image/*" style="display:none">
    </div>
  </div>
  <div id="zustand-panel">
    <div id="zp-header">ZUSTAND</div>
    <div id="zp-inhalt"><div style="color:#2a2a2a;font-size:10px;text-align:center;margin-top:20px;">laden…</div></div>
  </div>
</div>
<script>
var NAME = "__NAME__";
var verlauf = document.getElementById("verlauf");
var eingabe = document.getElementById("eingabe");
var modus   = document.getElementById("modus");
var btnSenden    = document.getElementById("btn-senden");
var btnAuswerten = document.getElementById("btn-auswerten");
var aktuellesBildB64 = null;
var aktuellerBildName = null;
var ttsAktiv = true;

document.getElementById("tts-btn").addEventListener("click", function() {
  ttsAktiv = !ttsAktiv;
  this.style.opacity = ttsAktiv ? "1" : "0.3";
  this.innerHTML = ttsAktiv ? "&#128266;" : "&#128263;";
});

function reinigeFuerTts(text) {
  return text
    .replace(/\\[MERKEN:[^\\]]*\\]/gi, "")
    .replace(/##[A-Z_]+[^#]*##/g, "")
    .replace(/```[\\s\\S]*?```/g, "")
    .replace(/`[^`]+`/g, "")
    .replace(/\\n{3,}/g, "\\n")
    .trim();
}

function ttsSplitChunks(text, maxLen) {
  var sentences = text.match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [text];
  var chunks = [];
  var current = '';
  for (var i = 0; i < sentences.length; i++) {
    var s = sentences[i];
    if (s.length > maxLen) {
      if (current) { chunks.push(current.trim()); current = ''; }
      var words = s.split(/\\s+/);
      var wcurrent = '';
      for (var j = 0; j < words.length; j++) {
        var w = words[j];
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
  return new Promise(function(resolve) {
    var url = URL.createObjectURL(blob);
    if (window._ttsAudio) {
      window._ttsAudio.pause();
      window._ttsAudio.src = '';
    }
    window._ttsAudio = new Audio(url);
    window._ttsAudio.onended = function(){ URL.revokeObjectURL(url); window._ttsAudio = null; resolve(); };
    window._ttsAudio.onerror = function(){ URL.revokeObjectURL(url); window._ttsAudio = null; resolve(); };
    window._ttsAudio.play().catch(function(){ URL.revokeObjectURL(url); window._ttsAudio = null; resolve(); });
  });
}

async function sprichText(text) {
  if (!ttsAktiv || text.trim().length < 5) return;
  var reinText = reinigeFuerTts(text);
  if (reinText.length < 5) return;
  var chunks = ttsSplitChunks(reinText, 400);
  for (var i = 0; i < chunks.length; i++) {
    var chunk = chunks[i];
    if (!chunk.trim()) continue;
    try {
      var r = await fetch("/api/tts", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({text: chunk, maennlich: true})
      });
      if (!r.ok) continue;
      var blob = await r.blob();
      if (blob.size < 100) continue;
      await playTtsBlob(blob);
    } catch(e) {}
  }
}

// ── Bild-Upload ────────────────────────────────────────────────────────────────
document.getElementById("bild-input").addEventListener("change", function() {
  var file = this.files[0];
  if (!file) return;
  var reader = new FileReader();
  reader.onload = function(e) {
    aktuellesBildB64 = e.target.result.split(",")[1];
    aktuellerBildName = file.name;
    var vorschau = document.getElementById("bild-vorschau");
    vorschau.src = e.target.result;
    vorschau.style.display = "inline-block";
    document.getElementById("bild-name-txt").textContent = file.name;
    document.getElementById("btn-bild-leer").style.display = "inline";
  };
  reader.readAsDataURL(file);
});

function bildLeeren() {
  aktuellesBildB64 = null; aktuellerBildName = null;
  document.getElementById("bild-input").value = "";
  var v = document.getElementById("bild-vorschau");
  v.src = ""; v.style.display = "none";
  document.getElementById("bild-name-txt").textContent = "";
  document.getElementById("btn-bild-leer").style.display = "none";
}

// ── Zustand-Panel ──────────────────────────────────────────────────────────────
function ladeZustand() {
  fetch("/api/zustand/" + NAME).then(function(r){ return r.json(); }).then(function(d) {
    var zpI = document.getElementById("zp-inhalt");
    zpI.innerHTML = "";
    document.getElementById("gespr-count").textContent = d.gespraeche ? d.gespraeche + " gespräche" : "";

    function block(titel, items, textFn) {
      if (!items || !items.length) return;
      var b = document.createElement("div"); b.className = "zp-block";
      var t = document.createElement("div"); t.className = "zp-block-titel"; t.textContent = titel;
      b.appendChild(t);
      items.forEach(function(it) {
        var item = document.createElement("div"); item.className = "zp-item";
        var n = document.createElement("div"); n.className = "zp-item-name"; n.textContent = it.name || "";
        var tx = document.createElement("div"); tx.className = "zp-item-text"; tx.textContent = textFn(it);
        item.appendChild(n); item.appendChild(tx); b.appendChild(item);
      });
      zpI.appendChild(b);
    }

    if (d.weltbild) {
      var wb = document.createElement("div"); wb.className = "zp-block";
      var wt = document.createElement("div"); wt.className = "zp-block-titel"; wt.textContent = "WELTBILD";
      var wtx = document.createElement("div"); wtx.className = "zp-block-text";
      wtx.textContent = d.weltbild.replace(/^---[\\s\\S]*?---/, "").trim().substring(0, 300);
      wb.appendChild(wt); wb.appendChild(wtx); zpI.appendChild(wb);
    }
    block("GEDANKEN", d.gedanken, function(it){ return it.auszug; });
    block("ENTWÜRFE", d.entwuerfe, function(it){ return it.auszug; });
    if (d.impulse && d.impulse.length) {
      block("IMPULSE", d.impulse, function(it){ return it.typ + (it.ts ? " · " + it.ts.substring(0,16) : ""); });
    }
    if (!zpI.children.length) {
      zpI.innerHTML = "<div style=\\"color:#2a2a2a;font-size:10px;text-align:center;margin-top:20px;\\">leer</div>";
    }
  }).catch(function(){});
}
ladeZustand();
setInterval(ladeZustand, 30000);

function formatTs(iso) {
  var n = iso ? new Date(iso) : new Date();
  return n.toLocaleDateString("de-DE", {day:"2-digit",month:"2-digit",year:"numeric"}) + " "
       + n.toLocaleTimeString("de-DE", {hour:"2-digit",minute:"2-digit"});
}
function msg(text, cls, iso) {
  var wrap = document.createElement("div");
  wrap.style.cssText = "display:flex;flex-direction:column;gap:2px;" + (cls==="mensch"?"align-self:flex-end;align-items:flex-end;":"align-self:flex-start;align-items:flex-start;");
  var ts = document.createElement("div");
  ts.style.cssText = "font-size:10px;color:#444;letter-spacing:1px;";
  ts.textContent = formatTs(iso);
  var d = document.createElement("div");
  d.className = "msg " + cls;
  d.style.alignSelf = "unset";
  d.textContent = text;
  wrap.appendChild(ts);
  wrap.appendChild(d);
  if (cls === "codewesen" && text) {
    var btn = document.createElement("button");
    btn.textContent = "→ Forum";
    btn.style.cssText = "background:none;border:1px solid #1a2a1a;color:#3a5a3a;font-size:10px;padding:2px 8px;border-radius:3px;cursor:pointer;font-family:inherit;align-self:flex-start;margin-top:1px;";
    btn.onmouseover = function(){ this.style.color="#7ab87a"; this.style.borderColor="#2a4a2a"; };
    btn.onmouseout  = function(){ this.style.color="#3a5a3a"; this.style.borderColor="#1a2a1a"; };
    btn.onclick = function() { direktPosten(d.textContent, btn); };
    wrap.appendChild(btn);
  }
  verlauf.appendChild(wrap);
  verlauf.scrollTop = verlauf.scrollHeight;
  return d;
}

function direktPosten(inhalt, btn) {
  var ersteZeile = inhalt.split("\\n")[0].trim();
  var titelVorschlag = ersteZeile.length > 5 ? ersteZeile.substring(0, 80) : inhalt.substring(0, 60).trim();
  var titel = prompt("Titel für den Forum-Post:", titelVorschlag);
  if (!titel) return;
  btn.disabled = true; btn.textContent = "…";
  fetch("/api/direkt-posten/" + NAME, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({titel: titel, inhalt: inhalt})
  }).then(function(r){ return r.json(); }).then(function(data){
    if (data.ok) {
      btn.textContent = "✓ gepostet #" + (data.diskussion_id || "");
      btn.style.color = "#4a8a4a"; btn.style.borderColor = "#2a5a2a";
    } else {
      btn.textContent = "Fehler"; btn.disabled = false;
    }
  }).catch(function(){ btn.textContent = "Fehler"; btn.disabled = false; });
}

fetch("/api/verlauf/" + NAME).then(function(r){ return r.json(); }).then(function(data){
  for (var i = 0; i < data.verlauf.length; i++) {
    var e = data.verlauf[i];
    var d = msg(e.inhalt, e.rolle === "mensch" ? "mensch" : "codewesen", e.ts);
  }
});

eingabe.addEventListener("keydown", function(e) {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); senden(); }
});
eingabe.addEventListener("input", function() {
  eingabe.style.height = "auto";
  eingabe.style.height = Math.min(eingabe.scrollHeight, 160) + "px";
});

btnSenden.onclick = senden;

function senden() {
  var text = eingabe.value.trim();
  if (!text && !aktuellesBildB64 || btnSenden.disabled) return;
  eingabe.value = "";
  eingabe.style.height = "auto";
  btnSenden.disabled = true;

  var hatBild = !!aktuellesBildB64;
  var bildB64 = aktuellesBildB64;
  var bildName = aktuellerBildName;
  if (hatBild) bildLeeren();

  // Nachricht mit optionalem Bild im Chat anzeigen
  var wrapMensch = document.createElement("div");
  wrapMensch.style.cssText = "display:flex;flex-direction:column;gap:2px;align-self:flex-end;align-items:flex-end;";
  var tsMensch = document.createElement("div");
  tsMensch.style.cssText = "font-size:10px;color:#444;letter-spacing:1px;";
  tsMensch.textContent = formatTs(null);
  var dMensch = document.createElement("div");
  dMensch.className = "msg mensch";
  dMensch.style.alignSelf = "unset";
  if (text) dMensch.textContent = text;
  if (hatBild) {
    var imgEl = document.createElement("img");
    imgEl.className = "msg-bild";
    imgEl.src = "data:image/jpeg;base64," + bildB64;
    dMensch.appendChild(imgEl);
  }
  wrapMensch.appendChild(tsMensch); wrapMensch.appendChild(dMensch);
  verlauf.appendChild(wrapMensch);
  verlauf.scrollTop = verlauf.scrollHeight;

  var antwort = msg("", "warte");
  var gesammelt = "";

  var payload = {nachricht: text || "", modus: modus.value};
  if (hatBild) { payload.bild_b64 = bildB64; payload.bild_name = bildName; }

  fetch("/api/chat/" + NAME, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  }).then(function(r) {
    var reader = r.body.getReader();
    var dec = new TextDecoder();
    var puffer = "";

    function lesen() {
      return reader.read().then(function(chunk) {
        if (chunk.done) { fertig(); return; }
        puffer += dec.decode(chunk.value, {stream: true});
        var zeilen = puffer.split("\\n");
        puffer = zeilen.pop();
        for (var i = 0; i < zeilen.length; i++) {
          var z = zeilen[i];
          if (!z.startsWith("data: ")) continue;
          var payload = z.slice(6);
          if (payload === "[DONE]") { fertig(); return; }
          try {
            var d = JSON.parse(payload);
            if (d.warte) {
              antwort.textContent = "";
              antwort.className = "msg warte";
            } else if (d.clear) {
              gesammelt = "";
              antwort.textContent = "";
              antwort.className = "msg codewesen laedt";
            } else if (d.token) {
              gesammelt += d.token;
              antwort.textContent = gesammelt;
              antwort.className = "msg codewesen laedt";
            } else if (d.rewrite) {
              gesammelt = d.rewrite;
              antwort.textContent = gesammelt;
            } else if (d.vorschlag) {
              zeigeVorschlag(d.vorschlag.titel, d.vorschlag.inhalt);
            } else if (d.post_veroeffentlicht) {
              var pv = d.post_veroeffentlicht;
              var karte = document.createElement("div"); karte.className = "vorschlag-karte";
              karte.innerHTML = "<div class=\\"vs-label\\" style=\\"color:#6a6\\">&#10003; Gepostet — #" + (pv.diskussion_id||"?") + " &mdash; " + (pv.titel||"") + "</div>";
              verlauf.appendChild(karte); verlauf.scrollTop = verlauf.scrollHeight;
            } else if (d.post_fehler) {
              msg("[Post-Fehler: " + d.post_fehler + "]", "system");
            }
            verlauf.scrollTop = verlauf.scrollHeight;
          } catch(e) {}
        }
        return lesen();
      });
    }

    return lesen();
  }).catch(function(err) {
    antwort.textContent = "[Fehler: " + err.message + "]";
    antwort.className = "msg system";
    fertig();
  });

  function fertig() {
    if (!gesammelt) { antwort.remove(); }
    else {
      antwort.className = "msg codewesen";
      var btn = document.createElement("button");
      btn.textContent = "→ Forum";
      btn.style.cssText = "background:none;border:1px solid #1a2a1a;color:#3a5a3a;font-size:10px;padding:2px 8px;border-radius:3px;cursor:pointer;font-family:inherit;align-self:flex-start;margin-top:1px;";
      btn.onmouseover = function(){ this.style.color="#7ab87a"; this.style.borderColor="#2a4a2a"; };
      btn.onmouseout  = function(){ this.style.color="#3a5a3a"; this.style.borderColor="#1a2a1a"; };
      btn.onclick = function() { direktPosten(antwort.textContent, btn); };
      antwort.parentElement.appendChild(btn);
      if (gesammelt.trim().length > 10) sprichText(gesammelt);
    }
    btnSenden.disabled = false;
    eingabe.focus();
    setTimeout(ladeZustand, 1500);
  }
}

function zeigeVorschlag(titel, inhalt) {
  var karte = document.createElement("div");
  karte.className = "vorschlag-karte";
  var titSafe = titel.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  var inhSafe = inhalt.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\\n/g,"<br>");
  karte.innerHTML = "<div class=\\"vs-label\\">Post-Vorschlag</div>"
    + "<div class=\\"vs-titel\\">" + titSafe + "</div>"
    + "<div class=\\"vs-inhalt\\">" + inhSafe + "</div>"
    + "<div class=\\"vs-buttons\\">"
    + "<button class=\\"vs-btn-ok\\" onclick=\\"bestaetigenPost(this)\\">&#10003; Posten</button>"
    + "<button class=\\"vs-btn-ab\\" onclick=\\"this.closest(\\'.vorschlag-karte\\').remove()\\">&#10005; Ablehnen</button>"
    + "</div>";
  karte.dataset.titel = titel;
  karte.dataset.inhalt = inhalt;
  verlauf.appendChild(karte);
  verlauf.scrollTop = verlauf.scrollHeight;
}

function bestaetigenPost(btn) {
  var karte = btn.closest(".vorschlag-karte");
  var titel = karte.dataset.titel;
  var inhalt = karte.dataset.inhalt;
  btn.disabled = true;
  btn.textContent = "… wird gepostet";
  fetch("/api/vorschlag/" + NAME, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({titel: titel, inhalt: inhalt})
  }).then(function(r){ return r.json(); }).then(function(d) {
    if (d.ok) {
      karte.innerHTML = "<div class=\\"vs-label\\" style=\\"color:#6a6\\">&#10003; Gepostet — Diskussion #" + (d.diskussion_id||"?") + "</div>";
    } else {
      karte.innerHTML = "<div class=\\"vs-label\\" style=\\"color:#a66\\">Fehler: " + (d.fehler||"unbekannt") + "</div>";
    }
  }).catch(function(e) {
    btn.textContent = "Fehler: " + e.message;
    btn.disabled = false;
  });
}

btnAuswerten.onclick = function() {
  btnAuswerten.disabled = true;
  btnAuswerten.textContent = "… läuft";
  var info = msg("Auswertung läuft…", "system");
  fetch("/api/analyse/" + NAME, {method: "POST"}).then(function(r){ return r.json(); }).then(function(data) {
    info.remove();
    if (data.fehler) { msg("Fehler: " + data.fehler, "system"); return; }
    var txt = "";
    if (data.zusammenfassung) txt += "Zusammenfassung: " + data.zusammenfassung + "\\n\\n";
    if (data.vereinbarungen && data.vereinbarungen.length) {
      txt += "Vereinbarungen:\\n";
      for (var i = 0; i < data.vereinbarungen.length; i++) {
        var v = data.vereinbarungen[i];
        txt += "  [" + v.prioritaet + "] " + v.titel + "\\n";
      }
    }
    if (txt) msg(txt.trim(), "codewesen");
  }).catch(function(e) {
    info.textContent = "Fehler: " + e.message;
  }).finally(function() {
    btnAuswerten.disabled = false;
    btnAuswerten.textContent = "\\u2853 auswerten";
  });
};
</script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="warning")
