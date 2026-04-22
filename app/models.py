from pydantic import BaseModel, Field

class WriteFileRequest(BaseModel):
    path: str = Field(..., description="Relative file path within workspace")
    content: str = Field(..., description="New file contents")

class CommandRequest(BaseModel):
    cmd: str = Field(..., description="Shell command to execute")
    cwd: str = Field(default=".", description="Working directory relative to workspace")
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    max_output_chars: int = Field(default=20000, ge=1000, le=200000)

class GitCommitRequest(BaseModel):
    message: str = Field(..., min_length=3, max_length=300)
    cwd: str = Field(default=".", description="Git repo directory relative to workspace")
