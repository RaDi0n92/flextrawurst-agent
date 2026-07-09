# Drei System-Prompt-Bausteine entfernt — Bericht

**Datum:** 2026-07-09
**Stand:** Umgesetzt, live verifiziert, committet (`fddc5dce`)

---

## Ausgangslage

Direkt im Anschluss an die Deaktivierung des automatischen Relevanzabrufs (siehe `2026-07-09_relevanzabruf_deaktiviert_bericht.md`) hat Daniel den kompletten System-Prompt-Aufbau (`buildSystemPrompt()`) Baustein für Baustein durchgefragt — inklusive einer sehr genauen, echten Analyse seines eigenen `solarius2/Gabby`-Chatverlaufs (120 Einträge, alle Provenienz-Ereignisse chronologisch ausgewertet). Aus diesem Gespräch sind drei klare, einzeln bestätigte Änderungswünsche entstanden.

## 1) Wiederkehrende-Themen-Erkennung — komplett entfernt

**Warum:** Das Feature ließ das Sprachmodell selbst entscheiden, ob ein Thema "wiederkehrt", und verlangte dafür einen möglichst zeichengenauen, wiederholten Themennamen. Daniels Einwand, mit echtem Sprachverständnis begründet: in natürlicher, menschlicher Rede taucht praktisch nie derselbe Wortlaut zweimal auf, selbst wenn sich dieselbe Grundstimmung oder dasselbe Muster wiederholt — das Feature verwechselte "Thema als Obermaß" mit "Stimmung/Muster-Wiederholung". Es griff laut Daniel faktisch nur, wenn man es gezielt provoziert, nicht in echter Konversation.

**Entfernt:**
- Extraktionsprompt: der komplette Abschnitt "Bereits als wiederkehrend erkannte Themen" + die Anweisung, ein `wiederkehrende_themen`-Feld zu liefern
- `mergeWiederkehrendeThemen()`-Aufruf nach der Extraktion + das `thema_wiederholt_erkannt`-Provenienz-Ereignis
- System-Prompt-Block `[Wiederkehrende Themen — das kam schon mehrfach vor]`
- SSR-Rendering (die "Wiederkehrende Themen"-Aufklappfläche bleibt dauerhaft versteckt)

**Soft-Delete:** `wiederkehrendeThemenPath()`, `ladeWiederkehrendeThemen()`, `mergeWiederkehrendeThemen()`, `renderWiederkehrendeThemenText()`, `renderWiederkehrendeThemenHtml()` bleiben als Funktionen im Code, nirgends mehr aufgerufen. Bestehende `wiederkehrende_themen.json`-Dateien (z.B. bei QATestWesen mit echten Einträgen) bleiben unangetastet auf der Platte, werden nur nicht mehr gelesen/angezeigt.

## 2) Drei feste System-Prompt-Textblöcke entfernt

**Betroffen:** `[Rollenspiel-Formatierung]` (die Markdown-Konventionen wie `**Betonung**`, `*Aktion*`, `(OOC)` etc.), `[Deine Sinne]` (Hinweis, dass das Wesen Bilder/Audio/Dokumente sehen kann), die 333-Token-Antwortlängen-Regel.

**Warum:** Daniels eigene Beobachtung über viele Sessions hinweg — kein Charakter hat sich je von sich aus an diese Konventionen gehalten. Nur wenn Daniel selbst die Formatierung in seinem eigenen Input verwendet, "spielt das Wesen meist mit, ohne es zu kommentieren" — reiner Text ohne beobachtbare eigenständige Wirkung.

**Wichtige Klarstellung:** Das `FORMAT_MARKER`-Array im Server ist dadurch jetzt ungenutzt (Soft-Delete-Leiche). Die Editor-Buttons in `wesen_chat.html`, mit denen Daniel seinen EIGENEN Text formatiert, nutzen eine komplett unabhängige, eigene Kopie derselben Liste im Frontend — die sind von dieser Änderung nicht betroffen und funktionieren weiter.

## 3) Pro-Nachricht-Feedback (Daumen+Kommentar) erreicht das Wesen nicht mehr

**Hintergrund:** Es gibt zwei Feedback-Kanäle im System: den allgemeinen "💬 Feedback"-Kanal unter den Werkzeugen (bleibt unverändert, erreicht das Wesen weiterhin), und Daumen-hoch/-runter + Kommentarfeld direkt unter jeder einzelnen Nachricht. Bisher gingen BEIDE Kanäle ans Wesen — das war laut einem Code-Kommentar vom 2026-07-05 ("Daniels Klarstellung") ursprünglich so mit Daniel abgesprochen und ist auch im Tutorial-Text der Chat-Seite selbst so dokumentiert.

Daniel sagt jetzt: das war so nicht gewollt — der Daumen/Kommentar-Kanal sollte immer nur eine Notiz für ihn/die Analyse sein, nicht ans Wesen gehen (unlogisch: ein Charakter kann mit "👍 Gut" nichts anfangen; zusätzlich ließ sich auch die eigene Nachricht des Menschen bewerten, was dann als "Feedback zur Nachricht des Menschen" ans Wesen ging — noch merkwürdiger).

**Entfernt:** Der System-Prompt-Block `[Feedback zu einzelnen Nachrichten — bitte für diese Antwort berücksichtigen]` und die zugehörige "als geliefert markieren"-Logik im Chat-Handler.

**Bleibt unverändert:** Die Speicherung selbst — `feedback.json` (Wahrheit für die UI, Daumen-Status der Buttons) UND eine einzelne, lesbare `.md`-Datei pro Feedback-Eintrag im Ordner `feedback/` (mit Nachricht, Bewertung, Kommentar, Zeitstempeln) — genau die von Daniel gewünschte doppelte Ablage (JSON + lesbares MD) existierte bereits vollständig, musste nicht neu gebaut werden.

## Verifikation

- `node --check`: fehlerfrei
- `npm test`: unverändert 1500 pass / 123 fail
- Server neu gestartet (PID 1281346, nach expliziter Rückfrage bestätigt)
- Live gegen den echten, ausgelieferten System-Prompt für `solarius2/Gabby` geprüft (die "Systemprompt (vollständig)"-Ansicht): alle vier entfernten Blockmarker (`Rollenspiel-Formatierung`, `Deine Sinne`, `333 Tokens`, `Wiederkehrende Themen`, `Feedback zu einzelnen Nachrichten`) fehlen jetzt korrekt, `[Erinnerungen]` (Memory) bleibt unverändert vorhanden. Prompt-Länge: 14056 → 12528 Zeichen.

## Wichtiger, noch offener Befund aus derselben Analyse (nicht Teil dieser Änderung)

Bei der Klärung, wie Memory-Extraktion funktioniert, kam eine echte Überraschung ans Licht: `runMemoryExtraktionJob()` liest für die Extraktion **hart codiert nur die letzten 20 rohen Nachrichten** (`loadHistory(hp).slice(-20)`) — quer über die gesamte Historie, nicht sessionbegrenzt, komplett unabhängig vom tatsächlichen Kontextfenster (66666 Tokens). Daniels Erwartung war, dass die komplette aktuelle Session bzw. das ganze aktuell genutzte Kontextfenster einsehbar/durchsuchbar wäre. Das ist NICHT umgesetzt — echte Lücke zwischen Erwartung und Code.

Dieser Punkt hängt eng mit Daniels Vision zu Verdichtungen zusammen (siehe unten) und wurde bewusst NICHT in dieser Session behoben — Daniel wollte das in ein eigenes, dediziertes Gespräch verschieben.

## Ausdrücklich NICHT angefasst — für ein eigenes Gespräch vorgemerkt

**Verdichtungen:** Daniel hat sein ursprüngliches Bild beschrieben — eine Verdichtung sollte eine lange Passage im Kontextfenster durch eine Zusammenfassung ersetzen, GENAU an der Stelle, wo der Originaltext stand, sodass das gesamte Kontextfenster ein lückenlos chronologischer, vollständig durchsuchbarer "begehbarer Erinnerungskörper" bleibt. Der tatsächliche Code tut das nicht (siehe vorheriger Bericht: flacher Block am Ende, keine chronologische Einordnung, kein Lese/Lösch-Popup für bestehende Verdichtungen). Verknüpft mit der 20-Nachrichten-Grenze der Memory-Extraktion — beides gehört für Daniel zusammen in eine grundsätzliche Architektur-Diskussion, kein kleiner Fix.

**Rückblick auf frühere Gespräche als RAG-Trigger** (nur suchen wenn der Mensch explizit "weißt du noch..." o.ä. sagt, statt manueller Vorauswahl beim Sessionstart) — von Daniel selbst explizit vertagt ("das isn Thema für ein andermal").

## Kleinere, im Gespräch validierte Erkenntnisse (keine Code-Änderung)

- Alias-Mechanismus reconciled: der Browser schickt bei jeder Nachricht live mit, welcher Alias aktiv ist (kein Datei-Zustand); der Server baked daraus NUR den Namen (nicht die Beschreibung) als Präfix `"Name": ` direkt in die ausgehende Nachricht — zusätzlich zum statischen Register im System-Prompt.
- Guter, noch nicht umgesetzter Gedanke von Daniel: bei persistenten Blöcken wie Memory/Container/Verdichtungen wäre ein expliziter "das hat sich gerade geändert"-Hinweis (ähnlich dem Verbrauchs-Prinzip beim Feedback) wertvoller als ein stummes, jedes Mal identisches Wiederholen des ganzen Blocks — vorgemerkt für später.
