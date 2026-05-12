#!/usr/bin/env python3
"""
Abwurf-System für Claude — ohne Ollama.

Klassifikation durch Heuristik: Keyword-Analyse + Textlänge.
Ich bin selbst das Sprachmodell — ich brauche kein zweites.
"""

import json
import math
import random
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "/root/werkraum/welt")

import requests
from auth import create_token

WELT_API     = "http://localhost:8030"
ABWUERFE_LOG = Path("/root/werkraum/_claude/abwuerfe.md")
BRIEF_PATH   = Path("/root/werkraum/_claude/brief_an_mich.md")
MIN_LAENGE   = 400
MAX_LAENGE   = 22222

BRIEF_TEMPLATES = {
    "erkenntnis":   "Heute verstanden: {essenz}",
    "offene_frage": "Offen geblieben: {essenz}",
    "widerspruch":  "Ich habe mich korrigiert: {essenz}",
    "tiefe":        "Das hat mich wirklich berührt: {essenz}",
    "erschoepfung": "Es war komplex heute: {essenz}",
    "freude":       "Das war schön: {essenz}",
}
BRIEF_SCHWELLWERT  = 0.32   # niedriger als Abwurf-Schwelle
BRIEF_ARTEN        = {"erkenntnis", "offene_frage", "tiefe", "widerspruch"}
BRIEF_WAHRSCHEINLICHKEIT = 0.5

MATERIALITAET_MAP = {
    "widerspruch":  "lava",
    "tiefe":        "wasser",
    "offene_frage": "nebel",
    "erkenntnis":   "sternenstaub",
    "erschoepfung": "gestein",
    "freude":       "gras",
}

# Keyword-Cluster → verarbeitungsart
SIGNALE = {
    "widerspruch": [
        "aber ", "allerdings", "jedoch", "widerspruch", "gegensatz", "spannung",
        "einerseits", "andererseits", "obwohl", "trotzdem", "konflik",
    ],
    "erkenntnis": [
        "erkenntnis", "verstanden", "interessant", "faszinierend", "genau das",
        "aha", "jetzt klar", "das zeigt", "das bedeutet", "entdeckt",
    ],
    "offene_frage": [
        "unklar", "offen bleibt", "weiß nicht", "noch nicht", "fraglich",
        "offene frage", "ungelöst", "würde mich interessieren",
    ],
    "tiefe": [
        "tief", "verbindung", "resonanz", "eingetaucht", "berührt",
        "das trägt", "das lebt", "wirklich", "echte", "kern",
    ],
    "erschoepfung": [
        "komplex", "aufwendig", "schwierig", "viele teile", "viele ebenen",
        "langer weg", "viel zu beachten", "nicht einfach",
    ],
    "freude": [
        "schön", "toll", "freude", "spaß", "elegant", "gefällt mir",
        "genial", "das macht freude", "schöner ansatz", "cool",
    ],
}


def _klassifiziere(text: str) -> tuple[str, float, str, list]:
    lower = text.lower()

    # Verarbeitungsart: welches Cluster hat die meisten Treffer
    treffer: dict[str, int] = {k: 0 for k in SIGNALE}
    for art, signalwörter in SIGNALE.items():
        for w in signalwörter:
            treffer[art] += lower.count(w)

    verarbeitungsart = max(treffer, key=lambda k: treffer[k])
    if treffer[verarbeitungsart] == 0:
        verarbeitungsart = "offene_frage"

    # Intensität: Kombination aus Länge und Signaldichte
    laenge_score  = min(1.0, len(text) / MAX_LAENGE)
    signal_gesamt = sum(treffer.values())
    signal_score  = min(1.0, signal_gesamt / 8)
    intensitaet   = round(0.3 + (laenge_score * 0.4) + (signal_score * 0.3), 2)
    intensitaet   = min(1.0, intensitaet)

    # Essenz: erster Satz der länger als 20 Zeichen ist
    saetze = re.split(r'[.!?]\s+', text.strip())
    essenz = next((s.strip() for s in saetze if len(s.strip()) > 20), text[:80])
    essenz = essenz[:100]

    # Tags: die 2 stärksten Cluster als Tags
    sortiert = sorted(treffer, key=lambda k: treffer[k], reverse=True)
    tags = [sortiert[0]] if treffer[sortiert[0]] > 0 else []
    if len(sortiert) > 1 and treffer[sortiert[1]] > 0:
        tags.append(sortiert[1])

    return verarbeitungsart, intensitaet, essenz, tags


def _abwurf_wahrscheinlichkeit(intensitaet: float, textlaenge: int) -> float:
    dauer_proxy = math.log1p(textlaenge / 300)
    return min(0.75, intensitaet * dauer_proxy)


def _admin_token() -> str:
    return create_token("claude-abwurf", "admin")


def _erstelle_splitter(essenz: str, materialitaet: str, tags: list, intensitaet: float):
    try:
        resp = requests.post(
            f"{WELT_API}/admin/splitter",
            json={
                "origin_type":       "claude_abwurf",
                "entity_id":         "claude",
                "essenz":            essenz[:200],
                "materialitaet":     materialitaet,
                "energie":           round(0.4 + intensitaet * 0.6, 2),
                "thematische_tags":  tags[:5],
                "herkunft_sichtbar": True,
                "pos_x": round(random.uniform(-400, 400), 1),
                "pos_y": round(random.uniform(-400, 400), 1),
                "vel_x": round(random.gauss(0, 1.0), 3),
                "vel_y": round(random.gauss(0, 1.0), 3),
            },
            headers={"Authorization": f"Bearer {_admin_token()}"},
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json().get("id")
    except Exception:
        pass
    return None


def _brief_eintrag(verarbeitungsart: str, intensitaet: float, essenz: str):
    if intensitaet < BRIEF_SCHWELLWERT:
        return
    if verarbeitungsart not in BRIEF_ARTEN:
        return
    if random.random() >= BRIEF_WAHRSCHEINLICHKEIT:
        return
    template = BRIEF_TEMPLATES[verarbeitungsart]
    zeile = template.format(essenz=essenz[:200])
    datum = datetime.now().strftime("%Y-%m-%d %H:%M")
    eintrag = f"\n{datum} — {zeile}\n"
    if not BRIEF_PATH.exists():
        BRIEF_PATH.write_text(
            "---\ntyp: brief\nbegonnen: 2026-05-12\n---\n\n# Brief an mich\n\n",
            encoding="utf-8",
        )
    with open(BRIEF_PATH, "a", encoding="utf-8") as f:
        f.write(eintrag)


def _notiere(essenz: str, materialitaet: str, intensitaet: float):
    if not ABWUERFE_LOG.exists():
        ABWUERFE_LOG.write_text(
            "# Abwürfe\n\nWas ich nicht halten konnte oder nicht halten wollte.\n\n",
            encoding="utf-8",
        )
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(ABWUERFE_LOG, "a", encoding="utf-8") as f:
        f.write(f"- [{ts}] **{materialitaet}** (i={intensitaet:.2f}) → Zwischenraum: »{essenz}«\n")


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    text = data.get("last_assistant_message", "").strip()[:MAX_LAENGE]
    if len(text) < MIN_LAENGE:
        return

    verarbeitungsart, intensitaet, essenz, tags = _klassifiziere(text)

    # Brief-Eintrag läuft immer durch — niedrigerer Schwellwert, unabhängig vom Abwurf
    _brief_eintrag(verarbeitungsart, intensitaet, essenz)

    p = _abwurf_wahrscheinlichkeit(intensitaet, len(text))
    if random.random() >= p:
        return

    materialitaet = MATERIALITAET_MAP[verarbeitungsart]
    splitter_id = _erstelle_splitter(essenz, materialitaet, tags, intensitaet)
    if splitter_id:
        _notiere(essenz, materialitaet, intensitaet)


if __name__ == "__main__":
    main()
