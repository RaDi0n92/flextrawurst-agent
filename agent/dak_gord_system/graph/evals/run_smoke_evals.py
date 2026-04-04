from __future__ import annotations

import ast
import json
import subprocess
import time
import sys
from datetime import datetime
from pathlib import Path

from agent.dak_gord_system.graph.trace_events import append_trace_event


EVALS_DIR = Path("/root/werkraum/agent/dak_gord_system/spuren/evals")
EVALS_DIR.mkdir(parents=True, exist_ok=True)


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _slug_ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _run(cmd: list[str], cwd: str = "/root/werkraum") -> tuple[int, str, str]:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=cwd)
    return result.returncode, result.stdout, result.stderr

def _run_with_retries(cmd: list[str], attempts: int = 2, pause_sec: float = 1.5) -> tuple[int, str, str]:
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


def _record_case(results: list[dict], name: str, ok: bool, detail: str, state: dict | None = None, stdout: str = "", stderr: str = "") -> None:
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
    rc, stdout, stderr = _run_with_retries(cmd, attempts=2, pause_sec=1.5)
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
    _record_case(results, "tool_low_read_text_file", ok, f"rc={rc}, status={state.get('status')}, approval={state.get('approval_status')}", state, stdout, stderr)

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
    _record_case(results, "tool_medium_shell_pending", ok, f"rc={rc}, status={state_open.get('status')}, approval={state_open.get('approval_status')}, task_id={open_task_id}", state_open, stdout, stderr)

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
        _record_case(results, "tool_resume_genehmigt", ok, f"rc={rc}, status={state.get('status')}, approval={state.get('approval_status')}", state, stdout, stderr)
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
    _record_case(results, "tool_medium_shell_pending_2", ok, f"rc={rc}, status={state_open2.get('status')}, approval={state_open2.get('approval_status')}, task_id={open_task_id2}", state_open2, stdout, stderr)

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
        _record_case(results, "tool_resume_abgelehnt", ok, f"rc={rc}, status={state.get('status')}, approval={state.get('approval_status')}", state, stdout, stderr)
    else:
        _record_case(results, "tool_resume_abgelehnt", False, "Kein offener task_id aus Vorfall 5 vorhanden.")

    passed = sum(1 for r in results if r["ok"])
    total = len(results)
    overall_ok = passed == total

    report = {
        "timestamp": _ts(),
        "overall_ok": overall_ok,
        "passed": passed,
        "total": total,
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

    if not overall_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
