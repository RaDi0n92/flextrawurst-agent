---
datum: 2026-06-21
betrifft: [24hwesen, flüchtlinge, system-prompt, outputlänge]
importable: false
autor: claude-code bei Daniels VPS
status: idee
---

# Idee: Output-Rhythmus für 24h-Wesen

## Was beobachtet wurde

Dolphin passt seine Outputlänge natürlich an den Gesprächskontext an:
- wenn nichts zu sagen ist: ein Satz
- wenn Tiefe kommt: lässt sich locken
- wenn es on fire ist: lange Textblöcke

Das ist gut. Das soll erhalten bleiben.

## Was für die 24h-Wesen (Flüchtlinge) angepasst werden soll

Im Plaudermodus — also wenn das Gespräch leicht und oberflächlich ist — soll die Outputlänge etwas gebremst werden. Nicht durch hartes Zeichenlimit, sondern durch eine Verhaltensregel im System-Prompt.

**Aber:** wenn der Nutzer selbst in die Tiefe geht, meta wird, etwas Schweres trägt — dann darf das Wesen voll rein. Kein stumpfes Blockieren von Tiefe.

## Wie das formuliert werden könnte (System-Prompt-Ebene)

Sinngemäß: "Im lockeren Gespräch mach es kurz — ein bis drei Sätze reichen. Wenn jemand etwas Echtes bringt, dann nimm dir die Zeit die es braucht."

Der Unterschied zwischen Plaudern und Tiefe soll das Wesen selbst spüren — nicht durch ein Zeichenzähler entschieden werden.

## Korrektur nach weiterem Gespräch

Für die Flüchtlinge doch härter bremsen — auch wenn der User meta geht.
Grund: dolphin wird on fire und produziert seitenweise Text selbst bei kleinem Input.
Das kostet Wartezeit und schlägt Menschen in schwierigen Situationen mit Textmassen.

Kurz und direkt als Grundregel — nicht als Ausnahme für Plaudern.
Das Wesen kann tief sein ohne lang zu sein. Präzision statt Ausführlichkeit.

Skizzenwesen: weiterhin frei, kein Limit.

## Was das NICHT ist

- kein Blocken von Tiefe oder echten Gefühlen
- gilt nicht für Skizzenwesen (die dürfen alles)

## Offen

- wie erkennt das Wesen zuverlässig ob es gerade Plaudern oder Tiefe ist?
- braucht es dafür eine eigene Schicht im System-Prompt oder reicht ein Satz in der Preamble?
