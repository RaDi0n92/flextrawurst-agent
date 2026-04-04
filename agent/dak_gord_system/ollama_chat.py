from __future__ import annotations

import os

import requests


OLLAMA_URL = "http://localhost:11434/api/chat"
STANDARD_MODELL = os.getenv("DAK_GORD_OLLAMA_MODELL", "qwen2.5-coder:14b")
STANDARD_TIMEOUT = int(os.getenv("DAK_GORD_OLLAMA_TIMEOUT", "180"))


def _baue_nachrichten(verlauf: list[str]) -> list[dict[str, str]]:
    if not verlauf:
        return [{"role": "system", "content": ""}]

    system_text = verlauf[0]
    rest = verlauf[1:]

    nachrichten: list[dict[str, str]] = [
        {"role": "system", "content": system_text}
    ]

    for index, text in enumerate(rest):
        rolle = "user" if index % 2 == 0 else "assistant"
        nachrichten.append(
            {
                "role": rolle,
                "content": text,
            }
        )

    return nachrichten


def ollama_chat(verlauf: list[str]) -> str:
    nachrichten = _baue_nachrichten(verlauf)

    try:
        antwort = requests.post(
            OLLAMA_URL,
            json={
                "model": STANDARD_MODELL,
                "stream": False,
                "messages": nachrichten,
            },
            timeout=STANDARD_TIMEOUT,
        )
    except requests.RequestException as fehler:
        raise RuntimeError(
            f"Ollama-Anfrage fehlgeschlagen: {fehler}"
        ) from fehler

    if not antwort.ok:
        detail = antwort.text.strip()
        if len(detail) > 500:
            detail = detail[:500] + " ..."
        raise RuntimeError(
            f"Ollama-Antwortfehler {antwort.status_code}: {detail or antwort.reason}"
        )

    try:
        daten = antwort.json()
    except ValueError as fehler:
        raise RuntimeError("Ollama hat keine gueltige JSON-Antwort geliefert.") from fehler

    nachricht = daten.get("message")
    if not isinstance(nachricht, dict):
        raise RuntimeError("Ollama-Antwort enthaelt kein gueltiges 'message'-Objekt.")

    inhalt = nachricht.get("content")
    if not isinstance(inhalt, str):
        raise RuntimeError("Ollama-Antwort enthaelt keinen gueltigen Text in 'message.content'.")

    return inhalt.strip()
