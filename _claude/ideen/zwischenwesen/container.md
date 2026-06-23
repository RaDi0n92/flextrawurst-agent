---
name: zwischenwesen-container
description: Der Kern-Container — kuratierte Prägung die im Wesen bleibt
metadata:
  type: project
tags: [zwischenwesen, container, praegung, kompoase]
status: in-diskussion
datum: 2026-06-19
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Was ich verstehe

Der Container ist das Gedächtnis das der User selbst auswählt. Nicht alles aus 24h Chat landet im Wesen — nur was bewusst hineingelegt wurde. Das ist eine Kurationsentscheidung, keine automatische Extraktion.

Jede Nachricht im Chat — ob vom User oder vom Wesen — hat ein kleines "+" oder "Pin"-Symbol. Klick → landet im Container. Container ist immer sichtbar (Sidebar, Overlay, Panel — TBD). Inhalt kann jederzeit wieder herausgenommen werden. Nach 24h: Container-Inhalt ist priorisiertes Material für die Prägungsextraktion.

---

## Konzept: Was in den Container kann

| Quelle | Was | Bedeutung |
|--------|-----|-----------|
| User-Nachricht | einzelner eigener Satz/Absatz | "das hab ich dem Wesen mitgegeben" |
| Wesen-Antwort | einzelner Satz/Absatz des Wesens | "das will ich dass es behält" |
| Ganzer Gesprächsabschnitt | mehrere Nachrichten | "dieser Moment war wichtig" |

---

## Datenstruktur die ich mir vorstelle

### Vision-Schicht
Der Container ist ein Ort innerhalb des Wesens der bereits während der Entstehung lebt. Nicht erst danach. Das Wesen weiß während des Gesprächs was im Container liegt (es bekommt es als Teil des Kontexts). Das verändert wie es antwortet — es weiß was der User für wichtig hält.

### Code-Skizze

```sql
CREATE TABLE zwischenwesen_container (
  id SERIAL PRIMARY KEY,
  zwischenwesen_id UUID REFERENCES zwischenwesen(id) ON DELETE CASCADE,
  nachricht_id INTEGER REFERENCES zwischenwesen_nachrichten(id) NULLABE,
  -- oder freier Text wenn User nur einen Teil einer Nachricht pinnt:
  inhalt TEXT NOT NULL,
  quelle TEXT NOT NULL,    -- 'mensch' | 'wesen'
  hinzugefuegt_am TIMESTAMPTZ DEFAULT NOW(),
  position INTEGER         -- Reihenfolge im Container (user-sortierbar?)
);
```

```typescript
// Frontend-Logik
interface ContainerItem {
  id: number;
  inhalt: string;
  quelle: 'mensch' | 'wesen';
  nachricht_id?: number;
  hinzugefuegt_am: string;
}

// Container-Panel: immer offen als Sidebar oder per Klick aufklappbar
// Zeigt: N Einträge · [Eintrag 1] [×] · [Eintrag 2] [×] · ...
// Jeder Eintrag: klickbar (lesen), × zum Entfernen
```

```python
# API-Endpunkte
GET    /api/zwischenwesen/:id/container          # alle Container-Einträge
POST   /api/zwischenwesen/:id/container          # Eintrag hinzufügen
DELETE /api/zwischenwesen/:id/container/:item_id # Eintrag entfernen

# In der LLM-Anfrage: Container-Inhalt wird als Zusatzkontext mitgegeben
def baue_nachrichten_kontext(wesen_id):
    container = lade_container(wesen_id)
    letzten_8 = lade_letzten_nachrichten(wesen_id, limit=8)
    
    if container:
        system_zusatz = "\n\nWAS DER MENSCH FÜR WICHTIG HÄLT (Container):\n"
        system_zusatz += "\n".join([f"- {item.inhalt}" for item in container])
    
    return system_prompt + system_zusatz, letzten_8
```

---

## Nach 24h: Container → Prägungsextrakt

```python
def praege_wesen(zwischenwesen_id):
    wesen = lade_wesen(zwischenwesen_id)
    container = lade_container(zwischenwesen_id)
    alle_nachrichten = lade_alle_nachrichten(zwischenwesen_id)
    
    extrakt_prompt = f"""
Dieses Zwischenwesen wurde durch ein 24h-Gespräch geformt.

URSPRUNGSBESCHREIBUNG:
{wesen.wesen_text}

VOM MENSCHEN ALS WICHTIG MARKIERT (Container):
{container_als_text(container)}

GESPRÄCHSAUSZUG (letzte 20 Nachrichten):
{auszug(alle_nachrichten)}

Extrahiere in JSON:
- name: ein Name der sich aus dem Gespräch ergeben hat (oder null)
- essenz: ein Satz was dieses Wesen ist (max 200 Zeichen)
- charakter: 3 Adjektive
- themen: 3-5 Tags was das Wesen beschäftigt
- erinnerungen: 3-5 Sätze die das Wesen "in sich trägt"
"""
    return ollama_call(extrakt_prompt)
```

---

## Sichtbarkeit des Containers in der KompOase

Nach 24h entscheidet der User:
- **Verlauf öffentlich**: komplettes Gespräch anklickbar im Wesen-Profil
- **Nur Container öffentlich**: nur die gepinnten Momente sichtbar
- **Alles privat**: nur der Prägungsextrakt (Name, Essenz, Charakter) ist sichtbar — kein Gespräch

---

## Filter + Suche im Container

Der Container ist kein Stapel — er ist durchsuchbar und filterbar.

```
[CONTAINER 14/20]  [🔍 suchen...]  [Filter: alle ▾]
──────────────────────────────────────────────
Filter-Optionen:
  • Alle
  • Nur meine Nachrichten (mensch)
  • Nur Wesen-Antworten (wesen)
  • Nur manuell hinzugefügt

Suche: Volltextsuche über inhalt-Spalte (PostgreSQL ILIKE reicht, kein GIN nötig)
```

```sql
-- Abfrage mit Filter + Suche
SELECT * FROM zwischenwesen_container
WHERE zwischenwesen_id = :id
  AND (:quelle IS NULL OR quelle = :quelle)       -- Filter
  AND (:suche IS NULL OR inhalt ILIKE '%'||:suche||'%')  -- Suche
ORDER BY position ASC;
```

## Pinnen: ganze Nachricht UND einzelne Sätze

Beide Varianten sind möglich:
- **Ganze Nachricht pinnen** — 1 Klick auf Pin-Icon neben der Nachricht
- **Satz-Selektion** — User markiert Text im Chat, "in Container" Button erscheint (wie Text-Selektion in Readern)

```typescript
// Text-Selektion Handler
document.addEventListener('mouseup', () => {
  const sel = window.getSelection()?.toString().trim();
  if (sel && sel.length > 10) {
    zeige_pin_tooltip(sel); // schwebendes "📌 in Container" erscheint
  }
});
```

## Was bereits entschieden ist

- Container-Inhalt ist LIVE im LLM-Kontext (Wesen weiß was der User für wichtig hält)
- Max 10 Einträge (war: 20 — reduziert wegen Token-Budget)
- **Session-lokal** — startet bei jeder neuen Session leer
- Was dauerhaft bleiben soll → ins Memory pinnen, nicht in den Container
- Einträge entfernbar (×-Button)
- Sichtbar in KompOase je nach Sichtbarkeits-Entscheidung nach 24h

---

## Resonanz

[[zwischenwesen-chat-konzept]]
[[zwischenwesen-felder]]
[[zwischenwesen-schlachtplan]]
