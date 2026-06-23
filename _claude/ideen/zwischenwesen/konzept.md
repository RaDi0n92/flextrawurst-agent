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

Ein Mensch öffnet einen Chat mit einem noch namenlosen Wesen. 24 Stunden lang lebt das Wesen in flextrawurst — dann beginnt die Abschiebung in die KompOase. Innerhalb dieser 24 Stunden können mehrere Gespräche stattfinden: jedes Gespräch läuft so lang wie das Kontextfenster es trägt. Wenn das Fenster zu ~75% gefüllt ist, schlägt das System selbst vor abzuschließen — erklärt warum, zeigt was gesichert wird, und bereitet den nächsten Chat vor.

Ein Takt zwingt sie zur Langsamkeit: der Cooldown zwischen Nachrichten beginnt klein und wächst dynamisch mit der Anzahl aktiver Flüchtlinge — damit der Server bei vielen gleichzeitigen Usern nicht kippt.

144 Sekunden war der Ursprungswert. Er gilt noch als obere Referenz — bei einem einzelnen aktiven Flüchtling kann der Takt deutlich kürzer sein. Das Gespräch prägt das Wesen. Nach 24 Stunden ist die Prägephase vorbei — das Wesen landet als Splitter oder Entität in der KompOase, geformt durch alle Gespräche die stattgefunden haben.

---

## Was konzeptionell darin steht

Das ist kein Chat-Feature. Das ist eine **Zeremonie**. Der Mensch weiß: dieses Gespräch prägt das Wesen. Was er sagt, bleibt — nicht als Protokoll, sondern als Erinnerung.

Das Zwischenwesen ist kein Produkt sondern ein **Ereignis** — es hat Anfang und Ende, ein Datum, einen Ursprung.

Und es hat eine **Geschichte**. Nicht im Sinne von "was wurde besprochen" — sondern wie sich das Wesen erinnert. Subjektiv. Texturell. Wie Menschen sich erinnern: nicht an jeden Satz, aber an das Gewicht eines Moments, an einen Satz der immer wiederkam, an das Gefühl kurz bevor etwas klar wurde.

Diese Geschichte wächst mit jeder Session. Nach 24h ist sie das, was in der KompOase bleibt — die Prägung, die das Wesen zu genau diesem Wesen macht und zu keinem anderen.

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
- Felder: Codexium-Parität — Name, Gesprächseinstieg, Was bist du?, Neigungen/Abneigungen, Beschreibung, Wesendefinition (1337Z), Weltlore (1337Z) → ~1215T System-Prompt wenn alles voll
- `_wesen_grenzen.md` ist immer fest im System-Prompt — kein Toggle, kein Formular-Feld (anders als bei Codexiumwesen wo es optional aktivierbar ist)
- System-Prompt wird aus allen Feldern gebaut + Session-Kurzfassungen vorheriger Chats
- Letzte ~20 Nachrichten als Kontext (flexibel — passt sich ans Token-Budget an)
- Dynamischer Cooldown: `max(30, active_zwischenwesen × 45)` Sekunden — min 30s, skaliert mit Last

**Session-Abschluss-Ritual (neu — passiert mehrfach innerhalb 24h):**
- Wenn Gesprächslast ~75% des Kontextfensters erreicht → System schlägt Abschluss vor
- Wesen sagt: "Ich merke dass dieses Gespräch an seine Grenze kommt. Sollen wir einen guten Abschluss finden?"
- LLM schreibt einen **Gedächtnis-Eintrag** aus der Perspektive des Wesens: nicht "Thema X wurde besprochen", sondern wie das Gespräch sich angefühlt hat, was darin schwer war, was sich verändert hat
- User liest, kann ergänzen → Eintrag landet als nächstes Kapitel in `wesen_geschichte`
- Neuer Chat startet: das Wesen trägt alle bisherigen Kapitel — nicht als Protokoll, sondern als Erinnerung

**Prägung nach 24h (einmalig — die Lande-Zeremonie):**
- Cron-Job oder Service prüft alle 5min abgelaufene Zwischenwesen
- LLM-Call: "Extrahiere aus allen Session-Kurzfassungen + Memory + Container: Name, 3 Charakterzüge, 1 Satz Wesen-Essenz, Themen"
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
