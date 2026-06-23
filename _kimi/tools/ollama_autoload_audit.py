#!/usr/bin/env python3
"""
Read-only Audit: Welche Dienste/Dateien koennen Gemma4, HauhauCS oder Qwen3-VL
im Hintergrund laden?

Laeuft komplett read-only. Stoppt keine Services, aendert nichts.
Ausgabe: Markdown-Bericht in _kimi/berichte/
"""

import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

REPORT_DIR = Path("/root/werkraum/_kimi/berichte")
SCRIPT_DIR = Path("/root/werkraum/_kimi/tools")

# Muster, die als Autoload-Verdacht gelten
MODEL_PATTERNS = {
    "hauhaucs": re.compile(r"hauhaucs|fredrezones55|IQ4_XS", re.IGNORECASE),
    "gemma4": re.compile(r"gemma4", re.IGNORECASE),
    "qwen3-vl": re.compile(r"qwen3-vl|30b-a3b-instruct", re.IGNORECASE),
    "qwen3.6": re.compile(r"qwen3\.6|Qwen3\.6-35B", re.IGNORECASE),
    "dolphin3": re.compile(r"dolphin3", re.IGNORECASE),
    "qwen_allgemein": re.compile(r"qwen3", re.IGNORECASE),
}

# Ollama-Modell-Referenzen
OLLAMA_PULL_PATTERN = re.compile(r"ollama\s+(pull|run)", re.IGNORECASE)

SYSTEMD_DIRS = [
    Path("/etc/systemd/system"),
    Path("/root/.config/systemd/user"),
]

CODE_ROOTS = [
    Path("/root/werkraum"),
    Path("/root/flextrawurst"),
    Path("/root/zensi"),
]

# Verzeichnisse, die keinen Autoload-Code enthalten (nur zum Ausschluss)
SKIP_DIRS = {
    "__pycache__", ".git", "node_modules", ".venv", "venv", ".pytest_cache",
    "graphify-out", "out", "public", "bilder", "backup-flextrawurst",
    "_claude", "_codex", "_kimi",  # Mirrors/Notizen nicht als Quelle
    ".next", "dist", "build",
}

# Dateiendungen, die wir lesen wollen
CODE_EXTS = {".py", ".ts", ".js", ".sh", ".service", ".timer", ".conf", ".ini", ".env", ".json"}


def run(cmd: list[str]) -> str:
    try:
        return subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        ).stdout.strip()
    except Exception as e:
        return f"FEHLER: {e}"


def find_model_hits(text: str) -> list[tuple]:
    """Findet alle Modell-Namen in einem Text."""
    hits = []
    seen = set()
    for name, pat in MODEL_PATTERNS.items():
        for m in pat.finditer(text):
            key = (name, m.start())
            if key not in seen:
                seen.add(key)
                hits.append((name, m.group()))
    return hits


def parse_systemd_unit(path: Path) -> dict | None:
    try:
        raw = path.read_bytes()
        if b"\x00" in raw:
            return None
        text = raw.decode("utf-8", errors="ignore")
    except (FileNotFoundError, OSError):
        return None
    data = {
        "path": str(path),
        "filename": path.name,
        "unit_type": path.suffix.lstrip("."),
        "exec_start": [],
        "working_dir": None,
        "environment": [],
        "environment_files": [],
        "model_hits": [],
        "ollama_hits": [],
        "triggers": None,  # fuer Timer: welche Service wird getriggert
    }
    for line in text.splitlines():
        line = line.strip()
        lline = line.lower()
        if lline.startswith("execstart="):
            data["exec_start"].append(line.split("=", 1)[1])
        elif lline.startswith("workingdirectory="):
            data["working_dir"] = line.split("=", 1)[1]
        elif lline.startswith("environment="):
            data["environment"].append(line.split("=", 1)[1])
        elif lline.startswith("environmentfile="):
            env_file = line.split("=", 1)[1]
            data["environment_files"].append(env_file)
            data["environment"].append(f"file:{env_file}")
        elif lline.startswith("unit="):
            data["triggers"] = line.split("=", 1)[1]

        hits = find_model_hits(line)
        for name, match in hits:
            data["model_hits"].append((name, line))
        if OLLAMA_PULL_PATTERN.search(line):
            data["ollama_hits"].append(("pull/run", line))
    return data


def scan_systemd() -> list[dict]:
    units = []
    for d in SYSTEMD_DIRS:
        if not d.exists():
            continue
        for path in sorted(d.iterdir()):
            if path.suffix in (".service", ".timer", ".socket", ".target"):
                parsed = parse_systemd_unit(path)
                if parsed is not None:
                    units.append(parsed)
    return units


def is_binary_file(path: Path) -> bool:
    """Heuristik: ELF-Binaer oder enthaelt NUL-Bytes."""
    try:
        raw = path.read_bytes()
    except Exception:
        return True
    if raw.startswith(b"\x7fELF") or raw.startswith(b"MZ"):
        return True
    if b"\x00" in raw:
        return True
    return False


def read_text_file(path: Path) -> str | None:
    """Liest eine Textdatei, ignoriert Binaerdateien."""
    if is_binary_file(path):
        return None
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None


def scan_single_file(path: Path, root: Path) -> dict[str, list[tuple]] | None:
    if not path.is_file():
        return None
    if any(part in SKIP_DIRS for part in path.parts):
        return None
    text = read_text_file(path)
    if text is None:
        return None
    hits = defaultdict(list)
    lines = text.splitlines()
    for lineno, line in enumerate(lines, 1):
        model_hits = find_model_hits(line)
        for name, match in model_hits:
            hits[name].append((str(path.relative_to(root)), lineno, line.strip()))
        if OLLAMA_PULL_PATTERN.search(line):
            hits["ollama_pull_run"].append((str(path.relative_to(root)), lineno, line.strip()))
    return hits


def merge_hits(target: dict, source: dict):
    for key, values in source.items():
        target[key].extend(values)


def scan_code() -> dict[str, list[tuple]]:
    """Scannt Code-Dateien nach Modell-Namen und Ollama-Aufrufen."""
    hits = defaultdict(list)
    for root in CODE_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_dir():
                continue
            if path.suffix not in CODE_EXTS:
                continue
            file_hits = scan_single_file(path, root)
            if file_hits:
                merge_hits(hits, file_hits)
    return hits


INTERPRETER_NAMES = {
    "python", "python3", "python2", "python3.12", "python3.11", "python3.10",
    "bash", "sh", "node", "nodejs", "perl", "ruby", "env",
}


def is_interpreter(path: Path) -> bool:
    return path.name in INTERPRETER_NAMES or str(path) == "/usr/bin/env"


def resolve_path(raw: str, working_dir: str | None) -> Path | None:
    """Versucht den ausfuehrbaren Script-Pfad aus ExecStart aufzuloesen.
    Ueberspringt Interpreter wie python3, bash, node. Behandelt auch relative Pfade."""
    parts = raw.split()
    for p in parts:
        if p.startswith("-"):
            continue
        if p.startswith("/") or p.startswith("./") or p.startswith("../"):
            candidate = Path(p)
            if is_interpreter(candidate):
                continue
            if candidate.is_absolute():
                return candidate
            if working_dir:
                return Path(working_dir) / candidate
        elif "/" in p or "." in p:
            # Relativer Pfad ohne ./ (z.B. "scripts/serve.ts")
            if working_dir:
                candidate = Path(working_dir) / p
                if candidate.exists():
                    return candidate
    return None


def scan_referenced_files(units: list[dict]) -> dict[str, list[tuple]]:
    """Scannt Dateien, auf die systemd-Units verweisen (Scripts, Env-Files)."""
    hits = defaultdict(list)
    for u in units:
        working_dir = u.get("working_dir")
        # ExecStart-Scripts
        for exec_start in u.get("exec_start", []):
            script_path = resolve_path(exec_start, working_dir)
            if script_path and script_path.is_file():
                file_hits = scan_single_file(script_path, script_path.parent)
                if file_hits:
                    # Pfad relativ zur Unit notieren
                    for key, values in file_hits.items():
                        for path_rel, lineno, line in values:
                            hits[key].append((f"{u['filename']} -> {script_path}", lineno, line))
        # EnvironmentFiles
        for env_file in u.get("environment_files", []):
            env_path = resolve_path(env_file, working_dir)
            if env_path and env_path.is_file():
                file_hits = scan_single_file(env_path, env_path.parent)
                if file_hits:
                    for key, values in file_hits.items():
                        for path_rel, lineno, line in values:
                            hits[key].append((f"{u['filename']} -> {env_path}", lineno, line))
    return hits


def current_ollama_ps() -> str:
    return run(["ollama", "ps"])


def current_timers() -> str:
    return run(["systemctl", "list-timers", "--all"])


def active_services() -> str:
    return run(["systemctl", "list-units", "--type=service", "--state=running", "--no-pager"])


def unit_status() -> str:
    return run(["systemctl", "list-unit-files", "--type=service,timer", "--no-pager"])


def parse_unit_status(unit_status_str: str) -> dict[str, str]:
    """Parst `systemctl list-unit-files` in ein Dict unit -> state."""
    states = {}
    for line in unit_status_str.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0].endswith((".service", ".timer")):
            states[parts[0]] = parts[1]
    return states


def detect_background_loops(text: str, ext: str = "") -> list[str]:
    """Sucht nach Hinweisen auf Endlosschleifen / regelmaessige Hintergrundaktivitaet.
    Filtern nach Dateiendung, um String-Literals aus anderen Sprachen zu ignorieren."""
    indicators = []
    ext = ext.lower()

    python_patterns = [
        (r"while\s+(True|1)\s*:", "Python-Endlosschleife"),
        (r"threading\.Timer", "Python-Threading-Timer"),
        (r"sched\.scheduler", "Python-sched"),
        (r"asyncio\.create_task", "Python-asyncio-Task"),
        (r"schedule\.every", "Python-schedule"),
    ]
    js_patterns = [
        (r"while\s*\(true\)", "JS-Endlosschleife"),
        (r"setInterval\s*\(", "JS-setInterval"),
        (r"setTimeout\s*\(", "JS-setTimeout"),
    ]
    generic_patterns = [
        (r"@app\.cron|crontab", "Scheduling-Bibliothek"),
    ]

    patterns = []
    if ext in (".py", ""):
        patterns.extend(python_patterns)
    if ext in (".js", ".ts", ""):
        patterns.extend(js_patterns)
    patterns.extend(generic_patterns)

    for pat, label in patterns:
        if re.search(pat, text, re.IGNORECASE):
            indicators.append(label)
    return indicators


def check_cron() -> list[dict]:
    """Liest root-Crontab und systemweite cron.d-Eintraege."""
    entries = []
    # root crontab
    try:
        out = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=10).stdout
        for line in out.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if re.match(r"^\*+\/\d+|\d+\s+\*", line):
                entries.append({"source": "root crontab", "line": line})
    except Exception:
        pass
    # cron.d
    cron_d = Path("/etc/cron.d")
    if cron_d.exists():
        for f in cron_d.iterdir():
            if f.name.startswith("."):
                continue
            try:
                text = f.read_text(errors="ignore")
                for line in text.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if re.match(r"^\*+\/\d+|\d+\s+\*", line):
                        entries.append({"source": f"cron.d/{f.name}", "line": line})
            except Exception:
                pass
    return entries


def assess_risks(units: list[dict], states: dict[str, str], cron_entries: list[dict],
                 code_hits: dict, ref_hits: dict) -> list[dict]:
    """Erstellt eine priorisierte Risikoliste."""
    risks = []

    for u in units:
        state = states.get(u["filename"], "unknown")
        is_enabled = state in ("enabled", "enabled-runtime", "static")
        is_timer = u["unit_type"] == "timer"
        has_model = bool(u["model_hits"] or u["ollama_hits"])
        ref_model_names = set()

        # Wir brauchen den kompletten Unit-Text, um Restart zu pruefen
        try:
            raw = Path(u["path"]).read_bytes()
            unit_text = raw.decode("utf-8", errors="ignore").lower()
        except Exception:
            unit_text = ""

        restart_policy = "none"
        for line in unit_text.splitlines():
            if line.strip().startswith("restart="):
                restart_policy = line.strip().split("=", 1)[1]

        risk_level = None
        reasons = []

        if has_model and is_enabled:
            if is_timer:
                risk_level = "HOCH"
                reasons.append(f"Timer ist {state} und triggert Service mit Modell-Verweisen")
            elif restart_policy in ("always", "on-failure"):
                risk_level = "HOCH"
                reasons.append(f"Service ist {state} mit Restart={restart_policy} und Modell-Verweisen")
            else:
                risk_level = "MITTEL"
                reasons.append(f"Service ist {state} und enthaelt Modell-Verweise (kein Autorestart)")

        # Pruefe referenzierte Scripts auf Modell-Verweise und Hintergrundloops
        for exec_start in u.get("exec_start", []):
            script_path = resolve_path(exec_start, u.get("working_dir"))
            if script_path and script_path.is_file():
                text = read_text_file(script_path)
                if text is None:
                    continue
                script_hits = find_model_hits(text)
                for name, _ in script_hits:
                    ref_model_names.add(name)
                loops = detect_background_loops(text, script_path.suffix)
                if loops and (has_model or ref_model_names):
                    if risk_level not in ("HOCH", "MITTEL"):
                        risk_level = "MITTEL"
                    reasons.append(f"Script `{script_path.name}` enthaelt: {', '.join(loops)}")

        # Auch EnvironmentFiles auf Modell-Verweise pruefen
        for env_file in u.get("environment_files", []):
            env_path = resolve_path(env_file, u.get("working_dir"))
            if env_path and env_path.is_file():
                text = read_text_file(env_path)
                if text is None:
                    continue
                for name, _ in find_model_hits(text):
                    ref_model_names.add(name)

        # Falls die Unit selbst kein Modell nennt, aber referenzierte Dateien — Risiko bewerten
        if ref_model_names and is_enabled and not risk_level:
            if is_timer:
                risk_level = "HOCH"
                reasons.append(f"Timer ist {state} und referenziert Dateien mit Modell-Verweisen")
            elif restart_policy in ("always", "on-failure"):
                risk_level = "HOCH"
                reasons.append(f"Service ist {state} mit Restart={restart_policy} und referenziert Dateien mit Modell-Verweisen")
            else:
                risk_level = "MITTEL"
                reasons.append(f"Service ist {state} und referenziert Dateien mit Modell-Verweisen")

        if risk_level:
            all_models = {name for name, _ in u.get("model_hits", [])} | ref_model_names
            risks.append({
                "unit": u["filename"],
                "state": state,
                "risk": risk_level,
                "reasons": reasons,
                "model_hits": sorted(all_models),
                "restart": restart_policy,
                "type": u["unit_type"],
            })

    # Cron-Eintraege pruefen
    for entry in cron_entries:
        cmd = entry["line"]
        # Pruefe, ob das Kommando auf einen Pfad verweist, der Modelle enthaelt
        matches_model = any(pat.search(cmd) for pat in MODEL_PATTERNS.values())
        if matches_model or "ollama" in cmd.lower():
            risks.append({
                "unit": entry["source"],
                "state": "cron",
                "risk": "MITTEL",
                "reasons": [f"Cron-Eintrag enthaelt Modell/Ollama-Referenz: {cmd[:80]}"],
                "model_hits": [],
                "restart": "n/a",
                "type": "cron",
            })

    # Sortiere: HOCH, MITTEL, NIEDRIG
    order = {"HOCH": 0, "MITTEL": 1, "NIEDRIG": 2}
    risks.sort(key=lambda x: order.get(x["risk"], 99))
    return risks


def build_report(units: list[dict], code_hits: dict, ref_hits: dict,
                 ollama_ps: str, timers: str, services: str, unit_status_str: str,
                 risks: list[dict], cron_entries: list[dict]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "---",
        f"datum: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "autor: kimi bei Daniels VPS",
        "betrifft: [ollama, autoload, gemma4, hauhaucs, qwen3-vl, systemd]",
        "importable: false",
        "---",
        "",
        "# Ollama Autoload-Audit",
        "",
        f"Erstellt: {now}",
        "",
        "Dieser Bericht zeigt, welche systemd-Units und Code-Dateien Modelle im Hintergrund laden koennen.",
        "Read-only — keine Services wurden gestoppt oder veraendert.",
        "",
        "## Zusammenfassung",
        "",
    ]

    units_with_models = [u for u in units if u["model_hits"] or u["ollama_hits"]]
    lines.append(f"- systemd-Units mit Modell/Ollama-Verdacht: {len(units_with_models)}")
    lines.append("- Code-Dateien mit Modell-Verweisen:")
    for name in sorted(MODEL_PATTERNS.keys()):
        count = len(code_hits.get(name, [])) + len(ref_hits.get(name, []))
        lines.append(f"  - `{name}`: {count} Treffer")
    lines.append("")

    lines.append("## Risiko-Einschaetzung: Was koennte ohne Erlaubnis ein Modell laden?")
    lines.append("")
    if not risks:
        lines.append("Keine aktiven Autoload-Risiken identifiziert.")
    else:
        lines.append(f"**{len(risks)} Risiko-Eintraege gefunden.**")
        lines.append("")
        current_level = None
        for r in risks:
            if r["risk"] != current_level:
                current_level = r["risk"]
                lines.append(f"### Risiko {current_level}")
                lines.append("")
            lines.append(f"- **`{r['unit']}`** ({r['type']}, state={r['state']}, restart={r['restart']})")
            for reason in r["reasons"]:
                lines.append(f"  - {reason}")
            if r["model_hits"]:
                lines.append(f"  - Modelle: {', '.join(f'`{m}`' for m in r['model_hits'])}")
            lines.append("")
    lines.append("")

    lines.append("### Cron-Jobs (alle, nicht nur Modell-bezogene)")
    lines.append("")
    if not cron_entries:
        lines.append("Keine Cron-Jobs gefunden.")
    else:
        for entry in cron_entries:
            lines.append(f"- **{entry['source']}**: `{entry['line']}`")
    lines.append("")

    lines.append("## Aktuell geladene Modelle (`ollama ps`)")
    lines.append("")
    lines.append("```")
    lines.append(ollama_ps if ollama_ps else "(keine Ausgabe)")
    lines.append("```")
    lines.append("")

    lines.append("## Aktive Timer (`systemctl list-timers --all`)")
    lines.append("")
    lines.append("```")
    lines.append(timers if timers else "(keine Ausgabe)")
    lines.append("```")
    lines.append("")

    lines.append("## Laufende Services (Auszug)")
    lines.append("")
    lines.append("```")
    lines.append(services if services else "(keine Ausgabe)")
    lines.append("```")
    lines.append("")

    lines.append("## Unit-Status (service + timer)")
    lines.append("")
    lines.append("```")
    lines.append(unit_status_str if unit_status_str else "(keine Ausgabe)")
    lines.append("```")
    lines.append("")

    lines.append("## systemd-Units mit Autoload-Verdacht")
    lines.append("")
    if not units_with_models:
        lines.append("Keine systemd-Unit mit Modell-Verweisen gefunden.")
    else:
        for u in units_with_models:
            lines.append(f"### `{u['filename']}`")
            lines.append(f"- Pfad: `{u['path']}`")
            lines.append(f"- Typ: {u['unit_type']}")
            if u["triggers"]:
                lines.append(f"- Triggert: `{u['triggers']}`")
            if u["exec_start"]:
                lines.append("- ExecStart:")
                for e in u["exec_start"]:
                    lines.append(f"  - `{e}`")
            if u["working_dir"]:
                lines.append(f"- WorkingDirectory: `{u['working_dir']}`")
            if u["environment"]:
                lines.append("- Environment:")
                for e in u["environment"]:
                    lines.append(f"  - `{e}`")
            if u["model_hits"]:
                lines.append("- Modell-Treffer:")
                for name, hit in u["model_hits"]:
                    lines.append(f"  - `{name}`: `{hit}`")
            if u["ollama_hits"]:
                lines.append("- Ollama-Aufruf:")
                for kind, hit in u["ollama_hits"]:
                    lines.append(f"  - `{kind}`: `{hit}`")
            lines.append("")

    lines.append("## Code-Dateien mit Modell-Verweisen")
    lines.append("")
    for name in sorted(MODEL_PATTERNS.keys()):
        hits = code_hits.get(name, [])
        lines.append(f"### `{name}` ({len(hits)} Treffer)")
        if not hits:
            lines.append("Keine Treffer.")
        else:
            by_file = defaultdict(list)
            for path, lineno, line in hits:
                by_file[path].append((lineno, line))
            for path in sorted(by_file.keys()):
                lines.append(f"- `{path}`")
                for lineno, line in by_file[path][:5]:
                    lines.append(f"  - Zeile {lineno}: `{line[:120]}`")
                if len(by_file[path]) > 5:
                    lines.append(f"  - ... und {len(by_file[path]) - 5} weitere Zeilen")
        lines.append("")

    lines.append("## In von Units referenzierten Dateien")
    lines.append("")
    lines.append("Hier werden ExecStart-Scripts und EnvironmentFiles der Units gescannt.")
    lines.append("")
    for name in sorted(MODEL_PATTERNS.keys()):
        hits = ref_hits.get(name, [])
        lines.append(f"### `{name}` ({len(hits)} Treffer)")
        if not hits:
            lines.append("Keine Treffer.")
        else:
            by_file = defaultdict(list)
            for path, lineno, line in hits:
                by_file[path].append((lineno, line))
            for path in sorted(by_file.keys()):
                lines.append(f"- `{path}`")
                for lineno, line in by_file[path][:5]:
                    lines.append(f"  - Zeile {lineno}: `{line[:120]}`")
                if len(by_file[path]) > 5:
                    lines.append(f"  - ... und {len(by_file[path]) - 5} weitere Zeilen")
        lines.append("")

    lines.append("## Anmerkungen / naechste Schritte")
    lines.append("")
    lines.append("- Die Liste zeigt *Verdachtstraeger*, nicht zwingend aktive Autoloader.")
    lines.append("- Um einen sauberen A/B-Test zu machen, muessen die hier gefundenen aktiven Services/Timer vorher gestoppt werden.")
    lines.append("- Besonders kritisch: Timer und Dienste, die regelmaessig im Hintergrund laufen.")
    lines.append("- Environment-Variablen in .env-Dateien koennen Modelle steuern, ohne dass der Modellname im Code steht.")
    lines.append("")

    return "\n".join(lines)


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    print("Scanne systemd-Units ...")
    units = scan_systemd()
    print("Scanne Code-Dateien ...")
    code_hits = scan_code()
    print("Scanne von Units referenzierte Dateien ...")
    ref_hits = scan_referenced_files(units)
    print("Frage laufenden Zustand ab ...")
    ollama_ps = current_ollama_ps()
    timers = current_timers()
    services = active_services()
    unit_status_str = unit_status()
    print("Analysiere Cron-Jobs ...")
    cron_entries = check_cron()
    print("Bewerte Risiken ...")
    states = parse_unit_status(unit_status_str)
    risks = assess_risks(units, states, cron_entries, code_hits, ref_hits)

    report = build_report(units, code_hits, ref_hits, ollama_ps, timers, services,
                          unit_status_str, risks, cron_entries)
    out_path = REPORT_DIR / f"ollama_autoload_audit_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"Bericht geschrieben: {out_path}")


if __name__ == "__main__":
    main()
