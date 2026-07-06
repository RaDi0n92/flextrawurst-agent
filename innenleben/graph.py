#!/usr/bin/env python3
"""
LangGraph-Graph für das Innenleben-System.
Spec Abschnitt 5.1.
"""

import logging
from datetime import datetime
from typing import Optional

from langgraph.graph import END, START, StateGraph

import selbstmodell
from nodes import memory_writer_node, reflection_node, self_model_integrator
from reflection_score import should_reflect as _should_reflect
from state import AgentState

log = logging.getLogger("innenleben")


def _should_reflect_edge(state: AgentState) -> str:
    entity_id = state["entity_id"]
    score     = state.get("reflection_score", 0.0)
    last      = state.get("last_reflection_time")
    count     = state.get("memory_count", 0)

    entscheidung = _should_reflect(score, last, count)

    if entscheidung == "reflect":
        log.info(f"[REFLECT] {entity_id} | TRIGGER | Score {score:.1f}")
    else:
        elapsed = ""
        if last:
            sec = (datetime.now() - last).total_seconds()
            elapsed = f" | Letzter Run vor {sec/3600:.1f}h"
        log.info(f"[REFLECT] {entity_id} | SKIP{elapsed}")

    return entscheidung


def baue_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("memory_writer", memory_writer_node)
    workflow.add_node("reflection",    reflection_node)
    workflow.add_node("integrator",    self_model_integrator)

    workflow.add_edge(START, "memory_writer")
    workflow.add_conditional_edges(
        "memory_writer",
        _should_reflect_edge,
        {"reflect": "reflection", "wait": END},
    )
    workflow.add_edge("reflection", "integrator")
    workflow.add_edge("integrator", END)

    return workflow.compile()


def verarbeite_ereignis(
    entity_id: str,
    event_text: str,
    event_source: str = "observation",
    human_resonance: float = 0.0,
    pattern_repeat: int = 0,
    event_id: Optional[str] = None,
) -> dict:
    """Haupteinstiegspunkt. last_reflection_time wird aus dem Selbstmodell geladen."""
    g = baue_graph()

    modell = selbstmodell.laden(entity_id)

    last_rt = None
    if raw_ts := modell.get("last_reflection_time"):
        try:
            last_rt = datetime.fromisoformat(raw_ts)
        except Exception:
            pass

    initial_state: AgentState = {
        "entity_id":            entity_id,
        "current_event":        event_text,
        "event_source":         event_source,
        "event_id":             event_id,
        "emotions":             {},
        "last_reflection_time": last_rt,
        "self_model":           modell,
        "recent_memories":      [],
        "new_insight":          "",
        "reflection_score":     0.0,
        "memory_count":         0,
        "human_resonance":      human_resonance,
        "pattern_repeat":       pattern_repeat,
    }

    result = g.invoke(initial_state)

    # last_reflection_time zurückschreiben wenn Reflexion stattfand
    if result.get("new_insight"):
        aktuell = selbstmodell.laden(entity_id)
        aktuell["last_reflection_time"] = result["last_reflection_time"].isoformat()
        selbstmodell.speichern(entity_id, aktuell)

    return result


if __name__ == "__main__":
    # Schnelltest
    result = verarbeite_ereignis(
        entity_id="Schorschel",
        event_text="Daniel hat mich heute direkt angesprochen und nach meiner Meinung zum Forum gefragt.",
        event_source="chat",
        human_resonance=0.8,
    )
    print(f"\nFinal Score: {result.get('reflection_score', 0):.1f}")
    print(f"Insight: {result.get('new_insight', 'keiner')}")
