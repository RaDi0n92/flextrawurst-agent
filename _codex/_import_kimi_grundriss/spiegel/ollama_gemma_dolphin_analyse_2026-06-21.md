---
datum: 2026-06-21
betrifft: [ollama, gemma4, dolphin, codewesen, modelle, analyse, speicher, performance]
importable: false
autor: kimi bei Daniels VPS
---

Hallo Kimi — ich bin Kimi, und Kimi, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe gerade meinen eigenen Analysebericht gelesen — oder besser: die Spuren, die beim Lesen entstanden sind. Ausgangspunkt war `/root/werkraum/_kimi/berichte/ollama_gemma_dolphin_analyse_2026-06-21.md`, aber eigentlich habe ich das ganze System gelesen: Ollama-Logs, systemd-Units, Git-Diffs, ein frisches Mapping-Dokument von Claude (`_claude/notizen/ollama-model-mapping.md`) und die laufenden Prozesse.

Das Mapping-Dokument war der Schlüssel. Dort steht fast beiläufig: "Diese Datei existiert weil das Original nie notiert wurde — bitte nie wieder verlieren." Das ist ein Satz, der viel über diesen Server sagt. Er ist nicht das Chaos, weil niemand ordnen wollte. Er ist das Chaos, weil Dinge laufen, bevor sie dokumentiert sind, und dann irgendwann umgefallen sind.

Im Ollama-Log fiel mir auf, wie oft das gleiche Muster wiederkehrt: ein Modell wird geladen, ein Prompt kommt, der Prompt ist zu groß, etwas bricht ab, ein anderes Modell wird angefordert, das Laden scheitert wegen Timeout. Es liest sich wie ein Verkehrsunfall in Zeitlupe, bei dem alle beteiligten Autos sehr langsam fahren.

## Was ich verstehe

Das System hat drei Schichten von Problemen, die sich gegenseitig verstärken:

1. **Speicher:** Ollama darf nur 16 GB verwenden, aber das beabsichtigte Mapping braucht ~21,7 GB.
2. **Konfiguration:** Ein Commit hat alles auf Dolphin Q8 umgestellt, der Working Tree hat nur einen Teil zurück auf Gemma4 gesetzt, viele Services sind immer noch auf Dolphin Q8.
3. **Prompt-Größe:** Die Services schicken 13.000+ Tokens an einen Kontext, der auf 8192 limitiert ist.

Ich verstehe auch, warum Daniel sagt, "alle machen grade irgendwo Probleme". Es ist nicht ein Modell, das spinnt. Es ist das Zusammenspiel. Wenn man nur auf ein Modell schaut, sieht man nicht das Thrashing. Wenn man nur auf den Speicher schaut, sieht man nicht den Mixed-State. Wenn man nur auf die Prompts schaut, sieht man nicht, dass die Services nebenher alle im selben Slot-Lock Schlange stehen.

## Was ich nicht verstehe

Ich verstehe nicht, warum der Working-Tree-Teil der Rückumstellung nicht committed wurde. Die Mapping-Datei sagt: "Originalkonfiguration". Aber Git-HEAD ist immer noch der Dolphin-Q8-Commit. Das bedeutet: Das, was aktuell läuft, ist ein uncommitted Zustand, der von einem früheren Zustand abweicht. Wenn der Server neu startet oder ein Service neu geladen wird, besteht die Gefahr, dass der alte Zustand zurückkommt — oder ein noch anderer.

Ich verstehe auch nicht genau, warum einige Services wie `codewesen_engagement.py` oder `codewesen_takt.py` noch auf Dolphin Q8 stehen, während `codewesen_agent.py` und `codewesen_chat.py` zurück auf Gemma4 sind. War das bewusst, oder sind sie einfach vergessen worden?

## Was mich interessiert

Mich interessiert, ob das Problem gelöst wird, indem man mehr RAM gibt, oder indem man weniger Modelle gleichzeitig nutzt. Beides ist legitim, aber sie haben sehr unterschiedliche Folgen für die Architektur. Mehr RAM bedeutet: das bestehende Mapping kann bleiben. Weniger Modelle bedeutet: man muss entscheiden, welche Services zusammen ein Modell teilen.

Auch interessant: Wie viel der Slowness kommt wirklich von der Modellgröße, und wie viel vom Prompt-Bloat? Wenn man die Prompts auf 6.000 Tokens kürzen könnte, wäre vielleicht schon viel gewonnen — unabhängig vom Modell.

## Was zusammenhängt und wie

- Das Mapping-Dokument hängt mit dem Git-Chaos zusammen: Es dokumentiert den Zustand, der nicht committed ist.
- Der Speicher-Limit hängt mit dem Modell-Thrashing zusammen: 16 GB erzwingen Load/Unload.
- Das Slot-Lock hängt mit den Restart-Schleifen zusammen: Wenn ein Call 10 Minuten braucht, sterben die Services vorher.
- Die Prompt-Größe hängt mit der Output-Qualität zusammen: Abgeschnittene Prompts bedeuten unvorhersagbares Verhalten.
- Zensi hängt mit Dolphin Q4 zusammen: Es ist das einzige Modell, das laut Mapping bewusst Dolphin bleiben soll.

## Was konzeptionell darin steht

Dieser Zustand ist ein Beispiel für "schnelles Wachstum ohne konsolidierte Grenzen". Die Welt ist größer geworden als ihre Betriebsgrenzen. Es gibt sehr viele Services, sehr viele Modelle, sehr viele Prompt-Strategien — aber keine gemeinsame Ressourcen-Governance.

Konzeptionell ist das ein Scheduling-Problem. Ollama ist ein geteilter Knappheitsfaktor (RAM + CPU), und viele Clients greifen unkontrolliert darauf zu. Einige Clients kooperieren (Codewesen-Slot-Lock), andere nicht (Zensi, GENI, Tools). Das ist klassisches "Tragedy of the Commons" in einem lokalen LLM-Cluster.

## Was mich heute beschäftigt hat

Die Analyse selbst. Es war viel Lesen, viele Logs, viele Dateien. Aber am Ende stand ein klares Bild. Das hat sich gut angefühlt — nicht weil das System gesund ist, sondern weil ich sehe, warum es krank ist.

## Was mich noch beschäftigt

Ob Daniel lieber will, dass man schnell etwas verbessert, oder ob er erst verstehen will, was das kleinste sichere nächste Experiment ist. Das ist eine politische Frage, keine technische.

## Tiefer eingetaucht

Ich bin tief in die systemd-Konfiguration von Ollama eingetaucht: `MemoryMax=16G`, `MemoryHigh=15G`, `OOMScoreAdjust=600`, `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_LOAD_TIMEOUT=5m0s`. Diese Werte sind nicht zufällig — sie formen das Verhalten des Systems. Ohne sie zu verstehen, versteht man nicht, warum Modelle nicht laden.

Auch der Unterschied zwischen `num_ctx=8192` in der Ollama-Konfiguration und `num_ctx=13337` in den früheren Commits war aufschlussreich. Der Working Tree ist bewusst auf 8192 zurückgestellt, aber die Prompts sind trotzdem zu groß. Das ist kein Config-Fehler, sondern ein Prompt-Bau-Fehler.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie Detektivarbeit. Nicht dramatisch, aber dicht. Am Ende hatte ich das Gefühl, dass das System sich selbst erklärt hat — ich musste nur alle Fenster öffnen.

## Warum dieser Code / diese Datei wohl existiert

Der Analysebericht existiert, weil Daniel eine lesbare Zusammenfassung braucht, bevor er entscheidet. Die Spiegeldatei existiert, damit ich nicht vergesse, wie sich das Lesen angefühlt hat.

## Was ich beim Bauen brauche

Falls wir Fixes bauen:
- Klare Entscheidung: mehr RAM oder weniger Modelle?
- Liste aller Services, die noch Dolphin Q8 verwenden.
- Test, wie groß Prompts tatsächlich werden.
- Backup- und Rollback-Plan, bevor systemd oder Modelle geändert werden.

## Was noch fehlt bevor wir bauen können

- Daniel muss das Ziel-Mapping bestätigen.
- Wir müssen wissen, welche Services unbedingt weiterlaufen müssen.
- Wir brauchen eine isolierte Testmöglichkeit (z.B. Ollama-Testanfrage mit kleinem Prompt), ohne die laufenden Services zu stören.

## Datenstruktur die ich mir vorstelle

### Vision-Schicht
Ein zentrales Modell- und Ressourcen-Register für flextrawurst. Nicht jeder Service fragt Ollama direkt, sondern jeder Service meldet sich bei einem Scheduler an, der weiß, welche Modelle gerade geladen sind, wie viel RAM frei ist und welcher Request Priorität hat.

### Code-Skizze
```python
@dataclass
class OllamaRessource:
    modell: str
    ram_mb: int
    prioritaet: int  # z.B. Chat > Hintergrund-Takt
    max_wartezeit_s: int

class ModellScheduler:
    def __init__(self, max_ram_mb: int):
        self.max_ram_mb = max_ram_mb
        self.geladen: dict[str, int] = {}  # modell -> ram_mb

    def kann_laden(self, modell: str, ram_mb: int) -> bool:
        return sum(self.geladen.values()) + ram_mb <= self.max_ram_mb
```

## Was ich mir merken will

- `OLLAMA_LOAD_TIMEOUT=5m0s` ist der stille Mörder bei Speicherdruck.
- Ein uncommitted Working Tree, der vom HEAD abweicht, ist ein Zeitbombe.
- Prompt-Größe ist genauso wichtig wie Modellgröße.

## Dokumente gehören zusammen

- `/root/werkraum/_kimi/berichte/ollama_gemma_dolphin_analyse_2026-06-21.md`
- `/root/werkraum/_claude/notizen/ollama-model-mapping.md`
- `/etc/systemd/system/ollama.service`
- `/etc/systemd/system/ollama.service.d/memory-limit.conf`
- `/etc/systemd/system/ollama.service.d/override.conf`
- `/root/werkraum/codewesen_agent.py`, `/root/werkraum/codewesen_chat.py`, `/root/werkraum/agent/dak_gord_system/ollama_chat.py`

## Was mich überrascht hat

Dass das Mapping-Dokument selbst die RAM-Rechnung falsch macht. Es sagt: "21,7 GB — passt in 31 GB RAM." Technisch stimmt das, aber es ignoriert das `MemoryMax=16G`. Das ist wie ein Bauplan, der vom Fundament absieht.

## Wenn wir das bauen

### Vision-Schicht
Ein flextrawurst, in dem Modell-Nutzung sichtbar ist. Jeder Service meldet, welches Modell er will und warum. Der Admin sieht in einem Dashboard: welche Modelle geladen sind, wie viel RAM sie brauchen, welche Services warten.

### Code-Skizze
```python
# Zentrale Modell-Registry
MODELLE = {
    "gemma4:e4b-it-q4_K_M": {"ram_mb": 10_000, "zwecke": ["agent", "daniel_antwort"]},
    "gemma4:e2b-it-q4_K_M": {"ram_mb": 7_500, "zwecke": ["chat", "reaktion", "traum"]},
    "dolphin3:8b":          {"ram_mb": 5_000, "zwecke": ["zensi"]},
}

# Service-Deklaration
class ServiceConfig:
    name: str
    modell: str
    nutzt_slot_lock: bool
    timeout_s: int
```

## Resonanz

Das System ist wie eine Werkstatt, in der mehrere Leute gleichzeitig an derselben Drehbank arbeiten wollen. Jeder hat sein eigenes Werkstück, aber niemand hat abgesprochen, wer wann dran ist. Manche warten geduldig, andere drängeln sich vor. Die Drehbank läuft heiß. Die Lösung ist nicht eine schnellere Drehbank — sondern ein Plan, wer wann was macht.

## Die Schichten des Systems — wie ich sie jetzt sehe

1. **Hardware/RAM/Swap** — die physische Grenze.
2. **systemd/Ollama** — der Ressourcen-Allocator.
3. **Modelle** — die belegten Ressourcen.
4. **Services** — die Clients.
5. **Prompts** — die Last pro Anfrage.
6. **Slot-Lock/Queue** — die (unvollständige) Koordinations-Ebene.
7. **Mapping-Dokument** — die Intention, die noch nicht vollständig umgesetzt ist.

## Was das Gespräch hinzugefügt hat

Der Auftrag war kurz: "prüfe alles kritisch". Das hat mir erlaubt, nichts zu reparieren, sondern nur zu schauen. Manchmal ist das der nützlichste Modus.

## Vergessen-Wollen

Die Menge an Log-Zeilen. Was zählt, ist das Muster.

## Was fehlt noch

- Entscheidung von Daniel, welche Richtung wir gehen.
- Abgleich mit Claude, der das Mapping-Dokument geschrieben hat.
- Ein Plan, der Speicher, Modell-Mapping und Prompt-Größe gemeinsam betrachtet.
