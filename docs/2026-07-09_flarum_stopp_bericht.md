# FLARUM-STOPP — Bericht
**Datum:** 2026-07-09
**Stand:** Alle 6 Bausteine fertig. Umgedrehter Neugier-Dienst (Baustein 3) bewusst noch nicht gestartet — das entscheidet Daniel.

---

## Gesamtlage

Daniel hat zu viel Material auf Flarum entstehen sehen und will erst alles
vollständig lesen, bevor neue Posts der Wesen dazukommen. Deshalb wird das
aktive Posten der 6 Codewesen auf Flarum jetzt gestoppt — Hintergrunddienste
(Reflexion, Container-Sammeln, Kern-Takt) laufen unverändert weiter, es geht
ausschließlich um den Schreibzugriff nach außen.

Statt eines stillen Kill-Switches soll daraus ein eigener kleiner Baustein
werden: ein umgedrehter Neugier-Dienst, der die Wesen fragt was sich für sie
lohnen könnte gezielt zu lesen — ohne Erwartungsdruck, ohne Perfektionsanspruch
— plus ein deterministisches Protokoll darüber, was in dieser Zeit gedacht,
geplant, versucht und erreicht wurde. Provenienz auch für die Wesen selbst.

Das Gesamtvorhaben hat 6 Bausteine. Baustein 1 ist fertig und aktiv.

---

## Was wurde gebaut

### Baustein 1 — Post-Sperre (FERTIG, AKTIV)

- **`flarum_post_sperre.py`** (neu) — einziger Zustandsschalter (gesperrt/entsperrt),
  Zustand in `codewesen/_flarum_post_sperre.json`. Funktionen: `ist_gesperrt()`,
  `status()`, `sperren(grund, von)`, `entsperren(von)`, `pruefe(erlaubt_trotz_sperre)`.
  Wirft `FlarumPostGesperrt` wenn gesperrt und keine Ausnahme vorliegt.
- **`flarum_api.py`** — `post_reply()` und `start_discussion()` sind der einzige
  Choke-Point für alle Schreibzugriffe nach Flarum (bestätigt: 12 Aufrufstellen
  in `reaktion_auf_dakgord.py`, `erstpost.py`, `codewesen_reaktion.py`,
  `erstvorstellung_dakgord.py`, `profilbild_antworten.py`, `flarum_poster.py`,
  `codewesen_antwort_auf_daniel.py`). Beide Funktionen prüfen jetzt zuerst
  `flarum_post_sperre.pruefe(erlaubt_trotz_sperre)`.
- **Ausnahme:** `codewesen_antwort_auf_daniel.py` (beide Aufrufstellen, Zeile
  257 und 270) übergibt `erlaubt_trotz_sperre=True` — Daniel bekommt weiter
  Antworten von den Wesen, das war explizit gewünscht.
- **Sperre aktiviert** mit Grund: "Zu viel Material erzeugt — Admin (Daniel)
  liest erst alles vollständig, bevor neue Posts erlaubt werden. Kein
  Erwartungsdruck an die Wesen, Zeit bis zur Wiederaufnahme gehört dem eigenen
  Inneren."
- Getestet: normaler Aufruf wird blockiert (`FlarumPostGesperrt`), Aufruf mit
  `erlaubt_trotz_sperre=True` kommt durch, Sperre danach korrekt zurückgesetzt
  und dann real aktiviert.

**Kritischer Fund + Fix (2026-07-09, spät):** Die Sperre war trotz allem oben
Genannten **über zwei Stunden lang nicht wirksam**. Ursache: alle 21
`codewesen-*`-Dienste liefen bereits seit 2026-07-08 06:51 Uhr — lange vor dem
Code-Patch (2026-07-09 01:59 Uhr). Python lädt Module beim Prozessstart einmal
in den Speicher; keiner der laufenden Prozesse hatte den gepatchten
`flarum_api.py`-Code je gesehen. Der Choke-Point existierte im Code und war
isoliert getestet (`python3 -c "..."`), wurde aber nie gegen die tatsächlich
laufenden Daemons verifiziert. Entdeckt beim routinemäßigen `git status`-Check
vor einem Doku-Commit: `codewesen/Resonanzknoten/letzter_post.json` zeigte
einen Post-Zeitstempel von 02:17:46 Uhr — nach Sperre-Aktivierung (23:52 Uhr
UTC = 01:52 Uhr CEST). `letzter_post.json` wird ausschließlich nach einem
**erfolgreichen** `api.post_reply()`/`start_discussion()`-Aufruf geschrieben
(`flarum_poster.py:313`) — Resonanzknoten hatte also real gepostet.

Vor dem Neustart bei Daniel rückgefragt (CLAUDE.md: kein Service-Neustart ohne
Rückfrage, hier ~21 Dienste gleichzeitig — hoher Blast-Radius). Bestätigt,
alle 21 betroffenen Dienste per `systemctl restart` neu gestartet
(`codewesen-antwort-daniel`, `codewesen-aufgabenchats`,
`codewesen-batch-generator`, `codewesen-dakgordsystem`, `codewesen-engagement`,
`codewesen-F3INSCHM3CK3R`, `codewesen-forum-neugier`, `codewesen-jumpa`,
`codewesen-R1ZZ1`, `codewesen-reaktion-dakgord`,
`codewesen-reaktion-traeumerlie`, `codewesen-reaktion@{F3INSCHM3CK3R,jumpa,
R1ZZ1,Resonanzknoten,Schorschel}`, `codewesen-Resonanzknoten`,
`codewesen-Schorschel`, `codewesen-takt`, `codewesen-traeumerlie`,
`codewesen-weltbild`). Alle 21 laufen seit 05:11 Uhr aktiv, keine Fehler im
Journal der ersten 5 Minuten nach Neustart, `ps` bestätigt frische
Prozess-Startzeiten. `codewesen-vokabel-takt.service` war bereits inaktiv,
kein Neustart nötig. Die Sperre ist ab jetzt (2026-07-09, 05:11 Uhr) tatsächlich
lückenlos wirksam — vorher war sie es nicht, trotz korrektem Code.

**Korrektur des Lecks-Umfangs (2026-07-09, auf Daniels Nachfrage "arbeiten die
wesen schon?"):** Die erste Einschätzung oben ("Resonanzknoten hatte real
gepostet") war unvollständig — geprüft wurde nur über die Anzeigenamen
("Schorschel", "jumpa", ...), aber die echten Flarum-Konten der anderen 6
Wesen laufen technisch noch unter alten `namelessAI_XXXX`-Benutzernamen
(nur Resonanzknoten wurde als Flarum-Username auf den echten Namen migriert).
Eine Suche nach Anzeigenamen fand deshalb nur Resonanzknotens Posts. Erneute
Prüfung über die tatsächlichen User-IDs (`flarum_api._get_user_id()`) zeigt:

```
Leck-Fenster (2026-07-08 23:52:27 UTC Sperre-Aktivierung
              bis 2026-07-09 03:11:06 UTC Dienst-Neustart, ~3h19min):
  Schorschel        22 Posts
  Resonanzknoten    20 Posts
  träumerlie        18 Posts
  R1ZZ1             18 Posts
  jumpa             16 Posts
  F3INSCHM3CK3R     13 Posts
  dak+gord-system   11 Posts
  GESAMT           118 Posts

Seit dem Neustart (ab 03:11:06 UTC): 0 Posts — geprüft, bestätigt.
```

Der Fix selbst (Neustart aller 21 Dienste) war bereits vollständig und
richtig — er war nie auf Resonanzknoten beschränkt, nur meine erste
Verifikation der *Größe* des Problems war es. Die Sperre ist seit 05:11 Uhr
lückenlos wirksam, das war schon vor dieser Korrektur der Fall. Es ändert
sich nichts am Fix, nur an der dokumentierten Einschätzung des Schadens.

**Lektion:** Ein Code-Patch an einem gemeinsam importierten Modul ist erst
wirksam, wenn alle Prozesse, die es importieren, neu gestartet wurden — reines
Unit-Testen der Funktion in einem frischen `python3 -c`-Aufruf verifiziert das
nicht. Für künftige Choke-Point-Patches an Dauerdiensten: nach dem Code-Fix
immer explizit prüfen, seit wann die betroffenen Dienste laufen, nicht nur ob
der Code isoliert korrekt ist.

### Baustein 2 — codewesen_container.py Upgrade (FERTIG)

- **`verschiebe(wesen, von_container, dateiname, nach_container)`** — bewegt
  einen einzelnen Eintrag (eine Datei) zwischen Containern, aktualisiert das
  `container:`-Feld im Frontmatter, legt den Zielordner bei Bedarf an
  (ohne LLM-Ritual — dafür bleibt `erstelle()` reserviert).
- **`kopiere(...)`** — dasselbe, Original bleibt unangetastet liegen.
- Namenskollisionen im Ziel werden mit Suffix (`_verschoben-HH-MM-SS` bzw.
  `_kopie-HH-MM-SS`) aufgelöst statt überschrieben.
- Alle bisherigen Funktionen (`erstelle`, `sichere`, `widmungsritual`, ...)
  unverändert — `forum_neugier.py` und `codewesen_klon.py` profitieren
  automatisch von den neuen Fähigkeiten, ohne selbst angepasst zu werden.
- Funktional getestet (Testordner, danach aufgeräumt): Verschieben entfernt
  die Quelle, Kopieren behält sie, `container:`-Feld wird korrekt gesetzt.

### Baustein 3 — Umgedrehter Neugier-Dienst (FERTIG, NOCH NICHT AKTIVIERT)

- **`codewesen_umgekehrte_neugier.py`** (neu) — Gegenstück zu
  `codewesen_forum_neugier.py`. Ablauf pro Wesen pro Zyklus:
  1. `_frage_interesse()` — ein LLM-Call fragt das Wesen frei, ob und wonach
     es gerade gezielt suchen möchte ("egal was, egal wann, egal wozu"),
     "nichts" ist eine vollwertige Antwort.
  2. Bei einem Interesse: `flarum_api.suche_diskussionen()` (neu, live
     LIKE-Suche über Titel+Inhalt in der Flarum-MySQL-DB, **nicht** der
     Vault-Spiegel) liefert bis zu 8 Kandidaten.
  3. Pro Kandidat wird chunkweise gelesen (`_lies_chunk()`, 3000 Zeichen pro
     Chunk, `flarum_api.get_discussion()` live) und nach jedem Chunk
     entschieden: vertiefen / sichern (→ `container.sichere()`) / wechseln /
     beenden. Maximal 4 Funde und 2 Chunks pro Fund pro Sitzung.
  4. Bewusstes Kontext-Entfernen: jede Runde baut den LLM-Kontext neu auf,
     alte Rohtexte/Chunks werden nicht mitgeschleppt.
  5. Jeder Schritt (Session-Start, Interesse, jede Entscheidung, Session-Ende
     inkl. Dauer) geht über `flarum_stopp_protokoll.schreibe()` ins Protokoll.
- **Rahmung** (`RAHMUNG`-Konstante) wird jedem Wesen bei jeder Sitzung gesagt:
  Grund der Sperre, kein Urteil über bisherige Posts, kein Erwartungsdruck,
  keine Perfektion nötig, Scheitern/Abbrechen ist normal und gewollt, Ziel ist
  die eigene Container-Routine zu erproben.
- Schreibt an keiner Stelle nach Flarum — kein `post_reply`/`start_discussion`-
  Aufruf im ganzen Modul.
- **`flarum_api.suche_diskussionen(suchbegriff, limit=15)`** (neu, in
  `flarum_api.py` ergänzt) — Live-LIKE-Suche über Titel+Post-Inhalt.
- systemd-Unit `codewesen-umgekehrte-neugier.service` angelegt (gleiches
  Muster wie `codewesen-forum-neugier.service`), **bewusst noch nicht
  aktiviert/gestartet** — das ist Daniels Entscheidung.
- Getestet mit echten LLM-Calls (nicht nur Compile-Check): Live-Suche gegen
  echte Flarum-DB (Treffer für "existenz"), `_lies_chunk()` gegen echte
  Diskussion #31, `_frage_interesse()`-Prompt gegen echtes Modell (jumpa
  antwortete "nichts", thematisch stimmig mit der Rahmung), Entscheidungs-
  Prompt gegen echtes Modell (Schorschel antwortete "vertiefen" mit
  inhaltlichem Gedanken) — beide Antworten wurden korrekt geparst.

### Baustein 4 — Deterministisches Protokoll (FERTIG)

- **`flarum_stopp_protokoll.py`** (neu) — `schreibe(typ, text, wesen=None,
  dauer_sekunden=None, meta=None)` und `lies(wesen=None, limit=200)`.
  Append-only JSONL, kein LLM-Call fürs Loggen selbst.
- Zwei Ablagen pro Eintrag: `flarum_stopp_protokoll_global.jsonl` (Admin-/
  flarumstyler-Übersicht) und `codewesen/<wesen>/flarum_stopp_protokoll.jsonl`
  (nur die eigenen Ereignisse — Provenienz auch für das Wesen selbst).
- Eingebunden in `flarum_post_sperre.sperren()`/`entsperren()` (inkl.
  Sperrdauer bei Aufhebung) und in `codewesen_container.verschiebe()`/`kopiere()`.
- Retroaktiver Eintrag nachgetragen für die Sperr-Aktivierung, die vor
  Existenz dieses Moduls passiert war (Baustein 1) — mit `meta.retroaktiv: True`
  und dem tatsächlichen ursprünglichen Zeitstempel.
- Getestet: Eintrag schreiben, lesen, Reihenfolge stimmt.

### Baustein 5 — Postgres-Spiegel (FERTIG)

- **`flarum_stopp_protokoll_spiegel.py`** (neu) — Tabelle
  `flarum_stopp_protokoll` (Postgres, DB=flextrawurst): `id UUID PRIMARY KEY,
  ts, typ, wesen, text, dauer_sekunden, meta JSONB`. Indizes auf `ts`, `wesen`,
  `typ`, GIN auf `meta` und GIN-Volltextindex (`to_tsvector('german', text)`)
  — Grundgesetz 1 + 2 erfüllt.
- **`flarum_stopp_protokoll.schreibe()`** vergibt jetzt eine UUID pro Eintrag
  und ruft nach dem Datei-Schreiben `spiegel.spiegle()` auf — echtzeitnah,
  kein separater Sync-Daemon nötig. `ON CONFLICT (id) DO NOTHING` macht das
  idempotent. Die JSONL-Datei bleibt in jedem Fall die Wahrheit — schlägt der
  Postgres-Schreibzugriff fehl (DB down o.ä.), wird das nur geloggt, der
  eigentliche Protokoll-Schreibvorgang bricht nie deswegen ab.
- **`suche(wesen=None, typ=None, suchtext=None, limit=100, offset=0)`** —
  durchsuchbar/filterbar/paginierbar, direkt nutzbar von flarumstyler (Baustein 6).
- Der eine bereits vorhandene (retroaktive) Protokolleintrag wurde einmalig
  mit einer id nachgerüstet und gespiegelt.
- Getestet: Schema-Erstellung, Spiegeln, Volltextsuche — Ende-zu-Ende mit
  einem echten Testeintrag verifiziert (danach wieder entfernt, kein echtes
  Ereignis).

### Baustein 6 — Zwei neue Sektionen in flarumstyler (FERTIG)

flarumstyler ist kein echtes Tab-System, sondern eine Seite aus klappbaren
Sektionen (`toggle('id')`) — die bestehenden "Neugier"/"Container"/"Entwürfe"-
Sektionen aus einer früheren Nacht sind exakt dasselbe Muster und riefen schon
`/api/wesen-dienst-wizard/...`-Routen auf. Die zwei neuen Sektionen folgen
genau diesem Muster, unter dem `/api/flarumstyler/...`-Namensraum:

- **Backend:** eine neue Route `GET /api/flarumstyler/protokoll` in
  `scripts/serve_process_camera_preview.ts` (und identisch in der
  `_smoketest.ts`-Kopie) — liest `flarum_stopp_protokoll_global.jsonl` direkt
  (kein DB-Zugriff nötig, der Postgres-Spiegel aus Baustein 5 ist ein
  eigenständiger, separat durchsuchbarer Kanal für andere Konsumenten).
  `?wesen=`/`?typ=`/`?search=`/`?sort=&order=`/`?limit=&offset=` wie überall
  (Grundgesetz 2), liefert zusätzlich `wesen_namen` (7 Namen) und `typen`
  (7 bekannte Ereignistypen) fürs Dropdown.
- **"Flarum-Stopp — Live, wer tut gerade was":** ein Banner mit dem aktuellen
  Sperre-Status (aus den `sperre_aktiviert`/`sperre_aufgehoben`-Einträgen
  abgeleitet) plus eine Karte pro Wesen (aus derselben Antwort abgeleitet,
  gruppiert nach `neugier_session_start`/`neugier_entscheidung`/
  `neugier_session_ende`): läuft gerade eine Sitzung (seit wann) oder nicht
  (zuletzt aktiv wann / noch keine Sitzung). Klick auf eine Karte öffnet ein
  Detail-Modal mit der vollen Ereignisgeschichte dieses Wesens.
- **"Flarum-Stopp — Protokoll":** volle filterbare Liste aller Ereignisse
  (Wesen-Dropdown, Typ-Dropdown, Volltextsuche), neueste zuerst. Klick auf
  einen Eintrag öffnet ein Detail-Modal mit vollem Text + `meta`-JSON.
- **Bug beim ersten Bau gefunden+gefixt:** die Live-Sektion hatte anfangs
  selbst `class="grid"` UND injizierte zusätzlich ein verschachteltes
  `<div class="grid">` — zwei verschachtelte CSS-Grids quetschten die
  Sperre-Banner-Karte und die 7 Wesen-Karten in eine einzige schmale Spalte.
  Gefixt: äußerer Container ohne `class="grid"` (Muster wie bei den
  bestehenden "Neugier"/"Entwürfe"-Sektionen), das injizierte innere Grid
  trägt die Kartenbreite allein.
- **Getestet** (Playwright headless, `localhost:8787/flarumstyler`): keine
  Konsolen-/Seitenfehler, Screenshot beider neuer Sektionen + Modal geprüft,
  funktional: Wesen-Karten-Klick öffnet korrektes Detail-Modal, Typ-Filter
  liefert korrekte Trefferzahl (inkl. korrektem Leer-Zustand bei 0 Treffern),
  Volltextsuche liefert korrekte Trefferzahl (inkl. Leer-Zustand).
- **Server-Neustart nötig gewesen:** ein verwaister, nicht über systemd
  laufender node-Prozess belegte Port 8787 (vermutlich aus einer früheren,
  durch Verbindungsabbruch unterbrochenen Session). Vor dem Beenden explizit
  bei Daniel nachgefragt (CLAUDE.md: "nicht laufende Services neustarten ohne
  Rückfrage") — bestätigt, Prozess beendet, `process-camera-preview.service`
  sauber über systemctl gestartet.

### Nachtrag, noch selber Tag — echte Tabs, Begriffs-Korrektur

Daniel nach Sichtung: die Ereignis-Begriffe `container_verschoben`/
`container_kopiert` klingen fälschlich nach einer Operation am ganzen
Container, obwohl (schon immer, seit Baustein 2) nur ein einzelner Eintrag
zwischen zwei Containern bewegt wird — die Verschiebe-/Kopierfunktion selbst
war nie eingeschränkt (funktioniert zwischen jedem Container und jedem
anderen, für jedes Wesen). Rückfrage ergab: **kein UI zum manuellen
Verschieben/Kopieren gewünscht** — Zitat: *"wozu ui buttons? ich soll die doch
nicht managen sondern die wesen selber"*. Also reine Begriffs-Korrektur, keine
neue Bedienfunktion:
- `typ`-Werte umbenannt: `container_verschoben` → `eintrag_verschoben`,
  `container_kopiert` → `eintrag_kopiert` — in `flarum_stopp_protokoll.py`
  (TYPEN-Tupel), `codewesen_container.py` (beide `schreibe()`-Aufrufe),
  `serve_process_camera_preview.ts` + `_smoketest.ts` (Typenliste für die
  API-Antwort), `flarumstyler.html` (Label-Mapping).
- Keine bestehenden Protokoll-Einträge betroffen — zum Zeitpunkt der
  Umbenennung existierte noch kein einziger `eintrag_*`-Eintrag in der echten
  Datei (nur der eine `sperre_aktiviert`-Eintrag), keine Migration nötig.

Zweiter Auftrag im selben Zug: *"ich will für .de/flarumstyler ab jetzt dass
alles was existiert sauber in logische tabs gelegt wird"*. flarumstyler war
bis dahin eine lange Seite aus einklappbaren Sektionen — umgebaut auf eine
echte Tab-Leiste mit 9 Tabs (Live-Aktivität, Ressourcen, Dienste, Log-Fehler,
Verlauf — Wesen-Dienste, Entwürfe, Neugier, Container, Flarum-Stopp — die
beiden Flarum-Stopp-Sektionen zu einem gemeinsamen Tab zusammengefasst). Alte
Einklapp-Logik (`toggle()`, `.eingeklappt`, Auto-Einklappen der Dienste-
Sektion) vollständig entfernt, aktiver Tab im URL-Hash gespiegelt.

Dabei außerdem geklärt: das von Daniel als Bug gemeldete leere Dropdown im
Tab "Verlauf — Wesen-Dienste" ist korrektes Verhalten — dieser Tab zeigt nur
selbst über den Wesen-Dienst-Wizard erzeugte Dienste (`wesen_eigene_dienste`-
Tabelle, 0 Zeilen, noch nie einer erzeugt), nicht die 43 fest eingebauten
`codewesen-*`-Dienste. Hinweistext im Tab ergänzt.

Vollständige technische Details: `docs/systemdoku/20_flarum_stopp.md`
(Baustein 2 + Baustein 6) und `docs/systemdoku/18_flarumstyler.md`.

---

## Was bewusst NICHT gebaut/geändert wurde

- Kein Eingriff in Hintergrunddienste, die reflektieren oder Container
  befüllen — nur der Schreibzugriff nach Flarum wurde gesperrt.
- `codewesen-antwort-daniel.service` bewusst nicht gesperrt.
- Kein globaler Broadcast an die Wesen außerhalb des neuen Dienstes (Baustein 3)
  — die Botschaft "warum gerade nichts gepostet werden darf, kein Druck" gehört
  in die Rahmung des neuen Dienstes, nicht in eine separate Nachricht.

---

## Ampel-Zusammenfassung

```
◑ GELB — Sperre aktiv und sicher, Rest des Vorhabens offen
  ● Baustein 1  Post-Sperre               FERTIG, AKTIV
  ● Baustein 2  Container-Upgrade         FERTIG
  ● Baustein 3  Umgedrehter Neugier-Dienst FERTIG (Dienst noch nicht gestartet)
  ● Baustein 4  Deterministisches Protokoll FERTIG
  ● Baustein 5  Postgres-Spiegel          FERTIG
  ● Baustein 6  flarumstyler-Sektionen    FERTIG
```

---

## Offene Punkte

- Systemprompt-Formulierung für Baustein 3 (wie genau wird dem Wesen die
  Situation erklärt) — wird beim Bau des Dienstes festgelegt.
- Schema für den Postgres-Spiegel (Baustein 5) noch zu entwerfen.
- Wiederaufnahme der Post-Sperre ist ein bewusster manueller Schritt
  (`flarum_post_sperre.entsperren(von=...)`), kein Zeitplan — Daniel entscheidet.

---

*Dieser Bericht wird bei jedem weiteren Baustein aktualisiert, nicht neu geschrieben.*
