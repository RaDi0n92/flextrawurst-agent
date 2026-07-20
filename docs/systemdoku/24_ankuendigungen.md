# Ankündigungen — Admin-only News/Ankündigungen/History

**Datum:** 2026-07-20

Neuer öffentlicher Tab direkt links neben "Was ist das?" im view-bar. Jeder kann lesen, nur Admins dürfen posten/bearbeiten.

## Backend

- `welt/schema_ankuendigungen.sql` — Tabelle `ankuendigungen` (titel, inhalt, kategorie, autor_id, veroeffentlicht, angepinnt, meta JSONB, created_at/updated_at). Kategorie bewusst freier Text statt Enum (Grundgesetz 2), Start-Kategorien: `news`, `ankuendigung`, `history`.
- `welt/api.py`: `GET /ankuendigungen` (öffentlich, `search`/`kategorie`/`limit`/`offset`/`sort`/`order` — Grundgesetz 3; Admins sehen zusätzlich unveröffentlichte Entwürfe), `POST /admin/ankuendigungen` + `PATCH /admin/ankuendigungen/{id}` (beide `_require_admin`). Kein DELETE — nur `veroeffentlicht=false` (Grundgesetz 4). Schreibt `ankuendigung.veroeffentlicht`/`ankuendigung.bearbeitet`-Events (Grundgesetz 5).

## Frontend

- `flextrawurst`-Repo, `scripts/build_surface.ts`: Tab-Button vor "uber", `generateAnkuendigungenView()`, JS (`ankuendigungenLaden`, `ankNeuOeffnen`, `ankSpeichern`), i18n DE+EN vollständig.
- "+ Neue Ankündigung"-Button nur sichtbar wenn `localStorage.ftw_role === 'admin'` (clientseitig) — serverseitig ohnehin durch `_require_admin` abgesichert, UI-Verstecken ist nur Komfort, keine Sicherheitsgrenze.

## Verifikation

Live gegen echte welt-api getestet: öffentliches GET → 200 (leer, korrekt), POST/PATCH ohne Token → 401. JS-Syntax pro Script-Block einzeln geprüft (der Gesamt-HTML-Datei hat 22 `<script>`-Blöcke, ein bereits vorher bestehender, nicht von diesem Feature betroffener Block hat einen Anführungszeichen-Bug — nicht angefasst, außerhalb des Auftrags).

**Nicht möglich:** vollständiger authentifizierter Schreibtest (Token-Minting für Testzwecke wurde vom Safety-Classifier korrekt blockiert — echtes Admin-Credential hätte im Transcript gelandet). Daniel sollte den "Ankündigung erstellen"-Ablauf einmal mit seinem echten Admin-Login live durchklicken.

## Bekannter Nebenfund (nicht behoben, außerhalb des Auftrags)

`out/process_camera/flextrawurst_surface.html` Script-Block 1 (Wesen-Spawner-Avatar-Rendering) hat einen Anführungszeichen-Verschachtelungsfehler (`onerror="this.style.display='none'"` innerhalb eines bereits einfach gequoteten JS-Strings) — bricht die Zeile syntaktisch. Pre-existing, nicht Teil dieses Bausteins.
