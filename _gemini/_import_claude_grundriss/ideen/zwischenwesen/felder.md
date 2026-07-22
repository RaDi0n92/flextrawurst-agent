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

## Bestätigte Felder — Codexium-Parität (angepasst 2026-06-23)

Die Flüchtlinge bekommen dieselbe Feldstruktur wie Codexiumwesen.

| Feld | UI-Label | Typ | Limit | Tokens (voll) |
|------|----------|-----|-------|--------------|
| `wesen_name` | "Name" | Text | 22Z (optional) | ~6T |
| `gespraechseinstieg` | "Gesprächseinstieg" | Textarea | 222Z | ~63T |
| `was_bist_du` | "Was bist du?" | Text | 200Z | ~57T |
| `neigungen` | "Was mag dein Wesen?" | Tag-Input | max 5 Tags | ~21T |
| `abneigungen` | "Was mag dein Wesen nicht?" | Tag-Input | max 5 Tags | ~21T |
| `beschreibung` | "Beschreibung" | Textarea | 444Z | ~127T |
| `wesendefinition` | "Wesendefinition" | Textarea | 1337Z | ~382T |
| `weltlore` | "Weltlore" | Textarea | 1337Z | ~382T |
| `farbe` | "Farbe deines Wesens" | HSB-Picker | — | 0T |
| `wesen_bild` | "Bild deines Wesens" | Upload ODER /bildgenerator | max 1,11 MB | 0T |
| Boilerplate/Framing | — | — | — | ~150T |
| **GESAMT System-Prompt** | | | **3712Z (wenn Name leer: +Selbstbenennungs-Instruktion ~20T)** | **~1215T** |

**Name ist optional:** Leer lassen → das Wesen gibt sich in der ersten Antwort selbst einen Namen, basierend auf Wesendefinition und allen anderen Feldern. Intern wird ein Platzhalter-Schlüssel generiert bis das Wesen einen echten Namen wählt.

### Token-Budget (alle Felder vollständig ausgefüllt)

```
SESSION-START (leer):
  System-Prompt (alle Felder voll):   ~1215T
  grenzen.md (fest, kein Toggle):       ~50T
  Wesen-Geschichte (bisherige Kapitel): ~300T
  Kern-Memory (nur Gewicht 3):          ~400T
  Container (session-lokal, leer):         0T
  ─────────────────────────────────────────
  BASIS:                               ~1965T  → 24% des Fensters ✓

SESSION-ENDE (voll geladen):
  System-Prompt + grenzen.md:        ~1265T
  Wesen-Geschichte:                    ~300T
  Memory gesamt (3000Z):               ~857T
  Container (max 10 Einträge):         ~400T
  Letzte ~20 Nachrichten:            ~2000T
  Antwort-Puffer:                    ~1500T
  ─────────────────────────────────────────
  GESAMT:                            ~6322T  ✓ unter 8192T

75%-TRIGGER: bei ~4644T Input (Basis 1965T + Container 400T = 2365T gebunden)
  → Raum für Nachrichten: ~2279T → ~23 Exchanges pro Session
```

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

## Entscheidung nachgetragen (2026-07-05, aus dem Codexium2-Bau — Stand am selben Tag korrigiert)

Die "Codexium-Parität" oben bezieht sich auf den Stand vor dem 05.07. Codexium(2) hat sich seitdem geändert — aber in einem Punkt noch am selben Tag wieder zurückgenommen, deshalb hier der aktuelle Stand statt des ursprünglichen Zwischenstands:

1. **`[Label]`-Kopfzeilen zwischen den Feldern bleiben** (Gesprächseinstieg/Was-bist-du/Neigungen/Beschreibung/Wesendefinition/Weltlore als `[Wesendefinition]\n...`, `[Weltlore]\n...` usw.) — nur `wesen.md`/die Kernidentität bleibt ohne eigenes Label. Ein erster Versuch OHNE Kopfzeilen (roh hintereinander, mit der Begründung: viele separat gelabelte, abstrakte Felder ziehen das Modell in einen dokumentierenden/analysierenden Ton) wurde noch am selben Tag von Daniel wieder rückgängig gemacht — er will die Struktur behalten und verlässt sich stattdessen bewusst auf Punkt 2.
2. **Expliziter Formverbots-Absatz im Rollenspiel-Systemprompt** (nicht in den einzelnen Feldern, sondern in der gemeinsamen Präambel davor): keine Kopfzeilen, keine Aufzählungen, kein Fettdruck-Gliedern, keine Meta-Analyse-Sprache ("Das ist ein klassisches Beispiel für..."). Das ist der Teil, der tatsächlich als Hebel gegen den beobachteten Effekt gedacht ist — reine Charakterbeschreibung allein reicht nicht, es braucht eine harte Form-Regel für die *Antwort*, unabhängig davon ob die *Eingabefelder* selbst Kopfzeilen haben.
3. **Zusätzlich ein kurzer Rahmensatz direkt vor den Feldern**, der erklärt wie sie wirken sollen: nicht als Zusatzinfo über den Charakter, sondern als unmittelbar prägender Teil von ihm selbst.

Für Flüchtlinge heißt das konkret: Kopfzeilen pro Feld ruhig übernehmen (das war nie das eigentliche Problem), aber Punkt 2 und 3 nicht vergessen — die tragen den größten Teil der Wirkung. Details: `werkraum/_wesen_preamble.md` (aktive Fassung) und die beiden Nachträge "Rollenspiel-Systemprompt" in `_claude/ideen/codexium2_solarius2/provenienz_logging.md`.

---

## Resonanz

[[zwischenwesen-chat-konzept]]
[[zwischenwesen-container]]
