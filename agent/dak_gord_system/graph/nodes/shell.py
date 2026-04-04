from __future__ import annotations

from datetime import datetime

from agent.dak_gord_system.graph.state import AgentState
from agent.dak_gord_system.graph.tools import register_shell_tools
from agent.dak_gord_system.graph.tools.runtime import run_registered_tool


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run_shell_command_node(state: AgentState) -> AgentState:
    register_shell_tools()

    beobachtungen = list(state.get("beobachtungen", []))
    notizen = list(state.get("notizen", []))
    letzte_tool_aktionen = list(state.get("letzte_tool_aktionen", []))

    shell_argv = state.get("shell_argv", [])
    shell_cwd = state.get("shell_cwd", "/root/werkraum")
    shell_timeout = int(state.get("shell_timeout_sec", 15) or 15)

    if not isinstance(shell_argv, list) or not shell_argv:
        return {
            "status": "fehlgeschlagen",
            "fehler": "Kein shell_argv im State vorhanden.",
            "aktueller_schritt": "run_shell_command",
        }

    result, tool_aktion = run_registered_tool(
        state,
        "run_safe_shell",
        {
            "argv": shell_argv,
            "cwd": shell_cwd,
            "timeout_sec": shell_timeout,
        },
        aktion="shell_kommando",
    )
    letzte_tool_aktionen.append(tool_aktion)

    if not result.ok:
        return {
            "status": "fehlgeschlagen",
            "fehler": result.error or "Shell-Tool fehlgeschlagen.",
            "aktueller_schritt": "run_shell_command",
            "letzte_tool_aktionen": letzte_tool_aktionen,
        }

    output = result.output or {}
    stdout = str(output.get("stdout", ""))
    stderr = str(output.get("stderr", ""))
    exit_code = output.get("exit_code", None)

    beobachtungen.append({
        "art": "shell_result",
        "inhalt": stdout[:2000],
        "quelle": "run_safe_shell",
        "zeitstempel": _ts(),
    })

    if stderr.strip():
        beobachtungen.append({
            "art": "shell_stderr",
            "inhalt": stderr[:1000],
            "quelle": "run_safe_shell",
            "zeitstempel": _ts(),
        })

    notizen.append(f"Shell-Kommando ausgefuehrt: {' '.join(shell_argv)}")
    notizen.append(f"Shell-Exit-Code: {exit_code}")

    return {
        "aktueller_schritt": "done",
        "status": "fertig",
        "beobachtungen": beobachtungen,
        "letzte_tool_aktionen": letzte_tool_aktionen,
        "notizen": notizen,
        "fehler": None,
    }
