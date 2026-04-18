from __future__ import annotations

import ast
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

EVALS_DIR = Path("/root/werkraum/agent/dak_gord_system/spuren/evals")
EVALS_DIR.mkdir(parents=True, exist_ok=True)
NOTES_PATH = Path("/root/werkraum/agent/dak_gord_system/spuren/mcp_notes.log")


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _slug_ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _run(cmd: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        cwd="/root/werkraum",
    )
    return result.returncode, result.stdout, result.stderr


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
        try:
            value = ast.literal_eval(raw)
        except Exception:
            value = raw
        data[key.strip()] = value

    return data


def _record(
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
            "stdout_preview": stdout[:2500],
            "stderr_preview": stderr[:1200],
        }
    )


def main() -> None:
    results: list[dict] = []

    # J4: uppercase
    cmd = [
        sys.executable,
        "-m",
        "agent.dak_gord_system.graph.run_tool_agent",
        "mcp_uppercase",
        json.dumps({"text": "Hallo J4", "server_name": "mock_subprocess"}),
    ]
    rc, stdout, stderr = _run(cmd)
    state = _parse_final_state(stdout)
    has_upper_j4 = "HALLO J4" in stdout
    ok = (
        rc == 0
        and state.get("status") == "fertig"
        and state.get("approval_status") == "nicht_noetig"
        and state.get("tool_name") == "mcp_uppercase"
        and has_upper_j4
    )
    _record(
        results,
        "j4_uppercase",
        ok,
        f"rc={rc}, status={state.get('status')}, uppercase={has_upper_j4}",
        state,
        stdout,
        stderr,
    )

    # J4: tools/list
    cmd = [
        sys.executable,
        "-c",
        (
            "from agent.dak_gord_system.graph.tools.mcp_runtime import list_mcp_tools; "
            "import json; "
            "print(json.dumps(list_mcp_tools(server_name='mock_subprocess'), ensure_ascii=False))"
        ),
    ]
    rc, stdout, stderr = _run(cmd)
    has_echo = "mcp_echo" in stdout
    has_upper = "mcp_uppercase" in stdout
    has_method = '"method": "tools/list"' in stdout
    ok = rc == 0 and has_echo and has_upper and has_method
    _record(
        results,
        "j4_tools_list",
        ok,
        f"rc={rc}, has_echo={has_echo}, has_upper={has_upper}, method={has_method}",
        {},
        stdout,
        stderr,
    )

    # J5: pending -> approved
    approve_text = f"FAST_J5_APPROVE_{_slug_ts()}"
    cmd = [
        sys.executable,
        "-m",
        "agent.dak_gord_system.graph.run_tool_agent",
        "mcp_write_note",
        json.dumps({"content": approve_text, "server_name": "mock_subprocess"}),
    ]
    rc, stdout, stderr = _run(cmd)
    state_open = _parse_final_state(stdout)
    open_task_id = str(state_open.get("task_id", "") or "")
    ok = (
        rc == 0
        and state_open.get("status") == "wartet_auf_freigabe"
        and state_open.get("approval_status") == "offen"
        and state_open.get("tool_name") == "mcp_write_note"
    )
    _record(
        results,
        "j5_pending_approve",
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
        note_present = NOTES_PATH.exists() and approve_text in NOTES_PATH.read_text(encoding="utf-8", errors="replace")
        ok = (
            rc == 0
            and state.get("status") == "fertig"
            and state.get("approval_status") == "genehmigt"
            and note_present
        )
        _record(
            results,
            "j5_resume_approved",
            ok,
            f"rc={rc}, status={state.get('status')}, approval={state.get('approval_status')}, note_present={note_present}",
            state,
            stdout,
            stderr,
        )
    else:
        _record(results, "j5_resume_approved", False, "Kein offener task_id für genehmigt vorhanden.")

    # J5: pending -> rejected
    reject_text = f"FAST_J5_REJECT_{_slug_ts()}"
    cmd = [
        sys.executable,
        "-m",
        "agent.dak_gord_system.graph.run_tool_agent",
        "mcp_write_note",
        json.dumps({"content": reject_text, "server_name": "mock_subprocess"}),
    ]
    rc, stdout, stderr = _run(cmd)
    state_open2 = _parse_final_state(stdout)
    open_task_id2 = str(state_open2.get("task_id", "") or "")
    ok = (
        rc == 0
        and state_open2.get("status") == "wartet_auf_freigabe"
        and state_open2.get("approval_status") == "offen"
        and state_open2.get("tool_name") == "mcp_write_note"
    )
    _record(
        results,
        "j5_pending_reject",
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
        note_present = NOTES_PATH.exists() and reject_text in NOTES_PATH.read_text(encoding="utf-8", errors="replace")
        ok = (
            rc == 0
            and state.get("status") == "blockiert"
            and state.get("approval_status") == "abgelehnt"
            and not note_present
        )
        _record(
            results,
            "j5_resume_rejected",
            ok,
            f"rc={rc}, status={state.get('status')}, approval={state.get('approval_status')}, note_present={note_present}",
            state,
            stdout,
            stderr,
        )
    else:
        _record(results, "j5_resume_rejected", False, "Kein offener task_id für abgelehnt vorhanden.")

    # K: alt echo
    cmd = [
        sys.executable,
        "-m",
        "agent.dak_gord_system.graph.run_tool_agent",
        "mcp_echo",
        json.dumps({"text": "Hallo K", "server_name": "mock_subprocess_alt"}),
    ]
    rc, stdout, stderr = _run(cmd)
    state = _parse_final_state(stdout)
    has_alt_profile_echo = "server_profile': 'alt'" in stdout
    has_alt_msg = "[alt]" in stdout
    ok = (
        rc == 0
        and state.get("status") == "fertig"
        and state.get("tool_name") == "mcp_echo"
        and has_alt_profile_echo
        and has_alt_msg
    )
    _record(
        results,
        "k_alt_echo",
        ok,
        f"rc={rc}, status={state.get('status')}, alt_profile={has_alt_profile_echo}, alt_msg={has_alt_msg}",
        state,
        stdout,
        stderr,
    )

    # K: alt uppercase
    cmd = [
        sys.executable,
        "-m",
        "agent.dak_gord_system.graph.run_tool_agent",
        "mcp_uppercase",
        json.dumps({"text": "Hallo K", "server_name": "mock_subprocess_alt"}),
    ]
    rc, stdout, stderr = _run(cmd)
    state = _parse_final_state(stdout)
    has_alt_profile_upper = "server_profile': 'alt'" in stdout
    has_alt_upper = "ALT::HALLO K" in stdout
    ok = (
        rc == 0
        and state.get("status") == "fertig"
        and state.get("tool_name") == "mcp_uppercase"
        and has_alt_profile_upper
        and has_alt_upper
    )
    _record(
        results,
        "k_alt_uppercase",
        ok,
        f"rc={rc}, status={state.get('status')}, alt_profile={has_alt_profile_upper}, alt_upper={has_alt_upper}",
        state,
        stdout,
        stderr,
    )

    # K: alt tools/list
    cmd = [
        sys.executable,
        "-c",
        (
            "from agent.dak_gord_system.graph.tools.mcp_runtime import list_mcp_tools; "
            "import json; "
            "print(json.dumps(list_mcp_tools(server_name='mock_subprocess_alt'), ensure_ascii=False))"
        ),
    ]
    rc, stdout, stderr = _run(cmd)
    has_alt_list = '"server_profile": "alt"' in stdout
    has_upper_list = "mcp_uppercase" in stdout
    has_write_list = "mcp_write_note" in stdout
    has_list_method = '"method": "tools/list"' in stdout
    ok = rc == 0 and has_alt_list and has_upper_list and has_write_list and has_list_method
    _record(
        results,
        "k_alt_list",
        ok,
        f"rc={rc}, alt={has_alt_list}, has_upper={has_upper_list}, has_write={has_write_list}, method={has_list_method}",
        {},
        stdout,
        stderr,
    )

    passed = sum(1 for r in results if r["ok"])
    total = len(results)
    overall_ok = passed == total

    slug = _slug_ts()
    json_path = EVALS_DIR / f"eval_mcp_fast_{slug}.json"
    md_path = EVALS_DIR / f"eval_mcp_fast_{slug}.md"

    report = {
        "timestamp": _ts(),
        "overall_ok": overall_ok,
        "passed": passed,
        "total": total,
        "results": results,
    }
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        f"# MCP Fast Eval {slug}",
        "",
        f"- Zeit: {report['timestamp']}",
        f"- Gesamt: {'OK' if overall_ok else 'FEHLER'}",
        f"- Bestanden: {passed}/{total}",
        "",
        "## Fälle",
        "",
    ]

    for item in results:
        md.append(f"### {'OK' if item['ok'] else 'FAIL'} – {item['name']}")
        md.append("")
        md.append(f"- Detail: {item['detail']}")
        state = item.get("state") or {}
        if state:
            md.append(f"- status: {state.get('status', '')}")
            md.append(f"- approval_status: {state.get('approval_status', '')}")
            md.append(f"- task_id: {state.get('task_id', '')}")
        md.append("")

    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("MCP FAST EVAL:")
    print(f"overall_ok: {overall_ok}")
    print(f"passed: {passed}/{total}")
    print(f"json_report: {json_path}")
    print(f"md_report: {md_path}")
    for item in results:
        print(f"- {'OK' if item['ok'] else 'FAIL'} | {item['name']} | {item['detail']}")

    if not overall_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
