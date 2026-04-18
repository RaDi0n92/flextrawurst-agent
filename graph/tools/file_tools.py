from __future__ import annotations

import difflib
from pathlib import Path
from typing import Any

from .base import ToolContext, ToolDefinition, ToolResult
from .registry import ToolRegistry, registry


WERKRAUM_ROOT = Path("/root/werkraum")


def _safe_path(path_value: str) -> Path:
    raw = Path(path_value).expanduser()
    resolved = raw.resolve(strict=False)

    try:
        resolved.relative_to(WERKRAUM_ROOT)
    except ValueError as exc:
        raise ValueError(f"Pfad ausserhalb von /root/werkraum nicht erlaubt: {resolved}") from exc

    return resolved


def _read_text_file(ctx: ToolContext, args: dict[str, Any]) -> ToolResult:
    tool_name = "read_text_file"
    try:
        path = _safe_path(str(args["path"]))
        encoding = str(args.get("encoding", "utf-8"))
        max_chars = int(args.get("max_chars", 4000))

        if not path.exists():
            return ToolResult(
                ok=False,
                tool=tool_name,
                risk="low",
                error=f"Datei existiert nicht: {path}",
            )

        text = path.read_text(encoding=encoding, errors="replace")
        excerpt = text[:max_chars]

        return ToolResult(
            ok=True,
            tool=tool_name,
            risk="low",
            output={
                "path": str(path),
                "text": excerpt,
                "truncated": len(text) > max_chars,
                "total_chars": len(text),
            },
            artifacts=[str(path)],
            meta={"task_id": ctx.task_id, "thread_id": ctx.thread_id},
        )
    except Exception as exc:
        return ToolResult(ok=False, tool=tool_name, risk="low", error=str(exc))


def _write_text_file(ctx: ToolContext, args: dict[str, Any]) -> ToolResult:
    tool_name = "write_text_file"
    try:
        path = _safe_path(str(args["path"]))
        content = str(args.get("content", ""))
        encoding = str(args.get("encoding", "utf-8"))
        mode = str(args.get("mode", "overwrite"))

        old_content = ""
        if path.exists():
            old_content = path.read_text(encoding=encoding, errors="replace")

        path.parent.mkdir(parents=True, exist_ok=True)

        if mode == "append":
            new_content = old_content + content
        elif mode == "overwrite":
            new_content = content
        else:
            return ToolResult(
                ok=False,
                tool=tool_name,
                risk="medium",
                error=f"Unbekannter mode: {mode}",
            )

        path.write_text(new_content, encoding=encoding)

        return ToolResult(
            ok=True,
            tool=tool_name,
            risk="medium",
            output={
                "path": str(path),
                "chars_written": len(content),
                "mode": mode,
                "file_exists_now": path.exists(),
            },
            artifacts=[str(path)],
            meta={"task_id": ctx.task_id, "thread_id": ctx.thread_id},
        )
    except Exception as exc:
        return ToolResult(ok=False, tool=tool_name, risk="medium", error=str(exc))


def _diff_text_file(ctx: ToolContext, args: dict[str, Any]) -> ToolResult:
    tool_name = "diff_text_file"
    try:
        path = _safe_path(str(args["path"]))
        new_content = str(args.get("new_content", ""))
        encoding = str(args.get("encoding", "utf-8"))

        old_content = ""
        if path.exists():
            old_content = path.read_text(encoding=encoding, errors="replace")

        diff_lines = list(
            difflib.unified_diff(
                old_content.splitlines(),
                new_content.splitlines(),
                fromfile=f"{path} (alt)",
                tofile=f"{path} (neu)",
                lineterm="",
            )
        )
        diff_text = "\n".join(diff_lines)

        return ToolResult(
            ok=True,
            tool=tool_name,
            risk="low",
            output={
                "path": str(path),
                "diff": diff_text,
                "changed": old_content != new_content,
            },
            artifacts=[str(path)],
            meta={"task_id": ctx.task_id, "thread_id": ctx.thread_id},
        )
    except Exception as exc:
        return ToolResult(ok=False, tool=tool_name, risk="low", error=str(exc))


def register_file_tools(reg: ToolRegistry | None = None) -> ToolRegistry:
    reg = reg or registry

    reg.register(
        ToolDefinition(
            name="read_text_file",
            description="Liest eine Textdatei innerhalb von /root/werkraum.",
            risk="low",
            input_schema={
                "type": "object",
                "required": ["path"],
                "properties": {
                    "path": {"type": "string"},
                    "encoding": {"type": "string"},
                    "max_chars": {"type": "integer"},
                },
            },
            handler=_read_text_file,
        ),
        overwrite=True,
    )

    reg.register(
        ToolDefinition(
            name="write_text_file",
            description="Schreibt Text in eine Datei innerhalb von /root/werkraum.",
            risk="medium",
            input_schema={
                "type": "object",
                "required": ["path", "content"],
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                    "encoding": {"type": "string"},
                    "mode": {"type": "string", "enum": ["overwrite", "append"]},
                },
            },
            handler=_write_text_file,
        ),
        overwrite=True,
    )

    reg.register(
        ToolDefinition(
            name="diff_text_file",
            description="Erzeugt einen Unified Diff zwischen Dateistand und neuem Inhalt.",
            risk="low",
            input_schema={
                "type": "object",
                "required": ["path", "new_content"],
                "properties": {
                    "path": {"type": "string"},
                    "new_content": {"type": "string"},
                    "encoding": {"type": "string"},
                },
            },
            handler=_diff_text_file,
        ),
        overwrite=True,
    )

    return reg
