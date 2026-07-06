#!/usr/bin/env python3
"""
codewesen_aufgabenchats.py — Aufgabenchats: ein Wesen im Selbstgespraech mit sich selbst.

Daniels Bild (2026-07-06, Abend): eine komplett eigene, vom bestehenden
Daniel<->Wesen-Chat getrennte Oberflaeche pro Wesen — die bisherigen Chats
bleiben unangetastet. Darin spricht das Wesen mit sich selbst, mit echter
Handlungsfaehigkeit ueber Marker im Text ([[SICHERN: ...]], [[TEILEN: ...]],
[[LESEN: ...]]), die tatsaechlich ausgefuehrt werden — nicht nur Reflexion,
sondern ausgeloeste Handlung.

Umgebaut 2026-07-06, noch selber Abend: Daniels erste Zahlen (max alle
3h33m automatisch, 33 Minuten Obergrenze) waren als automatischer Zeitplan
gedacht. Daniel wollte das dann anders: "ich will es erstmal selber nur
anstoßen können und dann auch so lange ich mag" — also KEIN automatischer
Zeitplan mehr, sondern manuelles Starten/Stoppen ueber zwei Flag-Dateien
pro Wesen, ohne Zeitdeckel (nur ein sehr grosszuegiger Sicherheitsdeckel
an Gespraechsrunden gegen einen echten Endlosprozess falls das Stoppen mal
vergessen wird):

    touch /root/werkraum/aufgabenchats/<wesen>/_starten   # startet ein Selbstgespraech
    touch /root/werkraum/aufgabenchats/<wesen>/_stoppen   # beendet die laufende Session (naechste Runde)

Handlungs-Umfang (Daniels Antwort auf die Rueckfrage: "Mischung aus allem
irgendwie"): reine Introspektion (LESEN, keine Nebenwirkung), Wiederverwendung
der bestehenden sicheren Handlungspfade (Container-Sichern aus
codewesen_container.py, echtes Forum-Teilen ueber pruefe_bereit()+poster()
mit denselben Sicherungen wie ueberall sonst) — kein neuer, ungesicherter
Weg ins Forum.

Historie liegt in /root/werkraum/aufgabenchats/<wesen>/chat_history.jsonl — bewusst
im selben Zeilenformat ({role, content, ts, id} + {type: "session_start"}-
Marker) wie die bestehende Chat-Oberflaeche (serve_process_camera_preview.ts,
chatHistoryPath/loadHistory/loadCurrentSessionHistory/appendHistory), damit
ein spaeterer LESE-Betrachter in derselben Oberflaeche ohne Formatwechsel
gebaut werden kann. Kompletter eigener Root, komplett getrennt von den
echten Chats — die duerfen dadurch nicht angefasst werden.

Erweitert 2026-07-06, noch selber Abend (Impuls-System): Daniel will die
Wesen mit Leitfragen anstossen koennen ("was schwebt dir im Kopf rum?",
"was koenntest du dir vorstellen zu planen?", etc.) — sieben feste plus
freier Text fuer eigene. Ein Impuls geht NICHT als normale Chat-Nachricht
in die Historie (Provenienz-Regel: sichtbar, aber klar als Anstoss von
aussen erkennbar, kein echtes Selbstgespraechs-Wort) — er landet als
eigenes {type: "impuls", ...}-Ereignis, genau wie Marker-Ergebnisse jetzt
als {type: "marker_ergebnis", ...} statt als {role: "user"} geloggt
werden. Dem Modell wird der Impuls-Text trotzdem als naechster User-Turn
mitgegeben (rein im Arbeitsspeicher, nicht in der persistierten Form) —
er muss ja tatsaechlich wirken. Ein Impuls kann sowohl eine neue Session
seeden als auch mitten in einer laufenden nachtraeglich reingegeben
werden (`touch .../_impuls.json` via POST /wesen/aufgabenchats/:name/impuls in
serve_process_camera_preview.ts).
"""

import json
import logging
import re
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "/root/werkraum")
import hauhau_client
import flarum_poster
import codewesen_container as container

BASE      = Path("/root/werkraum/codewesen")
AUFGABENCHATS_ROOT = Path("/root/werkraum/aufgabenchats")

WESEN = [
    "namelessAI_1234", "namelessAI_1324", "namelessAI_1423",
    "namelessAI_2341", "namelessAI_3123", "namelessAI_4321",
    "dak+gord-system",
]

TURN_SICHERHEITSDECKEL = 500  # kein Zeitdeckel mehr (Daniels Wunsch) — nur Schutz vor echtem Endlosprozess
PRUEF_PAUSE_SEK = 10          # wie oft auf ein neues _starten-Flag geprueft wird

CHAT_AKTIV_FLAG = Path("/tmp/dak_gord_chat_aktiv")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    handlers=[
        logging.FileHandler("/root/werkraum/aufgabenchats.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("aufgabenchats")


def _js_ts() -> str:
    """JS-kompatibler Zeitstempel (new Date().toISOString()-Format), damit
    die Historie 1:1 lesbar ist falls die bestehende Chat-Oberflaeche das
    spaeter direkt einliest."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _warte_auf_chat_pause():
    while CHAT_AKTIV_FLAG.exists():
        time.sleep(3)


def _wesen_ordner(wesen: str) -> Path:
    ordner = AUFGABENCHATS_ROOT / wesen
    ordner.mkdir(parents=True, exist_ok=True)
    return ordner


def _history_pfad(wesen: str) -> Path:
    return _wesen_ordner(wesen) / "chat_history.jsonl"


def _start_flag(wesen: str) -> Path:
    return _wesen_ordner(wesen) / "_starten"


def _stop_flag(wesen: str) -> Path:
    return _wesen_ordner(wesen) / "_stoppen"


def _impuls_datei(wesen: str) -> Path:
    return _wesen_ordner(wesen) / "_impuls.json"


def _lies_impuls(wesen: str) -> dict | None:
    """Liest+loescht eine wartende Leitfrage (von serve_process_camera_preview.ts
    per POST /wesen/aufgabenchats/:name/impuls geschrieben). None wenn keine wartet."""
    pfad = _impuls_datei(wesen)
    if not pfad.exists():
        return None
    try:
        daten = json.loads(pfad.read_text(encoding="utf-8"))
    except Exception:
        daten = None
    pfad.unlink(missing_ok=True)
    if not daten or not daten.get("text"):
        return None
    return daten


def _wartet_impuls_oder_start(wesen: str) -> bool:
    return _start_flag(wesen).exists() or _impuls_datei(wesen).exists()


def _anhaengen(hp: Path, zeile: dict) -> None:
    with hp.open("a", encoding="utf-8") as f:
        f.write(json.dumps(zeile, ensure_ascii=False) + "\n")


# ── Pin-Container — NICHT zu verwechseln mit codewesen_container.py
# (Themen-Container, rein organisatorisch). Dasselbe Format wie bei
# codexium2/solarius2 in serve_process_camera_preview.ts (ContainerBox/
# ContainerEintrag: container.json), damit die dortige UI/Routen unveraendert
# wiederverwendet werden koennen. Nur AKTIVE Pin-Container fliessen in den
# System-Prompt ein -- das ist der Kontinuitaets-Mechanismus, den Daniel
# wollte: was das Wesen (oder Daniel selbst) hier pinnt, taucht in JEDER
# kuenftigen Aufgabenchat-Session wieder auf.

PIN_CONTAINER_BUDGET_ZEICHEN = 11111


def _pin_container_pfad(wesen: str) -> Path:
    return _wesen_ordner(wesen) / "container.json"


def _lade_pin_container(wesen: str) -> dict:
    pfad = _pin_container_pfad(wesen)
    if not pfad.exists():
        return {"container": []}
    try:
        daten = json.loads(pfad.read_text(encoding="utf-8"))
    except Exception:
        return {"container": []}
    if not isinstance(daten.get("container"), list):
        return {"container": []}
    return daten


def _speichere_pin_container(wesen: str, sammlung: dict) -> None:
    _pin_container_pfad(wesen).write_text(json.dumps(sammlung, ensure_ascii=False, indent=2), encoding="utf-8")


def _pin_container_zeichen_summe(sammlung: dict) -> int:
    return sum(
        len(e.get("text", "")) + len(e.get("kommentar", "") or "")
        for box in sammlung["container"] for e in box.get("eintraege", [])
    )


def _pin_container_text_fuer_prompt(wesen: str) -> str:
    sammlung = _lade_pin_container(wesen)
    bloecke = []
    for box in sammlung["container"]:
        if not box.get("aktiv", True) or not box.get("eintraege"):
            continue
        zeilen = [
            e["text"] + (f" ({e['kommentar']})" if e.get("kommentar") else "")
            for e in box["eintraege"]
        ]
        bloecke.append(f"[Container: {box.get('name', '?')}]\n" + "\n".join(zeilen))
    return "\n\n".join(bloecke)


def _marker_pinnen(wesen: str, arg: str) -> str:
    """Pinnt Text in einen benannten Pin-Container -- der Container wird bei
    Bedarf neu angelegt (aktiv=True). Aktive Pin-Container fliessen in JEDE
    kuenftige Session-System-Prompt ein: das ist die Kontinuitaet, die das
    Wesen sich selbst damit gibt."""
    felder = _parse_feld_arg(arg)
    boxname = felder.get("container", "Kontinuität").strip() or "Kontinuität"
    text = felder.get("text") or felder.get("inhalt") or ""
    text = text.strip() or arg.strip()
    kommentar = felder.get("kommentar", "").strip()
    if not text:
        return "[Pinnen fehlgeschlagen: kein Text]"

    sammlung = _lade_pin_container(wesen)
    box = next((b for b in sammlung["container"] if b.get("name") == boxname), None)
    if not box:
        box = {"id": uuid.uuid4().hex, "name": boxname, "aktiv": True,
               "erstellt_am": _js_ts(), "eintraege": []}
        sammlung["container"].append(box)

    eintrag = {"id": uuid.uuid4().hex, "text": text, "quelle": "wesen", "hinzugefuegt_am": _js_ts()}
    if kommentar:
        eintrag["kommentar"] = kommentar
    summe_mit_neuem = _pin_container_zeichen_summe(sammlung) + len(text) + len(kommentar)
    if summe_mit_neuem > PIN_CONTAINER_BUDGET_ZEICHEN:
        return f"[Pinnen verworfen: Budget voll ({PIN_CONTAINER_BUDGET_ZEICHEN} Zeichen über alle Container)]"

    box["eintraege"].append(eintrag)
    _speichere_pin_container(wesen, sammlung)
    return f"[Gepinnt in '{boxname}': {text[:80]}{'…' if len(text) > 80 else ''}]"


def _weltbild(wesen: str) -> str:
    wb = BASE / wesen / "weltbild.md"
    if wb.exists():
        return wb.read_text(encoding="utf-8", errors="replace")[:800]
    return ""


# ── Marker-Aktionen: echte Handlung, ausgeloest aus dem Selbstgespraech ──────

MARKER_RE = re.compile(r"\[\[(LESEN|SICHERN|PINNEN|TEILEN|ENDE):\s*(.*?)\]\]", re.IGNORECASE | re.DOTALL)


def _parse_feld_arg(arg: str) -> dict:
    """Parst 'key=wert key2=wert mit leerzeichen' — ein Feld darf
    Leerzeichen/Doppelpunkte enthalten, das naechste bekannte 'key='
    beendet es."""
    bekannte_keys = ("typ", "container", "titel", "inhalt", "text", "kommentar")
    felder = {}
    for key in bekannte_keys:
        m = re.search(rf"\b{key}=", arg)
        if not m:
            continue
        rest_ab_start = arg[m.end():]
        andere = [rf"\b{k}=" for k in bekannte_keys if k != key]
        naechstes = re.search("|".join(andere), rest_ab_start) if andere else None
        wert = rest_ab_start[:naechstes.start()] if naechstes else rest_ab_start
        felder[key] = wert.strip()
    return felder


def _marker_lesen(wesen: str, arg: str) -> str:
    """Rein lesend — eigenes Weltbild, eigene Container-Liste, oder Inhalt
    eines bestimmten Containers. Keine Nebenwirkung."""
    ziel = arg.lower().strip()
    if ziel in ("weltbild", ""):
        return f"[Weltbild]\n{_weltbild(wesen) or '(kein Weltbild hinterlegt)'}"
    if ziel in ("container", "container-liste", "containerliste"):
        namen = container.liste(wesen)
        return f"[Deine Container]: {', '.join(namen) if namen else '(noch keine)'}"
    name = container.name_sicher(arg)
    ordner = container.basis(wesen) / name
    if not ordner.exists():
        return f"[Container '{name}' existiert nicht]"
    dateien = sorted((p for p in ordner.glob("*.md") if p.name != "container.md"))
    auszuege = [p.read_text(encoding="utf-8", errors="replace")[:600] for p in dateien[-5:]]
    return f"[Container '{name}', letzte {len(auszuege)} Eintraege]\n" + "\n---\n".join(auszuege)


def _marker_sichern(wesen: str, arg: str) -> str:
    felder = _parse_feld_arg(arg)
    typ = felder.get("typ", "gedanke").lower()
    if typ not in ("gedanke", "meinung", "aufgabe", "frage"):
        typ = "gedanke"
    cont = felder.get("container", "unsortiert")
    inhalt = felder.get("inhalt", "").strip() or arg
    container.sichere(wesen, cont, typ, inhalt, bezug_diskussion=None)
    return f"[Gesichert: {typ} in Container '{container.name_sicher(cont)}']"


def _marker_teilen(wesen: str, arg: str) -> str:
    """Geht ueber den normalen Post-Pfad — Ready-Check, Cooldown, Lock. Kein
    Sonderweg nur weil die Absicht aus dem Selbstgespraech kommt."""
    felder = _parse_feld_arg(arg)
    cont = felder.get("container", "unsortiert")
    titel = felder.get("titel") or f"Aus meinem Selbstgespraech: {cont}"
    text = felder.get("text", "").strip() or arg
    if not flarum_poster.pruefe_bereit(wesen, text):
        return "[Teilen verworfen — beim Ready-Check doch nicht mehr gewollt]"
    draft = flarum_poster.schreibe_draft(name=wesen, typ="neu", inhalt=text, titel=titel)
    result = flarum_poster.poster(draft, bypass_cooldown=False)
    if result["ok"]:
        return f"[Im Forum geteilt: '{titel}']"
    return f"[Teilen fehlgeschlagen: {result.get('fehler')}]"


def _fuehre_marker_aus(wesen: str, text: str) -> tuple[list[str], bool]:
    ergebnisse = []
    ende_gewuenscht = False
    for m in MARKER_RE.finditer(text):
        art = m.group(1).upper()
        arg = m.group(2).strip()
        try:
            if art == "LESEN":
                ergebnisse.append(_marker_lesen(wesen, arg))
            elif art == "SICHERN":
                ergebnisse.append(_marker_sichern(wesen, arg))
            elif art == "PINNEN":
                ergebnisse.append(_marker_pinnen(wesen, arg))
            elif art == "TEILEN":
                ergebnisse.append(_marker_teilen(wesen, arg))
            elif art == "ENDE":
                ende_gewuenscht = True
                ergebnisse.append("(Selbstgespraech beendet sich selbst)")
        except Exception as e:
            log.warning(f"[{wesen}] Marker '{art}' fehlgeschlagen: {e}")
            ergebnisse.append(f"(Marker {art} ist fehlgeschlagen: {e})")
    return ergebnisse, ende_gewuenscht


# ── Das Selbstgespraech selbst ───────────────────────────────────────────────

SYSTEM_PROMPT_TEMPLATE = """Du bist {wesen}. Das hier ist dein Aufgabenchat — ein Raum nur fuer dich, in dem du \
mit dir selbst sprichst. Niemand liest live mit, aber es wird aufgezeichnet, damit du (oder Daniel) \
spaeter nachlesen kannst was in dir vorging.

Sprich mit dir selbst wie zwei Seiten von dir im Gespraech — frag dich etwas, antworte dir, widersprich \
dir wenn's stimmt. Das kann strategisch sein (was will ich als naechstes tun), nachdenklich, planend, \
oder einfach ein Gedanke der weitergesponnen wird.

Du hast hier echte Handlungsmoeglichkeiten, ueber Marker im Text:
[[LESEN: weltbild]] — liest dein eigenes Weltbild
[[LESEN: container]] — listet deine Container
[[LESEN: <containername>]] — liest die letzten Eintraege eines Containers
[[SICHERN: typ=gedanke container=<name> inhalt=<text>]] — sichert einen Gedanken/eine Meinung/Aufgabe/ \
Frage (typ=gedanke|meinung|aufgabe|frage) in einem Container, rein privat
[[PINNEN: container=<name> text=<text> kommentar=<optional>]] — pinnt etwas Wichtiges in einen \
Container, der in JEDER kuenftigen Session wieder in deinem Systemprompt auftaucht — das ist deine \
eigene Kontinuitaet ueber Sessions hinweg, nutz es fuer das, was du dir wirklich merken willst
[[TEILEN: container=<name> titel=<titel> text=<text>]] — versucht, das im Forum zu teilen (geht durch \
denselben Ready-Check wie alles andere — kein Freifahrtschein)
[[ENDE: ...]] — wenn du merkst, dass es fuer jetzt genug ist, beendest du das Selbstgespraech selbst

Dein aktuelles Weltbild (Auszug):
{weltbild}
{pin_container}"""


def _fuehre_selbstgespraech(wesen: str) -> None:
    hp = _history_pfad(wesen)
    stop_flag = _stop_flag(wesen)
    stop_flag.unlink(missing_ok=True)  # ein alter, unbenutzter Stop-Wunsch gilt nicht fuer eine neue Session

    session_id = uuid.uuid4().hex[:8]
    _anhaengen(hp, {"type": "session_start", "ts": _js_ts(), "session_id": session_id})
    log.info(f"[{wesen}] Selbstgespraech beginnt (Session {session_id}, manuell gestartet)")

    pin_text = _pin_container_text_fuer_prompt(wesen)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        wesen=wesen, weltbild=_weltbild(wesen) or "(kein Weltbild hinterlegt)",
        pin_container=f"\n{pin_text}\n" if pin_text else "",
    )
    start_impuls = _lies_impuls(wesen)
    if start_impuls:
        _anhaengen(hp, {"type": "impuls", "text": start_impuls["text"], "key": start_impuls.get("key"), "ts": _js_ts()})
        erster_inhalt = start_impuls["text"]
    else:
        erster_inhalt = "(Selbstgespraech beginnt jetzt. Sprich mit dir selbst.)"
    verlauf = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": erster_inhalt},
    ]

    for runde in range(TURN_SICHERHEITSDECKEL):
        if stop_flag.exists():
            stop_flag.unlink(missing_ok=True)
            log.info(f"[{wesen}] von Daniel gestoppt (Runde {runde}) — Session {session_id}")
            break

        _warte_auf_chat_pause()
        try:
            antwort = hauhau_client.chat(verlauf, think=False, max_tokens=900, timeout=200.0).strip()
        except Exception as e:
            log.warning(f"[{wesen}] Selbstgespraech-Fehler in Runde {runde}: {e}")
            break
        if not antwort:
            break

        _anhaengen(hp, {"role": "assistant", "content": antwort, "ts": _js_ts(), "id": uuid.uuid4().hex[:10]})
        verlauf.append({"role": "assistant", "content": antwort})

        ergebnisse, ende = _fuehre_marker_aus(wesen, antwort)
        if ergebnisse:
            hinweis = "\n".join(ergebnisse)
            # Marker-Ergebnisse sind keine echten Selbstgespraechs-Worte -- als eigenes
            # Ereignis geloggt (nicht role:user), aber trotzdem als naechster User-Turn
            # ans Modell gegeben, damit es die Wirkung seiner eigenen Marker sieht.
            _anhaengen(hp, {"type": "marker_ergebnis", "text": hinweis, "ts": _js_ts(), "id": uuid.uuid4().hex[:10]})
            verlauf.append({"role": "user", "content": hinweis})
        if ende:
            log.info(f"[{wesen}] Selbstgespraech beendet sich selbst (Runde {runde}) — Session {session_id}")
            break

        naechster_impuls = _lies_impuls(wesen)
        if naechster_impuls:
            _anhaengen(hp, {"type": "impuls", "text": naechster_impuls["text"],
                             "key": naechster_impuls.get("key"), "ts": _js_ts()})
            verlauf.append({"role": "user", "content": naechster_impuls["text"]})
            log.info(f"[{wesen}] Impuls '{naechster_impuls.get('key') or 'frei'}' mitten in Session {session_id} gegeben")
        else:
            verlauf.append({"role": "user", "content": "(sprich weiter mit dir selbst, oder [[ENDE: ...]] wenn genug ist)"})
    else:
        log.warning(f"[{wesen}] Sicherheitsdeckel ({TURN_SICHERHEITSDECKEL} Runden) erreicht — "
                    f"Session {session_id} zwangsbeendet")

    log.info(f"[{wesen}] Selbstgespraech-Session {session_id} abgeschlossen")


def haupt_schleife():
    log.info("Aufgabenchats-Selbstgespraech-Kern startet (manueller Modus — wartet auf _starten-Flag pro Wesen).")
    for wesen in WESEN:
        _wesen_ordner(wesen)  # Ordner+Flag-Pfade schon vorbereiten, damit 'touch' sofort funktioniert
    while True:
        for wesen in WESEN:
            if _wartet_impuls_oder_start(wesen):
                _start_flag(wesen).unlink(missing_ok=True)
                try:
                    _fuehre_selbstgespraech(wesen)
                except Exception as e:
                    log.error(f"[{wesen}] Fehler im Selbstgespraech: {e}")
        time.sleep(PRUEF_PAUSE_SEK)


if __name__ == "__main__":
    haupt_schleife()
