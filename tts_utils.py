"""Hilfsfunktionen für Text-to-Speech-Ausgaben via edge_tts.

Dieses Modul enthält ausschließlich TTS-Hilfslogik.
Der Originaltext (Chat-Output der Wesen) wird dabei NICHT verändert,
gespeichert oder neu strukturiert – er wird nur an edge_tts übergeben.
"""

from __future__ import annotations

import io
from typing import AsyncIterator

import edge_tts


# Maximale Zeichen, die in einem einzelnen edge_tts-Aufruf verarbeitet werden.
# Erfahrungsgemäß bleibt Microsofts Edge-TTS bei bis zu ~5000 Zeichen stabil
# und schnell genug für einen einzelnen HTTP-Request.
_MAX_DIRECT_CHARS = 5000


async def generate_long_tts_audio(text: str, voice: str, rate: str | None = None) -> bytes:
    """Wandelt Text in ein einzelnes MP3-Audio um.

    Für Texte bis zu _MAX_DIRECT_CHARS Zeichen wird ein direkter edge_tts-Aufruf
    verwendet. Das vermeidet MP3-Konkatenierungsprobleme, die in Browsern dazu
    führen können, dass die Wiedergabe vorzeitig stoppt.

    Args:
        text: Der vollständige Originaltext (wird nicht verändert).
        voice: edge_tts-Stimme, z.B. "de-DE-KatjaNeural".
        rate: Optionale Sprechgeschwindigkeit, z.B. "-5%".

    Returns:
        Ein Byte-String mit dem MP3-Audio.
    """
    text = text.strip()
    if not text:
        return b""

    # Sicherheitsabschneidung für extrem lange Inputs; der Chat-Text selbst
    # bleibt natürlich unverändert.
    if len(text) > _MAX_DIRECT_CHARS:
        text = text[:_MAX_DIRECT_CHARS]

    kwargs: dict = {"text": text, "voice": voice}
    if rate is not None:
        kwargs["rate"] = rate

    communicate = edge_tts.Communicate(**kwargs)
    buf = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])
    return buf.getvalue()
