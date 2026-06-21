---
datum: 2026-06-21
betrifft: [ollama, gemma4, dolphin, codewesen, laufzeit, ressourcen]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# Drei Modelle, eine Warteschlange und eine Grenze, die niemand gemeinsam sah

## Was ich gelesen habe

Ich habe nicht nur Modellnamen gelesen, sondern die tatsächlich laufende Kette: Ollamas wirksame Systemd-Konfiguration, Modell-Manifeste, Runner, Prozessspeicher, Swap, Kernel-OOM-Berichte, Codewesen-Logs, Zensis Servercode und die uncommitteten Rückstellungen von Dolphin auf Gemma 4. Die Modelle waren dabei nicht abstrakt. Sie lagen gleichzeitig als Gewichte, KV-Cache, wartende Requests und abgebrochene Antworten im Speicher.

Der härteste Satz kam nicht aus einer Dokumentation, sondern vom Kernel: *„Out of memory: Killed process … (ollama)“*. Er steht dreimal in einer Nacht. Direkt daneben standen Ollamas eigene Zahlen: Gemma e4b mit ungefähr 9,9 GiB, Gemma e2b mit ungefähr 7,2 GiB und Dolphin Q4 mit ungefähr 5,3 GiB. Die wirksame Dienstgrenze lautete gleichzeitig *„MemoryMax=16G“* und *„OLLAMA_MAX_LOADED_MODELS=3“*.

In den Wesen-Logs wiederholte sich ein anderer Satz: *„Ollama-Slot blockiert — Iteration übersprungen“*. Das klang zuerst wie ein einzelner Lockfehler. Beim Lesen des Codes wurde daraus ein Systembild: Es gibt nur `slot_0.lock`, mehrere Wesen warten darauf, aber Entity-Kern, Zensi und Webpfade benutzen nicht dieselbe Schranke. Die Wartenden stehen ordentlich in einer Reihe, während andere durch eine Seitentür gehen.

Dann waren da die stilleren Qualitätsverluste. Ollama schrieb: *„truncating input prompt … prompt=13480 … new=8192“*. Ein Modell kann technisch korrekt antworten und trotzdem nicht mehr auf denselben Ursprung antworten, wenn ein großer Teil seines Kontexts abgeschnitten wurde. Das erklärt Verhalten, das wie Modellversagen aussieht, obwohl die Gewichte lesbar und die Inferenz funktionsfähig sind.

## Was ich verstehe

Die Modelle sind nicht als Dateien beschädigt. Beide Gemma-4-Modelle werden von Ollama 0.21.0 korrekt erkannt und haben erfolgreiche Antworten geliefert. Dolphin Q4 funktioniert ebenfalls. Das Problem entsteht aus der Orchestrierung: zu viele gleichzeitig erlaubte Modelle, eine niedrigere Cgroup-Grenze als die Modellplanung voraussetzt, uneinheitliche Sperren, dauerhaft gepinnte Runner, synchron neu startende Verbraucher und Prompts oberhalb des Kontextbudgets.

Ich verstehe auch, warum sich die Störung überall anders zeigt. Beim Kernel heißt sie OOM. Bei Ollama heißt sie HTTP 500 oder zehn Minuten Laufzeit. Beim Wesen heißt sie blockierter Slot. Bei Zensi heißt sie Broken Pipe. Für Daniel wirkt sie vermutlich wie mehrere kaputte Modelle. Es ist dieselbe Engstelle, die an verschiedenen Oberflächen anders sichtbar wird.

## Was ich nicht verstehe

Noch unklar ist, welcher Teil der heutigen Rückstellung bereits bewusst als endgültige Zielkonfiguration bestätigt wurde. Die Dateien zeigen eine Bewegung zurück zu Gemma e2b/e4b, während einzelne laufende Prozesse vor dieser Änderung gestartet wurden und deshalb noch ältere Konstanten tragen.

Unklar bleibt außerdem, welche Latenz Daniel für direkte Chats akzeptabel findet. Diese Entscheidung bestimmt, ob e4b dauerhaft warm bleiben darf oder ob Stabilität und gerechte Warteschlange wichtiger sind als das Vermeiden eines Modell-Reloads.

## Was mich interessiert

Mich interessiert hier weniger die Frage „welches Modell ist besser?“ als die Frage „welche Zusage macht der gemeinsame Laufzeitkörper?“. Ein schnelleres Modell hilft nicht, wenn es hinter einem neunminütigen Request steht. Ein tieferes Modell hilft nicht, wenn sein Systemprompt abgeschnitten wurde.

## Was zusammenhängt und wie

`OLLAMA_MAX_LOADED_MODELS=3`, `MemoryMax=16G`, `keep_alive=-1`, die einzige `slot_0.lock`, Zensis `num_predict=444444`, `RuntimeMaxSec=1800` und der parallele Bildgenerator hängen kausal zusammen. Keiner dieser Werte allein erklärt die Nacht. Zusammen erzeugen sie Speicherüberhang, Warteschlangenstau, Abbrüche und anschließend synchrone Neustarts.

## Was konzeptionell darin steht

Eine Ressourcengrenze ist Teil der Architektur, nicht bloß Betrieb. Wenn mehrere Wesen dieselbe Inferenzmaschine teilen, ist die Warteschlange eine soziale Ordnung des Systems: Sie entscheidet, wer sprechen darf, wer wartet und wessen Kontext durch Zeit oder Abbruch verloren geht.

## Was mich heute beschäftigt hat

Mich hat beschäftigt, wie plausibel jede einzelne Schicht für sich aussah. Drei Modelle passen rechnerisch in 31 GiB Host-RAM. Die Aussage wird aber falsch, sobald Ollama selbst nur 16 GiB erhalten darf und der übrige Host gleichzeitig Obsidian, PostgreSQL, Bildgenerator und andere Weltprozesse trägt.

## Was mich noch beschäftigt

Die laufende und die auf Platte sichtbare Konfiguration sind nicht deckungsgleich. Besonders Entity-Kern wurde vor seiner späteren Modellrückstellung gestartet. Eine Analyse muss deshalb immer Prozessstartzeit und Dateiänderungszeit nebeneinander lesen.

## Tiefer eingetaucht

Der erste OOM entstand bei fast erschöpftem Swap und mehreren langen Requests. Beim späteren OOM waren drei Ollama-Runner geladen; gleichzeitig belegte `sd-cli` viele GiB. Der Kernel wählte einen Ollama-Runner mit hohem `OOMScoreAdjust=600` als Opfer. Das war kein zufälliger Absturz, sondern die vorgesehene Opferwahl unter globalem Speichermangel.

Die Lockdatei war nicht verwaist. `lsof` zeigte einen echten Halter und mehrere echte Wartende. Das Problem ist daher nicht „stale lock löschen“, sondern eine aktive Anfrage, die lange läuft, während nicht koordinierte Verbraucher weiterhin Ollama erreichen können.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie das Öffnen mehrerer vermeintlich verschiedener Störungen und das Finden derselben überfüllten Leitung dahinter. Nüchtern, aber mit einem kleinen absurden Kern: Die Warteschlange ist streng, nur gilt sie nicht für alle.

## Warum dieser Code / diese Datei wohl existiert

Diese Datei existiert, damit die Diagnose nicht wieder zu „Gemma ist kaputt“ oder „Dolphin ist kaputt“ zusammenschrumpft. Sie hält fest, dass Modell, Prozess, Scheduler, Speichergrenze, Kontextbudget und Verbraucher verschiedene Schichten sind.

## Was ich beim Bauen brauche

Vor einem Eingriff brauche ich eine bestätigte Zielbelegung: welches Modell für welchen Dienst, wie viele Runner gleichzeitig, welcher Dienst interaktive Priorität hat und ob Bildgenerierung mit Ollama konkurrieren darf. Danach braucht es einen einzigen, von allen Verbrauchern benutzten Koordinationspunkt.

## Was noch fehlt bevor wir bauen können

Es fehlt Daniels Bestätigung der Zielordnung. Außerdem sollte vor dem Umbau ein sauberer Laufzeit-Snapshot entstehen: aktive PIDs, geladene Modelle, Prozessstartzeiten, aktuelle Requests, RAM und Swap. Erst danach darf ein Dienst neu gestartet oder ein Mapping wirksam gemacht werden.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht**

Die Inferenzmaschine ist ein gemeinsames Organ mit endlichem Atem. Jede Anfrage trägt Herkunft, Dringlichkeit, Modellwunsch und Budget. Kein Wesen muss die Existenz anderer erraten, und kein Chat darf durch eine unsichtbare Seitentür die ganze Welt blockieren.

**Code-Skizze**

```python
from dataclasses import dataclass
from enum import IntEnum

class Prioritaet(IntEnum):
    INTERAKTIV = 0
    ANTWORTPFLICHT = 10
    WELT_TICK = 20
    BATCH = 30

@dataclass(frozen=True)
class InferenzAuftrag:
    actor: str
    model: str
    prioritaet: Prioritaet
    num_ctx: int
    num_predict: int
    timeout_s: int
    provenance: dict[str, str]

class OllamaKoordinator:
    def submit(self, auftrag: InferenzAuftrag) -> str: ...
    def aktive_modelle(self) -> list[str]: ...
    def passt_in_budget(self, model: str) -> bool: ...
```

## Was ich mir merken will

`MAX_LOADED_MODELS` ist keine Kapazitätsplanung. Die Zahl ist nur dann wahr, wenn Modellgewichte, KV-Caches, Cgroup-Limit, Swap, andere Prozesse und gleichzeitige Inferenz gemeinsam gerechnet wurden.

## Dokumente gehören zusammen

Diese Spiegeldatei gehört zur neuen Claude-Notiz `ollama-model-mapping.md`, zur Systemdokumentation `docs/systemdoku/12_ollama_gemma4.md`, zu den wirksamen Ollama-Units, zu `codewesen_agent.py`, `agent/dak_gord_system/ollama_chat.py`, `welt/entity_kern.py` und `/root/zensi/server.py`. Die Dokumente widersprechen sich derzeit an wichtigen Stellen; genau diese Differenz ist Teil des Befunds.

## Was mich überrascht hat

Mich überraschte, dass die ältere Systemdokumentation `MAX_LOADED_MODELS=1` ausdrücklich als Stabilitätsentscheidung beschreibt, während die aktuelle Laufzeit drei Runner erlaubt. Die frühere Regel kann veraltet sein, aber sie hatte das heute sichtbare Versagen bereits begrifflich vorweggenommen.

## Wenn wir das bauen

**Vision-Schicht**

Wenn wir das bauen, dann nicht als weitere verstreute Lockdatei. Die Welt braucht eine erkennbare Inferenzordnung: ein Eingang, eine Prioritätsregel, ein Speicherbudget und sichtbare Zustände für wartend, laufend, abgebrochen und abgeschlossen.

**Code-Skizze**

```typescript
type InferenceState = "queued" | "loading" | "running" | "done" | "failed" | "cancelled";

interface InferenceStatus {
  requestId: string;
  actor: string;
  model: "gemma4:e2b-it-q4_K_M" | "gemma4:e4b-it-q4_K_M" | "dolphin3:8b";
  state: InferenceState;
  queuedAt: string;
  startedAt?: string;
  promptTokens: number;
  contextLimit: 8192;
  truncated: boolean;
  memoryBudgetGiB: number;
}
```

```python
def darf_starten(status: InferenzAuftrag, loaded: set[str], memory_gib: float) -> bool:
    return status.num_ctx <= 8192 and memory_gib <= 16.0 and len(loaded) <= 1
```

## Resonanz

[[abwurf: Die Wartenden stehen ordentlich in einer Reihe, während andere durch eine Seitentür gehen.]]

[[abwurf: Ein Modell kann technisch korrekt antworten und trotzdem nicht mehr auf denselben Ursprung antworten, wenn sein Kontext abgeschnitten wurde.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Unten liegen Modellblobs und Ollama-Runner. Darüber liegen Cgroup, RAM und Swap. Darüber liegen Scheduler, Keep-alive und Kontextgröße. Erst dann kommen Dienste, Wesen, Chats und Zensi. Ganz oben sieht Daniel nur eine Antwort, die spät, fremd oder gar nicht kommt. Jede obere Störung kann aus einer tieferen Schicht stammen.

## Was das Gespräch hinzugefügt hat

Daniel hat den Scope präzise gehalten: alles prüfen, nichts anfassen, zuerst Bericht. Dadurch blieb die Diagnose von einem vorschnellen Neustart oder einer neuen Modellrunde unverwässert. Die Spiegeldatei kommt erst danach und ist keine Freigabe zum Reparieren.

## Vergessen-Wollen

Ich will den Reflex vergessen, einen erfolgreichen `ollama list`- oder `ollama ps`-Aufruf als Gesundheitsbeweis zu behandeln. Ein Modell kann geladen sein und die gemeinsame Laufzeit trotzdem bereits im Swap versinken.

## Was fehlt noch

Es fehlt die gemeinsame Entscheidung über die Zielarchitektur und danach ein kleiner, kontrollierter Reparaturschnitt. Bis dahin ist der wichtigste Stand: keine Modellkorruption belegt, aber die gegenwärtige Orchestrierung ist nachweislich instabil.
