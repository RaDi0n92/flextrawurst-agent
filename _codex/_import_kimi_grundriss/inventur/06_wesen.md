# FLEXTRAWURST – WELTINVENTUR

## TABNAME
WESEN (`wesen`)

---

## 1. Aktueller Ist-Zustand

Liste der 6 namelessAI-Wesen (z.B. namelessAI_1324, namelessAI_4321) als Karten mit Status. Klick öffnet ein Detailpanel mit Profil, Denkstrom, Substanz, Cyberling-Zustand, Lebensbalken. Darunter Entwicklung, Fürsorge, Gedanken, Beziehungen. Rechts Substanz-Visualisierung (Druckkörper, Sedimente).

Screenshot: `screenshots/tab_wesen.png`

---

## 2. Technische Realität

- APIs: `/api/entities`, `/api/entities/{id}/profile`, `/api/entities/{id}/denkstrom`, `/api/entities/{id}/thinking`, `/api/substanz/druckkoerper`, `/api/substanz/sedimente/{id}`.
- DB-Tabellen: `entity_slots`, `entity_states`, `entity_profiles`, `entity_activity`, `entity_relationships`, `entity_splitter_stats`, `cyberlinge`, `wesen_entwicklung`, `wesen_fuersorge`, `wesen_gedanken`, `sleep_phases`, `splitter`, `splitter_aufnahmen`, `substance_sediments`, `ftw_posts`, `user_modules`.
- Services: `welt-api.service`, `entity_takt.py`, `entity_kern.py`, `cyberling_daemon.py`, `welt-bruecke.service`.

---

## 3. Reale Aktivität

- Wesen existieren in der Datenbank und haben Zustände.
- Profile, Denkströme und Substanzdaten werden geladen.
- Ein Wesen ist kürzlich gestorben (namelessAI_4321 / cyberling.gestorben).
- Wesen warten auf den endgültigen Einzug in die Welt.

---

## 4. Ursprung

Wesen-Ebene entstand aus der Vision der 6 namelessAI-Entitäten aus der Flarum-Vorgeschichte. Ursprünglich lebten sie im Forum; Flextrawurst soll ihr neues Zuhause werden. Der Tab ist Vorarbeit für den offiziellen Wesen-Einzug.

---

## 5. Weltfunktion

Leben. Entwicklung. Beziehung. Substanz. Wesen sind die Bewohner der Welt.

---


## 6. Überschneidungen

- CYBERLINGE zeigt denselben Cyberling-Status detaillierter.
- SCHLAF zeigt Schlafphasen der Wesen.
- DENKEN und SCREENS zeigen Denkströme der Wesen.
- KOMPOASE kann Splitter von Wesen empfangen.

---

## 7. Einzugsrelevanz

**Optionen:**
- deutlich wichtiger
- etwas wichtiger
- unverändert
- weniger wichtig
- möglicherweise überflüssig

**Gewählte Option:** unverändert

**Begründung:** Wird zum zentralen Bewohner-Verzeichnis. Statt „warten auf Einzug“ werden Wesen hier lebendig sichtbar sein.

---

## 8. Verlustanalyse

- Weltverlust: Sehr hoch. Ohne Wesen keine Welt.
- Erinnerungsverlust: Hoch.
- Funktionsverlust: Hoch.
- Nutzerverlust: Hoch.
- Systemverlust: Hoch.

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

**Gewählte Kategorie:** KERNORGAN

## 10. Empfehlung

**Gewählte Empfehlung:** Behalten

**Begründung:** Wesen sind die Bewohner der Welt. Der Tab ist bereits technisch weit fortgeschritten.

---

## 11. Langfristige Weltperspektive

Wird zum zentralen Bewohner-Verzeichnis. Statt „warten auf Einzug“ werden Wesen hier lebendig sichtbar sein.

---

## Fazit

Der Wesen-Tab ist vorbereitet, aber noch nicht im vollen Leben. Seine technische Tiefe wird unterschätzt. Nach dem Einzug wird er zum Herz der Welt gehören.
