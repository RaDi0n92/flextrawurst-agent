# systemweiser_web.py + systemweiser_app.py

Migriert: 2026-07-06

**Was sie tun**: Zwei Varianten eines "Betriebswächters" auf Port 8080 —
Systemweiser beobachtet laufende Dienste, Fehlerzahlen (422er, Impuls-Fehler)
und beantwortet Fragen dazu per LLM ("Antworte kurz, klar — nur beobachten und
empfehlen, nicht handeln").

**Wozu**: Ein Wächter-Interface, das Betriebszustand in natürlicher Sprache
zusammenfasst, statt rohe Logs lesen zu müssen. `_app.py` und `_web.py` sind
zwei Entwicklungsstände/Varianten desselben Grundgedankens.

**Migration**: Beide `requests.post` (prompt-Stil) → `hauhau_client.chat()`.
`systemweiser_app.py` hatte zusätzlich einen `json_format`-Parameter (Ollamas
`"format":"json"`) der beim Umbau entfernt wurde — ungenutzt im Aufrufer.

**Zusammenhang**: Kein aktiver systemd-Service gefunden — vermutlich manuell
gestartete Diagnose-Werkzeuge.
