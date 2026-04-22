from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Literal

ToolRisk = Literal["low", "medium", "high"]
ToolTransport = Literal["local", "mcp"]


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass(slots=True)
class ToolContext:
    task_id: str = ""
    thread_id: str = ""
    run_type: str = ""
    actor: str = "graph_agent"


@dataclass(slots=True)
class ToolResult:
    ok: bool
    tool: str
    risk: ToolRisk
    output: Any = None
    error: str | None = None
    artifacts: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=_ts)


ToolHandler = Callable[[ToolContext, dict[str, Any]], ToolResult]


@dataclass(slots=True)
class ToolDefinition:
    name: str
    description: str
    risk: ToolRisk
    input_schema: dict[str, Any]
    handler: ToolHandler
    transport: ToolTransport = "local"
    server_name: str = ""
    remote_tool_name: str = ""

    def run(self, ctx: ToolContext, args: dict[str, Any]) -> ToolResult:
        return self.handler(ctx, args)
