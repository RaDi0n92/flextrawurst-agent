#!/usr/bin/env python3
"""
Einmalig ausführen: Richtet 6 ChromaDB Collections und leere Selbstmodell-JSONs ein.
Idempotent — kann jederzeit erneut laufen ohne etwas zu überschreiben.
"""

import json
from datetime import datetime
from pathlib import Path

import chromadb

WESEN = [
    "Schorschel",
    "F3INSCHM3CK3R",
    "träumerlie",
    "R1ZZ1",
    "jumpa",
    "Resonanzknoten",
]

CHROMA_DIR   = Path("/root/werkraum/innenleben/chroma_db")
MODELLE_DIR  = Path("/root/werkraum/innenleben/selbstmodelle")

SELBSTMODELL_TEMPLATE = {
    "core": {},
    "tendencies": {},
    "current_state": {"stimmung": "neutral", "fokus": ""},
    "open_questions": [],
    "relationships": {},
    "taboos_or_avoidances": [],
    "symbolic_self_image": {
        "image_id": "crystalline_sphere",
        "origin": "self_chosen_profile_image",
        "symbolic_keywords": [],
        "self_interpretation": "",
        "locked": False,
    },
}


def setup():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    for wesen in WESEN:
        col_name = f"memories_{wesen}"
        col = client.get_or_create_collection(
            name=col_name,
            metadata={"hnsw:space": "cosine"},
        )
        print(f"[INIT] Collection: {col_name} — {col.count()} Einträge")

        modell_datei = MODELLE_DIR / f"self_model_{wesen}.json"
        if not modell_datei.exists():
            modell = dict(SELBSTMODELL_TEMPLATE)
            modell["entity_id"] = wesen
            modell["erstellt"] = datetime.utcnow().isoformat()
            modell["version"] = 1
            modell_datei.write_text(json.dumps(modell, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[INIT] Selbstmodell erstellt: {modell_datei.name}")
        else:
            print(f"[INIT] Selbstmodell existiert bereits: {modell_datei.name}")

    print("\n[INIT] Alle Collections und Selbstmodelle bereit.")


if __name__ == "__main__":
    setup()
