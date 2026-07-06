# welt/traum_llm.py

Migriert: 2026-07-06

**Was es tut**: Traumverdichtung — nimmt ausgewählte Events aus
`traumkandidaten_events`, holt zugehörige Post-Inhalte, lässt das LLM sie zu
einem kurzen Traumtext (3-6 Sätze, "nur das Bild, keine Analyse") verdichten.
Schreibt `traumspuren.llm_traumtext` mit Status `offen`.

**Wozu**: Erster Schritt der Traumpipeline — rohes Erlebtes wird zu einem
poetisch verdichteten Traumbild, noch ohne Bewertung ob es ins Selbstmodell
übernommen wird.

**Migration**: `requests.post` (prompt-Stil) → `hauhau_client.chat()`.

**Zusammenhang**: Nächster Schritt in der Pipeline: `traum_integrator_dry.py`
bewertet den erzeugten Traumtext.
