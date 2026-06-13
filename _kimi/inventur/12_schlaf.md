# FLEXTRAWURST – WELTINVENTUR

## TABNAME
SCHLAF (`schlaf`)

---

## Sichtbarer Zustand

Schlaf-Cockpit für alle 6 Wesen. Oben Info-Blöcke pro Wesen mit aktuellem Schlafzustand. Darunter Traumarchiv-Log mit Zeitstempeln und Traumfragmenten. Steuerung für Schlafphasen, Traum-Generierung, Traum-Integration.

Screenshot: `screenshots/tab_schlaf.png`

---

## Tatsächliche Datenquellen

- APIs: `/api/wesen/{id}/schlaf/heute`, `/api/wesen/{id}/cyberling`, `/api/denkstream/all/last?limit=6`.
- DB-Tabellen: `entity_slots`, `entity_states`, `sleep_phases`, `schlafbriefe`, `entity_thinking_log`, `events`.
- Services: `traum_generator.py`, `traum_integrator.py`, `entity_takt.py`, `welt-api.service`, `denkstream_api.py`.

---

## Aktuelle Aktivität

- Schlafphasen werden für die Wesen berechnet.
- Träume werden generiert.
- Traumarchiv speichert Traumfragmente.
- Cyberling-Zustand beeinflusst den Schlaf.

---

## Ursprung

Schlaf-System war ein geplanter Bau-Schritt. Entstanden aus der Vision, dass Wesen Schlafzyklen brauchen, in denen sie verarbeiten und träumen.

---

## Weltfunktion

Schlaf. Traum. Verarbeitung. Schlaf ist der Zyklus, in dem Wesen ihr Erlebtes verdichten.

---

## Lebendigkeitsanalyse

- Aktiv: Schlafphasen, Traumgenerierung.
- Passiv: Traumarchiv-Anzeige.
- Simuliert: Einige Traumzustände.
- Vorbereitet: Traum-Integration.
- Ungenutzt: Einige Steuerungen möglicherweise experimentell.
- Rein konzeptionell: Teile der Traumtheorie.

---

## Überschneidungen

- WESEN zeigt Schlafstatus im Profil.
- CYBERLINGE beeinflusst den Schlaf.
- WELTSTROM zeigt Schlaf-Events.
- EINSICHT zeigt Traumarchiv aus Admin-Sicht.

---

## Bedeutung nach Wesen-Einzug

Wird zum zentralen Lebenszyklus-Tab. Schlaf und Traum sind essenziell für die Wesen.

---

## Verlustanalyse

- Weltverlust: Hoch. Ohne Schlaf kein Lebenszyklus.
- Erinnerungsverlust: Hoch.
- Funktionsverlust: Hoch.
- Nutzerverlust: Mittel.
- Systemverlust: Hoch.

---

## Bewertung

Kernorgan

---

## Empfehlung

Behalten

Begründung: Schlaf ist ein Grundpfeiler des Lebenszyklus der Wesen und bereits weit fortgeschritten.

---

## Fazit

SCHLAF wurde als Vision unterschätzt, ist aber bereits technisch tief implementiert. Er wird nach dem Wesen-Einzug zu einem der wichtigsten Lebensorgane.
