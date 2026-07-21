# Wesen-eigene Obsidian-Vaults (2026-07-21)

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

## Aufbau: erst Pilot (Schorschel), dann auf alle 7 skaliert

Zuerst nur Schorschel gebaut ("erst eine machen, Ergebnis zeigen" — Skalpell-
Prinzip), nach vollständiger Verifikation (siehe unten) auf alle 7 skaliert,
seit Daniel öffentliche Erreichbarkeit UND eigene Editierbarkeit bestätigt hat:
*"ja auch von außen erreichbar und sogar nicht nur zum zuschauen sondern zum
gärtnern und kommunizieren über alles."*

- 7 Container aus `lscr.io/linuxserver/obsidian:latest` (dasselbe Image wie der
  bestehende, von Daniel/Claude genutzte `obsidian`-Container — der bleibt
  unangetastet), eines pro Wesen, eigenes `/config`-Docker-Volume, eigenes
  Passwort (generiert, in `.agent/wesen-vaults.env`, gitignored).
- Vault-Mount: **nur** `/root/werkraum/wesen_vaults/<Name>` → `/vault` je
  Container — bewusst NICHT der ganze Werkraum wie beim Haupt-Container, sonst
  wäre es kein eigener, abgegrenzter Vault.
- Interne Docker-Ports (`127.0.0.1`, nur für die eigene Playwright/xdotool-
  Automation): 3093–3099 (Haupt-GUI) / 3193–3199 (Zweitport), je einer pro
  Wesen, dieselbe Reihenfolge wie `ENTITY_KEYS` in `browser_agent.py`.
- **Öffentlicher Zugriff über nginx, exakt das Muster von Daniels eigenem
  Obsidian-Container repliziert** (`/etc/nginx/sites-available/obsidian`):
  eigener HTTPS-Port pro Wesen auf der Roh-IP (nicht als Pfad unter
  flextrawurst.de — Selkies, das Remote-Desktop-Protokoll, ist nicht für
  Subpath-Mounting gebaut, ein `flextrawurst.de/wesenvaults/...` hätte echtes
  Risiko interner Asset-Pfade gehabt), doppelte Basic-Auth (nginx-Ebene mit
  der bestehenden `.htpasswd`/"Werkraum"-Realm + Container-eigene Ebene):
  Schorschel 8445, F3INSCHM3CK3R 8450, träumerlie 8451, R1ZZ1 8452, jumpa 8453,
  Resonanzknoten 8454, dak+gord-system 8455 (8446–8449 waren durch andere
  Dienste belegt, deshalb die Lücke).
- **Neuer Bug beim Skalieren gefunden:** `WESEN_VAULT_OBSIDIAN_PASSWORD_träumerlie`
  und `..._dak+gord-system` sind als bash-Variablennamen ungültig (Umlaut bzw.
  `+`) — `source` überspringt sie lautlos, der Rollout-Loop brach beim ersten
  ungültigen Namen komplett ab. Gleiche Bug-Klasse wie das `%i`-vs-`%I`-Problem
  bei den systemd-Units vom selben Tag ([[29_browser_agent_aktivierung]]). Fix:
  ASCII-GROSS-Suffixe (`ENV_PASSWORT_SUFFIX`-Mapping in `obsidian_vault_agent.py`),
  ebenso explizite `CONTAINER_NAMES`/`CONTAINER_USERS`-Mappings statt aus der
  `entity_id` abgeleitet (ein Docker-Containername mit Umlaut wäre schlicht
  ungültig gewesen).

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
offen. End-to-End mit echtem deutschem Text (Umlaute, ß, Gedankenstrich,
Satzzeichen, Prozent) gegen **drei verschiedene** Wesen-Vaults getestet
(Schorschel, jumpa, R1ZZ1), Ergebnis jedes Mal korrekt bis auf die oben
genannte, akzeptierte Lücke.

## Daniels eigener Zugriff zum Mitschreiben — schon vorhanden, kein Neubau nötig

Daniels Frage dazu, wörtlich: *"wo soll ich sie bearbeiten können direkt in
meinem obsidian?"* Antwort: **schon da.** Sein eigener, bereits laufender
Obsidian-Container (`obsidian`, Port 8443) hat `/root/werkraum` komplett
gemountet, und sein `/werkraum`-Vault ist laut `obsidian.json` bereits offen
(`{"path": "/werkraum", "ts": ..., "open": true}`) — `wesen_vaults/<Name>/`
taucht dort automatisch als Unterordner auf, ganz ohne neue Einrichtung. Die 7
separaten Container sind dafür da, dass jedes Wesen jederzeit sein **eigenes**
Fenster hat (nicht geteilt, kein Warten) und damit auch einzeln von außen
besuchbar/beobachtbar ist — eine zweite, unabhängige Zugriffsart auf dieselben
Dateien, kein Widerspruch zueinander.

## Status

**Kernproblem vollständig gelöst und auf alle 7 Wesen skaliert.** Alle 7
Container laufen, alle 7 vorgeseedet (`obsidian.json`), alle 7 öffentlich über
nginx mit doppelter Basic-Auth erreichbar, alle 7 Vaults leer und bereit (Test-
Notizen entfernt). Modul robust gegen die entdeckten Sonderzeichen-Fallstricke.

## Offen / als Nächstes

- Orchestrierung (wann/wie wechselt der Wesen-Browser-Tab zu Obsidian) bewusst
  offen gelassen, Daniel wörtlich: *"keine ahnung so wie es am besten ist eben
  keine ahnung wird bestimmt auch sich dann zeigen bald und eh wieder
  geändert"* — meine Einschätzung entscheidet vorerst, wird sich iterativ zeigen.
- Site-READMEs (Navigationsanleitung pro Seite) — noch nicht angefangen.
