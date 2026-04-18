from __future__ import annotations

from typing import Any

from agent.dak_gord_system.graph.state import AgentState, ToolAktion
from agent.dak_gord_system.graph.tools.base import ToolContext, ToolResult
from agent.dak_gord_system.graph.tools.file_tools import register_file_tools
from agent.dak_gord_system.graph.tools.shell_tools import register_shell_tools
from agent.dak_gord_system.graph.tools.mcp_tools import register_mcp_tools
from agent.dak_gord_system.graph.tools.registry import registry


def tool_context_from_state(state: AgentState) -> ToolContext:
    return ToolContext(
        task_id=state.get("task_id", ""),
        thread_id=state.get("thread_id", ""),
        run_type=state.get("run_type", ""),
        actor="graph_agent",
    )


def result_to_tool_aktion(
    result: ToolResult,
    *,
    aktion: str,
    args: dict[str, Any],
) -> ToolAktion:
    output_preview = ""
    if isinstance(result.output, dict):
        output_preview = str(result.output)[:300]
    elif result.output is not None:
        output_preview = str(result.output)[:300]

    return {
        "tool": result.tool,
        "aktion": aktion,
        "eingabe": str(args)[:300],
        "ergebnis": output_preview,
        "erfolgreich": result.ok,
        "zeitstempel": result.timestamp,
    }


def ensure_default_tools_registered() -> None:
    register_file_tools()
    register_shell_tools()
    register_mcp_tools()
    register_mcp_tools()


def run_registered_tool(
    state: AgentState,
    name: str,
    args: dict[str, Any],
    *,
    aktion: str,
) -> tuple[ToolResult, ToolAktion]:
    ensure_default_tools_registered()
    ctx = tool_context_from_state(state)
    result = registry.run(name, ctx, args)
    tool_aktion = result_to_tool_aktion(result, aktion=aktion, args=args)
    return result, tool_aktion
