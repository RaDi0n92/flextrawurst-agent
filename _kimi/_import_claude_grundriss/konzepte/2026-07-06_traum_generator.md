# welt/traum_generator.py

Migriert: 2026-07-06

**Was es tut**: Generiert Traumtext aus dem erlebten Tag eines Wesens — wird
von `browser_agent.py` innerhalb von `schlafe()` aufgerufen. Streamt Token für
Token live in `entity_denkstream` (type='traum'), speichert den fertigen Traum
in `traumspuren`, stößt danach optional Traumbild-Generierung an.

**Wozu**: Der eigentliche Traum-Erzeugungsmoment — passiert während das Wesen
"schläft" (Browser-Agent pausiert die Weltbeobachtung), sichtbar im Denkfenster.

**Migration**: Streaming mit `schreibe_denkstream_chunk()`-Helper (schon vorher
sauber gekapselt) → `hauhau_client.chat_stream()`, Helper-Aufrufe unverändert,
nur die Quelle der Chunks getauscht.

**Zusammenhang**: Speist `traum_llm.py`/`traum_luzid.py`/`traum_integrator_dry.py`
— die gesamte Traum-Pipeline.
