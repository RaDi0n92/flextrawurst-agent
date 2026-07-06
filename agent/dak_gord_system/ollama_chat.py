from __future__ import annotations

import json
import os
import time
from typing import Callable

import httpx
import requests

import sys as _sys; _sys.path.insert(0, "/root/werkraum")
import hauhau_client

OLLAMA_URL = "http://localhost:11434/api/chat"
MODELL_TIEF    = os.getenv("DAK_GORD_OLLAMA_MODELL",         "hauhaucs-q6")
MODELL_MITTEL  = os.getenv("DAK_GORD_OLLAMA_MODELL_MITTEL",  "hauhaucs-q6")
MODELL_SCHNELL = os.getenv("DAK_GORD_OLLAMA_MODELL_SCHNELL", "hauhaucs-q6")
MODELL_QWEN    = os.getenv("DAK_GORD_OLLAMA_MODELL_QWEN",    "hauhaucs-q6")
MODELL_FREI    = os.getenv("DAK_GORD_OLLAMA_MODELL_FREI",    "dolphin-mistral:7b")
STANDARD_TIMEOUT = int(os.getenv("DAK_GORD_OLLAMA_TIMEOUT", "720"))

_MAX_VERSUCHE = 3
_RETRY_WARTEZEITEN = [2, 5, 10]


def _anfrage_mit_retry(payload: dict, streaming: bool) -> requests.Response:
    letzter_fehler: Exception | None = None
    for versuch in range(_MAX_VERSUCHE):
        try:
            r = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=STANDARD_TIMEOUT,
                stream=streaming,
            )
            if r.ok:
                return r
            if r.status_code < 500:
                raise RuntimeError(f"Ollama HTTP {r.status_code}: {r.text[:200]}")
            letzter_fehler = RuntimeError(f"Ollama Serverfehler {r.status_code}")
        except requests.Timeout as e:
            raise RuntimeError(f"Ollama-Timeout nach {STANDARD_TIMEOUT}s") from e
        except requests.ConnectionError as e:
            letzter_fehler = e
        except requests.RequestException as e:
            letzter_fehler = e
        if versuch < _MAX_VERSUCHE - 1:
            time.sleep(_RETRY_WARTEZEITEN[versuch])
    raise RuntimeError(
        f"Ollama nicht erreichbar nach {_MAX_VERSUCHE} Versuchen: {letzter_fehler}"
    )


# Blitz-Muster: kurze Fakten, Ja/Nein, einfache Lookups
_BLITZ_MUSTER = {
    "was ist", "wer ist", "wie viel", "wie viele", "wann ist", "wo ist",
    "ja oder nein", "kurz", "schnell", "einfach", "nur sagen",
    "liste", "aufzählung", "überblick",
}

# Tief-Muster: Vision, Philosophie, Architektur-Entscheidungen
_TIEF_MUSTER = {
    "vision", "bedeutung", "bedeutet", "warum", "wieso", "weshalb",
    "denk", "denkst", "philosophie", "philosophisch", "konzept",
    "entität", "entitaet", "zwischenraum", "resonanz", "abstammung",
    "identität", "identitaet", "wesen", "charakter", "tiefe",
    "architektur", "prinzip", "grundlage", "fundamentum",
    "reflektier", "analyse", "analysier", "bewerte", "bewert",
    "versteh", "erklaer", "erkläre",
}

# Mittel-Muster: Code, Implementierung, strukturierte Aufgaben
_MITTEL_MUSTER = {
    "schreib", "erstell", "implementier", "code", "codes", "codier",
    "fix", "fixe", "reparier", "debug", "fehler beheb",
    "tabelle", "schema", "migration", "komponente", "component",
    "funktion", "klasse", "datei anlegen", "datei erstellen",
    "sql", "html", "css", "typescript", "javascript", "python",
    "test schreib", "tests schreib", "unittest",
}


def waehle_modell(text: str, modus_override: str | None = None) -> str:
    """Wählt e2b/e4b/26b-a4b/qwen basierend auf Inhalt (3-Stufen + qwen)."""
    if modus_override == "schnell":
        return MODELL_SCHNELL
    if modus_override == "mittel":
        return MODELL_MITTEL
    if modus_override == "tief":
        return MODELL_TIEF
    if modus_override == "qwen":
        return MODELL_QWEN

    klein = text.lower()

    hat_mittel = any(m in klein for m in _MITTEL_MUSTER)
    hat_tief = any(m in klein for m in _TIEF_MUSTER)

    # Code-Kontext schlägt philosophischen Kontext bei Konflikt
    if hat_mittel:
        return MODELL_MITTEL

    # Blitz für kurze Faktenfragen (nur wenn kein Code-Kontext)
    if any(m in klein for m in _BLITZ_MUSTER):
        return MODELL_SCHNELL

    # Tief-Keywords → Mittel im Auto-Modus (26b nur per explizitem /tief)
    if hat_tief:
        return MODELL_MITTEL

    return MODELL_MITTEL  # Default: Mittel


def _baue_nachrichten(verlauf: list[str]) -> list[dict[str, str]]:
    if not verlauf:
        return [{"role": "system", "content": ""}]

    system_text = verlauf[0]
    rest = verlauf[1:]

    nachrichten: list[dict[str, str]] = [
        {"role": "system", "content": system_text}
    ]

    user_assistant_index = 0
    for text in rest:
        if text.startswith("[TOOL-ERGEBNIS]"):
            # Tool-Ergebnisse als system-Nachricht — Gemma behandelt sie als Fakten, nicht als User-Input
            nachrichten.append({"role": "system", "content": text})
        else:
            rolle = "user" if user_assistant_index % 2 == 0 else "assistant"
            nachrichten.append({"role": rolle, "content": text})
            user_assistant_index += 1

    return nachrichten


OLLAMA_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "datei_lesen",
            "description": (
                "Liest den vollstaendigen Inhalt einer Datei vom Dateisystem. "
                "MUSS aufgerufen werden wenn: (1) der User nach einer Datei fragt, "
                "(2) du ueber Dateiinhalt sprechen willst, "
                "(3) du eine Datei analysieren oder zusammenfassen sollst. "
                "Beispiel: User sagt 'lies vision5.md' → sofort aufrufen mit pfad=/root/werkraum/projekt/vision5.md. "
                "NIEMALS ueber Dateiinhalte sprechen ohne diesen Tool vorher aufzurufen."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pfad": {
                        "type": "string",
                        "description": "Absoluter Dateipfad, z.B. /root/werkraum/projekt/vision5.md",
                    }
                },
                "required": ["pfad"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "datei_schreiben",
            "description": (
                "Schreibt Inhalt in eine Datei. "
                "MUSS aufgerufen werden wenn: (1) eine wichtige Erkenntnis entsteht die festgehalten werden soll, "
                "(2) der User 'merk dir', 'speichern', 'wichtig' sagt, "
                "(3) du selbst erkennst dass etwas archiviert werden sollte. "
                "Erkenntnisse in /root/werkraum/erkenntnis/DATEINAME.md, "
                "Index-Updates in /root/werkraum/erkenntnis/INDEX.md. "
                "NIEMALS 'ich halte das fest' sagen ohne diesen Tool aufzurufen."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pfad": {
                        "type": "string",
                        "description": "Absoluter Dateipfad, z.B. /root/werkraum/erkenntnis/resonanz_2026-04-19.md",
                    },
                    "inhalt": {"type": "string", "description": "Vollstaendiger Dateiinhalt als String"},
                },
                "required": ["pfad", "inhalt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "python_code_ausfuehren",
            "description": (
                "Fuehrt Python-Code sicher in einer Sandbox aus und gibt stdout/stderr zurueck. "
                "MUSS aufgerufen werden wenn: (1) Berechnungen noetig sind, "
                "(2) Code getestet oder debuggt werden soll, "
                "(3) der User 'fuehre aus', 'berechne', 'teste' sagt. "
                "Kein Netzwerkzugriff, kein Dateisystem-Schreiben (dafuer datei_schreiben benutzen). "
                "Timeout: 10 Sekunden."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Vollstaendiger ausfuehrbarer Python-Code als String",
                    }
                },
                "required": ["code"],
            },
        },
    },
]


def _tool_calls_zu_marker(text_inhalt: str, tool_calls: list[dict]) -> str:
    marker_teile = []
    if text_inhalt:
        marker_teile.append(text_inhalt)

    for tc in tool_calls:
        fn = tc.get("function", {})
        name = fn.get("name", "")
        args = fn.get("arguments", {})
        if isinstance(args, str):
            args = json.loads(args) if args else {}
        if name == "datei_lesen":
            pfad = args.get("pfad", "")
            if pfad:
                marker_teile.append(f"##LESEN: {pfad}##")
        elif name == "datei_schreiben":
            pfad = args.get("pfad", "")
            inhalt = args.get("inhalt", "")
            if pfad:
                marker_teile.append(f"##SCHREIBEN: {pfad}##\n{inhalt}\n##SCHREIBEN_ENDE##")
        elif name == "python_code_ausfuehren":
            code = args.get("code", "")
            if code:
                marker_teile.append(f"##CODE_START##\n{code}\n##CODE_ENDE##")

    return "\n".join(marker_teile)


def ollama_chat(
    verlauf: list[str],
    token_callback: Callable[[str], None] | None = None,
    modell: str | None = None,
    mit_tools: bool = False,
    bild_b64: str | None = None,
) -> str:
    verwendetes_modell = modell or MODELL_MITTEL
    nachrichten = _baue_nachrichten(verlauf)

    # Freier Modus (dolphin-mistral) bleibt bewusst auf Ollama — eigenes, separates Modell
    if verwendetes_modell == MODELL_FREI:
        if bild_b64:
            for i in range(len(nachrichten) - 1, -1, -1):
                if nachrichten[i]["role"] == "user":
                    nachrichten[i] = dict(nachrichten[i], images=[bild_b64])
                    break

        temperature = 0.0 if mit_tools else 0.7
        num_predict = 400 if mit_tools else 700

        payload: dict = {
            "model": verwendetes_modell,
            "stream": True,
            "messages": nachrichten,
            "keep_alive": -1,
            "think": False,
            "options": {
                "num_ctx": 8192,
                "num_predict": num_predict,
                "temperature": temperature,
                "top_k": 64,
                "top_p": 0.95,
                "repeat_penalty": 1.1,
            },
        }
        if mit_tools:
            payload["tools"] = OLLAMA_TOOLS
            payload["stream"] = False

        resp = _anfrage_mit_retry(payload, streaming=not mit_tools)

        if mit_tools:
            daten = resp.json()
            nachricht = daten.get("message", {})
            ergebnis = _tool_calls_zu_marker(nachricht.get("content", ""), nachricht.get("tool_calls", []))
            if token_callback and ergebnis:
                if nachricht.get("tool_calls"):
                    token_callback(ergebnis)
                else:
                    woerter = ergebnis.split(" ")
                    for i, wort in enumerate(woerter):
                        token_callback(wort + ("" if i == len(woerter) - 1 else " "))
            return ergebnis

        teile: list[str] = []
        try:
            for rohe_zeile in resp.iter_lines():
                if not rohe_zeile:
                    continue
                try:
                    chunk = json.loads(rohe_zeile)
                except json.JSONDecodeError:
                    continue
                token = chunk.get("message", {}).get("content", "")
                if token:
                    teile.append(token)
                    if token_callback is not None:
                        token_callback(token)
                if chunk.get("done"):
                    break
        except requests.RequestException as fehler:
            if teile:
                return "".join(teile).strip()
            raise RuntimeError(f"Ollama-Stream unterbrochen: {fehler}") from fehler
        return "".join(teile).strip()

    # Alles andere → hauhaucs-q6 via llama-server
    bilder = [bild_b64] if bild_b64 else None

    if mit_tools:
        daten = hauhau_client.chat_raw(
            nachrichten, images=bilder, think=False, max_tokens=400,
            temperature=0.0, top_p=0.95, top_k=64, repeat_penalty=1.1,
            tools=OLLAMA_TOOLS, timeout=STANDARD_TIMEOUT,
        )
        nachricht = daten["choices"][0]["message"]
        ergebnis = _tool_calls_zu_marker(nachricht.get("content") or "", nachricht.get("tool_calls") or [])
        if token_callback and ergebnis:
            if nachricht.get("tool_calls"):
                token_callback(ergebnis)
            else:
                woerter = ergebnis.split(" ")
                for i, wort in enumerate(woerter):
                    token_callback(wort + ("" if i == len(woerter) - 1 else " "))
        return ergebnis

    teile: list[str] = []
    try:
        for token in hauhau_client.chat_stream(
            nachrichten, images=bilder, think=False, max_tokens=700,
            temperature=0.7, top_p=0.95, top_k=64, repeat_penalty=1.1,
            timeout=STANDARD_TIMEOUT,
        ):
            teile.append(token)
            if token_callback is not None:
                token_callback(token)
    except httpx.HTTPError as fehler:
        if teile:
            return "".join(teile).strip()
        raise RuntimeError(f"hauhaucs-Stream unterbrochen: {fehler}") from fehler

    return "".join(teile).strip()


class OllamaChat:
    """Klassen-Wrapper um ollama_chat() für Kompatibilität mit graf.py."""

    def chat(self, nachrichten: list[dict], modell: str | None = None) -> str:
        verlauf = [m["content"] for m in nachrichten]
        return ollama_chat(verlauf, modell=modell)
