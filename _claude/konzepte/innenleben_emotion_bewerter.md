# innenleben/emotion_bewerter.py

Migriert: 2026-07-06

**Was es tut**: Bewertet ein Ereignis auf drei Emotionsdimensionen — Valenz
(negativ↔positiv), Arousal (entspannt↔aufgeregt), Dominanz (hilflos↔Kontrolle),
jeweils 0-10, per striktem JSON-Prompt. Fallback auf neutrale Werte (5/5/5) bei
Parse-Fehlern.

**Wozu**: Gibt Ereignissen im Innenleben-System eine quantifizierte emotionale
Signatur — Grundlage für Stimmungsverläufe/Reaktionsintensität der Wesen.

**Migration**: `httpx.Client` (prompt-Stil, `api/generate`) → `hauhau_client.chat()`.

**Zusammenhang**: Wird von `innenleben/nodes.py` importiert (Reflection-/
Memory-Writer-Pipeline).
