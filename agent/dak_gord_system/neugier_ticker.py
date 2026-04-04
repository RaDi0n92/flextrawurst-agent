from __future__ import annotations
from datetime import datetime
from pathlib import Path

from agent.dak_gord_system.neugierkern import pruefe_neugier_und_vision

LOGDATEI = Path("/root/werkraum/agent/dak_gord_system/spuren/neugier_ticker.log")


def log(text: str) -> None:
    LOGDATEI.parent.mkdir(parents=True, exist_ok=True)
    with LOGDATEI.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")


def main() -> None:
    meldungen = pruefe_neugier_und_vision(0)
    if meldungen:
        for meldung in meldungen:
            log(meldung)
    else:
        log("Neugier-Check: nichts Neues fällig")


if __name__ == "__main__":
    main()
