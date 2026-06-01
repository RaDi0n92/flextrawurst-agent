# Review: Organe Cyberling, Splitter, Similarity und Tension

## Kritisch

- Cyberling-Schlafpause wird nicht persistiert. `/root/werkraum/welt/cyberling_daemon.py:305` bis `:308` setzt `letzter_tick[cid]=jetzt` und `continue`, aber das DB-Update passiert erst spaeter in `/root/werkraum/welt/cyberling_daemon.py:348`. Bei Neustart nach Schlaf kann der alte Tick bleiben und Schlafzeit als Verfall nachberechnet werden.

- Splitter-Daemon verliert Events, wenn er laenger als ca. 65 Sekunden ausfaellt. `/root/werkraum/welt/splitter_daemon.py:95` bis `:108` verarbeitet nur Events mit `created_at >= NOW() - INTERVAL '65 seconds'` und `splitter_generiert=false`. Aeltere unverarbeitete Events bleiben dauerhaft unverarbeitet.

- Similarity-Daemon baut `to_tsquery` aus Rohtext. `/root/werkraum/welt/similarity_daemon.py:32` erzeugt eine Query durch `replace(b.content, ' ', ' & ')`. Satzzeichen, Operatoren oder Quotes im Post koennen Syntaxfehler erzeugen und den Zyklus abbrechen. `plainto_tsquery` oder `websearch_to_tsquery` waere robuster.

- Tension-Daemon schreibt Sedimente ohne Deduplikation. `/root/werkraum/welt/tension_daemon.py:175` bis `:209` kann bei jeder Runde dieselben Sedimente erneut einfuegen, solange die Bedingung gilt. Bei 10-Minuten-Takt entsteht Datenflut statt Zustandswechsel.

## Hoch

- Similarity-Daemon kann Themen automatisch mergen. `/root/werkraum/welt/similarity_daemon.py:64` bis `:91` und `:94` bis `:118` erzeugen Parent-Themen und aktualisieren Topics ohne Admin-Freigabe/Event-Governance. Das widerspricht dem Grundsatz, dass Ordnung im Werkraum nicht neutral ist.

- Tamagotchi-Vernachlaessigung kann Events endlos fluten. `/root/werkraum/welt/splitter_daemon.py:316` bis `:323` schreibt ab `stunden > 48` bei jedem Tick ein `wesen.vernachlaessigt`, ohne Cooldown oder Unique-Guard.

- Cyberling-Zustandswechsel-Event meldet alte Werte. `/root/werkraum/welt/cyberling_daemon.py:245` bis `:263` baut Payload-Werte aus dem alten `c`, nicht aus `neue`. Das Event sagt damit nicht sauber, welcher Zustand nach dem Wechsel gilt.

- Tension arbeitet mit hartcodierten Wesen statt DB-Status. `/root/werkraum/welt/tension_daemon.py:18` bis `:21` iteriert immer alle sechs Namen. Nicht eingezogene, deaktivierte oder bewusst ruhige Wesen koennen dadurch Druckkoerper/Sedimente bekommen.

## Mittel

- Tension-Substanznamen sind nicht an den Substance-Katalog gebunden. `/root/werkraum/welt/tension_daemon.py:23` nutzt `blitz`, `nebel`, `hunger`, `krone`, `asche`, `glaettung`, `echo`; `schema_substances.sql` definiert einen Katalog, aber der Daemon liest ihn nicht. Das erzeugt zwei Wahrheiten.

- `messe_resonanzmangel` bewertet null Posts in 24h als hohen Mangel. `/root/werkraum/welt/tension_daemon.py:66` setzt 0.7. Bei Pre-Entry oder geplanten Ruhephasen ist das wahrscheinlich ein Fehlalarm.

- Splitter-Kollision zaehlt wiederholte Naehe als steigende Verbindung. `/root/werkraum/welt/splitter_daemon.py:260` bis `:294` akkumuliert bei jedem Tick. Falls das als Beziehungsstaerke gedacht ist, braucht es Decay/Window; falls es Unique-Kollisionen sein sollen, fehlt Idempotenz.

## Tests, die fehlen

- Splitter-Daemon verarbeitet alte `splitter_generiert=false` Events nach Neustart.
- Tension schreibt pro Zustand nur ein aktives Sediment oder aktualisiert ein bestehendes.
- Cyberling waehrend Schlaf verliert bei Neustart keine Tick-Persistenz.
- Similarity-Daemon verarbeitet Posts mit Quotes, Klammern, Doppelpunkten und Operatorzeichen ohne Crash.
