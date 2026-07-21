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

## Echtes Tippen: Bug gefunden und diagnostiziert

`page.keyboard.type(text, delay=N)` sendet zwar echte Zeichen-für-Zeichen-Events (kein
LLM-Call pro Taste nötig, genau wie gewünscht) — aber durch Selkies durchgereicht geht
dabei jede Großschreibung verloren, und gelegentlich fällt das erste Zeichen nach
einem Fokuswechsel (Klick/Enter) komplett weg. Bestätigt am echten Dateiinhalt auf
Platte: `"Das ist..."` wurde zu `"as ist..."`, komplett kleingeschrieben.

**Root Cause gefunden:** manuelles Modifier-Handling (`page.keyboard.down("Shift")`
→ `press("KeyX")` → `up("Shift")`) erzeugt zuverlässig ein korrektes Großbuchstabe
("X") gefolgt von einem korrekten Kleinbuchstaben ("y") — `type()`s eingebautes
Shift-Handling überlebt die Selkies-Weiterleitung nicht, manuelles Down/Up schon.
**Fix ist bekannt, aber noch nicht gebaut:** ein `human_type(page, text)`-Helper, der
pro Zeichen entscheidet ob Shift nötig ist (Großbuchstabe, Sonderzeichen) und dann
explizit down/press/up statt `type()` nutzt, plus eine kurze Vorlaufzeit nach jedem
Fokuswechsel gegen das verschluckte erste Zeichen.

## Status

Pilot-Container läuft (`obsidian-schorschel`), Vault ist leer und bereit (Test-Notizen
wieder gelöscht — die Leinwand soll für die erste echte Notiz frei sein, nicht mit
Debug-Text vorbelegt). Noch **nicht** gebaut: der `human_type()`-Helper selbst, die
Integration in `browser_agent.py` (neue Aktion? eigenes Skript? wie wird "Tab
minimieren, Obsidian öffnen" konkret orchestriert?), die 6 weiteren Container, die
Site-READMEs mit Navigationsanleitung, Daniels gewünschte Mitschreib-Möglichkeit.

## Offen / als Nächstes

- `human_type()`-Helper bauen und gegen den Pilot-Vault verifizieren (auch Umlaute,
  Satzzeichen mit Shift wie `!`/`?`/`:` auf der im Container aktiven Tastaturbelegung
  prüfen — noch nicht getestet, nur reine Buchstaben).
- Entscheidung mit Daniel: Ports weiterhin nur localhost, oder wie der Haupt-Container
  öffentlich erreichbar (damit Daniel selbst live zuschauen kann)?
- Orchestrierung klären: wie/wann "minimiert" der Wesen-Browser-Tab und wechselt zu
  Obsidian — eigene neue Aktion im bestehenden `browser_agent.py`-Vokabular, oder ein
  komplett separater Prozess/Zustand?
- Site-READMEs (Navigationsanleitung pro Seite) sind noch gar nicht angefangen.
