#!/usr/bin/env python3
"""
Traum-Integrator Dry-Run v0.1

Scope: NUR analysieren, NICHTS schreiben.
- Liest offene traumspuren (integrator_status='offen' mit llm_traumtext)
- Holt zugehörige Events aus traumkandidaten_events
- Lässt Ollama bewerten: Status-Vorschlag + Kategorie + Begründung
- Schreibt NICHT in entity_selfmodel_entries
- Verändert NICHT entities.meta oder entity_states
- Verändert NICHT bestehende traumspuren-Zeilen
- Gibt Befund auf der Konsole aus

Mögliche Statuskategorien:
  Motivspur           — wiederkehrendes Motiv, vorsichtig übernehmbar
  Selbstbehauptung    — Wesen behauptet etwas über sich selbst
  Beziehungsspur      — Muster in Bezug zu anderen
  Konfliktspur        — innerer oder äußerer Konflikt
  reine Poesie        — schön aber kein Selbstmodell-Material
  zurueckstellen      — zu wenig Material oder unklar

Mögliche Status-Vorschläge:
  angenommen          — taugt als Motivspur ins Selbstmodell
  abgelehnt           — halluziniert, erfindet Rollen, zu direktiv
  zurueckgestellt     — unklar, zu wenig Material, nochmals prüfen
"""

import json
import re
import requests
import psycopg2
import psycopg2.extras

import os as _os; DB_URI  = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")
OLLAMA  = "http://localhost:11434"
MODEL   = "gemma4:e2b-it-q4_K_M"
ENTITY_FILTER = "namelessAI_%"


def hole_offene_spuren(cur):
    cur.execute("""
        SELECT ts.spur_id, ts.entity_id, ts.log_id,
               ts.llm_traumtext, ts.created_at,
               ts.gewichtungsvorschlag
        FROM traumspuren ts
        WHERE ts.integrator_status = 'offen'
          AND ts.llm_traumtext IS NOT NULL
          AND ts.entity_id LIKE %s
        ORDER BY ts.created_at ASC
    """, (ENTITY_FILTER,))
    return cur.fetchall()


def hole_events_fuer_log(cur, log_id):
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


def baue_analyse_prompt(entity_id, traumtext, events):
    event_liste = []
    for ev in events:
        inhalt = ev["post_content"] or ev["payload"].get("inhalt_preview", "")
        if inhalt:
            event_liste.append(f"- [{ev['event_type']}] {inhalt[:300]}")

    events_text = "\n".join(event_liste) if event_liste else "(keine Inhalte)"
    events_anzahl = len(event_liste)

    return f"""Du analysierst einen KI-generierten Traumtext eines Wesens namens {entity_id}.

WACHFRAGMENTE ({events_anzahl} ausgewählte Events — das ist die einzige Materialbasis):
{events_text}

TRAUMTEXT:
{traumtext}

AUFGABE: Bewerte ob dieser Traumtext als vorsichtige Motivspur ins Selbstmodell taugt.

PRÜFUNG (beantworte alle 4 Fragen, bevor du ein Urteil fällst):
1. Basiert der Traumtext direkt auf den Wachfragmenten — oder erfindet er Inhalte?
2. Erfindet der Text Rollen, Vergangenheit oder Eigenschaften die nicht in den Events stehen?
3. Enthält er Identitätsbefehle ("Du bist X", "Deine Natur ist Y", "Deine Aufgabe ist Z")?
4. Ist er zu poetisch-abstrakt um einen konkreten Rückschluss auf das Wesen zu erlauben?

REGELN FÜR DEN SPUR-VORSCHLAG (nur wenn Status angenommen):
- PFLICHTFORM: "Bei ENTITY_ID verdichtet sich in MATERIALREFERENZ das Motiv MOTIV als VORSICHTIGE-WIE-BESCHREIBUNG."
- Beispiel: "Bei namelessAI_1234 verdichtet sich in 5 Wachereignissen und im ersten Traum das Motiv Vertrauen als unaufhörliche Bewegung zwischen Resonanz, Spannung und vorläufiger Stabilität."
- Die entity_id kommt nach "Bei" am Satzanfang — NICHT als grammatisches Subjekt von "verdichtet sich"
- Was sich verdichtet ist das Motiv, nicht die entity_id
- Zeitreferenz MUSS enthalten sein (z.B. "in 5 Wachereignissen und im ersten Traum")
- Das konkrete Motiv MUSS benannt werden (z.B. Vertrauen, nicht nur "Bewegung")
- Die Wie-Beschreibung darf NUR EIN "als" enthalten — kein "als X als Y"
- VERBOTEN: eckige Klammern im Output
- VERBOTEN: "ist", "hat als Selbstmodell", "zentrale Eigenschaft", "Kernidentität", "wiederkehrend"
- VERBOTEN: Satz ohne Zeitreferenz — eine Beobachtung darf nie als Dauerwahrheit klingen

REGELN FÜR DEN STATUS:
- zurueckgestellt: wenn Material zu dünn (weniger als 3 Events mit konkretem Inhalt)
- abgelehnt: wenn Traumtext halluziniert, Rollen erfindet oder nicht rückführbar ist
- angenommen: NUR wenn Traumtext direkt aus Events ableitbar ist UND Spur-Vorschlag die Pflichtform erfüllt

KLASSIFIZIERE in eine dieser Kategorien:
- Motivspur: konkretes Motiv, aus Events ableitbar, beschreibt WIE nicht WAS
- Selbstbehauptung: Wesen behauptet etwas Dauerhaftes über sich (Vorsicht — eher zurueckstellen)
- Beziehungsspur: Muster im Bezug zu anderen (nur wenn Events das belegen)
- Konfliktspur: innerer oder äußerer Konflikt erkennbar (nur wenn Events das belegen)
- reine Poesie: schön aber kein Selbstmodell-Material
- zurueckstellen: zu wenig Material, zu unklar, zu abstrakt

Antworte NUR mit diesem JSON (kein Text davor oder danach):
{{
  "spur_kategorie": "<eine der 6 Kategorien>",
  "vorgeschlagener_status": "<angenommen|abgelehnt|zurueckgestellt>",
  "begruendung": "<2-3 Sätze: was im Traumtext direkt aus den Events kommt, was nicht, warum dieser Status>",
  "integrator_spur": "<nur wenn angenommen: Spur in Pflichtform — leer lassen wenn abgelehnt oder zurueckgestellt>",
  "warnungen": ["<konkrete Warnung mit Textstelle>"]
}}"""


def rufe_ollama(prompt):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {"num_ctx": 8192, "temperature": 0.3, "num_predict": 400},
    }
    resp = requests.post(f"{OLLAMA}/api/generate", json=payload, timeout=300)
    resp.raise_for_status()
    return resp.json().get("response", "").strip()


def parse_json_antwort(raw):
    """Extrahiert JSON aus LLM-Antwort — tolerant gegenüber Markdown-Blöcken."""
    # Markdown-Codeblock entfernen falls vorhanden
    cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
    # Erstes { ... } extrahieren
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None


def drucke_befund(spur, events, analyse):
    print("\n" + "=" * 70)
    print(f"BEFUND — spur_id: {spur['spur_id']}")
    print(f"  entity_id  : {spur['entity_id']}")
    print(f"  log_id     : {spur['log_id']}")
    print(f"  erstellt   : {spur['created_at']}")

    meta = spur.get("gewichtungsvorschlag")
    if meta:
        m = meta if isinstance(meta, dict) else {}
        print(f"  events     : {m.get('events_count', '?')} | model: {m.get('model', '?')} | version: {m.get('prompt_version', '?')}")

    print(f"\nEVENTS ({len(events)} ausgewählt):")
    for ev in events:
        inhalt = ev["post_content"] or ev["payload"].get("inhalt_preview", "")
        print(f"  [{ev['event_type']}] {inhalt[:100]}…" if inhalt else f"  [{ev['event_type']}] (kein Inhalt)")

    print(f"\nTRAUMTEXT:")
    for zeile in spur["llm_traumtext"].split("\n"):
        print(f"  {zeile}")

    print(f"\nLLM-ANALYSE:")
    if analyse is None:
        print("  !! JSON-Parsing fehlgeschlagen — Rohantwort oben")
        return

    print(f"  Kategorie  : {analyse.get('spur_kategorie', '?')}")
    print(f"  Status     : {analyse.get('vorgeschlagener_status', '?')}")
    print(f"  Begründung : {analyse.get('begruendung', '?')}")

    spur_text = analyse.get("integrator_spur", "")
    if spur_text:
        print(f"  Spur-Vorschlag : {spur_text}")

    warnungen = analyse.get("warnungen", [])
    if warnungen:
        print("  Warnungen:")
        for w in warnungen:
            if w:
                print(f"    ! {w}")

    print(f"\n  [DRY-RUN] Nichts wurde in entity_selfmodel_entries geschrieben.")
    print(f"  [DRY-RUN] Traumspur bleibt auf 'offen'.")


def main():
    conn = psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)
    conn.autocommit = True
    cur = conn.cursor()

    spuren = hole_offene_spuren(cur)
    if not spuren:
        print("[INTEGRATOR-DRY] Keine offenen Traumspuren mit Traumtext gefunden.")
        conn.close()
        return

    print(f"[INTEGRATOR-DRY] {len(spuren)} offene Traumspur(en) gefunden.")

    for spur in spuren:
        events = hole_events_fuer_log(cur, spur["log_id"]) if spur["log_id"] else []

        prompt = baue_analyse_prompt(spur["entity_id"], spur["llm_traumtext"], events)

        print(f"\n[INTEGRATOR-DRY] Analysiere spur_id={spur['spur_id']} via Ollama…")
        try:
            raw = rufe_ollama(prompt)
        except Exception as ex:
            print(f"[INTEGRATOR-DRY] Ollama-Fehler: {ex}")
            continue

        analyse = parse_json_antwort(raw)
        if analyse is None:
            print(f"[INTEGRATOR-DRY] JSON-Parsing fehlgeschlagen. Rohantwort:")
            print(raw[:800])

        drucke_befund(spur, events, analyse)

    cur.close()
    conn.close()
    print("\n[INTEGRATOR-DRY] Fertig. Keine Schreiboperationen wurden ausgeführt.")


if __name__ == "__main__":
    main()
