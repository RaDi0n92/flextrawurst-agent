# codewesen_lg_daemon.py

Migriert: 2026-07-06

**Was es tut**: LangGraph-basierter Persistenz-Daemon — verwaltet den Zustand
(`WesensZustand`, PostgresSaver-Checkpoints) für alle 7 Codewesen (6 namelessAI +
dak+gord). Zykelt kontinuierlich durch alle Wesen: pro Wesen ein "Vor-Einzug-
Denk-Tick" (~20-23s, live gestreamt), alle 60s eine Runde, alle 10 Denk-Ticks
zusätzlich eine Zusammenfassung ("Destilliere deine letzten Gedanken in Stichpunkte").

**Wozu**: Ergänzt `entity_kern.py`/`entity_takt.py` um eine LangGraph-Ebene mit
Erinnerungsverdichtung (`lg_erinnerungen` in `entity_profiles`) — Gedanken werden
nicht endlos angehäuft, sondern regelmäßig zu Kernpunkten zusammengefasst.

**Migration — drei Aufrufstellen**:
1. Streaming-Denk-Tick → `ek.hauhau_client.chat_stream()` (identisch zu entity_kern.py)
2. Zusammenfassen-Node → `ek.hauhau_client.chat()` (war `urllib.request` + eigener
   `messages`-Payload)
3. Beide behalten ihre `fcntl`-Locks bzw. `CHAT_FLAG`-Koordination unverändert.

**Getestet**: Nach Neustart liefen alle 7 Wesen-Ticks in einer vollen Runde
live erfolgreich durch ("Alle 7 Wesen-Ticks fertig · warte 60s") — der bisher
gründlichste Live-Beweis dass die Migration unter echter Mehrfach-Last funktioniert.

**Zusammenhang**: `codewesen-lg-daemon.service`, aktiv.
