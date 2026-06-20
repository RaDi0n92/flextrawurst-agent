---
name: bildgenerator
description: Allgemeiner Bildgenerator für flextrawurst — lokal (sd.cpp), erreichbar über flextrawurst.de/bildgenerator, nutzbar für alles
metadata:
  type: project
tags: [bildgenerator, sd-cpp, nginx, tool]
status: in-planung
datum: 2026-06-19
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Was ich verstehe

Ein allgemeines Bildgenerierungs-Tool für flextrawurst. Kein externes API, kein Geld. sd.cpp läuft lokal auf Port 8042 (bereits installiert). Erreichbar über nginx-Route /bildgenerator auf flextrawurst.de — für jeden, nicht nur im Kontext von Zwischenwesen. Kann von anderen Teilen der Plattform verlinkt werden (z.B. aus dem Erschaffungs-Formular für Flüchtlinge als optionaler Schritt für das Wesen-Bild).

---

## Technischer Stand

- sd.cpp installiert, läuft auf Port 8042
- Getestet: 512×512, 8 Steps → 121 Sekunden
- Getestet: 256×256, 4 Steps → ~15 Sekunden
- RAM-Verbrauch: ~2GB — andere Services laufen durch

## nginx-Routing

```nginx
location /bildgenerator {
    proxy_pass http://localhost:8042;
    proxy_read_timeout 3600s;   ← große Bilder brauchen lange
}
```

---

## Auflösungen mit Zeitschätzungen (CPU, 4 Steps)

| Auflösung | Pixel | Geschätzte Zeit |
|-----------|-------|-----------------|
| 512×512 | 262K | ~1 Min |
| 640×480 | 307K | ~1,5 Min |
| 666×666 | 443K | ~2 Min |
| 768×576 | 442K | ~2 Min |
| 768×768 | 589K | ~2,5 Min |
| 777×777 | 603K | ~3 Min |
| 768×1024 | 786K | ~3,5 Min |
| 888×888 | 788K | ~3,5 Min |
| 960×540 | 518K | ~2,5 Min |
| 1024×768 | 786K | ~3,5 Min |
| 1111×1111 | 1,23M | ~5 Min |
| 1280×960 | 1,22M | ~5 Min |
| 1336×768 | 1,02M | ~4,5 Min |
| 1440×900 | 1,29M | ~6 Min |
| 1440×1080 | 1,55M | ~7 Min |
| 1600×900 | 1,44M | ~6,5 Min |
| 1600×1200 | 1,92M | ~8,5 Min |
| 1600×1600 | 2,56M | ~11 Min |
| 1920×1080 | 2,07M | ~9 Min |

Zeitschätzungen sind Richtwerte (lineare Hochrechnung vom getesteten Wert). Im UI immer mit ~-Prefix anzeigen: "~5 Minuten".

---

## Stile (Default + 15)

| ID | Label | Prompt-Suffix |
|----|-------|---------------|
| `default` | Standard (Prompt entscheidet) | — |
| `skizze` | Skizzenhaft | pencil sketch, rough lines, monochrome |
| `bilderbuch` | Bilderbuch | children's book illustration, colorful, soft |
| `realistisch` | Realistisch | photorealistic, detailed, sharp |
| `impressionismus` | Impressionismus | impressionist painting, visible brushstrokes, soft light, Monet style |
| `surrealismus` | Surrealismus | surrealist, dreamlike, paradoxical, Salvador Dali style |
| `aquarell` | Aquarell | watercolor, soft edges, flowing colors, organic |
| `anime` | Anime / Manga | anime style, expressive eyes, clean lines, vibrant |
| `cyberpunk` | Cyberpunk | cyberpunk, neon lights, dark dystopian, futuristic |
| `pixel` | Pixel Art | 8-bit pixel art, retro game style, limited palette |
| `pixar` | 3D Animationsfilm | Pixar style, warm lighting, soft textures, expressive |
| `popart` | Pop Art | pop art, bold primary colors, Ben-Day dots, Andy Warhol style |
| `ghibli` | Studio Ghibli | Studio Ghibli style, painterly, lush nature, dreamy |
| `flat` | Flat Design | minimalist flat design, clean shapes, no gradients |
| `papercraft` | Papercraft | papercraft, layered paper, 3D cut paper illusion |

---

## Status-Anzeige im UI

Der User muss immer sehen ob der Generator läuft oder abgestürzt ist.

Drei Zustände:
- **Läuft** (grün pulsierend): `POST /generate` wurde abgeschickt, Antwort ausstehend — zeigt Fortschrittsleiste mit Zeitschätzung
- **Fertig**: Bild erscheint, Download-Button + "In Wesen übernehmen"-Button
- **Fehler / Timeout** (rot): "Generator antwortet nicht" — Retry-Button + Hinweis: "vielleicht ist er kurz überlastet, bitte warte 30 Sekunden"

Fortschrittsanzeige: einfache animierte Leiste + Text "~X Minuten verbleibend" (berechnet aus Auflösung beim Start).

---

## UI-Konzept /bildgenerator

Eigene Seite, erreichbar von flextrawurst.de/bildgenerator und als Popup aus dem Erschaffungs-Formular:

```
┌─────────────────────────────────────────────┐
│  ◇ BILDGENERATOR                            │
│─────────────────────────────────────────────│
│  [Beschreibe dein Wesen-Bild...            ]│
│                                             │
│  Auflösung: [512×512 (~1 Min)          ▾]  │
│  Stil:      [Standard (Prompt entscheidet) ▾]│
│                                             │
│  [ Bild generieren ]                        │
│                                             │
│  ████████████░░░░░░░░  ~3 Min verbleibend  │  ← während Generierung
│                                             │
│  [generiertes Bild erscheint hier]         │
│  [ In Wesen übernehmen ] [ Neu generieren ]│
└─────────────────────────────────────────────┘
```

---

## Was noch offen ist

- Kann ein User ein fertig generiertes Bild direkt in der Plattform speichern / herunterladen?
- Soll es eine Galerie der zuletzt generierten Bilder geben (temporär, nur für den eigenen User)?
- Maximale gleichzeitige Generierungen? (Empfehlung: 1 Queue — sd.cpp ist single-threaded)
- Wird das Bild temporär gespeichert oder direkt beim Klick auf "Übernehmen" weitergeschickt?
- Welche anderen Stellen in flextrawurst werden /bildgenerator verlinken?

---

## Resonanz

[[flextrawurst-vision]]
