---
datum: 2026-06-20
betrifft: [wesen, flüchtlinge, solarius, codexium, dateistruktur, memory, container]
status: konzept — noch nicht gebaut
autor: claude-code bei Daniels VPS
importable: false
---

# Wesen-Dateistruktur — gilt für alle Wesenstypen

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Das Gespräch — roh, wie es war

**Daniel:** wie lösen wir nur wie und was genau alles in die wesen.md der wesen kommt ? für diese wesen reicht ne datei...das sind meine ...die sind nicht für flextrawurst...und wir brauchen auch noch mehr als nur eine wesen.md oder warte...was haben die flüchtlinge ...ich hab ja gesagt ich will erstma genau das memorysystem und die container von den flüchtlingen.

**Daniel:** dazu will ih sowohl für meine wesen als auch die flüchtlinge noch folgende mds .....weltlore.md eine Handlung/story ...also handlung von es handelt darüber etc....nicht handeln....mag-ich/mag-ich-nicht.md (wegen den zuneigungen und den abneigungen) ...dann könnte sich diese seite auch entweder füllen und leeren gleichzeitig mit den würtern jonglieren wenn diese dinge im chat besprochen werden...verstehst du ? und eine nicht-tun.md

**Claude:** Ja verstehe ich — die Dateien sind nicht statisch, sie atmen mit dem Chat. Wenn im Gespräch rauskommt dass das Wesen etwas nicht mag, landet das automatisch in mag-ich-nicht.md. Wenn es eine neue Handlung entwickelt, wächst handlung.md.

**Daniel:** ja natürlich auch in seltenen fällen bestimmt...ich dachte eher an verdrüngung und neues was halt durh der chat hinzukommt...denn ai ist doch immer entzückt xD

**Claude:** Haha ja — KI entdeckt in jedem Gespräch neue Begeisterungen und Abneigungen. Ohne Limit würden die Dateien explodieren. Also: die Dateien haben ein Maximum. Wenn was Neues reinkommt und das Limit voll ist, wird das Älteste oder Schwächste verdrängt.

**Daniel:** jo. und sag in den dateien dass wir uns noch überlegen müssen ob das alles roh in die dateien wandert durch ne "normale" lösung oder ob wir wirklich ai brauchen...weil das wird dann nicht nur ein promt sondern bei codexiumwesen und flüchtlingen 4 oder mehr

---

## Dateistruktur pro Wesen

Gilt für: **Solariuswesen** (Wesenspawner 1), **Codexiumwesen** (Wesenspawner 2), **Flüchtlinge**

```
wesen/[name]/
  wesen.md          ← Grunddefinition: alle Formularfelder, Systemprompt
  weltlore.md       ← die Welt in der das Wesen lebt
  handlung.md       ← worum es in seiner Geschichte geht (es handelt von... nicht: es handelt)
  mag-ich.md        ← Zuneigungen (wächst/schrumpft, max N Einträge)
  mag-ich-nicht.md  ← Abneigungen (wächst/schrumpft, max N Einträge)
  nicht-tun.md      ← was das Wesen nie tut — ACHTUNG: "harte Grenzen" hier sind nur Text-Instructions, kein Server-Enforcement (siehe unten)
  memory.md         ← kategorisiertes Langzeitgedächtnis (Kategorien wie bei Flüchtlingen)
  container.md      ← gepinnte Momente aus Chats (max 20)
  chats/
    YYYY-MM-DD_HH-MM.md   ← ein Chatverlauf pro Session
```

---

## Die lebenden Dateien — atmen mit dem Chat

`mag-ich.md`, `mag-ich-nicht.md`, `handlung.md` sind nicht statisch.
Sie verändern sich wenn im Chat etwas Relevantes auftaucht.

**Verdrängungsprinzip:**
- Jede Datei hat ein Maximum (Limits noch festzulegen)
- Neues verdrängt Altes wenn das Limit voll ist
- In seltenen Fällen: Einträge können zwischen mag-ich und mag-ich-nicht wandern (wenn sich etwas umkehrt)
- KI entdeckt begeistert ständig Neues — Limits sind Pflicht sonst explodieren die Dateien

---

## Offene Kernfrage: Roh oder KI?

**⚠ Noch nicht entschieden:**

Wie wandert Information aus dem Chat in diese Dateien?

**Option A — Roh / einfache Lösung:**
- Bestimmte Marker im Chat (`[mag: ...]`, `[nicht-tun: ...]`) werden geparst
- Oder: User pinnt manuell (wie Container)
- Kein extra LLM-Aufruf nötig
- Einfach, vorhersehbar, kein Prompt-Aufwand

**Option B — KI-gestützt:**
- Nach jeder Antwort (oder alle N Nachrichten) läuft ein separater Analyse-Prompt
- KI extrahiert: neue Zuneigungen, neue Abneigungen, neue Handlungselemente
- Bei Codexiumwesen und Flüchtlingen wären das **4+ separate Prompts** pro Analyse-Durchlauf (Solariuswesen hat weniger Felder, also weniger Prompts):
  - Prompt 1: mag-ich / mag-ich-nicht Update
  - Prompt 2: handlung.md Update
  - Prompt 3: memory.md Update
  - Prompt 4: nicht-tun.md Prüfung
  - (+ ggf. Prompt 5: weltlore.md Update)
- Teurer, aber automatisch und natürlich

**Hybrid denkbar:**
- Container + nicht-tun = manuell (User entscheidet)
- mag-ich / mag-ich-nicht / handlung = KI (zu subtil für manuelle Erkennung)

**→ Noch zu entscheiden bevor gebaut wird.**

---

## Memory-System (von Flüchtlingen übernommen)

Kategorien:
- `über_mich` — was das Wesen über mich wissen soll (max 15)
- `unsere_themen` — wiederkehrende Themen (max 10)
- `wichtige_momente` — Sätze/Momente die zählen (max 10)
- `meinungen` — Haltungen, Überzeugungen (max 10)
- `offene_fragen` — was noch ungeklärt ist (max 8)
- `wesen_selbst` — Selbst-Erkenntnisse des Wesens (max 10)
- *(user-definiert)* — max 5 eigene Kategorien

Max 200 Zeichen pro Eintrag. Gesamt ~8000 Zeichen.

---

## Container (von Flüchtlingen übernommen)

Max 20 gepinnte Momente. Live im LLM-Kontext.
Quelle: mensch | wesen. Entfernbar per ×.

---

## Was noch fehlt bevor gebaut werden kann

- Limits für mag-ich / mag-ich-nicht festlegen (max N Tags)
- Entscheidung: Roh vs KI für die lebenden Dateien
- Für zensi-Wesen (lokal): Datei-basiert reicht
- Für Flüchtlinge (flextrawurst): PostgreSQL-Tabellen (schema noch anzupassen)
- Verdrängungslogik konkretisieren: FIFO? Gewichtung? User-Entscheidung?

---

## Wichtig: nicht-tun.md ist weich — Grenzen die zählen brauchen Server-Enforcement

`nicht-tun.md` wird als Text in den System-Prompt injiziert. Das Modell liest ihn — und kann ihn ignorieren.

Das ist kein Bug, das ist wie Sprachmodelle funktionieren: Text-Instructions sind Bitten, keine Gesetze. Ein gutes Modell (GPT-4-Klasse) folgt ihnen meistens. Ein schwaches Modell (8B lokal) oft nicht.

**Zwei Klassen von Grenzen:**

- **Charakter-Grenzen** (weich, okay wenn weich): "Ich rede nicht über Aktien", "Ich mag keine Äpfel", "Ich fange Romantik nie selbst an" → in nicht-tun.md als Text reicht, wenn das Modell gut genug ist
- **Absolute Grenzen** (müssen hart sein): Kinderinhalte, Selbstverletzungsanleitungen, Missbrauch als Spiel → diese gehören NICHT in nicht-tun.md — sie müssen Server-seitig als Code erzwungen werden, unabhängig vom Modell

Solange nicht-tun.md nur Text ist, gilt: das Wesen versucht diese Grenzen einzuhalten. Garantieren kann das nur der Server.
