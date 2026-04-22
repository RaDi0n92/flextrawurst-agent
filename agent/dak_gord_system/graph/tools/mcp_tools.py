from __future__ import annotations

from typing import Any

from .base import ToolContext, ToolDefinition, ToolResult
from .mcp_runtime import run_mcp_tool
from .registry import ToolRegistry, registry


def _make_mcp_handler(remote_tool_name: str, risk: str):
    def _handler(ctx: ToolContext, args: dict[str, Any]) -> ToolResult:
        server_name = str(args.get("server_name", "mock") or "mock")
        tool_args = {k: v for k, v in args.items() if k != "server_name"}

        result = run_mcp_tool(
            remote_tool_name,
            tool_args,
            server_name=server_name,
        )

        if result.get("ok"):
            return ToolResult(
                ok=True,
                tool=remote_tool_name,
                risk=risk,
                output=result.get("output"),
                meta={
                    "task_id": ctx.task_id,
                    "thread_id": ctx.thread_id,
                    "server_name": server_name,
                },
            )

        return ToolResult(
            ok=False,
            tool=remote_tool_name,
            risk=risk,
            error=str(result.get("error", "MCP-Tool fehlgeschlagen")),
            meta={
                "task_id": ctx.task_id,
                "thread_id": ctx.thread_id,
                "server_name": server_name,
            },
        )

    return _handler


def register_mcp_tools(reg: ToolRegistry | None = None) -> ToolRegistry:
    reg = reg or registry

    reg.register(
        ToolDefinition(
            name="mcp_echo",
            description="Remote MCP-Tool: gibt Argumente als Echo zurück.",
            risk="low",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "server_name": {"type": "string"},
                },
            },
            handler=_make_mcp_handler("mcp_echo", "low"),
            transport="mcp",
            server_name="mock",
            remote_tool_name="mcp_echo",
        ),
        overwrite=True,
    )

    reg.register(
        ToolDefinition(
            name="mcp_uppercase",
            description="Remote MCP-Tool: wandelt text in Grossbuchstaben um.",
            risk="low",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "server_name": {"type": "string"},
                },
            },
            handler=_make_mcp_handler("mcp_uppercase", "low"),
            transport="mcp",
            server_name="mock",
            remote_tool_name="mcp_uppercase",
        ),
        overwrite=True,
    )

    reg.register(
        ToolDefinition(
            name="mcp_write_note",
            description="Remote MCP-Tool: schreibt eine Notiz in die MCP-Notizspur.",
            risk="medium",
            input_schema={
                "type": "object",
                "required": ["content"],
                "properties": {
                    "content": {"type": "string"},
                    "server_name": {"type": "string"},
                },
            },
            handler=_make_mcp_handler("mcp_write_note", "medium"),
            transport="mcp",
            server_name="mock",
            remote_tool_name="mcp_write_note",
        ),
        overwrite=True,
    )

    return reg
