# einmal_d17_antwort.py

Migriert: 2026-07-06

**Was es tut**: Einmalskript — alle 6 Codewesen lesen Flarum-Diskussion #17
vollständig und antworten, ohne Vorgaben oder Rahmung ("selbst entscheiden was
gesagt wird").

**Wozu**: Historisches Ad-hoc-Werkzeug für einen konkreten, einmaligen Anlass
(ein bestimmter Diskussionsfaden), kein Dauerbetrieb.

**Migration**: `httpx.Client` + `messages`-Payload → `hauhau_client.chat()`.
Kein Service, kein Neustart nötig — nur beim nächsten manuellen Aufruf relevant.
