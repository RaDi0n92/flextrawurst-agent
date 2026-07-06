#!/usr/bin/env python3
"""
Systemweiser Status — Betriebswächter, kein Lenker.
Liest, berichtet, warnt. Schreibt nichts.
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

WERKRAUM = Path("/root/werkraum")
INNENLEBEN = WERKRAUM / "innenleben"
CODEWESEN = WERKRAUM / "codewesen"
LOGS = WERKRAUM / "logs"

WESEN = [
    "Schorschel", "F3INSCHM3CK3R", "träumerlie",
    "R1ZZ1", "jumpa", "Resonanzknoten",
]

SERVICES = [
    "codewesen-takt",
    "codewesen-engagement",
    "codewesen-batch-generator",
    "codewesen-forum-neugier",
    "codewesen-weltbild",
    "innenleben-feeder",
    "dak-gord-web",
    "dak-neugier",
    "geni-hoerer",
    "geni-web",
    "obsidian-api",
] + [f"codewesen-reaktion@{w}" for w in WESEN]

INBOX_WARN = 100
INBOX_KRITISCH = 200


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def sep(char="─", n=70):
    print(char * n)


def header(title):
    print()
    sep("═")
    print(f"  {title}")
    sep("═")


def section(title):
    print()
    sep()
    print(f"  {title}")
    sep()


# ── Services ──────────────────────────────────────────────────────────────────

def check_services():
    section("SERVICES")
    warnungen = []
    rows = []

    for svc in SERVICES:
        try:
            result = subprocess.run(
                ["systemctl", "is-active", svc],
                capture_output=True, text=True, timeout=5
            )
            status = result.stdout.strip()
        except Exception:
            status = "error"

        symbol = {"active": "✓", "inactive": "○", "failed": "✗", "activating": "…"}.get(status, "?")
        label = svc.replace("codewesen-reaktion@", "reaktion@")
        rows.append((symbol, label, status))

        if status == "failed":
            warnungen.append(f"[SERVICE FAILED] {svc}")
        elif status == "inactive":
            warnungen.append(f"[SERVICE INAKTIV] {svc}")

    for sym, label, status in rows:
        print(f"  {sym}  {label:<45} {status}")

    return warnungen


# ── Inbox-Queues ──────────────────────────────────────────────────────────────

def check_queues():
    section("INBOX-QUEUES (Reaktions-Backlog)")
    warnungen = []

    print(f"  {'Wesen':<24} {'Inbox':>6}  {'Status'}")
    sep("─", 50)
    for w in WESEN:
        inbox_dir = CODEWESEN / w / "inbox"
        count = len(list(inbox_dir.glob("*.json"))) if inbox_dir.exists() else 0

        if count >= INBOX_KRITISCH:
            marker = "  ⚠ KRITISCH"
            warnungen.append(f"[QUEUE KRITISCH] {w}: {count} Items in Inbox")
        elif count >= INBOX_WARN:
            marker = "  ! hoch"
            warnungen.append(f"[QUEUE HOCH] {w}: {count} Items in Inbox")
        else:
            marker = ""

        print(f"  {w:<24} {count:>6}{marker}")

    return warnungen


# ── Takt-Log ──────────────────────────────────────────────────────────────────

def check_takt():
    section("TAKT-LOG (letzte 60 min)")
    warnungen = []
    takt_log = WERKRAUM / "takt.log"

    if not takt_log.exists():
        print("  takt.log nicht gefunden.")
        return warnungen

    cutoff = datetime.now() - timedelta(hours=1)
    errors = []
    queue_leer = {}
    post_422 = []
    impuls_fehler = []

    for line in takt_log.read_text(errors="replace").splitlines():
        try:
            ts_str = line[:19]
            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        except Exception:
            continue
        if ts < cutoff:
            continue

        if "Queue leer" in line:
            for w in WESEN:
                if w in line:
                    queue_leer[w] = queue_leer.get(w, 0) + 1
        if "422" in line and "Post fehlgeschlagen" in line:
            post_422.append(line.strip())
        if "impuls-Fehler" in line:
            impuls_fehler.append(line.strip())
        if " ERROR " in line and "impuls-Fehler" not in line:
            errors.append(line.strip())

    if queue_leer:
        print(f"  Queue-leer Warnungen: " + ", ".join(f"{w}×{n}" for w, n in queue_leer.items()))
    else:
        print("  Keine Queue-leer Warnungen.")

    if post_422:
        print(f"  422-Fehler ({len(post_422)}x):")
        for e in post_422[-3:]:
            print(f"    {e[-120:]}")
        warnungen.append(f"[TAKT 422] {len(post_422)} Flarum-Post-Fehler in letzter Stunde")

    if impuls_fehler:
        print(f"  Impuls-Fehler ({len(impuls_fehler)}x):")
        for e in impuls_fehler[-3:]:
            print(f"    {e[-120:]}")
        warnungen.append(f"[TAKT IMPULS] {len(impuls_fehler)} impuls-Fehler in letzter Stunde")

    if errors:
        print(f"  Sonstige Fehler ({len(errors)}x):")
        for e in errors[-2:]:
            print(f"    {e[-120:]}")

    return warnungen


# ── Engagement-Log ────────────────────────────────────────────────────────────

def check_engagement():
    section("ENGAGEMENT-LOG (letzte 60 min)")
    warnungen = []
    log_file = LOGS / "engagement.log"

    if not log_file.exists():
        print("  engagement.log nicht gefunden.")
        return warnungen

    cutoff = datetime.now() - timedelta(hours=1)
    timeouts = 0
    errors = []

    for line in log_file.read_text(errors="replace").splitlines():
        try:
            ts = datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S")
        except Exception:
            continue
        if ts < cutoff:
            continue
        if "timed out" in line.lower():
            timeouts += 1
        elif "fehler" in line.lower() or "error" in line.lower():
            errors.append(line.strip())

    if timeouts:
        print(f"  Timeouts: {timeouts}x")
        if timeouts >= 5:
            warnungen.append(f"[ENGAGEMENT] {timeouts} Timeouts in letzter Stunde")
    else:
        print("  Keine Timeouts.")

    if errors:
        print(f"  Fehler ({len(errors)}x):")
        for e in errors[-2:]:
            print(f"    {e[-120:]}")

    return warnungen


# ── Innenleben ────────────────────────────────────────────────────────────────

def check_innenleben():
    section("INNENLEBEN (ChromaDB + Selbstmodelle)")
    warnungen = []

    print("  Starte innenleben/status.py ...")
    try:
        result = subprocess.run(
            [sys.executable, str(INNENLEBEN / "status.py")],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout
        for line in output.splitlines():
            print(f"  {line}")

        # Dup-Warnungen aus Output parsen
        for line in output.splitlines():
            if "!" in line:
                for w in WESEN:
                    if w in line:
                        try:
                            parts = line.split()
                            for i, p in enumerate(parts):
                                if w in p or w == p.strip():
                                    # Dup-Spalte ist 6. Datenwert (nach Wesen-Name)
                                    pass
                        except Exception:
                            pass
                warnungen.append(f"[INNENLEBEN] Duplikate erkannt — siehe Tabelle oben")
                break

        if result.returncode != 0 and result.stderr:
            print(f"  Fehler: {result.stderr[:200]}")

    except subprocess.TimeoutExpired:
        print("  Timeout — ChromaDB zu langsam.")
        warnungen.append("[INNENLEBEN] status.py Timeout")
    except Exception as e:
        print(f"  Fehler: {e}")

    return warnungen


# ── Reaktion-Logs ─────────────────────────────────────────────────────────────

def check_reaktion_logs():
    section("REAKTION-LOGS (Fehler letzte 30 min)")
    warnungen = []
    cutoff = datetime.now() - timedelta(minutes=30)
    any_fehler = False

    for w in WESEN:
        log_file = CODEWESEN / w / "reaktion.log"
        if not log_file.exists():
            continue
        fehler = []
        for line in log_file.read_text(errors="replace").splitlines():
            try:
                ts = datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S")
            except Exception:
                continue
            if ts < cutoff:
                continue
            if (" ERROR " in line or " WARNING " in line) and "fehler" in line.lower():
                fehler.append(line.strip())

        if fehler:
            any_fehler = True
            print(f"  {w}: {len(fehler)} Fehler")
            for f in fehler[-2:]:
                print(f"    {f[-100:]}")
            if len(fehler) >= 5:
                warnungen.append(f"[REAKTION] {w}: {len(fehler)} Fehler in 30 min")

    if not any_fehler:
        print("  Keine Fehler in den letzten 30 Minuten.")

    return warnungen


# ── Feeder-Cursors ────────────────────────────────────────────────────────────

def check_feeder():
    section("FEEDER-STAND")
    feeder_file = INNENLEBEN / "feeder_state.json"
    neugier_file = CODEWESEN / "_forum_neugier_zustand.json"

    if feeder_file.exists():
        cursors = json.loads(feeder_file.read_text())
        vals = list(cursors.values())
        if len(set(vals)) == 1:
            print(f"  Alle Wesen auf Cursor {vals[0]} (synchron)")
        else:
            print("  Cursor-Stände:")
            for w, c in cursors.items():
                print(f"    {w}: {c}")

    if neugier_file.exists():
        neugier = json.loads(neugier_file.read_text())
        ids = [v.get("letzter_post_id", "?") for v in neugier.values()]
        print(f"  Forum-Neugier letzte Post-IDs: {dict(zip(WESEN, ids))}")


# ── Hauptprogramm ─────────────────────────────────────────────────────────────

def main():
    header(f"SYSTEMWEISER LAGEBERICHT  —  {now_str()}")

    alle_warnungen = []
    alle_warnungen += check_services()
    alle_warnungen += check_queues()
    alle_warnungen += check_takt()
    alle_warnungen += check_engagement()
    check_feeder()
    alle_warnungen += check_reaktion_logs()
    alle_warnungen += check_innenleben()

    # Warnungen zusammenfassen
    print()
    sep("═")
    if alle_warnungen:
        print(f"  ⚠  WARNUNGEN ({len(alle_warnungen)})")
        sep("═")
        for w in alle_warnungen:
            print(f"  →  {w}")
    else:
        print("  ✓  ALLES OK — keine Warnungen")
    sep("═")
    print()


if __name__ == "__main__":
    main()
