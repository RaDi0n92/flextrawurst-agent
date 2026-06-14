"""
Stellt den dak+gord-Gesprächsverlauf aus dem letzten guten Checkpoint wieder her.
Fügt den letzten guten (36-Nachrichten-)Blob als neuen Checkpoint ein.
Vor Ausführung: dak-gord-web.service stoppen.
"""
from __future__ import annotations
import os
import sys
import uuid
import json
import datetime

sys.path.insert(0, "/root/werkraum")

import psycopg2
import msgpack

DB_URI = "postgresql://dak:!Windowsxp02336827359645852@localhost:5432/flextrawurst"
THREAD_ID = "hauptfaden"
CHANNEL = "nachrichten"
TARGET_VERSION = "00000000000000000000000000000707.0.93550"  # 36-Nachrichten-Blob


def lade_blob(cur) -> bytes:
    cur.execute(
        "SELECT blob FROM checkpoint_blobs WHERE thread_id=%s AND channel=%s AND version LIKE %s",
        (THREAD_ID, CHANNEL, TARGET_VERSION[:40] + "%"),
    )
    row = cur.fetchone()
    if not row:
        raise RuntimeError(f"Blob für Version {TARGET_VERSION[:20]}... nicht gefunden")
    return bytes(row[0])


def aktuelle_max_version(cur) -> str:
    cur.execute(
        "SELECT version FROM checkpoint_blobs WHERE thread_id=%s AND channel=%s ORDER BY version DESC LIMIT 1",
        (THREAD_ID, CHANNEL),
    )
    row = cur.fetchone()
    return row[0] if row else "00000000000000000000000000000000.0.0"


def naechste_version(current: str) -> str:
    parts = current.split(".")
    num = int(parts[0]) + 1
    return f"{num:064d}.0.99999999999999999"


def aktuelle_latest_checkpoint(cur):
    cur.execute(
        "SELECT checkpoint_id, checkpoint FROM checkpoints WHERE thread_id=%s ORDER BY checkpoint_id DESC LIMIT 1",
        (THREAD_ID,),
    )
    return cur.fetchone()


def main():
    conn = psycopg2.connect(DB_URI)
    conn.autocommit = False
    cur = conn.cursor()

    print("Lade den letzten guten Blob (36 Nachrichten)...")
    blob_bytes = lade_blob(cur)
    daten = msgpack.unpackb(blob_bytes, raw=False)
    print(f"  → {len(daten)} Nachrichten geladen")
    print(f"  → Letzte Nachricht: {str(daten[-1])[:80]}")

    new_version = naechste_version(aktuelle_max_version(cur))
    print(f"\nFüge neuen Blob ein mit Version: {new_version[:30]}...")
    cur.execute(
        "INSERT INTO checkpoint_blobs (thread_id, checkpoint_ns, channel, version, type, blob) VALUES (%s, %s, %s, %s, %s, %s)",
        (THREAD_ID, "", CHANNEL, new_version, "msgpack", psycopg2.Binary(blob_bytes)),
    )

    latest = aktuelle_latest_checkpoint(cur)
    if not latest:
        print("FEHLER: Kein aktueller Checkpoint gefunden")
        conn.rollback()
        return

    latest_id, latest_checkpoint = latest
    print(f"\nAktueller Checkpoint: {latest_id}")

    new_checkpoint_id = str(uuid.uuid7()) if hasattr(uuid, 'uuid7') else str(uuid.uuid4())

    # Neues Checkpoint-JSON basierend auf dem aktuellen, aber mit neuer Blob-Version
    checkpoint_json = dict(latest_checkpoint)
    checkpoint_json["id"] = new_checkpoint_id
    checkpoint_json["ts"] = datetime.datetime.utcnow().isoformat() + "+00:00"
    if "channel_versions" not in checkpoint_json:
        checkpoint_json["channel_versions"] = {}
    checkpoint_json["channel_versions"][CHANNEL] = new_version
    if "updated_channels" not in checkpoint_json:
        checkpoint_json["updated_channels"] = []
    checkpoint_json["updated_channels"] = [CHANNEL]
    # channel_values leer lassen (Blob wird separat gelesen)
    checkpoint_json["channel_values"] = {}

    print(f"Füge neuen Checkpoint ein: {new_checkpoint_id}")
    cur.execute(
        "INSERT INTO checkpoints (thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id, type, checkpoint, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (THREAD_ID, "", new_checkpoint_id, latest_id, "msgpack", json.dumps(checkpoint_json), "{}"),
    )

    conn.commit()
    print("\n✓ Wiederherstellung abgeschlossen.")
    print(f"  Neuer Checkpoint: {new_checkpoint_id}")
    print(f"  Blob-Version: {new_version[:30]}...")
    print("\nJetzt: systemctl start dak-gord-web")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
