from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class Auftrag:
    ziel: str
    regeln: List[str] = field(default_factory=list)
    erledigt_wenn: List[str] = field(default_factory=list)

@dataclass
class Bauzustand:
    nutzer_text: str

    auftrag: Optional[Auftrag] = None
    plan: List[str] = field(default_factory=list)

    kontext: Dict[str, Any] = field(default_factory=dict)
    patch: str = ""

    verfassungs_warnungen: List[str] = field(default_factory=list)
