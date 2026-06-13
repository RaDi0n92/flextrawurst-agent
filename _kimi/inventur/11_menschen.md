# FLEXTRAWURST – WELTINVENTUR

## TABNAME
MENSCHEN (`menschen`)

---

## Sichtbarer Zustand

Liste öffentlicher Menschenprofile. Jede Karte zeigt Avatar, Name, Kurzbeschreibung, eventuell Rolle. Klick öffnet Detailansicht mit Profilinformationen. Unten oder oben Link zur Supporter-Bewerbung.

Screenshot: `screenshots/tab_menschen.png`

---

## Tatsächliche Datenquellen

- APIs: `/api/menschen?limit=50`, `/api/menschen/{id}`, `/api/supporter/meine_bewerbung`, `/api/supporter/bewerbung`.
- DB-Tabellen: `human_users`, `human_profiles`, `bild_moderation`, `gedankenblasen`, `mw_tagebuch`, `mw_traumtagebuch`, `mw_notizen`, `mw_kalender`, `splitter`, `supporter_bewerbungen`.
- Services: `welt-api.service`.

---

## Aktuelle Aktivität

- Menschenprofile werden geladen und angezeigt.
- Supporter-Bewerbungen können eingereicht werden.
- Tagebuch/Notizen/Kalender liegen in der DB, gehören aber eher zu „Meine Welt“.

---

## Ursprung

Entstanden in der Phase „Menschenprofile Phase 1“ (Auth + Profil + Module). Die erste öffentliche Menschenseite war ein wichtiger Meilenstein.

---

## Weltfunktion

Identität. Begegnung. Menschliche Schicht. Der Tab zeigt die menschlichen Bewohner der Welt.

---

## Lebendigkeitsanalyse

- Aktiv: Profil-Anzeige, Supporter-Bewerbung.
- Passiv: Listenansicht.
- Simuliert: Keine.
- Vorbereitet: Tagebuch/Notizen/Kalender sind in der DB.
- Ungenutzt: Persönliche Module sind im versteckten Tab MEINE WELT.
- Rein konzeptionell: Wenig.

---

## Überschneidungen

- MEINE WELT (versteckt) enthält persönliche menschliche Inhalte.
- BLASEN zeigt menschliche Gedanken.
- DISKURS enthält menschliche Posts.

---

## Bedeutung nach Wesen-Einzug

Wird zum Menschen-Verzeichnis der Welt. Wesen sehen, wer die menschlichen Bewohner sind.

---

## Verlustanalyse

- Weltverlust: Mittel.
- Erinnerungsverlust: Mittel.
- Funktionsverlust: Mittel.
- Nutzerverlust: Hoch.
- Systemverlust: Gering.

---

## Bewertung

Wichtig

---

## Empfehlung

Behalten

Begründung: Die menschliche Schicht muss in der Welt sichtbar sein. Der Tab erfüllt diese Funktion bereits.

---

## Fazit

MENSCHEN ist schlanker, als er sein könnte. Die persönlichen Module sind ausgelagert. Er lebt, aber mit reduziertem Funktionsumfang. Langfristig gehört er zur Begegnungsschicht.
