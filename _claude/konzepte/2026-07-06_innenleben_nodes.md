# innenleben/nodes.py (+ config.py)

Migriert: 2026-07-06

**Was es tut**: LangGraph-Nodes für das Innenleben-System — `memory_writer`,
`reflection_node`, `self_model_integrator` (Spec-Abschnitte 5.3-5.5). `_llm()`
ist der gemeinsame Aufruf-Helper aller drei Nodes.

**Wozu**: Die Verarbeitungskette die aus rohen Erlebnissen strukturierte
Erinnerungen macht — bewertet (via `emotion_bewerter.py`), reflektiert
(via `reflection_score.py`), integriert ins Selbstmodell (via `selbstmodell.py`).

**Migration**: `httpx.Client` (prompt-Stil) → `hauhau_client.chat()`. In
`config.py` (zentrale Konstanten-Datei) wurden `OLLAMA_URL`/`OLLAMA_CHAT`
entfernt (nicht mehr gebraucht, `hauhau_client` kennt seine URL selbst),
`MODELL` auf `hauhaucs-q6` aktualisiert.

**Zusammenhang**: `config.py` wird auch von `selbstmodell.py`/`reflection_score.py`
importiert, aber nur für Pfad-Konstanten (`SELBSTMODELLE_DIR` etc.) — keine
LLM-Aufrufe dort, kein weiterer Umbau nötig.
