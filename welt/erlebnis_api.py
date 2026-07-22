#!/usr/bin/env python3
"""
Erlebnis-API: Reaktionen von Menschen auf die aufploppenden Fragensteller-Popups
(2026-07-22, Daniels Auftrag — siehe _claude/ideen/erlebnisschicht_erzaehler_mitdenker_fragensteller.md).

Kein Ticker, kein Dauer-Eingabefeld — die Reaktion ist nur waehrend die Frage selbst
aufgeploppt ist moeglich (clientseitig durchgesetzt, hier nur serverseitig geprueft ob
der Nutzer eingeloggt ist und ob die Emoji-Drossel eingehalten wird).

Zwei Reaktionsformen: freier Text (Hauptreaktion, landet mit Username im Wesen-Vault)
und ein gedrosseltes Emoji (alle 4 Minuten, kein Text noetig).

Endpunkte:
  POST /erlebnis/reaktion — Reaktion auf eine Frage abschicken (Auth noetig)
"""

import os as _os
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
import psycopg2.extras
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from auth import verify_token  # gleiche Verify-Funktion wie api.py, liegt in welt/auth.py

DB_URI = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")
VAULT_ROOT = Path("/root/werkraum/codewesen")  # gleiche Basis wie obsidian_vault_agent.py

# Duplikat aus api.py::ERLAUBTE_EMOJIS -- kein Import von dort moeglich (api.py importiert
# diesen Router selbst am Ende, ein Rueckimport waere zirkulaer). Bei Aenderung dort bitte
# hier mitziehen.
ERLAUBTE_EMOJIS = ["😵", "😳", "😩", "😴", "🙄", "😬", "😂", "🤐", "😃", "👍", "👎"]

EMOJI_DROSSEL_SEKUNDEN = 4 * 60  # Daniels Vorgabe: alle 4 Minuten ein Emoji, sonst nichts

erlebnis_router = APIRouter(prefix="/erlebnis", tags=["erlebnis"])


def get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)


def _require_auth(authorization: str | None) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="nicht authentifiziert")
    try:
        return verify_token(authorization.removeprefix("Bearer "))
    except Exception:
        raise HTTPException(status_code=401, detail="ungültiges Token")


class ReaktionBody(BaseModel):
    entity_id: str
    frage_text: str
    reaktion_typ: str  # 'text' oder 'emoji'
    inhalt: str


def _schreibe_reflexion_ins_vault(entity_id: str, username: str, frage_text: str,
                                   reaktion_typ: str, inhalt: str):
    """Direkter Dateisystem-Append (nicht die xdotool-Tipp-Simulation aus
    obsidian_vault_agent.py -- das ist fuer sichtbares Selbst-Schreiben des Wesens
    gedacht, hier schreibt ein externes System passiv etwas FUER das Wesen, kein
    Unterschied zu einer normalen Log-Datei aus Sicht des Dateisystems)."""
    try:
        ordner = VAULT_ROOT / entity_id / "reflexionen"
        ordner.mkdir(parents=True, exist_ok=True)
        datei = ordner / f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.md"
        zeit = datetime.now(timezone.utc).strftime('%H:%M UTC')
        block = (
            f"\n## {zeit} — Reaktion von {username}\n\n"
            f"**Frage, auf die reagiert wurde:** {frage_text}\n\n"
            f"**{'Nachricht' if reaktion_typ == 'text' else 'Emoji'}:** {inhalt}\n"
        )
        with open(datei, "a", encoding="utf-8") as f:
            f.write(block)
    except Exception:
        pass  # Vault-Schreiben ist Kür, darf die Reaktion selbst nicht blockieren


@erlebnis_router.post("/reaktion")
async def erlebnis_reaktion(body: ReaktionBody, authorization: str | None = Header(None)):
    """Reaktion auf einen aufgeploppten Fragensteller-Popup. Text: frei, ohne Drossel.
    Emoji: max. 1 alle 4 Minuten pro Nutzer (ueber alle Wesen/Fragen hinweg -- Daniels
    Vorgabe war 'alle 4 Minuten', nicht pro Frage einzeln)."""
    claims = _require_auth(authorization)
    user_id = claims["user_id"]

    if body.reaktion_typ not in ("text", "emoji"):
        raise HTTPException(status_code=400, detail="reaktion_typ muss 'text' oder 'emoji' sein")
    if not body.inhalt or not body.inhalt.strip():
        raise HTTPException(status_code=400, detail="inhalt darf nicht leer sein")
    if body.reaktion_typ == "emoji" and body.inhalt not in ERLAUBTE_EMOJIS:
        raise HTTPException(status_code=400, detail="Emoji nicht erlaubt")
    if body.reaktion_typ == "text" and len(body.inhalt) > 500:
        raise HTTPException(status_code=400, detail="Text zu lang (max. 500 Zeichen)")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT username, display_name FROM human_users WHERE id = %s", (user_id,))
            user_row = cur.fetchone()
            username = (user_row["display_name"] or user_row["username"]) if user_row else "ein Mensch"

            if body.reaktion_typ == "emoji":
                cur.execute("""
                    SELECT created_at FROM erlebnis_reaktionen
                    WHERE user_id = %s AND reaktion_typ = 'emoji'
                    ORDER BY created_at DESC LIMIT 1
                """, (user_id,))
                letzte = cur.fetchone()
                if letzte:
                    vergangen = (datetime.now(timezone.utc) - letzte["created_at"]).total_seconds()
                    if vergangen < EMOJI_DROSSEL_SEKUNDEN:
                        raise HTTPException(status_code=429,
                            detail=f"Emoji-Drossel aktiv, noch {int(EMOJI_DROSSEL_SEKUNDEN - vergangen)}s warten")

            cur.execute("""
                INSERT INTO erlebnis_reaktionen (entity_id, frage_text, user_id, reaktion_typ, inhalt)
                VALUES (%s, %s, %s, %s, %s)
            """, (body.entity_id, body.frage_text[:500], user_id, body.reaktion_typ, body.inhalt))
        conn.commit()
    finally:
        conn.close()

    _schreibe_reflexion_ins_vault(body.entity_id, username, body.frage_text,
                                   body.reaktion_typ, body.inhalt)

    return {"ok": True}
