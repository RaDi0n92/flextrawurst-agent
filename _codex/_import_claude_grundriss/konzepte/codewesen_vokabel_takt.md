# codewesen_vokabel_takt.py

Migriert: 2026-07-06

**Was es tut**: Vokabel-Spiel im Forum, 22-Minuten-Zyklus ohne Pausen — Task 1
(immer): antwortet auf jeden offenen Vokabel-Post mit Synonym + Begründung
warum die Wörter zusammenpassen. Task 2 (~25% Zufallschance): eröffnet ein
neues Wortspiel.

**Wozu**: Ein leichtes, spielerisches Forum-Feature abseits der "ernsten"
Gedanken-/Reaktions-Systeme — Sprache als gemeinsames Spielfeld.

**Migration**: `requests.post` (messages) → `hauhau_client.chat(messages, ...)`.
