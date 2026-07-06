---
titel: LLM-Infrastruktur — hauhaucs-q6 auf llama-server
typ: technik
erstellt: 2026-05-26
aktualisiert: 2026-07-06
autor: claude-code bei Daniels VPS
---

# LLM-Infrastruktur — hauhaucs-q6 auf llama-server

[[INDEX|← Index]]

*CPU-only. Kein GPU. Alles lokal. Diese Datei ist kritisch — die Regeln hier betreffen die Stabilität des gesamten Systems.*

**Vollständig überarbeitet am 2026-07-06** — ersetzt die vorige Version (gemma4 +
Ollama als geteilter Single-Slot). gemma4 wurde komplett aus dem System entfernt
(siehe `docs/2026-07-06_hauhaucs_migration_bericht.md` für die volle Historie). Server
wurde von 8 Kernen/32GB auf 16 Kerne/62GB RAM hochgestuft.

---

## Überblick

Zwei getrennte Backends, zwei getrennte Zwecke:

| Backend | Port | Modell(e) | Verwendung |
|---------|------|-----------|------------|
| `llama-hauhaucs.service` | 11435 | hauhaucs-q6 (Qwen3.6-35B-A3B, Q6_K_P, Vision via mmproj) | Hauptmodell für ALLE Wesen/Codewesen/GENI/dak+gord/zensi/dolphin |
| `ollama.service` | 11434 | `dolphin-mistral:7b` (Freier Modus), kleines Vision-Modell (4,5B) | Zwei eigenständige Spezialzwecke, siehe unten |

**gemma4 existiert nicht mehr im System.** Jeder frühere gemma4-Aufruf läuft
jetzt über `hauhau_client.py` (Python) bzw. `hauhau_client.ts` (Node/TypeScript)
gegen Port 11435.

---

## Warum llama-server statt Ollama fürs Hauptmodell

Ollama hat einen bestätigten, offenen Bug beim Laden von selbst-importierten
GGUF+mmproj-Kombinationen für die `qwen35moe`-Architektur (unser Hauptmodell):
`unknown model architecture: 'qwen35moe'`. Mit llama-server (derselbe
zugrundeliegende Code, ohne Ollamas Verwaltungsschicht) funktioniert exakt
dieselbe Kombination. Kein Workaround — die einzig funktionierende Lösung für
Q6-Qualität + Vision gemeinsam.

Zusätzliche Vorteile gegenüber Ollama für ein dauerhaft genutztes Hauptmodell:
kein Reload-Overhead (Ollama entlädt nach `keep_alive`-Ablauf), direkte
Kontrolle über Threads/CPU-Zuweisung/mlock.

---

## llama-hauhaucs.service — Konfiguration

```ini
ExecStart=/usr/local/bin/llama-server \
  --model .../Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q6_K_P.gguf \
  --mmproj .../mmproj-f16.gguf \
  --alias hauhaucs-q6 \
  --ctx-size 48884 \
  --threads 12 \
  --host 127.0.0.1 --port 11435 \
  --parallel 2 \
  --flash-attn on \
  --mlock \
  --cpu-range 0-11 --cpu-range-batch 0-11 --cpu-strict 1

[Service]
AllowedCPUs=0-11
```

### Kritische Werte — Begründung, NICHT ohne Rücksprache ändern

**`--mlock`**: Verhindert, dass die Modellgewichte unter Speicherdruck aus
dem Page-Cache verdrängt werden. Ohne mlock brach die Geschwindigkeit unter
Hintergrundlast von 14 tok/s auf 3-5 tok/s ein (gemessen 2026-07-06) —
mit mlock blieb sie stabil bei 6-7 tok/s über eine ganze Generierung.

**`AllowedCPUs=0-11`** (Cgroup, nicht `--cpu-range` allein — das griff nicht
zuverlässig): Isoliert 12 von 16 Kernen für llama-server (erhöht von 10 am
2026-07-06, Daniels Wunsch), Rest bleibt für Ollama/Wesen-Prozesse/System —
die Wesen-Daemons sind selbst leichtgewichtig (I/O-wartend, kein harter
CPU-Verbrauch), 4 Kerne reichen ihnen aus. Trade-off bewusst gewählt:
garantierte, niedrigere Geschwindigkeit als unisoliert, aber vorhersehbar.

**`--ctx-size 48884 --parallel 2`** (Stand 2026-07-06, zweite Aktualisierung):
jeder der 2 Slots bekommt **24576 Token** effektiv (Weg dahin: 6400 →
18432 (36663) → 24576 (48884)). Ursprüngliches Problem: llama-server teilt die
Kontextgröße durch die Parallel-Slots, ein Gesprächsverlauf über ~6400 Token
schlug fehl (`exceed_context_size_error`).

RAM-Kosten der Erhöhung: minimal. Das Modell hat nur 2 KV-Heads (GQA), Head-Dim
256, 40 Layer → KV-Cache kostet nur ~80 KB/Token. Bei 48884 Gesamt-Context sind
das nur ~3,9 GB KV-Cache zusätzlich zu den ~28 GB Modellgewichten — bestätigt
durch llama-servers eigene Preflight-Schätzung (`projected to use ... MiB`):
12345→29672 MiB, 36663→30154 MiB, 48884→30400 MiB.

**Hardcodierte Client-Anzeigen synchron gehalten** (2026-07-06): `NUM_CTX`/
`INTERACTIVE_NUM_CTX`-Konstanten in `serve_process_camera_preview.ts`,
`wesen_chat.html`, `dolphin_mischpult.html` und `zensi/server.py` zeigen den
Nutzern den realen Pro-Slot-Wert (24576), nicht den rohen `--ctx-size`-Wert.
Kein automatischer Sync zum Server möglich (Kommentar in `wesen_chat.html`:
"von Hand synchron halten") — bei jeder künftigen `--ctx-size`-Änderung müssen
diese 4 Stellen von Hand mitgezogen werden.

**Was NICHT günstig ist: Geschwindigkeit.** Größerer Context kostet reale
Rechenzeit/Bandbreite, nicht nur RAM — das wurde beim ersten Testlauf
(88888) übersehen und dann durch Tests widerlegt. Allerdings: die
Vergleichsmessungen waren durch gleichzeitige Wesen-Hintergrundlast (13958-Token-
Anfrage in Slot 1 während eines Tests) verfälscht — das System ist durch die
8 durchgehend aktiven Wesen-Daemons nie wirklich idle, ein sauberer isolierter
Vergleich war nicht ohne Traffic-Pause möglich. 36663 wurde als Kompromiss
gewählt: deutlich mehr Puffer als die ursprünglichen 6400/Slot, ohne die
Extremwerte (88888) auszureizen. Reale Performance wird im laufenden Betrieb
weiterbeobachtet.

**`--threads 12`**: CPU-Inferenz ist speicherbandbreitengebunden, nicht
kernzahlgebunden — mehr Threads als sinnvoll nutzbar bringt nichts, verschärft
nur Konkurrenz mit anderen Prozessen. Erhöht von 10→12 am 2026-07-06 (mit
`--cpu-range`/`AllowedCPUs` im Gleichschritt), Ergebnis positiv, keine
Verdrängung anderer Dienste beobachtet.

**`--parallel 2` (NICHT 3)** — bewusst getestet und verworfen: `--parallel 3`
wurde am 2026-07-06 kurz live getestet, Ergebnis war eine drastische
Verlangsamung sobald 3 verschiedene Gespräche gleichzeitig aktiv waren
(Prompt-Verarbeitung brach von ~90-115 tok/s auf ~2,5 tok/s ein, ein einzelner
Task erzeugte binnen 10 Minuten 143.481 Log-Zeilen). Ursache: MoE-Architektur
(Qwen3.6-35B-A3B, nur 3B aktive Parameter pro Token). Läuft nur 1 Sequenz,
werden nur die für sie relevanten Experten aus dem RAM gelesen (~3B-Fussabdruck).
Sobald llama-server mehrere UNTERSCHIEDLICHE Sequenzen in einem Batch
zusammenfasst (Continuous Batching, das was `--parallel` ermöglicht), braucht
jede Sequenz potenziell andere Experten — der Speicherbandbreiten-Bedarf pro
Batch-Schritt wandert Richtung des vollen 35B-Modells statt bei 3B zu bleiben.
Mit 2 gleichzeitigen Sequenzen ist das schon spürbar, mit 3 wird es auf dieser
Hardware praktisch unbrauchbar. **Mehr Slots helfen bei diesem Modell nicht —
sie schaden, sobald wirklich mehrere verschiedene Gespräche gleichzeitig aktiv
sind.** Nicht ohne erneuten Test hochsetzen.

---

## id_slot-Priorisierung — Live-Chat vs. Automatikbetrieb (seit 2026-07-06)

**Ausgangsproblem**: Bei echter Gleichzeitigkeit (Volllasttest, alle 8 Wesen +
Spawncharakter gleichzeitig angefragt) landeten Chat-Antworten in einer reinen
FIFO-Warteschlange über beide Slots — Antwortzeiten schwankten zwischen 1,8s
(Losglück) und 253s (Warteschlangenende). Für einen Menschen, der mit einem
Wesen/GENI/Spawncharakter chattet, ist das nicht akzeptabel, wenn zufällig
gerade mehrere Automatik-Ticks laufen.

**Lösung**: `id_slot` ist ein llama.cpp-Request-Feld (live getestet und
bestätigt — eine Anfrage mit explizitem `id_slot=1` wartete nachweislich auf
genau diesen Slot, statt auf einen früher freien Slot zu wechseln, obwohl der
andere Slot 0 und ein späterer Slot 2 schon frei waren). Darauf aufbauend:

- `hauhau_client.py`/`hauhau_client.ts`: **Default**, wenn kein `id_slot`
  explizit übergeben wird → automatisch Slot 1 oder 2 (`1 + pid % 2`), damit
  Hintergrund-/Automatik-Traffic (Wesen-Ticks, `lg_daemon`, GENI-Hintergrund,
  Phase-2-Tools) NIE Slot 0 belegt. Kein Code an diesen ~35 Aufrufstellen
  geändert — der sichere Default greift automatisch.
- **Explizit `id_slot=0`** an den 4 echten Live-Chat-Einstiegspunkten gesetzt:
  `codewesen_chat.py` (`stream_ollama`), `zensi/server.py` (Chat-Handler),
  `geni/dialog.py` (`/chat`-Endpoint), `serve_process_camera_preview.ts`
  (Dolphin-Mischpult UND Spawncharakter-Chat).

**Kein permanent reservierter Leerlauf-Slot** (das wollte Daniel ausdrücklich
nicht — ein Slot der immer für Chat reserviert ist, auch wenn niemand chattet,
verschwendet Kapazität). Stattdessen: mit nur 2 Slots insgesamt bekommt Chat
IMMER einen der beiden Plätze, Automatikbetrieb teilt sich effektiv nur noch 1
Slot, sobald ein Mensch aktiv chattet — das ist der akzeptierte Kompromiss
(mehr Slots würden wegen des MoE-Effekts oben ohnehin schaden, nicht helfen).

**Getestet (2026-07-06, warmer Service)**: Ein kurzer Chat-Request (18 Token
Prompt, 10 Token Antwort) mit `id_slot=0` brauchte 19,3s bei parallel
laufendem Hintergrund-Task auf Slot 1 — spürbar langsamer als die reine
Idle-Baseline (~14-15 tok/s), aber KEIN Wartezeit-Problem mehr: die Anfrage
musste nicht mehr hinter mehreren Automatik-Tasks in einer Schlange warten,
sondern bekam sofort einen Slot. Die verbleibende Verlangsamung ist normaler
Mehrbenutzer-Overhead (2 echte gleichzeitige Sequenzen teilen sich
Speicherbandbreite) — kein Bug, nicht weiter reduzierbar ohne auf Slot 0 ganz
zu verzichten.

---

## hauhau_client.py / hauhau_client.ts

Zentrale Client-Module, ersetzen JEDEN direkten Ollama/llama-server-HTTP-Aufruf
im System:

- `/root/werkraum/hauhau_client.py` — für alle Python-Skripte (Codewesen, GENI,
  welt/-System, innenleben, zensi)
- `/root/flextrawurst/scripts/hauhau_client.ts` — für Node/TypeScript
  (dolphin/serve_process_camera_preview.ts)

**Funktionen (beide Sprachen äquivalent)**: `chat()` (nicht-streamend),
`chat_stream()`/`chatStream()` (streamend), `chat_raw()`/`chatRaw()` (volle
Response für Tool-Calling). `think=False` per Default (steuert Thinking über
`chat_template_kwargs.enable_thinking`, funktioniert pro Request). `images=`
Parameter konvertiert rohe Base64-Strings automatisch ins OpenAI
`image_url`-Content-Part-Format.

**Alle bisherigen Koordinationsmechanismen blieben unverändert**: `fcntl`-Locks
(`/tmp/ollama_locks/slot_0.lock`), `CHAT_AKTIV_FLAG`-Warteschleifen
(`/tmp/dak_gord_chat_aktiv`) — die regeln weiterhin wer zuerst dran ist, nur
der eigentliche HTTP-Call dahinter wurde ausgetauscht.

**Trace-Log für Slot-0-Anfragen** (seit 2026-07-06): `hauhau_client.py`
(`trace_prioritaet()`) und `hauhau_client.ts` (`tracePrioritaet()`) schreiben vor
jedem `id_slot=0`-Call einen Eintrag nach `_shared/chat_prioritaet_trace.jsonl`
(Quelle, Zeitpunkt, Zeichenlänge, PID) — getrennt von den schweren
Chat-Verlaufsdateien. Grund: zwei Chat-Hänger am 2026-07-06 ließen sich trotz
gründlicher Recherche (alle Chat-Logs, alle Dateizeiten geprüft) keiner Quelle
zuordnen, weil llama-server selbst keine Client-Herkunft loggt. Bei künftigen
Hängern zuerst diese Datei prüfen, bevor der Dienst neu gestartet wird — ein
Neustart löscht den laufenden Zustand, der für die Diagnose gebraucht wird.

---

## Was weiterhin auf Ollama (Port 11434) läuft — bewusst, kein Aufräumfall

### dolphin-mistral:7b — "Freier Modus"

Eigenständiges, bereits unzensiertes Modell für einen separaten Zweck
(`/frei`-Befehl in dak+gord, `agent/dak_gord_system/freier_modus.py`) —
keine gemma4-Altlast, absichtlich nicht migriert.

### Kleines Vision-Modell (4,5B) — Bild-Beschreibung

`fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b` in
`serve_process_camera_preview.ts`. Bewusste, dokumentierte
Architektur-Entscheidung: das 35B-Hauptmodell brauchte auf reiner CPU über
3 Minuten für ein Bild (nie zu Ende getestet), das kleine Modell schafft
dieselbe Beschreibung in ~14 Sekunden. Zwei-Schritt-Pipeline: kleines Modell
beschreibt das Bild als Text, das Hauptmodell bekommt nur den Text, nie die
Rohbilddaten.

Der frühere Mechanismus, der nach jedem Bild-Upload das Hauptmodell für 90s
als "lädt neu" markierte (weil beide sich früher einen Ollama-Slot teilten),
wurde entfernt — seit das Hauptmodell auf llama-server läuft, gibt es diese
gegenseitige Verdrängung nicht mehr.

---

## Performance-Daten (gemessen 2026-07-06, hauhaucs-q6 auf llama-server)

| Szenario | Geschwindigkeit |
|---|---|
| Einzelne Anfrage, ohne Hintergrundlast, ohne mlock | ~14 tok/s (Start), bricht unter Last auf 3-5 tok/s ein |
| Einzelne Anfrage, mit `--mlock` | stabil 6-7 tok/s über eine ganze Generierung |
| Mit `AllowedCPUs=0-9` (Kernisolierung) | stabil ~4 tok/s (niedriger, aber garantiert) |
| Referenz Consumer-Hardware (Ryzen, gleiche Modellklasse) | 12-15 tok/s |

CPU-only-Faktor bleibt: 35B-A3B-MoE auf reiner CPU ist deutlich langsamer als
auf GPU — das ist die Grundlage aller Timing-Entscheidungen im System.

---

## Migrations-Historie

Vollständiger Bericht mit allen migrierten Dateien: `docs/2026-07-06_hauhaucs_migration_bericht.md`.
Kurzdokumentation pro migrierter Datei: `_claude/konzepte/*.md`.

---

*Weiter: [[13_langgraph]] | [[14_obsidian]]*
