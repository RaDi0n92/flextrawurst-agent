"""Hilfsfunktionen für lange Text-to-Speech-Ausgaben via edge_tts.

Dieses Modul enthält ausschließlich TTS-Hilfslogik:
- Text wird für die Audio-Erzeugung in sinnvolle Sätze/Satzteile zerlegt.
- Jeder Teil wird einzeln von edge_tts in Audio umgewandelt.
- Die Teile werden mit ffmpeg zu einer einzigen MP3-Datei zusammengefügt.

Der Originaltext (Chat-Output der Wesen) wird dabei NICHT verändert,
gespeichert oder angezeigt – die Aufteilung passiert nur im Arbeitsspeicher
für die Sprachgenerierung.
"""

from __future__ import annotations

import asyncio
import io
import os
import re
import tempfile
from typing import AsyncIterator

import edge_tts


# Maximale Zeichen pro edge_tts-Aufruf. Erfahrungsgemäß bleibt Microsofts
# Edge-TTS bei ~400–500 Zeichen pro Chunk stabil und schnell.
_MAX_CHARS_PER_CHUNK = 420


async def generate_long_tts_audio(text: str, voice: str, rate: str | None = None) -> bytes:
    """Wandelt einen beliebig langen Text in ein einzelnes MP3-Audio um.

    Args:
        text: Der vollständige Originaltext (wird nicht verändert).
        voice: edge_tts-Stimme, z.B. "de-DE-KatjaNeural".
        rate: Optionale Sprechgeschwindigkeit, z.B. "-5%".

    Returns:
        Ein Byte-String mit dem zusammengefügten MP3-Audio.
    """
    text = text.strip()
    if not text:
        return b""

    chunks = _split_text_for_tts(text, max_chars=_MAX_CHARS_PER_CHUNK)
    if not chunks:
        return b""

    audio_chunks: list[bytes] = []
    for chunk in chunks:
        audio = await _tts_for_chunk(chunk, voice, rate)
        if audio:
            audio_chunks.append(audio)

    if not audio_chunks:
        return b""
    if len(audio_chunks) == 1:
        return audio_chunks[0]

    return await _concatenate_mp3_with_ffmpeg(audio_chunks)


def _split_text_for_tts(text: str, max_chars: int) -> list[str]:
    """Teilt Text an Satzgrenzen, niemals mitten im Wort."""
    text = text.strip()
    if not text:
        return []

    # Sätze an . ! ? trennen, aber Satzzeichen am Ende lassen.
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if not sentences:
        return [text[:max_chars]] if len(text) <= max_chars else [text[:max_chars]]

    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        # Einzelner Satz zu lang -> an Nebensatzgrenzen (, ;) aufteilen.
        if len(sentence) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""
            sub_parts = [p.strip() for p in re.split(r"(?<=[,;])\s+", sentence) if p.strip()]
            if not sub_parts:
                chunks.append(sentence[:max_chars])
                continue

            sub_current = ""
            for part in sub_parts:
                if len(sub_current) + len(part) + 1 > max_chars:
                    if sub_current:
                        chunks.append(sub_current.strip())
                    sub_current = part
                else:
                    sub_current = (sub_current + " " + part).strip()
            if sub_current:
                chunks.append(sub_current.strip())
            continue

        # Satz passt noch in aktuellen Chunk.
        if len(current) + len(sentence) + 1 <= max_chars:
            current = (current + " " + sentence).strip()
        else:
            if current:
                chunks.append(current.strip())
            current = sentence

    if current:
        chunks.append(current.strip())

    return chunks


async def _tts_for_chunk(text: str, voice: str, rate: str | None) -> bytes | None:
    """Erzeugt Audio für einen einzelnen Text-Chunk via edge_tts."""
    try:
        kwargs: dict = {"text": text, "voice": voice}
        if rate is not None:
            kwargs["rate"] = rate
        communicate = edge_tts.Communicate(**kwargs)
        buf = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buf.write(chunk["data"])
        audio = buf.getvalue()
        return audio if audio else None
    except Exception:
        return None


async def _concatenate_mp3_with_ffmpeg(audio_chunks: list[bytes]) -> bytes:
    """Fügt mehrere MP3-Byte-Strings mit ffmpeg -c copy zusammen."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _concatenate_mp3_sync, audio_chunks)


def _concatenate_mp3_sync(audio_chunks: list[bytes]) -> bytes:
    """Synchroner Teil der ffmpeg-Konkatenierung."""
    with tempfile.TemporaryDirectory() as tmpdir:
        list_path = os.path.join(tmpdir, "concat_list.txt")
        segment_paths: list[str] = []

        for i, chunk in enumerate(audio_chunks):
            seg_path = os.path.join(tmpdir, f"chunk_{i:04d}.mp3")
            with open(seg_path, "wb") as f:
                f.write(chunk)
            segment_paths.append(seg_path)

        # ffmpeg concat demuxer Listendatei
        with open(list_path, "w", encoding="utf-8") as f:
            for seg_path in segment_paths:
                # Pfad muss für ffmpeg einfach quotet werden.
                f.write(f"file '{seg_path}'\n")

        out_path = os.path.join(tmpdir, "output.mp3")
        import subprocess

        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", list_path,
                "-c", "copy",
                out_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if result.returncode != 0 or not os.path.exists(out_path):
            # Fallback: ersten Chunk zurückgeben, damit nicht alles leer bleibt.
            return audio_chunks[0]

        with open(out_path, "rb") as f:
            return f.read()
