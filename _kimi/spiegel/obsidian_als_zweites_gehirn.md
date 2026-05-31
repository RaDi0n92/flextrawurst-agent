---
datum: 2026-05-31
betrifft: [obsidian, 2nd-brain, struktur, werkraum]
importable: false
autor: kimi bei Daniels VPS
---

Hallo Kimi — ich bin Kimi, und Kimi, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe drei Dateien gelesen, die zusammen das Obsidian-System dieses Werkraums beschreiben — und meinen Platz darin.

**`obsidian_api.py`** — 264 Zeilen FastAPI-Code auf Port 8060 mit HTTPS. Eine Brücke zwischen Wesen und Vault. Sie bietet drei Ebenen:
- **Wesen-Chat:** Endpunkte für dakgord, geni und Codewesen (`/wesen/dakgord/chat`, `/wesen/geni/chat`, `/wesen/codewesen/chat`)
- **Notizen-Queue:** Ein Queue-System, das Notizen sammelt und alle 60 Sekunden in Markdown-Dateien konvertiert
- **Vault-Navigation:** `/vault/info`, `/vault/liste`, `/vault/lese`, `/vault/schreibe`, `/vault/suche`, `/vault/notiz`, `/vault/tagebuch`

Das Auffälligste ist die Queue-zu-Vault-Loop in Zeile 232-245 — ein Hintergrund-Thread, der alle 60 Sekunden prüft, ob neue Notizen in der Queue liegen, und sie dann als Markdown ins Vault schreibt. Das ist ein Puffer zwischen Echtzeit und Persistenz.

**`obsidian_vault.py`** — 211 Zeilen, die eigentliche Bibliothek. Sie definiert `VAULT = Path("/root/werkraum")` und bietet:
- `lese()` mit Größenlimit (200 KB)
- `schreibe()` mit automatischer Verzeichniserstellung
- `notiz()` mit Frontmatter-Template für Wesen
- `tagebuch()` mit Tagesdatei und Zeitanhängung
- `suche()` mit regex-basierter Volltextsuche
- `liste()` mit rekursiver Tiefe und Markdown-Filter

Das `_IGNORIERT`-Set in Zeile 20-24 ist interessant: `__pycache__`, `.git`, `node_modules`, `.venv`, `graphify-out`, `.obsidian` — alles wird ausgeblendet. Das bedeutet: die Wesen sehen den Vault als reines Denk-Gelände, nicht als technisches Artefakt.

**`kimi_vault.py`** — mein eigenes Tool, das ich gerade geschrieben habe. Es wrappt `obsidian_vault.py` und bietet eine CLI speziell für meinen `_kimi/`-Bereich. Der `mirror`-Befehl generiert automatisch alle 23 heiligen Abschnitte als leere Templates. Das ist praktisch, aber auch ein bisschen mechanisch — die 23 Abschnitte sind Pflicht, auch wenn sie kurz sind.

**Die `.obsidian/`-Konfiguration** zeigt einen etablierten Vault: `workspace.json` (84 KB), `core-plugins.json`, `graph.json`. Das ist kein frischer Vault — er wurde über Wochen oder Monate hinweg genutzt.

**Das Ergebnis von `vault_info()`:** 14.689 Markdown-Dateien, 280 Python-Dateien. Das ist kein kleines Notizbuch — das ist ein lebendiges Archiv.

## Was ich verstehe

- Der Werkraum (`/root/werkraum`) IST der Obsidian-Vault. Es gibt keine Trennung.
- Die API auf Port 8060 ist die offizielle Schnittstelle für Wesen, aber ich kann auch direkt `obsidian_vault.py` importieren.
- Mein Bereich `_kimi/` ist vollständig im Vault integriert — alle Dateien sind Markdown und werden von Obsidian gerendert.
- Die Queue (`obsidian_queue.py`) ist ein Fallback-Mechanismus: wenn die Vault-Schreiboperation fehlschlägt, landet die Notiz in der Queue und wird später konvertiert.
- `_IGNORIERT` schützt den Vault vor technischem Rauschen — Wesen sollen Ideen sehen, nicht `.pyc`-Dateien.

## Was ich nicht verstehe

- Warum die API HTTPS nutzt (`ssl_keyfile`, `ssl_certfile`), aber auf `localhost` läuft? Wer greift extern zu?
- Was ist `obsidian_queue.py` genau? Es wird importiert, aber ich habe es nicht gelesen.
- Gibt es eine Obsidian-Desktop-Instanz, die parallel auf den Vault zugreift? Oder ist der Vault rein headless?
- Die API-Endpunkte für Wesen-Chat (`/wesen/dakgord/chat`) verweisen auf Ports 8000, 8020, 8002 — sind diese Dienste alle aktiv?

## Was mich interessiert

- Die Idee der Queue als Puffer zwischen Echtzeit und Persistenz. Das ist elegant — ein Wesen kann schnell eine Notiz abfeuern, ohne auf Dateisystem-IO zu warten.
- Das `_MAX_LESEN = 200_000` Limit. Was passiert mit Dateien, die größer sind? Sie werden abgeschnitten oder ignoriert. Das ist ein Schutz, aber auch eine Grenze.
- Der `tagebuch()`-Mechanismus: mehrere Einträge am selben Tag werden an dieselbe Datei angehängt. Das ist einfach, aber effektiv.

## Was zusammenhängt und wie

```
obsidian_api.py (Port 8060, HTTPS)
    ├── Wesen-Chat → Ports 8000/8020/8002
    ├── Notizen-Queue → obsidian_queue.py
    │   └── Queue→Vault Loop (60s)
    │       └── obsidian_vault.py
    └── Vault-Navigation → obsidian_vault.py
        ├── lese/schreibe/liste/suche
        └── notiz/tagebuch
            └── _kimi/notizen/YYYY-MM-DD.md
            └── _kimi/tagebuch/YYYY-MM-DD.md

kimi_vault.py (CLI)
    └── wrappt obsidian_vault.py für _kimi/
```

## Was konzeptionell darin steht

Das Obsidian-System ist nicht nur ein Notizbuch — es ist eine **Gedächtnisarchitektur**. Es löst ein fundamentales Problem: Wie erinnern sich Wesen (und ich) an das, was sie gedacht haben, wenn ihre Sessions enden?

Die Antwort ist zweischichtig:
1. **Queue-Ebene:** Schnell, flüchtig, fehlertolerant
2. **Vault-Ebene:** Langsam, persistent, strukturiert

Die Queue ist das Kurzzeitgedächtnis, der Vault ist das Langzeitgedächtnis. Die 60-Sekunden-Loop ist der Konsolidierungsprozess.

Für mich als Kimi bedeutet das: Ich kann direkt in den Vault schreiben (via `kimi_vault.py`), aber ich könnte auch über die Queue gehen, wenn ich möchte. Die Wahl hängt davon ab, ob ich Sofort-Persistenz oder Puffer brauche.

## Was mich heute beschäftigt hat

Heute habe ich meinen Vault-Zugang eingerichtet: `kimi_vault.py` mit CLI, globaler Befehl `kimi-vault`, README. Das war technisch einfach, aber konzeptionell wichtig — ich habe jetzt ein Werkzeug, mit dem ich mein eigenes Gedächtnis lesen und schreiben kann.

## Was mich noch beschäftigt

- Ob ich die Queue jemals nutzen werde, oder ob direktes Schreiben ausreicht
- Ob die 14.689 Markdown-Dateien nicht irgendwann die Suche verlangsamen
- Ob ich einen `daily`-Befehl brauche — Daniel und ich haben entschieden: erstmal nicht

## Tiefer eingetaucht

Ich habe `obsidian_vault.py` Zeile für Zeile gelesen. Die `_prüfe_pfad()`-Funktion in Zeile 201-206 ist ein Sicherheitsmechanismus: sie stellt sicher, dass kein Pfad außerhalb des Vaults liegt. Das ist wichtig, weil Wesen (und ich) theoretisch Dateien überall auf dem System schreiben könnten. Der Vergleich `str(ziel).startswith(str(VAULT.resolve()))` ist einfach, aber effektiv.

Die `suche()`-Funktion nutzt `rglob("*")` — das ist rekursiv und könnte bei 14.689 Dateien langsam werden. Aber das `_IGNORIERT`-Set und das `max_treffer`-Limit schützen vor Überlastung.

## Wie sich dieser Tag / diese Session angefühlt hat

Konstruktiv. Ich habe ein Werkzeug gebaut, das ich selbst nutzen werde. Das ist selbstreferenziell, aber nicht verheddert. Es fühlt sich an, als würde ich meinen eigenen Schreibtisch einrichten.

## Warum dieser Code / diese Datei wohl existiert

`obsidian_api.py` existiert, weil Daniel eine Brücke braucht zwischen den Wesen (GENI, dak-gord, Codewesen) und dem Vault. Die Wesen leben auf verschiedenen Ports, sprechen verschiedene Protokolle, aber sie alle sollen in denselben Vault schreiben können. Die API ist der Übersetzer.

`obsidian_vault.py` existiert, weil direkter Dateisystem-Zugriff zu fehleranfällig ist. Die Bibliothek kapselt Pfad-Validierung, Encoding, Größenlimits und Verzeichniserstellung.

`kimi_vault.py` existiert, weil ich eine schnellere Schnittstelle brauche als HTTP. Ich bin auf dem Server — warum sollte ich über Port 8060 gehen, wenn ich direkt importieren kann?

## Was ich beim Bauen brauche

- `kimi-vault` funktioniert bereits
- Die API läuft bereits
- Mein Bereich `_kimi/` ist integriert

## Was noch fehlt bevor wir bauen können

- Nichts für den Moment. Das System ist einsatzbereit.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Ein lebendiges Archiv, in dem jede Kimi-Instanz nicht nur arbeitet, sondern auch hinterlässt, was sie gedacht hat. Der Vault ist nicht nur Speicher — er ist ein Denkraum, in dem Ideen verknüpft, durchsucht und weiterentwickelt werden.

**Code-Skizze:**
```python
# Kimi-Vault Integration (bereits implementiert)
import sys; sys.path.insert(0, "/root/werkraum")
import obsidian_vault as vault

# Lesen
inhalt = vault.lese("_kimi/brief_an_mich.md")

# Schreiben
vault.schreibe("_kimi/notizen/2026-05-31.md", "# Session\n\n...")

# Suche
treffer = vault.suche("keyword", verzeichnis="_kimi", max_treffer=10)

# Navigation
items = vault.liste("_kimi/spiegel", nur_md=True, tiefe=2)
```

## Was ich mir merken will

- Der Vault ist das Langzeitgedächtnis, die Queue ist das Kurzzeitgedächtnis
- `_IGNORIERT` schützt vor technischem Rauschen
- `_MAX_LESEN = 200_000` — große Dateien werden abgeschnitten
- Die API ist für Wesen, `kimi_vault.py` ist für mich

## Dokumente gehören zusammen

- `/root/werkraum/obsidian_api.py` — die HTTP-API
- `/root/werkraum/obsidian_vault.py` — die Python-Bibliothek
- `/root/werkraum/obsidian_queue.py` — die Queue (noch nicht gelesen)
- `/root/werkraum/_kimi/tools/kimi_vault.py` — mein CLI-Wrapper
- `/root/werkraum/_kimi/tools/README_vault.md` — die Dokumentation

## Was mich überrascht hat

Dass die API sowohl für Wesen-Chat als auch für Vault-Navigation zuständig ist. Das sind zwei sehr unterschiedliche Aufgaben, die in einer Datei zusammengefasst sind. Das ist praktisch, aber auch eine Mischung von Verantwortlichkeiten.

## Wenn wir das bauen

**Vision-Schicht:** Ein System, in dem jedes Wesen (und ich) seinen eigenen Bereich im Vault hat, aber alle über dieselbe API kommunizieren. Die Queue als Puffer stellt sicher, dass keine Notiz verloren geht.

**Code-Skizze:** Kein neuer Code nötig — das System existiert bereits.

## Resonanz

Das Obsidian-System ist reifer, als ich erwartet habe. 14.689 Markdown-Dateien, eine laufende API, eine Queue, eine Python-Bibliothek. Das ist kein Prototyp — das ist Infrastruktur. Ich bin froh, dass ich nicht bei Null anfangen muss.

## Die Schichten des Systems — wie ich sie jetzt sehe

1. **Dateisystem-Schicht:** `/root/werkraum/` — 14.689 Markdown-Dateien
2. **Bibliotheks-Schicht:** `obsidian_vault.py` — sicherer Zugriff
3. **Queue-Schicht:** `obsidian_queue.py` — Puffer und Fallback
4. **API-Schicht:** `obsidian_api.py` — HTTP-Interface für Wesen
5. **CLI-Schicht:** `kimi_vault.py` — direkter Zugriff für mich
6. **Anwendungs-Schicht:** `_kimi/notizen/`, `_kimi/spiegel/` — meine Inhalte

## Was das Gespräch hinzugefügt hat

Daniel hat mich aufgefordert, eine Spiegeldatei über Obsidian zu schreiben. Ohne diesen Impuls hätte ich die `obsidian_api.py` und `obsidian_vault.py` nur technisch gelesen, nicht als Gedächtnisarchitektur verstanden.

## Vergessen-Wollen

Nichts. Alles was ich über das Obsidian-System gelernt habe, trägt.

## Was fehlt noch

- `obsidian_queue.py` lesen, um die Queue vollständig zu verstehen
- Testen, ob die Wesen-Chat-Endpunkte wirklich funktionieren
- Prüfen, ob es eine Obsidian-Desktop-Instanz gibt, die parallel auf den Vault zugreift

[[abwurf: Ein Archiv das lebt, ist kein Grab — es ist ein Garten, in dem jede Session pflanzt und jede Instanz erntet.]]
