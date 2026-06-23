---
datum: 2026-06-23
betrifft: [dolphin_mischpult, hauhaucs, ollama, qwen35b]
autor: kimi
---

# hauhaucs-Ausfall im Chat „ailien tomaten-wesen“

## Ausgangslage

- Chat: https://flextrawurst.de/dolphin → Session `2026-06-23T11-19-18`
- Session-Datei: `/root/werkraum/dolphin_mischpult/sessions/2026-06-23T11-19-18.jsonl`
- Verwendetes Modell: `fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS`
- Backend: `/root/flextrawurst/scripts/serve_process_camera_preview.ts` (Port 8787)
- Ollama: Port 11434, CPU-only, `MemoryMax=22G`

## Beobachtung

Die Session lief von 11:20 bis ca. 14:01. In diesem Zeitraum kamen Antworten von hauhaucs (z. B. als „Pomodori“), allerdings mit zunehmenden Verzögerungen und Abbrüchen. Ab 14:08 kamen auf wiederholte User-Fragen keine Antworten mehr.

## Technische Diagnose

### 1. Das Modell ist zu groß für CPU-only

- 35B-MoE-Modell, quantisiert auf IQ4_XS
- Im Ollama-Runner belegt es mit `num_ctx=8192` ca. **20,4 GB RAM**
- Kein GPU-Offloading: `offloaded 0/41 layers to GPU`
- Ollama läuft unter `MemoryMax=22G` / `MemoryHigh=20G`

Das System hat zwar 31 GB RAM, aber Ollama darf selbst nur 22 GB verwenden. Das Modell + KV-Cache + Compute-Graph füllen diesen Raum fast komplett aus.

### 2. Das Backend erzwingt 8192 Kontext

In `serve_process_camera_preview.ts`:

```ts
const INTERACTIVE_NUM_CTX = 8192;
const INTERACTIVE_CHAT_MODEL = "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS";
```

Jede Anfrage an Ollama enthält `num_ctx: 8192`. Mit wachsender Session wächst die tatsächlich genutzte Prompt-Länge — und damit die Verarbeitungszeit pro Antwort.

### 3. Ladezeiten und Instabilität

Log-Auszüge (`journalctl -u ollama`):

```
llama runner started in 43.31 seconds
llama runner started in 42.37 seconds
llama runner started in 55.56 seconds
```

Neustart von Ollama um 14:19:56:

```
ollama.service: Consumed 6h 29min 11.144s CPU time, 20.4G memory peak, 10.3G swap peak.
```

Das sind klassische Anzeichen eines Prozesses, der am harten Speicherlimit hängt.

### 4. Fehlerbild im Chat-Zeitraum

Ab 14:08 sind in den Ollama-Logs keine erfolgreichen `POST /api/chat` mehr zu sehen — nur noch `HEAD /` und `GET /api/ps` (Healthchecks). Die User-Anfragen gingen entweder nie bei Ollama an oder wurden vorher vom Client/Server abgebrochen.

### 5. Live-Test während der Diagnose

Ein manueller `/api/generate`-Test mit `num_ctx=2048` und `num_predict=5`:

```json
{
  "model": "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS",
  "response": "",
  "done_reason": "length",
  "total_duration": 91601708670,
  "load_duration": 87838169437,
  "prompt_eval_count": 18,
  "prompt_eval_duration": 2113428753,
  "eval_count": 5,
  "eval_duration": 647269298
}
```

- Gesamtdauer: **91,6 Sekunden**
- Modell-Ladezeit allein: **87,8 Sekunden**
- Antwort: leer (`done_reason: "length"`)

Einmal gelaufen, ist die Token-Generierung schnell (~0,65s für 5 Tokens). Das Problem ist das Laden und der volle 8192-Kontext.

## Warum es „so lange so gut“ ging

- Bei kurzem Kontext und frisch geladenem Modell konnte das 35B-Modell noch Antworten produzieren.
- Die Qualität war hoch, weil das Modell selbst leistungsfähig ist.
- Die Geschwindigkeit war aber schon von Anfang an gering: Mehrere Antworten brauchten Minuten.

Mit jeder weiteren Nachricht wuchs der Prompt, die Verarbeitungszeit stieg, und irgendwann brach die Stabilität zusammen.

## Handlungsoptionen

1. **Kontext reduzieren**
   - `INTERACTIVE_NUM_CTX` von 8192 auf 2048 oder 4096 senken.
   - Spart RAM und Ladezeit.

2. **Kleineres Modell verwenden**
   - `dolphin3-daniel` (8B) ist im System vorhanden und deutlich ressourcenschonender.

3. **Mehr Ressourcen bereitstellen**
   - GPU mit ausreichend VRAM
   - Oder mehr System-RAM und Anhebung von `MemoryMax`

4. **Session-Reset**
   - Den Kontext der Session leeren, damit hauhaucs wieder mit kurzem Prompt arbeiten kann.

## Fazit

hauhaucs ist nicht durch einen Codefehler oder Prompt-Defekt ausgefallen, sondern durch **Ressourcenüberlastung**: Ein 35B-MoE-Modell auf CPU mit fast vollem 8192-Kontext und einem 22-GB-Ollama-Limit ist für längere Chat-Sessions nicht stabil.

---
*Bericht erstellt von Kimi am 2026-06-23.*
