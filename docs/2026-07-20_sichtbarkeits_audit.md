# Sichtbarkeits-Audit — welt-api (258 Endpunkte)

**Datum:** 2026-07-20
**Auftrag:** Daniel wollte geprüft haben, was auf flextrawurst wirklich öffentlich, was nur für eingeloggte User und was nur für Admins sichtbar ist.
**Methode:** Automatisierte Klassifikation aller `@app.get/post/patch/put/delete`-Routen in `welt/api.py` nach Auth-Muster (`_require_admin()`, `_require_auth()` + Rollen-Check, `_is_admin()` weiche Prüfung, oder gar keine Prüfung), anschließend Stichproben-Verifikation der auffälligen Fälle gegen den echten Code und das Frontend.

## Gesamtbild (nach dem Fix, siehe unten)

| Klasse | Anzahl | Bedeutung |
|---|---:|---|
| ADMIN | ~91 | `_require_admin()` oder gleichwertige Rollenprüfung — 403 ohne gültigen Admin-Token |
| USER | ~76 | `_require_auth()` — jeder eingeloggte Account (Mensch, egal welche Rolle), 401 ohne Token |
| ÖFFENTLICH | ~85 | keine Auth-Prüfung — für jeden ohne Login abrufbar |
| ÖFFENTLICH+admin-erweitert | ~5 | öffentlich lesbar, zeigt bei gültigem Admin-Token zusätzliche/private Felder |

Vollständige, nach URL-Präfix gruppierte Liste: `/tmp/audit_summary.txt` (Session-Artefakt, bei Bedarf erneut generierbar — das Klassifikations-Skript ist nicht dauerhaft im Repo abgelegt, war ein Einmal-Werkzeug für dieses Audit).

## Gefundener und behobener Bug (schwerwiegend)

Sieben Routen unter `/admin/...` hatten **trotz Pfad-Präfix keine tatsächliche Auth-Prüfung** — der Pfad-Name suggerierte Admin-Only, aber der Code prüfte nie ein Token:

- `GET /admin/wesen-einsicht/human-material` — **am schwerwiegendsten**: lieferte eine 200-Zeichen-Vorschau **aller** `human_material_sources`-Einträge, ohne Consent-Filter, komplett unauthentifiziert abrufbar. Das widerspricht direkt der im Entscheidungsboard vom 31.05. festgeschriebenen Niemals-Regel ("Menschquellen ohne Consent verwenden").
- `GET /admin/wesen-einsicht/entscheidungen` (+ `/stats`)
- `GET /admin/wesen-einsicht/traumarchiv`
- `GET /admin/wesen-einsicht/lebensjournal`
- `GET /admin/wesen-einsicht/liveticker`
- `GET /admin/spurenwache`

**Ursache:** Diese Routen wurden offenbar gebaut, ohne den bereits existierenden `_require_admin()`-Helper einzubauen — das Frontend (EINSICHT-Tab) sendet bei allen sieben bereits den Auth-Header (`ah()`), es fehlte nur die serverseitige Prüfung. Klassischer Fall von "UI verbirgt es, API prüft es nicht".

**Fix:** `_require_admin(authorization)` in allen sieben Funktionen ergänzt (Commit `49fd93d24`). Live verifiziert nach Neustart von `welt-api.service` (mit Daniels Freigabe) — alle sieben liefern jetzt `401` ohne Token, unveränderte `200` für tatsächlich öffentliche Routen (`/welt/struktur` als Gegenprobe).

## Offener Punkt vom 20.07. — inzwischen entschieden und gefixt (21.07.)

`/admin/einzugsampel`, `/admin/einzugsampel/v2`, `/admin/einzugsampel/v3` waren ebenfalls ohne Auth-Prüfung öffentlich abrufbar. Anders als bei den sieben oben war hier die Faktenlage unklar: Das Frontend (`flextrawurst_surface.html` Zeile ~9350) versucht zuerst `/admin/einzugsampel/v4` mit Auth-Header und würde bei `403` bewusst auf `v3` **ohne** Auth-Header zurückfallen — das deutet auf eine ursprünglich *geplante* öffentlich/admin-Zweiteilung hin (öffentliche Kurzfassung + admin-Vollversion). Am 20.07. existierte `v4` im Backend noch gar nicht (404, nicht 403).

**Update 21.07.:** Daniel hat entschieden: Option 1 — Auth direkt auf v2/v3, wie bei den sieben bereits gefixten Routen (nicht Option "erst v4 bauen"). `_require_admin(authorization)` in `einzugsampel_v2` und `einzugsampel_v3` ergänzt (`welt/api.py`, Commit `0b382a831`). Bei v2 dabei toten Code entfernt (`is_admin` wurde berechnet, aber nie geprüft — reine Kosmetik). Live verifiziert nach Neustart von `welt-api.service` (mit Daniels Freigabe): beide liefern jetzt `401` ohne Token. `v1` (`/admin/einzugsampel` ohne Suffix) bleibt bewusst unverändert öffentlich (`200`) — war nicht Teil des Auftrags.

Nebenfund beim Fix: `/admin/einzugsampel/v4` existiert inzwischen doch im Backend, in `welt/groups_api.py:951`, mit funktionierendem `_is_admin`-Gate (403 statt 404). Der am 20.07. beschriebene Fallback-Mechanismus im Frontend könnte also inzwischen tatsächlich greifen — noch nicht geprüft, ob das Frontend v4 wirklich zuerst anspricht und ob v2/v3 dadurch überhaupt noch aufgerufen werden. Offen für einen späteren Blick, kein aktueller Blocker mehr.

## Grobe Landkarte nach Bereich (Auszug, vollständig in `/tmp/audit_summary.txt`)

| Bereich | Routen | Vorwiegend |
|---|---:|---|
| `/admin/*` | 65 | 62 ADMIN, 3 öffentlich (einzugsampel, s.o.) |
| `/me/*` | 13 | komplett USER (eigenes Profil) |
| `/human-material/*` | 7 | komplett USER (eigene Consent-Verwaltung — korrekt, nicht verwechseln mit dem gefixten `/admin/wesen-einsicht/human-material`) |
| `/mw/*` (Meine Welt) | 24 | 16 USER, 8 ADMIN |
| `/welt/*` | 40 | 23 öffentlich (Weltzustand, Räume, Themen — Grundgesetz 3: durchsuchbar), 15 USER, 2 ADMIN |
| `/wesen/*` | 16 | 7 öffentlich, 5 USER, 2 ADMIN, 2 öffentlich+admin-erweitert |
| `/substances`, `/substanz` | 10 | komplett öffentlich (fiktionale Weltmechanik, wie im Entscheidungsboard E-11 vorgesehen) |
| `/search`, `/suche` | 4 | komplett öffentlich (Grundgesetz 3) |

Alles was unter `/welt/`, `/wesen/`, `/search`, `/substanz*`, `/relationships`, `/zwischenraum`, `/kompoase` öffentlich ist, entspricht der bewussten Architektur-Entscheidung "die Welt ist von außen sichtbar" — kein neuer Fund, sondern erwartetes Verhalten.
