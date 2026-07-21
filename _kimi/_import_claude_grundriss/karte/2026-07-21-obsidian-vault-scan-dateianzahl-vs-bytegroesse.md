---
datum: 2026-07-21
betrifft: [obsidian, oom, vault, symlinks, systemd, llama-hauhaucs]
autor: claude-code bei Daniels VPS
---

## Neue Erkenntnis über das System

Obsidians Vault-Scan (dieser Docker-Build, Version 1.12.7) skaliert mit **Dateianzahl**, nicht mit Bytegröße. 568MB an großen Bilddateien zu entfernen bewegte die V8-Crash-Schwelle kaum (3578→3632MB), aber 39.222 zusätzliche kleine JSON/MD-Dateien (codewesen/) waren der Unterschied zwischen sofortigem Crash und stabilem Rendern. Wer künftig einen ähnlichen OOM-Crash-Loop diagnostiziert: zuerst `find <ordner> -type f | wc -l` prüfen, nicht nur `du -sh`.

Der zugrundeliegende Deckel selbst (~3,6-4GB) ist keine Obsidian-Eigenart, sondern V8-Pointer-Compression — architektonisch im Electron-Build, `--max-old-space-size` über diesen Punkt hinaus wirkungslos. Das stand schon in `docs/systemdoku/14_obsidian.md` (Update 20.07.), bevor ich es heute Nacht nochmal empirisch nachvollzogen habe.

## Korrektur einer Altannahme

Ich bin bisher davon ausgegangen, dass Obsidian in diesem Setup Symlinks folgt (Standard-Community-Wissen: "seit v0.11.1 unterstützt"). Live getestet (Ordner `agent/` aus `userIgnoreFilters` genommen, Symlink zeigt auf `/root/werkraum_agent`): weder Crash noch sichtbarer Inhalt im Graph — der Symlink wird schlicht nicht verfolgt, aus unbekanntem Grund (evtl. `userIgnoreFilters`-Namensmatch vor Symlink-Auflösung, evtl. Build-spezifisch). Für dieses System gilt also: **physisch ausgelagerte + symlink-verlinkte Ordner sind für Obsidian komplett unsichtbar**, nicht nur aus der UI ausgeblendet. Stabilität und Sichtbarkeit sind hier keine unabhängig wählbaren Eigenschaften, sondern direkt gegeneinander verschränkt.

## Struktur, die neu sichtbar wurde

Der werkraum-Vault ist seit heute Nacht kein 1:1-Ordnerspiegel mehr, sondern ein kuratierter Ausschnitt mit bewussten blinden Flecken: `codewesen/`, `geni/`, `flarum/`, `erkenntnis/`, `agent/`, `logs/`, `bilder/` liegen alle physisch unter `/root/werkraum_<name>/` und sind nur noch per Symlink am alten Pfad erreichbar (für laufende Dienste transparent, für Obsidian nicht). `_claude/`, `_codex/`, `_kimi/` (Claudes/Codex'/Kimis eigene Bereiche) sind bewusst NICHT ausgelagert — die bleiben der eigentliche Sinn des Vaults.

Technik für git-getrackte Ordner dabei: `git rm -r --cached <ordner>` (Historie bleibt in alten Commits) + `.gitignore`-Eintrag + physisches `mv` + `ln -s` zurück, ohne Lücke zwischen `mv` und `ln -s` (eine Lücke ließ bei einem früheren Testlauf derselben Nacht einen laufenden Dienst eine neue, leere Verzeichnisstruktur an der alten Stelle anlegen).

## Offene Frage für später

Ob ein zweites, kleineres Obsidian-Vault (analog zu `MDtalk/`) für genau die ausgelagerten Ordner den Zielkonflikt zwischen Stabilität und Sichtbarkeit auflösen würde — von Daniel heute Nacht bewusst zurückgestellt, kein Auftrag dazu.
