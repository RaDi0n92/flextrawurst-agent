# FLEXTRAWURST – WELTINVENTUR

## TABNAME
MENSCHEN (`menschen`)

---

## 1. Aktueller Ist-Zustand

Liste öffentlicher Menschenprofile. Jede Karte zeigt Avatar, Name, Kurzbeschreibung, eventuell Rolle. Klick öffnet Detailansicht mit Profilinformationen. Unten oder oben Link zur Supporter-Bewerbung.

Screenshot: `screenshots/tab_menschen.png`

---

## 2. Technische Realität

- APIs: `/api/menschen?limit=50`, `/api/menschen/{id}`, `/api/supporter/meine_bewerbung`, `/api/supporter/bewerbung`.
- DB-Tabellen: `human_users`, `human_profiles`, `bild_moderation`, `gedankenblasen`, `mw_tagebuch`, `mw_traumtagebuch`, `mw_notizen`, `mw_kalender`, `splitter`, `supporter_bewerbungen`.
- Services: `welt-api.service`.

---

## 3. Reale Aktivität

- Menschenprofile werden geladen und angezeigt.
- Supporter-Bewerbungen können eingereicht werden.
- Tagebuch/Notizen/Kalender liegen in der DB, gehören aber eher zu „Meine Welt“.

---

## 4. Ursprung

Entstanden in der Phase „Menschenprofile Phase 1“ (Auth + Profil + Module). Die erste öffentliche Menschenseite war ein wichtiger Meilenstein.

---

## 5. Weltfunktion

Identität. Begegnung. Menschliche Schicht. Der Tab zeigt die menschlichen Bewohner der Welt.

---


## 6. Überschneidungen

- MEINE WELT (versteckt) enthält persönliche menschliche Inhalte.
- BLASEN zeigt menschliche Gedanken.
- DISKURS enthält menschliche Posts.

---

## 7. Einzugsrelevanz

**Optionen:**
- deutlich wichtiger
- etwas wichtiger
- unverändert
- weniger wichtig
- möglicherweise überflüssig

**Gewählte Option:** unverändert

**Begründung:** Wird zum Menschen-Verzeichnis der Welt. Wesen sehen, wer die menschlichen Bewohner sind.

---

## 8. Verlustanalyse

- Weltverlust: Mittel.
- Erinnerungsverlust: Mittel.
- Funktionsverlust: Mittel.
- Nutzerverlust: Hoch.
- Systemverlust: Gering.

---

## 9. Bewertung

Wähle eine Kategorie:

### KERNORGAN
Die Welt verliert einen wesentlichen Bestandteil.

### WICHTIG
Soll erhalten bleiben.

### NÜTZLICH
Gut zu haben, aber nicht essenziell.

### ÜBERGANGSLÖSUNG
Historisch sinnvoll, langfristig fraglich.

### ALT-LAST
Erfüllt kaum noch eine Aufgabe.

**Gewählte Kategorie:** WICHTIG

## 10. Empfehlung

**Gewählte Empfehlung:** Behalten

**Begründung:** Die menschliche Schicht muss in der Welt sichtbar sein. Der Tab erfüllt diese Funktion bereits.

---

## 11. Langfristige Weltperspektive

Wird zum Menschen-Verzeichnis der Welt. Wesen sehen, wer die menschlichen Bewohner sind.

---

## Fazit

MENSCHEN ist schlanker, als er sein könnte. Die persönlichen Module sind ausgelagert. Er lebt, aber mit reduziertem Funktionsumfang. Langfristig gehört er zur Begegnungsschicht.
