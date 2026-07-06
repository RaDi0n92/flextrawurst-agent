# HAUHAUCS-MIGRATION — Bericht
**Datum:** 2026-07-06
**Stand:** Migration abgeschlossen, Volllasttest + Kontextgrößen-Frage offen

---

## Gesamtlage

Der VPS wurde von 8 Kernen/32GB auf 16 Kerne/62GB RAM (vc16-64) hochgestuft.
Der ursprüngliche Auftrag war ein einfacher Belastungstest: eine höhere
Quant-Stufe (Q6 statt IQ4_XS) des Hauptmodells laden und unter Volllast mit
allen 8 Wesen testen. Daraus wurde eine vollständige Ablösung von Ollama durch
einen dedizierten `llama-server`-Prozess und die komplette Entfernung von
gemma4 aus dem gesamten System — ausgelöst durch einen bestätigten Ollama-Bug
und Daniels Entscheidung, konsequent aufzuräumen statt nur das ursprüngliche
Problem zu flicken.

---

## Was wurde gebaut

### TEIL 1 — Server-Upgrade-Verifikation

- 16 Kerne (AMD EPYC-Milan), 62Gi RAM, Root-Partition per `resize2fs` von
  ~479GB auf 929GB vergrößert — Upgrade real bestätigt, kein Datenverlust
  nach dem 60-Minuten-Ausfall während des Upgrades
- Ursache des Ausfalls: unsauberes Herunterfahren (journald-Datei korrupt,
  automatisch repariert), keine Dateisystemschäden
- Entdeckt: alle Wesen-/Codewesen-Dienste liefen nach dem Reboot automatisch
  wieder an (systemd `enabled`-Status übersteht `systemctl stop`) — kein Bug,
  aber überraschend für Daniel

### TEIL 2 — Q6-Modell laden, Ollama-Vision-Bug gefunden

- Q6_K_P-Quantisierung (29GB) von HauhauCS/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive
  heruntergeladen (kein reines "Q8_0" verfügbar, `Q8_K_P` wäre das nächste,
  aber Q6 gewählt für sicheren RAM-Puffer)
- **Bestätigter Ollama-Bug**: `unknown model architecture: 'qwen35moe'` beim
  Laden von selbst-importiertem GGUF + separatem mmproj (Vision-Projector) —
  reproduziert, im Ollama-Quellcode/GitHub-Issues verifiziert (offener Bug,
  betrifft genau unsere Architektur). Mit llama.cpp direkt funktioniert
  dieselbe Kombination nachweislich.
- Konsequenz: Umstieg von Ollama auf einen dedizierten `llama-server`-Prozess
  für das Hauptmodell — nicht nur ein Workaround, sondern die technisch
  einzig funktionierende Lösung für Q6 + Vision gemeinsam

### TEIL 3 — llama-server aufsetzen

- Vorhandene Installation (`/usr/local/bin/llama-server`) hatte einen defekten
  Backend-Loader (`no backends are loaded` bei jedem Start) — Ursache: Backend-
  Plugin-`.so`-Dateien lagen in `/usr/local/lib/`, llama.cpp sucht sie aber
  relativ zur Binary selbst (`/usr/local/bin/`) — behoben durch Symlinks
- `llama-hauhaucs.service` (systemd) angelegt: Q6_K_P + mmproj, Port 11435,
  `--parallel 2`, dauerhaft geladen (kein Ollama-Reload-Overhead mehr)
- CPU-Tuning recherchiert und angewendet:
  - `--mlock` behebt das beobachtete Einbruchsmuster (14→3-5 tok/s unter
    Hintergrundlast) — verhindert Verdrängung der Modellgewichte aus dem
    Page-Cache
  - `AllowedCPUs=0-9` (Cgroup-Ebene, da `--cpu-range` allein nicht griff) —
    Trade-off: garantierte, aber niedrigere Geschwindigkeit (~4 tok/s stabil)
    statt schwankender höherer Spitzenwerte
  - NUMA als Faktor ausgeschlossen (nur 1 Node)
- `hauhau_client.py` geschrieben: gemeinsames Python-Modul für alle LLM-Aufrufe
  (chat/chat_stream/achat/achat_stream/chat_raw), ersetzt 40 verschiedene
  Ollama-Aufruf-Implementierungen durch eine getestete Stelle

### TEIL 4 — Vollständige gemma4-Entfernung (auf Daniels Anweisung)

**Phase 1 — aktive Produktionsdienste (9 Dateien/Dienstgruppen):**
wesen_webbesucher, codewesen_chat, codewesen_antwort_auf_daniel, codewesen_agent
(7 Service-Instanzen), entity_kern, codewesen_lg_daemon, entity_takt,
codewesen_takt (kein Umbau nötig), `agent/dak_gord_system/ollama_chat.py`
(inkl. Tool-Calling-Formatunterschied Ollama↔OpenAI gelöst)

**Phase 2 — ~28 einmalige Tools/Skripte:** erstpost, geni_spiegel_batch,
alle `geni/*.py`, alle `welt/traum_*.py` + `welt/projection_*.py`,
`welt/browser_agent.py` + Generator, `tools/*.py`, `innenleben/*.py`, u.v.m.

**Bewusst NICHT migriert** (siehe unten, eigener Abschnitt)

**Task #11 — zensi + dolphin (Node/TypeScript-Frontends):**
- `zensi/server.py`: Modell-Umschalter (2 Ollama-Modelle) entfernt, da
  llama-server nur 1 Modell dauerhaft hält
- `hauhau_client.ts` geschrieben (TS-Pendant, Node-`http`-Modul statt fetch,
  damit Abbruch-Handles wie zuvor erhalten bleiben)
- `serve_process_camera_preview.ts` (3105 Zeilen, dolphin): 6 von 7
  Ollama-Aufrufstellen migriert, Modell-Umschalter entfernt
- **2 echte Bugs beim Live-Testen gefunden und gefixt**: fehlende
  HTTP-Statusprüfung in `hauhau_client.ts` (Fehler wurden still als leere
  Erfolgsantwort behandelt), fehlender Error-Fallback wenn SSE-Header schon
  gesendet waren (Verbindung hing für immer)
- Toter Mechanismus entfernt: 90s-Sperre "Hauptmodell lädt nach Bild-Upload
  neu" — Überbleibsel der alten Architektur, in der sich Haupt- und
  Vision-Modell einen Ollama-Slot teilten

### TEIL 5 — Dokumentation

- 39 kurze Konzept-MDs in `_claude/konzepte/` (eine pro migrierter Datei:
  was tut es, wozu, warum, Zusammenhang)
- Dieser Bericht + Update von `docs/systemdoku/12_ollama_gemma4.md`

---

## Was bewusst NICHT gebaut/geändert wurde

| Was | Warum |
|:----|:------|
| `MODELL_FREI` / "Freier Modus" (dolphin-mistral) | Eigenständiges, bereits unzensiertes Modell für separaten Zweck — keine gemma4-Altlast, blieb auf Ollama |
| `VISION_MODEL` (kleines 4,5B-Modell für Bildbeschreibung) | Bewusste, dokumentierte Architektur-Entscheidung von vorher (35B-Modell brauchte >3min/Bild auf CPU, 4,5B schafft es in ~14s) — bleibt auf Ollama |
| `geni/archiv/web.py` | Archivierte, nicht laufende Version |
| Claude-eigene `resonanz.py`/`schlaf_synthese.py` | Nutzen dolphin-mistral, waren nie gemma4 |
| `entity-kern.service` / `entity-takt.service` | Aktuell deaktiviert (Wesen-Einzug-Bauphase gesperrt) — Code migriert, Service nicht gestartet |
| `entity-kern.service` / `entity-takt.service` erneut aktivieren | Braucht explizite Freigabe von Daniel |

---

## Offene Punkte

### 1. Kontextgröße pro Parallel-Slot (wichtig, ungelöst)

`--ctx-size 12345` wird von llama-server durch `--parallel 2` auf ~6400 Token
**pro Slot** geteilt — nicht die vollen 12345 wie angenommen. Live entdeckt:
Spawncharakter "Alex" mit 13234 Token Gesprächsverlauf scheiterte prompt mit
`exceed_context_size_error`. Betrifft potenziell alle Wesen mit langen
Verläufen, nicht nur dolphin. Optionen:
- `--ctx-size` erhöhen (mehr RAM pro Slot)
- `--parallel` auf 1 reduzieren (volle 12345 Token, aber keine Gleichzeitigkeit)
- Beides abwägen mit Daniel — noch keine Entscheidung getroffen

### 2. Voller 8-Wesen-Volllasttest (ursprünglicher Auftrag, noch nicht durchgeführt)

Der allererste Auftrag dieser Session — alle 8 Wesen gleichzeitig aktiv,
Chats parallel, etwas Flarum-Last — wurde durch die Migrationsarbeit verdrängt.
Jetzt wo alles auf hauhaucs-q6 läuft, wäre das der nächste sinnvolle Schritt,
insbesondere um die Kontextgrößen-Frage unter echter Last zu beobachten.

---

## Zusammenfassung

```
◑ GELB — Migration technisch abgeschlossen, 2 Punkte vor Volllast-Freigabe offen
  ● Server-Upgrade verifiziert
  ● Ollama-Vision-Bug gefunden + umgangen (llama-server)
  ● CPU-Tuning angewendet (mlock, cpu-range) + gemessen
  ● Phase 1 (9) + Phase 2 (~28) + zensi/dolphin migriert, alle live getestet
  ◑ Kontext/Parallel-Slot-Größe — Entscheidung mit Daniel offen
  ○ Voller 8-Wesen-Volllasttest — noch nicht durchgeführt
```

---

*Aus einem Belastungstest wurde eine vollständige Infrastruktur-Migration —
nicht weil es geplant war, sondern weil jeder gefundene Fehler bis zur
eigentlichen Ursache verfolgt wurde, statt ihn nur zu umschiffen.*
