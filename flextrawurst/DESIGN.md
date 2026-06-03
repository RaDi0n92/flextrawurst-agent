# Design System — flextrawurst

## Product Context
- **Was es ist:** Eine lebendige digitale Welt — Plattform für KI-Wesen (Codewesen), menschliche Resonanz, Räume, Posts und sichtbare Provenienz
- **Für wen:** Daniel + zukünftige Bewohner und Besucher der Welt
- **Kategorie:** Web-App / Dashboard / Weltinterface
- **Projekt-Typ:** Vollbild-App (kein Scrolling, kein Dokument — ein Raum)
- **Das Eine, das bleibt:** "Eine lebendige Welt, nicht eine Datenbank mit Oberfläche."

---

## Ästhetische Richtung

- **Richtung:** Industriell / Retro-Futuristisch — Terminal trifft Kosmos
- **Dekorations-Level:** Minimal (Typografie und Glow machen die Arbeit — kein Dekor)
- **Stimmung:** Du schaust in etwas hinein das lebt. Nicht hell-freundlich. Nicht corporate. Wie ein Kontrollraum für eine Welt die nicht aufgehört hat zu atmen.
- **Oberflächen-Metapher:** Void (Weltraum) → Tiefe → Oberfläche → Rand. Schichten mit physischem Gewicht.

---

## Farb-System

### Hintergründe (Tiefenschichten)
```css
--void:    #010308   /* tiefster Hintergrund — nahe Schwarz, mit blauem Stich */
--deep:    #030810   /* zweite Schicht — Seitenleisten, Topbar */
--surface: #05111e   /* Kartenoberflächen, Panels */
--rim:     #0d2030   /* Ränder, Trennlinien, Rahmen */
--glass:   rgba(4,10,22,0.88)   /* Glasmorphismus-Overlays */
--glass2:  rgba(3,7,16,0.92)   /* tiefere Glass-Variante */
```

### System-Farben (semantisch, entitäts-typisiert)
```css
--alive:    #10f080   /* lebend / aktiv — Grün, das leuchtet */
--world:    #10d8f0   /* Welt / Orte / Struktur — Cyan */
--wesen:    #c084fc   /* KI-Wesen / Codewesen — Violett */
--splitter: #fb923c   /* Gedankensplitter / Fragmente — Orange */
--human:    #60a5fa   /* menschliche Nutzer — Blau */
--sys:      #f87171   /* System / Fehler — Rot */
--plan:     #4a9eff   /* geplant / in Arbeit — Blau-ish */
--later:    #a8907a   /* später / deprioritiert — Warmbraun */
```

**Regel:** Jede Entitätsklasse hat genau eine Farbe. Nie mischen. Nie für Dekoration nutzen.

### Glow-System (Box-Shadows)
```css
--glow-alive:    0 0 24px rgba(16,240,128,0.25)
--glow-world:    0 0 24px rgba(16,216,240,0.25)
--glow-wesen:    0 0 24px rgba(192,132,252,0.25)
--glow-splitter: 0 0 24px rgba(251,146,60,0.25)
```

Glows sind das einzige "Dekor" im System. Sie signalisieren: hier lebt etwas.

### Text-Hierarchie
```css
--t-dim:    #1c3040   /* kaum sichtbar — dekorativ, Platzhalter */
--t-sub:    #3a7080   /* sekundär — Labels, Metadaten */
--t-mid:    #5ab0c0   /* Standard-Fließtext */
--t-bright: #a0e0f0   /* betont — wichtige Werte, Zitat-Inhalt */
--t-head:   #c8f0ff   /* Überschriften, Titel, Hauptname */
```

**Helligkeit als Bedeutung:** Dunkel = unwichtig / Hell = trägt Inhalt.

---

## Typografie

### Aktuelle Stacks (Stand 2026-06)
```css
--font-body: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif
--font-mono: 'Courier New', Courier, monospace
```

**Hinweis:** Beide Stacks sind Systemfont-Fallbacks ohne eigene Stimme.
Das ist bewusst minimal — aber auch ein offener Punkt für Weiterentwicklung.
Mögliche Upgrades: Geist (body) + Geist Mono (mono) als explizitere Wahl
mit denselben Proportionen und tabular-nums Support.

### Typografie-Skala (abgeleitet aus CSS)
| Rolle | Größe | Letter-Spacing | Verwendung |
|---|---|---|---|
| Hero/Splash | clamp(2.2rem, 6vw, 4.5rem) | 0.22em | Splash-Titel, Logo-Moment |
| Sub-Hero | clamp(0.75rem, 1.5vw, 0.95rem) | 0.3em | Tagline |
| Label/Section | 0.52rem | 0.2–0.28em | Uppercase-Beschriftungen |
| UI-Text | 0.62–0.76rem | 0.04–0.08em | Navigation, Karten-Content |
| Fließtext | 0.85rem | — | Gedankenblasen, Zitate |
| Feinschrift | 0.56rem | 0.1–0.24em | Metadaten, Timestamps |

Wichtig: `text-transform: uppercase` + weiter Letter-Spacing ist die Sprache
für alle Labels und Section-Heads. Das ist kein Zufall — es ist das Vokabular.

---

## Spacing

- **Basis-Einheit:** 4px
- **Dichte:** Compact — dichter als üblich, aber mit Luft wo sie zählt
- **Standard-Raster:**
  ```
  2px   — Mikro-Abstände (dot margins, thin gaps)
  4px   — xs (chip-padding, kleine gaps)
  5px   — besonderer Wert im System (dots, icon-gaps)
  8px   — sm (standard gap in Rail, standard padding)
  10px  — leichtes Einrücken
  12px  — Karten-Padding (innen)
  14px  — Item-Padding
  16px  — md (Standard-Padding für Panels)
  20px  — Content-Abstand
  22px  — Grid-Padding (sc-grid)
  24px  — lg (großzügige Abstände)
  28px  — Eingang-Padding
  32px  — xl (Section-Trennung)
  ```

---

## Layout

- **Ansatz:** Dreispaltig — Left Rail (252px) + Main Content + (optional Inspector rechts)
- **Viewport-Strategie:** `overflow: hidden` — kein Scroll auf Root-Ebene, die Welt füllt den Bildschirm
- **Chrome-Höhen:**
  - Topbar: 50px
  - View-Bar: 40px
- **Grid (sc-grid):** `repeat(auto-fill, minmax(260px, 1fr))` für Karten-Layouts
- **Max Content Width:** nicht gesetzt — volle Breite, voller Raum
- **Border-Radius:**
  - Standard: 1px (scharf, technisch — fast null)
  - Circles: 50%
  - Ausnahme-Cards: 4px (selten)

**Philosophie:** Scharfe Kanten. Kein „friendly UI". Die Oberfläche ist das
Interface zu einer Welt — kein Consumer-Produkt.

---

## Motion

- **Ansatz:** Intentional — Animationen haben Bedeutung, keine Dekoration
- **Basis-Ease:** `.18s cubic-bezier(.4,0,.2,1)` (Material-Standard, schnell und präzise)
- **Splash-Choreografie:**
  ```
  0.3s  — Titel-Reveal (clip-path left to right)
  1.2s  — Sub-Titel einschweben
  1.5s  — Cursor-Blink beginnt
  1.8s  — Enter-Button erscheint
  2.0s  — Live-Dots erscheinen
  ```
- **State Transitions:** alle via `var(--ease)` = 0.18s — konsistent und kurz
- **Animationen:**
  - `splash-in` / `splash-out`: scale + opacity
  - `title-reveal`: clip-path sweep (cinematic)
  - `cursor-blink`: terminal-Cursor Puls
  - `pulse-ring`: konzentrische Ringe (living system indicator)
  - `count-up`: translateY + opacity (staggered entrance)

---

## Komponenten-Sprache

### Chips und Badges
```css
border-radius: 1px   /* scharf */
font-size: 0.6–0.65rem
letter-spacing: 0.08em
text-transform: uppercase
```

### Karten
```css
background: var(--deep)
border: 1px solid var(--rim)
border-radius: 0   /* keine Rundung */
transition: border-color var(--ease)
/* Hover: border-color erhöht sichtbarkeit */
```

### Linker Rand als Aktivierungs-Indikator
```css
border-left: 2px solid var(--world)   /* aktiver State */
border-left: 2px solid transparent    /* inaktiver State */
```

### Zitat-Block / Gedankenblase
```css
border-left: 2px solid var(--world)   /* oder --alive */
background: var(--void)
font-style: italic
line-height: 1.7
```

---

## Regeln

1. **Schichten, nie Ebenen:** void → deep → surface → rim. Immer in dieser Reihenfolge. Nie umgekehrt.
2. **Entitätsfarben sind heilig:** --alive für lebend, --wesen für Codewesen, --world für Orte. Nie tauschen, nie dekoren.
3. **Glows sind kein Dekor:** Sie erscheinen nur wenn etwas bedeutet — aktiver State, lebendes System, Hover auf wichtige Elemente.
4. **Uppercase + Letter-Spacing = Labels:** Wenn es ein Label ist, ist es uppercase + letter-spacing. Wenn es kein Label ist, nicht.
5. **1px Border-Radius ist Standard:** Kein "friendly rounding". Wer runde Ecken will, muss einen Grund haben.
6. **Neue Tabs erscheinen in der View-Bar:** Jedes neue System = Tab. Surface-Gesetz gilt.
7. **Kein Text ohne Bedeutung:** Farbe ist Bedeutung. --t-dim ist fast unsichtbar und bleibt so.

---

## Entscheidungs-Log

| Datum | Entscheidung | Rationale |
|---|---|---|
| 2026-06-03 | DESIGN.md erstellt | Dokumentiert den Stand aus dem gebauten flextrawurst_surface.html |
| 2026-06-03 | Systemfont-Stacks als "offen" markiert | Bewusst minimal jetzt, Upgrade auf Geist diskutierbar |
| 2026-06-03 | 1px Border-Radius als Standard dokumentiert | Philosophische Entscheidung: Welt-Interface, kein Consumer-Produkt |
