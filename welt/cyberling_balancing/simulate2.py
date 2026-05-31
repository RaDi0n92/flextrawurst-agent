#!/usr/bin/env python3
"""
Cyberling-Balancing-Simulation 2 — KEIN PRODUKTIVCODE
Drei Profile: Leicht / Mittel / Hart
6 Szenarien × 3 Profile = 18 CSVs + Markdown-Vergleich

Keine Werte werden in die Datenbank geschrieben.
Keine produktiven Importe.
"""

import csv
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

OUT = Path(__file__).parent / "output_sim2"
OUT.mkdir(exist_ok=True)


# ─── Profile ─────────────────────────────────────────────────────────────────

PROFILES = {
    "leicht": {
        "name": "LEICHT (sanftes Profil)",
        "hunger_pro_h": 2.5,
        "durst_pro_h": 5.0,
        "energie_abfall_normal": 0.5,      # sanfter Basisabfall
        "energie_abfall_kaskade": 4.0,
        "stimmung_abfall_kaskade": 3.0,
        "gesundheit_abfall": 2.0,
        "kaskade_schwelle": 35.0,
        "gesundheit_schwelle": 25.0,
        "wasser_effekt": 20.0,
        "futter_effekt": 18.0,
        "wasser_cooldown_h": 1.5,
        "futter_cooldown_h": 2.0,
        "wasser_schwelle_min": 70.0,
        "futter_schwelle_min": 75.0,
        "wasser_max": 85.0,
        "futter_max": 85.0,
        "energie_regen_h": 2.0,          # sichtbare Energie-Erholung
        "gesundheit_regen_h": 1.5,
        "energie_regen_nach_krit_h": 1.0,  # langsame Erholung nach Krise
        "energie_basisrauschen": 1.0,    # leichtes Schwanken bei guter Pflege
        "tod_moeglich": False,
    },
    "mittel": {
        "name": "MITTEL (aktuell verbessert)",
        "hunger_pro_h": 12.0,
        "durst_pro_h": 18.0,
        "energie_abfall_normal": 1.0,      # aktiv sichtbar, nicht dekorativ
        "energie_abfall_kaskade": 8.0,
        "stimmung_abfall_kaskade": 6.0,
        "gesundheit_abfall": 4.0,
        "kaskade_schwelle": 40.0,
        "gesundheit_schwelle": 30.0,
        "wasser_effekt": 30.0,             # größerer Effekt für nachhaltige Balance
        "futter_effekt": 26.0,
        "wasser_cooldown_h": 1.0,
        "futter_cooldown_h": 1.5,
        "wasser_schwelle_min": 75.0,       # früher triggern
        "futter_schwelle_min": 75.0,
        "wasser_max": 95.0,               # mehr Puffer
        "futter_max": 92.0,
        "energie_regen_h": 1.5,           # verbessert gegenüber IST
        "gesundheit_regen_h": 0.8,
        "energie_regen_nach_krit_h": 0.5, # langsame Erholung nach Krise
        "energie_basisrauschen": 2.0,
        "tod_moeglich": True,
    },
    "hart": {
        "name": "HART (kein Pardon)",
        "hunger_pro_h": 12.0,
        "durst_pro_h": 18.0,
        "energie_abfall_normal": 2.0,
        "energie_abfall_kaskade": 12.0,
        "stimmung_abfall_kaskade": 8.0,
        "gesundheit_abfall": 3.0,          # härter als IST
        "kaskade_schwelle": 40.0,
        "gesundheit_schwelle": 35.0,
        "wasser_effekt": 22.0,
        "futter_effekt": 22.0,
        "wasser_cooldown_h": 1.0,
        "futter_cooldown_h": 1.5,
        "wasser_schwelle_min": 80.0,
        "futter_schwelle_min": 80.0,
        "wasser_max": 88.0,
        "futter_max": 88.0,
        "energie_regen_h": 0.5,           # kaum Erholung
        "gesundheit_regen_h": 0.3,
        "energie_regen_nach_krit_h": 0.2,
        "energie_basisrauschen": 3.0,
        "tod_moeglich": True,
    },
}


# ─── Szenarien ────────────────────────────────────────────────────────────────

SZENARIEN = {
    "perfekt": {
        "name": "Perfekte Pflege (alle 2h)",
        "pflege_intervall_h": 2.0,
        "simuliert_h": 24,
    },
    "normal": {
        "name": "Normale Pflege (alle 4h)",
        "pflege_intervall_h": 4.0,
        "simuliert_h": 24,
    },
    "leicht_verspaetet": {
        "name": "Leicht verspätet (alle 6h)",
        "pflege_intervall_h": 6.0,
        "simuliert_h": 24,
    },
    "vernachlaessigt_12h": {
        "name": "Vernachlässigt 12h ohne Pflege",
        "pflege_intervall_h": 99,
        "simuliert_h": 12,
    },
    "vernachlaessigt_24h": {
        "name": "Vernachlässigt 24h",
        "pflege_intervall_h": 99,
        "simuliert_h": 24,
    },
    "vernachlaessigt_48h": {
        "name": "Vernachlässigt 48h (Härtetest)",
        "pflege_intervall_h": 99,
        "simuliert_h": 48,
    },
}


# ─── Simulation ───────────────────────────────────────────────────────────────

def simulate(profile: dict, szenario: dict) -> List[dict]:
    """Simuliert einen Cyberling-Zustand über die Zeit."""
    ticks_per_h = 6  # alle 10 Minuten ein Tick
    p = profile
    rows = []

    hunger = 100.0
    durst = 100.0
    energie = 100.0
    stimmung = 100.0
    gesundheit = 100.0
    am_leben = True
    letzte_wasser = -99.0
    letzte_futter = -99.0
    krit_rettung_vor = None  # wann war kritische Rettung

    total_ticks = szenario["simuliert_h"] * ticks_per_h

    for tick in range(total_ticks + 1):
        h = tick / ticks_per_h

        if not am_leben:
            rows.append({"h": round(h, 2), "hunger": 0, "durst": 0, "energie": 0,
                         "stimmung": 0, "gesundheit": 0, "status": "TOT"})
            continue

        # Pflege anwenden
        gepflegt = False
        if h > 0 and h % szenario["pflege_intervall_h"] < (1 / ticks_per_h):
            # Wasser-Pflege
            if durst <= p["wasser_schwelle_min"] and (h - letzte_wasser) >= p["wasser_cooldown_h"]:
                durst = min(p["wasser_max"], durst + p["wasser_effekt"])
                letzte_wasser = h
                gepflegt = True
            # Futter-Pflege
            if hunger <= p["futter_schwelle_min"] and (h - letzte_futter) >= p["futter_cooldown_h"]:
                hunger = min(p["futter_max"], hunger + p["futter_effekt"])
                letzte_futter = h
                gepflegt = True

        # Abfall pro Tick
        dt = 1 / ticks_per_h
        hunger = max(0.0, hunger - p["hunger_pro_h"] * dt)
        durst = max(0.0, durst - p["durst_pro_h"] * dt)

        # Energie: Basisabfall + Rauschen + Kaskade
        if hunger < p["kaskade_schwelle"] or durst < p["kaskade_schwelle"]:
            energie = max(0.0, energie - p["energie_abfall_kaskade"] * dt)
            stimmung = max(0.0, stimmung - p["stimmung_abfall_kaskade"] * dt)
        else:
            energie = max(0.0, energie - p["energie_abfall_normal"] * dt)
            rauschen = p.get("energie_basisrauschen", 0) * math.sin(h * 3.0) * dt
            energie = max(0.0, min(100.0, energie + rauschen))

        # Kritische Rettung: war energie < 10 und jetzt gepflegt?
        if energie < 10 and gepflegt:
            krit_rettung_vor = h

        # Energie-Regeneration
        regen_rate = p["energie_regen_h"]
        if krit_rettung_vor is not None and (h - krit_rettung_vor) < 4:
            regen_rate = p.get("energie_regen_nach_krit_h", 0.5)  # langsame Erholung nach Krise
        if hunger >= p["kaskade_schwelle"] and durst >= p["kaskade_schwelle"]:
            energie = min(100.0, energie + regen_rate * dt)

        # Gesundheit
        if energie < p["gesundheit_schwelle"]:
            gesundheit = max(0.0, gesundheit - p["gesundheit_abfall"] * dt)
        else:
            gesundheit = min(100.0, gesundheit + p["gesundheit_regen_h"] * dt)

        # Tod
        if p["tod_moeglich"] and gesundheit <= 0:
            am_leben = False

        status = "lebendig"
        if nicht_lebendig := (not am_leben):
            status = "tot"
        elif gesundheit < 20:
            status = "kritisch"
        elif gesundheit < 50:
            status = "krank"
        elif energie < 20:
            status = "erschöpft"
        elif hunger < 20 or durst < 20:
            status = "hungrig/durstig"

        rows.append({
            "h": round(h, 2),
            "hunger": round(hunger, 1),
            "durst": round(durst, 1),
            "energie": round(energie, 1),
            "stimmung": round(stimmung, 1),
            "gesundheit": round(gesundheit, 1),
            "status": status,
        })

    return rows


# ─── Ausgabe ─────────────────────────────────────────────────────────────────

summary_rows = []

for pname, profile in PROFILES.items():
    for sname, szenario in SZENARIEN.items():
        rows = simulate(profile, szenario)
        fname = OUT / f"sim2_{pname}_{sname}.csv"
        with open(fname, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["h", "hunger", "durst", "energie", "stimmung", "gesundheit", "status"])
            w.writeheader()
            w.writerows(rows)

        final = rows[-1]
        ueberlebt = final["status"] != "TOT"
        summary_rows.append({
            "profil": profile["name"],
            "szenario": szenario["name"],
            "stunden": szenario["simuliert_h"],
            "final_hunger": final["hunger"],
            "final_durst": final["durst"],
            "final_energie": final["energie"],
            "final_gesundheit": final["gesundheit"],
            "final_status": final["status"],
            "ueberlebt": "✓" if ueberlebt else "✗",
        })

        print(f"  {pname:8} × {sname:25} → {final['status']:15} G={final['gesundheit']:4.0f}  E={final['energie']:4.0f}  ✓" if ueberlebt else f"  {pname:8} × {sname:25} → {final['status']:15} ✗")


# Markdown-Vergleichsbericht
md = ["# Cyberling Simulation 2 — Vergleichsbericht\n",
      "**KEIN PRODUKTIVCODE — nur Simulation**\n",
      "Drei Profile: Leicht / Mittel / Hart — 6 Szenarien\n\n",
      "| Profil | Szenario | Stunden | H | D | E | G | Status | Lebt? |\n",
      "|:-------|:---------|--------:|--:|--:|--:|--:|:-------|:------|\n"]
for r in summary_rows:
    md.append(f"| {r['profil']} | {r['szenario']} | {r['stunden']} | "
              f"{r['final_hunger']} | {r['final_durst']} | {r['final_energie']} | {r['final_gesundheit']} | "
              f"{r['final_status']} | {r['ueberlebt']} |\n")

md.append("\n## Empfehlung\n\n")
md.append("**Mittel** als Default-Profil empfohlen:\n")
md.append("- Energie-Abfall sichtbar, nicht dekorativ (1.0/h normal)\n")
md.append("- Energie-Regen nach kritischer Rettung langsam (0.5/h), danach 1.5/h\n")
md.append("- Energie schwankt leicht (Basisrauschen 2.0)\n")
md.append("- Tod möglich, aber nur bei echter 48h-Vernachlässigung\n")
md.append("- Aktionen erst ab Schwelle (80%) + Cooldown (1-1.5h) + Cap (88%)\n\n")
md.append("**Leicht** für Tests und Onboarding.\n\n")
md.append("**Hart** für die, die es ernst nehmen.\n\n")
md.append("**Aktivierung:** Nicht automatisch. Profile müssen explizit in cyberling_daemon.py eingebaut werden.\n")

report_path = OUT / "SIM2_BERICHT.md"
report_path.write_text("".join(md), encoding="utf-8")
print(f"\nBericht: {report_path}")
print(f"CSVs in: {OUT}/")
