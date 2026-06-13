# OOM-Diagnose und Stabilisierung — 2026-06-12 20:10

## Ausgangszustand (nach Neustart, ~20:10)

**Uptime:** 21 Minuten nach Neustart
**Load:** 13.93 / 16.03 / 12.85 — kritisch hoch
**RAM:** 31 GiB total, 15 GiB used, 416 MiB free, 16 GiB available
**Swap:** 11 GiB total, 7.2 GiB used — bereits stark belastet
**Disk:** 148G / 464G (32%)

---

## OOM-Ereignisse letzter Boot (Kernel-Log)

```
08:39:10 — themen-cluster.service python3 KILLED: 16.1 GB RSS (total_vm 16.4 GB)
14:16:03 — themen-cluster.service python3 KILLED: 25.4 GB RSS (total_vm 25.7 GB)
18:46:03 — geni-muster.service python3 KILLED: 15.4 GB RSS (total_vm 19 GB)
           (oom-killer invoked by: ollama)
```

Alle drei: OOM killer, kein graceful exit.

---

## Root Cause Analyse

### Primärer Täter: themen-cluster.service

**Script:** `/root/werkraum/welt/themen_cluster.py`
**Problem:** 
- `CROSS JOIN ftw_posts p1, p2` auf 11.276 public Posts = ~63 Millionen Paare
- `cur.fetchall()` lädt alle Similarity-Paare in Python-Speicher
- Pro Tick (alle 5 min) kann das je nach Threshold-Matches GB an RAM binden
- Wächst über Zeit weil `post_similarity`-Tabelle akkumuliert

### Sekundärer Täter: geni-muster.service  

**Script:** `/root/werkraum/geni/muster.py`
**Problem:**
- `lade_alle_knoten()` lädt ALLE JSON-Dateien aus KNOTEN_DIR
- KNOTEN_DIR enthält **9.875.388 Dateien** (38 GB)
- Python lädt alle in eine Liste → 6–15 GB RAM-Wachstum
- Timer: alle 2 Stunden

### Verstärker: ollama.service

**Modell:** gemma4:e2b-it-q4_K_M (7.2 GB)
**Problem:**
- Lädt 7 GB Modell in RAM (kein GPU)
- Wird durch hoerer.py/dialog.py angetriggert (Vision-Input erkannt)
- keep_alive hält Modell im Speicher
- Zusammen mit themen-cluster + muster = > 31 GB RAM → OOM

### Verstärker: git status RAM

**.git Größe:** 16 GB (22 Packs, 3.82 GiB loose objects, 9.74 GiB pack)
**Untracked Root-Verzeichnisse:** NICHT in .gitignore:
  - `geni_gedaechtnis/` — 42 GB, 9.875.388+ JSON-Dateien
  - `werkraum_node_modules/` — 319 MB
  - `werkraum_venv/`, `werkraum_venv2/`, `venv/` — ~220 MB
  - `graphify-out/` — 460 MB
  - `.cache/`, `.npm/`, `.bun/` — 5.4 GB
**Folge:** `git status` kostet 1.7 GB RAM und hohe CPU

---

## Durchgeführte Stabilisierung

### Gestoppt (reversibel via systemctl start):
1. `systemctl stop geni-muster.service` — bestätigt OOM-Täter
2. `systemctl stop geni-muster.timer` — verhindert Neustart
3. `systemctl stop ollama` — 7 GB Modell entladen

### Nicht angefasst:
- nginx (active, Port 80/443)
- welt-api (active, Port 8030)  
- welt-bruecke (active)
- postgresql
- alle codewesen_agent/reaktion Prozesse
- hoerer.py, dialog.py (klein, keine akute Gefahr)

### Hinweis zu flextrawurst.service:
- `flextrawurst` unit: inactive — aber Port 8787 läuft via
  `node --experimental-strip-types scripts/serve_process_camera_preview.ts` (PID 834)
- Öffentliche Seite ist erreichbar

---

## Zustand nach Stabilisierung (~20:35)

**RAM:** 6.7 GiB used (war 15 GiB) — 8+ GiB freigegeben
**Swap:** 3.0 GiB used (war 7.2 GiB, fast voll)
**Available:** 24 GiB

**Ports:** 22, 80, 443, 8787, 8030 — alle aktiv

---

## Offene Risiken

1. **themen-cluster.service** läuft noch — nächster Tick in < 5 min
   Status: currently 348 KB, aber CROSS JOIN wird wieder teuer
   → Dringend: MemoryMax oder Query-Fix

2. **geni_gedaechtnis fehlt in .gitignore** → jeder git-Aufruf kostet 1.7 GB RAM

3. **geni-muster.service** timer gestoppt aber service enabled
   → Neustart nach Reboot wenn nicht disabled

4. **themen-cluster.service** hat kein MemoryMax
   → Kann wieder auf 25 GB wachsen

---

## Empfohlene nächste Schritte (Phase 5)

Siehe Schutzkonfiguration im Abschnitt unten.
