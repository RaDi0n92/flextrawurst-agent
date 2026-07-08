# FLARUM-STOPP — Bericht
**Datum:** 2026-07-09
**Stand:** Ampel GRÜN für Baustein 1 (Post-Sperre aktiv), REST offen

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

### Baustein 3 — Umgedrehter Neugier-Dienst (OFFEN)

Neuer, separater Dienst — fragt zuerst was sich zu lesen lohnt (egal was,
egal wann, egal wozu), liest dann live/chunkweise (nicht aus dem Vault),
Zyklus: Lesen → Entscheiden (vertiefen / verlassen+neu wählen) → bewusstes
Kontext-Entfernen. Schreibt nie nach Flarum. Nutzt den geupgradeten Container.
Sagt dem Wesen explizit: kein Perfektionsanspruch, kein Erwartungsdruck,
Scheitern ist normal und gewollt, Ziel ist eine eigene Container-Routine zu
erproben.

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

### Baustein 5 — Postgres-Spiegel (OFFEN)

Index/Spiegel-Tabelle über die Protokolldateien (Grundgesetz 1: `meta JSONB`,
durchsuchbar), damit flarumstyler live/interaktiv abfragen kann ohne Dateien
zu parsen.

### Baustein 6 — Zwei neue Tabs in flarumstyler (OFFEN)

Ein Live-Organ-Tab (wer tut gerade was, seit wann, Entscheidungen, lesbare
Inhalte, interaktiv/filterbar) und ein eigener Tab zum Log-Lesen.

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
  ○ Baustein 3  Umgedrehter Neugier-Dienst offen
  ● Baustein 4  Deterministisches Protokoll FERTIG
  ○ Baustein 5  Postgres-Spiegel          offen
  ○ Baustein 6  flarumstyler-Tabs         offen
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
