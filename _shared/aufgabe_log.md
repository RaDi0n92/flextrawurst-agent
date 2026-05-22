
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
