from __future__ import annotations

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from agent.dak_gord_system.graph.state import AgentState
from agent.dak_gord_system.graph.nodes import (
    resolve_file_node,
    read_file_node,
    refresh_focus_node,
    build_summary_node,
    refresh_agent_file_node,
    write_trace_node,
)
from agent.dak_gord_system.graph.nodes.background import (
    background_tick_node,
    write_background_trace_node,
)


def build_minimal_graph():
    builder = StateGraph(AgentState)

    builder.add_node("resolve_file", resolve_file_node)
    builder.add_node("read_file", read_file_node)
    builder.add_node("refresh_focus", refresh_focus_node)
    builder.add_node("build_summary", build_summary_node)
    builder.add_node("refresh_agent_file", refresh_agent_file_node)
    builder.add_node("write_trace", write_trace_node)

    builder.add_edge(START, "resolve_file")
    builder.add_edge("resolve_file", "read_file")
    builder.add_edge("read_file", "refresh_focus")
    builder.add_edge("refresh_focus", "build_summary")
    builder.add_edge("build_summary", "refresh_agent_file")
    builder.add_edge("refresh_agent_file", "write_trace")
    builder.add_edge("write_trace", END)

    checkpointer = InMemorySaver()
    return builder.compile(checkpointer=checkpointer)


def build_background_graph():
    builder = StateGraph(AgentState)

    builder.add_node("background_tick", background_tick_node)
    builder.add_node("write_background_trace", write_background_trace_node)

    builder.add_edge(START, "background_tick")
    builder.add_edge("background_tick", "write_background_trace")
    builder.add_edge("write_background_trace", END)

    checkpointer = InMemorySaver()
    return builder.compile(checkpointer=checkpointer)
