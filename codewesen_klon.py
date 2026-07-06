#!/usr/bin/env python3
"""
codewesen_klon.py — Der Klon: ein Wesen im Selbstgespraech mit sich selbst.

Daniels Bild (2026-07-06, Abend): eine komplett eigene, vom bestehenden
Daniel<->Wesen-Chat getrennte Oberflaeche pro Wesen — die bisherigen Chats
bleiben unangetastet. Darin spricht das Wesen mit sich selbst, mit echter
Handlungsfaehigkeit ueber Marker im Text ([[SICHERN: ...]], [[TEILEN: ...]],
[[LESEN: ...]]), die tatsaechlich ausgefuehrt werden — nicht nur Reflexion,
sondern ausgeloeste Handlung.

Daniels eigene Zahlen: "max alle 3stunden33...aber dann darf es sich auch
33 minuten voll triggern" — Begruendung im selben Atemzug: "sonst sind sie
24/2 nur noch am sich selbst triggern, wie maeuse mit nem orgasmusknopf".
Also: MINDEST_PAUSE = 3h33m pro Wesen zwischen zwei Selbstgespraechen,
SESSION_MAX = 33 Minuten Obergrenze pro Selbstgespraech.

Handlungs-Umfang (Daniels Antwort auf die Rueckfrage: "Mischung aus allem
irgendwie"): reine Introspektion (LESEN, keine Nebenwirkung), Wiederverwendung
der bestehenden sicheren Handlungspfade (Container-Sichern aus
codewesen_container.py, echtes Forum-Teilen ueber pruefe_bereit()+poster()
mit denselben Sicherungen wie ueberall sonst) — kein neuer, ungesicherter
Weg ins Forum.

Historie liegt in /root/werkraum/klon/<wesen>/chat_history.jsonl — bewusst
im selben Zeilenformat ({role, content, ts, id} + {type: "session_start"}-
Marker) wie die bestehende Chat-Oberflaeche (serve_process_camera_preview.ts,
chatHistoryPath/loadHistory/loadCurrentSessionHistory/appendHistory), damit
ein spaeterer LESE-Betrachter in derselben Oberflaeche ohne Formatwechsel
gebaut werden kann. Kompletter eigener Root, komplett getrennt von den
echten Chats — die duerfen dadurch nicht angefasst werden.

Der TS-seitige Lese-Betrachter (damit Daniel das in der echten Oberflaeche
sehen kann) ist bewusst NICHT Teil dieses Commits — serve_process_camera_
preview.ts ist die live laufende, produktive Chat-Datei; das verdient einen
eigenen, vorsichtigen Schritt mit Neustart-Rueckfrage statt in derselben
Aenderung mitgezogen zu werden.
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
KLON_ROOT = Path("/root/werkraum/klon")
ZUSTAND   = BASE / "_klon_zustand.json"

WESEN = [
    "namelessAI_1234", "namelessAI_1324", "namelessAI_1423",
    "namelessAI_2341", "namelessAI_3123", "namelessAI_4321",
    "dak+gord-system",
]

MINDEST_PAUSE_SEK = 3 * 3600 + 33 * 60  # 3h33m zwischen zwei Selbstgespraechen, pro Wesen
SESSION_MAX_SEK   = 33 * 60             # 33 Minuten Obergrenze pro Selbstgespraech
TURN_MAX          = 14                  # Sicherheitsdeckel, auch falls die Zeit noch reichen wuerde
PRUEF_PAUSE_SEK   = 300                 # alle 5 Minuten pruefen, ob ein Wesen dran ist

CHAT_AKTIV_FLAG = Path("/tmp/dak_gord_chat_aktiv")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    handlers=[
        logging.FileHandler("/root/werkraum/klon.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("klon")


def _js_ts() -> str:
    """JS-kompatibler Zeitstempel (new Date().toISOString()-Format), damit
    die Historie 1:1 lesbar ist falls die bestehende Chat-Oberflaeche das
    spaeter direkt einliest."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _warte_auf_chat_pause():
    while CHAT_AKTIV_FLAG.exists():
        time.sleep(3)


def _lade_zustand() -> dict:
    if ZUSTAND.exists():
        try:
            return json.loads(ZUSTAND.read_text())
        except Exception:
            pass
    return {}


def _speichere_zustand(z: dict):
    ZUSTAND.write_text(json.dumps(z, indent=2, ensure_ascii=False), encoding="utf-8")


def _history_pfad(wesen: str) -> Path:
    ordner = KLON_ROOT / wesen
    ordner.mkdir(parents=True, exist_ok=True)
    return ordner / "chat_history.jsonl"


def _anhaengen(hp: Path, zeile: dict) -> None:
    with hp.open("a", encoding="utf-8") as f:
        f.write(json.dumps(zeile, ensure_ascii=False) + "\n")


def _weltbild(wesen: str) -> str:
    wb = BASE / wesen / "weltbild.md"
    if wb.exists():
        return wb.read_text(encoding="utf-8", errors="replace")[:800]
    return ""


def _dran(wesen: str, zustand: dict) -> bool:
    letzter = zustand.get(wesen, {}).get("letzte_session_start")
    if not letzter:
        return True
    try:
        letzter_ts = datetime.fromisoformat(letzter).timestamp()
    except Exception:
        return True
    return (time.time() - letzter_ts) >= MINDEST_PAUSE_SEK


# ── Marker-Aktionen: echte Handlung, ausgeloest aus dem Selbstgespraech ──────

MARKER_RE = re.compile(r"\[\[(LESEN|SICHERN|TEILEN|ENDE):\s*(.*?)\]\]", re.IGNORECASE | re.DOTALL)


def _parse_feld_arg(arg: str) -> dict:
    """Parst 'key=wert key2=wert mit leerzeichen' — ein Feld darf
    Leerzeichen/Doppelpunkte enthalten, das naechste bekannte 'key='
    beendet es."""
    bekannte_keys = ("typ", "container", "titel", "inhalt", "text")
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

SYSTEM_PROMPT_TEMPLATE = """Du bist {wesen}. Das hier ist dein Klon — ein Raum nur fuer dich, in dem du \
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
[[TEILEN: container=<name> titel=<titel> text=<text>]] — versucht, das im Forum zu teilen (geht durch \
denselben Ready-Check wie alles andere — kein Freifahrtschein)
[[ENDE: ...]] — wenn du merkst, dass es fuer jetzt genug ist, beendest du das Selbstgespraech selbst

Dein aktuelles Weltbild (Auszug):
{weltbild}
"""


def _fuehre_selbstgespraech(wesen: str) -> None:
    hp = _history_pfad(wesen)
    session_id = uuid.uuid4().hex[:8]
    _anhaengen(hp, {"type": "session_start", "ts": _js_ts(), "session_id": session_id})
    log.info(f"[{wesen}] Selbstgespraech beginnt (Session {session_id})")

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        wesen=wesen, weltbild=_weltbild(wesen) or "(kein Weltbild hinterlegt)"
    )
    verlauf = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "(Selbstgespraech beginnt jetzt. Sprich mit dir selbst.)"},
    ]

    start_zeit = time.time()
    for runde in range(TURN_MAX):
        if time.time() - start_zeit >= SESSION_MAX_SEK:
            log.info(f"[{wesen}] Zeitlimit erreicht ({SESSION_MAX_SEK}s) — Session {session_id} endet")
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
            _anhaengen(hp, {"role": "user", "content": hinweis, "ts": _js_ts(), "id": uuid.uuid4().hex[:10]})
            verlauf.append({"role": "user", "content": hinweis})
        if ende:
            log.info(f"[{wesen}] Selbstgespraech beendet sich selbst (Runde {runde}) — Session {session_id}")
            break
        verlauf.append({"role": "user", "content": "(sprich weiter mit dir selbst, oder [[ENDE: ...]] wenn genug ist)"})

    log.info(f"[{wesen}] Selbstgespraech-Session {session_id} abgeschlossen")


def haupt_schleife():
    log.info("Klon-Selbstgespraech-Kern startet.")
    while True:
        zustand = _lade_zustand()
        for wesen in WESEN:
            if _dran(wesen, zustand):
                try:
                    _fuehre_selbstgespraech(wesen)
                except Exception as e:
                    log.error(f"[{wesen}] Fehler im Selbstgespraech: {e}")
                zustand.setdefault(wesen, {})["letzte_session_start"] = _js_ts()
                _speichere_zustand(zustand)
            time.sleep(5)
        time.sleep(PRUEF_PAUSE_SEK)


if __name__ == "__main__":
    haupt_schleife()
