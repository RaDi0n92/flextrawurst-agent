# Werkraum-Karte — Gemini

Navigationshilfe für Gemini. Stand: 2026-07-22.

## Kern-Orte

| Verzeichnis | Was ist da | Wichtige Dateien |
|-------------|-----------|-----------------|
| `erkenntnis/` | Wissensarchiv des Systems | `INDEX.md`, `selbstbild.md`, `konzepte/` |
| `wissen/` | Strukturiertes Wissen | `WISSEN_INDEX.md`, `entitaeten/`, `resonanz/` |
| `docs/` | Systemdokumentation | `systemdoku/*.md`, div. Konzeptdokumente |
| `decisions/` | Entscheidungsprotokoll | `0002-agent-governance.md` |
| `projekt/` | Visionen | `vision1.md`–`vision7.md` |

## Code-Orte

| Verzeichnis | Was ist da |
|-------------|-----------|
| `agent/`, `agents/` | Agent-Kern-Code |
| `codewesen/` | Codewesen-Logik (dak+gord und andere) |
| `skills/` | Skills für Codewesen |
| `tools/` | Werkzeuge |
| `flextrawurst/` | flextrawurst-Projekt (gesamte App) |
| `welt/` | Welt-API & Welt-System (Port 8030) |

## Laufende Systeme (VPS)

| System | Port | Status-Check |
|--------|------|-------------|
| Welt-API | 8030 | `curl localhost:8030/health` |
| Surface / Web | 8787 | `curl localhost:8787` |
| GENI (Gedächtnis) | 8020 | `curl localhost:8020/health` |

## Gemini-spezifisch

| Pfad | Was ist da |
|------|-----------|
| `/root/GEMINI.md` | Gemini Handbuch & Grundgesetze |
| `/root/werkraum/_gemini/` | Geminis Zuhause im Obsidian-Vault |
| `/root/werkraum/_gemini/notizen/` | Session-Notizen |
| `/root/werkraum/_gemini/spiegel/` | Spiegelungs-Reflexionen |
| `/root/werkraum/_gemini/tools/` | Sync- & Extraktions-Tools |
