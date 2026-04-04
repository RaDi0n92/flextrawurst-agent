from __future__ import annotations

import sys
import uuid

from agent.dak_gord_system.graph.build import build_background_graph
from agent.dak_gord_system.graph.run_types import ist_gueltiger_run_type
from agent.dak_gord_system.graph.state import new_agent_state


def main() -> None:
    run_type = sys.argv[1] if len(sys.argv) > 1 else "neugier_scan"
    if not ist_gueltiger_run_type(run_type):
        raise SystemExit(f"Ungueltiger run_type: {run_type}")

    if run_type not in {"neugier_scan", "vision_cycle"}:
        raise SystemExit("run_background unterstuetzt aktuell nur neugier_scan oder vision_cycle")

    task_id = f"task_{uuid.uuid4().hex[:8]}"
    thread_id = f"thread_{uuid.uuid4().hex[:8]}"

    state = new_agent_state(
        task_id=task_id,
        thread_id=thread_id,
        run_type=run_type,
        ziel=f"Hintergrundlauf fuer {run_type}",
        modus="hintergrund",
        aktueller_schritt="background_tick",
    )

    graph = build_background_graph()
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke(state, config=config)

    print("FINAL STATE:")
    for k, v in result.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
