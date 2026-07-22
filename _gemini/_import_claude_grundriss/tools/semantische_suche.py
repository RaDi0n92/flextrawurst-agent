#!/usr/bin/env python3
"""
Semantische Suche ueber notizen/spiegel/ideen/karte -- lokal, keine Drittanbieter-Hooks.
Nutzt die bereits im System vorhandene ONNX-MiniLM-Embedding (wie innenleben/),
gespeichert in einer lokalen, dateibasierten Chroma-Collection unter _claude/semantik_index/.

Ersetzt NICHT das Schreib-Ritual (Notizen/Spiegel bleiben handgeschrieben) -- ist nur
ein zusaetzlicher Such-Layer darueber, weil grep/RESONANZFELD bei 150+ Dateien an seine
Grenzen kommt.

Usage:
  python3 semantische_suche.py index              # (Re-)Indiziert neue/geaenderte Dateien
  python3 semantische_suche.py suche "<begriff>" [-n 5]
"""
import sys
import hashlib
import json
from pathlib import Path

import chromadb

CLAUDE_ROOT = Path("/root/werkraum/_claude")
QUELL_ORDNER = ["notizen", "spiegel", "ideen", "karte"]
DB_PFAD = CLAUDE_ROOT / "semantik_index"
STATE_PFAD = DB_PFAD / "_indiziert.json"


def lade_state():
    try:
        return json.loads(STATE_PFAD.read_text())
    except Exception:
        return {}


def speichere_state(state):
    DB_PFAD.mkdir(parents=True, exist_ok=True)
    STATE_PFAD.write_text(json.dumps(state))


def chunks_aus_datei(pfad: Path):
    """Teilt eine Datei an '## '-Ueberschriften -- ein Chunk pro Abschnitt."""
    text = pfad.read_text(encoding="utf-8", errors="replace")
    zeilen = text.split("\n")
    chunks = []
    aktueller_titel = "(Anfang)"
    aktueller_inhalt = []

    def abschliessen():
        inhalt = "\n".join(aktueller_inhalt).strip()
        if inhalt:
            chunks.append((aktueller_titel, inhalt))

    for zeile in zeilen:
        if zeile.startswith("## "):
            abschliessen()
            aktueller_titel = zeile[3:].strip()
            aktueller_inhalt = []
        else:
            aktueller_inhalt.append(zeile)
    abschliessen()
    return chunks


def sammle_dateien():
    dateien = []
    for ordner in QUELL_ORDNER:
        basis = CLAUDE_ROOT / ordner
        if not basis.exists():
            continue
        dateien.extend(sorted(basis.rglob("*.md")))
    return dateien


def indizieren():
    client = chromadb.PersistentClient(path=str(DB_PFAD))
    coll = client.get_or_create_collection("claude_reflexionen")
    state = lade_state()
    dateien = sammle_dateien()
    neu = 0
    aktualisiert = 0

    for pfad in dateien:
        rel = str(pfad.relative_to(CLAUDE_ROOT))
        mtime = pfad.stat().st_mtime
        if state.get(rel) == mtime:
            continue  # unveraendert seit letztem Index

        try:
            coll.delete(where={"datei": rel})
        except Exception:
            pass

        chunks = chunks_aus_datei(pfad)
        if not chunks:
            state[rel] = mtime
            continue

        ids, docs, metas = [], [], []
        for i, (titel, inhalt) in enumerate(chunks):
            chunk_id = hashlib.md5(f"{rel}::{titel}::{i}".encode()).hexdigest()
            ids.append(chunk_id)
            docs.append(f"{titel}\n\n{inhalt}"[:4000])
            metas.append({"datei": rel, "abschnitt": titel})

        coll.upsert(ids=ids, documents=docs, metadatas=metas)
        if rel in state:
            aktualisiert += 1
        else:
            neu += 1
        state[rel] = mtime

    speichere_state(state)
    print(f"Index aktualisiert: {neu} neue Dateien, {aktualisiert} geaenderte Dateien, "
          f"{len(dateien)} insgesamt gescannt.")


def suchen(begriff: str, n: int = 5):
    client = chromadb.PersistentClient(path=str(DB_PFAD))
    coll = client.get_or_create_collection("claude_reflexionen")
    ergebnis = coll.query(query_texts=[begriff], n_results=n)
    if not ergebnis["ids"][0]:
        print("Keine Treffer -- ist der Index aktuell? ('python3 semantische_suche.py index')")
        return
    for i in range(len(ergebnis["ids"][0])):
        meta = ergebnis["metadatas"][0][i]
        dist = ergebnis["distances"][0][i]
        doc = ergebnis["documents"][0][i]
        schnipsel = doc[:220].replace("\n", " ")
        print(f"\n[{i+1}] {meta['datei']} — {meta['abschnitt']}  (Distanz {dist:.3f})")
        print(f"    {schnipsel}...")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: semantische_suche.py index | suche <begriff> [-n N]")
        sys.exit(1)

    kommando = sys.argv[1]
    if kommando == "index":
        indizieren()
    elif kommando == "suche":
        if len(sys.argv) < 3:
            print("Bitte einen Suchbegriff angeben.")
            sys.exit(1)
        begriff = sys.argv[2]
        n = 5
        if "-n" in sys.argv:
            n = int(sys.argv[sys.argv.index("-n") + 1])
        suchen(begriff, n)
    else:
        print(f"Unbekanntes Kommando: {kommando}")
        sys.exit(1)
