#!/usr/bin/env python3
"""
llm_warteschlange_status.py — reiner Read-Only-Snapshot der aktuellen
LLM-Warteschlange (llm_scheduler.py, Tabelle llm_warteschlange), fuer die
Live-Aktivitaets-Anzeige in flarumstyler (Daniel: "wenn sie in llma warten
will ich es wissen"). Node hat keine eigene Postgres-Anbindung (bestehendes
Muster, siehe wesen_dienst_liste.py).

Zeigt nur Zeilen, die JETZT tatsaechlich relevant sind: haelt gerade einen
Slot (slot_bis > jetzt) oder wartet gerade (slot_bis IS NULL). Bekannter
Seiteneffekt von llm_scheduler.py: Zeilen mit abgelaufenem slot_bis und
altem (nicht 'pid='-praefigiertem) rufer-Format werden von
_cleanup_stale_waiters() nie automatisch entfernt (Zombie-Reste, z.B. ids
1169/1604 seit heute morgen) -- dieses Skript filtert sie bewusst aus der
Live-Anzeige heraus, LOESCHT aber nichts (Grundgesetz 4, und es ist ohnehin
nur ein Lese-Skript).
"""

import json
import re
import sys

sys.path.insert(0, "/root/werkraum")
import psycopg2
import psycopg2.extras

_DB_URI_RE = re.compile(r"^FLEXTRAWURST_DB_URI=(.+)$", re.MULTILINE)


def _db_uri() -> str:
    import os
    env = os.environ.get("FLEXTRAWURST_DB_URI")
    if env:
        return env
    text = open("/root/werkraum/.agent/flextrawurst-db.env", encoding="utf-8").read()
    m = _DB_URI_RE.search(text)
    if not m:
        raise RuntimeError("FLEXTRAWURST_DB_URI nicht gefunden")
    return m.group(1).strip().strip('"').strip("'")


def main():
    conn = psycopg2.connect(_db_uri(), cursor_factory=psycopg2.extras.RealDictCursor, connect_timeout=5)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, server, prioritaet, rufer, angefragt_um, slot_bis,
                       (slot_bis IS NOT NULL AND slot_bis > NOW()) AS aktiv
                FROM llm_warteschlange
                WHERE slot_bis IS NULL OR slot_bis > NOW()
                ORDER BY angefragt_um ASC
                """
            )
            zeilen = cur.fetchall()
    finally:
        conn.close()

    ausgabe = [
        {
            "id": z["id"], "server": z["server"], "prioritaet": z["prioritaet"],
            "rufer": z["rufer"], "aktiv": bool(z["aktiv"]),
            "angefragt_um": z["angefragt_um"].isoformat() if z["angefragt_um"] else None,
            "slot_bis": z["slot_bis"].isoformat() if z["slot_bis"] else None,
        }
        for z in zeilen
    ]
    print(json.dumps(ausgabe, ensure_ascii=False))


if __name__ == "__main__":
    main()
