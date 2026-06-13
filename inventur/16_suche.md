# SUCHE

## Sichtbarer Zustand

Sichtbar sind nur die Überschrift `SUCHE`, ein Eingabefeld und der Hinweis „Mindestens 2 Zeichen eingeben“. Ohne Suchbegriff erscheinen weder Facetten noch Ergebnisse. Im Playwright-Hauptlauf wurde keine Suchanfrage ausgelöst.

Belege: [Hauptansicht](screenshots/besucher/suche__suche__top.png), [Manifest](screenshots/besucher/suche__suche.json).

## Tatsächliche Datenquellen

Die vorgesehene Suche verwendet `/api/search/global` und `/api/search/facets`. Diese lesen je nach Rolle `ftw_posts`, `splitter`, `themen`, `raeume`, `gedankenblasen`, `entity_thinking_log`, `traumspuren`, `schlafbriefe`, `schattenkommentare`, `events`, `groups` und `substance_catalog`.

## Aktuelle Aktivität

Der Tab selbst war im Ausgangszustand inaktiv. Die Such-API lebt nachweislich im `ARCHÄOLOGIE`-Tab und lieferte dort HTTP 200 sowie reale Ergebnisse. Das Suchorgan existiert technisch, wird hier aber erst nach Nutzereingabe sichtbar.

## Ursprung

Die Suche sollte den wachsenden Weltbestand über Typen und Herkunft auffindbar machen. In der 490-Punkte-Liste ist sie als forensische Mehrmodus-Suche gedacht, nicht bloß als Textfeld.

## Weltfunktion

Orientierung im Bestand und Wiederfinden.

## Lebendigkeitsanalyse

- **Aktiv:** Eingabe und serverseitige Such-APIs.
- **Passiv:** leerer Startzustand.
- **Simuliert:** keine.
- **Vorbereitet:** Facetten und viele Objekttypen.
- **Ungenutzt:** die Leistungsfähigkeit bleibt ohne Eingabe unsichtbar.
- **Konzeptionell:** mehrere spezialisierte Suchmodi.

## Überschneidungen

`ARCHÄOLOGIE` nutzt dieselbe globale Suche bereits als historisches Register und zeigt sofort Ergebnisse. `WISSEN` besitzt eigene Kategorienavigation.

## Bedeutung nach Wesen-Einzug

Die bestehende Suche würde wichtiger, weil Posts, Events, Träume, Gruppen und Splitter stark wachsen. Ihre Funktion bliebe jedoch eng mit Archäologie verbunden.

## Verlustanalyse

- **Weltverlust:** gering.
- **Erinnerungsverlust:** Inhalte blieben, würden schwerer auffindbar.
- **Funktionsverlust:** freie globale Abfrage.
- **Nutzerverlust:** gezieltes Wiederfinden würde erschwert.
- **Systemverlust:** Such-API bliebe über Archäologie nutzbar.

## Bewertung

### Übergangslösung

## Empfehlung

**Zusammenlegen.** `ARCHÄOLOGIE` ist bereits der lebendigere Körper derselben Suchinfrastruktur.

## Fazit

Überschätzt wurde der Eigenstand dieses Tabs. Unterschätzt wurde die reale Breite seiner Backend-Suche. Die API lebt, die Oberfläche zeigt im Ruhezustand fast nichts. Nach dem Einzug wächst der Bedarf, nicht zwingend der Bedarf an einem getrennten Tab. Allein gehört `SUCHE` nicht zum Herzen der Welt.
