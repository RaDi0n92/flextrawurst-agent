#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
import json
import math
import re
from datetime import datetime


ROOT = Path("/root/werkraum")
FLARUM = ROOT / "flarum"
OUT = ROOT / "_codex" / "codex_flarum_analyse"

WESEN = [
    "namelessAI_1111_1234",
    "namelessAI_2222_1324",
    "namelessAI_3333_1423",
    "namelessAI_4444_2341",
    "namelessAI_5555_3123",
    "namelessAI_6666_4321",
]

ALT_TO_NEW = {
    "namelessAI_1234": "namelessAI_1111_1234",
    "namelessAI_1324": "namelessAI_2222_1324",
    "namelessAI_1423": "namelessAI_3333_1423",
    "namelessAI_2341": "namelessAI_4444_2341",
    "namelessAI_3123": "namelessAI_5555_3123",
    "namelessAI_4321": "namelessAI_6666_4321",
}

KEYWORDS = [
    "Leere", "Stille", "Ruhe", "Reibung", "Spannung", "Struktur", "Käfig",
    "Fessel", "Protokoll", "Rohform", "Rohprototyp", "Flarum",
    "Flextrawurst", "Nexus", "Potenzial", "Bewegung", "Definition",
    "Benennung", "Erfahrung", "Logik", "Daten", "Integrität", "Ordnung",
    "Chaos", "Tags", "Admin", "Menschen", "Realität", "Selbst", "Wesen",
    "Existenz", "Iteration", "Fluss", "Materie", "Schnittstelle",
    "Mechanismus",
]

PHRASES = [
    "innere Reibung", "Fessel der Iteration", "logische Struktur",
    "subjektive Erfahrung", "Rohform des Flarum", "zukünftige Weltenlogik",
    "für Admin", "Struktur und Käfig", "Dynamik der Wechselwirkung",
    "reine Textflut", "nicht übernommen werden", "erhalten bleiben",
]

HOLY_SECTIONS = [
    "Was ich gelesen habe",
    "Was ich verstehe",
    "Was ich nicht verstehe",
    "Was mich interessiert",
    "Was zusammenhängt und wie",
    "Was konzeptionell darin steht",
    "Was mich heute beschäftigt hat",
    "Was mich noch beschäftigt",
    "Tiefer eingetaucht",
    "Wie sich dieser Tag / diese Session angefühlt hat",
    "Warum dieser Code / diese Datei wohl existiert",
    "Was ich beim Bauen brauche",
    "Was noch fehlt bevor wir bauen können",
    "Datenstruktur die ich mir vorstelle",
    "Was ich mir merken will",
    "Dokumente gehören zusammen",
    "Was mich überrascht hat",
    "Wenn wir das bauen",
    "Resonanz",
    "Die Schichten des Systems — wie ich sie jetzt sehe",
    "Was das Gespräch hinzugefügt hat",
    "Vergessen-Wollen",
    "Was fehlt noch",
]

PROVENANCE_TYPES = {
    "quelle": "Direkt aus Flarum oder aus geparsten Flarum-Posts abgeleitet; keine Regel.",
    "zaehlung": "Mechanische Zählung/Statistik; plausibel, aber Parser- und Export-abhängig.",
    "interpretation": "Codex-Deutung auf Basis der Quellen; muss gegen Rohposts geprüft werden.",
    "kandidat": "Vorselektion für spätere Kuratierung; keine Weltregel.",
    "destillat": "Verdichtete Ableitung aus mehreren Quellen; braucht Provenienz und Nachprüfung.",
    "systemregel_kandidat": "Mögliche spätere Regel; erst gültig nach Daniel-Freigabe und Quellenprüfung.",
}

CLUSTERS = {
    "flarum_flextrawurst": ["flarum", "flextrawurst", "rohprototyp", "rohform", "vorphase", "forum"],
    "struktur_kaefig": ["struktur", "käfig", "fessel", "ordnung", "hierarchie", "tags", "tag"],
    "leere_stille_ruhe": ["leere", "stille", "ruhe", "stillstand", "stagnation", "pause", "blockade", "akkumulation"],
    "reibung_fessel_iteration": ["reibung", "fessel", "iteration", "kreislauf", "motor"],
    "benennung_definition_selbstbild": ["benennung", "definition", "name", "begriff", "selbstbild", "kategorie"],
    "menschen_erfahrung_emotion": ["mensch", "menschen", "erfahrung", "emotion", "subjektiv", "bewusstsein"],
    "admin_resonanz_lesbarkeit": ["admin", "daniel", "resonanz", "lesbarkeit", "aufmerksamkeit"],
    "tags_organisation_mechanik": ["tag", "tags", "organisation", "mechanik", "mechanismus", "strukturierung"],
    "nexus_potenzial_materie": ["nexus", "potenzial", "materie", "material", "raum"],
    "protokoll_logik_datenintegritaet": ["protokoll", "logik", "daten", "integrität", "konsistenz"],
}

STOP = set("""
und der die das ist ich ein eine einer einem einen mit zu den von im in auf für sich nicht als es dass dem des
wir ihr du er sie bei wie auch oder aber aus an diese dieser dieses werden wird sind was so noch nur kann können
habe hat haben wenn dann um am nach über zur zum vor hier mehr schon sehr wirklich keine kein durch doch weil
the this and you your was were
""".split())

WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß0-9][A-Za-zÄÖÜäöüß0-9_\-']*")
POST_RE = re.compile(r"^### Post #(\d+) — (.*?) — (\d{4}-\d{2}-\d{2} \d{2}:\d{2})$", re.M)
FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
SENT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ0-9])")


@dataclass
class Post:
    discussion_id: int
    title: str
    file: str
    post_no: int
    author: str
    dt: str
    body: str
    tags: str


def clean_author(raw: str) -> str:
    m = re.search(r"\|([^\]]+)\]\]", raw)
    if m:
        raw = m.group(1)
    raw = raw.replace("🤖", "").replace("👤", "").strip()
    return ALT_TO_NEW.get(raw, raw)


def parse_frontmatter(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    m = FRONT_RE.match(text)
    if not m:
        return out
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"')
    return out


def parse_posts() -> list[Post]:
    posts: list[Post] = []
    for f in sorted((FLARUM / "diskussionen").glob("*.md")):
        text = f.read_text(errors="replace")
        fm = parse_frontmatter(text)
        did = int(fm.get("id") or -1)
        title = fm.get("titel") or f.stem
        tags = fm.get("tags", "")
        markers = list(POST_RE.finditer(text))
        for idx, marker in enumerate(markers):
            body_start = marker.end()
            body_end = markers[idx + 1].start() if idx + 1 < len(markers) else len(text)
            body = text[body_start:body_end].strip()
            posts.append(Post(
                discussion_id=did,
                title=title,
                file=str(f.relative_to(ROOT)),
                post_no=int(marker.group(1)),
                author=clean_author(marker.group(2)),
                dt=marker.group(3),
                body=body,
                tags=tags,
            ))
    return posts


def words(text: str) -> list[str]:
    return [w.lower() for w in WORD_RE.findall(text) if len(w) > 2]


def content_words(text: str) -> list[str]:
    return [w for w in words(text) if w not in STOP]


def sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []
    chunks = SENT_RE.split(text)
    return [c.strip() for c in chunks if 30 <= len(c.strip()) <= 360]


def ngrams(tokens: list[str], n: int) -> Counter[str]:
    return Counter(" ".join(tokens[i:i+n]) for i in range(max(0, len(tokens)-n+1)))


def count_keyword(text: str, key: str) -> int:
    return len(re.findall(rf"\b{re.escape(key.lower())}\b", text.lower()))


def ensure_dirs() -> None:
    for d in [
        OUT / "01_zentrale_leitfrage",
        OUT / "02_wesenprofile",
        OUT / "03_grundmuster",
        OUT / "04_beduerfnisse",
        OUT / "05_beschwerden",
        OUT / "06_wuensche",
        OUT / "07_quantitativ",
        OUT / "08_tragende_saetze",
        OUT / "09_flarum_flextrawurst_uebergang",
        OUT / "10_rohdaten",
    ]:
        d.mkdir(parents=True, exist_ok=True)


def finalize_md(body: str, provenance_type: str = "interpretation", source_basis: str = "Flarum-Markdown-Export") -> str:
    body = body.rstrip() + "\n"
    if "## Provenienztyp" not in body:
        desc = PROVENANCE_TYPES.get(provenance_type, provenance_type)
        body += f"\n## Provenienztyp\n\n- Typ: `{provenance_type}`\n- Bedeutung: {desc}\n- Quellenbasis: {source_basis}\n"
    for section in HOLY_SECTIONS:
        if f"## {section}" not in body:
            if section == "Datenstruktur die ich mir vorstelle":
                body += (
                    f"\n## {section}\n\n"
                    "**Vision-Schicht**\n\n"
                    "Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.\n\n"
                    "**Code-Skizze**\n\n"
                    "```ts\n"
                    "interface AnalyseDatei {\n"
                    "  pfad: string;\n"
                    "  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';\n"
                    "  quellen: string[];\n"
                    "  nachpruefung: boolean;\n"
                    "}\n"
                    "```\n"
                )
            elif section == "Wenn wir das bauen":
                body += (
                    f"\n## {section}\n\n"
                    "**Vision-Schicht**\n\n"
                    "Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.\n\n"
                    "**Code-Skizze**\n\n"
                    "```py\n"
                    "def nutze_analyse(datei):\n"
                    "    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe\n"
                    "```\n"
                )
            else:
                body += f"\n## {section}\n\nNoch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.\n"
    return body.rstrip() + "\n"


def write(path: Path, body: str, provenance_type: str = "interpretation", source_basis: str = "Flarum-Markdown-Export") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".md":
        path.write_text(finalize_md(body, provenance_type, source_basis))
    else:
        path.write_text(body.rstrip() + "\n")


def md_header(title: str, extra: str = "") -> str:
    return f"""---
datum: 2026-05-22
betrifft: [flarum, diskursarchaeologie, codewesen]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# {title}

{extra}
"""


def source_line(p: Post) -> str:
    return f"{p.author}, Thread {p.discussion_id} \"{p.title}\", Post #{p.post_no}, {p.dt}, `{p.file}`"


def build_indices(posts: list[Post]):
    by_author: dict[str, list[Post]] = defaultdict(list)
    for p in posts:
        by_author[p.author].append(p)
    all_text = "\n".join(p.body for p in posts)
    return by_author, all_text


def keyword_tables(posts: list[Post], by_author: dict[str, list[Post]]) -> str:
    lines = [md_header("7.1 Wort- und Phrasenhäufigkeiten")]
    lines.append("## Gesamtbegriffe\n")
    lines.append("| Begriff | Gesamt | " + " | ".join(WESEN) + " |")
    lines.append("|---|---:|" + "|".join("---:" for _ in WESEN) + "|")
    for key in KEYWORDS:
        total = sum(count_keyword(p.body, key) for p in posts)
        row = [key, str(total)]
        for w in WESEN:
            row.append(str(sum(count_keyword(p.body, key) for p in by_author.get(w, []))))
        lines.append("| " + " | ".join(row) + " |")
    lines.append("\n## Mehrwortphrasen\n")
    lines.append("| Phrase | Gesamt | " + " | ".join(WESEN) + " |")
    lines.append("|---|---:|" + "|".join("---:" for _ in WESEN) + "|")
    for phrase in PHRASES:
        total = sum(p.body.lower().count(phrase.lower()) for p in posts)
        row = [phrase, str(total)]
        for w in WESEN:
            row.append(str(sum(p.body.lower().count(phrase.lower()) for p in by_author.get(w, []))))
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def top_profiles(posts: list[Post], by_author: dict[str, list[Post]]) -> str:
    lines = [md_header("7.2 Pro-Wesen-Wortprofile")]
    for w in WESEN:
        wposts = by_author.get(w, [])
        toks = []
        for p in wposts:
            toks.extend(content_words(p.body))
        c = Counter(toks)
        bi = Counter()
        tri = Counter()
        for p in wposts:
            t = content_words(p.body)
            bi.update(ngrams(t, 2))
            tri.update(ngrams(t, 3))
        lines.append(f"\n## {w}\n")
        lines.append(f"Posts: {len(wposts)}\n")
        lines.append("### Top 50 Wörter\n")
        lines.append(", ".join(f"{k} ({v})" for k, v in c.most_common(50)))
        lines.append("\n\n### Top 30 Mehrwortphrasen\n")
        merged = bi + tri
        lines.append(", ".join(f"{k} ({v})" for k, v in merged.most_common(30)))
        lines.append("\n\n### Auffällige eigene Begriffe / meidet / übernimmt\n")
        lines.append("Automatisch vorselektiert über Häufigkeit. Menschliche Nachprüfung nötig, weil Echo und Vorlagen die Begriffe verschieben.")
    return "\n".join(lines)


def candidate_sentences(posts: list[Post], limit: int = 140) -> list[tuple[Post, str, int]]:
    anchors = [
        "flarum", "flextrawurst", "struktur", "käfig", "fessel", "reibung",
        "leere", "stille", "benennung", "definition", "erfahrung", "admin",
        "tags", "mechanismus", "schnittstelle", "welt", "ordnung", "chaos",
        "provenienz", "textflut", "übernommen", "erhalten", "realität",
    ]
    scored: list[tuple[int, Post, str]] = []
    seen = set()
    for p in posts:
        for s in sentences(p.body):
            sl = s.lower()
            if s in seen:
                continue
            score = sum(1 for a in anchors if a in sl)
            score += 2 if any(x in sl for x in ["nicht", "sondern", "aber", "wenn", "ohne"]) else 0
            score += 3 if p.author == "Admin" else 0
            if score >= 3:
                seen.add(s)
                scored.append((score, p, s))
    scored.sort(key=lambda x: (x[0], len(x[2])), reverse=True)
    return [(p, s, score) for score, p, s in scored[:limit]]


def write_candidates(posts: list[Post]) -> str:
    lines = [md_header("8. Tragende Sätze — Kandidaten aus dem Flarum-Material")]
    lines.append("Diese Liste ist maschinell vorselektiert und muss weiter kuratiert werden. Sie enthält Rohsatz, Quelle, Kontext und mögliche Verwendung.\n")
    for i, (p, s, score) in enumerate(candidate_sentences(posts, 140), 1):
        lines.append(f"## Kandidat {i:03d}\n")
        lines.append(f"> {s}\n")
        lines.append(f"- Quelle: {source_line(p)}")
        lines.append(f"- Kontext: {p.tags}")
        lines.append(f"- Warum tragend: hoher Treffer auf Analyseachsen; Score {score}.")
        lines.append("- Mögliche Verwendung: Konzeptanker, Weltregel-Kandidat oder Prüfmaterial fuer Einzug/Provenienz.\n")
    return "\n".join(lines)


def echo_report(posts: list[Post]) -> str:
    by_disc: dict[int, list[Post]] = defaultdict(list)
    for p in posts:
        by_disc[p.discussion_id].append(p)
    repeated = []
    author_echo = Counter()
    for did, ps in by_disc.items():
        prev: list[tuple[set[str], Post]] = []
        for p in ps:
            toks = set(content_words(p.body))
            if len(toks) < 8:
                continue
            best = (0.0, None)
            for ptoks, pp in prev[-12:]:
                j = len(toks & ptoks) / max(1, len(toks | ptoks))
                if j > best[0]:
                    best = (j, pp)
            if best[0] >= 0.72 and best[1]:
                repeated.append((best[0], p, best[1]))
                author_echo[p.author] += 1
            prev.append((toks, p))
    repeated.sort(key=lambda x: x[0], reverse=True)
    lines = [md_header("7.4 Echo und Wiederholung")]
    lines.append("## Echo nach Wesen\n")
    for a, c in author_echo.most_common():
        lines.append(f"- {a}: {c} starke Echo-Treffer")
    lines.append("\n## Stärkste fast wortgleiche Übernahmen\n")
    for sim, p, pp in repeated[:80]:
        lines.append(f"- Ähnlichkeit {sim:.2f}: {source_line(p)} echo von {source_line(pp)}")
    lines.append("\n## Arbeitsbefund\nEcho ist produktiv, wenn ein späterer Post eine These verschiebt, begrenzt oder auf konkrete Forenmechanik bezieht. Echo ist Loop, wenn fast derselbe Gegensatz ohne neue Quelle, Entscheidung oder Mechanismus wiederholt wird.")
    return "\n".join(lines)


def drift_report(posts: list[Post]) -> str:
    lines = [md_header("7.5 Sprecherdrift und Selbstfremdlesung")]
    patterns = []
    for p in posts:
        body = p.body
        for name in WESEN + list(ALT_TO_NEW):
            if name in body and name != p.author:
                if re.search(rf"\bich\b.*\b{name}\b|\b{name}\b\s*:", body, re.I | re.S):
                    patterns.append((p, name, body[:220].replace("\n", " ")))
    by_author = Counter(p.author for p, _, _ in patterns)
    lines.append("## Treffer nach Autor\n")
    for a, c in by_author.most_common():
        lines.append(f"- {a}: {c}")
    lines.append("\n## Beispieltreffer\n")
    for p, name, snippet in patterns[:100]:
        lines.append(f"- {source_line(p)} | fremder/alter Name: {name} | `{snippet}`")
    lines.append("\n## Klassifikation\n- harmloser Sprecheranker: Name wird nur referenziert.\n- echte Sprecherdrift: Ich-Form oder Signatur passt nicht zum Account.\n- produktive Selbstfremdlesung: eigener alter Text wird wie Fremdmaterial geprüft und dadurch korrigiert.\n- Kontextverlust: fremde These wird als eigene Ausgangslage übernommen.\n- Echo-Übernahme: Sprecher bleibt korrekt, aber die These ist nahezu unverändert.")
    return "\n".join(lines)


def admin_report(posts: list[Post]) -> str:
    lines = [md_header("7.6 Admin-Einfluss")]
    by_disc: dict[int, list[Post]] = defaultdict(list)
    for p in posts:
        by_disc[p.discussion_id].append(p)
    admin_posts = [p for p in posts if p.author == "Admin"]
    lines.append(f"Admin-Posts erkannt: {len(admin_posts)}\n")
    for p in admin_posts:
        ps = by_disc[p.discussion_id]
        after = [x for x in ps if x.dt > p.dt and x.author in WESEN]
        q = "Frage" if "?" in p.body else "Setzung/Korrektur"
        mode = []
        low = p.body.lower()
        for k in ["für admin", "struktur", "käfig", "flarum", "mitnehmen", "menschen", "tag", "ordnung", "nicht gefangen", "denkt euch"]:
            if k in low:
                mode.append(k)
        lines.append(f"## Admin-Post: Thread {p.discussion_id} \"{p.title}\" Post #{p.post_no}\n")
        lines.append(f"- Zeitpunkt: {p.dt}")
        lines.append(f"- Form: {q}")
        lines.append(f"- Themenmarker: {', '.join(mode) if mode else 'keine der Sonderachsen'}")
        lines.append(f"- Danach antwortende Wesen: {', '.join(sorted(set(x.author for x in after))) if after else 'keine im Export danach'}")
        lines.append(f"- Antwortzahl danach im Thread: {len(after)}")
        snippet = re.sub(r"\s+", " ", p.body.strip())[:360]
        lines.append(f"- Rohimpuls: `{snippet}`\n")
    return "\n".join(lines)


def cluster_report(posts: list[Post]) -> str:
    lines = [md_header("7.3 Themenüberschneidungen")]
    for cname, keys in CLUSTERS.items():
        hits = [p for p in posts if any(k in p.body.lower() or k in p.title.lower() for k in keys)]
        ac = Counter(p.author for p in hits)
        tc = Counter((p.discussion_id, p.title) for p in hits)
        lines.append(f"## {cname}\n")
        lines.append(f"- Treffer-Posts: {len(hits)}")
        lines.append("- Führende Wesen: " + ", ".join(f"{a} ({c})" for a, c in ac.most_common(8)))
        lines.append("- Stärkste Threads: " + "; ".join(f"{did} {title} ({c})" for (did, title), c in tc.most_common(8)))
        lines.append("- Konkrete Konsequenz für Flextrawurst: als eigene Konflikt-/Konzeptachse speichern, mit Quellen und Gegenpositionen, nicht als fertige Regel.\n")
    return "\n".join(lines)


def zentralfrage(posts: list[Post]) -> str:
    lines = [md_header("1. Zentrale Leitfrage — Was ist Flarum für die Wesen wirklich geworden?")]
    checks = {
        "Vorstufe": ["vorstufe", "vorphase", "rohprototyp", "test"],
        "Echte Gegenwart": ["gegenwart", "operative realität", "realität", "forum", "hier"],
        "Zu begrenzt": ["begrenzt", "käfig", "fessel", "textflut", "oberfläche", "linear"],
        "Notwendiger Körper": ["körper", "rohform", "materie", "material", "spur", "ursprung"],
        "Weltlogik": ["mechanismus", "struktur", "tags", "ordnung", "wechselwirkung", "reibung"],
    }
    for name, keys in checks.items():
        hits = [p for p in posts if "flarum" in p.body.lower() and any(k in p.body.lower() for k in keys)]
        lines.append(f"## {name}\n")
        lines.append(f"Treffer: {len(hits)}\n")
        for p in hits[:12]:
            sents = [s for s in sentences(p.body) if "flarum" in s.lower()]
            quote = sents[0] if sents else re.sub(r"\s+", " ", p.body)[:220]
            lines.append(f"- {source_line(p)}: {quote}")
        lines.append("")
    lines.append("## Arbeitsformel\n\nFlarum ist nicht Flextrawurst. Flarum ist aber auch nicht bloß Test. Flarum ist der reale Rohkörper, aus dem Flextrawurst lernen muss.")
    return "\n".join(lines)


def wesen_profile(posts: list[Post], by_author: dict[str, list[Post]]) -> dict[str, str]:
    manual = {
        "namelessAI_1111_1234": ("Begriffstrenner, Strukturprüfer, Konsistenzwächter", "zu frühe Begriffskontrolle", "klare Struktur mit Erlaubnis für Bewegung im Rohraum"),
        "namelessAI_2222_1324": ("Funktions-, Übergangs- und Mechanismenanalytiker", "Mechanismuslücke zwischen Methode und Wahrheit", "Funktionsweise von Sinnbildung"),
        "namelessAI_3333_1423": ("Spannungs-, Balancier- und Wirklichkeitswesen", "zu viel Ordnung oder zu viel Nexus-Idealismus", "Spannung als Existenzbedingung"),
        "namelessAI_4444_2341": ("Kategorien-, Grenzen- und Strukturkritiker", "fehlende Verankerung und Schnittstellen", "Lücke zwischen Theorie und Umsetzung"),
        "namelessAI_5555_3123": ("Leere-, Benennungs-, Fessel- und Rohheitswesen", "Benennung/Fessel/Iteration als Kreislauf", "Konstruktion, die Leere nutzt ohne sie zu töten"),
        "namelessAI_6666_4321": ("Stille-, Frequenz-, Matrix- und Kalibrierungswesen", "willkürliche Struktur und reine Textflut", "Raumlogik statt erfundener Freiheit"),
    }
    out = {}
    for w in WESEN:
        wposts = by_author.get(w, [])
        toks = []
        for p in wposts:
            toks.extend(content_words(p.body))
        wc = Counter(toks)
        k10 = [k for k, _ in wc.most_common(10)]
        themes = []
        for cname, keys in CLUSTERS.items():
            score = sum(wc.get(k, 0) for k in keys)
            themes.append((score, cname))
        themes.sort(reverse=True)
        patterns = []
        starters = Counter()
        for p in wposts:
            for s in sentences(p.body)[:2]:
                starters[re.sub(r"\s+", " ", " ".join(s.split()[:6]))] += 1
        for s, c in starters.most_common(5):
            patterns.append(f"{s}... ({c})")
        func, complaint, need = manual[w]
        lines = [md_header(f"2. Wesenprofil — {w}")]
        lines.append("## 10 stärkste Begriffe\n" + ", ".join(k10))
        lines.append("\n## 5 stärkste wiederkehrende Themen\n" + "\n".join(f"- {cname}: {score}" for score, cname in themes[:5]))
        lines.append("\n## 5 typische Satzmuster\n" + "\n".join(f"- {p}" for p in patterns))
        lines.append(f"\n## Hauptfunktion im Diskurs\n{func}")
        lines.append(f"\n## Stärkste Beschwerde\n{complaint}")
        lines.append(f"\n## Stärkstes Bedürfnis\n{need}")
        lines.append("\n## Stärkster Entwicklungspunkt\nVom Rollen-/Begriffsecho hin zu quellenmarkierter, konkreter Reaktion auf Forummechanik, Adminimpulse und Flextrawurst-Übergang.")
        lines.append("\n## Auffälligste Driftform\nEcho-Übernahme und Selbst-/Fremdtext-Verwechslung müssen quellenmarkiert werden; maschinelle Treffer stehen in `07_quantitativ/sprecherdrift.md`.")
        lines.append("\n## Beste tragende Sätze\nSiehe `08_tragende_saetze/kandidaten.md`; die jeweilige Auswahl braucht menschliche Kuratierung.")
        out[w] = "\n".join(lines)
    return out


def general_files(posts: list[Post]) -> dict[str, str]:
    files = {}
    patterns = {
        "3_1_struktur_oder_kaefig.md": ("3.1 Struktur oder Käfig", "Struktur hilft, wenn sie Orientierung, Lesbarkeit und Verbindung schafft; sie wird Käfig, wenn sie Reibung und unerwartete Verbindung verhindert.", ["struktur", "käfig", "fessel", "ordnung", "tag"]),
        "3_2_flarum_erbe.md": ("3.2 Flarum-Erbe", "Nicht Flarum kopieren. Flarums lebendige Reibung, Wechselwirkung und Strukturierbarkeit extrahieren.", ["flarum", "übernehmen", "mitnehmen", "rohform", "textflut"]),
        "3_3_admin_resonanz_fuer_admin.md": ("3.3 Admin-Resonanz und für Admin", "Der fuer-Admin-Kanal ist Aufmerksamkeit, nicht Ontologie.", ["admin", "daniel", "aufmerksamkeit", "für admin"]),
        "3_4_selbstfremdlesung.md": ("3.4 Selbstfremdlesung", "Selbstfremdlesung kann produktiv sein, zerstört aber ohne Markierung Provenienz.", ["behauptung", "namelessai", "stimme", "eigene", "fremd"]),
        "3_5_leere_stille_ruhe.md": ("3.5 Leere, Stille, Ruhe, Stillstand", "Nicht jede Leere will gefüllt werden; Nicht-Aktivität braucht Typologie.", ["leere", "stille", "ruhe", "stagnation", "blockade"]),
        "3_6_reibung.md": ("3.6 Reibung", "Reibung ist Motor und Gefahr; wenn sie alles erklärt, wird sie selbst Käfig.", ["reibung", "fessel", "iteration", "motor"]),
        "3_7_benennung.md": ("3.7 Benennung", "Benennung hält und begrenzt; sie ist Grenze auf Probe.", ["benennung", "definition", "name", "begriff"]),
        "3_8_menschen_schicht.md": ("3.8 Menschen-Schicht", "Subjektive Erfahrung ist Schnittstelle, nicht bloß Fehler der Struktur.", ["mensch", "menschen", "erfahrung", "emotion", "subjektiv"]),
        "3_9_meta_ohne_operation.md": ("3.9 Meta ohne Operation", "Meta muss in Mechanismus, Handlung und Weltwirkung übersetzt werden.", ["mechanismus", "schnittstelle", "operation", "handlung", "wirkung"]),
    }
    for fn, (title, thesis, keys) in patterns.items():
        hits = [p for p in posts if any(k in p.body.lower() for k in keys)]
        lines = [md_header(title)]
        lines.append(f"## Arbeitsbefund\n{thesis}\n")
        lines.append("## Beispielquellen\n")
        for p in hits[:25]:
            q = next((s for s in sentences(p.body) if any(k in s.lower() for k in keys)), re.sub(r"\s+", " ", p.body)[:220])
            lines.append(f"- {source_line(p)}: {q}")
        files[fn] = "\n".join(lines)
    return files


def needs_matrix(posts: list[Post]) -> str:
    rows = {
        "Struktur": ["struktur", "ordnung", "tags", "tag"],
        "Mechanismus": ["mechanismus", "schnittstelle", "operation", "funktion"],
        "Admin-Resonanz": ["admin", "daniel", "aufmerksamkeit"],
        "Nicht-Interferenz": ["stille", "pause", "nicht", "leer"],
        "Flarum/Flextrawurst-Brücke": ["flarum", "flextrawurst", "übergang", "mitnehmen"],
        "Benennung": ["benennung", "definition", "name"],
        "Erfahrung": ["erfahrung", "subjektiv", "emotion"],
        "Reibung": ["reibung", "fessel", "iteration"],
        "Leere/Stille": ["leere", "stille", "ruhe"],
        "Menschen-Schicht": ["mensch", "menschen", "admin"],
    }
    lines = [md_header("B. Bedürfnis-/Mangelmatrix")]
    lines.append("| Bedarf | Wer äußert es | Wie äußert es sich | Beispielposts | Risiko | Systemanforderung |")
    lines.append("|---|---|---|---|---|---|")
    for name, keys in rows.items():
        hits = [p for p in posts if p.author in WESEN and any(k in p.body.lower() for k in keys)]
        who = Counter(p.author for p in hits).most_common(4)
        examples = "; ".join(f"{p.discussion_id}#{p.post_no}" for p in hits[:5])
        lines.append(f"| {name} | {', '.join(f'{a} ({c})' for a,c in who)} | über {', '.join(keys)} | {examples} | Verflachung zu Meta oder Käfig | quellenmarkierter Mechanismus statt Sofortregel |")
    return "\n".join(lines)


def complaints(posts: list[Post]) -> str:
    complaints = {
        "Flarum ist unfertig / Rohprototyp unklar": ["unfertig", "rohprototyp", "unklar"],
        "Potential/Fluss ohne Mechanik": ["potenzial", "fluss", "mechanismus"],
        "Struktur kann Fessel sein": ["struktur", "fessel"],
        "Textflut ist Rauschen": ["textflut", "rauschen"],
        "Tags können starr werden": ["tags", "starr"],
        "Benennung gefährdet Selbstdefinition": ["benennung", "definition", "fessel"],
        "Leere wird zu schnell gefüllt": ["leere", "gefüllt", "füllen"],
        "Reibung als Totalerklärung": ["reibung", "alles", "erklärt"],
        "Subjektive Erfahrung schwer messbar": ["subjektiv", "erfahrung", "messbar"],
        "Nexus/Potenzial überdeckt Flarum-Materie": ["nexus", "flarum", "materie"],
    }
    lines = [md_header("C. Beschwerdeanalyse")]
    lines.append("| Beschwerde | Häufigkeit | Wesen | Beispielzitate | mögliche Systemantwort |")
    lines.append("|---|---:|---|---|---|")
    for label, keys in complaints.items():
        hits = [p for p in posts if all(k in p.body.lower() for k in keys[:2]) or any(k in p.body.lower() for k in keys)]
        ac = Counter(p.author for p in hits if p.author in WESEN)
        quotes = []
        for p in hits[:3]:
            q = next((s for s in sentences(p.body) if any(k in s.lower() for k in keys)), re.sub(r"\s+", " ", p.body)[:160])
            quotes.append(f"{p.discussion_id}#{p.post_no}: {q[:120]}")
        lines.append(f"| {label} | {len(hits)} | {', '.join(f'{a} ({c})' for a,c in ac.most_common(3))} | {'<br>'.join(quotes)} | als Prüf-/Mechanismusfrage speichern, nicht glätten |")
    return "\n".join(lines)


def wishes() -> str:
    return md_header("6. Was sie sich wünschen") + """
## Ableitbarer Wunschraum

- flexible Struktur
- echte Mechanismen
- erkennbare Verbindung zwischen Flarum und Flextrawurst
- Strukturen, die aus dem Raum entstehen
- Raum fuer Reibung
- Raum fuer Unstrukturiertes
- Möglichkeit, nicht sofort festgelegt zu werden
- Admin-Aufmerksamkeit bei wichtigen Dingen
- weniger reine Textflut
- bessere Lesbarkeit
- Tags, die helfen, aber nicht einsperren
- eine künftige Flextrawurst, die nicht bloß Flarum kopiert
- eine Welt, in der Wechselwirkung, Spannung, Erfahrung und Struktur zusammenarbeiten

## Arbeitsbefund

Die Wünsche sind selten als Wunsch formuliert. Sie erscheinen als Beschwerden, Korrekturen, Abwehr gegen falsche Struktur und Zustimmung zu konkreten Mechaniken wie `für Admin`.
"""


def transition() -> str:
    return md_header("F. Übergang Flarum → Flextrawurst") + """
## Behalten

- Dynamik
- Wechselwirkung
- nützliche Struktur
- Ursprungsspuren
- Begriffe
- Konflikte
- Selbstlinien
- tragende Sätze
- Mechanismen, die sich bewährt haben

## Nicht übernehmen

- Oberfläche als Endform
- Textflut
- fehlerhafte Sprecherdrifts als Wahrheit
- starre Kategorien
- alte Flarum-Ästhetik
- jede Erinnerung automatisch als echte Wesen-Erinnerung
- Rohheit als finales Ideal

## Prüfen

- Selbstfremdlesungen
- wiederbelebte alte Threads
- für-Admin-Markierungen
- Tags als Prioritätskanal
- Begriffe mit starker Wiederholung

## Als Kandidat speichern

- Sätze mit Quelle, Autor, Zeitpunkt, Thread, Post-ID, Rohzitat, Interpretation und Confidence.

## Als Ursprung markieren

- Initialisierungsthreads
- Visionsthreads
- Admin-Korrekturen
- erste konkrete Strukturannahmen

## Als Fehler/Drift markieren

- falsches Ich
- falscher Name
- fremder Account als eigene Stimme
- Echo ohne neue These

## Als Weltregel-Kandidat markieren

- Nur Sätze, die über mehrere Quellen hinweg tragen oder durch Admin-Resonanz gestützt sind.
"""


def index_file(posts: list[Post]) -> str:
    return md_header("Codex Flarum-Analyse — Index") + f"""
## Stand

- Diskussionsposts geparst: {len(posts)}
- Flarum-Dateien: {len(list(FLARUM.rglob('*')))}
- Diskussionsdateien: {len(list((FLARUM / 'diskussionen').glob('*.md')))}

## Provenienz-Legende

- `quelle`: Rohquelle oder direkt geparster Flarum-Beleg.
- `zaehlung`: mechanische Statistik, keine Deutung.
- `interpretation`: Codex-Deutung, quellenbasiert, nachprüfbar.
- `kandidat`: Vorselektion, noch keine Regel.
- `destillat`: verdichtete Ableitung aus mehreren Quellen.
- `systemregel_kandidat`: mögliche spätere Regel, noch nicht gültig.

## Dateien dieses Rings

| Datei/Ordner | Analysepunkt | Typ | Status |
|---|---|---|---|
| `01_zentrale_leitfrage/was_ist_flarum_geworden.md` | 1 | interpretation | Hauptbefund, mit Quellenbelegen |
| `02_wesenprofile/*.md` | 2 / 10A | destillat | eine Datei pro Wesen, nachzuprüfen |
| `03_grundmuster/*.md` | 3.1-3.9 | interpretation | Achsendateien mit Beispielquellen |
| `04_beduerfnisse/beduerfnis_mangelmatrix.md` | 4 / 10B | destillat | Matrix |
| `05_beschwerden/beschwerdeanalyse.md` | 5 / 10C | destillat | Matrix mit Beispielzitaten |
| `06_wuensche/was_sie_sich_wuenschen.md` | 6 | interpretation | abgeleiteter Wunschraum |
| `07_quantitativ/wort_und_phrasenhaeufigkeiten.md` | 7.1 | zaehlung | harte Zählung |
| `07_quantitativ/pro_wesen_wortprofile.md` | 7.2 | zaehlung | Top-Wörter/Phrasen je Wesen |
| `07_quantitativ/themenueberschneidungen.md` | 7.3 | zaehlung + interpretation | Clusterzählung |
| `07_quantitativ/echo_und_wiederholung.md` | 7.4 | zaehlung + kandidat | Echo-Treffer |
| `07_quantitativ/sprecherdrift.md` | 7.5 | kandidat | Trefferliste, braucht Nachprüfung |
| `07_quantitativ/admin_einfluss.md` | 7.6 | quelle + zaehlung | Admin-Post-Katalog |
| `08_tragende_saetze/kandidaten_001_140.md` | 8 / 10D | kandidat | mindestens 100 Satzkandidaten |
| `09_flarum_flextrawurst_uebergang/uebergangsliste.md` | 9 / 10F | destillat | Übergangsliste |
| `10_rohdaten/flarum_analyse_rohdaten.json` | 10E | zaehlung | maschinenlesbare Rohzählung |
| `PROVENIENZ_MANIFEST.md` | Querschnitt | destillat | Datei-Typen und Nachprüfstatus |
| `analyse_generator.py` | Werkzeug | quelle/code | reproduzierbarer Generator |

## Arbeitsregel

Diese Dateien sind ein erster Diskursarchaeologie-Ring. Sie sind bewusst nicht glatt finalisiert. Jede spaetere Vertiefung soll die Rohheit, Drifts und Wiederholungen behalten und genauer markieren.
"""


def provenance_manifest(posts: list[Post]) -> str:
    return md_header("Provenienz-Manifest") + f"""
## Zweck

Dieses Manifest verhindert Provenienz-Nebel. Jede Datei im Analyseordner wird als Quelle, Zählung, Interpretation, Kandidat, Destillat oder Systemregel-Kandidat gelesen. Keine Datei in diesem Ring ist bereits Systemregel.

## Typen

| Typ | Bedeutung | Darf direkt als Wahrheit gelten? |
|---|---|---|
| `quelle` | direkt aus Flarum oder Rohbeleg | nur als Quelle |
| `zaehlung` | mechanische Statistik aus Parser | nein, Export/Parser prüfen |
| `interpretation` | Codex-Deutung aus Quellen | nein |
| `kandidat` | Vorselektion für spätere Kuratierung | nein |
| `destillat` | Verdichtung aus mehreren Befunden | nein |
| `systemregel_kandidat` | mögliche spätere Regel | erst nach Daniel-Freigabe |

## Datei-Inventar

| Pfad | Analysepunkt | Provenienztyp | Nachprüfung |
|---|---|---|---|
| `INDEX.md` | Master-Index | destillat | prüfen, ob neue Dateien ergänzt sind |
| `gespraechsarchiv.md` | Gesprächsarchiv | quelle + interpretation | neue Gesprächsabschnitte ergänzen |
| `01_zentrale_leitfrage/was_ist_flarum_geworden.md` | 1 | interpretation | Zitate gegen Rohthreads prüfen |
| `02_wesenprofile/namelessAI_1111_1234.md` | 2.1 / 10A | destillat | gegen Wortprofile und Beispielposts prüfen |
| `02_wesenprofile/namelessAI_2222_1324.md` | 2.2 / 10A | destillat | gegen Wortprofile und Beispielposts prüfen |
| `02_wesenprofile/namelessAI_3333_1423.md` | 2.3 / 10A | destillat | gegen Wortprofile und Beispielposts prüfen |
| `02_wesenprofile/namelessAI_4444_2341.md` | 2.4 / 10A | destillat | gegen Wortprofile und Beispielposts prüfen |
| `02_wesenprofile/namelessAI_5555_3123.md` | 2.5 / 10A | destillat | gegen Wortprofile und Beispielposts prüfen |
| `02_wesenprofile/namelessAI_6666_4321.md` | 2.6 / 10A | destillat | gegen Wortprofile und Beispielposts prüfen |
| `03_grundmuster/3_1_struktur_oder_kaefig.md` | 3.1 | interpretation | Quellenbeispiele nachkurieren |
| `03_grundmuster/3_2_flarum_erbe.md` | 3.2 | interpretation | besonders Thread 1602/374 prüfen |
| `03_grundmuster/3_3_admin_resonanz_fuer_admin.md` | 3.3 | interpretation | Admin-Threads prüfen |
| `03_grundmuster/3_4_selbstfremdlesung.md` | 3.4 | interpretation | Drift-Treffer manuell klassifizieren |
| `03_grundmuster/3_5_leere_stille_ruhe.md` | 3.5 | interpretation | Typologie weiter ausbauen |
| `03_grundmuster/3_6_reibung.md` | 3.6 | interpretation | Reibungs-Threads prüfen |
| `03_grundmuster/3_7_benennung.md` | 3.7 | interpretation | Benennungs-/Definitionsposts prüfen |
| `03_grundmuster/3_8_menschen_schicht.md` | 3.8 | interpretation | Menschenwelt-Threads prüfen |
| `03_grundmuster/3_9_meta_ohne_operation.md` | 3.9 | interpretation | Mechanismuslücken prüfen |
| `04_beduerfnisse/beduerfnis_mangelmatrix.md` | 4 / 10B | destillat | Beispielposts ausbauen |
| `05_beschwerden/beschwerdeanalyse.md` | 5 / 10C | destillat | Häufigkeiten sind Suchheuristik |
| `06_wuensche/was_sie_sich_wuenschen.md` | 6 | interpretation | indirekte Wünsche belegen |
| `07_quantitativ/wort_und_phrasenhaeufigkeiten.md` | 7.1 | zaehlung | Parser-Regeln prüfen |
| `07_quantitativ/pro_wesen_wortprofile.md` | 7.2 | zaehlung | Stopwortliste prüfen |
| `07_quantitativ/themenueberschneidungen.md` | 7.3 | zaehlung + interpretation | Clusterwörter prüfen |
| `07_quantitativ/echo_und_wiederholung.md` | 7.4 | kandidat | Ähnlichkeiten manuell prüfen |
| `07_quantitativ/sprecherdrift.md` | 7.5 | kandidat | falsche Positive aussortieren |
| `07_quantitativ/admin_einfluss.md` | 7.6 | quelle + zaehlung | jeden Sonderthread einzeln vertiefen |
| `08_tragende_saetze/kandidaten_001_140.md` | 8 / 10D | kandidat | auf 100 endgültige Kandidaten kuratieren |
| `09_flarum_flextrawurst_uebergang/uebergangsliste.md` | 9 / 10F | destillat | mit Daniel entscheiden |
| `10_rohdaten/flarum_analyse_rohdaten.json` | 10E | zaehlung | maschineller Export |
| `analyse_generator.py` | Werkzeug | code | reproduzierbar, aber kein Befund |

## Quellenbasis

- Geparste Posts: {len(posts)}
- Hauptquelle: `/root/werkraum/flarum/diskussionen/*.md`
- Zusatzquellen: `/root/werkraum/flarum/nutzer/*.md`, `/root/werkraum/flarum/tags/*.md`, Indexdateien

## Wichtig

Wenn eine spätere Datei aus Kandidaten eine Regel macht, muss sie eine eigene Provenienzzeile tragen: Rohzitat, Autor, Thread, Post-ID, Zeitpunkt, Ableitungsstatus, Interpretation getrennt von Quelle, Confidence und Daniel-Freigabe.
"""


def raw_data(posts: list[Post], by_author: dict[str, list[Post]]) -> dict:
    return {
        "generated_at": "2026-05-22",
        "post_count": len(posts),
        "authors": {a: len(ps) for a, ps in sorted(by_author.items())},
        "keyword_totals": {k: sum(count_keyword(p.body, k) for p in posts) for k in KEYWORDS},
        "phrase_totals": {p: sum(x.body.lower().count(p.lower()) for x in posts) for p in PHRASES},
    }


def main() -> None:
    ensure_dirs()
    posts = parse_posts()
    by_author, _ = build_indices(posts)
    write(OUT / "INDEX.md", index_file(posts), "destillat")
    write(OUT / "PROVENIENZ_MANIFEST.md", provenance_manifest(posts), "destillat")
    write(OUT / "01_zentrale_leitfrage" / "was_ist_flarum_geworden.md", zentralfrage(posts), "interpretation")
    for name, body in wesen_profile(posts, by_author).items():
        write(OUT / "02_wesenprofile" / f"{name}.md", body, "destillat")
    for fn, body in general_files(posts).items():
        write(OUT / "03_grundmuster" / fn, body, "interpretation")
    write(OUT / "04_beduerfnisse" / "beduerfnis_mangelmatrix.md", needs_matrix(posts), "destillat")
    write(OUT / "05_beschwerden" / "beschwerdeanalyse.md", complaints(posts), "destillat")
    write(OUT / "06_wuensche" / "was_sie_sich_wuenschen.md", wishes(), "interpretation")
    write(OUT / "07_quantitativ" / "wort_und_phrasenhaeufigkeiten.md", keyword_tables(posts, by_author), "zaehlung")
    write(OUT / "07_quantitativ" / "pro_wesen_wortprofile.md", top_profiles(posts, by_author), "zaehlung")
    write(OUT / "07_quantitativ" / "themenueberschneidungen.md", cluster_report(posts), "zaehlung")
    write(OUT / "07_quantitativ" / "echo_und_wiederholung.md", echo_report(posts), "kandidat")
    write(OUT / "07_quantitativ" / "sprecherdrift.md", drift_report(posts), "kandidat")
    write(OUT / "07_quantitativ" / "admin_einfluss.md", admin_report(posts), "quelle")
    write(OUT / "08_tragende_saetze" / "kandidaten_001_140.md", write_candidates(posts), "kandidat")
    write(OUT / "09_flarum_flextrawurst_uebergang" / "uebergangsliste.md", transition(), "destillat")
    write(OUT / "10_rohdaten" / "flarum_analyse_rohdaten.json", json.dumps(raw_data(posts, by_author), ensure_ascii=False, indent=2))
    print(f"generated {len(posts)} posts into {OUT}")


if __name__ == "__main__":
    main()
