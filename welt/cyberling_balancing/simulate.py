#!/usr/bin/env python3
"""
Cyberling-Balancing-Simulation
Kein Produktivcode. Nur Simulation und Ausgabe.
Zeigt: Aktuelle Rates (IST) vs. Vorschlag (SOLL) in 6 Szenarien.
"""

import csv
import sys
from dataclasses import dataclass, field
from pathlib import Path


# ─── Konfiguration: IST (was im Daemon steckt) ──────────────────────────────

IST = {
    "name": "IST (aktuell aktiv)",
    "hunger_pro_h": 12.0,       # 0.12 * 100
    "durst_pro_h": 18.0,        # 0.18 * 100
    "energie_pro_h_normal": 0.0,  # kein normaler Energieabfall im Daemon
    "energie_pro_h_kaskade": 8.0,  # bei hunger+durst < 40
    "stimmung_pro_h_kaskade": 6.0,
    "gesundheit_pro_h": 4.0,    # wenn energie < 30
    "kaskade_schwelle": 40.0,
    "gesundheit_schwelle": 30.0,
    # Aktionen
    "wasser_effekt": 22.0,      # +22% (kein Cooldown, keine Schwelle im Daemon)
    "futter_effekt": 22.0,
    "wasser_cooldown_h": 0.0,   # kein Cooldown im Daemon
    "futter_cooldown_h": 0.0,
    "wasser_schwelle": 100.0,   # keine Schwelle (immer erlaubt)
    "futter_schwelle": 100.0,
    "wasser_max": 100.0,        # kein Cap
    "futter_max": 100.0,
    # Regeneration
    "energie_regen_h": 0.0,
    "gesundheit_regen_h": 0.0,  # keine Regen im Daemon
}

# ─── Konfiguration: SOLL (Daniel's Vorschlag) ───────────────────────────────

SOLL = {
    "name": "SOLL (Vorschlag balanciert)",
    "hunger_pro_h": 3.0,
    "durst_pro_h": 6.0,
    "energie_pro_h_normal": 2.0,
    "energie_pro_h_kaskade": 4.0,   # zusätzlich bei H/D < 40
    "stimmung_pro_h_kaskade": 2.0,
    "gesundheit_pro_h": 3.0,        # wenn energie < 30 UND H/D < 25
    "kaskade_schwelle": 40.0,
    "gesundheit_schwelle": 30.0,
    # Aktionen
    "wasser_effekt": 22.0,
    "futter_effekt": 25.0,
    "wasser_cooldown_h": 3.0,
    "futter_cooldown_h": 6.0,
    "wasser_schwelle": 70.0,    # erst erlaubt wenn Durst ≤ 70
    "futter_schwelle": 65.0,    # erst erlaubt wenn Hunger ≤ 65
    "wasser_max": 88.0,         # Cap nach Trinken
    "futter_max": 90.0,         # Cap nach Essen
    # Regeneration
    "energie_regen_h": 1.5,     # bei stabilen Werten (beide > 60)
    "gesundheit_regen_h": 1.0 / 6.0,  # sehr langsam: 1% / 6h
}


# ─── Zustand ─────────────────────────────────────────────────────────────────

@dataclass
class State:
    hunger: float = 100.0
    durst: float = 100.0
    energie: float = 100.0
    gesundheit: float = 100.0
    stimmung: float = 100.0
    letztes_wasser: float = -999.0   # Stunde des letzten Trinkens
    letztes_futter: float = -999.0


def clamp(v: float, lo=0.0, hi=100.0) -> float:
    return max(lo, min(hi, v))


def kann_wasser(s: State, cfg: dict, h: float) -> bool:
    cooldown_ok = (h - s.letztes_wasser) >= cfg["wasser_cooldown_h"]
    schwelle_ok = s.durst <= cfg["wasser_schwelle"]
    return cooldown_ok and schwelle_ok


def kann_futter(s: State, cfg: dict, h: float) -> bool:
    cooldown_ok = (h - s.letztes_futter) >= cfg["futter_cooldown_h"]
    schwelle_ok = s.hunger <= cfg["futter_schwelle"]
    return cooldown_ok and schwelle_ok


def tick(s: State, cfg: dict, h: float, dt: float = 1.0) -> tuple[State, list[str]]:
    """Simuliert dt Stunden. Gibt neuen Zustand und Aktionen zurück."""
    aktionen = []

    # Decay
    s.durst  = clamp(s.durst  - cfg["durst_pro_h"]  * dt)
    s.hunger = clamp(s.hunger - cfg["hunger_pro_h"] * dt)

    # Energie normal
    s.energie = clamp(s.energie - cfg["energie_pro_h_normal"] * dt)

    # Kaskade Energie
    if s.hunger < cfg["kaskade_schwelle"] and s.durst < cfg["kaskade_schwelle"]:
        s.energie = clamp(s.energie - cfg["energie_pro_h_kaskade"] * dt)

    # Stimmung Kaskade
    if s.hunger < cfg["kaskade_schwelle"] or s.durst < cfg["kaskade_schwelle"]:
        s.stimmung = clamp(s.stimmung - cfg["stimmung_pro_h_kaskade"] * dt)

    # Gesundheit
    gesund_kritisch = s.energie < cfg["gesundheit_schwelle"] and (
        s.hunger < 25.0 or s.durst < 25.0
    )
    if gesund_kritisch:
        s.gesundheit = clamp(s.gesundheit - cfg["gesundheit_pro_h"] * dt)
    elif s.hunger > 60 and s.durst > 60:
        # Langsame Regen nur wenn stabil
        s.gesundheit = clamp(s.gesundheit + cfg["gesundheit_regen_h"] * dt)

    # Energie Regen bei guter Pflege
    if s.hunger > 60 and s.durst > 60:
        s.energie = clamp(s.energie + cfg["energie_regen_h"] * dt)

    # Aktionen: immer wenn möglich in Simulation
    if kann_wasser(s, cfg, h):
        s.durst = clamp(s.durst + cfg["wasser_effekt"], hi=cfg["wasser_max"])
        s.letztes_wasser = h
        aktionen.append("W")

    if kann_futter(s, cfg, h):
        s.hunger = clamp(s.hunger + cfg["futter_effekt"], hi=cfg["futter_max"])
        s.letztes_futter = h
        aktionen.append("F")

    return s, aktionen


# ─── Szenarien ────────────────────────────────────────────────────────────────

def pflege_intervall(szenario: str, h: float, cfg: dict, s: State) -> tuple[bool, bool]:
    """Bestimmt ob Wesen pflegt (true = es würde wenn es kann)."""
    if szenario == "perfekt":
        return True, True
    elif szenario == "leicht_verspaetet":
        # Pflegt 1h verspätet nach Cooldown-Ende
        return (h % (cfg["wasser_cooldown_h"] + 1) < 0.1 or h < 2), \
               (h % (cfg["futter_cooldown_h"] + 1) < 0.1 or h < 2)
    elif szenario == "vernachlaessigt_12h":
        return h >= 12, h >= 12
    elif szenario == "vernachlaessigt_24h":
        return h >= 24, h >= 24
    elif szenario == "vernachlaessigt_48h":
        return h >= 48, h >= 48
    elif szenario == "ueberpflege":
        # Versucht immer zu klicken — wird durch Schwelle/Cooldown blockiert
        return True, True
    return False, False


def simuliere(cfg: dict, szenario: str, stunden: int = 72, dt: float = 1.0) -> list[dict]:
    s = State()
    rows = []

    for step in range(int(stunden / dt)):
        h = step * dt

        aktionen = []

        # Decay
        s.durst  = clamp(s.durst  - cfg["durst_pro_h"]  * dt)
        s.hunger = clamp(s.hunger - cfg["hunger_pro_h"] * dt)
        s.energie = clamp(s.energie - cfg["energie_pro_h_normal"] * dt)

        if s.hunger < cfg["kaskade_schwelle"] and s.durst < cfg["kaskade_schwelle"]:
            s.energie = clamp(s.energie - cfg["energie_pro_h_kaskade"] * dt)

        if s.hunger < cfg["kaskade_schwelle"] or s.durst < cfg["kaskade_schwelle"]:
            s.stimmung = clamp(s.stimmung - cfg["stimmung_pro_h_kaskade"] * dt)

        gesund_kritisch = s.energie < cfg["gesundheit_schwelle"] and (
            s.hunger < 25.0 or s.durst < 25.0
        )
        if gesund_kritisch:
            s.gesundheit = clamp(s.gesundheit - cfg["gesundheit_pro_h"] * dt)
        elif s.hunger > 60 and s.durst > 60:
            s.gesundheit = clamp(s.gesundheit + cfg["gesundheit_regen_h"] * dt)

        if s.hunger > 60 and s.durst > 60:
            s.energie = clamp(s.energie + cfg["energie_regen_h"] * dt)

        # Pflege — Wesen entscheidet ob es pflegt
        will_wasser, will_futter = pflege_intervall(szenario, h, cfg, s)

        if will_wasser and kann_wasser(s, cfg, h):
            s.durst = clamp(s.durst + cfg["wasser_effekt"], hi=cfg["wasser_max"])
            s.letztes_wasser = h
            aktionen.append("W")

        if will_futter and kann_futter(s, cfg, h):
            s.hunger = clamp(s.hunger + cfg["futter_effekt"], hi=cfg["futter_max"])
            s.letztes_futter = h
            aktionen.append("F")

        # Status
        if s.gesundheit <= 0:
            status = "TOT"
        elif s.gesundheit < 10:
            status = "KRITISCH"
        elif s.hunger < 25 or s.durst < 25:
            status = "WARNUNG"
        elif s.hunger < 40 or s.durst < 40:
            status = "BEOBACHTEN"
        else:
            status = "stabil"

        rows.append({
            "h": h,
            "hunger": round(s.hunger, 1),
            "durst": round(s.durst, 1),
            "energie": round(s.energie, 1),
            "gesundheit": round(s.gesundheit, 1),
            "stimmung": round(s.stimmung, 1),
            "aktionen": ",".join(aktionen) or "—",
            "status": status,
        })

        if s.gesundheit <= 0 and szenario not in ("vernachlaessigt_48h", "vernachlaessigt_24h"):
            # Nach Tod keine weitere Simulation
            break

    return rows


# ─── Ausgabe ──────────────────────────────────────────────────────────────────

def print_tabelle(rows: list[dict], titel: str, max_rows: int = 30):
    print(f"\n{'═' * 80}")
    print(f"  {titel}")
    print(f"{'═' * 80}")
    header = ["h", "Hunger", "Durst", "Energie", "Gesundh.", "Stimmung", "Aktion", "Status"]
    print(f"{'h':>4}  {'Hunger':>6}  {'Durst':>6}  {'Energie':>7}  {'Gesundh.':>8}  {'Stimmung':>8}  {'Aktion':>6}  Status")
    print("─" * 70)
    shown = 0
    for i, r in enumerate(rows):
        # Zeige nur jeden n-ten Eintrag um Tabelle lesbar zu halten
        if len(rows) > max_rows and i % max(1, len(rows) // max_rows) != 0:
            if r["status"] not in ("TOT", "KRITISCH", "WARNUNG") and r["aktionen"] == "—":
                continue
        print(f"{r['h']:4.0f}  {r['hunger']:6.1f}  {r['durst']:6.1f}  {r['energie']:7.1f}  "
              f"{r['gesundheit']:8.1f}  {r['stimmung']:8.1f}  {r['aktionen']:>6}  {r['status']}")
        shown += 1
    if rows:
        last = rows[-1]
        if last["status"] == "TOT":
            print(f"\n  ► TOT nach {last['h']:.0f} Stunden")
        else:
            print(f"\n  ► Endzustand ({last['h']:.0f}h): "
                  f"H={last['hunger']}  D={last['durst']}  E={last['energie']}  "
                  f"G={last['gesundheit']}  [{last['status']}]")


def bewerte(alle_szenarien: dict) -> str:
    lines = []
    lines.append("\n" + "═" * 80)
    lines.append("  BALANCING-BEWERTUNG")
    lines.append("═" * 80)
    for cfg_name, szenarien in alle_szenarien.items():
        lines.append(f"\n  [{cfg_name}]")
        for sz_name, rows in szenarien.items():
            if not rows:
                lines.append(f"    {sz_name:30}: (leer)")
                continue
            last = rows[-1]
            erste_warnung = next((r for r in rows if r["status"] in ("WARNUNG", "KRITISCH", "TOT")), None)
            tot = last["status"] == "TOT"
            h_tot = last["h"] if tot else None
            h_warn = erste_warnung["h"] if erste_warnung else None
            zeile = f"    {sz_name:30}: "
            if tot:
                zeile += f"TOT nach {h_tot:.0f}h"
            else:
                zeile += f"Überlebt {last['h']:.0f}h | H={last['hunger']} D={last['durst']} G={last['gesundheit']}"
            if h_warn:
                zeile += f" | erste Warnung: {h_warn:.0f}h"
            lines.append(zeile)
    return "\n".join(lines)


def save_csv(cfg_name: str, sz_name: str, rows: list[dict], out_dir: Path):
    fname = out_dir / f"sim_{cfg_name.split()[0].lower()}_{sz_name}.csv"
    with open(fname, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


# ─── Empfehlungen ─────────────────────────────────────────────────────────────

def empfehlung(alle: dict):
    print("\n" + "═" * 80)
    print("  EMPFEHLUNGEN")
    print("═" * 80)
    print("""
  IST-Problem:
  ─────────────
  • Durst sinkt 18%/h → nach 5.5h komplett leer ohne Pflege
  • Hunger sinkt 12%/h → nach 8.3h leer
  • Wesen müssen sehr oft klicken — keine Aktionsschwellen, kein Cooldown
  • 4/6 Cyberlinge sind bereits TOT
  • Bei 24h Vernachlässigung: sicher TOT

  SOLL-Vorschlag:
  ────────────────
  • Durst sinkt 6%/h → nach 11.7h leer (ohne Pflege)
  • Hunger sinkt 3%/h → nach 22h leer
  • Aktionsschwelle: Wasser erst bei Durst ≤ 70, Futter erst bei Hunger ≤ 65
  • Cooldown: Wasser 3h, Futter 6h
  • Cap: Wasser bis max 88%, Futter bis max 90%
  • Gesundheit regeneriert langsam (+1% alle 6h) wenn stabil
  • Fairness: Nach Wasser (+22%) bei Cooldown 3h → darf Durst nicht vor 3h wieder kritisch
    Check: 88% → 88-6*3=70% nach 3h → noch kein Notfall → FAIR ✓

  Konkrete Werte für api.py / cyberling_daemon.py:
  ──────────────────────────────────────────────────
  DURST_PRO_H    = 0.06     # war 0.18 → 3x langsamer
  HUNGER_PRO_H   = 0.03     # war 0.12 → 4x langsamer
  ENERGIE_PRO_H_NORMAL   = 0.02
  ENERGIE_PRO_H_KASKADE  = 0.04   # zusätzlich wenn H+D < 40
  STIMMUNG_PRO_H_KASKADE = 0.02
  GESUNDHEIT_PRO_H       = 0.03   # wenn Energie < 30 UND H od. D < 25
  GESUNDHEIT_REGEN       = 0.00167  # +1%/6h bei stabilen Werten
  ENERGIE_REGEN          = 0.015   # +1.5%/h bei stabilen Werten

  WASSER_SCHWELLE = 0.70    # erst erlaubt wenn Durst ≤ 70%
  FUTTER_SCHWELLE = 0.65    # erst erlaubt wenn Hunger ≤ 65%
  WASSER_CAP      = 0.88    # max nach Trinken
  FUTTER_CAP      = 0.90    # max nach Essen
  WASSER_COOLDOWN_H = 3.0
  FUTTER_COOLDOWN_H = 6.0

  Bewertung:
  ──────────
  IST: zu aggressiv → 4/6 bereits tot → kein fairer Spielraum → kaputt
  SOLL: erfordert 1x Wasser alle ~3h, 1x Futter alle ~6h
        12h Vernachlässigung → Warnung aber überlebbar
        24h → kritisch aber reparierbar
        48h → Gefahr, Gesundheit sinkt
        Überpflege → durch Schwelle + Cooldown blockiert

  WICHTIG vor Implementierung:
  • Bestehende tote Cyberlinge manuell beleben (gesundheit=0.5, hunger=0.6, durst=0.6)
  • Rates erst nach Daniels Freigabe in daemon übertragen
  • Aktionsschwellen in api.py ergänzen (cyberling/füttern/aktion)
""")


def main():
    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)

    szenarien_namen = [
        "perfekt",
        "leicht_verspaetet",
        "vernachlaessigt_12h",
        "vernachlaessigt_24h",
        "vernachlaessigt_48h",
        "ueberpflege",
    ]

    alle_ergebnisse: dict[str, dict] = {}

    for cfg in [IST, SOLL]:
        cfg_name = cfg["name"]
        alle_ergebnisse[cfg_name] = {}
        print(f"\n\n{'#' * 80}")
        print(f"# KONFIGURATION: {cfg_name}")
        print(f"# Durst: {cfg['durst_pro_h']}%/h | Hunger: {cfg['hunger_pro_h']}%/h")
        print(f"# Wasser-Schwelle: ≤{cfg['wasser_schwelle']}% | Cooldown: {cfg['wasser_cooldown_h']}h")
        print(f"# Futter-Schwelle: ≤{cfg['futter_schwelle']}% | Cooldown: {cfg['futter_cooldown_h']}h")
        print(f"{'#' * 80}")

        for sz in szenarien_namen:
            rows = simuliere(cfg, sz, stunden=72)
            alle_ergebnisse[cfg_name][sz] = rows
            titel = f"{cfg_name} | Szenario: {sz.replace('_', ' ').upper()}"
            print_tabelle(rows, titel)
            save_csv(cfg["name"].split()[0].lower(), sz, rows, out_dir)

    print(bewerte(alle_ergebnisse))
    empfehlung(alle_ergebnisse)
    print(f"\n  CSV-Dateien gespeichert in: {out_dir}/")


if __name__ == "__main__":
    main()
