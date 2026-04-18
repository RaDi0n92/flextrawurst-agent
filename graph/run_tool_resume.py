from __future__ import annotations

import sys

from agent.dak_gord_system.graph.approval_api import resume_approval


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Nutzung: python -m agent.dak_gord_system.graph.run_tool_resume <task_id> <genehmigt|abgelehnt>")

    task_id = sys.argv[1]
    entscheidung = sys.argv[2].strip().lower()

    result = resume_approval(task_id, entscheidung)

    print("FINAL STATE:")
    for k, v in result.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
