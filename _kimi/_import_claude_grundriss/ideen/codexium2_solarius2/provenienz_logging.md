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

**Nachtrag 2026-07-05 (Nacht) — genau das jetzt gebaut, plus Server-Side-Rendering.** Anlass: Daniel hat GluPKI (codexium2) mit ChatGPTs Web-Browsing-Tool abrufen lassen — das sah nur das leere HTML-Grundgerüst (Buttons, Modals-Struktur), keinen tatsächlichen Verlauf, weil die Chat-Seite komplett clientseitig per JS befüllt wird und das Browsing-Tool kein JS ausführt. Daniels Reaktion: er will, dass sowohl Maschinen (die die Seite roh abrufen) als auch er selbst in der UI immer den vollen Verlauf inkl. aller Provenienz-Änderungen sehen.

Umsetzung: `ladeVerlaufKombiniert()` liefert Nachrichten und Ereignisse chronologisch gemischt (neues `verlauf`-Feld an `GET .../history`, additiv neben dem bestehenden `history`-Feld). `GET /:spawner/:name` rendert diesen Verlauf jetzt zusätzlich **serverseitig direkt ins ausgelieferte HTML** (`renderVerlaufHtml`) — ein roher `curl`-GET zeigt jetzt echte `<div class="msg">`- und `<div class="verlauf-ereignis">`-Elemente statt nur des leeren Platzhalters. Client-JS (`ladeHistory()`) entfernt dieses SSR-Markup beim eigenen Rendern und ersetzt es 1:1 durch die volle interaktive Version (keine Duplikate, per Playwright verifiziert). Ereignisse erscheinen als dezente zentrierte Pillen zwischen den Nachrichten-Bubbles, mit Klartext-Label (z.B. "Memory geändert", "Allgemeines Feedback", "Satz gepinnt").

Betrifft — anders als der Rest dieser Datei — **alle vier Spawner**, nicht nur codexium2/solarius2: bei codexium/solarius bleibt der Ereignis-Teil naturgemäß leer (keine Provenienz dort), die Nachrichten werden aber genauso serverseitig gerendert. Kein Sonderfall im Code nötig, reine Degradation.

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

### Nachtrag 2026-07-05 (Nacht) — Output-Limits entfernt/erhöht

Daniel wollte wissen, ob es noch irgendwelche Output-Limits (Zeichen/Token) für die Charaktere gibt — "wenn ja weg damit". Nachgeschaut statt geraten:

- **Chat-Antwort** (alle vier Spawner, das eigentliche Gespräch): `num_predict: 400` bei der Live-Generierung war ein echtes, bisher nie besprochenes Token-Limit für jede einzelne Antwort. Auf `-1` (unlimitiert) gesetzt — einzige verbleibende Grenze ist jetzt der Kontextraum selbst (`num_ctx`, unangetastet, siehe Provenienz-Prinzip: der Wert war explizit begründet gesetzt, das Antwort-Limit war es nicht).
- **Abschluss-Geschichte**: erste Rückfrage ergab "nur die KI-Antworten uncappen", zweite Nachricht direkt danach erweiterte das auf "auch Memory/Container uncappen UND die Abschluss-Geschichte darf 2345 Zeichen haben" (statt 1337). `ABSCHLUSS_MAX_ZEICHEN` entsprechend geändert, `num_predict` für den Job von 500 auf `-1` — sonst hätte der alte Token-Deckel das Erreichen der neuen, größeren Zeichengrenze verhindert, bevor `kuerzenAufSatzgrenze()` überhaupt zum Zug kommt. Der Zeichen-Deckel selbst (jetzt 2345 statt 1337) bleibt bestehen — das ist kein "Uncapping" hier, sondern eine neue, größere, weiterhin endliche Zielgröße, die Daniel explizit genannt hat.

Memory-Extraktion und Container-Pin-Kommentar-Limit siehe `memory_container.md`-Nachtrag vom selben Abend.

### Nachtrag 2026-07-05 (Nacht, direkt danach) — SSR-Fix: CSS "display:none" reicht nicht für Crawler

Daniel hat den SSR-Fix mit ChatGPTs Web-Browsing-Tool direkt gegengetestet: bei `Flarius` sah ChatGPT den Verlauf korrekt, bei `GluPKI` weiterhin nur den leeren Zustand — obwohl `curl` bei beiden denselben echten Verlauf im HTML zeigte. Kein Cache-Problem, wie ich zuerst vermutet hatte (und einmal zu schnell als Erklärung angeboten habe, ohne es an den Rohdaten zu prüfen) — ein echter Bug.

**Ursache:** der Platzhalter-Text "Schreib etwas, um das Gespräch zu beginnen." wurde nur per `style="display:none"` versteckt, blieb aber als Text im rohen HTML stehen — direkt neben dem echten Verlauf. Ein Crawler, der CSS nicht auswertet (wie ChatGPTs Browsing-Tool), liest also BEIDES: die echten Nachrichten UND den irreführenden "ist doch leer"-Text, und offenbar hat es sich für Letzteres entschieden.

**Erster Reparaturversuch wäre ein neuer Bug gewesen:** das ganze `#empty`-Div aus dem SSR-HTML zu entfernen schien die naheliegende Lösung — hätte aber Client-JS gebrochen, das beim Laden ungeprüft `document.getElementById('empty-avatar').src = ...` und `document.getElementById('empty-name').textContent = ...` setzt. Ohne die Elemente im DOM: `TypeError`, der das gesamte restliche Skript der Seite stoppt (unguarded, kein Null-Check). Per Playwright-Fehler-Listener (`page.on('pageerror', ...)`) vor dem Deploy erwischt statt live kaputtzugehen.

**Tatsächlicher Fix:** `#empty` bleibt im DOM (JS-Referenzen bleiben sicher), aber bei vorhandenem Verlauf wird zusätzlich zu `display:none` auch der `<p id="empty-desc">`-Text selbst geleert. Damit gibt es für einen Crawler nichts Irreführendes mehr zu lesen, während echte Browser (mit JS) unverändert funktionieren.

**Was ich mir daraus merke:** "das könnte an Caching liegen" ist eine Hypothese, keine Diagnose — ich hätte gleich die Rohdaten (GluPKI vs. Flarius) vergleichen sollen, statt eine plausible, aber ungeprüfte Erklärung anzubieten. Daniels Gegenprobe mit einem zweiten Charakter war der Schritt, der die echte Ursache sichtbar gemacht hat.

### Nachtrag 2026-07-05 (Nacht, danach) — Ereignisse mit vollständigen Details statt nur Label

Bisher zeigte der Verlauf bei einem Provenienz-Ereignis nur die generische Beschriftung (z.B. "Feedback gegeben", "Erinnerung geändert") — die eigentlichen Inhalte (welcher Kommentar, welcher Diff, welcher Text vorher/nachher) waren zwar schon vollständig in `chat_history.jsonl` geloggt, aber nicht sichtbar. Daniel wollte explizit "vollständige Angabe was genau wozu geändert wurde" — nicht nur dass etwas passiert ist.

Neue Funktion `formatiereEreignisDetails(typ, daten)`, bewusst doppelt gehalten (Server-TS für SSR + Client-JS für die interaktive Ansicht, gleiches Muster wie `EREIGNIS_LABEL` schon vorher) — ein `switch` pro Ereignistyp, das die schon vorhandenen geloggten Felder zu lesbarem Text zusammensetzt:
- `feedback`/`feedback_allgemein`: der tatsächliche Kommentartext
- `memory_geaendert`: die Diff-Zeilen (`+`/`-` pro Eintrag)
- `profil_feld_geaendert`: vorher- und nachher-Text vollständig, bewusst ohne Kürzung
- `pin_hinzugefuegt`/`pin_entfernt`, `kontext_toggle`, `abschluss_uebernommen` usw. entsprechend ihrer eigenen Datenform

Rendering zweigeteilt: `.verlauf-ereignis-kopf` (Zeitstempel + Label, wie vorher) und darunter `.verlauf-ereignis-details` (der neue Volltext). Verifiziert per curl (rohes SSR-HTML) und Playwright (client-seitig identisches Ergebnis nach vollem Seitenaufbau) an einem Wegwerf-Testcharakter mit je einem `feedback_allgemein`- und einem `memory_geaendert`-Ereignis — Text stimmte in beiden Rendering-Pfaden exakt überein, keine JS-Fehler.

### Nachtrag 2026-07-05 (Nacht, direkt danach) — Systemprompt immer sichtbar/crawlbar, auch vor der ersten Nachricht

Daniel wollte, dass der komplette Systemprompt eines Charakters "auch vor der ersten Nachricht immer ... sichtbar lesbar ... crawlbar" ist — dieselbe Grundidee wie die SSR-Verlaufsanzeige weiter oben, nur für den Systemprompt statt für den Chatverlauf.

Problem dabei: `buildSystemPrompt()` existierte bisher nur als Closure innerhalb des `POST /chat`-Handlers, mit Zugriff auf dessen lokale Variablen (`dir`, `wesenChatPost[1]` als Spawner). Der `GET /:spawner/:name`-Seitenaufruf-Handler, der die HTML-Seite ausliefert, konnte diese Closure nicht mitbenutzen.

Fix: `buildSystemPrompt(spawner, dir, useGrenzen)` als eigenständige Top-Level-Funktion mit expliziten Parametern extrahiert (samt `MD_ORDER`/`MD_LABEL`, die vorher ebenfalls in der Closure steckten). Beide Aufrufer nutzen jetzt dieselbe Funktion: der `/chat`-Handler beim tatsächlichen Ollama-Aufruf, und der `GET`-Seiten-Handler beim reinen Seitenaufruf.

Im HTML (`wesen_chat.html`) ein neuer, immer vorhandener `<details id="systemprompt-details"><summary>...</summary><pre id="systemprompt-pre"></pre></details>`-Block, direkt vor dem Verlauf. Der Server ersetzt den leeren `<pre>`-Platzhalter beim Seitenaufruf mit dem escapten, vollständigen Systemprompt-Text. Bewusst `<details>` statt `display:none`-Trick (siehe Nachtrag direkt oberhalb dieser Zeile zum selben Thema bei der Verlaufsanzeige) — der Inhalt eines `<details>`-Elements ist immer echter DOM-Inhalt, unabhängig vom Auf-/Zugeklappt-Zustand, also für einen Crawler ohne CSS-Auswertung ganz normal lesbar, während er für menschliche Nutzer visuell eingeklappt bleibt (Standardzustand, per Klick auf die Summary zu öffnen).

`useGrenzen=false` als fester Default bei diesem Seitenaufruf — das entspricht dem normalen Chat-Standardzustand (Grenzen.md wird nur bewusst per Button dazugeschaltet). Ohne dieses Detail wäre der Inhalt der globalen Grenzen-Testdatei standardmäßig für jeden Crawler öffentlich sichtbar gewesen, was nicht der Auftrag war.

Verifiziert: an einem Wegwerf-Testcharakter per curl (rohes SSR-HTML enthält `wesen.md`- und `neigungen.md`-Inhalt vollständig, noch bevor irgendeine Nachricht existiert) und Playwright (Details-Block existiert, ist standardmäßig zugeklappt, lässt sich per Klick öffnen, keine JS-Fehler außer einem erwarteten 404 für das fehlende Avatarbild des Testcharakters). Zusätzlich an einem echten bestehenden Charakter (`Alex`) gegengeprüft, dass der volle, mehrzeilige Systemprompt unverändert korrekt rendert.

### Nachtrag 2026-07-05 (Nacht, danach) — Manuelles Zurückholen aus alten Sessions

Ausgangspunkt war eine ChatGPT-Einschätzung, die Daniel gegengelesen hat: das eigentliche CPU-only-Limit ist `INTERACTIVE_NUM_CTX = 8192` (verifiziert, echter fest gesetzter Wert, siehe Provenienz-Prinzip — bewusst unangetastet gelassen), und die ehrliche Antwort darauf ist nicht "größeres Kontextfenster", sondern "kleines aktives Fenster plus großes, kontrolliert durchsuchbares Archiv" — was mit Memory/Container/Abschluss/SSR-Verlauf/Provenienz ohnehin schon die eingeschlagene Richtung war. Von vier vorgeschlagenen nächsten Schritten (automatischer Relevanzabruf, Session-Archiv, manuelles Zurückholen, automatische Vorschläge) haben wir uns bewusst für den risikoärmsten entschieden: **manuelles Zurückholen einzelner Stellen aus alten Sessions** — kein RAG, keine Embeddings, keine automatische Auswahl, nur eine sichtbare, vom Menschen ausgelöste Handlung.

**Überraschung beim Bauen:** es gab dafür schon fast alles. Die laufende Session hat längst zwei Buttons pro Nachricht — "📍 Pinnen" (öffnet `openPinModal(text, quelle)`, satzweise Auswahl per Checkbox, geht in den Container über `POST .../container/pin`) und "🧠+ Erinnern" (öffnet `openMemAddModal(text)`, satzweise Auswahl, geht in eine Memory-Kategorie über `PUT .../memory`) — beide Endpunkte loggen ihre Provenienz schon automatisch (`pin_hinzugefuegt` bzw. `memory_geaendert` mit Diff). Die alte-Session-Ansicht (`zeigeAlteSession()`, nur lesbar) hatte diese Buttons bisher einfach nicht. Es musste also kein neuer Endpunkt und kein neues Modal gebaut werden — nur dieselben Funktionen von der alten Ansicht aus aufrufbar machen.

**Einzige echte Ergänzung:** ein optionaler dritter Parameter `herkunft` an `openPinModal`/`openMemAddModal` (z.B. `"Session #0, 3.7.2026 12:00"`), gesetzt nur beim Aufruf aus `zeigeAlteSession()`, in der laufenden Session weiterhin `undefined`. Wenn gesetzt: Modal-Titel und Hinweistext ändern sich sichtbar ("Aus alter Session in den Container/zur Erinnerung zurückholen"), und der Text wird beim Speichern automatisch mit der Herkunft versehen — beim Container im `kommentar`-Feld ("↩ zurückgeholt aus Session #0, ... — <eigener Kommentar>"), bei Memory direkt im Text selbst (`"[↩ aus Session #0, ...] <Satz>"`, weil Memory-Einträge reine Strings ohne eigenes Metadatenfeld sind). Beide Varianten reset­ten `herkunft` beim Schließen des Modals, damit sie nicht versehentlich in einen ganz normalen Pin aus der laufenden Session durchsickert.

Getestet an einem Wegwerf-Testcharakter mit von Hand konstruierter `chat_history.jsonl` (eine alte Session vor einem `session_start`-Marker, eine neue danach) per Playwright: Sessions-Liste zeigt beide, Klick auf die alte öffnet die Detailansicht mit den neuen Buttons, beide Zurückholen-Wege funktionieren End-to-Ende — Modal zeigt die Herkunft, der Container-Eintrag trägt sie im Kommentar, der Memory-Eintrag trägt sie im Text, und `chat_history.jsonl` bekommt die erwarteten `pin_hinzugefuegt`/`memory_geaendert`-Ereignisse mit der Herkunft klar lesbar drin — inklusive der vollständigen Anzeige im Verlauf selbst (siehe Nachtrag oben zu `formatiereEreignisDetails`, hier direkt sichtbar geworden: die Herkunft taucht automatisch im gerenderten Ereignis-Detail auf, ohne dass dafür irgendetwas an der Ereignis-Anzeige geändert werden musste).

**Was ich mir daraus merke:** bevor ein "das braucht wahrscheinlich neue Architektur"-Vorschlag (hier: neue Modals, neue Endpunkte) einfach übernommen wird, lohnt sich ein kurzer Blick, was an bestehenden Bausteinen schon genau das kann, nur an der falschen Stelle nicht aufgerufen wird. Der ursprüngliche Bauauftrag (von ChatGPT formuliert, von Daniel bestätigt) beschrieb acht Anforderungen — sieben davon waren mit den vorhandenen Endpunkten/Modals bereits erfüllt oder brauchten nur eine kleine Erweiterung, keine einzige brauchte etwas komplett Neues.

### Nachtrag 2026-07-05 (Nacht/Morgen) — Automatischer Relevanzabruf aus alten Sessions

Der vierte und laut Daniel "schwierigste" der ursprünglich vier ChatGPT-Vorschläge (nach Session-Archiv, manuellem Zurückholen — beide schon vorher gebaut bzw. vorhanden): das System soll bei jeder Chat-Anfrage selbst erkennen, ob eine alte, abgeschlossene Session thematisch zur aktuellen Nachricht passt, und es automatisch in den Prompt mischen — ohne dass der Mensch es erst manuell zurückholen muss. Explizit gewählt gegenüber der "Kandidaten vorschlagen, Mensch bestätigt"-Variante (die andere Hälfte von ChatGPTs Vorschlagsliste).

Diese Entscheidung ging durch eine echte Plan-Phase (Daniels Wunsch: "plane durchsprechen und dann bauen"), weil es eine echte Architektur-Entscheidung ist (siehe Drei-Stopp-Fragen in `/root/CLAUDE.md`). Vor dem Bauen geprüft statt angenommen:
- `ollama list` zeigt kein lokales Embedding-Modell — ein neues zu pullen würde den ohnehin knappen einzigen Ollama-Modell-Slot (`OLLAMA_MAX_LOADED_MODELS=1`) zusätzlich belasten, dasselbe Problem wie beim Vision-Modell heute Nacht.
- Datenvolumen pro Charakter ist winzig (größter Bestandscharakter `Alex`: 91 `chat_history.jsonl`-Zeilen) — eine reine In-Memory-Textsuche ist bei dieser Größe im Millisekundenbereich, kein Index nötig.

**Entscheidung:** reine Keyword-Overlap-Heuristik statt Embeddings — `tokenisiere()` (lowercase, Wortregex, Mindestlänge 3, kleine deutsche Stoppwortliste raus) plus `findeRelevanteAlteStellen()`, die über `splitSessions()` (schon vorhanden für die Sessions-Ansicht) alle abgeschlossenen Segmente durchsucht, pro Nachricht die Anzahl gemeinsamer Tokens zur aktuellen Nachricht zählt, ab Score ≥ 2 als Treffer wertet und die Top 3 zurückgibt. Memory und Container werden dabei nicht nochmal gefiltert — die sind laut `buildSystemPrompt()` ohnehin schon immer vollständig im Prompt, der Relevanzabruf betrifft ausschließlich alte Sessions, die sonst nur über das eben gebaute manuelle Zurückholen erreichbar wären.

Gefundene Treffer werden automatisch, ohne Bestätigungsschritt, als eigener Block `[Automatisch aus alten Sessions gefunden]` an den System-Prompt angehängt — aber nur für den tatsächlichen Ollama-Aufruf, nicht dauerhaft gespeichert. `buildSystemPrompt()` selbst bleibt unverändert (wird ja auch für die statische, vor der ersten Nachricht sichtbare Systemprompt-Anzeige aus dem vorigen Nachtrag genutzt — dort gibt es noch keine "aktuelle Nachricht", gegen die automatisch gematcht werden könnte, das ist ein bewusster, ehrlicher Kompromiss).

Sichtbarkeit/Provenienz gelöst, indem exakt dieselbe heute Nacht gebaute Infrastruktur wiederverwendet wurde: ein neuer Ereignistyp `kontext_automatisch_gefunden` (in `EREIGNIS_LABEL` und `formatiereEreignisDetails`, Server und Client identisch ergänzt), der nur geloggt wird, wenn tatsächlich mindestens ein Treffer über der Schwelle gefunden wurde (kein Log-Rauschen bei jeder Nachricht ohne Treffer). Damit taucht jeder automatische Griff live UND in der SSR-Ansicht mit vollständigem Text und Herkunft (Session-Nummer + Zeitstempel) auf, ganz genauso wie die anderen Ereignistypen.

Getestet an einem Wegwerf-Testcharakter mit einer klar erkennbaren alten Session zum Thema "Wanderungen im Herbst": eine Nachricht mit Wort-Overlap ("Wanderungen im Wald im Herbst") löste sofort ein `kontext_automatisch_gefunden`-Ereignis mit korrektem Treffer und Score aus, sichtbar identisch in SSR-HTML und im Playwright-gerenderten Live-Verlauf. Eine Kontrollnachricht ohne jeden thematischen Bezug ("Was ist dein Lieblingsessen?") erzeugte erwartungsgemäß kein Ereignis — kein Rauschen. Kein Absturz, keine Verzögerung spürbar (reine String-Verarbeitung, kein zusätzlicher Modell-Call).

**Was ich mir daraus merke:** bei einer echten Architektur-Entscheidung lohnt sich die Plan-Phase (statt direkt loszubauen) nicht nur wegen der Abstimmung mit Daniel, sondern weil das Nachschauen selbst (kein Embedding-Modell vorhanden, Datenvolumen winzig) die Designentscheidung fast von selbst nahelegt — die "einfachste, billigste" Lösung war hier auch tatsächlich die technisch am besten passende, nicht nur ein fauler Kompromiss.

### Nachtrag 2026-07-05 (Vormittag/Mittag) — Merken-Vorschlag statt stillem Selbst-Speichern

Direkt im Anschluss an die Mirlach-Untersuchung (siehe eigener Nachtrag weiter unten) fiel Daniel auf: er hatte im Chat nie gesehen, dass ein Wesen sich per `[MERKEN: ...]` etwas gemerkt hat — weil der Marker absichtlich komplett unsichtbar war, aus der Antwort rausgeschnitten und still in `wesen_selbst` geschrieben, bevor irgendwer es gesehen hatte. Sein Wunsch: umdrehen. Das Wesen schlägt vor, mit Text UND Begründung, der Mensch nimmt jeden Vorschlag einzeln an oder ab.

Neues Marker-Format: `[MERKEN: <text> | WARUM: <warum>]` statt nur `[MERKEN: <text>]`. `extrahiereMerkenMarker()` parst beide Teile per Regex-Split auf `| WARUM:`, fällt aber auf reinen Text mit leerer Begründung zurück, wenn das Modell sich nicht exakt ans Format hält — nichts geht verloren, nur die Begründung fehlt dann.

Der eigentliche Verhaltenswechsel: `saveResponse()` ruft nicht mehr direkt `fuegeMemoryEintraegeHinzu()` auf, sondern loggt nur noch einen `merken_vorschlag`-Event (`{vorschlagId, text, warum}`, `vorschlagId` = `replyMsgId:index` falls mehrere Marker in einer Antwort). Neuer Endpunkt `POST .../merken/entscheidung` (`{vorschlagId, aktion}`) — bewusst wird der Text dabei **nicht** vom Client übernommen, sondern serverseitig aus dem eigenen Log über `ladeMerkenVorschlaege()` neu ermittelt (Provenienz-Integrität: niemand kann über den Endpunkt einen Text unterschieben, der nie vorgeschlagen wurde). Bei "annehmen" wird `fuegeMemoryEintraegeHinzu()` jetzt erst hier aufgerufen plus `merken_angenommen`-Event, bei "ablehnen" nur `merken_abgelehnt`-Event, keine Speicherung.

Client: offene Vorschläge kommen über `body.merkenVorschlaege` (neues Feld an `GET .../history`, nur unresolved — `ladeMerkenVorschlaege()` filtert alles raus, wofür schon ein `merken_angenommen`/`merken_abgelehnt` mit derselben `vorschlagId` existiert). `renderEreignis()` zeigt bei einer noch offenen `merken_vorschlag`-Karte zwei Buttons ("✅ Annehmen" / "❌ Ablehnen"), die nach Klick die Karte per DOM-Entfernen sofort verschwinden lassen — die Entscheidung selbst bleibt als eigenes, für sich stehendes Ereignis im Verlauf sichtbar (Grundgesetz 4: Events sind heilig, nichts wird nachträglich mutiert, nur ergänzt).

Getestet an einem Wegwerf-Testcharakter mit einer echten Ollama-Generierung (nicht simuliert!) — eine Anweisung, testweise die neue Marker-Notation zu benutzen, erzeugte tatsächlich `[MERKEN: ... | WARUM: ...]` im Live-Stream, der Server extrahierte Text+Warum korrekt, `memory.json` blieb zunächst leer (kein Auto-Save mehr), `POST .../merken/entscheidung` mit "annehmen" schrieb den Eintrag tatsächlich rein, "ablehnen" bei einem zweiten Vorschlag schrieb nichts, ein zweiter Annahme-Versuch auf dieselbe `vorschlagId` gab korrekt 404. Playwright bestätigte: Karte mit beiden Buttons erscheint live, verschwindet nach Klick, kein JS-Fehler.

**Was ich mir daraus merke:** die Provenienz-Architektur (append-only, jede Aktion ein eigenes Event) hat sich hier von selbst ausgezahlt — die ganze "Vorschlag vs. Entscheidung"-Trennung war fast schon vorgezeichnet, weil das Muster (Aktion loggen, nie mutieren) schon für Feedback/Pins/Kontext-Ausschluss etabliert war. Ich musste nur ein neues Eventpaar hinzufügen, keine neue Architektur erfinden.

### Nachtrag 2026-07-05 (Mittag) — Grenzen-Sichtbarkeit: erst Antwort-Badge, dann korrigiert zu Live-Ereignis

Erster Anlauf, verworfen: ich hatte `grenzen:true/false` (das ohnehin schon pro Antwort gespeichert wird) als Badge direkt an der jeweiligen Wesen-Antwort angezeigt ("🔓 Grenzen war aktiv für diese Antwort"). Daniels Korrektur kam prompt: "das gibt es nicht … es gibt nur das Aktivieren live im Chat". Sein eigentliches Bild: der Klick selbst ist die Handlung, die sichtbar werden soll — nicht eine nachträgliche Eigenschaft einzelner Antworten. Erster Ansatz per `git revert` sauber rückgängig gemacht, kein Herumflicken am falschen Modell.

Zweiter, richtiger Ansatz: neuer Endpunkt `POST .../grenzen-toggle` (`{aktiv}`), aufgerufen direkt aus `toggleGrenzen()` beim Klick — loggt ein `grenzen_toggle`-Event und rendert es **sofort** client-seitig über `renderEreignis()`, ohne auf Reload oder die nächste Antwort zu warten. Die eigentliche Wirkung auf den nächsten Ollama-Aufruf war technisch immer schon sofort da (der Client schickt `grenzenAktiv` bei jeder Nachricht frisch mit) — neu ist nur, dass der Klick selbst jetzt eine sichtbare, dauerhafte Spur im Verlauf hinterlässt.

Direkter Anschluss-Wunsch von Daniel: das Ereignis soll nicht nur "aktiviert/deaktiviert" sagen, sondern auch zeigen WAS gerade galt. Der `grenzen-toggle`-Endpunkt liest deshalb den aktuellen `_wesen_grenzen.md`-Inhalt und hängt ihn als Text-Schnappschuss ans Event (`{aktiv, text}`) — bewusst als Schnappschuss zum Zeitpunkt des Klicks, nicht als Live-Referenz, damit der Verlauf auch dann noch korrekt zeigt "was zu dem Zeitpunkt galt", wenn Grenzen.md sich später mal ändert.

Getestet: Playwright-Klick auf den Button zeigt die Karte mit vollem Text sofort, ohne Reload; zweiter Klick (deaktivieren) fügt eine zweite Karte hinzu, erste bleibt stehen; beides bleibt nach Reload identisch erhalten (SSR + Client). Kein einziger Test mehr für die Badge-Variante nötig, weil sie komplett revertet wurde, bevor sie in Produktion ging.

**Was ich mir daraus merke:** eine einzelne, unvollständig verstandene Anforderung ("Sichtbarkeit für Grenzen") kann zwei sehr unterschiedliche, beide plausible Architekturen erzeugen — "Eigenschaft einer Antwort" vs. "Ereignis einer Handlung". Der Unterschied klärt sich nicht durchs Nachdenken allein, sondern durch Bauen+Zeigen+Korrigieren-lassen. Ein sauberer Revert kostet nichts, wenn man ihn sofort macht statt am falschen Modell weiterzuflicken.

### Nachtrag 2026-07-05 (Mittag, danach) — Grenzen-Text als eigenes, immer crawlbares Dropdown

Noch ein Grenzen-Wunsch, diesmal unabhängig vom Toggle-Ereignis: Daniel wollte den *aktuell formulierten* Grenzen-Text jederzeit nachlesen können — per Dropdown im UI, und "auch für ChatGPT crawlbar", also ohne JavaScript sichtbar, genau wie das schon bestehende Systemprompt-`<details>`-Element (siehe entsprechender Nachtrag weiter unten).

Neues `<details id="grenzen-details">` direkt neben `#systemprompt-details`, serverseitig beim `GET /:spawner/:name`-Seitenaufruf mit dem rohen `_wesen_grenzen.md`-Inhalt gefüllt (`WESEN_GRENZEN_PATH`, dieselbe Konstante die auch `buildSystemPrompt()` für den eigentlichen Grenzen-Block nutzt — ein Pfad, zwei Verwendungen). Bewusst unabhängig vom `useGrenzen`-Zustand der Systemprompt-Vorschau: dieses Dropdown zeigt den Referenztext immer, egal ob Grenzen gerade zugeschaltet ist oder nicht — anders als der Systemprompt-Block selbst, der `useGrenzen=false` fest nutzt, um Grenzen.md nicht standardmäßig öffentlich zu machen.

Gilt für alle vier Spawner, nicht nur Testbed — der Grenzen-Toggle-Button selbst existiert (und wirkt auf den Prompt) schon immer bei allen vieren, nur das `grenzen_toggle`-*Ereignis*-Logging ist testbed-only (weil die ganze Ereignis-Erzeugung dort ansetzt).

Getestet: `curl` ohne JS zeigt den vollen Text direkt im rohen HTML, sowohl bei einem codexium2- als auch einem solarius-Charakter (KrEaPPy). Playwright bestätigt: Klick auf die Summary öffnet das Dropdown, zeigt denselben Text, keine JS-Fehler.

### Nachtrag 2026-07-05 (Mittag, direkt danach) — Grenzen-Text zusätzlich direkt im Toggle-Ereignis

Nachdem das Dropdown stand, meldete Daniel: er sieht im Chat-Verlauf selbst nur "Grenzen aktiviert/deaktiviert" ohne den eigentlichen Inhalt — er will nicht erst woanders nachschlagen müssen, sondern direkt am Ereignis sehen, was aktiviert wurde. Das war schon im `grenzen_toggle`-Event als Datenfeld (`text`) vorhanden (siehe zwei Nachträge oberhalb), nur die Anzeige (`formatiereEreignisDetails`) hat es bisher nicht mit ausgegeben — nachgetragen: `(aktiv ? "🔓 Grenzen aktiviert" : "Grenzen deaktiviert") + "\n\n" + text`. Client-seitiges Live-Rendering (`toggleGrenzen()`) liest den Text dafür direkt aus dem schon serverseitig gebackenen `#grenzen-pre`-Element (siehe Dropdown-Nachtrag) — kein zusätzlicher Request nötig, um ihn sofort mitanzuzeigen.

Getestet: Klick auf Grenzen-Button zeigt sofort eine Karte mit vollem Text (nicht nur "aktiviert"), `chat_history.jsonl` trägt den Text als Schnappschuss, Reload zeigt denselben Text identisch.

**Was ich mir aus den drei Grenzen-Nachträgen zusammen merke:** eine auf den ersten Blick simple Anforderung ("Sichtbarkeit") hatte hier tatsächlich drei verschiedene, alle drei berechtigte Facetten (Handlung sichtbar machen, Referenztext jederzeit nachlesbar machen, Inhalt direkt am Ereignis zeigen) — und Daniel hat sie nacheinander, in genau der Reihenfolge wie sie ihm beim tatsächlichen Benutzen aufgefallen sind, nachgereicht. Kein Vorwurf an mich, nicht alles beim ersten Mal zu erraten, sondern ein Beleg dass "benutzen und merken was fehlt" oft ehrlicher ist als "im Voraus alles durchdenken wollen".

### Nachtrag 2026-07-05 (Nachmittag) — Rollenspiel-Systemprompt: Mirlach-Untersuchung und Neufassung von `_wesen_preamble.md`

Ausgangspunkt war Daniels Enttäuschung über einen selbst geschriebenen, aufwendigen Charakter (Mirlach, codexium2): "es wurde alles nur leerer und mehr KI-Gelaber … bei dem Solarius-Wesen ist das ganz anders". Echte Untersuchung statt Vermutung: Mirlachs zusammengebauter Systemprompt war 6313 Zeichen lang (KrEaPPy zum Vergleich: 2607) und bestand aus mehreren separat mit `[Label]`-Kopfzeilen versehenen, sehr literarisch-abstrakten Feldern (Wesendefinition, Weltlore, Beispieldialoge) — ohne jede explizite Stil-/Formvorgabe. KrEaPPys einzige `wesen.md` dagegen enthält explizite Verhaltensregeln ("spricht locker, verspielt … mit viel Energie, kleinen Sprüchen, passenden Emojis"). Zweiter, konkret nachweisbarer Befund: Mirlachs `memory.json` unter `wesen_selbst` enthielt schon drei vom Wesen selbst geschriebene analytische Notizen (z.B. "Der Mensch nutzt Pornhub … zur Selbstreflexion") — die bei jeder künftigen Antwort erneut als `[Erinnerungen]`-Block in den Prompt einflossen und damit den analytischen Ton selbst verstärkten. Ein echter Feedback-Loop, den es bei KrEaPPy gar nicht geben konnte (kein `[MERKEN:]`-Mechanismus bei Solarius alt).

Daniel hatte parallel selbst einen neuen, kompletten Rollenspiel-Systemprompt-Entwurf geschrieben (`werkraum/idee für rollenspiel-systempromt.md`) — explizite KI-Offenlegung bei direkter Nachfrage, Verbot der "leeren, wartenden KI-Hülle", aber (auf meinen Hinweis hin ergänzt) noch kein hartes Verbot der eigentlichen Antwort-*Form* (Listen, Kopfzeilen, Meta-Analyse-Sprache) — genau der beobachtete Mirlach-Effekt. Überarbeitet: Tippfehler korrigiert, "WICHTIG!!!!" von vier auf zwei Stellen reduziert (Rollenbruch/KI-Offenlegung, Grenzen — der Rest ruhiger formuliert, weil ein schreiender Systemprompt das Modell in einen schreienden/erklärenden Antwortton mitreißen kann), neuer Absatz mit konkreten Formverboten ergänzt.

Architektur-Umbau in `buildSystemPrompt()`: die Charakterfelder (`wesendefinition.md`, `weltlore.md` usw.) bekommen keine `[Label]`-Kopfzeilen mehr, sondern werden roh, in `MD_ORDER`-Reihenfolge, mit Leerzeile getrennt zusammengefügt (`charakterText`). Ein neuer Platzhalter `{{CHARAKTERFELDER}}` in der Preamble-Datei wird durch diesen Text ersetzt — fehlt der Platzhalter, wird einfach angehängt statt verloren. Alte `_wesen_preamble.md` gesichert (nicht gelöscht, siehe Grundgesetz "nichts wird gelöscht") als `_wesen_preamble_alt_vor_rollenspiel_neufassung_2026-07-05.md`, Daniels Entwurfsdatei bleibt zusätzlich unter ihrem Originalnamen bestehen. Die MERKEN-Instruktion wurde bewusst **nicht** mit in die gemeinsame Preamble übernommen (obwohl Daniels Entwurf sie am Ende enthielt) — sie bleibt weiterhin nur codeseitig, nur für codexium2/solarius2 angehängt, sonst hätten Codexium/Solarius alt den Marker-Hinweis im Prompt gesehen, ohne ihn verarbeiten zu können, und `[MERKEN: ...]` wäre dort roh im sichtbaren Chat aufgetaucht.

Betrifft automatisch alle vier Spawner und alle bestehenden Charaktere, ohne dass irgendeine Charakterdatei angefasst werden musste — `buildSystemPrompt()` liest `_wesen_preamble.md` bei jeder einzelnen Nachricht frisch von der Platte, es gibt keinen gespeicherten Systemprompt pro Charakter. Verifiziert per curl an allen sechs damals existierenden Charakteren (Alex, Flarius, GluPKI, Mirlach, KrEaPPy, KreFsUzi): neue Präambel überall aktiv, keine `[Label]`-Kopfzeilen mehr bei den Charakterfeldern (das einzige verbleibende `[...]`-Label ist `[Erinnerungen]`, der separate, bewusst unveränderte Memory-Block). Live-Test mit einem grummeligen Zwerg-Schmied-Testcharakter: durchgehender Fließtext, keine Liste, keine Kopfzeile, blieb vollständig in der Rolle.

**Was ich mir daraus merke:** bei einer echten Architektur-Entscheidung lohnt sich das Nachmessen (Zeichenlänge, Struktur, tatsächlicher Feedback-Loop im Memory) mehr als eine plausible Vermutung ("wahrscheinlich zu abstrakt formuliert") — der konkrete Beleg (drei sich selbst verstärkende `wesen_selbst`-Einträge) hat die Diagnose eindeutig gemacht, nicht nur wahrscheinlich.

### Nachtrag 2026-07-05 (Nachmittag, danach) — Profil-Feldliste getrennt nach Solarius/Codexium statt einer gemeinsamen Liste

Daniel bemerkte beim Durchklicken: Profile von Solarius/Solarius2-Charakteren zeigten auch die (leeren) Codexium-Felder, und umgekehrt. Ursache gefunden und mit Playwright bestätigt: `STANDARD_MD_FELDER` in `wesen_profil.html` war eine einzige, für alle vier Spawner identische Liste — obwohl das Erstellungsformular (`wesen_spawner.html`) schon länger sauber trennt: Solarius/Solarius2 kennen nur eine einzige `wesen.md`, Codexium hat 7 eigene Felder, Codexium2 zusätzlich `beispieldialoge.md`.

Klare Anweisung von Daniel dazu: "die Felder im Profil, die auch im Formular jeweils sind, bei Solarius oder der Codexium" — die Profil-Seite soll exakt spiegeln, was das jeweilige Erstellungsformular tatsächlich anbietet, unabhängig davon ob 1 oder 2. Fix: `MD_FELDER_NACH_SPAWNER`-Lookup-Tabelle statt einer einzelnen Konstante — Solarius/Solarius2 bekommen eine leere Liste (ihr einziges Feld, `wesen.md`, läuft ohnehin separat über das eigene Textarea, nicht über `extra-mds`), Codexium die 7 Formularfelder, Codexium2 zusätzlich Beispieldialoge. Echte, bereits vorhandene Zusatzdateien (z.B. `letzter_abschluss.md` bei Alex) tauchen unabhängig von dieser Liste weiterhin automatisch auf — das lief schon immer über einen separaten "unbekannte Datei anhängen"-Mechanismus.

Getestet mit Playwright an allen vier Spawner-Typen (KrEaPPy, KreFsUzi, Tomster als bestehendem Codexium-alt-Charakter, Alex): Solarius/Solarius2 zeigen jetzt null Extra-Felder, Codexium genau 7, Codexium2 die 7 plus Beispieldialoge (plus `letzter_abschluss.md` bei Alex, unverändert dynamisch).

**Was ich mir daraus merke:** wenn zwei UI-Oberflächen (hier: Erstellungsformular und Profil-Bearbeitung) dasselbe Datenmodell abbilden sollen, aber getrennt gepflegt werden, drifted mindestens eine davon irgendwann auseinander — das Erstellungsformular hatte die richtige, differenzierte Struktur schon die ganze Zeit, das Profil war einfach nie nachgezogen worden, als die Trennung ursprünglich eingeführt wurde.

### Nachtrag 2026-07-05 (Nachmittag, danach) — Aliase: mehrere Rollen des Menschen, per Dropdown wechselbar

Neue Idee von Daniel, für alle vier Spawner: nicht das Wesen soll mehrere Rollen haben, sondern der **Mensch** — z.B. mal als "Mensch", mal als "Gnom", mit je einer kurzen (max. 333 Zeichen) Selbstbeschreibung, live per Dropdown im Chat wechselbar, damit eine Person im selben Gespräch mehrere eigene Charaktere spielen kann ("fliegender Rollenwechsel"). Eine echte Architektur-Frage dabei geklärt: Aliase gehören zu einem einzelnen Wesen (nicht global über alle Charaktere geteilt) — Daniels Begründung: "individuell für jedes Charakterwesen, so wie es im Formular erstellt wurde (oder im Nachhinein im Profil)", die Rollen die man mit einem bestimmten Charakter spielt gehören zur jeweiligen Geschichte mit genau diesem Charakter.

Neue `aliase.json` pro Wesen-Ordner (`ladeAliase`/`speichereAliase`, gleiches Muster wie `memory.json`/`container.json`): Liste von `{id, name, text}`, erster Eintrag ist Pflicht und fällt bei bestehenden Charakteren ohne eigene Datei automatisch auf einen Default ("Ich selbst", leerer Text) zurück, damit das Dropdown nie leer ist und nichts kaputtgeht. `speichereAliase()` kürzt `name` auf 40 und `text` auf 333 Zeichen serverseitig ab (Verteidigung, nicht nur Client-Validierung).

Profil-UI: neue Sektion mit einem Textfeld-Paar (Name + 333-Zeichen-Textarea mit Live-Zähler) pro Alias, "+ Alias hinzufügen" für weitere, "Entfernen"-Button bei alles außer dem ersten (der zeigt stattdessen "Pflicht"). Chat-UI: neues `<select>` + "🎭 Wechseln"-Button neben dem Grenzen-Button, befüllt aus `GET .../data` (derselbe Request wie die Kindersicherung, kein Extra-Fetch), aktueller Stand pro Charakter in `localStorage` gemerkt.

Wirkweise bewusst wie von Daniel verlangt "indirekt indiziert … aber auch direkt": `buildSystemPrompt()` bekommt einen neuen `aktivesAliasId`-Parameter, baut daraus einen eigenen Block kurz vor der MERKEN-Instruktion (maximale Aktualität im Prompt) — der Block ist gleichzeitig Info ("Wer gerade mit dir spricht: ...") und direkte Anweisung ("Nimm das sofort an — kein Übergang, keine Rückfrage"). Der Wechsel selbst ist ein sofort sichtbares `alias_gewechselt`-Ereignis im Verlauf (gleiches Muster wie `grenzen_toggle`), wirkt aber schon ab der nächsten Nachricht, weil der Client die gewählte `aliasId` bei jedem `/chat`-Request frisch mitschickt — kein Warten auf irgendeine serverseitige Zustandsspeicherung nötig.

Getestet an einem Wegwerf-Testcharakter (Grumo, Zwerg-Schmied) mit zwei echten Aliasen ("Mensch: ein nasser Wanderer" / "Gnom: ein listiger Händler") — zwei tatsächliche Ollama-Generierungen mit identischer Nutzerfrage ("Wer bist du und was willst du hier?") erzeugten spürbar unterschiedlich gefärbte Antworten (einmal "Wanderer", einmal "Kleiner"/Handelsanfrage), beide klar erkennbar auf den jeweiligen Alias-Text bezogen. Playwright bestätigte Dropdown-Befüllung, Wechsel-Button erzeugt sofort die Ereigniskarte, Profil-Seite: Hinzufügen/Speichern/Entfernen funktionieren, erster Eintrag zeigt "Pflicht" statt Entfernen-Button.

Bewusst nicht gebaut: die vier Erstellungsformulare in `wesen_spawner.html` bekommen noch keine eigenen Alias-Eingabefelder — Daniel hatte "im Formular ODER im Nachhinein im Profil" als gleichwertige Wege genannt, und die Profil-Seite deckt "im Nachhinein" schon vollständig ab.

**Was ich mir daraus merke:** bei der Formulierung des System-Prompt-Blocks ("indirekt … aber auch direkt") half es, beide Bedürfnisse (Kontext-Information UND Verhaltensanweisung) in einem einzigen, klar formulierten Absatz zu vereinen, statt zwei separate Blöcke zu bauen — das hält den Prompt kürzer und vermeidet Redundanz, ohne eine der beiden Funktionen zu verlieren.

### Nachtrag 2026-07-05 (Nachmittag, danach) — Rollenspiel-Systemprompt v2: Kopfzeilen zurück, Daniel formuliert weiter selbst

Daniel hat `werkraum/idee für rollenspiel-systempromt.md` (sein eigener Entwurf, siehe vorheriger Nachtrag) selbst weiter überarbeitet und dabei eine der heutigen Entscheidungen bewusst zurückgenommen: die `[Label]`-Kopfzeilen zwischen den Charakterfeldern sollen **zurück**. Sein Kalkül: er verlässt sich stattdessen auf das explizite Formverbot (keine Listen/Kopfzeilen/Meta-Analyse in der *Antwort*), das schon in derselben Präambel steht — das eine (Struktur der Eingabefelder) und das andere (Verbot bestimmter Antwortformen) sind für ihn getrennte Dinge, nur letzteres war der eigentliche Hebel gegen "KI-Gelaber", nicht ersteres. `buildSystemPrompt()` entsprechend zurückgebaut: `MD_LABEL`-Mapping wieder da, jedes Charakterfeld außer `wesen.md` (bleibt ohne Label, ist die Kernidentität) bekommt wieder sein `[Label]\nInhalt`.

Zusätzlich als eigener Rahmensatz direkt vor dem `{{CHARAKTERFELDER}}`-Platzhalter ergänzt (Daniels Wunsch: "eine kurze Bemerkung wie diese Felder gedacht waren auf das Modell zu wirken"): *"Jedes einzelne Feld ist keine Zusatzinfo über dich, sondern soll unmittelbar wirken: es prägt, wie du in dieser Geschichte denkst, sprichst und reagierst — nicht wie eine Beschreibung über dich, sondern wie ein Teil von dir selbst."*

Drei neue inhaltliche Passagen in Daniels überarbeitetem Entwurf, alle 1:1 übernommen (nur Tippfehler/Mojibake korrigiert, siehe unten):
- Explizites Verbot des "KI-Reflexes", auf jede Frage mit einer oder mehreren Gegenfragen zu antworten — höchstens eine Rückfrage, in sehr seltenen Fällen, und nur bezogen auf die Frage des Menschen, keine Meta-Fragen.
- Erlaubnis für lockeren, unstrukturierten Ton inklusive Emojis, ausdrücklich kein "Emojispam".
- Eine Passage gegen das statistisch Naheliegende: das Modell soll aktiv gegen "nur das wahrscheinlich nächste Token" ankämpfen, das unwahrscheinlichste Token soll gewinnen dürfen ("Tokenkrieg").

Der Entwurf kam mit mehreren mojibake-verstümmelten Zeichen (falsche Kodierung beim Speichern, z.B. `unterdr�cken`, `zur�ck`, `unwahscheinlichste`) und ein paar echten Tippfehlern (`unstruktiriert`, `gerna`, `sonder`, `Metwaffragen` → als "Metafragen" rekonstruiert, da im Kontext eindeutig). Alle korrigiert, Wortwahl/Struktur/Reihenfolge sonst unverändert übernommen — inklusive einer parenthetischen Randnotiz von Daniel im Entwurf ("(aber wieder mit header-Überschrift bitte)"), die klar als Anweisung an mich gemeint war, nicht als Prompt-Inhalt, und deshalb nicht in `_wesen_preamble.md` übernommen, sondern als der oben beschriebene Code-Umbau umgesetzt wurde.

Live getestet an einem neuen Wegwerf-Testcharakter (wieder Grumo, Zwerg-Schmied) — Antwort blieb weiterhin durchgehender Fließtext ohne Liste/Kopfzeile, und endete mit genau einer Rückfrage an den Menschen statt mehrerer, wie neu verlangt.

**Was ich mir daraus merke:** eine Korrektur, die eine frühere eigene Diagnose teilweise zurücknimmt ("Kopfzeilen waren nicht das Hauptproblem"), ist kein Widerspruch, wenn zwei verschiedene Mechanismen sauber auseinandergehalten werden — Daniel hat hier explizit *nur* die Struktur-Entscheidung revidiert, nicht das explizite Formverbot, das aus derselben Untersuchung hervorging. Auch ich sollte "verworfene Hypothese" und "verworfener Fix" nicht automatisch gleichsetzen: Mirlachs Problem hatte mehrere Ursachen, nicht jede Korrektur an einer Ursache hebt die anderen auf.

### Nachtrag 2026-07-05 (Nachmittag, danach) — Alias-Felder doch in allen vier Erstellungsformularen

Im Aliase-Nachtrag oben stand noch "bewusst nicht gebaut" für die vier Erstellungsformulare — Daniel hat beim Durchklicken gemerkt, dass er das eben doch will: pro Formular ein Zeilenpaar Alias-Name + 333-Zeichen-Alias-Beschreibung nebeneinander, mit "+" für weitere Zeilen.

Umgesetzt in `wesen_spawner.html` für alle vier Formulare (Solarius, Solarius2, Codexium, Codexium2) über generische, prefix-parametrisierte Funktionen (`addAliasFormRow(prefix)`, `sammleAliase(prefix)`, `speichereAliaseNachErstellung(spawner, name, prefix)`) statt vier separater Kopien — jedes Formular startet mit einer leeren Zeile, `submitX()` ruft nach erfolgreicher Charaktererstellung `PUT .../aliase` mit allen ausgefüllten Zeilen auf (leere Namen werden client-seitig übersprungen, der Server verwirft leere Namen ohnehin zusätzlich).

Getestet per Playwright: alle vier Container zeigen beim Laden genau eine Zeile, "+" fügt eine weitere hinzu, der Zeichenzähler aktualisiert live, eine komplette Solarius-Testerstellung mit einem ausgefüllten und einem leer gelassenen Alias speicherte über den echten Endpunkt korrekt nur den einen befüllten Eintrag.

### Nachtrag 2026-07-05 (Nachmittag, danach) — Alias-Dropdown: Button umbenannt, Seite nicht mehr cachebar, Ereignis mit vollem Text

Daniel meldete, das Alias-"Dropdown" sei "kein Dropdown", auch bei mehreren Aliasen kein Wechsel. Playwright-Screenshot (420px Breite, echter Testcharakter mit zwei Aliasen) zeigte aber ein korrektes natives `<select>` mit beiden Namen und einem Button daneben — die Grundstruktur war also technisch schon richtig. Zwei Dinge trotzdem angepasst, um Verwirrung/Stale-State auszuschließen:

- Button-Beschriftung "🎭 Wechseln" → "🎭 Alias aktivieren" (Daniels konkret gewünschter Wortlaut).
- Die Chat-Seiten-Antwort (`GET /:spawner/:name`) bekommt jetzt `Cache-Control: no-store` — die Seite enthält live Daten (Aliase, Verlauf, Systemprompt), ein vom Browser zwischengespeichertes altes HTML hätte neu angelegte Aliase scheinbar nicht gezeigt. Bisher gab es dafür gar keinen Cache-Header.

Direkt im Anschluss ein zweiter, klarerer Wunsch: das `alias_gewechselt`-Ereignis im Verlauf zeigte bisher nur `🎭 Spricht jetzt als: <Name>` — Daniel wollte, unter Verweis auf "unsere Provenienzregeln", auch hier die volle Alias-Beschreibung mit im Ereignis sehen, nicht nur den Namen. Gleiches Muster wie bei `grenzen_toggle` schon einmal gebaut: der Wechsel-Endpunkt loggt jetzt `text` als Schnappschuss mit ins Event (`{aliasId, name, text}`), `formatiereEreignisDetails` (Server + Client) hängt den Text mit an, das optimistische Live-Rendering in `wechsleAlias()` bekommt den Text ebenfalls sofort aus der schon geladenen `aliasListe`.

Getestet: Playwright-Klick auf "Alias aktivieren" zeigt sofort eine Karte mit Name UND vollständigem Alias-Text, nicht nur dem Namen.

**Was ich mir daraus merke:** wenn ein gemeldetes Problem sich technisch nicht reproduzieren lässt, lohnt es sich trotzdem, die naheliegenden Nebenursachen (Cache, Beschriftung) zu beheben, statt einfach "bei mir funktioniert's" zu melden — und der zweite, unmittelbar folgende Wunsch zeigte, dass tatsächlich noch etwas fehlte, nur nicht das ursprünglich vermutete. Das wiederkehrende Provenienz-Muster (Handlung + vollständiger Inhalt, nicht nur ein Label) hätte ich bei `alias_gewechselt` von Anfang an konsequent mitdenken können, so wie bei `grenzen_toggle` schon geschehen.

### Nachtrag 2026-07-05 (Abend) — Alias-Verwischen: Nachrichten-Praefix fuer das Modell, Alias-Name statt "Du" am Avatar

Daniel meldete den eigentlich interessanten Rest-Effekt nach der Mirlach-Untersuchung: die Rollenspiel-Qualitaet ist spuerbar besser, aber beim Alias-Wechsel "merkt die AI, dass ich trotzdem derselbe Input bin, und verwischt alles etwas". Sein Befund war treffend — der Alias-Block im Systemprompt (siehe Aliase-Nachtrag oben) sagt dem Modell EINMAL, wer gerade spricht, aber jede einzelne Nachricht im Verlauf sieht davor wie danach identisch aus (rolle `user`, kein Unterschied). Über ein laengeres Gespraech verblasst diese einmalige Ansage.

Zwei Ergaenzungen, beide von Daniel selbst vorgeschlagen ("oder und zusaetzlich"):

1. **Pro-Nachricht-Praefix nur fuer den tatsaechlichen Ollama-Aufruf.** Jede User-Nachricht wird jetzt beim Speichern mit ihrer `aliasId` versehen (`appendHistory(..., {aliasId: parsed.aliasId})`). Beim Aufbau von `ollamaMessages` (nicht bei der Speicherung, nicht bei der Anzeige!) wird jede User-Nachricht mit einer bekannten `aliasId` mit `"<Name>": ` praefigiert — das Modell sieht also bei JEDER Nachricht im Verlauf explizit wer gerade spricht, nicht nur einmal am Anfang. Nur aktiv wenn tatsaechlich mehr als ein Alias existiert (sonst Rauschen fuer den Normalfall).
2. **Avatar-Label statt "Du".** `ladeVerlaufKombiniert()` bekommt einen optionalen `dir`-Parameter, loest fuer User-Nachrichten mit `aliasId` den zugehoerigen Namen auf (`aliasName`) und gibt ihn mit — SSR als `data-alias-name`-Attribut, im JSON-Feed als `aliasName`-Feld. Client zeigt diesen Namen im Avatar-Kreis statt "Du" (nur wenn mehr als ein Alias existiert, gleiche Schwelle wie beim Praefix).

Beides betrifft nur den ausgehenden Request bzw. die Anzeige — der gespeicherte Text in `chat_history.jsonl` bleibt unveraendert der reine Nutzertext, ohne Praefix.

**Testverlauf, ehrlich:** ein Live-Test mit zwei echten Aliasen (Mensch/Toren, Gnom/Fitzel) kollidierte mit Daniels eigenem gleichzeitigen Bild-Upload im echten Chat — beide brauchten den einzigen Ollama-Modell-Slot gleichzeitig (Hauptmodell vs. Vision-Modell), die Testanfragen hingen, Load-Average auf dem Server ging auf über 10. Kein Code-Fehler, reine Ressourcen-Konkurrenz (dasselbe bekannte Muster wie beim Vision-Modell schon in frueheren Sessions). Getestet wurde deshalb nur bis zur Speicherebene: `aliasId` landet korrekt an der richtigen Nachricht in `chat_history.jsonl` (`Mensch`-Nachricht traegt die Mensch-`aliasId`, `Gnom`-Nachricht die Gnom-`aliasId`). Die eigentliche Live-Verifikation (verwischt das Modell jetzt wirklich weniger?) steht noch aus — nachzuholen sobald der Ollama-Slot wieder frei ist.

**Was ich mir daraus merke:** bei einem geteilten, knappen Ressourcen-Slot (hier: ein Ollama-Modell fuer alles) lohnt es sich, vor einem Live-Test kurz zu pruefen ob gerade jemand anders ihn braucht — sonst wird ein einfacher Funktionstest ungewollt zum Konkurrenzkampf um Rechenzeit, und ein eigentlich harmloses Timeout sieht aus wie ein Bug.
