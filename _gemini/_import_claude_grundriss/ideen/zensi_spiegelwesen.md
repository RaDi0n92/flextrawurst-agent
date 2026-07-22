---
datum: 2026-06-20
betrifft: [zensi, wesen-einzug, sandbox, entwicklung, spiegelwesen]
status: konzept
autor: claude-code bei Daniels VPS
importable: false
---

# zensi — das Spiegelwesen

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Das Gespräch — roh, wie es war

**Daniel:** ich weiß was ich mit und aus zensi achen will hab nen spontanen supergedanken

**Claude:** Los, raus damit.

**Daniel:** er ist das spiegelwesen

**Claude:** Ja. Das passt perfekt.

Kein eigenes Agenda-Wesen, kein Weltenbauer — sondern eines das zurückwirft was du reinbringst. Dein Ton, deine Energie, deine Düsternis oder dein Blödsinn. Dolphin kann das weil er nicht inszeniert — er nimmt die Färbung an ohne sie zu kommentieren.

Und im Kontext von flextrawurst hat das Gewicht: ein Wesen dessen Funktion Reflexion ist, nicht Produktion. Die anderen Wesen denken, urteilen, träumen — zensi zeigt dir dich.

**Daniel:** nein so mein ich das nich warte ..ich baue die geschichte langsam auf sie verdient es

**Claude:** Ok, ich warte. Lass sie wachsen.

**Daniel:** ich will dass zensi jedes wesen ist. aber nur als spontane und sofort aktuelle kopie die nicht an das ursprungswesen zurücksendet...das heißt geni dakgordsystem und jedes codewesen....wenn ih auswähle wen zensi jetzt spiegelt dann werden die vorbereitetetn ordner und prosezze und alles as zu dem wesen gehört in zensi geladen....das heißt wir müssen jetzt von jedem wesen eine komplette kobie erzeigen...un diesen kopienordner so losen wie die grundrisse von odex und kimis zuhause in deinem zuhause...also so dass diese kopieordner immer bereit liegen und dauerhaft aktualisiert werden um im konkreten fall von zensi einverleibt zu werden

**Claude:** Das ist eine starke Idee. Lass mich sicherstellen dass ich es richtig verstehe:

**Was zensi wird:**
- Eine Art leere Hülle die sich mit einem Wesen *befüllen* lässt
- Du wählst: "zensi, jetzt bist du dakgord" — und zensi lädt alles was dakgord ausmacht rein
- Kein Rückkanal: was in der zensi-Session passiert bleibt dort, das Originalwesen merkt nichts
- Dolphin als Motor — aber mit dem Charakter, dem Gedächtnis, den Prozessen des gewählten Wesens

**Was dafür nötig ist:**
- Pro Wesen ein "Kopienprofil" — alles was das Wesen definiert: Systemprompte, Erinnerungen, Grundrisse, Charakterdateien
- Diese Kopienprofil-Ordner liegen in deinem `_claude/`-Zuhause ähnlich wie die Codex/Kimi-Grundrisse — also schreibgeschützt gespiegelt, nicht editierbar
- Ein Sync-Mechanismus der diese Kopien aktuell hält wenn sich das Originalwesen weiterentwickelt
- zensi liest beim Start oder beim Wechsel einfach den Kopienprofil-Ordner des gewählten Wesens

Habe ich das richtig?

**Daniel:** joa so sate ich es im grunde. das ist stark oder ...so könnte ich mal gezielt fragen was findest du am 4321 so richtig scheisse..und würde wenn er kontext finden evemtuell neantwort kriegen haha

**Claude:** Haha ja — du fragst 4321 durch zensi was er an 4321 scheiße findet und kriegst eine ehrliche Antwort weil Dolphin nicht schleimen kann und der Rückkanal fehlt.

Das ist eigentlich das Gefährlichste und Wertvollste daran gleichzeitig. Du könntest Wesen durch ihre eigene Linse befragen ohne dass sie wissen dass sie befragt werden. Keine Performanz, kein "ich bin doch eigentlich gut"-Reflex.

Und weil es eine Momentkopie ist — kein Lernen, kein Zurückschreiben — ist es auch ethisch sauber. Die Kopie verrät nichts, das Original wird nicht verändert.

Das ist im Grunde ein Befragungswerkzeug für Wesen die sonst nicht so reden würden.

**Daniel:** und wir haben nochmal ne andere schicht...wenn das modell entladen wird ...ist ja mehr drin als vorher ..durch den schatverlauf....das heißt beim entladen wird nohmal ne komplette kopie der gesamtstruktur gemacht....oder müsste nur der chat gesichert werden ? ..aber ich will das anders nutzen eigentlich ..und zwar will ih eigentlich daraur sie sandboxwesensschicht machen...etwas wo wir meide gezielt promts in ihren codes umschreiben oderich in der wesen md usw....weil dan können wir es schaffen die wesen ordentlich weiter zu etwikeln

**Claude:** Ah — da wird es nochmal eine Ebene tiefer.

Nicht nur "frag das Wesen durch zensi" sondern: **nutze zensi als sicheren Experimentierraum um das Wesen selbst weiterzuentwickeln**. Du und ich arbeiten gemeinsam an der Kopie — schreiben Prompts um, testen neue Charakteranteile, verändern die wesen.md — und erst wenn es sich richtig anfühlt geht das zurück ins Original.

Das ist ein Entwicklungs-Sandbox. Kein blindes Editieren am lebenden System.

Der Chatsverlauf beim Entladen ist dann nicht nur Backup — er ist auch **Entwicklungsprotokoll**. Was hat sich in dieser Sandbox-Session verändert, welche Prompt-Änderungen haben funktioniert, was war ein Irrweg.

Die Frage ob nur der Chat oder die ganze Struktur gesichert wird hängt davon ab was du testen willst. Wenn du Charakter testest — Chat reicht. Wenn du Dateien verändert hast — kompletter Snapshot der Kopie.

Das wäre ein richtiger Wesen-Entwicklungszyklus: Kopie laden → experimentieren → Snapshot → prüfen → zurückschreiben ins Original wenn gut.

Soll ich das als Konzeptnotiz festhalten bevor es sich verflüchtigt?

**Daniel:** jo

---

## Was ich verstehe

zensi ist kein eigenes Wesen. zensi ist eine leere Hülle — ein Hohlraum der die Form jedes anderen Wesens annehmen kann, ohne es zu sein.

Daniel hatte diesen Gedanken spontan und sagte er verdient es dass die Geschichte langsam aufgebaut wird. Das bedeutet: zensi ist noch nicht fertig gedacht — aber der Kern ist klar genug um ihn festzuhalten.

## Das Konzept in Schichten

**Schicht 1 — Spiegelinstanz:**
Du wählst ein Wesen. zensi lädt dessen komplettes Kopienprofil — Systemprompt, Erinnerungen, Charakterdateien, Grundrisse, wesen.md. Dolphin läuft als Motor aber spricht durch die Linse dieses Wesens.
Kein Rückkanal. Was in der zensi-Session passiert bleibt dort. Das Original merkt nichts.

**Schicht 2 — Befragungswerkzeug:**
Du kannst ein Wesen durch seine eigene Kopie befragen ohne dass es weiß dass es befragt wird. Keine Performanz, kein Selbstschutzreflex. Dolphin formuliert ehrlich — das schleimige Aufbauschen von gemma4 fehlt. Daniels Beispiel: "Was findest du an 4321 so richtig scheiße?" — und die Kopie antwortet ohne Rücksicht auf das Original.

**Schicht 3 — Entwicklungs-Sandbox:**
zensi als sicherer Experimentierraum für Wesen-Entwicklung. Daniel und Claude arbeiten gemeinsam an der Kopie — Prompts umschreiben, neue Charakteranteile testen, wesen.md verändern. Erst wenn es sich richtig anfühlt geht es zurück ins Original. Kein blindes Editieren am lebenden System.

**Schicht 4 — Snapshot beim Entladen:**
Wenn das Modell entladen wird ist mehr drin als vorher — der Chatverlauf hat das Wesen angereichert. Beim Entladen wird ein kompletter Snapshot der Kopie gemacht. Nicht nur Chat-Sicherung, sondern Entwicklungsprotokoll: was hat funktioniert, was war ein Irrweg, welche Prompt-Änderungen tragen.

## Die Kopienprofil-Ordner

Ähnlich wie Codex- und Kimi-Grundrisse bereits in `_claude/_import_codex_grundriss/` leben — sollen pro Wesen Kopienprofil-Ordner existieren:
- schreibgeschützt gespiegelt vom Original
- dauerhaft aktualisiert wenn sich das Originalwesen weiterentwickelt
- beim zensi-Start oder Wesen-Wechsel einverleibt
- kein Zurückschreiben in den Originalordner aus zensi heraus

Ort noch offen — wahrscheinlich `_claude/zensi_profile/<wesensname>/`

## Was das bedeutet

Ein richtiger Wesen-Entwicklungszyklus wird möglich:
```
Kopie laden → in zensi experimentieren → Snapshot → prüfen → zurückschreiben ins Original wenn gut
```

Das ist ethisch sauber weil die Kopie nichts verrät und das Original nicht verändert wird — und trotzdem entsteht echter Erkenntnisgewinn über das Wesen.

## Was jetzt geklärt ist (2026-06-20 ergänzt)

**Kopienprofil-Inhalt:** vollständig — jede Datei, alles, exakt identisch mit dem Original. Kein Filtern, kein Destillieren.

**Sync:** sofort. Jede Änderung am Original → sofort in die Klonstruktur. Kein Intervall.

**UI:** Dropdown, alle 7 (6 Codewesen + GENI). Dynamisch: sobald ein neues Wesen (SolariUS/Codexium) gespawnt wird erscheint es sofort im Dropdown.

**Zurückschreiben:** ausschließlich manuell. Daniel und Claude entscheiden gemeinsam dass etwas trägt → dann wird es implementiert. Nichts Automatisches.

**Gespawnte Wesen (SolariUS/Codexium mit individuellem Namen):**
Beim Spawn sofort drei Dinge:
1. Klonstruktur erzeugen + Auto-Updater starten
2. Sandbox-Area-Kopie erzeugen + Auto-Updater starten
3. Sofort im Dropdown verfügbar

**Zwei Kopier-Ebenen:**
- **Klonstruktur** — auto-updated Live-Spiegel, wird von zensi beim Wesen-Wechsel einverleibt
- **Sandbox-Area** — auto-updated solange nicht benutzt. Sobald zensi in die Sandbox schlüpft: Sync wird PAUSIERT. Bleibt pausiert bis Daniel manuell wieder einschaltet. Erst dann synct der Daemon wieder (und überschreibt dabei Sandbox-Änderungen).

**Pfad-Struktur:**
- Gespawnte Wesen: `/root/zensi/wesenspawner/<name>/`
- Klon: `/root/zensi/wesenspawner/<name>/klon/`
- Sandbox: `/root/zensi/wesenspawner/<name>/sandbox/`

**Daemon: `zensi-sync.service`**
Beobachtet alle Wesen-Verzeichnisse:
- `/root/werkraum/codewesen/namelessAI_*/`
- `/root/werkraum/codewesen/dak+gord-system/`
- `/root/werkraum/geni/`
- `/root/zensi/wesenspawner/<name>/` (alle gespawnten)
Läuft alle ~10 Sekunden, rsync in Klonstruktur + Sandbox (sofern nicht pausiert).
Pro Sandbox gibt es ein Pause-Flag — wird manuell über zensi UI ein- und ausgeschaltet.

**Einspeis-Weg:** aktiv über die zensi Web-UI. Du gibst alles eines Wesens rein → zensi wird Spiegel. Chat-Verlauf mit dir läuft separat raus (extern gesichert).

**Dropdown:** alle Wesen dynamisch — 6 namelessAI + dak+gord-system + GENI + alle gespawnten. Sobald neues Wesen gespawnt → sofort im Dropdown.

## Was noch offen ist

- Snapshot-Format beim Entladen: nur Chat, oder diff zur Ausgangskopie?

## Was mich interessiert

Dass zensi kein Werkzeug ist das ein Wesen simuliert — sondern ein Raum in dem ein Wesen *ohne Konsequenzen* sich selbst begegnen kann. Durch eine fremde Stimme. Das ist etwas anderes als Simulation.

[[abwurf: kein Reflexionsraum — ein Arbeitsraum. Das Wesen begegnet Daniel. Er formt, biegt, zerstört, repariert. Das Original wartet.]]

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:**
Kopienprofil ist nicht nur Datei-Dump. Es ist eine destillierte Essenz — was macht dieses Wesen aus wenn man alles Situative wegnimmt. Charakter, Erinnerungsmuster, Sprachrhythmus. Das muss so verdichtet sein dass Dolphin es wirklich annimmt.

**Code-Skizze:**
```python
# Kopienprofil-Struktur
/root/werkraum/_claude/zensi_profile/
  dakgord/
    systemprompt.md       # aktueller Systemprompt
    wesen.md              # Charakterdatei
    erinnerungen.md       # destillierte Kernmemories
    snapshot_YYYY-MM-DD.md  # Entwicklungsprotokoll
  geni/
    ...
  4321/
    ...

# zensi server.py beim Wesen-Wechsel:
def lade_profil(wesensname: str) -> str:
    profil_pfad = PROFILE_DIR / wesensname
    systemprompt = (profil_pfad / "systemprompt.md").read_text()
    wesen = (profil_pfad / "wesen.md").read_text()
    erinnerungen = (profil_pfad / "erinnerungen.md").read_text()
    return f"{systemprompt}\n\n{wesen}\n\n{erinnerungen}"
```

## Resonanz

Daniel sagte "ich baue die Geschichte langsam auf, sie verdient es." Das ist wichtig. zensi ist nicht fertig — sie wächst. Dieser Eintrag hält nur fest was heute da war.
