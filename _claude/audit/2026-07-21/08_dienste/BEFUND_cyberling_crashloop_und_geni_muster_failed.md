# Befund: cyberling-daemon Crash-Loop (selbstgeheilt, Ursache identifiziert) + geni-muster.service FAILED

Stichtag: 2026-07-21, während des Audits live beobachtet.

## cyberling-daemon.service — Crash-Loop während dieser Audit-Session, inzwischen wieder aktiv

Beim Sammeln der Dienststatus-Übersicht fiel `NRestarts=122` auf `cyberling-daemon.service` auf — Restart-Zähler stieg während der Beobachtung im 10-Sekunden-Takt (118→122). Log (`werkraum_logs/cyberling_daemon.log`):

```
psycopg2.OperationalError: connection to server at "localhost" (127.0.0.1), port 5432 failed: FATAL:  the database system is not yet accepting connections
DETAIL:  Consistent recovery state has not been yet reached.
```

**Ursache, zeitlich passend:** In dieser selben Session ist zuvor die Festplatte vollgelaufen (ENOSPC, siehe Memory `project_flextrawurst_datenatlas_audit`), Daniel hat danach Platz geschaffen. PostgreSQL ist offensichtlich durch das Disk-Voll-Ereignis in einen Crash-Recovery-Zustand gegangen ("Consistent recovery state has not been yet reached" = WAL-Replay läuft) und war für eine Weile nicht erreichbar — der cyberling-daemon (60s-Takt) hat in dieser Zeit ununterbrochen neu gestartet und ist sofort wieder gescheitert, weil er beim Start eine DB-Verbindung braucht.

**Status jetzt (Nachprüfung):** `systemctl is-active cyberling-daemon.service` → `active`. Log zeigt letzten erfolgreichen Start um 20:32:40 mit "letzter_tick geladen für 8 Cyberlinge" — selbstständig wiederhergestellt, sobald Postgres wieder bereit war. **Kein Fix nötig, nur Beobachtung** — passt zum Neustart-Verhalten wie vorgesehen (systemd `Restart=`, kein manueller Eingriff, kein Datenverlust erkennbar).

**Was das für den Datenatlas bedeutet:** Zeigt exemplarisch, wie sich ein Infrastruktur-Vorfall (volle Platte) in Kaskaden durch mehrere Dienste zieht (Postgres → cyberling-daemon), ohne dass es einen zentralen Alarm gibt, der das zusammenführt — jeder Dienst loggt nur seine eigene Symptomatik.

## geni-muster.service — FAILED (separates, nicht selbstgeheiltes Problem)

```
Jul 21 19:50:56 geni-muster.service: Main process exited, code=killed, status=15/TERM
Jul 21 19:50:56 geni-muster.service: Consumed 2min 20.776s CPU time, 818.4M memory peak, 512.0M memory swap peak.
Jul 21 19:58:31 geni-muster.service: Main process exited, code=killed, status=15/TERM
Jul 21 19:58:31 geni-muster.service: Consumed 3min 8.321s CPU time, 3.0G memory peak, 1.5G memory swap peak.
```
`status=15/TERM` = extern per SIGTERM beendet (nicht selbst abgestürzt) — Speicherverbrauch bis 3GB+1.5GB Swap im zweiten Versuch, steigend. Sieht nach einem externen Kill (OOM-Killer oder Timeout-Mechanismus) aus, nicht nach einem Absturz im eigenen Code. `ActiveState=failed`, aktuell **nicht laufend** — im Gegensatz zum cyberling-daemon hat sich das nicht selbst geheilt. Nicht weiter verfolgt (kein Log mit Stacktrace gefunden, Ursache nicht abschließend geklärt) — Fundstelle für Daniel, kein Fix versucht (laufende Systeme nicht ohne Auftrag anfassen).

## Rohdaten
- `service_details.txt` — NRestarts/ActiveState/ExecStart etc. für alle 17 geprüften Dienste
- `relevante_services.txt` — systemctl-Kurzstatus
- `alle_timer.txt` — alle systemd-Timer
