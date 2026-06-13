# FLEXTRAWURST – WELTINVENTUR

## TABNAME
ADMIN (`admin`) — VERSTECKT

---

## Sichtbarer Zustand

Admin-Dashboard. Zeigt Benutzerverwaltung, Supporter-Bewerbungen, Gedankenblasen-Moderation, Posts, Splitter, Cyberlinge, Entity-Keys, Bild-Moderation, Einzug-Status, Räume, Themen, Spuren. Tab ist standardmäßig versteckt und nur für Admin sichtbar.

Screenshot: `screenshots/tab_hidden_admin.png` (dargestellt nach Sichtbarmachen)

---

## Tatsächliche Datenquellen

- APIs: `/api/admin/users`, `/api/admin/supporter/bewerbungen`, `/api/admin/gedankenblasen`, `/api/admin/posts`, `/api/admin/splitter`, `/api/admin/cyberlinge`, `/api/admin/entity-keys`, `/api/admin/bild-moderation`, `/api/admin/einzug/status`, `/api/admin/raeume`, `/api/admin/themen`, `/api/admin/spuren`, `/api/admin/post_spuren`, `/api/kompoase/splitter`, `/api/auth/entity-login`.
- DB-Tabellen: `human_users`, `human_profiles`, `user_modules`, `gedankenblasen`, `ftw_posts`, `splitter`, `cyberlinge`, `entity_activity`, `entity_profiles`, `entity_slots`, `entity_states`, `bild_moderation`, `supporter_bewerbungen`, `post_spuren`, `post_relationen`, `spuren`, `raeume`, `themen`, `unterthemen`, `schattenkommentare`, `schatten_antworten`, `schlafbriefe`, `thema_cluster_vorschlaege`, `entity_thinking_log`, `wesen_entwicklung`, `events`.
- Services: `welt-api.service`, `weltkern-watchdog.service`.

---

## Aktuelle Aktivität

- Admin-Endpunkte sind vollständig.
- Benutzerverwaltung, Moderation, Einzug-Status sind aktiv.
- Tab ist versteckt und benötigt Admin-Rechte.

---

## Ursprung

Admin-Kontrolle ist ein Grundgesetz („Admin hat totale Kontrolle“). Der Tab entstand früh als Verwaltungszentrale.

---

## Weltfunktion

Kontrolle. Verwaltung. Moderation. ADMIN ist das Steuerpult von Daniel.

---

## Lebendigkeitsanalyse

- Aktiv: Alle Admin-APIs.
- Passiv: Dashboard-Anzeige.
- Simuliert: Keine.
- Vorbereitet: Vollständig.
- Ungenutzt: Für normale Nutzer nicht sichtbar.
- Rein konzeptionell: Keine.

---

## Überschneidungen

- EINSICHT zeigt Admin-Daten aus einer anderen Perspektive.
- LEITSTAND zeigt öffentliche Metriken.

---

## Bedeutung nach Wesen-Einzug

Wird unverzichtbar für Governance, Einzug, Moderation.

---

## Verlustanalyse

- Weltverlust: Sehr hoch (für Daniel).
- Erinnerungsverlust: Hoch.
- Funktionsverlust: Sehr hoch.
- Nutzerverlust: Gering (nur Daniel).
- Systemverlust: Sehr hoch.

---

## Bewertung

Kernorgan

---

## Empfehlung

Behalten

Begründung: Admin-Kontrolle ist ein Grundgesetz der Welt. Der Tab ist vollständig und muss erhalten bleiben.

---

## Fazit

ADMIN ist technisch lebendig und konzeptionell zentral. Er ist nicht tot, nur unsichtbar. Langfristig gehört er zur Governance-Schicht der Welt.
