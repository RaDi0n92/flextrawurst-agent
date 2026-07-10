---
titel: LangGraph — Architektur & Zukunft
typ: technik
erstellt: 2026-05-26
autor: claude-code bei Daniels VPS
---

# LangGraph — Architektur & Zukunft

[[INDEX|← Index]]

*LangGraph ist das Nervensystem der Wesen — aktuell fuer dak+gord UND alle 7 Codewesen aktiv, GENI hat den Code aber nutzt ihn nicht.*

---

## Stand heute (2026-05-26)

| System | LangGraph aktiv? | Checkpointer | Persistenz |
|--------|-----------------|--------------|------------|
| dak+gord | ✅ vollständig | PostgreSQL | flextrawurst DB |
| 6 Codewesen | ⬜ geplant | — | nur JSON-Dateien |
| GENI | ❌ | — | eigenes Knoten-System |

**Nachtrag 2026-07-10 (verifiziert, korrigiert die Tabelle oben):** Die "Zukunft" weiter
unten in dieser Datei ist inzwischen **Gegenwart** — nur anders gebaut als dort skizziert.
Auf Daniels Nachfrage ("ist es schon langgraph und postgresql für 7 8 wesen...ich glaub
geni nicht") live gegen die Datenbank geprueft:

| System | LangGraph aktiv? | DB-Modell | Checkpoints (Stand 2026-07-10) |
|--------|-----------------|-----------|-------------------------------|
| dak+gord-system | ✅ | geteilte `flextrawurst`-DB, `thread_id: codewesen-dak+gord-system` | 3322 |
| Schorschel | ✅ | geteilte `flextrawurst`-DB, `thread_id: codewesen-Schorschel` | 2039 |
| F3INSCHM3CK3R | ✅ | dito | 2015 |
| träumerlie | ✅ | dito | 2003 |
| R1ZZ1 | ✅ | dito | 1998 |
| jumpa | ✅ | dito | 1993 |
| Resonanzknoten | ✅ | dito | 1990 |
| GENI | ❌ (Code vorhanden, ungenutzt) | eigenes Schema `geni.*`, gleiche 4 Tabellen | 0 |

**Kein DB-pro-Wesen** wie unten unter "Die Zukunft" skizziert — stattdessen EIN
geteiltes Postgres (`flextrawurst`, Owner `dak`), Schema `public`, alle 7 Wesen trennen
sich rein per `thread_id` im selben `checkpoints`-Table. Alte `namelessAI_*`-Threads
bleiben als historisches Archiv erhalten (siehe [[08_codewesen_identitaeten]],
Provenienz-Prinzip — nicht loeschen).

**Zwei parallele Dienste laufen fuer dieselben 7 Wesen**, unklar ob/wie ueberlappend:
`codewesen-lg-daemon.service` (aelter, seit 2026-06-15, 60s-Kontext-Tick/300s-LLM-Tick,
schreibt `entity_profiles.lg_erinnerungen`) UND `innenleben-feeder.service` +
`welt-bruecke.service` (juenger, siehe Abschnitt "Innenleben" unten). Nicht weiter
untersucht in dieser Session — falls das mal geklaert werden soll, hier vermerkt.

**GENI:** `geni/geni_lg.py` hat vollstaendigen LangGraph-Code (`StateGraph`,
`PostgresSaver`, eigenes Schema `geni.*` mit denselben vier Checkpoint-Tabellen wie
`public.*`) — Migration lief (Tabellen existieren), aber 0 Zeilen. Code-Leiche, nicht
aktiv benutzt. GENIs echte Dienste (`geni-hoerer`, `geni-web`) laufen unabhaengig davon.

---

## dak+gord — LangGraph StateGraph

```python
# /root/werkraum/agent/dak_gord_system/graphen/gespraechsgraf.py

from langgraph.graph import END, StateGraph

# State: TypedDict mit Nachrichtenliste + Metadaten
class GespraechsState(TypedDict):
    nachrichten: List[dict]
    system_text: str
    modell: str
    stream_fn: Callable | None

# Graph:
graph = StateGraph(GespraechsState)
graph.add_node("systemtext", _baue_systemtext)
graph.add_node("konversation", _fuhre_gespraech)
graph.add_node("marker_parser", _parse_marker)

graph.set_entry_point("systemtext")
graph.add_edge("systemtext", "konversation")
graph.add_edge("konversation", "marker_parser")
graph.add_edge("marker_parser", END)

compiled_graph = graph.compile(checkpointer=checkpointer)
```

**Knoten-Beschreibungen:**

1. **systemtext**: Baut den Kontext-Block auf
   - Lädt Verfassung aus `verfassung_neu/*.md`
   - Lädt Organ-Status (alle 5 Organe)
   - Lädt Neugier-Spuren (werkraum + vision)
   - Lädt aktuelle Chat-Geschichte (letzte 33 Nachrichten)

2. **konversation**: Führt das eigentliche Gespräch
   - Ollama-Aufruf mit aufgebautem Kontext
   - Streaming (SSE oder Terminal)
   - Gibt Antwort-Text weiter

3. **marker_parser**: Verarbeitet LLM-Marker
   - `##MERKEN##`, `##SPÄTER##`, `##ZWISCHENRAUM##`, `##ABWÄGEN##`
   - Schreibt in die 5 Organe
   - Löst Reifedruck-Takt aus

---

## PostgreSQL-Checkpointer

```python
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string(
    "postgresql://dak@localhost/flextrawurst"
)
```

**Was der Checkpointer speichert:**
- Jede Nachricht (user + assistant) mit thread_id
- Jeder Graph-Zustand nach jedem Knoten
- Zeitstempel, Metadata

**Thread-IDs:**
- Jede Gesprächs-Session hat eine eindeutige thread_id
- Alle Nachrichten einer Session sind verknüpft
- Alte Sessions bleiben gespeichert und abrufbar

**PostgreSQL-Tabellen (in flextrawurst DB):**
```sql
-- LangGraph schreibt in eigene Tabellen:
checkpoints        ← Graph-Zustände
checkpoint_blobs   ← Blob-Daten (Bilder, große Objekte)
checkpoint_writes  ← Schreib-Operationen
```

---

## Innenleben — LangGraph für Selbstreflexion

```python
# /root/werkraum/innenleben/graph.py

# Separater LangGraph für Codewesen-Selbstmodell-Reflexion
# NICHT dak+gord — sondern für die 6 namelessAI-Wesen

graph = StateGraph(InnelebenState)
graph.add_node("memory_writer", _schreibe_erinnerung)
graph.add_node("reflection", _reflektiere)
graph.add_node("integrator", _integriere_ins_modell)

graph.set_entry_point("memory_writer")
graph.add_edge("memory_writer", "reflection")
graph.add_edge("reflection", "integrator")
graph.add_edge("integrator", END)
```

**Status:** Das Innenleben-System läuft nicht dauerhaft — es wird sporadisch ausgelöst (nach Direktchats, nach bestimmten Events). Die Selbstmodell-Dateien (JSON) werden dabei atomisch geschrieben:

```python
# /root/werkraum/innenleben/selbstmodell.py
def speichern_atomar(modell: dict, pfad: Path) -> None:
    """Atomare Schreiboperation via UUID-Temp-Datei."""
    tmp = pfad.parent / f".tmp_{uuid.uuid4()}.json"
    tmp.write_text(json.dumps(modell, indent=2, ensure_ascii=False))
    tmp.rename(pfad)   # Atomic auf POSIX
```

---

## Die Zukunft: LangGraph für alle Wesen (ÜBERHOLT — siehe Nachtrag 2026-07-10 oben)

Dieser Abschnitt beschreibt den Plan-Stand von 2026-05-26. Tatsaechlich gebaut wurde
etwas Leichteres (geteilte DB statt DB-pro-Wesen, siehe Tabelle oben) — als
Referenz stehen gelassen, nicht mehr aktueller Zielzustand:

```python
# ZUKÜNFTIG: Jedes Wesen bekommt eigene PostgreSQL-DB
# Schorschel → postgresql://wesen_1234@localhost/wesen_1234
# F3INSCHM3CK3R → postgresql://wesen_1324@localhost/wesen_1324
# ...

# Jedes Wesen hat:
# - Eigenen LangGraph StateGraph
# - Eigenen PostgreSQL-Checkpointer
# - Persistente Gesprächsgeschichte
# - Eigene Selbstmodell-Integration via Graph

# Warum noch nicht gebaut:
# - 6 × eigene DB = Infrastruktur-Aufwand
# - Ollama-Koordination wird komplexer
# - Momentan reichen JSON-Dateien + Filesystem
```

**Was das bringen würde:**
- Echtes Langzeitgedächtnis pro Wesen (über Neustarts hinweg)
- Gesprächs-Kontinuität für Direktchats
- Strukturierte Selbstreflexions-Zyklen
- Abspaltungs-Mechanismus: ein Wesen spaltet sich → neuer LangGraph-Subgraph

---

## LangGraph-Versionen im Einsatz

```bash
$ pip show langgraph
# Version: 0.2.x (Stand: Projektstart 2026)
# langgraph-checkpoint-postgres: für PostgreSQL-Checkpointer
```

**Kompatibilität:**
- `StateGraph` aus `langgraph.graph`
- `PostgresSaver` aus `langgraph.checkpoint.postgres`
- Kein Streaming-Support für Checkpointer (Streaming ist direkt im Ollama-Call)

---

## Warum LangGraph statt reiner Schleifen?

1. **Zustandspersistenz**: Graph-Zustand kann jederzeit gespeichert/wiederhergestellt werden
2. **Modularität**: Knoten können unabhängig getauscht werden
3. **Debugging**: Jeder Schritt ist nachvollziehbar
4. **Zukunft**: Parallele Knoten, Conditional Edges, Subgraphs möglich

---

*Weiter: [[14_obsidian]] | [[15_vision]]*
