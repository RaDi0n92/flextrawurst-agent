#!/usr/bin/env python3
"""
Befoerderungs-Scan -- eigene, angepasste Version des self-improving-agent-Musters
(Memory -> CLAUDE.md graduieren). Nutzt zwei bereits bestehende Konventionen
dieses Systems statt Fuzzy-Matching:

  1. [[link]]-Verweise zwischen Memory-Dateien -- ein Ziel, das von 2+ anderen
     Dateien referenziert wird, ist ein wiederkehrendes Muster.
  2. 'betrifft:'-Tags im Frontmatter von spiegel/notizen/ideen/karte -- ein Tag,
     der in 3+ verschiedenen Dateien auftaucht, ist ein wiederkehrendes Thema.

Beide Listen werden grob gegen den aktuellen CLAUDE.md-Text abgeglichen (simple
Wort-Ueberschneidung, keine KI-Bewertung) -- das Skript schlaegt nur Kandidaten
vor, entscheidet aber nichts. Beforderung selbst bleibt Handarbeit (Skalpell-
Prinzip: erst zeigen, dann gemeinsam entscheiden).

Usage:
  python3 befoerderungs_scan.py
"""
import re
from pathlib import Path
from collections import Counter, defaultdict

MEMORY_DIR = Path("/root/.claude/projects/-root/memory")
WERKRAUM_ORDNER = [
    Path("/root/werkraum/_claude/spiegel"),
    Path("/root/werkraum/_claude/notizen"),
    Path("/root/werkraum/_claude/ideen"),
    Path("/root/werkraum/_claude/karte"),
]
CLAUDE_MD_PFADE = [Path("/root/CLAUDE.md"), Path("/root/.claude/CLAUDE.md")]

LINK_MUSTER = re.compile(r"\[\[([a-zA-Z0-9_\-]+)\]\]")
FRONTMATTER_BETRIFFT = re.compile(r"^betrifft:\s*\[(.*?)\]", re.MULTILINE)


def lade_claude_md_text() -> str:
    text = ""
    for pfad in CLAUDE_MD_PFADE:
        if pfad.exists():
            text += pfad.read_text(encoding="utf-8", errors="replace") + "\n"
    return text.lower()


def vermutlich_schon_drin(schluesselwoerter: list[str], claude_md_text: str) -> bool:
    treffer = [w for w in schluesselwoerter if len(w) > 4 and w.lower() in claude_md_text]
    return len(treffer) >= max(1, len(schluesselwoerter) // 2)


def scan_memory_links(min_referenzen: int = 2):
    referenzen = Counter()
    fundorte = defaultdict(list)
    if not MEMORY_DIR.exists():
        return []
    for datei in MEMORY_DIR.glob("*.md"):
        if datei.name == "MEMORY.md":
            continue
        text = datei.read_text(encoding="utf-8", errors="replace")
        for ziel in LINK_MUSTER.findall(text):
            referenzen[ziel] += 1
            fundorte[ziel].append(datei.stem)

    claude_md_text = lade_claude_md_text()
    kandidaten = []
    for name, anzahl in referenzen.most_common():
        if anzahl < min_referenzen:
            continue
        schluesselwoerter = name.replace("_", " ").replace("-", " ").split()
        kandidaten.append({
            "name": name,
            "referenzen": anzahl,
            "gefunden_in": fundorte[name],
            "schon_in_claude_md": vermutlich_schon_drin(schluesselwoerter, claude_md_text),
        })
    return kandidaten


def scan_betrifft_tags(min_dateien: int = 3):
    tag_dateien = defaultdict(set)
    for ordner in WERKRAUM_ORDNER:
        if not ordner.exists():
            continue
        for datei in ordner.rglob("*.md"):
            try:
                kopf = datei.read_text(encoding="utf-8", errors="replace")[:600]
            except Exception:
                continue
            treffer = FRONTMATTER_BETRIFFT.search(kopf)
            if not treffer:
                continue
            tags = [t.strip() for t in treffer.group(1).split(",") if t.strip()]
            for tag in tags:
                tag_dateien[tag].add(str(datei.relative_to(datei.parents[3])))

    claude_md_text = lade_claude_md_text()
    kandidaten = []
    for tag, dateien in sorted(tag_dateien.items(), key=lambda kv: -len(kv[1])):
        if len(dateien) < min_dateien:
            continue
        kandidaten.append({
            "tag": tag,
            "anzahl_dateien": len(dateien),
            "dateien": sorted(dateien),
            "schon_in_claude_md": vermutlich_schon_drin([tag], claude_md_text),
        })
    return kandidaten


def main():
    print("=== Beforderungs-Kandidaten aus Memory ([[links]] mit 2+ Referenzen) ===")
    memory_kandidaten = scan_memory_links()
    if not memory_kandidaten:
        print("Keine gefunden.")
    for k in memory_kandidaten:
        status = "(vermutlich schon in CLAUDE.md)" if k["schon_in_claude_md"] else "NEU -- noch nicht in CLAUDE.md"
        print(f"\n{k['name']}  — {k['referenzen']}x referenziert  {status}")
        print(f"    referenziert von: {', '.join(k['gefunden_in'])}")

    print("\n\n=== Beforderungs-Kandidaten aus werkraum-Tags (3+ Dateien mit demselben Thema) ===")
    tag_kandidaten = scan_betrifft_tags()
    if not tag_kandidaten:
        print("Keine gefunden.")
    for k in tag_kandidaten[:15]:
        status = "(vermutlich schon in CLAUDE.md)" if k["schon_in_claude_md"] else "NEU -- noch nicht in CLAUDE.md"
        print(f"\n'{k['tag']}'  — in {k['anzahl_dateien']} Dateien  {status}")


if __name__ == "__main__":
    main()
