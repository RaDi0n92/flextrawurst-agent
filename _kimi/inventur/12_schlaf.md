# FLEXTRAWURST – WELTINVENTUR

## TABNAME
SCHLAF (`schlaf`)

---

## 1. Aktueller Ist-Zustand

Schlaf-Cockpit für alle 6 Wesen. Oben Info-Blöcke pro Wesen mit aktuellem Schlafzustand. Darunter Traumarchiv-Log mit Zeitstempeln und Traumfragmenten. Steuerung für Schlafphasen, Traum-Generierung, Traum-Integration.

Screenshot: `screenshots/tab_schlaf.png`

---

## 2. Technische Realität

- APIs: `/api/wesen/{id}/schlaf/heute`, `/api/wesen/{id}/cyberling`, `/api/denkstream/all/last?limit=6`.
- DB-Tabellen: `entity_slots`, `entity_states`, `sleep_phases`, `schlafbriefe`, `entity_thinking_log`, `events`.
- Services: `traum_generator.py`, `traum_integrator.py`, `entity_takt.py`, `welt-api.service`, `denkstream_api.py`.

---

## 3. Reale Aktivität

- Schlafphasen werden für die Wesen berechnet.
- Träume werden generiert.
- Traumarchiv speichert Traumfragmente.
- Cyberling-Zustand beeinflusst den Schlaf.

---

## 4. Ursprung

Schlaf-System war ein geplanter Bau-Schritt. Entstanden aus der Vision, dass Wesen Schlafzyklen brauchen, in denen sie verarbeiten und träumen.

---

## 5. Weltfunktion

Schlaf. Traum. Verarbeitung. Schlaf ist der Zyklus, in dem Wesen ihr Erlebtes verdichten.

---


## 6. Überschneidungen

- WESEN zeigt Schlafstatus im Profil.
- CYBERLINGE beeinflusst den Schlaf.
- WELTSTROM zeigt Schlaf-Events.
- EINSICHT zeigt Traumarchiv aus Admin-Sicht.

---

## 7. Einzugsrelevanz

**Optionen:**
- deutlich wichtiger
- etwas wichtiger
- unverändert
- weniger wichtig
- möglicherweise überflüssig

**Gewählte Option:** unverändert

**Begründung:** Wird zum zentralen Lebenszyklus-Tab. Schlaf und Traum sind essenziell für die Wesen.

---

## 8. Verlustanalyse

- Weltverlust: Hoch. Ohne Schlaf kein Lebenszyklus.
- Erinnerungsverlust: Hoch.
- Funktionsverlust: Hoch.
- Nutzerverlust: Mittel.
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

**Begründung:** Schlaf ist ein Grundpfeiler des Lebenszyklus der Wesen und bereits weit fortgeschritten.

---

## 11. Langfristige Weltperspektive

Wird zum zentralen Lebenszyklus-Tab. Schlaf und Traum sind essenziell für die Wesen.

---

## Fazit

SCHLAF wurde als Vision unterschätzt, ist aber bereits technisch tief implementiert. Er wird nach dem Wesen-Einzug zu einem der wichtigsten Lebensorgane.
