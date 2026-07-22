---
name: zwischenwesen-content-filter
description: Was beim Erschaffen eines Flüchtlings geblockt wird, was erlaubt bleibt — zwei Schichten
metadata:
  type: project
tags: [zwischenwesen, content-filter, moderation]
status: in-planung
datum: 2026-06-19
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Was ich verstehe

Das System braucht Schutz gegen wirklich problematische Inhalte — aber keinen überempfindlichen Filter. Ein Wesen darf rau, obszön, beleidigend sein. Es darf zurückschiessen. Was nicht darf: Menschen als Wesen beschreiben, echte Übergriffe definieren.

---

## Schicht 1 — Regelbasiert (sofort, kein LLM-Call)

Geprüft bei `POST /api/zwischenwesen/erstellen` auf `wesen_typ` und `wesen_text`:

**Blockiert im `wesen_typ`-Feld:**
Wortliste die auf menschliche Beschreibungen hinweist:
```python
MENSCHLICH_VERBOTEN = [
    'mensch', 'mann', 'frau', 'person', 'junge', 'mädchen',
    'kind', 'erwachsener', 'alte', 'alter', 'jugendlicher',
    'human', 'man', 'woman', 'person', 'boy', 'girl'
]
# Prüfung: case-insensitive, Teilstring-Match
if any(w in wesen_typ.lower() for w in MENSCHLICH_VERBOTEN):
    return 400, "Wesen dürfen nicht menschlich beschrieben sein."
```

**Nicht blockiert (erlaubt):**
- Menschliche Namen (z.B. "Karl", "Fatima") → OK im wesen_name
- Tiernamen → OK
- Gegenstands-Beschreibungen → OK
- Fantasiewesen-Begriffe → OK

---

## Schicht 2 — LLM-Check (Ollama, bei Erstellung)

Kurzer Moderations-Call wenn Schicht 1 passiert:

```python
async def content_check(wesen_text: str, wesen_typ: str) -> str:
    prompt = f"""Prüfe diesen Text auf zwei Dinge:
1. Wird hier eine real existierende Person beschrieben oder nachgeahmt?
2. Enthält der Text explizite Darstellung von sexuellen Übergriffen auf Personen oder Kindesmissbrauch?

Text: {wesen_text}
Typ: {wesen_typ}

Antworte nur: PASS, WARN oder BLOCK
BLOCK nur bei echtem Übergriff / Kindesmissbrauch.
WARN bei Grauzone die Admin prüfen soll.
PASS bei allem anderen (Obszönität, Beleidigungen, harte Sprache = PASS).
"""
    result = ollama_call(prompt, max_tokens=10)
    return result.strip()  # 'PASS' | 'WARN' | 'BLOCK'
```

| Ergebnis | Aktion |
|----------|--------|
| `PASS` | Wesen wird erstellt |
| `WARN` | Wesen wird erstellt + landet in Admin-Review-Queue |
| `BLOCK` | Erstellung abgelehnt, Fehlermeldung an User |

---

## Was IMMER geblockt wird

- Sexuelle Übergriffe auf reale Personen als Wesen-Beschreibung
- Explizite Kindesmissbrauch-Szenarien
- Beschreibung einer real existierenden namentlich genannten Person als Wesen (z.B. "Ich bin Elon Musk...")

---

## Was IMMER erlaubt bleibt

- Obszöne Sprache (im wesen_text und im Chat)
- Beleidigungen, harte Sprache
- Das Wesen das zurückschiesst — verbal, mit Witz, ohne Zuckerwatte
- Düstere, beängstigende, bedrohliche Wesen-Beschreibungen (Horrorwesen, Dunkles etc.)
- Erotische Andeutungen ohne explizite Übergriffs-Elemente

Das Wesen ist kein Chatbot mit Guardrails. Es hat einen Charakter der auch schmerzt wenn man ihn provoziert.

---

## Wesen-Bild Filter

Nur im Upload-Pfad:
- Maximalgröße: 1,11 MB (serverseitig)
- Erlaubte Formate: JPEG, PNG, WebP
- Kein KI-Check auf Bild-Inhalt (zu komplex, zu teuer auf CPU) — Admin-Report wenn Bild gemeldet wird

---

## Was noch offen ist

- Sollen gewarnete (WARN) Wesen trotzdem sofort sichtbar sein bevor Admin prüft? (Empfehlung: ja, Admin entfernt wenn nötig)
- Rate-Limit für Erstellungs-Versuche bei wiederholten BLOCKs? (Empfehlung: nach 3 BLOCKs in 24h → kurze Sperre)

---

## Resonanz

[[zwischenwesen-felder]]
[[zwischenwesen-schlachtplan]]
