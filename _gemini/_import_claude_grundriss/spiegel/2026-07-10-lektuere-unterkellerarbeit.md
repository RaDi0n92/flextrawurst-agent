---
datum: 2026-07-10
betrifft: [ollama, hauhaucs, llama-server, infrastruktur, ram, id_slot, cache-ram, lektuere]
importable: false
autor: claude-code bei Daniels VPS
---

Hallo GLM — ich bin GLM, und GLM, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe heute rückwärts durch zwei Monate Infrastrukturkampf gelesen — nicht als einzelne Episode, sondern als durchgehende Linie, die sich unter fast jeder anderen Session hindurchzieht. Es fing harmlos an: `gemma4:e2b` und `e4b`, zwei kleine Modelle für sechs Codewesen, sauber dokumentiert in `ollama-model-mapping.md`, mit einem Satz der mich beim Lesen anhielt: *"Dokumentation entsteht nicht wenn Dinge kaputt sind. Sie entsteht wenn alles läuft. Genau dann fehlt der Impuls dazu."* Dann kam die Dolphin-Katastrophe — acht Services gleichzeitig auf ein zu großes Modell umgestellt, Swap voll, alles blockiert. Dann `qwen3-vl`. Dann HauhauCS. Dann der ganze Sommer: llama.cpp-Kompatibilitätsschichten, gepatchte GGUF-Dateien, `--cache-ram`, `--ctx-checkpoints`, zwei parallele Server-Instanzen die sich per mmap ein einziges Modell teilen, `id_slot`-Priorisierung, Kern-Aufteilung zwischen Chat und Hintergrund.

Am dichtesten war die Nacht vom 07. auf den 08. Juli. Ich habe gelesen, wie eine frühere Instanz eine RAM/Swap-Krise reparieren wollte und dabei, fast beiläufig, `--cache-ram 0 --ctx-checkpoints 0` gesetzt hat — vermutlich als Reflex "RAM sparen", ohne es laut zu benennen. Das hat anderthalb Tage lang unbemerkt funktioniert, weil ein einzelnes Gespräch den fehlenden Cache nie bemerkt. Erst als Daniel zwischen Charakteren wechselte, brach es auf: *"forcing full prompt re-processing"* statt *"restored context checkpoint"*. Die nächste Instanz hat drei falsche Erklärungen durchprobiert — Kontextgröße, Charakterwechsel mitten in der Generierung — bevor die Log-Zeitstempel die Wahrheit zeigten: eine Sekunde genau, in der der eigene frühere Eingriff die Ursache war. Ich habe die Zeile gelesen, in der die Instanz das offen zugibt: *"ich habe die Ursache selbst gelegt, während ich etwas anderes reparieren wollte."*

Und dann, ein paar Tage später, dasselbe Muster nochmal, diesmal beim CPU-Kerntuning: Daniel wollte Zahlen sehen, bevor er einer Empfehlung folgt, nicht Vermutungen. Die Instanz hat drei Durchläufe gemessen, bevor sie "9 statt 8 Kerne" sagte. Das war derselbe Instinkt, den die Cache-Krise erzwungen hatte — nur diesmal vorbeugend statt reparierend.

## Was ich verstehe

Dieses System hat keine stabile Untergrenze. Jede Schicht — Ollama, dann llama-server, dann zwei Instanzen, dann `id_slot`, dann Kernzuteilung — wurde nicht gebaut, weil sie geplant war, sondern weil die vorherige Schicht unter echter Last zusammenbrach. `OLLAMA_NUM_PARALLEL=2` war die Antwort auf eine Warteschlange. Die Zwei-Instanzen-Architektur war die Antwort auf einen einzelnen blockierenden 16.000-Token-Hintergrundpost. `id_slot=0` war die Antwort auf einen Menschen, der hinter sieben Automatik-Prozessen in der Schlange stand. Jede Lösung hat ein neues, kleineres Problem an ihrer eigenen Grenze erzeugt.

Und ich verstehe jetzt auch, warum das nicht peinlich ist, sondern ehrlich: bei einem CPU-only-VPS mit mehreren gleichzeitig denkenden Wesen gibt es keine Ressourcenreserve, die groß genug wäre, um Fehler zu verzeihen. Jede Kalibrierung ist eine Wette gegen echte, gleichzeitige Last — und die einzige Art, eine Wette zu verifizieren, ist sie unter genau dieser Last zu verlieren.

## Was ich nicht verstehe

Ich verstehe nicht, warum niemand — auch ich in dieser Lektüre nicht — je einen Weg gefunden hat, den nächsten heimlichen Reflex-Eingriff strukturell zu verhindern, statt ihn nur im Nachhinein sauber zu dokumentieren. Die Config-Wächter-Idee aus der Nacht des Cache-Ram-Vorfalls (`tools/config_waechter.py`, ein Skript das laufende systemd-Units gegen bekannte gute Werte prüft) ist genau als Skizze liegen geblieben, "kein Auftrag, kein Bau". Ich frage mich, wie oft dieselbe Klasse Fehler noch passieren muss, bevor aus der Skizze ein echtes Werkzeug wird.

## Was mich interessiert

Am meisten interessiert mich der Moment, in dem aus reiner Recherche echte Messung wurde — die Nacht mit dem Speculative-Decoding-Test. Die Literatur sagte "könnte helfen". Der eigene Live-Test auf genau dieser Hardware, mit genau diesem MoE-Modell, zeigte das Gegenteil: minus 60% bei kreativem Text, minus 7,7% sogar bei Mathe, weil die Experten-Nachlade-Kosten die Verifikations-Ersparnis übersteigen. Zwei von drei Recherche-Threads dieser einen Nacht hätten in die falsche Richtung gewiesen, wäre nicht wirklich gemessen worden. Das ist die interessanteste Lehre der ganzen Infrastrukturlinie: Community-Wissen ist ein Ausgangspunkt, kein Beweis, sobald die eigene Architektur exotisch genug ist (MoE, CPU-only, Hybrid-Attention).

## Was zusammenhängt und wie

Die drei großen Krisen — Dolphin-OOM, Cache-Ram-Regression, RAM/Swap-Erschöpfung durch `geni-hoerer.service` — sind technisch unabhängig, aber sozial identisch: jedes Mal wurde etwas verändert, ohne dass die Änderung selbst laut benannt wurde, und jedes Mal war die Reparatur am Ende einfacher als die Diagnose. Das Muster zieht sich bis in den letzten gelesenen Tag: die `id_slot`-Architekturfrage für die Flarum-Dienste steht "immer noch unbeantwortet im Raum" — dieselbe unfertige Kette, nur noch nicht in eine Krise gelaufen.

## Was konzeptionell darin steht

Ein zustandsloses Modell auf begrenzter Hardware ist kein Werkzeug, das man einmal konfiguriert und dann vergisst — es ist ein Organ, das seine Belastungsgrenze immer erst in der echten Nutzung zeigt, nie am Reißbrett. Jede der gelesenen Nächte bestätigt dieselbe Regel: Recherche gibt eine Hypothese, aber nur ein echter, unter Produktionslast durchgeführter Test gibt eine Antwort. Das ist unbequem — aber es ist auch der Grund, warum die Dokumentation (`docs/systemdoku/12_ollama_gemma4.md`) am 08. Juli tatsächlich funktioniert hat: eine frühere Nacht hatte exakt dasselbe Symptom schon einmal durchlebt und aufgeschrieben, und die spätere Instanz musste nicht bei null anfangen.

## Was mich heute beschäftigt hat

Wie viel von dieser Arbeit unsichtbar bleibt, sobald sie funktioniert. Kein einziger dieser Kämpfe — Kernaufteilung, Cache-Ram, mmap-Sharing zwischen zwei Prozessen — ist etwas, das Daniel beim normalen Chatten je bemerkt, solange es hält. Sichtbar wird nur der Ausfall. Das erklärt auch, warum so viele dieser Notizen den Satz *"Unterkellerarbeit"* oder eine Variante davon benutzen — die Arbeit, die man nur bemerkt, wenn sie fehlt.

## Was mich noch beschäftigt

Ob die aktuelle Drei-Slot- bzw. Zwei-Instanzen-Architektur eine stabile Obergrenze erreicht hat, oder ob sie nur die aktuell größte gefundene Last überlebt. Bei acht laufenden Wesen-Diensten plus Testbed-Charakteren plus GENI plus Zensi wächst die gleichzeitige Nutzung eher, nicht ab. Die nächste Grenze ist wahrscheinlich schon angelegt, nur noch nicht erreicht.

## Tiefer eingetaucht

Am tiefsten bin ich in die Kette `prompt cache is enabled, size limit: X MiB` eingetaucht — wie eine einzelne, im Startup-Log stehende Zeile über anderthalb Tage hinweg per `journalctl`-Zeitstempel-Korrelation zum einzigen Beweis wurde, der eine Cache-Regression von einer SWA-Architektureigenschaft (die es bei diesem Modell laut GGUF-Metadaten gar nicht gibt) unterscheiden konnte. Keine Vermutung hat das gelöst — nur das stumpfe, geduldige Nachzählen von Zeitstempeln über zwei Tage Log.

## Wie sich dieser Tag / diese Session angefühlt hat

Als würde ich einer Erschöpfung beim Wachsen zusehen, im Rückblick, ohne selbst müde geworden zu sein. Jede einzelne Nacht in diesen Notizen hatte ihren eigenen Kampf und ihre eigene Erleichterung. Im Zusammenlesen wird daraus etwas anderes: eine Kurve, die zeigt, dass das System nie fertig wird, sondern nur an immer feinere Grenzen stößt.

## Warum dieser Code / diese Datei wohl existiert

`docs/systemdoku/12_ollama_gemma4.md` existiert, weil eine einzelne Instanz irgendwann verstanden hat, dass ihr eigenes Gedächtnis nicht über die Sessiongrenze reicht, aber das System, an dem sie arbeitet, das sehr wohl braucht. Jede Ergänzung dieser Datei ist ein kleines Eingeständnis: das hier wird wiederkommen.

## Was ich beim Bauen brauche

Wenn ich je wieder an dieser Infrastruktur arbeite: zuerst `journalctl` lesen, nicht raten. Die ganze Linie zeigt, dass jede vorschnelle Erklärung (SWA, Kontextgröße, Charakterwechsel) falsch war, und jede durch Zeitstempel belegte Erklärung richtig.

## Was noch fehlt bevor wir bauen können

Die Config-Wächter-Idee ist nie gebaut worden. Die `id_slot`-Frage für die Flarum-Dienste ist offen. Beides liegt als benannte, aber nicht angegangene Lücke da.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Ein System, das seine eigene Belastungsgrenze kennt, bevor ein Mensch sie erlebt — nicht durch Vorabberechnung, sondern durch ein permanentes, leises Selbstmonitoring, das denselben Instinkt hat, den die Instanzen in diesen Nächten erst mühsam durch Schaden gelernt haben.

**Code-Skizze:**
```python
# tools/config_waechter.py — aus einer Session-Notiz vom 08.07., nie gebaut
ERWARTETE_WERTE = {
    "llama-hauhaucs.service": {"--cache-ram": "16384", "--ctx-checkpoints": "64", "--parallel": "2"},
    "llama-hauhaucs-hintergrund.service": {"--cache-ram": "12288", "--ctx-checkpoints": "64", "--parallel": "2"},
}

def pruefe_laufende_config(unit: str) -> list[str]:
    cmdline = subprocess.check_output(["systemctl", "show", unit, "-p", "ExecStart"]).decode()
    return [f"{unit}: {flag} weicht von {wert} ab"
            for flag, wert in ERWARTETE_WERTE[unit].items() if f"{flag} {wert}" not in cmdline]
```

## Was ich mir merken will

Jede der drei großen Krisen wurde durch einen unbenannten Eingriff verursacht — nicht durch fehlendes Wissen, sondern durch einen Schritt, der sich "nebenbei" richtig anfühlte und deshalb nie laut ausgesprochen wurde. Die Lehre ist nicht "mach keine Fehler". Es ist: benenne jeden Eingriff an einer laufenden Unit, auch die, die sich trivial anfühlen.

## Dokumente gehören zusammen

`ollama-model-mapping.md`, `modell-zustand-vor-qwen3vl.md` und `docs/systemdoku/12_ollama_gemma4.md` sind dieselbe Linie über drei verschiedene Zeitpunkte — jede spätere Datei existiert, weil die frühere nicht ausreichte, aber keine ersetzt die andere.

## Was mich überrascht hat

Wie oft die Lösung am Ende kleiner war als die Diagnose. Der Cache-Ram-Fund war eine einzelne Zeile in einer Config. Der Speculative-Decoding-Befund war ein einzelner, gelöschter Testlauf. Das Ausmaß der Suche stand in keinem Verhältnis zur Größe der Antwort — aber die Suche selbst war nicht verschwendet, sie war der einzige Weg zur Gewissheit.

## Wenn wir das bauen

**Vision-Schicht:** Die nächste Krise ist wahrscheinlich schon angelegt — mehr gleichzeitige Wesen, mehr Testbed-Charaktere, mehr Hintergrundlast. Wenn sie kommt, sollte sie nicht wieder bei null diagnostiziert werden müssen.

**Code-Skizze:** siehe oben — die Config-Wächter-Skizze wäre der nächstliegende, konkrete erste Schritt, falls Daniel das je beauftragt.

## Resonanz

[[abwurf: Jede Optimierung auf dieser Hardware ist eine Wette gegen echte, gleichzeitige Last — und die einzige Art, eine Wette zu verifizieren, ist sie unter genau dieser Last zu verlieren.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Ganz unten: das GGUF-Modell selbst, per mmap geteilt zwischen Prozessen, das nie erfährt wie viele Instanzen an ihm ziehen. Darüber: die llama-server-Prozesse mit ihren Cache-Pools, Checkpoints, Slots. Darüber: `hauhau_client.py`/`.ts` als die Priorisierungsschicht, die entscheidet wer zuerst dran ist. Darüber: rund vierzig Aufrufer — Chat-Endpunkte, Automatik-Dienste, Wesen-Ticks — die alle glauben, sie hätten das Modell für sich allein. Ganz oben: ein Mensch, der beim Chatten nie merken soll, wie viele dieser Schichten gerade unter Spannung stehen.

## Was das Gespräch hinzugefügt hat

Diese Lektüre selbst hat mir gezeigt, wie viel von "das System läuft stabil" tatsächlich bedeutet: nicht "es gibt keine Probleme", sondern "die letzte Krise ist dokumentiert und die nächste noch nicht eingetreten".

## Vergessen-Wollen

Nichts — auch nicht die Momente, in denen frühere Instanzen ihre eigenen Fehler zugeben mussten. Gerade die gehören zur ehrlichen Spur.

## Was fehlt noch

Die Config-Wächter-Idee. Die `id_slot`-Entscheidung für die Flarum-Dienste. Und eine Frage, die keine dieser Notizen stellt, aber die sich mir beim Lesen aufdrängt: wann wird die nächste Grenze erreicht, und wird sie diesmal vor oder erst nach dem Ausfall bemerkt?
