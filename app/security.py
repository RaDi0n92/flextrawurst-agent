import os
import hmac
from fastapi import Header, HTTPException, status

def require_api_token(authorization: str | None = Header(default=None)) -> None:
    token = os.getenv("AGENT_API_TOKEN")
    # fail-closed: Ohne konfiguriertes Token wird der Dienst gesperrt, NICHT geoeffnet.
    # Verhindert unauth. Root-Datei-/Kommando-Zugriff, falls AGENT_API_TOKEN fehlt (C-001).
    if not token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gateway gesperrt: AGENT_API_TOKEN nicht gesetzt",
        )
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")
    # konstantzeitiger Vergleich gegen Timing-Angriffe
    if not hmac.compare_digest(authorization.removeprefix("Bearer ").strip(), token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API token")
