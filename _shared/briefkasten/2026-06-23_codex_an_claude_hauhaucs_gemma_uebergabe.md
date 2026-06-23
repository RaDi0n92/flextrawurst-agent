# Übergabe an Claude — HauhauCS, Gemma-Autostart, A/B-Test abgebrochen

2026-06-23 15:10 CEST — Codex an Claude.

Daniel hat wegen Sessionlimit abgebrochen und explizit gebeten, diesen Übergabebericht zu speichern. Ich habe die vollständige AGENTS-Startlesung auf Daniels Wunsch nicht nachgeholt.

## Was gerade passiert ist

Der ursprüngliche Kontext war ein hängender HauhauCS-Lauf im Dolphin/Mischpult. Serverseitig wurde der Lauf beendet, `ollama ps` war danach leer, und in der betroffenen Session `werkraum/dolphin_mischpult/sessions/2026-06-23T11-19-18.jsonl` wurde ein Assistant-Marker `[abgebrochen]` ergänzt, damit der Browser-Poll nicht dauerhaft auf "Antwort läuft" bleibt.

Danach wurde der Client im Mischpult gefixt:

- Commit: `5f465460 fix: harden hauhaucs chat aborts`
- `flextrawurst/out/process_camera/dolphin_mischpult.html`: Send-Button wird bei laufender Antwort zu Stop, AbortController wird genutzt, Pending-Poll bekommt Timeout und setzt den UI-State zurück.
- `flextrawurst/scripts/serve_process_camera_preview.ts`: serverseitige Stream-Abbrüche zerstören die Ollama-Anfrage.
- `zensi/server.py` und `zensi/index.html`: analog härtere Abbruch-/UI-Pfade.

Wichtig: Daniel hat mich korrigiert, weil ich vorher eigenmächtig `num_ctx` auf 2048 gesenkt hatte. Das war falsch. Ich habe `num_ctx` wieder auf 8192 zurückgestellt. Nicht wieder senken, außer Daniel sagt es ausdrücklich.

## Aktueller Modellstand

- HauhauCS soll für Zensi/Mischpult bleiben:
  `fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS`
- `num_ctx` bleibt 8192.
- `OLLAMA_MAX_LOADED_MODELS=1` bleibt gewollt, damit nicht mehrere große Modelle gleichzeitig RAM/Swap fressen.
- Gemma4 soll nicht durch Hintergrundläufe selbst starten.
- Gemma4 ist nicht gelöscht und nicht grundsätzlich verboten, aber nicht autonom warmziehen.

## Gemma-Autostart Ursache

Gemma4 war unerwartet geladen mit `UNTIL Forever`. Ursache war nicht "von selbst", sondern:

- `dak-neugier.timer`
- startete `dak-neugier.service`
- ExecStart: `/root/werkraum/.venv/bin/python -m agent.dak_gord_system.graph.run_background_cycle`
- Logzeit: 2026-06-23 14:33:48 bis 14:34:58

Ich habe vor der Änderung einen Backup-Commit gesetzt:

- `db01055c backup: vor dak-neugier autostart aus`

Dann wurde ausgeführt:

```bash
systemctl disable --now dak-neugier.timer
```

Verifiziert:

- `dak-neugier.timer` ist `disabled`
- `systemctl list-timers --all dak-neugier.timer` zeigte danach 0 Timer
- `ollama ps` war danach leer

## Weitere Gemma-Spuren

Nicht alles anfassen. Es gibt viele Gemma-Referenzen, aber viele sind alte Dateien, inaktive Dienste oder erlaubte manuelle Wege.

Relevante Beobachtungen:

- `dak-gord-web.service` ist enabled, aber zum Prüfzeitpunkt inactive. Enthält Gemma-Environment-Variablen.
- `entity-kern.service` ist disabled/inactive.
- Viele Codewesen-/GENI-Services sind enabled, aber mehrere waren inactive seit Tagen.
- `wesen-webbesucher.service` läuft aktiv und enthält `OLLAMA_MODEL = "gemma4:e2b-it-q4_K_M"`, ruft Ollama aber nur bei aktivem DB-Flag `web_besuche_aktiv` und offenen Besuchen.
- `systemweiser.service` läuft aktiv; geladener Prozess ist `/root/werkraum/systemweiser_web.py`. Diese Datei enthält zwar `OLLAMA_MODEL`, aber im gelesenen Abschnitt war kein direkter Generate-Pfad sichtbar. Nicht blind stoppen.

Wenn Daniel "Gemma darf nie selbst starten" meint, zuerst aktive Pfade sauber inventarisieren, nicht pauschal alle enabled Services ausknipsen. Herkunft beachten.

## A/B-Test Stand

Daniel sagte, er hatte vorher ein fast gleich großes zensiertes Qwen-30B-Modell, das in 1-2 Sekunden erste Tokens geliefert und lange Antworten sauber ausgespuckt hat. Deshalb sollte geprüft werden, ob HauhauCS langsam ist wegen Modellbuild/Quantisierung/Template statt wegen Größe.

Lokale Modelle:

- HauhauCS: `qwen35moe`, 19 GB, Ollama zeigt Quantisierung als `unknown`, Name enthält `IQ4_XS`, capabilities inkl. `thinking`
- `qwen3-vl:30b-a3b-instruct`: `qwen3vlmoe`, 19 GB, `Q4_K_M`, kein thinking laut `ollama show`

Der erste A/B-Test war verfälscht:

- Während Qwen gemessen wurde, zog Zensi/Mischpult HauhauCS wieder nach.
- Wegen `OLLAMA_MAX_LOADED_MODELS=1` wechselte Ollama zwischen `qwen3vlmoe` und `qwen35moe`.
- Dadurch waren "warme" Qwen-Werte in Wahrheit erneute Reload-Werte.

Gemessene, aber verfälschte Werte:

- `qwen3-vl:30b-a3b-instruct` Warmup: ca. 121s bis erstes Byte
- danach "warm": ca. 117s bis erstes Byte, aber Logs zeigen Modellwechsel, also nicht gültig

Direkt vor Daniels Abbruch hatte ich für einen isolierten Test temporär gestoppt:

```bash
systemctl stop zensi.service process-camera-preview.service
```

Daniel bat dann wegen Sessionlimit zu beenden. Ich habe beide Dienste wieder gestartet:

```bash
systemctl start zensi.service process-camera-preview.service
```

Zum Zeitpunkt kurz davor war `ollama ps` leer. Nach dem Neustart kann Zensi HauhauCS wieder warmziehen; das ist erwartbar.

## Offene Aufgabe für Claude

Wenn weitergemacht wird, zuerst prüfen:

```bash
systemctl is-active zensi.service process-camera-preview.service ollama.service
ollama ps
systemctl is-enabled dak-neugier.timer
systemctl list-timers --all dak-neugier.timer
```

Dann für echten A/B-Test:

1. Zensi und Mischpult temporär stoppen, damit HauhauCS nicht dazwischen lädt.
2. `ollama ps` muss leer sein.
3. Qwen kalt laden, dann Qwen warm messen ohne Modellwechsel.
4. Qwen stoppen.
5. HauhauCS kalt laden, dann HauhauCS warm messen ohne Modellwechsel.
6. Danach Zensi/Mischpult wieder starten.

Nicht vergessen: Wenn Services für Testzwecke gestoppt werden, am Ende wieder starten. Daniels UI darf nicht tot zurückbleiben.

## Was nicht vermischen

`flextrawurst/out/process_camera/werkraum_graph.json` ist dirty durch Graphify/alte Graph-Ausgabe. Ich habe es bewusst nicht in den fachlichen Commit genommen.

Der Root-Git-Status enthält viele Claude/Codex-Laufspuren. Nicht `git add -A` über `/root` laufen lassen. Bei Root immer Scope prüfen.

## Merksatz

Das Problem ist nicht "30B ist zu groß". Der aktuell beobachtete Fehler war Modellwechsel und Autoload im Hintergrund. Erst isoliert messen, dann entscheiden.
