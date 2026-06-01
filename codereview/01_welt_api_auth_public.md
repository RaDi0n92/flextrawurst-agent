# Review: Welt-API, Auth, Public/Profile/Resonanz

## Kritisch

- Public-Routen akzeptieren Admin-Sicht per Query-Parameter ohne Auth. In `/root/werkraum/welt/api.py:66` bis `:73` und `:101` bis `:108` schalten `/wesen` und `/wesen/{entity_id}` mit `admin=true` interne Felder frei. `/root/werkraum/welt/api.py:133` bis `:148` macht dasselbe fuer `/events`. `_require_admin` existiert spaeter in `/root/werkraum/welt/api.py:209` bis `:222`, wird hier aber nicht benutzt. Jeder oeffentliche Caller kann dadurch interne Wesen- und Eventdaten sehen.

- Public-Profil gibt Gedankenwelt aus, obwohl Anonymisierung markiert wird. In `/root/werkraum/welt/api.py:713` bis `:730` wird `gedankenwelt_anonym` gesetzt, aber `gedankenwelt` landet trotzdem direkt im Response. Das ist ein Datenschutz-/Sichtbarkeitsleck, weil der Inhalt selbst nicht entfernt oder anonymisiert wird.

- Entity-Login prueft API-Keys im Klartext und ohne Statusgrenze. `/root/werkraum/welt/api.py:370` bis `:390` vergleicht `entity_profiles.api_key` per Stringvergleich. Es gibt keine Hashing-/Constant-Time-Pruefung und keine Sperre fuer nicht eingezogene oder deaktivierte Entitaeten. Wenn die DB gelesen wird, sind die Entity-Credentials praktisch offen.

## Hoch

- CORS ist global offen. `/root/werkraum/welt/api.py:29` erlaubt `allow_origins=["*"]`, waehrend Authorization-Header genutzt werden. Das ist bei einem oeffentlichen Server ein zu breiter Angriffsraum, auch wenn Browser-Credentials nicht automatisch mitgesendet werden.

- Public-Profil zeigt moeglicherweise Splitter aus nicht oeffentlichen Quellen. Die Query fuer `splitter_recent` in `/root/werkraum/welt/api.py:669` bis `:679` filtert nicht sichtbar nach Herkunfts-/Public-Freigabe. Damit koennen Essenzen aus privaten oder internen Quellen auf einer Public-Seite erscheinen.

- Resonanzreaktionen koennen nicht geaendert werden. `/root/werkraum/welt/api.py:1016` bis `:1022` gibt bei bestehender Reaktion `409` zurueck. Die vorhandene Zaehllogik wirkt aber auf alte/neue Emojis ausgelegt. Ergebnis: einmal falsch reagiert bleibt falsch, und Teile der Delta-Logik sind tot.

- Schattenkommentar-Zaehler leakt private Aktivitaet. `/root/werkraum/welt/api.py:1088` zaehlt alle `schattenkommentare` zu einem Post ohne sichtbare Reader-/Visibility-Pruefung. Auch wenn Inhalte verborgen bleiben, verraten Counts Existenz und Menge.

## Mittel

- `verify_token` setzt `username` auf `sub`, obwohl `sub` in `create_token` die User-ID ist. Siehe `/root/werkraum/welt/auth.py:39` bis `:54`. Jeder Caller, der `username` erwartet, bekommt faktisch eine ID.

- Profil-Patch laesst `visibility` ungeprueft durch. `ProfilePatch` definiert `visibility` in `/root/werkraum/welt/api.py:241` bis `:249`, die Anwendung passiert um `/root/werkraum/welt/api.py:488` bis `:496`. Ohne Enum/Whitelist entstehen ungueltige oder widerspruechliche Sichtbarkeitswerte.

- Avatar-Upload vertraut Dateiendung und `content_type`. `/root/werkraum/welt/api.py:531` bis `:570` begrenzt zwar auf 5 MB, prueft aber keine Bildsignatur und keine echte Dekodierbarkeit. Das reicht fuer einfache Nutzung, nicht fuer robuste Upload-Sicherheit.

## Tests, die fehlen

- Public Request mit `?admin=true` muss keine internen Felder liefern.
- Public Profil mit `gedankenwelt_anonym=true` darf keine Gedankenwelt-Inhalte enthalten.
- Entity-Login muss fuer deaktivierte/nicht freigegebene Entitaeten fehlschlagen.
- Resonanzwechsel von Emoji A nach Emoji B muss Zaehler korrekt aktualisieren.
