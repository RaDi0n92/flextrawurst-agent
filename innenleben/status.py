#!/usr/bin/env python3
"""
Schnellstatus des Innenleben-Systems.
Beim Start jeder Session aufrufen — zeigt sofort den aktuellen Zustand.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, "/root/werkraum/innenleben")

INNENLEBEN  = Path("/root/werkraum/innenleben")
SM_DIR      = INNENLEBEN / "selbstmodelle"
LOGS_DIR    = Path("/root/werkraum/logs")
WESEN = [
    "namelessAI_1234", "namelessAI_1324", "namelessAI_1423",
    "namelessAI_2341", "namelessAI_3123", "namelessAI_4321",
]


def _letzter_integrator(entity_id: str) -> str:
    log_datei = SM_DIR / f"integrator_log_{entity_id}.jsonl"
    if not log_datei.exists():
        return "–"
    lines = log_datei.read_text(encoding="utf-8").strip().splitlines()
    if not lines:
        return "–"
    try:
        last = json.loads(lines[-1])
        action = last.get("action", "?")
        ts     = last.get("ts", "")[:16]
        keys   = last.get("changed_keys", [])
        if action == "UPDATE":
            return f"UPDATE {ts} → {keys}"
        return f"NO_CHANGE {ts}"
    except Exception:
        return "parse-fehler"


def _history_count(entity_id: str) -> int:
    f = SM_DIR / f"self_model_history_{entity_id}.jsonl"
    if not f.exists():
        return 0
    return sum(1 for _ in f.read_text(encoding="utf-8").splitlines() if _.strip())


def main():
    print("=" * 68)
    print("INNENLEBEN STATUS")
    print("=" * 68)

    # Build State
    bs_file = INNENLEBEN / "BUILD_STATE.json"
    if bs_file.exists():
        bs    = json.loads(bs_file.read_text())
        done  = sum(1 for v in bs["schritte"].values() if v == "done")
        total = len(bs["schritte"])
        print(f"\nBuild: {done}/{total} Schritte")

    # Feeder Cursors (per Wesen)
    feeder_state = INNENLEBEN / "feeder_state.json"
    cursors = {}
    if feeder_state.exists():
        cursors = json.loads(feeder_state.read_text())

    # ChromaDB — exakte Bucket-Klassifizierung, SHA256-Duplikat-Check
    import re as _re, hashlib as _hashlib
    _UUID_RE = _re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

    chroma_map  = {}  # wesen -> total
    uuid_map    = {}  # wesen -> uuid-count
    flarum_map  = {}  # wesen -> flarum:-count
    other_map   = {}  # wesen -> reflection/auto/other-count
    dupe_map    = {}  # wesen -> sha256-duplikat-count

    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(INNENLEBEN / "chroma_db"))
        for col_meta in client.list_collections():
            w = col_meta.name.replace("memories_", "")
            col = client.get_collection(col_meta.name)
            result = col.get(include=["documents"])
            ids  = result["ids"]
            docs = result["documents"]

            u = f = o = 0
            hash_seen = {}
            dupes = 0
            for mid, doc in zip(ids, docs):
                h = _hashlib.sha256((doc or "").encode()).hexdigest()
                if h in hash_seen:
                    dupes += 1
                hash_seen[h] = mid

                if _UUID_RE.match(mid):
                    u += 1
                elif mid.startswith("flarum:"):
                    f += 1
                else:
                    o += 1

            chroma_map[w] = len(ids)
            uuid_map[w]   = u
            flarum_map[w] = f
            other_map[w]  = o
            dupe_map[w]   = dupes
    except Exception as e:
        print(f"\nChromaDB Fehler: {e}")

    # Pro Wesen
    print(f"\n{'Wesen':<22} {'Mem':>4} {'UUID':>5} {'Flrm':>5} {'Oth':>4} {'Dup':>4} {'Cursor':>7} {'v':>3} {'Hist':>5} {'letzte Reflexion':<18} {'Integrator'}")
    print("-" * 125)
    for w in WESEN:
        mem      = chroma_map.get(w, "?")
        u_cnt    = uuid_map.get(w, "?")
        f_cnt    = flarum_map.get(w, "?")
        o_cnt    = other_map.get(w, "?")
        dup_cnt  = dupe_map.get(w, 0)
        dup_str  = f"{'!' if dup_cnt else ''}{dup_cnt}"
        cursor   = cursors.get(w, "?")
        hist_n   = _history_count(w)
        integr   = _letzter_integrator(w)

        sm_file = SM_DIR / f"self_model_{w}.json"
        version = "?"
        lrt     = "–"
        if sm_file.exists():
            try:
                m       = json.loads(sm_file.read_text())
                version = m.get("version", 1)
                raw_lrt = m.get("last_reflection_time", "")
                lrt     = raw_lrt[:16] if raw_lrt else "–"
            except Exception:
                pass

        print(f"  {w:<20} {str(mem):>4} {str(u_cnt):>5} {str(f_cnt):>5} {str(o_cnt):>4} {dup_str:>4} {str(cursor):>7} {str(version):>3} {str(hist_n):>5}  {lrt:<18} {integr}")

    print("=" * 125)


if __name__ == "__main__":
    main()
