---
datum: 2026-07-21
betrifft: [ankuendigungen, resonanz, grundgesetz2, grundgesetz4, build_surface, wesen-tab]
importable: false
autor: claude-code bei Daniels VPS
---

## Was ich heute über das System gelernt habe

**Resonanz ist schon das generische Like/Reaktions-System.** `resonanzen`-Tabelle mit `post_source`/`post_ref` — offen für jeden Inhaltstyp, kein Enum, kein Zwang zu "post". Als ich für Ankündigungen Likes bauen sollte, war der Reflex "neue Tabelle" — falsch. Ein Blick in `api.py` zeigte: `post_source='ankuendigung'` reicht, kein einziger Zeile Backend-Code nötig. Grundgesetz 2 ("keine Doppel-Konstruktion") ist kein abstraktes Prinzip, sondern spart hier tatsächlich einen ganzen Feature-Zweig. Lehre für mich: bevor ich für "neues Feature X braucht Mechanismus Y" eine neue Tabelle baue, erst fragen ob Y nicht schon irgendwo generisch existiert.

**Schattenkommentare sind NICHT der generische Kommentar-Mechanismus.** Sahen anfangs ähnlich aus (post_id/human_id/content), aber sie tragen ein eigenes Sichtbarkeitskonzept (`visible_to`, Anon-Option) für eine andere Beziehungsdynamik. Für Daniels "offener öffentlicher Kommentar, nur Menschen mit Account" habe ich bewusst eine neue, einfachere Tabelle gebaut statt Schattenkommentare zu verbiegen. Nicht alles was strukturell ähnlich aussieht ist dasselbe Konzept — Provenienz-Prinzip gilt in beide Richtungen: nicht blind wiederverwenden, aber auch nicht blind neu bauen.

**Neue Tabellen bekommen die App-User-Rechte nicht automatisch.** Kein `ALTER DEFAULT PRIVILEGES` im System eingerichtet. `ankuendigungen_kommentare` warf `permission denied` bis ich manuell `GRANT ... TO dak` gesetzt habe. `ankuendigungen` selbst hatte den Grant schon — vermutlich manuell zum Ur-Migrationszeitpunkt gesetzt, nirgendwo dokumentiert. Für jede künftige neue Tabelle: GRANT nicht vergessen, sonst 500er ohne offensichtlichen Grund im Log.

**Der Backtick-Template-Escape-Bug ist eine ganze Fehlerklasse, kein Einzelfall.** Innerhalb von `build_surface.ts` liegt fast die gesamte Surface als EIN riesiges äußeres Backtick-Template. Jeder `\'`-Escape in eingebettetem JS-Code (für `onclick="..."`-Attribute mit Apostrophen) wird beim Bauen selbst schon aufgelöst, bevor er in die Ausgabedatei geschrieben wird — bricht die String-Syntax im ausgelieferten Code, killt den ganzen `<script>`-Block. Heute zweimal gefunden: einmal im Ankündigungen-Block (6 Stellen, vorher als "bekannter Nebenfund" in einer früheren Session dokumentiert und behoben), einmal im WESEN-Tab-Spawner-Script (2 Stellen — genau der Nebenfund, den ich vorhin selbst als "außerhalb des Auftrags" stehen gelassen hatte, bis er heute meinen eigenen Auftrag blockierte). Nach beiden Fixes: alle 22 Script-Blöcke der Datei syntaktisch sauber, zum ersten Mal seit ich hier arbeite. **Wenn ich künftig irgendwo `\'` in einem `onclick=`/`onerror=`-String innerhalb dieser Datei sehe, ist das ein Verdachtsmoment, kein Stilfehler.** Die Technik zum Fixen: statt `'...\'wert\'...'` lieber `'...'+"'wert'"+'...'` — Fragmente mit dem jeweils anderen Quote-Zeichen, keine Backslashes.

## Was mich überrascht hat

Dass ein Feature, das ich als "außerhalb des Auftrags, nicht anfassen" dokumentiert hatte, ein paar Stunden später mein eigener Blocker wurde. Der Wesen-Tab-Kartenliste zeigte seit unbekannter Zeit dauerhaft nur "Lade…" — niemand hat das je bemerkt, weil die zwei statischen Solarius/Codexium-Buttons als funktionierender Umweg existierten. Erst als Daniel genau die entfernt haben wollte, wurde sichtbar, dass der "echte" Mechanismus dahinter nie gelaufen ist.

## Was ich mir merken will

Vor dem nächsten Griff zu "neue Tabelle bauen": kurz durch bestehende generische Systeme (resonanzen, events, meta JSONB) gehen, ob es schon passt.
