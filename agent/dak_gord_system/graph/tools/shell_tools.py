from __future__ import annotations

import subprocess
from pathlib import Path

from .base import ToolContext, ToolDefinition, ToolResult
from .registry import ToolRegistry, registry


WERKRAUM_ROOT = Path("/root/werkraum")
ALLOWED_COMMANDS = {
    "pwd",
    "ls",
    "find",
    "grep",
    "sed",
    "head",
    "tail",
    "wc",
    "git",
    "python3",
}


def _safe_cwd(cwd_value: str | None) -> Path:
    if not cwd_value:
        return WERKRAUM_ROOT

    raw = Path(cwd_value).expanduser()
    resolved = raw.resolve(strict=False)

    try:
        resolved.relative_to(WERKRAUM_ROOT)
    except ValueError as exc:
        raise ValueError(f"cwd ausserhalb von /root/werkraum nicht erlaubt: {resolved}") from exc

    return resolved


def _run_safe_shell(ctx: ToolContext, args: dict[str, object]) -> ToolResult:
    tool_name = "run_safe_shell"
    try:
        argv = args.get("argv")
        if not isinstance(argv, list) or not argv or not all(isinstance(x, str) for x in argv):
            return ToolResult(
                ok=False,
                tool=tool_name,
                risk="medium",
                error="argv muss eine nicht-leere Liste von Strings sein.",
            )

        command = argv[0]
        if command not in ALLOWED_COMMANDS:
            return ToolResult(
                ok=False,
                tool=tool_name,
                risk="medium",
                error=f"Kommando nicht erlaubt: {command}",
            )

        cwd = _safe_cwd(args.get("cwd") if isinstance(args.get("cwd"), str) else None)
        timeout_sec = int(args.get("timeout_sec", 15))

        result = subprocess.run(
            argv,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )

        return ToolResult(
            ok=True,
            tool=tool_name,
            risk="medium",
            output={
                "argv": argv,
                "cwd": str(cwd),
                "exit_code": result.returncode,
                "stdout": result.stdout[:4000],
                "stderr": result.stderr[:4000],
            },
            artifacts=[],
            meta={"task_id": ctx.task_id, "thread_id": ctx.thread_id},
        )
    except subprocess.TimeoutExpired:
        return ToolResult(
            ok=False,
            tool=tool_name,
            risk="medium",
            error="Shell-Tool Timeout erreicht.",
        )
    except Exception as exc:
        return ToolResult(
            ok=False,
            tool=tool_name,
            risk="medium",
            error=str(exc),
        )


def register_shell_tools(reg: ToolRegistry | None = None) -> ToolRegistry:
    reg = reg or registry

    reg.register(
        ToolDefinition(
            name="run_safe_shell",
            description="Fuehrt erlaubte Shell-Kommandos innerhalb von /root/werkraum aus.",
            risk="medium",
            input_schema={
                "type": "object",
                "required": ["argv"],
                "properties": {
                    "argv": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "cwd": {"type": "string"},
                    "timeout_sec": {"type": "integer"},
                },
            },
            handler=_run_safe_shell,
        ),
        overwrite=True,
    )

    return reg
