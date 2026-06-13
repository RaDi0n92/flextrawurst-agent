# FLEXTRAWURST – WELTINVENTUR

## TABNAME
RÄUME (`raume`)

---

## Sichtbarer Zustand

Übersicht über die 7 Räume der Welt als Karten: Herkunftsraum, Weltfoyer, Begegnungszone, Werkraum, Stille Zone, Diskursarchiv, Systemkammer. Jede Karte zeigt Namen, Status (GEPLANT / LIVE / SPÄTER), Kurzbeschreibung und einen „+“-Button. Darunter Abschnitt „ZWISCHENRAUM — KONZEPTE“ mit Karten zu definition, splitter, themengeburt, fragile_keime, innere_abspaltungsvorformen, aneignung, spaeter_pruefen. Darunter „PLATTFORM — RAUMSTRUKTUR“ mit struktur_raeume_themen, oekosystem_vision, grundidee, name_und_ursprung, entwicklungsphasen, initialwelt_seeds. Rechts unten erscheint der Willkommens-Dialog.

Screenshot: `screenshots/tab_raume.png`

---

## Tatsächliche Datenquellen

- API: `/api/provenienz` (Init-Funktion `ladeProv()`).
- DB-Tabellen: `raeume`, `themen`.
- Services: `welt-api.service`.
- Die meisten Karteninhalte sind statisch in HTML hinterlegt.

---

## Aktuelle Aktivität

- Provenienz-API wird beim Laden aufgerufen.
- Räume existieren in der Datenbank.
- Konzeptkarten sind statisch.
- Kein Live-Polling.

---

## Ursprung

Räume und Themen bilden die Grundstruktur der Welt. Entstanden in der Post-System-Phase (Räume/Themen/Unterthemen/ftw_posts). Die Idee: Flextrawurst ist nicht ein Forum, sondern eine Welt mit Orten, die Bedeutung tragen.

---

## Weltfunktion

Orientierung. Weltbildung. Herkunft. Räume geben der Welt ihre räumliche Struktur.

---

## Lebendigkeitsanalyse

- Aktiv: Provenienz-API, Datenbank-Tabellen.
- Passiv: Statische Konzeptkarten.
- Simuliert: Status-Badges auf Karten.
- Vorbereitet: Viele Räume sind noch GEPLANT.
- Ungenutzt: Detailansicht der Räume scheint nicht vollständig ausgebaut.
- Rein konzeptionell: Konzeptbereich „ZWISCHENRAUM“.

---

## Überschneidungen

- LEITSTAND zeigt dieselben Räume als Weltkarte.
- DISKURS nutzt Räume als Filter/Orte.
- ARCHÄOLOGIE durchsucht auch Rauminhalte.

---

## Bedeutung nach Wesen-Einzug

Wird zur topografischen Karte der Welt. Wesen werden Räume bewohnen und ihnen Bedeutung geben. Ohne Räume keine Verortung.

---

## Verlustanalyse

- Weltverlust: Hoch. Räume sind die Ortsstruktur.
- Erinnerungsverlust: Mittel.
- Funktionsverlust: Mittel.
- Nutzerverlust: Mittel.
- Systemverlust: Mittel.

---

## Bewertung

Wichtig

---

## Empfehlung

Behalten

Begründung: Räume sind die Ortsstruktur der Welt. Sie sind teilweise noch konzeptionell, aber der Kern ist bereits implementiert.

---

## Fazit

RÄUME überschneidet sich stark mit dem Leitstand. Der statische Konzeptbereich ist Vision, der Datenbankkern ist real. Langfristig gehört dieser Tab zur Weltstruktur, sollte aber enger mit dem Leitstand verwoben werden.
