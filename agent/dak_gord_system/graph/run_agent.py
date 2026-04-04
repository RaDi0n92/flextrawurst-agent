from __future__ import annotations

import sys
import uuid

from agent.dak_gord_system.graph.build import build_minimal_graph
from agent.dak_gord_system.graph.state import new_agent_state


def main() -> None:
    fokus = sys.argv[1] if len(sys.argv) > 1 else "vision4.md"

    task_id = f"task_{uuid.uuid4().hex[:8]}"
    thread_id = f"thread_{uuid.uuid4().hex[:8]}"

    state = new_agent_state(
        task_id=task_id,
        thread_id=thread_id,
        run_type="datei_lesen",
        ziel=f"{fokus} lesen und Graph-Snapshot schreiben",
        modus="lesen",
        fokus_datei=fokus,
        fokus_pfad="",
        aktueller_schritt="resolve_file",
    )

    graph = build_minimal_graph()
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke(state, config=config)

    print("FINAL STATE:")
    for k, v in result.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
