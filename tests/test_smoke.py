"""Smoke tests for dak-gord-system core components."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

_braucht_postgres = pytest.mark.skipif(
    not os.getenv("DAK_GORD_DB_URI"),
    reason="DAK_GORD_DB_URI nicht gesetzt — postgres-Tests übersprungen",
)


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


@_braucht_postgres
def test_postgres_verbindung():
    """PostgreSQL checkpoint connection must work."""
    from agent.dak_gord_system.herz.postgres_herz import postgres_kontext
    with postgres_kontext() as ckpt:
        assert ckpt is not None


@_braucht_postgres
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


@_braucht_postgres
def test_tool_read_text_file():
    """read_text_file tool must return status fertig."""
    import subprocess, sys, json
    umgebung = {**os.environ, "DAK_GORD_DB_URI": os.environ["DAK_GORD_DB_URI"]}
    cmd = [
        sys.executable, "-m", "agent.dak_gord_system.graph.run_tool_agent",
        "read_text_file",
        json.dumps({"path": "/root/werkraum/requirements.txt", "max_chars": 100}),
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd="/root/werkraum", timeout=30, env=umgebung
    )
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


def test_sandbox_from_import_escape():
    """Sandbox must block 'from subprocess import run' escape vector."""
    from agent.dak_gord_system.sandbox import fuehre_code_aus
    ergebnis = fuehre_code_aus("from subprocess import run; run(['id'])")
    assert not ergebnis["ok"]
    assert "Verboten" in ergebnis["stderr"]


def test_sandbox_exec_escape():
    """Sandbox must block exec() builtin."""
    from agent.dak_gord_system.sandbox import fuehre_code_aus
    ergebnis = fuehre_code_aus("exec(\"import os; os.system('id')\")")
    assert not ergebnis["ok"]
    assert "Verboten" in ergebnis["stderr"]


def test_sandbox_dunder_import_escape():
    """Sandbox must block __import__ builtin."""
    from agent.dak_gord_system.sandbox import fuehre_code_aus
    ergebnis = fuehre_code_aus("__import__('os').system('id')")
    assert not ergebnis["ok"]
    assert "Verboten" in ergebnis["stderr"]


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


def test_organ_reifedruck():
    """Zwischenraumorgan muss Reifedruck akkumulieren und Transfer auslösen."""
    from agent.dak_gord_system.kerne.zwischenraumorgan import Zwischenraumorgan, REIFE_SCHWELLE
    organ = Zwischenraumorgan()
    organ.ablegen("Testgedanke der reif werden soll")
    assert organ.keime[0].reifedruck == 0

    for _ in range(REIFE_SCHWELLE):
        organ.tick()

    assert organ.keime[0].ist_reif()
    transfer, verblasst = organ.pruefe_reife()
    assert len(transfer) == 1
    assert transfer[0].text == "Testgedanke der reif werden soll"
    assert len(verblasst) == 0


def test_organ_verblassen():
    """Zwischenraum-Keime müssen nach VERBLASSE_SCHWELLE entfernt werden."""
    from agent.dak_gord_system.kerne.zwischenraumorgan import Zwischenraumorgan, VERBLASSE_SCHWELLE
    organ = Zwischenraumorgan()
    organ.ablegen("Dieser Gedanke wird verblassen")

    for _ in range(VERBLASSE_SCHWELLE):
        organ.tick()

    assert organ.keime[0].ist_verblasst()
    _, verblasst = organ.pruefe_reife()
    assert len(verblasst) == 1
    assert len(organ.keime) == 0  # entfernt


def test_resonanz_beschleuniger():
    """OrganManager soll Paare zwischen Zwischenraum und Erinnerung erkennen."""
    from agent.dak_gord_system.kerne.organ_manager import OrganManager
    mgr = OrganManager()
    mgr.erinnerung.merken("fakt", "Permeabilität bedeutet offene Verbindung zwischen Konzepten")
    mgr.zwischenraum.ablegen("Verbindung zwischen Konzepten ohne expliziten Pfad")
    mgr._resonanz_beschleuniger()
    fragen = [a.frage for a in mgr.entscheidung.offene_abwaegungen]
    assert any("Spannung:" in f for f in fragen)


def test_verblassen_log(tmp_path, monkeypatch):
    """Verblasste Keime müssen ins Log geschrieben werden, nicht still verschwinden."""
    import agent.dak_gord_system.kerne.gedaechtnisspeicher as gs
    monkeypatch.setattr(gs, "BASIS", tmp_path)

    from agent.dak_gord_system.kerne.organ_manager import OrganManager
    from agent.dak_gord_system.kerne.zwischenraumorgan import VERBLASSE_SCHWELLE

    mgr = OrganManager()
    mgr.zwischenraum.ablegen("Dieser Keim wird verblassen")
    # Auf Verblassung treiben
    for _ in range(VERBLASSE_SCHWELLE):
        mgr.zwischenraum.tick()

    mgr._verarbeite_reife()

    import json
    log_pfad = tmp_path / "verblassen_log.json"
    assert log_pfad.exists(), "Verblassen-Log muss angelegt werden"
    eintraege = json.loads(log_pfad.read_text())
    assert len(eintraege) == 1
    assert "Dieser Keim wird verblassen" in eintraege[0]["text"]


def test_beziehungsorgan_feedback():
    """Beziehungsorgan muss LLM-Antwort verarbeiten und Zustand anpassen."""
    from agent.dak_gord_system.kerne.beziehungsorgan import Beziehungsorgan
    organ = Beziehungsorgan()
    organ.lese_hinweis("ich brauche mehr struktur bitte")
    assert organ.zustand.strukturbedarf >= 1
    # Lange strukturierte Antwort senkt Strukturbedarf
    organ.lese_antwort_hinweis("x" * 900)
    assert organ.zustand.strukturbedarf == 0


def test_routing_resonanz_im_code_kontext():
    """'Wie implementiere ich Resonanz-Logik?' → MITTEL, nicht TIEF (Code schlägt Philosophie)."""
    from agent.dak_gord_system.ollama_chat import waehle_modell, MODELL_MITTEL, MODELL_SCHNELL
    # Code-Kontext mit philosophischem Begriff → Mittel
    ergebnis = waehle_modell("Wie implementiere ich Resonanz-Logik in Python?")
    assert ergebnis == MODELL_MITTEL
    # Blitz-Frage bleibt Blitz (kein Code-Kontext)
    ergebnis_blitz = waehle_modell("was ist 2+2? kurz bitte")
    assert ergebnis_blitz == MODELL_SCHNELL
    # Reiner Philosophie-Begriff ohne Code → Mittel (26b nur explizit)
    ergebnis_tief = waehle_modell("was bedeutet Zwischenraum für das Wesen?")
    assert ergebnis_tief == MODELL_MITTEL


def test_arbeitsbewegung_verlauf_akkumuliert():
    """Verlauf akkumuliert Bewegungen, kurzbild() zeigt Trend mit Pfeil."""
    from agent.dak_gord_system.kerne.beziehungsorgan import Beziehungsorgan
    organ = Beziehungsorgan()
    organ.lese_hinweis("ich bin unsicher")        # tastend
    organ.lese_hinweis("ich will tiefer gehen")   # vertiefend
    organ.lese_hinweis("noch mehr davon")          # vertiefend
    assert len(organ.zustand.arbeitsbewegung_verlauf) == 3
    bild = organ.kurzbild()
    assert "→" in bild, f"Trend-Pfeil fehlt in kurzbild(): {bild!r}"
    assert "tastend" in bild


def test_pool_schliesst_bei_shutdown():
    """schliesse_pool() muss Pool auf None setzen — kein offener ConnectionPool nach Shutdown."""
    import agent.dak_gord_system.herz.postgres_herz as herz
    # Pool erzwingen falls noch nicht offen (ohne echte DB — direkt _pool setzen)
    original = herz._pool
    from unittest.mock import MagicMock
    mock_pool = MagicMock()
    herz._pool = mock_pool
    herz.schliesse_pool()
    assert herz._pool is None
    mock_pool.close.assert_called_once()
    # Wiederherstellen
    herz._pool = original


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
