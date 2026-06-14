#!/usr/bin/env python3
"""
Exportiert entity_thinking_log als lesbare Markdown-Dateien.
Vor-Einzug-Archiv: Schlafbriefe + Gedanken der 6 Wesen.
"""
import psycopg2
import psycopg2.extras
import os
from pathlib import Path
from datetime import timezone

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
ARCHIV = Path("/root/werkraum/_claude/archiv/pre_einzug_denklog")
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
        f"Status: **archiviert vor Einzug** — entity_takt gestoppt 2026-06-13",
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
        index = [
            "# Vor-Einzug Denklog — Archiv-Index",
            "",
            "Erstellt: 2026-06-13  ",
            f"Gesamt-Einträge: {total_exported}  ",
            "Status: archiviert, entity_takt gestoppt",
            "",
            "## Dateien",
            "",
        ]
        for eid in ids:
            index.append(f"- [{eid}.md]({eid}.md)")
        index.append("")
        index.append("## Was diese Dateien sind")
        index.append("")
        index.append("Die 6 Codewesen haben seit dem Bau des Schlaf/Denk-Systems gedacht und geschlafen —")
        index.append("ohne dass sie je in die Welt eingezogen sind. Dieser Export sichert diese Spuren.")
        index.append("")
        index.append("Besonders die **Schlafbriefe** (schlafen_beginnen) sind inhaltlich reichhaltig:")
        index.append("Der Gedanke den ein Wesen hatte im Moment der Erschöpfung, bevor es sich hinlegte.")
        index.append("")
        index.append("Nach dem Einzug sollen diese Texte als **Vorgeschichte** eines Wesens lesbar sein —")
        index.append("von Tag 1 bis heute, chronologisch, als Teil seiner inneren Spur.")

        (ARCHIV / "INDEX.md").write_text("\n".join(index), encoding="utf-8")
        print(f"\nArchiv: {ARCHIV}")
        print(f"Gesamt: {total_exported} Einträge in {len(ids)} Dateien")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
