# welt/traum_integrator_dry.py

Migriert: 2026-07-06

**Was es tut**: Dry-Run (nur analysieren, nichts schreiben) — liest offene
Traumspuren (`integrator_status='offen'`), lässt das LLM bewerten: Status-
Vorschlag (angenommen/abgelehnt/zurückgestellt) + Kategorie (Motivspur,
Selbstbehauptung, Beziehungsspur, Konfliktspur, reine Poesie, zurückstellen)
+ Begründung. Gibt Befund nur auf der Konsole aus.

**Wozu**: Qualitätskontrolle bevor ein Traum ins Selbstmodell einfließen darf
— verhindert dass halluzinierte oder zu direktive Trauminhalte unkontrolliert
übernommen werden.

**Migration**: `requests.post` (prompt-Stil) → `hauhau_client.chat()`.
