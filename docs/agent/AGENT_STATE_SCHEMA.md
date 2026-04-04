# dak+gord-system – Agent State Schema v1

## Ziel
Dieses Schema beschreibt den minimalen LangGraph-AgentState, auf den alle späteren Runs aufsetzen.

## Kernfelder

### `task_id`
Eindeutige ID einer Aufgabe.

### `thread_id`
LangGraph-Thread-ID für Persistence und Resume.

### `run_type`
Art des Laufs, z.B.:
- `datei_lesen`
- `anschlussantwort`
- `neugier_scan`
- `vision_cycle`

### `ziel`
Das explizite Ziel des aktuellen Laufs.

### `modus`
Arbeitsmodus des Laufs, z.B.:
- `lesen`
- `verdichten`
- `antworten`
- `hintergrund`

### `fokus_datei`
Die zentrale Datei, auf die sich der aktuelle Lauf bezieht.

### `fokus_pfad`
Aufgelöster absoluter Pfad zur Fokusdatei.

### `aktueller_schritt`
Der derzeitige Graph-Schritt bzw. Arbeitsstand.

### `status`
Mögliche Werte:
- `neu`
- `in_arbeit`
- `wartet_auf_freigabe`
- `blockiert`
- `fertig`
- `fehlgeschlagen`

### `beobachtungen`
Liste strukturierter Beobachtungen aus Lesen, Tools oder Modellanalyse.

### `artefakte`
Liste erzeugter oder veränderter Artefakte:
- Agentdateien
- Verdichtungen
- Logs
- Patches
- Ausgabedateien

### `letzte_tool_aktionen`
Kurze Historie zuletzt genutzter Tools.

### `approval_status`
Status für Freigaben:
- `nicht_noetig`
- `offen`
- `genehmigt`
- `abgelehnt`

### `fehler`
Fehlerzustand oder Fehlermeldung, falls vorhanden.

### `notizen`
Freie interne Laufnotizen.

## Minimale JSON-artige Form

    {
      "task_id": "task_001",
      "thread_id": "thread_001",
      "run_type": "datei_lesen",
      "ziel": "vision4 lesen und Dossier aktualisieren",
      "modus": "lesen",
      "fokus_datei": "vision4.md",
      "fokus_pfad": "/root/werkraum/projekt/vision4.md",
      "aktueller_schritt": "refresh_dossier",
      "status": "in_arbeit",
      "beobachtungen": [],
      "artefakte": [],
      "letzte_tool_aktionen": [],
      "approval_status": "nicht_noetig",
      "fehler": null,
      "notizen": []
    }

## Grundregel
Kurzfristiger Laufzustand lebt im AgentState.
Langfristiges Dateigedächtnis lebt in `.agent.md` und den Spuren.
