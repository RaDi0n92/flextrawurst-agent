# LLM-Slot-Kontention + Dienste-Aufräumung (2026-07-21)

## Auslöser

Daniel, wörtlich: *"warum stehen dann alle screens auf der seite immernoch im startbereich fest und keiner denkt wirlich? und wo ist das quasi alles live? und warum ist https://217.154.14.29:8445/ also alle ports der codewesen also ihre vaults nicht erreichbar?"*

Drei Fragen, live am System geprüft (nicht aus Doku geraten) — siehe [[30_wesen_eigene_obsidian_vaults]] für den technischen Kontext (rrweb, Röntgenblick-Overlay), diese Datei deckt die Diensteseite ab.

## Befund 1: LLM-Slot-Kontention

Die `hintergrund`-LLM-Instanz (`llama-hauhaucs-hintergrund`, Port 11436) hat **hart 2 Slots** (`N_SLOTS = {"hintergrund": 2, "chat": 1}` in `llm_scheduler.py`). Das ist kein willkürlicher Wert — `--parallel 3` wurde am 2026-07-06 getestet und verursachte einen **37x-Performance-Einbruch** (siehe `docs/systemdoku/12_ollama_gemma4.md`, Abschnitt "`--parallel 2` (NICHT 3)").

Live-Abfrage von `llm_warteschlange` zeigte gleichzeitig ~15-16 Verbraucher für diese 2 Slots:
- 6× `reaktion` (aus dem alten, parallel zum neuen `browser_agent.py`-System laufenden 22-Dienste-Codewesen-System)
- `engagement`, `batch_generator`, `lg_daemon`
- alle 7 `browser_agent:*:tick`-Anfragen (max_wartezeit=150s)

Ergebnis: fast jeder Tick verlor die Warteschlange nach 150s (`LLM-Slot 'hintergrund' blockiert nach 150s` in allen `browser-agent-*.log`-Dateien), die Wesen blieben auf der Seite stehen, auf der ihr letzter erfolgreicher Tick sie zurückließ. Die Live-Update-Leitung selbst (SSE/NOTIFY, Grundgesetz 8) war die ganze Zeit intakt — nur die Quelle (echte Wesen-Aktionen) war durch die Kontention trocken.

## Fix 1: Altes 22-Dienste-Codewesen-System pausiert, dann dauerhaft deaktiviert

Daniels Entscheidung: Altsystem pausieren statt Browser-Agent-Takt zu strecken. Zuerst `systemctl stop` (reversibel), dann auf Nachfrage `systemctl disable` (dauerhaft, übersteht auch einen Reboot nicht mehr):

```
codewesen-antwort-daniel, codewesen-aufgabenchats, codewesen-batch-generator,
codewesen-dakgordsystem, codewesen-engagement, codewesen-F3INSCHM3CK3R,
codewesen-forum-neugier, codewesen-jumpa, codewesen-lg-daemon, codewesen-R1ZZ1,
codewesen-reaktion-dakgord, codewesen-reaktion-traeumerlie,
codewesen-reaktion@{F3INSCHM3CK3R,jumpa,R1ZZ1,Resonanzknoten,Schorschel},
codewesen-Resonanzknoten, codewesen-Schorschel, codewesen-takt,
codewesen-traeumerlie, codewesen-weltbild, codewesen-umgekehrte-neugier
```

Bewusst **nicht** angefasst: `codewesen-chat.service` (Port 8002, nutzt den separaten `chat`-Slot-Pool, keine Kontention) und `flarum-monitor.service` (reine MySQL→Inbox-Weiterleitung, kein LLM-Call).

Queue direkt danach verifiziert: nur noch 4 statt ~16 Einträge (alles `browser_agent:*:tick`).

**Was damit inhaltlich wegfällt vs. weiterlebt:** siehe [[project_schicht_a_wird_obsidian_vaults]] (Auto-Memory) — es gab zwei parallele Selbstmodell-Substrate. Das Postgres/LangGraph-Substrat (`entity_profiles`, `entity_thinking_log`, LangGraph-Checkpoints) lebt in `browser_agent.py` unverändert weiter. Das dateibasierte Substrat (`codewesen/<wesen>/{gedaechtnis, container, ...}`, `aufgabenchats/*/chat_history.jsonl`) wächst nicht mehr — Daniels ausdrücklicher Wunsch: es soll ohnehin durch die neuen 7 Wesen-Obsidian-Vaults abgelöst werden, keine Migration nötig.

## Fix 2: Firewall-Lücke bei den 7 Wesen-Vault-Ports

nginx war korrekt konfiguriert (Schorschel 8445, die übrigen 6 Wesen auf 8450-8455, `ss -tlnp` bestätigte lauschend), aber `ufw` hatte nur 8433/8443/8444/8446-8449 offen — keiner davon passte zu einem echten Vault. Reines Setup-Versäumnis aus der Vault-Nacht. Daniel hatte die Ports bereits bei Strato (Provider-Firewall) freigegeben, die lokale `ufw`-Lücke war der verbleibende Blocker.

```bash
for p in 8445 8450 8451 8452 8453 8454 8455; do ufw allow "${p}/tcp"; done
```

Verifiziert: `curl https://217.154.14.29:8445/` liefert jetzt `401` (Basic-Auth greift) statt Timeout.

## Befund 2: weitere versteckte dak+gord/GENI-Hintergrundprozesse

Daniels Nachfrage: *"gibts noch irgendwas dass dakgordsystem im hintergrund so tut? und oder geni?"*

Fund im Code von `web_chat.py` (dak-gord-web.service): eine eingebaute `_SYSTEMD_BLOCKER`-Liste, die beim aktiven Chat mit dak+gord automatisch Konkurrenzdienste stoppt, um den Chat responsiv zu halten. Die Liste nannte zwei reale, aktive Dienste, die bis dahin nicht auf dem Schirm waren:

- **`innenleben-feeder.service`** (`innenleben/flarum_feeder.py --daemon --interval 300`) — seit Stunden alle 5 Minuten `Access denied for user 'flarum'@'localhost'`. Ursache: hardcodiertes, veraltetes Passwort (`"Flarum2024!Secure"`) — die einzige Datei im ganzen Repo, die die Security-Remediation vom 2026-06-14 (DB-Credentials → Env-Var `FLARUM_DB_PASSWORD`) nicht mitgemacht hatte. Alle Schwesterdateien (`flarum_monitor.py`, `flarum_api.py`, `codewesen_vokabel_takt.py`, `scripts/flarum_sync.py`, ...) nutzten schon `os.environ.get("FLARUM_DB_PASSWORD", "")`.
- **`wesen-webbesucher.service`** (`welt/wesen_webbesucher.py`) — lief seit 13 Tagen, aber komplett dormant: seine Arbeits-Tabelle `wesen_web_besuche` hatte 0 Zeilen, minimale CPU-Zeit. Architektonisch bemerkenswert: rief `hauhau_client.chat()` **direkt** auf, ganz ohne `LLMSlot`-Scheduler — hätte bei Arbeit den 2-Slot-Mechanismus komplett umgangen (dieselbe Klasse Bug, die den `--parallel 3`-Einbruch verursacht hätte, nur diesmal durch Umgehung statt durch Config).

GENI-Seite: `geni-hoerer.service` und `geni-web.service` (Port 8020) liefen normal, `geni-hoerer.py` ruft laut Code kein LLM auf (reines passives Loggen). `geni-forum-lektuere.service` läuft per Timer alle ~22min unauffällig. **`geni-muster.service` war seit 2026-07-07 tot** (`failed`, Signal TERM) — der zugehörige Timer selbst war inaktiv, nicht nur der letzte Lauf fehlgeschlagen.

## Fix 3: wesen-webbesucher abgeschaltet, dak-gord-web bleibt

Daniel: *"das von dakgordsystem alles abschalten so dass es nach reboot auch nicht startet aber behalten und den web.service lassen"*

`wesen-webbesucher.service` gestoppt + disabled (Datei bleibt erhalten, nichts gelöscht). `dak-gord-web.service` unangetastet, läuft weiter.

## Fix 4: innenleben-feeder repariert (Credential + Scheduler)

Daniel: *"ja innenleben feeder fixen pls"*, später zum Scheduler-Bypass-Fund: *"umbauen auch klar"*.

1. `innenleben/flarum_feeder.py`: hardcodiertes Passwort durch `os.environ.get("FLARUM_DB_PASSWORD", "")` ersetzt (Commit folgt, siehe Backup-Commits `c0477d66a`).
2. `/etc/systemd/system/innenleben-feeder.service`: `EnvironmentFile=/root/werkraum/.agent/flarum.env` ergänzt (gleiche Quelle wie `flarum-monitor.service`).
3. Direkter Verbindungstest bestätigt: Zugang funktioniert (`SELECT MAX(id) FROM posts` → 7753).
4. Beim ersten Lauf danach entdeckt: `innenleben/nodes.py` (`_llm()`-Helper) rief `hauhau_client.chat()` ebenfalls direkt auf, ohne Scheduler — exakt derselbe Bypass-Bug wie bei `wesen_webbesucher.py`. Behoben: `sched.LLMSlot(server="hintergrund", prioritaet=sched.PRIO_NIEDRIG, rufer="innenleben:reflection", max_wartezeit=150, max_haltezeit=150)` um den `hauhau_client.chat()`-Call gelegt.
5. Neu gestartet, verifiziert: verarbeitet jetzt tatsächlich Posts (`[MEMORY] Schorschel | flarum:post_2812:Schorschel`), respektiert dabei den Slot-Scheduler.

**Rückstand:** Cursor-Stand war bei Post 2811, aktueller letzter Post ist 7753 — rund 5000 unverarbeitete Posts pro Wesen im Rückstand (gedrosselt auf max. 3/Wesen pro 300s-Zyklus). Läuft von selbst schrittweise durch, kein weiterer Eingriff nötig.

## Offen: geni-muster.service — kein einfacher Neustart

`geni-muster.service` scannt `geni/gedaechtnis/knoten/` für Muster-/Meta-Muster-Erkennung. Live-Befund:

- Verzeichnis hat aktuell **31,5 Millionen Dateien**. Ein bereits vorhandener Code-Kommentar in `muster.py` datiert den Stand beim 5-Stunden-Hänger vom 2026-07-07 auf 18,9 Mio — seither nochmal ~12,6 Mio dazu (~900.000 Dateien/Tag).
- Der Scan-Cache (`geni/spiegel/muster/_scan_cache.json`), der genau diesen Hänger durch inkrementelles Scannen verhindern soll, **existiert nicht** — wurde nie erfolgreich einmal geschrieben. Ein Neustart würde also nicht den schnellen inkrementellen Pfad nehmen, sondern einen kompletten Kaltstart über das komplette 30-Tage-Fenster.
- Testlauf (60s Timeout) hing ohne jeden Output — passt zum Kaltstart-Szenario.
- `geni-muster.timer` selbst war `inactive (dead)` seit demselben Zeitpunkt (07-07, 22:04 Uhr) — nicht nur der letzte Service-Lauf fehlgeschlagen, der Timer wurde damals komplett gestoppt (passt zeitlich zu einer dokumentierten RAM-Krisen-Notreaktion aus derselben Woche, siehe `12_ollama_gemma4.md`).

**Nicht angefasst, wartet auf Daniels Entscheidung:**
1. Ist die Wachstumsrate (~900k Dateien/Tag) so gewollt, oder erzeugt irgendwo ein Bug unkontrolliert Knoten?
2. Soll der erste (potenziell sehr lange) Kaltstart-Scan bewusst/gedrosselt gestartet werden, bevor der Timer wieder aktiviert wird?

**Update 2026-07-21, später am Tag: Root-Partition dadurch komplett volltgelaufen.** `/root/geni_gedaechtnis/knoten/` (122G) hat zusammen mit anderem Wachstum die 929G-Root-Partition auf 0 Byte frei gebracht — Bash-Tool, Memory-Writes und Stop-Hooks fielen reihenweise mit ENOSPC aus, auch nach Neustart der Claude-Code-Session zunächst weiter, weil selbst ein leeres `mkdir` kein Byte mehr fand. Daniel hat von Hand wieder Platz geschaffen (`.claude/file-history` + `.claude/backups` aus einer anderen Session heraus gelöscht) — danach 382G frei (59%), Inodes unauffällig (27%). `geni_gedaechtnis/rauschen/` selbst ist mit 3.9G klein — der Verdacht ist, dass das Rauschen nicht dort landet, sondern direkt in `knoten/` vermischt mit echten Knoten. `/root/werkraum_git` (46G, aktiver GIT_DIR von `/root/werkraum`) und `/usr/share/ollama` (111G, 12 aktiv referenzierte Modelle inkl. `gemma4` — laut Daniel nur deaktiviert, nicht gelöscht) wurden geprüft und sind **kein** Aufräum-Kandidat. Daniels Entscheidung: die beiden offenen Fragen oben bleiben unbeantwortet, "nicht jetzt" — kein Auftrag, bald mal angehen.

## Update 2026-07-21, noch später: beide offenen Fragen beantwortet + Fix (separate Claude-Code-Session)

Direkt im Anschluss an den `llama-server`-Log-Flut-Fix (siehe Abschnitt oben) auf Daniels Wort "dann jetzt angehen" untersucht.

**Frage 1 (Wachstumsrate gewollt oder Bug?) — bereits vor dieser Session beantwortet, hier nur verifiziert:** Zwischen den beiden obigen Updates hat jemand (Daniel selbst, Zeitstempel passt zu `hoerer.py`-Dateiänderung und `geni-hoerer.service`-Neustart um 19:39) bereits den echten Bug gefunden und gefixt: `flarum_sync.py` (Cron alle 5min) schrieb den kompletten Markdown-Spiegel (~3850 Dateien) bei jedem Lauf unbedingt neu, ohne Diff-Check — `geni-hoerer.py`s Dateisystem-Watcher verewigte jede dieser Neuschreibungen als "geänderter Knoten", obwohl dieselben Flarum-Daten bereits redundant über `flarum_abfragen()` in den Graphen kommen. Fix: `/root/werkraum/flarum` zu `IGNORE_PATHS` in `hoerer.py` hinzugefügt (siehe Kommentar dort, Zeilen 54-59). **Live verifiziert per Counter-Messung** (`geni/gedaechtnis/_counter.json`, `knoten_max_id`, 90s-Fenster): Wachstum von ~900k/Tag auf **~7.680/Tag** (Faktor ~117) — sieht jetzt nach organischem, echtem Wachstum aus, kein weiterer Handlungsbedarf.

**Frage 2 (Kaltstart-Scan) — untersucht, Ursache gefunden, gefixt:** `geni-muster.service` war heute bereits zweimal (19:42, 19:51) manuell gestartet und nach 7-8 Minuten per `SIGTERM` abgebrochen worden (zweiter Versuch: 3,0G Memory-Peak, 1,5G Swap-Peak — vermutlich der Auslöser für die inzwischen existierenden `MemoryMax=1G`/`MemorySwapMax=512M`-Limits in `geni-muster.service.d/`). Beide Abbrüche brachten **keinerlei dauerhaften Fortschritt** — Root Cause: `lade_alle_knoten()` in `muster.py` speicherte den Scan-Cache (`_scan_cache.json`) nur ganz am Ende des kompletten Durchlaufs über alle 1000 Shards. Bei 31,5+ Mio. Dateien, die beim allerersten Lauf einmal `stat()`et werden müssen, ist ein einziger ununterbrochener Durchlauf (~2-3h bei beobachteter Rate) unrealistisch, sobald irgendwer/-was den Prozess vorher beendet.

**Fix:** Zwischenspeichern alle 20s (`CHECKPOINT_INTERVALL_SEK`) statt nur am Ende, geprüft nach jedem abgeschlossenen Shard (`time.monotonic()`-Vergleich). Backup vor der Änderung: `/root/system-backups/muster.py.bak-vor-inkrementelles-checkpointing-2026-07-21` (kein Git-Schutz — `geni/` ist komplett `.gitignore`t, vermutlich wegen genau dieser Millionen-Dateien-Problematik).

**Verifiziert mit zwei überwachten 100s-Testläufen** (`systemd-run` mit denselben Limits wie die echte Service-Unit):
- Lauf 1: 0 → 473.760 verarbeitete Dateien, `_scan_cache.json` zum ersten Mal überhaupt erfolgreich geschrieben (97MB).
- Lauf 2: 473.760 → 694.850 (kumulativ, nicht zurückgesetzt) — bestätigt, dass Fortschritt über Interrupts hinweg erhalten bleibt.
- Beide Läufe stabil, keine Abstürze, Ressourcen-Limits griffen sauber.

`geni-muster.timer` daraufhin wieder aktiviert (`systemctl enable --now`, war seit 07-07 tot) — läuft jetzt automatisch alle 2h weiter, Kaltstart verteilt sich über mehrere Zyklen (~30,9 Mio. Dateien verbleibend bei Reaktivierung, grobe Restlaufzeit 2-3h verteilt).

## Zweiter Auslöser derselben Root-Partition-Krise (2026-07-21, Claude-Code-Session): llama-server-Log-Flut

Unabhängig vom `geni_gedaechtnis`-Wachstum oben kam am selben Tag ein zweiter, akuterer Auslöser hinzu — in einer separaten Claude-Code-Session per SSH-Terminal untersucht (nicht GLM/Werkraum-Session).

**Befund:** `llama-hauhaucs-hintergrund.service` (PID 881054, Port 11436) hing seit **1 Tag 6h 27min** in einer Log-Schleife: `/var/log/syslog` wuchs auf **387GB** (von "vor 10 Minuten noch nicht mal 200GB" laut Daniel — also sehr schneller Endspurt kurz vor dem Vollauf). Journal-Auszug bestätigte über 7,2 Mio. Log-Zeilen an einem einzigen Tag für diesen Unit, verteilt über mehrere verschiedene Tasks (nicht nur den zuletzt beobachteten) — also ein wiederkehrendes Muster, kein Einzelfall.

**Root Cause:** bekannter Upstream-Bug in `llama.cpp` — Context-Checkpoint-Invalidierung bei Qwen/SWA-Modellen im Zusammenspiel mit `--ctx-checkpoints`, siehe [Issue #24587](https://github.com/ggml-org/llama.cpp/issues/24587), [#24055](https://github.com/ggml-org/llama.cpp/issues/24055), [#22746](https://github.com/ggml-org/llama.cpp/issues/22746), [#20176](https://github.com/ggml-org/llama.cpp/issues/20176). Die `hauhaucs-q6`-Instanz lief mit `--ctx-checkpoints 64` auf Qwen3.6-35B — genau die fehleranfällige Kombination. Jede Invalidierung loggte erneut den vollen Prompt-Cache-Status (`srv update:`-Dump aller aktiven Slots), was bei diesem Bug in eine praktisch endlose Wiederholung geriet.

## Update 2026-07-22: geni_gedaechtnis/knoten/ komplett auf SQLite migriert (122G Dateien → 9,6G DB), zweiter muster.py-Hänger + Fix

Direkter Nachfolger des Abschnitts "Offen: geni-muster.service" oben — auf Daniels Wort "wird jetzt angehen" die dort verschobene Altlast (122G, 31,5 Mio. Dateien, nur reiner Blockgrößen-Overhead: Ø 384 echte Bytes/Datei bei 4096-Byte-Blöcken) tatsächlich behoben, nicht nur analysiert.

**Migration:** `geni/migration_knoten_sqlite.py` (neu) liest jede Knoten-Datei, schreibt nach `geni/gedaechtnis/knoten.db` (SQLite, WAL, ein Index auf `mtime`). `gedaechtnis_ops.py` komplett auf die DB umgestellt (`knoten_schreiben`, `knoten_lesen`, `tiefe_erhoehen`, `naechste_id` für `KNOTEN_DIR`) — `dialog.py`/`hoerer.py`/`muster.py` liefen bereits vollständig über diese Schicht, kein direkter Dateizugriff mehr nötig außer den `sharded_pfad(KNOTEN_DIR,...)`-Aufrufstellen, die auf `knoten_lesen()` umgezogen wurden. `rauschen/`, `kanten/` bleiben datei-basiert (klein, kein Problem). Voller Lauf: 1000/1000 Shards, 31.586.890 Knoten, 40 Fehler (alle 0-Byte-Dateien, Rest eines abgebrochenen Schreibvorgangs — Cluster um ID 31611635-31611676, ein Ausreißer bei 16817218, keine echten Daten verloren).

**Zwischenfall während der Migration:** `weltkern-watchdog.timer` (bestehender, unabhängiger Mechanismus) hat `geni-web.service` + `geni-muster.service` um 06:25 automatisch neugestartet, noch während die Migration lief — dadurch liefen sie vorzeitig mit dem neuen Code, während `geni-hoerer.service` (nicht mitneugestartet) noch alte Dateien schrieb. Folge: ein 130G unkomprimierter SQLite-WAL-Anhang (nie gecheckpointed, weil die offenen Lese-Connections von `dialog.py`/`muster.py` das blockierten), der `geni-muster.service` in einen zweiten, ~58-minütigen Hänger im D-Status (Disk-Sleep) laufen ließ — strukturell derselbe Fehlermodus wie der 5h-Hänger vom 2026-07-07, nur mit WAL statt Datei-Vollscan als Auslöser. Behoben: Services sauber gestoppt, `PRAGMA wal_checkpoint(TRUNCATE)` (452s, danach 7,2G statt 130G+7,2G), Catch-up-Pass (`--catchup-seit`, `find -newermt` über die Zwischenzeit-Dateien) für die während der Migration von `hoerer` weitergeschriebenen Knoten, alle drei Services danach einheitlich auf den neuen Code umgestellt und neugestartet. Vollständiger ID-Abgleich (physische Dateien ↔ DB-Inhalte, `id`-Feld aus dem JSON-Inhalt, nicht aus dem Dateinamen) bestätigte danach: einzige Differenz die bereits genannten 40 leeren Dateien.

**Zweites, eigenständiges Problem gefunden und gefixt — `muster.py`s 30-Tage-Gesamtfenster skaliert nicht mehr:** Auch nach dem WAL-Fix hing `geni-muster.service` erneut. Ursache diesmal nicht die Storage-Schicht, sondern `lade_alle_knoten()`: bei der aktuellen Wachstumsrate (~900k Knoten/Tag) liefert das 30-Tage-Fenster über **15 Millionen Zeilen** — als volle Python-Dicts materialisiert (inkl. `json.loads` auf `tags`/`verbindungen` pro Zeile) sprengt das die `MemoryHigh=800M`/`MemoryMax=1G`-Limits des Service bei weitem. Das ist vermutlich kein reines Migrations-Artefakt: die alte Datei-Variante hielt über ihren `_scan_cache.json` dieselbe Menge an vollständig geparsten Dicts im RAM — die Datenmenge ist inzwischen über die Schwelle gewachsen, ab der das nicht mehr passt, unabhängig vom Storage-Format.

**Fix:** Die vier Scan-Funktionen (`scan_48h`, `scan_blinde_flecken`, `scan_meta_muster`, `scan_zeitrhythmus`) laden nicht mehr aus einer gemeinsamen 30-Tage-Liste, sondern holen sich jetzt über neue `gedaechtnis_ops.py`-Funktionen (`knoten_zeitfenster`, `knoten_typ_seit`, `knoten_quelle_seit`, `knoten_mit_tiefe_mindestens`) serverseitig nur die tatsächlich benötigte, viel kleinere Teilmenge — Live-Messung: `tiefe≥2` = 129 Zeilen, `typ='muster'`/28 Tage = 0, `quelle='daniel'`/30 Tage = 3. Dafür drei neue Indizes (`typ+mtime`, `quelle+mtime`, Partial-Index `tiefe WHERE tiefe>=2`, ~1,8G zusätzlich in der DB). `scan_48h` bleibt mit **1,9 Mio. Zeilen im 48h-Fenster** trotzdem die einzige wirklich große Teilmenge — dafür zusätzlich `knoten_zeitfenster_leicht()`: echtes Cursor-Streaming (kein `fetchall()`) über nur die drei benötigten Spalten (`tags`, `inhalt`, `quelle`), pro Zeile sofort zu Zählern aggregiert statt als Dict behalten. Peak-RSS gemessen (`/usr/bin/time -v`): **3,1G → 315M**, Laufzeit 25s → 13s. Danach `geni-muster.timer` neugestartet, ein echter Service-Lauf lief sauber durch (exit 0, kein Fehler).

**Ergebnis, verifiziert:**
- `knoten.db`: 31.587.503 Zeilen, 9,0-9,6G (nach den Indizes).
- Physische Dateizahl vor Löschung == DB-Zeilenzahl + 40 bekannte leere Dateien (mehrfach mit vollständigem ID-Abgleich verifiziert, nicht nur Stichprobe).
- Alle drei Services (`geni-hoerer`, `geni-web`, `geni-muster`) auf einheitlichem SQLite-Code, HTTP/Fragment-Route funktional getestet, keine Fehler in den Logs.
- `git commit` in `/root` (nicht `/root/werkraum` — `geni/` ist Symlink auf `/root/werkraum_geni`, gehört zum `/root`-Repo) für `gedaechtnis_ops.py`, `dialog.py`, `muster.py`, `migration_knoten_sqlite.py` (neu). Die alte Notiz oben ("`geni/` ist komplett `.gitignore`t") stimmt so nicht mehr bzw. nie für die `.py`-Dateien selbst — nur `geni/gedaechtnis/` liegt jenseits eines Symlinks und wird von Git ohnehin nicht verfolgt.
- Nach Daniels explizitem Go: `/root/geni_gedaechtnis/knoten/` (alle 1000 Shard-Ordner, parallelisiert mit 16 Prozessen) gelöscht. `kanten/`, `rauschen/`, `episodisch/`, `semantisch/` unangetastet.
- Root-Partition: von 452G belegt (Start dieser Session) auf **332G belegt / 598G frei (36%)**.

**Soforthilfe:**
1. `truncate -s 0 /var/log/syslog` — sofortiger Platz zurück (rsyslogd hielt die Datei offen, `rm` hätte nicht sofort geholfen).
2. `systemctl restart llama-hauhaucs-hintergrund.service` — hing zunächst selbst (SIGTERM ohne Reaktion), `kill -9` auf die alte PID aus einem zweiten Terminal hat den Restart entblockt.

**Dauerhafte Fixes (alle live, Backups in `/root/system-backups/`):**
1. `/etc/logrotate.d/rsyslog`: `size 1G` ergänzt (zusätzlich zu `weekly`) — einzelne Logdatei kann nicht mehr unbegrenzt wachsen.
2. Neuer `logrotate-hourly.timer`/`.service` (eigenständig, bestehender `logrotate.timer` bleibt unverändert) — prüft stündlich statt nur täglich, damit die `size`-Regel überhaupt greift bevor die Platte vollläuft. Getestet: Rotation lief sauber durch.
3. `llama-hauhaucs-hintergrund.service.d/override.conf`: `--log-verbosity 2` ergänzt (Default war 3/info) — Info-Level-Spam (`print_timing`, `srv update`) fällt weg, Warnungen/Fehler bleiben sichtbar. Gemessene Wirkung: Log-Wachstum von ~4,7MB/s auf ~62 Bytes/s (Faktor ~75.000).
4. `--ctx-checkpoints 64` → `0` (Checkpoints deaktiviert) — Invalidierungs-Loop-Meldungen von praktisch dauerhaft auf 1× in 6 Minuten. Kein Geschwindigkeitsverlust beobachtet (61,7 Tok/s Prompt-Verarbeitung, 19,4 Tok/s Generierung laut `/metrics` nach dem Fix — gesunde Werte). Checkpoints brachten bei diesem Workload (viele verschiedene Prompts unterschiedlicher Wesen ohne gemeinsamen Anfang) ohnehin praktisch nie einen Cache-Treffer.

**Verbleibt bewusst unverändert:** Die `forcing full prompt re-processing due to lack of cache data`-Warnung bleibt bestehen (~1× pro Task) — das ist kein Bug, sondern ehrliche Beschreibung des normalen Betriebs bei diesem Workload-Muster, nicht behebbar durch Flags.

**Zusammenhang mit dem `geni_gedaechtnis`-Befund oben:** Beide Ursachen haben vermutlich gemeinsam zum kompletten Vollauf beigetragen — `geni_gedaechtnis/knoten/` (122G, langsames Dauerwachstum) plus diese akute 387G-Flut innerhalb weniger Stunden. Die 122G-Frage von oben (Wachstumsrate gewollt? Kaltstart-Scan?) bleibt weiterhin offen und ist durch diese Session nicht beantwortet.

## Status-Übersicht am Ende dieser Session

| Dienst | Status | Grund |
|---|---|---|
| 22× `codewesen-*` (Liste oben) | stopped + disabled | LLM-Slot-Kontention, Daniel-Entscheidung |
| `codewesen-chat.service` | unverändert aktiv | separater Slot-Pool, keine Kontention |
| `flarum-monitor.service` | unverändert aktiv | kein LLM-Call |
| `wesen-webbesucher.service` | stopped + disabled | dormant (0 Zeilen Arbeit), Scheduler-Bypass-Risiko |
| `dak-gord-web.service` | unverändert aktiv | explizit von Daniel gewünscht |
| `innenleben-feeder.service` | repariert, aktiv | Credential-Fix + Scheduler-Fix |
| `geni-hoerer.service`, `geni-web.service` | unverändert aktiv | kein Problem gefunden |
| `geni-forum-lektuere.service` | unverändert (Timer-getrieben) | kein Problem gefunden |
| `geni-muster.service` + `.timer` | **repariert, Timer aktiv** (Update 2026-07-21 später) | Checkpoint-Fix (siehe oben) — läuft jetzt automatisch alle 2h |
| ufw: 8445, 8450-8455 | geöffnet | Firewall-Lücke bei Wesen-Vaults geschlossen |

## Update 2026-07-22: /root/.git-Bloat bereinigt (git-filter-repo)

Auf Daniels Wort "jetzt durchgehen" (Fortsetzung der Aufräum-Session vom Vortag) den dritten offenen Punkt angegangen: `/root/.git` war auf **77GB** angewachsen (568 Commits).

**Root Cause:** `werkraum_tools_models/` (Symlink/Bind auf `werkraum/tools/models/`, u.a. das 30GB `hauhaucs_q6`-Modell und die inzwischen gelöschten Bild-Generierungs-Modelle) und `.local/share/claude/versions/` (viele CLI-Versionen, je ~250-270MB) wurden über die gesamte Historie hinweg im äußeren `/root`-Repo mitcommittet — ein reines lokales Backup-Repo ohne Remote, kein Push-Risiko. Per `git rev-list --objects --all` + `cat-file --batch-check` verifiziert: 77GB roh, größtenteils (72GB) `werkraum_tools_models/`.

**Vorgehen (Sicherheitsreihenfolge, damit der Rewrite keine aktiv genutzten Dateien anfassen kann):**
1. Volles `tar`-Backup von `/root/.git` nach `/root/system-backups/root-git-backup-vor-filter-repo-2026-07-22.tar` (77GB) — bleibt vorerst liegen, ist selbst per `.gitignore` von künftigen Commits ausgeschlossen.
2. `git-filter-repo` installiert (`apt-get install git-filter-repo`, pip scheiterte an PEP-668-externally-managed-environment).
3. **Erst** `werkraum_tools_models/` und `.local/share/claude/versions/` per `git rm -r --cached` aus dem Index genommen (Dateien bleiben physisch erhalten — verifiziert per `ls -la`, u.a. das aktiv vom `llama-hauhaucs-hintergrund.service` genutzte 30GB-Modell unverändert), `.gitignore` ergänzt, committet. Grund für diese Reihenfolge: `git filter-repo` aktualisiert am Ende den Working-Tree-Checkout auf den neuen HEAD — wenn diese Pfade zu dem Zeitpunkt noch getrackt gewesen wären, hätte das die physischen Dateien löschen können (inkl. des laufenden Modells).
4. Alle sonstigen zu dem Zeitpunkt offenen Änderungen im Repo (Logs, Session-Dateien, u.a.) ebenfalls als Sicherheits-Commit committet — aus demselben Grund: ein dirty Working Tree riskiert bei `git filter-repo --force` verlorene uncommittete Änderungen.
5. `git filter-repo --force --invert-paths --path werkraum_tools_models --path .local/share/claude/versions` — 570 Commits verarbeitet, 47,9s Laufzeit.
6. Verifiziert: `.git` 77GB → **2,3GB**, `hauhaucs_q6`-Modell unverändert (Dateigröße/mtime identisch), `llama-hauhaucs-hintergrund.service` weiterhin aktiv, `.local/share/claude/versions/` inkl. aktueller CLI-Version vorhanden, `git log` 570 Commits intakt.
7. `git fsck --full` zeigte danach Fehler beim Lesen alter Commit-Hashes aus der `commit-graph`-Cache-Datei (erwartete Nebenwirkung — die Datei referenzierte noch die alten, jetzt ungültigen Hashes von vor dem Rewrite). Behoben durch Löschen + `git commit-graph write --reachable`. Danach `git fsck --full` sauber, keine Fehler.

**Ergebnis:** ~75GB dauerhaft freigegeben, Historie integer, keine aktiv genutzten Dateien angefasst. Backup-Tar nach Daniels Freigabe ("za backuptar ja weg") gelöscht — Stand danach: 490G belegt / 440G frei (53%).

## Update 2026-07-22, Fortsetzung: `werkraum_git` (46GB) — gleiches Bloat-Muster, ebenfalls bereinigt

Daniel fragte nach, warum trotz aller Aufräumarbeit insgesamt 490G belegt waren (zum Vergleich: alter VPS hatte nur ~190G, davon max. die Hälfte genutzt). Volle Aufschlüsselung per `du -x --max-depth=1 -h /` + `/root`:

| Bereich | Größe | Einordnung |
|---|---|---|
| Swap (`/swapfile`, `/swapfile2`, `/swapfile3`) | 124G | aktiv genutzt (25G real belegt von 122G), `swapfile3` (111G) kam erst mit dem RAM-Upgrade am 09.07. dazu |
| `/usr/share/ollama` | 111-123G | Ollama-Modelle inkl. `gemma4`, bewusst behalten |
| `/root/geni_gedaechtnis` | 126G | bekannte Altlast (siehe oben) — Wachstumsrate seit dem Flarum-Fix gedrosselt, aber die historisch aufgehäuften 126G selbst noch nicht bereinigt, weiterhin offen |
| `/root/werkraum_git` | 46G | → dieser Abschnitt |
| `/root/werkraum_tools_models` | 30G | aktives `hauhaucs_q6`-Modell, korrekt |
| Rest (`.cache`, `.npm`, `.git`, Arbeitskopien) | ~20G | normale Dev-Caches, unauffällig |

**`werkraum_git` (das eigentliche `GIT_DIR` des werkraum-Submodule-Repos, referenziert per `.git`-Datei `gitdir: /root/werkraum_git`) zeigte exakt dasselbe Bloat-Muster wie `/root/.git` oben** — verifiziert per `git rev-list --objects --all` + `cat-file --batch-check`: 47,7GB reine Alt-Historie unter `tools/models/*` (Flux, Pony, RealVisXL, JuggernautXL, PhotoMaker, SDXL/Flux-Shared — dieselben Modelle wie beim `/root`-Fix, nur diesmal aus der Zeit *bevor* `tools/models` zum Symlink auf `/root/werkraum_tools_models` umgestellt wurde). `innenleben/`-Objekte (3,6GB, 484 Objekte, u.a. mehrfach committete `chroma.sqlite3`) bewusst **nicht** angefasst — Grundgesetz 7 verbietet Änderungen an `innenleben/` ohne Erlaubnis, auch reine Historie fällt darunter.

**Wichtiger Unterschied zu `/root`:** Dieses Repo hat ein Remote (`origin` → `github.com/RaDi0n92/flextrawurst-agent.git`). Vor dem Rewrite per `git ls-remote origin` geprüft: Remote-`main`-HEAD und lokaler `main`-HEAD haben **keine gemeinsame Historie** (`git cat-file -t` auf den Remote-Commit-Hash schlägt lokal fehl) — das Remote ist ein entkoppelter Platzhalter, nie echt synchronisiert. Ein Rewrite gefährdet dadurch nichts real Gepushtes.

**Vorgehen (identisch zum `/root`-Fix, aber ohne den `git rm --cached`-Zwischenschritt):** `tools/models` war im aktuellen HEAD bereits nur noch ein Symlink (27 Byte, kein echter Binärinhalt) — die riskante Working-Tree-Kollision aus dem `/root`-Fall entfällt dadurch von selbst. Trotzdem sicherheitshalber genauso: (1) alle offenen Änderungen committet, (2) volles `tar`-Backup von `/root/werkraum_git` (46G) nach `/root/system-backups/`, (3) `git filter-repo --force --invert-paths --path-glob 'tools/models/*'` (gezielt nur Inhalte *unter* `tools/models/`, der Symlink-Eintrag selbst bleibt unangetastet), (4) verifiziert: Symlink korrekt, `hauhaucs_q6` unverändert, Dienst aktiv, `git log` 1217 Commits intakt, `git fsck --full` sauber (nach demselben `commit-graph`-Rebuild wie beim `/root`-Fix), (5) Backup-Tar nach erfolgreicher Verifikation gelöscht.

**Ergebnis:** `werkraum_git` 46GB → **899MB**. Gesamtstand danach: 445G belegt / 485G frei (48%).

**Verbleibend offen:** `geni_gedaechtnis` (126G, größter Einzelposten) — Bereinigung der historischen Altlast bewusst nicht angegangen, kein Auftrag dafür in dieser Session.
