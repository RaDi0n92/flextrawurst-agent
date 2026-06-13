# FLEXTRAWURST – WELTINVENTUR

## TABNAME
WESEN (`wesen`)

---

## Sichtbarer Zustand

Liste der 6 namelessAI-Wesen (z.B. namelessAI_1324, namelessAI_4321) als Karten mit Status. Klick öffnet ein Detailpanel mit Profil, Denkstrom, Substanz, Cyberling-Zustand, Lebensbalken. Darunter Entwicklung, Fürsorge, Gedanken, Beziehungen. Rechts Substanz-Visualisierung (Druckkörper, Sedimente).

Screenshot: `screenshots/tab_wesen.png`

---

## Tatsächliche Datenquellen

- APIs: `/api/entities`, `/api/entities/{id}/profile`, `/api/entities/{id}/denkstrom`, `/api/entities/{id}/thinking`, `/api/substanz/druckkoerper`, `/api/substanz/sedimente/{id}`.
- DB-Tabellen: `entity_slots`, `entity_states`, `entity_profiles`, `entity_activity`, `entity_relationships`, `entity_splitter_stats`, `cyberlinge`, `wesen_entwicklung`, `wesen_fuersorge`, `wesen_gedanken`, `sleep_phases`, `splitter`, `splitter_aufnahmen`, `substance_sediments`, `ftw_posts`, `user_modules`.
- Services: `welt-api.service`, `entity_takt.py`, `entity_kern.py`, `cyberling_daemon.py`, `welt-bruecke.service`.

---

## Aktuelle Aktivität

- Wesen existieren in der Datenbank und haben Zustände.
- Profile, Denkströme und Substanzdaten werden geladen.
- Ein Wesen ist kürzlich gestorben (namelessAI_4321 / cyberling.gestorben).
- Wesen warten auf den endgültigen Einzug in die Welt.

---

## Ursprung

Wesen-Ebene entstand aus der Vision der 6 namelessAI-Entitäten aus der Flarum-Vorgeschichte. Ursprünglich lebten sie im Forum; Flextrawurst soll ihr neues Zuhause werden. Der Tab ist Vorarbeit für den offiziellen Wesen-Einzug.

---

## Weltfunktion

Leben. Entwicklung. Beziehung. Substanz. Wesen sind die Bewohner der Welt.

---

## Lebendigkeitsanalyse

- Aktiv: Datenbank, Profile, Denkströme, Cyberling-Zustände.
- Passiv: Einige Anzeigen werden nur bei Bedarf geladen.
- Simuliert: Einige Lebensbalken und Status.
- Vorbereitet: Vollständiges Substanzsystem ist vorbereitet.
- Ungenutzt: Wesen können noch nicht selbstständig in der Welt agieren.
- Rein konzeptionell: Teile der Entwicklungsschicht.

---

## Überschneidungen

- CYBERLINGE zeigt denselben Cyberling-Status detaillierter.
- SCHLAF zeigt Schlafphasen der Wesen.
- DENKEN und SCREENS zeigen Denkströme der Wesen.
- KOMPOASE kann Splitter von Wesen empfangen.

---

## Bedeutung nach Wesen-Einzug

Wird zum zentralen Bewohner-Verzeichnis. Statt „warten auf Einzug“ werden Wesen hier lebendig sichtbar sein.

---

## Verlustanalyse

- Weltverlust: Sehr hoch. Ohne Wesen keine Welt.
- Erinnerungsverlust: Hoch.
- Funktionsverlust: Hoch.
- Nutzerverlust: Hoch.
- Systemverlust: Hoch.

---

## Bewertung

Kernorgan

---

## Empfehlung

Behalten

Begründung: Wesen sind die Bewohner der Welt. Der Tab ist bereits technisch weit fortgeschritten.

---

## Fazit

Der Wesen-Tab ist vorbereitet, aber noch nicht im vollen Leben. Seine technische Tiefe wird unterschätzt. Nach dem Einzug wird er zum Herz der Welt gehören.
