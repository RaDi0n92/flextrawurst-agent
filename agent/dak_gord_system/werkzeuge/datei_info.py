from pathlib import Path
from datetime import datetime


def datei_info(pfad: str) -> str:
    datei = Path(pfad)

    if not datei.exists():
        return f"nicht gefunden: {pfad}"

    info = datei.stat()
    geaendert = datetime.fromtimestamp(info.st_mtime).isoformat()
    art = "ordner" if datei.is_dir() else "datei"

    return (
        f"pfad: {datei}\n"
        f"art: {art}\n"
        f"groesse: {info.st_size}\n"
        f"geaendert: {geaendert}\n"
    )
