#!/usr/bin/env python3
"""Zentrale Konfiguration für das Innenleben-System."""

from pathlib import Path

WESEN = [
    "namelessAI_1234",
    "namelessAI_1324",
    "namelessAI_1423",
    "namelessAI_2341",
    "namelessAI_3123",
    "namelessAI_4321",
]

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_CHAT  = "http://localhost:11434/api/chat"
MODELL       = "dolphin3:8b-llama3.1-q8_0"

INNENLEBEN_DIR  = Path("/root/werkraum/innenleben")
CHROMA_DIR      = INNENLEBEN_DIR / "chroma_db"
SELBSTMODELLE_DIR = INNENLEBEN_DIR / "selbstmodelle"
LOGS_DIR        = Path("/root/werkraum/logs")

REFLECTION_SCORE_THRESHOLD = 8.0
REFLECTION_MIN_ABSTAND_SEC = 14400   # 4 Stunden
REFLECTION_TAGES_SEC       = 86400   # 24 Stunden
REFLECTION_MIN_MEMORIES    = 5       # erst ab 5 Erinnerungen reflektieren
