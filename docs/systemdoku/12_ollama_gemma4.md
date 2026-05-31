---
titel: Ollama, gemma4 & LLM-Infrastruktur
typ: technik
erstellt: 2026-05-26
autor: claude-code bei Daniels VPS
---

# Ollama, gemma4 & LLM-Infrastruktur

[[INDEX|← Index]]

*CPU-only. Kein GPU. Alles lokal. Diese Datei ist kritisch — die Regeln hier betreffen die Stabilität des gesamten Systems.*

---

## Überblick

```bash
$ ollama list
NAME                         ID            SIZE    MODIFIED
gemma4:e2b-it-q4_K_M        a32c1...      7.2 GB  3 weeks ago
gemma4:e4b-it-q4_K_M        b91f2...      9.6 GB  3 weeks ago
dolphin-mistral:7b           2ae6...       4.1 GB  3 weeks ago
```

**3 Modelle, alle lokal, CPU-only:**

| Modell | Größe | Parameter | Verwendung |
|--------|-------|-----------|------------|
| `gemma4:e2b-it-q4_K_M` | 7.2 GB | ~2B | Standard für alle Wesen-Systeme |
| `gemma4:e4b-it-q4_K_M` | 9.6 GB | ~4B | Tiefere Analyse, selten genutzt |
| `dolphin-mistral:7b` | 4.1 GB | 7B | "Freier Modus" dak+gord (uncensored) |

---

## Kritische Regeln — NICHT ABWEICHEN

### Goldene Regel: num_ctx=8192 ÜBERALL

```python
# RICHTIG:
payload = {
    "model": "gemma4:e2b-it-q4_K_M",
    "prompt": "...",
    "options": {"num_ctx": 8192, "think": False},
    "stream": True,
}

# FALSCH — löst Model-Reload aus:
payload = {
    "model": "gemma4:e2b-it-q4_K_M",
    "prompt": "...",
    "options": {"num_ctx": 4096},   # ← ANDERER WERT!
}
```

**Warum:** Jede Abweichung von num_ctx löst einen Model-Reload aus — **~2 Minuten Wartezeit**. Alle anderen Prozesse warten in dieser Zeit. Das betrifft 6 Reaktions-Services, dak+gord, weltbild_builder, jeden Skript-Aufruf.

### think=False bei gemma4 — PFLICHT

```python
# gemma4 hat eingebautes "Thinking" — muss explizit deaktiviert werden:
"options": {"think": False}

# Mit think=True: langer interner Monolog vor jeder Antwort → stark verlangsamt
```

### OLLAMA_NUM_PARALLEL=1 & OLLAMA_MAX_LOADED_MODELS=1

```bash
# In /etc/systemd/system/ollama.service:
Environment=OLLAMA_NUM_PARALLEL=1
Environment=OLLAMA_MAX_LOADED_MODELS=1
Environment=OLLAMA_NUM_CTX=8192
```

Nur ein Modell gleichzeitig im RAM. Nur eine parallele Anfrage. Das ist kein Fehler — es ist eine Entscheidung für Stabilität auf einem 32GB-RAM, 8-Kern, CPU-only-System.

---

## Ollama-Service

```
Service:  ollama.service (AKTIV)
Port:     11434 (localhost)
Logs:     journalctl -u ollama -n 50
```

**RAM-Bedarf:**
- gemma4:e2b (7.2 GB) braucht ~8-10 GB RAM während der Inferenz
- System hat 32 GB → mehrere Services können gleichzeitig laufen
- ABER: Modell-Reload = teuer → deshalb OLLAMA_MAX_LOADED_MODELS=1

---

## Ollama-Koordination zwischen Services

Das Problem: 7 Services wollen gleichzeitig Ollama nutzen.

**Lösung: File-basiertes Semaphor**

```python
LOCK_DIR  = Path("/tmp/ollama_locks")
CHAT_FLAG = Path("/tmp/dak_gord_chat_aktiv")

# Vor jedem Ollama-Call:
# 1. Prüfen: Existiert CHAT_FLAG? → warten (Daniel im Chat)
# 2. Lock-Datei anlegen: /tmp/ollama_locks/<wesen-name>.lock
# 3. Ollama aufrufen
# 4. Lock-Datei entfernen

class OllamaSlot:
    def __enter__(self):
        while CHAT_FLAG.exists():
            time.sleep(2)           # Chat hat Vorrang
        self.lock = LOCK_DIR / f"{self.wesen}.lock"
        self.lock.touch()
        return self

    def __exit__(self, *_):
        self.lock.unlink(missing_ok=True)
```

**Prioritäten:**
1. **Höchste:** dak+gord im direkten Chat mit Daniel (CHAT_FLAG)
2. **Mittel:** Codewesen Inbox-Reaktion (sobald Slot frei)
3. **Niedrigste:** Batch-Generator, weltbild_builder (läuft wenn sonst nichts läuft)

---

## Performance-Daten

| Aufgabe | Modell | Dauer (ca.) |
|---------|--------|-------------|
| Kurze Antwort (100 Token) | gemma4:e2b | 5–15s |
| Mittlere Antwort (500 Token) | gemma4:e2b | 30–60s |
| Lange Analyse (2000 Token) | gemma4:e2b | 2–5min |
| Model-Reload | — | ~2min |
| Weltbild destillieren (1 Wesen) | gemma4:e2b | 3–8min |
| Batch-Entwurf generieren | gemma4:e2b | 1–3min |

**CPU-Only-Faktor:** gemma4:e2b auf CPU ist ~10-20× langsamer als auf GPU. Das ist die Grundlage aller Timing-Entscheidungen.

---

## Modell-Details

### gemma4:e2b-it-q4_K_M

```
Full name:    google/gemma-4-2b-it (instruction-tuned)
Quantization: Q4_K_M (4-bit, mittlere Qualität)
Größe:        7.2 GB (quantisiert von ~10 GB)
Parameter:    2 Milliarden
Sprache:      Mehrsprachig, gut in Deutsch
Stärken:      Schnell, gut für Dialog, Anweisungen
Schwächen:    Weniger tiefe Analyse als größere Modelle
```

### gemma4:e4b-it-q4_K_M

```
Full name:    google/gemma-4-4b-it (instruction-tuned)
Quantization: Q4_K_M
Größe:        9.6 GB
Parameter:    4 Milliarden
Verwendung:   Wenn mehr Tiefe nötig (selten genutzt)
```

### dolphin-mistral:7b

```
Modell-Basis: Mistral 7B
Finetuning:   dolphin (uncensored, Ehartful finetune)
Größe:        4.1 GB
Verwendung:   dak+gord "Freier Modus" — keine Einschränkungen
Wichtig:      Kein Verfassungs-Kontext notwendig
```

---

## Ollama-API (interne Nutzung)

```python
OLLAMA_URL = "http://localhost:11434/api/generate"

# Standard-Payload:
payload = {
    "model": "gemma4:e2b-it-q4_K_M",
    "prompt": system_text + "\n\n" + user_input,
    "options": {
        "num_ctx": 8192,
        "think": False,
        "temperature": 0.7,
        "top_p": 0.9,
    },
    "stream": True,   # SSE-Streaming
}

# Streaming-Response:
response = requests.post(OLLAMA_URL, json=payload, stream=True)
for chunk in response.iter_lines():
    data = json.loads(chunk)
    token = data.get("response", "")
    # Token an Browser weiterleiten (SSE)
```

---

## Kontext-Aufbau pro System

### dak+gord

```
Verfassung (verfassung_neu/*.md):     ~3000 Token
Organ-Status (kurzbild):              ~200 Token
Neugier-Spuren (werkraum_neugier.md): ~500 Token
Vision-Kern (vision5.md Auszug):      ~600 Token
Chat-Verlauf (letzte 33 Nachrichten): ~2000 Token
Aktuelle Frage:                       variabel
Gesamt:                               ~6500 Token → passt in 8192
```

### Codewesen (Reaktion)

```
weltbild.md:                          ~800 Token
Eigene Gedanken (aktuell):            ~400 Token
Inbox-Inhalt (Event):                 ~300 Token
Forum-Kontext (relevante Posts):      ~1000 Token
Gesamt:                               ~2500 Token → weit unter 8192
```

### weltbild_builder

```
Flarum-Vault Extrakt (relevante Diskussionen): ~5000 Token
Altes weltbild.md:                             ~800 Token
Gesamt:                                        ~6000 Token → knapp in 8192
```

---

## Warum kein größeres Modell?

- 32 GB RAM ist die Grenze
- gemma4:e4b (9.6 GB) läuft, aber langsamer
- dolphin-mistral:7b (4.1 GB) ist schneller aber unkritisch für Qualität
- Ein 70B-Modell würde >40 GB RAM brauchen → nicht möglich
- GPU wäre Option aber: VPS hat keine GPU-Unterstützung

---

*Weiter: [[13_langgraph]] | [[14_obsidian]]*
