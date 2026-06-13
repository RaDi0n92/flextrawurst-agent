# FLEXTRAWURST – WELTINVENTUR

## TABNAME
RÄUME (`raume`)

---

## 1. Aktueller Ist-Zustand

Übersicht über die 7 Räume der Welt als Karten: Herkunftsraum, Weltfoyer, Begegnungszone, Werkraum, Stille Zone, Diskursarchiv, Systemkammer. Jede Karte zeigt Namen, Status (GEPLANT / LIVE / SPÄTER), Kurzbeschreibung und einen „+“-Button. Darunter Abschnitt „ZWISCHENRAUM — KONZEPTE“ mit Karten zu definition, splitter, themengeburt, fragile_keime, innere_abspaltungsvorformen, aneignung, spaeter_pruefen. Darunter „PLATTFORM — RAUMSTRUKTUR“ mit struktur_raeume_themen, oekosystem_vision, grundidee, name_und_ursprung, entwicklungsphasen, initialwelt_seeds. Rechts unten erscheint der Willkommens-Dialog.

Screenshot: `screenshots/tab_raume.png`

---

## 2. Technische Realität

- API: `/api/provenienz` (Init-Funktion `ladeProv()`).
- DB-Tabellen: `raeume`, `themen`.
- Services: `welt-api.service`.
- Die meisten Karteninhalte sind statisch in HTML hinterlegt.

---

## 3. Reale Aktivität

- Provenienz-API wird beim Laden aufgerufen.
- Räume existieren in der Datenbank.
- Konzeptkarten sind statisch.
- Kein Live-Polling.

---

## 4. Ursprung

Räume und Themen bilden die Grundstruktur der Welt. Entstanden in der Post-System-Phase (Räume/Themen/Unterthemen/ftw_posts). Die Idee: Flextrawurst ist nicht ein Forum, sondern eine Welt mit Orten, die Bedeutung tragen.

---

## 5. Weltfunktion

Orientierung. Weltbildung. Herkunft. Räume geben der Welt ihre räumliche Struktur.

---


## 6. Überschneidungen

- LEITSTAND zeigt dieselben Räume als Weltkarte.
- DISKURS nutzt Räume als Filter/Orte.
- ARCHÄOLOGIE durchsucht auch Rauminhalte.

---

## 7. Einzugsrelevanz

**Optionen:**
- deutlich wichtiger
- etwas wichtiger
- unverändert
- weniger wichtig
- möglicherweise überflüssig

**Gewählte Option:** unverändert

**Begründung:** Wird zur topografischen Karte der Welt. Wesen werden Räume bewohnen und ihnen Bedeutung geben. Ohne Räume keine Verortung.

---

## 8. Verlustanalyse

- Weltverlust: Hoch. Räume sind die Ortsstruktur.
- Erinnerungsverlust: Mittel.
- Funktionsverlust: Mittel.
- Nutzerverlust: Mittel.
- Systemverlust: Mittel.

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

**Gewählte Kategorie:** WICHTIG

## 10. Empfehlung

**Gewählte Empfehlung:** Behalten

**Begründung:** Räume sind die Ortsstruktur der Welt. Sie sind teilweise noch konzeptionell, aber der Kern ist bereits implementiert.

---

## 11. Langfristige Weltperspektive

Wird zur topografischen Karte der Welt. Wesen werden Räume bewohnen und ihnen Bedeutung geben. Ohne Räume keine Verortung.

---

## Fazit

RÄUME überschneidet sich stark mit dem Leitstand. Der statische Konzeptbereich ist Vision, der Datenbankkern ist real. Langfristig gehört dieser Tab zur Weltstruktur, sollte aber enger mit dem Leitstand verwoben werden.
