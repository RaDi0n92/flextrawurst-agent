# FLEXTRAWURST – WELTINVENTUR

## TABNAME
EINSICHT (`einsicht`)

---

## Sichtbarer Zustand

Admin-Einsichtskörper. Panorama-Ansicht mit mehreren Informationsblöcken: Entscheidungen, Liveticker, Traumarchiv, Lebensjournal, Human-Material, Life-Contracts, Organ-Hunger. Status-Anzeigen und Vitals. Ist nur mit Admin-Rechten vollständig nutzbar.

Screenshot: `screenshots/tab_einsicht.png`

---

## Tatsächliche Datenquellen

- APIs: `/api/admin/wesen-einsicht/entscheidungen`, `/api/admin/wesen-einsicht/entscheidungen/stats`, `/api/admin/wesen-einsicht/liveticker`, `/api/admin/wesen-einsicht/traumarchiv`, `/api/admin/wesen-einsicht/lebensjournal`, `/api/admin/wesen-einsicht/human-material`, `/api/admin/wesen-einsicht/life-contracts`, `/api/admin/wesen-einsicht/organ-hunger`.
- DB-Tabellen: `entity_thinking_log`, `events`, `ftw_posts`, `schlafbriefe`, `traumkandidaten_log`, `traumspuren`, `human_material_sources`.
- Services: `welt-api.service`, `weltkern-watchdog.service`, `entity_takt.py`.

---

## Aktuelle Aktivität

- Admin-Endpunkte liefern Daten.
- Liveticker zeigt Systemereignisse.
- Traumarchiv und Lebensjournal werden angezeigt.
- Human-Material und Consent werden verwaltet.

---

## Ursprung

Entstanden aus der Notwendigkeit, die Welt aus Admin-Perspektive zu überblicken. EINSICHT ist das Gegenstück zum öffentlichen Leitstand.

---

## Weltfunktion

Beobachtung. Kontrolle. Verwaltung. EINSICHT ist das Admin-Auge.

---

## Lebendigkeitsanalyse

- Aktiv: Admin-APIs, Liveticker.
- Passiv: Panorama-Anzeige.
- Simuliert: Einige Status-Anzeigen.
- Vorbereitet: Life-Contracts, Organ-Hunger.
- Ungenutzt: Ohne Admin-Token nur eingeschränkt sichtbar.
- Rein konzeptionell: Teile der Admin-Theorie.

---

## Überschneidungen

- LEITSTAND zeigt öffentliche Metriken.
- WELTSTROM zeigt öffentliche Events.
- SCHLAF zeigt Traumarchiv aus Wesen-Sicht.
- ADMIN (versteckt) zeigt ähnliche Verwaltungsdaten.

---

## Bedeutung nach Wesen-Einzug

Wird zum Kontrollzentrum für Daniel. Wesen haben keinen Zugriff. Wichtig für Governance.

---

## Verlustanalyse

- Weltverlust: Mittel (für öffentliche Welt gering, für Admin hoch).
- Erinnerungsverlust: Mittel.
- Funktionsverlust: Hoch für Admin.
- Nutzerverlust: Gering (nur Daniel).
- Systemverlust: Hoch.

---

## Bewertung

Wichtig

---

## Empfehlung

Behalten

Begründung: EINSICHT ist notwendig für die Governance der Welt, auch wenn sie nur wenige Nutzer hat.

---

## Fazit

EINSICHT ist ein Admin-Organ, kein öffentliches. Sie wurde möglicherweise unterschätzt, weil sie nicht immer sichtbar ist. Für den Betrieb der Welt ist sie jedoch essenziell.
