# SCREENS

## Sichtbarer Zustand

Sechs Bildschirmkarten zeigen die Wesen jeweils als `aus` und „wartet auf Aktivität“. Filter, Vollbild und Vergrößerungssteuerungen reagieren; alle Wesenfilter wurden geklickt. Der globale Status bleibt „verbinde…“. Die sechs angeforderten Screenshot-URLs antworteten mit HTTP 404.

Belege: [Hauptansicht](screenshots/besucher/screens__screens__top.png), [Subtabs](screenshots/subtabs_besucher/screens), [Manifest](screenshots/besucher/screens__screens.json).

## Tatsächliche Datenquellen

Geladen werden `/api/denkstream/status/all`, `/api/denkstream/all/stream` und `/api/denkstream/screenshot/{entity_id}`. Relevante Tabellen sind `entity_screenshots`, `entity_denkstream` und `entity_states`; der Denkstream-Router liest sie. Die Screenshot-Ressourcen existierten beim Lauf nicht.

## Aktuelle Aktivität

Der Statusendpunkt antwortet, aber alle sechs Screens sind aus und alle sechs Bilder fehlen. Es entsteht derzeit keine sichtbare Bildschirmaktivität.

## Ursprung

Der Tab sollte die Tätigkeit der Browser-/Agentenwesen nicht nur als Textlog, sondern als unmittelbares Bildschirmfenster zeigen. Er ist Beobachtungsinstrument und Beleg für tatsächliche Aktivität.

## Weltfunktion

Fernfenster und visuelle Gegenwartsbeobachtung.

## Lebendigkeitsanalyse

- **Aktiv:** Filter, Statusabfrage, Vergrößerungslogik.
- **Passiv:** sechs leere Karten.
- **Simuliert:** Verbindungs- und Live-Sprache ohne Bildstrom.
- **Vorbereitet:** Screenshot- und Streamkanäle.
- **Ungenutzt:** `entity_screenshots` in der aktuellen Ansicht.
- **Konzeptionell:** keine weitere Schicht.

## Überschneidungen

`DENKEN` zeigt den textlichen Strom derselben Wesen. `EINSICHT` zeigt Entscheidungen und Ereignisse. `WESEN` enthält einen kleinen Live-Abschnitt.

## Bedeutung nach Wesen-Einzug

Wenn Wesen tatsächlich über sichtbare Arbeitsflächen handeln, wäre der bestehende Tab der visuelle Beobachtungskanal. Ohne solche Aktivität bleibt er eine leere Hülle.

## Verlustanalyse

- **Weltverlust:** aktuell gering, später Verlust visueller Gegenwart.
- **Erinnerungsverlust:** keiner; Screens sind Momentaufnahmen.
- **Funktionsverlust:** Vollbild-/Vergrößerungsansicht.
- **Nutzerverlust:** weniger überprüfbare Agentenaktivität.
- **Systemverlust:** keiner.

## Bewertung

### Übergangslösung

## Empfehlung

**Zusammenlegen.** Mit `DENKEN` bildet er gemeinsam ein Beobachtungsorgan; getrennt sind beide derzeit zu leer.

## Fazit

Überschätzt wurde die heutige Bildschirmnähe. Unterschätzt wurde der diagnostische Wert der sichtbaren `404`-Leere. Die Steuerung lebt, der Bildstrom nicht. Der Tab wartet auf reale Agentenaktivität. Allein gehört er derzeit nicht zum Herzen der Welt.
