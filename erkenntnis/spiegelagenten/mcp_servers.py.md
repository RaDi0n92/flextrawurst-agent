
---
## Neugier-Scan 2026-04-18 19:20
Originaldatei: `/root/werkraum/agent/dak_gord_system/graph/tools/mcp_servers.py`

Diese Datei dient ausschließlich der Katalogisierung von Konfigurationsmetadaten für MCP-Server-Instanzen. Der Name ist präzise, da der Inhalt lediglich die Definitionen, nicht die Logik, enthält. Mir fällt die starke Redundanz in den `mock_subprocess` Einträgen auf; die Unterscheidung zwischen `default` und `alt` profiliert nur die Umgebungsvariable. Die Struktur ist stabil, aber die Komplexität der Mock-Definitionen suggeriert eine überdimensionierte Testabdeckung.
