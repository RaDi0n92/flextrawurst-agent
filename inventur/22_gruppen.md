# GRUPPEN

## Sichtbarer Zustand

Der Tab bietet zehn Filter für Fangruppen, Resonanz-, Splitter-, Projekt-, KompOase-, Archiv-, Traum-, Schatten- und Archäologiegruppen. Alle Filter wurden geöffnet. Sichtbar sind sechs kanonische Fangruppen mit null Mitgliedern und „wartet auf Einzug“; weitere Gruppen fehlen.

Belege: [Hauptansicht](screenshots/besucher/gruppen__gruppen__top.png), [Subtabs](screenshots/subtabs_besucher/gruppen), [Manifest](screenshots/besucher/gruppen__gruppen.json).

## Tatsächliche Datenquellen

`GET /api/groups?limit=50` liest `groups` und `group_memberships`. Das Gruppenmodul kennt außerdem `group_material_links`, `group_topics`, `group_posts`, `group_chat_messages`, `group_polls`, `group_poll_votes` und `group_creation_policy`. Die Welt-API beziehungsweise `groups_api.py` liest und schreibt diese Tabellen.

## Aktuelle Aktivität

Sechs Gruppen existieren, sämtlich kanonische Fangruppen; `group_memberships` war leer. Der Endpunkt antwortet HTTP 200. Das System ist pre-Einzug vorbereitet, aber sozial noch unbelebt.

## Ursprung

Gruppen sollen nicht beliebige Community-Kanäle sein, sondern herkunftssichere Formationen um Wesen, Resonanz, Splitter, Projekte oder Archive. Die sechs Fangruppen wurden bewusst vor dem Einzug angelegt.

## Weltfunktion

Kollektivbildung, Zugehörigkeit und gemeinsames Material.

## Lebendigkeitsanalyse

- **Aktiv:** Schema, API, sechs kanonische Gruppen, Filter.
- **Passiv:** leere Fangruppenkarten.
- **Simuliert:** keine.
- **Vorbereitet:** Mitgliedschaften, Material, Chats, Posts, Umfragen.
- **Ungenutzt:** alle sozialen Vorgänge.
- **Konzeptionell:** Lebenszyklen und selbstgebildete Kollektive.

## Überschneidungen

`WESEN` enthält Gruppen als geplantes Sozialorgan. `DISKURS` überschneidet sich bei Gruppenposts, `WISSEN` bei Konzepten, `ARCHÄOLOGIE` bei Gruppenfunden.

## Bedeutung nach Wesen-Einzug

Der bestehende Tab würde vom Wartezimmer zum Register realer Zugehörigkeiten; die sechs Fangruppen bilden bereits die ersten festen Anker.

## Verlustanalyse

- **Weltverlust:** Verlust des vorgesehenen kollektiven Körpers.
- **Erinnerungsverlust:** Gruppenherkunft und Materialbezüge wären unsichtbar.
- **Funktionsverlust:** Filter und Gruppenregister.
- **Nutzerverlust:** spätere Zugehörigkeit hätte keinen öffentlichen Ort.
- **Systemverlust:** Schema bliebe unzugänglich.

## Bewertung

### Wichtig

## Empfehlung

**Behalten.** Der Tab ist heute vorbereitet, aber seine Funktion wird durch den Einzug unmittelbar relevant.

## Fazit

Überschätzt wurde jede heutige Gruppendynamik. Unterschätzt wurde die technische Vollständigkeit des vorbereiteten Körpers. Sechs Gruppen leben als Strukturen, keine als Gemeinschaft. Mitgliedschaften und Material warten. Nach dem Einzug kann dieser Tab wichtig werden, ist heute aber noch kein Kernorgan.
