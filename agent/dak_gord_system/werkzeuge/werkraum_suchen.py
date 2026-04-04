import subprocess


def werkraum_suchen(muster: str) -> str:
    befehl = ["bash", "-lc", f"rg -n -- '{muster}' . || true"]
    return subprocess.check_output(befehl, text=True)
