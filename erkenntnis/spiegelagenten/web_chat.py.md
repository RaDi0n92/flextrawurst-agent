
---
## Neugier-Scan 2026-04-19 03:21
Originaldatei: `/root/werkraum/web_chat.py`

Die Benennung ist zu oberflächlich für die Komplexität des Inhalts. Dieses Skript ist kein reiner Chat-Handler, sondern ein Persistenz-Wrapper für eine Zustandsmaschine. Die wahre Funktion liegt in der Wiederherstellung des `_graf` und des `_verlauf` aus dem Datenbank-Checkpoint. Der `lifespan`-Kontext ist der kritischste Punkt, da er die gesamte Existenz des aktuellen Sitzungszustands definiert. Es muss sichergestellt werden, dass die Wiederherstellung des Kontextes fehlerfrei erfolgt, bevor die Interaktion beginnt.
