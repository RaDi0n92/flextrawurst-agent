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


def dateiname_suchen(muster: str, start: str = "/", max_treffer: int = 200) -> str:
    muster = muster.lower().strip()
    wurzel = Path(start).resolve()
    treffer = []

    for pfad in wurzel.rglob("*"):
        if _ignorieren(pfad):
            continue

        if muster in pfad.name.lower():
            treffer.append(str(pfad))

        if len(treffer) >= max_treffer:
            treffer.append("... abgeschnitten ...")
            break

    return "\n".join(treffer)
