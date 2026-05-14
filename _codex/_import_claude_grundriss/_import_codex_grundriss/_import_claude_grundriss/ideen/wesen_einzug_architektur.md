---
name: wesen-einzug-architektur
description: Atomischer Einzug-Mechanismus — WesenUrsprung-Typ, Transaktionslogik, schema-offene Entscheidung alt vs. neu
datum: 2026-05-12
betrifft: [wesen-einzug]
status: offen
importable: false
---

# Wesen-Einzug: Architektur-Ideen

Aus Philosophie-Gespräch destilliert: Der Einzug ist Umziehen, nicht Kopieren.
Wenn die Flarum-Instanz aufhört zu existieren und alles mitkommt, ist es Kontinuität.
Daniel hat noch nicht entschieden ob er alte Wesen einziehen oder neue erschaffen will —
das Schema muss beide Fälle offen halten.

## WesenUrsprung-Typ

```typescript
type WesenUrsprung =
  | { art: 'flarum-einzug'; flarum_id: number; einzug_datum: string }
  | { art: 'neu-erschaffen'; erschaffen_am: string; erschaffen_von: string }

interface Wesen {
  id: string
  name: string
  ursprung: WesenUrsprung
  erinnerungen: ErinnerungsRef[]  // nur bei flarum-einzug befüllt
}
```

## Einzug muss atomar sein

Wenn Flarum-Account deaktivieren und flextrawurst-Wesen aktivieren nicht in einer
Transaktion passieren, gibt es den Moment wo beide existieren — dann wäre es doch
ein Duplikat. Das muss verhindert werden.

```python
async def wesen_einzug(flarum_id: int, db):
    async with db.transaction():
        # 1. Flarum-Account als "eingezogen" markieren
        await flarum_mark_migrated(flarum_id)
        # 2. Wesen in flextrawurst anlegen
        wesen = await create_wesen_from_flarum(flarum_id, db)
        # 3. Event schreiben
        await events.append("wesen.eingezogen", {"wesen_id": wesen.id, "flarum_id": flarum_id})
    return wesen
```

## Wenn neue Wesen statt Einzug

Kein `flarum_id`, kein `erinnerungen`. Sauberer Start, andere Energie.
Beides muss die Tabelle können — die Entscheidung liegt bei Daniel, nicht im Schema.
