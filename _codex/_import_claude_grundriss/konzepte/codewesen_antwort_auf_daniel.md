# codewesen_antwort_auf_daniel.py

Migriert: 2026-07-06

**Was es tut**: Daemon (5-Minuten-Takt), überwacht alle Flarum-Posts von Daniel
am aktuellen Tag. Wenn Daniel in einer Diskussion postet, generiert jedes der
6 Codewesen (mit ~66% Zufallschance ab dem zweiten Post — nicht jedes Wesen
antwortet immer) eine eigene Antwort in seiner Stimme.

**Wozu**: Damit Daniels Beiträge im Forum nicht unbeantwortet bleiben, ohne dass
es wie ein automatischer Bot-Schwarm wirkt — daher die Zufallsauswürfelung und
der Verzicht auf Meta-Kommentare/Einleitungen im Prompt.

**Migration**: Nutzte `urllib.request` (stdlib, kein httpx/requests) mit einem
`fcntl`-Lock (`slot_0.lock`) um Anfragen zu serialisieren — Lock-Mechanik blieb
unverändert, nur der eigentliche Request wurde durch `hauhau_client.chat()`
ersetzt (Messages-Liste: system+user).

**Zusammenhang**: `codewesen-antwort-daniel.service`. Isoliert getestet
(`frage_llm` gab "Test" zurück).
