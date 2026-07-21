# API-Landkarte — README

- `openapi.json` — vollständige FastAPI-Spezifikation (258 Pfade laut OpenAPI-Zählung, Titel "Welt-API", Version 0.1.0)
- `routenliste.txt` — 307 Methode+Pfad-Einträge aus openapi.json (Auth-Spalte darin **nicht verlässlich**, siehe Befund)
- `routenliste_mit_echtem_auth_VOLLSTAENDIG.txt` — 352 Routen aus allen 4 routen-registrierenden Dateien, Auth-Klassifikation direkt aus dem Quellcode (verlässlich)
- `BEFUND_admin_einzugsampel_v1_ungeschuetzt.md` — verifizierter, aktuell offener Sicherheitsbefund
- `beispielantworten/` — Live-Beispielantworten von 4 öffentlichen GET-Endpunkten

## Nebenbefund (keine Kollision, nur Dokumentation): `GET /wesen` liefert `{"wesen":[],"count":0}`

Live abgefragt, Stichtag. Passt zum Kanon-Status "pre_start/VOR-EINZUG" — die Wesen existieren als Konzept/Flarum-Archiv, aber (noch) nicht als Datensätze in der für `/wesen` zuständigen Tabelle/Quelle. Nicht als Bug gewertet, nur als Ist-Zustand festgehalten — relevant für den Datenatlas, weil es die 6-vs-7-Diskussion nochmal anders beleuchtet: **aktuell sind es weder 6 noch 7, sondern 0 "lebende" Wesen-Datensätze über die Live-API.**
