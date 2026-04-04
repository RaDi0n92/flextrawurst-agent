from pathlib import Path


MAX_ZEICHEN = 20000


def datei_lesen_serverweit(pfad: str) -> str:
    datei = Path(pfad)

    if not datei.exists():
        return f"nicht gefunden: {pfad}"

    if datei.is_dir():
        return f"ist ein ordner: {pfad}"

    try:
        text = datei.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"nicht als utf-8 lesbar: {pfad}"
    except Exception as fehler:
        return f"lesefehler bei {pfad}: {fehler}"

    if len(text) > MAX_ZEICHEN:
        return text[:MAX_ZEICHEN] + "\n\n... abgeschnitten ..."

    return text
