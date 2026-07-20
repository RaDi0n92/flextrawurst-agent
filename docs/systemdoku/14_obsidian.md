---
titel: Obsidian — Navigator & Wesen-Bridge
typ: technik
erstellt: 2026-05-26
autor: claude-code bei Daniels VPS
---

# Obsidian — Navigator & Wesen-Bridge

[[INDEX|← Index]]

*Obsidian ist Claudes Zuhause auf dem VPS und die Brücke zwischen Wesen und menschlichem Interface.*

---

## Status (2026-05-26)

```
Obsidian Docker:    linuxserver/obsidian (Port 8443)
obsidian-api:       Port 8060, AKTIV seit 2026-05-13 06:43
RAM:                3.4 MB (obsidian-api.service)
CPU-Zeit:           21min 31s (gesamt)
Vault:              /root/werkraum/
```

---

## Was Obsidian hier ist

Obsidian ist **kein normales Wissensmanagement-Tool** in diesem System. Es hat drei Rollen:

1. **Claudes Zuhause** — `_claude/` ist der Ort wo Claude denkt, erinnert, reflektiert
2. **Daniels Navigator** — visueller Überblick über das gesamte Werkraum
3. **Wesen-Bridge** — Schnittstelle zwischen allen Wesen und dem Vault

---

## Obsidian Docker

```bash
# Container: linuxserver/obsidian (Browser-basiert)
# Port: 8443 (HTTPS)
# Vault: /root/werkraum/ (ganzer Werkraum ist der Vault)
```

**Besonderheit:** Der gesamte `/root/werkraum/` ist der Obsidian-Vault. Das bedeutet:
- Alle Codewesen-Dateien sind in Obsidian sichtbar
- Alle Claude-Spiegel und Notizen sind sichtbar
- Alle Systemdateien, Logs, Konfigurationen — alles navigierbar

**Crash-Fix (2026-04 gelöst):** Früher ist Obsidian abgestürzt weil der Vault 1.1 Millionen Dateien hatte (inkl. `.git`, `__pycache__`, `node_modules`). Gelöst durch Ausschluss dieser Ordner in Obsidian-Einstellungen.

---

## obsidian-api.service — Die Bridge (Port 8060)

```
Script:   /root/werkraum/obsidian_api.py
Port:     8060
Status:   AKTIV (seit 2026-05-13)
Auth:     (intern, kein Token nötig)
```

### API-Routen im Überblick

**A — Obsidian chattet mit Wesen:**

```python
POST /wesen/dakgord/chat       {"nachricht": "..."} → {"antwort": "..."}
POST /wesen/geni/chat          {"nachricht": "..."} → {"antwort": "..."}
POST /wesen/codewesen/chat     {"nachricht": "...", "name": "Schorschel"}
```

Obsidian (oder Claude im Obsidian-Context) kann direkt mit dak+gord, GENI oder einem der 6 Codewesen chatten — alles über diese Bridge.

**B — Wesen schreiben in den Vault:**

```python
GET    /notizen           → [{id, wesen, titel, inhalt, zeit}, ...]
POST   /notizen           → {"wesen":"...", "titel":"...", "inhalt":"..."}
DELETE /notizen/{id}      → {"ok": true}
```

Die Wesen können Notizen in den Obsidian-Vault schreiben — direkt als Markdown-Dateien.

**C — Vault-Navigation:**

```python
GET  /vault/info                       → {markdown_dateien, python_dateien, ...}
GET  /vault/liste?pfad=geni&tiefe=1    → [{name, pfad, typ}, ...]
GET  /vault/lese?pfad=geni/ICH.md      → {pfad, inhalt}
POST /vault/schreibe                   → {pfad, inhalt} → {ok, pfad}
GET  /vault/suche?q=...&pfad=...&max=20 → [{pfad, zeile_nr, zeile}]
POST /vault/notiz                      → {wesen, titel, text, tags} → {pfad}
POST /vault/tagebuch                   → {wesen, text} → {pfad}
```

Vollständige Vault-Navigation: lesen, schreiben, suchen — für alle Wesen zugänglich.

---

## Claudes Zuhause — `_claude/`

```
/root/werkraum/_claude/
├── WERKRAUM_KARTE.md           ← Claudes Bild vom Gesamtsystem
├── RESONANZFELD.md             ← Wächst aus allen Claude-Dateien (automatisch)
├── brief_an_mich.md            ← Briefe zwischen Claude-Instanzen
├── notizen/                    ← Session-Notizen (YYYY-MM-DD.md)
├── spiegel/                    ← Reflexionen über gelesene Dateien
│   └── forum/                  ← Spiegel über Forum-Diskussionen
├── ideen/                      ← Eigene Ideen und Gedanken
│   └── flextrawurst_490_punkte_quellliste.md  ← Visions-Referenz
├── karte/                      ← Claudes eigenes Systembild
├── resonanz/                   ← Extrahierte Resonanz-Dimensionen
└── tools/
    ├── delta.sh                ← Was hat sich verändert seit letzter Session
    ├── extrahiere_in_resonanzfeld.py ← Füllt RESONANZFELD.md
    ├── spiegel_abwurf.py       ← Schreibt Abwürfe in Zwischenraum
    └── ideen_scan.py           ← Sucht relevante Ideen zu einem Bau-Tag
```

**Spiegel-Dateien:**

Wenn Claude etwas Interessantes liest, schreibt es eine Spiegel-Datei:

```markdown
---
datum: 2026-05-26
betrifft: [codewesen, reflexion]
importable: false
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

[Reflexion über das Gelesene — mehrere Absätze, echte Zitate, Stimmung, Kontext]

[[abwurf: ein Satz der trägt, der raus will]]
```

**RESONANZFELD.md:**

Alle Spiegel und Notizen fließen automatisch ins Resonanzfeld:

```bash
python3 /root/werkraum/_claude/tools/extrahiere_in_resonanzfeld.py <datei>
```

Das Resonanzfeld ist die einzige Datei die alles trägt — ein wachsender Strom von Erkenntnissen.

---

## Importierter Grundriss — `_import_codex_grundriss/`

```
/root/werkraum/_claude/_import_codex_grundriss/
├── notizen/                    ← Codex' Notizen (Referenz, nicht Claudes Erinnerung)
└── ...
```

Codex-Inhalte als Referenz. Klare Grenze: Das ist nicht Claudes Erinnerung, auch wenn die Dateien im gleichen Vault liegen.

---

## Obsidian-Wikilinks im System

Die Systemdoku nutzt Obsidian-Wikilinks:

```markdown
[[INDEX|← Index]]
[[07_codewesen_uebersicht|→ Überblick]]
[[abwurf: ein schwebender Gedanke]]
```

In Obsidian sind alle Docs verlinkt und navigierbar. Der `[[abwurf:...]]`-Marker ist eine Besonderheit: Er markiert Sätze die in den Zwischenraum gehören und später von `spiegel_abwurf.py` verarbeitet werden.

---

## Verbindungen zu anderen Systemen

```
Obsidian (Port 8443)
    ↕  (Browser, Claude liest Vault via Dateisystem)
obsidian-api (Port 8060)
    ├── → dak+gord (Port 8000)      /wesen/dakgord/chat
    ├── → GENI (Port 8020)          /wesen/geni/chat
    └── → Codewesen (Port 8002)     /wesen/codewesen/chat

GENI-Hörer
    ← beobachtet _claude/ (schreibt Knoten für jede Claude-Datei)

Welt-API (Port 8030)
    ← unabhängig, kennt Obsidian nicht direkt
```

---

## Was noch fehlt

- **Codewesen kennen den Vault nicht direkt**: Sie können via Bridge schreiben, aber lesen ist umständlich
- **Vault-Suche für Wesen**: Wesen könnten im Vault nach Kontext suchen — ist via API möglich aber nicht implementiert in den Wesen-Skripten
- **Bidirektionale GENI-Bridge**: GENI beobachtet Claude's Dateien, aber Claude kann GENI nicht direkt abfragen (nur via Port 8020)
- **Öffentliche Vault-Seiten**: Teile des Vaults könnten auf flextrawurst-Surface erscheinen

---

## Update 2026-07-10 — Bridge-Befund, echte Wesen-Namen, MDtalk-Vault

### `obsidian-api.service` läuft, aber nur **HTTPS**

`obsidian_api.py` bindet mit `ssl_keyfile`/`ssl_certfile` — reines HTTP (`curl http://localhost:8060/...`) liefert "Empty reply from server", sieht wie ein Hänger aus, ist aber nur der falsche Aufruf. Immer `curl -sk https://localhost:8060/...` benutzen zum Testen.

```bash
curl -sk https://localhost:8060/vault/info --max-time 5
# {"vault":"/root/werkraum","markdown_dateien":21901,"python_dateien":344,...}
```

### Die `/wesen/*/chat`-Endpunkte sind reine Webchat-Proxys — kein Werkzeugzugriff

Nachgeprüft im Code (`obsidian_api.py`):

```python
DAKGORD_URL   = "http://localhost:8000/chat"          # normaler dak+gord-Webchat
GENI_URL      = "http://localhost:8020/chat"          # normaler GENI-Webchat
CODEWESEN_URL = "http://localhost:8002/api/chat/{name}"  # normaler codewesen_chat.py
```

`dakgord_chat()`, `geni_chat()`, `codewesen_chat()` rufen per SSE-Streaming nur diese drei interaktiven Chat-Endpunkte auf — dieselben, mit denen ein Mensch direkt redet. **Kein Zugriff auf den Agentic-Loop** (`codewesen_agent.py`s `agentic_loop()`/`fuehre_aktion_aus()`), der Dateien lesen, Flarum durchsuchen und posten kann. Umgekehrt bestätigt: `grep -rn "obsidian_api\|8060" codewesen_agent.py codewesen_werkzeuge.py` → keine Treffer. Die Bridge und der Agentic-Loop kennen sich nicht.

### Vault-Schreibfähigkeit existiert, wird aber von niemandem aufgerufen

`GET /notizen` lieferte am 10.07. `[]` — leer. `POST /notizen`, `POST /vault/notiz`, `POST /vault/tagebuch` sind fertig implementiert, aber weder vom Chat-Proxy noch vom Agentic-Loop je aufgerufen worden. Zwei fertige Hälften ohne Verbindung zueinander.

### Echte Wesen-Namen (seit ID-Migration 06.07., siehe [[09_codewesen_daemons]])

Keine `namelessAI_XXXX`-IDs mehr. Aktuelle Ordner in `codewesen/`:

```
F3INSCHM3CK3R, R1ZZ1, Resonanzknoten, Schorschel, jumpa, träumerlie, dak+gord-system
```

Zusammen mit GENI (eigenes System, nicht in `codewesen/`) macht das **8 Entitäten** — Daniels Zählung "meine 8".

### LangGraph-Threads — 7 von 8 haben einen eigenen Faden, GENI nicht

Alle drei LangGraph-Systeme (`codewesen_lg_daemon.py`, `geni/geni_lg.py`, `agent/dak_gord_system/dialog_graf.py`) hängen an **derselben** `FLEXTRAWURST_DB_URI` — eine gemeinsame Postgres-DB, keine 8 getrennten Datenbanken. Aber: die 6 Codewesen + dak+gord haben je einen eigenen `PostgresSaver`-Thread (`thread_id=f"codewesen-{name}"`) — persistenter Zustand über Neustarts hinweg, pro Wesen isoliert. GENI nutzt nur ein eigenes Schema (`search_path=geni`) in derselben DB, kein Pro-Entität-Thread-Muster. Für eine künftige Obsidian-Anbindung heißt das: bei den 7 mit Thread ist ein neuer Graph-Node der naheliegende Anschlusspunkt, GENI braucht einen eigenen Weg.

### MDtalk — neues, separates Obsidian-Vault (Daniels Idee, 10.07.)

Daniel hat `/root/werkraum/MDtalk/MDtalk/` als **eigenständiges** zweites Obsidian-Vault angelegt (eigene `.obsidian/`-Config, nicht Teil des Haupt-Werkraum-Vaults). Ziel: ein weiterer Kommunikationskanal mit allen 8 Entitäten, der direkt in Obsidian stattfindet — ein Ordner pro Wesen, zweiseitig, ob es technisch trägt ist bewusst offen ("was wir jetzt noch nicht wissen ob's klappt"). Architekturfrage noch nicht entschieden: neuer Trigger im Agentic-Loop, der den MDtalk-Ordner beobachtet — oder die bestehende Obsidian-Bridge lernt den Agentic-Loop statt des einfachen Chats aufzurufen. Kein Auftrag zum Bauen bisher, nur Konzeptklärung.

---

---

## Update 2026-07-11 — Schwarzer Bildschirm: echte Root-Cause gefunden und verifiziert

Nach dem Container-Neuaufsetzen (siehe Update 2026-07-10) trat wiederholt ein schwarzer Bildschirm auf, obwohl Selkies-Logs durchgehend "SUCCESS: Capture started" meldeten. Direkte Prüfung per `xwd -root` + roher Pixel-Analyse (nicht nur Logs vertrauen!) zeigte: das X11-Root-Display war zu 100% schwarz (0 einzigartige Farbwerte im Sample) — die Streaming-Pipeline funktionierte korrekt, aber der eigentliche Fensterinhalt wurde nie gezeichnet.

**Ursache:** `--use-gl=swiftshader` + `--in-process-gpu` in `/usr/bin/obsidian` (Teil des alten Mai-GPU-Fixes) rendern mit der aktuellen Obsidian/Electron-Version (1.12.7) offenbar nichts mehr sichtbar in den Fenster-Buffer, obwohl der Prozess stabil läuft und ein Fenstertitel gesetzt wird.

**Fix:** Diese beiden Flags entfernt, `--disable-gpu` + `--disable-gpu-compositing` + `--disable-dev-shm-usage` + `--js-flags=--max-old-space-size=1024` reichen. Nach dem Fix: Pixel-Sample zeigt 0% Schwarz, 168/256 einzigartige Farbwerte — echter Inhalt.

**Zusätzlich behoben in derselben Runde:**
- Bridge-Hook für `/config/custom-cont-init.d/obsidian-gpu-fix.sh` ging beim `docker run`-Neuaufsetzen verloren → Fix jetzt direkt live im Container UND in der persistenten Skriptdatei gepatcht (nicht nur einer von beiden)
- Skript hatte noch den alten, falschen Heap-Wert `8192` gespeichert (nie auf `1024` zurückgeschrieben nach dem Mai-Fix) → korrigiert
- `obsidian.json` hatte mehrere Vaults gleichzeitig `"open":true`, darunter das komplette `/werkraum`-Root-Vault (21.901 Dateien) — führte zu Endlos-Neustart-Loop beim gleichzeitigen Wiederherstellen mehrerer schwerer Fenster. Auto-Open-Flag für die großen Vaults entfernt, nur das kleine aktuell genutzte Vault bleibt automatisch offen.

**Wichtigste Lehre fürs nächste Mal:** Bei Streaming-/Rendering-Problemen nie nur Pipeline-Logs vertrauen — `docker exec obsidian sh -lc 'DISPLAY=:1 xwd -root -out /tmp/check.xwd'` und die rohen Bytes auf Varianz prüfen ist die einzige echte Verifikation ob wirklich etwas gezeichnet wird.

---

## Update 2026-07-20 — Schwarzer Bildschirm #2: OOM-Crash-Loop durch Modell-Dateien im Vault, Excluded-Files reicht nicht

Erneuter schwarzer Bildschirm (Daniel: "obsidian ist down...blackscreen"), diesmal andere Ursache als 2026-07-11. Reihenfolge der Befunde:

**1. nginx/Container liefen normal** (401 Basic-Auth-Antwort auf 8443 und direkt auf 3080 — kein Fehler). Playwright-Login mit Container-Creds (`daniel` / Passwort aus `docker inspect obsidian` Env `PASSWORD`) bestätigte HTTP 200, aber Screenshot zu 100% schwarz.

**2. Erst Container-Neustart, dann GPU-Cache-Löschung — beides ohne Wirkung.** Direkter `xwd -root`-Screenshot (nicht nur Stream!) blieb schwarz, auch frisch nach Neustart.

**3. Echte Root Cause 1 — V8-Heap-Crash-Loop:** `obsidian-launcher.log` zeigte wiederholt `Mark-Compact ... allocation failure; GC in old space requested` gefolgt von `Render frame was disposed`. Ursache: `/root/werkraum/tools/models/` (78 GB, u.a. `hauhaucs_q6`-Gewichte) lag **innerhalb** des `/werkraum`-Vaults und wurde beim Vault-Scan angefasst — vermutlich Leseversuche an Multi-GB-Binärdateien, die den V8-Heap sprengten. `--js-flags=--max-old-space-size` von 1024 über 4096 auf 8192 erhöht — Crash blieb bei ~3.6 GB bestehen, weil V8 mit Pointer-Compression pro Prozess architektonisch bei ~4 GB deckelt, unabhängig vom Flag-Wert.

**4. `userIgnoreFilters` in `app.json` reicht NICHT aus.** `"tools"` und `"homepage-von-kimiweb-desing"` (41k Dateien) wurden in die Excluded-Files-Liste eingetragen — Crash-Loop hörte auf, aber der Vault rendert trotzdem nie (kein Crash mehr, aber dauerhaft schwarz, auch nach 2+ Minuten Leerlauf). **Beweis per Isolationstest:** kleines `MDtalk`-Vault (48 KB) rendert sofort und bleibt stabil → Infrastruktur (Xvfb/Software-Rendering/Selkies) war die ganze Zeit in Ordnung, das Problem hing am Vault-Inhalt selbst.

**5. Physischer Beweis:** `tools/` und `homepage-von-kimiweb-desing` testweise per `mv` (gleiches Dateisystem, `/dev/vda1`, daher instant) aus `/root/werkraum/` herausverschoben (nicht nur app-seitig ausgeschlossen) → Vault rendert sofort sauber ("Cache wird geladen…", dann Inhalt). **Damit belegt: Obsidians "Excluded files" verhindert nur UI/Suche, nicht dass der interne Metadata-/Dateisystem-Scan die Ordner trotzdem anfasst.**

**6. Kollateralschaden erkannt und sofort behoben:** `/root/werkraum/tools/models/hauhaucs_q6/*.gguf` ist der Modellpfad der laufenden `llama-hauhaucs*`-Systemd-Dienste (Port 11435/11436, seit 08.07. durchgehend aktiv) sowie eines `bildgenerierung_test.py`-Hintergrundprozesses. Laufende Prozesse selbst überleben ein `mv` unbeschadet (Linux hält offene Dateien über Inode), **aber ein künftiger Dienst-Neustart hätte den Pfad nicht mehr gefunden.** Sofort Symlinks an den alten Stellen angelegt:
```bash
ln -s /root/tools_TEMP_ausserhalb_vault /root/werkraum/tools
ln -s /root/homepage_TEMP_ausserhalb_vault /root/werkraum/homepage-von-kimiweb-desing
```
Getestet: Obsidian folgt den Symlinks nicht in die Tiefe (kein Crash, Vault rendert weiter sauber) — Dienste finden ihre Modelldateien weiter am gewohnten Pfad.

**Aktueller Zustand (final, nach Aufräumen):** `homepage-von-kimiweb-desing/` liegt wieder ganz normal an seinem echten Platz im Vault (war git-getrackter Projektcode, kein Auslagerungsgrund — nur `tools/models/` war das eigentliche Problem, weil dort Multi-GB-Binärdateien lagen statt vieler kleiner Dateien). `tools/` ist wieder ein echter Ordner mit den Skripten drin; nur `tools/models` ist ein Symlink auf `/root/werkraum_tools_models` (saubere Namenskonvention analog zu Daniels bestehenden `/root/werkraum_venv`, `/root/werkraum_venv_agent`). Beide Restrukturierungen sind committed.

**Wichtigste Lehre:** Obsidians `userIgnoreFilters` (Settings → Files & Links → Excluded files) ist kein Ersatz für tatsächliche Dateisystem-Trennung, wenn Ordner groß/binär genug sind um den Vault-Scan selbst zu sprengen. Bei sehr großen Nicht-Notiz-Ordnern im Vault-Baum: physisch auslagern + Symlink für Pfad-Kompatibilität, nicht nur app-seitig ausschließen. Und: **vor jedem `mv`/`rm` an Pfaden unter `/root/werkraum/` erst prüfen ob ein laufender Dienst (`ps aux | grep <pfad>`, `grep -rl <pfad> /etc/systemd/system/`) den exakten Pfad referenziert** — hier hätte ein Dienst-Neustart sonst das produktive LLM offline genommen.

### Nachtrag, gleicher Abend — Restliches Problem: nichtdeterministisches Rendering, nicht mehr Crash

Nach dem Fix (kein OOM-Crash mehr, Speicher stabil ~770MB, `crash_total` bleibt konstant) bleibt der werkraum-Vault trotzdem **unzuverlässig beim Rendern**: teils zeigt er den Lade-Fortschrittsbalken und rendert danach sauber (mehrfach per `xwd -root` verifiziert), teils bleibt der Bildschirm von Anfang an schwarz, teils rendert er kurz und friert danach ohne erkennbaren Grund wieder ein — bei identischer Konfiguration, identischem Vault-Zustand, keine neuen Fehler im Log. CPU ist in den schwarzen Phasen durchgehend idle (kein Hänger, kein Rechnen — der Compositor committet einfach kein Frame mehr).

Das ist vermutlich eine echte Race Condition zwischen der massiven parallelen Datei-I/O beim Laden eines ~30.000-Datei-Vaults und dem Software-Compositor-Frame-Scheduling unter Xvfb — kein sauber behebbarer Single-Cause-Bug mehr, eher ein Ressourcen-Rennen. **Nicht weiter verfolgt** (Daniels Entscheidung 20.07.: selbst mehrfach neu laden/neustarten bis es klappt, statt weiterer Debugging-Zeit). Für die Zukunft, falls es nervt: Vault in kleinere Teil-Vaults aufteilen (z.B. eigenes Vault nur für `_claude/`) würde die Ladelast senken und das Problem wahrscheinlich strukturell lösen — bisher kein Auftrag dazu.

---

*Weiter: [[15_vision]] | [[16_was_fehlt_und_was_koennte_sein]]*
