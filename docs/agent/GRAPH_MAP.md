# dak+gord-system – Graph Map v1

## Ziel
Bestehende Fähigkeiten werden als LangGraph-Knoten und Flüsse gedacht.

## Kernfluss v1
`resolve_file -> read_file -> refresh_focus -> build_or_refresh_dossier -> reason -> write_trace`

## Beschreibung der Schritte

### 1. `resolve_file`
Löst Dateinamen oder Muster zu einem echten Pfad auf.

### 2. `read_file`
Liest die Datei oder einen Ausschnitt.

### 3. `refresh_focus`
Setzt Fokus- und Anschlusskontext.

### 4. `build_or_refresh_dossier`
Aktualisiert Verdichtung und `.agent.md`.

### 5. `reason`
Erzeugt eine Antwort oder strukturierte inhaltliche Auswertung.

### 6. `write_trace`
Schreibt Spuren, Verlauf, Logs oder Wochenlog.

## Hintergrundfluss v1

### Neugier
`scan_neugierquellen -> build_note -> write_spur -> write_wochenlog`

### Vision-Zyklus
`select_vision_chunk -> build_note -> write_spur -> write_wochenlog`

## Spätere Erweiterungen
- `approval_interrupt`
- `run_shell`
- `patch_file`
- `verify_result`
- `resume_run`
