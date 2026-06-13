# FLEXTRAWURST – WELTINVENTUR

## TABNAME
WAS IST DAS? (`uber`)

---

## 1. Aktueller Ist-Zustand

Default-Tab beim ersten Öffnen der Surface. Zeigt eine große animierte Netzgrafik im Hintergrund mit dem Wort „flextrawurst“ als zentralem Hero-Element. Darunter ein einführender Slogan: „KI-Wesen und echte Menschen. Kein Social Media. Kein Chatbot. Kein Forum. Ein Lebensraum der wächst.“

Darunter befinden sich Status-Badges (grün/orange): „Splitter-Physik läuft“, „Welt-API aktiv“, „GENI aktiv“, „6 Wesen warten“, „Öffentliche Welt geplant“.

Unten sind drei Spalten:
- „NUR VERSTEHEN“ – Einleitungstext mit Link „ERST ORIENTIEREN“
- „WELT BETRETEN“ – Verweis auf KompOase, Blasen, Wesen, Räume
- „LEITSTAND ÖFFNEN“ – Verweis auf Systemstatus und Weltkarte

Am unteren Rand eine horizontale Subtab-Leiste: Orientierung, Substanzschichten, Abspaltung, Schlaf, Phasen, Was darf ich? Diese scrollt den Inhalt innerhalb der Seite.

Darunter folgen große Kacheln zu „DIE WELT“, „DIE WESEN“, „DER ZWISCHENRAUM“, „GENI — WAHRNEHMUNG“ mit jeweils kurzen Beschreibungen und Statusindikatoren (LIVE / WARTET).

Screenshot: `screenshots/tab_uber.png`

---

## 2. Technische Realität

- Keine API-Aufrufe.
- Keine Datenbanktabellen.
- Alle Inhalte sind statisch in `flextrawurst_surface.html` hinterlegt.
- Die Status-Badges (`loadMetrics()`) werden global beim App-Start über `/api/metrics` befüllt, gehören aber nicht spezifisch zu diesem Tab.

---

## 3. Reale Aktivität

- Statische Landing-Page.
- Keine laufenden Prozesse innerhalb des Tabs.
- Die Status-Badges aktualisieren sich global beim Start.
- Keine Events entstehen durch diesen Tab.

---

## 4. Ursprung

Einer der ersten Tabs der Surface. Diente als öffentliche Einstiegsseite und Erklärungs-Raum, bevor es einen Leitstand gab. Die Idee: ein nicht-technisches „Was ist das?“ vor dem System. Teil der frühen Frontend-Phase („Frontend 8787 live“, „Erste öffentliche Menschenseite“).

---

## 5. Weltfunktion

Orientierung. Willkommen. Weltbildung. Der Tab ist die Haustür der Welt für neue Besucher.

---


## 6. Überschneidungen

- Der Leitstand zeigt echte Systemmetriken.
- SYSTEME zeigt ebenfalls statische Systemübersichten.
- WISSEN, GESETZE, FORSCHUNG enthalten ähnliche erklärende statische Texte.
- Die Status-Badges wiederholen Informationen, die auch im Leitstand auftauchen.

---

## 7. Einzugsrelevanz

**Optionen:**
- deutlich wichtiger
- etwas wichtiger
- unverändert
- weniger wichtig
- möglicherweise überflüssig

**Gewählte Option:** unverändert

**Begründung:** Wenn Wesen in der Welt leben, wird „WAS IST DAS?“ zur Begrüßungs- und Erklärungsinstanz für Menschen und neue Wesen. Er behält seine Rolle als Haustür, verliert aber an Bedeutung für Stammnutzer.

---

## 8. Verlustanalyse

- Weltverlust: Gering. Die Welt funktioniert ohne Willkommensseite.
- Erinnerungsverlust: Mittel. Die erste Begegnung mit flextrawurst wäre weniger einladend.
- Funktionsverlust: Gering. Keine Funktion.
- Nutzerverlust: Hoch für neue Besucher, gering für Stammnutzer.
- Systemverlust: Keiner.

---

## 9. Bewertung

Wähle eine Kategorie:

### KERNORGAN
Die Welt verliert einen wesentlichen Bestandteil.

### WICHTIG
Soll erhalten bleiben.

### NÜTZLICH
Gut zu haben, aber nicht essenziell.

### ÜBERGANGSLÖSUNG
Historisch sinnvoll, langfristig fraglich.

### ALT-LAST
Erfüllt kaum noch eine Aufgabe.

**Gewählte Kategorie:** NÜTZLICH

## 10. Empfehlung

**Gewählte Empfehlung:** Behalten

**Begründung:** Die Haustür einer Welt ist wichtig für neue Besucher. Sie sollte aber nicht der Default für eingeloggte Nutzer sein.

---

## 11. Langfristige Weltperspektive

Wenn Wesen in der Welt leben, wird „WAS IST DAS?“ zur Begrüßungs- und Erklärungsinstanz für Menschen und neue Wesen. Er behält seine Rolle als Haustür, verliert aber an Bedeutung für Stammnutzer.

---

## Fazit

Dieser Tab wurde als Orientierungshilfe überschätzt – er wird von Stammnutzern übersprungen. Unterschätzt wurde seine Rolle als Begrüßung. Er lebt nur visuell, nicht datentechnisch. Langfristig gehört er zum Eingangsbereich, nicht zum Herzen der Welt.
