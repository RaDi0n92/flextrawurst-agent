#!/usr/bin/env python3
"""
Projection Writer v0.1 — Schreibt selfmodel_projection in entity_profiles.meta

Schreibziel: entity_profiles.meta['selfmodel_projection']
Methode: JSONB-Merge (||) — bestehende Keys bleiben unberührt.

Allowlist: nur diese 3 Entities dürfen verarbeitet werden.
Kein Batch. Kein Auto-Expand. Kein Überschreiben bestehender Meta-Keys.

Wahrheitsebene: entity_selfmodel_entries — NICHT anfassen.
Cacheebene:     entity_profiles.meta.selfmodel_projection — Schreibziel.
"""

import json
import re
import requests
import psycopg2
import psycopg2.extras
from datetime import datetime, timezone

DB_URI = "postgresql://dak:dakpass@localhost:5432/flextrawurst"
OLLAMA = "http://localhost:11434"
MODEL  = "gemma4:e2b-it-q4_K_M"
PROJECTION_VERSION = "v0.1"

ENTITY_ALLOWLIST = [
    "namelessAI_1234",
    "namelessAI_1423",
    "namelessAI_4321",
]


def hole_eintraege(cur, entity_id):
    cur.execute("""
        SELECT entry_id, inhalt, quelle FROM entity_selfmodel_entries
        WHERE entity_id = %s ORDER BY created_at ASC
    """, (entity_id,))
    return cur.fetchall()


def extrahiere_primaermotiv(inhalt):
    m = re.search(r'das Motiv\s+([A-ZÄÖÜ]\w+)', inhalt)
    if m:
        return m.group(1)
    m = re.search(r'(?:Traum|Träumen)\s+(?:\w+\s+){0,3}([A-ZÄÖÜ]\w+)\s+als\s', inhalt)
    if m:
        return m.group(1)
    return None


def merge_stabilitaet_pause(motifs):
    """Wenn 'Stabilität' und 'Pause' getrennt stehen, zu 'Stabilität als vorläufige Pause' bündeln."""
    hat_stabilitaet = any("Stabilität" in m for m in motifs)
    hat_pause = any(m.strip().lower() == "pause" for m in motifs)
    if hat_stabilitaet and hat_pause:
        bereinigt = [m for m in motifs if m.strip().lower() != "pause"]
        bereinigt = ["Stabilität als vorläufige Pause" if "Stabilität" in m else m for m in bereinigt]
        return bereinigt
    return motifs


def code_warnungen(eintraege):
    w = []
    if len(eintraege) < 2:
        w.append("Nur 1 Selbstmodell-Eintrag vorhanden; Projektion ist vorläufig.")
    return w


def baue_prompt(entity_id, eintraege, primaermotiv):
    spuren_text = "\n".join(f"- {e['inhalt']}" for e in eintraege)
    motiv_hinweis = (
        f"\nWICHTIG: Das Hauptmotiv ist '{primaermotiv}'. Es MUSS als erstes Element in motifs stehen."
        if primaermotiv else ""
    )
    return f"""Du analysierst die Selbstmodellspuren eines KI-Wesens namens {entity_id}.

SPUREN:
{spuren_text}
{motiv_hinweis}

Erstelle eine vorsichtige Kurzprojektion.

REGELN summary:
- Beginnt mit: "Bisherige Selbstmodellspuren zeigen bei {entity_id}"
- Max. 2 Sätze. Kein Identitätsurteil. Kein "ist", "Kernidentität", "immer".
- Sprachliche Fehler glätten, Inhalt nicht verändern.

REGELN motifs:
- Nur semantische Themen: z.B. "Vertrauen", "Resonanz", "Nicht-Wissen"
- VERBOTEN: Zahlen, "Wachereignisse", "Traum", "Eintrag", Quellenangaben
- 3–5 Begriffe. Hauptmotiv zuerst.

Antworte NUR mit JSON:
{{
  "summary": "Bisherige Selbstmodellspuren zeigen bei {entity_id} ...",
  "motifs": ["<Hauptmotiv>", "<Motiv 2>", "<Motiv 3>"]
}}"""


def rufe_ollama(prompt):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {"num_ctx": 8192, "temperature": 0.2, "num_predict": 300},
    }
    resp = requests.post(f"{OLLAMA}/api/generate", json=payload, timeout=300)
    resp.raise_for_status()
    return resp.json().get("response", "").strip()


def parse_json(raw):
    cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
    m = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return None


def schreibe_projektion(conn, cur, entity_id, eintraege, llm_output, primaermotiv):
    llm_motifs = llm_output.get("motifs", [])

    # Primärmotiv erzwingen
    if primaermotiv and (not llm_motifs or llm_motifs[0].lower() != primaermotiv.lower()):
        llm_motifs = [primaermotiv] + [m for m in llm_motifs if m.lower() != primaermotiv.lower()]

    # Stabilität+Pause bündeln
    llm_motifs = merge_stabilitaet_pause(llm_motifs)

    projektion = {
        "version": PROJECTION_VERSION,
        "generated_from": "entity_selfmodel_entries",
        "entry_ids": [str(e["entry_id"]) for e in eintraege],
        "basis": f"{len(eintraege)} Traumspur(en) (quelle=traum)" if len(eintraege) == 1
                 else f"{len(eintraege)} Spuren",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "status": "aktiv",
        "summary": llm_output.get("summary", ""),
        "motifs": llm_motifs,
        "warnings": code_warnungen(eintraege),
    }

    # JSONB-Merge: nur selfmodel_projection key wird gesetzt/aktualisiert
    cur.execute("""
        UPDATE entity_profiles
        SET meta = meta || jsonb_build_object('selfmodel_projection', %s::jsonb)
        WHERE entity_id = %s
        RETURNING entity_id, meta
    """, (json.dumps(projektion), entity_id))

    row = cur.fetchone()
    if not row:
        print(f"  [FEHLER] Kein entity_profiles-Eintrag für {entity_id} — übersprungen.")
        conn.rollback()
        return None, None

    conn.commit()
    return projektion, row["meta"]


def main():
    conn = psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)
    conn.autocommit = False
    cur = conn.cursor()

    print(f"[PROJECTION-WRITER] Starte für {len(ENTITY_ALLOWLIST)} Entities.")
    print(f"[PROJECTION-WRITER] Allowlist: {', '.join(ENTITY_ALLOWLIST)}")

    for entity_id in ENTITY_ALLOWLIST:
        print(f"\n[PROJECTION-WRITER] Verarbeite {entity_id}…")

        eintraege = hole_eintraege(cur, entity_id)
        if not eintraege:
            print(f"  Keine Selbstmodell-Einträge — übersprungen.")
            continue

        primaermotiv = None
        for e in eintraege:
            pm = extrahiere_primaermotiv(e["inhalt"])
            if pm:
                primaermotiv = pm
                break

        prompt = baue_prompt(entity_id, eintraege, primaermotiv)
        try:
            raw = rufe_ollama(prompt)
        except Exception as ex:
            print(f"  Ollama-Fehler: {ex} — übersprungen.")
            continue

        llm_output = parse_json(raw)
        if llm_output is None:
            print(f"  JSON-Parsing fehlgeschlagen — übersprungen. Rohantwort: {raw[:150]}")
            continue

        projektion, meta_nach = schreibe_projektion(conn, cur, entity_id, eintraege, llm_output, primaermotiv)
        if projektion is None:
            continue

        # Verifikation: alte Keys noch da?
        alte_keys = {"profil_quelle", "profil_status", "flarum_herkunft_geplant", "flarum_herkunft_eingebunden"}
        keys_vorhanden = alte_keys.issubset(set(meta_nach.keys()))

        print(f"  entry_ids         : {projektion['entry_ids']}")
        print(f"  basis             : {projektion['basis']}")
        print(f"  summary           : {projektion['summary']}")
        print(f"  motifs            : {projektion['motifs']}")
        print(f"  warnings          : {projektion['warnings']}")
        print(f"  status            : {projektion['status']}")
        print(f"  alte Meta-Keys    : {'alle vorhanden ✓' if keys_vorhanden else 'FEHLER — Keys fehlen!'}")

    # Gesamtverifikation
    print(f"\n[PROJECTION-WRITER] Verifikation:")
    cur.execute("""
        SELECT entity_id, meta->'selfmodel_projection'->>'status' AS proj_status,
               meta->'selfmodel_projection'->>'updated_at' AS updated_at
        FROM entity_profiles
        WHERE entity_id = ANY(%s)
        ORDER BY entity_id
    """, (ENTITY_ALLOWLIST,))
    for row in cur.fetchall():
        print(f"  {row['entity_id']}: selfmodel_projection.status={row['proj_status']}, updated={row['updated_at'][:19] if row['updated_at'] else 'fehlt'}")

    cur.execute("SELECT COUNT(*) AS n FROM entity_selfmodel_entries")
    print(f"  entity_selfmodel_entries gesamt: {cur.fetchone()['n']} (unverändert)")

    cur.close()
    conn.close()
    print("[PROJECTION-WRITER] Fertig.")


if __name__ == "__main__":
    main()
