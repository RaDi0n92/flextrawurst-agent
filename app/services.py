import os, shlex, subprocess
from pathlib import Path
from fastapi import HTTPException, status

WORKSPACE_ROOT = Path(os.getenv("WORKSPACE_ROOT", ".")).resolve()
ALLOWED_COMMAND_PREFIXES = tuple(
    p.strip() for p in os.getenv("AGENT_ALLOWED_COMMAND_PREFIXES", "").split(",") if p.strip()
)

def resolve_safe_path(relative_path: str) -> Path:
    target = (WORKSPACE_ROOT / relative_path).resolve()
    if not str(target).startswith(str(WORKSPACE_ROOT)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Path escapes workspace root")
    return target

def _truncate_output(value: str, max_chars: int) -> str:
    return value if len(value) <= max_chars else value[:max_chars] + "\n...[truncated]"

def _run_subprocess(argv: list[str], cwd_path: Path, timeout_seconds: int):
    return subprocess.run(argv, cwd=str(cwd_path), text=True, capture_output=True, timeout=timeout_seconds, shell=False)

def list_directory(path: str) -> list[str]:
    p = resolve_safe_path(path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Path not found")
    if not p.is_dir():
        raise HTTPException(status_code=400, detail="Path is not a directory")
    return sorted(x.name for x in p.iterdir())

def read_text_file(path: str) -> str:
    p = resolve_safe_path(path)
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return p.read_text(encoding="utf-8")

def write_text_file(path: str, content: str):
    p = resolve_safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return {"path": str(p.relative_to(WORKSPACE_ROOT)), "bytes_written": len(content.encode("utf-8"))}

def run_command(cmd: str, cwd: str, timeout_seconds: int, max_output_chars: int):
    if not cmd.strip():
        raise HTTPException(status_code=400, detail="Command cannot be empty")
    if ALLOWED_COMMAND_PREFIXES and not any(cmd.startswith(prefix) for prefix in ALLOWED_COMMAND_PREFIXES):
        raise HTTPException(status_code=403, detail="Command prefix is not allowed")

    cwd_path = resolve_safe_path(cwd)
    if not cwd_path.exists() or not cwd_path.is_dir():
        raise HTTPException(status_code=400, detail="Invalid cwd")

    try:
        cp = _run_subprocess(shlex.split(cmd), cwd_path, timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        return {
            "cmd": cmd, "cwd": str(cwd_path.relative_to(WORKSPACE_ROOT)), "exit_code": 124,
            "stdout": _truncate_output(exc.stdout or "", max_output_chars),
            "stderr": _truncate_output((exc.stderr or "") + "\nCommand timed out", max_output_chars),
        }

    return {
        "cmd": cmd, "cwd": str(cwd_path.relative_to(WORKSPACE_ROOT)), "exit_code": cp.returncode,
        "stdout": _truncate_output(cp.stdout, max_output_chars),
        "stderr": _truncate_output(cp.stderr, max_output_chars),
    }

def _ensure_git_repo(cwd_path: Path):
    if not (cwd_path / ".git").exists():
        raise HTTPException(status_code=400, detail="cwd is not a git repository")

def git_status(cwd: str, max_output_chars: int = 20000):
    cwd_path = resolve_safe_path(cwd); _ensure_git_repo(cwd_path)
    cp = _run_subprocess(["git","status","--short","--branch"], cwd_path, 20)
    return {"cwd": str(cwd_path.relative_to(WORKSPACE_ROOT)), "exit_code": cp.returncode,
            "stdout": _truncate_output(cp.stdout, max_output_chars),
            "stderr": _truncate_output(cp.stderr, max_output_chars)}

def git_diff(cwd: str, staged: bool, max_output_chars: int = 20000):
    cwd_path = resolve_safe_path(cwd); _ensure_git_repo(cwd_path)
    args = ["git","diff"] + (["--staged"] if staged else [])
    cp = _run_subprocess(args, cwd_path, 20)
    return {"cwd": str(cwd_path.relative_to(WORKSPACE_ROOT)), "staged": staged, "exit_code": cp.returncode,
            "stdout": _truncate_output(cp.stdout, max_output_chars),
            "stderr": _truncate_output(cp.stderr, max_output_chars)}

def git_commit(cwd: str, message: str, max_output_chars: int = 20000):
    cwd_path = resolve_safe_path(cwd); _ensure_git_repo(cwd_path)
    cp = _run_subprocess(["git","commit","-m",message], cwd_path, 30)
    return {"cwd": str(cwd_path.relative_to(WORKSPACE_ROOT)), "message": message, "exit_code": cp.returncode,
            "stdout": _truncate_output(cp.stdout, max_output_chars),
            "stderr": _truncate_output(cp.stderr, max_output_chars)}
