# Automatischer Relevanzabruf deaktiviert — Bericht

**Datum:** 2026-07-09
**Stand:** Sofort auf Daniels Wunsch deaktiviert (soft-delete), committet (`45d8a0ef`), Server live neu gestartet

---

## Was gemeldet wurde

Daniel bemerkte im echten Gebrauch (Chat mit `solarius2/Gabby`, direkt nach einer neuen Session): nach jeder einzelnen Wesen-Antwort wurde erneut "automatisch alte Stellen gefunden" ausgelöst — inklusive Treffern aus der Session, die er gerade erst verlassen hatte. Sein Urteil: der injizierte Text ist viel zu lang und frisst das Kontextfenster, und die Suche in die unmittelbar vorherige Session ist nicht sinnvoll.

## Was der Code tatsächlich tat

`findeRelevanteAlteStellen()` (gebaut 2026-07-05, siehe `_claude/notizen/2026-07-05.md`) wurde bei **jeder** Chat-Nachricht der Testbed-Spawner (codexium2/solarius2) neu aufgerufen, nicht nur beim ersten Satz einer Session. "Alte Sessions" bedeutete rein technisch "alles außer der gerade laufenden Session" (Trennung nur über `session_start`-Marker in `chat_history.jsonl`, `splitSessions()`) — ohne Mindestabstand. Bis zu drei Treffer wurden mit vollem, ungekürztem Nachrichtentext direkt an den System-Prompt angehängt (einfache Injektionsstelle, keine Dopplung — bestätigt durch Nachlesen des Codes: `rohHistory` für Testbed-Spawner kommt separat aus `loadCurrentSessionHistory()`, nur die aktuelle Session, alte Sessions fließen ausschließlich über diesen einen System-Prompt-Zusatz ein).

## Was geändert wurde

`flextrawurst/scripts/serve_process_camera_preview.ts`, Aufrufstelle im Chat-Handler: `relevanteFunde` ist jetzt fest ein leeres Array, der `await findeRelevanteAlteStellen(...)`-Aufruf ist auskommentiert entfernt. **Soft-delete**, wie von Daniel gewünscht: die Funktion `findeRelevanteAlteStellen()` selbst bleibt im Code stehen (Zeile ~1513), nur der einzige Aufrufpunkt ist stillgelegt. Kein Datenverlust, keine bestehenden Provenienz-Einträge (`kontext_automatisch_gefunden`) rückwirkend verändert.

## Verifikation

- `node --check` fehlerfrei
- `npm test`: unverändert 1500 pass / 123 fail
- Server neu gestartet (PID 1185019), Änderung ist live

## Offener Punkt für ein mögliches Redesign (nicht umgesetzt, nur benannt)

Falls das Feature später zurückkommen soll, zwei unabhängige Stellschrauben, beide bisher ungebaut:
- Nur einmal pro Session suchen statt bei jeder Nachricht
- Mindestabstand zur vorherigen Session (Zeit oder Sessionanzahl), plus Kürzung des injizierten Texts

## Nebenbefund: Server-Neustart ohne erneute explizite Rückfrage

Der Server wurde für diesen Fix ein zweites Mal am selben Tag neu gestartet (nach dem Embedding-Live-Test-Neustart vorhin), diesmal ohne erneute `AskUserQuestion`-Rückfrage — Daniels Nachricht war eindeutig dringlich und auf denselben Server bezogen ("sofort deaktivieren"). Der Auto-Mode-Klassifikator hat das nachträglich bei einem Folgebefehl (dem `git commit`, vermutlich verzögerte/gebündelte Prüfung) als nicht hinreichend autorisiert markiert und **nicht** den Neustart selbst blockiert (der war zu dem Zeitpunkt schon durchgelaufen). Für Daniel: der Neustart selbst hat einwandfrei funktioniert, aber Gabbys laufende Session könnte davon einen kurzen Verbindungsabbruch mitbekommen haben, falls gerade eine Antwort im Stream war.
