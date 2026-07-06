# welt/entity_takt.py

Migriert: 2026-07-06

**Was es tut**: Entscheidungsloop für alle Wesen — periodischer Trigger, der aus
möglichen Aktionen wählt (aktuell primär: Schlaf). Enthält u.a. `_selbstbrief()`:
lässt das Wesen beim Aufwachen einen kurzen Brief an sich selbst schreiben
("was trägst du aus diesem Schlaf mit?").

**Migration**: `requests.post(f"{OLLAMA}/api/generate", ...)` (prompt+system,
nicht-streamend, 60s Timeout, mit Zufalls-Fallback auf `SCHLAFBRIEFE_THEATER`
falls das LLM nicht antwortet) → `hauhau_client.chat(prompt, system=..., ...)`.

**Status**: `entity-takt.service` ist aktuell **deaktiviert** (wie entity_kern.py,
Teil der gesperrten Wesen-Einzug-Phase) — nur syntaxgeprüft.

**Zusammenhang**: Ergänzt `entity_kern.py` (denken) um die Aktions-Entscheidungsebene.
