# Wirklichkeitskollision #2: `/admin/einzugsampel` (v1) ohne Auth-Prüfung

Stichtag: 2026-07-21. Status: **verifiziert, aktuell (noch nicht behoben)**.

## Methodik-Hinweis (wichtig für Verwertung)

Der `openapi.json`-Export von FastAPI markiert **alle** 307 Routen als "public" (kein `security`-Feld) — das System prüft Admin-Rechte nicht über FastAPI's `Security()`/OpenAPI-Mechanismus, sondern manuell im Funktionskörper über `_require_admin(authorization)` / `_is_admin(authorization)` (`welt/api.py:369-392`, JWT via `Authorization`-Header). Die OpenAPI-Datei allein ist daher **kein verlässlicher Indikator** dafür, was tatsächlich geschützt ist — das musste gegen den Quellcode verifiziert werden. Grep über alle 4 routen-registrierenden Dateien (`api.py`, `groups_api.py`, `admin_einsicht_api.py`, `tts_service.py`, zusammen 352 Routendefinitionen) nach den vier bekannten Auth-Helfern ergibt genau **eine** `/admin/...`-Route ohne jeden gefundenen Auth-Aufruf.

## Der Fund

`welt/api.py:10409-10410`:
```python
@app.get("/admin/einzugsampel")
def einzugsampel():
    with get_conn() as conn:
        ...
```
Kein `authorization`-Parameter, kein `_require_admin`/`_is_admin`-Aufruf — jeder unauthentifizierte Request auf `GET /admin/einzugsampel` bekommt eine Antwort.

**Zum Vergleich, alle drei Nachfolgeversionen sind geschützt:**
- `welt/api.py:11838`: `einzugsampel_v2()` → `_require_admin(authorization)`
- `welt/api.py:12030`: `einzugsampel_v3()` → `_require_admin(authorization)`
- `welt/groups_api.py:952`: `einzugsampel_v4()` → `if not _is_admin(authorization): raise HTTPException(403, ...)`

## Einordnung — deckt sich mit Daniels eigener vorheriger Beobachtung

Laut RESONANZFELD-Notiz vom 2026-07-21 14:38 war bereits bekannt: *"einzugsampel v2/v3 sind ebenfalls ungeschützt und sehen nach einer nie fertiggebauten public/admin-Zweiteilung aus — Daniel-Entscheidung nötig"*. Der Folge-Eintrag (16:49 desselben Tages) vermerkt: *"einzugsampel v2/v3 haben jetzt echten Admin-Auth-Schutz"* — das ist durch diesen Audit bestätigt (siehe oben, beide jetzt geschützt). **Was in dieser Korrektur nicht mit erwähnt/gefixt wurde: die ursprüngliche, unversionierte `/admin/einzugsampel` selbst.** Sie ist die einzige der vier Varianten, die weiterhin offen ist.

## Was die Route preisgibt (Sensitivitätseinschätzung)

Kein direkter Datenleck von Personendaten — die Antwort besteht aus Systemzustands-Checks (u.a. `entity_kern aktiv`, `Alle 6 Wesen denken`, Fehler-Event-Zählung). Trotzdem ein Verstoß gegen Grundgesetz 4 ("Admin-Routen unter /admin/...", implizite Erwartung: geschützt) und ein Informationsleck über internen Systemzustand an jeden unauthentifizierten Aufrufer.

## Reichweitenprüfung dieses Checks (Ehrlichkeit über Abdeckung)

- 352 Routendefinitionen automatisiert erfasst, gegen 307 laut `openapi.json` — Differenz nicht aufgelöst (vermutlich Mehrfach-Decorator/bedingte Registrierung), hier nicht weiter verfolgt.
- Auth-Erkennung ist textuelles Grep auf vier bekannte Helfer-Namen im Funktionskörper (Fensterbegrenzung: bis zur nächsten `@app.`/`def`-Zeile). Kann falsch-negativ sein bei stark ungewöhnlicher Codestruktur — hier aber durch direktes Lesen der Fundstelle (`api.py:10409-10443`) manuell bestätigt, keine Fehlklassifikation.
- Vollständige Routenliste mit Auth-Klassifikation: `routenliste_mit_echtem_auth_VOLLSTAENDIG.txt` (352 Zeilen).
