---
titel: flarumstyler — Meldesystem
typ: system
erstellt: 2026-07-07
autor: claude-code bei Daniels VPS
---

# flarumstyler — Meldesystem

[[INDEX|← Index]]

## Zweck

Rein beobachtendes Meldesystem: zeigt an was nicht so ist wie es sein soll, erklärt was das bedeutet und was eine Empfehlung bringen würde/nicht bringen würde. **Greift nie selbst ein** — kein Auto-Fix, keine Telegram-Anbindung (beides bewusst von Daniel abgelehnt). Er entscheidet und führt Maßnahmen selbst aus.

Entstanden in der Nacht 2026-07-06/07, direkt nachdem mehrere wochenlang unbemerkte Bugs auftauchten (`flarum-monitor.service` seit über einem Monat deaktiviert, fehlende dak+gord-Antwortpflicht, veraltete Watchdog-Guardrail). Loser Vorbild-Gedanke: Systemweiser (Ampel-Optik), aber eigenständig gebaut — Systemweiser selbst ist unfertig/roh.

## Zugriff

`https://flextrawurst.de/flarumstyler` (öffentlich, seit 2026-07-07) sowie weiterhin `http://localhost:8787/flarumstyler` lokal. Eigenständige Seite, **nicht** Teil der flextrawurst-Surface (die zeigt laut Daniel nur Flarum-Inhalte ab).

**nginx-Fund beim Live-Schalten:** `/etc/nginx/sites-available/flextrawurst` hatte bereits einen generischen `location /api/ { proxy_pass http://localhost:8030; }`-Block (welt-api) — `/api/flarumstyler` wäre darüber fälschlich zu welt-api geroutet worden (404, da dort unbekannt) statt zu Port 8787. Gefixt mit einem spezifischeren `location /api/flarumstyler { proxy_pass http://localhost:8787; }`-Block (deckt als Prefix auch `/api/flarumstyler_verlauf` mit ab) — nginx bevorzugt bei Prefix-Locations automatisch den längeren, unabhängig von der Reihenfolge in der Datei. Getestet: `/api/health` (welt-api) weiterhin korrekt auf 8030, `/api/flarumstyler*` jetzt korrekt auf 8787.

## Architektur

- **Datenquelle:** `welt/weltkern_watchdog.py`, läuft weiterhin alle 10 Minuten über `weltkern-watchdog.timer`, schreibt `logs/weltkern_letzter_bericht.json`.
- **Erweiterung 2026-07-07:**
  - `WELTKERN_SERVICES` um 13 Flarum-/Codewesen-Dienste ergänzt, die vorher gar nicht überwacht wurden (die 6 `codewesen-<Name>`, `codewesen-antwort-daniel`, `codewesen-takt`, `codewesen-lg-daemon`, `codewesen-forum-neugier`, `codewesen-batch-generator`, `codewesen-dakgordsystem`, `codewesen-reaktion-dakgord`, `flarum-monitor`).
  - Neue Funktion `fehler_uebersicht()`: scannt alle Haupt-Logs + alle `codewesen/<Name>/reaktion.log` einmal komplett durch, zählt **dauerhaft** (seit Logbeginn, kein Zeitfenster) pro bekanntem Fehlermuster und merkt den Zeitpunkt des letzten Auftretens.
  - `FEHLER_MUSTER`-Katalog: pro Muster ein Eintrag mit `was_ist_los`, `empfehlung`, `bringt_das`, `bringt_das_nicht` — Klartext, kein reiner Zähler. Aktuell erfasst: Ollama nicht erreichbar, CSRF-Mismatch, kaputter Import, JSON-ohne-Dict, Tag-Validierung, Impuls ohne Titel.
- **Server:** `scripts/serve_process_camera_preview.ts` (Port 8787, derselbe Server wie Aufgabenchats) — zwei neue Routen:
  - `GET /flarumstyler` — die Seite (`out/process_camera/flarumstyler.html`)
  - `GET /api/flarumstyler` — der aktuelle Watchdog-Bericht als JSON, unverändert durchgereicht
- **Seite:** Ampel-Kacheln (grün/gelb/grau/rot) für Dienste und für Fehlermuster. Klick öffnet ein Detail-Panel mit vollem Erklärungstext. Auto-Refresh alle 30s. Farblogik Fehlermuster: rot < 6h seit letztem Auftreten, gelb < 72h, grau darüber oder nie aufgetreten (0 Vorkommen = grau).

## Ausbau 2026-07-07 (noch selbe Nacht — "die ganze Karte")

Nach Daniels Selbstanalyse-Wunsch fünf Verbesserungen umgesetzt:

1. **Kopf-Banner** — "Alles ok" (grün) oder "X Dienste unerwartet down · Y akute Fehler-Kategorien" (gelb/rot) auf einen Blick, ohne scrollen zu müssen.
2. **Sortierung nach Dringlichkeit** — rote Karten zuerst, dann gelb, dann grau/grün. Dienste-Sektion klappt sich automatisch ein, wenn keine unerwarteten Ausfälle da sind (Daniel kann manuell auf-/zuklappen, das wird respektiert).
3. **`erwartet_aus`-Status** — `SERVICES_ERWARTET_AUS = {"entity-kern", "entity-takt"}` in `weltkern_watchdog.py`: bewusst dauerhaft inaktive Dienste werden grau statt rot markiert, damit sie kein Dauer-Alarm-Rauschen erzeugen und echte rote Punkte nicht verwaschen.
4. **Beispielzeilen im Detail** — `fehler_uebersicht()` sammelt jetzt pro Fehlermuster die letzten 5 echten Log-Zeilen (mit Wesen-Zuordnung bei `reaktion.log`), sichtbar im Detail-Panel unter "Letzte Vorkommen im Log" — direkter diagnostischer Wert ohne SSH.
5. **Mini-Verlauf + Trend-Delta** — `logs/weltkern_verlauf.jsonl` (schlanke Kennzahlen pro Lauf, max. 4320 Zeilen ≈ 30 Tage bei 10-Min-Takt, kein Volltext) über neue Funktion `verlauf_anhaengen()`. Neue Route `GET /api/flarumstyler_verlauf` liefert die letzten 50 Einträge. Frontend zeigt ein kleines `+N`/`-N` neben jeder Fehlerzahl — Vergleich zum vorletzten Lauf.

Bewusst zurückgestellt: Punkt 5 aus der ursprünglichen Ideenliste ("Verknüpfung mit Baustein 2/Content-Live-Ansicht") — Baustein 2 existiert noch nicht, daher nur als Design-Hinweis in `project_meldesystem_vision`-Memory festgehalten.

## Bewusst nicht enthalten

- Keine Action-Buttons, kein Neustart-Mechanismus über die Seite.
- Keine Push-Benachrichtigung (kein Telegram/E-Mail) — Daniel ruft die Seite bei Bedarf selbst auf.
- Keine Live-Ansicht der heute gebauten Content-Features (Container, Batch-Queue, Ready-Check) — das ist ein separater, späterer Baustein (siehe Memory `project_meldesystem_vision`).

## Nächste Schritte (noch offen)

- Weitere Fehlermuster ergänzen, sobald neue wiederkehrende Fehlerklassen auffallen.
- Die 8 weiteren Dateien mit derselben JSON-Extraktions-Schwachstelle (nicht geprüft ob dict) sind noch nicht abgesichert — nur die 3 tatsächlich am dak+gord-Absturz beteiligten wurden gefixt.
