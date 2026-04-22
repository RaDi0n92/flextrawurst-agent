import os
from fastapi import Header, HTTPException, status

def require_api_token(authorization: str | None = Header(default=None)) -> None:
    token = os.getenv("AGENT_API_TOKEN")
    if not token:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")
    if authorization.removeprefix("Bearer ").strip() != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API token")
