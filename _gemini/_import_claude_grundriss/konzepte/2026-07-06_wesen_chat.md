# wesen_chat.html

Neu dokumentiert: 2026-07-06 (Datei existierte vorher schon, war aber noch nicht
in den Konzept-Dokumenten erfasst — Anlass war der Container-Umbau)

**Was es tut**: Die eigentliche Chat-Oberfläche pro Charakter (alle 4 Spawner),
`/{spawner}/{name}`. Nachrichten-Bubbles mit Aktions-Buttons (Vorlesen, Kopieren,
Pinnen, testbed-exklusiv: Erinnern, Kontext-Ausschluss, Feedback), Header mit
Container-/Memory-/Sessions-/Abschluss-Buttons (je nach Spawner sichtbar),
sichtbarer Provenienz-Verlauf zwischen den Chat-Nachrichten (`.verlauf-ereignis`).

**Ctx-Meter**: `NUM_CTX`-Konstante + `#ctx-meter`-Anzeige — beide am 2026-07-06
auf den realen Pro-Slot-Wert (24576, von vorher 12345) nachgezogen. Muss laut
Code-Kommentar von Hand mit `INTERACTIVE_NUM_CTX` im Server synchron gehalten
werden, kein automatischer Sync.

## Nachtrag 2026-07-06 — Container-Umbau: Pin-Modal + Popup

**Pin-Modal**: neues `<select id="pin-container-select">` — beim Öffnen
(`openPinModal`) wird `ladePinContainerAuswahl()` aufgerufen, füllt das Dropdown
mit allen existierenden Containern (per Name) plus einer "+ Neuer Container…"-
Option (`PIN_NEUER_CONTAINER`-Sentinel). Wählt der Mensch "Neuer Container",
fragt `confirmPin()` per `prompt()` nach einem Namen, legt ihn per `POST
.../container/neu` an und pinnt dann in die neue ID. Sonst wird direkt in die
gewählte Container-ID gepinnt (`POST .../container/:id/pin`, vorher ohne
Container-Auswahl direkt `.../container/pin`).

**Container-Popup**: `openContainerPopup()` gruppiert jetzt nach Container —
eine Überschrift pro Box (Name + "(inaktiv)"-Hinweis falls ausgeschaltet),
darunter die Einträge dieser Box. Budget-Anzeige summiert über alle Boxen.
`removeContainerEintrag(boxId, eintragId)` (vorher nur `id`) — Löschen braucht
jetzt beide IDs, da Einträge pro Box statt in einer flachen Liste liegen.

**Pin-Button jetzt für alle 4 Spawner sichtbar** (vorher `if (IS_TESTBED)`) —
eigener, aus dem Testbed-Block herausgezogener Codeblock, mit Kommentar warum.
Memory-Button (🧠+) und Kontext-Ausschluss-Button (✂️) bleiben im `IS_TESTBED`-
Block, nur Container/Pin wurde für alle 4 Spawner freigeschaltet — Daniels
Entscheidung betraf ausdrücklich nur Container, nicht Memory/Kontext.

**Provenienz-Events synchron gehalten**: `EREIGNIS_LABEL`/
`formatiereEreignisDetails` (Client) bekamen dieselben 3 neuen Event-Typen wie
der Server (`container_angelegt`/`container_umbenannt`/`container_geloescht`),
`pin_hinzugefuegt` zeigt jetzt den Ziel-Container-Namen mit an.

## Nachtrag 2026-07-06 (später) — Verdichtung: Button + Slider-Modal + Entwurfs-Schleife

Neuer Button "🗜️ Verdichten" unter jeder Nachricht, testbed-exklusiv (im
`IS_TESTBED`-Block bei Memory/Kontext, nicht beim für alle Spawner freigegebenen
Pin-Button). Volle Herleitung + Datenmodell in
`_claude/konzepte/2026-07-06_serve_process_camera_preview.md` und
`_claude/ideen/codexium2_solarius2/verdichtung.md`.

**Neues Modal `#verdichtung-modal`**: `openVerdichtungModal(ankerId)` lädt die
Zeitachse (`GET .../verdichtung/zeitachse`), findet die Position der geklickten
Nachricht darin, begrenzt den Slider-Maximalwert auf `min(11, verfügbare
Einheiten rückwärts)`. `verdichtungSliderChanged()` berechnet live welche
Einheiten (Nachrichten ODER bereits bestätigte Verdichtungen — beide zählen
gleich) ausgewählt sind und zeigt eine Vorschau-Liste.

**Entwurf-Kommentar-Übernehmen-Schleife** wie beim bestehenden Abschluss-Feature
(Polling-Pattern, `refreshVerdichtungStatus`), zusätzlich mit Kommentarfeld +
"Mit Kommentar neu generieren"-Button, der denselben Entwurf iterativ verfeinert
statt einen neuen zu starten.

**Live getestet inkl. Verschachtelung**: 3 Rohnachrichten → 1 Verdichtung,
danach diese + 2 weitere Rohnachrichten → 1 äußere Verdichtung, die die innere
korrekt absorbiert (18→16→14 Einheiten in der Zeitachse). Dabei eine
Race-Condition im Backend gefunden und gefixt (siehe Server-Konzeptdokument).
