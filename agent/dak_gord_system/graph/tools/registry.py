from __future__ import annotations

from typing import Any

from .base import ToolContext, ToolDefinition, ToolResult


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition, *, overwrite: bool = False) -> None:
        if tool.name in self._tools and not overwrite:
            raise ValueError(f"Tool bereits registriert: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition:
        if name not in self._tools:
            raise KeyError(f"Unbekanntes Tool: {name}")
        return self._tools[name]

    def list_names(self) -> list[str]:
        return sorted(self._tools.keys())

    def describe(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for name in self.list_names():
            tool = self._tools[name]
            out.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "risk": tool.risk,
                    "input_schema": tool.input_schema,
                    "transport": tool.transport,
                    "server_name": tool.server_name,
                    "remote_tool_name": tool.remote_tool_name,
                }
            )
        return out

    def run(self, name: str, ctx: ToolContext, args: dict[str, Any]) -> ToolResult:
        tool = self.get(name)
        return tool.run(ctx, args)


registry = ToolRegistry()
