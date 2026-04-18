from __future__ import annotations

from typing import Any


_SERVERS: dict[str, dict[str, Any]] = {
    "mock": {
        "server_name": "mock",
        "transport": "inproc_mock",
        "profile": "default",
    },
    "mock_subprocess": {
        "server_name": "mock_subprocess",
        "transport": "subprocess_stdio_json",
        "profile": "default",
        "module": "agent.dak_gord_system.graph.tools.mcp_subprocess_server",
        "env": {
            "MCP_SERVER_PROFILE": "default",
        },
    },
    "mock_subprocess_alt": {
        "server_name": "mock_subprocess_alt",
        "transport": "subprocess_stdio_json",
        "profile": "alt",
        "module": "agent.dak_gord_system.graph.tools.mcp_subprocess_server",
        "env": {
            "MCP_SERVER_PROFILE": "alt",
        },
    },
}


def get_mcp_server_config(server_name: str) -> dict[str, Any]:
    name = str(server_name or "mock").strip() or "mock"
    if name not in _SERVERS:
        raise KeyError(f"Unbekannter MCP-Server: {name}")
    return dict(_SERVERS[name])


def list_mcp_server_configs() -> list[dict[str, Any]]:
    return [dict(v) for v in _SERVERS.values()]
