from __future__ import annotations

from pathlib import Path

from agent.dak_gord_system.agentdateien import quelle_zu_agentdatei


def dossier_path_for_source(quelle: str) -> Path:
    return quelle_zu_agentdatei(quelle)


def load_dossier_text(quelle: str) -> tuple[Path, str]:
    pfad = dossier_path_for_source(quelle)
    if not pfad.exists():
        raise FileNotFoundError(f"Keine Agentdatei gefunden: {pfad}")
    return pfad, pfad.read_text(encoding="utf-8")


def _extract_between(text: str, start_marker: str, end_markers: list[str]) -> str:
    start = text.find(start_marker)
    if start == -1:
        return ""
    start += len(start_marker)

    end_positions = []
    for marker in end_markers:
        pos = text.find(marker, start)
        if pos != -1:
            end_positions.append(pos)

    end = min(end_positions) if end_positions else len(text)
    return text[start:end].strip()


def _limit_lines(block: str, max_lines: int) -> list[str]:
    if not block.strip():
        return []
    return block.splitlines()[:max_lines]


def dossier_overview_lines(quelle: str, max_lines: int = 80) -> tuple[Path, list[str]]:
    pfad, text = load_dossier_text(quelle)
    block = _extract_between(text, "AGENTDOSSIER:", ["=== VERLAUF ==="])
    return pfad, _limit_lines(block, max_lines)


def dossier_head_lines(quelle: str, max_lines: int = 60) -> tuple[Path, list[str]]:
    pfad, text = load_dossier_text(quelle)
    block = _extract_between(text, "AGENTDOSSIER:", ["AKTUELLER FOKUS:", "=== VERLAUF ==="])
    return pfad, _limit_lines(block, max_lines)


def dossier_focus_lines(quelle: str, max_lines: int = 60) -> tuple[Path, list[str]]:
    pfad, text = load_dossier_text(quelle)
    block = _extract_between(text, "AKTUELLER FOKUS:", ["=== VERLAUF ==="])
    return pfad, _limit_lines(block, max_lines)


def dossier_question_lines(quelle: str, max_lines: int = 30) -> tuple[Path, list[str]]:
    pfad, text = load_dossier_text(quelle)
    block = _extract_between(text, "OFFENE GRUNDFRAGEN:", ["AKTUELLER FOKUS:", "=== VERLAUF ==="])
    return pfad, _limit_lines(block, max_lines)
