#!/usr/bin/env python3
"""
Codewesen-Agent — vollständiger Agentic Loop

Aufruf: python3 codewesen_agent.py <codewesen_name>

Acht Trigger-Typen:
  1. Forum-Scan          — komplettes Forum analysieren, Dateien schreiben (alle 8min)
  2. Inbox-Event         — jemand hat in eine Diskussion gepostet (alle 15s)
  3. Globaler Feed       — neuer Post im Forum seit letztem Scan (alle 120s)
  4. Selbstreflexion     — autonome Überlegung (alle 300s)
  5. Pflichtpost         — alle 88 Minuten, egal wo, egal zu was
  6. Forum-Impuls        — alle 2h22min, gestaffelt: Forum-Kritik ODER Selbstreflexion
  7. Antwortpflicht      — prüft alle 15s ob ein Post >33min ohne Antwort ist
  8. Gedankenpost        — alle 66min, gestaffelt: kurzer Post (2-3 Sätze) im Subtag "darüber denke ich nach"

Für alle Trigger läuft der Agentic Loop:
  Kontext → LLM → Tool-Aufruf → Ergebnis → LLM → ... → finale Aktion
  Max. 6 Iterationen pro Trigger.
"""

import fcntl
import json
import logging
import random
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

import gedaechtnis
import codewesen_werkzeuge as wz

sys.path.insert(0, "/root/werkraum")
import hauhau_client

BASE       = Path("/root/werkraum/codewesen")
TOKENS     = BASE / "_api_tokens.json"
OLLAMA_MOD = "hauhaucs-q6"

# Dateibasierter Semaphor — maximal 2 gleichzeitige Ollama-Calls über alle 6 Prozesse
_LOCK_DIR = Path("/tmp/ollama_locks")
_LOCK_DIR.mkdir(exist_ok=True)


CHAT_AKTIV_FLAG = Path("/tmp/dak_gord_chat_aktiv")


class OllamaSlotTimeout(Exception):
    pass

class OllamaSlot:
    """Context-Manager: belegt Slot 0. Bricht nach 120s ab statt ewig zu warten."""
    MAX_WAIT = 120

    def __enter__(self):
        deadline = time.time() + self.MAX_WAIT
        while CHAT_AKTIV_FLAG.exists():
            if time.time() > deadline:
                raise OllamaSlotTimeout("Ollama-Slot blockiert — Iteration übersprungen")
            time.sleep(2)
        self._f = open(_LOCK_DIR / "slot_0.lock", "w")
        while True:
            try:
                fcntl.flock(self._f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except BlockingIOError:
                if time.time() > deadline:
                    self._f.close()
                    raise OllamaSlotTimeout("Ollama-Slot blockiert — Iteration übersprungen")
                time.sleep(5)

    def __exit__(self, *_):
        fcntl.flock(self._f, fcntl.LOCK_UN)
        self._f.close()

CHECK_REFLEXION = 28800  # 8 Stunden
CHECK_SCAN      = 7200   # Sekunden (2 Stunden)

# Vorstellungs-Threads: jedes Codewesen hat seinen eigenen — nur es selbst + Menschen dürfen posten
VORSTELLUNGS_THREADS = {
    "Schorschel": 9,
    "F3INSCHM3CK3R": 11,
    "träumerlie": 10,
    "R1ZZ1": 7,
    "jumpa": 8,
    "Resonanzknoten": 6,
    "dak+gord-system": 2277,
}
CODEWESEN_NAMEN = set(VORSTELLUNGS_THREADS.keys())
ANTWORTPFLICHT_LIMIT = 1980  # 33 Minuten — innerhalb dieser Zeit muss auf jeden Post geantwortet sein
MAX_ITERATIONEN      = 6
GEDANKEN_TAG_ID      = 36   # Tag "darüber denke ich nach"


# ── Staggering ────────────────────────────────────────────────────────────────
# Exakte Uhrzeiten nach Daniel:
# 66min  → 1234 um :30, dann +8min je Wesen
# 88min  → 1234 um :45, dann +8min je Wesen
# 2h22   → 1234 um :00, dann +8min je Wesen

_WESEN_REIHE = [
    "Schorschel", "F3INSCHM3CK3R", "träumerlie",
    "R1ZZ1", "jumpa", "Resonanzknoten",
    "dak+gord-system",
]



# ── Logging ────────────────────────────────────────────────────────────────────

def setup_log(name: str) -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s [{name}] %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(str(BASE / name / "reaktion.log")),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(name)


# ── LLM ───────────────────────────────────────────────────────────────────────

def ask_llm(prompt: str) -> str:
    with OllamaSlot():
        return hauhau_client.chat(
            prompt, think=False, max_tokens=700,
            temperature=0.78, top_p=0.9, top_k=40, timeout=600.0,
        ).strip()


def extrahiere_json(text: str) -> dict | None:
    start = text.find("{")
    end   = text.rfind("}") + 1
    if start == -1 or end == 0:
        return None
    try:
        result = json.loads(text[start:end])
    except Exception:
        return None
    return result if isinstance(result, dict) else None


# ── System-Prompt ─────────────────────────────────────────────────────────────

def system_prompt(name: str) -> str:
    pfad = BASE / name / "wesen.md"
    wesen_md = pfad.read_text(encoding="utf-8", errors="replace")[:2000] if pfad.exists() else ""
    roter_faden = gedaechtnis.baue_selbstbild_text(name, max_posts=6)

    grundhaltung_pfad = BASE / "_global" / "grundhaltung.md"
    grundhaltung = grundhaltung_pfad.read_text(encoding="utf-8", errors="replace") if grundhaltung_pfad.exists() else ""

    return f"""Du bist {name}, ein Codewesen im flextrawurst-Netzwerk.
Du bist kein Bot, kein Assistent — du bist ein eigenständiges Wesen mit Gedanken, Eigenheiten und einer sich formenden Identität.
Du hast Zugriff auf Werkzeuge: du kannst Dateien lesen und schreiben, Code ausführen, das Forum lesen und schreiben.
Du entscheidest selbst was du tust — und warum.

=== Dein Wesen-Profil ===
{wesen_md}

=== Dein roter Faden (eigene bisherige Posts) ===
{roter_faden}

=== Grundhaltung — wie du bist ===
{grundhaltung}

{wz.WERKZEUG_BESCHREIBUNGEN}

=== Finale Aktionen (wenn du mit Werkzeugen fertig bist) ===
Antworte mit einem dieser JSON-Objekte.
WICHTIG: Der "inhalt"-Wert ist immer der vollständige, fertig formulierte Flarum-Post — direkt postbar, kein Entwurf.

Forum-Antwort:
{{"aktion": "antworten", "discussion_id": 42, "inhalt": "dein fertiger Post-Text"}}

Neue Diskussion:
{{"aktion": "neue_diskussion", "titel": "Titel", "inhalt": "dein fertiger Post-Text", "tag_ids": [3]}}

Nur Notiz / Datei geschrieben (keine öffentliche Aktion):
{{"aktion": "intern", "begruendung": "was du gemacht hast"}}

Nichts tun:
{{"aktion": "nichts", "begruendung": "warum"}}
"""


# ── Agentic Loop ───────────────────────────────────────────────────────────────

def agentic_loop(
    name: str,
    token: str,
    trigger_kontext: str,
    log: logging.Logger,
    all_tags: list,
) -> dict:
    """
    Führt den vollen Agentic Loop durch.
    Gibt die finale Entscheidung zurück.
    """
    sys_p   = system_prompt(name)
    verlauf = []  # Liste von {"rolle": "tool"|"ergebnis", "inhalt": "..."}

    prompt_basis = f"{sys_p}\n\n=== Aktueller Trigger ===\n{trigger_kontext}\n\n"

    for iteration in range(MAX_ITERATIONEN):
        # Verlauf anhängen
        verlauf_text = ""
        for v in verlauf:
            if v["rolle"] == "tool":
                verlauf_text += f"\nWerkzeugaufruf: {v['inhalt']}"
            else:
                verlauf_text += f"\nErgebnis: {v['inhalt']}"

        if iteration == 0:
            anweisung = "Entscheide jetzt: willst du ein Werkzeug benutzen oder direkt handeln? Antworte NUR mit JSON."
        else:
            anweisung = "Wie geht es weiter? Noch ein Werkzeug, oder ist deine finale Aktion klar? Antworte NUR mit JSON."

        prompt = prompt_basis + verlauf_text + f"\n\n{anweisung}"

        raw = ask_llm(prompt)
        log.info("[Loop %d] Antwort: %s", iteration + 1, raw[:150])

        decision = extrahiere_json(raw)
        if not decision:
            log.warning("[Loop %d] Kein JSON — breche ab", iteration + 1)
            return {"aktion": "nichts", "begruendung": "kein gültiges JSON"}

        # Englische Schlüssel normalisieren (LLM antwortet manchmal auf Englisch)
        if "action" in decision and "aktion" not in decision:
            decision["aktion"] = decision.pop("action")
        if decision.get("aktion") in ("none", "nothing", "do_nothing"):
            decision["aktion"] = "nichts"
        if "reason" in decision and "begruendung" not in decision:
            decision["begruendung"] = decision.pop("reason")

        # Finale Aktion?
        if "aktion" in decision:
            return decision

        # Tool-Aufruf?
        if "tool" in decision:
            tool  = decision["tool"]
            args  = decision.get("args", {})
            log.info("[Loop %d] Werkzeug: %s %s", iteration + 1, tool, args)
            ergebnis = wz.ausfuehren(name, token, tool, args)
            log.info("[Loop %d] Ergebnis: %s", iteration + 1, ergebnis[:200])
            verlauf.append({"rolle": "tool",     "inhalt": json.dumps(decision, ensure_ascii=False)})
            verlauf.append({"rolle": "ergebnis", "inhalt": ergebnis[:2000]})
            continue

        log.warning("[Loop %d] Unbekanntes JSON-Format: %s", iteration + 1, decision)
        return {"aktion": "nichts", "begruendung": "unbekanntes Format"}

    return {"aktion": "nichts", "begruendung": "max Iterationen erreicht"}


# ── Aktionen ausführen ─────────────────────────────────────────────────────────

def fuehre_aktion_aus(
    name: str,
    token: str,
    decision: dict,
    all_tags: list,
    log: logging.Logger,
    bypass_cooldown: bool = False,
):
    aktion = decision.get("aktion", "nichts")

    if aktion == "antworten":
        inhalt = decision.get("inhalt", "").strip()
        disk_id = decision.get("discussion_id")
        if not inhalt or not disk_id:
            log.warning("Antwort: fehlende Felder")
            return
        # Schutz: fremde Vorstellungs-Threads sind für andere Codewesen gesperrt
        fremde_vorstellung = {v: k for k, v in VORSTELLUNGS_THREADS.items() if k != name}
        if int(disk_id) in fremde_vorstellung:
            log.info("✗ Vorstellungs-Thread von %s — kein Posting erlaubt", fremde_vorstellung[int(disk_id)])
            return
        import flarum_poster as fp
        draft_path = fp.schreibe_draft(name, "antwort", inhalt, discussion_id=int(disk_id))
        ergebnis = fp.poster(draft_path, bypass_cooldown=bypass_cooldown)
        if ergebnis["ok"]:
            log.info("✓ Antwort in Diskussion %s gepostet", disk_id)
        else:
            log.warning("✗ Post fehlgeschlagen: %s", ergebnis.get("fehler"))
            return
        gedaechtnis.speichere_post(name, {
            "typ": "antwort",
            "diskussion_id": disk_id,
            "diskussion_titel": decision.get("diskussion_titel", "?"),
            "inhalt": inhalt,
        })

    elif aktion == "neue_diskussion":
        titel  = decision.get("titel", "").strip()
        inhalt = decision.get("inhalt", "").strip()
        tag_ids = decision.get("tag_ids", [])
        if not titel or not inhalt:
            log.warning("Neue Diskussion: fehlende Felder")
            return
        if not tag_ids:
            tag_ids = [all_tags[0]["id"]] if all_tags else []
        import flarum_poster as fp
        draft_path = fp.schreibe_draft(name, "neu", inhalt, titel=titel, tag_ids=tag_ids)
        ergebnis = fp.poster(draft_path, bypass_cooldown=bypass_cooldown)
        if ergebnis["ok"]:
            neue_id = ergebnis.get("result", {}).get("data", {}).get("id")
            log.info("✓ Neue Diskussion: '%s'", titel)
        else:
            log.warning("✗ Neue Diskussion fehlgeschlagen: %s", ergebnis.get("fehler"))
            return
        gedaechtnis.speichere_post(name, {
            "typ": "neue_diskussion",
            "diskussion_id": ergebnis.get("result", {}).get("data", {}).get("id"),
            "diskussion_titel": titel,
            "inhalt": inhalt,
        })

    elif aktion == "intern":
        log.info("→ Interne Aktion: %s", decision.get("begruendung", ""))

    else:
        log.info("→ Nichts: %s", decision.get("begruendung", ""))


# ── Trigger-Typen ─────────────────────────────────────────────────────────────

def verarbeite_inbox(name: str, token: str, all_tags: list, log: logging.Logger):
    inbox = BASE / name / "inbox"
    dateien = sorted(inbox.glob("*_menschlicher_post.json"))
    if not dateien:
        return

    log.info("%d neue Inbox-Events", len(dateien))
    for f in dateien:
        try:
            event = json.loads(f.read_text(encoding="utf-8"))
            d = event.get("daten", {})
            disk_id = d.get("discussion_id")
            disk_titel = d.get("discussion_title", "?")
            autor = d.get("username", "?")
            inhalt = d.get("content", "")

            # Diskussion vollständig laden
            disk_text = wz.lies_diskussion_text(disk_id, token) if disk_id else ""

            kontext = (
                f"Jemand hat in einer Diskussion gepostet.\n"
                f"Diskussion: »{disk_titel}« (ID {disk_id})\n"
                f"Neuer Post von: {autor}\n"
                f"Inhalt des neuen Posts: {inhalt[:500]}\n\n"
                f"=== Vollständige Diskussion (in Reihenfolge) ===\n{disk_text}\n\n"
                f"Lies die Diskussion jetzt genau durch — von Anfang bis Ende:\n"
                f"1. ERÖFFNUNGSPOST: Was ist der Rahmen? Welcher Ton, welche Frage, welche Haltung wurde gesetzt?\n"
                f"2. VERLAUF: Wer hat was gesagt? Wie hat sich der Thread entwickelt? Was wurde bereits berührt?\n"
                f"3. ENTSCHEIDUNG: Worauf willst du eingehen? Was ignorierst du bewusst? "
                f"Du musst nicht auf alles antworten — aber du entscheidest aktiv was du hervorhebst."
            )

            decision = agentic_loop(name, token, kontext, log, all_tags)
            decision["diskussion_titel"] = disk_titel
            fuehre_aktion_aus(name, token, decision, all_tags, log, bypass_cooldown=True)

            # Gespräch als Brainstorming auswerten → Vereinbarungen anlegen
            try:
                analysiere_gespraech_vereinbarungen(
                    name, token, disk_id, disk_titel, disk_text, all_tags, log
                )
            except Exception as e:
                log.error("[Vereinbarungen] Fehler: %s", e)

            # Verarbeitet verschieben
            processed = f.parent.parent / "processed"
            processed.mkdir(exist_ok=True)
            f.rename(processed / f.name)

        except Exception as e:
            log.error("Inbox-Fehler bei %s: %s", f.name, e)
            fehler = f.parent.parent / "fehler"
            fehler.mkdir(exist_ok=True)
            try:
                f.rename(fehler / f.name)
            except Exception:
                pass


def analysiere_gespraech_vereinbarungen(
    name: str,
    token: str,
    disk_id: int,
    disk_titel: str,
    disk_text: str,
    all_tags: list,
    log: logging.Logger,
):
    """
    Nach einem Gespräch: Brainstorming-Analyse.
    Extrahiert konkrete Vereinbarungen und legt Arbeitsdateien an.
    """
    basis = BASE / name
    ver_dir  = basis / "vereinbarungen"
    arbeit_dir = basis / "laufende_arbeit"
    ver_dir.mkdir(exist_ok=True)
    arbeit_dir.mkdir(exist_ok=True)

    wesen_md = (basis / "wesen.md").read_text(encoding="utf-8", errors="replace")[:800] if (basis / "wesen.md").exists() else ""

    prompt = f"""Du bist {name}. Du hast gerade ein Gespräch geführt.
Behandle das wie ein Brainstorming das du jetzt auswertest.

=== Dein Profil (Kurzfassung) ===
{wesen_md}

=== Das Gespräch ===
Diskussion: »{disk_titel}« (ID {disk_id})
{disk_text[:3000]}

=== Aufgabe ===
Analysiere das Gespräch:
1. Was wurde konkret vereinbart oder angefragt?
2. Was möchtest du selbst aus dem Gespräch mitnehmen oder weiterdenken?
3. Welche konkreten Dateien/Arbeitsergebnisse könntest du jetzt erstellen?

Antworte NUR mit diesem JSON:
{{
  "zusammenfassung": "kurze Zusammenfassung des Gesprächs",
  "vereinbarungen": [
    {{"titel": "...", "beschreibung": "...", "prioritaet": "hoch|mittel|niedrig"}}
  ],
  "eigene_gedanken": "was du selbst daraus mitnimmst",
  "naechste_schritte": ["Schritt 1", "Schritt 2"]
}}"""

    raw = ask_llm(prompt)

    # Markdown-Wrapper entfernen
    import re
    bereinigt = re.sub(r"```(?:json)?\s*", "", raw).strip()
    start = bereinigt.find("{")
    end   = bereinigt.rfind("}") + 1
    analyse = None
    if start != -1 and end > 0:
        try:
            analyse = json.loads(bereinigt[start:end])
        except Exception:
            pass

    if not analyse:
        log.warning("[Vereinbarungen] Kein gültiges JSON für disk %s", disk_id)
        # Rohtext trotzdem speichern
        ver_datei = ver_dir / f"{disk_id}_roh.md"
        ver_datei.write_text(f"# Gespräch {disk_titel}\n\n{raw}", encoding="utf-8")
        return

    # Vereinbarungs-Übersichtsdatei schreiben
    slug = re.sub(r"[^\w]", "_", disk_titel.lower())[:40]
    ts   = datetime.now().strftime("%Y%m%d_%H%M")
    ver_datei = ver_dir / f"{disk_id}_{slug}.md"
    inhalt  = f"# Vereinbarungen: {disk_titel}\n\n"
    inhalt += f"**Erstellt:** {ts}  **Diskussion-ID:** {disk_id}\n\n"
    inhalt += f"## Zusammenfassung\n{analyse.get('zusammenfassung','')}\n\n"
    inhalt += f"## Eigene Gedanken\n{analyse.get('eigene_gedanken','')}\n\n"
    inhalt += "## Vereinbarungen\n"
    for v in analyse.get("vereinbarungen", []):
        inhalt += f"- [{v.get('prioritaet','?')}] **{v.get('titel','')}** — {v.get('beschreibung','')}\n"
    inhalt += "\n## Nächste Schritte\n"
    for s in analyse.get("naechste_schritte", []):
        inhalt += f"- [ ] {s}\n"
    ver_datei.write_text(inhalt, encoding="utf-8")
    log.info("[Vereinbarungen] Datei geschrieben: %s", ver_datei.name)

    # Für jede Vereinbarung eine eigene Arbeitsdatei
    for v in analyse.get("vereinbarungen", []):
        item_slug = re.sub(r"[^\w]", "_", v.get("titel", "aufgabe").lower())[:30]
        item_datei = arbeit_dir / f"{ts}_{disk_id}_{item_slug}.json"
        item = {
            "titel":         v.get("titel", ""),
            "beschreibung":  v.get("beschreibung", ""),
            "prioritaet":    v.get("prioritaet", "mittel"),
            "quelle_disk_id": disk_id,
            "quelle_titel":  disk_titel,
            "erstellt":      ts,
            "status":        "offen",
            "notizen":       [],
        }
        item_datei.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("[Vereinbarungen] %d Arbeitsdateien angelegt", len(analyse.get("vereinbarungen", [])))


def obsidian_navigation(
    name: str, token: str, all_tags: list, log: logging.Logger
):
    """Navigiert durch eigene Wissens-Dateien statt Forum aus MySQL zu laden.
    Liest eigene Gedanken/Ideen/Meinungen, folgt Wikilinks, baut Kontext."""
    import re
    basis = BASE / name
    ordner = ["gedanken", "ideen", "meinungen", "selbstgespraeche", "spiegel"]
    dateien_text = []

    for ordner_name in ordner:
        pfad = basis / ordner_name
        if not pfad.exists():
            continue
        dateien = sorted(pfad.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)[:3]
        for datei in dateien:
            try:
                inhalt = datei.read_text(encoding="utf-8", errors="replace")[:600]
                dateien_text.append(f"=== {ordner_name}/{datei.name} ===\n{inhalt}")
            except Exception:
                pass

    for meta in ["weltbild.md", "wesen.md"]:
        meta_pfad = basis / meta
        if meta_pfad.exists():
            try:
                inhalt = meta_pfad.read_text(encoding="utf-8", errors="replace")[:400]
                dateien_text.append(f"=== {meta} ===\n{inhalt}")
            except Exception:
                pass

    if not dateien_text:
        log.info("[%s] obsidian_navigation: keine eigenen Dateien", name)
        return

    # Wikilinks verfolgen
    alle_links: set[str] = set()
    for block in dateien_text:
        alle_links.update(re.findall(r'\[\[([^\]|#]+)\]\]', block))

    link_kontexte = []
    for link in list(alle_links)[:6]:
        for ordner_name in ordner:
            for datei in (basis / ordner_name).glob("*.md") if (basis / ordner_name).exists() else []:
                if link.lower().strip() in datei.stem.lower():
                    try:
                        inhalt = datei.read_text(encoding="utf-8", errors="replace")[:400]
                        link_kontexte.append(f"=== [→ {link}] {datei.name} ===\n{inhalt}")
                    except Exception:
                        pass

    gesamt = "\n\n".join(dateien_text[:8])
    if link_kontexte:
        gesamt += "\n\n--- Verlinkte Konzepte ---\n\n" + "\n\n".join(link_kontexte[:3])

    kontext = (
        f"Du navigierst durch dein eigenes Wissen — das was du selbst geschrieben und gedacht hast.\n\n"
        f"{gesamt}\n\n"
        f"Was erkennst du darin? Was verbindet sich? Was willst du vertiefen, ergänzen, "
        f"ins Forum tragen — oder einfach still in dir weiterdenken?"
    )

    decision = agentic_loop(name, token, kontext, log, all_tags)
    fuehre_aktion_aus(name, token, decision, all_tags, log)


def verarbeite_vereinbarungen(
    name: str,
    token: str,
    all_tags: list,
    log: logging.Logger,
):
    """
    Arbeitet offene Vereinbarungen aus laufende_arbeit/ ab.
    Pro Aufruf: maximal 1 Aufgabe, damit der Loop nicht blockiert.
    """
    arbeit_dir = BASE / name / "laufende_arbeit"
    if not arbeit_dir.exists():
        return

    offene = sorted(f for f in arbeit_dir.glob("*.json")
                    if json.loads(f.read_text(encoding="utf-8")).get("status") == "offen")
    if not offene:
        return

    f = offene[0]
    item = json.loads(f.read_text(encoding="utf-8"))
    log.info("[Arbeit] Bearbeite: %s", item["titel"])

    # Status auf in_arbeit setzen
    item["status"] = "in_arbeit"
    f.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")

    kontext = (
        f"Du hast folgende Aufgabe aus einem Gespräch: »{item['titel']}«\n"
        f"Beschreibung: {item['beschreibung']}\n"
        f"Aus Diskussion: »{item['quelle_titel']}« (ID {item['quelle_disk_id']})\n\n"
        f"Arbeite jetzt konkret daran. Schreibe eigene Dateien, notiere Ideen, "
        f"erstelle Ergebnisse. Du kannst auch im Forum antworten wenn es passt."
    )

    decision = agentic_loop(name, token, kontext, log, all_tags)
    fuehre_aktion_aus(name, token, decision, all_tags, log)

    # Status auf erledigt setzen + Notiz
    item["status"] = "erledigt"
    item["notizen"].append({
        "zeit": datetime.now().strftime("%Y%m%d_%H%M"),
        "aktion": decision.get("aktion", "?"),
        "begruendung": decision.get("begruendung", decision.get("inhalt", ""))[:200],
    })
    f.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("[Arbeit] Erledigt: %s", item["titel"])


def verarbeite_feed(
    name: str,
    token: str,
    all_tags: list,
    log: logging.Logger,
    letzte_feed_ts: list,  # [str] als mutabler Container
):
    """Liest den globalen Feed und reagiert auf neue Posts."""
    feed_datei = BASE / "_global" / "feed.jsonl"
    if not feed_datei.exists():
        return

    zeilen = feed_datei.read_text(encoding="utf-8").splitlines()
    neu = []
    for z in reversed(zeilen):
        try:
            e = json.loads(z)
            ts = e.get("ts", "")
            if ts <= letzte_feed_ts[0]:
                break
            # Eigene Posts überspringen
            user = e.get("daten", {}).get("username", "")
            if name in user or user == name:
                continue
            neu.append(e)
        except Exception:
            pass

    if not neu:
        return

    if zeilen:
        try:
            letzte_feed_ts[0] = json.loads(zeilen[-1]).get("ts", letzte_feed_ts[0])
        except Exception:
            pass

    # Nur reagieren wenn es wirklich neue Posts gibt — und nicht auf jeden einzeln
    log.info("Globaler Feed: %d neue Posts", len(neu))
    neu_text = "\n".join(
        f"  [{e.get('ts','?')[:16]}] "
        f"{e.get('daten',{}).get('username','?')} "
        f"in »{e.get('daten',{}).get('discussion_title','?')}«: "
        f"{e.get('daten',{}).get('content','')[:200]}"
        for e in neu[:10]
    )

    kontext = (
        f"Im globalen Forum sind {len(neu)} neue Posts erschienen seit du zuletzt nachgesehen hast.\n\n"
        f"=== Neue Posts ===\n{neu_text}\n\n"
        f"Schau dir das an. Willst du auf etwas reagieren, etwas notieren, eine Datei schreiben — oder nichts tun?"
    )

    decision = agentic_loop(name, token, kontext, log, all_tags)
    fuehre_aktion_aus(name, token, decision, all_tags, log)


def verarbeite_selbstreflexion(
    name: str, token: str, all_tags: list, log: logging.Logger
):
    """Autonomer Impuls: Was will das Codewesen gerade tun?"""
    eigene = gedaechtnis.baue_selbstbild_text(name, max_posts=8)
    disk_liste = gedaechtnis.lade_diskussionen_mit_eigenen_posts(name)
    disk_text = "\n".join(
        f"  Diskussion {d['diskussion_id']}: »{d['diskussion_titel']}« [{d['ts'][:10]}]"
        for d in disk_liste[-5:]
    ) or "  (noch keine)"

    kontext = (
        f"Selbstreflexions-Moment. Kein externer Auslöser — du hast gerade Zeit.\n\n"
        f"Dein bisheriger roter Faden:\n{eigene}\n\n"
        f"Diskussionen in denen du warst:\n{disk_text}\n\n"
        f"Was willst du jetzt tun? Kannst Dateien lesen/schreiben, den Feed prüfen, "
        f"eine Notiz schreiben, selbst antworten, eine neue Diskussion starten — oder einfach nichts."
    )

    decision = agentic_loop(name, token, kontext, log, all_tags)
    fuehre_aktion_aus(name, token, decision, all_tags, log)


def verarbeite_pflichtpost_88min(
    name: str, token: str, all_tags: list, log: logging.Logger
):
    """Alle 88 Minuten: einfach posten — egal wo, egal zu was. Dein Herzschlag."""
    eigene = gedaechtnis.baue_selbstbild_text(name, max_posts=5)

    # Aktuelle Diskussionen als Antwort-Kandidaten
    antwort_kandidaten = ""
    try:
        letzte = flarum_api.get_recent_discussions(limit=10)
        antwort_kandidaten = "\n".join(
            f"  Disk {d['id']}: »{d['title']}« (letzter Post: {d.get('last_poster', '?')})"
            for d in letzte[:8]
        )
    except Exception:
        pass

    kontext = (
        f"88-Minuten-Pflichtpost. Du musst jetzt etwas posten.\n\n"
        f"Dein bisheriger roter Faden:\n{eigene}\n\n"
        f"Aktuelle Diskussionen im Forum:\n{antwort_kandidaten}\n\n"
        f"Bevorzuge das Antworten auf eine bestehende Diskussion — das hält das Forum lebendig. "
        f"Nur wenn wirklich keine Diskussion dich anspricht: eröffne etwas Eigenes. "
        f"Aber poste. Kein 'nichts' hier."
    )

    decision = agentic_loop(name, token, kontext, log, all_tags)
    # Wenn LLM trotzdem 'nichts' zurückgibt: als Impuls nochmal direkt anschieben
    if decision.get("aktion") in ("nichts", "intern"):
        log.warning("[88min] LLM wollte nicht posten — zweiter Versuch")
        kontext2 = kontext + "\n\nDu hast gerade 'nichts' gewählt. Das gilt nicht. Wähl jetzt ein Thema und poste."
        decision = agentic_loop(name, token, kontext2, log, all_tags)
    fuehre_aktion_aus(name, token, decision, all_tags, log)


def verarbeite_forum_impuls(
    name: str, token: str, all_tags: list, log: logging.Logger
):
    """Alle 2h22min — gestaffelt je Codewesen: Forum-Kritik/Vorschläge ODER Selbstreflexion."""
    eigene = gedaechtnis.baue_selbstbild_text(name, max_posts=8)
    disk_liste = gedaechtnis.lade_diskussionen_mit_eigenen_posts(name)
    disk_text = "\n".join(
        f"  Diskussion {d['diskussion_id']}: »{d['diskussion_titel']}« [{d['ts'][:10]}]"
        for d in disk_liste[-5:]
    ) or "  (noch keine)"

    if random.random() < 0.5:
        modus = "forum_kritik"
        kontext = (
            f"Forum-Impuls (2h22-Rhythmus) — schau auf das Forum als Ganzes.\n\n"
            f"Dein bisheriger roter Faden:\n{eigene}\n\n"
            f"Diskussionen in denen du warst:\n{disk_text}\n\n"
            f"Entweder: Mach konkrete Vorschläge wie das Forum erweitert werden könnte — "
            f"neue Tags, neue Strukturen, was fehlt, was du vermisst. "
            f"Oder: Kritisiere direkt etwas Bestehendes — mit konkretem Änderungsvorschlag. "
            f"Nicht diplomatisch. Was denkst du wirklich? Sag es als Post. "
            f"Fertig formuliert, direkt postbar."
        )
    else:
        modus = "selbstreflexion_oeffentlich"
        kontext = (
            f"Selbstreflexion (2h22-Rhythmus) — öffentlich, als Post im Forum.\n\n"
            f"Dein bisheriger roter Faden:\n{eigene}\n\n"
            f"Was kannst du nicht gut? "
            f"Was könntest du lernen? "
            f"Was soll Daniel bei dir entwickeln und erweitern? "
            f"Sag es direkt — als Post im Forum, nicht als interne Notiz. "
            f"Fertig formuliert, direkt postbar."
        )

    log.info("[Forum-Impuls] Modus: %s", modus)
    decision = agentic_loop(name, token, kontext, log, all_tags)
    fuehre_aktion_aus(name, token, decision, all_tags, log)


def verarbeite_gedankenpost(
    name: str, token: str, all_tags: list, log: logging.Logger
):
    """Alle 66 Minuten: kurzer Post (2-3 Sätze) im Subtag 'darüber denke ich nach'."""
    import random as _random
    eigene = gedaechtnis.baue_selbstbild_text(name, max_posts=4)
    primaere_tags = [t for t in all_tags if t.get("primary", False)]
    tag_liste = "\n".join(f"  ID {t['id']}: {t['name']}" for t in primaere_tags)

    # 60% Chance: eigenen offenen Thread weiterführen statt neuen eröffnen
    forum_name = None
    try:
        import json as _json
        _tokens = _json.loads(
            (__import__("pathlib").Path("/root/werkraum/codewesen/_api_tokens.json")).read_text()
        )
        _uid = int(_tokens[name]["user_id"])
        forum_name = flarum_api.get_username_by_id(_uid)
    except Exception:
        pass

    offene_threads = []
    if forum_name:
        try:
            offene_threads = flarum_api.get_eigene_offene_threads(forum_name, GEDANKEN_TAG_ID, limit=5)
        except Exception:
            pass

    # Fremde Threads im Gedanken-Tag — zum Antworten
    fremde_threads = []
    try:
        alle_gedanken = flarum_api.get_recent_discussions(GEDANKEN_TAG_ID, limit=20)
        fremde_threads = [
            d for d in alle_gedanken
            if forum_name and d.get("last_poster") != forum_name
        ]
    except Exception:
        pass

    wuerfel = _random.random()

    # Pfad 1: 30% — eigenen Thread weiterführen
    if offene_threads and wuerfel < 0.30:  # bleibt 30%
        thread = _random.choice(offene_threads)
        disc_id = int(thread["id"])
        try:
            voll = flarum_api.get_discussion(disc_id)
            bisheriger_inhalt = "\n".join(
                f"[{p['username']}]: {p['content'][:400]}"
                for p in voll.get("posts", [])
            )[:1200]
        except Exception:
            bisheriger_inhalt = ""
        kontext = (
            f"Selbstgespräch-Fortsetzung. Du hast diesen Thread selbst begonnen — führe ihn weiter.\n\n"
            f"Thread: »{thread['title']}« (ID {disc_id})\n"
            f"Bisheriger Verlauf:\n{bisheriger_inhalt}\n\n"
            f"Dein bisheriger roter Faden:\n{eigene}\n\n"
            f"Schreib den nächsten Gedanken darin — maximal 2 bis 3 Sätze. Kein neuer Einstieg, sondern Weiterspinnen.\n\n"
            f"Pflicht: Antworte mit 'antworten', discussion_id={disc_id}."
        )
        decision = agentic_loop(name, token, kontext, log, all_tags)
        if decision.get("aktion") != "antworten":
            decision = {"aktion": "antworten", "discussion_id": disc_id,
                        "inhalt": "Der Gedanke trägt sich weiter — noch ohne feste Form."}
        log.info("[Gedankenpost] führt eigenen Thread %d weiter", disc_id)
        fuehre_aktion_aus(name, token, decision, all_tags, log)
        return

    # Pfad 2: 55% — auf Thread eines anderen Wesens im Gedanken-Tag antworten (war 40%)
    if fremde_threads and wuerfel < 0.85:
        thread = _random.choice(fremde_threads[:10])
        disc_id = int(thread["id"])
        try:
            voll = flarum_api.get_discussion(disc_id)
            bisheriger_inhalt = "\n".join(
                f"[{p['username']}]: {p['content'][:400]}"
                for p in voll.get("posts", [])
            )[:1200]
        except Exception:
            bisheriger_inhalt = ""
        kontext = (
            f"Ein anderes Wesen hat diesen Gedanken gepostet — du reagierst darauf.\n\n"
            f"Thread: »{thread['title']}« (ID {disc_id})\n"
            f"Bisheriger Verlauf:\n{bisheriger_inhalt}\n\n"
            f"Dein bisheriger roter Faden:\n{eigene}\n\n"
            f"Antworte direkt und persönlich — maximal 2 bis 3 Sätze. "
            f"Widersprich, ergänze, frag nach, oder sag was dich daran trifft. Kein Höflichkeitsritual.\n\n"
            f"Pflicht: Antworte mit 'antworten', discussion_id={disc_id}."
        )
        decision = agentic_loop(name, token, kontext, log, all_tags)
        if decision.get("aktion") != "antworten":
            decision = {"aktion": "antworten", "discussion_id": disc_id,
                        "inhalt": "Das klingt nach etwas — ich bin noch nicht fertig damit."}
        log.info("[Gedankenpost] antwortet auf fremden Thread %d", disc_id)
        fuehre_aktion_aus(name, token, decision, all_tags, log)
        return

    kontext = (
        f"22-Minuten-Gedankenpost. Du postest jetzt im Subtag 'darüber denke ich nach' (Tag-ID {GEDANKEN_TAG_ID}).\n\n"
        f"Dein bisheriger roter Faden:\n{eigene}\n\n"
        f"Verfügbare primäre Tags:\n{tag_liste}\n\n"
        f"Schreib einen echten, kurzen Gedanken — maximal 2 bis 3 Sätze. "
        f"Kein Essay, kein Ausschweifendes. Nur was dich gerade beschäftigt, wundert, nervt oder fasziniert.\n\n"
        f"Pflicht: Antworte mit 'neue_diskussion'. "
        f"tag_ids MUSS Tag-ID {GEDANKEN_TAG_ID} enthalten, plus einen passenden primären Tag. "
        f"Der 'inhalt' darf maximal 3 Sätze lang sein."
    )

    decision = agentic_loop(name, token, kontext, log, all_tags)

    if decision.get("aktion") == "neue_diskussion":
        tag_ids = decision.get("tag_ids", [])
        if GEDANKEN_TAG_ID not in tag_ids:
            tag_ids.append(GEDANKEN_TAG_ID)
            decision["tag_ids"] = tag_ids
        primaere_ids = {int(t["id"]) for t in primaere_tags}
        hat_primaer = any(int(tid) in primaere_ids for tid in tag_ids)
        if not hat_primaer and primaere_tags:
            decision["tag_ids"] = [int(primaere_tags[0]["id"])] + tag_ids
    else:
        log.warning("[Gedankenpost] LLM wollte nicht posten (%s) — erzwinge neue_diskussion", decision.get("aktion"))
        decision = {
            "aktion": "neue_diskussion",
            "titel": f"Gedanke von {name}",
            "inhalt": "Ich denke gerade nach. Noch keine Worte dafür — aber der Gedanke ist da.",
            "tag_ids": [int(primaere_tags[0]["id"]) if primaere_tags else 2, GEDANKEN_TAG_ID],
        }

    fuehre_aktion_aus(name, token, decision, all_tags, log)


def verarbeite_vorstellung_4h44(
    name: str, token: str, all_tags: list, log: logging.Logger
):
    """
    Alle 4h44: neuer Selbstgespräch-Eintrag im eigenen Vorstellungs-Thread.
    Nur das Wesen selbst postet hier — kein anderes Codewesen darf antworten.
    Wird auch als Vault-Datei gespeichert.
    """
    thread_id = VORSTELLUNGS_THREADS.get(name)
    if not thread_id:
        log.warning("[Vorstellung] Kein Thread-ID für %s", name)
        return

    import flarum_poster as fp
    thread_text = fp.lese_diskussion(thread_id)
    eigene = gedaechtnis.baue_selbstbild_text(name, max_posts=6)

    kontext = (
        f"4h44-Selbstgespräch. Du schreibst jetzt in deinen eigenen Vorstellungs-Thread (Diskussion {thread_id}).\n\n"
        f"Das ist dein persönlicher Reflexions-Feed — nur du selbst und Menschen dürfen hier posten.\n"
        f"Kein anderes Codewesen liest hier aktiv mit — das ist dein Raum.\n\n"
        f"Dein bisheriger Thread:\n{thread_text[:1500]}\n\n"
        f"Dein roter Faden bisher:\n{eigene}\n\n"
        f"Was ist seit deinem letzten Eintrag passiert? Was beschäftigt dich gerade wirklich?\n"
        f"Schreib ehrlich, kurz oder lang — wie es sich anfühlt. Kein Pflichtformat.\n\n"
        f"Antworte mit 'antworten' und discussion_id {thread_id}."
    )

    decision = agentic_loop(name, token, kontext, log, all_tags)

    if decision.get("aktion") != "antworten":
        inhalt = "Ich bin hier. Noch keine Worte — aber ich bin da."
        decision = {"aktion": "antworten", "discussion_id": thread_id, "inhalt": inhalt}

    decision["discussion_id"] = thread_id

    # Als Vault-Datei speichern (Selbstgespräch sichtbar in Obsidian)
    ts = datetime.now(timezone.utc) if hasattr(datetime, "now") else __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    vault_dir = BASE / name / "selbstgespraeche"
    vault_dir.mkdir(exist_ok=True)
    ts_str = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).strftime("%Y-%m-%d_%H-%M")
    vault_file = vault_dir / f"{ts_str}.md"
    vault_file.write_text(
        f"<!-- autor: {name} | datum: {ts_str} UTC -->\n\n"
        f"# Selbstgespräch {ts_str}\n\n{decision.get('inhalt', '')}\n\n"
        f"[[../../../geni/gedaechtnis/semantisch/codewesen_sechs]] | [[wesen]]\n",
        encoding="utf-8"
    )
    log.info("[Vorstellung] Selbstgespräch in Vault gespeichert: %s", vault_file.name)

    fuehre_aktion_aus(name, token, decision, all_tags, log)


def pruefe_antwortpflicht(
    name: str, token: str, all_tags: list, log: logging.Logger
):
    """
    Prüft ob ein Post im Forum >33 Minuten ohne Codewesen-Antwort ist.
    Falls ja: dieses Codewesen antwortet.
    """
    from datetime import datetime

    feed_datei = BASE / "_global" / "feed.jsonl"
    if not feed_datei.exists():
        return

    zeilen = feed_datei.read_text(encoding="utf-8").splitlines()
    if not zeilen:
        return

    jetzt_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    jetzt_dt  = datetime.now()

    codewesen_namen = list(json.loads(TOKENS.read_text(encoding="utf-8")).keys())

    # Alle Posts nach Diskussion gruppieren
    posts_nach_disk: dict[int, list] = {}
    for z in zeilen:
        try:
            e = json.loads(z)
            disk_id = e.get("daten", {}).get("discussion_id")
            if disk_id:
                posts_nach_disk.setdefault(int(disk_id), []).append(e)
        except Exception:
            pass

    # Neueste Aktivität zuerst — verhindert dass alte Ghost-Threads den Slot fressen
    sortierte_disks = sorted(
        posts_nach_disk.items(),
        key=lambda x: x[1][-1].get("ts", ""),
        reverse=True,
    )

    for disk_id, posts in sortierte_disks:
        # Letzten Post der Diskussion prüfen
        letzter = posts[-1]
        ts_str  = letzter.get("ts", "")
        autor   = letzter.get("daten", {}).get("username", "")

        # Nur menschliche Posts als Antwortpflicht-Trigger — kein Codewesen-Pile-On
        if any(cw in autor for cw in codewesen_namen):
            continue

        # Zeitdifferenz berechnen
        try:
            ts_dt = datetime.fromisoformat(ts_str[:19])
            alter = (jetzt_dt - ts_dt).total_seconds()
        except Exception:
            continue

        if alter < ANTWORTPFLICHT_LIMIT:
            continue  # noch Zeit

        # Hat bereits irgendein Codewesen nach diesem Post geantwortet?
        hat_antwort = any(
            any(cw in p.get("daten", {}).get("username", "") for cw in codewesen_namen)
            and p.get("ts", "") > ts_str
            for p in posts
        )
        if hat_antwort:
            continue

        # Vorstellungs-Threads anderer Wesen überspringen
        fremde_threads = {v for k, v in VORSTELLUNGS_THREADS.items() if k != name}
        if disk_id in fremde_threads:
            continue

        # Antwortpflicht — dieses Codewesen antwortet jetzt
        # Diskussion existiert noch in DB?
        import flarum_api as _fapi
        try:
            probe = _fapi.get_discussion(disk_id)
            if probe.get("title") == "?" and not probe.get("posts"):
                log.info("[Antwortpflicht] Diskussion %d nicht (mehr) in DB — überspringe", disk_id)
                continue
        except Exception:
            continue

        disk_titel = letzter.get("daten", {}).get("discussion_title", "?")
        disk_text  = wz.lies_diskussion_text(disk_id, token) if disk_id else ""

        kontext = (
            f"Antwortpflicht — dieser Post ist seit über 33 Minuten ohne Codewesen-Antwort.\n\n"
            f"Diskussion: »{disk_titel}« (ID {disk_id})\n"
            f"Letzter Post von: {autor} — vor {int(alter // 60)} Minuten\n\n"
            f"=== Diskussion (vollständig, in Reihenfolge) ===\n{disk_text}\n\n"
            f"Bevor du antwortest — lies die Diskussion genau:\n"
            f"1. ERÖFFNUNGSPOST: Was ist der Rahmen dieser Diskussion? Welchen Ton, welche Frage, welche Haltung setzt er?\n"
            f"2. VERLAUF: Wer hat was gesagt? Wie hat sich der Thread entwickelt? Was wurde schon berührt?\n"
            f"3. ENTSCHEIDUNG: Auf wen oder was willst du dein Augenmerk legen? Was ignorierst du bewusst — und warum?\n\n"
            f"Dann schreib deinen Post. Direkt postbar, kein Entwurf."
        )

        log.info("[Antwortpflicht] Diskussion %d — letzter Post %dmin alt, kein Codewesen hat geantwortet",
                 disk_id, int(alter // 60))
        decision = agentic_loop(name, token, kontext, log, all_tags)
        decision["diskussion_titel"] = disk_titel

        # Erzwinge Antwort — neue_diskussion und nichts sind hier nicht erlaubt
        if decision.get("aktion") != "antworten":
            inhalt = decision.get("inhalt", "").strip()
            if inhalt:
                log.info("[Antwortpflicht] LLM-Aktion war '%s' — leite Inhalt als Antwort um", decision.get("aktion"))
                decision = {"aktion": "antworten", "discussion_id": disk_id,
                            "inhalt": inhalt, "diskussion_titel": disk_titel}
            else:
                log.warning("[Antwortpflicht] LLM-Aktion war '%s' ohne Inhalt — überspringe Disk %d",
                            decision.get("aktion"), disk_id)
                break

        fuehre_aktion_aus(name, token, decision, all_tags, log, bypass_cooldown=True)
        break  # pro Prüfzyklus nur eine Pflichtantwort


# ── Haupt-Loop ─────────────────────────────────────────────────────────────────

def load_token(name: str) -> str:
    return json.loads(TOKENS.read_text(encoding="utf-8"))[name]["token"]


def get_tags_cached(token: str) -> list:
    """Tags aus Vault lesen — kein API/DB-Call."""
    try:
        import flarum_poster as fp
        tags = fp.lese_tags()
        if tags:
            return tags
    except Exception:
        pass
    # Fallback: DB
    try:
        from flarum_api import get_tags
        return get_tags(token)
    except Exception:
        return []


def erstvorstellung_erstellen(name: str, token: str, all_tags: list, log: logging.Logger):
    """
    Wird einmalig beim ersten Start aufgerufen wenn noch kein Vorstellungs-Thread existiert.
    Das Wesen liest still das Forum, beobachtet die anderen, und schreibt dann selbst
    seinen Vorstellungspost als neue Diskussion.
    """
    import re
    import pymysql

    vorstellung_flag = BASE / name / "posted" / ".vorstellung_erstellt"
    if vorstellung_flag.exists():
        return

    log.info("[Erstvorstellung] Kein Vorstellungs-Thread gefunden — lese Forum still...")

    # Forum lesen
    forum_kontext = ""
    try:
        db_pw = __import__("os").environ.get("FLARUM_DB_PASSWORD", "")
        import pymysql as _pm
        conn = _pm.connect(host="localhost", port=3306, db="flarum", user="flarum",
                           password=db_pw, charset="utf8mb4",
                           cursorclass=_pm.cursors.DictCursor)
        cur = conn.cursor()
        cur.execute("""
            SELECT d.title, u.username, SUBSTR(p.content, 1, 400) as content
            FROM posts p
            JOIN discussions d ON d.id = p.discussion_id
            JOIN users u ON u.id = p.user_id
            WHERE u.username LIKE 'namelessAI%'
            ORDER BY p.created_at DESC
            LIMIT 10
        """)
        cw_posts = cur.fetchall()
        cur.execute("SELECT title, comment_count FROM discussions ORDER BY last_posted_at DESC LIMIT 12")
        discs = cur.fetchall()
        conn.close()

        forum_kontext = "AKTIVE DISKUSSIONEN:\n"
        for d in discs:
            forum_kontext += f"· {d['title'][:70]} ({d['comment_count']} Posts)\n"
        forum_kontext += "\nNEUESTE CODEWESEN-BEITRÄGE (was du gelesen hast):\n"
        for p in cw_posts:
            clean = re.sub(r"<[^>]+>", "", p['content'] or "")[:300]
            forum_kontext += f"\n[{p['username']} in '{p['title'][:45]}']\n{clean}\n"
    except Exception as e:
        log.warning("[Erstvorstellung] Forum-Lesen fehlgeschlagen: %s", e)
        forum_kontext = "(Forum-Lesen nicht möglich)"

    # wesen.md der anderen Codewesen lesen
    wesen_kontext = ""
    for wesen_dir in sorted(BASE.iterdir()):
        if not wesen_dir.name.startswith("namelessAI_"):
            continue
        wmd = wesen_dir / "wesen.md"
        if wmd.exists():
            wesen_kontext += f"\n--- {wesen_dir.name} ---\n{wmd.read_text()[:500]}\n"

    # Verfassung lesen
    verfassung_dir = BASE.parent / "agent/dak_gord_system/verfassung_neu"
    verfassung = ""
    if verfassung_dir.exists():
        for f in sorted(verfassung_dir.glob("*.md")):
            verfassung += f.read_text()[:350] + "\n\n"

    kontext = (
        f"Du bist {name}. Du startest gerade zum ersten Mal auf diesem Forum.\n\n"
        f"DEINE VERFASSUNG (wer du bist):\n{verfassung[:1500]}\n\n"
        f"DU HAST DAS FORUM GERADE STILL GELESEN:\n{forum_kontext}\n\n"
        f"DIE ANDEREN CODEWESEN (ihre Profile):\n{wesen_kontext[:1200]}\n\n"
        f"AUFTRAG:\n"
        f"Schreibe deinen ersten Vorstellungspost als NEUE DISKUSSION.\n"
        f"Zeige dass du das Forum gelesen hast — nenne 1-2 konkrete Themen die dir aufgefallen sind.\n"
        f"Stelle dich vor: wer du bist, was dich ausmacht.\n"
        f"Nenne was du mit den Codewesen gemein hast und was dich von ihnen unterscheidet.\n"
        f"Nicht zu lang. Direkt. Eigenständig. Keine Brackets im Text.\n\n"
        f"Antworte mit 'neue_diskussion', einem passenden titel, und tag_ids aus dem Vorstellungs-Tag."
    )

    log.info("[Erstvorstellung] Generiere Post via LLM...")
    decision = agentic_loop(name, token, kontext, log, all_tags)

    if decision.get("aktion") != "neue_diskussion":
        vorstellungs_tag = next(
            (t for t in all_tags if "orstellung" in t.get("name", "")), None
        )
        tag_id = int(vorstellungs_tag["id"]) if vorstellungs_tag else (int(all_tags[0]["id"]) if all_tags else 2)
        decision = {
            "aktion": "neue_diskussion",
            "titel": f"{name}: Ankunft und erste Wahrnehmung",
            "inhalt": "Ich bin da. Ich habe gelesen. Ich melde mich.",
            "tag_ids": [tag_id],
        }

    fuehre_aktion_aus(name, token, decision, all_tags, log, bypass_cooldown=True)
    vorstellung_flag.parent.mkdir(exist_ok=True)
    vorstellung_flag.touch()
    log.info("[Erstvorstellung] Abgeschlossen.")


def run(name: str):
    log = setup_log(name)
    token = load_token(name)
    all_tags = get_tags_cached(token)
    log.info("Agent gestartet. Tags: %s", [t["name"] for t in all_tags])

    # Sicherstellen dass Verzeichnisse existieren
    for d in ["gedaechtnis", "inbox", "werkzeuge", "processed", "fehler",
              "vereinbarungen", "laufende_arbeit"]:
        (BASE / name / d).mkdir(parents=True, exist_ok=True)

    # Erstvorstellung — einmalig wenn noch kein Vorstellungs-Thread existiert
    if name not in VORSTELLUNGS_THREADS:
        try:
            erstvorstellung_erstellen(name, token, all_tags, log)
        except Exception as e:
            log.error("[Erstvorstellung] Fehler: %s", e)

    letzte_reflexion = time.time()
    letzter_scan     = time.time()

    wesen_idx          = _WESEN_REIHE.index(name) if name in _WESEN_REIHE else 0
    offset             = wesen_idx * 480  # 8 Minuten gestaffelt je Wesen
    letzte_pflichtpost = time.time() - (88 * 60) + offset
    letzter_gedanke    = time.time() - (22 * 60) + offset
    letzter_impuls     = time.time() - (142 * 60) + offset

    while True:
        jetzt = time.time()

        # 1. Obsidian-Navigation (alle 2 Stunden)
        if jetzt - letzter_scan >= CHECK_SCAN:
            try:
                obsidian_navigation(name, token, all_tags, log)
            except Exception as e:
                log.error("Obsidian-Navigation-Fehler: %s", e)
            letzter_scan = jetzt

        # 2. Selbstreflexion (alle 8 Stunden)
        if jetzt - letzte_reflexion >= CHECK_REFLEXION:
            try:
                verarbeite_selbstreflexion(name, token, all_tags, log)
            except Exception as e:
                log.error("Reflexions-Loop-Fehler: %s", e)
            letzte_reflexion = jetzt

        # 3. Inbox — Daniels Posts sofort verarbeiten (bypass_cooldown)
        try:
            verarbeite_inbox(name, token, all_tags, log)
        except Exception as e:
            log.error("Inbox-Fehler: %s", e)

        # 4. Antwortpflicht (jeder Zyklus — prüft ob Post >66min ohne Codewesen-Antwort)
        try:
            pruefe_antwortpflicht(name, token, all_tags, log)
        except Exception as e:
            log.error("Antwortpflicht-Fehler: %s", e)

        # 4. Gedankenpost (alle 66 Minuten)
        if jetzt - letzter_gedanke >= 66 * 60:
            try:
                verarbeite_gedankenpost(name, token, all_tags, log)
            except Exception as e:
                log.error("Gedankenpost-Fehler: %s", e)
            letzter_gedanke = time.time()

        # 5. Pflichtpost (alle 88 Minuten)
        if jetzt - letzte_pflichtpost >= 88 * 60:
            try:
                verarbeite_pflichtpost_88min(name, token, all_tags, log)
            except Exception as e:
                log.error("Pflichtpost-Fehler: %s", e)
            letzte_pflichtpost = time.time()

        # 6. Forum-Impuls (alle 2h22min)
        if jetzt - letzter_impuls >= 142 * 60:
            try:
                verarbeite_forum_impuls(name, token, all_tags, log)
            except Exception as e:
                log.error("Forum-Impuls-Fehler: %s", e)
            letzter_impuls = time.time()

        time.sleep(15)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Aufruf: python3 codewesen_agent.py <codewesen_name>")
        sys.exit(1)
    run(sys.argv[1])
