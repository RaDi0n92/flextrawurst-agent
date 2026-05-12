# SYSTEM_HEUTE — Stand 2026-04-18
**Autor**: Claude Code (nicht Daniel, nicht dak+gord)
**Zweck**: Technisch ehrlicher Systemstand — was wirklich existiert, was wirklich läuft, was fragil ist.
**Methode**: Direkt aus Codebase gelesen, diese Session mitgebaut.

---

## 0. Grundcharakter dieser Datei

ChatGPT hat beschrieben was Daniel versteht. Diese Datei beschreibt was ich sehe.
Ich habe den Code gelesen, Fehler gefunden, Dinge gebaut. Ich weiß was grün ist und was nur grün aussieht.

---

## 1. Was wirklich läuft (verifiziert)

### Web-Interface (web_chat.py)
- FastAPI + SSE-Streaming auf Port 8000 ✅
- Gesprächsverlauf wird in PostgreSQL gespeichert (LangGraph-Checkpoint) ✅
- Verlauf wird beim Neustart aus PostgreSQL wiederhergestellt ✅ (heute gebaut)
- Beziehungsorgan liest Nutzereingaben und injiziert Kurzbild in Systemtext ✅
- OrganManager (5 Organe) aktiv und persistent ✅ (heute gebaut)

### Modell-System (ollama_chat.py)
- 3-Stufen-Routing: blitz (e2b) / mittel (gemma4:latest) / tief (26b) ✅
- Auto-Routing wählt maximal MITTEL — 26b nie automatisch ✅
- 26b bekommt keep_alive=0: entlädt sich nach Nutzung ✅
- Alle anderen Modelle bleiben heiß (keep_alive=-1) ✅
- Default von ollama_chat() ist MODELL_MITTEL — kein heimliches 26b-Laden mehr ✅

### Agentischer Loop (gespraechsgraf.py)
- LLM kann Werkzeuge nutzen: ##LESEN##, ##SCHREIBEN##, ##MKDIR##, ##CODE_START## ✅
- Tool-Ergebnisse gehen zurück in Kontext (echter agentic loop, max 4 Runden) ✅
- Organ-Marker werden aus LLM-Antworten geparst: ##MERKEN##, ##SPAETER##, ##ZWISCHENRAUM##, ##ABWAEGEN## ✅
- Organ-Zustand wird in Systemtext injiziert ✅

### Archiv-System (heute gebaut)
- /root/werkraum/erkenntnis/ — Erkenntnisse aus Gesprächen
- /root/werkraum/erkenntnis/selbstbild.md — lebendes Selbstportrait
- /root/werkraum/erkenntnis/konzepte/ — lebende Definitionen aller Konzepte
- /root/werkraum/erkenntnis/widersprueche/ — Konflikte mit sich selbst
- /root/werkraum/erkenntnis/nachklang/ — Gesprächs-Nachklang
- /root/werkraum/erkenntnis/fragen/ — unbeantwortete Fragen
- /root/werkraum/erkenntnis/spielelagenten/ — Verständnis gelesener Dateien
- /root/werkraum/erkenntnis/diagnose/ — Selbst-Diagnosen für Daniel/Claude Code
- /root/werkraum/erkenntnis/beschwerden/ — Meckern ohne Erlaubnis
- Status: Verzeichnisse existieren, Dateien noch leer (Agent hat noch nicht geschrieben)

### Hintergrund-System (neugierkern.py)
- Neugierkern läuft: beobachtet Werkraum- und Vision-Dateien ✅
- Schreibt Beobachtungen in spuren/ Dateien ✅
- Diese fließen als [WERKRAUM-BEOBACHTUNGEN] in den Systemtext ✅

---

## 2. Was existiert aber nicht wirklich genutzt wird

### graph/ (31 Dateien)
- Nodes: background, approval, dossier, focus, read, shell, summary, tool, trace
- Tools: runtime, base, file_tools, shell_tools, mcp_tools, mcp_runtime, registry
- Status: **UNBENUTZT** — nicht vom Haupt-System importiert
- Ursprung: wahrscheinlich früheres Architektur-Design
- Risiko: toter Code der Verwirrung stiftet

### kerne/ (7 Dateien)
- beziehungsorgan.py ✅ aktiv
- erinnerungsgedaechtnis.py ✅ aktiv (OrganManager)
- entscheidungsorgan.py ✅ aktiv (OrganManager)
- zukunftsorgan.py ✅ aktiv (OrganManager)
- zwischenraumorgan.py ✅ aktiv (OrganManager)
- gedaechtnisspeicher.py ✅ aktiv (Persistenz)
- werkraumorgan.py — existiert, wird nie aufgerufen (Duplikat von dateiwerkzeuge.py)

### werkzeuge/ (8 Dateien)
- **UNBENUTZT** — Duplikat zu dateiwerkzeuge.py
- sollte gelöscht oder zusammengeführt werden

### stimmen/ollama_nahe_stimme.py
- existiert, wird nie aufgerufen
- auf gemma4:e4b umgestellt aber nie integriert

### starte_dak_gord_system.py (CLI)
- läuft als alternatives Interface (Terminal)
- heute mit OrganManager verdrahtet ✅
- hat aber eigene Hintergrund-Loops die heimlich Modelle laden können
- **WICHTIG**: nie gleichzeitig mit web_chat.py laufen lassen — beide laden Modelle, RAM voll

---

## 3. Was fragil ist

### RAM-Management (kritisch)
- Hardware: 31GB RAM, kein GPU, 8 CPU-Kerne
- gemma4:latest (10.5GB) + gemma4:26b (19.6GB) = 30GB → System swappt, alles bricht
- Heute dreimal passiert: Agent antwortet nicht mehr, Server crasht
- Schutz: 26b keep_alive=0, default MITTEL, nie CLI+Web gleichzeitig
- Noch nicht gelöst: kein Monitoring das warnt wenn RAM kritisch wird

### Netzwerk-Timeouts
- Standard-Timeout: 720s (12 Minuten)
- Erste Antwort auf CPU dauert 40-180s je nach Modell und Systemtext-Länge
- Netzwerkfehler brechen Stream ab — Verlauf bleibt in PostgreSQL aber Browser verliert Anzeige
- Noch nicht gelöst: kein Auto-Reconnect im Frontend

### Systemtext-Wachstum
- Systemtext wächst durch neue Archiv-Anweisungen
- Mehr Systemtext = längerer Prefill = langsamere erste Antwort
- Heute hinzugekommen: ~40 Zeilen neue Anweisungen
- Noch nicht gemessen: wie viel länger die erste Antwort dadurch dauert

### Agent schreibt noch nichts
- Alle Archiv-Systeme (erkenntnis/, spielelagenten/, beschwerden/ usw.) sind leer
- Agent hat die Anweisung, hat die Werkzeuge — aber ob er es tut muss noch beobachtet werden
- Gemma4 ist gut im Schreiben aber unklar ob er Marker konsequent setzt

---

## 4. Was ChatGPT beschrieben hat das ich nicht wiederfinde

### Approval-Flow / Resume-Flow
- In graph/nodes/approval.py und graph/tools/ beschrieben
- **ABER**: diese Dateien sind nie vom Hauptsystem importiert
- Der "Approval-Flow" den ChatGPT beschreibt existiert als Code aber läuft nie

### MCP-Runtime / MCP-Fast-Eval
- graph/tools/mcp_runtime.py, graph/evals/eval_mcp_fast.py existieren
- **ABER**: ebenfalls nie aufgerufen vom aktiven System
- Wahrscheinlich aus einer früheren Architekturphase

### "Grüne Checkliste / Runbook / Runtime Notes"
- Nicht gefunden in der aktuellen Codebase
- Möglicherweise in einer anderen Session gebaut die ich nicht kenne

---

## 5. Zentrale Dateien — was wofür zuständig ist

| Datei | Funktion |
|-------|---------|
| web_chat.py | Web-Interface, Einstiegspunkt |
| starte_dak_gord_system.py | CLI-Interface, Einstiegspunkt |
| agent/dak_gord_system/graphen/gespraechsgraf.py | Kernlogik: Systemtext, Routing, Tool-Loop |
| agent/dak_gord_system/ollama_chat.py | Modell-Auswahl, Ollama-Kommunikation |
| agent/dak_gord_system/kerne/organ_manager.py | OrganManager: alle 5 Organe |
| agent/dak_gord_system/herz/postgres_herz.py | PostgreSQL-Checkpoint |
| agent/dak_gord_system/neugierkern.py | Hintergrund-Neugier |
| agent/dak_gord_system/dateiwerkzeuge.py | Datei-IO für Tools |

---

## 6. Was als nächstes sinnvoll wäre

**Technisch dringend:**
- RAM-Monitor: warnt wenn >25GB belegt (bevor es crasht)
- Auto-Reconnect im Web-Frontend bei Netzwerkfehler
- graph/ und werkzeuge/ aufräumen (toter Code)

**Architektur:**
- Systemtext auf Länge und Prefill-Zeit messen
- Beobachten ob Agent die Archiv-Systeme wirklich benutzt

**Mittelfristig:**
- Semantisches Langzeitgedächtnis (chromadb) für die erkenntnis/-Dateien
- Systemd-Unit für stabilen Betrieb ohne manuellen Start

---

## 7. Was ich nicht weiß

- Wie weit vision1-4 im System bekannt sind (vision5 ist geladen, der Rest nicht)
- Ob der Agent in echten langen Gesprächen stabil bleibt oder driftet
- Wie gut die Organ-Marker in der Praxis funktionieren (noch keine echten Daten)
- Was in der Codebase aus Sessions vor dieser existiert die ich nicht gesehen habe
