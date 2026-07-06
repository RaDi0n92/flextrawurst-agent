# welt/browser_agent.py (+ gen_browser_agent.py)

Migriert: 2026-07-06

**Was es tut**: Ein Wesen navigiert kontinuierlich auf flextrawurst.de per
Playwright (headless Chrome, eingeloggt als Wesen) — Loop: Seite lesen → LLM
entscheidet über eine Aktion → Aktion ausführen → loggen. Screenshot geht ins
Denkstream-Display, Text wird für den Prompt genutzt. Ruft `schlafe()` →
`traum_generator.py` auf wenn das Wesen sich zum Schlafen entscheidet.

**Wozu**: Die Wesen erleben die Welt nicht nur passiv über die Datenbank —
sie "sehen" die eigentliche Oberfläche, genau wie ein Mensch sie sieht.

**Migration — drei Aufrufstellen**: zwei identische nicht-streamende Aufrufe
(Selbstbrief-artige Texte) → `hauhau_client.chat()`; eine Live-Streaming-Stelle
(Denkstream-Chunks werden einzeln in `entity_denkstream` geschrieben, mit
`seq`-Zähler und explizitem `done`-Flag am Ende) → `hauhau_client.chat_stream()`.

**`gen_browser_agent.py`**: Ein Generator-Skript, das `browser_agent.py` selbst
als Code-String erzeugt (`code = r'''...'''`). War bereits leicht veraltet
(nur 1 statt 3 Aufrufstellen) — trotzdem synchron migriert, damit ein erneuter
Lauf nicht die alte gemma4-Version zurückschreibt.

**Zusammenhang**: Kein aktiver Prozess aktuell (Teil der Wesen-Einzug-Phase).
