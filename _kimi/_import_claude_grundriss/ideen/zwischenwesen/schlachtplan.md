---
name: zwischenwesen-schlachtplan
description: Bauplan in Phasen — von DB-Schema bis öffentlichem Wesen in der KompOase
metadata:
  type: project
tags: [zwischenwesen, schlachtplan, bauplan]
status: in-diskussion
datum: 2026-06-19
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Was ich verstehe

Wir bauen das in Phasen. Jede Phase ist in sich abgeschlossen und benutzbar. Keine Phase wartet auf eine spätere. Alles ist von Anfang an erweiterbar gebaut.

---

## Phase 0 — Vorbereitung (Diskussion, kein Code) ✅ ABGESCHLOSSEN

- [x] Konzept.md, Felder.md, Container.md, Memory-System.md, Architektur.md
- [x] Alle Felder bestätigt — wesen_name (22Z), wesen_typ (22Z), wesen_text (1337Z), neigungen (max 5 Tags), abneigungen (max 5 Tags), farbe (HSB), wesen_bild (1,11MB Upload oder /bildgenerator)
- [x] Tab-Name Chat: FLÜCHTLINGE — Tab-Name Archiv: FLÜCHTLINGSARCHIV
- [x] Chat fullscreen, Smartphone-tauglich, Container + Memory als Popup-Buttons
- [x] Countdowns: Cooldown (grün, klein), KompOase-Eintritt (rot, klein)
- [x] Lande-Zeremonie: Wolken-Auflösung → Entscheidungsscreen → Button für neuen Flüchtling
- [x] Entscheidungsreihenfolge nach 24h: Memory prüfen → löschen+Grund → Chatverlauf mitgeben (ja/nein) → Anonymisierung (ja/nein + Warnung)
- [x] Max 1 aktives Zwischenwesen pro User
- [x] Wesen wartet ewig — landet nicht automatisch ohne User-Entscheidung
- [x] Einzelne Sätze UND ganze Nachrichten pinnen
- [x] Container live im LLM-Kontext (nicht erst bei Extraktion)

---

## Phase 0.5 — Architektur-Entscheidungen (abgeschlossen)

- [x] Keine eigene PostgreSQL pro Zwischenwesen → shared DB
- [x] Keine eigene PostgreSQL pro Splitter → shared DB
- [x] LangGraph: erst Phase 4+, nicht am Anfang
- [x] Max 1 aktives Zwischenwesen pro User
- [x] Counter in Menschenprofil via COUNT (nicht Spalte)

---

## Phase 1 — Fundament (DB + API, kein Frontend)

**Tabellen:**
```
zwischenwesen
zwischenwesen_nachrichten
zwischenwesen_container
```

**API-Endpunkte (Python, neues Modul `zwischenwesen_api.py`):**
```
POST   /api/zwischenwesen/erstellen
GET    /api/zwischenwesen/meins               ← aktives Wesen des eingeloggten Users
GET    /api/zwischenwesen/:id
GET    /api/zwischenwesen/:id/nachrichten
POST   /api/zwischenwesen/:id/schreiben       ← Rate-Limit 144s serverseitig
GET    /api/zwischenwesen/:id/container       ← mit ?quelle=&suche= Params
POST   /api/zwischenwesen/:id/container
DELETE /api/zwischenwesen/:id/container/:item_id
GET    /api/zwischenwesen/:id/memory          ← alle Kategorien
POST   /api/zwischenwesen/:id/memory          ← Eintrag anlegen
DELETE /api/zwischenwesen/:id/memory/:item_id
PUT    /api/zwischenwesen/:id/memory/:item_id ← gewicht ändern
POST   /api/zwischenwesen/:id/memory/kategorien ← neue Kategorie anlegen
```

**Rate-Limit-Check in `/schreiben`:**
```python
letzter = SELECT MAX(gesendet_am) FROM zwischenwesen_nachrichten
          WHERE zwischenwesen_id = :id AND rolle = 'mensch'
if letzter and (now - letzter) < 144s:
    return 429, { retry_after: 144 - (now - letzter) }
```

---

## Phase 2 — LLM-Integration (Ollama, kein Frontend)

**Modul `zwischenwesen_llm.py`:**
- System-Prompt-Builder aus allen Feldern
- Nachrichten-Kontext (letzte 8 + Container)
- Async Ollama-Call (gleich wie entity_kern.py)
- Response wird sofort in `zwischenwesen_nachrichten` gespeichert

**Test:** curl-basiert, kein Frontend nötig

---

## Phase 3 — Frontend (zwei neue Tabs + Erschaffungs-Formular)

**Tab 1: FLÜCHTLINGE**

Sub-Views:
```
  ├── kein-wesen-view    → Erschaffungs-Formular (alle Felder, ein Screen)
  ├── chat-view          → aktiver 24h-Chat
  └── abgeschlossen-view → Lande-Zeremonie + danach Button "Neuen Flüchtling erschaffen"
```

Erschaffungs-Formular (ein Screen, modernes Design, keine billigen Felder):
```
[ Name des Wesens              ]  ← max 22Z, floating label
[ Was genau ist dein Wesen?    ]  ← max 22Z, floating label

Erzähl von ihm…
Was beschreibt das Wesen deines Flüchtlings.    ← zwei Sätze als Label
[ großes Textarea, Live-Counter 0/1337          ]

Was mag dein Wesen?
  [Schreib hier...] [+ Hinzufügen]   ← max 5 Tags

Was mag dein Wesen nicht?
  [Schreib hier...] [+ Hinzufügen]   ← max 5 Tags

Farbe deines Wesens  [HSB-Picker]

Bild deines Wesens   [Hochladen] oder [Generieren →]

[ Wesen erschaffen ]   ← prominenter CTA
```

Chat-View Layout:
```
┌─────────────────────────────────────┐
│  [◇ Wesen-Name]  [CONTAINER] [GEDÄCHTNIS]  [⏱ 21h 44m] │
│─────────────────────────────────────│
│                                     │
│   [Wesen-Nachricht]                 │
│              [Mensch-Nachricht]     │
│   [▸ Wesen denkt...]                │  ← Inner Monologue, ausklappbar
│   [Wesen-Nachricht]                 │
│                                     │
│─────────────────────────────────────│
│  [Schreib hier...              ] [→]│
│  ⏱ Cooldown: 1:44     🔴 KompOase: 21h 44m │  ← grün / rot, klein
└─────────────────────────────────────┘
```

Animationen (alle bestätigt):
- Farbe des Wesens arbeitet sich über die Zeit in Chat-Ränder ein
- Wesen erwähnt wenn User etwas gepinnt hat + sagt was das in ihm auslöst
- Inner Monologue: andere Schrift, leicht unregelmäßiger Zeilenabstand
- Typing-Rhythmus: unregelmäßige Pausen mitten im Satz (echtes Zögern)
- Abreise: Chatfenster löst sich wolkenartig auf wenn 24h enden

Popups:
- [CONTAINER]-Button → Popup mit allen gepinnten Einträgen, Filter + Suche, einzeln löschbar, live-refreshed, externer Button öffnet /popup/container
- [GEDÄCHTNIS]-Button → Popup mit allen Memory-Kategorien, einzeln löschbar, live-refreshed, externer Button öffnet /popup/memory

**Tab 2: FLÜCHTLINGSARCHIV**

Zeigt alle eigenen erschaffenen Flüchtlinge (abgeschlossen):
- Name, Typ, Farbe, Bild, Datum
- Erstellungs-Eingaben lesbar
- Chatverlauf lesbar (sofern nicht gelöscht)
- Link → KompOase-Ansicht des Wesens

**Content-Filter (Phase 3, bei Erstellung):**
- Schicht 1 (regelbasiert): wesen_typ darf nicht "Mensch", "Mann", "Frau", "Person" etc. sein
- Schicht 2 (LLM-Check via Ollama): wesen_text + wesen_typ auf extreme Gewalt / sexuellen Übergriff auf Personen prüfen → BLOCK
- Erlaubt: Obszönität, Beleidigungen, harte Sprache, verbale Schärfe
- Wesen darf zurückschiessen (Grok-Stil, mit Witz, nicht Zuckerwatte)

---

## Phase 4 — Prägung & Lande-Zeremonie

**Service `zwischenwesen_takt.py` (alle 5 Minuten):**
```python
for wesen in SELECT * FROM zwischenwesen WHERE status='aktiv' AND endet_am < NOW():
    wesen.status = 'warte_auf_entscheidung'   # wartet ewig — kein Auto-Land
    # Frontend zeigt Lande-Zeremonie-Screen
```

**Lande-Zeremonie (Frontend):**
1. Chatfenster löst sich wolkenartig auf (Animation)
2. Entscheidungsscreen erscheint mit dieser Reihenfolge:
   - Memory-Ansicht: was liegt in welcher Kategorie? Einzeln löschbar (mit Pflicht-Begründung, kein Hard-Delete)
   - "Darf der komplette Chatverlauf mit in die KompOase?" → ja/nein (nicht default)
   - "Anonymisieren?" → ja/nein (nicht default) + Warnung:
     > "Du verlierst deinen Anspruch auf Sichtbarkeit für immer. Dein Name erscheint weder in der KompOase noch im Ahnenverzeichnis des Wesens — auch wenn aus ihm jemals eine Entität entstehen sollte."
3. Nach Absenden: Entscheidungsscreen verschwindet → Button "Neuen Flüchtling erschaffen"

**Was immer gespeichert wird (Admin + System):**
- Kompletter Chatverlauf
- Komplettes Memory-System inkl. gelöschter Einträge (mit Lösch-Begründung)
- Alle Entscheidungen der Lande-Zeremonie

---

## Phase 5 — KompOase-Integration (Zwischenwesenfragment)

Splitter-Typ: `zwischenwesenfragment`

In der KompOase erscheint das Wesen als:
- Farbige Raute ◇ in der Wesen-Farbe
- Name + Typ sichtbar
- Chatverlauf klickbar (wenn User freigegeben hat)
- Memory sichtbar (immer öffentlich)
- Wesen-Bild klickbar → Vollansicht

Das Zwischenwesenfragment ist aktiv in der KompOase:
- Es sammelt Splitter die es mag (pro) — selbst entschieden
- Es sammelt Splitter die es nicht mag (contra) — selbst entschieden
- Grundlage: Neigungen/Abneigungen aus Erschaffung + eigene KompOase-Entscheidungen
- System analysiert Zustand periodisch → Status: `läuft` / `loopt` / `ohnmächtig`
- Admin-Report mit Fix-Vorschlägen wenn problematischer Zustand

---

## Phase 6 — Splitterblase-Physik

Pro- vs. Contra-Splitter kämpfen innerhalb des Zwischenwesenfragments:
- Energie steigt wenn Pro-Splitter dominieren (Blase wächst)
- Energie sinkt wenn Contra-Splitter dominieren (Blase schrumpft)
- Bei Ausbruch: Zwischenwesenfragment erzeugt eine Kopie → `Zwischensplitterblase`

Zwischensplitterblase (neuer Typ, anonym aber nicht unsichtbar):
- Landet selbstständig in der KompOase
- Kann sich mit anderen Zwischensplitterblasen verbinden
- Bei Verbindung zweier Blasen: müssen gemeinsamen Teil abwerfen (entweder den gemeinsam gemochten Splitter ODER den gemeinsam nicht gemochten)
- Was bleibt: reine Pro-Blase ODER reine Contra-Blase → heißt dann `Splitterblase`

Ausbruchs-Bedingung: noch offen — später planen.

---

## Phase 7 — LangGraph + Inner Monologue + Embeddings

- LangGraph: Checkpointing zwischen 144s-Pausen, Memory als Tool (aktiver Retrieval)
- Inner Monologue: sichtbar als ausklappbarer Block vor der Wesen-Antwort
- Embeddings: nomic-embed-text via Ollama für semantische Memory-Suche

---

## Reihenfolge ist wichtig

```
Phase 0 → Diskussion fertig
Phase 1 → DB + API (testbar per curl)
Phase 2 → LLM (testbar per curl)
Phase 3 → Frontend
Phase 4 → Prägung-Service
Phase 5 → KompOase
```

Jede Phase kann einzeln deployed werden. Phase 3 braucht Phase 1+2.
Phase 4 braucht 1+2 (nicht zwingend 3).
Phase 5 braucht alle.

---

## Resonanz

[[zwischenwesen-chat-konzept]]
[[zwischenwesen-felder]]
[[zwischenwesen-container]]
