# RUNBOOK

## Teststufen

### Schnelltest für MCP-Arbeit
Nutzen bei Änderungen an:
- MCP-Servern
- MCP-Runtime
- MCP-Tools
- Approval-Verhalten für MCP-Tools
- Serverprofilen

Befehl:
/root/werkraum/scripts/eval_mcp_fast.sh

Prüft aktuell:
- J4: mcp_uppercase + tools/list
- J5: mcp_write_note mit pending / genehmigt / abgelehnt
- K: Serverprofile mock_subprocess vs. mock_subprocess_alt

### Voller Smoke
Nutzen bei:
- Meilensteinen
- vor Commit / Backup / Release
- Änderungen an Graph, Agentlauf, Trace, Approval, Tool-Registry oder mehreren Bereichen zugleich

Befehl:
python3 -m agent.dak_gord_system.graph.evals.run_smoke_evals

Hinweis:
- eval_mcp_fast.py ist der Standard für den Entwicklungsloop.
- run_smoke_evals.py ist der langsame Gesamttest und muss nicht bei jeder MCP-Änderung laufen.
