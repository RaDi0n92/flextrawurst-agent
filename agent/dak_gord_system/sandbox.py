from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

WERKRAUM = Path("/root/werkraum")
SANDBOX_TIMEOUT = 15
SANDBOX_MAX_OUTPUT = 4000

_VERBOTENE_MUSTER = [
    "import os; os.system",
    "import subprocess",
    "__import__('subprocess')",
    "open('/etc/",
    "open('/root/.ssh",
    "shutil.rmtree",
    "os.remove",
    "os.unlink",
]


def _prueffe_code(code: str) -> str | None:
    for muster in _VERBOTENE_MUSTER:
        if muster in code:
            return f"Verbotener Code-Ausdruck: {muster!r}"
    return None


def fuehre_code_aus(code: str, cwd: str | None = None) -> dict:
    fehler = _prueffe_code(code)
    if fehler:
        return {"ok": False, "stdout": "", "stderr": fehler, "returncode": -1}

    arbeitsverzeichnis = Path(cwd) if cwd else WERKRAUM

    eingerueckt = textwrap.dedent(code)

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        dir="/tmp",
        delete=False,
        encoding="utf-8",
    ) as f:
        f.write(eingerueckt)
        skript_pfad = f.name

    try:
        ergebnis = subprocess.run(
            [sys.executable, skript_pfad],
            capture_output=True,
            text=True,
            timeout=SANDBOX_TIMEOUT,
            cwd=str(arbeitsverzeichnis),
        )
        stdout = ergebnis.stdout[:SANDBOX_MAX_OUTPUT]
        stderr = ergebnis.stderr[:SANDBOX_MAX_OUTPUT]
        return {
            "ok": ergebnis.returncode == 0,
            "stdout": stdout,
            "stderr": stderr,
            "returncode": ergebnis.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "stdout": "",
            "stderr": f"Timeout nach {SANDBOX_TIMEOUT}s",
            "returncode": -1,
        }
    except Exception as exc:
        return {
            "ok": False,
            "stdout": "",
            "stderr": str(exc),
            "returncode": -1,
        }
    finally:
        Path(skript_pfad).unlink(missing_ok=True)
