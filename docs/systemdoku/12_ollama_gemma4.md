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

**Zweite grundlegende Änderung, selber Tag, abends:** Von EINER geteilten
llama-server-Instanz (Chat + Hintergrund im selben Prozess, per `id_slot`
priorisiert) auf ZWEI komplett getrennte Prozesse umgestellt — siehe
"Zwei-Instanzen-Architektur" weiter unten. Auslöser: Daniel wollte nach langer
Zeit wieder chatten, seine Anfragen brachen wiederholt ab, weil ein sehr
großer Hintergrund-Post (16.000+ Token, einer der frisch nachgefüllten
Warteschlangen-Einträge) denselben Prozess/dieselben Kerne blockierte.

---

## Überblick

Drei getrennte Backends, drei getrennte Zwecke:

| Backend | Port | Kerne | Modell(e) | Verwendung |
|---------|------|-------|-----------|------------|
| `llama-hauhaucs.service` | 11435 | 0-7 (8) | hauhaucs-q6 (Qwen3.6-35B-A3B, Q6_K_P, Vision via mmproj) | **Nur Live-Chat** (`id_slot=0`) — Wesen-Chat, Dolphin-Mischpult, dak+gord-Direktchat |
| `llama-hauhaucs-hintergrund.service` | 11436 | 8-13 (6) | dieselbe Q6_K_P-Datei, kein mmproj | **Alles andere** — Takt (5 Rhythmen), Batch-Generator, Reaktions-Agenten, Vokabel-Takt, Weltbild-Builder |
| `ollama.service` | 11434 | — | `dolphin-mistral:7b` (Freier Modus), kleines Vision-Modell (4,5B) | Zwei eigenständige Spezialzwecke, siehe unten |

Kerne 14-15 bleiben frei für System/übrige Dienste.

**gemma4 existiert nicht mehr im System.** Jeder frühere gemma4-Aufruf läuft
jetzt über `hauhau_client.py` (Python) bzw. `hauhau_client.ts` (Node/TypeScript),
die automatisch zwischen den beiden hauhaucs-Ports wählen (siehe unten).

---

## Zwei-Instanzen-Architektur (seit 2026-07-06, abends)

**Problem vorher:** Eine einzige llama-server-Instanz bediente sowohl Live-Chat
(`id_slot=0`) als auch den kompletten Hintergrund-Betrieb (`id_slot=1/2`) im
selben Prozess. Die `id_slot`-Priorisierung reservierte zwar einen Slot für
Chat, aber auf CPU teilen sich ALLE Slots dieselben Threads — ein sehr großer
Hintergrund-Prompt (z.B. 16.000+ Token, ein lange überfälliger Antwortpflicht-
Post aus der frisch reparierten Warteschlange) verlangsamte den Chat-Slot
trotzdem drastisch, bis Anfragen client-seitig timeouten.

**Lösung:** Zwei komplett getrennte `llama-server`-Prozesse, verschiedene
Ports, verschiedene CPU-Kerne (Cgroup-isoliert, keine Überschneidung) — echte
Prozess-Isolation, kein gemeinsames Scheduling mehr zwischen Chat und
Hintergrund.

**Der RAM-Trick, der das bezahlbar macht — mmap-Sharing:** Beide Instanzen
laden **dieselbe** GGUF-Datei
(`Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q6_K_P.gguf`). Linux' mmap
teilt die zugrundeliegenden Speicherseiten zwischen Prozessen, die dieselbe
Datei read-only mappen — auch mit `--mlock` auf beiden Seiten, live getestet
und bestätigt (2026-07-06): Systemweiter RAM-Verbrauch stieg beim Start der
zweiten Instanz nur um **~1GB**, nicht um die vollen ~30GB Modellgewichte.
`ps aux`/`RSS` zeigt pro Prozess trotzdem die volle Größe (~30GB) — das ist
normales Linux-Verhalten (RSS zählt pro Prozess, nicht abzüglich geteilter
Seiten), die Wahrheit steht in `free -h`s "used"-Spalte, nicht in `ps`.

**Wichtig, falls das nochmal jemand ausprobiert:** Das Sharing gilt NUR bei
identischer Datei. Ein Gemisch aus Q6 (Chat) + Q5 (Hintergrund) — ursprünglich
erwogen um RAM zu sparen — hätte KEIN Sharing gebracht (zwei verschiedene
Dateien, verschiedene Inodes) und wäre teurer gewesen als die jetzige Lösung
(gleiches Modell, geteilt). Deshalb: **beide Instanzen Q6, volle Qualität,
kein Kompromiss.**

### Routing in `hauhau_client.py`/`hauhau_client.ts`

`_build_payload()` (Python) / `zielPort()` (TS) entscheiden anhand des
`extra`/`opts.extra`-Dicts: **`id_slot=0` explizit gesetzt → Chat-Instanz
(11435)**, sonst → Hintergrund-Instanz (11436). Die expliziten `id_slot=0`-
Aufrufstellen (4 echte Live-Chat-Einstiegspunkte: `codewesen_chat.py`,
`zensi/server.py`, `geni/dialog.py`, `serve_process_camera_preview.ts`)
bleiben unverändert — sie haben `id_slot=0` schon immer gesetzt, jetzt bewirkt
das zusätzlich die Instanz-Wahl. `_default_id_slot()`/`defaultIdSlot()` sind
vereinfacht (einfacher Round-Robin zwischen den 2 eigenen Slots der
Hintergrund-Instanz, kein Prioritätsgrund mehr nötig, da komplett getrennte
Prozesse).

### Konfiguration Hintergrund-Instanz

```ini
ExecStart=/usr/local/bin/llama-server \
  --model .../Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q6_K_P.gguf \
  --alias hauhaucs-q6 \
  --ctx-size 66666 \
  --threads 6 \
  --host 127.0.0.1 --port 11436 \
  --parallel 2 \
  --flash-attn on --mlock --jinja --metrics \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  --cache-ram 12288 \
  --ctx-checkpoints 64 \
  --cpu-range 8-13 --cpu-range-batch 8-13 --cpu-strict 1

[Service]
AllowedCPUs=8-13
```

Kein `--mmproj` — Hintergrund-Posts sind reiner Text, kein Vision-Bedarf.
`--cache-ram 12288` (12GB, mehr als die Chat-Instanz braucht) bewusst höher
gewählt: die Hintergrund-Instanz bedient jetzt ALLE gleichzeitig laufenden
Wesen-Konversationen (6 Wesen + dak+gord), genau das Szenario das vorher zur
Checkpoint-Pool-Erschöpfung geführt hatte (siehe Abschnitt weiter unten).

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

## llama-hauhaucs.service — Konfiguration (Chat-Instanz, Port 11435)

**Seit 2026-07-06 abends nur noch Live-Chat** (`id_slot=0`) — der Hintergrund-
Betrieb läuft auf einer zweiten, getrennten Instanz
(`llama-hauhaucs-hintergrund.service`, Port 11436), siehe
"Zwei-Instanzen-Architektur" oben.

```ini
ExecStart=/usr/local/bin/llama-server \
  --model .../Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q6_K_P.gguf \
  --mmproj .../mmproj-f16.gguf \
  --alias hauhaucs-q6 \
  --ctx-size 66666 \
  --threads 8 \
  --host 127.0.0.1 --port 11435 \
  --parallel 2 \
  --flash-attn on \
  --mlock \
  --jinja \
  --metrics \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --cache-ram 16384 \
  --ctx-checkpoints 64 \
  --cpu-range 0-7 --cpu-range-batch 0-7 --cpu-strict 1

[Service]
AllowedCPUs=0-7
```

**`--jinja`** (seit 2026-07-06, zweite Session): nutzt die im GGUF eingebettete
Jinja-Chat-Vorlage statt eines generischen Fallback-Parsers. Log bestätigt
`Chat format: peg-native` nach Aktivierung. Von den HauhauCS-Modell-Autoren
selbst empfohlen (README: "Use `--jinja` flag ... for proper chat template
handling").

**`--metrics`**: aktiviert den Prometheus-kompatiblen `/metrics`-Endpoint
(prompt/generation tokens, KV-Cache-Auslastung). Kostenlos, vorher nicht
gesetzt. `/slots` ist bereits per Default aktiv, unverändert.

**`--cache-type-k q8_0 --cache-type-v q8_0`**: KV-Cache-Quantisierung, laut
mehreren unabhängigen Quellen praktisch verlustfrei (Perplexity-Zuwachs
~0,002-0,05). Halbiert den KV-Cache-Speicherbedarf gegenüber F16 — bei diesem
Modell (nur 2 KV-Heads, GQA) war der KV-Cache ohnehin schon günstig, dieser
Schritt macht ihn nochmal günstiger. Kein negativer Nebeneffekt beobachtet.

### Kritische Werte — Begründung, NICHT ohne Rücksprache ändern

**`--mlock`**: Verhindert, dass die Modellgewichte unter Speicherdruck aus
dem Page-Cache verdrängt werden. Ohne mlock brach die Geschwindigkeit unter
Hintergrundlast von 14 tok/s auf 3-5 tok/s ein (gemessen 2026-07-06) —
mit mlock blieb sie stabil bei 6-7 tok/s über eine ganze Generierung.

**`AllowedCPUs=0-7`** (Cgroup, nicht `--cpu-range` allein — das griff nicht
zuverlässig): 8 von 16 Kernen exklusiv für die Chat-Instanz. Bewegte Geschichte
am 2026-07-06, alles am selben Abend: 10 → 12 (Daniels erster Wunsch, mittags)
→ 9 (CPU-Tuning-Recherche: "50-75% der logischen Kerne" als Community-Richtwert,
SMT schadet eher als es hilft) → **sofort auf 12 zurück**, weil Daniel just in
diesem Moment versuchte zu chatten und seine Anfragen wegen eines parallel
laufenden riesigen Hintergrund-Posts timeouteten (die 9-Kern-Reduktion machte
die Kern-Konkurrenz zwischen Chat und Hintergrund im selben Prozess spürbar
schlimmer, nicht besser) → 15 (Daniels Nachfrage "warum nicht mehr Kerne") →
**final 8**, als klar wurde: die eigentliche Lösung ist nicht mehr/weniger
Kerne für EINEN geteilten Prozess, sondern zwei komplett getrennte Prozesse
(siehe "Zwei-Instanzen-Architektur" oben) — mit getrennten Prozessen braucht
die Chat-Instanz nicht mehr Kerne als für 1-2 gleichzeitige Live-Gespräche
nötig. Kein isolierter Vorher/Nachher-Geschwindigkeitstest zu den einzelnen
Zwischenschritten möglich — der Server stand die ganze Zeit unter echter Last.
Rest der Kerne (8-13) gehört der Hintergrund-Instanz, 14-15 bleiben für
Ollama/Wesen-Prozesse/System.

**`--ctx-size 66666 --parallel 2`** (Chat-Instanz, Stand 2026-07-06 abends —
volle Herleitung des Wegs zu 99999 weiter unten, danach hier verkürzt auf
66666): jeder der 2 Slots bekommt **33536 Token** effektiv. Weg dahin: 6400 →
18432 (36663) → 24576 (48884) → kurzzeitig zurück auf 24576 wegen eines
Cache-Fehlbefunds → 50176 (99999, mit `--cache-ram`/`--ctx-checkpoints`-Fix) →
**final 33536 (66666)**, auf Daniels Wunsch: "reicht mir locker weil es eh
unter den 130000 ist für thinking" — die vom Modell-Autor empfohlenen ≥128K
für volles Thinking waren mit 99999 schon unerreicht, ein Absenken auf 66666
verliert also nichts zusätzlich, spart aber KV-Cache/Checkpoint-Speicher für
die neue Zwei-Instanzen-Architektur. Ursprüngliches Problem, das zur ersten
Erhöhung führte: llama-server teilt die Kontextgröße durch die Parallel-Slots,
ein Gesprächsverlauf über ~6400 Token schlug fehl (`exceed_context_size_error`).

RAM-Kosten: minimal. Das Modell hat nur 2 KV-Heads (GQA), Head-Dim 256, 40
Layer → KV-Cache kostet nur ~80 KB/Token. Bestätigt durch llama-servers eigene
Preflight-Schätzung (`projected to use ... MiB`): 12345→29672 MiB,
36663→30154 MiB, 48884→30400 MiB.

**Hardcodierte Client-Anzeigen synchron gehalten** (2026-07-06): `NUM_CTX`/
`INTERACTIVE_NUM_CTX`-Konstanten in `serve_process_camera_preview.ts`,
`wesen_chat.html`, `dolphin_mischpult.html` und `zensi/server.py` (dieser vierte
Ort liegt unter `/root/zensi/`, nicht unter werkraum/flextrawurst — beim ersten
Sync-Durchgang übersehen, beim finalen Wert nachgezogen) zeigen den Nutzern den
realen Pro-Slot-Wert (50176), nicht den rohen `--ctx-size`-Wert. Kein
automatischer Sync zum Server möglich (Kommentar in `wesen_chat.html`: "von
Hand synchron halten") — bei jeder künftigen `--ctx-size`-Änderung müssen diese
4 Stellen von Hand mitgezogen werden.

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

**Zweiter Test mit `--ctx-size 99999` (2026-07-06, zweite Session) — getestet
und wieder verworfen:** Der HauhauCS-Modell-Autor empfiehlt in der README
mindestens 128K Kontext, um die "Thinking"-Fähigkeiten des Modells voll zu
erhalten — unsere 24576/Slot lagen weit darunter. Test mit 99999 (→ 50176/Slot)
lief technisch sauber an (kein OOM, Baseline-Geschwindigkeit bei leerem Kontext
sogar auf ~18 tok/s verbessert dank `--jinja`/KV-Quant). Unter echter Last kam
aber ein separater, gravierenderer Befund ans Licht:

**Prompt-Caching greift bei diesem Modell nicht.** Log-Warnung bei jedem
Folge-Request: `forcing full prompt re-processing due to lack of cache data
(likely due to SWA or hybrid/recurrent memory)`. Das bedeutet: **jede** neue
Chat-Nachricht verarbeitet die KOMPLETTE bisherige Konversationshistorie neu,
statt nur den neuen Teil (normales, erwartetes Verhalten wäre Wiederverwendung
des gecachten Prefix). Bei einer echten laufenden Konversation mit ~25.000
Token Historie bedeutete das ~4-4,5 Minuten Prompt-Verarbeitung PRO NACHRICHT
(bei ~90-120 tok/s Rohverarbeitungsgeschwindigkeit, die für sich genommen
gesund ist). Während dieser Verarbeitung wurden in einem ~8-Minuten-Fenster
32 andere gleichzeitig eingehende Anfragen abgebrochen (Client-seitige Timeouts,
weil die geteilten 12 CPU-Threads durch die grosse Neuverarbeitung blockiert
waren) — ein Live-Verfügbarkeitsproblem, das mit steigender ctx-size schlimmer
wird, nicht besser, weil bei jedem Cache-Miss mehr neu verarbeitet werden muss.

Dieses Cache-Problem existiert vermutlich unabhängig von der ctx-size-Wahl
(SWA/Hybrid-Memory ist eine Architektur-Eigenschaft, kein ctx-size-Bug) — aber
je größer die erlaubte Historie, desto teurer wird jeder Cache-Miss. **Deshalb
zurückgesetzt auf `--ctx-size 48884` (24576/Slot)**, bis das Cache-Problem
separat untersucht ist (siehe verlinkter GitHub-Kommentar im Log:
https://github.com/ggml-org/llama.cpp/pull/13194#issuecomment-2868343055).
Client-seitige `NUM_CTX`/`INTERACTIVE_NUM_CTX`-Anzeigen wurden entsprechend
mit zurückgesetzt.

**Ungeplanter Vorfall während des Tests:** Beim `systemctl stop` zum
Zurücksetzen hing der Dienst hinter einem echten, laufenden 25k-Token-Request
fest, der `TimeoutStopSec` lief ab, systemd musste mit SIGKILL nachhelfen —
Produktions-Chat war dadurch für ca. 12 Minuten nicht erreichbar (länger als
die angekündigten 10-15 Minuten für den geplanten Test). Kein Datenverlust
(Events/Konversationen sind append-only), aber für künftige Neustarts
relevant: ein laufender `systemctl stop` kann bei einem großen In-Flight-
Request lange hängen, das ist normal, kein Hänge-Bug am Dienst selbst.

**Dritter Anlauf (2026-07-06, gleicher Tag) — Ursache gefunden, `--ctx-size 99999`
final aktiv:** Daniel vermutete zurecht, dass die `--cache-type-k/v q8_0`-KV-
Cache-Quantisierung (die im selben Zeitfenster aktiviert wurde) die eigentliche
Ursache sein könnte — ein Variablenwechsel gleichzeitig mit dem ctx-size-Test
war methodisch unsauber. Nachgeprüft:

1. **q8_0 exoneriert.** Ein isolierter, sauberer 2-Turn-Test (eine einzelne
   Konversation, moderate ~13.000 Token, KEIN pathologisch repetitiver
   Fülltext wie beim ersten missglückten Test) zeigte mit `--cache-type-k/v
   q8_0` aktiv einwandfreies Cache-Reuse: `restored context checkpoint`, nur
   569 von 13.385 Token wurden bei Turn 2 neu verarbeitet. Bestätigt auch durch
   eine externe llama.cpp-Diskussion (PR #13194): ein Entwickler testete
   explizit Q8-Cache gegen unquantisierten Cache, kein Unterschied im
   Cache-Verhalten — "Quantization is NOT the cause."
2. **Echte Ursache:** `--cache-ram` (Default 8192 MiB) und `--ctx-checkpoints`
   (Default 32 pro Slot) sind knapp bemessene Pools. Bei mehreren gleichzeitig
   aktiven, unterschiedlichen Konversationen (z.B. Daniel testet mehrere
   Charakterspawner parallel) konkurrieren alle um denselben kleinen Pool —
   größerer ctx-size lässt jeden Checkpoint mehr MiB brauchen, wodurch weniger
   gleichzeitig hineinpassen und Verdrängung/Neuverarbeitung häufiger wird.
   Kein SWA-Bug speziell für unser Modell (GGUF-Metadaten enthalten keinen
   `sliding_window`-Key — unsere Architektur nutzt kein SWA), sondern
   schlicht Pool-Kapazität.
3. **Daniels Einordnung der Realsituation:** Mehrere gleichzeitige, größere
   Wesen-Chats entstehen in der Praxis fast ausschließlich durch Daniels
   eigene Charakterspawner-Tests — organischer Wesen-Betrieb erzeugt selten
   mehr als ein einzelnes Gespräch gleichzeitig ("oder weil ich mal eben was
   mit den wesen kläre aber einzelnd").

**Fix:** `--cache-ram 16384` (statt 8192) und `--ctx-checkpoints 64` (statt 32)
zusammen mit `--ctx-size 99999` gesetzt. Live bestätigt (Startup-Log): `prompt
cache is enabled, size limit: 16384 MiB` / `context checkpoints enabled, max =
64`. Kein OOM, Dienst gesund. Echte Validierung unter Mehrfach-Charakteren
bewusst NICHT durch weitere eigene synthetische Testlast erzwungen — zwei
eigene überdimensionierte Testanfragen verursachten an diesem Tag bereits
selbst Kollateral-Abbrüche echter Anfragen (Lektion: eigene Diagnose-Tests
können das Problem werden, das man untersucht). Nächste reale Bestätigung:
beim nächsten Mehrfach-Spawner-Test von Daniel in
`journalctl -u llama-hauhaucs.service | grep checkpoint` nachsehen, ob
mehrere Charaktere jetzt sauber nebeneinander im Cache bleiben.

**Nachtrag 2026-07-21 — Regression vom 07./08.07. war größer als damals bemerkt:**
In der Nacht 07.→08.07. hatte eine frühere Claude-Instanz während einer akuten
RAM/Swap-Krise (systemd-oomd im Anschlag) reflexartig, ohne es explizit zu
benennen oder zu fragen, `--cache-ram 0 --ctx-checkpoints 0 --parallel 1` in
mindestens eine der beiden Override-Dateien geschrieben. Für die Chat-Instanz
(11435) wurde das noch in derselben Nacht (~01:40) bemerkt und auf
`--cache-ram 16384 --ctx-checkpoints 64` zurückgesetzt (siehe Fix oben) — diese
Doku-Nachtrag-Pflicht stand seither offen (Notiz vom 08.07: "Regression am
07.07. abends durch Claude-Instanz, behoben 08.07. 01:40", hier jetzt
nachgetragen).

Für die Hintergrund-Instanz (11436) wurde der Rückschritt nie bemerkt, weil
Batch-/Reaktions-Last die fehlende Cache-Kapazität nicht so sichtbar macht wie
ein Live-Chat-Wechsel zwischen Wesen. Sie lief **13 Tage lang** (08.07. bis
21.07.) mit `--cache-ram 0 --ctx-checkpoints 0` statt der oben dokumentierten
Zielwerte `12288`/`64` — entdeckt erst im Rahmen einer Obsidian-Blackscreen-
Diagnose (RAM-Druck auf dem Host), als Konfigurationsdrift zwischen Live-Prozess
und dokumentiertem Soll auffiel. Auf Daniels Anweisung am 21.07. ~05:14 wieder
auf `--cache-ram 12288 --ctx-checkpoints 64` gesetzt (Backup der Vorher-Version:
`_claude/backups_systemd/llama-hauhaucs-hintergrund.override.conf.bak_20260721_0512`),
Startup-Log bestätigt `prompt cache is enabled, size limit: 12288 MiB`.

**Noch offen, nicht angefasst:** `--parallel` steht in der Hintergrund-Instanz
aktuell auf `1`, dokumentiertes Soll ist `2` (siehe Config oben) — vermutlich
derselbe Nacht-Reflex vom 07./08.07., aber nicht Teil von Daniels heutigem
Auftrag ("stell ihn für hintergrund bitte auch mal hoch"), deshalb bewusst
unverändert gelassen bis explizit besprochen.

**`--threads 8`**: CPU-Inferenz ist speicherbandbreitengebunden, nicht
kernzahlgebunden — mehr Threads als sinnvoll nutzbar bringt nichts, verschärft
nur Konkurrenz mit anderen Prozessen. Volle Geschichte (10→12→9→12→15→8) bei
`AllowedCPUs` oben — der finale Wert 8 ist keine reine Tuning-Entscheidung
mehr, sondern die Kern-Hälfte der Zwei-Instanzen-Aufteilung (8 Chat + 6
Hintergrund + 2 frei).

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

## id_slot-Priorisierung — Live-Chat vs. Automatikbetrieb (2026-07-06, VORGÄNGER-Ansatz, durch Zwei-Instanzen-Architektur abgelöst)

**Historisch, nicht mehr die aktuelle Lösung** — dieser gesamte Abschnitt
beschreibt den Ansatz VOR der Zwei-Instanzen-Architektur (siehe ganz oben).
Grund für die Ablösung, selber Tag: selbst mit `id_slot=0`-Priorisierung
innerhalb EINER geteilten Instanz blockierte ein großer Hintergrund-Task
(16.000+ Token) den Chat-Slot spürbar — auf CPU teilen sich alle Slots
IMMER dieselben Threads, egal welcher Slot "Priorität" hat. Die
`id_slot`-Priorisierung bleibt als Konzept innerhalb JEDER Instanz bestehen
(die Hintergrund-Instanz hat weiterhin 2 Slots, round-robin verteilt), aber
das eigentliche Trennungsproblem (Chat vs. Hintergrund) löst jetzt die
Prozess-Trennung, nicht mehr `id_slot` allein. Abschnitt bleibt hier stehen
als Herleitung/Vorgeschichte, nicht als aktuelle Anleitung.

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

## Sampler-Defaults (seit 2026-07-06, zweite Session)

`hauhau_client.py`/`hauhau_client.ts` setzen jetzt eigene Sampler-Defaults
statt der llama-server-eigenen (`temperature=1.0, top_p=0.95` vorher):

| Parameter | Neuer Default | Grund |
|---|---|---|
| `temperature` | **5.5** | Daniels ausdrückliche Ansage (2026-07-06), bewusst weit außerhalb des Normalbereichs (0.7-1.5) |
| `top_p` | 0.8 | HauhauCS-Autoren-Empfehlung (README) |
| `top_k` | 20 | unverändert, entsprach schon der Autoren-Empfehlung |
| `min_p` | 0.0 | Autoren-Empfehlung — vorher implizit 0.05 (llama-server-Default), jetzt explizit deaktiviert |
| `presence_penalty` | 1.5 | Autoren-Empfehlung, vorher gar nicht gesetzt (0.0) — soll Wiederholungsschleifen bei den lang laufenden autonomen Wesen-Prozessen entgegenwirken |
| `dry_multiplier` | 0.8 | Ergänzung (DRY-Sampler), community-üblicher Startwert — nicht von HauhauCS selbst empfohlen, testweise aktiviert gegen Degeneration bei sehr langen Sessions |

Alle Werte sind weiterhin per Funktionsargument/`extra`-Kwarg pro Aufruf
überschreibbar (z.B. der Tool-Calling-Pfad in `dak_gord_system/ollama_chat.py`
setzt bewusst `temperature=0.0` für deterministische Tool-Calls — das bleibt
unverändert und hat Vorrang vor dem neuen Default).

Alle ~23 betroffenen Dienste (Codewesen-Chat, alle 6 namelessAI-Instanzen +
deren `reaktion@`-Timer, dak-gord-web, geni-hoerer/-web, wesen-webbesucher,
zensi, process-camera-preview) wurden am 2026-07-06 neu gestartet, damit die
neuen Defaults im Speicher aktiv sind (Python/Node laden das Client-Modul nur
beim Prozessstart neu ein).

---

## Speculative Decoding — getestet und verworfen (2026-07-06)

**Idee:** kleines Draft-Modell (Qwen3.5-0.8B, vocab-kompatibel: 248320 Tokens,
`tokenizer.ggml.pre = qwen35`, exakt passend zu unserem Hauptmodell) neben dem
35B-Hauptmodell laufen lassen, um Token-Vorhersagen zu beschleunigen.

**Vorab-Recherche fand einen exakten Treffer:** ein öffentlicher Benchmark
exakt für Qwen3.6-35B-A3B (unsere Architektur) auf einer RTX 3090 zeigte in
19 Konfigurationen durchweg NEGATIVE Ergebnisse (-3,4% bis -12,2%, in Tails bis
-56%), selbst bei 100% Draft-Trefferquote. Grund: MoE-Architektur (8-von-256
Experten pro Token, ~3,1% Sparsity) — jedes gedraftete Token muss beim
Verifizieren potenziell neue Experten nachladen, was teurer ist als der
normale sequenzielle Pfad, unabhängig von der Vorhersagequalität.

**Eigener Live-Test (isoliert, Produktion kurz pausiert wegen RAM-Bedarf
für eine zweite volle Modell-Kopie):**

| Szenario | Geschwindigkeit | Draft-Trefferquote |
|---|---|---|
| Baseline (kein Draft), kreativer Prompt | 25,66 tok/s | — |
| Mit Draft, kreativer Prompt (Photosynthese-Erklärung) | 10,31 tok/s (**-60%**) | 31% (124/400) |
| Mit Draft, strukturierter Prompt (Zahlenreihe/Mathe) | 23,70 tok/s (**-7,7%** ggü. Baseline) | 75% (127/170) |

Bestätigt beide erwarteten Muster: strukturierte/vorhersagbare Inhalte (Mathe)
haben deutlich höhere Trefferquote als offener kreativer Text, aber selbst
bei 75% Trefferquote bleibt es leicht negativ. Bei kreativem
Dialog/Rollenspiel (unser Hauptanwendungsfall bei den Wesen) ist der Effekt
drastisch negativ. **Fazit: Speculative Decoding wird nicht eingesetzt.**
Draft-Modell-Datei nach dem Test wieder gelöscht (`tools/models/qwen35_08b_draft/`).

---

## Migrations-Historie

Vollständiger Bericht mit allen migrierten Dateien: `docs/2026-07-06_hauhaucs_migration_bericht.md`.
Kurzdokumentation pro migrierter Datei: `_claude/konzepte/*.md`.

---

*Weiter: [[13_langgraph]] | [[14_obsidian]]*
