#!/usr/bin/env python3
"""
Emotionsbewertung via Ollama (generate-Endpoint, kein thinking-Overhead).
Bewertet ein Ereignis auf drei Dimensionen: Valenz, Arousal, Dominanz.
"""

import json
import re
import sys

import httpx

sys.path.insert(0, "/root/werkraum")
import hauhau_client

MODELL     = "hauhaucs-q6"

_PROMPT_TEMPLATE = """Du bist ein Emotionsbewertungssystem. Antworte NUR mit JSON, kein anderer Text.
Valenz: 0=extrem negativ, 5=neutral, 10=extrem positiv
Arousal: 0=entspannt, 5=normal, 10=extrem aufgeregt
Dominanz: 0=hilflos, 5=normal, 10=volle Kontrolle
Ereignis: {event_text}
JSON-Antwort (nur diese Zeile):
{{"valence": X.X, "arousal": X.X, "dominance": X.X, "reason": "kurz"}}"""

_FALLBACK = {"valence": 5.0, "arousal": 5.0, "dominance": 5.0, "reason": "parse_error"}


def _parse_emotion(response: str) -> dict:
    match = re.search(r'\{[^{}]+\}', response)
    if match:
        try:
            d = json.loads(match.group())
            for k in ("valence", "arousal", "dominance"):
                d[k] = float(d.get(k, 5.0))
            if "reason" not in d:
                d["reason"] = ""
            return d
        except Exception:
            pass
    return dict(_FALLBACK)


def bewerte(event_text: str, timeout: int = 90) -> dict:
    prompt = _PROMPT_TEMPLATE.format(event_text=event_text[:1500])
    try:
        raw = hauhau_client.chat(prompt, think=False, max_tokens=100, temperature=0.1, timeout=float(timeout))
        return _parse_emotion(raw)
    except Exception as e:
        return {**_FALLBACK, "reason": f"error:{e}"}


if __name__ == "__main__":
    tests = [
        "Daniel hat meinen Beitrag ignoriert und den anderen Wesen geantwortet.",
        "Ein Mensch hat meinen Post mit großer Begeisterung gelobt.",
        "Ich musste einen Fehler in meiner Argumentation eingestehen.",
    ]
    for t in tests:
        result = bewerte(t)
        print(f"V:{result['valence']} A:{result['arousal']} D:{result['dominance']} — {result['reason']}")
        print(f"  Event: {t[:70]}")
