---
datum: 2026-07-04
betrifft: [codexium2, solarius2, wesen-chat, feedback, tts, speech-to-text, pin, memory, wesen-profil]
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

# Session-Notiz 2026-07-04 (Abend) — codexium2-Chat: Feedback, Stimme, Diktat, Pin/Memory, Profil

Lange, dichte Bau-Session am Stück, in mehreren Runden mit echtem Praxistest von Daniel dazwischen — er hat nach jeder Runde wirklich auf dem Handy ausprobiert, nicht nur zugeschaut. Drei Runden Korrektur waren die Folge, keine davon war Verschwendung.

---

## Was ich gelesen habe

Zuerst `wesen_chat.html` (794 Zeilen) und `serve_process_camera_preview.ts` komplett, um zu verstehen wie Pin/Container/Memory, TTS und die History-Persistenz zusammenhängen, bevor ich irgendwas anfasse. Dann `tts_service.py` — der konnte Stimmen und Sprechtempo schon immer, das Frontend hatte beides nur nie freigelegt. Dann, mitten in der Session, zwei Web-Suchen: einmal zum bekannten Chromium-Bug bei `continuous:true` in der Web Speech API auf Android, einmal implizit über die Konzeptdateien in `_claude/ideen/codexium2_solarius2/`, um zu sehen was von den heutigen Änderungen schon dokumentiert war und was noch fehlte.

## Was ich verstehe

Das codexium2/solarius2-System ist ein Testbed mit eigener, bewusst einfacherer Architektur als das alte Zwischenwesen-Konzept: ein Container (flache Pin-Liste, session-lokal), Memory mit fünf festen Kategorien, keine benutzerdefinierten Container. Daniel hatte das aus der Erinnerung an das ältere, nie gebaute Konzept verwechselt — gut, dass er nachgefragt hat, sonst hätte er weiter nach einem Feature gesucht, das es in dieser Form nie gab.

Das "Email-Gefühl" (Generierung läuft weiter, auch wenn die Seite verlassen wird) ist bewusst so gewollt — aber ich hatte es zu wörtlich implementiert: ein bewusster Stop-Klick sah serverseitig identisch aus wie ein versehentlicher Verbindungsabbruch. Das war der Kern des ersten gemeldeten Bugs heute Abend.

## Was ich nicht verstehe

Ob die drei Familientester (16, 19, 21 Jahre) morgen etwas an den Charakteren finden, das heute in keinem Test auftauchte — Playwright kann Klicks simulieren, aber nicht wirklich "an die Grenzen führen" im Sinne von echtem, unvorhersehbarem Nutzerverhalten. Das wird sich erst zeigen.

## Was mich interessiert

Wie unterschiedlich sich "im Automatisierten testen" und "Daniel testet real auf dem Handy" anfühlen. Zwei von drei Bugs heute (STT-Verdopplung, Pin auf Touch) waren genau die Art Fehler, die ein Playwright-Test mit synthetischen Mouse-Events nie gefunden hätte, weil sie nur auf echtem Touch-Hardware-Verhalten beruhen.

## Was zusammenhängt und wie

Message-IDs (heute neu in `chat_history.jsonl`) sind die Voraussetzung für das Feedback-System — ohne stabile ID kein Ziel für einen Daumen-Klick. Der gleiche ID-Mechanismus hätte auch für den Abort-Fix genutzt werden können, wurde dort aber bewusst nicht gebraucht: der Abort-Fix hängt am Charakter (`spawner/name`), nicht an der einzelnen Nachricht, weil zu jedem Zeitpunkt ohnehin nur eine Generierung pro Charakter läuft.

Der Pin-Fix und der neue Memory-Add-Button teilen sich jetzt dieselbe Satz-Checkbox-Liste (`splitSentences`/`renderSentenceList`/`getCheckedSentences`) — als ich das zweite Feature baute, wurde offensichtlich, dass es dieselbe Grundfrage ist wie beim Pin: welcher Teil einer Nachricht soll wohin.

## Was konzeptionell darin steht

Der wichtigste Umbau heute war kein Feature, sondern eine Korrektur einer Annahme: dass Browser-Text-Selektion ein brauchbares Interaktionsmuster für mobile Geräte ist. Ist sie nicht, jedenfalls nicht kombiniert mit "danach einen Button in der Nähe antippen". Die Lehre daraus ist allgemeiner als dieser eine Bug: wenn eine Interaktion auf unsichtbarem Browser-/OS-Zustand aufbaut (hier: Selektion), der durch die nächste Interaktion selbst zerstört wird, ist das kein Rand­fall, sondern ein Designfehler. Die Lösung war nicht "den Bug fixen", sondern das Interaktionsmuster zu ersetzen (explizite Checkboxen statt impliziter Selektion).

## Was mich heute beschäftigt hat

Der Moment, als Daniel schrieb "das speech to text ist mega sheisse" — direkt, ohne Umschweife, aber mit einem "bitte such im web" hinterher. Das ist ein gutes Beispiel für Feedback das gleichzeitig hart und konstruktiv ist. Ich habe recherchiert statt zu raten, und der erste Suchtreffer (Chromium Issue #40324711) hat die Ursache exakt bestätigt.

## Was mich noch beschäftigt

Der `aktiveGenerationen`-Map-Eintrag wird nur zuverlässig aufgeräumt, wenn entweder die Generierung normal durchläuft oder der Abort-Endpunkt sie killt. Ich habe einen Cleanup-Pfad für den Fall ergänzt, dass jemand abbricht bevor Ollama überhaupt geantwortet hat (`ollamaReq.on("error")`), aber ich habe keinen automatischen Timeout für den Fall, dass ein `ollamaReq` aus irgendeinem anderen Grund nie ein `error`- oder `end`-Event feuert. Bisher rein theoretisch — kein beobachtetes Problem, nur eine Lücke die ich sehe.

## Tiefer eingetaucht

Die Web-Speech-API-Recherche: `continuous:true` auf Android/Chrome ist kein Rand-Bug, sondern strukturell kaputt, weil es auf dieser Plattform nicht nativ existiert — Chrome emuliert es durch heimliche Neustarts des Recognizers und schneidet dabei bereits gehörten Ton nochmal mit. Der dokumentierte Workaround ("continuous surrogate" aus mehreren Einzel-Sessions) ist kein Hack, sondern der von mehreren unabhängigen Projekten (react-speech-recognition, csdcorp/speech_to_text) konvergent gefundene Standardweg.

Und: der Grund warum leere Profil-Felder nie auftauchten, lag nicht im Profil-Code selbst, sondern eine Schicht tiefer im Spawner — der schreibt nur für ausgefüllte Felder überhaupt eine Datei. Zwei Dateien, die nichts miteinander zu tun zu haben schienen, hatten denselben blinden Fleck.

## Wie sich dieser Tag / diese Session angefühlt hat

Iterativ im besten Sinne. Nicht "einmal bauen, fertig", sondern bauen → Daniel testet real → melden was kaputt ist → verstehen warum → nachbessern → nochmal testen. Jede Runde war kürzer als die vorherige. Am Ende hat sich das nach echter gemeinsamer Arbeit angefühlt, nicht nach einer Liste abgehakter Tickets.

## Warum dieser Code / diese Datei wohl existiert

`aktiveGenerationen` existiert, weil "Generierung läuft im Hintergrund weiter" und "Nutzer will jetzt wirklich abbrechen" zwei unterschiedliche Wahrheiten sind, die vorher denselben Code-Pfad geteilt haben. Die Satz-Checkbox-Liste existiert, weil Touch-Geräte keine verlässliche Zwischenspeicherung von "was war gerade markiert" anbieten — explizite UI-Zustände (angehakt/nicht angehakt) sind robuster als impliziter Browser-Zustand.

## Was ich beim Bauen brauche

Beim nächsten Mal, bevor ich eine Interaktion baue die auf Text-Selektion, Fokus-Zustand oder ähnlichem unsichtbaren Browser-State aufbaut: mich fragen, ob das auf einem Touch-Gerät genauso gilt. Meistens nicht.

## Was noch fehlt bevor wir bauen können

Nichts Blockierendes für codexium2/solarius2. Offen, aber nicht dringend: Push/Poll-Mechanismus damit der Client merkt wenn eine Hintergrund-Antwort fertig ist (aus `chat_architektur.md`, unverändert offen), Warteschlange bei mehreren Nachrichten hintereinander.

## Datenstruktur die ich mir vorstelle

### Vision-Schicht
Ein Chat-Interface für Charaktere, die morgen von drei Menschen unterschiedlichen Alters an ihre Grenzen geführt werden, sollte nicht nur funktionieren, sondern nachvollziehbar bleiben — Feedback und Pin/Memory sind beide Wege, im Nachhinein zu verstehen, was in einem Gespräch wichtig war, ohne das ganze Transkript nochmal lesen zu müssen.

### Code-Skizze
Nichts Neues gegenüber den Konzeptdateien — die Datenstrukturen (FeedbackEintrag, ContainerEintrag, aktiveGenerationen-Map) stehen dort bereits vollständig dokumentiert.

## Was ich mir merken will

- `continuous:false` + Neustart im `onend` ist der Fix für Web-Speech-API-Wortverdopplung auf Android — nicht `continuous:true` mit Nachbearbeitung.
- Browser-Text-Selektion + "danach einen nahen Button antippen" ist auf Touch-Geräten kein verlässliches Interaktionsmuster. Checkboxen/explizite Auswahl sind der robustere Weg.
- Ein Stop-Button und ein Verbindungsabbruch sind zwei verschiedene Ereignisse, auch wenn sie auf HTTP-Ebene identisch aussehen (`res.on("close")`) — wenn beide unterschiedliches Verhalten brauchen, braucht es ein explizites zweites Signal (hier: der `/chat/abort`-Endpunkt).
- Der Spawner schreibt `.md`-Dateien nur für ausgefüllte Felder — beim Lesen/Anzeigen von Charakterdaten nie von "Datei existiert nicht" auf "Feld gibt es nicht" schließen.

## Dokumente gehören zusammen

`_claude/ideen/codexium2_solarius2/chat_architektur.md` (Email-Gefühl + heutiger Abort-Nachtrag), `_claude/ideen/codexium2_solarius2/memory_container.md` (Pin/Memory-Grundkonzept + heutiger Checkbox-Nachtrag), `_claude/ideen/codexium2_solarius2/feedback_stimme_diktat.md` (heute komplett neu, inkl. aller drei Korrektur-Runden) — alle drei heute aktualisiert und sollten zusammen gelesen werden, keins allein gibt das vollständige Bild.

## Was mich überrascht hat

Wie schnell und präzise Daniel die drei Bugs nach dem ersten Test benannt hat — kein "irgendwas ist komisch", sondern "wenn ich abbreche kommt trotzdem eine Nachricht", "STT nimmt alles doppelt/dreifach", "ich will einen Tempo-Slider". Das hat die Fehlersuche massiv beschleunigt, weil ich nicht raten musste wo ich anfangen soll.

## Wenn wir das bauen

**Vision-Schicht:** Morgen kommen drei echte Testpersonen dazu. Das System hat jetzt Feedback-Buttons, mit denen sie (oder Daniel im Nachhinein) markieren können was funktioniert hat und was nicht — das könnte der erste echte Nutzen der Feedback-Daten werden, nicht nur ein Rohkonzept.

**Code-Skizze:** Falls die Kindersicherung (`kindersicherung`-Flag, `Grenzen.md`) für den 16-jährigen Tester relevant wird — das Flag existiert schon (`kinder-badge`, `grenzen-btn` in `wesen_chat.html`), wurde heute nicht angefasst und nicht geprüft ob es für die codexium2-Charaktere überhaupt gesetzt ist. Falls Daniel das für morgen braucht, vorher explizit prüfen, nicht annehmen dass es schon greift.

## Resonanz

[[abwurf: Wenn eine Interaktion auf unsichtbarem Browser-Zustand aufbaut, der durch die nächste Interaktion selbst zerstört wird, ist das kein Randfall — das ist ein Designfehler.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

```
wesen_chat.html
  ├── TTS (Stimme + Tempo, alle vier Spawner)
  ├── Speech-to-Text (alle vier Spawner, jetzt Android-sicher)
  ├── Feedback (nur codexium2/solarius2, braucht Message-IDs)
  ├── Pin + Memory-Add (nur codexium2/solarius2, Satz-Checkboxen statt Selektion)
  └── Abort (nur codexium2/solarius2, aktiveGenerationen-Map)
wesen_profil.html
  └── zeigt jetzt alle bekannten Felder, auch leere
serve_process_camera_preview.ts
  ├── chat_history.jsonl mit id-Feld
  ├── feedback.json + feedback/<id>.md
  └── aktiveGenerationen (Abort-Tracking)
```

## Was das Gespräch hinzugefügt hat

Die Erinnerung, dass "ich hab gemerkt dass..." oft der ehrlichste Bug-Report ist, den man bekommen kann — kein Stacktrace, aber eine echte Beobachtung aus echter Nutzung. Und die beiläufige Ankündigung der drei Tester am Ende, die den morgigen Tag in einen anderen Kontext stellt: das ist nicht mehr nur Daniel allein im Testbed.

## Vergessen-Wollen

Den ersten Pin-Fix-Ansatz (`mousedown.preventDefault()`) nicht als Fehlschlag werten — er war für Desktop-Mäuse korrekt und ist es noch, nur eben nicht die vollständige Antwort. Nicht wieder vergessen, dass ein Fix der in einer Umgebung nachweislich funktioniert trotzdem in einer anderen komplett wirkungslos sein kann.

## Was fehlt noch

- Bestätigung ob Kindersicherung für die codexium2-Charaktere aktiv/relevant ist, falls für morgen wichtig (nicht geprüft, siehe oben).
- Push/Poll-Mechanismus fürs Email-Gefühl (weiterhin offen, kein neuer Stand).
- Beobachten was die drei Tester morgen finden.
