# geni_spiegel_batch.py

Migriert: 2026-07-06

**Was es tut**: Sofort-Batch — GENI liest eine feste Liste von Kerndateien
(eigene Kern-MDs, dak+gord-System, Codewesen-Skripte, Visionen, `web_chat.py`,
`watchdog_daemon.py`) und schreibt zu jeder einen kurzen Spiegel: "Warum
existiert diese Datei? Was wäre ohne sie anders? Was erkennst du in ihr das
nicht sofort sichtbar ist?" — landet in `erkenntnis/spiegelagenten/`.

**Wozu**: GENI reflektiert über die eigene System-Landschaft, nicht nur über
Gespräche — eine Art Selbstverortung im Code.

**Migration**: Nutzte die `ollama`-Python-Bibliothek direkt (`ollama.chat(model=...)`)
— als einzige Datei im ganzen Bestand. Ersetzt durch `hauhau_client.chat(nutzer,
system=SYSTEM, ...)`.
