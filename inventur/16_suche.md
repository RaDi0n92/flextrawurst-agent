# SUCHE

## 1. Aktueller Ist-Zustand

Sichtbar sind nur die Überschrift `SUCHE`, ein Eingabefeld und der Hinweis „Mindestens 2 Zeichen eingeben“. Ohne Suchbegriff erscheinen weder Facetten noch Ergebnisse. Im Playwright-Hauptlauf wurde keine Suchanfrage ausgelöst.

Belege: [Hauptansicht](screenshots/besucher/suche__suche__top.png), [Manifest](screenshots/besucher/suche__suche.json).

## 2. Technische Realität

Die vorgesehene Suche verwendet `/api/search/global` und `/api/search/facets`. Diese lesen je nach Rolle `ftw_posts`, `splitter`, `themen`, `raeume`, `gedankenblasen`, `entity_thinking_log`, `traumspuren`, `schlafbriefe`, `schattenkommentare`, `events`, `groups` und `substance_catalog`.

## 3. Reale Aktivität

Der Tab selbst war im Ausgangszustand inaktiv. Die Such-API lebt nachweislich im `ARCHÄOLOGIE`-Tab und lieferte dort HTTP 200 sowie reale Ergebnisse. Das Suchorgan existiert technisch, wird hier aber erst nach Nutzereingabe sichtbar.

### Ergänzende Lebendigkeitsabgrenzung

- **Aktiv:** Eingabe und serverseitige Such-APIs.
- **Passiv:** leerer Startzustand.
- **Simuliert:** keine.
- **Vorbereitet:** Facetten und viele Objekttypen.
- **Ungenutzt:** die Leistungsfähigkeit bleibt ohne Eingabe unsichtbar.
- **Konzeptionell:** mehrere spezialisierte Suchmodi.

## 4. Ursprung

Die Suche sollte den wachsenden Weltbestand über Typen und Herkunft auffindbar machen. In der 490-Punkte-Liste ist sie als forensische Mehrmodus-Suche gedacht, nicht bloß als Textfeld.

## 5. Weltfunktion

Orientierung im Bestand und Wiederfinden.

## 6. Überschneidungen

`ARCHÄOLOGIE` nutzt dieselbe globale Suche bereits als historisches Register und zeigt sofort Ergebnisse. `WISSEN` besitzt eigene Kategorienavigation.

## 7. Einzugsrelevanz

**etwas wichtiger**

Der wachsende Bestand erhöht den Suchbedarf, ohne die Redundanz zur Archäologie aufzuheben.

## 8. Verlustanalyse

- **Technischer Verlust:** freie globale Abfrage. Such-API bliebe über Archäologie nutzbar.
- **Weltverlust:** gering.
- **Nutzerverlust:** gezieltes Wiederfinden würde erschwert.
- **Erinnerungsverlust:** Inhalte blieben, würden schwerer auffindbar.

## 9. Bewertung

### ÜBERGANGSLÖSUNG

## 10. Empfehlung

**Zusammenlegen.** `ARCHÄOLOGIE` ist bereits der lebendigere Körper derselben Suchinfrastruktur.

## 11. Langfristige Weltperspektive

Unter der Annahme, dass Wesen seit einem Jahr dauerhaft in Flextrawurst leben, Resonanzen, Gruppen und Träume existieren, die KompOase lebt und der Weltstrom läuft:

Die bestehende Suche würde wichtiger, weil Posts, Events, Träume, Gruppen und Splitter stark wachsen. Ihre Funktion bliebe jedoch eng mit Archäologie verbunden.

## Abschluss: Fazit

Überschätzt wurde der Eigenstand dieses Tabs. Unterschätzt wurde die reale Breite seiner Backend-Suche. Die API lebt, die Oberfläche zeigt im Ruhezustand fast nichts. Nach dem Einzug wächst der Bedarf, nicht zwingend der Bedarf an einem getrennten Tab. Allein gehört `SUCHE` nicht zum Herzen der Welt.
