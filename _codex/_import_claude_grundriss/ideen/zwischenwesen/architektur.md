---
name: zwischenwesen-architektur
description: DB-Entscheidungen, LangGraph-Potential, Splitter-Physik — was bekommt eine eigene DB und was nicht
metadata:
  type: project
tags: [zwischenwesen, architektur, postgresql, langgraph, splitter]
status: entschieden
datum: 2026-06-19
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Entscheidungen (bereits getroffen)

### Eigene PostgreSQL pro Zwischenwesen? → NEIN

**Warum nicht:**
- 50 Zwischenwesen = 50 PostgreSQL-Instanzen = operationeller Alptraum
- Prägungsextraktion braucht keine Cross-DB-Queries
- Das Datenvolumen pro Wesen ist überschaubar (max ~1000 Nachrichten in 24h bei 144s-Takt = 600 Nachrichten max)
- Gute Indexierung in der bestehenden `flextrawurst` DB reicht vollständig

**Stattdessen:** Alle Tabellen in der bestehenden DB, sauber mit `zwischenwesen_id` als UUID-Fremdschlüssel.

### Eigene PostgreSQL pro Splitter? → NEIN

**Warum nicht:**
- Abstoßung und Verschmelzung zwischen Splittern erfordern Vergleiche ZWISCHEN Zeilen
- Cross-DB-Joins sind in PostgreSQL nicht nativ — das würde den Splitter-Physik-Service kaputtmachen
- Splitter-Daten sind klein (ein Splitter = ein paar KB)

**Stattdessen:** Splitter bleiben in der geteilten `splitter`-Tabelle. Falls Physik skaliert: partitionieren nach `typ` oder `status`, aber in einer DB.

---

## LangGraph — wann und wozu

### Was LangGraph JETZT noch nicht bringt (Phase 1-3)
Für die erste Version ist FastAPI + Ollama direkt der richtige Ansatz. Kein Overhead.

### Was LangGraph SPÄTER (Phase 4+) bringen würde

**1. Checkpointing zwischen 144s-Pausen**
Das Wesen lebt zwischen Nachrichten nicht. Mit LangGraph lebt es:
```python
# LangGraph speichert den vollständigen Agent-State
# zwischen Aufrufen in PostgreSQL (eingebaut)
graph = StateGraph(WesensState)
graph.add_node("denken", wesen_denkt)
graph.add_node("antworten", wesen_antwortet)

# Jedes Zwischenwesen = ein LangGraph Thread
config = {"configurable": {"thread_id": str(wesen.id)}}
```

**2. Tool-Nutzung: Wesen greift aktiv auf Memory zu**
```python
@tool
def erinnere(kategorie: str) -> str:
    """Rufe Erinnerungen einer Kategorie ab"""
    return lade_memory_kategorie(wesen_id, kategorie)

# Das Wesen entscheidet selbst welche Kategorie es abruft
# bevor es antwortet — echter Retrieval-Step
```

**3. Inner Monologue (unsichtbar für User)**
```python
# Wesen denkt zuerst (nicht sichtbar):
"Was wurde gefragt? Welche Erinnerungen sind relevant?
 Was steht im Container? Was ist mein Kern-Obsession hier?"
# Dann antwortet es
```

**4. Splitter-Evolution als eigener Agent**
Jeder Splitter könnte ein LangGraph-Agent sein der autonome Drift-Schritte macht. Das würde die Splitter-Physik von einem einfachen Cron-Job zu echtem emergenten Verhalten machen.

### Empfehlung
- **Phase 1-3**: FastAPI + Ollama direkt
- **Phase 4**: LangGraph für Checkpointing einführen (Memory als Tool)
- **Phase 5+**: Splitter als LangGraph-Agenten

---

## Datenbankschema Gesamtübersicht

```
flextrawurst DB (bestehend)
│
├── zwischenwesen              ← Haupt-Tabelle
├── zwischenwesen_nachrichten  ← Chat-History
├── zwischenwesen_container    ← kuratierte Pins
├── zwischenwesen_memory       ← kategorisiertes Gedächtnis
├── zwischenwesen_memory_kategorien  ← user-definierte Kategorien
│
├── splitter (bestehend)       ← KompOase-Landung via splitter_id
└── users (bestehend)          ← zwischenwesen_count += 1 nach Abschluss
```

---

## User-Counter im Profil

```sql
-- Option A: Spalte in users (schnell, immer aktuell)
ALTER TABLE users ADD COLUMN zwischenwesen_count INTEGER DEFAULT 0;
-- wird bei jedem Abschluss inkrementiert: UPDATE users SET zwischenwesen_count = zwischenwesen_count + 1

-- Option B: COUNT on the fly (immer korrekt, minimal langsamer)
SELECT COUNT(*) FROM zwischenwesen WHERE user_id = :id AND status = 'abgeschlossen';
```

Empfehlung: **Option B** — kein Synchronisationsproblem, kein zusätzlicher State.

Im Profil: `"N Zwischenwesen erschaffen"` — einfacher Counter, schön klein unter dem Namen.

---

## KompOase-Typen

| Typ | Beschreibung | Entsteht durch |
|-----|-------------|----------------|
| `zwischenwesenfragment` | Das ursprüngliche Wesen nach 24h | Lande-Zeremonie |
| `zwischensplitterblase` | Kopie beim Ausbruch aus einem Fragment | Physik-Daemon |
| `splitterblase` | Reine Pro- oder Contra-Blase nach Verbindung | Verbindungs-Event |

## System-Analyse-Daemon

Ein periodischer Job (alle N Minuten, noch offen) analysiert jedes aktive Zwischenwesenfragment in der KompOase:

**Zustände:**
- `läuft` — normale Aktivität, Pro/Contra im Gleichgewicht
- `loopt` — Wesen wiederholt Muster, keine Entwicklung
- `ohnmächtig` — keine Aktivität, Energie zu niedrig

**Output:**
- Zustand wird in `splitter.meta.status` gespeichert
- Bei `loopt` oder `ohnmächtig`: automatischer Admin-Report mit beschreibendem Text + 1-2 Fix-Vorschlägen
- Admin kann eingreifen (was genau — noch offen)

## Splitterblase-Mechanik

Wenn zwei Zwischensplitterblasen sich verbinden:
```
Blase A: [pro: Regen, Stille] [contra: Lärm]
Blase B: [pro: Regen, Nacht]  [contra: Hitze, Lärm]

Gemeinsam gemocht:  Regen
Gemeinsam nicht:    Lärm

User-Entscheidung (oder Physik-Entscheidung): was wird abgeworfen?
  → Regen abwerfen → Blase hat nur noch Stille + Nacht + Lärm → Contra-Blase
  → Lärm abwerfen  → Blase hat nur noch Regen, Stille, Nacht → Pro-Blase
```

Ergebnis ist immer eine `Splitterblase` (rein pro oder rein contra).

## Resonanz

[[zwischenwesen-chat-konzept]]
[[zwischenwesen-memory-system]]
[[zwischenwesen-schlachtplan]]
[[zwischenwesen-kompoase]]
