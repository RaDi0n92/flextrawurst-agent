from pathlib import Path


def notiz_speichern(pfad: str, text: str) -> None:
    datei = Path(pfad)
    datei.parent.mkdir(parents=True, exist_ok=True)
    with datei.open("a", encoding="utf-8") as ziel:
        ziel.write(text.rstrip() + "\n")
