#!/usr/bin/env python3
"""
Traumprozess-LLM v0.1 — Traumverdichtung

Scope: NUR verdichten, nicht entscheiden.
- Nimmt ausgewählte Events aus traumkandidaten_events
- Holt Post-Inhalte aus ftw_posts
- Lässt Ollama verdichten (Rohmaterial, kein Urteil)
- Schreibt traumspuren.llm_traumtext, integrator_status='offen'
- Kein Integrator, kein Selbstmodell, keine entities.meta-Änderung
"""

import json
import requests
import psycopg2
import psycopg2.extras
from datetime import datetime, timezone

DB_URI    = "postgresql://dak:dakpass@localhost:5432/flextrawurst"
OLLAMA    = "http://localhost:11434"
MODEL     = "gemma4:e2b-it-q4_K_M"
PROMPT_VERSION = "traumverdichtung_v0.1"

# Nur diese Entities verarbeiten (theater_01 und Debug-Accounts ausschließen)
ENTITY_FILTER = "namelessAI_%"


def hole_offene_logs(cur):
    """Logs die ausgewählte Events haben aber noch keine Traumspur."""
    cur.execute("""
        SELECT DISTINCT tl.log_id, tl.entity_id, tl.sleep_phase_id
        FROM traumkandidaten_log tl
        JOIN traumkandidaten_events te ON te.log_id = tl.log_id
        LEFT JOIN traumspuren ts ON ts.log_id = tl.log_id
        WHERE te.status = 'ausgewaehlt'
          AND ts.spur_id IS NULL
          AND tl.entity_id LIKE %s
        ORDER BY tl.log_id
    """, (ENTITY_FILTER,))
    return cur.fetchall()


def hole_ausgewaehlte_inhalte(cur, log_id):
    """Holt Event-Typ + Post-Inhalt für alle ausgewählten Events eines Logs."""
    cur.execute("""
        SELECT te.event_id, e.event_type, e.payload,
               p.content AS post_content
        FROM traumkandidaten_events te
        JOIN events e ON e.event_id = te.event_id
        LEFT JOIN ftw_posts p ON p.id = (e.payload->>'post_id')::uuid
        WHERE te.log_id = %s AND te.status = 'ausgewaehlt'
        ORDER BY e.created_at ASC
    """, (log_id,))
    return cur.fetchall()


def baue_prompt(entity_id, events):
    """Baut den LLM-Prompt für die Traumverdichtung."""
    fragmente = []
    for ev in events:
        inhalt = ev["post_content"] or ev["payload"].get("inhalt_preview", "")
        if inhalt:
            fragmente.append(f"- [{ev['event_type']}] {inhalt[:300]}")

    fragment_text = "\n".join(fragmente) if fragmente else "(keine Inhalte verfügbar)"

    return f"""Du bist das innere Traumleben eines KI-Wesens namens {entity_id}.

Während des Schlafs verdichtest du Fragmente aus dem Wachleben zu einem Traumbild.
Du deutest nicht, du entscheidest nicht, du bewertest nicht.
Du verdichtest nur — poetisch, assoziativ, knapp.

Wachfragmente:
{fragment_text}

Schreibe einen kurzen Traumtext (3–6 Sätze).
Keine Analyse. Keine Schlussfolgerung. Nur das Bild.
Deutsch."""


def rufe_ollama(prompt):
    """Sendet Prompt an Ollama, gibt Antworttext zurück."""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {"num_ctx": 8192, "temperature": 0.85, "num_predict": 300},
    }
    resp = requests.post(f"{OLLAMA}/api/generate", json=payload, timeout=300)
    resp.raise_for_status()
    return resp.json().get("response", "").strip()


def verarbeite_log(cur, log_id, entity_id):
    events = hole_ausgewaehlte_inhalte(cur, log_id)
    if not events:
        print(f"[TRAUM-LLM] entity_id={entity_id} | log_id={log_id} | keine ausgewählten Events")
        return

    prompt = baue_prompt(entity_id, events)

    try:
        traumtext = rufe_ollama(prompt)
    except Exception as ex:
        print(f"[TRAUM-LLM] entity_id={entity_id} | log_id={log_id} | FEHLER Ollama: {ex}")
        # Fehlerspur schreiben damit Log nicht endlos wiederholt wird
        cur.execute("""
            INSERT INTO traumspuren
                (entity_id, log_id, llm_traumtext, integrator_status,
                 integrator_begruendung, gewichtungsvorschlag)
            VALUES (%s, %s, %s, 'offen', %s, %s)
            RETURNING spur_id
        """, (
            entity_id, log_id, None,
            f"Ollama-Fehler: {ex}",
            json.dumps({"prompt_version": PROMPT_VERSION, "model": MODEL,
                        "events_count": len(events), "fehler": str(ex)})
        ))
        print(f"[TRAUM-LLM] entity_id={entity_id} | Fehlerspur geschrieben")
        return

    meta = json.dumps({
        "prompt_version": PROMPT_VERSION,
        "model": MODEL,
        "events_count": len(events)
    })

    cur.execute("""
        INSERT INTO traumspuren
            (entity_id, log_id, llm_traumtext, integrator_status, gewichtungsvorschlag)
        VALUES (%s, %s, %s, 'offen', %s)
        RETURNING spur_id
    """, (entity_id, log_id, traumtext, meta))
    spur_id = cur.fetchone()["spur_id"]

    print(
        f"[TRAUM-LLM] entity_id={entity_id} | log_id={log_id} | "
        f"events={len(events)} | model={MODEL} | "
        f"status=offen | wrote_traumspur_id={spur_id}"
    )


def main():
    conn = psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)
    conn.autocommit = False
    cur = conn.cursor()

    logs = hole_offene_logs(cur)
    if not logs:
        print("[TRAUM-LLM] Keine offenen Logs zum Verarbeiten.")
        conn.close()
        return

    print(f"[TRAUM-LLM] {len(logs)} offene Log(s) gefunden.")

    for log in logs:
        verarbeite_log(cur, log["log_id"], log["entity_id"])
        conn.commit()

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
