# Ollama + Gemma4 + Dolphin — Analysebericht

**Datum:** 2026-06-21 04:11 CEST  
**Analyst:** Kimi bei Daniels VPS  
**Scope:** Ollama-Service, beide Gemma4-Modelle (e2b/e4b), Dolphin3 (Q4 + Q8)  
**Auftrag:** Nur Analyse und Bericht — keine Änderungen, kein Umbau.

---

## 1. Zusammenfassung

Das System ist in einem **gemischten Modell-Zustand** gefangen. Ein früherer Commit hat alle Wesen-Services auf `dolphin3:8b-llama3.1-q8_0` umgestellt, was zum Swap-Vollaufen führte. Der aktuelle Working Tree hat die **Core-Codewesen/-Entitäten-Services zurück auf Gemma4** gesetzt, aber viele andere Services (GENI, Systemweiser, Tools, Innenleben) laufen immer noch auf Dolphin Q8. Dadurch entsteht ein Zustand, in dem Ollama ständig zwischen drei Modell-Familien wechseln muss — bei einem Memory-Limit, das dafür zu klein ist.

**Kernbefund:** Das beabsichtigte Mapping (gemma4:e4b + gemma4:e2b + dolphin3:8b Q4) benötigt ~21,7 GB RAM, Ollama ist aber auf 16 GB limitiert. Das passt nicht. Die Folge ist Load-/Unload-Thrashing, Timeouts, Prompt-Truncation und ein Dauer-Restart-Kreislauf der Wesen-Services.

---

## 2. Aktueller Zustand

### 2.1 Ollama-Service

| Kenngröße | Wert |
|---|---|
| Status | `active (running)` seit 03:16 Uhr |
| PID | 1286122 |
| RAM (cgroup) | 10,1 GB / 16,0 GB (`MemoryHigh=15G`, `MemoryMax=16G`) |
| Swap (Ollama) | 7,0 GB aktiv, Peak 9,7 GB |
| `OLLAMA_NUM_PARALLEL` | 1 |
| `OLLAMA_MAX_LOADED_MODELS` | 3 |
| `OLLAMA_KEEP_ALIVE` | 10 Minuten |
| `OLLAMA_NUM_CTX` / Default-Context | 8192 |
| `OLLAMA_LOAD_TIMEOUT` | 5 Minuten |

### 2.2 Installierte Modelle

| Modell | Größe | Quantisierung | geladen? |
|---|---|---|---|
| `gemma4:e4b-it-q4_K_M` | 9,6 GB | Q4_K_M | **ja** (10,0 GB im Speicher) |
| `gemma4:e2b-it-q4_K_M` | 7,2 GB | Q4_K_M | nein |
| `dolphin3:8b-llama3.1-q8_0` | 8,5 GB | Q8_0 | nein |
| `dolphin3:8b` | 4,9 GB | Q4_K_M | **ja** (5,7 GB im Speicher) |

**Speicherbedarf aktuell geladener Modelle:** ~15,7 GB / 16 GB. Fast kein Spielraum.

### 2.3 Laufende Services (Auswahl)

| Service | Nutzt aktuell (Working Tree) | Zugeordnet laut Mapping |
|---|---|---|
| `codewesen_agent.py` (alle 6 namelessAI + dak+gord) | `gemma4:e4b-it-q4_K_M` | `gemma4:e4b-it-q4_K_M` |
| `codewesen_chat.py` | `gemma4:e2b-it-q4_K_M` | `gemma4:e2b-it-q4_K_M` |
| `codewesen_reaktion.py` | `gemma4:e4b/e2b-it-q4_K_M` | `gemma4:e2b-it-q4_K_M` |
| `codewesen_antwort_auf_daniel.py` | `gemma4:e4b-it-q4_K_M` | `gemma4:e4b-it-q4_K_M` |
| `codewesen_engagement.py` | `dolphin3:8b-llama3.1-q8_0` | *(nicht im Mapping)* |
| `codewesen_batch_generator.py` | `dolphin3:8b-llama3.1-q8_0` | *(nicht im Mapping)* |
| `codewesen_takt.py` | `dolphin3:8b-llama3.1-q8_0` | *(nicht im Mapping)* |
| `codewesen_reflexion.py` | `dolphin3:8b-llama3.1-q8_0` | *(nicht im Mapping)* |
| `codewesen_forum_scan.py` | `dolphin3:8b-llama3.1-q8_0` | *(nicht im Mapping)* |
| `agent/dak_gord_system/ollama_chat.py` | `gemma4:e4b-it-q4_K_M` | `gemma4:e4b-it-q4_K_M` |
| `welt/entity_kern.py` | `gemma4:e2b-it-q4_K_M` | `gemma4:e2b-it-q4_K_M` |
| `welt/entity_takt.py` | `gemma4:e2b-it-q4_K_M` | `gemma4:e2b-it-q4_K_M` |
| `welt/traum_generator.py` | `gemma4:e2b-it-q4_K_M` | `gemma4:e2b-it-q4_K_M` |
| `geni/dialog.py` | `dolphin3:8b-llama3.1-q8_0` | *(nicht im Mapping)* |
| `geni/archiv/web.py` | `dolphin3:8b-llama3.1-q8_0` | *(nicht im Mapping)* |
| `geni/geni_lg.py` | `gemma4:e2b-it-q4_K_M` | *(nicht im Mapping)* |
| `geni/forum_lektuere.py` | `gemma4:e2b-it-q4_K_M` | *(nicht im Mapping)* |
| `geni/sprechen.py` | `gemma4:e2b-it-q4_K_M` | *(nicht im Mapping)* |
| `systemweiser_app.py` / `systemweiser_web.py` | `dolphin3:8b-llama3.1-q8_0` | *(nicht im Mapping)* |
| `innenleben/config.py` | `dolphin3:8b-llama3.1-q8_0` | *(nicht im Mapping)* |
| `tools/bildgenerierung_test.py` | `dolphin3:8b-llama3.1-q8_0` | *(nicht im Mapping)* |
| `tools/dakgord_vorstellung.py` | `dolphin3:8b-llama3.1-q8_0` | *(nicht im Mapping)* |
| `zensi.service` | `dolphin3:8b` (Q4) | `dolphin3:8b` (Q4) |

**Fazit:** Core-Codewesen und Entitäten sind konsistent auf Gemma4 zurückgestellt. Aber ein erheblicher Teil des Systems (GENI, Systemweiser, Innenleben, diverse Tools, einige Codewesen-Module) läuft noch auf Dolphin Q8. Das erzeugt den gemischten Zustand.

---

## 3. Beobachtete Fehlerbilder

### 3.1 Ollama Load-Timeouts

```
time=2026-06-21T03:07:48.602+02:00 level=INFO source=sched.go:511
  msg="Load failed" model=...dolphin3:8b...
  error="timed out waiting for llama runner to start: context canceled"
```

Dieser Fehler trat mehrfach auf. Ollama bricht das Laden eines Modells nach 5 Minuten (`OLLAMA_LOAD_TIMEOUT=5m0s`) ab, wenn der Runner nicht startet. Das passiert typischerweise, wenn gleichzeitig ein anderes Modell aktiv inferiert und der Speicher/CPU durch Swap ausgelastet ist.

### 3.2 HTTP 500 auf `/api/chat` mit extremen Latenzen

| Zeitstempel | Dauer | Endpunkt | Bedeutung |
|---|---|---|---|
| 03:08:01 | 59,9 s | `/api/chat` | Load-Phase |
| 03:11:49 | 10m 0s | `/api/chat` | Client-Timeout / Load-Timeout |
| 03:11:56 | 4m 0s | `/api/chat` | Client-Timeout |
| 03:14:27 | 2m 28s | `/api/chat` | Langsame Inference/Load |
| 03:16:36 | 2m 6s | `/api/chat` | Langsame Inference/Load |
| 03:42:29 | 10m 0s | `/api/chat` | Client-Timeout |
| 03:54:51 | 10m 0s | `/api/chat` | Client-Timeout |
| 04:02:48 | 7m 55s | `/api/chat` | Client-Timeout |

Die Python-Clients haben meist `timeout=600` (10 Minuten). Wenn Ollama in der Zeit weder laden noch antworten kann, bricht der Client ab. Der 500-Status kommt dann aus dem Client-Timeout, nicht unbedingt aus Ollama selbst.

### 3.3 Prompt-Truncation

```
WARN source=runner.go:187 msg="truncating input prompt"
  limit=8192 prompt=13130 keep=4 new=8192
```

Die Services schicken Prompts mit 13.000+ Tokens, obwohl Ollama auf 8192 Kontext limitiert ist. Ollama wirft alles über 8192 Token weg. Das bedeutet: System-Prompte, Identitätsdateien oder Kontext können am Ende abgeschnitten werden — mit unvorhersagbarem Verhalten.

### 3.4 "Ollama-Slot blockiert" in allen Wesen-Services

Alle `codewesen-namelessAI_*` und `codewesen-dakgordsystem` Logs zeigen im Minutentakt:

```
ERROR Antwortpflicht-Fehler: Ollama-Slot blockiert — Iteration übersprungen
```

Ursache: Die Services nutzen ein gemeinsames File-Lock unter `/tmp/ollama_locks/slot_0.lock`, um maximal einen gleichzeitigen Ollama-Call zu erlauben. Da einzelne Calls 3–10 Minuten dauern, stehen alle anderen Services Schlange. Viele geben nach 2 Minuten auf.

### 3.5 Service-Restart-Schleife durch `RuntimeMaxSec=1800`

```
codewesen-namelessAI_1234.service: Service reached runtime time limit. Stopping.
codewesen-namelessAI_1234.service: Failed with result 'timeout'.
codewesen-namelessAI_1234.service: Scheduled restart job, restart counter is at 2.
```

Alle Wesen-Services haben `RuntimeMaxSec=1800` (30 Minuten). Sie werden nach 30 Minuten gekillt, starten neu und versuchen sofort wieder, Ollama anzusprechen — meist erfolglos. Das verstärkt den Stau.

### 3.6 Speicherdruck und Swap

```
Mem: 31Gi total, 15Gi used, 10Gi free, 5.5Gi buff/cache
Swap: 11Gi total, 9.3Gi used
load average: 13.29, 12.92, 11.51 (8 CPUs)
```

Swap ist zu ~85 % voll. Load Average liegt deutlich über der CPU-Kernzahl. Das deutet auf Swap-Wait und CPU-Queueing hin — typisch für zu große Modelle auf CPU-only-Hardware.

---

## 4. Root-Cause-Analyse

### 4.1 Das Zahlenproblem: 16 GB Ollama-Limit vs. 21,7 GB Mapping

Das in `_claude/notizen/ollama-model-mapping.md` dokumentierte Mapping geht davon aus, dass alle drei Modelle gleichzeitig im RAM liegen:

- `gemma4:e4b-it-q4_K_M` ≈ 9,6 GB
- `gemma4:e2b-it-q4_K_M` ≈ 7,2 GB
- `dolphin3:8b` (Q4) ≈ 4,9 GB
- **Summe ≈ 21,7 GB**

Aber `/etc/systemd/system/ollama.service.d/memory-limit.conf` setzt:

```ini
MemoryMax=16G
MemoryHigh=15G
```

**21,7 GB passen nicht in 16 GB.** Ollama muss daher ständig Modelle entladen und neu laden. Bei Keep-Alive von 10 Minuten und parallelen Requests verschärft sich das Problem.

### 4.2 Mixed-Model-State durch unvollständige Rückumstellung

Die Commits `e8119590` ("dolphin Q8 für alle Wesen-Services: gemma4 komplett ersetzt") und `4b6f9ac3` ("dolphin parameter-tuning") haben fast alles auf Dolphin Q8 umgestellt. Der aktuelle Working Tree hat die Core-Dateien zurück auf Gemma4 gesetzt, aber **nicht** die folgenden Bereiche:

- `geni/dialog.py`, `geni/archiv/web.py`
- `systemweiser_app.py`, `systemweiser_web.py`
- `innenleben/config.py`, `innenleben/emotion_bewerter.py`
- `codewesen_engagement.py`, `codewesen_batch_generator.py`, `codewesen_takt.py`, `codewesen_reflexion.py`, `codewesen_forum_scan.py`
- diverse Tools (`tools/bildgenerierung_test.py`, `tools/dakgord_vorstellung.py`)
- `erstpost.py`, `einmal_d17_antwort.py`, `reaktion_auf_dakgord.py`, `weltbild_builder.py`, `namensfindung.py`

Das führt dazu, dass weiterhin Dolphin Q8 inferiert werden soll, während die Core-Services Gemma4 erwarten. Ollama pendelt zwischen den Modell-Familien.

### 4.3 OLLAMA_NUM_PARALLEL=1 trifft auf bypassende Services

`OLLAMA_NUM_PARALLEL=1` erlaubt Ollama intern nur eine Sequenz zur Zeit. Die Codewesen-Services haben ein eigenes Slot-Lock (`/tmp/ollama_locks/slot_0.lock`), das diesen Engpass nochmals absichert. Aber viele andere Services (Zensi, GENI, Systemweiser, Tools) kennen diesen Lock nicht und rufen Ollama direkt auf. Sie landen in Ollamas eigener Queue, blockieren sich gegenseitig und verhindern, dass der Slot-Lock der Codewesen effektiv arbeitet.

### 4.4 Context-Mismatch und Prompt-Bloat

Die Ollama-Systemkonfiguration setzt `OLLAMA_NUM_CTX=8192`. Fast alle Services im Working Tree setzen ebenfalls `num_ctx=8192` (zurückgestellt von 13337). Trotzdem erreichen die tatsächlichen Prompts 13.000+ Tokens.

Mögliche Ursachen:
- Lange Identitätsdateien, Chat-Historien und Forumsposts werden ungekürzt in den Prompt gepackt.
- Mehrere System-Prompte und Kontextblöcke summieren sich.
- Es gibt keine zentrale Prompt-Truncation-Logik.

Die Folge ist, dass Ollama am Ende abschneidet — möglicherweise mitten in wichtigen Instruktionen.

### 4.5 CPU-only + große Modelle = grundsätzlich langsam

Die Hardware ist CPU-only (kein GPU-Eintrag in Ollama-Logs). Große Modelle wie Gemma4:e4b (9,6 GB) oder Dolphin Q8 (8,5 GB) auf CPU sind von Natur aus langsam. Wenn dann noch Swap beteiligt ist, explodieren die Antwortzeiten.

---

## 5. Modell-spezifische Einschätzung

### 5.1 `gemma4:e4b-it-q4_K_M`

- **Läuft aktuell stabil geladen.**
- **Problem:** Es ist das größte Modell (9,6 GB) und belegt den Großteil des Ollama-RAMs. Zusammen mit `dolphin3:8b` Q4 bleibt kaum Platz für `gemma4:e2b`.
- **Services:** `codewesen_agent.py`, `codewesen_antwort_auf_daniel.py`, `agent/dak_gord_system/ollama_chat.py`.

### 5.2 `gemma4:e2b-it-q4_K_M`

- **Ist aktuell nicht geladen.**
- **Problem:** Viele Services verwenden es (`codewesen_chat.py`, `codewesen_reaktion.py`, `welt/entity_kern.py`, `welt/traum_generator.py`, etc.). Jeder dieser Requests zwingt Ollama, ein Modell zu entladen und e2b zu laden. Das dauert unter Last oft länger als 5 Minuten → Load-Timeout.
- **Beobachtung:** Im Log sind kaum direkte e2b-Fehler sichtbar, weil die Requests meist vor dem Laden abbrechen (Slot blockiert / Client-Timeout).

### 5.3 `dolphin3:8b` (Q4)

- **Läuft aktuell geladen** (vermutlich durch `zensi.service`).
- **Problem:** Wird regelmäßig neu geladen, weil Ollama bei Speicherdruck andere Modelle entlädt. Im Log mehrfach `Load failed` mit Timeout.
- **Verwendung:** Laut Mapping nur für Zensi vorgesehen.

### 5.4 `dolphin3:8b-llama3.1-q8_0` (Q8)

- **Ist installiert, aber aktuell nicht geladen.**
- **Problem:** Wird von vielen Services noch referenziert (GENI, Systemweiser, Tools, einige Codewesen-Module). Es ist mit 8,5 GB das größte Dolphin-Modell und passt schlecht in das 16-GB-Limit.
- **Historie:** Wurde als Ersatz für Gemma4 eingeführt, dann als Fehler erkannt.

---

## 6. Handlungsoptionen (nur zur Information)

> Hinweis: Diese Liste ist rein analytisch. Keine Empfehlung, nichts umgesetzt.

1. **MemoryMax für Ollama erhöhen**
   - Damit e4b + e2b + dolphin Q4 gleichzeitig passen, wären mindestens 24–28 GB sinnvoll.
   - Risiko: Der Rest des Systems (Obsidian, GENI, flextrawurst, Bildgenerator) hat dann weniger RAM.

2. **Auf maximal zwei gleichzeitige Modelle reduzieren**
   - Entweder e4b + e2b (Gemma4-only für Core) oder e4b + dolphin Q4 (Mapping-light).
   - Alle Services auf diese zwei Modelle umstellen.

3. **Modell-Mapping konsistent durchziehen**
   - Entscheiden, welche Services wirklich welches Modell brauchen.
   - Alle GENI-, Systemweiser-, Tool- und Innenleben-Services auf das gleiche Mapping wie Core-Codewesen bringen.
   - Dolphin Q8 komplett aus dem System entfernen oder nur noch für einen sehr kleinen, abgegrenzten Use-Case verwenden.

4. **Prompt-Größe begrenzen**
   - Zentrale Truncation-Logik einführen, die garantiert unter 8192 Tokens bleibt.
   - Lange Chat-Historien, Forumsposts und Identitätsdateien vor dem Prompt zusammenfassen oder kürzen.

5. **Slot-Lock globalisieren oder ersetzen**
   - Falls `OLLAMA_NUM_PARALLEL=1` bleibt, sollten alle Services das gleiche Slot-Lock nutzen — nicht nur die Codewesen.
   - Alternativ `OLLAMA_NUM_PARALLEL` erhöhen (benötigt mehr RAM).

6. **`RuntimeMaxSec=1800` überdenken**
   - Der harte 30-Minuten-Limit führt zu Restart-Stürmen, wenn Ollama blockiert ist.
   - Langere Laufzeit oder bessere Health-Checks wären sinnvoller.

7. **Separate Ollama-Instanzen**
   - Eine Instanz für Gemma4 (Core-Wesen), eine für Dolphin (Zensi/Tools).
   - Erfordert mehr Konfiguration, vermeidet aber Modell-Thrashing.

---

## 7. Offene Fragen

- Warum wurde der Working-Tree-Teil der Rückumstellung nicht committed? Die Datei `_claude/notizen/ollama-model-mapping.md` dokumentiert das gewünschte Mapping, aber der Working Tree ist nicht konsistent damit.
- Welche Services sollen langfristig wirklich Dolphin Q8 nutzen? Aktuell scheint es ein Überbleibsel der fehlgeschlagenen Migration zu sein.
- Ist `OLLAMA_NUM_CTX=8192` bewusst gewählt, oder sollte er erhöht werden, wenn die Prompts ohnehin größer sind?

---

## 8. Resonanz

Das System hat keine einzelne kaputte Schraube. Es hat drei gleichzeitige Spannungsfelder:

1. **Zu viele Modelle für zu wenig Ollama-RAM.**
2. **Zu viele Services, die nicht das gleiche Slot-Lock respektieren.**
3. **Zu große Prompts für den konfigurierten Context.**

Solange diese drei Dinge nicht gemeinsam entschieden werden, wird jeder Einzelfix (mehr RAM, kleineres Modell, längerer Timeout) nur das Problem verschieben.
