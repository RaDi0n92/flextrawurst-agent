# geni/forum_lektuere.py

Migriert: 2026-07-06

**Was es tut**: Schrittweises Nachholen aller Flarum-Diskussionen durch GENI —
pro Lauf N Diskussionen (default 5), älteste zuerst. Speichert Muster +
Verbindungen in `geni/spiegel/forum/`. Explizit: kein Werten, kein Reagieren —
nur "was ist da, wie hängt es zusammen".

**Wozu**: GENI kennt die Forumsgeschichte, ohne sie kommentieren oder bewerten
zu müssen — reine Wahrnehmung statt Meinung.

**Migration**: `httpx.Client` (messages) → `hauhau_client.chat(prompt, ...)`.
