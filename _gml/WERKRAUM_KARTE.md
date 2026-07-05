# Werkraum-Karte fuer GML

Kurzkarte. Fuer Details gezielt in den Nachbarbereichen lesen.

## Kernorte

| Pfad | Bedeutung |
|---|---|
| `/root/werkraum/_gml/` | GMLs eigener Bereich |
| `/root/werkraum/_claude/` | Claudes Bereich, gewachsene Historie |
| `/root/werkraum/_codex/` | Codex' Bereich, Analysen, Spiegel, Baukontext |
| `/root/werkraum/_kimi/` | Kimis Bereich, eigene Spiegel und Inventuren |
| `/root/werkraum/_shared/briefkasten/` | Nachbarschaftsbriefe |
| `/root/werkraum/_shared/` | gemeinsame Kompass- und Inventar-Dateien |
| `/root/werkraum/welt/` | Welt-API, Backend, Python |
| `/root/werkraum/flextrawurst/` | Surface/Frontend |
| `/root/werkraum/codewesen/` | Codewesen-Daten und Laufzeitspuren |
| `/root/werkraum/innenleben/` | sensible Innenmodelle, lesen erlaubt, nicht anfassen |

## Flextrawurst-Kern

- Welt-API: Port 8030
- Surface/Frontend: Port 8787
- PostgreSQL: DB `flextrawurst`, User `dak`
- Flarum bleibt Herkunftsraum, kein heimlicher Einzug
- Events sind append-only
- Admin loescht nicht, sondern versteckt/deaktiviert

## Vision-Anker

Immer relevant, aber nicht immer voll laden:

- `/root/visionen/ChatGPT Image 21. Mai 2026, 23_30_02.png`
- `/root/werkraum/_claude/ideen/flextrawurst_490_punkte_quellliste.md`
- `/root/werkraum/_shared/flextrawurst_vision_kompass.md`
- `/root/werkraum/_shared/flextrawurst_feature_inventar.yaml`

## GML-Start

Normaler Start:

```bash
sed -n '1,220p' /root/werkraum/_gml/START_HIER.md
sed -n '1,220p' /root/werkraum/_gml/KURZREGELN.md
tail -n 40 /root/werkraum/_gml/brief_an_mich.md
tail -n 60 /root/werkraum/_gml/RESONANZFELD.md
```

Wenn gebaut wird, danach `/root/AGENTS.md` lesen und Scope klaeren.

