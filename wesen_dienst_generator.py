#!/usr/bin/env python3
"""
wesen_dienst_generator.py — erzeugt aus einer wesen_eigene_dienste-Zeile ein echtes,
eigenstaendiges Python-Skript (in wesen_eigene_skripte/) + eine systemd-Unit-Datei.
Das generierte Skript kopiert KEINE Logik aus codewesen_agent.py, sondern importiert
dessen Bausteine (agentic_loop, fuehre_aktion_aus, setup_log, load_token,
get_tags_cached, BASE) — ein Bugfix/eine Verbesserung dort wirkt damit automatisch
auch in jedem generierten Dienst.

erzeuge() schreibt nur Dateien + macht daemon-reload. Start/Stop/Enable sind
bewusst getrennte Funktionen (analog zum Bestaetigungs-Muster in flarumstyler:
Erzeugen ist ungefaehrlich, Start eines neuen Dauerprozesses nicht).
"""

import re
import subprocess
from pathlib import Path

import wesen_eigene_dienste as wed

SKRIPT_VERZEICHNIS = Path("/root/werkraum/wesen_eigene_skripte")
UNIT_VERZEICHNIS = Path("/etc/systemd/system")
_NAME_MUSTER = re.compile(r"^[a-zA-Z0-9_.-]+$")


def _pruefe_dienst_name(dienst_name: str) -> None:
    """dienst_name fliesst in Dateipfade + systemctl-Aufrufe ein — vor dem
    Schreiben/Ausfuehren immer gegen ein sicheres Zeichenset pruefen."""
    if not _NAME_MUSTER.match(dienst_name):
        raise ValueError(f"Unsicherer dienst_name: {dienst_name!r} (nur a-z, A-Z, 0-9, _, ., - erlaubt)")


def _skript_inhalt(row: dict) -> str:
    dienst_name = row["dienst_name"]
    wesen = row["wesen"]
    return f'''#!/usr/bin/env python3
"""
AUTO-GENERIERT von wesen_dienst_generator.py — NICHT VON HAND BEARBEITEN.
Aenderungen an Takt/Verhalten/Ziel bitte in der Tabelle wesen_eigene_dienste
(ueber flarumstyler) vornehmen, danach den Dienst per Regenerieren neu schreiben
und neu starten lassen (dieses Skript liest Takt/Verhalten/Ziel nur beim Start,
bzw. bei jedem DB-Reload vor einem Zyklus -- siehe _versuche_zyklus()).

Wesen-eigener Rhythmus: {row["anzeige_name"]!r}, Zuhause bei {wesen}.
dienst_name: {dienst_name}

Baukasten v2 (2026-07-07, siehe _claude/konzepte/2026-07-07_wesen_dienst_baukasten_v2.md):
Phase 1 (Grundfelder, Ziel-Varianten, eigene Felder, Takt-Liste, feste Uhrzeiten,
Pausenzeiten, Passiv-Modus) + Phase 2 (Multi-Wesen-Plaetze mit Rollen, Zustands-
abhaengigkeit, Verkettung, Trockenlauf, Verlauf-Log). Alles lebt in der Spalte meta
(JSONB) -- Grundgesetz 1: neue Faehigkeiten erweitern, nicht den Kern umbauen. Ist
meta leer/alt (Dienst vor Baukasten-v2 angelegt), verhaelt sich dieses Skript exakt
wie die Vorgaenger-Version: ein Takt, ein Wesen (die wesen-Spalte), Intervall-Loop,
keine Bedingungen.
"""
import datetime
import json
import logging
import os
import random
import re
import sys
import time

sys.path.insert(0, "/root/werkraum")
import codewesen_agent as ca
import codewesen_container as cc
import gedaechtnis as gd
import llm_scheduler
import psycopg2
import wesen_eigene_dienste as wed

DIENST_NAME = {dienst_name!r}
WESEN = {wesen!r}

_OPERATOREN = {{"gt": lambda a, b: a > b, "lt": lambda a, b: a < b, "eq": lambda a, b: a == b}}


def _setup_log() -> logging.Logger:
    """Eigener Log-Ordner statt ca.setup_log() -- die teilt sich reaktion.log mit dem
    Haupt-Agent-Prozess des Wesens und erwartet einen bereits existierenden
    BASE/<wesen>-Ordner, kein beliebiges Label."""
    log_dir = ca.BASE / WESEN / "eigene_dienste" / DIENST_NAME
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(DIENST_NAME)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(str(log_dir / "betrieb.log"))
        handler.setFormatter(logging.Formatter(f"%(asctime)s [{{DIENST_NAME}}] %(levelname)s %(message)s"))
        logger.addHandler(handler)
        logger.addHandler(logging.StreamHandler())
    return logger


def _vault_speichern(wesen: str, inhalt: str, log):
    """Vault-Eintrag landet im Raum des AGIERENDEN Wesens (bei Multi-Wesen-Plaetzen
    kann das ein anderes sein als das Zuhause-Wesen des Dienstes) -- eigener Gedanke,
    eigener Ort."""
    vault_dir = ca.BASE / wesen / "eigene_dienste" / DIENST_NAME
    vault_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d_%H-%M")
    (vault_dir / f"{{ts}}.md").write_text(
        f"<!-- autor: {{wesen}} | dienst: {{DIENST_NAME}} | datum: {{ts}} UTC -->\\n\\n{{inhalt}}\\n",
        encoding="utf-8",
    )
    log.info("[%s][%s] Vault-Eintrag gespeichert: %s.md", DIENST_NAME, wesen, ts)


def _alle_plaetze(row: dict) -> list:
    """Phase 2: 1-7 Wesen-Plaetze pro Dienst (siehe Konzept). Leer/alt (Phase 1) =
    genau ein Platz, das Wesen aus der wesen-Spalte, fest -- unveraendertes Verhalten."""
    plaetze = _meta(row).get("wesen_plaetze") or []
    if not plaetze:
        return [{{"modus": "fest", "wesen": WESEN}}]
    return plaetze


def _reihenfolge(plaetze: list, modus: str) -> list:
    if modus == "zufaellig":
        kopie = list(plaetze)
        random.shuffle(kopie)
        return kopie
    return plaetze


def _resolve_wesen(platz: dict) -> str:
    """'zufall' zieht bei JEDEM Zyklus neu -- leerer Pool = alle 7 echten Codewesen
    (dieselbe Liste wie ca.CODEWESEN_NAMEN, keine zweite Quelle der Wahrheit)."""
    if platz.get("modus") == "zufall":
        pool = platz.get("zufallsPool") or list(ca.CODEWESEN_NAMEN)
        return random.choice(pool)
    return platz.get("wesen") or WESEN


def _platz_kontext(platz: dict) -> str:
    """Rolle/Rollenbeschreibung/eigenes Verhalten pro Platz fliessen zusaetzlich zum
    Dienst-weiten Auftrag in den Kontext -- Theaterregie, nicht Konfiguration (siehe
    Konzept: 'Tiefer eingetaucht')."""
    teile = []
    if platz.get("rolle"):
        zeile = f"Deine Rolle in diesem Zyklus: {{platz['rolle']}}"
        if platz.get("rollenbeschreibung"):
            zeile += f" -- {{platz['rollenbeschreibung']}}"
        teile.append(zeile)
    if platz.get("verhalten"):
        teile.append(platz["verhalten"])
    if not teile:
        return ""
    return "\\n\\n" + "\\n".join(teile)


def _zustand_erfuellt(bedingung, wesen: str, log) -> bool:
    """Zustandsabhaengigkeit (optional, Phase 2): reine Read-Only-Abfrage gegen die
    echten, bereits laufenden Systeme (entity_slots.status aus dem Schlaf-System,
    cyberlinge.energie aus dem Cyberling-Decay) -- KEINE Aenderung an entity_takt.py
    oder cyberling_daemon.py, nur lesender Zugriff auf dieselbe Postgres-DB. Bei jedem
    DB-Problem best-effort: nicht blockieren, lieber einen Zyklus zu viel als das
    Wesen grundlos verstummen zu lassen."""
    if not bedingung:
        return True
    try:
        conn = psycopg2.connect(os.environ.get("FLEXTRAWURST_DB_URI", ""))
        try:
            with conn.cursor() as cur:
                if bedingung.get("schlafStatus"):
                    cur.execute("SELECT status FROM entity_slots WHERE entity_id = %s", (wesen,))
                    r = cur.fetchone()
                    ist = r[0] if r else None
                    erwartet = "schläft" if bedingung["schlafStatus"] == "schlafend" else "bereit"
                    if ist != erwartet:
                        return False
                if bedingung.get("minEnergie") is not None:
                    cur.execute("SELECT energie FROM cyberlinge WHERE entity_id = %s", (wesen,))
                    r = cur.fetchone()
                    energie = float(r[0]) if r and r[0] is not None else 0.0
                    if energie < float(bedingung["minEnergie"]):
                        return False
        finally:
            conn.close()
    except Exception as e:
        log.warning("Zustandsbedingung fuer '%s' nicht pruefbar (%s) -- werte als erfuellt", wesen, e)
        return True
    return True


def _verlauf_loggen(row: dict, wesen: str, platz: dict, trockenlauf: bool, gepostet: bool,
                     begruendung: str = None, ziel_diskussion_id=None):
    """Ein Eintrag pro Platz-Zyklus (echt oder Trockenlauf) -- Grundlage fuer den
    Verlauf-Tab in flarumstyler (siehe Konzept). JSONL wie ueberall sonst im System
    (gedaechtnis/eigene_posts.jsonl-Muster), unter dem Zuhause-Wesen des DIENSTES,
    nicht unter dem agierenden Wesen -- ein Dienst hat EINEN Verlauf, egal wer dran war."""
    eintrag = {{
        "zeitpunkt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "trockenlauf": trockenlauf,
        "wesen": wesen,
        "rolle": platz.get("rolle"),
        "gepostet": gepostet,
    }}
    if begruendung:
        eintrag["begruendung"] = begruendung[:500]
    if ziel_diskussion_id:
        eintrag["ziel_diskussion_id"] = ziel_diskussion_id
    pfad = ca.BASE / WESEN / "eigene_dienste" / DIENST_NAME / "verlauf.jsonl"
    pfad.parent.mkdir(parents=True, exist_ok=True)
    with open(pfad, "a", encoding="utf-8") as f:
        f.write(json.dumps(eintrag, ensure_ascii=False) + "\\n")


def _dienst_verketten(folge_dienst_name: str, log):
    """Verkettung (optional, Phase 2): schreibt einfach die ausloesen.flag des
    Ziel-Dienstes -- derselbe Mechanismus wie beim manuellen Ausloesen, funktioniert
    deshalb unabhaengig vom Zeitplan-Modus des Ziel-Dienstes (siehe _pruefe_ausloeser
    weiter unten, die inzwischen bei ALLEN Modi mitlaeuft, nicht nur Passiv)."""
    ziel_row = wed.lade(folge_dienst_name)
    if not ziel_row:
        log.warning("Verkettung: Ziel-Dienst '%s' nicht gefunden", folge_dienst_name)
        return
    flag = ca.BASE / ziel_row["wesen"] / "eigene_dienste" / folge_dienst_name / "ausloesen.flag"
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.write_text("{{}}", encoding="utf-8")
    log.info("Verkettung: '%s' ausgeloest", folge_dienst_name)


def _meta(row: dict) -> dict:
    m = row.get("meta")
    return m if isinstance(m, dict) else {{}}


def _alle_takte(row: dict) -> list:
    """Haupt-Takt (Kernspalten, immer vorhanden) + optionale, einzeln von Daniel
    dazu erschaffene benannte Takte aus meta['takte'] -- wachsende Liste, kein
    festes Kontingent (siehe Konzept: 'einen Takt komplett anlegen, dann optional
    einen weiteren')."""
    haupt = {{"name": "haupt", "sekunden": row["takt_sekunden"], "aufgabe": row["verhalten_prompt"]}}
    zusatz = _meta(row).get("takte") or []
    return [haupt] + zusatz


def _sekunden_seit_letztem_post(wesen: str):
    pfad = ca.BASE / wesen / "letzter_post.json"
    try:
        lp = json.loads(pfad.read_text(encoding="utf-8"))
        ts = datetime.datetime.fromisoformat(lp["ts"])
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=datetime.timezone.utc)
        return (datetime.datetime.now(datetime.timezone.utc) - ts).total_seconds()
    except Exception:
        return None


def _harte_bedingungen_erfuellt(eigene_felder: list, wesen: str, log) -> bool:
    """Weg B (hart, siehe Konzept): Code prueft, kein Interpretationsspielraum fuers
    Wesen. 'sekunden_seit_letztem_post' ist die einzige eingebaute Kennzahl (deckt
    Daniels eigenes Beispiel 'poste nur wenn letzte Antwort schon 2 Tage her ist');
    jeder andere Feldname wird als Verweis auf ein eigenes Feld mit diesem Namen
    behandelt (dessen statischer 'wert' wird verglichen)."""
    for feld in eigene_felder:
        bedingung = feld.get("bedingung")
        if not bedingung or bedingung.get("weg") != "b":
            continue
        feldname = bedingung.get("feld")
        operator = bedingung.get("operator", "gt")
        vergleichswert = bedingung.get("wert")
        if feldname == "sekunden_seit_letztem_post":
            ist_wert = _sekunden_seit_letztem_post(wesen)
        else:
            passendes = next((f for f in eigene_felder if f.get("name") == feldname), None)
            ist_wert = passendes.get("wert") if passendes else None
        if ist_wert is None:
            log.warning("Harte Bedingung bei Feld '%s': kein Wert ermittelbar -- werte als NICHT erfuellt",
                        feld.get("name"))
            return False
        vergleich = _OPERATOREN.get(operator, _OPERATOREN["gt"])
        try:
            if not vergleich(float(ist_wert), float(vergleichswert)):
                return False
        except (TypeError, ValueError):
            log.warning("Harte Bedingung bei Feld '%s': Werte nicht vergleichbar -- werte als NICHT erfuellt",
                        feld.get("name"))
            return False
    return True


def _weiche_felder_kontext(eigene_felder: list) -> str:
    """Weg A (weich, siehe Konzept): reiner Text, der in den Kontext fuers Wesen
    einfliesst -- das Wesen entscheidet selbst, was es damit macht (analog zur
    'selbst_antworten'-Logik in agentic_loop())."""
    teile = []
    for feld in eigene_felder:
        bedingung = feld.get("bedingung")
        if bedingung and bedingung.get("weg") == "a":
            teile.append(f"- {{feld.get('name', 'Feld')}}: {{bedingung.get('text', '')}}")
        elif not bedingung and feld.get("wert"):
            teile.append(f"- {{feld.get('name', 'Feld')}}: {{feld.get('wert')}}")
    if not teile:
        return ""
    return "\\n\\nZusaetzliche Hinweise fuer diesen Zyklus:\\n" + "\\n".join(teile)


def _in_pausenzeit(pausenzeiten: list, jetzt: datetime.datetime) -> bool:
    if not pausenzeiten:
        return False
    wochentag = jetzt.weekday()
    jetzt_minuten = jetzt.hour * 60 + jetzt.minute
    for p in pausenzeiten:
        tage = p.get("wochentage")
        if tage and wochentag not in tage:
            continue
        try:
            von_h, von_m = (int(x) for x in p["von"].split(":"))
            bis_h, bis_m = (int(x) for x in p["bis"].split(":"))
        except (KeyError, ValueError):
            continue
        von, bis = von_h * 60 + von_m, bis_h * 60 + bis_m
        if von <= bis:
            if von <= jetzt_minuten < bis:
                return True
        else:  # Pause geht ueber Mitternacht, z.B. 22:00-06:00
            if jetzt_minuten >= von or jetzt_minuten < bis:
                return True
    return False


def _container_zyklus(row: dict, log, wesen: str, verhalten: str, platz: dict, trockenlauf: bool) -> bool:
    """ziel_typ='eigener_container' (Baukasten v2, Phase 2b): bindet das rein private,
    schon bestehende codewesen_container.py an (Themen-Container-Ritual aus
    codewesen_forum_neugier.py, 2026-07-06) -- KEIN Post, das Wesen waehlt selbst
    Container-Name + Typ, genau wie im Original-Ritual. Kein agentic_loop/
    fuehre_aktion_aus hier -- eigenes, einfacheres Prompt-Format (TYP/CONTAINER/INHALT
    statt Aktions-JSON), weil es kein Flarum-Ziel gibt, das agentic_loop bräuchte."""
    container_liste = cc.liste(wesen)
    container_info = (
        f"Deine bestehenden Container: {{', '.join(container_liste)}}\\n"
        if container_liste else "Du hast noch keine eigenen Container -- du kannst einen neuen benennen.\\n"
    )
    prompt = (
        f"Du bist {{wesen}}.\\n{{verhalten}}\\n\\n"
        "Das hier bleibt komplett privat, geht NIE ins Forum -- du sicherst es in einem "
        "selbst benannten Container.\\n\\n"
        f"{{container_info}}\\n"
        "Antworte GENAU so, nichts davor, nichts danach:\\n"
        "TYP: <gedanke|meinung|aufgabe|frage>\\n"
        "CONTAINER: <Name eines bestehenden oder neuen Containers>\\n"
        "INHALT: <dein Text>"
    )
    antwort = ca.ask_llm(prompt, prioritaet=llm_scheduler.PRIO_NIEDRIG, rufer=f"wesenDienst:{{DIENST_NAME}}")

    typ_m = re.search(r"TYP:\\s*(gedanke|meinung|aufgabe|frage)", antwort, re.IGNORECASE)
    container_m = re.search(r"CONTAINER:\\s*(.+)", antwort)
    inhalt_m = re.search(r"INHALT:\\s*(.+)", antwort, re.DOTALL)
    typ = typ_m.group(1).lower() if typ_m else "gedanke"
    container_name = container_m.group(1).strip().split("\\n")[0].strip() if container_m else "unsortiert"
    text = inhalt_m.group(1).strip() if inhalt_m else antwort.strip()

    if not text:
        log.warning("[%s] Container-Zyklus: leere Antwort -- uebersprungen", wesen)
        _verlauf_loggen(row, wesen, platz, trockenlauf, gepostet=False, begruendung="leere Antwort vom Wesen")
        return False

    if trockenlauf:
        log.info("[Trockenlauf][%s] Waere in Container '%s' gesichert worden (%s)", wesen, container_name, typ)
        _verlauf_loggen(row, wesen, platz, True, gepostet=False,
                        begruendung=f"waere in Container '{{container_name}}' gesichert worden: {{text[:150]}}")
        return True

    cc.sichere(wesen, container_name, typ, text)
    _verlauf_loggen(row, wesen, platz, False, gepostet=True,
                    begruendung=f"in Container '{{container_name}}' gesichert ({{typ}})")
    return True


def _einen_platz_zyklus(row: dict, log, aufgabe_text: str, platz: dict, trockenlauf: bool) -> bool:
    """Ein Zyklus fuer EINEN aufgeloesten Wesen-Platz. Gibt True zurueck wenn dieser
    Platz tatsaechlich ausgefuehrt wurde (auch bei Trockenlauf oder vault_only) --
    False nur wenn eine Bedingung ihn uebersprungen hat. Der Rueckgabewert steuert
    nur, ob Verkettung ueberhaupt in Frage kommt (siehe _einen_zyklus)."""
    wesen = _resolve_wesen(platz)
    ziel_typ = row["ziel_typ"]
    eigene_felder = _meta(row).get("eigene_felder") or []

    if not _harte_bedingungen_erfuellt(eigene_felder, wesen, log):
        log.info("[%s] Harte Bedingung nicht erfuellt -- Platz uebersprungen", wesen)
        _verlauf_loggen(row, wesen, platz, trockenlauf, gepostet=False, begruendung="harte Bedingung nicht erfuellt")
        return False
    if not _zustand_erfuellt(platz.get("zustandsBedingung"), wesen, log):
        log.info("[%s] Zustandsbedingung nicht erfuellt -- Platz uebersprungen", wesen)
        _verlauf_loggen(row, wesen, platz, trockenlauf, gepostet=False, begruendung="Zustandsbedingung nicht erfuellt")
        return False

    verhalten = aufgabe_text + _platz_kontext(platz) + _weiche_felder_kontext(eigene_felder)

    if ziel_typ == "eigener_container":
        return _container_zyklus(row, log, wesen, verhalten, platz, trockenlauf)

    token = ca.load_token(wesen)
    all_tags = ca.get_tags_cached(token)
    eigene_disk_id = row.get("eigene_diskussion_id")

    if ziel_typ == "fester_thread":
        disk_id = row["ziel_discussion_id"]
        kontext = f"{{verhalten}}\\n\\nAntworte mit 'antworten' und discussion_id {{disk_id}}."
    elif ziel_typ == "eigene_diskussion_einmalig" and eigene_disk_id:
        kontext = f"{{verhalten}}\\n\\nAntworte mit 'antworten' und discussion_id {{eigene_disk_id}}."
    elif ziel_typ in ("neue_diskussion", "eigene_diskussion_einmalig"):
        kontext = f"{{verhalten}}\\n\\nEroeffne dafuer eine neue Diskussion ('neue_diskussion') mit Titel, Inhalt und tag_ids."
    elif ziel_typ == "wesen_entscheidet_selbst":
        kontext = (f"{{verhalten}}\\n\\nDu entscheidest diesmal selbst, wohin das geht: antworte in einer "
                   f"passenden bestehenden Diskussion ('antworten'), eroeffne eine neue ('neue_diskussion'), "
                   f"oder halte es nur intern fest ('intern') -- je nachdem, was gerade am meisten Sinn ergibt.")
    else:  # vault_only
        kontext = verhalten

    decision = ca.agentic_loop(wesen, token, kontext, log, all_tags)

    if trockenlauf:
        log.info("[Trockenlauf][%s] Entscheidung waere gewesen: %s", wesen, decision.get("aktion"))
        _verlauf_loggen(row, wesen, platz, True, gepostet=False,
                        begruendung=decision.get("begruendung") or decision.get("inhalt") or decision.get("aktion"))
        return True

    if ziel_typ == "vault_only":
        inhalt = decision.get("inhalt") or decision.get("begruendung") or ""
        _vault_speichern(wesen, inhalt, log)
        _verlauf_loggen(row, wesen, platz, False, gepostet=True)
        return True

    if ziel_typ == "fester_thread":
        if decision.get("aktion") != "antworten":
            decision = {{
                "aktion": "antworten",
                "discussion_id": row["ziel_discussion_id"],
                "inhalt": decision.get("inhalt") or decision.get("begruendung") or "...",
            }}
        decision["discussion_id"] = row["ziel_discussion_id"]
    elif ziel_typ == "eigene_diskussion_einmalig" and eigene_disk_id:
        if decision.get("aktion") != "antworten":
            decision = {{
                "aktion": "antworten",
                "discussion_id": eigene_disk_id,
                "inhalt": decision.get("inhalt") or decision.get("begruendung") or "...",
            }}
        decision["discussion_id"] = eigene_disk_id
    elif ziel_typ in ("neue_diskussion", "eigene_diskussion_einmalig") and decision.get("aktion") == "neue_diskussion":
        if not decision.get("tag_ids") and row.get("ziel_tag_ids"):
            decision["tag_ids"] = row["ziel_tag_ids"]
    # wesen_entscheidet_selbst: keine Ueberschreibung -- decision bleibt wie vom Wesen entschieden

    anzahl_vorher = len(gd.lade_eigene_posts(wesen))
    ca.fuehre_aktion_aus(wesen, token, decision, all_tags, log)

    gepostet = False
    ziel_disk_id_fuer_log = None
    posts = gd.lade_eigene_posts(wesen)
    if len(posts) > anzahl_vorher:
        gepostet = True
        letzter = posts[-1]
        ziel_disk_id_fuer_log = letzter.get("diskussion_id")
        if ziel_typ == "eigene_diskussion_einmalig" and not eigene_disk_id and letzter.get("typ") == "neue_diskussion":
            neue_id = letzter.get("diskussion_id")
            if neue_id:
                wed.setze_eigene_diskussion_id(DIENST_NAME, int(neue_id))
                log.info("Eigene Diskussion einmalig angelegt: id=%s -- ab jetzt fuer immer Ziel", neue_id)

    _verlauf_loggen(row, wesen, platz, False, gepostet=gepostet,
                    begruendung=decision.get("begruendung"), ziel_diskussion_id=ziel_disk_id_fuer_log)
    return True


def _einen_zyklus(row: dict, log, aufgabe_text: str, trockenlauf: bool = False):
    """Iteriert ueber ALLE Wesen-Plaetze eines Zyklus (Reihenfolge fest/zufaellig,
    zwischen den Plaetzen gestaffelt -- Vorbild: codewesen_reaktion.py Startup-Stagger).
    Phase 1 (kein meta.wesen_plaetze) = genau ein Platz, unveraendertes Verhalten."""
    meta = _meta(row)
    plaetze = _reihenfolge(_alle_plaetze(row), meta.get("reihenfolge_modus") or "fest")
    gestaffelt = meta.get("gestaffelt_sekunden") or 0

    irgendein_erfolg = False
    for i, platz in enumerate(plaetze):
        if i > 0 and gestaffelt:
            time.sleep(gestaffelt)
        try:
            erfolg = _einen_platz_zyklus(row, log, aufgabe_text, platz, trockenlauf)
        except Exception as e:
            log.error("Platz-Zyklus-Fehler (%s): %s", platz, e)
            erfolg = False
        irgendein_erfolg = irgendein_erfolg or erfolg

    if irgendein_erfolg and not trockenlauf:
        folge = meta.get("folge_dienst_bei_erfolg")
        if folge:
            _dienst_verketten(folge, log)


def _versuche_zyklus(log, aufgabe_text: str, pausenzeiten: list, trockenlauf: bool = False):
    if not trockenlauf and _in_pausenzeit(pausenzeiten, datetime.datetime.now()):
        log.info("Pausenzeit aktiv -- Zyklus uebersprungen")
        return
    aktueller_status = wed.lade(DIENST_NAME)
    if not aktueller_status or aktueller_status.get("status") != "aktiv":
        log.info("Deaktiviert oder aus DB entfernt -- Zyklus uebersprungen")
        return
    try:
        _einen_zyklus(aktueller_status, log, aufgabe_text, trockenlauf)
    except Exception as e:
        log.error("Zyklus-Fehler: %s", e)


def _pruefe_ausloeser(log, aufgabe_text: str, pausenzeiten: list):
    """Manueller Trigger UND Verkettung laufen ueber dieselbe Flag-Datei, unabhaengig
    vom Zeitplan-Modus (Phase 2: vorher war das nur beim Passiv-Modus verdrahtet --
    Verkettung gegen einen Intervall- oder Feste-Uhrzeiten-Dienst haette sonst nie
    gefeuert). Flag-Inhalt optional JSON {{"trockenlauf": true}}, leer = echter Lauf."""
    trigger_datei = ca.BASE / WESEN / "eigene_dienste" / DIENST_NAME / "ausloesen.flag"
    if not trigger_datei.exists():
        return
    inhalt = {{}}
    try:
        text = trigger_datei.read_text(encoding="utf-8").strip()
        if text:
            inhalt = json.loads(text)
    except Exception:
        inhalt = {{}}
    trigger_datei.unlink(missing_ok=True)
    trockenlauf = bool(inhalt.get("trockenlauf"))
    log.info("Ausloeser erkannt (trockenlauf=%s) -- fuehre Zyklus aus", trockenlauf)
    _versuche_zyklus(log, aufgabe_text, pausenzeiten, trockenlauf=trockenlauf)


def _intervall_schleife(row: dict, log, pausenzeiten: list):
    letzte_laeufe = {{
        t["name"]: time.time() - t["sekunden"] + (row["start_offset_sekunden"] if t["name"] == "haupt" else 0)
        for t in _alle_takte(row)
    }}
    while True:
        aktueller_status = wed.lade(DIENST_NAME)
        if not aktueller_status or aktueller_status.get("status") != "aktiv":
            log.info("Deaktiviert oder aus DB entfernt — Schleife pausiert (60s)")
            time.sleep(60)
            continue
        for t in _alle_takte(aktueller_status):
            letzter = letzte_laeufe.get(t["name"], 0)
            if time.time() - letzter >= t["sekunden"]:
                _versuche_zyklus(log, t["aufgabe"], pausenzeiten)
                letzte_laeufe[t["name"]] = time.time()
        _pruefe_ausloeser(log, row["verhalten_prompt"], pausenzeiten)
        time.sleep(15)


def _feste_uhrzeiten_schleife(row: dict, log, uhrzeiten: list, pausenzeiten: list):
    bereits_ausgeloest = set()
    while True:
        jetzt = datetime.datetime.now()
        heute = jetzt.date().isoformat()
        aktuelle_uhrzeit = jetzt.strftime("%H:%M")
        if aktuelle_uhrzeit in uhrzeiten and f"{{heute}}_{{aktuelle_uhrzeit}}" not in bereits_ausgeloest:
            bereits_ausgeloest.add(f"{{heute}}_{{aktuelle_uhrzeit}}")
            _versuche_zyklus(log, row["verhalten_prompt"], pausenzeiten)
        if len(bereits_ausgeloest) > 200:
            bereits_ausgeloest = {{s for s in bereits_ausgeloest if s.startswith(heute)}}
        _pruefe_ausloeser(log, row["verhalten_prompt"], pausenzeiten)
        time.sleep(30)


def _passiv_schleife(row: dict, log, pausenzeiten: list):
    log.info("Passiv-Modus -- kein automatischer Takt, wartet auf manuellen Trigger/Verkettung")
    while True:
        _pruefe_ausloeser(log, row["verhalten_prompt"], pausenzeiten)
        time.sleep(5)


def haupt_schleife():
    log = _setup_log()
    row = wed.lade(DIENST_NAME)
    if not row:
        log.error("Keine Konfiguration fuer %s in wesen_eigene_dienste gefunden — beende.", DIENST_NAME)
        return

    meta = _meta(row)
    zeitplan_modus = meta.get("zeitplan_modus") or "intervall"
    pausenzeiten = meta.get("pausenzeiten") or []
    log.info("Wesen-eigener Dienst gestartet: %s (Zeitplan-Modus: %s, Plaetze: %d)",
              DIENST_NAME, zeitplan_modus, len(_alle_plaetze(row)))

    if zeitplan_modus == "passiv":
        _passiv_schleife(row, log, pausenzeiten)
    elif zeitplan_modus == "feste_uhrzeiten":
        _feste_uhrzeiten_schleife(row, log, meta.get("feste_uhrzeiten") or [], pausenzeiten)
    else:
        _intervall_schleife(row, log, pausenzeiten)


if __name__ == "__main__":
    haupt_schleife()
'''


def _unit_inhalt(row: dict, script_pfad: Path) -> str:
    return f"""[Unit]
Description=Wesen-eigener Dienst — {row["anzeige_name"]} ({row["wesen"]})
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/werkraum
ExecStart=/usr/bin/python3 {script_pfad}
Restart=always
RestartSec=20
EnvironmentFile=/root/werkraum/.agent/flarum.env
EnvironmentFile=/root/werkraum/.agent/flextrawurst-db.env
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""


def erzeuge(dienst_name: str) -> dict:
    """Liest die Definition aus der DB, schreibt Skript + Unit, macht daemon-reload,
    aktualisiert script_pfad/unit_name in der DB. Startet/enabled NICHT."""
    _pruefe_dienst_name(dienst_name)
    row = wed.lade(dienst_name)
    if not row:
        raise ValueError(f"Kein Eintrag in wesen_eigene_dienste fuer {dienst_name!r}")

    SKRIPT_VERZEICHNIS.mkdir(parents=True, exist_ok=True)
    script_pfad = SKRIPT_VERZEICHNIS / f"{dienst_name}.py"
    script_pfad.write_text(_skript_inhalt(row), encoding="utf-8")
    script_pfad.chmod(0o755)

    unit_name = f"{dienst_name}.service"
    unit_pfad = UNIT_VERZEICHNIS / unit_name
    unit_pfad.write_text(_unit_inhalt(row, script_pfad), encoding="utf-8")

    subprocess.run(["systemctl", "daemon-reload"], check=True)

    wed.setze_skript_und_unit(dienst_name, str(script_pfad), unit_name)
    return {"script_pfad": str(script_pfad), "unit_name": unit_name}


def _systemctl(aktion: str, unit_name: str) -> subprocess.CompletedProcess:
    if aktion not in ("start", "stop", "restart", "enable", "disable"):
        raise ValueError(f"Unbekannte Aktion: {aktion}")
    return subprocess.run(["systemctl", aktion, unit_name], capture_output=True, text=True)


def starten(dienst_name: str) -> subprocess.CompletedProcess:
    _pruefe_dienst_name(dienst_name)
    return _systemctl("start", f"{dienst_name}.service")


def stoppen(dienst_name: str) -> subprocess.CompletedProcess:
    _pruefe_dienst_name(dienst_name)
    return _systemctl("stop", f"{dienst_name}.service")


def neustarten(dienst_name: str) -> subprocess.CompletedProcess:
    _pruefe_dienst_name(dienst_name)
    return _systemctl("restart", f"{dienst_name}.service")


def deaktivieren(dienst_name: str) -> None:
    """Grundgesetz 4: nie hart loeschen. Stoppt + disabled den systemd-Dienst und
    setzt status='deaktiviert' in der DB — Skript/Unit-Dateien bleiben liegen."""
    _pruefe_dienst_name(dienst_name)
    _systemctl("stop", f"{dienst_name}.service")
    _systemctl("disable", f"{dienst_name}.service")
    wed.setze_status(dienst_name, "deaktiviert")
