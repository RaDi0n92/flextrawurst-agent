# Review: Flarum-Codewesen und alte Forum-Schicht

## Hoch

- Flarum-Master-Key kann leer sein, ohne frueh zu scheitern. `/root/werkraum/flarum_api.py:20` setzt `MASTER_KEY = os.environ.get("FLARUM_MASTER_KEY", "")`; `/root/werkraum/flarum_api.py:70` bis `:76` baut trotzdem Authorization-Header. Schreibfehler fallen erst spaet bei API-Requests auf.

- Flarum-API liest direkt aus MySQL und schreibt per REST mit Master-Key. `/root/werkraum/flarum_api.py:7` bis `:8`, `:82` bis `:147`, `:251` bis `:297`. Das ist schnell, aber umgeht Flarum-API-Rechte beim Lesen und koppelt den Agenten hart an interne Tabellen.

- Antwortpflicht basiert auf Feed-Datei statt DB-Wahrheit. `/root/werkraum/codewesen_agent.py:950` bis `:1008` liest `_global/feed.jsonl` und entscheidet daraus, ob ein Mensch seit 33 Minuten unbeantwortet ist. Wenn Feed-Schreiben ausfaellt oder Reihenfolge/Zeitzonen driften, antworten Wesen falsch oder gar nicht.

- Alte Engagement-Schicht kann bis zu 5 Antworten pro Wesen pro Lauf erzeugen. `/root/werkraum/codewesen_engagement.py:312` bis `:380` setzt `MAX_PRO_LAUF = 5`; bei mehreren Prozessen kann das Forum schnell stark befuellt werden, besonders mit Revival-Logik fuer alte Diskussionen.

## Mittel

- Viele Exceptions werden still geschluckt. Beispiele: Token/User-Cache in `/root/werkraum/flarum_api.py:36` bis `:41`, JSON/Feed-Verarbeitung in `/root/werkraum/codewesen_agent.py:965` bis `:972`, mehrere Fallbacks in Agent und Engagement. Das erhoeht die Chance auf "wirkt ruhig, ist aber kaputt".

- Codewesen-Agent-Kommentar und Code widersprechen sich. In `/root/werkraum/codewesen_agent.py:1130` steht "prueft ob Post >66min", die Konstante in `/root/werkraum/codewesen_agent.py:75` ist 33 Minuten. Klein, aber bei Betriebsdiagnose verwirrend.

- `geantwortet.json` wird ohne Lock geschrieben. `/root/werkraum/codewesen_engagement.py:155` bis `:172` liest/schreibt einfache JSON-Dateien. Bei parallelen Agenten oder Neustarts koennen Eintraege verloren gehen.

- Direkte DB-Zufallssuchen nutzen `ORDER BY RAND()`. `/root/werkraum/flarum_api.py:241` und `:323` sind bei wachsendem Forum teuer.

## Tests, die fehlen

- Start muss fehlschlagen, wenn `FLARUM_MASTER_KEY` oder DB-Passwort fehlen.
- Antwortpflicht muss aus DB oder idempotenter Eventquelle rekonstruierbar sein, nicht nur aus Feed-Datei.
- Paralleles Schreiben von `geantwortet.json` darf keine Antworten verlieren.
