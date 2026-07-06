# wesen_webbesucher.py

Migriert: 2026-07-06

**Was es tut**: Daemon, der auf Einträge in der Tabelle `wesen_web_besuche` wartet
(reaktion IS NULL), öffnet die angegebene URL per Playwright (headless Chromium),
macht einen Screenshot, extrahiert den Text der Seite.

**Wozu**: Ein Wesen bekommt von Daniel den Auftrag "schau dir diese Seite an" —
das Wesen "besucht" die Seite wirklich (nicht nur der Name wird genannt) und
schreibt eine ehrliche Reaktion (2-4 Sätze, Ich-Form) basierend auf dem, was
es tatsächlich gesehen hat.

**Warum als eigener Daemon**: Playwright-Browser-Start ist relativ teuer, läuft
deshalb entkoppelt vom Chat-Interface, pollt alle 30s auf neue Aufträge statt
synchron im Request-Pfad zu laufen.

**Migration**: War der erste migrierte Service (Pilotdatei) — einfachster Fall,
synchron, nicht-streamend, `requests.post` → `hauhau_client.chat(prompt, ...)`.

**Zusammenhang**: Läuft als `wesen-webbesucher.service` (systemd, enabled+active).
Ergebnis landet zusätzlich in `entity_denkstream` (source='web_besuch') fürs
Denkfenster/Prozesskamera-System.
