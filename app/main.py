from fastapi import Depends, FastAPI, Query
from .models import CommandRequest, GitCommitRequest, WriteFileRequest
from .security import require_api_token
from .services import WORKSPACE_ROOT, git_commit, git_diff, git_status, list_directory, read_text_file, run_command, write_text_file

app = FastAPI(title="Flextrawurst Agent Gateway", version="0.2.0")

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/workspace")
def workspace_info(_: None = Depends(require_api_token)): return {"workspace_root": str(WORKSPACE_ROOT)}

@app.get("/files")
def files(path: str = Query(default="."), _: None = Depends(require_api_token)): return {"path": path, "entries": list_directory(path)}

@app.get("/read")
def read(path: str, _: None = Depends(require_api_token)): return {"path": path, "content": read_text_file(path)}

@app.post("/write")
def write(payload: WriteFileRequest, _: None = Depends(require_api_token)): return write_text_file(payload.path, payload.content)

@app.post("/run")
def run(payload: CommandRequest, _: None = Depends(require_api_token)): return run_command(payload.cmd, payload.cwd, payload.timeout_seconds, payload.max_output_chars)

@app.get("/git/status")
def git_status_endpoint(cwd: str = Query(default="."), max_output_chars: int = Query(default=20000, ge=1000, le=200000), _: None = Depends(require_api_token)):
    return git_status(cwd=cwd, max_output_chars=max_output_chars)

@app.get("/git/diff")
def git_diff_endpoint(cwd: str = Query(default="."), staged: bool = Query(default=False), max_output_chars: int = Query(default=20000, ge=1000, le=200000), _: None = Depends(require_api_token)):
    return git_diff(cwd=cwd, staged=staged, max_output_chars=max_output_chars)

@app.post("/git/commit")
def git_commit_endpoint(payload: GitCommitRequest, _: None = Depends(require_api_token)): return git_commit(cwd=payload.cwd, message=payload.message)
