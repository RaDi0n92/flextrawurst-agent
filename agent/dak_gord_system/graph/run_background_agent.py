from __future__ import annotations

import subprocess
import sys

def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Verwendung: python -m agent.dak_gord_system.graph.run_background_agent "
            "<neugier_scan|vision_cycle>"
        )
        raise SystemExit(2)

    run_type = str(sys.argv[1]).strip()
    if run_type not in {"neugier_scan", "vision_cycle"}:
        print(f"Unbekannter background run_type: {run_type}")
        raise SystemExit(2)

    cmd = [sys.executable, "-m", "agent.dak_gord_system.graph.run_background", run_type]
    result = subprocess.run(cmd, check=False)
    raise SystemExit(result.returncode)

if __name__ == "__main__":
    main()
