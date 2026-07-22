# Werkraum-Karte

Navigationshilfe für Kimi. Stand: 2026-05-31.

## Kern-Orte

| Verzeichnis | Was ist da | Wichtige Dateien |
|-------------|-----------|-----------------|
| `erkenntnis/` | Wissensarchiv des Systems | `INDEX.md`, `selbstbild.md`, `konzepte/` |
| `wissen/` | Strukturiertes Wissen | `WISSEN_INDEX.md`, `entitaeten/`, `resonanz/` |
| `docs/` | Systemdokumentation | div. Konzeptdokumente |
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

## Laufende Systeme (VPS)

| System | Port | Status-Check |
|--------|------|-------------|
| GENI (Gedächtnis) | 8020 | `curl localhost:8020/health` |
| Obsidian | 3080 → 8443 | Docker: `docker ps` |
| dak+gord | — | `ps aux | grep starte_dak` |
| Welt-API | 8030 | `curl localhost:8030/health` |
| flextrawurst Frontend | 8787 | `curl localhost:8787` |

## Daten & Zustand

| Verzeichnis | Was ist da |
|-------------|-----------|
| `state/` | Systemzustände |
| `brain/` | Projektvisionen (vision1–7) |
| `telemetry/` | Telemetrie-Daten |
| `backups/` | Backups |

## Kimi-spezifisch

| Pfad | Was ist da |
|------|-----------|
| `/root/werkraum/_kimi/` | Kimis Zuhause im Obsidian-Vault |
| `/root/werkraum/_kimi/notizen/` | Session-Notizen |
| `/root/werkraum/_kimi/spiegel/` | Spiegel-Reflexionen |
| `/root/werkraum/_kimi/resonanz/` | Extrahierte Dimensionen |
| `/root/werkraum/_kimi/tools/` | Werkzeuge |
