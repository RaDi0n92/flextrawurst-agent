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
  --ctx-size 12345 \
  --threads 10 \
  --host 127.0.0.1 --port 11435 \
  --parallel 2 \
  --flash-attn on \
  --mlock \
  --cpu-range 0-9 --cpu-range-batch 0-9 --cpu-strict 1

[Service]
AllowedCPUs=0-9
```

### Kritische Werte — Begründung, NICHT ohne Rücksprache ändern

**`--mlock`**: Verhindert, dass die Modellgewichte unter Speicherdruck aus
dem Page-Cache verdrängt werden. Ohne mlock brach die Geschwindigkeit unter
Hintergrundlast von 14 tok/s auf 3-5 tok/s ein (gemessen 2026-07-06) —
mit mlock blieb sie stabil bei 6-7 tok/s über eine ganze Generierung.

**`AllowedCPUs=0-9`** (Cgroup, nicht `--cpu-range` allein — das griff nicht
zuverlässig): Isoliert 10 von 16 Kernen für llama-server, Rest bleibt für
Ollama/Wesen-Prozesse/System. Trade-off bewusst gewählt: garantierte,
niedrigere Geschwindigkeit (~4 tok/s stabil) statt schwankender höherer
Spitzenwerte ohne Isolierung.

**`--ctx-size 12345 --parallel 2`**: ⚠️ **Wichtige Einschränkung** — llama-server
teilt die Kontextgröße durch die Parallel-Slots: jeder der 2 Slots bekommt nur
~6400 Token, nicht die vollen 12345. Ein Gesprächsverlauf über ~6400 Token
schlägt fehl (`exceed_context_size_error`). **Stand 2026-07-06 noch nicht
gelöst** — Entscheidung zwischen höherem `--ctx-size` (mehr RAM) oder
`--parallel 1` (volle Kontextgröße, keine Gleichzeitigkeit) steht noch aus.

**`--threads 10`**: CPU-Inferenz ist speicherbandbreitengebunden, nicht
kernzahlgebunden — mehr Threads als sinnvoll nutzbar bringt nichts, verschärft
nur Konkurrenz mit anderen Prozessen.

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
