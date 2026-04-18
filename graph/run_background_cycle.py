from __future__ import annotations

import subprocess
import sys


def _run(run_type: str) -> int:
    cmd = [sys.executable, "-m", "agent.dak_gord_system.graph.run_background", run_type]
    result = subprocess.run(cmd, check=False)
    return result.returncode


def main() -> None:
    rc1 = _run("neugier_scan")
    rc2 = _run("vision_cycle")

    if rc1 != 0 or rc2 != 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
