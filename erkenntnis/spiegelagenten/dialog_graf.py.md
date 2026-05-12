
---
## Neugier-Scan 2026-05-12 14:54
Originaldatei: `/root/werkraum/agent/dak_gord_system/dialog_graf.py`

Diese Datei definiert die Struktur eines Zustandsgraphen für ein Dialogsystem. Sie organisiert den Fluss von Benutzerinput und Systemantworten mithilfe von LangGraph. Die Funktionen `eingabe_node` und `antwort_node` steuern die Speicherung des Gesprächsverlaufs und die Interaktion mit dem LLM. Der Graph sorgt für eine zyklische Schleife zwischen Eingabe und Antwort, gesteuert durch eine Bedingung zum Beenden des Gesprächs.
