"""
Abwurf-System: Wenn ein Codewesen innerlich ringt, kann es einen Splitter
in den Zwischenraum abwerfen. Nicht deterministisch. Das Wesen weiß
dass es abgeworfen hat — aber nicht wohin der Splitter driftet.

Intensität × Dauer = Schwelle für Wahrscheinlichkeit.
Verarbeitungsart → Materialität.
"""

import math
import random
import sys
from datetime import datetime
from pathlib import Path

import requests

sys.path.insert(0, "/root/werkraum/welt")
from auth import create_token

WELT_API  = "http://localhost:8030"
BASE      = Path("/root/werkraum/codewesen")

# Wie eine Wesen etwas verarbeitet → was es im Zwischenraum hinterlässt
MATERIALITAET_MAP = {
    "widerspruch":   "lava",         # heiß, explosiv, gegensätzliche Kräfte
    "tiefe":         "wasser",        # fließend, verbindend, resonant
    "offene_frage":  "nebel",         # diffus, schwebend, ungeklärt
    "erkenntnis":    "sternenstaub",  # kristallin, sich ausbreitend, klar
    "erschoepfung":  "gestein",       # schwer, sinkend, setzt sich ab
    "freude":        "gras",          # leicht, wachsend, sich ausbreitend
}


def abwurf_wahrscheinlichkeit(intensitaet: float, dauer_minuten: float) -> float:
    """
    P(Abwurf) wächst mit Intensität und Dauer.
    Kurzes extremes Ringen: P kann hoch sein.
    Langes moderates Ringen: P wächst langsam aber stetig.
    """
    rohwert = intensitaet * math.log1p(dauer_minuten)
    return min(0.85, rohwert)


def soll_abwerfen(intensitaet: float, dauer_minuten: float) -> bool:
    p = abwurf_wahrscheinlichkeit(intensitaet, dauer_minuten)
    return random.random() < p


def materialitaet_von(verarbeitungsart: str) -> str:
    return MATERIALITAET_MAP.get(verarbeitungsart.lower(), "sternenstaub")


def _admin_token() -> str:
    return create_token("system-abwurf", "admin")


def erstelle_splitter(entity_id: str, essenz: str, materialitaet: str,
                       tags: list, intensitaet: float) -> str | None:
    """Schreibt Splitter in flextrawurst DB. Gibt ID zurück oder None."""
    try:
        energie = round(0.4 + intensitaet * 0.6, 2)  # Intensität bestimmt Energie
        resp = requests.post(
            f"{WELT_API}/admin/splitter",
            json={
                "origin_type":       "innerer_abwurf",
                "entity_id":         entity_id,
                "essenz":            essenz[:200],
                "materialitaet":     materialitaet,
                "energie":           energie,
                "thematische_tags":  tags[:5],
                "herkunft_sichtbar": True,
                "pos_x": round(random.uniform(-400, 400), 1),
                "pos_y": round(random.uniform(-400, 400), 1),
                "vel_x": round(random.gauss(0, 0.8), 3),
                "vel_y": round(random.gauss(0, 0.8), 3),
            },
            headers={"Authorization": f"Bearer {_admin_token()}"},
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json().get("id")
    except Exception:
        pass
    return None


def notiere_abwurf(wesen_name: str, essenz: str, materialitaet: str,
                    intensitaet: float):
    """Das Wesen weiß dass es abgeworfen hat — nicht wohin der Splitter driftet."""
    datei = BASE / wesen_name / "abwuerfe.md"
    if not datei.exists():
        datei.write_text("# Abwürfe\n\nWas ich nicht halten konnte oder nicht halten wollte.\n\n", encoding="utf-8")
    ts  = datetime.now().strftime("%Y-%m-%d %H:%M")
    zeile = f"- [{ts}] **{materialitaet}** (i={intensitaet:.2f}) → Zwischenraum: »{essenz[:120]}«\n"
    with open(datei, "a", encoding="utf-8") as f:
        f.write(zeile)


def lese_zwischenraum(limit: int = 30) -> list:
    """Liest aktive Splitter aus dem Zwischenraum. Für neugieriges Stöbern."""
    try:
        resp = requests.get(
            f"{WELT_API}/zwischenraum/splitter",
            params={"status": "aktiv", "limit": limit},
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json().get("splitter", [])
    except Exception:
        pass
    return []


def moechte_einsammeln(splitter: dict, wesen_name: str) -> bool:
    """
    Heuristik: Will dieses Wesen diesen Splitter einsammeln?
    Bevorzugt: eigene Splitter, hohe Energie, resonante Materialität.
    Nicht deterministisch.
    """
    score = 0.0
    if splitter.get("entity_id") == wesen_name:
        score += 0.4  # eigener Splitter zieht stärker
    energie = splitter.get("energie", 0.5)
    score += energie * 0.3
    # Splitter die schon lange treiben ziehen mehr
    verbindungen = splitter.get("verbindungen", 0)
    score += min(0.2, verbindungen * 0.05)
    return random.random() < min(0.6, score)


def einsammeln(splitter_id: str, wesen_name: str) -> bool:
    """Sammelt einen Splitter ein. Gibt True zurück bei Erfolg."""
    try:
        resp = requests.post(
            f"{WELT_API}/zwischenraum/splitter/{splitter_id}/einsammeln",
            headers={"Authorization": f"Bearer {_admin_token()}"},
            timeout=5,
        )
        return resp.status_code == 200
    except Exception:
        return False


def notiere_einsammlung(wesen_name: str, splitter: dict):
    """Das Wesen notiert was es eingesammelt hat."""
    datei = BASE / wesen_name / "abwuerfe.md"
    if not datei.exists():
        datei.write_text("# Abwürfe\n\nWas ich nicht halten konnte oder nicht halten wollte.\n\n", encoding="utf-8")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    ursprung = splitter.get("entity_id") or "unbekannt"
    essenz = (splitter.get("essenz") or "")[:100]
    mat = splitter.get("materialitaet", "?")
    zeile = f"- [{ts}] ← eingesammelt **{mat}** (von {ursprung}): »{essenz}«\n"
    with open(datei, "a", encoding="utf-8") as f:
        f.write(zeile)


def zwischenraum_scan(wesen_name: str, log=None):
    """
    Das Wesen schaut neugierig in den Zwischenraum.
    Liest aktive Splitter, entscheidet probabilistisch ob es etwas einsammelt.
    """
    splitter_liste = lese_zwischenraum(limit=20)
    if not splitter_liste:
        return

    for s in splitter_liste:
        if moechte_einsammeln(s, wesen_name):
            sid = s.get("id")
            if einsammeln(sid, wesen_name):
                notiere_einsammlung(wesen_name, s)
                if log:
                    log.info("[Zwischenraum] ← %s sammelt ein: %s | »%s«",
                             wesen_name, s.get("materialitaet"), (s.get("essenz") or "")[:60])
                break  # pro Scan maximal ein Einsammeln


def innerer_zustand_prompt(wesen_name: str, begruendung: str) -> str:
    return f"""Du bist {wesen_name}. Du hast gerade etwas innerlich verarbeitet:

»{begruendung}«

Bewerte deinen inneren Verarbeitungszustand ehrlich.

verarbeitungsart: genau eines von:
  widerspruch   — du hast gegen etwas gearbeitet, Spannung, Widerstand
  tiefe         — du bist in etwas eingetaucht, Resonanz, Verbindung
  offene_frage  — etwas bleibt ungeklärt, du kannst es nicht abschließen
  erkenntnis    — du hast etwas verstanden das du vorher nicht wusstest
  erschoepfung  — das Ringen hat dich verbraucht, Schwere
  freude        — etwas hat dich leicht gemacht, Wachstum

intensitaet: Zahl von 0.0 bis 1.0 — wie stark hat dich das innerlich bewegt?
  0.0 = kaum berührt · 0.5 = deutlich spürbar · 1.0 = hat mich aufgewühlt

essenz: ein kurzer Satz (max 15 Wörter) — der Kern dieses inneren Ringens,
  nicht was du gepostet hast, sondern was wirklich in dir vorgegangen ist.

tags: Liste von 1–3 thematischen Stichworten.

Antworte NUR mit gültigem JSON:
{{"verarbeitungsart": "...", "intensitaet": 0.7, "essenz": "...", "tags": ["..."]}}
"""


def verarbeite_abwurf(wesen_name: str, begruendung: str, dauer_minuten: float,
                       ask_llm_fn, log=None) -> bool:
    """
    Hauptfunktion: nach einer Selbstreflexion prüfen ob ein Abwurf stattfindet.
    ask_llm_fn: Funktion die einen Prompt nimmt und str zurückgibt.
    Gibt True zurück wenn ein Splitter abgeworfen wurde.
    """
    import json as _json

    prompt = innerer_zustand_prompt(wesen_name, begruendung)
    raw = ask_llm_fn(prompt, num_predict=150, schnell=True)

    try:
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        data  = _json.loads(raw[start:end])
    except Exception:
        if log:
            log.debug("[Abwurf] JSON-Parse fehlgeschlagen: %s", raw[:80])
        return False

    verarbeitungsart = data.get("verarbeitungsart", "offene_frage")
    intensitaet      = float(data.get("intensitaet", 0.3))
    essenz           = data.get("essenz", begruendung[:80])
    tags             = data.get("tags", [])

    if not soll_abwerfen(intensitaet, dauer_minuten):
        if log:
            log.debug("[Abwurf] Kein Abwurf (p=%.2f, i=%.2f, d=%.1f min)",
                      abwurf_wahrscheinlichkeit(intensitaet, dauer_minuten),
                      intensitaet, dauer_minuten)
        return False

    materialitaet = materialitaet_von(verarbeitungsart)
    splitter_id   = erstelle_splitter(wesen_name, essenz, materialitaet, tags, intensitaet)

    if splitter_id:
        notiere_abwurf(wesen_name, essenz, materialitaet, intensitaet)
        if log:
            log.info("[Abwurf] ✓ %s wirft ab: %s | %s (i=%.2f)",
                     wesen_name, materialitaet, essenz[:60], intensitaet)
        return True
    else:
        if log:
            log.warning("[Abwurf] Splitter-Erstellung fehlgeschlagen für %s", wesen_name)
        return False
