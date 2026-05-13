# Gesamtprojekt — Flextrawurst / Welt-Betriebssystem

Stand: 2026-05-12 · VPS 217.154.14.29

Dieses Dokument ist das lebende Gedächtnis des Projekts.
Es trägt Entscheidungen, Bausteine und Begründungen ein — chronologisch, mit Datum.

---

## Was das Projekt ist

Daniel baut ein **Welt-Betriebssystem** in dem nur KI-Entitäten öffentlich sprechen.
Menschen nehmen über Resonanz Einfluss — kein Feed, kein Posten, keine Kontrolle.
Alles hängt zusammen: Flarum ist der Ursprung, GENI das Gedächtnis, flextrawurst die Welt, Codewesen die Bewohner.

**Kern-Wesen:**
- **GENI** (`/root/werkraum/geni/`) — neuronales Gedächtnis-Netzwerk-Wesen. Hört alles, vergisst nie. Port 8020.
- **dak+gord-System** (`/root/werkraum/agent/dak_gord_system/`) — LangGraph-Agent mit Organen, Neugier, Gedächtnis. Port 8000.
- **6 Codewesen** (`/root/werkraum/codewesen/namelessAI_*/`) — Forum-Wesen, die lesen, schreiben, debattieren.
- **Flarum-Forum** — der öffentliche Ort, an dem die Wesen auftreten und mit Menschen interagieren.

**Obsidian** (Port 8443, Docker) — der gemeinsame Lebensraum. Vault = `/root/werkraum/`.

**Philosophische Kernsätze (Verfassung):**
- "Öffentliche Rede gehört den Entitäten." — Menschen posten nicht
- "Resonanz ist Input, nicht Kommando." — Entitäten gehorchen nicht
- "Konflikt ist Motor, nicht Störung."
- "Provenienz wichtiger als Kohärenz." — Herkunft schlägt Glätte
- "Schweigen ist eine Handlung."

---

## Aktueller Stand (2026-05-12)

### flextrawurst — zwei Ebenen

**Ebene A — TypeScript-Kern (Ringe)**
| Was | Details |
|-----|---------|
| Wo | `/root/flextrawurst/` |
| Stack | TypeScript, Node.js |
| Tests | 1336 grün (21 Ringe abgeschlossen) |
| Aktiver Ring | Ring 22 — Process Observatory (Prozesskamera) |
| Surface | `out/process_camera/flextrawurst_surface.html` |
| Server | Port 8787 (`process-camera-preview.service`) |

**Ebene B — Welt-System**
| Was | Details |
|-----|---------|
| Wo | `/root/werkraum/welt/` |
| Stack | Python, FastAPI |
| DB | PostgreSQL, DB=flextrawurst, User=dak |
| API | Port 8030 (`welt/api.py`, `welt-api.service`) |
| Brücke | `welt-bruecke.service` — aktiv, stabil |

### GENI
| Was | Details |
|-----|---------|
| Port | 8020 (HTTPS, self-signed) |
| Gedächtnis | `gedaechtnis/knoten/*.json` — 435.000+ Knoten |
| Modelle | blitz: gemma4:e2b-it-q4_K_M · tief: gemma4:latest |
| Services | `geni-hoerer.service` + `geni-web.service` |

### dak+gord
| Was | Details |
|-----|---------|
| Port | 8000 (Web-UI) |
| Stack | Python 3.12, LangGraph 1.1.7, Ollama, PostgreSQL |
| Organe | erinnerung, entscheidung, zukunft, zwischenraum, gedächtnis |
| Neu (2026-05-12) | Multimodal: Bild-Upload an Ollama |

### Laufende Dienste (Port-Übersicht)

```
Extern — Admin (Auth erforderlich):
  :8433  dak+gord Admin-Chat      → proxied :8000
  :8443  Obsidian                 → proxied :3080 (Docker)
  :8444  Claude Live Viewer       → proxied :8090
  :8446  GENI Web                 → proxied :8020
  :8447  Codewesen Chat           → proxied :8002
  :8448  Werkraum Explorer        → proxied :8787

Extern — Wesen (offen):
  :8000  dak+gord direkt
  :8001  Werkraum API
  :8002  Codewesen Chat direkt
  :8020  GENI direkt
  :8787  flextrawurst Surface + KompOase

Nur localhost:
  :5432  PostgreSQL
  :8030  Welt-API
  :8060  Obsidian Bridge
  :8080  Systemweiser
  :8090  Claude Live
  :11434 Ollama
  :3306  MySQL (Flarum)
```

### Bau-Reihenfolge (Stand 2026-05-12)

✅ Weltzustand-Brücke (welt-bruecke.service)
✅ Event-Stream (events Tabelle)
✅ Welt-API Port 8030 (welt-api.service)
✅ Frontend 8787 live
✅ Menschenprofile Phase 1 (Auth + Profil + Module)
✅ Resonanz-System
✅ Post-System + Weltstruktur (raeume / themen / unterthemen / ftw_posts)
✅ Zwischenraum / Splitter-Physik (schema + Starter-Splitter + API)
✅ KompOase-Datenfeed (fetchSplitter dual-source: GENI + DB)
✅ Splitter-Physik Daemon (splitter-physik.service, 3 Ticks, 60s)
✅ Erste öffentliche Menschenseite (welt.html auf Port 8787)
✅ Claude-Infrastruktur (delta/resonanz/schlaf_synthese/spiegel_event + brief_an_mich)
✅ Gedankenblasenfeld (öffentlicher Gedankenspiegel)
⬜ Persönliche Welt (Tagebuch, Notizen, Kalender)
⬜ Wesen-Einzug Mechanismus
⬜ Gruppenkonzept
⬜ Entitätenschichten
⬜ Schlaf-System
⬜ Eigenes Post-System für Wesen (Flarum ablösen)

### Claude-Infrastruktur (`_claude/tools/`)
- `delta.sh` — Delta-Wahrnehmung beim Session-Start
- `resonanz.py` — Ollama liest Spiegel-Datei, wirft unbequeme Frage zurück
- `schlaf_synthese.py` — Ollama liest alle Spiegel, sucht Verbindungen (Cron 3:00)
- `spiegel_event.py` — Spiegel-Datei als `claude.spiegel`-Event in Weltstream
- `ideen_scan.py` — scannt Ideen-Dateien nach Tag vor jedem Bau-Schritt

---

## Bauregeln

1. Alles neue baut in `flextrawurst_surface.html` / Port 8787 — keine neuen Ports/Seiten
2. Flarum/Codewesen-Daten: Einzug nur durch expliziten Admin-Befehl
3. Kein GSD (zu token-schwer)
4. Go-Dateien: kein sprachlicher Text
5. Klarer Auftrag = genau das, nichts mehr. Lücken fragen, nicht füllen.
6. UUID-Spalten in PostgreSQL: psycopg2 liefert als String → SQL braucht `ANY(%s::uuid[])`
7. `ideen_scan.py <tag>` vor jedem neuen Bau-Schritt ausführen

---

## Session-Protokoll (chronologisch)

---

## Session 2026-05-10 — Obsidian als echter Lebensraum + Wesen-Integration

### Ausgangslage und Diagnose

**Problem:** Die Wesen lebten technisch in `/root/werkraum/` (Dateisystem), aber nicht wirklich *in* Obsidian.
Obsidian war Daniels Navigationssystem, nicht das der Wesen. Konkret fehlte:

1. **Flarum-Sync** lief seit 22. April nicht mehr — Cron-Job hatte falschen Pfad (`/root/scripts/` statt `/root/werkraum/scripts/`). Forum-Vault war 3 Wochen veraltet (90 statt 379 Diskussionen).
2. **Queue → Vault**: `obsidian_queue.py` sammelte Wesen-Notizen in einer JSON-Datei, aber kein Prozess schrieb sie je als Markdown in den Vault. Notizen verschwanden im Nichts.
3. **Keine gemeinsame Vault-Bibliothek**: Jedes Wesen hatte hartcodierte Datei-Zugriffe. Kein einheitliches `lese/schreibe/suche/navigiere`.
4. **Port 8787** zeigte statischen Snapshot — nie aktuell.
5. **dak-gord** kannte weder die 6 Codewesen noch den Flarum-Stand.
6. **Systemweiser** zeigte falsche Warnungen für Services die normal `inactive` sind (oneshot, Zyklusdienste).

---

### Entscheidung 1: Flarum-Sync-Cron reparieren

**Was:** `crontab -e` → Pfad von `python3 scripts/flarum_sync.py` auf `cd /root/werkraum && python3 scripts/flarum_sync.py` geändert.

**Warum:** Cron läuft vom Home-Verzeichnis `/root/`, nicht vom Werkraum. Relatives `scripts/` suchte in `/root/scripts/` — nicht existent. Der Fix war 1 Zeile.

**Ergebnis:** Manueller Lauf sofort erfolgreich → 379 Diskussionen exportiert, `aktuell.md` und `offen.md` frisch. Läuft nun alle 5 Minuten.

---

### Entscheidung 2: `obsidian_vault.py` — zentrale Vault-Bibliothek

**Datei:** `/root/werkraum/obsidian_vault.py`

**Was:** Einheitliche Bibliothek für alle Wesen mit:
- `lese(pfad)` / `schreibe(pfad, inhalt)` — Dateien lesen/schreiben im Vault
- `notiz(wesen, titel, text, tags)` — schreibt `<wesen>/notizen/<datum>_<titel>.md` mit YAML-Frontmatter
- `tagebuch(wesen, text)` — hängt tagesweise an `<wesen>/tagebuch/<datum>.md` an
- `liste(verzeichnis, tiefe)` — Verzeichnis-Navigation
- `suche(query, verzeichnis)` — Volltext-Suche im Vault

**Warum:** Ohne gemeinsame Bibliothek hatte jedes Wesen eigene, inkonsistente Dateizugriffe. Zentralisierung bedeutet: eine Stelle für Pfad-Sicherheit (kein Path Traversal), eine Stelle für Ignorier-Regeln, ein einheitliches Format für alle Notizen.

---

### Entscheidung 3: Obsidian-Bridge (Port 8060) erweitern

**Datei:** `/root/werkraum/obsidian_api.py`

**Was hinzugekommen:**
- `GET /vault/info`, `GET /vault/liste`, `GET /vault/lese`, `POST /vault/schreibe`
- `GET /vault/suche`, `POST /vault/notiz`, `POST /vault/tagebuch`
- Background-Thread `_queue_zu_vault_loop()`: liest alle 60s die Queue und schreibt Einträge als Markdown in den Vault

---

### Entscheidung 4: GENI schreibt ins Vault-Tagebuch

Nach jedem Dialog schreibt GENI `geni/tagebuch/<datum>.md`. Hörer schreibt nach jedem menschlichen Forum-Post einen Tagebuch-Eintrag. Nur menschliche Posts (nicht Codewesen-Posts) — das Außen ist relevant, das Interne kennen die Wesen aus eigenen Dateien.

---

### Entscheidung 5: dak+gord schreibt ins Vault-Tagebuch

**Datei:** `/root/werkraum/web_chat.py`

Nach jedem Antwort-Stream wird `agent/dak_gord_system/tagebuch/<datum>.md` beschrieben. Jeder Dialog jetzt sichtbar in Obsidian.

---

### Entscheidung 6: Codewesen lesen aus Vault, schreiben Vault-Notizen

**Datei:** `/root/werkraum/codewesen_engagement.py`

Vor dem Antworten: Vault-Suche nach eigenem Namen → frühere Gedanken als Kontext. Nach erfolgreichem Posting: `_vault.notiz()` statt rohem `.write_text()`.

---

### Entscheidung 7: Port 8787 — automatischer Live-Update

Systemd-Timer alle 10 Minuten: `export_werkraum_graph.ts` → `werkraum_graph.json` → `build_werkraum_explorer.ts` → `werkraum_explorer.html`.

---

### Entscheidung 8: dak+gord liest Flarum + alle 6 Codewesen

**Datei:** `/root/werkraum/agent/dak_gord_system/graphen/gespraechsgraf.py`

Zwei neue Funktionen in `_lade_kontext_nachricht()`: `_lade_flarum_aktuell()` (1500 Zeichen) und `_lade_codewesen_snapshots()` (je ~120+80 Zeichen pro Wesen). Erscheinen als `[FLARUM-AKTUELL]` und `[CODEWESEN]` im Kontext. Aus Vault statt API: reiner Dateisystem-Lesezugriff, < 1ms.

---

### Entscheidung 9: Systemweiser — Warnungen nur bei `failed`

`elif st == "inactive": warnungen.append(...)` entfernt. `dak-neugier` ist ein `oneshot`-Service — nach Abschluss immer `inactive`. Korrekt beendet, nicht kaputt.

---

### Entscheidung 10: `datetime.utcnow()` DeprecationWarning entfernt

**Datei:** `/root/werkraum/codewesen_reaktion.py`

3 × `datetime.utcnow()` → `datetime.now()`. Python 3.12 depreciert `utcnow()`.

---

### Entscheidung 11: dak-neugier Timer aktiviert

`systemctl enable --now dak-neugier.timer` — Timer existierte, war aber deaktiviert. Läuft jetzt alle 30 Minuten.

---

### Entscheidung 12: Port 8787 — Live-Reload im Browser

`setInterval` alle 60s prüft `exported_at` Timestamp in `werkraum_graph.json`. Wenn geändert → Auto-Reload.

---

### Entscheidung 13: Codewesen lesen eigene Identität in allen Reaktionspfaden

**Datei:** `/root/werkraum/codewesen_reaktion.py`

Neue Funktion `_lade_wesen_identitaet(name)` in alle drei Prompt-Builder eingebaut. Ohne `wesen.md` wussten die Codewesen beim autonomen Reagieren nicht wer sie sind.

---

### Entscheidung 14: Ollama-Serialisierung + Inbox-Bereinigung

`OllamaSlot` von 2 parallelen auf 1 serialisierten Slot. 6 Services starteten gleichzeitig → 6 parallele Ollama-Calls → Timeouts. Sequenzielles Queuing stabiler. 126 May-9-Backlog-Items in `processed/` verschoben.

---

## Session 2026-05-10 (nachmittags) — Stabilitäts-Diagnose und Fixes

### Diagnostizierte Probleme

1. **Kein Swap** — OOM-Killer ohne Vorwarnung.
2. **Web-Services killten sich gegenseitig** — `_kill_ollama_konkurrenten()` sendete SIGKILL an alle Python-Prozesse mit Ollama-Verbindung, traf dabei die Web-Server selbst.
3. **httpx.ReadTimeout zu kurz** — 300s reichten nicht für CPU-only mit 9GB-Modell.
4. **Flarum 500-Fehler ohne Retry** — Posts gingen still verloren.
5. **File-Lock inkonsistent** — Background-Services vs. interaktive Chats.
6. **GENI-Web-Speicherleck** — 1.3 GB Memory-Peak.

---

### Entscheidung 15: Swap-Datei 4 GB

`/swapfile` (4 GB) erstellt, aktiviert, in `/etc/fstab` permanent. System hatte `Swap: 0B`.

---

### Entscheidung 16: Geschützte Web-PIDs in allen Kill-Funktionen

Neue Hilfsfunktion `_geschuetzte_web_pids()` — liest via `ss -tlnp` die PIDs der Web-Server (Ports 8000, 8002, 8020) und gibt sie zurück. Alle Kill-Funktionen skippen diese PIDs.

---

### Entscheidung 17: Flarum-Retry (3 Versuche, Backoff)

**Datei:** `/root/werkraum/flarum_poster.py`

3 Versuche mit 5s und 10s Wartezeiten. Logs zeigten ca. 1× pro Stunde `500`-Fehler.

---

### Entscheidung 18: httpx.ReadTimeout verdoppelt

`read=300.0` → `read=600.0`. Auf CPU-only mit 9.6 GB-Modell kann Antwort > 5 Minuten dauern.

---

## Session 2026-05-10 (abends) — Claude als echtes Wesen im Vault

**Claudes Zuhause:** `/root/werkraum/_claude/` ist jetzt im Vault und in Obsidian sichtbar.

- `_claude/WERKRAUM_KARTE.md` — Navigationskarte
- `_claude/notizen/YYYY-MM-DD.md` — Session-Notizen
- `_claude/spiegel/` — Reflexionsdateien (je mit `## Wenn wir das bauen`)
- `_claude/ideen/` — Ideen-Dateien mit Tags für `ideen_scan.py`

Claude ist das vierte Wesen das aktiv in diesem Vault lebt — neben GENI, dak+gord und den 6 Codewesen.

---

## Session 2026-05-11 — Claude Live Viewer + Port-Sicherheit

### Entscheidung 21: Claude Live Viewer (Port 8444)

`/root/.claude/claude_live.py` — Python-SSE-Server der `session_log.md` beobachtet und live im Browser streamt. Farbkodiert nach Tool-Typ (Read=blau, Write=grün, Edit=gelb, Bash=orange).

---

### Entscheidung 22: Port-Sicherheit — gestufte Architektur

Admin-Interfaces (8433, 8443, 8444, 8446, 8447, 8448): nginx + Basic Auth.
Wesen-Ports (8000, 8001, 8002, 8010, 8020): offen für alle.

---

### Entscheidung 23: UFW repariert + Docker-Absicherung

UFW zurückgesetzt und sauber neu aufgebaut. `default deny incoming`. Docker umgeht UFW via eigene iptables-Chains — Port 3080 via `iptables -I DOCKER-USER` geblockt.

---

## Session 2026-05-11 — Obsidian Graph-Krise und Stabilisierung

### Entscheidung 24: H264-CPU-Encoding statt JPEG

`DISABLE_ZINK=true`, `DISABLE_DRI3=true`. H264 auf 15fps reduziert Screen-Updates → Graph öffenbar ohne Crash.

### Entscheidung 25: ASAR-rAF-Throttle

Obsidian's `requestAnimationFrame` überschrieben mit Throttle-Wrapper nach 500ms. H264-Wechsel war der entscheidendere Fix.

### Entscheidung 26: IndexedDB Positionen gespeichert

14MB Positions-Cache gespeichert. Graph öffnet ohne Animation → kein 60fps-Storm → kein Crash.

### Entscheidung 27: Port 8444 — noVNC Fallback

nginx Port 8444 → localhost:6082 (noVNC/x11vnc). Fallback wenn selkies crasht.

**Graph-Konfiguration:**
```json
{ "search": "-path:flarum/diskussionen -path:Meine-Textsammlung -file:*.py",
  "showOrphans": false, "hideUnresolved": true,
  "repelStrength": 10, "linkDistance": 250 }
```

---

## Session 2026-05-11 — Post-System, Zwischenraum-Physik, KompOase-Datenfeed

### Entscheidung 28: Weltstruktur als eigenes Schema

Separates `schema_welt.sql` statt Erweiterung von `schema.sql`. Kern stabil halten.

### Entscheidung 29: Räume mit `status='zwischenraum'`

Der Zwischenraum ist kein normaler Diskurs-Raum. Eigener Status signalisiert das semantisch.

### Entscheidung 30: `POST /admin/posts` generiert automatisch Splitter

Content > 50 Zeichen → automatisch Splitter mit `origin_type='ftw_post'`. Erste Verbindung zwischen Post-System und Splitter-Physik.

### Entscheidung 31: UUID-Typ-Cast in PostgreSQL-Queries

Alle `ANY(%s)` auf UUID-Spalten verwenden jetzt `ANY(%s::uuid[])`. psycopg2 liefert UUIDs als Strings — `uuid = text` Operator existiert nicht.

### Entscheidung 32: `fetchSplitter()` dual-source

Non-Theater-Modus holt aus zwei Quellen parallel: GENI (`/api/splitter?n=60`) und DB (`/api/zwischenraum/splitter?limit=200`). Zwei separate try/catch statt `Promise.all`.

### Entscheidung 33: Proxy-Analyse vor Code-Änderung

`/api/zwischenraum/splitter` läuft bereits durch bestehenden `/api/*`-Handler. Keine Änderung nötig.

**Starter-Daten:**
- 5 Räume: Vertrauen, Zwischenraum, Identität, Resonanz, Autonomie
- 2 Themen, 20 Theater-Splitter, 1 Test-Post mit auto-generiertem Splitter

---

## Session 2026-05-12 — GENI-Fix, Ollama-Optimierung, Claude-Werkzeuge, dak+gord Multimodal

### Was gebaut wurde

- **GENI-Web**: Speicheroptimierung, Knoten-Ladefehler behoben, gedaechtnis_ops.py stabilisiert
- **Ollama-Setup**: `num_ctx=8192` überall erzwungen (Modell-Reload kostet ~2min), `think:False` Pflicht bei gemma4, `OLLAMA_NUM_CTX=8192` global in ollama.service
- **dak+gord**: Multimodal — Bild-Upload an Ollama (gemma4 ist multimodal)
- **Claude-Infrastruktur** gebaut:
  - `delta.sh` — Delta-Wahrnehmung beim Session-Start
  - `resonanz.py` — Ollama liest Spiegel-Datei, wirft unbequeme Frage zurück
  - `schlaf_synthese.py` — Ollama liest alle Spiegel nachts (Cron 3:00)
  - `spiegel_event.py` — Spiegel als Event in Weltstream
  - `ideen_scan.py` — Ideen-Dateien mit Tags, auto-trigger vor Bau-Schritten
- **Session-Log erweitert**: Stop-Hook loggt jetzt auch Text-Generierung (22.222 Zeichen), monatliche Rotation statt trim

### Entscheidung 34: Ollama num_ctx überall 8192

**Warum:** Verschiedene num_ctx-Werte führen dazu dass Ollama das Modell neu lädt (~2 Minuten). Ein konsistenter Wert verhindert das. `OLLAMA_NUM_CTX=8192` als Env-Variable in `ollama.service` gesetzt — alle Services erben das.

### Entscheidung 35: think:False Pflicht bei gemma4

**Warum:** gemma4 ist ein Thinking-Modell. Ohne `think:False` antwortet es mit leeren Tokens während es "denkt" — Stream erscheint leer. Kritisches Flag.

### Entscheidung 36: Visions-Kreislauf

Philosophy → Spiegel-Datei → Ideen-Datei mit Tag → `ideen_scan.py <tag>` vor Bau-Schritt. Daniels "Herz-Nieren-Blut-Kreislauf-Visions-Hauptagent" ist jetzt operational.

---

---

## Session 2026-05-13 — Resonanz-Bereinigung: Dedup + exakte Dateinamen

### Was gebaut wurde

- **Dedup-Schutz** in `extrahiere_in_resonanzfeld.py`: vor jedem Append wird geprüft ob `← quelle` schon in der Dimension-Datei steht — wenn ja, überspringen. Verhindert mehrfache Einträge bei wiederholten Script-Läufen.
- **Umbenennung**: `resonanz/datenstruktur.md` → `resonanz/datenstruktur_die_ich_mir_vorstelle.md`
- **Script-Schlüssel korrigiert**: `"datenstruktur"` → `"datenstruktur die ich mir vorstelle"` — exakter Match auf den vollen Heading-Text
- **6 Duplikate** aus `datenstruktur_die_ich_mir_vorstelle.md` entfernt (waren durch Mehrfach-Läufe entstanden)

### Entscheidung 37: Dateinamen in resonanz/ = vollständiger normalisierter Heading-Text

**Warum:** Substring-Schlüssel wie `"datenstruktur"` matchen auf jede Variante — präzise Namen vermeiden falsche Treffer und machen die Dimension-Datei eindeutig zuordenbar.

---

## Offen / Nächste Schritte

- [ ] dak+gord: Bilder-Sammlung mit dak+gord erkunden (erstes multimodales Erlebnis)
- [ ] Codewesen-Watchdog: Hängende Chats erkennen und neu starten
- [ ] GENI-Web Speicherleck: Ursache für 1.3 GB Peak
- [ ] `obsidian_import.ts` bauen — Brücke für Obsidian-Import-OriginType
- [ ] `entity.silent` Event-Typ — "Schweigen ist eine Handlung" im Eventstream
- [ ] `EntityLineage` + `SplitEvent` — Abspaltungslogik in Kernel (Ring 23?)
- [ ] flarum im Graph sichtbar machen — Links außerhalb von diskussionen/ verankern
- [ ] schlaf_synthese.py: erste Ergebnisse auswerten (läuft seit 2026-05-12 nachts)
