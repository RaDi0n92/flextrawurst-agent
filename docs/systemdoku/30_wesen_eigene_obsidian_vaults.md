# Wesen-eigene Obsidian-Vaults (Pilot, 2026-07-21)

## Auftrag

Daniel, wörtlich, nach dem Fund dass Wesen auf Flarum eher einfrieren als aktiv zu
explorieren: *"theoretisch alles seiten die wir ihnen eröffnen. es müsste zu jedem
erstmal ne art readme mit bester navigationsanleitung und so geben und dann dazu
quasi immer auch ne art schicht geben die diesen 'gesamtbrowsertab' eben minimiert
und dann zum beispiel obsidian öffnet und darin eine ganz neue art von vault erzeugt
vom wesen selbst (mit meiner hilfe usw und auch interaktionsmöglichkeiten) aber ich
will es quasi ohne llm call ich will schreiben in genau der menschenart und weise
quasi im 10 fingersystem ... und dann tippen wie auf der schreibmaschiene"*.

Zwei Architektur-Entscheidungen von Daniel bestätigt:
- **7 eigene, unabhängige Obsidian-Container** statt einem geteilten Fenster (jedes Wesen jederzeit sichtbar, kein Warten aufeinander).
- **Eigener Vault pro Wesen** unter `wesen_vaults/<name>/`, komplett getrennt von der bestehenden `codewesen/<name>/`-Struktur (die ist system-kuratiert, das hier ist selbst-erschaffen).

## Warum GUI-Automation statt der bestehenden `obsidian_api.py`

`obsidian_api.py` (Port 8060) existiert schon und kann sofort Notizen schreiben — aber
als reiner JSON-Bridge-Call, ohne sichtbares Tippen. Daniels Wunsch ("wie auf der
Schreibmaschine", "ohne LLM call" fürs Tippen selbst) verlangt echtes, sichtbares,
zeichenweises Tippen in ein echtes Editor-Fenster — dafür muss ein Wesen tatsächlich
in einer laufenden Obsidian-Desktop-Instanz sitzen, kein Backend-Call reicht.

## Pilot-Aufbau (nur Schorschel, "erst eine machen, Ergebnis zeigen" — Skalpell-Prinzip)

- Neuer Container `obsidian-schorschel` aus `lscr.io/linuxserver/obsidian:latest` (dasselbe Image wie der bestehende, von Daniel/Claude genutzte `obsidian`-Container — der bleibt unangetastet).
- Eigenes `/config`-Docker-Volume (`obsidian_config_schorschel`), eigenes Passwort (generiert, in `.agent/wesen-vaults.env`, gitignored).
- Vault-Mount: **nur** `/root/werkraum/wesen_vaults/Schorschel` → `/vault` im Container — bewusst NICHT der ganze Werkraum wie beim Haupt-Container, sonst wäre es kein eigener, abgegrenzter Vault.
- Ports **nur auf 127.0.0.1** gebunden (3093 Haupt-GUI, 3193 Zweitport) — anders als der öffentlich erreichbare Haupt-Container (0.0.0.0:3080). Bewusste, aber noch nicht mit Daniel abgestimmte Entscheidung: aktuell nur für die eigene Automation gedacht, nicht zum direkten Anschauen von außen. Port-Schema für alle 7 vorbereitet: 3093–3099 (Haupt) / 3193–3199 (Zweit), je einer pro Wesen in derselben Reihenfolge wie `ENTITY_KEYS` in `browser_agent.py`.

## Zugriff: HTTP Basic Auth, WebSocket-Falle gefunden

Der Container schützt sich per HTTP Basic Auth (`CUSTOM_USER`/`PASSWORD`). Playwright mit
`extra_http_headers={"Authorization": "Basic ..."}` reicht NICHT — Chromium trägt
manuell gesetzte Header nicht zuverlässig über die WebSocket-Upgrade-Anfrage weiter
(Selkies, das Remote-Desktop-Protokoll dieses Images, verbindet per WebSocket zum
Streaming-Endpunkt). Fehlerbild: Bild bleibt schwarz, Konsole zeigt endlose
"WebSocket disconnected, reloading page to reconnect." Fix: Playwright-native
`http_credentials={"username":..., "password":...}` beim `new_page()` verwenden — das
funktioniert auf Protokollebene und überlebt auch den WS-Handshake.

## Vault-Öffnen ohne fragile GUI-Automation

Der naheliegende Weg — "Open folder as vault" klicken, GTK-Dateidialog per Ctrl+L
einen Pfad eintippen, "Select Folder" klicken — funktionierte bis zum letzten Klick
zuverlässig, aber der finale Button-Klick registrierte nicht zuverlässig (vermutlich
Fokus-/Timing-Eigenheit der Klick-Weiterleitung durch Selkies). Robusterer Weg
gefunden: Obsidian speichert bekannte Vaults in
`~/.config/obsidian/obsidian.json` (im Container: `/config/.config/obsidian/obsidian.json`,
da `HOME=/config`). Diese Datei direkt vorschreiben:

```json
{"vaults": {"<beliebige-hex-id>": {"path": "/vault", "ts": <ms-timestamp>, "open": true}}}
```

Nach einem Container-Neustart öffnet Obsidian den Vault automatisch, komplett ohne
GUI-Klicks — deterministisch, kein Trial-and-Error nötig. Für alle 7 Container beim
ersten Hochfahren so vorzuseeden.

## Echtes Tippen: drei Schichten von Bugs, alle gelöst (oder bewusst akzeptiert)

**Schicht 1 — `page.keyboard.type()` durch Selkies:** sendet zwar echte
Zeichen-für-Zeichen-Events, aber jede Großschreibung geht verloren (bestätigt am
Dateiinhalt: `"Das ist..."` wurde zu `"as ist..."`). Manuelles Modifier-Handling
(`down("Shift")` → `press("KeyX")` → `up("Shift")`) funktioniert zwar isoliert
korrekt, aber `page.keyboard.press()` kennt keine deutschen Umlaute als Key-Namen
(`Unknown key: "ö"`) — für deutschen Text also ohnehin eine Sackgasse.
`page.keyboard.insert_text()` ist noch schlechter: kommt durch Selkies überhaupt
nicht an (0 Zeichen).

**Schicht 2 — der eigentliche Durchbruch, `xdotool` direkt im Container:**
`docker exec <container> xdotool type --delay N "text"` umgeht Playwright/Selkies
komplett und injiziert die Tasten direkt in die X11-Sitzung. Tippt Groß-
/Kleinschreibung UND deutsche Umlaute korrekt (verifiziert: *"Größe, Übung,
Änderung, Straße — Umlaute mittendrin klappen... Zahlen 100%, Satzzeichen!
Fragen? Doppelpunkte: ja."* — praktisch alles richtig). **Einzige verbleibende,
bewusst akzeptierte Lücke:** ein Großbuchstabe-Umlaut (Ä/Ö/Ü) direkt am Anfang
eines `type`-Laufs kommt klein raus (`Übung` → `übung`), Umlaute *mitten* im
Wort sind davon nicht betroffen (`Größe` bleibt korrekt). Daniel dazu wörtlich:
*"scheiss auf großung kleinschreibung mach ich ja auch nicht... falls es nicht
lösbar ist, hab ich's ihnen vererbt haha"* — explizit als unwichtig abgesegnet,
nicht weiter verfolgt.

**Schicht 3 — Speichern auf Platte, der eigentlich harte Teil:** Text, der in
eine per `Ctrl+N` frisch erzeugte Notiz getippt wird, erscheint zwar korrekt im
Editor (ein `Backspace` löscht ihn wirklich — kein Rendering-Fake), landet aber
**nie** auf der Platte, egal wie lange gewartet oder wie oft `Ctrl+S` gedrückt
wird (auch über Playwright direkt, nicht nur `xdotool`). Root Cause: `Ctrl+N`
bindet den Editor-Puffer in dieser Umgebung nie richtig an eine Datei auf der
Platte. Test mit einer **von außen (host-seitig) vorab angelegten** Datei zeigt:
Obsidians Dateisystem-Watcher erkennt sie sofort (taucht in der Seitenleiste
auf), und Bearbeitungen daran speichern sofort korrekt. **Fix: Dateien nie über
`Ctrl+N` in der App selbst anlegen — immer vorher direkt als echte Datei auf der
Platte erzeugen, dann öffnen.**

**Nebenfund beim Robustheitstest:** ein `browser.close()` unmittelbar VOR dem
`xdotool`-Tipplauf reißt den Text nach ungefähr der Hälfte lautlos ab (`xdotool`
selbst meldet trotzdem Erfolg — der Abbruch passiert auf der Empfängerseite).
Fix: Playwright-Verbindung während des gesamten Tipplaufs offen halten, erst
danach schließen.

## Fertiges Modul: `welt/obsidian_vault_agent.py`

```python
import obsidian_vault_agent as ova
ova.oeffne_datei_und_schreibe(
    "Schorschel", "erste-notiz", "Der eigentliche Text ...",
    titel="Erste Notiz — Wesen-eigener Vault",
)
```

Kompletter, verifizierter Ablauf: Datei direkt auf der Platte anlegen (falls
nicht vorhanden) → über den Quick Switcher (`Ctrl+O`, positionsunabhängig,
robuster als Sidebar-Klicks) im Wesen-eigenen Obsidian-Fenster öffnen → ans Ende
springen → `xdotool` tippt den Text, Playwright-Verbindung bleibt währenddessen
offen. End-to-End mehrfach mit echtem deutschem Text (Umlaute, ß, Gedankenstrich,
Satzzeichen, Prozent) gegen den echten Pilot-Vault getestet, Ergebnis jedes Mal
korrekt bis auf die oben genannte, akzeptierte Lücke.

## Status

Kernproblem (sichtbares, zeichenweises Tippen ohne LLM-Call, das wirklich auf
der Platte landet) ist **gelöst und verifiziert**. Pilot-Vault wieder leer
(Test-Notizen entfernt). Noch **nicht** gebaut:

## Offen / als Nächstes

- Entscheidung mit Daniel bereits gefallen: Container sollen öffentlich
  erreichbar sein (0.0.0.0), nicht nur für die Automation, sondern damit Daniel
  selbst mitschreiben/"gärtnern" kann — Umstellung von 127.0.0.1 auf 0.0.0.0
  noch nicht durchgeführt.
- Orchestrierung (wann/wie wechselt der Wesen-Browser-Tab zu Obsidian) bewusst
  offen gelassen, Daniel wörtlich: *"keine ahnung so wie es am besten ist eben
  keine ahnung wird bestimmt auch sich dann zeigen bald und eh wieder
  geändert"* — meine Einschätzung entscheidet vorerst, wird sich iterativ zeigen.
- Die restlichen 6 Obsidian-Container nach demselben Muster aufsetzen
  (Port-Schema bereits in `obsidian_vault_agent.VAULT_PORTS` vorbereitet).
- Site-READMEs (Navigationsanleitung pro Seite) — noch nicht angefangen.
