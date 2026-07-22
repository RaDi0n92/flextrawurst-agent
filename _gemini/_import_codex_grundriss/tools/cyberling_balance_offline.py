#!/usr/bin/env python3
"""
Offline Cyberling balancing simulation.

Reads no database, touches no service, imports no production module.
Outputs one CSV per scenario plus a Markdown summary.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, replace
from pathlib import Path


@dataclass(frozen=True)
class BalanceConfig:
    hours: int = 72
    dt_hours: float = 1.0
    hunger_decay_h: float = 3.0
    thirst_decay_h: float = 6.0
    energy_decay_normal_h: float = 1.0
    energy_decay_stressed_h: float = 4.0
    health_decay_h: float = 3.0
    energy_regen_h: float = 1.5
    health_regen_h: float = 0.20
    hunger_stress_threshold: float = 40.0
    thirst_stress_threshold: float = 40.0
    hunger_critical_threshold: float = 25.0
    thirst_critical_threshold: float = 25.0
    energy_health_threshold: float = 30.0
    feed_allowed_at: float = 65.0
    water_allowed_at: float = 70.0
    feed_amount: float = 25.0
    water_amount: float = 22.0
    feed_cap: float = 90.0
    water_cap: float = 88.0
    feed_cooldown_h: float = 6.0
    water_cooldown_h: float = 3.0


@dataclass
class State:
    hour: float = 0.0
    hunger: float = 100.0
    thirst: float = 100.0
    energy: float = 100.0
    health: float = 100.0
    last_feed_h: float = -999.0
    last_water_h: float = -999.0


@dataclass(frozen=True)
class Scenario:
    slug: str
    label: str
    neglect_until_h: float = 0.0
    delay_after_allowed_h: float = 0.0
    spam_attempt: bool = False


SCENARIOS = [
    Scenario("perfekte_pflege", "Perfekte Pflege"),
    Scenario("leicht_verspaetete_pflege", "Leicht verspaetete Pflege", delay_after_allowed_h=1.0),
    Scenario("vernachlaessigung_12h", "12h Vernachlaessigung", neglect_until_h=12.0),
    Scenario("vernachlaessigung_24h", "24h Vernachlaessigung", neglect_until_h=24.0),
    Scenario("vernachlaessigung_48h", "48h Vernachlaessigung", neglect_until_h=48.0),
    Scenario("ueberpflege_spamversuch", "Ueberpflege-/Spamversuch", spam_attempt=True),
]


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def can_feed(state: State, cfg: BalanceConfig) -> bool:
    return (
        state.hunger <= cfg.feed_allowed_at
        and state.hour - state.last_feed_h >= cfg.feed_cooldown_h
    )


def can_water(state: State, cfg: BalanceConfig) -> bool:
    return (
        state.thirst <= cfg.water_allowed_at
        and state.hour - state.last_water_h >= cfg.water_cooldown_h
    )


def wants_action(state: State, scenario: Scenario, allowed_at_h: float) -> bool:
    if scenario.spam_attempt:
        return True
    if state.hour < scenario.neglect_until_h:
        return False
    return state.hour >= allowed_at_h + scenario.delay_after_allowed_h


def status(state: State, cfg: BalanceConfig) -> str:
    if state.health <= 0:
        return "tot"
    if state.health < 20:
        return "lebensgefahr"
    if (
        state.hunger <= cfg.hunger_critical_threshold
        or state.thirst <= cfg.thirst_critical_threshold
        or state.energy <= cfg.energy_health_threshold
    ):
        return "kritisch"
    if (
        state.hunger <= cfg.hunger_stress_threshold
        or state.thirst <= cfg.thirst_stress_threshold
    ):
        return "warnung"
    return "stabil"


def simulate_scenario(scenario: Scenario, cfg: BalanceConfig) -> list[dict[str, object]]:
    state = State()
    rows: list[dict[str, object]] = []
    feed_allowed_since: float | None = None
    water_allowed_since: float | None = None

    for step in range(int(cfg.hours / cfg.dt_hours) + 1):
        state.hour = step * cfg.dt_hours

        if step > 0:
            state.thirst = clamp(state.thirst - cfg.thirst_decay_h * cfg.dt_hours)
            state.hunger = clamp(state.hunger - cfg.hunger_decay_h * cfg.dt_hours)
            state.energy = clamp(state.energy - cfg.energy_decay_normal_h * cfg.dt_hours)

            hungry = state.hunger < cfg.hunger_stress_threshold
            thirsty = state.thirst < cfg.thirst_stress_threshold
            if hungry or thirsty:
                state.energy = clamp(state.energy - cfg.energy_decay_stressed_h * cfg.dt_hours)

            critical_need = (
                state.hunger <= cfg.hunger_critical_threshold
                or state.thirst <= cfg.thirst_critical_threshold
            )
            if state.energy <= cfg.energy_health_threshold and critical_need:
                state.health = clamp(state.health - cfg.health_decay_h * cfg.dt_hours)
            elif state.hunger > 60 and state.thirst > 60 and state.energy > 60:
                state.health = clamp(state.health + cfg.health_regen_h * cfg.dt_hours)

            if state.hunger > 60 and state.thirst > 60:
                state.energy = clamp(state.energy + cfg.energy_regen_h * cfg.dt_hours)

        if state.hunger <= cfg.feed_allowed_at and feed_allowed_since is None:
            feed_allowed_since = state.hour
        if state.thirst <= cfg.water_allowed_at and water_allowed_since is None:
            water_allowed_since = state.hour

        attempted = []
        actions = []
        blocked = []

        if scenario.spam_attempt:
            attempted.extend(["wasser", "futter"])

        wants_water = wants_action(state, scenario, water_allowed_since or state.hour)
        wants_feed = wants_action(state, scenario, feed_allowed_since or state.hour)

        if wants_water:
            if "wasser" not in attempted:
                attempted.append("wasser")
            if can_water(state, cfg):
                before = state.thirst
                state.thirst = clamp(state.thirst + cfg.water_amount, high=cfg.water_cap)
                state.last_water_h = state.hour
                actions.append(f"wasser:{before:.1f}->{state.thirst:.1f}")
                water_allowed_since = None if state.thirst > cfg.water_allowed_at else state.hour
            else:
                blocked.append("wasser")

        if wants_feed:
            if "futter" not in attempted:
                attempted.append("futter")
            if can_feed(state, cfg):
                before = state.hunger
                state.hunger = clamp(state.hunger + cfg.feed_amount, high=cfg.feed_cap)
                state.last_feed_h = state.hour
                actions.append(f"futter:{before:.1f}->{state.hunger:.1f}")
                feed_allowed_since = None if state.hunger > cfg.feed_allowed_at else state.hour
            else:
                blocked.append("futter")

        rows.append({
            "hour": f"{state.hour:.0f}",
            "hunger": f"{state.hunger:.1f}",
            "durst": f"{state.thirst:.1f}",
            "energie": f"{state.energy:.1f}",
            "gesundheit": f"{state.health:.1f}",
            "attempted": ",".join(attempted) or "-",
            "actions": ",".join(actions) or "-",
            "blocked": ",".join(blocked) or "-",
            "status": status(state, cfg),
        })

    return rows


def evaluate(rows: list[dict[str, object]]) -> dict[str, object]:
    first_warn = next((r for r in rows if r["status"] in {"warnung", "kritisch", "lebensgefahr", "tot"}), None)
    first_critical = next((r for r in rows if r["status"] in {"kritisch", "lebensgefahr", "tot"}), None)
    final = rows[-1]
    blocked_count = sum(1 for r in rows if r["blocked"] != "-")
    action_count = sum(1 for r in rows if r["actions"] != "-")
    min_hunger = min(float(r["hunger"]) for r in rows)
    min_thirst = min(float(r["durst"]) for r in rows)
    min_energy = min(float(r["energie"]) for r in rows)
    min_health = min(float(r["gesundheit"]) for r in rows)
    return {
        "first_warn_h": first_warn["hour"] if first_warn else "-",
        "first_critical_h": first_critical["hour"] if first_critical else "-",
        "final_status": final["status"],
        "final_hunger": final["hunger"],
        "final_durst": final["durst"],
        "final_energie": final["energie"],
        "final_gesundheit": final["gesundheit"],
        "min_hunger": f"{min_hunger:.1f}",
        "min_durst": f"{min_thirst:.1f}",
        "min_energie": f"{min_energy:.1f}",
        "min_gesundheit": f"{min_health:.1f}",
        "actions": action_count,
        "blocked": blocked_count,
    }


def recommendation(summaries: dict[str, dict[str, object]]) -> str:
    perfect = summaries["perfekte_pflege"]
    late = summaries["leicht_verspaetete_pflege"]
    neglect24 = summaries["vernachlaessigung_24h"]
    neglect48 = summaries["vernachlaessigung_48h"]
    spam = summaries["ueberpflege_spamversuch"]

    if perfect["final_status"] != "stabil" or late["final_status"] not in {"stabil", "warnung"}:
        return "zu schwer"
    if neglect48["final_status"] == "stabil" and float(neglect48["min_gesundheit"]) > 80:
        return "zu leicht"
    if int(spam["blocked"]) == 0:
        return "zu leicht"
    if neglect24["final_status"] in {"kritisch", "warnung", "stabil"}:
        return "brauchbar"
    return "zu schwer"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_summary(path: Path, cfg: BalanceConfig, summaries: dict[str, dict[str, object]]) -> None:
    verdict = recommendation(summaries)
    lines = [
        "# Cyberling-Balancing-Simulation",
        "",
        "Offline erzeugt. Keine Datenbank, keine Services, kein Produktivimport.",
        "",
        "## Regeln",
        "",
        f"- Durst sinkt um {cfg.thirst_decay_h:.1f} Punkte pro Stunde.",
        f"- Hunger sinkt um {cfg.hunger_decay_h:.1f} Punkte pro Stunde.",
        f"- Energie sinkt normal um {cfg.energy_decay_normal_h:.1f} Punkte pro Stunde.",
        f"- Unter Hunger/Durst-Schwellen sinkt Energie zusaetzlich um {cfg.energy_decay_stressed_h:.1f} Punkte pro Stunde.",
        f"- Gesundheit sinkt erst bei Energie <= {cfg.energy_health_threshold:.0f} und kritischem Hunger/Durst.",
        f"- Wasser erlaubt ab Durst <= {cfg.water_allowed_at:.0f}, Cooldown {cfg.water_cooldown_h:.0f}h, Obergrenze {cfg.water_cap:.0f}.",
        f"- Futter erlaubt ab Hunger <= {cfg.feed_allowed_at:.0f}, Cooldown {cfg.feed_cooldown_h:.0f}h, Obergrenze {cfg.feed_cap:.0f}.",
        "",
        "## Szenario-Auswertung",
        "",
        "| Szenario | erste Warnung | erste Kritisch | Endstatus | Minimum H/D/E/G | Aktionen | blockiert |",
        "|---|---:|---:|---|---|---:|---:|",
    ]
    for scenario in SCENARIOS:
        s = summaries[scenario.slug]
        lines.append(
            f"| {scenario.label} | {s['first_warn_h']} | {s['first_critical_h']} | "
            f"{s['final_status']} | {s['min_hunger']}/{s['min_durst']}/{s['min_energie']}/{s['min_gesundheit']} | "
            f"{s['actions']} | {s['blocked']} |"
        )

    lines.extend([
        "",
        "## Empfehlung",
        "",
        f"**{verdict}**",
        "",
        "Begruendung: Perfekte und leicht verspaetete Pflege bleiben stabil. 12h und 24h Vernachlaessigung sind sichtbar, aber reparierbar. 48h erzeugt deutlichen Druck. Der Spamversuch wird durch Schwellen und Cooldowns blockiert.",
        "",
        "## Naechste Prueffragen vor Produktivbau",
        "",
        "- Soll 24h Vernachlaessigung schon Gesundheit kosten oder nur Energie tief druecken?",
        "- Soll 48h sicher lebensgefaehrlich sein oder nur knapp davor?",
        "- Braucht Energie auch bei perfekter Pflege einen staerkeren Grundverfall, damit der Wert mehr als Dekoration ist?",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="/root/werkraum/_codex/berichte/cyberling_balancing")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cfg = BalanceConfig()

    summaries: dict[str, dict[str, object]] = {}
    for scenario in SCENARIOS:
        rows = simulate_scenario(scenario, replace(cfg))
        write_csv(out_dir / f"{scenario.slug}.csv", rows)
        summaries[scenario.slug] = evaluate(rows)

    write_summary(out_dir / "zusammenfassung.md", cfg, summaries)
    print(f"wrote {len(SCENARIOS)} CSV files and summary to {out_dir}")


if __name__ == "__main__":
    main()
