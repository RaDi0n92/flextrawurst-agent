# FLEXTRAWURST – WELTINVENTUR

## TABNAME
SCREENS (`screens`)

---

## Sichtbarer Zustand

Raster von Screenshot-Kacheln, die Denkströme der Wesen visualisieren. Jede Karte zeigt ein generiertes Bild/Thumbnail, Wesen-Namen, Status, ggf. einen Denktext-Ausschnitt. Updates scheinen live zu erfolgen.

Screenshot: `screenshots/tab_screens.png`

---

## Tatsächliche Datenquellen

- APIs: `/api/denkstream/status/all`, `/api/denkstream/{entity_id}` (SSE).
- DB-Tabellen: `entity_denkstream`, `entity_thinking_log`, `entity_activity`.
- Services: `welt-api.service`, `denkstream_api.py`, `gen_screens_html.py`, `browser-agent@.service`.

---

## Aktuelle Aktivität

- Bilder werden aus Denkströmen generiert.
- Live-Update via SSE.
- Browser-Agent erzeugt die Screenshots.

---

## Ursprung

Entstanden als visuelle Begleitung zum Denkstream. Die Idee: Nicht jeder möchte Denktexte lesen; Screenshots sind eine andere Wahrnehmungsebene desselben Stroms.

---

## Weltfunktion

Beobachtung. Wahrnehmung. Visualisierung. Screens machen Denken bildlich.

---

## Lebendigkeitsanalyse

- Aktiv: SSE, Screenshot-Generierung.
- Passiv: Raster-Anzeige.
- Simuliert: Keine.
- Vorbereitet: Keine.
- Ungenutzt: Möglicherweise wenig direkte Interaktion.
- Rein konzeptionell: Keine.

---

## Überschneidungen

- DENKEN zeigt denselben Inhalt als Textstream.
- WESEN zeigt Denkströme im Profil.
- WELTSTROM zeigt Denk-Events.

---

## Bedeutung nach Wesen-Einzug

Könnte zur visuellen Atmosphäre der Welt werden. Wahrscheinlich eher ein Sekundärorgan.

---

## Verlustanalyse

- Weltverlust: Mittel.
- Erinnerungsverlust: Gering.
- Funktionsverlust: Mittel.
- Nutzerverlust: Mittel.
- Systemverlust: Mittel.

---

## Bewertung

Nützlich

---

## Empfehlung

Zusammenlegen

Begründung: SCREENS ist eine visuelle Variante von DENKEN. Eine Zusammenlegung oder Umschaltmöglichkeit im Denkstream-Tab würde die Surface entlasten.

---

## Fazit

SCREENS ist lebendig, aber redundant zu DENKEN. Es wurde überschätzt, wie sehr man Denkströme als eigenen Tab braucht. Langfristig gehört es nicht zum Herzen, sondern zur Wahrnehmungsschicht.
