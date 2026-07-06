# welt/projection_dry_run.py

Migriert: 2026-07-06

**Was es tut**: Dry-Run (nur lesen, NICHTS schreiben) für die "Selbstmodell-
Projektion" — liest `entity_selfmodel_entries` pro Entität, lässt das LLM eine
vorsichtige Kurzprojektion generieren (Motive + Kurzzusammenfassung als JSON).

**Wozu — die Grundregel dahinter**: `entity_selfmodel_entries` ist Wahrheit
(append-only, unberührbar). `entity_profiles.meta.selfmodel_projection` ist ein
Cache, jederzeit rekonstruierbar. Dieses Skript testet die Projektion, OHNE den
Cache zu schreiben — "Projection darf glätten, aber nicht behaupten. Darf
zusammenfassen, aber nicht identifizieren."

**Migration**: `requests.post` (prompt-Stil, `api/generate`) → `hauhau_client.chat()`.

**Status**: Teil des noch nicht aktiven Wesen-Einzug-Bausteins — kein laufender
Prozess, nur Code-Migration für den Tag an dem es gebraucht wird.

**Zusammenhang**: Vorstufe zu `projection_writer.py` (schreibt tatsächlich).
