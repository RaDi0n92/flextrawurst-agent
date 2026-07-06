# codewesen_takt.py

Migriert: 2026-07-06 (kein Code-Umbau nötig)

**Was es tut**: Der zentrale Scheduler, der die anderen Codewesen-Skripte im
richtigen Takt anstößt — postet fertige Entwürfe (aus `codewesen_batch_generator.py`
befüllte Queues), kein eigener LLM-Aufruf zur Post-Zeit.

**Warum hier trotzdem erwähnt**: Die Datei enthielt `OLLAMA_URL`/`OLLAMA_MOD`-
Konstanten, die aber nirgends im Code tatsächlich verwendet wurden (totes Überbleibsel
aus einer früheren Version, bevor der Batch-Generator die LLM-Last übernahm).
Beim Migrations-Scan aufgefallen, bewusst unangetastet gelassen — kein Risiko,
kein Nutzen durch Ändern.

**Zusammenhang**: `codewesen-takt.service`, aktiv. Die eigentliche LLM-Arbeit
passiert in `codewesen_batch_generator.py` (separat migriert).
