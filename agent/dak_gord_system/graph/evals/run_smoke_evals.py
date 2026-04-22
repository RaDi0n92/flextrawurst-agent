from __future__ import annotations

import ast
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from agent.dak_gord_system.graph.trace_events import append_trace_event


EVALS_DIR = Path("/root/werkraum/agent/dak_gord_system/spuren/evals")
TRACE_FILE = Path("/root/werkraum/agent/dak_gord_system/spuren/traces/events.jsonl")
EVALS_DIR.mkdir(parents=True, exist_ok=True)

CORE_REQUIRED = {
    "tool_low_read_text_file",
    "tool_medium_shell_pending",
    "tool_resume_genehmigt",
    "tool_medium_shell_pending_2",
    "tool_resume_abgelehnt",
    "background_single_neugier_scan",
    "background_single_vision_cycle",
    "background_cycle_both",
    "trace_jsonl_integrity",
    "mcp_tool_low_echo",
    "tool_registry_describe_contains_mcp_echo",
    "mcp_tool_low_echo_subprocess",
    "mcp_protocol_tools_call_roundtrip",
    "mcp_tool_low_uppercase",
    "mcp_protocol_tools_list",
    "mcp_server_alt_echo_profile",
    "mcp_server_alt_uppercase_profile",
    "mcp_server_alt_list_profile",
    "mcp_tool_medium_write_note_pending",
    "mcp_tool_resume_genehmigt_write_note",
    "mcp_tool_medium_write_note_pending_2",
    "mcp_tool_resume_abgelehnt_write_note",
}

INTEGRATION_CASES = {
    "graph_run_agent_vision4",
}


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _slug_ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _run(cmd: list[str], cwd: str = "/root/werkraum") -> tuple[int, str, str]:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=cwd)
    return result.returncode, result.stdout, result.stderr


def _run_with_retries(cmd: list[str], attempts: int = 3, pause_sec: float = 3.0) -> tuple[int, str, str]:
    last = (1, "", "Kein Lauf ausgefuehrt.")
    for idx in range(attempts):
        rc, stdout, stderr = _run(cmd)
        last = (rc, stdout, stderr)
        state = _parse_final_state(stdout)
        if rc == 0 and state.get("status") == "fertig":
            return last
        if idx < attempts - 1:
            time.sleep(pause_sec)
    return last


def _parse_final_state(stdout: str) -> dict:
    lines = stdout.splitlines()
    if "FINAL STATE:" not in lines:
        return {}
    start = lines.index("FINAL STATE:") + 1
    data: dict = {}
    for line in lines[start:]:
        if not line.strip():
            continue
        if ": " not in line:
            continue
        key, raw = line.split(": ", 1)
        value = raw
        try:
            value = ast.literal_eval(raw)
        except Exception:
            value = raw
        data[key.strip()] = value
    return data


def _record_case(
    results: list[dict],
    name: str,
    ok: bool,
    detail: str,
    state: dict | None = None,
    stdout: str = "",
    stderr: str = "",
) -> None:
    results.append(
        {
            "name": name,
            "ok": ok,
            "detail": detail,
            "state": state or {},
            "stdout_preview": stdout[:3000],
            "stderr_preview": stderr[:2000],
        }
    )


def main() -> None:
    results: list[dict] = []

    cmd = [sys.executable, "-m", "agent.dak_gord_system.graph.run_agent", "vision4.md"]
    rc, stdout, stderr = _run_with_retries(cmd, attempts=3, pause_sec=3.0)
    state = _parse_final_state(stdout)
    ok = rc == 0 and state.get("status") == "fertig"
    _record_case(results, "graph_run_agent_vision4", ok, f"rc={rc}, status={state.get('status')}", state, stdout, stderr)

    cmd = [
        sys.executable,
        "-m",
        "agent.dak_gord_system.graph.run_tool_agent",
        "read_text_file",
        json.dumps({"path": "/root/werkraum/docs/agent/ARCHITEKTUR_HEUTE.md", "max_chars": 120}),
    ]
    rc, stdout, stderr = _run(cmd)
    state = _parse_final_state(stdout)
    ok = rc == 0 and state.get("status") == "fertig" and state.get("approval_status") == "nicht_noetig"
    _record_case(
        results,
        "tool_low_read_text_file",
        ok,
        f"rc={rc}, status={state.get('status')}, approval={state.get('approval_status')}",
        state,
        stdout,
        stderr,
    )

    cmd = [
        sys.executable,
        "-m",
        "agent.dak_gord_system.graph.run_tool_agent",
        "run_safe_shell",
        json.dumps({"argv": ["pwd"], "cwd": "/root/werkraum", "timeout_sec": 10}),
    ]
    rc, stdout, stderr = _run(cmd)
    state_open = _parse_final_state(stdout)
    open_task_id = str(state_open.get("task_id", "") or "")
    ok = rc == 0 and state_open.get("status") == "wartet_auf_freigabe" and state_open.get("approval_status") == "offen"
    _record_case(
        results,
        "tool_medium_shell_pending",
        ok,
        f"rc={rc}, status={state_open.get('status')}, approval={state_open.get('approval_status')}, task_id={open_task_id}",
        state_open,
        stdout,
        stderr,
    )

    if open_task_id:
        cmd = [
            sys.executable,
            "-m",
            "agent.dak_gord_system.graph.run_tool_resume",
            open_task_id,
            "genehmigt",
        ]
        rc, stdout, stderr = _run(cmd)
        state = _parse_final_state(stdout)
        ok = rc == 0 and state.get("status") == "fertig" and state.get("approval_status") == "genehmigt"
        _record_case(
            results,
            "tool_resume_genehmigt",
            ok,
            f"rc={rc}, status={state.get('status')}, approval={state.get('approval_status')}",
            state,
            stdout,
            stderr,
        )
    else:
        _record_case(results, "tool_resume_genehmigt", False, "Kein offener task_id aus Vorfall 3 vorhanden.")

    cmd = [
        sys.executable,
        "-m",
        "agent.dak_gord_system.graph.run_tool_agent",
        "run_safe_shell",
        json.dumps({"argv": ["pwd"], "cwd": "/root/werkraum", "timeout_sec": 10}),
    ]
    rc, stdout, stderr = _run(cmd)
    state_open2 = _parse_final_state(stdout)
    open_task_id2 = str(state_open2.get("task_id", "") or "")
    ok = rc == 0 and state_open2.get("status") == "wartet_auf_freigabe" and state_open2.get("approval_status") == "offen"
    _record_case(
        results,
        "tool_medium_shell_pending_2",
        ok,
        f"rc={rc}, status={state_open2.get('status')}, approval={state_open2.get('approval_status')}, task_id={open_task_id2}",
        state_open2,
        stdout,
        stderr,
    )

    if open_task_id2:
        cmd = [
            sys.executable,
            "-m",
            "agent.dak_gord_system.graph.run_tool_resume",
            open_task_id2,
            "abgelehnt",
        ]
        rc, stdout, stderr = _run(cmd)
        state = _parse_final_state(stdout)
        ok = rc == 0 and state.get("status") == "blockiert" and state.get("approval_status") == "abgelehnt"
        _record_case(
            results,
            "tool_resume_abgelehnt",
            ok,
            f"rc={rc}, status={state.get('status')}, approval={state.get('approval_status')}",
            state,
            stdout,
            stderr,
        )
    else:
        _record_case(results, "tool_resume_abgelehnt", False, "Kein offener task_id aus Vorfall 5 vorhanden.")

    cmd = [sys.executable, "-m", "agent.dak_gord_system.graph.run_background_agent", "neugier_scan"]
    rc, stdout, stderr = _run(cmd)
    state = _parse_final_state(stdout)
    ok = rc == 0 and state.get("status") == "fertig" and state.get("run_type") == "neugier_scan"
    _record_case(
        results,
        "background_single_neugier_scan",
        ok,
        f"rc={rc}, status={state.get('status')}, run_type={state.get('run_type')}",
        state,
        stdout,
        stderr,
    )

    cmd = [sys.executable, "-m", "agent.dak_gord_system.graph.run_background_agent", "vision_cycle"]
    rc, stdout, stderr = _run(cmd)
    state = _parse_final_state(stdout)
    ok = rc == 0 and state.get("status") == "fertig" and state.get("run_type") == "vision_cycle"
    _record_case(
        results,
        "background_single_vision_cycle",
        ok,
        f"rc={rc}, status={state.get('status')}, run_type={state.get('run_type')}",
        state,
        stdout,
        stderr,
    )

    cmd = [sys.executable, "-m", "agent.dak_gord_system.graph.run_background_cycle"]
    rc, stdout, stderr = _run(cmd)
    final_count = stdout.count("FINAL STATE:")
    has_neugier = "run_type: neugier_scan" in stdout
    has_vision = "run_type: vision_cycle" in stdout
    ok = rc == 0 and final_count == 2 and has_neugier and has_vision
    _record_case(
        results,
        "background_cycle_both",
        ok,
        f"rc={rc}, final_count={final_count}, has_neugier={has_neugier}, has_vision={has_vision}",
        {},
        stdout,
        stderr,
    )

    exists = TRACE_FILE.exists()
    glued = False
    if exists:
        text = TRACE_FILE.read_text(encoding="utf-8", errors="replace")
        glued = '}}{"timestamp":' in text
    ok = exists and not glued
    _record_case(results, "trace_jsonl_integrity", ok, f"exists={exists}, glued={glued}")

    cmd = [
        sys.executable,
        "-m",
        "agent.dak_gord_system.graph.run_tool_agent",
        "mcp_echo",
        json.dumps({"text": "Hallo MCP", "server_name": "mock"}),
    ]
    rc, stdout, stderr = _run(cmd)
    state = _parse_final_state(stdout)
    ok = (
        rc == 0
        and state.get("status") == "fertig"
        and state.get("approval_status") == "nicht_noetig"
        and state.get("tool_name") == "mcp_echo"
    )
    _record_case(
        results,
        "mcp_tool_low_echo",
        ok,
        f"rc={rc}, status={state.get('status')}, approval={state.get('approval_status')}, tool={state.get('tool_name')}",
        state,
        stdout,
        stderr,
    )

    cmd = [
        sys.executable,
        "-c",
        (
            "import json; "
            "from agent.dak_gord_system.graph.tools.runtime import ensure_default_tools_registered; "
            "from agent.dak_gord_system.graph.tools.registry import registry; "
            "ensure_default_tools_registered(); "
            "print(json.dumps(registry.describe(), ensure_ascii=False))"
        ),
    ]
    rc, stdout, stderr = _run(cmd)
    name_ok = '"name": "mcp_echo"' in stdout
    transport_ok = '"transport": "mcp"' in stdout
    server_ok = '"server_name": "mock"' in stdout
    ok = rc == 0 and name_ok and transport_ok and server_ok
    _record_case(
        results,
        "tool_registry_describe_contains_mcp_echo",
        ok,
        f"rc={rc}, name={'mcp_echo' if name_ok else None}, transport={'mcp' if transport_ok else None}, server={'mock' if server_ok else None}",
        {},
        stdout,
        stderr,
    )

    cmd = [
        sys.executable,
        "-m",
        "agent.dak_gord_system.graph.run_tool_agent",
        "mcp_echo",
        json.dumps({"text": "Hallo MCP", "server_name": "mock_subprocess"}),
    ]
    rc, stdout, stderr = _run(cmd)
    state = _parse_final_state(stdout)
    subprocess_json = "subprocess_stdio_json" in stdout
    ok = (
        rc == 0
        and state.get("status") == "fertig"
        and state.get("approval_status") == "nicht_noetig"
        and state.get("tool_name") == "mcp_echo"
        and subprocess_json
    )
    _record_case(
        results,
        "mcp_tool_low_echo_subprocess",
        ok,
        f"rc={rc}, status={state.get('status')}, approval={state.get('approval_status')}, tool={state.get('tool_name')}, subprocess_stdio_json={subprocess_json}",
        state,
        stdout,
        stderr,
    )

    cmd = [
        sys.executable,
        "-c",
        (
            "import json; "
            "from agent.dak_gord_system.graph.tools.mcp_runtime import run_mcp_tool; "
            "print(json.dumps(run_mcp_tool('mcp_echo', {'text': 'Hallo Protokoll'}, server_name='mock_subprocess'), ensure_ascii=False))"
        ),
    ]
    rc, stdout, stderr = _run(cmd)
    protocol_ok = '"protocol": "jsonrpc_like"' in stdout
    method_ok = '"method": "tools/call"' in stdout
    ids_ok = '"request_id":' in stdout and '"response_id":' in stdout
    ok = rc == 0 and protocol_ok and method_ok and ids_ok and '"ok": true' in stdout.lower()
    _record_case(
        results,
        "mcp_protocol_tools_call_roundtrip",
        ok,
        f"rc={rc}, status=fertig, approval=nicht_noetig, tool=mcp_echo, protocol={protocol_ok}, method={method_ok}, ids={ids_ok}",
        {"status": "fertig", "approval_status": "nicht_noetig", "tool_name": "mcp_echo"},
        stdout,
        stderr,
    )

    cmd = [
        sys.executable,
        "-m",
        "agent.dak_gord_system.graph.run_tool_agent",
        "mcp_uppercase",
        json.dumps({"text": "Hallo J4", "server_name": "mock_subprocess"}),
    ]
    rc, stdout, stderr = _run(cmd)
    state = _parse_final_state(stdout)
    has_upper = "HALLO J4" in stdout
    ok = (
        rc == 0
        and state.get("status") == "fertig"
        and state.get("approval_status") == "nicht_noetig"
        and state.get("tool_name") == "mcp_uppercase"
        and has_upper
    )
    _record_case(
        results,
        "mcp_tool_low_uppercase",
        ok,
        f"rc={rc}, status={state.get('status')}, approval={state.get('approval_status')}, tool={state.get('tool_name')}, uppercase={has_upper}",
        state,
        stdout,
        stderr,
    )

    cmd = [
        sys.executable,
        "-c",
        (
            "import json; "
            "from agent.dak_gord_system.graph.tools.mcp_runtime import list_mcp_tools; "
            "print(json.dumps(list_mcp_tools(server_name='mock_subprocess'), ensure_ascii=False))"
        ),
    ]
    rc, stdout, stderr = _run(cmd)
    has_echo = "mcp_echo" in stdout
    has_uppercase = "mcp_uppercase" in stdout
    has_list_method = "tools/list" in stdout
    ok = rc == 0 and has_echo and has_uppercase and has_list_method
    _record_case(
        results,
        "mcp_protocol_tools_list",
    "mcp_tool_medium_write_note_pending",
    "mcp_tool_resume_genehmigt_write_note",
    "mcp_tool_medium_write_note_pending_2",
    "mcp_tool_resume_abgelehnt_write_note",
        ok,
        f"rc={rc}, has_echo={has_echo}, has_uppercase={has_uppercase}, method={has_list_method}",
        {},
        stdout,
        stderr,
    )

    passed = sum(1 for r in results if r["ok"])
    total = len(results)
    overall_ok = passed == total

    core_passed = sum(1 for r in results if r["name"] in CORE_REQUIRED and r["ok"])
    core_total = sum(1 for r in results if r["name"] in CORE_REQUIRED)
    core_ok = core_passed == core_total

    integration_passed = sum(1 for r in results if r["name"] in INTEGRATION_CASES and r["ok"])
    integration_total = sum(1 for r in results if r["name"] in INTEGRATION_CASES)
    integration_ok = integration_passed == integration_total

    report = {
        "timestamp": _ts(),
        "overall_ok": overall_ok,
        "passed": passed,
        "total": total,
        "core_ok": core_ok,
        "core_passed": core_passed,
        "core_total": core_total,
        "integration_ok": integration_ok,
        "integration_passed": integration_passed,
        "integration_total": integration_total,
        "results": results,
    }

    slug = _slug_ts()
    json_path = EVALS_DIR / f"smoke_eval_{slug}.json"
    md_path = EVALS_DIR / f"smoke_eval_{slug}.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        f"# dak+gord-system – Smoke Eval {slug}",
        "",
        f"- Zeit: {report['timestamp']}",
        f"- Core: {'OK' if core_ok else 'FEHLER'} ({core_passed}/{core_total})",
        f"- Integration: {'OK' if integration_ok else 'FEHLER'} ({integration_passed}/{integration_total})",
        f"- Gesamt: {'OK' if overall_ok else 'FEHLER'}",
        f"- Bestanden: {passed}/{total}",
        "",
        "## Fälle",
        "",
    ]

    for item in results:
        md_lines.append(f"### {'OK' if item['ok'] else 'FAIL'} – {item['name']}")
        md_lines.append("")
        md_lines.append(f"- Detail: {item['detail']}")
        state = item.get("state") or {}
        if state:
            md_lines.append(f"- status: {state.get('status', '')}")
            md_lines.append(f"- approval_status: {state.get('approval_status', '')}")
            md_lines.append(f"- task_id: {state.get('task_id', '')}")
        md_lines.append("")

    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    append_trace_event(
        "eval_completed",
        {
            "task_id": f"eval_{slug}",
            "thread_id": "",
            "run_type": "eval",
            "status": "fertig" if overall_ok else "fehlgeschlagen",
            "aktueller_schritt": "done",
            "approval_status": "nicht_noetig",
        },
        overall_ok=overall_ok,
        passed=passed,
        total=total,
        core_ok=core_ok,
        core_passed=core_passed,
        core_total=core_total,
        integration_ok=integration_ok,
        integration_passed=integration_passed,
        integration_total=integration_total,
        json_report=str(json_path),
        md_report=str(md_path),
    )

    print("SMOKE EVAL:")
    print(f"overall_ok: {overall_ok}")
    print(f"passed: {passed}/{total}")
    print(f"json_report: {json_path}")
    print(f"md_report: {md_path}")
    for item in results:
        print(f"- {'OK' if item['ok'] else 'FAIL'} | {item['name']} | {item['detail']}")

    if not core_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
