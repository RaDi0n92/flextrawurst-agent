#!/usr/bin/env python3
"""AgentState Definition für das Innenleben-LangGraph."""

from datetime import datetime
from typing import Dict, List, Optional, TypedDict


class AgentState(TypedDict):
    entity_id: str
    current_event: str
    event_source: str            # 'forum_post' | 'chat' | 'reflection' | 'observation'
    event_id: Optional[str]      # deterministisch: 'flarum:post_N:entity' oder Hash
    emotions: Dict
    last_reflection_time: Optional[datetime]
    self_model: Dict
    recent_memories: List
    new_insight: str
    reflection_score: float
    memory_count: int
    human_resonance: float       # Gewicht menschlicher Reaktion (0.0–1.0)
    pattern_repeat: int          # Wiederholungszähler für gleiches Muster
