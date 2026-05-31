# Cyberling Simulation 2 — Vergleichsbericht
**KEIN PRODUKTIVCODE — nur Simulation**
Drei Profile: Leicht / Mittel / Hart — 6 Szenarien

| Profil | Szenario | Stunden | H | D | E | G | Status | Lebt? |
|:-------|:---------|--------:|--:|--:|--:|--:|:-------|:------|
| LEICHT (sanftes Profil) | Perfekte Pflege (alle 2h) | 24 | 79.6 | 74.2 | 100.0 | 100.0 | lebendig | ✓ |
| LEICHT (sanftes Profil) | Normale Pflege (alle 4h) | 24 | 84.6 | 79.2 | 100.0 | 100.0 | lebendig | ✓ |
| LEICHT (sanftes Profil) | Leicht verspätet (alle 6h) | 24 | 84.6 | 39.2 | 88.1 | 100.0 | lebendig | ✓ |
| LEICHT (sanftes Profil) | Vernachlässigt 12h ohne Pflege | 12 | 69.6 | 39.2 | 100.0 | 100.0 | lebendig | ✓ |
| LEICHT (sanftes Profil) | Vernachlässigt 24h | 24 | 39.6 | 0.0 | 55.3 | 100.0 | hungrig/durstig | ✓ |
| LEICHT (sanftes Profil) | Vernachlässigt 48h (Härtetest) | 48 | 0.0 | 0.0 | 0.0 | 67.0 | erschöpft | ✓ |
| MITTEL (aktuell verbessert) | Perfekte Pflege (alle 2h) | 24 | 90.0 | 27.0 | 25.9 | 97.3 | lebendig | ✓ |
| MITTEL (aktuell verbessert) | Normale Pflege (alle 4h) | 24 | 24.0 | 27.0 | 0.0 | 56.0 | erschöpft | ✓ |
| MITTEL (aktuell verbessert) | Leicht verspätet (alle 6h) | 24 | 24.0 | 27.0 | 0.0 | 51.3 | erschöpft | ✓ |
| MITTEL (aktuell verbessert) | Vernachlässigt 12h ohne Pflege | 12 | 0.0 | 0.0 | 29.3 | 99.3 | hungrig/durstig | ✓ |
| MITTEL (aktuell verbessert) | Vernachlässigt 24h | 24 | 0.0 | 0.0 | 0.0 | 51.3 | erschöpft | ✓ |
| MITTEL (aktuell verbessert) | Vernachlässigt 48h (Härtetest) | 48 | 0 | 0 | 0 | 0 | TOT | ✗ |
| HART (kein Pardon) | Perfekte Pflege (alle 2h) | 24 | 64.0 | 19.0 | 0.0 | 62.0 | erschöpft | ✓ |
| HART (kein Pardon) | Normale Pflege (alle 4h) | 24 | 20.0 | 19.0 | 0.0 | 54.0 | erschöpft | ✓ |
| HART (kein Pardon) | Leicht verspätet (alle 6h) | 24 | 20.0 | 19.0 | 0.0 | 52.5 | erschöpft | ✓ |
| HART (kein Pardon) | Vernachlässigt 12h ohne Pflege | 12 | 0.0 | 0.0 | 0.0 | 88.5 | erschöpft | ✓ |
| HART (kein Pardon) | Vernachlässigt 24h | 24 | 0.0 | 0.0 | 0.0 | 52.5 | erschöpft | ✓ |
| HART (kein Pardon) | Vernachlässigt 48h (Härtetest) | 48 | 0 | 0 | 0 | 0 | TOT | ✗ |

## Empfehlung

**Mittel** als Default-Profil empfohlen:
- Energie-Abfall sichtbar, nicht dekorativ (1.0/h normal)
- Energie-Regen nach kritischer Rettung langsam (0.5/h), danach 1.5/h
- Energie schwankt leicht (Basisrauschen 2.0)
- Tod möglich, aber nur bei echter 48h-Vernachlässigung
- Aktionen erst ab Schwelle (80%) + Cooldown (1-1.5h) + Cap (88%)

**Leicht** für Tests und Onboarding.

**Hart** für die, die es ernst nehmen.

**Aktivierung:** Nicht automatisch. Profile müssen explizit in cyberling_daemon.py eingebaut werden.
