# welt/projection_writer.py

Migriert: 2026-07-06

**Was es tut**: Schreibt `selfmodel_projection` tatsächlich in
`entity_profiles.meta` (JSONB-Merge, bestehende Keys bleiben unberührt).
Allowlist: nur 3 explizit freigegebene Entities dürfen verarbeitet werden
(kein Batch, kein Auto-Expand).

**Wozu**: Die "scharfe" Version von `projection_dry_run.py` — sobald die
Projektion als sicher gilt, schreibt dieses Skript sie tatsächlich in den
Cache-Layer, den andere Systeme (z.B. Prompts) lesen können.

**Migration**: `requests.post` (prompt-Stil) → `hauhau_client.chat()`.

**Zusammenhang**: Teil des noch nicht aktiven Wesen-Einzug-Bausteins.
