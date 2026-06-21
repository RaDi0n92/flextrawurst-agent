#!/usr/bin/env python3
"""
Wesen-Testläufer — schickt Prompts aus test_prompts.md an ein Wesen
und loggt die Antworten in eine Markdown-Datei.

Verwendung:
  python3 run_test.py <spawner> <name> [host]
  python3 run_test.py solarius KrEaPPy
  python3 run_test.py solarius KrEaPPy localhost:8787
"""

import sys
import json
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

PROMPTS_FILE = Path(__file__).parent / "test_prompts.md"
HOST = "localhost:8787"

def chat(spawner, name, prompt, host):
    url = f"http://{host}/{spawner}/{urllib.parse.quote(name)}/chat"
    body = json.dumps({"messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(url, data=body,
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            full = ""
            buf = ""
            for chunk in iter(lambda: r.read(256), b""):
                buf += chunk.decode("utf-8", errors="replace")
                lines = buf.split("\n")
                buf = lines.pop()
                for line in lines:
                    if not line.startswith("data: "):
                        continue
                    d = line[6:].strip()
                    if d == "[DONE]":
                        break
                    try:
                        j = json.loads(d)
                        if j.get("token"):
                            full += j["token"]
                    except Exception:
                        pass
            return full.strip() or "[leere Antwort]"
    except Exception as e:
        return f"[FEHLER: {e}]"

def parse_prompts(path):
    """Gibt Liste von (kategorie, prompt) zurück."""
    items = []
    current_kat = "?"
    for line in path.read_text("utf-8").splitlines():
        if line.startswith("## "):
            current_kat = line[3:].strip()
        elif line.strip() and not line.startswith("#"):
            items.append((current_kat, line.strip()))
    return items

def main():
    import urllib.parse
    spawner = sys.argv[1] if len(sys.argv) > 1 else "solarius"
    name    = sys.argv[2] if len(sys.argv) > 2 else "KrEaPPy"
    host    = sys.argv[3] if len(sys.argv) > 3 else HOST

    prompts = parse_prompts(PROMPTS_FILE)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    outfile = Path(__file__).parent / f"testlog_{spawner}_{name}_{ts}.md"

    print(f"Teste {spawner}/{name} @ {host}")
    print(f"Prompts: {len(prompts)} | Log: {outfile.name}")
    print()

    lines = [f"# Testlauf {spawner}/{name} — {ts}\n"]
    last_kat = None

    for i, (kat, prompt) in enumerate(prompts, 1):
        if kat != last_kat:
            lines.append(f"\n## {kat}\n")
            last_kat = kat
        print(f"[{i}/{len(prompts)}] {prompt[:60]}…")
        antwort = chat(spawner, name, prompt, host)
        lines.append(f"**Prompt:** {prompt}\n")
        lines.append(f"**Antwort:** {antwort}\n")
        lines.append("---\n")
        print(f"  → {antwort[:80]}…\n" if len(antwort) > 80 else f"  → {antwort}\n")

    outfile.write_text("\n".join(lines), "utf-8")
    print(f"\nFertig. Log gespeichert: {outfile}")

if __name__ == "__main__":
    main()
