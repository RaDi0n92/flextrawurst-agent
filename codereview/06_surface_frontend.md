# Review: Surface-Frontend

## Kritisch

- Token wird doppelt mit `Bearer` versehen. Login speichert `ftw_token` bereits als `"Bearer " + d.token` in `/root/werkraum/flextrawurst/flextrawurst_surface.html:11579` und `:11611`. Einige Calls senden danach erneut `Authorization: 'Bearer '+tok`, z.B. Gedankenblasen in `:11454` bis `:11457` und Admin-Spuren in `:10201`, `:10216`, `:10230`. Das ergibt `Bearer Bearer ...` und fuehrt zu sporadisch kaputten API-Calls.

- Diskurs-Admin-Toggle ist fuer alle sichtbar. `/root/werkraum/flextrawurst/flextrawurst_surface.html:10087` bis `:10091` enthaelt `(role==='admin'||role==='entity'||true)`. Das `||true` hebelt die UI-Grenze aus. Backend sollte schuetzen, aber die Surface signalisiert falsche Rechte.

## Hoch

- AGENTS-Surface-Pipeline passt nicht zur realen Dateiablage. Die Regel nennt `scripts/build_surface.ts`, `tests/surface_ring_23.test.ts` und Output unter `out/surface/...`. Im Werkraum wurden diese Dateien bei der Suche nicht gefunden; real liegt eine grosse `/root/werkraum/flextrawurst/flextrawurst_surface.html`, und `/root/werkraum/package.json:9` bis `:11` hat keinen sinnvollen Test. Damit kann die Pflicht "Tab plus Test plus Build" aktuell nicht wie dokumentiert laufen.

- Die Surface ist eine grosse, generierte/handgepflegte Monolith-Datei. Viele API-Calls, Auth-Status, Admin-UI und Feature-Inventar liegen direkt in einem HTML. Das macht Review und Regressionstests schwer und beguenstigt Token-/Rechte-Drift.

## Mittel

- Login-Gueltigkeit koppelt Username-Format an Tokenstatus. `/root/werkraum/flextrawurst/flextrawurst_surface.html:11637` bis `:11639` erklaert Tokens fuer ungueltig, wenn der Name `-` enthaelt. Das ist fachlich fragil und kann legitime Nutzer blockieren.

- Viele Fetches haben keine einheitliche Fehlerbehandlung und keine Timeouts. Einzelne Stellen nutzen `AbortSignal.timeout`, viele andere nicht. Dadurch kann die UI bei API-Haengern inkonsistent wirken.

## Tests, die fehlen

- Smoke-Test: Login, danach ein Call mit `Authorization` exakt `Bearer <token>`, nie doppelt.
- UI-Test: Nicht-Admin sieht keine Admin-/Diskurs-Admin-Steuerung.
- Build-Test: dokumentierte Surface-Views existieren in der tatsaechlichen HTML oder die Pipeline wird neu festgelegt.
