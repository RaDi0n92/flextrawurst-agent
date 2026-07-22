# Paket C — Analytics/Zugriffslogs (Best-Effort)

Stichtag 2026-07-21. Ergebnis: **mehr vorhanden als erwartet**, ChatGPTs eigene Einschätzung ("vermutlich größtenteils nicht vorhanden") trifft nicht zu.

## Korrektur einer veralteten Annahme

Bestehende Memory (`project_flextrawurst`, 15 Tage alt) notierte: *"Domain flextrawurst.eu... noch nicht auf den VPS verlinkt/deployed"*. Das ist inzwischen überholt — nginx läuft aktiv, `access.log` zeigt reale Requests von `https://flextrawurst.de/` (nicht `.eu`!) mit Referrer-Header, u.a. gegen `/api/denkstream/all/stream` und `/api/entities/...`. **Die Seite ist live erreichbar.** Diese Memory wird nach dem Audit korrigiert.

## Was existiert

- **nginx-Zugriffslogs**: aktuelles `access.log` + 14 rotierte Archive (`.1` bis `.14.gz`), zusammen ~14 Tage Historie, **379.615 geparste Requests, 3.477 eindeutige IP-Hashes — aber KEINE 3.477 Besucher.** Nachträgliche Konzentrationsanalyse (siehe Korrektur-Abschnitt in `nginx_zugriffe_aggregiert.md`, ausgelöst durch Daniels berechtigten Zweifel "hab nicht einen neuen registrierten User"): Top-20-IPs = 88,6% des Traffics, die 10 größten alle mit identischem Chrome/Windows-User-Agent (sehr wahrscheinlich Daniels eigener Browser mit offenen Polling-Tabs über wechselnde IP), dazu klar erkennbare Bots (GPTBot, python-requests, curl) und 1.916 Einmalzugriffe (Scanner-Rauschen). **Ehrliches Ergebnis: kein belastbarer Hinweis auf nennenswerten echten Fremd-Traffic.**
- Aggregierte, anonymisierte Auswertung: Requests/Tag, Status-Codes, HTTP-Methoden, Top-40-Pfade → `nginx_zugriffe_aggregiert.md`
- Eine einmalige Ressourcen-Momentaufnahme (RAM/Swap/Disk/Load) → `ressourcen_momentaufnahme.txt` — **kein historischer Verlauf**, da kein Prometheus/Grafana/Monitoring-Tool installiert ist (geprüft, keine Treffer)

## Was nicht vorhanden ist

- Kein Prometheus, Grafana, Matomo, Plausible oder vergleichbares Analytics-/Monitoring-Tool installiert
- Keine strukturierten Sessions/Scroll-/Verweildaten, keine Tabwechsel-Telemetrie, keine Frontend-Ladezeiten-Erfassung
- Keine historischen RAM/CPU/Disk-Verläufe — nur der eine Snapshot von heute
- API-Latenzen/Modellantwortzeiten/Kontextgrößen/Queuezeiten: nicht separat erfasst (wäre aus den Anwendungs-Logs einzeln rekonstruierbar, hier nicht gemacht — Zeitgrund)

## Warum anonymisiert statt Rohexport

ChatGPTs Auftrag wollte explizit anonymisierte Zugriffslogs. Rohe `access.log`-Zeilen enthalten echte IP-Adressen realer Besucher (Personendaten Dritter) — deshalb hier nur die aggregierte, gehashte Auswertung, keine Rohdatei kopiert.
