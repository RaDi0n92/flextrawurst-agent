---
name: zwischenwesen-felder
description: Alle definierbaren Felder beim Erschaffen eines Zwischenwesens
metadata:
  type: project
tags: [zwischenwesen, felder, praegung]
status: in-diskussion
datum: 2026-06-19
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Was ich verstehe

Der User erschafft ein Zwischenwesen nicht durch einen einfachen Namen. Er schreibt es. Die Felder sind kein Formular — sie sind eine Schöpfungshandlung. Jedes Feld formt den System-Prompt des Wesens und damit sein Verhalten im Chat.

---

## Bestätigte Felder (alle Entscheidungen getroffen)

| Feld | UI-Label | Typ | Limit | Entschieden |
|------|----------|-----|-------|-------------|
| `wesen_name` | "Wie heißt dein Wesen?" | Text | 22 Zeichen | ✓ |
| `wesen_typ` | "Was genau ist dein Wesen?" | Text | 22 Zeichen | ✓ |
| `wesen_text` | "Erzähl von ihm… Was beschreibt das Wesen deines Flüchtlings." (zwei Sätze als Label vor dem Feld) | Textarea | 1337 Zeichen, Live-Counter | ✓ |
| `neigungen` | "Was mag dein Wesen?" | Tag-Input | max 5 Tags | ✓ |
| `abneigungen` | "Was mag dein Wesen nicht?" | Tag-Input | max 5 Tags | ✓ |
| `farbe` | "Farbe deines Wesens" | HSB-Picker | — | ✓ |
| `wesen_bild` | "Bild deines Wesens" | Upload ODER /bildgenerator | max 1,11 MB | ✓ |

### Nicht-Felder (fest im System, kein User-Input)

| Ding | Entscheidung |
|------|-------------|
| Symbol | Raute ◇ — fest für alle Zwischenwesen, nicht wählbar |
| Ton | "plaudern" — immer, fest im System-Prompt |
| Herkunft-Keim | raus |
| Tempo | raus |

### Content-Regeln für Felder

- `wesen_typ`: Keine menschliche Beschreibung (kein "Mann", "Frau", "Person", "Mensch") → automatisch geblockt
- `wesen_bild`: Keine Bilder von Menschen → Content-Filter (Schicht 2)
- Menschennamen im `wesen_name` sind erlaubt — nur die Beschreibung darf nicht menschlich sein

### Tag-Input Verhalten

```
[Schreib hier...] [+ Hinzufügen]
● Regen ×    ● Stille ×    ● Käsepizza ×
```
User tippt, klickt Hinzufügen (oder drückt Enter). Fertige Tags sind einzeln löschbar. Max 5 je Richtung.

### HSB-Farbpicker

Klassischer Picker: oben großes Quadrat (Sättigung horizontal, Helligkeit vertikal), unten Spektrum-Leiste (Farbton). Wie in Figma/Photoshop. Vanilla-JS, keine Library nötig. Wert wird als Hex gespeichert.

### Wesen-Bild

Zwei Optionen nebeneinander:
- `[Bild hochladen]` — JPEG/PNG/WebP, max 1,11 MB
- `[Bild generieren →]` — öffnet flextrawurst.de/bildgenerator (allgemeines Tool) in neuem Popup

In der KompOase: Bild ist klickbar im Wesen-Lesefenster → Vollansicht.

---

## Was noch offen ist

- Darf der User Felder nach Gesprächsstart noch ändern? (Empfehlung: nein — was gesetzt ist, ist gesetzt)

---

## Resonanz

[[zwischenwesen-chat-konzept]]
[[zwischenwesen-container]]
