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
