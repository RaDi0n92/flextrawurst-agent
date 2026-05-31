# Surface-UI-Inventur 2026-05-31

Scope: nur gelesen. Aktive Quelle: `/root/flextrawurst/scripts/build_surface.ts`; Live-Output: `/root/flextrawurst/out/process_camera/flextrawurst_surface.html`.

## Vorhandene Komponenten und Patterns

| Pattern | Vorhandene Stellen | Wiederverwendbar fuer |
|---|---|---|
| Haupt-Tabs | `.v-tab`, `switchView`, Views: Leitstand, Ueber, Raeume, Diskurs, Wesen, KompOase, Blasen, Menschen, Meine Welt, Schlaf, EINSICHT, Systeme, Admin, Wissen, Gesetze, Forschung, Partner | EINSICHT II als Subtab statt neuer Haupttab |
| Subtabs | `.ei-tab`, `.adm-inhalt-tab`, `.auth-tab`, Wissen-Shelves | EINSICHT II, Suche-Facetten, Admin-Detailbereiche |
| Cards | `.rv-card`, `.wv-card`, `.metric-card`, `.sc-card`, `.ei-item`, `.organ-chip`, `.entity-card`, `.mp-*` | Suchresultate, Cyberling-Zustand, Splitter-/Traum-/Brief-Details |
| Timeline/List | `.ei-item`, `.ei-ticker-item`, Diskurs-Postlisten, Meine-Welt-Browser | Lebensjournal, Archäologie-Suche, Denkfenster |
| Detailpanel/Drawer | Leitstand-Inspector, EINSICHT `ei-detail-panel`, KompOase `ko-info`, Menschenprofil `.mp-detail` | Suchdetail-Zielansicht und EINSICHT II |
| Modals/Overlay | Auth-Overlay, Tour-Card, Diskurs-Popups | Suchdetail nur dann, wenn kein Sidepanel reicht |
| Filter | Topbar `filter-chip`, Diskurs-Suche-Selects, EINSICHT Wesenfilter, Wissen-Shelves | Archäologie-Suche mit Typ/Entity/Zeit/Visibility |
| Entity-Selector | EINSICHT Wesenbuttons `.ei-wesen-btn`, Wesen-Sidebar, Menschenprofil-Liste | EINSICHT II und Search-Facet `entity_id` |
| Status-Badges | `.s-chip`, `.badge-*`, `.top-badge`, `.ei-item-tag`, `.ez-badge`, `.ub2-card-status` | Quelle/Sichtbarkeit/Status in Suchresultaten |
| Accordions/expandable Cards | `rv-card[data-open]`, `wv-card[data-open]` | Raum-/Wesen-Detail, Suchresultate mit Provenienz |
| i18n | `UI_TR.de`, `UI_TR.en`, `data-i18n`, `data-i18n-html`, Placeholder/Title, Build-Pruefung | Neue UI-Texte immer mit DE+EN-Key |

## Was wiederverwendbar ist

- EINSICHT-Grundlayout: Header + Entity-Selector + Subnav + Liste + rechtes Detailpanel ist die beste Andockstelle fuer EINSICHT II.
- `ei-item` ist fuer Timeline- und Suchtreffer geeignet: Zeit, Haupttext, Tag.
- `ei-detail-panel` ist fuer Detail-Zielansichten geeignet: Entscheidung, Traum, Brief, Splitter, Schatten.
- Topbar-Suche und Diskurs-Suche liefern Patterns fuer schnelles Suchen, aber Archäologie braucht mehr Filtertiefe.
- `organ-chip`/`s-chip` sind brauchbar fuer Status/Quelle/Visibility.
- KompOase `koZeigeSpur()` zeigt bereits ein gutes Provenienz-Muster: Akteur, Event, Quelle, Zeit.

## Was doppelt gebaut wurde

- Suche existiert mehrfach: Topbar-Suche (`onSearch`), Diskurs-Suche (`dkSuche*`), Backend `/suche`, Backend `/api/search/global`, Backend `/api/search/archaeology`.
- EINSICHT-APIs existieren doppelt: direkt in `api.py` und als `admin_einsicht_api.py`.
- Listen/Card-Patterns wiederholen sich in Admin, Diskurs, EINSICHT, Meine Welt und Menschenprofil.
- Schattenkommentare existieren als alte Resonanz-API und neue Post-Schatten-API.
- Surface-Pfade: aktive Buildquelle `/root/flextrawurst`, zusaetzlicher Werkraum-Pfad `/root/werkraum/flextrawurst`.

## Was fehlt

- Ein kanonisches `SearchResult`-UI-Pattern mit Typ, Zeit, Entity/Human, Sichtbarkeit, Herkunft und Detailziel.
- Ein gemeinsames Detailpanel fuer Suche und EINSICHT II.
- Klare Typnamen ohne Umlaut-Fallen fuer API/Client (`traeume` statt `träume` als API-Key, Label separat).
- Sichtbarkeitsmarker pro Resultat: public/internal/admin-only/hidden.
- Provenienz-Kette als wiederverwendbarer Block, nicht nur in KompOase.
- Cyberling-Aktionsstatus: erlaubt/gesperrt, Cooldown, Cap, naechster Bedarf.

## Bester Anschluss fuer EINSICHT II

EINSICHT II sollte im vorhandenen EINSICHT-Tab anschliessen:

1. Neuer Subtab in `generateEinsichtView()`, z.B. `archaeologie` oder `suche`.
2. Linke Seite: Such-/Filterleiste + Trefferliste im `ei-item`-Pattern.
3. Rechte Seite: `ei-detail-panel` als kanonische Detailansicht.
4. Entity-Selector aus EINSICHT wiederverwenden.
5. Status/Visibility/Herkunft als `ei-item-tag`/`s-chip`.

Damit bleibt EINSICHT II Teil des vorhandenen Einsichtskörpers und wird kein dritter Suchraum neben Topbar und Diskurs.

## Nutzbare Komponenten nach Ziel

| Ziel | Nutzbare Komponenten |
|---|---|
| Suche | EINSICHT `ei-item` + `ei-detail-panel`, Topbar `filter-chip`, Diskurs-Suche-Filter, `s-chip` |
| KompOase | `ko-info`, `koZeigeSpur`, Splitter-Badges, Canvas-Detail mit Akteur/Event/Quelle |
| Cyberling | Schlaf/Cyberling `.sc-card`, Balken `.sc-bar`, EINSICHT Status-Tags |
| Lebensjournal | EINSICHT `lebensjournal` Subtab, `ei-ticker-item`, `ei-item` |
| Traeume/Selbstbriefe | EINSICHT `traumarchiv`, `ei-detail-panel`, Brief/Spur-Tags |

## UI-Risiken

- Viele Inline-Styles und grosse Template-Strings erschweren Wiederverwendung.
- EINSICHT-Substanz-UI zeigt teils feste Textannahmen, statt nur API-Daten.
- KompOase kann "live" wirken, obwohl Theaterdaten/echte DB-Daten je nach Buildstand auseinanderfallen koennen.
- i18n muss bei jedem neuen Text symmetrisch gepflegt werden; sonst Build-Warnungen oder Sprachluecken.
