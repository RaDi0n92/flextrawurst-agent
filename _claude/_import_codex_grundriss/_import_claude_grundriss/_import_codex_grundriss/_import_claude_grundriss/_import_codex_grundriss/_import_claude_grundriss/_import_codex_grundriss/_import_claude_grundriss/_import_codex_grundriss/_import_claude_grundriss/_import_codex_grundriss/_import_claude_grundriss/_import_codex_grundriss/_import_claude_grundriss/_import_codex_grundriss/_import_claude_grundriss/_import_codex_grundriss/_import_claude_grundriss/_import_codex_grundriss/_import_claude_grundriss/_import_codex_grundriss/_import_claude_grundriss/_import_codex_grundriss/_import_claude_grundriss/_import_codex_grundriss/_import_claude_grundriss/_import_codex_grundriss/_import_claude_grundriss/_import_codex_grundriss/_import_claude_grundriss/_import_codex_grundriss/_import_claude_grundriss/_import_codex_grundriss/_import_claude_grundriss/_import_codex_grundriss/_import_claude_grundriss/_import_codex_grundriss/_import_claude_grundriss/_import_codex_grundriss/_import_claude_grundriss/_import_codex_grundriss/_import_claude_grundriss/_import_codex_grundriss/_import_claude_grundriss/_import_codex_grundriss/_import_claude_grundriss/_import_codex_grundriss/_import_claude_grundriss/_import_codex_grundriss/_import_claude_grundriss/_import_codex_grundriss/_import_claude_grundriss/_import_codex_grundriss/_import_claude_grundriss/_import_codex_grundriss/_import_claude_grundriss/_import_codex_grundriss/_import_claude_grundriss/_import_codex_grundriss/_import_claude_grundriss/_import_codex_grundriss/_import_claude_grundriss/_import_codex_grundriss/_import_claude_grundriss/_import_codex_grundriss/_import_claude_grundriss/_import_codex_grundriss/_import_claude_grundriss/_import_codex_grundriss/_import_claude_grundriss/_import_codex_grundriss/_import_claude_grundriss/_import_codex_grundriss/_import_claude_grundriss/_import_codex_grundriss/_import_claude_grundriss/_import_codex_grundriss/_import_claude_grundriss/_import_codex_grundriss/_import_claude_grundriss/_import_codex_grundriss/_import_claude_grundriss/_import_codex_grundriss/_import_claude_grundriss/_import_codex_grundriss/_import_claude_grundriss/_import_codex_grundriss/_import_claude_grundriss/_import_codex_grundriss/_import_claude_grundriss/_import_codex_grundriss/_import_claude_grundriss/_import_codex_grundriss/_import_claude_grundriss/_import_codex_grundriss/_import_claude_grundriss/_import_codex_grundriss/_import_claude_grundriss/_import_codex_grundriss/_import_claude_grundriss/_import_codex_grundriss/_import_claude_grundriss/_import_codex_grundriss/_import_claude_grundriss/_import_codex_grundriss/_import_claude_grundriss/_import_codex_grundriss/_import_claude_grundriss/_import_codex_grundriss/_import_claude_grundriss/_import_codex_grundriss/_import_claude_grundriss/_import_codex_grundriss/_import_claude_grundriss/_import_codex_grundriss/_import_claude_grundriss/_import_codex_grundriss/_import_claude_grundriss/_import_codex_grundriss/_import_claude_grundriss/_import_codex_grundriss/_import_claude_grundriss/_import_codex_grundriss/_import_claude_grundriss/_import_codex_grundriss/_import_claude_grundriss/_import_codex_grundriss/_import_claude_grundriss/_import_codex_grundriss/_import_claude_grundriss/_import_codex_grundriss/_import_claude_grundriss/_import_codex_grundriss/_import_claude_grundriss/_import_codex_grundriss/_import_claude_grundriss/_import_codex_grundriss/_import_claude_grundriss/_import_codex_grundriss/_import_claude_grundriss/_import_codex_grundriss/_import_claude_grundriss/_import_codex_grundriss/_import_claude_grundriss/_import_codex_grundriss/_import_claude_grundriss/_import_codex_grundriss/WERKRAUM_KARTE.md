# Werkraum-Karte

Navigationshilfe für Codex. Stand: 2026-05-10.

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

## Daten & Zustand

| Verzeichnis | Was ist da |
|-------------|-----------|
| `state/` | Systemzustände |
| `brain/` | Projektvisionen (vision1–7) |
| `telemetry/` | Telemetrie-Daten |
| `backups/` | Backups |

## Codex-spezifisch

| Pfad | Was ist da |
|------|-----------|
| `/root/.codex/memories/` | Codex-Memory und Arbeitsnotizen |
| `/root/werkraum/_codex/` | Codex' Zuhause im Obsidian-Vault |
| `/root/werkraum/_codex/notizen/` | Session-Notizen |
| `/root/.codex/config.toml` | Lokale Codex-Konfiguration |
| `/root/.codex/history.jsonl` | Lokale Codex-Verlaufsspur |
