---
name: codexium2-solarius2-provenienz-logging
description: Vollständiges Event-Logging aller Charakter-Aktionen in chat_history.jsonl — Chat, Feedback, Pin, Memory, Profil-Edits, Abbrüche
metadata:
  type: project
tags: [codexium2, solarius2, provenienz, logging, testbed]
status: gebaut
datum: 2026-07-04
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Scope

Nur codexium2/solarius2 (siehe `project_codexium2_testbed`). Auftrag von Daniel wörtlich: "ich will dass alles jedes kleinste Detail wie bei dem Mischpult auch geloggt wird im chat und in der verlaufsdatei. jeder memoryeintrag jede änderung im profil alles."

Referenz ist die Dolphin-Mischpult-Provenienz-Session vom 24.06. (`_claude/notizen/2026-06-24-*.md` bzw. Claude-Memory dazu): "Ein Gespräch ist eine Handlung in der Zeit. Jede Handlung hinterlässt eine Spur... 'vollständig' bedeutet nicht nur Text — es bedeutet: wann, womit, unter welchen Bedingungen, mit welchem Feedback." Gleiches Prinzip jetzt auf codexium2/solarius2 übertragen.

---

## Was ich verstehe

`chat_history.jsonl` ist jetzt nicht mehr nur ein Nachrichtenverlauf, sondern die vollständige Akte eines Charakters. Jede Aktion — nicht nur Chat — landet als eigene Event-Zeile mit `type`-Feld in derselben Datei, nach demselben Muster wie der schon vorher bestehende `session_start`-Marker. `loadHistory`/`loadCurrentSessionHistory` filtern beim Laden für Ollama automatisch auf Zeilen mit `role`+`content` — Event-Zeilen ohne diese Felder werden also nie in den Modell-Kontext geladen, verschmutzen ihn nicht, sind aber beim Rohlesen der Datei alle da.

---

## Event-Typen (alle: `{type, ts, ...}`)

| type | wann | Felder |
|---|---|---|
| `role: "assistant"` (kein `type`) | jede Wesen-Antwort | zusätzlich zu content/id: `model`, `grenzen` (bool), `dauer_ms` |
| `feedback` | Daumen/Kommentar gesetzt | `msgId`, `rolle`, `rating?`, `kommentar?` (nur die tatsächlich geänderten Felder) |
| `pin_hinzugefuegt` | Pin gesetzt | `eintrag` (voller ContainerEintrag) |
| `pin_entfernt` | Pin entfernt | `eintrag` (der entfernte, vollständig) |
| `memory_geaendert` | PUT auf `/memory` mit tatsächlicher Änderung | `diffs`: Array `{kategorie, hinzugefuegt[], entfernt[]}` — deckt manuelle Edits, den 🧠+-Button UND das Ergebnis der Extraktion ab (alle laufen über denselben PUT-Endpunkt) |
| `memory_extraktion` | Extraktionslauf fertig, wenn etwas passiert ist | `hinzugefuegt` (Zahl), `verworfen` (Zahl, Budget voll), `texte`: welche Texte in welche Kategorie |
| `profil_feld_geaendert` | `.md`-Datei gespeichert (Profil oder wesen.md) | `datei`, `vorher` (voller Inhalt), `nachher` (voller Inhalt) |
| `profil_feld_geloescht` | `.md`-Datei gelöscht | `datei`, `vorher` |
| `generierung_abgebrochen` | Stop-Klick killt eine laufende Generierung wirklich | `msgId` (= die verworfene Antwort) |
| `kontext_toggle` | Nachricht/Satz aus dem Kontextfenster genommen/wieder reingenommen | `msgId`, `ganz` (bool), `saetze` (number[]) |
| `abschluss_uebernommen` | Entwurf der Abschluss-Geschichte übernommen | `vorher` (voller alter Inhalt von `letzter_abschluss.md`, meist leer), `nachher` (voller neuer Text) |
| `session_start` | bereits vorher bestehend | `ts` |

---

## Was mich heute beschäftigt hat

Der Abort-Fall war der einzige nicht-triviale: mein erster Versuch hat das Logging in `saveResponse()` bzw. im `ollamaReq.on("error")`-Handler eingebaut — beides Stellen die beim Abbrechen *während* des Streamens laut meiner Einschätzung eventuell nie feuern (`ollamaReq.destroy()` ohne Error-Argument löst wahrscheinlich weder ein `error`-Event auf dem Request noch ein sauberes `end` auf der Response aus). Korrektur: das Logging passiert jetzt ausschließlich direkt im `/chat/abort`-Handler selbst, an der einzigen Stelle die garantiert erreicht wird, sobald der Nutzer wirklich klickt — nicht abhängig von unsicheren Node-Stream-Events danach.

## Was ich nicht verstehe

Ob `profil_feld_geaendert` mit vollem Vorher/Nachher-Inhalt bei sehr häufigen kleinen Edits (z.B. jemand tippt und speichert oft) die Datei unnötig aufbläht. Aktuell kein Problem (Felder sind kurz, max. 1337 Zeichen), aber falls `chat_history.jsonl` mal sehr groß wird, wäre das eine Stelle zum Nachschauen.

---

## Umsetzung (2026-07-04, alle sieben Event-Typen gebaut + getestet)

- `appendProvenienz(hp, typ, daten)` — genereller Event-Append-Helper, neben dem bestehenden `appendHistory`.
- `appendHistory` um optionalen `extra`-Parameter erweitert (fürs Anhängen von `model`/`grenzen`/`dauer_ms` an Chat-Nachrichten).
- `aktiveGenerationen`-Map um `hp` und `replyMsgId` erweitert, damit der Abort-Handler direkt loggen kann ohne durch den Streaming-Closure zu müssen.
- Getestet an einem eigens angelegten Wegwerf-Charakter (`ProvenienzTest`, codexium2) — alle sieben Event-Typen ausgelöst, geprüft, Charakter danach komplett gelöscht. Kein Testdaten-Rückstand.

## Was fehlt noch

Keine offenen Punkte aus dem Auftrag. Nicht gebaut, weil nicht verlangt: eine UI die diese Events sichtbar rendert (der Auftrag war die Verlaufsdatei, nicht die Chat-Oberfläche) — falls Daniel das später will, ist die Datenbasis jetzt vollständig da.

---

## Nachtrag 2026-07-04 (Abend) — Nachrichten ganz/satzweise aus dem Kontextfenster nehmen

Direkte Folgeanfrage: "wie im Mischpult" sollte man jede Nachricht aus dem Kontextfenster entfernen können — "noch krasser": beim Antippen einer Nachricht auch satzweise. Wichtiger Unterschied zum Mischpult-Vorbild: dort gibt es nur einen einzigen Cutoff-Index (`ctxStart`, alles davor pauschal archiviert). Hier wollte Daniel gezieltes Ein-/Ausschließen einzelner Nachrichten und sogar einzelner Sätze darin — eine feinere Granularität.

**Bewusste Entscheidung: nichts löschen.** Das stünde im Widerspruch zum gerade gebauten Provenienz-Prinzip (siehe oben). Stattdessen: ein neuer Event-Typ `kontext_toggle` (`msgId`, `ganz`, `saetze: number[]`) — die Nachricht bleibt vollständig und für immer in `chat_history.jsonl`, nur ob sie beim nächsten Prompt an Ollama mitgeschickt wird, ändert sich. Mehrfaches Toggeln erzeugt mehrere Events, letzter gewinnt — auch das Umschalten selbst ist Provenienz (wer hat wann was wieder reingenommen).

**Satz-Zählung serverseitig neu implementiert** (`splitSentencesServer`) statt der Chat-History-Zeile direkt zu vertrauen — muss exakt dieselbe Regex sein wie `splitSentences()` im Client, sonst zeigt das Modal andere Satzgrenzen als das was der Server tatsächlich rausfiltert. Beide Stellen kommentiert aufeinander verwiesen, falls die Regex mal geändert wird.

**Verifikation ohne Ollama abzuwarten:** statt auf eine echte (oft minutenlange) Modellantwort zu warten um zu sehen was ankam, kurz eine Debug-Log-Zeile eingebaut (`DEBUG_KTX`-Env-Var), Server manuell mit der Variable gestartet, echten Request geschickt, im Log exakt gesehen was an Ollama gegangen wäre (ganze Nachricht fehlte, ein Satz aus einer anderen fehlte, Rest intakt), Debug-Zeile wieder entfernt. Schneller und eindeutiger als auf eine Modellantwort zu warten und daraus zu raten ob sie das Ausgeschlossene "gewusst" hat.

### Umsetzung

- Backend: `splitSentencesServer`, `ladeKontextAusschluesse` (scannt alle `kontext_toggle`-Events, letzter pro msgId gewinnt), `wendeKontextAusschlussAn` (Filterlogik), neuer Endpunkt `POST .../kontext-ausschluss`, `GET .../history` liefert `ausschluesse`-Map mit.
- Frontend: neuer "✂️"-Button pro Nachricht, Modal mit "ganze Nachricht"-Checkbox + Satz-Checkliste (wiederverwendet `renderSentenceList`/`getCheckedSentences` aus dem Pin-Feature), visuelle Markierung (durchgestrichen bei Vollausschluss, Badge bei Teilausschluss), ctx-Meter zieht Ausgeschlossenes ab.
- Getestet: Backend-Filterlogik direkt am tatsächlich gesendeten Payload verifiziert, UI-Fluss (Button → Modal → Satz abwählen → Badge erscheint) per Playwright — beide an Wegwerf-Testcharakteren, danach gelöscht.

### Nachtrag — Listen-Zugang (wie ursprünglich gemeint)

Der ✂️-Button pro Bubble war meine erste Interpretation. Daniel meinte es näher am Mischpult-Vorbild: eine eigene Übersicht (wie Container/Memory/Sessions), die alle Nachrichten der Session als **111-Zeichen-Vorschau** in einer Liste zeigt, antippen öffnet dann die Satzauswahl. Neuer Header-Button "🗒️ Kontext" macht genau das — ruft für die angeklickte Zeile dieselbe `openKtxModal()` auf wie der Bubble-Button, keine doppelte Logik. Beide Zugänge bleiben nebeneinander bestehen (Bubble-Button für "gerade diese eine Nachricht", Liste für "ganze Session auf einen Blick durchgehen").

### Nachtrag — Checkbox-Richtung umgedreht + Live-Vorschau

Zwei Korrekturen nach dem ersten Test: (1) die Checkboxen waren mit "angehakt = bleibt drin" vorbelegt — Daniel wollte das Gegenteil, "angehakt = wird rausgeworfen", Default also überall unangehakt. Eigene Optik (roter Rahmen, durchgestrichener Text) nur im Kontext-Modal, damit die Umkehrung gegenüber Pin/Memory-Add (dort bleibt "angehakt = ausgewählt") nicht verwechselt wird. (2) Wie im Mischpult sollte man sofort sehen, wie viel Kontext eine Auswahl freigibt — nicht erst nach dem Speichern. Löst das über einen `preview`-Parameter in `updateCtxMeter()`: solange das Modal offen ist, rechnet der ganz normale Header-Zähler den gerade angehakten (noch ungespeicherten) Stand für die eine offene Nachricht sofort mit ein, zusätzlich eine eigene Zeile im Modal mit der Zeichen-Differenz in Klartext.

### Nachtrag — 77%-Kontext-Warnung

Direkter Folgeauftrag beim Durchgehen des ctx-Meters: "mach es ab 77% und nur als hinweis auf qualitätsverlust durch rausfallen kompletter nachrichten usw" — explizit kein Vorschlag was zu tun ist (keine "Neue Session jetzt!"-Aufforderung), nur eine reine Information. Umgesetzt in `updateCtxMeter()`: ab `geschaetzeTokens/8192 >= 0.77` bekommt `#ctx-meter` die Klasse `.ctx-warn` (gelb, fett) plus ein `⚠️ wird knapp` im Text und einen erklärenden `title`-Tooltip. Keine Ampelfarben darunter (rot/grün) — das war im ursprünglichen Konzept bewusst gegen das Mischpult-Vorbild entschieden, hier bewusst beibehalten: nur ein einziger Schwellwert, eine einzige Warnfarbe.

## Nachtrag 2026-07-04 (spät) — Abschluss-Geschichte (erzählerischer Rückblick, sessionübergreifend)

Direkter Folgeauftrag, im selben Atemzug wie die 77%-Warnung: "ich will immer die möglichkeit diese 'geschichte'... auch immer zwischendurch generieren zu lassen und dann zu lesen und sie entwerder wider zu verwerfen oder dann als schönen abschluss zu wählen der dann mitrüber genommen wird in neue [Session]". Auf Nachfrage (AskUserQuestion) zum genauen Übertragungsmechanismus hat Daniel sich für "eigenes Feld im System-Prompt" entschieden — keine Vermischung mit Memory/Container, ein eigenständiges, jederzeit ersetzbares Feld.

### Was ich verstehe

Das ist konzeptionell etwas anderes als Memory/Container (die sammeln einzelne Fakten/Sätze) — die Abschluss-Geschichte ist ein einziger zusammenhängender, erzählerischer Text, geschrieben aus der Perspektive/im Ton des Wesens selbst, der bewusst nicht kategorisch ist. Sie ersetzt sich selbst komplett bei jeder neuen Übernahme (keine Historie mehrerer alter Abschlüsse im Prompt — nur der jeweils letzte zählt), aber die alte Version geht nicht verloren: sie steht vollständig im `abschluss_uebernommen`-Provenienz-Event (`vorher`).

### Umsetzung

- Backend: `ABSCHLUSS_MAX_ZEICHEN = 1337`. `runAbschlussJob()` lädt den aktuellen Session-Verlauf (`loadCurrentSessionHistory`), baut daraus (plus dem bisherigen `letzter_abschluss.md`, falls vorhanden, für thematische Kontinuität) einen Prompt an Ollama, schreibt das Ergebnis in einen Status-File `abschluss_entwurf.json` (`laeuft`/`fertig`/`fehler`) — exakt dasselbe Async-Job-Muster wie `runMemoryExtraktionJob`, damit kein Doppelstart möglich ist.
- Drei Endpunkte: `GET .../abschluss/status` (liefert Job-Status plus den aktuell *übernommenen* Abschluss separat als `aktueller_abschluss`), `POST .../abschluss/generieren` (startet Job, 409 wenn schon läuft), `POST .../abschluss/uebernehmen` (schreibt `letzter_abschluss.md`, loggt Provenienz mit vollem vorher/nachher).
- `letzter_abschluss.md` in `MD_ORDER` ganz ans Ende gesetzt (nach `anleitung.md`) — von allen System-Prompt-Feldern das mit der stärksten Aktualität, soll zuletzt gelesen werden.
- Frontend: neuer Header-Button "📖 Abschluss" (jederzeit verfügbar, nicht ans Sessionende gebunden — genau wie gewünscht: "auch immer zwischendurch"). Modal zeigt den aktuell übernommenen Abschluss (falls vorhanden) plus einen Bereich für einen neuen Entwurf. "Geschichte generieren" startet den Job und pollt den Status alle 3 Sekunden nach, solange `laeuft` — ist das Modal geschlossen, wird der Timer gestoppt (kein Hintergrund-Polling ohne sichtbares Modal). Ist der Entwurf fertig: "Verwerfen" oder "Als Abschluss übernehmen" (schreibt ihn dauerhaft) — siehe Korrektur unten zum ersten Verwerfen-Bug.
- Getestet End-to-End an einem Wegwerf-Charakter (`AbschlussTest`, codexium2): echtes Gespräch geführt, Geschichte generiert (dauerte ca. 45s auf dem CPU-only-VPS mit dem 35B-Modell), übernommen, `letzter_abschluss.md` und Provenienz-Event geprüft, dann `POST .../session/beenden` ausgelöst und eine neue Nachricht geschickt — das Wesen hat sich korrekt auf das vorherige Gespräch bezogen ("Wir sprachen über Stille... Wanderungen im Wald..."), obwohl die eigentliche Chat-History der alten Session nicht mehr im aktiven Kontext war. Charakter danach komplett gelöscht, kein Testdaten-Rückstand.

### Was fehlt noch

Nichts Blockierendes. Offen, kein Auftrag: was passiert bei sehr langen Sessions, wenn `loadCurrentSessionHistory` selbst schon so groß ist, dass sie das 8192-Kontextfenster für den Abschluss-Prompt sprengt (aktuell keine Kürzung eingebaut, nur der *Output* ist auf 1337 Zeichen begrenzt) — bisher in der Praxis nicht aufgetreten, da Sessions meist deutlich kürzer sind.

### Nachtrag — drei Bugs direkt nach dem ersten echten Testlauf

Daniel hat unmittelbar nach dem ersten Test drei Dinge gemeldet, alle noch am selben Abend behoben:

1. **Satzabbruch mitten im Wort.** Der erste echte Entwurf endete mit "...bleibt als warmer Funken in" — abgeschnitten. Ursache: `.slice(0, ABSCHLUSS_MAX_ZEICHEN)` auf die rohe Modellantwort, obwohl der Prompt dem Modell zwar "maximal 1337 Zeichen" mitgibt, sich Modelle aber erfahrungsgemäß selten exakt an eine Zeichen-Vorgabe halten (sie zählen keine Zeichen, sie generieren Token). Ergebnis war oft deutlich länger als 1337 Zeichen, der blinde Schnitt landete dann mitten im Satz. Fix: neue Funktion `kuerzenAufSatzgrenze(text, maxZeichen)` — nutzt die schon vorhandene `splitSentencesServer()`-Satzerkennung, hängt Sätze an bis das nächste den Rahmen sprengen würde, und hört dort auf. Getestet: zweiter Testlauf produzierte 1236 Zeichen, endete sauber mit einem Punkt.
2. **Verwerfen wirkte nicht dauerhaft.** Klick auf "Verwerfen" blendete den Entwurf im Frontend aus, aber die Status-Datei `abschluss_entwurf.json` blieb unverändert auf der Platte liegen — beim nächsten Öffnen des Popups tauchte derselbe, bereits abgelehnte Entwurf wieder auf. Grund: die ursprüngliche Annahme "Verwerfen braucht keinen eigenen Endpunkt, der Entwurf bleibt einfach unübernommen liegen" war falsch, weil der GET-Status-Endpunkt genau diese liegen gebliebene Datei als aktuellen Stand zurückgibt. Fix: neuer Endpunkt `POST .../abschluss/verwerfen` löscht die Status-Datei tatsächlich; kein Provenienz-Event dafür (der Entwurf hat nie ein persistiertes Feld berührt, es gibt also nichts, dessen Verschwinden dokumentiert werden müsste).
3. **Mobile UI.** Zwei getrennte Probleme im Abschluss-Modal auf schmalen Bildschirmen: (a) `.modal-btns` hatte kein `flex-wrap` — bei vier Buttons ("Generieren", "Verwerfen", "Übernehmen", "Schließen") liefen die Beschriftungen aus dem Modal statt umzubrechen (betrifft potenziell auch künftige Modals mit vielen Buttons, jetzt generell gefixt). (b) die Abschluss-Textboxen (aktueller Abschluss + neuer Entwurf) nutzten aus Versehen `testbed-list` statt der bereits im Code vorhandenen `.modal-text-preview`-Klasse — dadurch zu große Schrift ohne Höhenbegrenzung, während lange Rückblicktexte gerade auf Mobilgeräten viel vertikalen Platz brauchen. Fix: beide Boxen nutzen jetzt `.modal-text-preview` (0.8rem, `max-height:140px` mit eigenem Scroll). Verifiziert per Playwright bei 375×667px (iPhone-SE-Breite): kein horizontaler Overflow mehr, Buttons brechen sauber in zwei Reihen um, `modalBoxScrollHeight === modalBoxClientHeight` (kein Modal-internes Vertikal-Overflow mehr nötig bei normaler Entwurfslänge).

### Nachtrag 2026-07-04/05 (Nacht) — "Flachheit" bei ~6000/8192 Kontext, Anker-Anweisung, Neue-Session-Hinweise

Daniel berichtete nach einem echten längeren Testgespräch (~6000/8192 Kontext gefüllt): sowohl Memory-Extraktion als auch Abschluss-Geschichte dauerten auf dem CPU-only-VPS ca. 4 Minuten (erwartbar — Prefill skaliert mit Kontextlänge, kein Bug) UND beide Ergebnisse wirkten "etwas flach". Diagnose: beide Prompts zwingen zu harter Kompression (Memory: max. 200 Zeichen pro Fakt; Abschluss: max. 1337 Zeichen für einen ganzen langen Verlauf) ohne das Modell anzuweisen, sich an etwas Konkretem festzuhalten — dasselbe Muster wie bei der Character.AI-Vergleichsanalyse (dünnes Material → generische, austauschbare Sprache).

Fix (nur für die Abschluss-Geschichte, das war der explizite Wunsch — "für deine Geschichte sollte das zumindest selbst nochmal versucht werden dort wenigstens anker zu finden die es selbst berühren"): der Prompt verlangt jetzt zuerst, mindestens einen konkreten, das Wesen selbst berührenden Moment/Detail aus dem Gespräch zu finden und den Rückblick daran zu verankern, statt allgemein zusammenzufassen. Memory-Extraktion bewusst nicht angefasst (kein Auftrag dafür, die 200-Zeichen-Kürze ist dort ohnehin gewollt kurz/faktenartig, nicht erzählerisch).

Zusätzlich zwei neue, permanente Hinweise im "Neue Session starten?"-Dialog (der vorher sowieso schon eine veraltete Aussage enthielt — "Container wird geleert", obwohl Container seit dem Vorabend persistiert; korrigiert):
- Immer sichtbar: Erinnerung, dass man vor dem Beenden selbst noch Wichtiges ins Memory oder den Container aufnehmen kann, für Kontinuität über die Session hinaus.
- Bedingt sichtbar (nur wenn `aktueller_abschluss` leer ist): Hinweis, dass man vor dem Beenden noch eine Abschluss-Geschichte generieren lassen könnte, inklusive der Zeit-Erwartung ("bis zu 7 Minuten oder länger").

Beide Hinweise per Playwright getestet: der bedingte Hinweis erscheint bei einem frischen Charakter ohne Abschluss und verschwindet, sobald einer übernommen wurde.
