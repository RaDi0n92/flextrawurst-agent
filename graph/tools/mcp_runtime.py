from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from typing import Any

from .mcp_servers import get_mcp_server_config


def _run_inproc_mock(tool_name: str, tool_args: dict[str, Any], server_name: str) -> dict[str, Any]:
    if not tool_name:
        return {
            "ok": False,
            "tool_name": tool_name,
            "server_name": server_name,
            "error": "tool_name fehlt",
            "output": None,
        }

    if tool_name == "mcp_echo":
        return {
            "ok": True,
            "tool_name": tool_name,
            "server_name": server_name,
            "error": "",
            "output": {
                "transport": "inproc_mock",
                "server_profile": "default",
                "protocol": "direct_call",
                "tool_name": tool_name,
                "tool_args": tool_args,
                "message": "mock mcp call erfolgreich",
            },
        }

    if tool_name == "mcp_uppercase":
        text = str(tool_args.get("text", "") or "")
        return {
            "ok": True,
            "tool_name": tool_name,
            "server_name": server_name,
            "error": "",
            "output": {
                "transport": "inproc_mock",
                "server_profile": "default",
                "protocol": "direct_call",
                "tool_name": tool_name,
                "tool_args": tool_args,
                "text": text.upper(),
                "length": len(text),
            },
        }

    return {
        "ok": False,
        "tool_name": tool_name,
        "server_name": server_name,
        "error": f"Unbekanntes Inproc-MCP-Tool: {tool_name}",
        "output": None,
    }


def _call_subprocess(method: str, params: dict[str, Any], server_name: str) -> dict[str, Any]:
    cfg = get_mcp_server_config(server_name)
    module = str(cfg.get("module", "") or "").strip()
    if not module:
        return {
            "ok": False,
            "server_name": server_name,
            "error": "module fehlt in MCP-Serverkonfiguration",
            "output": None,
        }

    req_id = f"mcp_{uuid.uuid4().hex[:10]}"
    payload = {
        "id": req_id,
        "method": method,
        "params": params,
    }

    env = os.environ.copy()
    env.update({str(k): str(v) for k, v in (cfg.get("env", {}) or {}).items()})

    result = subprocess.run(
        [sys.executable, "-m", module],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        check=False,
        cwd="/root/werkraum",
        env=env,
    )

    stdout = result.stdout.strip()
    if not stdout:
        return {
            "ok": False,
            "server_name": server_name,
            "error": f"Leere Antwort vom MCP-Subprozess. stderr={result.stderr[:500]}",
            "output": None,
        }

    try:
        response = json.loads(stdout.splitlines()[-1])
    except Exception as exc:
        return {
            "ok": False,
            "server_name": server_name,
            "error": f"Antwort ist kein gueltiges JSON: {exc}",
            "output": {"stdout": stdout[:1000], "stderr": result.stderr[:1000]},
        }

    if response.get("error"):
        return {
            "ok": False,
            "server_name": server_name,
            "error": str(response["error"]),
            "output": response,
        }

    out = response.get("result", {}) or {}
    out["protocol"] = "jsonrpc_like"
    out["request_id"] = req_id
    out["response_id"] = str(response.get("id", "") or "")
    out["method"] = method

    return {
        "ok": True,
        "server_name": server_name,
        "error": "",
        "output": out,
    }


def run_mcp_tool(tool_name: str, tool_args: dict[str, Any], *, server_name: str = "mock") -> dict[str, Any]:
    cfg = get_mcp_server_config(server_name)
    transport = str(cfg.get("transport", "") or "").strip()

    if transport == "inproc_mock":
        return _run_inproc_mock(tool_name, tool_args, server_name)

    if transport == "subprocess_stdio_json":
        result = _call_subprocess(
            "tools/call",
            {
                "tool_name": tool_name,
                "tool_args": tool_args,
            },
            server_name,
        )
        result["tool_name"] = tool_name
        return result

    return {
        "ok": False,
        "tool_name": tool_name,
        "server_name": server_name,
        "error": f"Unbekannter MCP-Transport: {transport}",
        "output": None,
    }


def list_mcp_tools(*, server_name: str = "mock") -> dict[str, Any]:
    cfg = get_mcp_server_config(server_name)
    transport = str(cfg.get("transport", "") or "").strip()

    if transport == "inproc_mock":
        return {
            "ok": True,
            "server_name": server_name,
            "error": "",
            "output": {
                "tools": [
                    {"name": "mcp_echo", "description": "Gibt Argumente als Echo zurück.", "risk": "low", "server_profile": "default"},
                    {"name": "mcp_uppercase", "description": "Wandelt text in GROSSBUCHSTABEN um.", "risk": "low", "server_profile": "default"},
                ],
                "transport": "inproc_mock",
                "protocol": "direct_call",
                "method": "tools/list",
                "server_profile": "default",
            },
        }

    if transport == "subprocess_stdio_json":
        return _call_subprocess("tools/list", {}, server_name)

    return {
        "ok": False,
        "server_name": server_name,
        "error": f"Unbekannter MCP-Transport: {transport}",
        "output": None,
    }


if __name__ == "__main__":
    print(run_mcp_tool("mcp_echo", {"text": "hallo"}, server_name="mock"))
    print(run_mcp_tool("mcp_echo", {"text": "hallo"}, server_name="mock_subprocess"))
    print(run_mcp_tool("mcp_echo", {"text": "hallo"}, server_name="mock_subprocess_alt"))
    print(run_mcp_tool("mcp_uppercase", {"text": "Hallo Welt"}, server_name="mock_subprocess_alt"))
    print(list_mcp_tools(server_name="mock_subprocess_alt"))
