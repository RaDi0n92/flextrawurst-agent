# geni/geni_lg.py

Migriert: 2026-07-06

**Was es tut**: LangGraph-PostgreSQL-Persistenz für GENI-Sessions (ersetzt eine
frühere In-Memory-Dict-Lösung). Eigenes `geni`-Schema in Postgres. Destilliert
alle `DESTILLATIONS_INTERVALL` (=10) Gesprächsrunden die letzten Erinnerungen
zu maximal 8 Stichpunkten.

**Wozu**: GENIs Gedächtnis über einzelne Sessions hinweg — ohne Destillation
würde der Kontext unbegrenzt wachsen.

**Migration**: `urllib.request` (chat, messages) → `hauhau_client.chat(prompt,
system=..., ...)`.

**Zusammenhang**: Nutzt eigenes DB-Schema (`search_path=geni`), getrennt von
`public.*` — Thread-IDs im Format `geni-{session_id}`.
