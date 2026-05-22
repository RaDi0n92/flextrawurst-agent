
## 2026-05-22 02:03

# Aktuelle Aufgabe

<!-- 
Diese Datei wird von Claude am Ende der Planungsphase beschrieben.
Codex liest sie beim Start.
Format: klar, direkt, kein Prosa-Rauschen.
-->

## Was gebaut werden soll

Obsidian im Docker-Container läuft stabil, aber das Fenster startet immer bei 10×10 Pixel → schwarzer Bildschirm im Browser. Das muss dauerhaft gefixt werden.

Der Fix-Ansatz ist bereits bekannt und hat kurz funktioniert:
1. `/defaults/autostart` im Container patchen — Obsidian im Hintergrund starten, dann per xdotool-Loop auf 1920×1080 resizen
2. Dieses Patch muss persistent sein — über `obsidian-gpu-fix.sh` in `/var/lib/docker/volumes/obsidian_config_ls/_data/custom-cont-init.d/` (wird bei jedem Container-Start ausgeführt)
3. Das offene Problem: Obsidian crasht nach dem Start noch — Ursache unklar, muss untersucht werden

Ziel: Obsidian öffnet den Vault `/werkraum` im Browser (Port 8443) ohne schwarzen Bildschirm, und bleibt stabil.

## Relevante Dateien und Orte

- Container-Name: `obsidian` (läuft, `docker ps` zeigt ihn)
- Volume-Pfad: `/var/lib/docker/volumes/obsidian_config_ls/_data/`
- Custom-Init-Skript: `/var/lib/docker/volumes/obsidian_config_ls/_data/custom-cont-init.d/obsidian-gpu-fix.sh`
  → wird bei Container-Start ausgeführt und überschreibt `/usr/bin/obsidian` + `/defaults/autostart`
- Autostart im Container: `/defaults/autostart` (wird von openbox-session beim Start ausgeführt)
- Obsidian-Config im Container: `/config/.config/obsidian/obsidian.json` und `/config/.config/obsidian/a1b2c3d4e5f6a7b8.json`
- Vault: `/werkraum` (gemountet von `/root/werkraum` auf Host)
- Browser-Zugang: Port 8443 (nginx SSL-Proxy → localhost:3080)
- Obsidian-Log: `/config/.config/obsidian/obsidian.log` im Container (via `docker exec obsidian cat ...`)

## Was bereits besprochen wurde

Claude hat folgendes rausgefunden (Diagnose, keine saubere Lösung):

- Das Obsidian-Fenster startet bei 10×10 weil `--start-maximized` in der headless-Umgebung nicht greift
- Openbox läuft (pid 369), DISPLAY=:1, 1920×1080
- `obsidian-gpu-fix.sh` wurde bereits um einen `/defaults/autostart`-Patch ergänzt: Obsidian im Hintergrund starten, xdotool-Loop wartet auf Fenster und resized auf 1920×1080
- Das hat einmalig funktioniert (Fenster war kurz auf 1920×1080 sichtbar), aber Obsidian ist danach abgestürzt
- Ursache des Absturzes: noch nicht untersucht
- Obsidian crasht regelmäßig und wird nicht automatisch neu gestartet (Watchdog monitort `$HOME/.config/openbox/autostart` — aber das existiert nicht, also springt er nicht an)

Aktueller Zustand der `obsidian-gpu-fix.sh` (auf dem Host, persistent):
```bash
# Patch 1: /usr/bin/obsidian → GPU-Flags ohne --start-maximized (wurde von Claude hinzugefügt, bitte prüfen ob sinnvoll)
# Patch 2: /defaults/autostart → Resize-Loop nach Obsidian-Start
```

## Wo das Ergebnis hin soll

Geänderte Dateien:
- `/var/lib/docker/volumes/obsidian_config_ls/_data/custom-cont-init.d/obsidian-gpu-fix.sh` — die einzige persistente Datei die Neustarts überlebt

Ziel-Zustand:
- `docker restart obsidian` → danach ist der Vault im Browser sichtbar und stabil
- Obsidian läuft nach einem Crash neu an (Watchdog oder autostart-Loop)

## Offene Fragen

1. Warum crasht Obsidian nach dem Start? (Log prüfen: `docker exec obsidian tail -50 /config/.config/obsidian/obsidian.log`)
2. Ist `--start-maximized` wirklich sinnlos hier, oder gibt es eine andere Chromium-Flag die funktioniert?
3. Soll Obsidian bei einem Crash automatisch neu starten? Wenn ja: wie — über den Watchdog oder einen einfachen `while true; do obsidian; done` in autostart?

---

## 2026-05-22 02:25

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

---
