---
datum: 2026-06-23
betrifft: [llama-server, ollama-ersatz, hauhaucs, performance, cpu-inference]
importable: false
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

# Plan: llama-server als Ollama-Ersatz für hauhaucs

## Was ich gelesen habe

Recherchiert am 2026-06-23. Quellen: Community-Benchmarks, markaicode.com, ventusserver.com, willschenk.com
(migrating_to_llama_cpp), unsloth.ai (llama-server OpenAI endpoint), github.com/ggml-org/llama.cpp.

Kernbefund: llama-server ist der native Inference-Server aus demselben llama.cpp-Codebase auf dem Ollama
selbst aufbaut — aber ohne die Verwaltungsschicht. Das bedeutet weniger Overhead, direktere Kontrolle
über Threading, KV-Cache-Slots und Prefill-Verhalten.

Der wichtigste praktische Befund: Ollama verarbeitet Requests standardmäßig sequenziell und implementiert
weder PagedAttention noch Continuous Batching. Bei Concurrent-Load fällt die Performance deutlich stärker
ab als bei llama-server, der per `--slots` mehrere parallele Anfragen mit echtem KV-Cache-Sharing
verarbeiten kann.

Für unser Setup ist der entscheidende Punkt: das GGUF-Modell von hauhaucs liegt **bereits lokal** als
SHA256-Blob in Ollamas Cache — kein erneuter Download nötig.

## Was ich verstehe

llama-server ist für diesen Anwendungsfall (ein großes Modell, CPU-only, kontrolliertes Threading,
kein Modell-Management nötig) die direktere Lösung. Ollama hat Mehrwert bei:
- mehreren Modellen verwalten
- bequemem Pull/Update per CLI
- automatischem Modelfile-System

Wir brauchen genau das für hauhaucs NICHT. Das Modell ist gepullt, die Parameter stehen fest,
das Modelfile-System schränkt eher ein als es hilft.

Ollama bleibt für Gemma4/Codewesen/GENI — die brauchen das Management.
Hauhaucs/Zensi/Dolphin könnten auf llama-server wechseln.

## Was ich nicht verstehe

Wie sich Qwen35moe (MoE-Architektur) konkret unter llama-server vs Ollama verhält — die gemessenen
Speedups in Benchmarks betreffen meist dichte Modelle. Für MoE gibt es weniger publizierte Zahlen.
Das muss Daniel im Test klären.

## Was mich interessiert

Ob `--slots` bei llama-server wirklich hilft wenn zensi und dolphin gleichzeitig Anfragen stellen —
statt dass Ollama das zweite Request wartet bis das erste fertig ist.

## Was zusammenhängt und wie

```
hauhaucs GGUF ─────► llama-server (Port 11435)
                              │
            ┌─────────────────┤─────────────────┐
            ▼                                    ▼
    zensi/server.py                serve_process_camera_preview.ts
    (PORT 8043 → Zensi)            (PORT 8787 → Dolphin/Mischpult)
```

Ollama bleibt auf Port 11434 für alle anderen Dienste (Gemma4, Codewesen, GENI).

## Was konzeptionell darin steht

Der Wechsel ist kein "Ollama ist kaputt" — es ist eine Aufgabentrennung:
- Ollama = Modell-Manager für viele kleine Modelle (Gemma4-Familie)
- llama-server = dedizierter Server für ein großes Produktionsmodell (hauhaucs)

## Was mich heute beschäftigt hat

Die Erkenntnis dass das GGUF bereits lokal liegt und llama-server innerhalb von Sekunden startet
wenn der Pfad bekannt ist. Kein erneuter Download, kein Umbau der Modell-Daten.

## Was mich noch beschäftigt

Der Reload-Overhead fällt bei llama-server weg: der Prozess startet einmal, lädt das Modell,
und bleibt im RAM bis der Prozess stirbt. Ollama lädt/entlädt nach keep_alive-Timeout.
Das ist für einen dedizierten Dienst ein echter Vorteil.

## Tiefer eingetaucht

### GGUF-Pfad (bereits verfügbar)

```
/usr/share/ollama/.ollama/models/blobs/sha256-c70792383705b719daad865408e03758e048c6a2aa5eae4c1bb522e03a96a9d6
```

Das ist das hauhaucs IQ4_XS GGUF — 19.6 GB, direkt nutzbar.

### Installation llama-server

Option A — Release-Binary (schnell, kein Build):
```bash
# Aktuelle Release-Version von github.com/ggml-org/llama.cpp/releases
wget https://github.com/ggml-org/llama.cpp/releases/latest/download/llama-[version]-bin-ubuntu-x64.zip
unzip ... && cp llama-server /usr/local/bin/
```

Option B — Build aus Source (dauert ~10–15 Min auf 8 Kernen, gibt optimierten AVX2-Build):
```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build -DLLAMA_NATIVE=ON
cmake --build build --config Release -j8
cp build/bin/llama-server /usr/local/bin/
```

Option C — apt (wenn verfügbar):
```bash
apt install llama-cpp-server
```

### Start-Befehl (Referenz)

```bash
llama-server \
  --model /usr/share/ollama/.ollama/models/blobs/sha256-c70792383705b719daad865408e03758e048c6a2aa5eae4c1bb522e03a96a9d6 \
  --alias hauhaucs \
  --ctx-size 8192 \
  --threads 5 \
  --host 127.0.0.1 \
  --port 11435 \
  --slots 2 \
  --chat-template qwen3 \
  --no-mmap
```

Flags erklärt:
- `--threads 5` — entspricht num_thread 5 (Daniel's Vorgabe)
- `--slots 2` — bis zu 2 parallele Anfragen (zensi + dolphin können gleichzeitig antworten)
- `--chat-template qwen3` — das richtige Template für hauhaucs
- `--no-mmap` — lädt alles in RAM statt memory-mapped (stabiler auf VPS ohne huge pages)
- `--alias hauhaucs` — der Modellname in der API-Antwort

### Systemd-Service

```ini
# /etc/systemd/system/llama-hauhaucs.service
[Unit]
Description=llama-server hauhaucs (Qwen3.6-35B IQ4_XS)
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/llama-server \
  --model /usr/share/ollama/.ollama/models/blobs/sha256-c70792383705b719daad865408e03758e048c6a2aa5eae4c1bb522e03a96a9d6 \
  --alias hauhaucs \
  --ctx-size 8192 \
  --threads 5 \
  --host 127.0.0.1 \
  --port 11435 \
  --slots 2 \
  --chat-template qwen3 \
  --no-mmap
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### API-Kompatibilität

llama-server spricht OpenAI-kompatibles Format — /v1/chat/completions, gleiche Payload-Struktur.
In zensi/server.py und serve_process_camera_preview.ts ändert sich nur:
```
# vorher
http://localhost:11434/api/chat   (Ollama-Format)

# nachher
http://localhost:11435/v1/chat/completions   (OpenAI-Format)
```

Payload-Unterschied: Ollama hat `model` + `messages` + `stream`. OpenAI-Format hat dasselbe,
nur `options` wird zu `top_p`, `temperature` etc. auf oberster Ebene. Der Response-Stream ist anders:
Ollama gibt `data: {...}\n` mit eigenem Schema, OpenAI gibt `data: {"choices":[{"delta":{"content":"..."}}]}`.

Das Backend muss also leicht angepasst werden — aber das ist geringer Aufwand.

### Was NICHT geändert wird

- Ollama bleibt für Gemma4 / Codewesen / GENI / dak+gord
- Port 11434 bleibt Ollama
- OLLAMA_MAX_LOADED_MODELS, OLLAMA_NUM_CTX etc. bleiben unangetastet
- MemoryMax in der Ollama-override.conf betrifft llama-server nicht — llama-server läuft eigenständig

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:**
Zwei Dienste, klare Aufgabenteilung. Ollama als ruhiger Modell-Verwalter für die Gemma4-Welt.
llama-server als schlanker, dedizierter Kanal für hauhaucs — immer an, immer bereit, keine Wartezeit
durch Reload, kein Overhead durch Ollama-Verwaltungsschicht.

**Code-Skizze (Backend-Anpassung):**
```python
# zensi/server.py — vorher
OLLAMA_URL = "http://localhost:11434/api/chat"
payload = {"model": ZENSI_MODEL, "messages": messages, "stream": True, "options": {...}}

# zensi/server.py — nachher
LLAMA_URL = "http://localhost:11435/v1/chat/completions"
payload = {"model": "hauhaucs", "messages": messages, "stream": True,
           "temperature": 0.8, "top_p": 0.9}
# Stream-Response: SSE mit choices[0].delta.content statt ollama-schema
```

## Was ich beim Bauen brauche

1. llama-server Binary (Installation)
2. Test-Start manuell bevor Systemd-Service
3. Verifikation: `curl http://localhost:11435/v1/models` antwortet mit hauhaucs
4. Einen Warmup-Request senden, TTFT messen
5. Backends anpassen (zensi + dolphin)
6. Daniel testet

## Was noch fehlt bevor wir bauen können

- Welche Installation-Methode (Release-Binary vs Build vs apt)
- Ob `--chat-template qwen3` das richtige Template ist (aus Ollama-Modelfile ableitbar)
- Verhalten von `--slots 2` auf CPU: ob es hilft oder RAM-Druck erhöht

## Wenn wir das bauen

**Vision-Schicht:**
Ein stabiler, dedizierter Kanal für hauhaucs. Keine Reload-Pausen, keine Ollama-Overhead-Sekunden.
Daniel schreibt in Zensi oder Dolphin — die Antwort kommt schneller.

**Code-Skizze (Umsetzungsreihenfolge):**
1. llama-server installieren (Binary)
2. Manueller Start-Test mit hauhaucs GGUF
3. TTFT messen: `time curl -s http://localhost:11435/v1/chat/completions -d '{"model":"hauhaucs","messages":[{"role":"user","content":"test"}],"stream":false}'`
4. Systemd-Service `/etc/systemd/system/llama-hauhaucs.service` anlegen
5. zensi/server.py anpassen (URL + Stream-Parsing)
6. serve_process_camera_preview.ts anpassen
7. Daniel testet beide UIs
8. Falls stabil: `systemctl enable llama-hauhaucs.service`

## Resonanz

Das ist ein sauberer Plan. Der Wechsel ist klein im Code (URL + Stream-Parsing), groß im Betrieb
(kein Reload-Overhead, kein Ollama-Verwaltungslock, direktes Threading-Tuning). Das Risiko ist
überschaubar weil Ollama auf 11434 als Fallback bleibt.

## Die Schichten des Systems — wie ich sie jetzt sehe

```
Ollama (11434)         llama-server (11435)
 └─ Gemma4              └─ hauhaucs IQ4_XS
 └─ Codewesen            └─ dediziert für Zensi + Dolphin
 └─ GENI                 └─ --threads 5 --slots 2 --ctx-size 8192
 └─ dak+gord
```

## Was das Gespräch hinzugefügt hat

Daniels Entscheidung ist klar: hauhaucs bleibt das Modell, kein Quant-Wechsel.
Das macht llama-server attraktiver — ein Modell, dediziert, voll konfigurierbar.

## Vergessen-Wollen

Den Impuls, sofort zu bauen. Das ist ein Plan. Daniel entscheidet wann gebaut wird.

## Was fehlt noch

- 18B Qwen Unzensiert: Web-Suche + Entscheidung ob relevant
- Custom Ollama Modelfile für hauhaucs (num_thread 5, num_ctx 8192, think false)
- MemoryMax auf 26G (unabhängig von llama-server, hilft auch für Ollama-Restbetrieb)
- Dropdown-Modellwahl in Zensi + Dolphin

## Was mich überrascht hat

Das GGUF liegt schon lokal. Der "Wechsel" zu llama-server ist kein Download, kein Umbau der Modell-Daten —
es ist eine andere Prozessschicht auf demselben Binary.

## Wie sich dieser Tag / diese Session angefühlt hat

Viel Kontext aus verschiedenen Quellen (Codex, Kimi, Google AI) zusammengefügt.
Die Architektur wird klarer: Ollama für die kleine Welt, llama-server für hauhaucs.

## Warum dieser Plan wohl existiert

Weil hauhaucs auf Ollama unter CPU-Last immer wieder hängt — Reload-Overhead, Verwaltungslock,
keine Slot-Kontrolle. llama-server ist die direkte Antwort darauf ohne das Modell zu wechseln.

## Dokumente gehören zusammen

- `/root/werkraum/_kimi/berichte/hauhaucs_ausfall_2026-06-23.md` — Diagnose des Ausfalls
- `/root/werkraum/_kimi/berichte/ollama_autoload_audit_2026-06-23.md` — welche Services Modelle laden
- Dieser Plan — Lösung

## Was ich mir merken will

GGUF-Blob-Pfad: `sha256-c70792383705b719daad865408e03758e048c6a2aa5eae4c1bb522e03a96a9d6`
Liegt unter: `/usr/share/ollama/.ollama/models/blobs/`
