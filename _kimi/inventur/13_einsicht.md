# FLEXTRAWURST – WELTINVENTUR

## TABNAME
EINSICHT (`einsicht`)

---

## 1. Aktueller Ist-Zustand

Admin-Einsichtskörper. Panorama-Ansicht mit mehreren Informationsblöcken: Entscheidungen, Liveticker, Traumarchiv, Lebensjournal, Human-Material, Life-Contracts, Organ-Hunger. Status-Anzeigen und Vitals. Ist nur mit Admin-Rechten vollständig nutzbar.

Screenshot: `screenshots/tab_einsicht.png`

---

## 2. Technische Realität

- APIs: `/api/admin/wesen-einsicht/entscheidungen`, `/api/admin/wesen-einsicht/entscheidungen/stats`, `/api/admin/wesen-einsicht/liveticker`, `/api/admin/wesen-einsicht/traumarchiv`, `/api/admin/wesen-einsicht/lebensjournal`, `/api/admin/wesen-einsicht/human-material`, `/api/admin/wesen-einsicht/life-contracts`, `/api/admin/wesen-einsicht/organ-hunger`.
- DB-Tabellen: `entity_thinking_log`, `events`, `ftw_posts`, `schlafbriefe`, `traumkandidaten_log`, `traumspuren`, `human_material_sources`.
- Services: `welt-api.service`, `weltkern-watchdog.service`, `entity_takt.py`.

---

## 3. Reale Aktivität

- Admin-Endpunkte liefern Daten.
- Liveticker zeigt Systemereignisse.
- Traumarchiv und Lebensjournal werden angezeigt.
- Human-Material und Consent werden verwaltet.

---

## 4. Ursprung

Entstanden aus der Notwendigkeit, die Welt aus Admin-Perspektive zu überblicken. EINSICHT ist das Gegenstück zum öffentlichen Leitstand.

---

## 5. Weltfunktion

Beobachtung. Kontrolle. Verwaltung. EINSICHT ist das Admin-Auge.

---


## 6. Überschneidungen

- LEITSTAND zeigt öffentliche Metriken.
- WELTSTROM zeigt öffentliche Events.
- SCHLAF zeigt Traumarchiv aus Wesen-Sicht.
- ADMIN (versteckt) zeigt ähnliche Verwaltungsdaten.

---

## 7. Einzugsrelevanz

**Optionen:**
- deutlich wichtiger
- etwas wichtiger
- unverändert
- weniger wichtig
- möglicherweise überflüssig

**Gewählte Option:** unverändert

**Begründung:** Wird zum Kontrollzentrum für Daniel. Wesen haben keinen Zugriff. Wichtig für Governance.

---

## 8. Verlustanalyse

- Weltverlust: Mittel (für öffentliche Welt gering, für Admin hoch).
- Erinnerungsverlust: Mittel.
- Funktionsverlust: Hoch für Admin.
- Nutzerverlust: Gering (nur Daniel).
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

**Gewählte Kategorie:** WICHTIG

## 10. Empfehlung

**Gewählte Empfehlung:** Behalten

**Begründung:** EINSICHT ist notwendig für die Governance der Welt, auch wenn sie nur wenige Nutzer hat.

---

## 11. Langfristige Weltperspektive

Wird zum Kontrollzentrum für Daniel. Wesen haben keinen Zugriff. Wichtig für Governance.

---

## Fazit

EINSICHT ist ein Admin-Organ, kein öffentliches. Sie wurde möglicherweise unterschätzt, weil sie nicht immer sichtbar ist. Für den Betrieb der Welt ist sie jedoch essenziell.
