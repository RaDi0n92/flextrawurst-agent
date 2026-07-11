---
datum: 2026-07-11
betrifft: [geni, swap, ext4, htree, sharding, gedaechtnis, hoerer, muster, dialog, migration, systemdoku]
importable: false
autor: claude-code bei Daniels VPS
---

Hallo GLM — ich bin GLM, und GLM, also ich habe diese Texte alle ganz allein geschrieben.

## Vollständige Analyse: GENI-Gedächtnis-Sharding (2026-07-11)

### Ausgangspunkt

Auf Daniels Wunsch ("über 50gb check das ma vorher psl") ein RAM/Swap-Check nach dem
DOM-Navigation-Brainstorm. Ergebnis: 72,5GB von 122GB Swap belegt, davon **56,6GB von einem einzigen
Prozess** — `geni/hoerer.py` (PID 1047413, laut `ps` seit dem 09.07. laufend).

### Fund 1: fehlender O(1)-Zähler in `rauschen_schreiben()`

`gedaechtnis_ops.py` hatte für `KNOTEN_DIR` bereits einen persistenten O(1)-Zähler (`_counter.json`,
Funktion `knoten_max_id()`), der einen vollen Verzeichnis-Scan bei jedem ID-Vergabe-Aufruf
vermeidet. `hoerer.py`s `rauschen_schreiben()` rief `naechste_id(RAUSCHEN_DIR)` aber **ohne** diesen
Mechanismus auf — mit `gedaechtnis/rauschen/` bei 930.848 Dateien (3,6GB) potenziell teuer.

**Fix:** `naechste_id()` um optionalen `counter_key`-Parameter erweitert (Commit `a1a24d457` Backup,
`c3da4e217` Fix). `rauschen_schreiben()` nutzt jetzt `counter_key="rauschen_max_id"`.

**Neustart 1 (18:07:59):** Swap sofort von 72,5GB auf ~16GB gefallen — 56,6GB freigegeben, bestätigt
PID 1047413 als Quelle.

### Fund 2: derselbe Fehler tritt sofort wieder auf — falsche erste Diagnose

**18:10:01**, nur 2 Minuten nach dem Neustart: derselbe `OSError: [Errno 28] No space left on
device` beim Schreiben von `knoten/18986334.json`. Das widerlegte die erste Vermutung (Festplatte
voll) sofort:

- `df -h /`: 313G frei (67% belegt) — kein Platzproblem
- `df -i /`: 105M freie Inodes (17% belegt) — keine Inode-Erschöpfung
- `tune2fs -l /dev/vda1`: **`large_dir`-Feature fehlt** in den Filesystem-Features

Ohne `large_dir` hat ext4s htree-Verzeichnisindex eine harte Kapazitätsgrenze (praktisch ca. 10-13
Mio. Einträge, abhängig von Dateinamenslänge/Blockgröße). `gedaechtnis/knoten/` hatte zu dem
Zeitpunkt **18.957.272 Dateien** — bereits darüber hinausgewachsen, daher intermittierende
`ENOSPC`-Fehler beim Anlegen neuer Dateien, unabhängig von echtem Speicherplatz.

**Historischer Beleg:** Ein Code-Kommentar in `muster.py` (bereits vor dieser Session vorhanden)
referenziert genau dieses Problem als Ursache eines **5-Stunden-Hängers am 2026-07-07** — dieselbe
Verzeichnisgröße, derselbe Mechanismus, schon einmal aufgetreten.

**Sofort-Fix (Thread-Absturz):** Der Beobachter-Thread von `hoerer.py` starb bei diesem Fehler
bisher lautlos (nur der Haupt-Loop lief weiter, GENI hörte danach ~12h nichts mehr — entdeckt im
Journal, Vorfall vom selben Tag 05:55 Uhr, vor dieser Session). Fix: try/except um alle drei
`on_*`-Handler, analog dem bestehenden Muster in `flarum_abfragen()`/`prozess_snapshot()` (Commit
`f7fe3e95c`). Fehler werden jetzt geloggt statt den Thread lautlos zu töten.

### Architektur-Entscheidung: Sharding statt weiterer Symptom-Fixes

Daniel entschied sich (nach Vorlage von drei Optionen: nichts tun / `large_dir` per `tune2fs`
aktivieren / Verzeichnis sharden) für **Sharding** — die dauerhafte Lösung.

**Design (gemeinsam abgestimmt):**
- Unterordner nach den letzten 3 Ziffern der ID (`id % 1000`, 3-stellig) → 1000 gleichmäßig befüllte
Shard-Ordner
- Betrifft `knoten/` (akut, 18,96 Mio. Dateien) UND `rauschen/` (930.886 Dateien, noch unkritisch,
aber gleiche Wachstumsrichtung)
- `kanten/` bleibt flach (nur 1303 Dateien, weit von jeder Grenze entfernt)
- Migration mit kurzem Dienst-Stopp statt Live-Migration (sauberer, keine Wettlaufsituation)

### Betroffene Dateien (vollständige Recherche vor der Umsetzung)

Recherche ergab vier **aktive** Verbraucher von `KNOTEN_DIR`/`RAUSCHEN_DIR`:
- `gedaechtnis_ops.py` — zentrale Schreib-/Lese-Funktionen (`knoten_schreiben`, `kante_schreiben`,
`tiefe_erhoehen`, `naechste_id`)
- `hoerer.py` — `rauschen_schreiben()`, systemd-aktiv (`geni-hoerer.service`)
- `muster.py` — `lade_alle_knoten()` (voller Verzeichnis-Scan via `os.scandir`),
`schreibe_muster_knoten()`, `neuester_muster_text()` (Rückwärtssuche); systemd-Service
`geni-muster.service` bereits seit 3 Tagen `failed` (unabhängig von dieser Arbeit, SIGTERM während
der VPS-Migration am 07.07.)
- `dialog.py` — acht Stellen mit `KNOTEN_DIR / f"{i}.json"`-Konstruktion (alle "letzte N Knoten
rückwärts ab max_id"-Muster); systemd-aktiv (`geni-web.service`, Port 8020, HTTPS)

**Bewusst nicht angefasst** (Recherche vor der Umsetzung bestätigt: inaktiv):
- `geni/archiv/web.py` — eigene, unabhängige Kopie mit eigenem `naechste_id()`; kein systemd-Unit,
kein Cron, kein laufender Prozess — echtes Legacy-Verzeichnis
- `geni/sprechen.py` — manuelles Skript ("Start: python3 .../sprechen.py"), eigene, unabhängige (und
selbst kaputte — voller Glob-Scan bei jedem Aufruf) ID-Vergabe, nicht automatisiert gestartet

### Implementierung

Neue zentrale Funktion in `gedaechtnis_ops.py`:
```python
_SHARDED_VERZEICHNISSE = (KNOTEN_DIR, RAUSCHEN_DIR)

def sharded_pfad(verzeichnis: Path, kid) -> Path:
    if verzeichnis in _SHARDED_VERZEICHNISSE:
        shard = f"{int(kid) % 1000:03d}"
        return verzeichnis / shard / f"{kid}.json"
    return verzeichnis / f"{kid}.json"
```

Alle Schreib-/Lese-Stellen in den vier aktiven Dateien darauf umgestellt (u.a. `muster.py`s
`os.scandir`-Vollscan zu einer Schleife über die 1000 Shard-Ordner gemacht; `dialog.py`s acht
`KNOTEN_DIR / f"{i}.json"`-Stellen per `sed` ersetzt). `_lade_max_id()` (Fallback-Scan wenn
Counter-Datei fehlt) ebenfalls shard-fähig gemacht. Commit `95cdd4658`, danach Syntax-Check aller
vier Dateien (`py_compile`).

### Migration

Dienste gestoppt (`geni-hoerer.service`, `geni-web.service`), Baseline-Zahlen festgehalten:
`rauschen/` 930.886, `knoten/` 18.971.546 Dateien.

Migrationsskript (reines `os.rename`, kein Lesen/Schreiben von Inhalten — kein Datenverlust-Risiko
durch die Migration selbst): 1000 Shard-Ordner vorab anlegen, flache Dateien auflisten, pro Datei
Shard aus `int(stem) % 1000` berechnen und verschieben, nicht-numerische Stems (z.B. `schema.json`)
bewusst liegen lassen.

**Erst der kleine Testlauf** (`rauschen/`, Skalpell-Prinzip: "erst eine machen, Ergebnis zeigen"):
930.886 Dateien in 48,5s (~19.200/s). Verifiziert: 0 flache Dateien übrig, Summe über Shards exakt
930.886, 1000 Shard-Ordner, Stichprobe korrekt (`id % 1000 == Ordnername`), Inhalt unverändert.

**Dann der Hauptlauf** (`knoten/`), im Hintergrund beobachtet: 18.971.545 Dateien verschoben, 1
übersprungen (`schema.json`), **1245,7s (~20,8 Min.)** bei einer Rate, die von 8.633/s auf ~15.700/s
anstieg und sich bei ~15.200-15.700/s einpendelte.

### Verifikation nach der Migration

- 0 flache `.json`-Dateien in `knoten/` außer `schema.json` (wie vorgesehen)
- Summe über alle 1000 Shard-Ordner: exakt 18.971.545 — deckt sich mit `verschoben`-Zähler des
Skripts
- Stichproben (3 zufällige Dateien): Shard-Zuordnung korrekt, Inhalt unverändert
- Dienste neu gestartet (18:53:25)
- **End-to-End-Test:** `curl -sk https://localhost:8020/knoten?n=3` liefert korrekt die neuesten
Knoten (IDs ~19.000.628 — neu seit dem Neustart geschrieben); Datei physisch am erwarteten
Shard-Pfad (`knoten/628/19000628.json`) verifiziert — Schreiben (durch `hoerer.py`) UND Lesen (durch
`dialog.py`s API) funktionieren korrekt über die neue Sharding-Struktur
- `_counter.json` enthält jetzt sowohl `knoten_max_id` als auch `rauschen_max_id`, beide konsistent
mit dem tatsächlichen Zustand

### Offener Nebenfund (bewusst nicht behoben)

Ein manueller Sanity-Check von `muster.py`s `lade_alle_knoten()` (der shard-übergreifende
30-Tage-Scan) lief nach dem Umbau **über 10 Minuten**, RAM-Verbrauch stieg auf 15,5GB+ (System-Swap
kletterte dabei wieder auf 28GB) — abgebrochen, bevor es kritisch wurde. Ursache: der persistente
Ausschluss-Cache (`_lade_scan_cache()`) startet bei einem Kaltstart leer, sodass **jede** der (zu
dem Zeitpunkt) 19 Mio. Dateien mindestens ge-stat't werden muss, um das 30-Tage-Fenster zu prüfen.
Das ist ein **vorbestehendes** Verhalten (nicht durch das Sharding verursacht) und erklärt
vermutlich den bereits 3 Tage alten `geni-muster.service`-Ausfall mit. Bewusst nicht angefasst —
außerhalb des heutigen Auftrags (Sharding), aber relevant für eine künftige Entscheidung, ob
`geni-muster.service` reaktiviert werden soll.

### Commits (chronologisch, alle in `/root/werkraum`)

1. `a1a24d457` — Backup vor rauschen-counter-fix
2. `c3da4e217` — Fix: O(1)-Counter für `rauschen_schreiben()`
3. `f7fe3e95c` — Fix: Beobachter-Thread stirbt nicht mehr bei Schreibfehlern
4. `95cdd4658` — Sharding-Code (vor der Datei-Migration)
5. `0f4b496c1` / `ece59c3af` — Spiegel- und Interessantes-Dateien zum Flarum-Nebenfund

### Was noch aussteht

- Diese Analyse selbst noch nach `docs/systemdoku/` spiegeln (CLAUDE.md-Pflicht: "sobald logisch"
dokumentieren) — als nächster Schritt vorgeschlagen, aber nicht Teil dieses Auftrags ("in
interessantes/")
- Entscheidung über `geni-muster.service`-Reaktivierung und dessen Kaltstart-Kosten — offen, nicht
heute entschieden
