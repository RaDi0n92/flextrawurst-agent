# Cyberling-Balancing-Simulation

Offline erzeugt. Keine Datenbank, keine Services, kein Produktivimport.

## Regeln

- Durst sinkt um 6.0 Punkte pro Stunde.
- Hunger sinkt um 3.0 Punkte pro Stunde.
- Energie sinkt normal um 1.0 Punkte pro Stunde.
- Unter Hunger/Durst-Schwellen sinkt Energie zusaetzlich um 4.0 Punkte pro Stunde.
- Gesundheit sinkt erst bei Energie <= 30 und kritischem Hunger/Durst.
- Wasser erlaubt ab Durst <= 70, Cooldown 3h, Obergrenze 88.
- Futter erlaubt ab Hunger <= 65, Cooldown 6h, Obergrenze 90.

## Szenario-Auswertung

| Szenario | erste Warnung | erste Kritisch | Endstatus | Minimum H/D/E/G | Aktionen | blockiert |
|---|---:|---:|---|---|---:|---:|
| Perfekte Pflege | - | - | stabil | 66.0/76.0/100.0/100.0 | 28 | 70 |
| Leicht verspaetete Pflege | - | - | stabil | 63.0/66.0/99.0/100.0 | 26 | 0 |
| 12h Vernachlaessigung | 10 | - | stabil | 66.0/34.0/57.5/100.0 | 26 | 58 |
| 24h Vernachlaessigung | 10 | 13 | kritisch | 31.0/0.0/0.0/58.0 | 19 | 43 |
| 48h Vernachlaessigung | 10 | 13 | tot | 0.0/0.0/0.0/0.0 | 9 | 20 |
| Ueberpflege-/Spamversuch | - | - | stabil | 66.0/76.0/100.0/100.0 | 28 | 70 |

## Empfehlung

**brauchbar**

Begruendung: Perfekte und leicht verspaetete Pflege bleiben stabil. 12h und 24h Vernachlaessigung sind sichtbar, aber reparierbar. 48h erzeugt deutlichen Druck. Der Spamversuch wird durch Schwellen und Cooldowns blockiert.

## Naechste Prueffragen vor Produktivbau

- Soll 24h Vernachlaessigung schon Gesundheit kosten oder nur Energie tief druecken?
- Soll 48h sicher lebensgefaehrlich sein oder nur knapp davor?
- Braucht Energie auch bei perfekter Pflege einen staerkeren Grundverfall, damit der Wert mehr als Dekoration ist?
