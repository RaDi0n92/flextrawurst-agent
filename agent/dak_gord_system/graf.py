from pathlib import Path
import subprocess

from langgraph.graph import StateGraph, END

from agent.dak_gord_system.zustand import Bauzustand, Auftrag
from agent.dak_gord_system.ollama_chat import OllamaChat

llm = OllamaChat()

def lese_datei(pfad: str) -> str:
    p = Path(pfad)
    return p.read_text(encoding="utf-8") if p.exists() else ""

def dateibaum(max_tiefe: int = 4) -> str:
    cmd = ["bash", "-lc", f"find . -maxdepth {max_tiefe} -type f | sed 's|^\\./||' | sort"]
    return subprocess.check_output(cmd, text=True)

def eingabe(z: Bauzustand) -> Bauzustand:
    system = lese_datei("agent/dak_gord_system/aufforderungen/system.md")
    antwort = llm.chat([
        {"role": "system", "content": system + "\nExtrahiere: Ziel, Regeln, Erledigt-wenn als Stichpunkte."},
        {"role": "user", "content": z.nutzer_text},
    ])
    z.auftrag = Auftrag(ziel=z.nutzer_text)
    z.plan = [zeile.strip() for zeile in antwort.splitlines() if zeile.strip()]
    return z

def planen(z: Bauzustand) -> Bauzustand:
    verfassung = lese_datei("docs/vision/verfassung.md")
    system = lese_datei("agent/dak_gord_system/aufforderungen/system.md")
    antwort = llm.chat([
        {"role": "system", "content": system + "\nErstelle einen Umsetzungsplan. Nenne Dateien und einen Test-Befehl."},
        {"role": "user", "content": f"VERFASSUNG:\n{verfassung}\n\nAUFTRAG:\n{z.auftrag.ziel}\n\nNotizen:\n" + "\n".join(z.plan)},
    ])
    z.plan = [zeile.strip() for zeile in antwort.splitlines() if zeile.strip()]
    return z

def verfassung_pruefen(z: Bauzustand) -> Bauzustand:
    verfassung = lese_datei("docs/vision/verfassung.md")
    schutz = lese_datei("agent/dak_gord_system/aufforderungen/verfassungs_schutz.md")
    antwort = llm.chat([
        {"role": "system", "content": schutz},
        {"role": "user", "content": f"VERFASSUNG:\n{verfassung}\n\nPLAN:\n" + "\n".join(z.plan)},
    ])
    text = [a.strip() for a in antwort.splitlines() if a.strip()]
    if len(text) == 1 and text[0].strip().upper() == "OK":
        z.verfassungs_warnungen = []
    else:
        z.verfassungs_warnungen = text
    return z

def kontext(z: Bauzustand) -> Bauzustand:
    z.kontext["dateibaum"] = dateibaum()
    return z

def umsetzen(z: Bauzustand) -> Bauzustand:
    system = lese_datei("agent/dak_gord_system/aufforderungen/system.md")
    regeln = lese_datei("agent/dak_gord_system/aufforderungen/code_regeln.md")
    antwort = llm.chat([
        {"role": "system", "content": system + "\n" + regeln + "\nGib NUR den Patch als unified diff aus."},
        {"role": "user", "content": "DATEIBAUM:\n" + z.kontext["dateibaum"] + "\n\nPLAN:\n" + "\n".join(z.plan)},
    ])
    z.patch = antwort
    return z

def baue_graf():
    g = StateGraph(Bauzustand)
    g.add_node("EINGABE", eingabe)
    g.add_node("PLANEN", planen)
    g.add_node("VERFASSUNG", verfassung_pruefen)
    g.add_node("KONTEXT", kontext)
    g.add_node("UMSETZEN", umsetzen)

    g.set_entry_point("EINGABE")
    g.add_edge("EINGABE", "PLANEN")
    g.add_edge("PLANEN", "VERFASSUNG")
    g.add_edge("VERFASSUNG", "KONTEXT")
    g.add_edge("KONTEXT", "UMSETZEN")
    g.add_edge("UMSETZEN", END)
    return g.compile()

graf = baue_graf()
