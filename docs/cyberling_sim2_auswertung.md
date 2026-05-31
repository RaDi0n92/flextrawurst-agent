# Cyberling Simulation 2 — Auswertung

**Datum:** 2026-05-31
**Status:** Analyse, KEIN Produktivcode geändert
**Quelle:** `welt/cyberling_balancing/output_sim2/`

---

## Drei Profile im Vergleich

### LEICHT — sanftes Profil

| Szenario | H | D | E | G | Lebt? |
|:---------|--:|--:|--:|--:|:------|
| Perfekt (2h) | 79.6 | 74.2 | 100 | 100 | ✓ |
| Normal (4h) | 84.6 | 79.2 | 100 | 100 | ✓ |
| Verspätet (6h) | 84.6 | 39.2 | 88 | 100 | ✓ |
| 12h Vernachlässigt | 69.6 | 39.2 | 100 | 100 | ✓ |
| 24h Vernachlässigt | 39.6 | 0 | 55 | 100 | ✓ (hungrig) |
| 48h Vernachlässigt | 0 | 0 | 0 | 67 | ✓ (erschöpft) |

**Befund:** Nie tödlich. Kein echter Druck. Für Onboarding/Tests geeignet.

---

### MITTEL — empfohlenes Produktivprofil

| Szenario | H | D | E | G | Lebt? |
|:---------|--:|--:|--:|--:|:------|
| Perfekt (2h) | 90.0 | 27.0 | 25.9 | 97.3 | ✓ |
| Normal (4h) | 24.0 | 27.0 | 0 | 56.0 | ✓ (erschöpft) |
| Verspätet (6h) | 24.0 | 27.0 | 0 | 51.3 | ✓ (erschöpft) |
| 12h Vernachlässigt | 0 | 0 | 29.3 | 99.3 | ✓ (hungrig/durstig) |
| 24h Vernachlässigt | 0 | 0 | 0 | 51.3 | ✓ (erschöpft) |
| **48h Vernachlässigt** | **0** | **0** | **0** | **0** | **✗ TOT** |

**Befund:**
- Energie fällt sichtbar, nicht dekorativ
- Normale Pflege (4h) reicht nicht aus — Energie geht auf 0
- 48h-Tod: klar, nicht willkürlich
- Recovery nach Rettung modelliert (langsam, dann normal)
- **Empfehlung: MITTEL als Default**

---

### HART — kein Pardon

| Szenario | H | D | E | G | Lebt? |
|:---------|--:|--:|--:|--:|:------|
| Perfekt (2h) | 64.0 | 19.0 | 0 | 62.0 | ✓ (erschöpft) |
| Normal (4h) | 20.0 | 19.0 | 0 | 54.0 | ✓ (erschöpft) |
| **48h Vernachlässigt** | **0** | **0** | **0** | **0** | **✗ TOT** |

**Befund:** Zu hart für erste Phase. Energie sinkt bei perfekter Pflege auf 0.

---

## Produktionsdaemon — aktueller Stand

Der `cyberling-daemon.service` läuft seit einer Woche mit diesen Parametern:

```python
DURST_PRO_H    = 0.18   # = 18/h in 100-Skala
HUNGER_PRO_H   = 0.12   # = 12/h in 100-Skala
KASKADE_SCHWELLE = 0.4  # = 40 in 100-Skala
ENERGIE_PRO_H_KASKADE = 0.08  # = 8/h
```

**Vergleich mit MITTEL:**

| Parameter | Produktion | MITTEL-Sim2 | Drift? |
|:----------|:-----------|:------------|:-------|
| durst_pro_h | 18 | 18 | ✓ identisch |
| hunger_pro_h | 12 | 12 | ✓ identisch |
| energie_kaskade | 8 | 8 | ✓ identisch |
| kaskade_schwelle | 40 | 40 | ✓ identisch |
| energie_regen | **fehlt** | 0.5–1.5/h | ⚠ fehlt |
| energie_basisrauschen | **fehlt** | 2.0 | ⚠ fehlt |

---

## Kritische Lücke: Energie-Recovery fehlt in Produktion

Das MITTEL-Profil modelliert langsame Energie-Erholung nach kritischer Rettung.
Im Produktionsdaemon fehlt diese Recovery-Logik vollständig.

**Was passiert aktuell:**
Wenn ein Cyberling gerettet wird (Hunger/Durst aufgefüllt),
steigt die Energie nicht von selbst wieder.
Sie bleibt auf dem Tiefstwert, bis die nächste externe Pflegeaktion erfolgt.

**Was gewünscht wäre (nach MITTEL):**
Nach Rettung erholt sich Energie langsam (+0.5/h für 4h, dann +1.5/h).

**Entscheidung:** Diese Recovery ist **noch nicht gebaut**. Aktivierung braucht Daniel-Auftrag.

---

## Empfehlung: MITTEL als Default, mit Recovery-Patch

Wenn Daniel MITTEL freigibt, braucht der Daemon einen Patch:
1. `ENERGIE_REGEN_NACH_KRIT_H = 0.005` (0.5/h = 0.005 * 100 pro h, in 0-1-Skala)
2. Zustand `in_erholung` nach Rettung tracken
3. Nach 4h Erholung: `ENERGIE_REGEN_NORMAL_H = 0.015` (1.5/h)

**Das ist nicht urgent.** Die Kernparameter stimmen.

---

## Was das bedeutet für Einzugsreife

- Cyberling-Daemon läuft mit faktisch MITTEL-Parametern ✓
- Kein Drift bei Kern-Decay ✓
- Energie-Recovery fehlt — kleines Gap, kein Blocker
- 48h-Tod funktioniert (wenn Produktion gleich wie Sim2 verhält)
- Kein produktiver Code geändert in dieser Session

---

*Diese Auswertung ist Doku. Keine Produktivänderung.*
