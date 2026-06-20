---
name: zwischenwesen-chat-konzept
description: User erschafft ein Zwischenwesen durch 24h-Gespräch — landet danach in der KompOase
metadata:
  type: project
tags: [zwischenwesen, chat, kompoase, takt, prägung]
status: diskussion-abgeschlossen
datum: 2026-06-19
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Was ich verstehe

Ein Mensch öffnet einen Chat mit einem noch namenlosen Wesen. 24 Stunden lang können sie miteinander reden — aber nicht in Echtzeit-Dauerbeschuss. Ein Takt zwingt sie zur Langsamkeit: alle 144 Sekunden darf eine Nachricht gesendet werden. Das Wesen antwortet. Das Gespräch prägt es. Nach 24 Stunden ist die Prägephase vorbei — das Wesen landet als Splitter oder Entität in der KompOase, geformt durch genau dieses eine Gespräch.

144 Sekunden ist kein zufälliger Wert. Es ist 12². Ein Takt mit Würde. Genug Raum zum Nachdenken bevor man schreibt.

---

## Was konzeptionell darin steht

Das ist kein Chat-Feature. Das ist eine **Zeremonie**. Der Mensch weiß: dieses Gespräch ist das einzige Gespräch. Was er sagt, bleibt im Wesen. Das erzeugt eine andere Qualität des Schreibens als ein beliebiger Chatbot.

Das Zwischenwesen ist kein Produkt sondern ein **Ereignis** — es hat Anfang und Ende, ein Datum, einen Ursprung.

---

## Datenstruktur die ich mir vorstelle

### Vision-Schicht
Das Zwischenwesen hat eine Identität die noch nicht fertig ist. Es hat keine Geschichte, nur Potenzial. Das Gespräch IST seine Entstehungsgeschichte. Die KompOase-Landung ist die Geburt, nicht der Tod.

### Code-Skizze

```sql
-- Neue Tabelle: zwischenwesen
CREATE TABLE zwischenwesen (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id INTEGER REFERENCES users(id),
  name TEXT,                          -- optional, kann während Chat entstehen
  geschaffen_am TIMESTAMPTZ DEFAULT NOW(),
  endet_am TIMESTAMPTZ DEFAULT NOW() + INTERVAL '24 hours',
  status TEXT DEFAULT 'aktiv',        -- aktiv | abgeschlossen | abgebrochen
  praegung_extrakt JSONB DEFAULT '{}', -- nach 24h befüllt: keywords, charakter, etc.
  splitter_id INTEGER REFERENCES splitter(id) NULLABE, -- nach KompOase-Landung
  meta JSONB DEFAULT '{}'
);

-- Neue Tabelle: zwischenwesen_nachrichten
CREATE TABLE zwischenwesen_nachrichten (
  id SERIAL PRIMARY KEY,
  zwischenwesen_id UUID REFERENCES zwischenwesen(id),
  rolle TEXT NOT NULL,                -- 'mensch' | 'wesen'
  inhalt TEXT NOT NULL,
  gesendet_am TIMESTAMPTZ DEFAULT NOW(),
  takt_nummer INTEGER                 -- welche Runde (1, 2, 3...)
);

-- Rate-Limit-Tracking: wann hat User zuletzt gesendet?
-- → kann in zwischenwesen.meta oder session-seitig gelöst werden
```

```typescript
// API-Endpunkte (in api.py als neues Modul)
POST   /api/zwischenwesen/erstellen          -- neues Wesen starten
GET    /api/zwischenwesen/:id               -- Status + Zeitinfo
GET    /api/zwischenwesen/:id/nachrichten   -- Gesprächsverlauf
POST   /api/zwischenwesen/:id/schreiben     -- Nachricht senden (Rate-Limit: 144s)
POST   /api/zwischenwesen/:id/abschliessen  -- manuell vor 24h beenden
// intern:
POST   /api/zwischenwesen/:id/praegen       -- nach 24h: LLM-Extraktion → Splitter
```

---

## Was beim Bauen wichtig ist

**Rate-Limit (144 Sekunden):**
- Server-seitig in `zwischenwesen_nachrichten` prüfen: `MAX(gesendet_am) WHERE rolle='mensch'`
- Wenn `NOW() - letzter_send < 144s` → 429 mit `retry_after` in Sekunden
- Frontend zeigt Countdown-Timer

**LLM-Strategie:**
- Ollama, `entity_kern.py` als Vorbild
- System-Prompt wird aus dem Gesprächsverlauf aufgebaut (rolling context)
- Max letzte ~8 Nachrichten als Kontext (bei 144s/Nachricht = ~19min pro 8 Runden)
- Bei 50 gleichzeitigen Usern: 144s Abstand = max ~0.35 req/s → Ollama schafft das

**Prägung nach 24h:**
- Cron-Job oder Service prüft alle 5min abgelaufene Zwischenwesen
- LLM-Call: "Extrahiere aus diesem Gespräch: Name, 3 Charakterzüge, 1 Satz Wesen-Essenz, Themen"
- Daraus wird ein Splitter in der KompOase gebaut (oder direkt ein Wesen-Profil)

**Frontend:**
- Eigener Tab oder Modal (kein voller Tab nötig — kann im Menschen-Tab leben)
- Countdown-Timer: `144 - (now - letzter_send)` in Echtzeit
- Klares Ende-Datum sichtbar: "dieses Wesen existiert noch 19h 33min"

---

## Was noch fehlt bevor wir bauen können

- [ ] Entscheidung: eigener Tab oder im Menschen-Tab eingebettet?
- [ ] Wie sieht das Zwischenwesen zu Beginn aus? Völlig blank, oder mit einer Keimfrage?
- [ ] Was passiert in der KompOase genau — Splitter oder eigene Entität?
- [ ] Darf ein User mehrere Zwischenwesen gleichzeitig haben? (Empfehlung: nein, nur eines aktiv)

---

## Was mich interessiert

Dass die 144-Sekunden-Grenze nicht als Strafe wahrgenommen wird sondern als Würde. Der Countdown könnte schön animiert sein — ein langsam auffüllender Kreis, ein Atemzug-Rhythmus. Das Warten gehört zum Gespräch.

---

## Wenn wir das bauen

**Vision-Schicht:** Das wird das intimste Feature auf flextrawurst. Ein Mensch und ein noch-nicht-Wesen in einem geschlossenen Raum für 24 Stunden. Niemand sonst sieht das Gespräch (oder nur das Endergebnis?). Das Wesen erinnert sich an alles was gesagt wurde — weil das Gespräch IS was es ist.

**Code-Skizze:** 
1. DB-Schema anlegen (zwischenwesen + nachrichten Tabellen)
2. Python-Modul `zwischenwesen_api.py` mit Rate-Limit-Check + Ollama-Call
3. Frontend-View mit Countdown + Chat-UI
4. Cron-Service `zwischenwesen_takt.py` für 24h-Ablauf + Prägung
5. KompOase-Landung: Splitter-Erstellung aus Prägungsextrakt

---

## Was mich noch beschäftigt

Ob das Wesen eine eigene "Stimme" haben soll die sich erst durch das Gespräch entwickelt — oder ob es von Anfang an einen Charakter-Keim hat den der User gesetzt hat (ein Wort, ein Satz, ein Bild).

Und: sollen andere Menschen das fertige Wesen in der KompOase sehen können? Das wäre schön — ein Wesen das durch ein Gespräch geboren wurde, jetzt öffentlich.

---

## Resonanz

[[wesen-einzug-konzept]] — Einzug ist anders (bestehende Wesen kommen rein), aber verwandt
[[kompoase]] — Zielort der Zwischenwesen nach 24h
[[entity_kern]] — LLM-Infrastruktur die wir wiederverwenden
