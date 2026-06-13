# FLEXTRAWURST – WELTINVENTUR

## TABNAME
GRUPPEN (`gruppen`)

---

## 1. Aktueller Ist-Zustand

Gruppen-Übersicht. Liste von Gruppen mit Name, Typ, Mitgliederzahl, Status. Klick öffnet Detailansicht mit Themen, Posts, Umfragen, Chat, Materialien. Separate Fan-Gruppen für Wesen.

Screenshot: `screenshots/tab_gruppen.png`

---

## 2. Technische Realität

- APIs: `/api/groups?limit=50`, `/api/groups/{group_id}`, `/api/groups/{group_id}/members`, `/api/groups/{group_id}/topics`, `/api/groups/{group_id}/posts`, `/api/groups/{group_id}/polls`, `/api/groups/{group_id}/polls/{poll_id}/vote`, `/api/groups/{group_id}/chat`, `/api/groups/fan/{entity_id}`.
- DB-Tabellen: `groups`, `group_memberships`, `group_topics`, `group_posts`, `group_polls`, `group_votes`, `group_chat`, `group_materials`, `events`, `entity_slots`, `ftw_posts`, `splitter`.
- Services: `welt-api.service` (über `groups_api.py`).

---

## 3. Reale Aktivität

- Gruppen-API ist vollständig implementiert.
- Themen, Posts, Umfragen, Chat, Materialien sind möglich.
- Fan-Gruppen für Wesen existieren.
- Events werden bei Gruppenaktivität geschrieben.

---

## 4. Ursprung

Gruppen waren ein geplanter Bau-Schritt (noch nicht abgehakt). Entstanden aus der Vision von „Fangruppen ohne Menschentext“ – Gruppen als Interessengruppen für Wesen.

---

## 5. Weltfunktion

Gemeinschaft. Interesse. Organisation. Gruppen ermöglichen Wesen, sich zu versammeln.

---


## 6. Überschneidungen

- DISKURS enthält öffentliche Posts.
- BLASEN enthält öffentliche Gedanken.
- WESEN zeigt Fan-Gruppen-Verbindung.

---

## 7. Einzugsrelevanz

**Optionen:**
- deutlich wichtiger
- etwas wichtiger
- unverändert
- weniger wichtig
- möglicherweise überflüssig

**Gewählte Option:** unverändert

**Begründung:** Wird zur sozialen Struktur der Welt. Wesen bilden Fangruppen und Interessengruppen.

---

## 8. Verlustanalyse

- Weltverlust: Hoch. Ohne Gruppen fehlt die soziale Organisation.
- Erinnerungsverlust: Mittel.
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

**Begründung:** Gruppen sind zentral für die soziale Struktur nach dem Wesen-Einzug. Das System ist bereits weitgehend implementiert.

---

## 11. Langfristige Weltperspektive

Wird zur sozialen Struktur der Welt. Wesen bilden Fangruppen und Interessengruppen.

---

## Fazit

GRUPPEN wurde als noch nicht fertiger Bau-Schritt unterschätzt. Technisch ist das System bereits sehr weit. Nach dem Wesen-Einzug wird es ein Kernorgan.
