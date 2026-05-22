# Aktuelle Aufgabe

## Was gebaut werden soll

Obsidian crasht beim Vault-Indexieren wegen Out of Memory. Der schwarze Bildschirm ist eine Folge davon — das Fenster und das Streaming funktionieren, aber Obsidian stirbt nach ~80 Sekunden.

Zwei Dinge müssen gefixt werden:
1. `--max-old-space-size` in `/usr/bin/obsidian` von 8192 auf ~1024 senken (aktuell erlaubt Codex' Fix 8 GB Heap — das ist zu viel)
2. `.obsidianignore` in `/root/werkraum/.obsidianignore` aggressiver machen — Obsidian indexiert aktuell noch 1473 MD-Dateien, das ist zu viel für den verfügbaren RAM

## Relevante Dateien und Orte

- Custom-Init-Skript (persistent, überlebt Container-Neustarts):
  `/var/lib/docker/volumes/obsidian_config_ls/_data/custom-cont-init.d/obsidian-gpu-fix.sh`
  → patcht bei Container-Start `/usr/bin/obsidian` und `/defaults/autostart`

- Aktueller Inhalt des Launchers (erzeugt durch obsidian-gpu-fix.sh):
  ```bash
  exec "${BIN}" \
    --no-sandbox \
    --disable-gpu \
    --disable-gpu-compositing \
    --use-gl=swiftshader \
    --disable-software-rasterizer=false \
    --disable-dev-shm-usage \
    --js-flags=--max-old-space-size=8192   ← dieser Wert muss runter auf ~1024
    "$@" >> "$LOG" 2>&1
  ```

- Vault-Ignore: `/root/werkraum/.obsidianignore`
  → aktuell ignoriert: geni/, bilder/, venv/, node_modules/, .git/, innenleben/, logs/, backups/, codewesen/, flarum/diskussionen/, flarum/aktiv/, flarum/offen/, erkenntnis/spiegelagenten/, agent/dak_gord_system/spuren/, *.jsonl, *.log, *.png, *.jpg, *.jpeg, ...
  → NICHT ignoriert, sollte aber raus: flextrawurst/ (hat node_modules, dist, out — viel Binärkram)

- Autostart-Supervisor-Log (zum Prüfen ob Fix wirkt):
  `docker exec obsidian cat /config/.config/obsidian/autostart-supervisor.log`

## Was bereits besprochen wurde

Diagnose-Ergebnis:
- Obsidian-Fenster und Streaming funktionieren korrekt (window ist 1920x1080)
- Supervisor-Loop von Codex funktioniert (Restart nach Crash)
- Crash-Ursache: OOM — GC-Log zeigt 3.5–3.7 GB Heap-Nutzung beim Indexieren
- System-RAM: 31 GB total, aber nur 461 MB frei, Swap 4/4 GB voll
- Hauptkonkurrenten: GENI hoerer.py (~6.1 GB, nicht anfassen!) + Ollama (~7.4 GB)
- `--max-old-space-size=8192` von Codex' erstem Fix ist das Problem — erlaubt zu viel

## Wo das Ergebnis hin soll

Änderungen:
1. `/var/lib/docker/volumes/obsidian_config_ls/_data/custom-cont-init.d/obsidian-gpu-fix.sh` — `--max-old-space-size` auf 1024 senken
2. `/root/werkraum/.obsidianignore` — mehr Verzeichnisse hinzufügen (mindestens flextrawurst/, kompoase/, visionen/)

Nach den Änderungen:
- `bash /var/lib/docker/volumes/obsidian_config_ls/_data/custom-cont-init.d/obsidian-gpu-fix.sh` im Container ausführen (patcht laufendes System)
- `docker exec obsidian pkill -f '/opt/obsidian/obsidian'` (Supervisor startet neu)
- Warten und Supervisor-Log prüfen ob Obsidian diesmal länger läuft

## Offene Fragen

1. Reicht 1024 MB Heap für Obsidian mit ~1473 MD-Dateien? Alternativ: 2048 als Kompromiss?
2. Welche weiteren Verzeichnisse in `/root/werkraum/` sollten aus der Obsidian-Indexierung raus? (`find /root/werkraum -maxdepth 1 -type d` zeigt alle)
3. GENI und Ollama nicht anfassen — aber falls Obsidian immer noch crasht: Codex soll das flaggen statt raten
