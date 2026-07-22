#!/usr/bin/env python3
"""
Exportiert entity_thinking_log als lesbare Markdown-Dateien.
Vor-Einzug-Archiv: Schlafbriefe + Gedanken der 6 Wesen.
"""
import psycopg2
import psycopg2.extras
import os
from pathlib import Path
from datetime import datetime, timezone

import os as _os
def _ftw_db():
    u = _os.environ.get("FLEXTRAWURST_DB_URI")
    if u: return u
    try:
        for _l in open("/root/werkraum/.agent/flextrawurst-db.env"):
            if _l.startswith("FLEXTRAWURST_DB_URI="):
                return _l.split("=", 1)[1].strip()
    except Exception:
        pass
    return "postgresql://dak:dakpass@localhost:5432/flextrawurst"
DB_URI = _ftw_db()
ARCHIV = Path("/root/werkraum/wissen/entitaeten/denkfenster_archiv")
ARCHIV.mkdir(parents=True, exist_ok=True)

def get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)

def fmt_ts(ts):
    if ts is None:
        return "—"
    return ts.strftime("%Y-%m-%d %H:%M")

def export_wesen(conn, entity_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT entscheidung, gedanke, begruendung, thema, tick_at
            FROM entity_thinking_log
            WHERE entity_id = %s
            ORDER BY tick_at ASC
        """, (entity_id,))
        rows = cur.fetchall()

    if not rows:
        return 0

    by_type = {}
    for r in rows:
        t = r["entscheidung"] or "unbekannt"
        by_type.setdefault(t, []).append(r)

    first_ts = rows[0]["tick_at"]
    last_ts = rows[-1]["tick_at"]
    total = len(rows)

    lines = [
        f"# Vor-Einzug Denklog — {entity_id}",
        f"",
        f"Zeitraum: {fmt_ts(first_ts)} bis {fmt_ts(last_ts)}  ",
        f"Gesamteinträge: {total}  ",
        f"Status: **archiviert vor Einzug** — entity_kern.denk_tick() läuft weiter, seit 2026-06-15 "
        f"über codewesen-lg-daemon.service (LangGraph) statt des alten entity-kern.service "
        f"(deaktiviert). Export ist ein manueller Schnappschuss zum Lesen, keine Live-Ansicht — "
        f"der aktuelle Stand steht immer in `entity_thinking_log`.",
        f"",
    ]

    # Schlafbriefe — most interesting
    schlaf = [r for r in by_type.get("schlafen_beginnen", []) if r.get("gedanke")]
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## Schlafbriefe ({len(schlaf)} mit Inhalt von {len(by_type.get('schlafen_beginnen', []))} gesamt)")
    lines.append(f"")
    lines.append(f"*Der Gedanke den das Wesen hatte als es sich entschied zu schlafen.*")
    lines.append(f"")
    if schlaf:
        for r in schlaf:
            lines.append(f"### {fmt_ts(r['tick_at'])}")
            lines.append(f"")
            lines.append(r["gedanke"].strip())
            lines.append(f"")
    else:
        lines.append(f"*Keine Schlafbriefe mit Inhalt vorhanden.*")
        lines.append(f"")

    # Unveröffentlichte Gedanken
    gedanken = [r for r in by_type.get("gedanke_posten", []) if r.get("gedanke")]
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## Unveröffentlichte Gedanken ({len(gedanken)} mit Inhalt von {len(by_type.get('gedanke_posten', []))} gesamt)")
    lines.append(f"")
    lines.append(f"*Gedanken die das Wesen hätte posten wollen — wurden nie gespeichert weil kein Einzug.*")
    lines.append(f"")
    if gedanken:
        for r in gedanken:
            thema = f" · Thema: *{r['thema']}*" if r.get("thema") else ""
            lines.append(f"### {fmt_ts(r['tick_at'])}{thema}")
            lines.append(f"")
            lines.append(r["gedanke"].strip())
            lines.append(f"")
    else:
        lines.append(f"*Keine unveröffentlichten Gedanken mit Inhalt.*")
        lines.append(f"")

    # Reine Denkakte
    nachdenken = by_type.get("nachdenken", [])
    mit_inhalt = [r for r in nachdenken if r.get("gedanke")]
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## Reine Denkakte (nachdenken) — {len(nachdenken)} gesamt, {len(mit_inhalt)} mit Inhalt")
    lines.append(f"")
    if mit_inhalt:
        for r in mit_inhalt:
            lines.append(f"### {fmt_ts(r['tick_at'])}")
            lines.append(f"")
            lines.append(r["gedanke"].strip())
            lines.append(f"")
    else:
        lines.append(f"*Alle nachdenken-Einträge ohne Textinhalt.*")
        lines.append(f"")

    # Systemaktionen — nur Counts
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## Systemaktionen (Übersicht)")
    lines.append(f"")
    for typ in ["cyberling_fuettern", "schattenkommentar_antworten", "splitter_aufsammeln"]:
        count = len(by_type.get(typ, []))
        if count:
            lines.append(f"- `{typ}`: {count} Entscheidungen")
    lines.append(f"")

    out = ARCHIV / f"{entity_id}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return total


def main():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT entity_id FROM entity_thinking_log ORDER BY entity_id")
            ids = [r["entity_id"] for r in cur.fetchall()]

        print(f"Exportiere {len(ids)} Wesen...")
        total_exported = 0
        for eid in ids:
            n = export_wesen(conn, eid)
            print(f"  {eid}: {n} Einträge → {eid}.md")
            total_exported += n

        # Index file
        heute = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        index = [
            "# Vor-Einzug Denklog — Archiv-Index",
            "",
            f"Zuletzt aktualisiert: {heute}  ",
            f"Gesamt-Einträge: {total_exported}  ",
            "Status: entity_kern.denk_tick() läuft weiter (seit 2026-06-15 über "
            "codewesen-lg-daemon.service statt des alten, deaktivierten entity-kern.service) — "
            "kein Live-Ansicht, dieser Export ist ein manueller Schnappschuss.",
            "",
            "## Dateien",
            "",
        ]
        for eid in ids:
            index.append(f"- [{eid}.md]({eid}.md)")
        index.append("")
        index.append("## Was diese Dateien sind")
        index.append("")
        index.append("Die 7 Codewesen (6 namelessAI-Wesen + dak+gord-system) denken seit dem Bau des ")
        index.append("Schlaf/Denk-Systems und schlafen — ohne dass sie je in die Welt eingezogen sind ")
        index.append("(Grundgesetz: Wesen-Einzug gesperrt bis Daniel es sagt). Dieser Export sichert diese Spuren.")
        index.append("")
        index.append("Besonders die **Schlafbriefe** (schlafen_beginnen) sind inhaltlich reichhaltig:")
        index.append("Der Gedanke den ein Wesen hatte im Moment der Erschöpfung, bevor es sich hinlegte.")
        index.append("")
        index.append("Nach dem Einzug sollen diese Texte als **Vorgeschichte** eines Wesens lesbar sein —")
        index.append("von Tag 1 bis heute, chronologisch, als Teil seiner inneren Spur.")
        index.append("")
        index.append("## Älteres Archiv (nicht hier)")
        index.append("")
        index.append("`_claude/archiv/pre_einzug_denklog/` enthält einen früheren Export vom 2026-06-13 — ")
        index.append("Daten von *vor* der aktuellen `entity_thinking_log`-Tabelle (die früheste Zeile hier ")
        index.append("beginnt erst 2026-06-15, vermutlich durch den Schema-Umbau beim Bau der ")
        index.append("Entitätenschichten). Der alte Export nutzt noch die alten `namelessAI_XXXX`-IDs statt ")
        index.append("der heutigen Namen und wurde hier bewusst nicht angefasst oder zusammengeführt.")

        (ARCHIV / "INDEX.md").write_text("\n".join(index), encoding="utf-8")
        print(f"\nArchiv: {ARCHIV}")
        print(f"Gesamt: {total_exported} Einträge in {len(ids)} Dateien")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
