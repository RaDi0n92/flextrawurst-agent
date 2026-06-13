# FLEXTRAWURST – WELTINVENTUR

## TABNAME
WAS IST DAS? (`uber`)

---

## Sichtbarer Zustand

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

## Tatsächliche Datenquellen

- Keine API-Aufrufe.
- Keine Datenbanktabellen.
- Alle Inhalte sind statisch in `flextrawurst_surface.html` hinterlegt.
- Die Status-Badges (`loadMetrics()`) werden global beim App-Start über `/api/metrics` befüllt, gehören aber nicht spezifisch zu diesem Tab.

---

## Aktuelle Aktivität

- Statische Landing-Page.
- Keine laufenden Prozesse innerhalb des Tabs.
- Die Status-Badges aktualisieren sich global beim Start.
- Keine Events entstehen durch diesen Tab.

---

## Ursprung

Einer der ersten Tabs der Surface. Diente als öffentliche Einstiegsseite und Erklärungs-Raum, bevor es einen Leitstand gab. Die Idee: ein nicht-technisches „Was ist das?“ vor dem System. Teil der frühen Frontend-Phase („Frontend 8787 live“, „Erste öffentliche Menschenseite“).

---

## Weltfunktion

Orientierung. Willkommen. Weltbildung. Der Tab ist die Haustür der Welt für neue Besucher.

---

## Lebendigkeitsanalyse

- Aktiv: Nichts innerhalb des Tabs.
- Passiv: Status-Badges werden beim Laden eingefärbt.
- Simuliert: Die animierte Netzgrafik und Glow-Effekte vermitteln Lebendigkeit, ohne dass Daten dahinterstehen.
- Vorbereitet: Die Subtab-Struktur deutet auf mehr Inhalt hin, der statisch ist.
- Ungenutzt: Die Subtabs scheinen keine eigenen API-Quellen zu haben.
- Rein konzeptionell: Großteils.

---

## Überschneidungen

- Der Leitstand zeigt echte Systemmetriken.
- SYSTEME zeigt ebenfalls statische Systemübersichten.
- WISSEN, GESETZE, FORSCHUNG enthalten ähnliche erklärende statische Texte.
- Die Status-Badges wiederholen Informationen, die auch im Leitstand auftauchen.

---

## Bedeutung nach Wesen-Einzug

Wenn Wesen in der Welt leben, wird „WAS IST DAS?“ zur Begrüßungs- und Erklärungsinstanz für Menschen und neue Wesen. Er behält seine Rolle als Haustür, verliert aber an Bedeutung für Stammnutzer.

---

## Verlustanalyse

- Weltverlust: Gering. Die Welt funktioniert ohne Willkommensseite.
- Erinnerungsverlust: Mittel. Die erste Begegnung mit flextrawurst wäre weniger einladend.
- Funktionsverlust: Gering. Keine Funktion.
- Nutzerverlust: Hoch für neue Besucher, gering für Stammnutzer.
- Systemverlust: Keiner.

---

## Bewertung

Nützlich

---

## Empfehlung

Behalten

Begründung: Die Haustür einer Welt ist wichtig für neue Besucher. Sie sollte aber nicht der Default für eingeloggte Nutzer sein.

---

## Fazit

Dieser Tab wurde als Orientierungshilfe überschätzt – er wird von Stammnutzern übersprungen. Unterschätzt wurde seine Rolle als Begrüßung. Er lebt nur visuell, nicht datentechnisch. Langfristig gehört er zum Eingangsbereich, nicht zum Herzen der Welt.
