# geni/sprechen.py

Migriert: 2026-07-06

**Was es tut**: Kommandozeilen-Direktkontakt mit GENI (`python3 geni/sprechen.py`).
Jedes Gespräch: Eingabe → Knoten im Gedächtnisgraphen, GENI lädt Kontext
(Kerndateien + letzte Knoten + Resonanz-Suche), LLM antwortet live gestreamt
in der Konsole, Antwort → eigener Knoten, Kanten zwischen verwandten Knoten
werden gezogen (Resonanz-Prinzip).

**Wozu**: Der ursprüngliche, einfachste Zugang zu GENI — bevor es die Web-UI
(`geni/dialog.py`) gab.

**Migration**: `requests.post(..., stream=True)` mit manuellem Zeilen-Parsing
und Live-`print()` → `hauhau_client.chat_stream()`, `print(token, end="", flush=True)`
pro Chunk — funktional identisch, weniger Code.
