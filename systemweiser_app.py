#!/usr/bin/env python3
"""
SystemWeiser — Standalone Web-App
Laeuft auf Port 8080, nutzt Ollama lokal (gemma4:e4b) und Bridge-API.
"""

import json
import re
import time
import base64
import os
from datetime import datetime
from typing import Optional

import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

app = FastAPI(title="SystemWeiser", version="1.0.0")

# ===== CONSTANTS =====
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma4:e4b"

SKILLS = {
    "mcp_tooling": "Werkzeugkasten (MCP Tooling) — Externe Tools als installierbare Superkraefte",
    "memory_3layer": "Gedaechtnis in 3 Schichten — Langzeit-Regeln, Entscheidungen, Session-Zustand",
    "plan_execute_verify_journal": "Planen-Ausfuehren-Pruefen-Dokumentieren (PEVJ Loop)",
    "observability_otel": "Beobachtbarkeit — OpenTelemetry fuer Logs, Traces, Metrics",
    "ownership_katalog": "Wer gehoert wem — Backstage-Style Software Catalog",
    "kanban_adaptive": "Aufgaben schrittweise — WIP-Limits, kleine Schritte",
    "moonshot_stack": "Grosser Bauplan — MCP Hub + Policy + Memory + Execution + Insight",
    "proaktives_mitdenken": "Mitdenken statt blind ausfuehren — Rueckfragen bei Risiko",
    "risk_guardian": "Sicherheitswache — Safety Matrix, Blocked Commands",
}

WESEN = [
    "geni",
    "dak_gord_system",
    "namelessAI_1234",
    "namelessAI_1324",
    "namelessAI_1423",
    "namelessAI_2341",
    "namelessAI_3123",
    "namelessAI_4321",
]

MODI = [
    "",
    "inbox",
    "outbox",
    "beobachten",
    "skill_transfer",
    "konsens",
    "changelog",
    "regelcheck",
]

BLOCKED_COMMANDS = ["rm -rf /", "format ", "dd if=", "mkfs", "shutdown", "reboot"]


# ===== BRIDGE HELPERS =====
def bridge_read(base_url: str, api_key: str, path: str) -> str:
    url = base_url.rstrip("/") + "/read"
    headers = _auth_headers(api_key)
    try:
        resp = requests.get(url, params={"path": path}, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("content", "")
    except:
        pass
    return ""


def bridge_write(base_url: str, api_key: str, path: str, content: str) -> bool:
    url = base_url.rstrip("/") + "/write"
    headers = _auth_headers(api_key)
    headers["Content-Type"] = "application/json"
    try:
        resp = requests.post(url, json={"path": path, "content": content}, headers=headers, timeout=10)
        return resp.status_code == 200
    except:
        return False


def bridge_list(base_url: str, api_key: str, path: str = ".") -> dict:
    url = base_url.rstrip("/") + "/files"
    headers = _auth_headers(api_key)
    try:
        resp = requests.get(url, params={"path": path}, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return {}


def bridge_run(base_url: str, api_key: str, cmd: str, timeout: int = 30) -> dict:
    url = base_url.rstrip("/") + "/run"
    headers = _auth_headers(api_key)
    headers["Content-Type"] = "application/json"
    try:
        resp = requests.post(url, json={"cmd": cmd, "timeout_seconds": timeout}, headers=headers, timeout=timeout + 10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        return {"error": str(e)}
    return {"error": f"HTTP {resp.status_code}"}


def _auth_headers(api_key: str) -> dict:
    h = {}
    if api_key and api_key.strip():
        h["Authorization"] = f"Bearer {api_key}"
    return h


# ===== OLLAMA =====
def ollama_generate(prompt: str, temperature: float = 0.3, json_format: bool = False) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if json_format:
        payload["format"] = "json"
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        if resp.status_code == 200:
            return resp.json().get("response", "")
        return f"Ollama-Fehler: {resp.status_code}"
    except Exception as e:
        return f"Ollama nicht erreichbar: {e}"


# ===== KONTEXT LADEN =====
def load_context(base_url: str, api_key: str, modus: str, ziel_wesen: str) -> dict:
    # 3-Layer Memory
    rules = bridge_read(base_url, api_key, "watchdog/memory/rules.md")
    decisions = bridge_read(base_url, api_key, "watchdog/memory/decisions.md")
    if decisions:
        dec_lines = decisions.strip().split("\n---\n")
        decisions = "\n---\n".join(dec_lines[-10:])
    state = bridge_read(base_url, api_key, "watchdog/memory/state.md")
    chat_history = bridge_read(base_url, api_key, "watchdog/memory/chat_history.md")
    if chat_history:
        hist_lines = chat_history.strip().split("\n---\n")
        chat_history = "\n---\n".join(hist_lines[-15:])

    parts = []
    if rules: parts.append(f"[REGELN]\n{rules}")
    if state: parts.append(f"[STATE]\n{state}")
    if decisions: parts.append(f"[ENTSCHEIDUNGEN]\n{decisions}")
    if chat_history: parts.append(f"[CHAT]\n{chat_history}")
    memory_context = "\n\n".join(parts) if parts else "(kein Gedaechtnis)"

    # Tools
    custom_tools = bridge_read(base_url, api_key, "watchdog/config/tools.md")
    tools_desc = """TOOLS:
1. read GET /read?path=... Safety:AUTO
2. write POST /write {"path":"...","content":"..."} Safety:WARN
3. files/list GET /files?path=. Safety:AUTO
4. run POST /run {"cmd":"...","timeout_seconds":30} Safety:CONFIRM
5. health GET /health Safety:AUTO

SAFETY: AUTO=direkt, WARN=bestaetigung, CONFIRM=immer bestaetigung
BLOCKED: rm -rf /, format, dd if=, mkfs, shutdown, reboot"""
    if custom_tools:
        tools_desc += f"\n\nCUSTOM:\n{custom_tools}"

    # Ownership
    ownership = bridge_read(base_url, api_key, "watchdog/config/ownership.md") or "(kein Ownership-Katalog)"

    # Inbox
    inbox_raw = ""
    if modus == "inbox":
        inbox_raw = bridge_read(base_url, api_key, "watchdog/inbox/pending.md") or "(keine Anfragen)"

    # Outbox
    outbox_raw = ""
    if modus == "outbox":
        outbox_raw = bridge_read(base_url, api_key, f"watchdog/outbox/responses_from_{ziel_wesen}.md") or "(keine Antworten)"

    # Wesen State
    wesen_state = ""
    if modus == "beobachten":
        ws = []
        for key, path in [
            ("STATE", f"{ziel_wesen}/memory/state.md"),
            ("REGELN", f"{ziel_wesen}/config/rules.md"),
            ("SKILLS", f"{ziel_wesen}/config/skills.md"),
            ("CHANGELOG", f"{ziel_wesen}/changelog/latest.md"),
        ]:
            content = bridge_read(base_url, api_key, path)
            if content: ws.append(f"[{key}]\n{content}")
        wesen_log = bridge_read(base_url, api_key, f"{ziel_wesen}/logs/latest.log")
        if wesen_log:
            ws.append(f"[LOG letzte 20]\n" + "\n".join(wesen_log.strip().split("\n")[-20:]))
        wesen_state = "\n\n".join(ws) if ws else f"(kein State fuer {ziel_wesen})"

    # Tasks
    tasks_raw = bridge_read(base_url, api_key, "watchdog/tasks/board.md") or "(kein Task-Board)"

    # Watchdog Events
    result = bridge_run(base_url, api_key, "tail -n 30 /tmp/werkraum_events.jsonl 2>/dev/null || echo '(keine Events)'", 5)
    watchdog_events = result.get("stdout", "(keine Watchdog-Events)")

    # Changelog
    changelog_raw = bridge_read(base_url, api_key, "watchdog/changelog/latest.md") or "(kein Changelog)"

    # Erkenntnisse
    erkenntnisse_raw = bridge_read(base_url, api_key, "watchdog/erkenntnisse/archiv.md") or "(keine Erkenntnisse)"

    return {
        "memory_context": memory_context,
        "tools_desc": tools_desc,
        "ownership": ownership,
        "inbox_raw": inbox_raw,
        "outbox_raw": outbox_raw,
        "wesen_state": wesen_state,
        "tasks_raw": tasks_raw,
        "watchdog_events": watchdog_events,
        "changelog_raw": changelog_raw,
        "erkenntnisse_raw": erkenntnisse_raw,
    }


# ===== MODUS ROUTER =====
def route_modus(modus: str, anweisung: str, skill_aktion: str, ziel_wesen: str,
                ctx: dict, outbox_nachricht: str, konsens_frage: str,
                konsens_als_forum: bool, forum_config: str) -> dict:
    effective = modus.strip().lower() if modus and modus.strip() else ""

    if not effective:
        a = anweisung.lower().strip()
        checks = [
            ("inbox", ["inbox", "anfragen", "eingehende", "was liegt an"]),
            ("outbox", ["schick", "sende", "nachricht an", "sag ", "outbox"]),
            ("beobachten", ["beobacht", "was macht", "zustand von", "state von", "wie geht es"]),
            ("skill_transfer", ["uebertrag", "skill", "transfer", "beibringen"]),
            ("konsens", ["konsens", "abstimmung", "alle wesen", "meinung aller"]),
            ("changelog", ["changelog", "changes", "aenderungen"]),
            ("regelcheck", ["regelcheck", "regel pruefen"]),
        ]
        for m, words in checks:
            if any(w in a for w in words):
                effective = m
                break
        if not effective:
            effective = "anweisung"

    result = {"detected_modus": effective, "show_inbox": None, "show_outbox": None,
              "show_wesen_feed": None, "show_tasks": None, "show_watchdog": None,
              "show_changelog": None, "show_erkenntnisse": None, "planer_input": ""}

    if ctx["watchdog_events"] != "(keine Watchdog-Events)":
        result["show_watchdog"] = ctx["watchdog_events"]
    if ctx["tasks_raw"] != "(kein Task-Board)":
        result["show_tasks"] = ctx["tasks_raw"]
    if ctx["changelog_raw"] != "(kein Changelog)":
        result["show_changelog"] = ctx["changelog_raw"]
    if ctx["erkenntnisse_raw"] != "(keine Erkenntnisse)":
        result["show_erkenntnisse"] = ctx["erkenntnisse_raw"]

    if effective == "inbox":
        if ctx["inbox_raw"] != "(keine Anfragen)":
            result["show_inbox"] = ctx["inbox_raw"]
        result["planer_input"] = f"MODUS: INBOX\nINBOX:\n{ctx['inbox_raw']}\nANWEISUNG: {anweisung}"

    elif effective == "outbox":
        if ctx["outbox_raw"] != "(keine Antworten)":
            result["show_outbox"] = ctx["outbox_raw"]
        msg = ""
        if outbox_nachricht and outbox_nachricht.strip():
            msg = f"\nNEUE NACHRICHT AN {ziel_wesen}:\n{outbox_nachricht}"
        result["planer_input"] = f"MODUS: OUTBOX\nKommunikation mit {ziel_wesen}{msg}\nANWEISUNG: {anweisung}"

    elif effective == "beobachten":
        result["show_wesen_feed"] = ctx["wesen_state"]
        result["planer_input"] = f"MODUS: BEOBACHTEN\nWESEN-STATE:\n{ctx['wesen_state']}\nANWEISUNG: {anweisung}"

    elif effective == "skill_transfer":
        result["planer_input"] = (
            f"MODUS: SKILL TRANSFER\nUebertrage '{skill_aktion}' an '{ziel_wesen}'.\n"
            f"1. Erstelle/ergaenze {ziel_wesen}/config/skills.md\n"
            f"2. Changelog in {ziel_wesen}/changelog/latest.md\n"
            f"3. Selbst-Check: {ziel_wesen}/changelog/check_{skill_aktion}.md\n"
            f"OWNERSHIP:\n{ctx['ownership']}\nANWEISUNG: {anweisung}"
        )

    elif effective == "konsens":
        forum = ""
        if konsens_als_forum and forum_config:
            forum = f"\nALS FORUMBEITRAG: Ja\nFORUM-CONFIG: {forum_config}\nSEQUENTIELL!"
        result["planer_input"] = (
            f"MODUS: KONSENS\nFRAGE: {konsens_frage}\n"
            f"Alle Codewesen sollen Stellung nehmen.{forum}\n"
            f"SEQUENTIELL, nie gleichzeitig!\nANWEISUNG: {anweisung}"
        )

    elif effective == "changelog":
        result["planer_input"] = f"MODUS: CHANGELOG\nChangelog:\n{ctx['changelog_raw']}\nANWEISUNG: {anweisung}"

    elif effective == "regelcheck":
        result["planer_input"] = (
            f"MODUS: REGELCHECK\nPruefe Regeln fuer {ziel_wesen}.\n"
            f"OWNERSHIP:\n{ctx['ownership']}\nANWEISUNG: {anweisung}"
        )

    else:
        extra = ""
        if skill_aktion and skill_aktion != "(keine)":
            extra += f"\nSKILL: {skill_aktion}"
        if ziel_wesen != "geni":
            extra += f"\nZIEL-WESEN: {ziel_wesen}"
        result["planer_input"] = f"MODUS: ANWEISUNG{extra}\nANWEISUNG: {anweisung}"

    return result


# ===== PLANER PROMPT =====
def build_planer_prompt(ctx: dict, planer_input: str) -> str:
    return f"""SYSTEMWEISER. VOLLER ZUGRIFF.

OBSIDIAN-REGELN:
- Jede neue Datei: Frontmatter (tags, created, type, links)
- Wikilinks: [[pfad/zur/datei]]
- Tags: #systemweiser #wesen #changelog #erkenntnis #konsens #task
- Graph-kompatibel

SICHTBARKEIT:
- geni sieht IMMER ALLES
- Codewesen sehen NICHT: watchdog/erkenntnisse/, watchdog/memory/, watchdog/config/
- Erkenntnisse-Archiv: erst nach Freigabe

{ctx['tools_desc']}

{ctx['memory_context']}

OWNERSHIP:
{ctx['ownership']}

TASKS:
{ctx['tasks_raw']}

WATCHDOG-EVENTS:
{ctx['watchdog_events']}

{planer_input}

Plan-Execute-Verify:
1. Was wird verlangt?
2. Welche Tools, welche Reihenfolge?
3. Welches Wesen betroffen?
4. Obsidian: Frontmatter, Wikilinks, Tags?
5. Changelog noetig?
6. Risiken? Safety?

NUR JSON-Array:
[{{"step":1,"action":"read|write|list|exec|status","endpoint":"/read|/write|/files|/run|/health","method":"GET|POST","body":{{}},"safety":"AUTO|WARN|CONFIRM","reason":"warum"}}]

BLOCKED: rm -rf /, format, dd if=, mkfs, shutdown, reboot"""


# ===== PLAN PARSER =====
def parse_plan(raw: str) -> dict:
    steps = []
    try:
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            steps = json.loads(match.group())
    except:
        steps = [{"step": 1, "action": "list", "endpoint": "/files", "method": "GET",
                  "body": {"path": "."}, "safety": "AUTO", "reason": "Fallback: Struktur anzeigen"}]

    has_confirm = False
    safe_steps = []
    summaries = []

    for s in steps:
        cmd = str(s.get("body", {}).get("cmd", ""))
        if any(b in cmd for b in BLOCKED_COMMANDS):
            summaries.append(f"BLOCKED: {s.get('reason', '?')}")
            continue
        safety = s.get("safety", "AUTO")
        if safety in ("CONFIRM", "WARN"):
            has_confirm = True
        safe_steps.append(s)
        summaries.append(f"{s.get('step', '?')}. [{safety}] {s.get('action', '?')}: {s.get('reason', '?')}")

    return {
        "steps": safe_steps,
        "has_confirm": has_confirm,
        "plan_summary": "\n".join(summaries) or "Keine Schritte geplant.",
    }


# ===== EXECUTE STEPS =====
def execute_steps(steps: list, base_url: str, api_key: str) -> list:
    results = []
    headers = _auth_headers(api_key)
    headers["Content-Type"] = "application/json"

    for s in steps:
        endpoint = s.get("endpoint", "")
        method = s.get("method", "POST").upper()
        body = s.get("body", {})
        url = base_url.rstrip("/") + endpoint

        start = time.time()
        try:
            if method == "GET":
                resp = requests.get(url, params=body, headers=headers, timeout=30)
            else:
                resp = requests.post(url, json=body, headers=headers, timeout=30)
            elapsed = round(time.time() - start, 2)
            try:
                data = resp.json()
            except:
                data = resp.text[:2000]
            results.append({
                "step": s.get("step"), "status": resp.status_code,
                "data": data, "duration_s": elapsed,
                "action": s.get("action"), "reason": s.get("reason"),
            })
        except Exception as e:
            results.append({"step": s.get("step"), "status": "error", "data": str(e),
                            "duration_s": round(time.time() - start, 2)})
    return results


# ===== VERIFY =====
def verify_results(anweisung: str, plan_summary: str, results: list) -> str:
    results_text = "\n".join(
        json.dumps(r, ensure_ascii=False, default=str)[:500] for r in results if r
    ) or "(keine Ergebnisse)"

    prompt = f"""VERIFY: Pruefe ob die Ergebnisse zur Anweisung passen.

ANWEISUNG: {anweisung}
PLAN: {plan_summary}
ERGEBNISSE: {results_text}

Antwort als JSON:
{{"success":true/false,"summary":"was passiert ist","issues":"probleme oder leer","decision_note":"","task_update":"","ownership_change":"","changelog_entry":"","erkenntnis":""}}"""

    return ollama_generate(prompt, temperature=0.3, json_format=True)


# ===== FORMAT =====
def format_output(anweisung: str, verify: str, results: list) -> str:
    raw_parts = []
    for r in results:
        if r:
            d = r.get("data", "")
            if isinstance(d, dict):
                raw_parts.append(json.dumps(d, ensure_ascii=False, indent=2, default=str)[:1000])
            else:
                raw_parts.append(str(d)[:1000])
    raw_text = "\n---\n".join(raw_parts) or "(leer)"

    prompt = f"""Formatiere als klare Antwort auf Deutsch.

ANWEISUNG: {anweisung}
VERIFY: {verify}
ROH-DATEN: {raw_text}

Regeln:
- Baumstrukturen eingerueckt
- Code in Bloecken
- Kurz und praezise
- Bei Fehlern: was schief ging + Vorschlag
- Wikilinks erwaehnen wo relevant"""

    return ollama_generate(prompt, temperature=0.5)


# ===== JOURNAL =====
def save_journal(base_url: str, api_key: str, anweisung: str, modus: str,
                 ziel_wesen: str, skill_aktion: str, plan_summary: str,
                 verify_result: str, formatted_response: str) -> dict:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Chat History
    chat_entry = (
        f"---\ntags: [systemweiser, chat]\ncreated: {now}\ntype: chat\n"
        f"links: [[watchdog/memory/state]]\n---\n## {now}\n"
        f"**Modus:** {modus} | **Wesen:** {ziel_wesen} | **Skill:** {skill_aktion}\n"
        f"**Anweisung:** {anweisung}\n**Plan:** {plan_summary}\n"
        f"**Antwort:** {formatted_response}\n"
    )
    existing = bridge_read(base_url, api_key, "watchdog/memory/chat_history.md")
    bridge_write(base_url, api_key, "watchdog/memory/chat_history.md",
                 (existing + "\n---\n" + chat_entry) if existing else chat_entry)

    # Parse verify
    try:
        vd = json.loads(verify_result) if verify_result else {}
    except:
        vd = {}

    # Decision log
    dn = vd.get("decision_note", "")
    if dn and dn.strip():
        existing = bridge_read(base_url, api_key, "watchdog/memory/decisions.md")
        entry = f"---\ntags: [systemweiser, entscheidung]\ncreated: {now}\ntype: decision\n---\n## {now}\n{dn}\n"
        bridge_write(base_url, api_key, "watchdog/memory/decisions.md",
                     (existing + "\n---\n" + entry) if existing else entry)

    # Changelog
    cl = vd.get("changelog_entry", "")
    if cl and cl.strip() and ziel_wesen:
        existing = bridge_read(base_url, api_key, f"{ziel_wesen}/changelog/latest.md")
        entry = (
            f"---\ntags: [changelog, {ziel_wesen}]\ncreated: {now}\ntype: changelog\n"
            f"links: [[watchdog/config/ownership]]\n---\n## {now}\n{cl}\n"
        )
        bridge_write(base_url, api_key, f"{ziel_wesen}/changelog/latest.md",
                     (existing + "\n---\n" + entry) if existing else f"# Changelog {ziel_wesen}\n\n{entry}")
        # Self-check
        check = (
            f"---\ntags: [changelog, selbstcheck, {ziel_wesen}]\ncreated: {now}\ntype: self_check\n---\n"
            f"# Selbst-Check\n## Was wurde geaendert?\n{cl}\n"
            f"## Wie verstehe ich die Aenderung?\n(Wird vom Wesen ausgefuellt)\n"
            f"## Was koennte es ausloesen?\n(Wird vom Wesen ausgefuellt)\n"
        )
        bridge_write(base_url, api_key,
                     f"{ziel_wesen}/changelog/check_{now.replace(' ', '_').replace(':', '-')}.md", check)

    # Erkenntnisse
    erk = vd.get("erkenntnis", "")
    if erk and erk.strip():
        existing = bridge_read(base_url, api_key, "watchdog/erkenntnisse/archiv.md")
        entry = f"---\ntags: [erkenntnis, {ziel_wesen}]\ncreated: {now}\ntype: erkenntnis\n---\n## {now} — {ziel_wesen}\n{erk}\n"
        bridge_write(base_url, api_key, "watchdog/erkenntnisse/archiv.md",
                     (existing + "\n---\n" + entry) if existing else f"# Erkenntnisse-Archiv\n\n{entry}")

    # Log
    log = f"{now} | modus={modus} wesen={ziel_wesen} skill={skill_aktion} | {anweisung[:60]}\n"
    existing = bridge_read(base_url, api_key, "watchdog/logs/traces.log")
    bridge_write(base_url, api_key, "watchdog/logs/traces.log", (existing + log) if existing else log)

    # State
    state = (
        f"---\ntags: [systemweiser, state]\nupdated: {now}\ntype: state\n---\n"
        f"# SystemWeiser State\nLetzte Aktion: {now}\nModus: {modus}\n"
        f"Ziel-Wesen: {ziel_wesen}\nStatus: {'OK' if vd.get('success', True) else 'FEHLER'}\n"
    )
    bridge_write(base_url, api_key, "watchdog/memory/state.md", state)

    # Tasks
    tu = vd.get("task_update", "")
    if tu and tu.strip():
        existing = bridge_read(base_url, api_key, "watchdog/tasks/board.md")
        if not existing:
            existing = "---\ntags: [systemweiser, tasks]\ntype: kanban\n---\n# Task Board\n\n## TODO\n\n## DOING\n\n## DONE\n"
        existing = existing.replace("## TODO", f"## TODO\n- [{now}] {tu}", 1)
        bridge_write(base_url, api_key, "watchdog/tasks/board.md", existing)

    # Ownership
    oc = vd.get("ownership_change", "")
    if oc and oc.strip():
        existing = bridge_read(base_url, api_key, "watchdog/config/ownership.md")
        if not existing:
            existing = "---\ntags: [systemweiser, ownership]\ntype: registry\n---\n# Ownership Katalog\n\n"
        bridge_write(base_url, api_key, "watchdog/config/ownership.md", existing + f"## Update {now}\n{oc}\n\n")

    return {"saved": True, "memory": state}


# ===== HTML UI =====
HTML_PAGE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SystemWeiser</title>
<style>
  :root { --bg: #0d1117; --card: #161b22; --border: #30363d; --text: #e6edf3;
          --muted: #8b949e; --accent: #58a6ff; --green: #3fb950; --red: #f85149;
          --orange: #d29922; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
         background: var(--bg); color: var(--text); line-height: 1.6; }
  .container { max-width: 900px; margin: 0 auto; padding: 20px; }
  h1 { color: var(--accent); margin-bottom: 8px; font-size: 1.8em; }
  h1 span { color: var(--muted); font-size: 0.5em; font-weight: normal; }
  .subtitle { color: var(--muted); margin-bottom: 24px; }
  .phase { background: var(--card); border: 1px solid var(--border); border-radius: 8px;
           padding: 20px; margin-bottom: 16px; }
  .phase-title { color: var(--accent); font-size: 1.1em; margin-bottom: 16px;
                 padding-bottom: 8px; border-bottom: 1px solid var(--border); }
  .field { margin-bottom: 16px; }
  .field label { display: block; color: var(--text); font-weight: 600; margin-bottom: 4px; }
  .field .hint { color: var(--muted); font-size: 0.85em; margin-bottom: 4px; }
  input[type="text"], input[type="password"], textarea, select {
    width: 100%; padding: 10px 12px; background: var(--bg); color: var(--text);
    border: 1px solid var(--border); border-radius: 6px; font-size: 0.95em;
    font-family: inherit; }
  input:focus, textarea:focus, select:focus { outline: none; border-color: var(--accent); }
  textarea { min-height: 100px; resize: vertical; }
  select { cursor: pointer; }
  .toggle-row { display: flex; align-items: center; gap: 10px; }
  .toggle { position: relative; width: 44px; height: 24px; cursor: pointer; }
  .toggle input { opacity: 0; width: 0; height: 0; }
  .toggle .slider { position: absolute; inset: 0; background: var(--border); border-radius: 12px;
                    transition: 0.2s; }
  .toggle .slider::before { content: ""; position: absolute; width: 18px; height: 18px;
                            left: 3px; top: 3px; background: var(--muted); border-radius: 50%;
                            transition: 0.2s; }
  .toggle input:checked + .slider { background: var(--accent); }
  .toggle input:checked + .slider::before { transform: translateX(20px); background: white; }

  .btn-run { display: block; width: 100%; padding: 14px; background: var(--accent); color: #000;
             border: none; border-radius: 8px; font-size: 1.1em; font-weight: 700;
             cursor: pointer; margin-top: 8px; transition: 0.15s; }
  .btn-run:hover { background: #79c0ff; }
  .btn-run:disabled { background: var(--border); color: var(--muted); cursor: not-allowed; }
  .btn-run:active { transform: scale(0.98); }

  .status { margin-top: 16px; padding: 12px 16px; border-radius: 8px; display: none; }
  .status.running { display: block; background: #0d1f3c; border: 1px solid var(--accent);
                    color: var(--accent); }
  .status.error { display: block; background: #2d1216; border: 1px solid var(--red);
                  color: var(--red); }

  .results { margin-top: 24px; display: none; }
  .results.visible { display: block; }
  .result-card { background: var(--card); border: 1px solid var(--border); border-radius: 8px;
                 padding: 16px; margin-bottom: 12px; }
  .result-card h3 { color: var(--green); margin-bottom: 8px; font-size: 1em; }
  .result-card pre { background: var(--bg); padding: 12px; border-radius: 6px;
                     overflow-x: auto; font-size: 0.85em; white-space: pre-wrap;
                     word-break: break-word; max-height: 400px; overflow-y: auto; }
  .result-card.empty { display: none; }

  .confirm-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7);
                     display: flex; align-items: center; justify-content: center; z-index: 100; }
  .confirm-box { background: var(--card); border: 1px solid var(--orange); border-radius: 12px;
                 padding: 24px; max-width: 600px; width: 90%; }
  .confirm-box h3 { color: var(--orange); margin-bottom: 12px; }
  .confirm-box pre { background: var(--bg); padding: 12px; border-radius: 6px;
                     margin-bottom: 16px; white-space: pre-wrap; font-size: 0.9em;
                     max-height: 300px; overflow-y: auto; }
  .confirm-buttons { display: flex; gap: 12px; }
  .confirm-buttons button { flex: 1; padding: 10px; border: none; border-radius: 6px;
                            font-size: 1em; font-weight: 600; cursor: pointer; }
  .btn-approve { background: var(--green); color: #000; }
  .btn-reject { background: var(--red); color: white; }

  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
  .running { animation: pulse 1.5s infinite; }

  .skill-legend { color: var(--muted); font-size: 0.82em; margin-top: 6px; line-height: 1.5; }
</style>
</head>
<body>
<div class="container">
  <h1>SystemWeiser <span>v1.0</span></h1>
  <p class="subtitle">Autonomer Orchestrator fuer alle Wesen</p>

  <form id="mainForm" onsubmit="return false;">

  <!-- Phase 1: Verbindung -->
  <div class="phase">
    <div class="phase-title">Verbindung</div>
    <div class="field">
      <label>VPS Base URL</label>
      <input type="text" id="base_url" value="http://217.154.14.29:8001">
    </div>
    <div class="field">
      <label>Bridge API Key</label>
      <div class="hint">Leer lassen wenn kein Token gesetzt</div>
      <input type="password" id="api_key" placeholder="Bearer Token...">
    </div>
  </div>

  <!-- Phase 2: Anweisung -->
  <div class="phase">
    <div class="phase-title">Anweisung</div>
    <div class="field">
      <label>Deine Anweisung</label>
      <textarea id="anweisung" placeholder="Was soll SystemWeiser tun?">Zeig mir die Projektstruktur</textarea>
    </div>
    <div class="field">
      <label>Modus</label>
      <div class="hint">Leer = automatische Erkennung aus der Anweisung</div>
      <select id="modus">
        <option value="">(automatisch)</option>
        <option value="inbox">Inbox — Anfragen anderer Wesen</option>
        <option value="outbox">Outbox — Nachricht an ein Wesen</option>
        <option value="beobachten">Beobachten — Zustand eines Wesens</option>
        <option value="skill_transfer">Skill Transfer — Faehigkeit uebertragen</option>
        <option value="konsens">Konsens — Abstimmung aller Wesen</option>
        <option value="changelog">Changelog — Aenderungen pruefen</option>
        <option value="regelcheck">Regelcheck — Regel pruefen</option>
      </select>
    </div>
    <div class="field">
      <label>Ziel-Wesen</label>
      <select id="ziel_wesen">
        <option value="geni" selected>geni (du)</option>
        <option value="dak_gord_system">dak_gord_system (Gesamtsystem)</option>
        <option value="namelessAI_1234">namelessAI_1234 (reflexion)</option>
        <option value="namelessAI_1324">namelessAI_1324 (reflexion)</option>
        <option value="namelessAI_1423">namelessAI_1423 (reflexion)</option>
        <option value="namelessAI_2341">namelessAI_2341 (kritik)</option>
        <option value="namelessAI_3123">namelessAI_3123 (kritik)</option>
        <option value="namelessAI_4321">namelessAI_4321 (kritik)</option>
      </select>
    </div>
  </div>

  <!-- Phase 3: Erweitert -->
  <div class="phase">
    <div class="phase-title">Erweitert</div>
    <div class="field">
      <label>Skill zum Uebertragen</label>
      <select id="skill_aktion">
        <option value="(keine)">(keine)</option>
        <option value="mcp_tooling">Werkzeugkasten (MCP Tooling)</option>
        <option value="memory_3layer">Gedaechtnis in 3 Schichten</option>
        <option value="plan_execute_verify_journal">Planen-Ausfuehren-Pruefen-Dokumentieren</option>
        <option value="observability_otel">Beobachtbarkeit (Observability)</option>
        <option value="ownership_katalog">Wer gehoert wem (Ownership)</option>
        <option value="kanban_adaptive">Aufgaben schrittweise (Kanban)</option>
        <option value="moonshot_stack">Grosser Bauplan (Moonshot)</option>
        <option value="proaktives_mitdenken">Mitdenken statt blind ausfuehren</option>
        <option value="risk_guardian">Sicherheitswache (Risk Guardian)</option>
      </select>
      <div class="skill-legend">
        <strong>Legende:</strong><br>
        Werkzeugkasten — Externe Tools als Superkraefte einbinden, Scopes, Trust<br>
        Gedaechtnis — Langzeit-Regeln, Entscheidungen, Session-Zustand<br>
        PEVJ Loop — Intake → Plan → Execute → Verify → Journal<br>
        Beobachtbarkeit — OpenTelemetry fuer Logs, Traces, Metrics<br>
        Ownership — Backstage-Style Catalog, nichts verwaist<br>
        Kanban — WIP-Limits, kleine Schritte, Repriorisierung<br>
        Moonshot — MCP Hub + Policy + Memory + Execution + Insight<br>
        Mitdenken — Rueckfragen bei Risiko, Alternativen, Unklarheit<br>
        Sicherheitswache — Safety Matrix, Blocked Commands, WARN/CONFIRM
      </div>
    </div>
    <div class="field">
      <label>Outbox Nachricht</label>
      <div class="hint">Nur relevant bei Modus "Outbox"</div>
      <textarea id="outbox_nachricht" rows="3" placeholder="Nachricht an das Ziel-Wesen..."></textarea>
    </div>
    <div class="field">
      <label>Konsens-Frage</label>
      <div class="hint">Nur relevant bei Modus "Konsens"</div>
      <textarea id="konsens_frage" rows="3" placeholder="Frage an alle Wesen..."></textarea>
    </div>
    <div class="field">
      <div class="toggle-row">
        <label class="toggle"><input type="checkbox" id="konsens_als_forum"><span class="slider"></span></label>
        <span>Konsens als Forumbeitrag</span>
      </div>
    </div>
    <div class="field">
      <label>Forum-Config</label>
      <div class="hint">Haupttag, Subtag, Regeln fuer den Forumbeitrag</div>
      <input type="text" id="forum_config" placeholder="z.B. Deep Dive, Theorie & Philosophie">
    </div>
  </div>

  <!-- SENDEN BUTTON -->
  <button type="button" class="btn-run" id="btnRun" onclick="runSystemWeiser()">
    Ausfuehren
  </button>

  </form>

  <div class="status" id="status"></div>

  <!-- Confirm overlay -->
  <div class="confirm-overlay" id="confirmOverlay" style="display:none;">
    <div class="confirm-box">
      <h3>Bestaetigung noetig</h3>
      <p style="color:var(--muted);margin-bottom:12px;">Mindestens ein Schritt hat Safety WARN oder CONFIRM:</p>
      <pre id="confirmPlan"></pre>
      <div class="confirm-buttons">
        <button class="btn-approve" onclick="confirmPlan(true)">Genehmigen</button>
        <button class="btn-reject" onclick="confirmPlan(false)">Ablehnen</button>
      </div>
    </div>
  </div>

  <!-- Results -->
  <div class="results" id="results">
    <div class="result-card" id="res_main">
      <h3>Ergebnis</h3>
      <pre id="res_main_text"></pre>
    </div>
    <div class="result-card" id="res_memory">
      <h3>Memory Feed</h3>
      <pre id="res_memory_text"></pre>
    </div>
    <div class="result-card" id="res_wesen">
      <h3>Wesen Feed</h3>
      <pre id="res_wesen_text"></pre>
    </div>
    <div class="result-card" id="res_tasks">
      <h3>Task Board</h3>
      <pre id="res_tasks_text"></pre>
    </div>
    <div class="result-card" id="res_watchdog">
      <h3>Watchdog Events</h3>
      <pre id="res_watchdog_text"></pre>
    </div>
    <div class="result-card" id="res_changelog">
      <h3>Changelog</h3>
      <pre id="res_changelog_text"></pre>
    </div>
    <div class="result-card" id="res_erkenntnisse">
      <h3>Erkenntnisse-Archiv (nur fuer dich)</h3>
      <pre id="res_erkenntnisse_text"></pre>
    </div>
    <div class="result-card" id="res_outbox">
      <h3>Outbox Feed</h3>
      <pre id="res_outbox_text"></pre>
    </div>
  </div>
</div>

<script>
let pendingResolve = null;

function setStatus(msg, type) {
  const el = document.getElementById('status');
  el.textContent = msg;
  el.className = 'status ' + type;
}

function showResult(id, text) {
  const card = document.getElementById('res_' + id);
  const pre = document.getElementById('res_' + id + '_text');
  if (text && text.trim()) {
    pre.textContent = text;
    card.classList.remove('empty');
  } else {
    card.classList.add('empty');
  }
}

function confirmPlan(approved) {
  document.getElementById('confirmOverlay').style.display = 'none';
  if (pendingResolve) pendingResolve(approved);
}

async function runSystemWeiser() {
  const btn = document.getElementById('btnRun');
  btn.disabled = true;
  btn.textContent = 'Laeuft...';
  document.getElementById('results').classList.remove('visible');

  const data = {
    base_url: document.getElementById('base_url').value,
    api_key: document.getElementById('api_key').value,
    anweisung: document.getElementById('anweisung').value,
    modus: document.getElementById('modus').value,
    ziel_wesen: document.getElementById('ziel_wesen').value,
    skill_aktion: document.getElementById('skill_aktion').value,
    outbox_nachricht: document.getElementById('outbox_nachricht').value,
    konsens_frage: document.getElementById('konsens_frage').value,
    konsens_als_forum: document.getElementById('konsens_als_forum').checked,
    forum_config: document.getElementById('forum_config').value,
  };

  try {
    // Step 1: Plan
    setStatus('Kontext laden + Plan erstellen (Ollama denkt nach)...', 'running');
    const planResp = await fetch('/api/plan', {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)
    });
    const planData = await planResp.json();
    if (planData.error) throw new Error(planData.error);

    // Show feeds
    showResult('wesen', planData.feeds?.wesen_feed || '');
    showResult('tasks', planData.feeds?.tasks || '');
    showResult('watchdog', planData.feeds?.watchdog || '');
    showResult('changelog', planData.feeds?.changelog || '');
    showResult('erkenntnisse', planData.feeds?.erkenntnisse || '');
    showResult('outbox', planData.feeds?.outbox || '');
    showResult('inbox', planData.feeds?.inbox || '');

    // Step 2: Confirm if needed
    let approved = true;
    if (planData.has_confirm) {
      setStatus('Bestaetigung noetig...', 'running');
      document.getElementById('confirmPlan').textContent = planData.plan_summary;
      document.getElementById('confirmOverlay').style.display = 'flex';
      approved = await new Promise(resolve => { pendingResolve = resolve; });
    }

    if (!approved) {
      setStatus('Abgelehnt.', 'error');
      showResult('main', 'Plan wurde abgelehnt.');
      document.getElementById('results').classList.add('visible');
      btn.disabled = false;
      btn.textContent = 'Ausfuehren';
      return;
    }

    // Step 3: Execute + Verify + Format + Journal
    setStatus('Ausfuehren + Pruefen + Formatieren + Speichern...', 'running');
    const execResp = await fetch('/api/execute', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ ...data, steps: planData.steps, plan_summary: planData.plan_summary })
    });
    const execData = await execResp.json();
    if (execData.error) throw new Error(execData.error);

    showResult('main', execData.formatted);
    showResult('memory', execData.memory);
    document.getElementById('results').classList.add('visible');
    setStatus('', '');

  } catch (e) {
    setStatus('Fehler: ' + e.message, 'error');
    showResult('main', 'Fehler: ' + e.message);
    document.getElementById('results').classList.add('visible');
  }

  btn.disabled = false;
  btn.textContent = 'Ausfuehren';
}
</script>
</body>
</html>"""


# ===== API ENDPOINTS =====
@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_PAGE


@app.post("/api/plan")
async def api_plan(request: Request):
    try:
        data = await request.json()
        base_url = data["base_url"]
        api_key = data.get("api_key", "")
        anweisung = data["anweisung"]
        modus = data.get("modus", "")
        ziel_wesen = data.get("ziel_wesen", "geni")
        skill_aktion = data.get("skill_aktion", "(keine)")
        outbox_nachricht = data.get("outbox_nachricht", "")
        konsens_frage = data.get("konsens_frage", "")
        konsens_als_forum = data.get("konsens_als_forum", False)
        forum_config = data.get("forum_config", "")

        # Load context
        ctx = load_context(base_url, api_key, modus, ziel_wesen)

        # Route modus
        routed = route_modus(modus, anweisung, skill_aktion, ziel_wesen, ctx,
                             outbox_nachricht, konsens_frage, konsens_als_forum, forum_config)

        # Build planer prompt and call Ollama
        prompt = build_planer_prompt(ctx, routed["planer_input"])
        raw_plan = ollama_generate(prompt, temperature=0.3)

        # Parse plan
        parsed = parse_plan(raw_plan)

        return {
            "steps": parsed["steps"],
            "has_confirm": parsed["has_confirm"],
            "plan_summary": parsed["plan_summary"],
            "raw_plan": raw_plan,
            "detected_modus": routed["detected_modus"],
            "feeds": {
                "wesen_feed": routed["show_wesen_feed"],
                "tasks": routed["show_tasks"],
                "watchdog": routed["show_watchdog"],
                "changelog": routed["show_changelog"],
                "erkenntnisse": routed["show_erkenntnisse"],
                "outbox": routed["show_outbox"],
                "inbox": routed["show_inbox"],
            },
        }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/execute")
async def api_execute(request: Request):
    try:
        data = await request.json()
        base_url = data["base_url"]
        api_key = data.get("api_key", "")
        anweisung = data["anweisung"]
        steps = data["steps"]
        plan_summary = data["plan_summary"]
        modus = data.get("modus", "")
        ziel_wesen = data.get("ziel_wesen", "geni")
        skill_aktion = data.get("skill_aktion", "(keine)")

        # Execute
        results = execute_steps(steps, base_url, api_key)

        # Verify
        verify = verify_results(anweisung, plan_summary, results)

        # Format
        formatted = format_output(anweisung, verify, results)

        # Journal
        journal = save_journal(base_url, api_key, anweisung, modus, ziel_wesen,
                               skill_aktion, plan_summary, verify, formatted)

        return {
            "formatted": formatted,
            "verify": verify,
            "results": results,
            "memory": journal.get("memory", ""),
        }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/health")
def health():
    return {"status": "ok", "app": "SystemWeiser"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
