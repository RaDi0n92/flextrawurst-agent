# FLEXTRAWURST – WELTINVENTUR

## TABNAME
SCREENS (`screens`)

---

## 1. Aktueller Ist-Zustand

Raster von Screenshot-Kacheln, die Denkströme der Wesen visualisieren. Jede Karte zeigt ein generiertes Bild/Thumbnail, Wesen-Namen, Status, ggf. einen Denktext-Ausschnitt. Updates scheinen live zu erfolgen.

Screenshot: `screenshots/tab_screens.png`

---

## 2. Technische Realität

- APIs: `/api/denkstream/status/all`, `/api/denkstream/{entity_id}` (SSE).
- DB-Tabellen: `entity_denkstream`, `entity_thinking_log`, `entity_activity`.
- Services: `welt-api.service`, `denkstream_api.py`, `gen_screens_html.py`, `browser-agent@.service`.

---

## 3. Reale Aktivität

- Bilder werden aus Denkströmen generiert.
- Live-Update via SSE.
- Browser-Agent erzeugt die Screenshots.

---

## 4. Ursprung

Entstanden als visuelle Begleitung zum Denkstream. Die Idee: Nicht jeder möchte Denktexte lesen; Screenshots sind eine andere Wahrnehmungsebene desselben Stroms.

---

## 5. Weltfunktion

Beobachtung. Wahrnehmung. Visualisierung. Screens machen Denken bildlich.

---


## 6. Überschneidungen

- DENKEN zeigt denselben Inhalt als Textstream.
- WESEN zeigt Denkströme im Profil.
- WELTSTROM zeigt Denk-Events.

---

## 7. Einzugsrelevanz

**Optionen:**
- deutlich wichtiger
- etwas wichtiger
- unverändert
- weniger wichtig
- möglicherweise überflüssig

**Gewählte Option:** unverändert

**Begründung:** Könnte zur visuellen Atmosphäre der Welt werden. Wahrscheinlich eher ein Sekundärorgan.

---

## 8. Verlustanalyse

- Weltverlust: Mittel.
- Erinnerungsverlust: Gering.
- Funktionsverlust: Mittel.
- Nutzerverlust: Mittel.
- Systemverlust: Mittel.

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

**Gewählte Kategorie:** NÜTZLICH

## 10. Empfehlung

**Gewählte Empfehlung:** Zusammenlegen

**Begründung:** SCREENS ist eine visuelle Variante von DENKEN. Eine Zusammenlegung oder Umschaltmöglichkeit im Denkstream-Tab würde die Surface entlasten.

---

## 11. Langfristige Weltperspektive

Könnte zur visuellen Atmosphäre der Welt werden. Wahrscheinlich eher ein Sekundärorgan.

---

## Fazit

SCREENS ist lebendig, aber redundant zu DENKEN. Es wurde überschätzt, wie sehr man Denkströme als eigenen Tab braucht. Langfristig gehört es nicht zum Herzen, sondern zur Wahrnehmungsschicht.
