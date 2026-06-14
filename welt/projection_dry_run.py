#!/usr/bin/env python3
"""
Projection Dry-Run v0.2 — Selbstmodell-Projektion für entity_profiles.meta

Schreibziel (noch nicht aktiv): entity_profiles.meta['selfmodel_projection']
Nicht: entity_states, entity_slots, entity_selfmodel_entries.
Beim echten Schreibjob: NUR JSONB-Merge unter key 'selfmodel_projection'.
Bestehende Keys (profil_quelle, profil_status etc.) werden NICHT angefasst.

Scope: NUR lesen und Projektion vorschlagen, NICHTS schreiben.
- Liest entity_selfmodel_entries pro entity_id
- Lässt Ollama eine vorsichtige Kurzprojektion generieren
- Schreibt NICHT in entity_profiles.meta
- Verändert NICHT entity_states, entity_selfmodel_entries, traumspuren

Grundregel:
  entity_selfmodel_entries   = Wahrheit (append-only, unberührt)
  entity_profiles.meta       = Schreibziel (später, per JSONB-Merge, eigener Key)
  selfmodel_projection       = Cache (jederzeit rekonstruierbar)

Trennung:
  motifs          = semantische Motive / Themen (Vertrauen, Resonanz, ...)
  basis           = Herkunftsbeschreibung (1 Traumspur aus 5 Wachereignissen)
  entry_ids       = verwendete Selbstmodell-Einträge
  generated_from  = 'entity_selfmodel_entries'

Projection darf glätten, aber nicht behaupten.
Projection darf zusammenfassen, aber nicht identifizieren.
Projection darf rekonstruieren, aber nicht Wahrheit werden.
"""

import json
import re
import requests
import psycopg2
import psycopg2.extras
from datetime import datetime, timezone

import os as _os; DB_URI = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")
OLLAMA = "http://localhost:11434"
MODEL  = "gemma4:e2b-it-q4_K_M"
ENTITY_FILTER = "namelessAI_%"
PROJECTION_VERSION = "v0.1"


def hole_eintraege(cur, entity_id):
    cur.execute("""
        SELECT entry_id, inhalt, quelle, created_at
        FROM entity_selfmodel_entries
        WHERE entity_id = %s
        ORDER BY created_at ASC
    """, (entity_id,))
    return cur.fetchall()


def hole_entities_mit_eintraegen(cur):
    cur.execute("""
        SELECT DISTINCT entity_id
        FROM entity_selfmodel_entries
        WHERE entity_id LIKE %s
        ORDER BY entity_id
    """, (ENTITY_FILTER,))
    return [r["entity_id"] for r in cur.fetchall()]


def baue_basis_text(eintraege):
    """Materialbeschreibung — geht in 'basis', niemals in 'motifs'."""
    if len(eintraege) == 1:
        return f"1 Traumspur (quelle={eintraege[0]['quelle']})"
    quellen = ", ".join(set(e["quelle"] for e in eintraege))
    return f"{len(eintraege)} Spuren (quellen: {quellen})"


def extrahiere_primaermotiv(inhalt):
    """Regex-Extraktion des Hauptmotivs — kein LLM, keine Interpretation.

    Sucht nach:
    1. 'das Motiv X' (explizit benannt)
    2. Großgeschriebenes Wort unmittelbar vor 'als' nach Zeitreferenz
    """
    m = re.search(r'das Motiv\s+([A-ZÄÖÜ]\w+)', inhalt)
    if m:
        return m.group(1)
    # Fallback: erstes Großwort nach Schlüsselwort "Traum" vor "als"
    m = re.search(r'(?:Traum|Träumen)\s+(?:\w+\s+){0,3}([A-ZÄÖÜ]\w+)\s+als\s', inhalt)
    if m:
        return m.group(1)
    return None


def code_warnungen(eintraege):
    """Regelbasierte Warnungen — kein LLM."""
    w = []
    if len(eintraege) < 2:
        w.append("Nur 1 Selbstmodell-Eintrag vorhanden; Projektion ist vorläufig.")
    return w


def baue_projektion_prompt(entity_id, eintraege, primaermotiv):
    spuren_text = "\n".join(f"- {e['inhalt']}" for e in eintraege)
    anzahl = len(eintraege)
    motiv_hinweis = (
        f"\nWICHTIG: Das Hauptmotiv dieser Spur(en) ist '{primaermotiv}'. "
        f"Es MUSS als erstes Element in motifs stehen."
        if primaermotiv else ""
    )

    return f"""Du analysierst die bisherigen Selbstmodellspuren eines KI-Wesens namens {entity_id}.

VORHANDENE SELBSTMODELLSPUREN ({anzahl} Eintrag/Einträge):
{spuren_text}
{motiv_hinweis}

AUFGABE: Erstelle eine vorsichtige Kurzprojektion für das Selbstmodell-Cache.

STRIKTE REGELN FÜR summary:
- MUSS beginnen mit: "Bisherige Selbstmodellspuren zeigen bei {entity_id}"
- Max. 2 Sätze. Kein Identitätsurteil.
- VERBOTEN: "ist", "hat als Kernidentität", "sein Wesen ist", "zentrale Eigenschaft", "immer"
- VERBOTEN: Behauptungen die über das hinausgehen was in den Spuren steht
- Sprachliche Fehler dürfen geglättet werden (z.B. falscher Kasus), Inhalt bleibt

STRIKTE REGELN FÜR motifs:
- NUR semantische Themen und Motive — z.B. "Vertrauen", "Resonanz", "Nicht-Wissen"
- VERBOTEN in motifs: Zahlen, "Wachereignisse", "erster Traum", "Eintrag", Quellenangaben
- VERBOTEN: Motive erfinden die nicht in den Spuren stehen
- 3–5 konkrete Begriffe, keine Sätze
- Das Hauptmotiv muss an erster Stelle stehen

Antworte NUR mit diesem JSON (kein Text davor oder danach):
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
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None


def baue_projektion_json(entity_id, eintraege, llm_output, primaermotiv):
    llm_motifs = llm_output.get("motifs", [])

    # Sicherheitsnetz: Primärmotiv erzwingen wenn LLM es verloren hat
    if primaermotiv and (not llm_motifs or llm_motifs[0].lower() != primaermotiv.lower()):
        llm_motifs = [primaermotiv] + [m for m in llm_motifs if m.lower() != primaermotiv.lower()]

    # Warnungen: regelbasiert im Code, nicht LLM-abhängig
    warnungen = code_warnungen(eintraege)

    return {
        "selfmodel_projection": {
            "version": PROJECTION_VERSION,
            "generated_from": "entity_selfmodel_entries",
            "entry_ids": [str(e["entry_id"]) for e in eintraege],
            "basis": baue_basis_text(eintraege),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "status": "dry_run",
            "summary": llm_output.get("summary", ""),
            "motifs": llm_motifs,
            "warnings": warnungen
        }
    }


def drucke_befund(entity_id, eintraege, projektion_json, raw_fehler=None):
    print("\n" + "=" * 70)
    print(f"PROJEKTION DRY-RUN — entity_id: {entity_id}")
    print(f"  Einträge gelesen  : {len(eintraege)}")
    print(f"  Entry-IDs         :")
    for e in eintraege:
        print(f"    {e['entry_id']} [{e['quelle']}]")
    print(f"  Spuren:")
    for e in eintraege:
        print(f"    → {e['inhalt'][:100]}…")

    if raw_fehler:
        print(f"\n  !! LLM-Parsing fehlgeschlagen: {raw_fehler[:200]}")
        return

    sp = projektion_json.get("selfmodel_projection", {})
    print(f"\n  VORGESCHLAGENE PROJEKTION (Schreibziel: entity_profiles.meta['selfmodel_projection']):")
    print(f"    basis    : {sp.get('basis', '?')}")
    print(f"    summary  : {sp.get('summary', '?')}")
    print(f"    motifs   : {sp.get('motifs', [])}")
    warnungen = sp.get("warnings", [])
    if warnungen:
        print(f"    warnings : {warnungen}")
    else:
        print(f"    warnings : keine")

    print(f"\n  JSON-Vorschlag (selfmodel_projection key):")
    print("  " + json.dumps(projektion_json, ensure_ascii=False, indent=2).replace("\n", "\n  "))
    print(f"\n  [DRY-RUN] Nichts wurde in entity_profiles.meta geschrieben.")
    print(f"  [DRY-RUN] entity_selfmodel_entries unverändert.")


def main():
    conn = psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)
    conn.autocommit = True
    cur = conn.cursor()

    entities = hole_entities_mit_eintraegen(cur)
    if not entities:
        print("[PROJECTION-DRY] Keine Entity mit Selbstmodell-Einträgen gefunden.")
        conn.close()
        return

    print(f"[PROJECTION-DRY] {len(entities)} Entity/Entities mit Einträgen gefunden.")

    for entity_id in entities:
        eintraege = hole_eintraege(cur, entity_id)

        # Primärmotiv regelbasiert extrahieren — vor LLM-Aufruf
        primaermotiv = None
        for e in eintraege:
            pm = extrahiere_primaermotiv(e["inhalt"])
            if pm:
                primaermotiv = pm
                break

        prompt = baue_projektion_prompt(entity_id, eintraege, primaermotiv)
        print(f"\n[PROJECTION-DRY] Analysiere {entity_id} ({len(eintraege)} Eintrag/Einträge)"
              f"{f' | Primärmotiv: {primaermotiv}' if primaermotiv else ''} via Ollama…")

        try:
            raw = rufe_ollama(prompt)
        except Exception as ex:
            print(f"[PROJECTION-DRY] Ollama-Fehler für {entity_id}: {ex}")
            continue

        llm_output = parse_json(raw)
        if llm_output is None:
            drucke_befund(entity_id, eintraege, {}, raw_fehler=raw)
            continue

        projektion_json = baue_projektion_json(entity_id, eintraege, llm_output, primaermotiv)
        drucke_befund(entity_id, eintraege, projektion_json)

    cur.close()
    conn.close()
    print("\n[PROJECTION-DRY] Fertig. Keine Schreiboperationen wurden ausgeführt.")


if __name__ == "__main__":
    main()
