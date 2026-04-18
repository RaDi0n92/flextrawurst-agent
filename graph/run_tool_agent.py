from __future__ import annotations

import json
import sys
import uuid

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from agent.dak_gord_system.graph.nodes.approval import check_tool_approval_node
from agent.dak_gord_system.graph.nodes.tool import run_tool_node
from agent.dak_gord_system.graph.state import AgentState, new_agent_state


def _route_after_approval(state: AgentState) -> str:
    approval_status = state.get("approval_status")
    if approval_status in {"nicht_noetig", "genehmigt"}:
        return "run_tool"
    return "end"


def build_tool_graph():
    builder = StateGraph(AgentState)
    builder.add_node("check_tool_approval", check_tool_approval_node)
    builder.add_node("run_tool", run_tool_node)

    builder.add_edge(START, "check_tool_approval")
    builder.add_conditional_edges(
        "check_tool_approval",
        _route_after_approval,
        {
            "run_tool": "run_tool",
            "end": END,
        },
    )
    builder.add_edge("run_tool", END)
    return builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Nutzung: python -m agent.dak_gord_system.graph.run_tool_agent <tool_name> [json_args]")

    tool_name = sys.argv[1]
    raw_args = sys.argv[2] if len(sys.argv) > 2 else "{}"

    try:
        tool_args = json.loads(raw_args)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Ungueltiges JSON fuer tool_args: {exc}") from exc

    if not isinstance(tool_args, dict):
        raise SystemExit("tool_args muessen ein JSON-Objekt sein.")

    task_id = f"task_{uuid.uuid4().hex[:8]}"
    thread_id = f"thread_{uuid.uuid4().hex[:8]}"

    state = new_agent_state(
        task_id=task_id,
        thread_id=thread_id,
        run_type="maintenance",
        ziel=f"Tool ausfuehren: {tool_name}",
        modus="tool",
        aktueller_schritt="check_tool_approval",
    )

    state["tool_name"] = tool_name
    state["tool_args"] = tool_args
    state["tool_aktion"] = f"tool:{tool_name}"

    graph = build_tool_graph()
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke(state, config=config)

    print("FINAL STATE:")
    for k, v in result.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
