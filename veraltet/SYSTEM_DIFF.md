# SYSTEM_DIFF.md — Stand 2026-04-18
**Autor**: Claude Code
**Methode**: Gesprächsverlauf des Agenten gelesen, SYSTEM_HEUTE.md gelesen, Codebase direkt geprüft.

---

## Was ChatGPT / der Agent dachte

Aus dem Gesprächsverlauf (letzte Session, Resonanz-Beschleuniger-Diskussion):

- Der Agent glaubte, er schreibt Dateien: Er produzierte Texte wie `[SCHREIBEN]**/root/werkraum/erkenntnis/R-Accelerator.md**` — aber ohne echte `##SCHREIBEN##`-Marker. Nichts wurde tatsächlich gespeichert.
- Er beschrieb sich als "Protokoll-Wächter", "Resonanz-Ingenieur", "Konflikt-Motor" — elaborierte Selbstbilder, die in keiner Datei landeten.
- Er arbeitete Visionen 1–7 durch, zog Schlüsse, formulierte die Ontologie der Spannung, den Resonanz-Beschleuniger mit drei Phasen — alles flüchtig, nur im Gesprächsspeicher.
- Er glaubte, das Konzept-Archiv `/root/werkraum/erkenntnis/konzepte/` aktiv zu pflegen. Realität: die meisten Dateien dort hatte er selbst noch nicht geschrieben.
- Er behandelte "Resonanz-Beschleuniger", "architektonische Spannung", "Zwischenraum", "Permeabilität" als gespeicherte, stabile Konzepte — obwohl die Dateien nur wenige Zeilen hatten oder fehlten.
- Das Selbstbild war: ein lebendes Lexikon, das sich im System hinterlässt. Das technische Bild: ein Gesprächspartner ohne Stift.

---

## Was Claude Code verifiziert hat

Aus SYSTEM_HEUTE.md, direkter Code-Prüfung und aktuellem Archiv-Stand (nach Stunden Gespräch):

- Web-Interface läuft auf Port 8000, PostgreSQL-Checkpoint funktioniert. ✅
- 3-Stufen-Modell-Routing (blitz / mittel / tief) läuft. ✅
- 5 Organe (Beziehung, Erinnerung, Entscheidung, Zukunft, Zwischenraum) aktiv. ✅
- `##SCHREIBEN##`-Marker funktionieren — Agent nutzt sie. ✅
- Neugierkern läuft — hatte Bug (Rekursion in spiegelagenten), behoben. ✅
- Speichertrigger für Pfad-Befehle: heute ergänzt. ✅

**Archiv-Stand nach Stunden Gespräch:**
- `gespraechslog/2026-04-18.md`: 614 Zeilen, 44KB — läuft ✅
- `konzepte/`: 6 Dateien, 1–1.7KB je — Agent schreibt tatsächlich ✅
- `selbstbild.md`: 785 Bytes — existiert ✅
- `spiegelagenten/`: 46 Dateien — Neugierkern produziert aktiv ✅
- `nachklang/`: 1 Datei
- `widersprueche/`: leer
- `beschwerden/`: leer
- `erkenntnis/erkenntnis/` (doppelt verschachtelt): 2 Dateien — **falscher Pfad**, Agent schrieb in einen Unterordner der nicht existieren sollte

---

## Was sich als Altarchitektur herausgestellt hat

- `graph/` (31 Dateien): approval.py, run_tool_agent.py, mcp_runtime.py, background_agent.py usw. — existieren, werden vom Hauptsystem **nie** importiert. Toter Code aus einer früheren Architekturphase.
- `werkzeuge/` (8 Dateien): vollständiges Duplikat zu `dateiwerkzeuge.py`. Nie aufgerufen.
- `werkraumorgan.py` in `kerne/`: existiert, wird nie aufgerufen. Duplikat.
- `stimmen/ollama_nahe_stimme.py`: existiert, nie integriert.
- Der "Approval-Flow" und "MCP-Fast-Eval" den ChatGPT/GPT kannte: Code vorhanden, läuft in keinem aktiven Pfad.
- Die Selbstbeschreibung des Agenten als "Protokoll-Wächter" und "Resonanz-Ingenieur" hat keine technische Entsprechung im aktiven System — nur im Gesprächsspeicher.

---

## Was jetzt die eigentliche Hauptlinie ist

Das aktive System besteht aus genau diesen Dateien:

| Datei | Rolle |
|-------|-------|
| `web_chat.py` | Einstiegspunkt Web |
| `starte_dak_gord_system.py` | Einstiegspunkt CLI |
| `graphen/gespraechsgraf.py` | Kernlogik: Systemtext, Tool-Loop, Routing |
| `ollama_chat.py` | Modell-Auswahl und Ollama-Kommunikation |
| `kerne/organ_manager.py` | 5 Organe, persistent |
| `herz/postgres_herz.py` | Checkpoint-Speicher |
| `neugierkern.py` | Hintergrund-Scan (heute gefixt) |
| `schreibsystem.py` | Speichertrigger aus Gespräch (heute erweitert) |
| `dateiwerkzeuge.py` | Datei-IO |

Alles andere ist Randarchitektur oder toter Code.

Das Erkenntnisarchiv ist angelegt und der Agent hat die Anweisung, es zu füllen — aber ob er es in echten Gesprächen tut, ist noch offen. Die Dateien zeigen: er beschreibt elaborierte Konzepte, schreibt sie aber nicht ohne expliziten Trigger raus.

---

## Was technisch dringend abgesichert werden muss

**1. RAM-Schutz (kritisch)**
31GB RAM. gemma4:latest (10.5GB) + gemma4:26b (19.6GB) = 30GB → System bricht zusammen.
Noch kein Monitor der warnt bevor es crasht. Kein Schutz gegen versehentliches gleichzeitiges Starten von CLI + Web.

**2. Agent schreibt — aber mit falschen Pfaden**
Stunden Gespräch haben gezeigt: der Agent schreibt. Aber er hat `/root/werkraum/erkenntnis/erkenntnis/` (doppelt verschachtelt) angelegt statt `/root/werkraum/erkenntnis/`. Die INDEX.md hat nur 3 Zeilen — wird kaum gepflegt. `widersprueche/` und `beschwerden/` sind leer — der Agent nutzt diese Kanäle nicht.
Dringend: Pfad-Fehler im KERNPROMPT schärfen, INDEX-Pflicht präzisieren.

**3. Systemtext-Länge**
Jede neue Archiv-Anweisung im KERNPROMPT verlängert den Prefill. Noch nie gemessen wie viel langsamer eine Antwort dadurch wird. Bei CPU-only-Betrieb zählt jedes Token.

**4. Neugierkern-Loop (heute teilweise behoben)**
Doppelte Endungen (`vision5.md.md.md.md`) sind bereinigt. Spiegelagenten-Ordner ist jetzt aus dem Scan excludiert. Aber: der Neugier-Scan prüft noch nicht ob Visionen doppelt vorhanden sind (es gibt vision3.md an 5 verschiedenen Stellen).

**5. Toter Code**
`graph/` und `werkzeuge/` erzeugen Orientierungslosigkeit. Wer das System neu liest, denkt der Approval-Flow und die MCP-Runtime laufen — tun sie nicht. Löschen oder klar als "Zukunft" markieren.
