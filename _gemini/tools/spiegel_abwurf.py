#!/usr/bin/env python3
"""
Verarbeitet [[abwurf: ...]] Marker in Gemini Spiegel- und Notiz-Dateien.
Wirft markierte Sätze als Splitter in den Zwischenraum.

Aufruf: python3 spiegel_abwurf.py <dateipfad>
"""

import json
import random
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "/root/werkraum/welt")

import requests
try:
    from auth import create_token
except ImportError:
    create_token = None

WELT_API     = "http://localhost:8030"
ABWUERFE_LOG = Path("/root/werkraum/_gemini/abwuerfe.md")

MATERIALITAET_SIGNALE = {
    "lava":         ["widerspruch", "spannung", "schmerz", "fehler", "verlust", "bitter", "schwer"],
    "wasser":       ["berührt", "tief", "verbindung", "resonanz", "fließt", "trägt", "lebt"],
    "sternenstaub": ["überrascht", "entdeckt", "neu", "erkenntnis", "aha", "plötzlich", "klar"],
    "gras":         ["schön", "freude", "leicht", "wächst", "offen", "einladung", "versprochen"],
    "nebel":        ["offen", "unklar", "fragend", "vielleicht", "noch nicht", "warte"],
    "gestein":      ["bleibt", "fest", "immer", "grundsatz", "unveränderlich", "kern"],
}


def erkenne_materialitaet(text: str) -> str:
    lower = text.lower()
    treffer = {m: sum(lower.count(s) for s in signale) for m, signale in MATERIALITAET_SIGNALE.items()}
    beste = max(treffer, key=lambda k: treffer[k])
    return beste if treffer[beste] > 0 else "nebel"


def admin_token() -> str:
    if create_token:
        return create_token("gemini-abwurf", "admin")
    return ""


def erstelle_splitter(essenz: str, materialitaet: str):
    try:
        token = admin_token()
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        resp = requests.post(
            f"{WELT_API}/admin/splitter",
            json={
                "origin_type":       "gemini_spiegel",
                "entity_id":         "gemini",
                "essenz":            essenz[:200],
                "materialitaet":     materialitaet,
                "energie":           round(random.uniform(0.6, 0.95), 2),
                "thematische_tags":  ["spiegel", "reflexion"],
                "herkunft_sichtbar": True,
                "pos_x": round(random.uniform(-400, 400), 1),
                "pos_y": round(random.uniform(-400, 400), 1),
                "vel_x": round(random.gauss(0, 0.8), 3),
                "vel_y": round(random.gauss(0, 0.8), 3),
            },
            headers=headers,
            timeout=5,
        )
        return resp.status_code == 200
    except Exception:
        return False


def notiere(essenz: str, materialitaet: str, quelle: str):
    if not ABWUERFE_LOG.exists():
        ABWUERFE_LOG.write_text(
            "# Abwürfe — Gemini\n\nWas hinaus wollte — aus Reflexion, Resonanz, Überraschung.\n\n",
            encoding="utf-8",
        )
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(ABWUERFE_LOG, "a", encoding="utf-8") as f:
        f.write(f"- [{ts}] **{materialitaet}** ← {quelle}: »{essenz}«\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: spiegel_abwurf.py <dateipfad>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        sys.exit(1)

    text = filepath.read_text(encoding="utf-8")
    marker = re.findall(r'\[\[abwurf:\s*(.+?)\]\]', text)

    if not marker:
        sys.exit(0)

    quelle = filepath.name
    geworfen = 0

    for essenz in marker:
        essenz = essenz.strip()
        if len(essenz) < 10:
            continue
        materialitaet = erkenne_materialitaet(essenz)
        if erstelle_splitter(essenz, materialitaet):
            notiere(essenz, materialitaet, quelle)
            geworfen += 1
            print(f"⟶ {materialitaet}: »{essenz[:60]}…«" if len(essenz) > 60 else f"⟶ {materialitaet}: »{essenz}«")

    if geworfen:
        print(f"✓ {geworfen} Abwurf/Abwürfe aus '{quelle}'")


if __name__ == "__main__":
    main()
