# dak+gord-system – Node Catalog v1

## `resolve_file_node`
Heute:
- Dateiname/Muster wird zu Pfad aufgelöst

## `read_file_node`
Heute:
- Datei oder Chunk lesen

## `refresh_focus_node`
Heute:
- Fokus- und Anschlusskontext setzen

Quellen:
- `anschlusskontext.py`

## `build_summary_node`
Heute:
- Verdichtung aus Textauszug erzeugen

Quellen:
- `verdichtung.py`

## `refresh_dossier_node`
Heute:
- `.agent.md` pflegen
- stabiler Gesamtstand
- aktueller Fokus
- Verlauf

Quellen:
- `agentdateien.py`

## `reason_node`
Heute:
- modellbasierte Antwort oder Einordnung erzeugen

Quellen:
- Antwortlogik im Startskript
- `ollama_chat.py`

## `write_trace_node`
Heute:
- Spuren, Logs, Wochenlog, Ticker-Log schreiben

Quellen:
- `neugierkern.py`
- `neugier_ticker.py`

## `neugier_scan_node`
Heute:
- Werkraum-Neugier

Quellen:
- `neugierkern.py`

## `vision_cycle_node`
Heute:
- Vision-Zyklus

Quellen:
- `neugierkern.py`

## Spätere Nodes
- `approval_interrupt_node`
- `patch_file_node`
- `run_shell_node`
- `verify_result_node`
- `resume_run_node`
