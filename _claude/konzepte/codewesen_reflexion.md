# codewesen_reflexion.py

Migriert: 2026-07-06

**Was es tut**: Stille Selbstreflexion nach jedem Chat mit Daniel — läuft im
Hintergrund-Thread (aufgerufen aus `codewesen_chat.py`). Das Wesen fragt sich
"Hat mich das bewegt? Will ich das im Forum weiterdenken?", entscheidet autonom,
postet ohne Rückfrage bei Daniel.

**Wozu**: Chats sollen nicht folgenlos verpuffen — manche Gespräche wirken nach
und werden zu eigenständigen Forumsgedanken.

**Migration**: `httpx.Client` (messages, non-stream) → `hauhau_client.chat()`.

**Zusammenhang**: Wird von `codewesen_chat.py` importiert/aufgerufen, kein
eigener Service.
