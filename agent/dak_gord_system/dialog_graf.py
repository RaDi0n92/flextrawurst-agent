import os
from pathlib import Path
from typing import TypedDict, List, Dict

import psycopg
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt
from langgraph.checkpoint.postgres import PostgresSaver

from agent.dak_gord_system.ollama_chat import OllamaChat

llm = OllamaChat()

_DB_URI = os.environ.get(
    "FLEXTRAWURST_DB_URI",
    "postgresql://dak:!Windowsxp02336827359645852@localhost:5432/flextrawurst",
)

def lese(pfad: str) -> str:
    p = Path(pfad)
    return p.read_text(encoding="utf-8") if p.exists() else ""

class DialogZustand(TypedDict):
    verlauf: List[Dict[str, str]]
    letzte_antwort: str
    beenden: bool

def eingabe_node(z: DialogZustand):
    text = interrupt({"frage": "Du (tippe 'ende' zum Beenden):"})
    if isinstance(text, str) and text.strip().lower() in {"ende", "/ende", "quit", "exit"}:
        return {"beenden": True}
    verlauf = list(z["verlauf"])
    verlauf.append({"role": "user", "content": str(text)})
    return {"verlauf": verlauf}

def antwort_node(z: DialogZustand):
    antwort = llm.chat(z["verlauf"], temperatur=0.2)
    verlauf = list(z["verlauf"])
    verlauf.append({"role": "assistant", "content": antwort})
    return {"verlauf": verlauf, "letzte_antwort": antwort}

def routen(z: DialogZustand) -> str:
    return "ENDE" if z.get("beenden") else "WEITER"

def baue_dialog_graf():
    g = StateGraph(DialogZustand)
    g.add_node("EINGABE", eingabe_node)
    g.add_node("ANTWORT", antwort_node)
    g.set_entry_point("EINGABE")
    g.add_edge("EINGABE", "ANTWORT")
    g.add_conditional_edges("ANTWORT", routen, {
        "WEITER": "EINGABE",
        "ENDE": END,
    })
    conn = psycopg.connect(_DB_URI, autocommit=True)
    checkpointer = PostgresSaver(conn)
    checkpointer.setup()
    return g.compile(checkpointer=checkpointer)

dialog_graf = baue_dialog_graf()
