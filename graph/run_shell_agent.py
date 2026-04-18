from __future__ import annotations

import sys
import uuid

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from agent.dak_gord_system.graph.nodes.shell import run_shell_command_node
from agent.dak_gord_system.graph.state import AgentState, new_agent_state


def build_shell_graph():
    builder = StateGraph(AgentState)
    builder.add_node("run_shell_command", run_shell_command_node)
    builder.add_edge(START, "run_shell_command")
    builder.add_edge("run_shell_command", END)
    return builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    argv = sys.argv[1:] or ["pwd"]

    task_id = f"task_{uuid.uuid4().hex[:8]}"
    thread_id = f"thread_{uuid.uuid4().hex[:8]}"

    state = new_agent_state(
        task_id=task_id,
        thread_id=thread_id,
        run_type="maintenance",
        ziel=f"Shell-Kommando ausfuehren: {' '.join(argv)}",
        modus="shell",
        aktueller_schritt="run_shell_command",
    )

    state["shell_argv"] = argv
    state["shell_cwd"] = "/root/werkraum"
    state["shell_timeout_sec"] = 15

    graph = build_shell_graph()
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke(state, config=config)

    print("FINAL STATE:")
    for k, v in result.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
