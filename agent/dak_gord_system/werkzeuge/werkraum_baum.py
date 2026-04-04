from pathlib import Path


def werkraum_baum(max_tiefe: int = 3) -> str:
    basis = Path(".").resolve()
    zeilen = []

    for pfad in sorted(basis.rglob("*")):
        rel = pfad.relative_to(basis)
        if ".venv" in rel.parts:
            continue
        if len(rel.parts) > max_tiefe:
            continue
        zeilen.append(str(rel))

    return "\n".join(zeilen)
