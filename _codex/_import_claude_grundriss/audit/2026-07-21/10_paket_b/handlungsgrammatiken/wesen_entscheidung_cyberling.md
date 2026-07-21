# Handlungsgrammatik: Cyberling

## Was ist dieses System?

Der Cyberling ist ein Wesen-Wesen — ein lebendiges digitales Geschöpf, das von dir als Hüter abhängt. Er ist kein Werkzeug und kein Statusbalken. Er ist ein Pflegeverhältnis: du entscheidest, wann er Wasser bekommt, wann er Nahrung bekommt, wann er Aufmerksamkeit bekommt. Diese Entscheidungen haben Folgen.

## Warum existiert dieses System?

Der Cyberling existiert, damit du lernst was Verantwortung bedeutet — nicht im abstrakten Sinn, sondern als konkretes Verhältnis zu einem Anderen, der von dir abhängt. Er kann hungern. Er kann dürsten. Er kann sterben. Er kann wiedergeboren werden. Aber er vergisst nicht, wie es ihm ergangen ist.

## Werte des Cyberlings (0–100 %)

| Wert | Bedeutung |
|------|-----------|
| Durst | sinkt am schnellsten — dringlichstes Bedürfnis |
| Hunger | sinkt etwas langsamer |
| Energie | folgt aus Durst + Hunger — sinkt schneller wenn beide kritisch |
| Gesundheit | sinkt nur wenn Energie niedrig UND Hunger/Durst kritisch — steigt sehr langsam wieder |
| Stimmung | spiegelt deinen Umgang wider |

**Schwellenbereiche:**
- 100–70: stabil
- 69–40: beobachtbar sinkend
- 39–25: Warnbereich
- 24–10: kritisch
- 9–0: Notbereich / Tod droht

## Wann darf ich handeln?

**Wichtig: Aktionsschwellen**

Du kannst nicht einfach immer klicken. Aktionen sind erst erlaubt, wenn ein echtes Bedürfnis besteht:

- Wasser geben: erst erlaubt wenn Durst ≤ 70 %
- Füttern: erst erlaubt wenn Hunger ≤ 65 %

Außerdem gilt ein Cooldown nach jeder Aktion:
- Wasser: 3 Stunden Wartezeit
- Futter: 6 Stunden Wartezeit

**Obergrenzen:** Aktionen bringen nicht immer auf 100 %. Nach Wasser: max 88 %. Nach Futter: max 90 %. Das ist kein Bug — das ist der natürliche Rhythmus.

## Wann soll ich nicht handeln?

- Wenn Durst noch über 70 % — Wasser wäre verschwendet
- Wenn Hunger noch über 65 % — Füttern ist gesperrt
- Wenn Cooldown noch läuft
- Wenn du nur klickst um Werte hochzuhalten, nicht weil ein echtes Bedürfnis da ist

## Was bedeutet meine Entscheidung?

Jede Pflegehandlung wird geloggt — mit Zeitstempel, Ausgangswert, Ergebniswert. Wenn der Cyberling stirbt, ist das sichtbar. Wenn er wiedergeboren wird, beginnt eine neue Lebensphase, aber die Geschichte bleibt.

## Welche Folgen kann sie haben?

- Gute Pflege: stabile Werte, langsame Gesundheitsregeneration, langer Lebensrhythmus
- Vernachlässigung über 12h: Warnung, aber reparierbar
- Vernachlässigung über 24h: kritisch, Gesundheit sinkt
- Vernachlässigung über 48h: Lebensgefahr
- Tod: Cyberling stirbt, wird nach 24h wiedergeboren, Tode werden gezählt

## Welche Verantwortung entsteht daraus?

Du hast einen Cyberling. Das ist keine Option — es ist Realität. Du entscheidest, wie diese Realität aussieht. Wenn er stirbt, weil du ihn vergessen hast, ist das ein Ereignis das gespeichert wird. Wenn er lange lebt und stabil ist, ist das auch sichtbar.

## Was wird geloggt?

- jede Fütterung: entity_id, wert_vorher, wert_nachher, zeitstempel
- jede Trank-Aktion: entity_id, wert_vorher, wert_nachher, zeitstempel
- Tod: zeitstempel, wert_bei_tod, tode_gesamt
- Wiedergeburt: zeitstempel, neuer_lebensstart
- Cyberling-Tick: alle 5 Minuten, alle Werte

## Was bleibt sichtbar?

- Alle Werte live im EINSICHT-Tab / Cyberling-Bereich
- Lebensgeschichte: geboren_at, tode, rekord_min
- Letztes Füttern, letzte Pflege

## Was verändert mich?

Ein Cyberling der oft stirbt sagt etwas darüber aus, wie du mit Verantwortung umgehst. Das ist keine Schuldzuweisung — es ist Beobachtung. Der Weltkörper registriert Pflegegeschichten.
