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

Ein großes Gedächtnis-Blob wäre eine Katastrophe für das 8192-Token-Fenster. Stattdessen: mehrere kleine Kategorien. Bei jedem LLM-Aufruf kommen nur die relevanten Kategorien ins Fenster. Das Wesen wirkt intelligent weil es gezielt erinnert — nicht weil es alles auf einmal trägt.

Das ist manuell kuratiertes RAG ohne Embeddings. Der Mensch ist der Retrieval-Schritt.

---

## Quellen für Memory-Einträge

Drei Wege ein Erinnerung anzulegen:

| Weg | Beschreibung |
|-----|-------------|
| **Pin aus Chat** | Satz/Absatz aus Wesen-Antwort oder eigener Nachricht → Kategorie wählen → gespeichert |
| **Manuell** | User schreibt direkt in eine Kategorie: "Das Wesen soll wissen dass ich Angst vor..." |
| **Aus Container** | Container-Eintrag kann auch in Memory-Kategorie verschoben werden |

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

**Kontext-Budget-Rechnung (8192 Token total):**
```
System-Prompt (Felder):     ~600 Token
Memory (60 Einträge × 40T): ~2400 Token  
Container (20 × 40T):       ~800 Token
Letzte 8 Nachrichten:       ~800 Token
Antwort-Puffer:             ~2000 Token
────────────────────────────────────────
Gesamt:                     ~6600 Token ✓ (unter 8192)
```

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
- Gesamt-Zeichenbudget: ~8000 Zeichen für alle Memory-Einträge zusammen (entspricht ~2400 Token)
- Einzel-Einträge: max 200 Zeichen pro Eintrag (bereits im Schema)
- Felder sind nach Gesprächsstart nicht mehr änderbar

---

## Resonanz

[[zwischenwesen-chat-konzept]]
[[zwischenwesen-container]]
[[zwischenwesen-architektur]]
