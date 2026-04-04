from pathlib import Path
from typing import TypedDict, List, Dict

from langgraph.graph import StateGraph, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver

from agent.dak_gord_system.ollama_chat import OllamaChat

llm = OllamaChat()

def lese(pfad: str) -> str:
    p = Path(pfad)
    return p.read_text(encoding="utf-8") if p.exists() else ""

class DialogZustand(TypedDict):
    verlauf: List[Dict[str, str]]          # Chat-Gedächtnis
    letzte_antwort: str                    # letzte Antwort des Systems
    beenden: bool                          # Abbruch-Flag

def eingabe_node(z: DialogZustand):
    # Wichtig: vor interrupt() keine Seiteneffekte
    text = interrupt({"frage": "Du (tippe 'ende' zum Beenden):"})
    if isinstance(text, str) and text.strip().lower() in {"ende", "/ende", "quit", "exit"}:
        return {"beenden": True}

    # Nutzer-Text in Verlauf hängen
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

    # Checkpointer ist Pflicht für interrupt()
    return g.compile(checkpointer=InMemorySaver())

dialog_graf = baue_dialog_graf()
