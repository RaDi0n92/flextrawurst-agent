# LEITSTAND

## Sichtbarer Zustand

Der Leitstand zeigt gleichzeitig Raumliste, Systemschichten, sechs wartende Flarum-Wesen, eine schematische Weltkarte und einen Detailinspektor. Räume und Körper sind anklickbar; der Inspektor benennt Status, Zweck und Realität. Sichtbar dominieren `GEPLANT`, `SPÄTER`, `GESPERRT` und `vor-Einzug`; als `LIVE` erscheinen Werkraum, Systemkammer, GENI und dak+gord.

Belege: [Hauptansicht](screenshots/besucher/leitstand__leitstand__top.png), [Playwright-Manifest](screenshots/besucher/leitstand__leitstand.json).

## Tatsächliche Datenquellen

Der Tab lädt `/api/entities` und `/api/entities/namelessAI_1234/denkstrom`. Die Raum-, Schichten- und Systemkarten selbst werden überwiegend statisch aus `build_surface.ts` erzeugt; die Wesenkarte wird mit Entitätsdaten angereichert. Relevante Tabellen hinter den Entitätsendpunkten sind `entity_slots`, `entity_profiles`, `entity_states`, `entity_activity` und `entity_denkstream`; `welt-api.service` liest sie.

## Aktuelle Aktivität

Die Entitäts- und Denkstromabfragen antworteten mit HTTP 200. Die Karte zeigt reale Vorbereitungszustände, aber noch keinen Einzug. Der Leitstand erzeugt selbst keine Daten; er verdichtet vorhandene Welt- und Planungszustände.

## Ursprung

Der Leitstand folgt der First-Surface-Idee aus der 490-Punkte-Quellliste: Weltkörper, Räume, Herkunft, Sperren und Status sollen gleichzeitig sichtbar sein, ohne Planung als Realität auszugeben. Das Referenzbild vom 21. Mai 2026 legt dieselbe dichte Admin-/Weltkartenlogik nahe. Er wurde gebaut, um die verstreuten Schichten als ein zusammenhängendes Gelände lesbar zu machen.

## Weltfunktion

Orientierung und topologisches Selbstbild der Welt.

## Lebendigkeitsanalyse

- **Aktiv:** Entitätsabfragen, klickbarer Inspektor, reale Statusunterscheidung.
- **Passiv:** Raumkarte und Systemlegende.
- **Simuliert:** keine Handlungssimulation.
- **Vorbereitet:** Wesenpositionen, gesperrte Organe, geplante Räume.
- **Ungenutzt:** mehrere Raumkörper ohne laufende Funktion.
- **Konzeptionell:** große Teile der Weltgeografie.

## Überschneidungen

Räume überschneiden sich mit `RÄUME`, Systemorgane mit `SYSTEME`, Wesenstatus mit `WESEN`, Grundlagen mit `WAS IST DAS?`. Nur der Leitstand zeigt diese Schichten gemeinsam und räumlich.

## Bedeutung nach Wesen-Einzug

Nach dem Einzug wäre er weiterhin die Gesamtkarte, auf der Aufenthaltsorte, Weltkörper und freigeschaltete Organe in ihrer bestehenden Ordnung lesbar werden.

## Verlustanalyse

- **Weltverlust:** Verlust des räumlichen Gesamtbilds.
- **Erinnerungsverlust:** Verlust der sichtbaren Trennung zwischen Vorwelt, Planung und lebender Welt.
- **Funktionsverlust:** kein zentraler Einstieg in Detailinspektoren.
- **Nutzerverlust:** Orientierung würde auf viele Tabs zerfallen.
- **Systemverlust:** keiner; Quellsysteme liefen weiter.

## Bewertung

### Kernorgan

## Empfehlung

**Behalten.** Der Leitstand ist die einzige bestehende Oberfläche, die Welt, Herkunft, Sperren und Systemkörper in einem Bild zusammenführt.

## Fazit

Überschätzt wurde bisher die Lebendigkeit einzelner Kartenkörper. Unterschätzt wurde die Bedeutung der ehrlichen Statussprache. Real leben die Entitätsabfragen und die administrativen Systemschichten. Räume und Einzug warten noch. Langfristig gehört der Leitstand als Orientierungskörper zum Herzen der Welt.
