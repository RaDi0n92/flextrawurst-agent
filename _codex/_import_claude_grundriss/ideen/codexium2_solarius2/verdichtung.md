---
name: codexium2-solarius2-verdichtung
description: Kontext-Verdichtung — Slider-gesteuertes Zusammenfassen von Nachrichten-Paaren, mit Kommentar-Verfeinerung und Bestaetigung, beliebig verschachtelbar
metadata:
  type: project
tags: [codexium2, solarius2, verdichtung, kontext, testbed]
status: gebaut, live getestet inkl. Verschachtelung
datum: 2026-07-06
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Was ich verstehe

Auslöser: Daniel wollte wissen, warum Chats wieder hängen — Antwort war (auch)
die MoE-Speicherbandbreiten-Realität dieses Systems: je länger ein
Gesprächsverlauf, desto länger die Prompt-Verarbeitung, bis hin zu
minutenlangen Hängern bei einzelnen sehr langen Unterhaltungen (siehe
`docs/2026-07-06_kontext_prioritaet_container_bericht.md`).

Der bestehende Kontext-Ausschluss (`kontext_toggle`, ✂️-Button) entfernt zwar
wirklich Token aus dem gesendeten Kontext — aber nur durch manuelles,
Nachricht-für-Nachricht-Ausschließen. Kein Mechanismus reduziert den Umfang
selbst. Daniels eigentliches Ziel: "quasi endlos gut weiter chatten können"
durch **echte Verdichtung** (Zusammenfassen statt nur Ausblenden) — mit voller
Kontrolle, nicht automatisch im Hintergrund.

---

## Der Ablauf (entschieden)

1. Button (🗜️ o.ä.) unter jeder Nachricht, wie die bestehenden Pin/Erinnern/
   Kontext-Buttons.
2. Klick öffnet ein Modal mit Slider (0-11): wählt, wie viele der letzten
   Ein-/Ausgabe-**Einheiten** ab dieser Stelle rückwärts in die Verdichtung
   einbezogen werden sollen.
3. Bestätigung der Auswahl → Hintergrund-Job (Email-Prinzip wie bei
   Memory-Extraktion/Abschluss) erstellt einen Zusammenfassungs-**Entwurf**.
4. Entwurf wird angezeigt. Daniel kann einen **Kommentar** dazuschreiben
   ("kürzer", "Detail X muss rein" etc.).
5. Kommentar löst eine **Neugenerierung** des Entwurfs aus, die den Kommentar
   berücksichtigt — wiederholbar, keine feste Anzahl Durchläufe.
6. Erst nach **aktivem Bestätigen** ("Übernehmen") ersetzt die Verdichtung die
   Rohtexte im an das Modell gesendeten Kontext. Die Originaltexte bleiben
   vollständig im sichtbaren Verlauf stehen (gleiches Prinzip wie Pin/
   Kontext-Ausschluss — nichts wird je gelöscht).

## Verschachtelung (entschieden, keine Tiefenbegrenzung)

Eine Verdichtung ist selbst wieder eine auswählbare, erneut verdichtbare
Einheit — beliebig tief. Beispiel: 5 einzelne Verdichtungen wurden nacheinander
erstellt; später wählt Daniel diese 5 (der Slider zählt sie wie normale
Nachrichten-Paare) und lässt sie zu EINER neuen, kürzeren Verdichtung
zusammenfassen. Die 5 alten Verdichtungen werden dabei "absorbiert" — sie
verschwinden aus der aktiven Zeitachse, ihre ursprünglichen Rohtexte bleiben
aber unverändert im Verlauf sichtbar (nur über die neue Verdichtung noch
weiter zurückverfolgbar, nicht mehr direkt als eigene Einheit wählbar).

---

## Datenstruktur die ich mir vorstelle

### Vision-Schicht
Verdichtung ist eine Faltung, kein Löschen. Der Gesprächsverlauf bleibt ein
Baum aus dem, was wirklich gesagt wurde — die Verdichtung ist nur eine
alternative, kompaktere Ansicht davon, die das Modell sieht, während der
Mensch immer noch jede einzelne Falte aufklappen und das Original lesen kann.

### Code-Skizze
```typescript
interface Verdichtung {
  id: string;
  ersetztIds: string[];       // IDs der direkt ersetzten Elemente — Nachrichten-IDs
                               // ODER IDs anderer (aelterer) Verdichtungen, beliebig gemischt
  zusammenfassung: string;     // aktueller Text, nach Kommentar-Runden ggf. mehrfach ueberschrieben
  kommentare: Array<{ text: string; ts: string }>;  // Verfeinerungs-Historie, nichts geloescht
  bestaetigt: boolean;         // erst nach "Uebernehmen" TRUE, vorher reiner Entwurf
  erstellt_am: string;
  aktualisiert_am: string;
}
// verdichtungen.json pro Charakter (analog zu container.json/memory.json)
// { verdichtungen: Verdichtung[] }
```

**Aktive Zeitachse berechnen** (fuer Slider-Anzeige UND fuer den tatsaechlichen
Prompt-Aufbau, dieselbe Funktion): eine Nachricht/Verdichtung ist "aktiv" (noch
einzeln sichtbar/waehlbar), wenn ihre ID in KEINER bestaetigten Verdichtung als
`ersetztIds`-Eintrag vorkommt. Rekursiv/transitiv — sobald V2 die ID von V1
absorbiert, verschwindet V1 automatisch aus der aktiven Zeitachse, ohne dass
das explizit nachverfolgt werden muss.

```typescript
function aktiveZeitachse(nachrichten, bestaetigteVerdichtungen) {
  const ersetzteIds = new Set(bestaetigteVerdichtungen.flatMap(v => v.ersetztIds));
  const gezeigt = new Set(); // welche Verdichtungs-IDs schon in der Zeitachse stehen
  const zeitachse = [];
  for (const msg of nachrichten) {
    if (!ersetzteIds.has(msg.id)) { zeitachse.push({ typ: 'nachricht', daten: msg }); continue; }
    const v = findeAeusserstenTraeger(msg.id, bestaetigteVerdichtungen, ersetzteIds);
    if (v && !gezeigt.has(v.id)) { zeitachse.push({ typ: 'verdichtung', daten: v }); gezeigt.add(v.id); }
  }
  return zeitachse;
}
```

**Prompt-Aufbau**: an der Stelle jeder aktiven Verdichtung wird EINE
synthetische Nachricht eingefuegt (z.B. `[Verdichtung frueherer Nachrichten]:
<zusammenfassung>`), alle davon abgedeckten Rohnachrichten/inneren
Verdichtungen werden uebersprungen.

**Neue Endpunkte** (Entwurf, analog zu Abschluss/Memory-Extraktion-Pattern):
- `POST .../verdichtung/entwurf` `{ersetztIds: string[]}` → Hintergrund-Job
  startet, generiert ersten Entwurf
- `GET .../verdichtung/entwurf/:jobId` → Status/aktueller Entwurfstext
- `POST .../verdichtung/entwurf/:jobId/kommentar` `{text}` → Neugenerierung mit
  Kommentar als Zusatzinstruktion
- `POST .../verdichtung/entwurf/:jobId/uebernehmen` → schreibt bestaetigte
  Verdichtung nach `verdichtungen.json`
- `POST .../verdichtung/entwurf/:jobId/verwerfen` → Entwurf verwerfen, nichts
  gespeichert

---

## Was ich mir merken will

Budget-Frage noch offen (nicht mit Daniel besprochen): zaehlt eine bestaetigte
Verdichtung fuer das Container-/Memory-Budget mit? Vermutlich nein (eigene
Datei, eigener Zweck) — aber falls das Kontextfenster insgesamt ein Thema
wird, hier nachtragen.

## Was noch fehlt bevor wir bauen können

Nichts Offenes mehr — Ablauf, Verschachtelung und Datenstruktur sind
entschieden. Direkt umsetzbar.

## Nachtrag 2026-07-06 (nach dem Bauen) — gebaut, getestet, ein Bug gefunden

Alles wie oben entschieden umgesetzt. Beim Live-Test der Verschachtelung
(3 Rohnachrichten → 1 Verdichtung, dann diese + 2 weitere → 1 äußere
Verdichtung) eine echte Race Condition gefunden: ein verworfener
Entwurfsversuch lief im Hintergrund weiter und überschrieb später das
korrekt bestätigte Ergebnis eines neueren Versuchs. Gefixt über einen
`jobToken`, den jeder Hintergrund-Job vor dem Schreiben seines Ergebnisses
gegen den aktuellen Dateiinhalt prüft — verworfene/überholte Jobs erkennen
das und schreiben nichts mehr. Nach dem Fix zweimal sauber durchgetestet
(einfache und verschachtelte Verdichtung), beide korrekt. Volle Details in
`_claude/konzepte/2026-07-06_serve_process_camera_preview.md`.

Ebenfalls dabei aufgefallen: das Zusammenfassen selbst dauert auf dieser
CPU-Hardware mehrere Minuten pro Durchlauf (MoE-Modell, siehe
`docs/systemdoku/12_ollama_gemma4.md`) — für 1-3 kleine Nachrichten fühlt
sich das lang an, ist aber die reale Geschwindigkeit des Systems, kein
Fehler im Feature selbst.
