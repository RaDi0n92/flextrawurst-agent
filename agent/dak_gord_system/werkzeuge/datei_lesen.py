from pathlib import Path


def datei_lesen(pfad: str) -> str:
    datei = Path(pfad)
    if not datei.exists():
        return ""
    return datei.read_text(encoding="utf-8")
