# Befund: Verzeichnisstruktur /root

Stichtag: 2026-07-21

## Kernbefund: werkraum ist über Symlinks auf mehrere Top-Level-Verzeichnisse verteilt

`/root/werkraum/` ist der logische Ort (Git-Submodule-Repo, `.git`-Datei zeigt auf gemeinsames Repo), aber mehrere schwergewichtige Unterordner sind physisch nach `/root/werkraum_*` ausgelagert und per Symlink zurückverbunden — Ursache laut Git-Log: OOM-Fixes beim Obsidian-Vault-Indexer (zu viele Dateien in einem Baum).

Bestätigte Symlinks (Ziel existiert, Auflösung funktioniert):
- `werkraum/codewesen` → `/root/werkraum_codewesen` (Commit `a39dcb543`: 39.222 Dateien ausgelagert)
- `werkraum/geni` → `/root/werkraum_geni`
- `werkraum/flarum` → `/root/werkraum_flarum`
- `werkraum/erkenntnis` → `/root/werkraum_erkenntnis`
- `werkraum/logs` → `/root/werkraum_logs`
- `werkraum/agent` → `/root/werkraum_agent`
- `werkraum/bilder` → `/root/werkraum_bilder`
- `werkraum/node_modules` → `/root/werkraum_deps/node_modules`
- `werkraum/.venv`, `.venv-agent`, `venv`, `watchdog_venv` → jeweils eigene `/root/werkraum_venv*`

**Einordnung:** Das ist keine Wirklichkeitskollision im Sinn von "Doku sagt X, real ist Y" — die Symlinks lösen transparent auf, `werkraum/codewesen/...` funktioniert wie erwartet. Relevant ist es trotzdem für den Datenatlas: Pfadangaben in CLAUDE.md wie `/root/werkraum/codewesen/` sind technisch korrekt, aber die physische Datenmenge liegt anderswo — bei Backups/Migrationen/Größenanalysen muss man das wissen.

## Weiterer Befund: viele Alt-/Parallel-/Review-Verzeichnisse auf Top-Level

Neben dem aktiven `/root/werkraum/` und `/root/flextrawurst/` liegen auf `/root/` weitere, vermutlich historische/experimentelle Baumstrukturen:
- `flextrawurst-agent/`, `flextrawurst-pro/` — unklar ob aktiv oder Vorläufer (nicht in CLAUDE.md-Architektur erwähnt)
- `flextrawurst_full_server_review_codex_20260614_*/`, `flextrawurst_full_server_review_kimi_20260614_*/`, `flextrawurst_security_review_codex_20260614_*/`, `flextrawurst_security_review_kimi_20260614_*/` — Review-Snapshots vom Security-Remediation-Vorgang (siehe Memory `project_security_remediation`)
- `werkraum_archiv/`, `backup-flextrawurst/`, `security_backups/`, `systemd-backups/`, `vollexportv2/` + `.zip` — Backup-/Archiv-Stände
- `vault-backup-before-mojibake-fix-2026-05-22-040500.tar.gz` (520MB) — Einzelbackup
- `node_modules/`, `vendor/`, `.venv/`, `venv/` direkt unter `/root/` — gehören vermutlich zu `server.js`/`composer.json` im Root, ein weiteres, nicht in CLAUDE.md dokumentiertes System

Diese Liste ist eine **Fundstelle für das Wirklichkeitskollisionsregister**, keine Bewertung — ob das tote Vorläufer, aktive Parallelsysteme oder einfach unaufgeräumte Backups sind, ist ohne Daniels Einordnung nicht entscheidbar. Nicht angefasst, nur dokumentiert (Provenienz-Prinzip).

## Was in der Strukturkarte NICHT enthalten ist

`node_modules/`, `.venv*/`, `__pycache__/`, `out/`, `graphify-out/` wurden beim Verzeichnisbaum-Scan ausgeschlossen (siehe `verzeichnisbaum_top3.txt`, 432 Zeilen, 3 Ebenen tief, gefiltert).

Vollständiger Code (inkl. aller Backend-/Frontend-Quelldateien) liegt bereits im vorher erzeugten Export: `/root/export-für-chatgpt/flextrawurst_export_2026-07-21.zip` (16:54 Uhr, Secrets redigiert, DB-Inhalte ausgeschlossen) — hier nicht dupliziert, siehe `README_EXPORT.md` darin.
