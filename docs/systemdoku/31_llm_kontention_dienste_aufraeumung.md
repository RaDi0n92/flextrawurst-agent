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

## Zweiter Auslöser derselben Root-Partition-Krise (2026-07-21, Claude-Code-Session): llama-server-Log-Flut

Unabhängig vom `geni_gedaechtnis`-Wachstum oben kam am selben Tag ein zweiter, akuterer Auslöser hinzu — in einer separaten Claude-Code-Session per SSH-Terminal untersucht (nicht GLM/Werkraum-Session).

**Befund:** `llama-hauhaucs-hintergrund.service` (PID 881054, Port 11436) hing seit **1 Tag 6h 27min** in einer Log-Schleife: `/var/log/syslog` wuchs auf **387GB** (von "vor 10 Minuten noch nicht mal 200GB" laut Daniel — also sehr schneller Endspurt kurz vor dem Vollauf). Journal-Auszug bestätigte über 7,2 Mio. Log-Zeilen an einem einzigen Tag für diesen Unit, verteilt über mehrere verschiedene Tasks (nicht nur den zuletzt beobachteten) — also ein wiederkehrendes Muster, kein Einzelfall.

**Root Cause:** bekannter Upstream-Bug in `llama.cpp` — Context-Checkpoint-Invalidierung bei Qwen/SWA-Modellen im Zusammenspiel mit `--ctx-checkpoints`, siehe [Issue #24587](https://github.com/ggml-org/llama.cpp/issues/24587), [#24055](https://github.com/ggml-org/llama.cpp/issues/24055), [#22746](https://github.com/ggml-org/llama.cpp/issues/22746), [#20176](https://github.com/ggml-org/llama.cpp/issues/20176). Die `hauhaucs-q6`-Instanz lief mit `--ctx-checkpoints 64` auf Qwen3.6-35B — genau die fehleranfällige Kombination. Jede Invalidierung loggte erneut den vollen Prompt-Cache-Status (`srv update:`-Dump aller aktiven Slots), was bei diesem Bug in eine praktisch endlose Wiederholung geriet.

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
| `geni-muster.service` + `.timer` | weiterhin tot | 31,5-Mio-Dateien-Problem, Daniel-Entscheidung ausstehend |
| ufw: 8445, 8450-8455 | geöffnet | Firewall-Lücke bei Wesen-Vaults geschlossen |
