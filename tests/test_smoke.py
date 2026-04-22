"""Smoke tests for dak-gord-system core components."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_imports():
    """All core modules must import without error."""
    import importlib
    mods = [
        "agent.dak_gord_system.graphen.gespraechsgraf",
        "agent.dak_gord_system.ollama_chat",
        "agent.dak_gord_system.neugierkern",
        "agent.dak_gord_system.schreibsystem",
        "agent.dak_gord_system.anschlusskontext",
        "agent.dak_gord_system.verdichtung",
        "agent.dak_gord_system.agentdateien",
        "agent.dak_gord_system.dateiwerkzeuge",
        "agent.dak_gord_system.sandbox",
        "agent.dak_gord_system.graph.build",
        "agent.dak_gord_system.graph.state",
        "agent.dak_gord_system.graph.tools",
    ]
    for m in mods:
        importlib.import_module(m)


def test_ollama_erreichbar():
    """Ollama API must be reachable and have at least one model."""
    import requests
    r = requests.get("http://localhost:11434/api/tags", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert len(data.get("models", [])) > 0, "Kein Ollama-Modell geladen"


def test_postgres_verbindung():
    """PostgreSQL checkpoint connection must work."""
    from agent.dak_gord_system.herz.postgres_herz import postgres_kontext
    with postgres_kontext() as ckpt:
        assert ckpt is not None


def test_graph_baut():
    """Dialog graph must compile with postgres checkpointer."""
    from agent.dak_gord_system.graphen.gespraechsgraf import baue_graf
    from agent.dak_gord_system.herz.postgres_herz import postgres_kontext
    with postgres_kontext() as ckpt:
        g = baue_graf(ckpt)
        assert g is not None


def test_systemtext_enthaelt_gedaechtnis():
    """System prompt must include tool docs."""
    from agent.dak_gord_system.graphen.gespraechsgraf import _systemtext
    text = _systemtext()
    assert "##LESEN:" in text
    assert "##CODE_START##" in text
    assert "##SCHREIBEN:" in text


def test_tool_read_text_file():
    """read_text_file tool must return status fertig."""
    import subprocess, sys, json
    cmd = [
        sys.executable, "-m", "agent.dak_gord_system.graph.run_tool_agent",
        "read_text_file",
        json.dumps({"path": "/root/werkraum/requirements.txt", "max_chars": 100}),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="/root/werkraum", timeout=30)
    assert result.returncode == 0
    assert "status: fertig" in result.stdout


def test_sandbox_einfacher_code():
    """Sandbox must execute simple Python code."""
    from agent.dak_gord_system.sandbox import fuehre_code_aus
    ergebnis = fuehre_code_aus("print('hallo welt')")
    assert ergebnis["ok"]
    assert "hallo welt" in ergebnis["stdout"]


def test_sandbox_fehler_wird_abgefangen():
    """Sandbox must handle code errors gracefully."""
    from agent.dak_gord_system.sandbox import fuehre_code_aus
    ergebnis = fuehre_code_aus("raise ValueError('test fehler')")
    assert not ergebnis["ok"]
    assert "ValueError" in ergebnis["stderr"]


def test_sandbox_timeout():
    """Sandbox must enforce timeout."""
    from agent.dak_gord_system.sandbox import fuehre_code_aus, SANDBOX_TIMEOUT
    import time
    ergebnis = fuehre_code_aus(f"import time; time.sleep({SANDBOX_TIMEOUT + 5})")
    assert not ergebnis["ok"]
    assert "Timeout" in ergebnis["stderr"]


def test_werkzeugaufrufe_lesen(tmp_path):
    """LLM response parser must detect and execute ##LESEN## markers."""
    testdatei = tmp_path / "test.txt"
    testdatei.write_text("Inhalt fuer Lesen-Test", encoding="utf-8")

    import sys
    sys.path.insert(0, "/root/werkraum")
    from starte_dak_gord_system import _verarbeite_llm_werkzeugaufrufe

    antwort = f"Ich lese die Datei:\n##LESEN: {testdatei}##\nFertig."
    ausgaben = _verarbeite_llm_werkzeugaufrufe(antwort)
    assert len(ausgaben) == 1
    assert "Inhalt fuer Lesen-Test" in ausgaben[0]


def test_werkzeugaufrufe_code():
    """LLM response parser must detect and execute ##CODE_START## blocks."""
    import sys
    sys.path.insert(0, "/root/werkraum")
    from starte_dak_gord_system import _verarbeite_llm_werkzeugaufrufe

    antwort = "Ich rechne:\n##CODE_START##\nprint(2 + 2)\n##CODE_ENDE##\nFertig."
    ausgaben = _verarbeite_llm_werkzeugaufrufe(antwort)
    assert len(ausgaben) == 1
    assert "4" in ausgaben[0]


def test_werkzeugaufrufe_leer_bei_kein_marker():
    """No tool markers = empty list, no side effects."""
    import sys
    sys.path.insert(0, "/root/werkraum")
    from starte_dak_gord_system import _verarbeite_llm_werkzeugaufrufe

    antwort = "Eine normale Antwort ohne Werkzeuge."
    ausgaben = _verarbeite_llm_werkzeugaufrufe(antwort)
    assert ausgaben == []


def test_vision_kern_geladen():
    """Vision5 kern must be loaded and contain key flextrawurst concepts."""
    from agent.dak_gord_system.graphen.gespraechsgraf import _lade_vision_kern
    kern = _lade_vision_kern()
    assert len(kern) > 500
    assert "flextrawurst" in kern
    assert "Entit" in kern  # Entitäten


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
