# Review: Gruppen-API, Chat, Materialien und Einzugsampel

## Kritisch

- Interne Gruppen sind anonym sichtbar. `/root/werkraum/welt/groups_api.py:230` bis `:233` liefert fuer Nicht-Admins `visibility_layer IN ('public','internal')`. `get_group` und Folge-Endpunkte blocken sichtbar nur `private`, nicht `internal`. Wenn `internal` wirklich intern meint, ist das ein Datenleck.

- Mitglieder koennen ohne ausreichende Policy hinzugefuegt werden. `/root/werkraum/welt/groups_api.py:533` bis `:537` beschraenkt nur Menschen beim Hinzufuegen anderer Menschen. Entity-Tokens koennen dadurch beliebige Member/Rollen setzen. Ausserdem wird `rights_policy.public_join` nicht sichtbar durchgesetzt.

- Materialien koennen ohne Besitz-/Mitgliedschaftspruefung verknuepft werden. `/root/werkraum/welt/groups_api.py:594` bis `:640` prueft Consent nur fuer `human_material`. Fuer `post`, `splitter`, `gedankenblase`, `shadow_dialog` kann ein authentifizierter Nutzer beliebige Objekte an Gruppen haengen.

- Gruppenchat ist praktisch nur Login-geschuetzt. `/root/werkraum/welt/groups_api.py:1240` bis `:1266` prueft Gruppe und Token, aber nicht Membership, Visibility, Status oder Chat-Rechte. WebSocket-Chat in `/root/werkraum/welt/groups_api.py:1272` bis `:1345` hat dasselbe Problem.

## Hoch

- Gruppen-API implementiert JWT separat mit Fallback-Secret. `/root/werkraum/welt/groups_api.py:71` bis `:87` faellt auf `"changeme-secret-key"` zurueck, wenn `.jwt_secret` nicht gelesen wird. Das driftet von `/root/werkraum/welt/auth.py` weg und ist bei Fehlkonfiguration gefaehrlich.

- Event-Inserts uebergeben rohe Python-Dicts. `/root/werkraum/welt/groups_api.py:554` bis `:557` und `/root/werkraum/welt/groups_api.py:919` bis `:922` geben `payload` direkt an psycopg2. Ohne `Json(...)` kann das mit `can't adapt type 'dict'` brechen.

- Einzugsampel v4 hat hart gruene Checks. `/root/werkraum/welt/groups_api.py:993` bis `:1001` setzt zentrale Sicherheits-/Gruppen-/Chat-Pruefungen auf `True`, statt sie real zu testen. Eine kaputte Rechtepruefung kann dadurch gruen erscheinen.

- Ampel meldet alle sechs einzugbereit unabhaengig vom Check. `/root/werkraum/welt/groups_api.py:1186` setzt `"alle_sechs_einzug_bereit": True` hart. Das widerspricht dem vorherigen `wesen_n`-Check und macht die Ampel als Gate unzuverlaessig.

## Mittel

- Slug-Erzeugung ist zu naiv. `/root/werkraum/welt/groups_api.py:402` bis `:407` nutzt lowercase plus Space/Hyphen-Replacement. Sonderzeichen, leere Namen, doppelte Unterstriche und sehr aehnliche Namen werden nicht sauber normalisiert.

- Schema-Migrationen laufen zur API-Laufzeit. `_ensure_group_social_schema` in `/root/werkraum/welt/groups_api.py:101` bis `:183` erstellt Tabellen/Indizes beim Import/Boot. Das macht API-Start abhaengig von DB-Schreibrechten und versteckt Migrationsstatus.

## Tests, die fehlen

- Anonymer Request darf keine `internal` Gruppen sehen.
- Nicht-Mitglied darf nicht in private/internal Gruppe chatten oder Materialien haengen.
- Entity-Token darf nicht beliebige Mitglieder/Rollen setzen.
- Ampel muss rot werden, wenn Chatrechte oder Materialrechte absichtlich gebrochen sind.
