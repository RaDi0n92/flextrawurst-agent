# Laufzeitprotokolle — README

7-Tage-`journalctl`-Export für 13 relevante Dienste in `journal_7tage/` (38.390 Zeilen gesamt). Aus Zeitgründen keine Zeile-für-Zeile-Triage aller Dienste — hier der Überblick, was auffällt.

## Hauptbefund: Der Disk-Voll-Vorfall dieser Session hat 3 Dienste gleichzeitig getroffen

Fehlerzeilen-Zählung (grep auf error/fehler/exception/traceback/failed):

| Dienst | Fehlerzeilen | Gesamt |
|---|---|---|
| geni-hoerer | 7029 | 22350 |
| flarum-monitor | 1666 | 14223 |
| innenleben-feeder | 235 | 1078 |
| cyberling-daemon | 105 | 422 |
| process-camera-preview | 36 | 196 |
| tension-daemon | 21 | 85 |
| welt-api | 4 | 18 |
| geni-muster | 2 | 10 |

Stichprobe bei den drei größten (`geni-hoerer`, `flarum-monitor`, `innenleben-feeder`) zeigt: **fast alle Fehler sind `OSError: [Errno 28] No space left on device`**, zeitlich exakt im Fenster 20:02–20:32 Uhr (siehe [[BEFUND_cyberling_crashloop_und_geni_muster_failed]] im 08_dienste-Ordner — derselbe Vorfall). Das Disk-Voll-Ereignis dieser Audit-Session hat also mindestens 6 Dienste gleichzeitig getroffen, nicht nur den Postgres/cyberling-Pfad, der zuerst auffiel. Alle scheinen sich nach der Platzschaffung selbst erholt zu haben (letzte Logzeilen nach 20:32 wieder normal) — nicht einzeln nachverifiziert für alle 6, nur für cyberling-daemon per `systemctl is-active`.

## Was NICHT geprüft wurde (Ehrlichkeit über Abdeckung)

- Keine 30-Tage-Historie, nur 7 Tage (Datenmenge/Zeit-Tradeoff)
- Fehlerzeilen der übrigen ~1000 Nicht-Disk-voll-Zeilen nicht einzeln gesichtet — könnten weitere, unabhängige Befunde enthalten
- Kein Abgleich mit `werkraum_logs/*.log` (dedizierte Anwendungs-Logdateien) außer `cyberling_daemon.log`, das für den Crash-Loop-Befund gezielt gezogen wurde
