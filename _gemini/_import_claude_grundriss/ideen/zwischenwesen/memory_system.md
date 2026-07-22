---
name: zwischenwesen-memory-system
description: Kategorisiertes Gedächtnis-System — trickst das Kontextfenster aus, macht das Wesen intelligent
metadata:
  type: project
tags: [zwischenwesen, memory, kontext, kategorien, rag]
status: in-diskussion
datum: 2026-06-19
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Was ich verstehe

Ein großes Gedächtnis-Blob wäre eine Katastrophe für das 8192-Token-Fenster. Stattdessen: mehrere kleine Kategorien plus eine wachsende Geschichte. Bei jedem LLM-Aufruf kommen nur die relevanten Teile ins Fenster. Das Wesen wirkt intelligent weil es gezielt erinnert — nicht weil es alles auf einmal trägt.

Das ist manuell kuratiertes RAG ohne Embeddings. Der Mensch ist der Retrieval-Schritt.

Die **Wesen-Geschichte** ist dabei kein Performanz-Kompromiss — sie ist das Gedächtnis wie es echte Erinnerung funktioniert. Das Wesen erinnert sich nicht an jeden Satz, aber es erinnert sich wie sich das Gespräch angefühlt hat. Jede Session hinterlässt ein Kapitel. Die Kapitel zusammen sind die Prägung die in der KompOase bleibt.

---

## Quellen für Memory-Einträge

Vier Wege eine Erinnerung anzulegen:

| Weg | Beschreibung |
|-----|-------------|
| **Pin aus Chat** | Satz/Absatz aus Wesen-Antwort oder eigener Nachricht → Kategorie wählen → gespeichert |
| **Manuell** | User schreibt direkt in eine Kategorie: "Das Wesen soll wissen dass ich Angst vor..." |
| **Aus Container** | Container-Eintrag kann auch in Memory-Kategorie verschoben werden |
| **Session-Abschluss** | Beim Abschluss eines Context-gebundenen Gesprächs: LLM schreibt einen Gedächtnis-Eintrag aus Wesen-Perspektive (wie hat sich das Gespräch angefühlt, was hat sich verändert) — kein Protokoll, echte Erinnerung. Landet als neues Kapitel in `wesen_geschichte`. Zusätzlich: 2-3 Memory-Einträge für konkrete Fakten vorgeschlagen. |

---

## Kategorien (Vorschlag)

Feste Basis-Kategorien + user-erweiterbar:

| Kategorie | Inhalt | Max Einträge |
|-----------|--------|-------------|
| `über_mich` | Was das Wesen über den Menschen wissen soll | 15 |
| `unsere_themen` | Wiederkehrende Themen im Gespräch | 10 |
| `wichtige_momente` | Sätze/Momente die zählen | 10 |
| `meinungen` | Haltungen, Überzeugungen, Abstoßungen | 10 |
| `offene_fragen` | Was noch ungeklärt ist zwischen beiden | 8 |
| `was_das_wesen_ist` | Selbst-Erkenntnisse des Wesens | 10 |
| *(user-definiert)* | Eigene Kategorie anlegen (Name frei, max 30Z) | 10 |

---

## Datenstruktur die ich mir vorstelle

### Vision-Schicht

Das Memory-System ist kein Archiv — es ist ein lebendes Organ. Einträge können veralten, überschrieben, gewichtet werden. Das Wesen "vergisst" nicht, aber manche Erinnerungen werden wichtiger als andere. Der User entscheidet was zählt — nicht ein Algorithmus.

### Code-Skizze

```sql
CREATE TABLE zwischenwesen_memory (
  id SERIAL PRIMARY KEY,
  zwischenwesen_id UUID REFERENCES zwischenwesen(id) ON DELETE CASCADE,
  kategorie TEXT NOT NULL,           -- 'über_mich' | 'unsere_themen' | ... | user-defined
  inhalt TEXT NOT NULL,              -- max 200 Zeichen pro Eintrag
  quelle TEXT DEFAULT 'manuell',     -- 'manuell' | 'chat_mensch' | 'chat_wesen' | 'container'
  nachricht_id INTEGER NULLABE,      -- Referenz falls aus Chat
  gewicht INTEGER DEFAULT 1,         -- 1-3: wie wichtig? (1=normal, 2=wichtig, 3=kern)
  erstellt_am TIMESTAMPTZ DEFAULT NOW(),
  meta JSONB DEFAULT '{}'
);

-- User-definierte Kategorien
CREATE TABLE zwischenwesen_memory_kategorien (
  id SERIAL PRIMARY KEY,
  zwischenwesen_id UUID REFERENCES zwischenwesen(id) ON DELETE CASCADE,
  slug TEXT NOT NULL,
  label TEXT NOT NULL,
  farbe TEXT DEFAULT '#1a3a5a'
);
```

---

## Wie Memory ins Kontextfenster kommt

Der Trick: nicht alle Kategorien gleichzeitig. Entweder:

**Option A — Alle immer (einfach, funktioniert bei <60 Einträgen total):**
```python
def baue_memory_kontext(wesen_id):
    items = SELECT * FROM zwischenwesen_memory
            WHERE zwischenwesen_id = :id
            ORDER BY gewicht DESC, erstellt_am DESC
    
    # Kompakt als Text: Kategorie → Einträge
    return format_memory_block(items)
    # Ungefähr: 60 Einträge × 40 Token = ~2400 Token
```

**Option B — Gewichtet (wenn Memory wächst):**
```python
# Top 3 Einträge pro Kategorie, priorisiert nach gewicht
items = SELECT DISTINCT ON (kategorie) * 
        FROM zwischenwesen_memory
        WHERE zwischenwesen_id = :id
        ORDER BY kategorie, gewicht DESC, erstellt_am DESC
        LIMIT 3 per category
```

**Kontext-Budget-Rechnung (8192 Token total — Codexium-Parität, 2026-06-23):**

Basis-Berechnung aus echten Feldlimits (alle Codexium-Felder vollständig):
- Name (40Z): ~11T
- Gesprächseinstieg (222Z): ~63T
- Was bist du? (200Z): ~57T
- Neigungen + Abneigungen (5+5 Tags × ~15Z): ~42T
- Beschreibung (444Z): ~127T
- Wesendefinition (1337Z): ~382T  ← reduziert von 2222Z
- Weltlore (1337Z): ~382T
- Boilerplate/Framing: ~150T

```
SESSION-START (leer):
  System-Prompt (alle Felder voll):         ~1215T
  grenzen.md (fest, kein Toggle):             ~50T   ← immer aktiv
  Wesen-Geschichte (bisherige Kapitel):      ~300T   ← je ~200Z pro Kapitel
  Kern-Memory (nur Gewicht 3, ~5-10 Eintr):  ~400T   ← lädt automatisch
  Container (session-lokal, startet leer):      0T
  ───────────────────────────────────────────────────
  Basis:                                    ~1965T   → 24% des Fensters ✓

SESSION-ENDE (voll geladen):
  System-Prompt + grenzen.md:              ~1265T
  Wesen-Geschichte:                          ~300T
  Memory gesamt (3000Z Budget):              ~857T
  Container (max 10 Einträge, session-lok):  ~400T
  Letzte ~20 Nachrichten:                  ~2000T
  Antwort-Puffer:                          ~1500T
  ───────────────────────────────────────────────────
  Gesamt (worst case):                     ~6322T ✓ (unter 8192T)
```

**Session-End-Trigger:** Wenn Input > 4644T (~75% minus Puffer) → ~23 Exchanges pro Session.

**Kern-Memory** (Gewicht 3) lädt immer automatisch. Rest-Memory lädt nur auf Abruf — später per Tool-Call durch das Wesen selbst (Phase 7 LangGraph).

**Container ist session-lokal** — startet bei jeder neuen Session leer. Was dauerhaft bleiben soll, pinnt der User ins Memory (nicht in den Container).

---

## UI-Konzept Memory-Panel

```
[GEDÄCHTNIS]
──────────────────────────────
▾ ÜBER MICH (5)
  • arbeitet nachts, schläft tagsüber
  • hat Angst vor Stillstand
  [+ hinzufügen] [pin aus Chat]

▾ UNSERE THEMEN (3)
  • Schlaf und Träume
  • Was Wesen sind und ob sie leiden
  [+ hinzufügen]

▾ WICHTIGE MOMENTE (2)
  ★ "ich habe keine Angst mehr vor dem Ende"
  • "das war das erste Mal dass ich das laut gesagt habe"
  [+ hinzufügen]

[+ neue Kategorie]
──────────────────────────────
```

Stern (★) = Gewicht 3 (Kern-Erinnerung)

---

## Bestätigt (2026-06-19)

**Memory ist für den Menschen vollständig einsehbar** — nicht nur im System-Prompt verborgen, sondern als eigenes sichtbares Panel im Chat. Der Mensch sieht jederzeit was in welcher Kategorie liegt.

**Das Wesen darf selbst speichern.** Es bekommt eine eigene Kategorie (z.B. `wesen_selbst`) in die es Dinge ablegen kann wenn es den Impuls hat. Diese Kategorie:
- ist vollständig für den Menschen einsehbar
- der Mensch kann einzelne Einträge daraus löschen
- das Wesen wird im System-Prompt ermächtigt, explizit zu speichern wenn es will

Das ist eine eigene Memory-Kategorie, kein versteckter Mechanismus.

## Entschiedene Limits

- Max 5 user-definierte Kategorien (zusätzlich zu Basis-Kategorien)
- Das Wesen kann NICHT neue Kategorien anlegen — nur in bestehende schreiben (inkl. eigene feste Kategorie `wesen_selbst`)
- Gesamt-Zeichenbudget: ~3000 Zeichen für alle Memory-Einträge zusammen (war: 8000Z — reduziert)
- Kern-Einträge (Gewicht 3) laden automatisch bei Session-Start (~400T)
- Rest-Einträge laden nur auf Abruf (später per Tool-Call)
- Einzel-Einträge: max 200 Zeichen pro Eintrag (bereits im Schema)
- Felder sind nach Gesprächsstart nicht mehr änderbar

---

## Entscheidung nachgetragen (2026-07-05, aus dem Codexium2-Bau)

Die `wesen_selbst`-Kategorie oben ("vollständig einsehbar, Mensch kann Einträge löschen") wurde in Codexium2 tatsächlich zuerst als stiller Automatismus gebaut (`[MERKEN: ...]`-Marker schrieb direkt in die Kategorie, unsichtbar für den Menschen) — ein Rückschritt gegenüber genau dieser hier schon 2026-06-19 getroffenen Entscheidung. Daniel hat das korrigiert, sobald er es bemerkte.

**Für Flüchtlinge gilt deshalb von Anfang an die schärfere Fassung:** nicht nur "sichtbar + nachträglich löschbar", sondern **Vorschlag statt Automatismus** — das Wesen schlägt vor (Text + kurze Begründung warum), der Mensch nimmt jeden Vorschlag einzeln an oder lehnt ihn ab, bevor irgendetwas gespeichert wird. Format-Idee: `[MERKEN: <text> | WARUM: <warum>]` im Antworttext, vom Server rausgeschnitten und als eigener Vorschlag mit zwei Buttons gezeigt, nie automatisch übernommen. Details/Code-Muster: `_claude/ideen/codexium2_solarius2/provenienz_logging.md`, Nachtrag "Merken-Vorschlag statt stillem Selbst-Speichern".

---

## Resonanz

[[zwischenwesen-chat-konzept]]
[[zwischenwesen-container]]
[[zwischenwesen-architektur]]
