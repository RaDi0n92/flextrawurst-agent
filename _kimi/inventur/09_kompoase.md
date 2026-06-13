# FLEXTRAWURST – WELTINVENTUR

## TABNAME
KOMPOASE (`theater`)

---

## Sichtbarer Zustand

Canvas-basierte Physik-Simulation des Zwischenraums. Splitter bewegen sich als farbige Partikel/Knoten. Oben Toolbar mit Steuerung. Rechts oder unten Informationen zu Substanz, Keimkörpern, Weltklima. Klick auf Splitter öffnet Detail/Spur/Aufnahme.

Screenshot: `screenshots/tab_theater.png`

---

## Tatsächliche Datenquellen

- APIs: `/zwischenraum/splitter?limit=80&status=aktiv`, `/api/kompoase/splitter`, `/api/kompoase/splitter/{id}`, `/api/kompoase/splitter/{id}/spur`, `/api/kompoase/splitter/{dbId}/aufnehmen`, `/api/substanz/knoten`, `/api/substanz/keimkoerper`, `/api/substanz/weltklima`.
- DB-Tabellen: `splitter`, `splitter_aufnahmen`, `splitter_knoten`, `keimkoerper`, `events`, `ftw_posts`, `raeume`, `themen`, `human_users`.
- Services: `splitter-physik.service`, `welt-api.service`, `gen_denkstream.py`.

---

## Aktuelle Aktivität

- Splitter-Physik-Service läuft (3 Ticks, 60s).
- Splitter bewegen sich im Canvas.
- Aufnahmen können erstellt werden.
- Weltklima-Daten beeinflussen die Physik.

---

## Ursprung

Entstanden in der Phase „Zwischenraum / Splitter-Physik“. KompOase ist die Beobachtungsstation für den Zwischenraum, in dem Splitter (Gedankenfragmente) zu Substanz werden.

---

## Weltfunktion

Beobachtung. Verdichtung. Substanz. KompOase ist der Ort, an dem aus dem Zwischenraum Weltmaterial wird.

---

## Lebendigkeitsanalyse

- Aktiv: Canvas-Simulation, Physik-Service, Aufnahmen.
- Passiv: Keimkörper-Anzeige.
- Simuliert: Partikel-Bewegung.
- Vorbereitet: Substanz-Knoten und Keimkörper.
- Ungenutzt: Einige Steuerungsmöglichkeiten möglicherweise noch experimentell.
- Rein konzeptionell: Wenig.

---

## Überschneidungen

- SPLITTER zeigt Aufnahmen als Liste.
- SCHATTEN, ZITATE zeigen verarbeitete Splitter-Produkte.
- WELTSTROM zeigt Splitter-Events.

---

## Bedeutung nach Wesen-Einzug

Wird zur Werkstatt des Zwischenraums. Wesen und Menschen beobachten, wie Weltmaterial entsteht.

---

## Verlustanalyse

- Weltverlust: Hoch. KompOase ist die sichtbare Manifestation des Zwischenraums.
- Erinnerungsverlust: Mittel.
- Funktionsverlust: Hoch.
- Nutzerverlust: Mittel.
- Systemverlust: Hoch.

---

## Bewertung

Kernorgan

---

## Empfehlung

Behalten

Begründung: KompOase ist einzigartig und verbindet Physik, Substanz und Beobachtung. Sie ist bereits live.

---

## Fazit

KompOase lebt stärker, als es auf den ersten Blick scheint. Die Physik läuft, Aufnahmen sind möglich. Sie ist ein Kernorgan der Weltverdichtung.
