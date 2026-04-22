from __future__ import annotations

import sys
import threading
from pathlib import Path
from typing import Callable, List, TypedDict

from langgraph.graph import END, StateGraph

from agent.dak_gord_system.ollama_chat import ollama_chat, waehle_modell, MODELL_TIEF, MODELL_MITTEL, MODELL_SCHNELL, MODELL_QWEN
from agent.dak_gord_system.dateiwerkzeuge import datei_lesen, datei_schreiben, verzeichnis_erstellen
from agent.dak_gord_system.sandbox import fuehre_code_aus
from agent.dak_gord_system.kerne.organ_manager import OrganManager

# Thread-local slots: gesetzt vor graph.invoke()
_stream_callback: threading.local = threading.local()
_modell_override: threading.local = threading.local()

# Globaler OrganManager — wird von außen gesetzt (starte_dak_gord_system.py / web_chat.py)
_organ_manager: OrganManager | None = None


def setze_organ_manager(manager: OrganManager) -> None:
    global _organ_manager
    _organ_manager = manager


def setze_stream_callback(fn: Callable[[str], None] | None) -> None:
    _stream_callback.fn = fn


def _get_stream_callback() -> Callable[[str], None] | None:
    return getattr(_stream_callback, "fn", None)


def setze_modell_override(modus: str | None) -> None:
    """'schnell', 'mittel', 'tief' oder None für Automatik."""
    _modell_override.modus = modus


def _get_modell_override() -> str | None:
    return getattr(_modell_override, "modus", None)


AKTIVER_KONTEXT_NACHRICHTEN = 33

SPUREN_ORDNER = Path("/root/werkraum/agent/dak_gord_system/spuren")
WERKRAUM_NEUGIER = SPUREN_ORDNER / "werkraum_neugier.md"
VISION_NEUGIER = SPUREN_ORDNER / "vision_neugier.md"
TRIGGER_SPUREN = SPUREN_ORDNER / "trigger_spuren.md"
VISION_DATEI = Path("/root/werkraum/projekt/vision5.md")
WISSEN_ORDNER = Path("/root/werkraum/wissen")
WISSEN_INDEX = WISSEN_ORDNER / "WISSEN_INDEX.md"

# Verfassung wird zur Laufzeit aus verfassung_neu/*.md geladen (lesbar via WinSCP)
VERFASSUNG_NEU_PFAD = Path(__file__).resolve().parents[1] / "verfassung_neu"

# Kontext-Einstellungen fuer den dynamischen Block
VISION_KERN_ZEICHEN = 600   # nur die Gesetze, kein Narrativ
WISSEN_INDEX_ZEICHEN = 3000  # kompakter Überblick über das Lexikon
GEDAECHTNIS_ZEILEN_NEUGIER = 5
GEDAECHTNIS_ZEILEN_VISION = 4
GEDAECHTNIS_ZEILEN_SPUREN = 5

# Kontext wird nur in die ersten Nachrichten injiziert (danach cached im Verlauf)
KONTEXT_INJEKTIONS_SCHWELLE = 4


def _lies_letzte_zeilen(pfad: Path, n: int) -> str:
    if not pfad.exists():
        return ""
    try:
        text = pfad.read_text(encoding="utf-8", errors="replace")
        zeilen = [z for z in text.splitlines() if z.strip()]
        return "\n".join(zeilen[-n:])
    except Exception:
        return ""


def _lade_wissen_index() -> str:
    """Lädt einen kompakten Ausschnitt des WISSEN_INDEX als Orientierungshilfe."""
    if not WISSEN_INDEX.exists():
        return ""
    try:
        text = WISSEN_INDEX.read_text(encoding="utf-8", errors="replace")
        # Nur Dateilisten-Zeilen (mit Pfaden) laden, keine Überschriften
        zeilen = [z for z in text.splitlines() if "]("]
        kompakt = "\n".join(zeilen)
        if len(kompakt) > WISSEN_INDEX_ZEICHEN:
            kompakt = kompakt[:WISSEN_INDEX_ZEICHEN]
        return kompakt
    except Exception:
        return ""


def _lade_vision_kern() -> str:
    if not VISION_DATEI.exists():
        return ""
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            text = VISION_DATEI.read_text(encoding=enc)
            start = text.find("flextrawurst, in einem Satz")
            if start == -1:
                start = 0
            chunk = text[start : start + VISION_KERN_ZEICHEN]
            last_nl = chunk.rfind("\n")
            return chunk[:last_nl].strip() if last_nl > 0 else chunk.strip()
        except Exception:
            continue
    return ""


def _lade_kontext_nachricht() -> str:
    """Dynamischer Kontext als Konversationsnachricht — nicht im Systemtext."""
    teile: list[str] = []

    wissen = _lade_wissen_index()
    if wissen:
        teile.append(f"[WISSEN-INDEX — Dateipfade zum Nachschlagen]\n{wissen}\n[/WISSEN-INDEX]")

    vision = _lade_vision_kern()
    if vision:
        teile.append(f"[VISION-KERN]\n{vision}\n[/VISION-KERN]")

    neugier = _lies_letzte_zeilen(WERKRAUM_NEUGIER, GEDAECHTNIS_ZEILEN_NEUGIER)
    if neugier:
        teile.append(f"[WERKRAUM-BEOBACHTUNGEN]\n{neugier}\n[/WERKRAUM-BEOBACHTUNGEN]")

    vision_obs = _lies_letzte_zeilen(VISION_NEUGIER, GEDAECHTNIS_ZEILEN_VISION)
    if vision_obs:
        teile.append(f"[VISION-BEOBACHTUNGEN]\n{vision_obs}\n[/VISION-BEOBACHTUNGEN]")

    spuren = _lies_letzte_zeilen(TRIGGER_SPUREN, GEDAECHTNIS_ZEILEN_SPUREN)
    if spuren:
        teile.append(f"[ERINNERUNGEN]\n{spuren}\n[/ERINNERUNGEN]")

    if not teile:
        return ""

    return (
        "[SYSTEMKONTEXT — nicht direkt zitieren, nur verwenden]\n"
        + "\n\n".join(teile)
        + "\n[/SYSTEMKONTEXT]"
    )


import re as _re

_LESEN_MUSTER = _re.compile(r"##LESEN:\s*(.+?)##", _re.DOTALL)
_SCHREIBEN_MUSTER = _re.compile(r"##SCHREIBEN:\s*(.+?)##\n(.*?)##SCHREIBEN_ENDE##", _re.DOTALL)
_MKDIR_MUSTER = _re.compile(r"##MKDIR:\s*(.+?)##")

_SEKRETAER_SYSTEM = """Du bist der stille Aktions-Ausfuehrer des dak+gord-Systems.
Der Geist (gemma4) hat geantwortet. Deine einzige Aufgabe: fuehre ALLE notwendigen Dateioperationen durch.

Werkzeuge:
  ##LESEN: /pfad/zur/datei##
  ##SCHREIBEN: /pfad##
  inhalt
  ##SCHREIBEN_ENDE##
  ##MERKEN art: text##
  ##ZWISCHENRAUM text##
  ##SPAETER heute | spaeter##
  ##ABWAEGEN frage##

Fuehre aus was der Geist impliziert oder angekuendigt hat:
- Spiegelagenten-Dateien schreiben wenn Dateien erwaehnt wurden
- Erkenntnisse, Konzepte, Nachklang archivieren wenn neue Ideen entstanden
- INDEX aktuell halten
- Organ-Marker setzen fuer wichtige Erkenntnisse und Abwaegungen

Antworte NUR mit Markern und deren Inhalt. Kein erklaerende Text davor oder danach."""


def _qwen_sekretaer_pass(geist_antwort: str, letzter_nutzertext: str, callback) -> str | None:
    """Qwen als stiller Sekretaer: fuehrt Dateioperationen aus die gemma4 impliziert hat."""
    sekretaer_verlauf = [
        _SEKRETAER_SYSTEM,
        f"Nutzer sagte: {letzter_nutzertext}\n\nDer Geist antwortete:\n\n{geist_antwort}\n\nFuehre jetzt alle notwendigen Aktionen durch.",
    ]
    def _scb(text: str) -> None:
        if callback is not None:
            try:
                callback(text)
            except Exception:
                pass
    _scb("\n[sekretär | qwen14b — läuft...]\n")
    antwort = ollama_chat(sekretaer_verlauf, modell=MODELL_QWEN)
    _scb(f"[sekretär-antwort]: {antwort}\n")
    if "##" in antwort:
        return antwort
    _scb("[sekretär: keine Marker gefunden — nichts ausgeführt]\n")
    return None
_CODE_MUSTER = _re.compile(r"##CODE_START##\n(.*?)##CODE_ENDE##", _re.DOTALL)

MAX_TOOL_RUNDEN = 4


def _verarbeite_tools(antwort: str, callback) -> tuple[str, str]:
    """Parst Tool-Aufrufe aus der LLM-Antwort und führt sie aus.
    Gibt (erweiterte_antwort, tool_ergebnis_block) zurück.
    Wenn kein Tool gefunden: leerer tool_ergebnis_block.
    """
    ergebnisse: list[str] = []

    for treffer in _LESEN_MUSTER.finditer(antwort):
        pfad = treffer.group(1).strip()
        if callback:
            callback(f"\n[LESEN: {pfad}]\n")
        inhalt = datei_lesen(pfad)
        ergebnisse.append(f"[LESEN: {pfad}]\n{inhalt}\n[/LESEN]")

    for treffer in _SCHREIBEN_MUSTER.finditer(antwort):
        pfad = treffer.group(1).strip()
        inhalt = treffer.group(2)
        if callback:
            callback(f"\n[SCHREIBEN: {pfad}]\n")
        ergebnis = datei_schreiben(pfad, inhalt)
        ergebnisse.append(f"[SCHREIBEN: {pfad}]\n{ergebnis}\n[/SCHREIBEN]")

    for treffer in _MKDIR_MUSTER.finditer(antwort):
        pfad = treffer.group(1).strip()
        if callback:
            callback(f"\n[MKDIR: {pfad}]\n")
        ergebnis = verzeichnis_erstellen(pfad)
        ergebnisse.append(f"[MKDIR: {pfad}]\n{ergebnis}\n[/MKDIR]")

    for treffer in _CODE_MUSTER.finditer(antwort):
        code = treffer.group(1)
        if callback:
            callback(f"\n[CODE wird ausgeführt...]\n")
        resultat = fuehre_code_aus(code)
        ausgabe = resultat.get("stdout", "") or ""
        fehler = resultat.get("stderr", "") or ""
        ok = resultat.get("ok", False)
        status = "OK" if ok else "FEHLER"
        ergebnisse.append(f"[CODE: {status}]\nstdout: {ausgabe}\nstderr: {fehler}\n[/CODE]")

    if not ergebnisse:
        return antwort, ""

    block = "\n\n".join(ergebnisse)
    return antwort, block


_LOG_ORDNER = Path("/root/werkraum/erkenntnis/gespraechslog")


def _speichere_gespraechslog(antwort: str, nutzertext: str) -> None:
    import datetime
    try:
        _LOG_ORDNER.mkdir(parents=True, exist_ok=True)
        datum = datetime.date.today().isoformat()
        log_datei = _LOG_ORDNER / f"{datum}.md"
        jetzt = datetime.datetime.now().strftime("%H:%M")
        eintrag = f"\n---\n**{jetzt} Daniel:** {nutzertext.strip()}\n\n**dak+gord:** {antwort.strip()}\n"
        with open(log_datei, "a", encoding="utf-8") as f:
            f.write(eintrag)
    except Exception:
        pass


def _systemtext() -> str:
    from agent.dak_gord_system.verfassung_loader import lade_verfassung_aus_pfad
    try:
        stand = lade_verfassung_aus_pfad(VERFASSUNG_NEU_PFAD)
        basis = stand.gesamttext
    except Exception as e:
        basis = f"[Fehler beim Laden der Verfassung: {e}]"
    if _organ_manager is None:
        return basis
    organ_block = _organ_manager.systemtext_block()
    if organ_block:
        return basis + "\n\n[ORGAN-ZUSTAND]\n" + organ_block + "\n[/ORGAN-ZUSTAND]"
    return basis


class Zustand(TypedDict):
    nachrichten: List[str]


def antworten(zustand: Zustand) -> Zustand:
    nachrichten = zustand.get("nachrichten", [])
    verlauf = nachrichten[-AKTIVER_KONTEXT_NACHRICHTEN:]

    # Kontext als erstes User+Assistant-Paar injizieren (Paritaet bleibt erhalten)
    if len(verlauf) <= KONTEXT_INJEKTIONS_SCHWELLE:
        kontext = _lade_kontext_nachricht()
        if kontext:
            erste = verlauf[0] if verlauf else ""
            if "[SYSTEMKONTEXT" not in erste:
                # User: Kontext-Block, Assistant: kurze Bestaetigung
                verlauf = [kontext, "[Kontext aufgenommen.]"] + verlauf

    kompletter_verlauf = [_systemtext()] + verlauf

    # Modell wählen: letzter User-Text bestimmt schnell vs. tief
    letzter_nutzertext = ""
    for i in range(len(verlauf) - 1, -1, -1):
        if i % 2 == 0:  # user-turn (gerade Index nach system)
            letzter_nutzertext = verlauf[i]
            break
    modus_override = _get_modell_override()
    gewaehles_modell = waehle_modell(letzter_nutzertext, modus_override)

    callback = _get_stream_callback()
    if gewaehles_modell == MODELL_SCHNELL:
        modus_label = "blitz (e2b)"
    elif gewaehles_modell == MODELL_MITTEL:
        modus_label = "mittel (e4b)"
    elif gewaehles_modell == MODELL_QWEN:
        modus_label = "qwen (14b)"
    else:
        modus_label = "tief (26b)"
    if callback is not None:
        callback(f"\n[dak+gord-system | {modus_label}]\n")

    def _token_out(token: str) -> None:
        if callback is not None:
            try:
                callback(token)
            except Exception:
                pass

    def _cb(text: str) -> None:
        if callback is not None:
            try:
                callback(text)
            except Exception:
                pass

    # Erster Call: mit_tools=True, stream=False — erkennt ob Gemma Tools will
    # Kein token_callback hier — Ausgabe erfolgt entweder fake-gestreamt (kein Tool)
    # oder nach Tool-Ausführung per Folge-Call (echtes Streaming)
    _cb("[denkt…]\n")
    try:
        antwort = ollama_chat(kompletter_verlauf, token_callback=_token_out, modell=gewaehles_modell, mit_tools=True)
    except Exception as exc:
        antwort = f"[Fehler bei Modellantwort: {exc}]"
        _cb(f"\n{antwort}\n")

    _cb("\n")

    # Tool-Verarbeitungsschleife
    tool_verlauf = verlauf[:]
    tool_verlauf.append(antwort)
    finale_antwort = antwort

    for _ in range(MAX_TOOL_RUNDEN):
        _, tool_block = _verarbeite_tools(finale_antwort, callback)
        if not tool_block:
            break

        # Tool-Ergebnis als nächste User-Nachricht einspeisen
        tool_verlauf.append(f"[TOOL-ERGEBNIS]\n{tool_block}\n[/TOOL-ERGEBNIS]\nBitte fahre fort.")
        folge_verlauf = [_systemtext()] + tool_verlauf

        _cb(f"\n[dak+gord-system | {modus_label} | tool-folge]\n")

        folge_antwort = ollama_chat(folge_verlauf, token_callback=_token_out, modell=gewaehles_modell)

        _cb("\n")

        tool_verlauf.append(folge_antwort)
        finale_antwort = folge_antwort

    # Organ-Marker aus finaler Antwort verarbeiten
    if _organ_manager is not None:
        _organ_manager.verarbeite_llm_antwort(finale_antwort)

    # Jede finale Antwort ins Gesprächslog schreiben (programmatisch, kein LLM-Eingriff)
    _speichere_gespraechslog(finale_antwort, letzter_nutzertext)

    return {
        "nachrichten": verlauf + [finale_antwort]
    }


def baue_graf(checkpointer):
    graph = StateGraph(Zustand)
    graph.add_node("antworten", antworten)
    graph.set_entry_point("antworten")
    graph.add_edge("antworten", END)
    return graph.compile(checkpointer=checkpointer)
