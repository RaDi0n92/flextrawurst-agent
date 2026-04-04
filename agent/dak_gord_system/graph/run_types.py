from __future__ import annotations
from typing import Literal, get_args

RunType = Literal[
    "datei_lesen",
    "anschlussantwort",
    "neugier_scan",
    "vision_cycle",
    "verdichtung_refresh",
    "maintenance",
]

RUN_TYPES: tuple[str, ...] = get_args(RunType)


def ist_gueltiger_run_type(wert: str) -> bool:
    return wert in RUN_TYPES
