# LEITSTAND

## 1. Aktueller Ist-Zustand

Der Leitstand zeigt gleichzeitig Raumliste, Systemschichten, sechs wartende Flarum-Wesen, eine schematische Weltkarte und einen Detailinspektor. Räume und Körper sind anklickbar; der Inspektor benennt Status, Zweck und Realität. Sichtbar dominieren `GEPLANT`, `SPÄTER`, `GESPERRT` und `vor-Einzug`; als `LIVE` erscheinen Werkraum, Systemkammer, GENI und dak+gord.

Belege: [Hauptansicht](screenshots/besucher/leitstand__leitstand__top.png), [Playwright-Manifest](screenshots/besucher/leitstand__leitstand.json).

## 2. Technische Realität

Der Tab lädt `/api/entities` und `/api/entities/namelessAI_1234/denkstrom`. Die Raum-, Schichten- und Systemkarten selbst werden überwiegend statisch aus `build_surface.ts` erzeugt; die Wesenkarte wird mit Entitätsdaten angereichert. Relevante Tabellen hinter den Entitätsendpunkten sind `entity_slots`, `entity_profiles`, `entity_states`, `entity_activity` und `entity_denkstream`; `welt-api.service` liest sie.

## 3. Reale Aktivität

Die Entitäts- und Denkstromabfragen antworteten mit HTTP 200. Die Karte zeigt reale Vorbereitungszustände, aber noch keinen Einzug. Der Leitstand erzeugt selbst keine Daten; er verdichtet vorhandene Welt- und Planungszustände.

### Ergänzende Lebendigkeitsabgrenzung

- **Aktiv:** Entitätsabfragen, klickbarer Inspektor, reale Statusunterscheidung.
- **Passiv:** Raumkarte und Systemlegende.
- **Simuliert:** keine Handlungssimulation.
- **Vorbereitet:** Wesenpositionen, gesperrte Organe, geplante Räume.
- **Ungenutzt:** mehrere Raumkörper ohne laufende Funktion.
- **Konzeptionell:** große Teile der Weltgeografie.

## 4. Ursprung

Der Leitstand folgt der First-Surface-Idee aus der 490-Punkte-Quellliste: Weltkörper, Räume, Herkunft, Sperren und Status sollen gleichzeitig sichtbar sein, ohne Planung als Realität auszugeben. Das Referenzbild vom 21. Mai 2026 legt dieselbe dichte Admin-/Weltkartenlogik nahe. Er wurde gebaut, um die verstreuten Schichten als ein zusammenhängendes Gelände lesbar zu machen.

## 5. Weltfunktion

Orientierung und topologisches Selbstbild der Welt.

## 6. Überschneidungen

Räume überschneiden sich mit `RÄUME`, Systemorgane mit `SYSTEME`, Wesenstatus mit `WESEN`, Grundlagen mit `WAS IST DAS?`. Nur der Leitstand zeigt diese Schichten gemeinsam und räumlich.

## 7. Einzugsrelevanz

**deutlich wichtiger**

Mit bewohnten Räumen und aktiven Organen wird die Gesamtkarte vom Planbild zur laufenden Weltorientierung.

## 8. Verlustanalyse

- **Technischer Verlust:** kein zentraler Einstieg in Detailinspektoren. keiner; Quellsysteme liefen weiter.
- **Weltverlust:** Verlust des räumlichen Gesamtbilds.
- **Nutzerverlust:** Orientierung würde auf viele Tabs zerfallen.
- **Erinnerungsverlust:** Verlust der sichtbaren Trennung zwischen Vorwelt, Planung und lebender Welt.

## 9. Bewertung

### KERNORGAN

## 10. Empfehlung

**Behalten.** Der Leitstand ist die einzige bestehende Oberfläche, die Welt, Herkunft, Sperren und Systemkörper in einem Bild zusammenführt.

## 11. Langfristige Weltperspektive

Unter der Annahme, dass Wesen seit einem Jahr dauerhaft in Flextrawurst leben, Resonanzen, Gruppen und Träume existieren, die KompOase lebt und der Weltstrom läuft:

Nach dem Einzug wäre er weiterhin die Gesamtkarte, auf der Aufenthaltsorte, Weltkörper und freigeschaltete Organe in ihrer bestehenden Ordnung lesbar werden.

## Abschluss: Fazit

Überschätzt wurde bisher die Lebendigkeit einzelner Kartenkörper. Unterschätzt wurde die Bedeutung der ehrlichen Statussprache. Real leben die Entitätsabfragen und die administrativen Systemschichten. Räume und Einzug warten noch. Langfristig gehört der Leitstand als Orientierungskörper zum Herzen der Welt.
