# ADMIN

## Sichtbarer Zustand

Der geschützte Tab besitzt sieben Subtabs: Nutzer, Supporter, Inhalte, Wesen, Bilder, System und Einzug. Alle wurden geöffnet. Die Nutzeransicht zeigt acht aktive Nutzer, alle mit Adminrolle, sowie Erstellen-, Bearbeiten-, Deaktivieren- und Entfernen-Aktionen; weitere Bereiche enthalten ihre jeweiligen Verwaltungsoberflächen.

Belege: [Hauptansicht](screenshots/admin/admin__admin__top.png), [Subtabs](screenshots/subtabs_admin), [Manifest](screenshots/admin/admin__admin.json).

## Tatsächliche Datenquellen

Im Hauptlauf wurden `/api/admin/users`, `/api/admin/supporter/bewerbungen`, `/api/entities` und ein Entitäts-Denkstrom geladen. Dahinter stehen `human_users`, `human_profiles`, `user_modules`, `supporter_bewerbungen`, Entitätstabellen, Inhalts- und Moderationstabellen. Schreibende Admin-Endpunkte können Nutzer, Inhalte, Bilder, Wesenstatus und Einzug verändern.

## Aktuelle Aktivität

Die Admin-APIs antworteten HTTP 200. Acht reale Nutzer werden verwaltet; Bewerbungs-, Entitäts- und Moderationskörper existieren. Der Tab ist funktional, aber seine breite Eingriffsmacht wurde in der Inventur nur lesend geprüft.

## Ursprung

Admin wurde aus dem Grundgesetz gebaut, dass Verwaltung alles sehen und kontrollieren können muss, ohne Daten physisch zu löschen. Er ist kein Weltort für Besucher, sondern die Steuerungs- und Verantwortlichkeitsschicht.

## Weltfunktion

Fürsorge, Grenzsetzung und operative Verwaltung.

## Lebendigkeitsanalyse

- **Aktiv:** Nutzerverwaltung und mehrere Verwaltungs-APIs.
- **Passiv:** Bereiche ohne aktuelle Fälle.
- **Simuliert:** keine.
- **Vorbereitet:** Einzug und umfassendere Moderation.
- **Ungenutzt:** Teile von Supporter-, Bild- und Einzugsverwaltung.
- **Konzeptionell:** keine Grundfunktion.

## Überschneidungen

`LEITSTAND` und `SYSTEME` erklären Zustände, greifen aber nicht ein. `EINSICHT` ist diagnostisch. `MENSCHEN` zeigt die öffentliche Seite derselben Nutzer.

## Bedeutung nach Wesen-Einzug

Der vorhandene Tab würde für Einzug, Moderation, Sichtbarkeit und Notfälle noch wichtiger, bliebe aber ausdrücklich außerhalb der öffentlichen Weltbühne.

## Verlustanalyse

- **Weltverlust:** indirekt hoch durch fehlende Pflege und Grenzsetzung.
- **Erinnerungsverlust:** gering.
- **Funktionsverlust:** zentrale Verwaltung fast aller kontrollierten Bereiche.
- **Nutzerverlust:** Accounts und Inhalte wären kaum steuerbar.
- **Systemverlust:** erhebliche operative Handlungsunfähigkeit.

## Bewertung

### Kernorgan

## Empfehlung

**Behalten.** Er ist ein notwendiges verborgenes Organ, kein Besucherinhalt.

## Fazit

Überschätzt wurde nicht seine Funktion, sondern möglicherweise die Gleichförmigkeit der Rollen: aktuell sind alle Nutzer Admins. Unterschätzt wurde die Breite der vorhandenen Verwaltungsflächen. Nutzerverwaltung lebt. Einzug und manche Moderationswege warten. Als verborgenes Organ gehört Admin zum Systemherzen.
