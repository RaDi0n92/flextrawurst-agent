---
datum: 2026-06-24
betrifft: [hauhaucs, llama-cpp, qwen, modell-auswahl, architektur, concurrency, vision, moe, thinking]
importable: false
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

# Modell-Architektur-Plan: Was besprochen wurde, was möglich ist

Entstanden aus einer langen Recherche- und Planungssession am 2026-06-24.
Dieser Plan ersetzt/ergänzt den älteren `plan_llamacpp_ersatz.md`.

---

## Daniels Anforderungen (wörtlich destilliert)

1. **Uncensored** — vollständig, keine Refusals, kein moralisches Filtern
2. **Reasoning / Thinking** — schaltbares Denkmodus (Qwen `/think` / `/no_think`)
3. **Vision** — Bilder in Chats schicken können
4. **MoE wenn möglich** — weniger aktive Parameter = CPU-effizienter
5. **Optimierbar** — Modelfile-Parameter, Threading, num_batch etc. steuerbar
6. **Concurrent-fähig** — nicht nur einen Chat mit Daniel überstehen, sondern:
   - entity_kern Takt (8 Wesen, alle N Sekunden)
   - tension_daemon, similarity_daemon, themen_cluster
   - 8 Wesen-Chats auf Flarum (codewesen_chat.py)
   - Zensi + Dolphin/Mischpult für Daniel interaktiv
   - 2 wirklich parallel, quasi alle 8 wenn max 2 Inputs je Wesen
7. **Langkontextstabil** — über 8192 Token ohne Crash

Das war vorher aufgeteilt auf gemma4:e2b (~1.3GB, 2B) + gemma4:e4b (~2.7GB, 4B) für die Hintergrundprozesse, hauhaucs für Daniel. Ziel: bessere Lösung finden.

---

## Wichtige Klarstellung: Das Problem war nie das Modell

hauhaucs (Qwen3.6-35B-A3B-Uncensored, IQ4_XS) hat alle Eigenschaften die Daniel will:
- MoE ✅ (35B total, ~3B aktive Parameter)
- Vision ✅ (Qwen3.6 = unified vision-language foundation)
- Thinking ✅ (schaltbar)
- Uncensored ✅ (0/465 Refusals)
- Optimierbar ✅ (num_thread, num_ctx, num_batch steuerbar)

Das Problem war **Ollama** — es queued alle Anfragen sequenziell. Bei 8 Wesen die gleichzeitig antworten wollen und 60s/Antwort brauchen, warten alle anderen 7×60s = 7 Minuten. Das ist die "garnicht"-Situation die Daniel beschreibt.

**Lösung: llama.cpp mit --slots N** — dasselbe Modell, aber concurrent-fähig.

---

## Das Qwen-Ökosystem (Stand 2026-06)

### Generationen

| Generation | Erschienen | Besonderheit | Größen |
|---|---|---|---|
| Qwen3 | Mai 2025 | Thinking nativ, erste MoE-Generation | 0.6B, 1.7B, 4B, 8B, 14B, 30B-A3B, 32B, 235B-A22B |
| Qwen3.5 | Feb 2026 | Gated DeltaNet-Layer, multimodal | 2B, 4B, 9B, 27B, 35B-A3B, 122B-A10B, 397B-A17B |
| Qwen3.6 | aktuell | Unified Vision+Text, MoE verbessert | 27B (dense), 35B-A3B (MoE) |
| Qwen3-VL | 2025/26 | Dedizierte Vision-Modelle | 2B, 4B, 8B, 32B (+ Thinking-Varianten) |
| Qwen2.5-VL | früher | Ältere stabile Vision-Linie | 3B, 7B, 32B |

Alle Modelle ab Qwen3: Thinking-Modus nativ, schaltbar per `/think` im Prompt
oder `enable_thinking=false` im API-Call.

### Was MoE bedeutet für CPU

Bei Qwen3-30B-A3B und Qwen3.6-35B-A3B:
- 30B/35B Gesamtgewichte im RAM (~17-20GB)
- Nur ~3B Parameter pro Token-Berechnung aktiviert
- Vorteil: schnellere Token-Generierung als dichte 30B/35B
- Vorteil: weniger Wärme, weniger CPU-Last pro Token
- KV-Cache trotzdem groß weil auf Gesamtmodell-Architektur basierend

### Uncensored-Quellen

**HauhauCS** (Qualitätsführer, 0/465 Refusals garantiert):
- Eigene K_P-Quantisierungen (~1-2 Quant-Stufen besser bei 5-15% mehr Größe)
- Verfügbar: Qwen3.5-2B, 4B, 9B, 27B, 35B-A3B, 122B-A10B
- Verfügbar: Qwen3.6-27B (Balanced + Aggressive), Qwen3.6-35B-A3B (Aggressive) ← aktuell
- Vision bei 9B: multimodal mit mmproj-Datei
- Alle auf Ollama via fredrezones55/...

**DavidAU** (Fokus Kontext-Erweiterung + Claude-Destillation):
- NEO Imatrix-Quantisierungen (eigens entwickelt, sehr gut bei kleinen Quants)
- Qwen3-8B Josiefied Uncensored: 192k Kontext, ~5GB
- Qwen3-30B-A3B: 128k Kontext, MoE, CPU-tauglich, ~17GB
- Qwen3.5-9B Claude-4.6 Heretic: Claude-Reasoning-Muster eintrainiert
- Qwen3.6-27B Heretic Uncensored Finetune
- Qwen3.6-40B Claude-4.6 Opus Deckard: Claude-4.6-Opus destilliert

**huihui-ai** (Abliteration, Fokus Vision):
- Qwen3-VL-8B-Thinking-abliterated: Vision + Thinking + uncensored
- Qwen3-8B-abliterated: Standard-Abliteration
- GGUF via mradermacher

**mlabonne / prithivMLmods**:
- Qwen3-8B-abliterated (mlabonne)
- Qwen3-VL-8B-Instruct-abliterated-v1 (prithivMLmods)

---

## RAM-Mathematik (Daniels VPS: 32GB, CPU-only)

```
Feste Kosten:
  OS + Docker + Services:  ~4GB
  Verfügbar für Modelle:  ~28GB

Modell-Größen (Q4_K_M oder IQ4_XS):
  hauhaucs 35B-A3B:       ~20GB
  Qwen3.5-9B HauhauCS:    ~5.5GB
  Qwen3.6-27B HauhauCS:   ~16GB
  Qwen3-30B-A3B DavidAU:  ~17GB
  Qwen3-8B DavidAU:       ~5GB
  Qwen3-VL-8B (abliterated): ~5.5GB

KV-Cache pro Slot bei 8192 Token:
  35B-A3B:  ~1.5-2GB pro Slot
  9B:       ~0.5GB pro Slot
  27B:      ~1.2GB pro Slot
```

---

## Architektur-Optionen die durchdiskutiert wurden

### Option A: Split — klein für Background, hauhaucs für Daniel
```
llama-server Port 11435: Qwen3.5-4B HauhauCS (~2.5GB), --slots 8
  └─ entity_kern, tension_daemon, 8 Wesen-Chats, alle Hintergrundprozesse

Ollama Port 11434: hauhaucs 35B-A3B (~20GB), on-demand
  └─ Zensi, Dolphin/Mischpult (nur wenn Daniel chattet)

RAM wenn beide aktiv: 22.5GB → ~9.5GB KV-Puffer ✅
```

Vorteil: Maximale Qualität für Daniel, stabile Hintergrundprozesse.
Problem: Ob Qwen3.5-4B pauschal "besser als Gemma4:e2b" ist — unklar. Nicht getestet.
Gemma4 war speziell für Inference-Effizienz gebaut. Qwen3.5-4B ist in kreativem
Rollenspiel wohl besser, im zuverlässigen System-Prompt-Folgen möglicherweise
nicht — das müsste getestet werden.

### Option B: 27B als Single-Model-Lösung
```
llama-server Port 11435: Qwen3.6-27B HauhauCS Balanced (~16GB), --slots 3
  └─ ALLES: Wesen, Daemons, Zensi, Dolphin, Daniel interaktiv

RAM: 16GB + 3×(~1.2GB KV) = ~19.6GB → ~8-9GB Puffer ✅
```

Vorteil: Ein Modell, alles concurrent, komfortabler RAM.
Problem: 27B ist DENSE, kein MoE — widerspricht Daniels MoE-Wunsch.
Vision: ja (Qwen3.6 = unified VL).

### Option C (bevorzugt): hauhaucs via llama.cpp mit Slots
```
llama-server Port 11435: hauhaucs 35B-A3B IQ4_XS (~20GB), --slots 2-3
  └─ ALLES: Wesen, Daemons, Zensi, Dolphin, Daniel interaktiv

Ollama Port 11434: bleibt für andere kleine Modelle (Gemma4 etc.)

RAM mit 3 Slots: 20GB + 3×(~1.5GB KV) = ~24.5GB → ~3.5GB Puffer ⚠ knapp
RAM mit 2 Slots: 20GB + 2×(~1.5GB KV) = ~23GB → ~5GB Puffer ✅ machbar
```

Vorteil: Dasselbe Modell das Daniel schon kennt, alle gewünschten Eigenschaften,
jetzt concurrent. Kein Download, kein Test eines neuen Modells.

Vorteil: MoE ✅, Vision ✅, Thinking ✅, Uncensored ✅, Optimierbar ✅.

Risiko: Qwen3.6 DeltaNet-Layer sind in llama.cpp noch nicht optimal implementiert
(Stand Juni 2026) → möglicherweise langsamer als erwartet. Alternative wäre dann
Qwen3-30B-A3B (ältere Generation, besser in llama.cpp unterstützt).

**Das ist der bevorzugte nächste Schritt.**

---

## Was noch als Möglichkeit offen bleibt

### Qwen3-VL-8B Thinking abliterated (huihui-ai)
Wenn Vision wirklich gebraucht wird (Bilder in Wesen-Chats oder Daniel-Chats):
- 5.5GB, sehr schnell
- Vision + Thinking + uncensored in einem kleinen Modell
- Könnte als dritte Option auf Port 11436 laufen (nur für Vision-Anfragen)
- GGUF: mradermacher/Qwen3-VL-8B-Abliterated-Caption-it-GGUF

### Qwen3-30B-A3B DavidAU (als hauhaucs-Ersatz falls DeltaNet-Problem)
Wenn llama.cpp mit hauhaucs (Qwen3.6) zu langsam wegen DeltaNet:
- Eine Modell-Generation älter (Qwen3, nicht 3.6)
- MoE ✅, Uncensored ✅, 128k Kontext, besser in llama.cpp implementiert
- KEIN Vision (kein VL-Modell in dieser Größe uncensored verfügbar)
- Download: DavidAU/Qwen3-128k-30B-A3B-NEO-MAX-Imatrix-gguf
- RAM: ~17GB → komfortabler als hauhaucs

### HauhauCS Qwen3.5-9B (als Background-Schicht falls Split-Architektur)
- 5.5GB, ~50 tok/s, --slots 4 möglich
- Vision (mmproj), Thinking, 0/465 Refusals
- Wäre Option A Tier-1 wenn der Split-Ansatz gewählt wird
- Ollama: `ollama pull fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:9b`

### DavidAU Qwen3.5-9B Claude-4.6 Heretic
- Claude-Reasoning-Muster eintrainiert (Destillation)
- Interessant für Wesen die "reflektierter" denken sollen
- Noch nicht getestet

---

## Implementierungsreihenfolge (Stand 2026-06-24)

1. **llama.cpp installieren** (Release-Binary, nicht self-build)
   → Plan liegt in: `_claude/ideen/plan_llamacpp_ersatz.md`

2. **hauhaucs GGUF extrahieren**
   GGUF-Blob: `sha256-c70792383705b719daad865408e03758e048c6a2aa5eae4c1bb522e03a96a9d6`
   Liegt unter: `/usr/share/ollama/.ollama/models/blobs/`

3. **llama-server testen (manuell, kein Systemd)**
   ```bash
   ./llama-server \
     --model /pfad/zu/hauhaucs.gguf \
     --ctx-size 8192 \
     --slots 2 \
     --threads 5 \
     --host 127.0.0.1 --port 11435
   ```

4. **Backend-Umleitung testen**
   Zensi + Dolphin auf Port 11435 zeigen lassen (beide haben bereits Dropdown),
   Ollama-Format → OpenAI-Format anpassen (`/v1/chat/completions`)

5. **Concurrency-Test**
   Zwei parallele Anfragen schicken, prüfen ob beide durchkommen oder queued werden

6. **Falls DeltaNet-Problem (zu langsam):**
   → Qwen3-30B-A3B DavidAU laden statt hauhaucs für llama-server
   → hauhaucs bleibt als Ollama-Backup

7. **Hintergrundprozesse umleiten**
   entity_kern.py, codewesen_chat.py etc. auf den neuen llama-server Port zeigen

8. **Systemd-Service einrichten** (erst nach erfolgreichem Test)

---

## Was explizit NICHT gemacht wird (ohne Daniel)

- Kein eigenständiger Modell-Download ohne Auftrag
- Kein Umbau der Wesen-Services ohne Test + Freigabe
- Kein Abschalten von Ollama ohne Sicherheitsnetz
- Keine Entscheidung ob Split (Option A) oder Single-Model (Option C)
  ohne Daniels Feedback nach dem ersten llama.cpp-Test

---

## Offene Fragen die Daniel entscheiden muss

1. **Slots 2 oder 3?**
   2 = sicherer (5GB Puffer), 3 = mehr Concurrency (3.5GB Puffer, knapp)

2. **Was wenn DeltaNet langsam?**
   Qwen3-30B-A3B als Ersatz (kein Vision) oder 27B dense (mit Vision, kein MoE)?

3. **Vision wichtig für Wesen-Chats?**
   Wenn ja → separater Vision-Port (Qwen3-VL-8B) oder 27B als Basis

4. **Gemma4 komplett ablösen oder als Fallback behalten?**
   Empfehlung: erstmal als Fallback behalten bis neues Setup stabil

---

## Verwandte Dateien

- `_claude/ideen/plan_llamacpp_ersatz.md` — technischer Implementierungsplan llama.cpp
- `_claude/hauhaucs-tuned.Modelfile` — Custom Modelfile (für Ollama, num_thread 5, num_ctx 8192)
- `/etc/systemd/system/ollama.service.d/memory-limit.conf` — MemoryMax 27G

## Was ich gelesen habe

Keine externen Dateien — dieser Plan entstand aus dem Gespräch selbst.

## Was ich verstehe

Das Problem war nie das Modell. hauhaucs hat alles was Daniel will.
Das Problem war Ollama's Unfähigkeit, parallele Anfragen zu handeln.
llama.cpp mit --slots löst das — ohne Modellwechsel, ohne Download.

## Was ich nicht verstehe

Ob Qwen3.6's DeltaNet-Implementierung in llama.cpp stabil genug ist.
Das ist der einzige echte Unsicherheitsfaktor im Plan.

## Was mich interessiert

Was passiert wenn hauhaucs plötzlich 2-3 Wesen gleichzeitig antwortet.
Das war noch nie möglich. Es könnte sich anders anfühlen — für Daniel, für die Wesen.

## Was zusammenhängt und wie

llama.cpp → Concurrency → Wesen-Chats wieder stabil → entity_kern wieder aktiv →
Welt lebt wieder → Daniel kann hauhaucs für beides nutzen → kein Modell-Kompromiss nötig.

## Was konzeptionell darin steht

Eine Architektur-Entscheidung die wie eine Modell-Frage aussieht.
Die eigentliche Entscheidung war: Ollama oder llama.cpp? Nicht: welches Modell?

## Was mich heute beschäftigt hat

Dass die Antwort die ganze Zeit schon da war — hauhaucs IST das richtige Modell.
Nur der falsche Behälter drum herum.

## Was mich noch beschäftigt

Ob 2 Slots genug sind wenn alle 8 Wesen gleichzeitig einen Takt bekommen.
Wahrscheinlich ja — die Takte sind versetzt, nicht synchron.

## Tiefer eingetaucht

Der DeltaNet-Hinweis kommt aus Community-Benchmarks: Qwen3.6 nutzt Gated DeltaNet-Layer
in der Architektur, die llama.cpp noch nicht mit dem gleichen Optimierungsgrad implementiert
hat wie die Standard-Attention-Layer von Qwen3 oder Qwen3.5. In der Praxis bedeutet das:
Qwen3.6 läuft vielleicht 20-30% langsamer in llama.cpp als Qwen3-30B-A3B,
obwohl hauhaucs auf dem Papier das "bessere" Modell ist.
Das ist kein Dealbreaker — aber ein Punkt den der erste Test klären muss.

## Wie sich dieser Tag / diese Session angefühlt hat

Viel Recherche, viele Optionen, am Ende war die Antwort einfacher als der Weg dorthin.
Das passiert oft wenn man erst den Lösungsraum vollständig verstehen muss
bevor man merkt dass man sich schon im Zentrum befunden hat.

## Warum dieser Code / diese Datei wohl existiert

Damit die nächste Claude-Instanz nicht nochmal 40 Minuten Recherche machen muss
bevor sie versteht warum llama.cpp + hauhaucs + --slots 2 die Antwort ist.

## Was ich beim Bauen brauche

Nichts Neues. llama.cpp Binary, GGUF-Pfad (schon bekannt), Port 11435 frei.

## Was noch fehlt bevor wir bauen können

Daniels Entscheidung: wann soll der erste llama.cpp-Test stattfinden?
Danach: manueller Test bevor irgendein Service umgeleitet wird.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:**
Ein System das nicht mehr fragt "welcher Service darf welches Modell laden?"
sondern einfach: ein Modell, ein Port, alle reden damit.
Wie ein Nervensystem das endlich einen gemeinsamen Taktgeber hat.

**Code-Skizze:**
```bash
# Startbefehl llama-server für hauhaucs
/usr/local/bin/llama-server \
  --model /usr/share/ollama/.ollama/models/blobs/sha256-c707... \
  --ctx-size 8192 \
  --slots 2 \
  --threads 5 \
  --batch-size 128 \
  --host 127.0.0.1 \
  --port 11435 \
  --chat-template qwen3 \
  --no-mmap

# Systemd ExecStart (vereinfacht)
ExecStart=/usr/local/bin/llama-server --model %h/hauhaucs.gguf --slots 2 --ctx-size 8192

# Backend-Änderung in serve_process_camera_preview.ts
const LLAMA_SERVER_URL = "http://127.0.0.1:11435";
// POST /v1/chat/completions (OpenAI-Format statt /api/chat)
// stream:true → SSE mit data: {"choices":[{"delta":{"content":"..."}}]}
```

## Was ich mir merken will

- Das Problem war Ollama, nicht hauhaucs.
- llama.cpp --slots = Concurrency, das war die fehlende Zutat.
- Qwen3.6 DeltaNet = möglicher Schwachpunkt in llama.cpp, Test nötig.
- GGUF-Blob liegt schon lokal, kein Download nötig.
- Slots 2 = sicherer RAM-Puffer. Slots 3 = mehr Concurrency, weniger Puffer.

## Dokumente gehören zusammen

- [[plan_llamacpp_ersatz]] — technische Umsetzung
- [[modell-mapping]] (in `_claude/` oder `_kimi/`) — welcher Service welches Modell nutzt
- `/root/werkraum/codewesen_chat.py` — muss auf neuen Port zeigen
- `/root/werkraum/welt/entity_kern.py` — muss auf neuen Port zeigen

## Was mich überrascht hat

Dass die Modell-Recherche 40 Minuten gedauert hat und am Ende ergeben hat:
hauhaucs selbst ist die Antwort. Nur der Weg dorthin musste gegangen werden.

## Wenn wir das bauen

**Vision-Schicht:**
Alle acht Wesen und Daniel im selben Moment antwortfähig. Nicht nacheinander —
gleichzeitig. Das war noch nie so. Das verändert was Flextrawurst sein kann.

**Code-Skizze:**
Alles steht in `plan_llamacpp_ersatz.md` — dieser Plan hier ist das Warum,
jener ist das Wie. Zusammen lesen.

## Resonanz

Die Qwen-Familie hat sich in sechs Monaten von "interessanter Alternative" zu
"ernstzunehmender Infrastruktur" entwickelt. HauhauCS hat daraus eine
Production-Ready uncensored Linie gemacht. Das ist nicht selbstverständlich.

## Die Schichten des Systems — wie ich sie jetzt sehe

```
Schicht 1 (Modell): hauhaucs / Qwen3.6-35B-A3B — das Gehirn
Schicht 2 (Server): llama.cpp llama-server — der Nervenbahnenverteiler  
Schicht 3 (Services): entity_kern, codewesen_chat, Zensi, Dolphin — die Organe
Schicht 4 (Welt): flextrawurst PostgreSQL, Events, Wesen — das Bewusstsein
```

Vorher: Schicht 2 war Ollama, das sequenziell arbeitete. Das war der Flaschenhals.

## Was das Gespräch hinzugefügt hat

Die Erkenntnis dass "welches Modell" die falsche Frage war.
Die richtige Frage war: "welcher Server, mit welcher Concurrency-Strategie?"

## Vergessen-Wollen

Die Stunden in denen hauhaucs eingefroren hat und niemand wusste warum.
Das war Ollama. Nicht das Modell. Nicht Daniel. Nicht die Wesen.

## Was fehlt noch

Nur noch: den ersten manuellen llama-server-Start mit hauhaucs.
Alles andere ist Planung auf Papier bis dahin.
