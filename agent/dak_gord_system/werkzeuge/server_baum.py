from pathlib import Path


IGNORIERTE_ORDNER = {
    "/proc",
    "/sys",
    "/dev",
    "/run",
    "/tmp",
    "/mnt",
    "/media",
}


def _ignorieren(pfad: Path) -> bool:
    text = str(pfad)
    return any(text == basis or text.startswith(basis + "/") for basis in IGNORIERTE_ORDNER)


def server_baum(start: str = "/", max_tiefe: int = 4, max_eintraege: int = 5000) -> str:
    wurzel = Path(start).resolve()
    zeilen = []
    anzahl = 0

    for pfad in sorted(wurzel.rglob("*")):
        if _ignorieren(pfad):
            continue

        try:
            rel = pfad.relative_to(wurzel)
        except ValueError:
            rel = pfad

        tiefe = len(rel.parts)
        if tiefe > max_tiefe:
            continue

        zeilen.append(str(pfad))
        anzahl += 1

        if anzahl >= max_eintraege:
            zeilen.append("... abgeschnitten ...")
            break

    return "\n".join(zeilen)
