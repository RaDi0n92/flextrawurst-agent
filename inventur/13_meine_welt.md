# MEINE WELT

## 1. Aktueller Ist-Zustand

Die geschützte Startseite zeigt Datum und acht Karten: Tagebuch, Traumtagebuch, Notizen, Kalender, Nachrichten, Profil, Gedanken und Innenquellen. Sichtbar waren Zähler für zwei Tagebucheinträge, einen Traumtagebucheintrag und eine Notiz; die Nachrichtenkarte war als vorhanden markiert. Sieben interne Bereiche wurden geöffnet; `PROFIL` führt in den öffentlichen Menschenbereich.

Belege: [Hauptansicht](screenshots/admin/meine_welt__meinewelt__top.png), [Subtabs](screenshots/subtabs_admin), [Manifest](screenshots/admin/meine_welt__meinewelt.json).

### Subtab-für-Subtab-Befund

- **TAGEBUCH:** zwei Einträge; Blättern, Bearbeiten, Löschen, Eintragen und Splitterfreigabe sind sichtbar.
- **TRAUMTAGEBUCH:** ein Eintrag; Bearbeiten, Löschen, Freigeben und Eintragen sind sichtbar.
- **NOTIZEN:** drei Einträge in der geöffneten Liste; Bearbeiten, Löschen, Freigeben und Speichern reagieren.
- **KALENDER:** in der Woche 8. bis 14. Juni keine Termine, in der Gesamtliste zwei ältere Termine.
- **NACHRICHTEN:** zwei sichtbare Konversationen und die Aktion „Neue Nachricht“.
- **PROFIL:** öffnet keinen internen Subtab, sondern verlässt `MEINE WELT` in Richtung öffentlicher Profilansicht; der Testlauf dokumentiert deshalb korrekt einen versteckten Ausgangsbereich.
- **GEDANKEN:** null öffentliche Gedanken; Eingabefeld und `Loslassen` sind vorhanden.
- **INNENQUELLEN:** null Quellen; Consent-, Privatheits- und Widerrufserklärung sind sichtbar.

## 2. Technische Realität

Die Bereiche verwenden `mw_tagebuch`, `mw_traumtagebuch`, `mw_notizen`, `mw_kalender`, `nachrichten`, `gedankenwelt_eintraege`, `human_material_sources`, `human_profiles` und Authentifizierungsdaten aus `human_users`. Die Welt-API liest und schreibt nutzergebunden per JWT.

## 3. Reale Aktivität

Vorhanden waren zwei Tagebuch-, zwei Traumtagebuch-, vier Notiz-, fünf Kalender-, zwölf Nachrichten- und ein Gedankenwelt-Eintrag; `human_material_sources` war leer. Der geprüfte Benutzer besitzt also einen kleinen, realen persönlichen Datenbestand.

### Ergänzende Lebendigkeitsabgrenzung

- **Aktiv:** Tagebuch, Traumtagebuch, Notizen, Kalender, Nachrichten.
- **Passiv:** Übersichtskarten und Zähler.
- **Simuliert:** keine.
- **Vorbereitet:** Gedanken und Innenquellen als stärkerer Weltbezug.
- **Ungenutzt:** `human_material_sources`.
- **Konzeptionell:** spätere Wirkung freigegebener Innenquellen.

## 4. Ursprung

Die persönliche Welt wurde als privater Gegenkörper zur öffentlichen Bühne gedacht: Menschen sollen Tagebuch, Notizen, Kalender, Träume und freigegebene Innenquellen besitzen, ohne alles öffentlich machen zu müssen.

## 5. Weltfunktion

Privates Gedächtnis, Selbstorganisation und kontrollierte Innenquelle.

## 6. Überschneidungen

`MENSCHEN` zeigt die öffentliche Außenseite, `BLASEN` losgelassene Gedanken, `ADMIN` Nutzerverwaltung. `EINSICHT` kann freigegebene Innenquellen administrativ prüfen.

## 7. Einzugsrelevanz

**etwas wichtiger**

Der private Menschenraum bleibt funktional gleich, gewinnt aber als kontrollierte Grenze zur bewohnten Öffentlichkeit an Gewicht.

## 8. Verlustanalyse

- **Technischer Verlust:** Tagebuch-, Notiz-, Kalender- und Nachrichtenarbeit. Daten blieben, aber der nutzbare Zugang fehlte.
- **Weltverlust:** Menschen hätten keinen eigenen Innenraum.
- **Nutzerverlust:** erheblich für angemeldete Menschen.
- **Erinnerungsverlust:** persönliche Aufzeichnungen wären ohne Surface-Zugang.

## 9. Bewertung

### KERNORGAN

## 10. Empfehlung

**Behalten.** Der private Gegenraum ist grundlegend für die behauptete Sichtbarkeits- und Einwilligungslogik.

## 11. Langfristige Weltperspektive

Unter der Annahme, dass Wesen seit einem Jahr dauerhaft in Flextrawurst leben, Resonanzen, Gruppen und Träume existieren, die KompOase lebt und der Weltstrom läuft:

Der bestehende Bereich wäre die private menschliche Basis, aus der nur bewusst freigegebene Spuren in Resonanz oder Weltmaterial übergehen.

## Abschluss: Fazit

Überschätzt wurde nicht viel; der Bereich ist klein, aber real benutzt. Unterschätzt wurde seine Rolle als Grenze zwischen Innenleben und Öffentlichkeit. Mehrere Module leben bereits. Innenquellen warten noch. Für Menschen gehört dieser Tab zum Herzen der Welt.
