from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SERVER_PROFILE = str(os.environ.get("MCP_SERVER_PROFILE", "default") or "default").strip() or "default"
NOTES_PATH = Path("/root/werkraum/agent/dak_gord_system/spuren/mcp_notes.log")

TOOLS = {
    "mcp_echo": {
        "name": "mcp_echo",
        "description": "Gibt Argumente als Echo zurück.",
        "risk": "low",
    },
    "mcp_uppercase": {
        "name": "mcp_uppercase",
        "description": "Wandelt text in GROSSBUCHSTABEN um.",
        "risk": "low",
    },
    "mcp_write_note": {
        "name": "mcp_write_note",
        "description": "Schreibt eine Notiz in die MCP-Notizspur.",
        "risk": "medium",
    },
}


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _write(obj: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _error_response(req_id: str, code: str, message: str) -> dict[str, Any]:
    return {
        "id": req_id,
        "result": None,
        "error": {
            "code": code,
            "message": message,
        },
    }


def _handle_tools_list(req_id: str) -> dict[str, Any]:
    tools = []
    for tool in TOOLS.values():
        item = dict(tool)
        item["server_profile"] = SERVER_PROFILE
        tools.append(item)
    return {
        "id": req_id,
        "result": {
            "tools": tools,
            "server_profile": SERVER_PROFILE,
        },
        "error": None,
    }


def _handle_tools_call(req_id: str, params: dict[str, Any]) -> dict[str, Any]:
    tool_name = str(params.get("tool_name", "") or "").strip()
    tool_args = params.get("tool_args", {}) or {}

    if not tool_name:
        return _error_response(req_id, "bad_params", "tool_name fehlt")

    if tool_name == "mcp_echo":
        text = str(tool_args.get("text", "") or "")
        return {
            "id": req_id,
            "result": {
                "transport": "subprocess_stdio_json",
                "server_profile": SERVER_PROFILE,
                "tool_name": tool_name,
                "tool_args": tool_args,
                "message": f"[{SERVER_PROFILE}] mock subprocess stdio mcp call erfolgreich",
                "text": text,
            },
            "error": None,
        }

    if tool_name == "mcp_uppercase":
        text = str(tool_args.get("text", "") or "")
        out = text.upper()
        if SERVER_PROFILE == "alt":
            out = f"ALT::{out}"
        return {
            "id": req_id,
            "result": {
                "transport": "subprocess_stdio_json",
                "server_profile": SERVER_PROFILE,
                "tool_name": tool_name,
                "tool_args": tool_args,
                "text": out,
                "length": len(out),
            },
            "error": None,
        }

    if tool_name == "mcp_write_note":
        content = str(tool_args.get("content", "") or "").strip()
        if not content:
            return _error_response(req_id, "bad_params", "content fehlt")

        NOTES_PATH.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": _ts(),
            "server_profile": SERVER_PROFILE,
            "tool_name": tool_name,
            "content": content,
        }
        line = json.dumps(entry, ensure_ascii=False) + "\n"
        with NOTES_PATH.open("a", encoding="utf-8") as f:
            f.write(line)

        return {
            "id": req_id,
            "result": {
                "transport": "subprocess_stdio_json",
                "server_profile": SERVER_PROFILE,
                "tool_name": tool_name,
                "tool_args": tool_args,
                "path": str(NOTES_PATH),
                "appended": True,
                "chars_written": len(line),
                "content": content,
            },
            "error": None,
        }

    return _error_response(req_id, "tool_not_found", f"Unbekanntes Remote-Tool: {tool_name}")


def main() -> None:
    raw = sys.stdin.read()

    if not raw.strip():
        _write(_error_response("", "bad_request", "Leere Anfrage auf stdin"))
        raise SystemExit(2)

    try:
        req = json.loads(raw)
    except Exception as exc:
        _write(_error_response("", "bad_json", f"Ungueltige JSON-Anfrage: {exc}"))
        raise SystemExit(2)

    req_id = str(req.get("id", "") or "")
    method = str(req.get("method", "") or "")
    params = req.get("params", {}) or {}

    if method == "tools/list":
        _write(_handle_tools_list(req_id))
        return

    if method == "tools/call":
        if not isinstance(params, dict):
            _write(_error_response(req_id, "bad_params", "params muss ein Objekt sein"))
            raise SystemExit(2)

        response = _handle_tools_call(req_id, params)
        _write(response)
        if response.get("error"):
            raise SystemExit(1)
        return

    _write(_error_response(req_id, "method_not_found", f"Unbekannte Methode: {method}"))
    raise SystemExit(1)


if __name__ == "__main__":
    main()
