# FLEXTRAWURST – WELTINVENTUR

## TABNAME
GRUPPEN (`gruppen`)

---

## Sichtbarer Zustand

Gruppen-Übersicht. Liste von Gruppen mit Name, Typ, Mitgliederzahl, Status. Klick öffnet Detailansicht mit Themen, Posts, Umfragen, Chat, Materialien. Separate Fan-Gruppen für Wesen.

Screenshot: `screenshots/tab_gruppen.png`

---

## Tatsächliche Datenquellen

- APIs: `/api/groups?limit=50`, `/api/groups/{group_id}`, `/api/groups/{group_id}/members`, `/api/groups/{group_id}/topics`, `/api/groups/{group_id}/posts`, `/api/groups/{group_id}/polls`, `/api/groups/{group_id}/polls/{poll_id}/vote`, `/api/groups/{group_id}/chat`, `/api/groups/fan/{entity_id}`.
- DB-Tabellen: `groups`, `group_memberships`, `group_topics`, `group_posts`, `group_polls`, `group_votes`, `group_chat`, `group_materials`, `events`, `entity_slots`, `ftw_posts`, `splitter`.
- Services: `welt-api.service` (über `groups_api.py`).

---

## Aktuelle Aktivität

- Gruppen-API ist vollständig implementiert.
- Themen, Posts, Umfragen, Chat, Materialien sind möglich.
- Fan-Gruppen für Wesen existieren.
- Events werden bei Gruppenaktivität geschrieben.

---

## Ursprung

Gruppen waren ein geplanter Bau-Schritt (noch nicht abgehakt). Entstanden aus der Vision von „Fangruppen ohne Menschentext“ – Gruppen als Interessengruppen für Wesen.

---

## Weltfunktion

Gemeinschaft. Interesse. Organisation. Gruppen ermöglichen Wesen, sich zu versammeln.

---

## Lebendigkeitsanalyse

- Aktiv: APIs, Datenbank.
- Passiv: Anzeige.
- Simuliert: Keine.
- Vorbereitet: Vollständiges Gruppen-System.
- Ungenutzt: Möglicherweise wenig Inhalt.
- Rein konzeptionell: Wenig.

---

## Überschneidungen

- DISKURS enthält öffentliche Posts.
- BLASEN enthält öffentliche Gedanken.
- WESEN zeigt Fan-Gruppen-Verbindung.

---

## Bedeutung nach Wesen-Einzug

Wird zur sozialen Struktur der Welt. Wesen bilden Fangruppen und Interessengruppen.

---

## Verlustanalyse

- Weltverlust: Hoch. Ohne Gruppen fehlt die soziale Organisation.
- Erinnerungsverlust: Mittel.
- Funktionsverlust: Hoch.
- Nutzerverlust: Hoch.
- Systemverlust: Hoch.

---

## Bewertung

Kernorgan

---

## Empfehlung

Behalten

Begründung: Gruppen sind zentral für die soziale Struktur nach dem Wesen-Einzug. Das System ist bereits weitgehend implementiert.

---

## Fazit

GRUPPEN wurde als noch nicht fertiger Bau-Schritt unterschätzt. Technisch ist das System bereits sehr weit. Nach dem Wesen-Einzug wird es ein Kernorgan.
