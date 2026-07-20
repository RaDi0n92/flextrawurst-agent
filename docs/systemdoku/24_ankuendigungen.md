# Ankündigungen — Admin-only News/Ankündigungen/History

**Datum:** 2026-07-20, Bild-Upload + Escape-Bugfix ergänzt 2026-07-21 (Recovery-Session nach PC-Freeze)

Neuer öffentlicher Tab direkt links neben "Was ist das?" im view-bar. Jeder kann lesen, nur Admins dürfen posten/bearbeiten.

## Backend

- `welt/schema_ankuendigungen.sql` — Tabelle `ankuendigungen` (titel, inhalt, kategorie, autor_id, veroeffentlicht, angepinnt, meta JSONB, created_at/updated_at, **bild_url TEXT, nullable, 2026-07-21 nachgetragen**). Kategorie bewusst freier Text statt Enum (Grundgesetz 2), Start-Kategorien: `news`, `ankuendigung`, `history`.
- `welt/api.py`: `GET /ankuendigungen` (öffentlich, `search`/`kategorie`/`limit`/`offset`/`sort`/`order` — Grundgesetz 3; Admins sehen zusätzlich unveröffentlichte Entwürfe), `POST /admin/ankuendigungen` + `PATCH /admin/ankuendigungen/{id}` (beide `_require_admin`). Kein DELETE — nur `veroeffentlicht=false` (Grundgesetz 4). Schreibt `ankuendigung.veroeffentlicht`/`ankuendigung.bearbeitet`-Events (Grundgesetz 5).
- **Neu (2026-07-21):** `POST /admin/ankuendigungen/{id}/bild` — Admin-only Bild-Upload (Multipart, `bild`-Feld). Whitelist JPEG/PNG/WebP/GIF, max. 5MB, Dateiname `{id}_{uuid}.{ext}` unter `uploads/ankuendigungen/`. Altes Bild bleibt beim Wechsel als Datei liegen (nichts wird gelöscht, Grundgesetz 5), nur `bild_url` in der DB zeigt neu. Schreibt `ankuendigung.bild_geaendert`-Event.

## Frontend

- `flextrawurst`-Repo, `scripts/build_surface.ts`: Tab-Button vor "uber", `generateAnkuendigungenView()`, JS (`ankuendigungenLaden`, `ankNeuOeffnen`, `ankSpeichern`), i18n DE+EN vollständig.
- "+ Neue Ankündigung"-Button nur sichtbar wenn `localStorage.ftw_role === 'admin'` (clientseitig) — serverseitig ohnehin durch `_require_admin` abgesichert, UI-Verstecken ist nur Komfort, keine Sicherheitsgrenze.
- **Neu (2026-07-21):** Bild-Feld im Formular (`ak-f-bild-input`), deaktiviert bis zum ersten Speichern (neue Ankündigung hat noch keine ID, `POST /admin/ankuendigungen/{id}/bild` braucht eine). Nach erstem Speichern öffnet `ankSpeichern()` automatisch `ankBearbeitenOeffnen(d.id)`, Feld wird aktiv. `ankBildUpload()` schickt `FormData` an den neuen Endpunkt, aktualisiert Vorschau + Liste sofort.

## Verifikation

Live gegen echte welt-api getestet: öffentliches GET → 200, POST/PATCH ohne Token → 401. Schema-Migration bestätigt live in der DB (`\d ankuendigungen` zeigt `bild_url`), `welt-api.service` läuft bereits mit dem neuen Code (Neustart 23:36 Uhr, nach dem letzten Edit um 23:34).

**Escape-Bug gefunden und gefixt (2026-07-21):** Beim Tiefen-Check (JS-Syntax pro Script-Block einzeln geprüft, wie beim Erstbau) fiel ein zweiter, echter Syntaxfehler in Script-Block 15 auf — **nicht** Teil des Bild-Features, sondern schon im ursprünglichen Ankündigungen-Tab-Commit vom 20.07. enthalten und bislang nicht bemerkt. Ursache: `akRender()`/`akDetailOeffnen()` bauten `onclick`-Attribute mit `\'`-escapten Anführungszeichen (z.B. `akChipKlick(\'\')`), aber dieser gesamte JS-Bereich liegt selbst in einem riesigen äußeren Backtick-Template — und Backtick-Templates lösen `\'`-Escapes beim Bauen selbst schon auf, bevor der Code je in die Ausgabedatei geschrieben wird. Ergebnis: Im ausgelieferten Code fehlten die Backslashes, was die String-Syntax an 6 Stellen brach (Kategorie-Chips, Kartenklick, Hero-Klick, Bearbeiten-Button, Hintergrundbild-URL). Ein JS-Syntaxfehler killt den kompletten Script-Block — d.h. potenziell mehr als nur Ankündigungen war betroffen, je nachdem was sonst noch in Block 15 steht. Fix: an allen 6 Stellen `\'` durch einen separat doppelt-gequoteten String ersetzt (`"'"`, `"''"`), damit keine Backslash-Escapes mehr nötig sind — dieselbe Technik, die der Rest der Datei überall sonst verwendet. Nach dem Fix: 0 Syntaxfehler im Block, alle 82 Ring-23-Tests grün.

**Verifikationsmethode ohne echten Browser-Login:** Da Daniel einen echten Klicktest mit seinem Admin-Account für diese Runde bewusst abgelehnt hat (Sicherheits-Classifier hatte zuvor Token-Minting korrekt blockiert), wurden die tatsächlichen gebauten Funktionen (`akRender`, `akChipKlick`, `akDetailOeffnen`) per Node `vm`-Sandbox mit realistischen Testdaten **wirklich ausgeführt** (nicht nur gelesen) — inklusive eines HTML-Injection-Teststrings im Titel (`Test News & <b>fett</b>`), der korrekt escaped wurde. Erzeugte `onclick`-Attribute (`akChipKlick('news')`, `akDetailOeffnen('bbb-222')`, `background-image:url('/uploads/x.png')`) sind alle wohlgeformt. **Weiterhin nicht getestet:** der echte Bild-Upload-Klick durch einen Browser mit echtem Admin-Login (`POST /admin/ankuendigungen/{id}/bild` selbst) — Daniel sollte das einmal live durchklicken, sobald er möchte.

Liegengebliebener Test-Eintrag aus der vorherigen (durch den PC-Freeze unterbrochenen) Session (`"Testankündigung mit Bild (wird gleich wieder gelöscht)"`, bild_url zeigte auf `/uploads/avatars/...` — vermutlich über einen Avatar-Upload-Workaround vor Existenz des dedizierten Endpunkts) wurde nicht gelöscht, sondern per `veroeffentlicht=false` unsichtbar gemacht (Grundgesetz 4/5 — nichts wird gelöscht).

## Bekannter Nebenfund (nicht behoben, außerhalb des Auftrags)

`out/process_camera/flextrawurst_surface.html` Script-Block 1 (Wesen-Spawner-Avatar-Rendering) hat einen Anführungszeichen-Verschachtelungsfehler (`onerror="this.style.display='none'"` innerhalb eines bereits einfach gequoteten JS-Strings) — bricht die Zeile syntaktisch. Pre-existing, nicht Teil dieses Bausteins, nicht angefasst.
