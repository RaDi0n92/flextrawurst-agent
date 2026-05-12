#!/usr/bin/env python3
"""
Reflection Score Formel und should_reflect Entscheidungslogik.
Spec Abschnitt 4 + 5.2.
"""

from datetime import datetime
from typing import Optional

from config import (
    REFLECTION_MIN_ABSTAND_SEC,
    REFLECTION_MIN_MEMORIES,
    REFLECTION_SCORE_THRESHOLD,
    REFLECTION_TAGES_SEC,
)


def berechne(emotions: dict, human_resonance: float = 0.0, pattern_repeat: int = 0) -> float:
    return (
        abs(emotions.get("valence", 5.0) - 5) * 1.2
        + emotions.get("arousal", 5.0) * 0.8
        + abs(emotions.get("dominance", 5.0) - 5) * 0.6
        + human_resonance * 1.5
        + pattern_repeat * 2.0
    )


def should_reflect(
    reflection_score: float,
    last_reflection_time: Optional[datetime],
    memory_count: int,
) -> str:
    now = datetime.now()

    if not last_reflection_time:
        return "reflect" if memory_count >= REFLECTION_MIN_MEMORIES else "wait"

    elapsed = (now - last_reflection_time).total_seconds()

    if elapsed < REFLECTION_MIN_ABSTAND_SEC:
        return "wait"

    if reflection_score > REFLECTION_SCORE_THRESHOLD:
        return "reflect"

    if elapsed > REFLECTION_TAGES_SEC:
        return "reflect"

    return "wait"
