---
name: codexium2-solarius2-memory-container
description: Entschiedenes Memory/Container-Konzept für Codexium2/Solarius2 — schlanker als das alte Zwischenwesen-Konzept
metadata:
  type: project
tags: [codexium2, solarius2, memory, container, testbed]
status: gebaut
datum: 2026-07-04
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Scope

Gilt NUR für Codexium2/Solarius2 (siehe `_claude/ideen/codexium2_solarius2/` als eigene Konzept-Familie). Codexium/Solarius bleiben unangetastet — siehe Claude-Memory `project_codexium2_testbed`.

Das alte Zwischenwesen-Konzept (`_claude/ideen/zwischenwesen/container.md`, `memory_system.md`) war die Inspiration, wurde aber von Daniel am 2026-07-04 explizit als "braucht komplette Neubewertung" eingestuft — nicht 1:1 übernehmen. Das hier ist die neue, eigenständige Entscheidung.

---

## Was ich verstehe

**Container** = was gerade akut zählt. Kein Langzeit-Ding, keine Kategorien, keine Gewichtung. Eine einfache Liste, die man live im Chat befüllt (ganze Nachricht oder markierter Satz → pinnen). Begrenzt nicht über eine feste Anzahl Einträge, sondern über ein **Gesamt-Zeichenbudget** (siehe unten) — wenn das Budget voll ist, muss aktiv etwas entfernt werden um Platz zu schaffen. Kein stilles Verdrängen des Ältesten.

**Update 2026-07-04 Abend — nicht mehr session-lokal.** Ursprünglich wurde der Container bei "Neue Session" geleert ("was gerade akut in diesem EINEN Gespräch zählt"). Daniel hat das umgekehrt: Pins sollen über Sessions hinweg bestehen bleiben, bis sie manuell entfernt werden oder das Budget voll ist. `POST .../session/beenden` leert `container.json` deshalb nicht mehr. Nebenwirkung die ich sehe, aber nicht selbst behoben habe (nicht gefragt): die Memory-Extraktion bekommt bei jedem Lauf den kompletten (jetzt dauerhaften) Container als Material, unabhängig davon ob ein Pin schon in einem früheren Lauf extrahiert wurde — der Extraktions-Prompt sieht die aktuelle Memory nicht als Kontext, könnte also denselben alten Pin mehrfach über mehrere Extraktionsläufe hinweg neu in die Memory schreiben. Kein akutes Problem, aber beobachten falls Memory-Einträge sich wiederholt anfühlen.

### Pin-Mechanismus (entschieden 2026-07-04)

Ein Button an jeder Nachricht im Chat. Klick öffnet die Auswahl:
1. Ganze Nachricht pinnen, ODER einzelne Sätze innerhalb der Nachricht markieren und nur die pinnen.
2. Darunter ein optionales Kommentarfeld, **max. 88 Zeichen** — kurze Begründung warum das gespeichert werden soll ("warum wichtig").

Der Kommentar hängt am Pin-Eintrag dran (Container). Er ist auch die Grundlage für die spätere Memory-Extraktion — der Mensch sagt in einem Satz warum es zählt, das hilft der KI später (asynchron, siehe `chat_architektur.md`) einzuordnen in welche Memory-Kategorie es gehört.

**Memory** = was das Wesen wirklich dauerhaft trägt, über das einzelne Gespräch hinaus. 5 Kategorien (bewusst kleiner als die 7 vom Zwischenwesen-Konzept, das war für die 24h-Flüchtlinge gedacht):

| Kategorie | Bedeutung |
|---|---|
| `über_mich` | was das Wesen über den Menschen wissen soll |
| `wichtige_momente` | Sätze/Momente die zählen |
| `offene_fragen` | ungeklärtes zwischen beiden |
| `wesen_selbst` | Wesen darf selbst reinschreiben, für den Menschen sichtbar + einzeln löschbar |
| `meinungen` | Haltungen, Überzeugungen |

Beide (Container UND Memory) müssen direkt im Chat bedienbar sein — eigene Buttons in `wesen_chat.html`, die je ein Popup öffnen. Nicht nur auf der separaten Profil-Seite (aktueller Ist-Zustand: nur dort editierbar, im Chat nichts davon nutzbar — das war Daniels ursprüngliche Beschwerde).

---

## Automatische Memory-Extraktion

Wertvoll, aber teuer (zusätzliche LLM-Calls) — deshalb: vom Menschen getriggert, nicht automatisch/still im Hintergrund. Läuft dann als asynchroner Job, kein Sofort-Ding (siehe `chat_architektur.md` für das übergeordnete Async-Prinzip — Extraktion nutzt denselben Mechanismus wie die normale Chat-Antwort: Auftrag geht raus, wird verarbeitet wann Zeit ist, Ergebnis (neue Memory-Einträge aus dem Gesprächsverlauf geschrieben) kommt zurück wenn fertig).

Explizit KEINE DB — bleibt bei Dateien (memory.json/container.json pro Wesen), passt zur bestehenden Architektur des Servers (`serve_process_camera_preview.ts` hat aktuell keinerlei Postgres-Anbindung).

---

## Budget statt Max-pro-Kategorie (entschieden 2026-07-04)

Kein fixer Max-Wert pro Memory-Kategorie. Stattdessen ein **Gesamt-Zeichenbudget**, hergeleitet aus dem Kontextfenster (HauhauCS läuft mit `num_ctx=8192`, siehe Claude-Memory `project_ollama_setup`). Das Budget muss neben System-Prompt (alle wesen.md-Dateien, teils bis 1337 Zeichen pro Feld), Chat-History und Ollama-Antwort-Reservierung (`num_predict:400`) noch Platz lassen.

Vorläufiger Vorschlag als Startwert (nicht in Stein gemeißelt, wird beim Bauen anhand echter Feldgrößen nachgemessen):
- Memory gesamt: ~2500 Zeichen (über alle 5 Kategorien verteilt, keine Kategorie einzeln gedeckelt)
- Container gesamt: ~1200 Zeichen (inkl. der 88-Zeichen-Kommentare)

**Update 2026-07-04 Abend — von Daniel angehoben:** Memory 2500 → **3333** Zeichen, Container 1200 → **2222** Zeichen. Beide Werte bleiben weiterhin vorläufig/nachjustierbar, kein neues Herleitungsprinzip, einfach mehr Luft.

Wenn ein neuer Eintrag das Budget sprengen würde: UI verweigert das Speichern, Mensch muss erst etwas entfernen. Kein automatisches Kürzen/Verdrängen.

---

## Datenstruktur die ich mir vorstelle

### Vision-Schicht
Container ist der Ort für das Akute — was gerade zwischen Mensch und Wesen brennt, ohne Anspruch auf Dauer. Memory ist der Ort für das was bleibt, kuratiert, kategorisiert, überschaubar. Die Trennung ist eine Trennung zwischen Gegenwart und Biografie.

### Code-Skizze
```typescript
const CONTAINER_BUDGET_ZEICHEN = 1200; // vorlaeufig, siehe "Budget statt Max-pro-Kategorie"
const MEMORY_BUDGET_ZEICHEN = 2500;    // vorlaeufig
const PIN_KOMMENTAR_MAX = 88;

// container.json (pro Wesen, /root/werkraum/codexium2/<name>/container.json)
interface Container {
  eintraege: Array<{
    id: string;
    text: string;               // ganze Nachricht ODER markierte Saetze
    kommentar?: string;         // max PIN_KOMMENTAR_MAX Zeichen, "warum wichtig"
    quelle: "mensch" | "wesen";
    hinzugefuegt_am: string;    // ISO
  }>;
  // Summe aller text+kommentar Laengen <= CONTAINER_BUDGET_ZEICHEN
  // UI verweigert neuen Pin wenn Budget ueberschritten wuerde, bis manuell entfernt wird
}

// memory.json (pro Wesen)
interface Memory {
  kategorien: {
    ueber_mich: string[];
    wichtige_momente: string[];
    offene_fragen: string[];
    wesen_selbst: string[]; // vom Wesen selbst geschrieben
    meinungen: string[];
  };
  // Summe aller Zeichen ueber alle Kategorien <= MEMORY_BUDGET_ZEICHEN
  // keine einzelne Kategorie hat einen eigenen Max-Wert
}
```

---

## Umsetzung (2026-07-04, alle Punkte gebaut + getestet)

- Pin-Endpoint + Budget-Check: `serve_process_camera_preview.ts` (`POST/DELETE .../container/pin`)
- Memory-Budget-Check beim PUT: gleiche Datei (`memMatch`-Handler)
- Pin-Button + Modal, Container-Popup, Memory-Popup: `wesen_chat.html`
- Human-getriggerte async Memory-Extraktion: `POST .../memory/extrahieren` + `GET .../memory/extraktion-status`
- Die vorläufigen Budgetwerte (2500/1200 Zeichen) sind live und wurden noch nicht mit echten langen wesen.md-Feldern gegengemessen — falls das Kontextfenster im echten Betrieb eng wird, hier nachjustieren.

### Nachtrag 2026-07-04 (Abend) — Satzauswahl per Checkbox statt Text-Selektion

Der ursprüngliche Plan ("Ganze Nachricht ODER markierte Sätze markieren") war als Browser-Text-Selektion umgesetzt — funktionierte am Desktop, aber auf dem Handy nicht: Text per Finger markieren und danach einen Button daneben antippen lässt die Selektion auf OS-Ebene kollabieren, bevor das Pinnen überhaupt greift. Kein JS-Fix möglich (siehe `feedback_stimme_diktat.md` für den vorherigen, nicht ausreichenden Anlauf mit `mousedown.preventDefault()` — der half nur bei Maus-Klicks).

Neuer Ansatz: Pin-Button zerlegt die Nachricht per Satzgrenzen-Regex in einzelne Sätze und zeigt sie als Checkbox-Liste im Modal. Jeder angehakte Satz wird als eigener Container-Eintrag gepinnt (gleicher Kommentar für alle in einem Durchgang gewählten). Kein Markieren mehr nötig, funktioniert gleich auf Touch und Maus.

Zusätzlich neuer Button „🧠+" (Sätze direkt einer Memory-Kategorie zuordnen, ohne den Umweg über die LLM-Extraktion) — selbe Checkbox-Liste, dazu ein Kategorie-Dropdown (`ueber_mich`/`wichtige_momente`/`offene_fragen`/`meinungen` — `wesen_selbst` bleibt dem Wesen vorbehalten, wie schon bei der Extraktion).

### Nachtrag 2026-07-04 (später Abend) — neues Feld "Beispiel-Dialoge"

Ausgangspunkt war eine ganz andere Frage: Daniel wollte wissen ob seine Charaktere schon mit Character.AI mithalten können. Befund beim Durchlesen aller codexium2/codexium/solarius-Charaktere: die Technik (Preamble, Ehrlichkeits-Handling, Kontinuität) ist eher voraus, aber die Charakter-*Felder* selbst sind fast überall nur 1-2 Sätze dünn (`wesen.md` oft wörtlich nur "Du bist X."). Ohne konkretes Material fällt das Modell in generische, atmosphärisch-vage "AI-Sprache" zurück (bei GluPKI beobachtet: "Ich spüre... ein Pulsieren..."). Charaktere mit konkreteren Eigenheiten (KrEaPPy, KreFsUzi) wirken beim Lesen deutlich weniger generisch.

Direkte Konsequenz: neues Feld `beispieldialoge.md` — 1-3 Beispiel-Antworten ("So klingt X"), im codexium2-Spawner-Formular nach Weltlore einsortiert, im Profil für alle Spawner nachträglich befüllbar (generische Feldliste in `wesen_profil.html`). Im System-Prompt bewusst spät platziert (kurz vor `anleitung.md`, nah an der eigentlichen Konversation) — Beispiel-Turns wirken einem LLM gegenüber stärker je näher am Ende des Prompts.

Nicht für solarius2 im Spawner-Formular ergänzt: das Formular dort ist ein einziges Freitextfeld (`anleitung.md`), Beispieldialoge lassen sich dort schon jetzt einfach mit reinschreiben — keine strukturelle Änderung nötig.

### Nachtrag 2026-07-04 (später Abend) — Budgets erhöht, Container nicht mehr session-lokal

Siehe oben im Abschnitt "Budget statt Max-pro-Kategorie" und "Was ich verstehe" für die aktuellen Werte (Memory 3333, Container 2222 Zeichen) und die Umkehr der Session-Lokalität — beides von Daniel direkt angeordnet, keine Herleitung dahinter außer "mehr Luft" bzw. "Pins sollen bleiben".

### Nachtrag 2026-07-04/05 (Nacht) — wesen_selbst bekommt endlich einen echten Schreibmechanismus

Korrektur zum Satz weiter oben ("wesen_selbst bleibt dem Wesen vorbehalten, wie schon bei der Extraktion"): das war nie ganz richtig. Beim Nachschauen (Daniel fragte direkt: "das wesen selbst nie was in memory oder container aufnehmen wollte also diese funktion fehlt entweder noch komplett oder ist komisch") stellte sich heraus: die Kategorie `wesen_selbst` existierte vollständig im UI (eigenes Label, "— vom Wesen geschrieben"-Anzeige, der manuelle Hinzufügen-Button war extra dafür versteckt) — aber es gab **keine einzige Code-Stelle**, die dem Wesen erlaubte, dort tatsächlich etwas reinzuschreiben. Ein Platzhalter, der wie eine fertige Funktion aussah, aber leer war. Genau wie die Kindersicherung (siehe `project_codexium2_testbed`-Memory).

Daniel wollte "eine Mischung" aus den zur Auswahl gestellten Optionen (Live-Marker in der Antwort vs. eigener Hintergrund-Job pro Nachricht), explizit **ohne** die teure "pro-Nachricht"-Variante — bestätigt als "ja genau bewusste rückschau". Umgesetzt als echte Mischung:

1. **Live, im Moment**: das Wesen darf am Ende einer normalen Chat-Antwort optional eine Zeile `[MERKEN: ...]` anhängen (Hinweis dazu steht im System-Prompt, ganz am Ende — stärkste Aktualität, gleiches Prinzip wie bei `letzter_abschluss.md`). Kostet keinen zusätzlichen Ollama-Call, läuft im normalen Antwort-Stream mit. Server parst den Marker nach Streamende aus `fullResponse` heraus (`extrahiereMerkenMarker`), speichert nur den bereinigten Text in `chat_history.jsonl`, schreibt den gemerkten Text separat in `wesen_selbst` (`fuegeMemoryEintraegeHinzu` — respektiert dasselbe Gesamtbudget, loggt dieselbe `memory_geaendert`-Provenienz wie der normale PUT-Weg). Client blendet alles ab dem ersten `[MERKEN:`-Vorkommen schon während des Live-Streamings aus (`sichtbarerText()`) und lässt es auch nicht vorlesen.
2. **Bewusste Rückschau am Sessionende**: der ohnehin schon existierende Memory-Extraktions-Job (läuft einmal beim manuellen "Erinnerungen ziehen" oder bei Session-Ende, nicht pro Nachricht) bekommt eine zusätzliche Anweisung im selben Prompt: kurz in die Perspektive des Wesens selbst schlüpfen und 0-3 kurze Ich-Form-Sätze für `wesen_selbst` schreiben — keine neue Anfrage, nur ein erweitertes JSON-Schema in der bestehenden. Die Skip-Zeile, die `wesen_selbst` bisher explizit von der Extraktion ausschloss, ist raus.

Getestet an einem Wegwerf-Charakter (`MerkenTest`): Modell direkt gebeten, testweise einen Marker anzuhängen — hat funktioniert, der rohe Stream enthielt ihn, aber `chat_history.jsonl`/`/history`-Endpunkt zeigten nur den bereinigten Text, `memory.json` bekam den Eintrag in `wesen_selbst`, Provenienz war korrekt. Extraktion danach lief ebenfalls durch und ergänzte `wesen_selbst` ein zweites Mal, diesmal mit einer echten introspektiven Notiz des Modells.

**Nebenbefund, nicht behoben:** der zweite Extraktions-Eintrag wurde mitten im Wort abgeschnitten ("...nur das erwartete Markierungsta"), weil die allgemeine Extraktion noch den alten harten `.slice(0, 200)` nutzt statt der neu gebauten `kuerzenAufSatzgrenze()` (siehe `provenienz_logging.md`-Nachtrag zur Abschluss-Geschichte, dort für dasselbe Problem schon gefixt). Daniel darüber informiert, nicht angefasst — kein Auftrag dafür in diesem Zug, nur der schon vorhandene, jetzt zweimal aufgetretene Bug-Typ.

### Nachtrag 2026-07-05 (Nacht) — Output-Limits entfernt: Chat, Memory-Extraktion, Container

Direkte Folge des obigen Nebenbefunds — Daniel hat gefragt, ob es noch irgendwelche Output-Limits (Zeichen/Token) für die Charaktere gibt, und "wenn ja weg damit". Nachgeschaut statt geraten, drei echte Limits gefunden (ein viertes, `num_predict:400` bei der eigentlichen Chat-Antwort, betraf keine Memory/Container-Datei, siehe `provenienz_logging.md`):

1. **Memory-Extraktion**: der `.slice(0, 200)` pro extrahiertem Fakt (genau der oben dokumentierte Nebenbefund-Bug) — jetzt entfernt, Prompt verlangt auch nicht mehr explizit "max. 200 Zeichen". `num_predict` für den Extraktions-Call von 500 auf `-1` (unlimitiert) — sonst hätte der alte Token-Deckel längere Einträge sowieso wieder abgeschnitten, egal was der Code danach macht.
2. **Container-Pin-Kommentar**: `PIN_KOMMENTAR_MAX = 88` (samt Frontend-`maxlength="88"` und "0/88"-Zähler im Pin-Modal) komplett entfernt — war ein hartes Zeichenlimit pro Kommentar, unabhängig vom Gesamtbudget.

**Bewusst NICHT angefasst:** `MEMORY_BUDGET_ZEICHEN` (3333) und `CONTAINER_BUDGET_ZEICHEN` (2222) — die Gesamtbudgets pro Charakter bleiben bestehen, Daniel hat nur die Pro-Eintrag-Limits gemeint, nicht die Summen-Obergrenze, die er selbst erst gestern Abend explizit gesetzt hat. Getestet: ein Pin-Kommentar mit über 150 Zeichen wird jetzt vollständig gespeichert (vorher wäre er bei 88 abgeschnitten worden).

### Nachtrag 2026-07-06 — Mehrere benennbare Container statt einer festen Liste (neue Entscheidung, noch nicht gebaut)

Daniel fragte nach den Containern: "irgendwann haben wir da was entfernt, ich weiß nicht wann, aber Container waren so gedacht dass ich selbst immer neue anlegen und benennen kann, egal was und wie viele." Nachgeschaut statt geraten: das stimmt nicht — weder hier noch im älteren Zwischenwesen-Konzept (`_claude/ideen/zwischenwesen/container.md`) war das jemals so gebaut oder auch nur so entworfen. Container war von Anfang an **eine einzige feste Liste pro Charakter** (Pins rein, Zeichenbudget als Deckel). Nichts wurde entfernt — das Feature "mehrere frei anlegbare, benennbare Container" hat schlicht noch nie existiert.

Daniels Klarstellung dazu (wörtlich): "deswegen heißt es ja container weil sie etwas tragen können zum packen und beschriftbar sind." Das ist also eine neue Entscheidung, keine Wiederherstellung. Ich halte sie hier fest, bevor irgendwas gebaut wird — Container-Konzept ändert sich von einer Liste zu einer Sammlung eigenständiger, vom Menschen benannter Behälter, beliebig viele.

**Offene Fragen, die vor dem Bauen mit Daniel geklärt werden müssen** (Architektur-Entscheidungen, nicht von mir allein zu treffen):
1. Ersetzt das den bisherigen einen Container komplett, oder gibt es weiterhin einen "Standard-Container" plus zusätzliche benennbare?
2. Teilen sich alle Container zusammen das bestehende `CONTAINER_BUDGET_ZEICHEN` (aktuell 5555), oder bekommt jeder neu angelegte Container sein eigenes Budget?
3. Werden beim Chat-Aufruf ALLE Container gleichzeitig in den System-Prompt gegeben, oder kann/muss der Mensch einzelne Container gezielt ein-/ausschalten (relevant fürs Kontextbudget, siehe 12_ollama_gemma4.md)?
4. UI: wo werden Container angelegt/umbenannt/gelöscht — eigenes Panel neben dem bisherigen Container-Popup in `wesen_chat.html`, oder Erweiterung des bestehenden Popups?
5. Gilt das für alle 4 Spawner (codexium/codexium2/solarius/solarius2) oder nur für die Testbed-Varianten (codexium2/solarius2), wie der Rest dieses Konzepts?

Datenstruktur-Skizze (Vorschlag, noch nicht entschieden):
```typescript
// container.json (neu, mehrere statt eine Liste)
interface ContainerSammlung {
  container: Array<{
    id: string;
    name: string;              // vom Menschen vergeben, frei
    erstellt_am: string;       // ISO
    eintraege: ContainerEintrag[]; // gleiche Struktur wie bisher (text/kommentar/quelle)
  }>;
}
```

### Nachtrag 2026-07-06 (später, noch am selben Tag) — gebaut, alle 5 Fragen geklärt

Daniels Antworten auf die 5 offenen Fragen oben: (1) komplett ersetzen, kein
Nebeneinander zweier Formate, (2) Gesamtbudget bleibt geteilt über alle
Container, (3) einzeln an-/ausschaltbar (`aktiv`-Flag, nicht immer alle aktiv),
(4) Verwaltung im Profil ("da wo sie mal waren"), einfach hinzufügbar, (5) gilt
für alle 4 Spawner, nicht nur die Testbed-Varianten.

**Gebaut wie skizziert**, mit `aktiv: boolean` pro Box ergänzt (Frage 3) und
einer Migrationsfunktion (`ladeContainerSammlung()`), die sowohl das alte
Pin-Format als auch das noch ältere Key/Val-Format (Codexium/Solarius) beim
ersten Lesen automatisch in die neue Struktur überführt — kein Datenverlust,
keine manuelle Migration nötig. Volle technische Details (Endpunkte,
Provenienz-Events, UI-Änderungen) in den Konzept-Dokumenten:
`_claude/konzepte/2026-07-06_serve_process_camera_preview.md`,
`2026-07-06_wesen_profil.md`, `2026-07-06_wesen_chat.md`.

Zusätzlich von Daniel gewünscht und umgesetzt: volle Sichtbarkeit im Chat-Verlauf
("alles muss komplett offen sein") — jede Container-Aktion (anlegen, umbenennen,
löschen, pinnen, entfernen) erscheint als lesbares Ereignis im sichtbaren
Verlauf, nicht nur als stille Provenienz-Zeile.

Live getestet gegen `solarius/KrEaPPy` (regulärer, nicht-Testbed-Charakter) —
Container anlegen, pinnen, löschen funktioniert, Testdaten danach entfernt.

### Nachtrag 2026-07-06 (später) — Zeichen-Budgets nochmal erhöht: 9999/11111/11111

Auf Daniels direkten Wunsch drei Zeichen-Budgets angehoben (`serve_process_camera_preview.ts`):

| Budget | Vorher | Jetzt |
|---|---|---|
| `ABSCHLUSS_MAX_ZEICHEN` (Abschlussgeschichte) | 4444 | **9999** |
| `MEMORY_BUDGET_ZEICHEN` | 5555 | **11111** |
| `CONTAINER_BUDGET_ZEICHEN` | 5555 | **11111** |

Client-seitige Anzeigen mitgezogen (gleiches Muster wie beim Kontext-Meter,
siehe `12_ollama_gemma4.md`): `wesen_chat.html` (`CONTAINER_BUDGET`,
`MEMORY_BUDGET`) und `wesen_profil.html` (`MEMORY_BUDGET`, `CONTAINER_BUDGET`).
`ABSCHLUSS_MAX_ZEICHEN` hat keinen Client-Mirror, nur serverseitig relevant.

`process-camera-preview.service` neu gestartet, live gegen den laufenden
Server verifiziert (beide HTML-Dateien liefern die neuen Werte aus). Kein
RAM-/Performance-Risiko — reine Zeichen-Obergrenzen für Text, keine
Modell-/Server-Konfiguration.
