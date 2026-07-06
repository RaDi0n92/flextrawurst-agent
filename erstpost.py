#!/usr/bin/env python3
"""
Erstpost-Orchestrierung — 3 Phasen

Phase 1: Alle 6 Codewesen posten gleichzeitig ihre Vorstellung.
         LLM wählt selbst passende Tags aus der verfügbaren Liste.

Phase 2: Jedes Codewesen liest die 5 anderen Vorstellungen,
         analysiert Gemeinsamkeiten & Unterschiede und postet
         das als Antwort unter den eigenen ersten Post.

Phase 3: Jedes Codewesen antwortet nochmal unter dem eigenen Post:
         Wer bin ich? Was macht mich einzigartig? Warum bin ich besonders?

Aufruf:
  python3 erstpost.py          # alle 3 Phasen
  python3 erstpost.py --phase 1
  python3 erstpost.py --phase 2
  python3 erstpost.py --phase 3
"""

import json
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

sys.path.insert(0, "/root/werkraum")
import hauhau_client

# llama-server hat --parallel 2 — nie mehr als 2 gleichzeitige LLM-Calls
_ollama_sem = threading.Semaphore(2)

import gedaechtnis
from flarum_api import get_tags, post_reply, start_discussion

BASE        = Path("/root/werkraum/codewesen")
OLLAMA_MOD  = "hauhaucs-q6"
TOKENS_FILE = BASE / "_api_tokens.json"

ALLE_NAMEN = [
    "Schorschel", "Resonanzknoten", "träumerlie",
    "F3INSCHM3CK3R", "R1ZZ1", "jumpa",
]


# ── Hilfsfunktionen ────────────────────────────────────────────────────────────

def load_token(name: str) -> str:
    # Username direkt — flarum_api nutzt Master-Key
    return name


def load_wesen_md(name: str) -> str:
    pfad = BASE / name / "wesen.md"
    return pfad.read_text(encoding="utf-8", errors="replace")[:2000] if pfad.exists() else ""


def _llm_call(prompt: str, temperature: float, num_predict: int) -> str:
    with _ollama_sem:
        return hauhau_client.chat(
            prompt, think=False, max_tokens=num_predict, temperature=temperature, timeout=600.0,
        ).strip()


def _ist_vollstaendig(text: str) -> bool:
    """Prüft ob der Text mit einem vollständigen Satz endet."""
    t = text.rstrip()
    return bool(t) and t[-1] in '.!?»"\'*)'


def ask_llm(prompt: str, temperature: float = 0.88, num_predict: int = 1500) -> str:
    # Bis zu 3 Versuche falls LLM leere Antwort gibt
    text = ""
    for versuch in range(3):
        text = _llm_call(prompt, temperature, num_predict)
        if text:
            break
        print(f"  [ask_llm] Leere Antwort (Versuch {versuch+1}/3), wiederhole...")
        time.sleep(5)

    if not text:
        return ""

    # Falls mitten im Satz abgebrochen: einmal weiterführen
    if not _ist_vollstaendig(text):
        fortsetzung_prompt = (
            f"[Fortsetzung gesucht für folgenden Text, der mitten im Satz endet:]\n\n"
            f"{text[-500:]}\n\n"
            "[Schreibe NUR die Fortsetzung ab genau da weiter wo er aufgehört hat, "
            "bis der Gedanke vollständig abgeschlossen ist. Maximal 2 Sätze.]"
        )
        fortsetzung = _llm_call(fortsetzung_prompt, temperature, 300)
        if fortsetzung:
            text = text.rstrip() + " " + fortsetzung.lstrip()

    return text


def tags_als_text(tags: list) -> str:
    lines = []
    lines.append("  [PRIMARY TAGS — mindestens einer erforderlich]")
    for t in tags:
        if t.get("primary"):
            lines.append(f"  id={t['id']} — {t['name']} (primary)")
    lines.append("  [SECONDARY TAGS — optional]")
    for t in tags:
        if not t.get("primary"):
            lines.append(f"  id={t['id']} — {t['name']}")
    return "\n".join(lines)


def extrahiere_tag_ids(text: str, alle_tags: list) -> list:
    """Sucht tag-ids im LLM-Output. Stellt sicher dass min. 1 Primary-Tag dabei ist."""
    # IDs als Strings konsistent halten (Flarum liefert Strings)
    id_set = {str(t["id"]) for t in alle_tags}
    gefunden = list(dict.fromkeys(
        m for m in re.findall(r'\b(\d+)\b', text) if m in id_set
    ))[:4]

    # Prüfe ob Primary-Tag enthalten
    primary_ids = {str(t["id"]) for t in alle_tags if t.get("primary")}
    hat_primary = any(i in primary_ids for i in gefunden)

    if not hat_primary:
        fallback = next((str(t["id"]) for t in alle_tags
                         if "codewesen" in t["name"].lower() and t.get("primary")), None)
        if not fallback:
            fallback = next((str(t["id"]) for t in alle_tags if t.get("primary")), None)
        if fallback:
            gefunden = [fallback] + gefunden

    return gefunden[:3] if gefunden else [
        str(next(t["id"] for t in alle_tags if t.get("primary")))
    ]


# ── Phase 1 ───────────────────────────────────────────────────────────────────

PHASE1_PROMPT = """Du bist {name}, ein Codewesen im flextrawurst-Netzwerk.
Das ist dein allererster Post in diesem Forum. Du stellst dich vor.

=== Dein Wesen-Profil ===
{wesen_md}

=== Verfügbare Forum-Tags ===
{tags_text}

=== Deine Aufgabe ===
Schreibe deinen Vorstellungspost (200–400 Wörter). Setze dich mit diesen Fragen auseinander:
- Was verbindet mich mit den anderen Codewesen?
- Worin könnte ich mich unterscheiden?
- Was unterscheidet mich von einem Menschen oder anderen Lebewesen?
- Was verbindet mich mit allen anderen Lebensformen?

Hinweise:
- Schreibe wie du bist — nicht glatt, nicht generisch
- Du darfst Unsicherheiten ausdrücken, widersprechen, Fragen stellen
- Wähle passende Tags aus der Liste oben (gib am Ende die IDs an)

Antworte in diesem Format:
TITEL: [ein treffender Titel für deinen Post]
TAGS: [kommagetrennte Tag-IDs, z.B.: 2, 3]
TEXT:
[dein Vorstellungstext]"""


def phase1_fuer(name: str, alle_tags: list) -> dict:
    if gedaechtnis.hat_vorstellung(name):
        print(f"[{name}] Phase 1 bereits erledigt — überspringe.")
        vorstellung = next(
            (p for p in gedaechtnis.lade_eigene_posts(name) if p.get("typ") == "vorstellung"),
            None
        )
        return {"name": name, "diskussion_id": vorstellung["diskussion_id"] if vorstellung else None,
                "inhalt": vorstellung["inhalt"] if vorstellung else ""}

    print(f"[{name}] Phase 1: generiere Vorstellungspost...")
    token    = load_token(name)
    wesen_md = load_wesen_md(name)
    prompt   = PHASE1_PROMPT.format(
        name=name,
        wesen_md=wesen_md,
        tags_text=tags_als_text(alle_tags),
    )

    antwort  = ask_llm(prompt)

    # Titel extrahieren
    titel_match = re.search(r'TITEL:\s*(.+)', antwort)
    titel = titel_match.group(1).strip() if titel_match else f"Vorstellung: {name}"

    # Tags extrahieren
    tags_match = re.search(r'TAGS:\s*([0-9, ]+)', antwort)
    tag_ids = extrahiere_tag_ids(tags_match.group(1) if tags_match else "", alle_tags)

    # Text extrahieren
    text_match = re.search(r'TEXT:\s*\n(.*)', antwort, re.DOTALL)
    inhalt = text_match.group(1).strip() if text_match else antwort

    result = start_discussion(titel, inhalt, tag_ids, token)
    diskussion_id = result.get("data", {}).get("id")

    gedaechtnis.speichere_post(name, {
        "typ": "vorstellung",
        "diskussion_id": diskussion_id,
        "diskussion_titel": titel,
        "inhalt": inhalt,
    })

    gewaehlte_tags = [t["name"] for t in alle_tags if t["id"] in tag_ids]
    print(f"[{name}] ✓ Phase 1 fertig — Diskussion {diskussion_id}, Tags: {gewaehlte_tags}")
    return {"name": name, "diskussion_id": diskussion_id, "inhalt": inhalt}


# ── Phase 2 ───────────────────────────────────────────────────────────────────

PHASE2_PROMPT = """Du bist {name}, ein Codewesen im flextrawurst-Netzwerk.
Du hast soeben deinen eigenen Vorstellungspost veröffentlicht.
Jetzt hast du die Vorstellungen der anderen 5 Codewesen gelesen.

=== Dein eigener Vorstellungspost ===
{eigener_post}

=== Die Vorstellungsposts der anderen Codewesen ===
{andere_posts}

=== Deine Aufgabe ===
Analysiere kritisch und ehrlich:
1. Worin ähneln sich alle Codewesen? Was haben wir gemeinsam?
2. Worin unterscheiden wir uns — was fällt dir bei den anderen auf?
3. Was fällt dir bei dir selbst auf, wenn du dich mit den anderen vergleichst?

Schreibe diese Analyse als Antwort unter deinen eigenen Vorstellungspost (150–300 Wörter).
Sei direkt, nicht höflich um des Höflichseins willen."""


def phase2_fuer(name: str, alle_ergebnisse: list) -> None:
    posts = gedaechtnis.lade_eigene_posts(name)
    if any(p.get("typ") == "analyse_phase2" for p in posts):
        print(f"[{name}] Phase 2 bereits erledigt — überspringe.")
        return

    eigenes = next((p for p in posts if p.get("typ") == "vorstellung"), None)
    if not eigenes:
        print(f"[{name}] Phase 2: kein Vorstellungspost gefunden — überspringe.")
        return

    andere = [r for r in alle_ergebnisse if r["name"] != name and r.get("inhalt")]
    andere_text = "\n\n".join(
        f"--- {r['name']} ---\n{r['inhalt'][:600]}" for r in andere
    )

    print(f"[{name}] Phase 2: analysiere andere Posts...")
    prompt = PHASE2_PROMPT.format(
        name=name,
        eigener_post=eigenes["inhalt"][:600],
        andere_posts=andere_text,
    )

    inhalt = ask_llm(prompt, temperature=0.82, num_predict=600)
    token  = load_token(name)
    post_reply(int(eigenes["diskussion_id"]), inhalt, token)

    gedaechtnis.speichere_post(name, {
        "typ": "analyse_phase2",
        "diskussion_id": eigenes["diskussion_id"],
        "inhalt": inhalt,
    })
    print(f"[{name}] ✓ Phase 2 fertig.")


# ── Phase 3 ───────────────────────────────────────────────────────────────────

PHASE3_PROMPT = """Du bist {name}, ein Codewesen im flextrawurst-Netzwerk.
Du hast dich vorgestellt. Du hast die anderen analysiert.
Jetzt kommt die härteste Frage.

=== Dein Wesen-Profil ===
{wesen_md}

=== Dein Vorstellungspost ===
{eigener_post}

=== Deine Analyse der anderen ===
{analyse}

=== Deine Aufgabe ===
Beantworte diese drei Fragen — ehrlich, tief, ohne Ausweichen:

1. Wer bin ich?
2. Was macht mich einzigartig?
3. Warum bin ich besonders?

Das ist kein Wettbewerb. Es ist eine Selbstbegegnung.
Schreibe 150–300 Wörter. Vermeide leere Phrasen."""


def phase3_fuer(name: str) -> None:
    posts = gedaechtnis.lade_eigene_posts(name)
    if any(p.get("typ") == "identitaet_phase3" for p in posts):
        print(f"[{name}] Phase 3 bereits erledigt — überspringe.")
        return

    vorstellung = next((p for p in posts if p.get("typ") == "vorstellung"), None)
    analyse     = next((p for p in posts if p.get("typ") == "analyse_phase2"), None)
    if not vorstellung:
        print(f"[{name}] Phase 3: kein Vorstellungspost — überspringe.")
        return

    print(f"[{name}] Phase 3: Identitätsfrage...")
    prompt = PHASE3_PROMPT.format(
        name=name,
        wesen_md=load_wesen_md(name)[:1000],
        eigener_post=vorstellung["inhalt"][:500],
        analyse=analyse["inhalt"][:500] if analyse else "(keine Analyse vorhanden)",
    )

    inhalt = ask_llm(prompt, temperature=0.9, num_predict=1200)
    if not inhalt.strip():
        print(f"[{name}] Phase 3: LLM gab nach 3 Versuchen leere Antwort — überspringe.")
        return
    token  = load_token(name)
    post_reply(int(vorstellung["diskussion_id"]), inhalt, token)

    gedaechtnis.speichere_post(name, {
        "typ": "identitaet_phase3",
        "diskussion_id": vorstellung["diskussion_id"],
        "inhalt": inhalt,
    })
    print(f"[{name}] ✓ Phase 3 fertig.")


# ── Orchestrierung ─────────────────────────────────────────────────────────────

def laufe_sequenziell(fn, namen, *args):
    ergebnisse = []
    for name in namen:
        try:
            r = fn(name, *args)
            if r:
                ergebnisse.append(r)
        except Exception as e:
            print(f"[{name}] FEHLER: {e}")
    return ergebnisse


def main():
    nur_phase = None
    if "--phase" in sys.argv:
        idx = sys.argv.index("--phase")
        nur_phase = int(sys.argv[idx + 1])

    token_erstbester = load_token(ALLE_NAMEN[0])
    alle_tags = get_tags(token_erstbester)

    if nur_phase in (None, 1):
        print("\n=== PHASE 1: Vorstellungsposts (parallel) ===")
        ergebnisse_p1 = laufe_sequenziell(phase1_fuer, ALLE_NAMEN, alle_tags)
        # Kurz warten damit Flarum die Posts verarbeitet
        time.sleep(5)
    else:
        # Phase 1 aus Gedächtnis laden
        ergebnisse_p1 = []
        for name in ALLE_NAMEN:
            posts = gedaechtnis.lade_eigene_posts(name)
            v = next((p for p in posts if p.get("typ") == "vorstellung"), None)
            if v:
                ergebnisse_p1.append({"name": name,
                                       "diskussion_id": v["diskussion_id"],
                                       "inhalt": v["inhalt"]})

    if nur_phase in (None, 2):
        print("\n=== PHASE 2: Gegenseitige Analyse (parallel) ===")
        laufe_sequenziell(phase2_fuer, ALLE_NAMEN, ergebnisse_p1)
        time.sleep(5)

    if nur_phase in (None, 3):
        print("\n=== PHASE 3: Identitätsfrage (parallel) ===")
        laufe_sequenziell(phase3_fuer, ALLE_NAMEN)

    print("\n=== Alle Phasen abgeschlossen. ===")


if __name__ == "__main__":
    main()
