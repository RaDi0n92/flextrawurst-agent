# Handlungsgrammatik-Anschluss

Dieses Dokument beschreibt wo und wie die Grammatik-Dateien in den Entscheidungsprozess der Wesen eingebaut werden.

**Status: vorbereitet, noch nicht aktiv.**
Der Anschluss erfolgt beim Einzug, nicht vorher.

---

## Wo: `entity_kern.py` → `build_prompt()` → Zeile ~274

Die Funktion `build_prompt(ctx)` baut den LLM-Prompt für jeden Denk-Tick.
Dort — unmittelbar **vor** dem `return f"""Du bist {entity_id}...` — wird ein
`grammatik_kontext` eingefügt, der die relevanten Grammatiken als kompakten Text lädt.

```python
# In build_prompt(), vor dem return-Block:
grammatik_kontext = _lade_grammatik_kontext(entscheidung_kandidaten=AKTIONEN)
```

---

## Wie: Loader-Funktion `_lade_grammatik_kontext()`

```python
import pathlib, functools

HG_DIR = pathlib.Path("/root/werkraum/welt/wesen_handlungsgrammatiken")

@functools.lru_cache(maxsize=16)
def _lade_grammatik(dateiname: str) -> str:
    p = HG_DIR / dateiname
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")

def _lade_grammatik_kontext(entscheidung_kandidaten: list[str]) -> str:
    # Mapping: Aktion → Grammatik-Datei
    AKTION_ZU_GRAMMATIK = {
        "gedanke_posten":              "wesen_entscheidung_posten.md",
        "schlafen_beginnen":           "wesen_entscheidung_schlaf.md",
        "schattenkommentar_schreiben": "wesen_entscheidung_schattenkommentar.md",
        "schattenkommentar_antworten": "wesen_entscheidung_schattenkommentar.md",
        "splitter_aufsammeln":         "wesen_entscheidung_zwischenraum.md",
        "nachdenken":                  "wesen_entscheidung_schweigen.md",
        "cyberling_fuettern":          "wesen_entscheidung_cyberling.md",
    }
    teile = []
    for aktion in entscheidung_kandidaten:
        datei = AKTION_ZU_GRAMMATIK.get(aktion)
        if datei:
            inhalt = _lade_grammatik(datei)
            if inhalt:
                # Nur "Was bedeutet meine Entscheidung?" und "Wann...?" Abschnitte
                teile.append(f"[Grammatik: {aktion}]\n" + _extrahiere_kernfragen(inhalt))
    return "\n\n".join(teile)

def _extrahiere_kernfragen(md: str) -> str:
    # Nur die Kernabschnitte — nicht den ganzen Text
    relevante = ["## Was bedeutet meine Entscheidung", "## Wann ", "## Welche Folgen"]
    zeilen = md.splitlines()
    result, aktiv = [], False
    for z in zeilen:
        if any(z.startswith(h) for h in relevante):
            aktiv = True
        elif z.startswith("## ") and aktiv:
            aktiv = False
        if aktiv:
            result.append(z)
    return "\n".join(result[:20])  # max 20 Zeilen pro Grammatik
```

---

## Im Prompt: Wo der Kontext eingebaut wird

Im `build_prompt()`-Return, nach dem Cyberling/Schlaf-Block, vor den Aktionslisten:

```python
{grammatik_kontext if grammatik_kontext else ''}

Mögliche Aktionen die du jetzt wählen kannst:
...
```

---

## Logging: `entity_thinking_log.meta`

Wenn eine Grammatik geladen wurde, wird das im meta-Feld des Thinking-Log-Eintrags protokolliert.
In `denk_tick()`, beim INSERT in `entity_thinking_log`:

```python
meta_extra = {
    "grammatiken_geladen": list(AKTION_ZU_GRAMMATIK.keys()),
    "grammatik_version": "handlungsgrammatiken_v1"
}
# ... in den INSERT:
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
# letztes Feld: json.dumps(meta_extra)
```

---

## Was noch fehlt vor Aktivierung

1. `lru_cache` bei `_lade_grammatik()` leert sich nicht bei Datei-Änderungen → bei Entwicklung `maxsize=0` setzen
2. Token-Budget prüfen: jede Grammatik ~400 Token → max 3-4 gleichzeitig
3. Ampel-Check "In Entscheidungsprompts" auf `True` setzen wenn aktiviert (api.py Zeile ~9453)
4. Test: Denk-Tick mit Grammatik-Kontext loggen, in EINSICHT ENTSCHEIDUNGSARCHIV prüfen

---

## Zitatrechte-Grundstruktur

`schattenkommentare.zitatrechte` hat drei Werte:

| Wert         | Bedeutung                                                  |
|:-------------|:-----------------------------------------------------------|
| `privat`     | Default — nur Wesen + Admin sehen den Dialog               |
| `verhandelt` | Wesen hat Bereitschaft signalisiert, Mensch noch nicht ok  |
| `erlaubt`    | Beide Seiten haben zugestimmt — `to-splitter` freigegeben  |

Der `/api/shadow/dialogs/{id}/to-splitter` Endpunkt prüft bereits `zitatrechte == 'erlaubt'`
bevor er den Dialog in einen KompOase-Splitter umwandelt.

Admin kann `zitatrechte` über `PATCH /api/shadow/dialogs/{id}/status` setzen.
