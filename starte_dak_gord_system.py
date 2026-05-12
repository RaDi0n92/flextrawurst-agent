from __future__ import annotations
import queue as queue_mod

import os
import re
import select
import signal
import sys
import threading
import time
import subprocess
import shlex
import uuid
from pathlib import Path

os.environ.setdefault("DAK_GORD_OLLAMA_TIMEOUT", "720")

from agent.dak_gord_system.graphen.gespraechsgraf import (
    baue_graf,
    setze_stream_callback,
    setze_modell_override,
    setze_organ_manager,
)
from agent.dak_gord_system.kerne.organ_manager import OrganManager
from agent.dak_gord_system.ollama_chat import MODELL_TIEF, MODELL_SCHNELL, waehle_modell
from agent.dak_gord_system.herz.postgres_herz import postgres_kontext, schliesse_pool
from agent.dak_gord_system.schreibsystem import verarbeite_speichertrigger
from agent.dak_gord_system.dateiwerkzeuge import (
    baum,
    datei_info,
    datei_lesen,
    dateiname_suchen,
)
from agent.dak_gord_system.neugierkern import (
    VISION_SPUREN,
    WERKRAUM_SPUREN,
    pruefe_neugier_und_vision,
)
from agent.dak_gord_system.anschlusskontext import (
    aktualisiere_anschlusskontext,
    aktualisiere_fokuskontext,
    hole_anschlusskontext,
    hole_fokuskontext,
    loesche_fokuskontext,
    merke_anschlusskontext,
    setze_fokus_aus_anschlusskontext,
)
from agent.dak_gord_system.verdichtung import (
    verdichte_text,
    speichere_verdichtung,
)
from agent.dak_gord_system.kerne.beziehungsorgan import Beziehungsorgan
from agent.dak_gord_system.agentdateien import (
    aktualisiere_agentdatei,
    lese_agentdatei_kurz,
    schreibe_antwortspur,
)

KANONISCHE_FAEDEN = {
    "haupt": "hauptfaden",
    "code": "codierwerkstatt",
    "zwischen": "zwischenraum",
    "entscheidung": "entscheidungen",
}

EINGABE_PRUEF_INTERVALL = 1.0
DENKSTATUS_INTERVAL = 10
NEUGIER_PRUEF_INTERVAL = 45.0
NEUGIER_MIN_IDLE = 60.0
NEUGIER_STATUS_DATEI = "/root/werkraum/agent/dak_gord_system/spuren/neugier_status.md"
ANSCHLUSS_CHUNK_GROESSE = 1600
TEXT_ENCODINGS = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]
PROJEKTWURZEL = Path("/root/werkraum")
_INPUT_DEBUG_LOG = PROJEKTWURZEL / "agent/dak_gord_system/spuren/input_debug.log"
RESOLVER_IGNORIERTE_ORDNER = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
}
RESOLVER_MAX_TREFFER = 12


def _tool_befehl(nutzer: str) -> tuple[str, str] | None:
    text = nutzer.strip()
    klein = text.lower()

    if klein.startswith("lesen:"):
        return "lesen", text.split(":", 1)[1].strip()

    if klein.startswith("lesen "):
        return "lesen", text[6:].strip()

    if klein.startswith("dateiname:"):
        return "dateiname", text.split(":", 1)[1].strip()

    if klein.startswith("dateiname "):
        return "dateiname", text[10:].strip()

    if klein.startswith("info:"):
        return "info", text.split(":", 1)[1].strip()

    if klein.startswith("info "):
        return "info", text[5:].strip()

    if klein.startswith("baum:"):
        return "baum", text.split(":", 1)[1].strip()

    if klein.startswith("baum "):
        return "baum", text[5:].strip()

    return None


def _resolver_ignoriert(pfad: Path) -> bool:
    return any(name in pfad.parts for name in RESOLVER_IGNORIERTE_ORDNER)


def _wirkt_wie_pfad(text: str) -> bool:
    t = (text or "").strip()
    return "/" in t or t.startswith(".") or t.startswith("~")


def _sortierschluessel_fuer_treffer(suchtext: str, pfadtext: str) -> tuple[int, int, str]:
    pfad = Path(pfadtext)
    rel = str(pfad)
    try:
        rel = str(pfad.relative_to(PROJEKTWURZEL))
    except Exception:
        pass

    name = pfad.name.lower()
    stem = pfad.stem.lower()
    q = suchtext.lower().strip()

    score = 0
    if name == q:
        score += 300
    elif stem == q:
        score += 250
    elif q in name:
        score += 150

    rel_norm = "/" + rel.replace("\\", "/").lower().strip("/") + "/"

    if "/projekt/" in rel_norm:
        score += 40
    elif "/docs/vision/" in rel_norm:
        score += 30
    elif "/quellen/" in rel_norm:
        score += 20
    elif "/agent/" in rel_norm:
        score += 10

    return (-score, len(rel), rel)


def _formatiere_lesetreffermeldung(argument: str, treffer: list[str]) -> str:
    zeilen = [f"Mehrere Dateitreffer fuer: {argument}"]
    for i, pfad in enumerate(treffer[:RESOLVER_MAX_TREFFER], start=1):
        zeilen.append(f"{i}. {pfad}")
    if len(treffer) > RESOLVER_MAX_TREFFER:
        zeilen.append("... weitere Treffer ausgeblendet ...")
    zeilen.append("Bitte nenne einen genaueren Namen oder einen Pfad.")
    return "\n".join(zeilen)


def _lese_argument_auflosen(argument: str) -> tuple[str | None, str | None, str | None]:
    roh = (argument or "").strip()
    if not roh:
        return None, None, "Kein Leseargument angegeben."

    if _wirkt_wie_pfad(roh):
        kandidat = Path(roh).expanduser()
        if not kandidat.is_absolute():
            kandidat = (PROJEKTWURZEL / roh).resolve()
        else:
            kandidat = kandidat.resolve()

        if kandidat.exists() and kandidat.is_file():
            return str(kandidat), None, None

        return None, None, f"Nicht gefunden: {kandidat}"

    suchtext = roh.lower()
    exakter_name: list[str] = []
    exakter_stamm: list[str] = []
    teiltreffer: list[str] = []

    for kandidat in PROJEKTWURZEL.rglob("*"):
        if not kandidat.is_file():
            continue
        if _resolver_ignoriert(kandidat):
            continue

        name = kandidat.name.lower()
        stamm = kandidat.stem.lower()
        pfadtext = str(kandidat)

        if name == suchtext:
            exakter_name.append(pfadtext)
        elif stamm == suchtext:
            exakter_stamm.append(pfadtext)
        elif suchtext in name:
            teiltreffer.append(pfadtext)

    exakter_name = sorted(exakter_name, key=lambda p: _sortierschluessel_fuer_treffer(roh, p))
    exakter_stamm = sorted(exakter_stamm, key=lambda p: _sortierschluessel_fuer_treffer(roh, p))
    teiltreffer = sorted(teiltreffer, key=lambda p: _sortierschluessel_fuer_treffer(roh, p))

    treffer = exakter_name or exakter_stamm or teiltreffer

    if not treffer:
        return None, None, f"Keine Datei gefunden fuer: {roh}"

    if len(treffer) == 1:
        ziel = treffer[0]
        return ziel, f"Datei aufgeloest zu: {ziel}", None

    return None, None, _formatiere_lesetreffermeldung(roh, treffer)


def _ist_dateiwerkzeug_fehler(text: str) -> bool:
    t = (text or "").strip()
    fehler_prefixe = [
        "Nicht gefunden:",
        "Das ist ein Ordner, keine Datei:",
        "Das ist kein Ordner:",
        "Virtueller Systempfad wird hier nicht direkt gelesen:",
        "Baum fuer virtuellen Systempfad ist hier nicht erlaubt:",
        "Suche in virtuellem Systempfad ist hier nicht erlaubt:",
        "Datei ist nicht als Text lesbar:",
        "Lesefehler bei ",
        "Stat-Fehler bei ",
    ]
    return any(t.startswith(prefix) for prefix in fehler_prefixe)


def _ist_reiner_triggertext(nutzer: str) -> bool:
    t = nutzer.strip().lower()

    if not t:
        return False

    reine_trigger = {
        "wichtig",
        "wuchtig",
        "merk dir das",
        "speicher das in einer neuen datei",
    }

    if t in reine_trigger:
        return True

    if t.startswith("speicher das in einer neuen datei namens "):
        return True

    if t.startswith("das was du gerade gesagt hast") and "merk dir das" in t:
        return True

    if t.startswith("deine letzte antwort") and "merk dir das" in t:
        return True

    if t.startswith("dein letzter satz") and "merk dir das" in t:
        return True

    if re.search(r"speicher[e]?\s+das\s+(?:als\s+datei\s+)?in\s+/", t):
        return True

    return False


def _normalisiere_fuer_anschluss(text: str) -> str:
    t = (text or "").strip().lower()
    ersetzungen = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
        ",": " ",
        ".": " ",
        "?": " ",
        "!": " ",
        ":": " ",
        ";": " ",
        "  ": " ",
    }

    for alt, neu in ersetzungen.items():
        t = t.replace(alt, neu)

    while "  " in t:
        t = t.replace("  ", " ")

    return t


def _ist_anschlussfrage(nutzer: str) -> bool:
    t = _normalisiere_fuer_anschluss(nutzer)

    feste_muster = [
        "was weisst du darueber",
        "was weist du darueber",
        "was weisst du davon",
        "was weist du davon",
        "was haeltst du davon",
        "was haltest du davon",
        "was kannst du darueber sagen",
        "was willst du dazu sagen",
        "was willst du dazu fragen",
        "erzaehl mal etwas aus der datei",
        "erzaehl mal etwas daraus",
        "dann erzaehl mal etwas aus der datei",
        "was faellt dir daran auf",
        "was daran wichtig",
    ]

    if any(m in t for m in feste_muster):
        return True

    tiefe_muster = [
        "tiefer",
        "noch tiefer",
        "und tiefer",
        "weiter",
        "und weiter",
        "mehr daraus",
        "mehr davon",
        "mehr darueber",
        "noch mehr",
    ]

    if any(m in t for m in tiefe_muster):
        return True

    bezugsworte = [
        "darueber",
        "davon",
        "dazu",
        "darauf",
        "daraus",
        "datei",
        "auszug",
        "text",
        "davpn",
        "darubr",
        "daruber",
    ]

    verbwurzeln = [
        "weis",
        "weist",
        "halt",
        "haelt",
        "erzaehl",
        "sag",
        "frag",
        "faell",
        "wichtig",
        "mein",
        "meinst",
    ]

    if any(wort in t for wort in bezugsworte) and any(verb in t for verb in verbwurzeln):
        return True

    return False


def _drucke_prompt() -> None:
    print("\nDaniel:\n> ", end="", flush=True)


def _graf_invoke_mit_denkanzeige(graf, aktueller_faden: str, verlauf: list[str], modus_override: str | None = None):
    ergebnis: dict[str, object] = {"result": None, "error": None}
    fertig = threading.Event()
    streaming_gestartet = threading.Event()

    def _stream_token(token: str) -> None:
        if not streaming_gestartet.is_set():
            streaming_gestartet.set()
        sys.stdout.write(token)
        sys.stdout.flush()

    def _lauf() -> None:
        setze_stream_callback(_stream_token)
        setze_modell_override(modus_override)
        try:
            ergebnis["result"] = graf.invoke(
                {"nachrichten": verlauf},
                config={"configurable": {"thread_id": aktueller_faden}},
            )
        except Exception as fehler:
            ergebnis["error"] = fehler
        finally:
            setze_stream_callback(None)
            setze_modell_override(None)
            fertig.set()

    thread = threading.Thread(target=_lauf, daemon=True)
    thread.start()

    start = time.time()
    naechste_meldung = DENKSTATUS_INTERVAL

    while not fertig.is_set():
        bereit = _legacy_input_ready(1.0)

        if bereit:
            zeile = _legacy_readline(0.0)
            if zeile:
                eingabe = zeile.strip().lower()

                if eingabe == "stopp":
                    print("\n[System] Lauf fuer diese Antwort abgebrochen. Spaete Modellantwort wird verworfen.")
                    return None

                if eingabe:
                    if _queue_followup_input(zeile):
                        print("\n[System] Eingabe fuer nach diesem Lauf vorgemerkt.")
                    else:
                        print("\n[System] Eingabe waehrend Modelllauf konnte nicht vorgemerkt werden.")

        if not streaming_gestartet.is_set():
            vergangen = int(time.time() - start)
            if vergangen >= naechste_meldung:
                _drain_pending_input_during_model_run()
                print(f"[System] dak+gord-system laedt ({vergangen}s) ...", flush=True)
                naechste_meldung += DENKSTATUS_INTERVAL

    if ergebnis["error"] is not None:
        raise ergebnis["error"]  # type: ignore[misc]

    return ergebnis["result"]

def _lese_datei_chunk(datei: str | Path, offset: int, chunk_groesse: int) -> tuple[str | None, int]:
    pfad = Path(str(datei)).resolve()

    if not pfad.exists() or pfad.is_dir():
        return None, offset

    for encoding in TEXT_ENCODINGS:
        try:
            text = pfad.read_text(encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
        except Exception:
            return None, offset
    else:
        return None, offset

    if not text:
        return "(leer)", 0

    if offset >= len(text):
        offset = 0

    stueck = text[offset:offset + chunk_groesse]
    neuer_offset = offset + len(stueck)

    if neuer_offset >= len(text):
        neuer_offset = 0

    return stueck.strip(), neuer_offset


def _lese_verdichtungszusammenfassung(pfad: str | None, max_len: int = 3500) -> str:
    if not pfad:
        return ""

    text = datei_lesen(pfad, max_len=max_len)
    if _ist_dateiwerkzeug_fehler(text):
        return ""

    start = text.find("VERDICHTUNG")
    if start == -1:
        return text.strip()

    ende = text.find("ROHANTWORT:")
    if ende == -1:
        ende = len(text)

    return text[start:ende].strip()


def _versuche_verdichtung_nach_lesen(
    datei: str,
    textstueck: str,
    offset: int,
    chunk_groesse: int,
) -> tuple[bool, str, list[str], str | None, str | None]:
    if not textstueck.strip():
        return False, "Kein Text fuer Verdichtung vorhanden.", [], None, None

    try:
        ergebnis = verdichte_text(
            art="lesen-verdichtung",
            datei=datei,
            textauszug=textstueck,
            offset=offset,
            chunk_groesse=chunk_groesse,
        )
        ziel = speichere_verdichtung(ergebnis)
        agentdatei = aktualisiere_agentdatei(ergebnis)
        return True, str(ziel), ergebnis.kernsaetze, str(ziel), str(agentdatei)
    except Exception as fehler:
        return False, f"Verdichtung fehlgeschlagen: {fehler}", [], None, None


def _merke_gelesene_datei(pfadtext: str) -> tuple[bool, str, list[str], str | None, str | None]:
    start_offset = 0
    textstueck, neuer_offset = _lese_datei_chunk(
        pfadtext,
        offset=start_offset,
        chunk_groesse=ANSCHLUSS_CHUNK_GROESSE,
    )

    if not textstueck:
        return False, "Kein anschlussfaehiger Textausschnitt.", [], None, None

    merke_anschlusskontext(
        art="lesen",
        datei=pfadtext,
        textstueck=textstueck,
        spurdatei=None,
        offset=neuer_offset,
        chunk_groesse=ANSCHLUSS_CHUNK_GROESSE,
        nachfrage_tiefe=0,
    )
    setze_fokus_aus_anschlusskontext()

    return _versuche_verdichtung_nach_lesen(
        pfadtext,
        textstueck,
        offset=start_offset,
        chunk_groesse=ANSCHLUSS_CHUNK_GROESSE,
    )


def _merke_neugier_meldung(meldung: str) -> None:
    if meldung.startswith("Werkraum-Neugier: "):
        datei = meldung.split(": ", 1)[1].strip()
        textstueck, neuer_offset = _lese_datei_chunk(
            datei,
            offset=0,
            chunk_groesse=ANSCHLUSS_CHUNK_GROESSE,
        )
        if not textstueck:
            textstueck = ""
        merke_anschlusskontext(
            art="werkraum-neugier",
            datei=datei,
            textstueck=textstueck,
            spurdatei=WERKRAUM_SPUREN,
            offset=neuer_offset,
            chunk_groesse=ANSCHLUSS_CHUNK_GROESSE,
            nachfrage_tiefe=0,
        )
        return

    if meldung.startswith("Vision-Zyklus: "):
        datei = meldung.split(": ", 1)[1].strip()
        textstueck, neuer_offset = _lese_datei_chunk(
            datei,
            offset=0,
            chunk_groesse=ANSCHLUSS_CHUNK_GROESSE,
        )
        if not textstueck:
            textstueck = ""
        merke_anschlusskontext(
            art="vision-zyklus",
            datei=datei,
            textstueck=textstueck,
            spurdatei=VISION_SPUREN,
            offset=neuer_offset,
            chunk_groesse=ANSCHLUSS_CHUNK_GROESSE,
            nachfrage_tiefe=0,
        )


def _anschlussauftrag_fuer_tiefe(tiefe: int, art: str, nutzer: str) -> str:
    t = _normalisiere_fuer_anschluss(nutzer)

    if "haelt" in t or "halt" in t:
        if tiefe <= 0:
            return (
                "Antworte in genau 3 Abschnitten mit kurzen Punkten. "
                "1. DIREKT IM AUSZUG: 2 bis 3 textnahe Punkte, fast belegnah, keine Deutung. "
                "2. DARAUS VERDICHTET SICH: 2 bis 3 Muster oder Linien, aber keine Wiederholung der ersten Schicht. "
                "3. WEITERGEDACHT: 1 bis 2 Folgen, Spannungen oder Richtungen. "
                "Keine Selbstbeschreibung. Keine Einleitung. Keine Gesamtfloskel."
            )
        if tiefe == 1:
            return (
                "Gehe tiefer. Antworte in 3 Abschnitten: "
                "1. SPANNUNGEN IM AUSZUG: 2 bis 3 Punkte. "
                "2. MOEGLICHE FOLGEN: 2 bis 3 Punkte, nicht einfach Wiederholung. "
                "3. KRITISCHE FRAGEN: 1 bis 2 Punkte. "
                "Kurz, praezise, textnah."
            )
        return (
            "Gehe noch tiefer. Antworte in 3 Abschnitten: "
            "1. BRUCHSTELLEN: 2 bis 3 Punkte. "
            "2. RISIKEN ODER GEFAHREN: 2 bis 3 Punkte. "
            "3. WAS DARAUS NOCH OFFEN BLEIBT: 1 bis 2 Punkte. "
            "Kurz, textnah, ohne Floskeln."
        )

    if "tiefer" in t or "weiter" in t or "mehr" in t:
        if tiefe <= 0:
            return (
                "Antworte in genau 4 Abschnitten mit kurzen Punkten. "
                "1. DIREKT IM AUSZUG: 2 bis 4 textnahe Punkte, fast belegnah, ohne Interpretation. "
                "2. DARAUS VERDICHTET SICH: 2 bis 4 Muster, Linien oder Prinzipien, aber keine Wiederholung von Abschnitt 1. "
                "3. WEITERGEDACHT: 1 bis 3 Folgen, Spannungen oder Weltbewegungen. "
                "4. FUER CODE KOENNTE DAS HEISSEN: 1 bis 3 konkrete strukturelle Folgen wie Rollen, Rechte, Posttypen, Trigger, Zustaende, Beziehungen oder Datenfelder. "
                "Keine Selbstbeschreibung. Keine Einleitung. Keine Floskeln."
            )
        if tiefe == 1:
            return (
                "Gehe tiefer. Antworte in 4 Abschnitten: "
                "1. SPANNUNGEN: 2 bis 3 Punkte. "
                "2. BEWEGUNGEN IM TEXT: 2 bis 3 Punkte, nicht bloss paraphrasieren. "
                "3. IMPLIZITE REGELN ODER STRUKTUREN: 2 bis 3 Punkte. "
                "4. FUER CODE KOENNTE DAS HEISSEN: 1 bis 3 konkrete Folgen fuer Rollen, Rechte, Trigger, Zustaende oder Datenfelder. "
                "Kurz, praezise, textnah."
            )
        if tiefe == 2:
            return (
                "Gehe noch tiefer. Antworte in 4 Abschnitten: "
                "1. BRUCHSTELLEN ODER WIDERSPRUCHSNAEHE: 2 bis 3 Punkte. "
                "2. VERBORGENE MECHANIKEN: 2 bis 3 Punkte. "
                "3. WAS NOCH UNTERBESTIMMT IST: 2 bis 3 Punkte. "
                "4. MOEGLICHE CODEFOLGEN: 1 bis 3 konkrete strukturelle Folgen. "
                "Kurz, textnah, ohne Floskeln."
            )
        return (
            "Gehe noch tiefer. Antworte in 4 Abschnitten: "
            "1. OFFENE FRAGEN: 2 bis 3 Punkte. "
            "2. WAS IM TEXT NUR ANGEDACHT IST: 2 bis 3 Punkte. "
            "3. MOEGLICHE RICHTUNGEN DER WELT: 1 bis 3 Punkte. "
            "4. WAS FUER CODE NOCH FEHLT: 1 bis 3 konkrete Luecken in Rollen, Rechten, Zustaenden, Triggern oder Datenfeldern. "
            "Kurz, textnah, ohne Floskeln."
        )

    if art == "vision-zyklus":
        return (
            "Antworte in genau 4 Abschnitten mit kurzen Punkten. "
            "1. DIREKT IM AUSZUG: 2 bis 4 textnahe Punkte, fast belegnah, ohne Interpretation. "
            "2. DARAUS VERDICHTET SICH: 2 bis 4 Muster, Linien oder Prinzipien, aber keine Wiederholung von Abschnitt 1. "
            "3. WEITERGEDACHT: 1 bis 3 Folgen, Spannungen oder Weltbewegungen. "
            "4. FUER CODE KOENNTE DAS HEISSEN: 1 bis 3 konkrete strukturelle Folgen wie Rollen, Rechte, Posttypen, Trigger, Zustaende, Beziehungen oder Datenfelder. "
            "Keine Selbstbeschreibung. Keine Einleitung. Keine Floskeln."
        )

    return (
        "Antworte in genau 4 Abschnitten mit kurzen Punkten. "
        "1. DIREKT IM AUSZUG: 2 bis 4 textnahe Punkte, fast belegnah, ohne Interpretation. "
        "2. DARAUS VERDICHTET SICH: 2 bis 4 Muster, Linien oder Prinzipien, aber keine Wiederholung von Abschnitt 1. "
        "3. WEITERGEDACHT: 1 bis 3 Folgen, Spannungen oder Weltbewegungen. "
        "4. FUER CODE KOENNTE DAS HEISSEN: 1 bis 3 konkrete strukturelle Folgen wie Rollen, Rechte, Posttypen, Trigger, Zustaende, Beziehungen oder Datenfelder. "
        "Keine Selbstbeschreibung. Keine Einleitung. Keine Floskeln."
    )


def _hole_basis_kontext_fuer_anschluss():
    fokus = hole_fokuskontext()
    if fokus is not None:
        return fokus, "fokus"

    anschluss = hole_anschlusskontext()
    if anschluss is None:
        return None, None

    neuer_fokus = setze_fokus_aus_anschlusskontext()
    if neuer_fokus is None:
        return None, None

    return neuer_fokus, "neu_aus_anschluss"


def _nutzertext_mit_anschlusskontext(
    nutzer: str,
    verdichtungspfad: str | None,
    agentdateipfad: str | None,
) -> tuple[str, dict | None]:
    if not _ist_anschlussfrage(nutzer):
        return nutzer, None

    kontext, quelle = _hole_basis_kontext_fuer_anschluss()
    if kontext is None:
        return nutzer, None

    verwendetes_textstueck = (kontext.textstueck or "").strip()
    neuer_offset = kontext.offset
    alte_tiefe = kontext.nachfrage_tiefe
    norm_nutzer = _normalisiere_fuer_anschluss(nutzer)

    ist_tiefenfrage = any(w in norm_nutzer for w in ("tiefer", "weiter", "mehr"))

    if ist_tiefenfrage and kontext.datei:
        tieferes_textstueck, tieferer_offset = _lese_datei_chunk(
            kontext.datei,
            offset=kontext.offset,
            chunk_groesse=min(kontext.chunk_groesse, 900),
        )
        if tieferes_textstueck:
            verwendetes_textstueck = tieferes_textstueck
            neuer_offset = tieferer_offset

    if not verwendetes_textstueck and kontext.datei:
        erstes_textstueck, erster_offset = _lese_datei_chunk(
            kontext.datei,
            offset=0,
            chunk_groesse=min(kontext.chunk_groesse, 900),
        )
        if erstes_textstueck:
            verwendetes_textstueck = erstes_textstueck
            neuer_offset = erster_offset

    agentdatei_text = lese_agentdatei_kurz(agentdateipfad, max_len=2200)
    dossier_vorhanden = bool((agentdatei_text or "").strip())

    verdichtung_text = ""
    if not dossier_vorhanden:
        verdichtung_text = _lese_verdichtungszusammenfassung(verdichtungspfad)

    teile = [
        "ANSCHLUSSKONTEXT",
        f"QUELLE: {quelle}",
        f"ART: {kontext.art}",
        f"ZEIT: {kontext.zeitstempel}",
        f"DATEI: {kontext.datei}",
        f"OFFSET: {kontext.offset}",
        f"CHUNK_GROESSE: {kontext.chunk_groesse}",
    ]

    if kontext.spurdatei:
        teile.append(f"SPURDATEI: {kontext.spurdatei}")

    if dossier_vorhanden:
        teile.append(agentdatei_text)

    if ist_tiefenfrage or not dossier_vorhanden:
        if verdichtung_text:
            teile.append("VERDICHTUNG ZUR QUELLE:")
            teile.append(verdichtung_text)

        if verwendetes_textstueck:
            teile.append("KLEINER ROHTEXTAUSZUG:")
            teile.append(verwendetes_textstueck)

    teile.append("WICHTIG FUER DIE ANTWORT:")
    teile.append("Antworte primaer aus dem AGENTDOSSIER, wenn eines vorhanden ist.")
    teile.append("Nutze den Rohtext nur zur Absicherung oder fuer neue Tiefe.")
    teile.append("Nutze die Verdichtung nur dann, wenn noch kein belastbares Dossier vorhanden ist.")
    teile.append("Rekonstruiere nicht alles neu von null aus dem Rohtext.")
    teile.append("Wenn Rohtext, Verdichtung und Agentdatei auseinanderlaufen, gilt der Rohtext.")
    teile.append("Die Abschnitte muessen sich klar unterscheiden und duerfen nicht einfach dieselben Inhalte umformulieren.")
    teile.append("DIREKT IM AUSZUG = textnah, knapp, fast belegnah.")
    teile.append("DARAUS VERDICHTET SICH = Muster, Linien, Prinzipien, nicht Wiederholung.")
    teile.append("WEITERGEDACHT = Folgen, Spannungen, Richtungen.")
    teile.append("FUER CODE KOENNTE DAS HEISSEN = konkrete strukturelle Folgen fuer Rollen, Rechte, Posttypen, Trigger, Zustaende, Beziehungen oder Datenfelder.")
    teile.append("Keine Selbstbeschreibung.")
    teile.append("Keine allgemeine Rede ueber das Gesamtprojekt.")
    teile.append("Wenn das Dossier schon reicht, bleib kurz und nutze es.")
    teile.append("AUFGABE FUER DIESE ANTWORT:")
    teile.append(_anschlussauftrag_fuer_tiefe(alte_tiefe, kontext.art, nutzer))
    teile.append("DANIELS FRAGE:")
    teile.append(nutzer)

    update_plan = {
        "textstueck": verwendetes_textstueck,
        "offset": neuer_offset,
        "nachfrage_tiefe": alte_tiefe + 1,
    }

    return "\n".join(teile), update_plan




def _schreibe_neugier_status(
    idle_sekunden: float,
    meldungen: list[str],
    effektiver_input_zeitpunkt: float,
) -> None:
    from pathlib import Path
    from datetime import datetime

    pfad = Path(NEUGIER_STATUS_DATEI)
    pfad.parent.mkdir(parents=True, exist_ok=True)

    teile = [
        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] dak+gord-system",
        f"IDLE_SEKUNDEN: {idle_sekunden:.1f}",
        f"EFFEKTIVER_INPUTZEITPUNKT: {effektiver_input_zeitpunkt}",
    ]

    if meldungen:
        teile.append("ERGEBNIS: neue Meldungen")
        teile.append("MELDUNGEN:")
        for meldung in meldungen:
            teile.append(f"- {meldung}")
    else:
        teile.append("ERGEBNIS: nichts Neues faellig")

    pfad.write_text("\n".join(teile) + "\n", encoding="utf-8")


_NEUGIER_VORSCHLAG_MUSTER = [
    ("vision", "Soll ich einen Abschnitt daraus lesen und kommentieren?"),
    ("werkraum", "Soll ich die Datei oeffnen und dir zeigen was darin ist?"),
    ("code", "Soll ich den Code analysieren?"),
    ("datei", "Soll ich die Datei lesen?"),
]


def _neugier_vorschlag(meldung: str) -> str | None:
    klein = meldung.lower()
    for schluessel, vorschlag in _NEUGIER_VORSCHLAG_MUSTER:
        if schluessel in klein:
            return vorschlag
    return None


def _drucke_neugiermeldungen(meldungen: list[str], prompt_steht: bool) -> bool:
    if not meldungen:
        return prompt_steht

    if prompt_steht:
        print()
        prompt_steht = False

    for meldung in meldungen:
        print(f"[System] {meldung}")
        vorschlag = _neugier_vorschlag(meldung)
        if vorschlag:
            print(f"[dak+gord-system] {vorschlag}")

    return False




def _pruefe_periodische_neugier(
    letzter_input_zeitpunkt: float,
    naechster_neugier_check: float,
    prompt_steht: bool,
) -> tuple[float, bool]:
    jetzt = time.time()
    if jetzt < naechster_neugier_check:
        return naechster_neugier_check, prompt_steht

    idle_sekunden = jetzt - letzter_input_zeitpunkt
    effektiver_input_zeitpunkt = 0 if idle_sekunden >= NEUGIER_MIN_IDLE else letzter_input_zeitpunkt

    try:
        meldungen = pruefe_neugier_und_vision(effektiver_input_zeitpunkt)
    except Exception as fehler:
        if prompt_steht:
            print()
            prompt_steht = False
        print(f"[System] Neugierlauf fehlgeschlagen: {fehler}")
        return jetzt + NEUGIER_PRUEF_INTERVAL, prompt_steht

    _schreibe_neugier_status(idle_sekunden, meldungen, effektiver_input_zeitpunkt)

    if meldungen:
        prompt_steht = _drucke_neugiermeldungen(meldungen, prompt_steht)
    else:
        if prompt_steht:
            print()
            prompt_steht = False
        print(f"[System] Neugier-Check: nichts Neues faellig (idle={idle_sekunden:.0f}s)")

    return jetzt + NEUGIER_PRUEF_INTERVAL, prompt_steht


def _format_approval_result_lines(result: dict) -> list[str]:
    lines = [
        f"[System] TASK_ID: {result.get('task_id', '')}",
        f"[System] TOOL: {result.get('tool_name', '')}",
        f"[System] STATUS: {result.get('status', '')}",
        f"[System] APPROVAL_STATUS: {result.get('approval_status', '')}",
        f"[System] SCHRITT: {result.get('aktueller_schritt', '')}",
    ]
    fehler = result.get("fehler")
    if fehler:
        lines.append(f"[System] FEHLER: {fehler}")
    return lines


def _handle_approval_command(nutzer: str) -> tuple[bool, list[str]]:
    norm = nutzer.strip()
    lower = norm.lower()
    if not norm:
        return False, []

    try:
        from agent.dak_gord_system.graph.approval_api import list_pending_approvals, resume_approval
    except Exception as fehler:
        return False, [f"[System] Approval-Import fehlgeschlagen: {fehler}"]

    if lower in {"freigaben", "freigeben"}:
        eintraege = [x for x in list_pending_approvals() if x.get("approval_status") == "offen"]
        if not eintraege:
            return True, ["[System] Keine offenen Freigaben."]
        lines = ["[System] Offene Freigaben:"]
        for eintrag in eintraege:
            lines.append(
                f"- {eintrag.get('task_id', '')} | {eintrag.get('tool_name', '')} | {eintrag.get('status', '')} | {eintrag.get('ziel', '')}"
            )
        return True, lines

    if lower.startswith("genehmige "):
        task_id = norm.split(" ", 1)[1].strip()
        try:
            result = resume_approval(task_id, "genehmigt")
        except Exception as fehler:
            return True, [f"[System] Genehmigung fehlgeschlagen: {fehler}"]
        return True, ["[System] Freigabe genehmigt."] + _format_approval_result_lines(result)

    if lower.startswith("lehne "):
        task_id = norm.split(" ", 1)[1].strip()
        try:
            result = resume_approval(task_id, "abgelehnt")
        except Exception as fehler:
            return True, [f"[System] Ablehnung fehlgeschlagen: {fehler}"]
        return True, ["[System] Freigabe abgelehnt."] + _format_approval_result_lines(result)

    approval_like_prefixes = (
        "freigab",
        "genehmig",
        "lehn",
        "ablehn",
        "approve",
        "deny",
    )
    if lower.startswith(approval_like_prefixes):
        return True, [
            "[System] Unbekannter Freigabebefehl.",
            "[System] Verfuegbar: freigaben | freigeben | genehmige <task_id> | lehne <task_id>",
        ]

    return False, []

def _verarbeite_llm_werkzeugaufrufe(antwort: str) -> list[str]:
    """Parse LLM response for ##LESEN##, ##CODE_START##, ##SCHREIBEN## markers and execute them."""
    from agent.dak_gord_system.sandbox import fuehre_code_aus

    ausgaben: list[str] = []
    zeilen = antwort.splitlines()
    i = 0
    while i < len(zeilen):
        zeile = zeilen[i].strip()

        # ##LESEN: /pfad##
        if zeile.startswith("##LESEN:") and zeile.endswith("##"):
            pfad_roh = zeile[8:-2].strip()
            try:
                pfad = Path(pfad_roh)
                if not pfad.is_absolute():
                    pfad = (PROJEKTWURZEL / pfad_roh).resolve()
                if pfad.exists() and pfad.is_file():
                    inhalt = pfad.read_text(encoding="utf-8", errors="replace")[:3000]
                    ausgaben.append(f"[Werkzeug] GELESEN: {pfad}\n{inhalt}")
                else:
                    ausgaben.append(f"[Werkzeug] LESEN fehlgeschlagen: Datei nicht gefunden: {pfad}")
            except Exception as exc:
                ausgaben.append(f"[Werkzeug] LESEN fehlgeschlagen: {exc}")
            i += 1
            continue

        # ##CODE_START## ... ##CODE_ENDE##
        if zeile == "##CODE_START##":
            code_zeilen: list[str] = []
            i += 1
            while i < len(zeilen) and zeilen[i].strip() != "##CODE_ENDE##":
                code_zeilen.append(zeilen[i])
                i += 1
            code = "\n".join(code_zeilen)
            ergebnis = fuehre_code_aus(code)
            if ergebnis["ok"]:
                ausgaben.append(f"[Werkzeug] CODE ausgefuehrt (rc=0):\n{ergebnis['stdout']}")
            else:
                ausgaben.append(
                    f"[Werkzeug] CODE fehlgeschlagen (rc={ergebnis['returncode']}):\n"
                    f"stdout: {ergebnis['stdout']}\nstderr: {ergebnis['stderr']}"
                )
            i += 1
            continue

        # ##SCHREIBEN: /pfad## ... ##SCHREIBEN_ENDE##
        if zeile.startswith("##SCHREIBEN:") and zeile.endswith("##"):
            schreib_pfad_roh = zeile[12:-2].strip()
            inhalt_zeilen: list[str] = []
            i += 1
            while i < len(zeilen) and zeilen[i].strip() != "##SCHREIBEN_ENDE##":
                inhalt_zeilen.append(zeilen[i])
                i += 1
            inhalt = "\n".join(inhalt_zeilen)
            try:
                schreib_pfad = Path(schreib_pfad_roh)
                if not schreib_pfad.is_absolute():
                    schreib_pfad = (PROJEKTWURZEL / schreib_pfad_roh).resolve()
                schreib_pfad.parent.mkdir(parents=True, exist_ok=True)
                schreib_pfad.write_text(inhalt, encoding="utf-8")
                ausgaben.append(f"[Werkzeug] GESCHRIEBEN: {schreib_pfad} ({len(inhalt)} Zeichen)")
            except Exception as exc:
                ausgaben.append(f"[Werkzeug] SCHREIBEN fehlgeschlagen: {exc}")
            i += 1
            continue

        i += 1

    return ausgaben


def _run_tool_request_from_main(tool_name: str, tool_args: dict) -> dict:
    from agent.dak_gord_system.graph.run_tool_agent import build_tool_graph
    from agent.dak_gord_system.graph.state import new_agent_state

    task_id = f"task_{uuid.uuid4().hex[:8]}"
    thread_id = f"thread_{uuid.uuid4().hex[:8]}"

    state = new_agent_state(
        task_id=task_id,
        thread_id=thread_id,
        run_type="maintenance",
        ziel=f"Tool aus Hauptprogramm: {tool_name}",
        modus="tool",
        aktueller_schritt="check_tool_approval",
    )
    state["tool_name"] = tool_name
    state["tool_args"] = tool_args
    state["tool_aktion"] = f"tool:{tool_name}"

    graph = build_tool_graph()
    config = {"configurable": {"thread_id": thread_id}}
    return dict(graph.invoke(state, config=config))


def _format_tool_request_lines(result: dict) -> list[str]:
    lines = [
        "[System] Tool-Anfrage verarbeitet.",
        f"[System] TASK_ID: {result.get('task_id', '')}",
        f"[System] TOOL: {result.get('tool_name', '')}",
        f"[System] STATUS: {result.get('status', '')}",
        f"[System] APPROVAL_STATUS: {result.get('approval_status', '')}",
        f"[System] SCHRITT: {result.get('aktueller_schritt', '')}",
    ]

    approval_reason = result.get("approval_reason")
    if approval_reason:
        lines.append(f"[System] APPROVAL_REASON: {approval_reason}")

    approval_request_path = result.get("approval_request_path")
    if approval_request_path:
        lines.append(f"[System] APPROVAL_DATEI: {approval_request_path}")

    letzte_tool_aktionen = result.get("letzte_tool_aktionen", []) or []
    if letzte_tool_aktionen:
        last = letzte_tool_aktionen[-1]
        ergebnis = str(last.get("ergebnis", "") or "")
        if ergebnis:
            lines.append(f"[System] TOOL-ERGEBNIS: {ergebnis[:300]}")

    fehler = result.get("fehler")
    if fehler:
        lines.append(f"[System] FEHLER: {fehler}")

    return lines


def _handle_tool_request_command(nutzer: str) -> tuple[bool, list[str]]:
    norm = nutzer.strip()
    if not norm:
        return False, []

    if norm.startswith("tool-read "):
        path = norm.split(" ", 1)[1].strip()
        if not path:
            return True, ["[System] Nutzung: tool-read <pfad>"]
        try:
            result = _run_tool_request_from_main(
                "read_text_file",
                {"path": path, "max_chars": 1200},
            )
        except Exception as fehler:
            return True, [f"[System] Tool-Read fehlgeschlagen: {fehler}"]
        return True, _format_tool_request_lines(result)

    if norm.startswith("tool-shell "):
        cmd_text = norm.split(" ", 1)[1].strip()
        if not cmd_text:
            return True, ["[System] Nutzung: tool-shell <kommando>"]
        try:
            argv = shlex.split(cmd_text)
        except ValueError as fehler:
            return True, [f"[System] Shell-Parsing fehlgeschlagen: {fehler}"]
        if not argv:
            return True, ["[System] Kein Shell-Kommando erkannt."]
        try:
            result = _run_tool_request_from_main(
                "run_safe_shell",
                {"argv": argv, "cwd": "/root/werkraum", "timeout_sec": 15},
            )
        except Exception as fehler:
            return True, [f"[System] Tool-Shell fehlgeschlagen: {fehler}"]
        return True, _format_tool_request_lines(result)

    return False, []


def _evals_dir() -> Path:
    return Path("/root/werkraum/agent/dak_gord_system/spuren/evals")


def _run_eval_smoke() -> tuple[bool, list[str]]:
    cmd = [sys.executable, "-m", "agent.dak_gord_system.graph.evals.run_smoke_evals"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    lines: list[str] = []
    if result.stdout.strip():
        for line in result.stdout.splitlines():
            lines.append(f"[System] {line}")

    if result.returncode != 0:
        if result.stderr.strip():
            lines.append("[System] STDERR:")
            for line in result.stderr.splitlines():
                lines.append(f"[System] {line}")
        return False, lines or ["[System] Eval-Smoke fehlgeschlagen."]

    return True, lines or ["[System] Eval-Smoke abgeschlossen."]


def _list_eval_reports(limit: int = 10) -> list[str]:
    eval_dir = _evals_dir()
    if not eval_dir.exists():
        return ["[System] Noch kein Eval-Verzeichnis vorhanden."]

    reports = sorted(eval_dir.glob("smoke_eval_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not reports:
        return ["[System] Noch keine Eval-Reports vorhanden."]

    lines = ["[System] Letzte Eval-Reports:"]
    for pfad in reports[:limit]:
        lines.append(f"- {pfad.name}")
    return lines


def _latest_eval_report_lines(max_lines: int = 40) -> list[str]:
    eval_dir = _evals_dir()
    if not eval_dir.exists():
        return ["[System] Noch kein Eval-Verzeichnis vorhanden."]

    reports = sorted(eval_dir.glob("smoke_eval_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not reports:
        return ["[System] Noch keine Eval-Reports vorhanden."]

    latest = reports[0]
    lines = [f"[System] Letzter Eval-Report: {latest}"]
    content = latest.read_text(encoding="utf-8").splitlines()
    for line in content[:max_lines]:
        lines.append(line)
    return lines


def _handle_eval_command(nutzer: str) -> tuple[bool, list[str]]:
    norm = nutzer.strip().lower()
    if not norm:
        return False, []

    if norm == "eval-smoke":
        _, lines = _run_eval_smoke()
        return True, lines

    if norm == "evals":
        return True, _list_eval_reports()

    if norm in {"letzter-eval", "letzter eval", "latest-eval"}:
        return True, _latest_eval_report_lines()

    eval_like_prefixes = ("eval", "smoke", "latest-eval", "letzter-eval")
    if norm.startswith(eval_like_prefixes) and norm not in {"eval-smoke", "evals", "letzter-eval", "letzter eval", "latest-eval"}:
        return True, [
            "[System] Unbekannter Eval-Befehl.",
            "[System] Verfuegbar: eval-smoke | evals | letzter-eval",
        ]

    return False, []


def _handle_memory_command(nutzer: str) -> tuple[bool, list[str]]:
    norm = nutzer.strip()
    lower = norm.lower()
    if not norm:
        return False, []

    try:
        from agent.dak_gord_system.graph.memory_queries import (
            latest_events,
            filter_events_by_type,
            filter_events_by_task,
            format_event_lines,
        )
    except Exception as fehler:
        return False, [f"[System] Memory-Import fehlgeschlagen: {fehler}"]

    if lower == "events":
        return True, ["[System] Letzte Events:"] + format_event_lines(latest_events(limit=10))

    if lower == "events tool":
        return True, ["[System] Tool-Events:"] + format_event_lines(filter_events_by_type("tool_", limit=10))

    if lower == "events approval":
        return True, ["[System] Approval-Events:"] + format_event_lines(filter_events_by_type("approval_", limit=10))

    if lower == "events background":
        return True, ["[System] Background-Events:"] + format_event_lines(filter_events_by_type("background_", limit=10))

    if lower == "events eval":
        return True, ["[System] Eval-Events:"] + format_event_lines(filter_events_by_type("eval_", limit=10))

    if lower.startswith("events task "):
        task_id = norm.split(" ", 2)[2].strip()
        if not task_id:
            return True, ["[System] Nutzung: events task <task_id>"]
        return True, [f"[System] Events fuer {task_id}:"] + format_event_lines(filter_events_by_task(task_id, limit=20))

    memory_like_prefixes = ("events", "memory", "trace", "traces")
    bekannte = {"events", "events tool", "events approval", "events background", "events eval"}
    if lower.startswith(memory_like_prefixes) and lower not in bekannte and not lower.startswith("events task "):
        return True, [
            "[System] Unbekannter Memory-Befehl.",
            "[System] Verfuegbar: events | events tool | events approval | events background | events eval | events task <task_id>",
        ]

    return False, []


def _resolve_dossier_source_name(name: str) -> str | None:
    kandidat = name.strip()
    if not kandidat:
        return None

    def choose_best(raw: str) -> str | None:
        kandidaten = [x.strip() for x in str(raw).splitlines() if x.strip()]
        if not kandidaten:
            return None

        def score(p: str) -> tuple[int, int, int, int]:
            s = str(p)
            is_project = 1 if "/projekt/" in s else 0
            is_not_spuren = 1 if "/spuren/" not in s else 0
            is_not_agent = 1 if not s.endswith(".agent.md") else 0
            exists = 1 if Path(s).exists() else 0
            return (is_project, is_not_spuren, is_not_agent, exists)

        kandidaten.sort(key=score, reverse=True)
        return kandidaten[0]

    treffer = dateiname_suchen(kandidat)
    best = choose_best(treffer) if treffer else None
    if best:
        return best

    if "." not in kandidat:
        treffer = dateiname_suchen(kandidat + ".md")
        best = choose_best(treffer) if treffer else None
        if best:
            return best

    if kandidat.startswith("/"):
        return kandidat

    return None


def _handle_dossier_command(nutzer: str) -> tuple[bool, list[str]]:
    norm = nutzer.strip()
    lower = norm.lower()
    if not norm:
        return False, []

    try:
        from agent.dak_gord_system.graph.dossier_queries import (
            dossier_overview_lines,
            dossier_head_lines,
            dossier_focus_lines,
            dossier_question_lines,
        )
    except Exception as fehler:
        return False, [f"[System] Dossier-Import fehlgeschlagen: {fehler}"]

    befehle = ("dossier ", "dossier-kopf ", "dossier-fokus ", "dossier-fragen ")
    if not lower.startswith(befehle):
        return False, []

    if lower.startswith("dossier-kopf "):
        quelle_name = norm.split(" ", 1)[1].strip()
        quelle = _resolve_dossier_source_name(quelle_name)
        if not quelle:
            return True, [f"[System] Quelle nicht gefunden: {quelle_name}"]
        try:
            pfad, lines = dossier_head_lines(quelle)
        except Exception as fehler:
            return True, [f"[System] Dossier-Kopf fehlgeschlagen: {fehler}"]
        return True, [f"[System] Dossier-Kopf: {pfad}"] + (lines or ["[System] Kein Dossier-Kopf gefunden."])

    if lower.startswith("dossier-fokus "):
        quelle_name = norm.split(" ", 1)[1].strip()
        quelle = _resolve_dossier_source_name(quelle_name)
        if not quelle:
            return True, [f"[System] Quelle nicht gefunden: {quelle_name}"]
        try:
            pfad, lines = dossier_focus_lines(quelle)
        except Exception as fehler:
            return True, [f"[System] Dossier-Fokus fehlgeschlagen: {fehler}"]
        return True, [f"[System] Dossier-Fokus: {pfad}"] + (lines or ["[System] Kein Fokusabschnitt gefunden."])

    if lower.startswith("dossier-fragen "):
        quelle_name = norm.split(" ", 1)[1].strip()
        quelle = _resolve_dossier_source_name(quelle_name)
        if not quelle:
            return True, [f"[System] Quelle nicht gefunden: {quelle_name}"]
        try:
            pfad, lines = dossier_question_lines(quelle)
        except Exception as fehler:
            return True, [f"[System] Dossier-Fragen fehlgeschlagen: {fehler}"]
        return True, [f"[System] Dossier-Fragen: {pfad}"] + (lines or ["[System] Keine offenen Grundfragen gefunden."])

    if lower.startswith("dossier "):
        quelle_name = norm.split(" ", 1)[1].strip()
        quelle = _resolve_dossier_source_name(quelle_name)
        if not quelle:
            return True, [f"[System] Quelle nicht gefunden: {quelle_name}"]
        try:
            pfad, lines = dossier_overview_lines(quelle)
        except Exception as fehler:
            return True, [f"[System] Dossier fehlgeschlagen: {fehler}"]
        return True, [f"[System] Dossier: {pfad}"] + (lines or ["[System] Kein Dossierinhalt gefunden."])

    return False, []


def _normalize_single_command_arg(raw: str) -> str:
    text = str(raw).replace("\r", "\n").strip()
    if not text:
        return ""

    first = text.splitlines()[0].strip()
    lower = first.lower()

    inline_markers = [
        " dossier ",
        " dossier-kopf ",
        " dossier-fokus ",
        " dossier-fragen ",
        " events",
        " ereignisse",
        " freigaben",
        " freigeben",
        " genehmige ",
        " lehne ",
        " tool-read ",
        " tool-shell ",
        " eval-smoke",
        " evals",
        " letzter-eval",
        " kopf ",
        " fokus ",
        " fragen ",
        " lesen ",
        " dateiname ",
        " info ",
        " baum ",
        " /faden ",
    ]

    cut_positions = []
    for marker in inline_markers:
        pos = lower.find(marker)
        if pos > 0:
            cut_positions.append(pos)

    if cut_positions:
        first = first[:min(cut_positions)].strip()

    return first


def _resolve_dossier_source_name(name: str) -> str | None:
    kandidat = _normalize_single_command_arg(name)
    if not kandidat:
        return None

    def choose_best(raw: str) -> str | None:
        kandidaten = [x.strip() for x in str(raw).splitlines() if x.strip()]
        if not kandidaten:
            return None

        def score(p: str) -> tuple[int, int, int, int]:
            s = str(p)
            is_project = 1 if "/projekt/" in s else 0
            is_not_spuren = 1 if "/spuren/" not in s else 0
            is_not_agent = 1 if not s.endswith(".agent.md") else 0
            exists = 1 if Path(s).exists() else 0
            return (is_project, is_not_spuren, is_not_agent, exists)

        kandidaten.sort(key=score, reverse=True)
        return kandidaten[0]

    treffer = dateiname_suchen(kandidat)
    best = choose_best(treffer) if treffer else None
    if best:
        return best

    if "." not in kandidat:
        treffer = dateiname_suchen(kandidat + ".md")
        best = choose_best(treffer) if treffer else None
        if best:
            return best

    if kandidat.startswith("/"):
        return kandidat

    return None


def _handle_memory_command(nutzer: str) -> tuple[bool, list[str]]:
    norm = nutzer.strip()
    lower = norm.lower()
    if not norm:
        return False, []

    try:
        from agent.dak_gord_system.graph.memory_queries import (
            latest_events,
            filter_events_by_type,
            filter_events_by_task,
            format_event_lines,
        )
    except Exception as fehler:
        return False, [f"[System] Memory-Import fehlgeschlagen: {fehler}"]

    if lower in {"events", "ereignisse"}:
        return True, ["[System] Letzte Events:"] + format_event_lines(latest_events(limit=10))

    if lower in {"events tool", "ereignisse tool"}:
        return True, ["[System] Tool-Events:"] + format_event_lines(filter_events_by_type("tool_", limit=10))

    if lower in {"events approval", "ereignisse approval", "ereignisse freigaben"}:
        return True, ["[System] Approval-Events:"] + format_event_lines(filter_events_by_type("approval_", limit=10))

    if lower in {"events background", "ereignisse background"}:
        return True, ["[System] Background-Events:"] + format_event_lines(filter_events_by_type("background_", limit=10))

    if lower in {"events eval", "ereignisse eval"}:
        return True, ["[System] Eval-Events:"] + format_event_lines(filter_events_by_type("eval_", limit=10))

    if lower.startswith("events task ") or lower.startswith("ereignisse task "):
        teile = norm.split(" ", 2)
        if len(teile) < 3:
            return True, ["[System] Nutzung: events task <task_id>"]
        task_id = _normalize_single_command_arg(teile[2])
        if not task_id:
            return True, ["[System] Nutzung: events task <task_id>"]
        return True, [f"[System] Events fuer {task_id}:"] + format_event_lines(filter_events_by_task(task_id, limit=20))

    memory_like_prefixes = ("events", "ereignisse", "memory", "trace", "traces")
    bekannte = {
        "events", "ereignisse",
        "events tool", "ereignisse tool",
        "events approval", "ereignisse approval", "ereignisse freigaben",
        "events background", "ereignisse background",
        "events eval", "ereignisse eval",
    }
    if lower.startswith(memory_like_prefixes) and lower not in bekannte and not lower.startswith("events task ") and not lower.startswith("ereignisse task "):
        return True, [
            "[System] Unbekannter Memory-Befehl.",
            "[System] Verfuegbar: events | events tool | events approval | events background | events eval | events task <task_id>",
        ]

    return False, []


def _handle_dossier_command(nutzer: str) -> tuple[bool, list[str]]:
    norm = nutzer.strip()
    lower = norm.lower()
    if not norm:
        return False, []

    try:
        from agent.dak_gord_system.graph.dossier_queries import (
            dossier_overview_lines,
            dossier_head_lines,
            dossier_focus_lines,
            dossier_question_lines,
        )
    except Exception as fehler:
        return False, [f"[System] Dossier-Import fehlgeschlagen: {fehler}"]

    def _quelle_aus_befehl(prefix: str) -> str:
        rest = norm[len(prefix):].strip()
        return _normalize_single_command_arg(rest)

    if lower.startswith("dossier-kopf ") or lower.startswith("kopf "):
        prefix = "dossier-kopf " if lower.startswith("dossier-kopf ") else "kopf "
        quelle_name = _quelle_aus_befehl(prefix)
        quelle = _resolve_dossier_source_name(quelle_name)
        if not quelle:
            return True, [f"[System] Quelle nicht gefunden: {quelle_name}"]
        try:
            pfad, lines = dossier_head_lines(quelle)
        except Exception as fehler:
            return True, [f"[System] Dossier-Kopf fehlgeschlagen: {fehler}"]
        return True, [f"[System] Dossier-Kopf: {pfad}"] + (lines or ["[System] Kein Dossier-Kopf gefunden."])

    if lower.startswith("dossier-fokus ") or lower.startswith("fokus "):
        prefix = "dossier-fokus " if lower.startswith("dossier-fokus ") else "fokus "
        quelle_name = _quelle_aus_befehl(prefix)
        quelle = _resolve_dossier_source_name(quelle_name)
        if not quelle:
            return True, [f"[System] Quelle nicht gefunden: {quelle_name}"]
        try:
            pfad, lines = dossier_focus_lines(quelle)
        except Exception as fehler:
            return True, [f"[System] Dossier-Fokus fehlgeschlagen: {fehler}"]
        return True, [f"[System] Dossier-Fokus: {pfad}"] + (lines or ["[System] Kein Fokusabschnitt gefunden."])

    if lower.startswith("dossier-fragen ") or lower.startswith("fragen "):
        prefix = "dossier-fragen " if lower.startswith("dossier-fragen ") else "fragen "
        quelle_name = _quelle_aus_befehl(prefix)
        quelle = _resolve_dossier_source_name(quelle_name)
        if not quelle:
            return True, [f"[System] Quelle nicht gefunden: {quelle_name}"]
        try:
            pfad, lines = dossier_question_lines(quelle)
        except Exception as fehler:
            return True, [f"[System] Dossier-Fragen fehlgeschlagen: {fehler}"]
        return True, [f"[System] Dossier-Fragen: {pfad}"] + (lines or ["[System] Keine offenen Grundfragen gefunden."])

    if lower.startswith("dossier "):
        quelle_name = _quelle_aus_befehl("dossier ")
        quelle = _resolve_dossier_source_name(quelle_name)
        if not quelle:
            return True, [f"[System] Quelle nicht gefunden: {quelle_name}"]
        try:
            pfad, lines = dossier_overview_lines(quelle)
        except Exception as fehler:
            return True, [f"[System] Dossier fehlgeschlagen: {fehler}"]
        return True, [f"[System] Dossier: {pfad}"] + (lines or ["[System] Kein Dossierinhalt gefunden."])

    return False, []





_SYSTEM_COMMAND_QUEUE: list[str] = []
_INPUT_QUEUE: queue_mod.Queue[str | None] = queue_mod.Queue()
_INPUT_READER_STARTED = False
_INPUT_READER_LOCK = threading.Lock()


def _stdin_reader_loop() -> None:
    while True:
        line = sys.stdin.readline()
        if line == "":
            try:
                _debug_input_event("stdin_eof", "")
                _INPUT_QUEUE.put_nowait(None)
            except Exception:
                pass
            break
        _INPUT_QUEUE.put(line.rstrip("\n"))


def _ensure_input_reader_started() -> None:
    global _INPUT_READER_STARTED
    with _INPUT_READER_LOCK:
        if _INPUT_READER_STARTED:
            return
        thread = threading.Thread(
            target=_stdin_reader_loop,
            name="dak-stdin-reader",
            daemon=True,
        )
        thread.start()
        _INPUT_READER_STARTED = True


def _queue_system_command(nutzer: str) -> bool:
    raw = str(nutzer).strip()
    if not raw:
        return False

    lines = [x.strip() for x in raw.replace("\r", "\n").split("\n") if x.strip()]
    if not lines:
        return False

    if not all(_is_supported_batch_command(line) for line in lines):
        return False

    vorher = len(_SYSTEM_COMMAND_QUEUE)
    _SYSTEM_COMMAND_QUEUE.extend(lines)
    nachher = len(_SYSTEM_COMMAND_QUEUE)

    _debug_input_event("system_queue_put_many", f"vorher={vorher} nachher={nachher} lines={lines}")
    print(f"[System] Befehl vorgemerkt. Queue={nachher} (vorher={vorher}, neu={len(lines)})")
    for line in lines:
        print(f"[System] Vorgemerkt: {line}")
    return True



def _queue_followup_input(nutzer: str) -> bool:
    raw = str(nutzer).strip()
    if not raw:
        return False

    lines = [x.strip() for x in raw.replace("\r", "\n").split("\n") if x.strip()]
    if not lines:
        return False

    vorher = len(_SYSTEM_COMMAND_QUEUE)
    _SYSTEM_COMMAND_QUEUE.extend(lines)
    nachher = len(_SYSTEM_COMMAND_QUEUE)

    _debug_input_event("followup_queue_put_many", f"vorher={vorher} nachher={nachher} lines={lines}")
    print(f"[System] Folgeeingabe vorgemerkt. Queue={nachher} (vorher={vorher}, neu={len(lines)})")
    for line in lines:
        print(f"[System] Vorgemerkt: {line}")
    return True

def _pop_next_system_command() -> str | None:
    if not _SYSTEM_COMMAND_QUEUE:
        return None

    befehl = _SYSTEM_COMMAND_QUEUE.pop(0)
    _debug_input_event("system_queue_pop", befehl)
    print(f"[System] Hole Befehl aus Queue: {befehl}")
    print(f"[System] Queue verbleibend: {len(_SYSTEM_COMMAND_QUEUE)}")
    return befehl


def _take_next_raw_input(timeout: float) -> str | None:
    queued = _pop_next_system_command()
    if queued is not None:
        _debug_input_event("take_next_raw_input.from_system_queue", queued)
        return queued

    try:
        item = _INPUT_QUEUE.get(timeout=timeout)
    except queue_mod.Empty:
        _debug_input_event("take_next_raw_input.timeout", "")
        return None

    if item is None:
        _debug_input_event("take_next_raw_input.eof", "")
        return ""

    wert = str(item).strip()
    _debug_input_event("take_next_raw_input.from_input_queue", wert)
    return wert



def _drain_pending_input_during_model_run() -> None:
    while True:
        try:
            item = _INPUT_QUEUE.get_nowait()
        except queue_mod.Empty:
            break

        if item is None:
            break

        nutzer = str(item).strip()
        _debug_input_event("drain.model_run.seen", nutzer)

        if not nutzer:
            continue

        if nutzer.lower() == "stopp":
            _debug_input_event("drain.model_run.stop", nutzer)
            print("[System] Stopp angefordert (noch nicht live verdrahtet).")
            continue

        if _queue_followup_input(nutzer):
            _debug_input_event("drain.model_run.queued", nutzer)
            print("[System] Folgeeingabe aus Input-Queue vorgemerkt.")
        else:
            _debug_input_event("drain.model_run.ignored", nutzer)
            print("[System] Eingabe waehrend Modelllauf empfangen, aber nicht vorgemerkt.")

def _debug_input_event(kind: str, detail: str = "") -> None:
    try:
        _INPUT_DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
        detail_clean = str(detail).replace("\r", "\\r").replace("\n", "\\n")
        with _INPUT_DEBUG_LOG.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {kind} | {detail_clean}\n")
    except Exception:
        pass

def _is_supported_batch_command(line: str) -> bool:
    lower = line.strip().lower()
    if not lower:
        return False

    prefixes = (
        "dossier ",
        "dossier-kopf ",
        "dossier-fokus ",
        "dossier-fragen ",
        "kopf ",
        "fokus ",
        "fragen ",
        "events",
        "ereignisse",
        "freigaben",
        "freigeben",
        "genehmige ",
        "lehne ",
        "eval-smoke",
        "evals",
        "letzter-eval",
        "latest-eval",
        "tool-read ",
        "tool-shell ",
    )
    return lower.startswith(prefixes)


def _handle_batch_system_commands(nutzer: str) -> tuple[bool, list[str]]:
    raw_lines = [x.strip() for x in nutzer.replace("\r", "\n").split("\n") if x.strip()]
    if len(raw_lines) <= 1:
        return False, []

    if not all(_is_supported_batch_command(line) for line in raw_lines):
        return False, []

    out: list[str] = []

    for line in raw_lines:
        out.append(f"[System] Batch-Befehl: {line}")
        handled, lines = _dispatch_single_system_command(line)
        if handled:
            if lines:
                out.extend(lines)
        else:
            out.append(f"[System] Batch konnte Befehl nicht verarbeiten: {line}")

    return True, out



_LEGACY_INPUT_PUSHBACK: list[str] = []


def _legacy_input_ready(timeout: float) -> bool:
    if _LEGACY_INPUT_PUSHBACK:
        return True

    try:
        item = _INPUT_QUEUE.get(timeout=timeout)
    except queue_mod.Empty:
        return False

    if item is None:
        _LEGACY_INPUT_PUSHBACK.append("")
        return True

    _LEGACY_INPUT_PUSHBACK.append(str(item).strip())
    return True


def _legacy_readline(timeout: float = 0.0) -> str:
    if _LEGACY_INPUT_PUSHBACK:
        item = _LEGACY_INPUT_PUSHBACK.pop(0)
    else:
        try:
            item = _INPUT_QUEUE.get(timeout=timeout)
        except queue_mod.Empty:
            return ""

        if item is None:
            return ""

        item = str(item).strip()

    if item == "":
        return ""
    return item + "\n"

def _handle_queue_command(nutzer: str) -> tuple[bool, list[str]]:
    lower = nutzer.strip().lower()
    if lower not in {"queue", "warteschlange"}:
        return False, []

    if not _SYSTEM_COMMAND_QUEUE:
        return True, ["[System] Queue ist leer."]

    lines = [f"[System] Queue-Laenge: {len(_SYSTEM_COMMAND_QUEUE)}"]
    for idx, item in enumerate(_SYSTEM_COMMAND_QUEUE[:20], start=1):
        lines.append(f"{idx}. {item}")
    if len(_SYSTEM_COMMAND_QUEUE) > 20:
        lines.append(f"[System] ... weitere {len(_SYSTEM_COMMAND_QUEUE) - 20} Eintraege")
    return True, lines

def _print_system_lines(lines: list[str]) -> None:
    if not lines:
        return
    for line in lines:
        print(line)


def _dispatch_single_system_command(nutzer: str) -> tuple[bool, list[str]]:
    handlers = [
        _handle_queue_command,
        _handle_approval_command,
        _handle_eval_command,
        _handle_memory_command,
        _handle_dossier_command,
        _handle_tool_request_command,
    ]

    for handler in handlers:
        handled, lines = handler(nutzer)
        if handled:
            _debug_input_event("dispatch.system.handled", f"handler={handler.__name__} input={nutzer}")
            return True, lines

    return False, []


def _dispatch_system_command(nutzer: str) -> tuple[bool, list[str]]:
    handled, lines = _handle_batch_system_commands(nutzer)
    if handled:
        return True, lines

    return _dispatch_single_system_command(nutzer)


def main() -> None:
    _ensure_input_reader_started()
    aktueller_faden = "hauptfaden"
    letzter_input_zeitpunkt = time.time()
    naechster_neugier_check = time.time()

    letzte_dak_antworten = {
        "hauptfaden": "",
        "codierwerkstatt": "",
        "zwischenraum": "",
        "entscheidungen": "",
    }

    letzte_relevante_daniel_aussagen = {
        "hauptfaden": "",
        "codierwerkstatt": "",
        "zwischenraum": "",
        "entscheidungen": "",
    }

    def _sigterm_handler(signum, frame):
        schliesse_pool()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _sigterm_handler)

    beziehungsorgan = Beziehungsorgan()
    organ_manager = OrganManager()
    organ_manager.laden()
    setze_organ_manager(organ_manager)

    verlauf_pro_faden = {
        "hauptfaden": [],
        "codierwerkstatt": [],
        "zwischenraum": [],
        "entscheidungen": [],
    }

    letzte_verdichtungen = {
        "hauptfaden": "",
        "codierwerkstatt": "",
        "zwischenraum": "",
        "entscheidungen": "",
    }

    letzte_agentdateien = {
        "hauptfaden": "",
        "codierwerkstatt": "",
        "zwischenraum": "",
        "entscheidungen": "",
    }

    aktueller_modus: str | None = None  # None = Auto, "schnell", "tief"

    with postgres_kontext() as checkpointer:
        checkpointer.setup()
        graf = baue_graf(checkpointer)

        # Modell vorladen damit erster Dialog sofort antwortet
        print("[System] Modell wird geladen ...", flush=True)
        try:
            from agent.dak_gord_system.ollama_chat import ollama_chat as _warmup_chat
            _warmup_chat(["Du bist bereit.", "bereit"])
            print("[System] Modell geladen.", flush=True)
        except Exception:
            print("[System] Modell-Warmup fehlgeschlagen (nicht kritisch).", flush=True)

        print("dak+gord-system laeuft. Zum Beenden: ende")
        print("Faden wechseln mit: /faden haupt | /faden code | /faden zwischen | /faden entscheidung")
        print("Dateibefehle: lesen <pfad> | dateiname <muster> | info <pfad> | baum <pfad>")
        print(
            "Waehren eines laufenden Modelllaufs kannst du 'stopp' tippen.\n"
            "Modell: /schnell (e2b, blitz) | /mittel (e4b, Code) | /tief (26b, Vision) | /auto (automatisch) | /modus (zeigen)\n"
            "  oder Prefix: 'schnell: ...' | 'mittel: schreib ...' | 'tief: was bedeutet ...'\n"
            "Freigaben: freigaben | genehmige <task_id> | lehne <task_id>\n"
            "Tools: tool-read <pfad> | tool-shell <kommando>\n"
            "Evals: eval-smoke | evals | letzter-eval\n"
            "Memory: events | events tool | events approval | events background | events eval | events task <task_id>\n"
            "Dossiers: dossier <quelle> | dossier-kopf <quelle> | dossier-fokus <quelle> | dossier-fragen <quelle>\n"
            "Queue: queue | warteschlange"
        )

        prompt_steht = False

        while True:
            if not prompt_steht:
                _drucke_prompt()
                prompt_steht = True

            naechster_neugier_check, prompt_steht = _pruefe_periodische_neugier(
                letzter_input_zeitpunkt,
                naechster_neugier_check,
                prompt_steht,
            )

            nutzer = _take_next_raw_input(EINGABE_PRUEF_INTERVALL)

            if nutzer is None:
                try:
                    meldungen = pruefe_neugier_und_vision(letzter_input_zeitpunkt)
                except Exception as fehler:
                    print(f"\n[System] Neugierlauf fehlgeschlagen: {fehler}")
                    prompt_steht = False
                    continue

                if meldungen:
                    print()
                    for meldung in meldungen:
                        print(f"[System] {meldung}")
                        _merke_neugier_meldung(meldung)
                    prompt_steht = False
                continue

            rohe_zeile = nutzer + "\n"
            prompt_steht = False

            if rohe_zeile == "":
                print("\ndak+gord-system beendet.")
                break

            nutzer = rohe_zeile.strip()
            if not nutzer:
                continue

            letzter_input_zeitpunkt = time.time()

            if nutzer.lower() == "stopp":
                print("\n[System] Gerade laeuft kein Modelllauf.")
                continue

            handled, system_lines = _dispatch_system_command(nutzer)
            if handled:
                _print_system_lines(system_lines)
                prompt_steht = False
                continue

            _debug_input_event("dispatch.to_model", nutzer)

            if nutzer.lower() == "ende":
                print("\ndak+gord-system beendet.")
                break

            if nutzer.startswith("/faden"):
                loesche_fokuskontext()
                teile = nutzer.split()
                if len(teile) >= 2:
                    name = teile[1].lower()
                    mapping = {
                        "haupt": "hauptfaden",
                        "code": "codierwerkstatt",
                        "zwischen": "zwischenraum",
                        "entscheidung": "entscheidungen",
                    }
                    aktueller_faden = mapping.get(name, "hauptfaden")
                    print(f"\n[System] Faden gewechselt zu: {aktueller_faden}")
                continue

            tool_befehl = _tool_befehl(nutzer)
            if tool_befehl is not None:
                loesche_fokuskontext()
                tool_name, argument = tool_befehl

                verdichtungs_hinweis = None
                kernhinweise: list[str] = []

                aufloesungs_hinweis = None

                if tool_name == "lesen":
                    zielpfad, aufloesung_hinweis, aufloesungs_fehler = _lese_argument_auflosen(argument)
                    if zielpfad is None:
                        direkte_toolantwort = aufloesungs_fehler or f"Keine Datei gefunden fuer: {argument}"
                    else:
                        direkte_toolantwort = datei_lesen(zielpfad)
                        if not _ist_dateiwerkzeug_fehler(direkte_toolantwort):
                            ok, info, kernhinweise, verdichtungspfad, agentdateipfad = _merke_gelesene_datei(zielpfad)
                            if ok:
                                verdichtungs_hinweis = info
                                letzte_verdichtungen[aktueller_faden] = verdichtungspfad or ""
                                letzte_agentdateien[aktueller_faden] = agentdateipfad or ""
                            else:
                                verdichtungs_hinweis = f"(keine Verdichtung) {info}"
                                letzte_verdichtungen[aktueller_faden] = ""
                                letzte_agentdateien[aktueller_faden] = ""
                elif tool_name == "dateiname":
                    direkte_toolantwort = dateiname_suchen(argument)
                elif tool_name == "info":
                    direkte_toolantwort = datei_info(argument)
                elif tool_name == "baum":
                    direkte_toolantwort = baum(argument)
                else:
                    direkte_toolantwort = "Unbekannter Toolbefehl."

                letzte_dak_antworten[aktueller_faden] = direkte_toolantwort

                if aufloesung_hinweis:
                    print("\n[System]")
                    print(aufloesung_hinweis)

                print("\n[dak+gord-system]")
                print(direkte_toolantwort)

                if verdichtungs_hinweis is not None:
                    print("\n[System] Erste Verdichtung:")
                    print(verdichtungs_hinweis)

                    agentdatei_hinweis = letzte_agentdateien.get(aktueller_faden, "")
                    if agentdatei_hinweis:
                        print("\n[System] Agentdatei:")
                        print(agentdatei_hinweis)

                    if kernhinweise:
                        print("\n[System] 5 Kernsaetze:")
                        for i, punkt in enumerate(kernhinweise[:5], start=1):
                            print(f"{i}. {punkt}")

                continue

            ist_anschluss = _ist_anschlussfrage(nutzer)
            if not ist_anschluss:
                loesche_fokuskontext()

            gespeicherte_pfade = verarbeite_speichertrigger(
                nutzer_text=nutzer,
                letzte_antwort_von_dak=letzte_dak_antworten.get(aktueller_faden, ""),
                letzte_relevante_aussage_von_daniel=letzte_relevante_daniel_aussagen.get(
                    aktueller_faden, ""
                ),
            )

            if gespeicherte_pfade:
                print("\n[System] Gespeichert in:")
                for pfad in gespeicherte_pfade:
                    print(f"- {pfad}")

            if not _ist_reiner_triggertext(nutzer):
                letzte_relevante_daniel_aussagen[aktueller_faden] = nutzer

            # Modus-Befehle und Prefixe auswerten
            nutzer_bereinigt = nutzer
            einmal_modus: str | None = None

            norm_nutzer = nutzer.strip().lower()
            if norm_nutzer in ("/schnell", "schnell", "/fast"):
                aktueller_modus = "schnell"
                print(f"[System] Modus: SCHNELL ({MODELL_SCHNELL})")
                continue
            elif norm_nutzer in ("/tief", "tief", "/deep"):
                aktueller_modus = "tief"
                print(f"[System] Modus: TIEF ({MODELL_TIEF})")
                continue
            elif norm_nutzer in ("/auto", "auto"):
                aktueller_modus = None
                print("[System] Modus: AUTO (Modell wird per Inhalt gewaehlt)")
                continue
            elif norm_nutzer in ("/modus", "modus", "/modell", "modell"):
                if aktueller_modus:
                    print(f"[System] Aktueller Modus: {aktueller_modus.upper()}")
                else:
                    erkannt = waehle_modell(nutzer)
                    print(f"[System] Aktueller Modus: AUTO — naechste Antwort waere: {erkannt}")
                continue
            elif norm_nutzer.startswith("schnell:"):
                nutzer_bereinigt = nutzer[8:].strip()
                einmal_modus = "schnell"
            elif norm_nutzer.startswith("tief:"):
                nutzer_bereinigt = nutzer[5:].strip()
                einmal_modus = "tief"

            verwendeter_modus = einmal_modus or aktueller_modus

            nutzer_fuer_kontext, anschluss_update_plan = _nutzertext_mit_anschlusskontext(
                nutzer_bereinigt,
                letzte_verdichtungen.get(aktueller_faden, ""),
                letzte_agentdateien.get(aktueller_faden, ""),
            )

            beziehungsorgan.lese_hinweis(nutzer_bereinigt)

            verlauf = list(verlauf_pro_faden.get(aktueller_faden, []))
            verlauf.append(nutzer_fuer_kontext)

            try:
                result = _graf_invoke_mit_denkanzeige(graf, aktueller_faden, verlauf, modus_override=verwendeter_modus)
            except Exception as fehler:
                fehlermeldung = (
                    "Der Modelllauf ist gerade zu langsam, haengen geblieben oder ungueltig beantwortet worden. "
                    "Die Schleife bleibt aber an. "
                    f"Fehler: {fehler}"
                )
                letzte_dak_antworten[aktueller_faden] = fehlermeldung
                print("\n[System]")
                print(fehlermeldung)
                continue

            if result is None:
                continue

            neue_nachrichten = result["nachrichten"]
            verlauf_pro_faden[aktueller_faden] = neue_nachrichten
            antwort = neue_nachrichten[-1]

            # Feedback-Loop: LLM-Antwort zurück ins Beziehungsorgan
            beziehungsorgan.lese_antwort_hinweis(antwort)

            # --- Agentic Loop: Tool-Ergebnisse zurueck in LLM ---
            MAX_WERKZEUG_ITERATIONEN = 5
            for _iteration in range(MAX_WERKZEUG_ITERATIONEN):
                werkzeug_ausgaben = _verarbeite_llm_werkzeugaufrufe(antwort)
                if not werkzeug_ausgaben:
                    break
                print("\n[System] Werkzeuge werden ausgefuehrt...")
                for ausgabe in werkzeug_ausgaben:
                    print(ausgabe)
                tool_rueckmeldung = (
                    "[WERKZEUG-ERGEBNISSE]\n"
                    + "\n---\n".join(werkzeug_ausgaben)
                    + "\n[/WERKZEUG-ERGEBNISSE]\n"
                    "Fahre fort. Wenn du fertig bist, antworte ohne weitere Werkzeugaufrufe."
                )
                aktueller_verlauf = list(verlauf_pro_faden.get(aktueller_faden, []))
                aktueller_verlauf.append(antwort)
                aktueller_verlauf.append(tool_rueckmeldung)
                print(f"\n[System] Agent denkt weiter (Iteration {_iteration + 1})...")
                folge_result = _graf_invoke_mit_denkanzeige(graf, aktueller_faden, aktueller_verlauf)
                if folge_result is None:
                    break
                folge_nachrichten = folge_result["nachrichten"]
                verlauf_pro_faden[aktueller_faden] = folge_nachrichten
                antwort = folge_nachrichten[-1]
            # --- Ende Agentic Loop ---

            letzte_dak_antworten[aktueller_faden] = antwort

            if anschluss_update_plan is not None:
                aktualisiere_fokuskontext(
                    textstueck=anschluss_update_plan["textstueck"],
                    offset=anschluss_update_plan["offset"],
                    nachfrage_tiefe=anschluss_update_plan["nachfrage_tiefe"],
                )
                aktualisiere_anschlusskontext(
                    textstueck=anschluss_update_plan["textstueck"],
                    offset=anschluss_update_plan["offset"],
                    nachfrage_tiefe=anschluss_update_plan["nachfrage_tiefe"],
                )

                agentdateipfad = letzte_agentdateien.get(aktueller_faden, "")
                quellpfad = ""
                fokus = hole_fokuskontext()
                if fokus is not None and getattr(fokus, "datei", ""):
                    quellpfad = fokus.datei
                else:
                    anschluss = hole_anschlusskontext()
                    if anschluss is not None and getattr(anschluss, "datei", ""):
                        quellpfad = anschluss.datei

                if agentdateipfad and quellpfad:
                    try:
                        schreibe_antwortspur(
                            agentdateipfad=agentdateipfad,
                            quellpfad=quellpfad,
                            frage=nutzer,
                            antwort=antwort,
                            art="anschlussantwort",
                        )
                    except Exception as fehler:
                        print("\n[System] Antwortspur konnte nicht in Agentdatei geschrieben werden:")
                        print(fehler)

            # Antwort wurde bereits live gestreamt — kein nochmaliges Ausgeben noetig


if __name__ == "__main__":
    main()
