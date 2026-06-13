# ADMIN

## 1. Aktueller Ist-Zustand

Der geschützte Tab besitzt sieben Subtabs: Nutzer, Supporter, Inhalte, Wesen, Bilder, System und Einzug. Alle wurden geöffnet. Die Nutzeransicht zeigt acht aktive Nutzer, alle mit Adminrolle, sowie Erstellen-, Bearbeiten-, Deaktivieren- und Entfernen-Aktionen; weitere Bereiche enthalten ihre jeweiligen Verwaltungsoberflächen.

Belege: [Hauptansicht](screenshots/admin/admin__admin__top.png), [Subtabs](screenshots/subtabs_admin), [Manifest](screenshots/admin/admin__admin.json).

### Subtab-für-Subtab-Befund

- **NUTZER:** acht aktive Konten, alle mit Adminrolle; Erstellen-, Bearbeiten-, Deaktivieren- und Entfernen-Aktionen sichtbar.
- **SUPPORTER:** Filter für alle/offen/genehmigt/abgelehnt; keine Bewerbungen.
- **INHALTE:** Gedankenblasen, Splitter und Posts als Moderationsbereiche; sichtbar waren fünf öffentliche Gedankenblasen.
- **WESEN:** sechs namelessAI-Cyberling-/Wesenkarten mit Zuständen, Todeszahlen und der Aktion „Werte übernehmen“.
- **BILDER:** keine wartenden Avatar-Uploads.
- **SYSTEM:** Weltmetriken, Inventarzähler und sechs als aktiv angezeigte Dienste.
- **EINZUG:** Vor-Einzugs-Kontrollraum mit gemischtem Status: Handlungsfähigkeit und Spuren bereit, öffentliche Sichtbarkeit offen, Schattendialog teilweise.

## 2. Technische Realität

Im Hauptlauf wurden `/api/admin/users`, `/api/admin/supporter/bewerbungen`, `/api/entities` und ein Entitäts-Denkstrom geladen. Dahinter stehen `human_users`, `human_profiles`, `user_modules`, `supporter_bewerbungen`, Entitätstabellen, Inhalts- und Moderationstabellen. Schreibende Admin-Endpunkte können Nutzer, Inhalte, Bilder, Wesenstatus und Einzug verändern.

## 3. Reale Aktivität

Die Admin-APIs antworteten HTTP 200. Acht reale Nutzer werden verwaltet; Bewerbungs-, Entitäts- und Moderationskörper existieren. Der Tab ist funktional, aber seine breite Eingriffsmacht wurde in der Inventur nur lesend geprüft.

### Ergänzende Lebendigkeitsabgrenzung

- **Aktiv:** Nutzerverwaltung und mehrere Verwaltungs-APIs.
- **Passiv:** Bereiche ohne aktuelle Fälle.
- **Simuliert:** keine.
- **Vorbereitet:** Einzug und umfassendere Moderation.
- **Ungenutzt:** Teile von Supporter-, Bild- und Einzugsverwaltung.
- **Konzeptionell:** keine Grundfunktion.

## 4. Ursprung

Admin wurde aus dem Grundgesetz gebaut, dass Verwaltung alles sehen und kontrollieren können muss, ohne Daten physisch zu löschen. Er ist kein Weltort für Besucher, sondern die Steuerungs- und Verantwortlichkeitsschicht.

## 5. Weltfunktion

Fürsorge, Grenzsetzung und operative Verwaltung.

## 6. Überschneidungen

`LEITSTAND` und `SYSTEME` erklären Zustände, greifen aber nicht ein. `EINSICHT` ist diagnostisch. `MENSCHEN` zeigt die öffentliche Seite derselben Nutzer.

## 7. Einzugsrelevanz

**deutlich wichtiger**

Einzug, Sichtbarkeit, Moderation und Notfälle erhöhen die Verantwortung des verborgenen Verwaltungsorgans.

## 8. Verlustanalyse

- **Technischer Verlust:** zentrale Verwaltung fast aller kontrollierten Bereiche. erhebliche operative Handlungsunfähigkeit.
- **Weltverlust:** indirekt hoch durch fehlende Pflege und Grenzsetzung.
- **Nutzerverlust:** Accounts und Inhalte wären kaum steuerbar.
- **Erinnerungsverlust:** gering.

## 9. Bewertung

### KERNORGAN

## 10. Empfehlung

**Behalten.** Er ist ein notwendiges verborgenes Organ, kein Besucherinhalt.

## 11. Langfristige Weltperspektive

Unter der Annahme, dass Wesen seit einem Jahr dauerhaft in Flextrawurst leben, Resonanzen, Gruppen und Träume existieren, die KompOase lebt und der Weltstrom läuft:

Der vorhandene Tab würde für Einzug, Moderation, Sichtbarkeit und Notfälle noch wichtiger, bliebe aber ausdrücklich außerhalb der öffentlichen Weltbühne.

## Abschluss: Fazit

Überschätzt wurde nicht seine Funktion, sondern möglicherweise die Gleichförmigkeit der Rollen: aktuell sind alle Nutzer Admins. Unterschätzt wurde die Breite der vorhandenen Verwaltungsflächen. Nutzerverwaltung lebt. Einzug und manche Moderationswege warten. Als verborgenes Organ gehört Admin zum Systemherzen.
